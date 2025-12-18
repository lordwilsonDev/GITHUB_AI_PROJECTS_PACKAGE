/**
 * Standardized Breakthrough Question Template
 * Used for consistent automated breakthrough search across OSS repositories
 */

export interface BreakthroughQuestion {
  id: string
  question: string
  context: string
  expectedOutputFormat: string
  vdrFocus: string
}

/**
 * Standard breakthrough questions for different repository types
 */
export const BREAKTHROUGH_QUESTIONS = {
  /**
   * Universal breakthrough question - works for any codebase
   */
  UNIVERSAL: {
    id: 'universal_breakthrough',
    question: 'Find one change that increases function while reducing complexity. Propose it and explain why VDR improves.',
    context: 'Analyze the codebase to identify opportunities where a single change can both add functionality and reduce complexity. Focus on areas with redundancy, over-engineering, or unclear abstractions.',
    expectedOutputFormat: 'Specific change proposal with before/after VDR calculations and implementation steps.',
    vdrFocus: 'Maximize Vitality (functional improvement) while minimizing Density (complexity increase)'
  },

  /**
   * CLI tool specific breakthrough question
   */
  CLI_TOOL: {
    id: 'cli_breakthrough',
    question: 'Identify a command or feature that can be simplified while adding user value. Propose the change and calculate VDR improvement.',
    context: 'Focus on CLI interface design, command structure, argument parsing, and user experience. Look for opportunities to consolidate commands or improve usability.',
    expectedOutputFormat: 'CLI improvement proposal with user experience benefits and complexity reduction metrics.',
    vdrFocus: 'Improve user experience (Vitality) while reducing interface complexity (Density)'
  },

  /**
   * Agent framework specific breakthrough question
   */
  AGENT_FRAMEWORK: {
    id: 'agent_breakthrough',
    question: 'Find an agent capability that can be enhanced while simplifying the underlying architecture. Propose the change with VDR analysis.',
    context: 'Examine agent reasoning, tool integration, memory management, and execution patterns. Look for architectural improvements that enhance capabilities.',
    expectedOutputFormat: 'Agent enhancement proposal with capability improvements and architectural simplification.',
    vdrFocus: 'Enhance agent capabilities (Vitality) while reducing architectural complexity (Density)'
  },

  /**
   * Library/framework specific breakthrough question
   */
  LIBRARY: {
    id: 'library_breakthrough',
    question: 'Identify an API or feature that can be made more powerful while simplifying the interface. Propose the change and show VDR gains.',
    context: 'Focus on API design, developer experience, feature composition, and library architecture. Look for opportunities to improve the public interface.',
    expectedOutputFormat: 'API improvement proposal with developer experience benefits and interface simplification.',
    vdrFocus: 'Improve API power and usability (Vitality) while reducing interface complexity (Density)'
  },

  /**
   * Configuration/setup specific breakthrough question
   */
  CONFIG: {
    id: 'config_breakthrough',
    question: 'Find a configuration or setup process that can be automated while reducing complexity. Propose the change with VDR metrics.',
    context: 'Examine configuration files, setup processes, build systems, and deployment workflows. Look for automation opportunities.',
    expectedOutputFormat: 'Configuration improvement proposal with automation benefits and setup simplification.',
    vdrFocus: 'Automate manual processes (Vitality) while reducing configuration complexity (Density)'
  }
}

/**
 * Breakthrough Question Template Engine
 */
export class BreakthroughQuestionTemplate {
  /**
   * Get question by repository type
   */
  static getQuestionByType(repoType: 'cli' | 'agent' | 'library' | 'config' | 'universal'): BreakthroughQuestion {
    switch (repoType) {
      case 'cli':
        return BREAKTHROUGH_QUESTIONS.CLI_TOOL
      case 'agent':
        return BREAKTHROUGH_QUESTIONS.AGENT_FRAMEWORK
      case 'library':
        return BREAKTHROUGH_QUESTIONS.LIBRARY
      case 'config':
        return BREAKTHROUGH_QUESTIONS.CONFIG
      default:
        return BREAKTHROUGH_QUESTIONS.UNIVERSAL
    }
  }

  /**
   * Auto-detect repository type from structure and content
   */
  static detectRepositoryType(repoStructure: {
    hasCliCommands?: boolean
    hasAgentFramework?: boolean
    hasPublicAPI?: boolean
    hasConfigFiles?: boolean
    packageJson?: any
    readme?: string
  }): 'cli' | 'agent' | 'library' | 'config' | 'universal' {
    // Check for CLI indicators
    if (repoStructure.hasCliCommands || 
        repoStructure.packageJson?.bin ||
        repoStructure.readme?.toLowerCase().includes('command line')) {
      return 'cli'
    }

    // Check for agent framework indicators
    if (repoStructure.hasAgentFramework ||
        repoStructure.readme?.toLowerCase().includes('agent') ||
        repoStructure.readme?.toLowerCase().includes('llm') ||
        repoStructure.readme?.toLowerCase().includes('ai assistant')) {
      return 'agent'
    }

    // Check for library indicators
    if (repoStructure.hasPublicAPI ||
        repoStructure.packageJson?.main ||
        repoStructure.readme?.toLowerCase().includes('library') ||
        repoStructure.readme?.toLowerCase().includes('framework')) {
      return 'library'
    }

    // Check for config-heavy repositories
    if (repoStructure.hasConfigFiles ||
        repoStructure.readme?.toLowerCase().includes('configuration') ||
        repoStructure.readme?.toLowerCase().includes('setup')) {
      return 'config'
    }

    // Default to universal
    return 'universal'
  }

  /**
   * Generate contextual breakthrough question
   */
  static generateContextualQuestion(
    repoType: 'cli' | 'agent' | 'library' | 'config' | 'universal',
    repoName: string,
    specificContext?: string
  ): BreakthroughQuestion {
    const baseQuestion = this.getQuestionByType(repoType)
    
    return {
      ...baseQuestion,
      question: `For ${repoName}: ${baseQuestion.question}`,
      context: specificContext ? `${baseQuestion.context}

Specific context: ${specificContext}` : baseQuestion.context
    }
  }

  /**
   * Validate breakthrough question format
   */
  static validateQuestion(question: BreakthroughQuestion): boolean {
    return !!(
      question.id &&
      question.question &&
      question.context &&
      question.expectedOutputFormat &&
      question.vdrFocus
    )
  }

  /**
   * Get all available question types
   */
  static getAllQuestionTypes(): string[] {
    return Object.keys(BREAKTHROUGH_QUESTIONS)
  }
}
