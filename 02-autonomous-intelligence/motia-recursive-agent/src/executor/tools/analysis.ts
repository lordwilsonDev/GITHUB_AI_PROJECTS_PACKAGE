import { Tool, ToolInfo } from './registry.js';
import { RunContext } from '../../core/runContext.js';
import * as fs from 'fs/promises';
import * as path from 'path';

/**
 * Analysis Tool - handles code and repository analysis
 */
export class AnalysisTool implements Tool {
  private readonly context: RunContext;

  constructor(context: RunContext) {
    this.context = context;
  }

  async execute(operation: string, params: Record<string, any>): Promise<any> {
    if (operation !== 'analyze') {
      throw new Error(`Unknown analysis operation: ${operation}`);
    }

    return this.performAnalysis(params);
  }

  async validate(operation: string, params: Record<string, any>): Promise<void> {
    if (!params.type) {
      throw new Error('Missing required parameter: type');
    }

    const validTypes = this.getValidAnalysisTypes();
    if (!validTypes.includes(params.type)) {
      throw new Error(`Invalid analysis type: ${params.type}`);
    }
  }

  getInfo(): ToolInfo {
    return {
      name: 'Analysis',
      description: 'Code and repository analysis',
      operations: ['analyze'],
      requiredParams: {
        'analyze': ['type']
      },
      optionalParams: {
        'analyze': ['target', 'depth', 'format', 'include', 'exclude']
      }
    };
  }

  /**
   * Perform analysis based on type
   */
  private async performAnalysis(params: Record<string, any>): Promise<any> {
    const { type, target, depth = 2, format = 'json' } = params;

    this.context.log('debug', `Starting analysis: ${type}`, { target, depth });

    const startTime = Date.now();
    let result;

    switch (type) {
      case 'repository':
        result = await this.analyzeRepository(target, depth);
        break;
      case 'filesystem':
        result = await this.analyzeFilesystem(target, depth);
        break;
      case 'code':
        result = await this.analyzeCode(target);
        break;
      case 'dependencies':
        result = await this.analyzeDependencies(target);
        break;
      case 'structure':
        result = await this.analyzeStructure(target, depth);
        break;
      case 'report':
        result = await this.generateReport(params);
        break;
      default:
        throw new Error(`Unknown analysis type: ${type}`);
    }

    const duration = Date.now() - startTime;
    
    this.context.log('debug', `Analysis completed: ${type}`, { duration });

    return {
      type,
      target,
      result,
      duration,
      timestamp: new Date().toISOString(),
      format
    };
  }

  /**
   * Analyze repository structure and metadata
   */
  private async analyzeRepository(target?: string, depth: number = 2): Promise<any> {
    const repoPath = target || this.context.repoContext.rootPath;
    
    const analysis = {
      path: repoPath,
      structure: await this.scanDirectory(repoPath, depth),
      packageInfo: await this.getPackageInfo(repoPath),
      gitInfo: await this.getGitInfo(repoPath),
      fileTypes: await this.analyzeFileTypes(repoPath),
      metrics: await this.calculateMetrics(repoPath)
    };

    return analysis;
  }

  /**
   * Analyze filesystem structure
   */
  private async analyzeFilesystem(target?: string, depth: number = 2): Promise<any> {
    const targetPath = target || this.context.repoContext.rootPath;
    
    return {
      path: targetPath,
      structure: await this.scanDirectory(targetPath, depth),
      stats: await this.getDirectoryStats(targetPath)
    };
  }

  /**
   * Analyze code quality and structure
   */
  private async analyzeCode(target?: string): Promise<any> {
    const targetPath = target || this.context.repoContext.rootPath;
    
    const codeFiles = await this.findCodeFiles(targetPath);
    const analysis = {
      files: codeFiles.length,
      languages: await this.detectLanguages(codeFiles),
      complexity: await this.analyzeComplexity(codeFiles),
      patterns: await this.detectPatterns(codeFiles)
    };

    return analysis;
  }

