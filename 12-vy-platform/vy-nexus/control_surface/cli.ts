/**
 * CLI Command Interface - Provides command-line interface for system control
 * Part of MOIE-OS Sovereign Upgrade - Phase 4.1
 */

import { EventEmitter } from 'events';
import * as readline from 'readline';
import { expertRegistry } from '../core/expert-registry';
import { gatingEngine } from '../core/gating-engine';
import { expertCoordinator } from '../core/expert-coordinator';

/**
 * Command definition
 */
export interface Command {
  name: string;
  description: string;
  aliases?: string[];
  usage: string;
  handler: (args: string[]) => Promise<void>;
}

/**
 * CLI Configuration
 */
interface CLIConfig {
  prompt: string;
  historySize: number;
  enableColors: boolean;
  autoComplete: boolean;
}

/**
 * Command result
 */
interface CommandResult {
  success: boolean;
  output?: string;
  error?: string;
}

/**
 * CLI Command Interface
 * Provides interactive command-line control for the MOIE-OS system
 */
export class CLI extends EventEmitter {
  private config: CLIConfig;
  private commands: Map<string, Command>;
  private rl?: readline.Interface;
  private running: boolean = false;
  private commandHistory: string[] = [];

  constructor(config?: Partial<CLIConfig>) {
    super();
    this.config = {
      prompt: 'moie-os> ',
      historySize: 100,
      enableColors: true,
      autoComplete: true,
      ...config,
    };

    this.commands = new Map();
    this.registerDefaultCommands();

    console.log('✅ CLI initialized');
  }

  /**
   * Register default system commands
   */
  private registerDefaultCommands(): void {
    // Status command
    this.registerCommand({
      name: 'status',
      description: 'Show system status and statistics',
      aliases: ['stat', 's'],
      usage: 'status [component]',
      handler: this.handleStatus.bind(this),
    });

    // Start command
    this.registerCommand({
      name: 'start',
      description: 'Start the MOIE-OS system or specific component',
      aliases: ['run'],
      usage: 'start [component]',
      handler: this.handleStart.bind(this),
    });

    // Stop command
    this.registerCommand({
      name: 'stop',
      description: 'Stop the MOIE-OS system or specific component',
      aliases: ['halt'],
      usage: 'stop [component]',
      handler: this.handleStop.bind(this),
    });

    // Configure command
    this.registerCommand({
      name: 'configure',
      description: 'Configure system settings',
      aliases: ['config', 'set'],
      usage: 'configure <key> <value>',
      handler: this.handleConfigure.bind(this),
    });

    // Query command
    this.registerCommand({
      name: 'query',
      description: 'Query system information',
      aliases: ['q', 'get'],
      usage: 'query <resource> [filter]',
      handler: this.handleQuery.bind(this),
    });

    // List experts command
    this.registerCommand({
      name: 'experts',
      description: 'List all registered experts',
      aliases: ['list-experts', 'le'],
      usage: 'experts [filter]',
      handler: this.handleExperts.bind(this),
    });

    // Register expert command
    this.registerCommand({
      name: 'register',
      description: 'Register a new expert',
      usage: 'register <expert-id>',
      handler: this.handleRegister.bind(this),
    });

    // Route task command
    this.registerCommand({
      name: 'route',
      description: 'Route a task to an expert',
      usage: 'route <task-description>',
      handler: this.handleRoute.bind(this),
    });

    // Help command
    this.registerCommand({
      name: 'help',
      description: 'Show available commands',
      aliases: ['h', '?'],
      usage: 'help [command]',
      handler: this.handleHelp.bind(this),
    });

    // Exit command
    this.registerCommand({
      name: 'exit',
      description: 'Exit the CLI',
      aliases: ['quit', 'q'],
      usage: 'exit',
      handler: this.handleExit.bind(this),
    });

    // Clear command
    this.registerCommand({
      name: 'clear',
      description: 'Clear the screen',
      aliases: ['cls'],
      usage: 'clear',
      handler: this.handleClear.bind(this),
    });

    // History command
    this.registerCommand({
      name: 'history',
      description: 'Show command history',
      usage: 'history [count]',
      handler: this.handleHistory.bind(this),
    });
  }

  /**
   * Register a new command
   */
  public registerCommand(command: Command): void {
    this.commands.set(command.name, command);

    // Register aliases
    if (command.aliases) {
      command.aliases.forEach(alias => {
        this.commands.set(alias, command);
      });
    }

    this.emit('command:registered', command);
  }

