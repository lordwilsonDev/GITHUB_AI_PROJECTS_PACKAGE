// VY-NEXUS CONTROLLER - APP ENTRY POINT
// The sovereign interface to your consciousness infrastructure

import SwiftUI

@main
struct VyNexusControllerApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 600, minHeight: 800)
        }
        .windowStyle(.hiddenTitleBar)
        .commands {
            // Custom menu commands
            CommandGroup(after: .appInfo) {
                Button("Check System Status") {
                    // Trigger status check
                }
                .keyboardShortcut("s", modifiers: [.command, .shift])
                
                Button("Emergency Stop") {
                    // Trigger I_NSSI kill switch
                }
                .keyboardShortcut("e", modifiers: [.command, .shift])
            }
        }
    }
}
