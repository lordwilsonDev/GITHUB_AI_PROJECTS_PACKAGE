/**
 * File System Step - Enable Vy to write code to disk safely
 * Part of MOIE-OS Sovereign Upgrade - Phase 1.1
 */

import * as fs from 'fs';
import * as path from 'path';

interface WriteOptions {
  path: string;
  content: string;
  mode?: number; // Unix file permissions (e.g., 0o644)
  createDirs?: boolean;
}

interface ReadOptions {
  path: string;
  encoding?: BufferEncoding;
}

export class FileSystemStep {
  private basePath: string;
  private safeMode: boolean;

  constructor(basePath: string = '/Users/lordwilson/vy-nexus', safeMode: boolean = true) {
    this.basePath = basePath;
    this.safeMode = safeMode;
  }

  /**
   * Safely write content to disk with proper permissions
   */
  async writeFile(options: WriteOptions): Promise<void> {
    const { path: filePath, content, mode = 0o644, createDirs = true } = options;
    
    // Validate path is within safe boundaries
    if (this.safeMode && !this.isPathSafe(filePath)) {
      throw new Error(`Unsafe path detected: ${filePath}`);
    }

    const fullPath = path.resolve(this.basePath, filePath);
    const dirPath = path.dirname(fullPath);

    try {
      // Create parent directories if needed
      if (createDirs && !fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true, mode: 0o755 });
      }

      // Write file with specified permissions
      fs.writeFileSync(fullPath, content, { mode, encoding: 'utf8' });
      
      console.log(`✅ File written successfully: ${fullPath}`);
      console.log(`   Permissions: ${mode.toString(8)}`);
    } catch (error) {
      console.error(`❌ Failed to write file: ${fullPath}`);
      throw error;
    }
  }

  /**
   * Safely read content from disk
   */
  async readFile(options: ReadOptions): Promise<string> {
    const { path: filePath, encoding = 'utf8' } = options;
    
    if (this.safeMode && !this.isPathSafe(filePath)) {
      throw new Error(`Unsafe path detected: ${filePath}`);
    }

    const fullPath = path.resolve(this.basePath, filePath);

    try {
      const content = fs.readFileSync(fullPath, { encoding });
      console.log(`✅ File read successfully: ${fullPath}`);
      return content;
    } catch (error) {
      console.error(`❌ Failed to read file: ${fullPath}`);
      throw error;
    }
  }

  /**
   * Check if file exists
   */
  fileExists(filePath: string): boolean {
    const fullPath = path.resolve(this.basePath, filePath);
    return fs.existsSync(fullPath);
  }

  /**
   * Validate path is safe (no directory traversal, within basePath)
   */
  private isPathSafe(filePath: string): boolean {
    const fullPath = path.resolve(this.basePath, filePath);
    
    // Ensure resolved path is within basePath
    if (!fullPath.startsWith(this.basePath)) {
      return false;
    }

    // Block dangerous patterns
    const dangerousPatterns = [
      /\.\.\//,  // Directory traversal
      /^\/etc/,   // System directories
      /^\/usr/,
      /^\/bin/,
      /^\/sbin/,
    ];

    return !dangerousPatterns.some(pattern => pattern.test(filePath));
  }

  /**
   * Set base path for operations
   */
  setBasePath(newBasePath: string): void {
    this.basePath = newBasePath;
  }

  /**
   * Toggle safe mode
   */
  setSafeMode(enabled: boolean): void {
    this.safeMode = enabled;
    console.log(`Safe mode ${enabled ? 'enabled' : 'disabled'}`);
  }
}

// Export singleton instance
export const fileSystem = new FileSystemStep();

// Example usage:
// await fileSystem.writeFile({
//   path: 'core/new-module.ts',
//   content: 'export const hello = "world";',
//   mode: 0o644
// });
