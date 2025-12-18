import * as fs from 'fs'
import * as path from 'path'
import { MotiaStep, RunContext } from '../core/types'

export interface SafetyConfig {
  bannedCommands: string[]
  allowedWriteRoots: string[]
  protectedFiles: string[]
  maxFileSize: number
  maxFilesPerOperation: number
  requireConfirmation: string[]
  safetyLevel: 'permissive' | 'normal' | 'strict'
  enableRollback: boolean
  backupBeforeModification: boolean
  testBeforeCommit: boolean
}

export interface SafetyValidationResult {
  ok: boolean
  reason?: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  suggestedAction?: string
}

export interface RollbackResult {
  totalFiles: number
  successCount: number
  failureCount: number
  results: { filePath: string; success: boolean; error?: string }[]
}

export interface RollbackPoint {
  id: string
  timestamp: string
  description: string
  backupMap: Map<string, string>
}

export interface RollbackPointSummary {
  id: string
  timestamp: string
  description: string
  fileCount: number
}

export class SafetyCore {
  private config: SafetyConfig
  private backupDir: string

  constructor(configPath: string = './config/safety.json') {
    this.config = this.loadConfig(configPath)
    this.backupDir = './.motia/backups'
    this.ensureBackupDir()
  }

  private loadConfig(configPath: string): SafetyConfig {
    try {
      const configData = fs.readFileSync(configPath, 'utf8')
      return JSON.parse(configData)
    } catch (error) {
      console.warn(`Failed to load safety config from ${configPath}, using defaults`)
      return this.getDefaultConfig()
    }
  }

  private getDefaultConfig(): SafetyConfig {
    return {
      bannedCommands: ['rm -rf', 'shutdown', 'reboot'],
      allowedWriteRoots: ['./'],
      protectedFiles: ['.git/**', 'config/safety.json'],
      maxFileSize: 10485760, // 10MB
      maxFilesPerOperation: 50,
      requireConfirmation: ['delete', 'remove'],
      safetyLevel: 'normal',
      enableRollback: true,
      backupBeforeModification: true,
      testBeforeCommit: false
    }
  }

  private ensureBackupDir(): void {
    if (!fs.existsSync(this.backupDir)) {
      fs.mkdirSync(this.backupDir, { recursive: true })
    }
  }

  /**
   * Main validation function - checks if a step is safe to execute
   */
  public validateStep(step: MotiaStep, context: RunContext): SafetyValidationResult {
    // Check for banned commands
    const commandCheck = this.validateCommand(step)
    if (!commandCheck.ok) return commandCheck

    // Check file operations
    const fileCheck = this.validateFileOperation(step)
    if (!fileCheck.ok) return fileCheck

    // Check write permissions
    const writeCheck = this.validateWritePermissions(step)
    if (!writeCheck.ok) return writeCheck

    // Check protected files
    const protectedCheck = this.validateProtectedFiles(step)
    if (!protectedCheck.ok) return protectedCheck

    // Check operation scale
    const scaleCheck = this.validateOperationScale(step)
    if (!scaleCheck.ok) return scaleCheck

    return { ok: true, severity: 'info' }
  }

  private validateCommand(step: MotiaStep): SafetyValidationResult {
    if (step.tool !== 'run_command') {
      return { ok: true, severity: 'info' }
    }

    const command = step.params.command || ''
    
    for (const bannedPattern of this.config.bannedCommands) {
      if (this.matchesPattern(command, bannedPattern)) {
        return {
          ok: false,
          reason: `Command matches banned pattern: ${bannedPattern}`,
          severity: 'critical',
          suggestedAction: 'Use a safer alternative command or modify the operation'
        }
      }
    }

    return { ok: true, severity: 'info' }
  }

  private validateFileOperation(step: MotiaStep): SafetyValidationResult {
    const fileTools = ['edit_file', 'create_file', 'delete_file', 'move_file']
    
    if (!fileTools.includes(step.tool)) {
      return { ok: true, severity: 'info' }
    }

    const filePath = step.params.path || step.params.filePath || ''
    
    // Check file size limits
    if (step.tool === 'edit_file' || step.tool === 'create_file') {
      const content = step.params.content || ''
      if (content.length > this.config.maxFileSize) {
        return {
          ok: false,
          reason: `File content exceeds maximum size limit (${this.config.maxFileSize} bytes)`,
          severity: 'error',
          suggestedAction: 'Split into smaller files or reduce content size'
        }
      }
    }

    return { ok: true, severity: 'info' }
  }

