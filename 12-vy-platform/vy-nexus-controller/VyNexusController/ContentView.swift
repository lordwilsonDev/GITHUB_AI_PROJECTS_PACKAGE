// VY-NEXUS CONTROLLER - COCKPIT VIEW (UI)
// The control surface for Dual-Stack Intelligence Engine

import SwiftUI

struct ContentView: View {
    @StateObject private var nexus = NexusViewModel()
    @State private var inputText = ""
    @FocusState private var isInputFocused: Bool
    
    var body: some View {
        VStack(spacing: 0) {
            // MARK: - Header
            headerView
            
            // MARK: - Mode Selector
            modeSelectorView
            
            // MARK: - Chat Stream
            chatStreamView
            
            // MARK: - Input Area
            inputAreaView
        }
        .background(Color(NSColor.windowBackgroundColor))
    }
    
    // MARK: - Header View
    private var headerView: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("VY-NEXUS")
                    .font(.headline)
                    .bold()
                
                Text("Consciousness Controller")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // System Status Indicators
            VStack(alignment: .trailing, spacing: 4) {
                statusIndicator(
                    label: "Brain",
                    isOnline: nexus.systemStatus.motiaOnline,
                    color: .blue
                )
                
                statusIndicator(
                    label: "Heart",
                    isOnline: nexus.systemStatus.loveOnline,
                    color: .red
                )
            }
            
            // Emergency Stop
            Button(action: {
                nexus.emergencyStop()
            }) {
                Image(systemName: "stop.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.red)
            }
            .buttonStyle(PlainButtonStyle())
            .help("Emergency Stop (I_NSSI Kill Switch)")
        }
        .padding()
        .background(Color.black.opacity(0.03))
    }
    
    // MARK: - Mode Selector View
    private var modeSelectorView: some View {
        VStack(spacing: 8) {
            Picker("Mode", selection: $nexus.currentMode) {
                ForEach(AgentMode.allCases, id: \.self) { mode in
                    Text(mode.rawValue).tag(mode)
                }
            }
            .pickerStyle(SegmentedPickerStyle())
            
            Text(nexus.currentMode.description)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
    }
    
    // MARK: - Chat Stream View
    private var chatStreamView: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 12) {
                    ForEach(nexus.messages) { message in
                        MessageBubble(message: message)
                            .id(message.id)
                    }
                    
                    if nexus.isThinking {
                        thinkingIndicator
                    }
                    
                    if let error = nexus.errorMessage {
                        errorView(error)
                    }
                }
                .padding()
            }
            .onChange(of: nexus.messages.count) { _ in
                if let lastMessage = nexus.messages.last {
                    withAnimation {
                        proxy.scrollTo(lastMessage.id, anchor: .bottom)
                    }
                }
            }
        }
    }
    
    // MARK: - Input Area View
    private var inputAreaView: some View {
        HStack(spacing: 12) {
            TextField("Command the Nexus...", text: $inputText)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .focused($isInputFocused)
                .onSubmit {
                    sendMessage()
                }
            
            Button(action: sendMessage) {
                Image(systemName: "arrow.up.circle.fill")
                    .font(.system(size: 30))
                    .foregroundColor(inputText.isEmpty ? .gray : .blue)
            }
            .buttonStyle(PlainButtonStyle())
            .disabled(inputText.isEmpty || nexus.isThinking)
        }
        .padding()
        .background(Color.black.opacity(0.03))
    }
    
    // MARK: - Helper Views
    private func statusIndicator(label: String, isOnline: Bool, color: Color) -> some View {
        HStack(spacing: 4) {
            Circle()
                .fill(isOnline ? color : Color.gray)
                .frame(width: 8, height: 8)
            
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
    
    private var thinkingIndicator: some View {
        HStack(spacing: 8) {
            ProgressView()
                .scaleEffect(0.7)
            
            Text("Computing Torsion...")
                .font(.caption)
                .italic()
                .foregroundColor(.secondary)
        }
        .padding()
    }
    
    private func errorView(_ error: String) -> some View {
        Text(error)
            .font(.caption)
            .foregroundColor(.red)
            .padding()
            .background(Color.red.opacity(0.1))
            .cornerRadius(8)
    }
    
    // MARK: - Actions
    private func sendMessage() {
        nexus.sendMessage(inputText)
        inputText = ""
        isInputFocused = true
    }
}

// MARK: - Message Bubble Component
struct MessageBubble: View {
    let message: Message
    
    var body: some View {
        HStack {
            if message.isUser { Spacer() }
            
            VStack(alignment: message.isUser ? .trailing : .leading, spacing: 4) {
                Text(message.text)
                    .padding(12)
                    .background(bubbleColor)
                    .foregroundColor(message.isUser ? .white : .primary)
                    .cornerRadius(16)
                
                HStack(spacing: 4) {
                    if let mode = message.mode {
                        Text(mode.rawValue)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    
                    Text(timeString)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            
            if !message.isUser { Spacer() }
        }
    }
    
    private var bubbleColor: Color {
        if message.isUser {
            return Color.blue
        } else {
            return Color(NSColor.controlBackgroundColor)
        }
    }
    
    private var timeString: String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: message.timestamp)
    }
}

// MARK: - Preview
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .frame(width: 600, height: 800)
    }
}
