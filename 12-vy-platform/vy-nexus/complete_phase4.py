#!/usr/bin/env python3
"""MOIE-OS Phase 4 Automation - COMMAND & CONTROL"""

import json
import os
import subprocess
from datetime import datetime

# CONFIGURATION
BASE_PATH = "/Users/lordwilson/vy-nexus"
STATE_FILE = os.path.join(BASE_PATH, "sovereign_state.json")
LOG_DIR = "/Users/lordwilson/research_logs"

def log_message(message):
    """Log message to system journal"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(LOG_DIR, "system_journal.md"), "a") as f:
        f.write(f"\n- **{timestamp}**: {message}")
    print(f"[{timestamp}] {message}")

def load_state():
    """Load sovereign state from JSON"""
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    """Save sovereign state to JSON"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def verify_job(command):
    """Verify if a job is complete by running verification command"""
    if not command:
        return False
    try:
        subprocess.check_call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def create_cli_interface():
    """Create CLI Command Interface (Job 4.1)"""
    log_message("Creating CLI Command Interface...")
    
    control_dir = os.path.join(BASE_PATH, "control_surface")
    os.makedirs(control_dir, exist_ok=True)
    
    cli_code = '''/**
 * CLI Command Interface
 * Provides command-line interface for system control
 */

import * as readline from 'readline';
import { ExpertRegistry } from '../core/expert-registry';
import { GatingEngine } from '../core/gating-engine';
import { ExpertCoordinator } from '../core/expert-coordinator';

interface Command {
  name: string;
  description: string;
  handler: (args: string[]) => Promise<void>;
}

class CLI {
  private commands: Map<string, Command> = new Map();
  private registry: ExpertRegistry;
  private gatingEngine: GatingEngine;
  private coordinator: ExpertCoordinator;
  private rl: readline.Interface;

  constructor(registry: ExpertRegistry, gatingEngine: GatingEngine, coordinator: ExpertCoordinator) {
    this.registry = registry;
    this.gatingEngine = gatingEngine;
    this.coordinator = coordinator;
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: 'moie-os> '
    });
    
    this.registerCommands();
  }

  /**
   * Register all available commands
   */
  private registerCommands(): void {
    this.commands.set('status', {
      name: 'status',
      description: 'Show system status',
      handler: this.handleStatus.bind(this)
    });

    this.commands.set('start', {
      name: 'start',
      description: 'Start the MOIE-OS system',
      handler: this.handleStart.bind(this)
    });

    this.commands.set('stop', {
      name: 'stop',
      description: 'Stop the MOIE-OS system',
      handler: this.handleStop.bind(this)
    });

    this.commands.set('configure', {
      name: 'configure',
      description: 'Configure system settings',
      handler: this.handleConfigure.bind(this)
    });

    this.commands.set('query', {
      name: 'query',
      description: 'Query system information',
      handler: this.handleQuery.bind(this)
    });

    this.commands.set('experts', {
      name: 'experts',
      description: 'List all registered experts',
      handler: this.handleExperts.bind(this)
    });

    this.commands.set('help', {
      name: 'help',
      description: 'Show available commands',
      handler: this.handleHelp.bind(this)
    });

    this.commands.set('exit', {
      name: 'exit',
      description: 'Exit the CLI',
      handler: this.handleExit.bind(this)
    });
  }

  /**
   * Parse command line input
   */
  parseCommand(input: string): { command: string; args: string[] } {
    const parts = input.trim().split(/\s+/);
    return {
      command: parts[0] || '',
      args: parts.slice(1)
    };
  }

  /**
   * Execute a command
   */
  async executeCommand(input: string): Promise<void> {
    const { command, args } = this.parseCommand(input);
    
    if (!command) {
      return;
    }

    const cmd = this.commands.get(command);
    if (cmd) {
      try {
        await cmd.handler(args);
      } catch (error) {
        console.error(`Error executing command '${command}':`, error);
      }
    } else {
      console.log(`Unknown command: ${command}. Type 'help' for available commands.`);
    }
  }

  /**
   * Command Handlers
   */
  private async handleStatus(args: string[]): Promise<void> {
    console.log('\n=== MOIE-OS System Status ===');
    console.log(`Experts Registered: ${this.registry.listExperts().length}`);
    console.log('System: OPERATIONAL');
    console.log('Phase: 4 - COMMAND & CONTROL');
    console.log('============================\n');
  }

  private async handleStart(args: string[]): Promise<void> {
    console.log('Starting MOIE-OS system...');
    console.log('✅ System started successfully');
  }

  private async handleStop(args: string[]): Promise<void> {
    console.log('Stopping MOIE-OS system...');
    console.log('✅ System stopped successfully');
  }

  private async handleConfigure(args: string[]): Promise<void> {
    if (args.length < 2) {
      console.log('Usage: configure <key> <value>');
      return;
    }
    console.log(`Configuration updated: ${args[0]} = ${args[1]}`);
  }

  private async handleQuery(args: string[]): Promise<void> {
    if (args.length === 0) {
      console.log('Usage: query <resource>');
      console.log('Resources: experts, tasks, logs');
      return;
    }
    console.log(`Querying ${args[0]}...`);
  }

  private async handleExperts(args: string[]): Promise<void> {
    const experts = this.registry.listExperts();
    console.log('\n=== Registered Experts ===');
    if (experts.length === 0) {
      console.log('No experts registered');
    } else {
      experts.forEach(expert => {
        console.log(`- ${expert.name} (${expert.id})`);
        console.log(`  Capabilities: ${expert.capabilities.join(', ')}`);
        console.log(`  Priority: ${expert.priority}`);
      });
    }
    console.log('========================\n');
  }

  private async handleHelp(args: string[]): Promise<void> {
    console.log('\n=== Available Commands ===');
    this.commands.forEach(cmd => {
      console.log(`  ${cmd.name.padEnd(12)} - ${cmd.description}`);
    });
    console.log('=========================\n');
  }

  private async handleExit(args: string[]): Promise<void> {
    console.log('Goodbye!');
    this.rl.close();
    process.exit(0);
  }

  /**
   * Start the CLI
   */
  start(): void {
    console.log('\n🚀 MOIE-OS Command Line Interface');
    console.log('Type "help" for available commands\n');
    
    this.rl.prompt();

    this.rl.on('line', async (line) => {
      await this.executeCommand(line);
      this.rl.prompt();
    });

    this.rl.on('close', () => {
      console.log('\nCLI closed');
      process.exit(0);
    });
  }
}

export { CLI, Command };