  /**
   * Analyze project dependencies
   */
  private async analyzeDependencies(target?: string): Promise<any> {
    const targetPath = target || this.context.repoContext.rootPath;
    
    const dependencies = {
      npm: await this.getNpmDependencies(targetPath),
      python: await this.getPythonDependencies(targetPath),
      rust: await this.getRustDependencies(targetPath)
    };

    return dependencies;
  }

  /**
   * Analyze project structure
   */
  private async analyzeStructure(target?: string, depth: number = 2): Promise<any> {
    const targetPath = target || this.context.repoContext.rootPath;
    
    return {
      directories: await this.getDirectoryStructure(targetPath, depth),
      patterns: await this.detectStructurePatterns(targetPath),
      recommendations: await this.getStructureRecommendations(targetPath)
    };
  }

  /**
   * Generate comprehensive report
   */
  private async generateReport(params: Record<string, any>): Promise<any> {
    const { format = 'markdown' } = params;
    
    const repoAnalysis = await this.analyzeRepository();
    const codeAnalysis = await this.analyzeCode();
    const depAnalysis = await this.analyzeDependencies();

    const report = {
      summary: {
        projectName: repoAnalysis.packageInfo?.name || 'Unknown',
        totalFiles: repoAnalysis.metrics.totalFiles,
        totalLines: repoAnalysis.metrics.totalLines,
        languages: codeAnalysis.languages
      },
      repository: repoAnalysis,
      code: codeAnalysis,
      dependencies: depAnalysis,
      recommendations: await this.generateRecommendations(repoAnalysis, codeAnalysis)
    };

    if (format === 'markdown') {
      return {
        ...report,
        markdown: this.formatAsMarkdown(report)
      };
    }

    return report;
  }

  /**
   * Scan directory structure
   */
  private async scanDirectory(dirPath: string, depth: number): Promise<any> {
    if (depth <= 0) return null;

    try {
      const entries = await fs.readdir(dirPath, { withFileTypes: true });
      const structure = {};

      for (const entry of entries) {
        if (entry.name.startsWith('.')) continue; // Skip hidden files
        
        const fullPath = path.join(dirPath, entry.name);
        
        if (entry.isDirectory()) {
          structure[entry.name] = await this.scanDirectory(fullPath, depth - 1);
        } else {
          const stats = await fs.stat(fullPath);
          structure[entry.name] = {
            type: 'file',
            size: stats.size,
            modified: stats.mtime
          };
        }
      }

      return structure;
    } catch (error) {
      return { error: error.message };
    }
  }

  /**
   * Get package.json information
   */
  private async getPackageInfo(repoPath: string): Promise<any> {
    try {
      const packagePath = path.join(repoPath, 'package.json');
      const content = await fs.readFile(packagePath, 'utf8');
      return JSON.parse(content);
    } catch {
      return null;
    }
  }

  /**
   * Get git information
   */
  private async getGitInfo(repoPath: string): Promise<any> {
    try {
      const gitPath = path.join(repoPath, '.git');
      await fs.access(gitPath);
      
      // This would integrate with git commands
      return {
        isRepo: true,
        // Additional git info would be gathered here
      };
    } catch {
      return { isRepo: false };
    }
  }

  /**
   * Analyze file types in repository
   */
  private async analyzeFileTypes(repoPath: string): Promise<any> {
    const fileTypes = {};
    
    const scanFiles = async (dir: string) => {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        if (entry.name.startsWith('.')) continue;
        
        const fullPath = path.join(dir, entry.name);
        
        if (entry.isDirectory()) {
          await scanFiles(fullPath);
        } else {
          const ext = path.extname(entry.name).toLowerCase();
          fileTypes[ext] = (fileTypes[ext] || 0) + 1;
        }
      }
    };

    try {
      await scanFiles(repoPath);
    } catch (error) {
      // Handle error
    }