  private validateWritePermissions(step: MotiaStep): SafetyValidationResult {
    const writeTools = ['edit_file', 'create_file', 'move_file']
    
    if (!writeTools.includes(step.tool)) {
      return { ok: true, severity: 'info' }
    }

    const filePath = step.params.path || step.params.filePath || ''
    const normalizedPath = path.normalize(filePath)

    // Check if path is within allowed write roots
    const isAllowed = this.config.allowedWriteRoots.some(root => {
      const normalizedRoot = path.normalize(root)
      return normalizedPath.startsWith(normalizedRoot)
    })

    if (!isAllowed) {
      return {
        ok: false,
        reason: `Write operation outside allowed directories: ${filePath}`,
        severity: 'error',
        suggestedAction: `Ensure file path starts with one of: ${this.config.allowedWriteRoots.join(', ')}`
      }
    }

    return { ok: true, severity: 'info' }
  }

  private validateProtectedFiles(step: MotiaStep): SafetyValidationResult {
    const fileTools = ['edit_file', 'delete_file', 'move_file']
    
    if (!fileTools.includes(step.tool)) {
      return { ok: true, severity: 'info' }
    }

    const filePath = step.params.path || step.params.filePath || ''
    
    for (const protectedPattern of this.config.protectedFiles) {
      if (this.matchesPattern(filePath, protectedPattern)) {
        return {
          ok: false,
          reason: `Attempting to modify protected file: ${filePath}`,
          severity: 'critical',
          suggestedAction: 'Protected files cannot be modified for safety reasons'
        }
      }
    }

    return { ok: true, severity: 'info' }
  }

  private validateOperationScale(step: MotiaStep): SafetyValidationResult {
    // Check for bulk operations that might be dangerous
    const bulkTools = ['run_command']
    
    if (!bulkTools.includes(step.tool)) {
      return { ok: true, severity: 'info' }
    }

    const command = step.params.command || ''
    
    // Check for operations that might affect many files
    const bulkPatterns = ['find . -name', 'grep -r', 'sed -i', 'awk']
    
    for (const pattern of bulkPatterns) {
      if (command.includes(pattern)) {
        return {
          ok: true,
          severity: 'warning',
          reason: `Bulk operation detected: ${pattern}`,
          suggestedAction: 'Ensure this operation is intended and safe'
        }
      }
    }

    return { ok: true, severity: 'info' }
  }

  private matchesPattern(text: string, pattern: string): boolean {
    // Simple pattern matching - can be enhanced with regex
    if (pattern.includes('*')) {
      const regexPattern = pattern.replace(/\*/g, '.*')
      return new RegExp(regexPattern).test(text)
    }
    return text.includes(pattern)
  }

  /**
   * Create backup of file before modification
   */
  public async createBackup(filePath: string): Promise<string> {
    if (!this.config.backupBeforeModification) {
      return ''
    }

    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const backupFileName = `${path.basename(filePath)}.${timestamp}.backup`
      const backupPath = path.join(this.backupDir, backupFileName)
      
      if (fs.existsSync(filePath)) {
        fs.copyFileSync(filePath, backupPath)
        console.log(`Created backup: ${backupPath}`)
        return backupPath
      }
    } catch (error) {
      console.warn(`Failed to create backup for ${filePath}:`, error)
    }
    
