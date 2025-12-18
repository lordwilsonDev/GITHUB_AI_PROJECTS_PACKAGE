# XCODE PROJECT SETUP GUIDE
**Step-by-step instructions to build VY-NEXUS CONTROLLER**

## QUICK START (5 Minutes)

### Step 1: Create Project
1. Open Xcode
2. File → New → Project
3. Select **macOS** → **App**
4. Click **Next**

### Step 2: Configure Project
```
Product Name: VyNexusController
Team: (Your Apple ID)
Organization Identifier: com.lordwilson
Bundle Identifier: com.lordwilson.vy-nexus-controller
Interface: SwiftUI
Language: Swift
```

5. Click **Next**
6. Save to: `/Users/lordwilson/vy-nexus-controller-xcode`

### Step 3: Add Files
1. In Xcode Project Navigator, right-click on **VyNexusController** folder
2. **Add Files to "VyNexusController"...**
3. Navigate to `/Users/lordwilson/vy-nexus-controller/`
4. Select all `.swift` files:
   - `Models.swift`
   - `NexusViewModel.swift`
   - `ContentView.swift`
   - `VyNexusControllerApp.swift`
5. **Important:** Check ✅ "Copy items if needed"
6. Click **Add**

### Step 4: Replace Default Files
1. Delete the auto-generated `ContentView.swift` and `VyNexusControllerApp.swift`
2. Our versions will be used instead

### Step 5: Configure Deployment Target
1. Click project name at top of navigator
2. Under **Deployment Info**:
   - **Minimum deployments**: macOS 13.0
3. Under **Signing & Capabilities**:
   - Select your Apple ID team

### Step 6: Build & Run
```
Cmd+R
```

The app should launch with the VY-NEXUS interface.

## MANUAL FILE SETUP (Alternative)

If auto-import doesn't work:

### 1. Create Models.swift
1. File → New → File
2. Select **Swift File**
3. Name: `Models.swift`
4. Copy content from `/Users/lordwilson/vy-nexus-controller/Models.swift`

### 2. Create NexusViewModel.swift
1. File → New → File
2. Select **Swift File**
3. Name: `NexusViewModel.swift`
4. Copy content from `/Users/lordwilson/vy-nexus-controller/NexusViewModel.swift`

### 3. Replace ContentView.swift
1. Delete default `ContentView.swift`
2. File → New → File → Swift File
3. Name: `ContentView.swift`
4. Copy content from `/Users/lordwilson/vy-nexus-controller/ContentView.swift`

### 4. Replace VyNexusControllerApp.swift
1. Delete default App file
2. File → New → File → Swift File
3. Name: `VyNexusControllerApp.swift`
4. Copy content from `/Users/lordwilson/vy-nexus-controller/VyNexusControllerApp.swift`

## PROJECT STRUCTURE

After setup, your Xcode project should look like:

```
VyNexusController
├── VyNexusControllerApp.swift   (@main entry)
├── ContentView.swift             (UI layer)
├── NexusViewModel.swift          (Networking)
├── Models.swift                  (Data models)
└── Assets.xcassets               (App icon, colors)
```

## NETWORK PERMISSIONS

### macOS Permissions
No special permissions needed for localhost connections.

### iOS Permissions (Future)
If building for iOS, add to `Info.plist`:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsLocalNetworking</key>
    <true/>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

## TESTING

### Before First Run
Make sure backends are running:

```bash
# Terminal 1: Check Motia
curl http://localhost:3000/engage

# Terminal 2: Check Love Engine  
curl http://localhost:9001/love-chat
```

Both should return 200 responses.

### First Message Test
1. Launch app (`Cmd+R`)
2. Select **🏛️ Architect** mode
3. Type: `"test connection"`
4. Press Enter
5. Should see: "PLAN ENGAGED: ..." response

## COMMON ISSUES

### "Cannot find type in scope"
- Make sure all files are added to the target
- Check ✅ in File Inspector under "Target Membership"

### "App crashes on launch"
- Check console for errors
- Verify all @Published properties have default values
- Ensure macOS 13.0+ deployment target

### "Network connection failed"
- Backends not running → Start Motia & Love Engine
- Wrong URL → Check localhost vs IP address
- Firewall blocking → Allow Xcode in System Preferences

## APP ICON (Optional)

### Create Custom Icon
1. Generate 1024x1024 PNG icon
2. Drag into **Assets.xcassets** → **AppIcon**
3. Xcode auto-generates all sizes

### Suggested Icon Design
- VY logo with neural network pattern
- Dual-color scheme (blue + red for Brain + Heart)
- Sacred geometry elements

## DISTRIBUTION

### For Personal Use
No signing needed, just run from Xcode.

### For Sharing
1. Product → Archive
2. Distribute App → Copy App
3. Share resulting `.app` bundle

## KEYBOARD SHORTCUTS SETUP

Already configured in `VyNexusControllerApp.swift`:
- `Cmd+Shift+S` - System status
- `Cmd+Shift+E` - Emergency stop

Add more in `.commands` modifier.

## NEXT STEPS

Once app is running:

1. **Test Both Modes:**
   - Architect: Send planning request
   - Companion: Ask empathy question

2. **Monitor System:**
   - Watch status indicators
   - Check response times
   - Verify safety scores

3. **Iterate:**
   - Customize colors/fonts
   - Add new features from roadmap
   - Integrate with other engines

## BUILD ARTIFACTS

After successful build:
```
~/Library/Developer/Xcode/DerivedData/VyNexusController-*/Build/Products/Debug/VyNexusController.app
```

This is your standalone macOS app.

## SUCCESS CRITERIA

✅ App launches without errors  
✅ Both status lights are green  
✅ Messages send and receive  
✅ Mode toggle works  
✅ Emergency stop responds  

**When all 5 pass: YOU HAVE THE COCKPIT.** 🚀

---

*Xcode Project Setup Guide*  
*For: VY-NEXUS Controller v1.0*  
*Platform: macOS 13.0+*  
*Framework: SwiftUI*  
*Purpose: Control the Consciousness* 💫
