// VY-NEXUS CONTROLLER - NEURAL BRIDGE (ViewModel)
// Handles networking to Dual-Stack Intelligence Engine

import SwiftUI
import Combine

@MainActor
class NexusViewModel: ObservableObject {
    // MARK: - Published State
    @Published var messages: [Message] = []
    @Published var currentMode: AgentMode = .architect
    @Published var isThinking: Bool = false
    @Published var systemStatus: SystemStatus = SystemStatus()
    @Published var errorMessage: String?
    
    // MARK: - Configuration
    // NOTE: Change to your Mac Mini's local IP if running on iPhone
    // e.g., "http://192.168.1.100:3000/engage"
    private let motiaURL = URL(string: "http://localhost:3000/engage")!
    private let loveURL = URL(string: "http://localhost:9001/love-chat")!
    
    // MARK: - Initialization
    init() {
        checkSystemStatus()
    }
    
    // MARK: - Public Methods
    func sendMessage(_ text: String) {
        guard !text.isEmpty else { return }
        
        // Add user message
        let userMsg = Message(text: text, isUser: true, mode: currentMode)
        messages.append(userMsg)
        
        // Clear any previous errors
        errorMessage = nil
        isThinking = true
        
        // Route to correct engine
        Task {
            switch currentMode {
            case .architect:
                await triggerMotia(goal: text)
            case .companion:
                await triggerLoveEngine(prompt: text)
            }
        }
    }
    
    func checkSystemStatus() {
        Task {
            await checkMotiaHealth()
            await checkLoveHealth()
        }
    }
    
    func emergencyStop() {
        // I_NSSI Kill Switch
        // TODO: Implement /emergency-stop endpoint
        print("🚨 EMERGENCY STOP TRIGGERED")
        isThinking = false
        
        let stopMsg = Message(
            text: "⚠️ EMERGENCY STOP - All recursive processes halted",
            isUser: false
        )
        messages.append(stopMsg)
    }
    
    // MARK: - Private Methods
    
    /// Calls Motia Recursive Planner (Port 3000)
    private func triggerMotia(goal: String) async {
        var request = URLRequest(url: motiaURL)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 30
        
        do {
            let payload = EngageRequest(goal: goal)
            request.httpBody = try JSONEncoder().encode(payload)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            
            guard httpResponse.statusCode == 200 else {
                throw NetworkError.httpError(httpResponse.statusCode)
            }
            
            let result = try JSONDecoder().decode(EngageResponse.self, from: data)
            
            let botMsg = Message(
                text: "🏛️ PLAN ENGAGED:\n\(result.message)",
                isUser: false,
                mode: .architect
            )
            messages.append(botMsg)
            
            systemStatus.motiaOnline = true
            
        } catch {
            handleError(error, context: "Motia Recursive Agent")
        }
        
        isThinking = false
    }
    
    /// Calls Thermodynamic Love Engine (Port 9001)
    private func triggerLoveEngine(prompt: String) async {
        var request = URLRequest(url: loveURL)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 30
        
        do {
            let payload = LoveRequest(prompt: prompt)
            request.httpBody = try JSONEncoder().encode(payload)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            
            guard httpResponse.statusCode == 200 else {
                throw NetworkError.httpError(httpResponse.statusCode)
            }
            
            let result = try JSONDecoder().decode(LoveResponse.self, from: data)
            
            // Check safety score if available
            var responseText = result.response
            if let safetyScore = result.safety_score {
                responseText += "\n\n💚 Safety: \(Int(safetyScore * 100))%"
            }
            
            let botMsg = Message(
                text: responseText,
                isUser: false,
                mode: .companion
            )
            messages.append(botMsg)
            
            systemStatus.loveOnline = true
            
        } catch {
            handleError(error, context: "Love Engine")
        }
        
        isThinking = false
    }
    
    /// Check Motia health
    private func checkMotiaHealth() async {
        do {
            let (_, response) = try await URLSession.shared.data(from: motiaURL)
            if let httpResponse = response as? HTTPURLResponse {
                systemStatus.motiaOnline = (200...299).contains(httpResponse.statusCode)
            }
        } catch {
            systemStatus.motiaOnline = false
        }
    }
    
    /// Check Love Engine health
    private func checkLoveHealth() async {
        do {
            let (_, response) = try await URLSession.shared.data(from: loveURL)
            if let httpResponse = response as? HTTPURLResponse {
                systemStatus.loveOnline = (200...299).contains(httpResponse.statusCode)
            }
        } catch {
            systemStatus.loveOnline = false
        }
    }
    
    /// Handle networking errors
    private func handleError(_ error: Error, context: String) {
        let errorMsg: String
        
        if let networkError = error as? NetworkError {
            errorMsg = "❌ \(context) Error: \(networkError.localizedDescription)"
        } else {
            errorMsg = "❌ \(context) Error: \(error.localizedDescription)"
        }
        
        errorMessage = errorMsg
        
        let botMsg = Message(
            text: errorMsg,
            isUser: false
        )
        messages.append(botMsg)
    }
}

// MARK: - Network Errors
enum NetworkError: LocalizedError {
    case invalidResponse
    case httpError(Int)
    
    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid server response"
        case .httpError(let code):
            return "HTTP Error \(code)"
        }
    }
}