    return ''
  }

  /**
   * Rollback file from backup
   */
  public async rollbackFile(filePath: string, backupPath: string): Promise<boolean> {
    if (!this.config.enableRollback || !backupPath) {
      return false
    }

    try {
      if (fs.existsSync(backupPath)) {
        fs.copyFileSync(backupPath, filePath)
        console.log(`Rolled back ${filePath} from ${backupPath}`)
        return true
      }
    } catch (error) {
      console.error(`Failed to rollback ${filePath}:`, error)
    }
    
    return false
  }

  /**
   * Rollback multiple files from their backups
   */
  public async rollbackMultipleFiles(rollbackMap: Map<string, string>): Promise<RollbackResult> {
    const results: { filePath: string; success: boolean; error?: string }[] = []
    let successCount = 0
    let failureCount = 0

    for (const [filePath, backupPath] of rollbackMap) {
      try {
        const success = await this.rollbackFile(filePath, backupPath)
        results.push({ filePath, success })
        if (success) {
          successCount++
        } else {
          failureCount++
        }
      } catch (error) {
        results.push({ filePath, success: false, error: error.message })
        failureCount++
      }
    }

    return {
      totalFiles: rollbackMap.size,
      successCount,
      failureCount,
      results
    }
  }

  /**
   * Create rollback point for multiple files
   */
  public async createRollbackPoint(filePaths: string[]): Promise<RollbackPoint> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const rollbackId = `rollback-${timestamp}`n    const backupMap = new Map<string, string>()

    for (const filePath of filePaths) {
      if (fs.existsSync(filePath)) {
        const backupPath = await this.createBackup(filePath)
        if (backupPath) {
          backupMap.set(filePath, backupPath)
        }
      }
    }

    const rollbackPoint: RollbackPoint = {
      id: rollbackId,
      timestamp,
      backupMap,
      description: `Rollback point created for ${filePaths.length} files`
    }

    // Save rollback point metadata
    await this.saveRollbackPoint(rollbackPoint)

    return rollbackPoint
  }

  /**
   * Execute rollback to a specific point
   */
  public async executeRollback(rollbackPoint: RollbackPoint): Promise<RollbackResult> {
    console.log(`Executing rollback to point: ${rollbackPoint.id}`)
    return await this.rollbackMultipleFiles(rollbackPoint.backupMap)
  }

  /**
   * Save rollback point metadata
   */
  private async saveRollbackPoint(rollbackPoint: RollbackPoint): Promise<void> {
    try {
      const rollbackDir = path.join(this.backupDir, 'rollback-points')
      if (!fs.existsSync(rollbackDir)) {
        fs.mkdirSync(rollbackDir, { recursive: true })
      }

      const metadataPath = path.join(rollbackDir, `${rollbackPoint.id}.json`)
      const metadata = {
        id: rollbackPoint.id,
        timestamp: rollbackPoint.timestamp,
        description: rollbackPoint.description,
        files: Array.from(rollbackPoint.backupMap.entries())
      }

      fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2))
      console.log(`Saved rollback point metadata: ${metadataPath}`)
    } catch (error) {
      console.warn(`Failed to save rollback point metadata:`, error)
    }
  }

  /**
   * Load rollback point from metadata
   */
  public async loadRollbackPoint(rollbackId: string): Promise<RollbackPoint | null> {
    try {
      const rollbackDir = path.join(this.backupDir, 'rollback-points')
      const metadataPath = path.join(rollbackDir, `${rollbackId}.json`)

      if (!fs.existsSync(metadataPath)) {
        return null
      }

      const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'))
      const backupMap = new Map<string, string>(metadata.files)

      return {
        id: metadata.id,
        timestamp: metadata.timestamp,
        description: metadata.description,
        backupMap
      }
    } catch (error) {
      console.error(`Failed to load rollback point ${rollbackId}:`, error)
      return null
    }
  }

  /**
   * List available rollback points
   */
  public async listRollbackPoints(): Promise<RollbackPointSummary[]> {
    try {
      const rollbackDir = path.join(this.backupDir, 'rollback-points')
      if (!fs.existsSync(rollbackDir)) {
        return []
      }

      const files = fs.readdirSync(rollbackDir).filter(f => f.endsWith('.json'))
      const summaries: RollbackPointSummary[] = []

      for (const file of files) {
        try {
          const metadata = JSON.parse(fs.readFileSync(path.join(rollbackDir, file), 'utf8'))
          summaries.push({
            id: metadata.id,
            timestamp: metadata.timestamp,
            description: metadata.description,
            fileCount: metadata.files.length
          })
        } catch (error) {
          console.warn(`Failed to read rollback metadata from ${file}:`, error)
        }
      }

      return summaries.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    } catch (error) {
      console.error('Failed to list rollback points:', error)
      return []
    }
  }

  /**
   * Clean up old rollback points
   */
  public async cleanupOldRollbackPoints(maxAge: number = 7 * 24 * 60 * 60 * 1000): Promise<void> {
    try {
      const rollbackPoints = await this.listRollbackPoints()
      const now = Date.now()

      for (const point of rollbackPoints) {
        const age = now - new Date(point.timestamp).getTime()
        if (age > maxAge) {
          await this.deleteRollbackPoint(point.id)
        }
      }
    } catch (error) {
      console.error('Failed to cleanup old rollback points:', error)
    }
  }

  /**
   * Delete a rollback point and its backups
   */
  private async deleteRollbackPoint(rollbackId: string): Promise<void> {
    try {
      const rollbackPoint = await this.loadRollbackPoint(rollbackId)
      if (!rollbackPoint) return

      // Delete backup files
      for (const backupPath of rollbackPoint.backupMap.values()) {
        if (fs.existsSync(backupPath)) {
          fs.unlinkSync(backupPath)
        }
      }

      // Delete metadata file
      const rollbackDir = path.join(this.backupDir, 'rollback-points')
      const metadataPath = path.join(rollbackDir, `${rollbackId}.json`)
      if (fs.existsSync(metadataPath)) {
        fs.unlinkSync(metadataPath)
      }

      console.log(`Deleted rollback point: ${rollbackId}`)
    } catch (error) {
      console.error(`Failed to delete rollback point ${rollbackId}:`, error)
    }
  }

  /**
   * Run quick safety checks after code modifications
   */
  public async runCommitGateChecks(modifiedFiles: string[]): Promise<SafetyValidationResult> {
    if (!this.config.testBeforeCommit) {
      return { ok: true, severity: 'info' }
    }

    try {
      // Check git diff for protected files
      const gitDiffResult = await this.checkGitDiff(modifiedFiles)
      if (!gitDiffResult.ok) return gitDiffResult

      // Run tests if available
      const testResult = await this.runAvailableTests()
      if (!testResult.ok) return testResult

      return { ok: true, severity: 'info' }
    } catch (error) {
      return {
        ok: false,
        reason: `Commit gate checks failed: ${error}`,
        severity: 'error',
        suggestedAction: 'Review changes and fix issues before proceeding'
      }
    }
  }

  private async checkGitDiff(modifiedFiles: string[]): Promise<SafetyValidationResult> {
    for (const file of modifiedFiles) {
      for (const protectedPattern of this.config.protectedFiles) {
        if (this.matchesPattern(file, protectedPattern)) {
          return {
            ok: false,
            reason: `Git diff shows changes to protected file: ${file}`,
            severity: 'critical',
            suggestedAction: 'Revert changes to protected files'
          }
        }
      }
    }
    return { ok: true, severity: 'info' }
  }

  private async runAvailableTests(): Promise<SafetyValidationResult> {
    // Check for common test commands
    const testCommands = ['npm test', 'yarn test', 'pytest', 'cargo test']
    
    for (const testCmd of testCommands) {
      const [cmd, ...args] = testCmd.split(' ')
      
      try {
        // Check if command exists (simplified check)
        if (fs.existsSync('package.json') && (cmd === 'npm' || cmd === 'yarn')) {
          console.log(`Would run: ${testCmd}`)
          // In a real implementation, you'd run the actual test
          return { ok: true, severity: 'info' }
        }
      } catch (error) {
        // Continue to next test command
      }
    }

    return { ok: true, severity: 'info', reason: 'No tests found to run' }
  }

  /**
   * Get safety configuration
   */
  public getConfig(): SafetyConfig {
    return { ...this.config }
  }

  /**
   * Update safety configuration
   */
  public updateConfig(updates: Partial<SafetyConfig>): void {
    this.config = { ...this.config, ...updates }
  }
}

// Export singleton instance
export const safetyCore = new SafetyCore()