    return fileTypes;
  }

  /**
   * Calculate repository metrics
   */
  private async calculateMetrics(repoPath: string): Promise<any> {
    let totalFiles = 0;
    let totalLines = 0;
    let totalSize = 0;

    const scanMetrics = async (dir: string) => {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        if (entry.name.startsWith('.')) continue;
        
        const fullPath = path.join(dir, entry.name);
        
        if (entry.isDirectory()) {
          await scanMetrics(fullPath);
        } else {
          totalFiles++;
          const stats = await fs.stat(fullPath);
          totalSize += stats.size;
          
          // Count lines for text files
          if (this.isTextFile(entry.name)) {
            try {
              const content = await fs.readFile(fullPath, 'utf8');
              totalLines += content.split('\n').length;
            } catch {
              // Skip binary files
            }
          }
        }
      }
    };

    try {
      await scanMetrics(repoPath);
    } catch (error) {
      // Handle error
    }

    return {
      totalFiles,
      totalLines,
      totalSize
    };
  }

  /**
   * Check if file is a text file
   */
  private isTextFile(filename: string): boolean {
    const textExtensions = [
      '.js', '.ts', '.jsx', '.tsx', '.py', '.rs', '.go', '.java',
      '.c', '.cpp', '.h', '.hpp', '.css', '.scss', '.html',
      '.md', '.txt', '.json', '.yaml', '.yml', '.xml'
    ];
    
    const ext = path.extname(filename).toLowerCase();
    return textExtensions.includes(ext);
  }

  /**
   * Find code files in repository
   */
  private async findCodeFiles(repoPath: string): Promise<string[]> {
    const codeFiles = [];
    
    const scanCode = async (dir: string) => {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        if (entry.name.startsWith('.')) continue;
        
        const fullPath = path.join(dir, entry.name);
        
        if (entry.isDirectory()) {
          await scanCode(fullPath);
        } else if (this.isCodeFile(entry.name)) {
          codeFiles.push(fullPath);
        }
      }
    };

    try {
      await scanCode(repoPath);
    } catch (error) {
      // Handle error
    }

    return codeFiles;
  }

  /**
   * Check if file is a code file
   */
  private isCodeFile(filename: string): boolean {
    const codeExtensions = [
      '.js', '.ts', '.jsx', '.tsx', '.py', '.rs', '.go', '.java',
      '.c', '.cpp', '.h', '.hpp'
    ];
    
    const ext = path.extname(filename).toLowerCase();
    return codeExtensions.includes(ext);
  }

  /**
   * Detect programming languages
   */
  private async detectLanguages(codeFiles: string[]): Promise<string[]> {
    const languages = new Set<string>();
    
    const languageMap = {
      '.js': 'JavaScript',
      '.ts': 'TypeScript',
      '.jsx': 'React',
      '.tsx': 'React TypeScript',
      '.py': 'Python',
      '.rs': 'Rust',
      '.go': 'Go',
      '.java': 'Java',
      '.c': 'C',
      '.cpp': 'C++',
      '.h': 'C Header',
      '.hpp': 'C++ Header'
    };

    for (const file of codeFiles) {
      const ext = path.extname(file).toLowerCase();
      if (languageMap[ext]) {
        languages.add(languageMap[ext]);
      }
    }

    return Array.from(languages);
  }

  /**
   * Analyze code complexity (simplified)
   */
  private async analyzeComplexity(codeFiles: string[]): Promise<any> {
    // Simplified complexity analysis
    return {
      files: codeFiles.length,
      averageFileSize: 0, // Would calculate actual metrics
      estimatedComplexity: codeFiles.length > 50 ? 'high' : codeFiles.length > 20 ? 'medium' : 'low'
    };
  }

  /**
   * Detect code patterns
   */
  private async detectPatterns(codeFiles: string[]): Promise<string[]> {
    const patterns = [];
    
    // Simple pattern detection based on file structure
    const hasTests = codeFiles.some(f => f.includes('test') || f.includes('spec'));
    const hasConfig = codeFiles.some(f => f.includes('config'));
    const hasComponents = codeFiles.some(f => f.includes('component'));
    
    if (hasTests) patterns.push('Testing');
    if (hasConfig) patterns.push('Configuration');
    if (hasComponents) patterns.push('Component Architecture');

    return patterns;
  }

  /**
   * Get NPM dependencies
   */
  private async getNpmDependencies(repoPath: string): Promise<any> {
    try {
      const packageInfo = await this.getPackageInfo(repoPath);
      return {
        dependencies: packageInfo?.dependencies || {},
        devDependencies: packageInfo?.devDependencies || {}
      };
    } catch {
      return null;
    }
  }

  /**
   * Get Python dependencies
   */
  private async getPythonDependencies(repoPath: string): Promise<any> {
    try {
      const requirementsPath = path.join(repoPath, 'requirements.txt');
      const content = await fs.readFile(requirementsPath, 'utf8');
      const deps = content.split('\n').filter(line => line.trim() && !line.startsWith('#'));
      return { requirements: deps };
    } catch {
      return null;
    }
  }

  /**
   * Get Rust dependencies
   */
  private async getRustDependencies(repoPath: string): Promise<any> {
    try {
      const cargoPath = path.join(repoPath, 'Cargo.toml');
      const content = await fs.readFile(cargoPath, 'utf8');
      // Would parse TOML here
      return { cargo: 'detected' };
    } catch {
      return null;
    }
  }

  /**
   * Get directory structure
   */
  private async getDirectoryStructure(repoPath: string, depth: number): Promise<any> {
    return this.scanDirectory(repoPath, depth);
  }

  /**
   * Detect structure patterns
   */
  private async detectStructurePatterns(repoPath: string): Promise<string[]> {
    const patterns = [];
    
    try {
      const entries = await fs.readdir(repoPath);
      
      if (entries.includes('src')) patterns.push('Source Directory');
      if (entries.includes('tests') || entries.includes('test')) patterns.push('Test Directory');
      if (entries.includes('docs')) patterns.push('Documentation');
      if (entries.includes('examples')) patterns.push('Examples');
      if (entries.includes('scripts')) patterns.push('Scripts');
      
    } catch {
      // Handle error
    }

    return patterns;
  }

  /**
   * Get structure recommendations
   */
  private async getStructureRecommendations(repoPath: string): Promise<string[]> {
    const recommendations = [];
    
    try {
      const entries = await fs.readdir(repoPath);
      
      if (!entries.includes('README.md')) {
        recommendations.push('Add README.md file');
      }
      
      if (!entries.includes('.gitignore')) {
        recommendations.push('Add .gitignore file');
      }
      
      if (!entries.includes('tests') && !entries.includes('test')) {
        recommendations.push('Consider adding tests directory');
      }
      
    } catch {
      // Handle error
    }

    return recommendations;
  }

  /**
   * Generate recommendations
   */
  private async generateRecommendations(repoAnalysis: any, codeAnalysis: any): Promise<string[]> {
    const recommendations = [];
    
    if (codeAnalysis.files > 50 && !repoAnalysis.structure.tests) {
      recommendations.push('Consider adding comprehensive test suite');
    }
    
    if (!repoAnalysis.packageInfo?.scripts?.build) {
      recommendations.push('Consider adding build script');
    }
    
    return recommendations;
  }

  /**
   * Format report as markdown
   */
  private formatAsMarkdown(report: any): string {
    return `# Project Analysis Report

## Summary
- **Project**: ${report.summary.projectName}
- **Total Files**: ${report.summary.totalFiles}
- **Total Lines**: ${report.summary.totalLines}
- **Languages**: ${report.summary.languages.join(', ')}

## Recommendations
${report.recommendations.map(r => `- ${r}`).join('\n')}
`;
  }

  /**
   * Get directory stats
   */
  private async getDirectoryStats(dirPath: string): Promise<any> {
    try {
      const stats = await fs.stat(dirPath);
      return {
        size: stats.size,
        created: stats.birthtime,
        modified: stats.mtime
      };
    } catch (error) {
      return { error: error.message };
    }
  }

  /**
   * Get valid analysis types
   */
  private getValidAnalysisTypes(): string[] {
    return [
      'repository',
      'filesystem',
      'code',
      'dependencies',
      'structure',
      'report'
    ];
  }
}