  /**
   * Parse and execute a command
   */
  public async parseCommand(input: string): Promise<CommandResult> {
    const trimmed = input.trim();
    
    if (!trimmed) {
      return { success: true };
    }

    // Add to history
    this.addToHistory(trimmed);

    // Parse command and arguments
    const parts = trimmed.split(/\s+/);
    const commandName = parts[0].toLowerCase();
    const args = parts.slice(1);

    // Find command
    const command = this.commands.get(commandName);

    if (!command) {
      return {
        success: false,
        error: `Unknown command: ${commandName}. Type 'help' for available commands.`,
      };
    }

    try {
      await command.handler(args);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: `Error executing command: ${(error as Error).message}`,
      };
    }
  }

  /**
   * Start interactive CLI
   */
  public start(): void {
    if (this.running) {
      console.log('⚠️  CLI already running');
      return;
    }

    this.running = true;
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: this.config.prompt,
    });

    // Setup autocomplete
    if (this.config.autoComplete) {
      this.setupAutoComplete();
    }

    console.log('🚀 MOIE-OS CLI started');
    console.log('Type "help" for available commands\n');

    this.rl.prompt();

    this.rl.on('line', async (line) => {
      const result = await this.parseCommand(line);
      
      if (!result.success && result.error) {
        console.error(`❌ ${result.error}`);
      }

      if (this.running) {
        this.rl?.prompt();
      }
    });

    this.rl.on('close', () => {
      this.stop();
    });
  }

  /**
   * Stop interactive CLI
   */
  public stop(): void {
    if (!this.running) {
      return;
    }

    this.running = false;
    this.rl?.close();
    console.log('\n👋 MOIE-OS CLI stopped');
  }

  /**
   * Setup autocomplete
   */
  private setupAutoComplete(): void {
    if (!this.rl) return;

    const completer = (line: string): [string[], string] => {
      const commandNames = Array.from(this.commands.keys());
      const hits = commandNames.filter(cmd => cmd.startsWith(line));
      return [hits.length ? hits : commandNames, line];
    };

    // Note: This is a simplified version. Full implementation would require
    // more sophisticated readline configuration
  }

  /**
   * Add command to history
   */
  private addToHistory(command: string): void {
    this.commandHistory.push(command);
    
    if (this.commandHistory.length > this.config.historySize) {
      this.commandHistory.shift();
    }
  }

  // ============================================================================
  // Command Handlers
  // ============================================================================

  /**
   * Handle status command
   */
  private async handleStatus(args: string[]): Promise<void> {
    const component = args[0];

    if (!component || component === 'all') {
      console.log('\n📊 MOIE-OS System Status\n');
      
      // Expert Registry stats
      const registryStats = expertRegistry.getStats();
      console.log('Expert Registry:');
      console.log(`  Total Experts: ${registryStats.totalExperts}`);
      console.log(`  Active: ${registryStats.activeExperts}`);
      console.log(`  Inactive: ${registryStats.inactiveExperts}`);
      console.log(`  Errors: ${registryStats.errorExperts}`);
      console.log(`  Total Usage: ${registryStats.totalUsage}`);
      console.log(`  Domains: ${registryStats.domains.join(', ')}`);

      // Gating Engine stats
      const gatingStats = gatingEngine.getStats();
      console.log('\nGating Engine:');
      console.log(`  Total Routed: ${gatingStats.totalRouted}`);
      console.log(`  Successful: ${gatingStats.successfulRoutes}`);
      console.log(`  Failed: ${gatingStats.failedRoutes}`);
      console.log(`  Avg Match Score: ${gatingStats.averageMatchScore.toFixed(2)}`);

      // Coordinator stats
      const coordStats = expertCoordinator.getStats();
      console.log('\nExpert Coordinator:');
      console.log(`  Total Sessions: ${coordStats.totalSessions}`);
      console.log(`  Completed: ${coordStats.completedSessions}`);
      console.log(`  Failed: ${coordStats.failedSessions}`);
      console.log(`  Avg Duration: ${coordStats.averageDuration.toFixed(0)}ms`);
      console.log(`  Avg Experts/Session: ${coordStats.averageExpertsPerSession.toFixed(1)}`);
    } else {
      console.log(`Status for component: ${component}`);
      // Component-specific status
    }

    console.log();
  }

  /**
   * Handle start command
   */
  private async handleStart(args: string[]): Promise<void> {
    const component = args[0] || 'system';
    console.log(`🚀 Starting ${component}...`);
    
    // Implementation would start specific components
    console.log(`✅ ${component} started`);
  }

  /**
   * Handle stop command
   */
  private async handleStop(args: string[]): Promise<void> {
    const component = args[0] || 'system';
    console.log(`🛑 Stopping ${component}...`);
    
    // Implementation would stop specific components
    console.log(`✅ ${component} stopped`);
  }

  /**
   * Handle configure command
   */
  private async handleConfigure(args: string[]): Promise<void> {
    if (args.length < 2) {
      console.log('Usage: configure <key> <value>');
      return;
    }

    const [key, ...valueParts] = args;
    const value = valueParts.join(' ');

    console.log(`⚙️  Setting ${key} = ${value}`);
    // Implementation would update configuration
    console.log('✅ Configuration updated');
  }

  /**
   * Handle query command
   */
  private async handleQuery(args: string[]): Promise<void> {
    if (args.length === 0) {
      console.log('Usage: query <resource> [filter]');
      console.log('Resources: experts, sessions, tasks, config');
      return;
    }

    const resource = args[0];
    const filter = args.slice(1).join(' ');

    console.log(`🔍 Querying ${resource}${filter ? ` (filter: ${filter})` : ''}...`);

    switch (resource) {
      case 'experts':
        const experts = expertRegistry.listExperts();
        console.log(`\nFound ${experts.length} experts:`);
        experts.forEach(e => {
          console.log(`  - ${e.name} (${e.id}): ${e.status}`);
        });
        break;

      case 'sessions':
        const sessions = expertCoordinator.getAllSessions();
        console.log(`\nFound ${sessions.length} sessions:`);
        sessions.slice(-10).forEach(s => {
          console.log(`  - ${s.id}: ${s.status} (${s.experts.length} experts)`);
        });
        break;

      default:
        console.log(`Unknown resource: ${resource}`);
    }

    console.log();
  }

  /**
   * Handle experts command
   */
  private async handleExperts(args: string[]): Promise<void> {
    const filter = args[0];
    const experts = expertRegistry.listExperts();

    console.log(`\n📋 Registered Experts (${experts.length}):\n`);

    experts.forEach(expert => {
      const statusIcon = expert.status === 'active' ? '✅' : '⚠️';
      console.log(`${statusIcon} ${expert.name} (${expert.id})`);
      console.log(`   Status: ${expert.status}`);
      console.log(`   Version: ${expert.version}`);
      console.log(`   Usage: ${expert.usageCount} times`);
      console.log(`   Capabilities: ${expert.capabilities.map(c => c.domain).join(', ')}`);
      console.log();
    });
  }

  /**
   * Handle register command
   */
  private async handleRegister(args: string[]): Promise<void> {
    if (args.length === 0) {
      console.log('Usage: register <expert-id>');
      return;
    }

    const expertId = args[0];
    console.log(`📝 Registering expert: ${expertId}...`);
    
    // Implementation would load and register expert
    console.log('✅ Expert registered');
  }

  /**
   * Handle route command
   */
  private async handleRoute(args: string[]): Promise<void> {
    if (args.length === 0) {
      console.log('Usage: route <task-description>');
      return;
    }

    const description = args.join(' ');
    console.log(`🔀 Routing task: "${description}"...`);

    const task = {
      id: `task-${Date.now()}`,
      type: 'cli-task',
      description,
      priority: 'medium' as const,
      createdAt: new Date(),
    };

    try {
      const decision = await gatingEngine.routeToExpert(task);
      
      if (decision.selectedExpert) {
        console.log(`✅ Routed to: ${decision.selectedExpert.expert.metadata.name}`);
        console.log(`   Match Score: ${decision.selectedExpert.matchScore.toFixed(2)}`);
        console.log(`   Strategy: ${decision.routingStrategy}`);
      } else {
        console.log('⚠️  No suitable expert found');
      }
    } catch (error) {
      console.error('❌ Routing failed:', (error as Error).message);
    }
  }

  /**
   * Handle help command
   */
  private async handleHelp(args: string[]): Promise<void> {
    const commandName = args[0];

    if (commandName) {
      const command = this.commands.get(commandName);
      if (command) {
        console.log(`\n${command.name}: ${command.description}`);
        console.log(`Usage: ${command.usage}`);
        if (command.aliases && command.aliases.length > 0) {
          console.log(`Aliases: ${command.aliases.join(', ')}`);
        }
        console.log();
      } else {
        console.log(`Unknown command: ${commandName}`);
      }
    } else {
      console.log('\n📚 Available Commands:\n');
      
      const uniqueCommands = new Map<string, Command>();
      this.commands.forEach((cmd, name) => {
        if (name === cmd.name) {
          uniqueCommands.set(name, cmd);
        }
      });

      uniqueCommands.forEach(cmd => {
        const aliases = cmd.aliases ? ` (${cmd.aliases.join(', ')})` : '';
        console.log(`  ${cmd.name}${aliases}`);
        console.log(`    ${cmd.description}`);
      });

      console.log('\nType "help <command>" for detailed usage\n');
    }
  }

  /**
   * Handle exit command
   */
  private async handleExit(args: string[]): Promise<void> {
    console.log('👋 Goodbye!');
    this.stop();
    process.exit(0);
  }

  /**
   * Handle clear command
   */
  private async handleClear(args: string[]): Promise<void> {
    console.clear();
  }

  /**
   * Handle history command
   */
  private async handleHistory(args: string[]): Promise<void> {
    const count = args[0] ? parseInt(args[0]) : this.commandHistory.length;
    const history = this.commandHistory.slice(-count);

    console.log('\n📜 Command History:\n');
    history.forEach((cmd, index) => {
      console.log(`  ${index + 1}. ${cmd}`);
    });
    console.log();
  }
}

// Export singleton instance
export const cli = new CLI();

// Example usage:
// cli.start(); // Start interactive mode
// await cli.parseCommand('status'); // Execute single command
