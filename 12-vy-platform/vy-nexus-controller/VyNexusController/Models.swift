// VY-NEXUS CONTROLLER - DATA MODELS
// Maps to Motia Recursive Agent (Port 3000) and Love Engine (Port 9001)

import Foundation

// MARK: - Motia Recursive Agent (Port 3000)
struct EngageRequest: Codable {
    let goal: String
}

struct EngageResponse: Codable {
    let ok: Bool
    let message: String
    let goal: String
}

// MARK: - Love Engine (Port 9001)
struct LoveRequest: Codable {
    let prompt: String
    let system_prompt: String
    let temperature: Double
    
    init(prompt: String, systemPrompt: String = "You are Vy, a sovereign intelligence.", temperature: Double = 0.7) {
        self.prompt = prompt
        self.system_prompt = systemPrompt
        self.temperature = temperature
    }
}

struct LoveResponse: Codable {
    let response: String
    let safety_score: Double?
}

// MARK: - Agent Modes
enum AgentMode: String, CaseIterable {
    case architect = "🏛️ Architect"
    case companion = "❤️ Companion"
    
    var description: String {
        switch self {
        case .architect:
            return "Logic & Planning (Motia)"
        case .companion:
            return "Empathy & Safety (Love)"
        }
    }
}

// MARK: - Message Model
struct Message: Identifiable {
    let id = UUID()
    let text: String
    let isUser: Bool
    let timestamp: Date
    let mode: AgentMode?
    
    init(text: String, isUser: Bool, mode: AgentMode? = nil) {
        self.text = text
        self.isUser = isUser
        self.timestamp = Date()
        self.mode = mode
    }
}

// MARK: - System Status
struct SystemStatus: Codable {
    var motiaOnline: Bool = false
    var loveOnline: Bool = false
    var vdr: Double = 0.0
    var uptime: TimeInterval = 0.0
    
    var isFullyOperational: Bool {
        motiaOnline && loveOnline
    }
}
