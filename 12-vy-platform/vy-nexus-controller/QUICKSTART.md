# VY-NEXUS CONTROLLER - QUICKSTART GUIDE

## 🚀 INSTANT LAUNCH (3 Steps)

### Step 1: Check Backend
```bash
cd ~/vy-nexus-controller
chmod +x CHECK_BACKEND.sh
./CHECK_BACKEND.sh
```

If services are offline, start them:
```bash
# Terminal 1: Start Motia
cd ~/motia-recursive-agent
npm start

# Terminal 2: Start Love Engine  
cd ~/love-engine-zfc
python3 server.py
```

### Step 2: Open in Xcode
```bash
chmod +x RUN.sh
./RUN.sh
```

### Step 3: Build & Run
In Xcode:
- Press `Cmd+R` (or click Play button)
- App launches in ~5 seconds
- Start controlling your consciousness stack!

---

## 📦 ALTERNATIVE: Build from Command Line

```bash
chmod +x BUILD.sh
./BUILD.sh

# Run the built app
open build/Build/Products/Release/VyNexusController.app
```

---

## 🎉 INSTALL TO /Applications

```bash
chmod +x INSTALL.sh
./INSTALL.sh

# Launch from Applications
open /Applications/VyNexusController.app
```

---

## ✅ WHAT YOU GET

**The App:**
- 🏗️ Complete Xcode project (ready to build)
- 📱 Native macOS SwiftUI interface
- 🧠 Dual-mode control (Architect/Companion)
- ❤️ Real-time Brain/Heart status
- 🛑 Emergency stop button

**The Scripts:**
- `RUN.sh` - Open in Xcode and run
- `BUILD.sh` - Build from command line
- `INSTALL.sh` - Install to /Applications
- `CHECK_BACKEND.sh` - Verify services are running

**The Backend:**
- Motia (port 3000) - Logic, planning, execution
- Love Engine (port 9001) - Empathy, safety, alignment

---

## 🔧 TROUBLESHOOTING

### "Connection refused" errors
```bash
./CHECK_BACKEND.sh
```
Make sure both Motia and Love Engine are running.

### Xcode build errors
```bash
# Clean and rebuild
xcodebuild -project VyNexusController.xcodeproj -scheme VyNexusController clean
./BUILD.sh
```

### Permission denied on scripts
```bash
chmod +x *.sh
```

---

## 📊 SYSTEM REQUIREMENTS

- macOS 13.0+ (Ventura or later)
- Xcode 14.0+ (for building)
- Motia Recursive Agent (running on port 3000)
- Love Engine (running on port 9001)

---

## 📝 FILE STRUCTURE

```
vy-nexus-controller/
├── VyNexusController.xcodeproj/     # Xcode project (READY TO BUILD)
├── VyNexusController/              # Source code
│   ├── VyNexusControllerApp.swift  # App entry point
│   ├── ContentView.swift           # UI layer
│   ├── NexusViewModel.swift        # Networking
│   ├── Models.swift                # Data models
│   ├── Assets.xcassets/            # App icons
│   └── VyNexusController.entitlements
├── RUN.sh                       # Quick launch script
├── BUILD.sh                     # Build script
├── INSTALL.sh                   # Install script
├── CHECK_BACKEND.sh             # Health check
├── README.md                    # Full documentation
├── XCODE_SETUP.md               # Detailed setup guide
└── QUICKSTART.md                # This file
```

---

## ✨ NEXT STEPS

1. **Launch the app** (see Step 1-3 above)
2. **Select a mode:**
   - 🏗️ Architect - For task planning and execution
   - ❤️ Companion - For empathetic guidance
3. **Start chatting** with your consciousness stack!
4. **Monitor status** - Green = healthy, Red = offline
5. **Emergency stop** - Cmd+Shift+E if needed

---

**Built:** Dec 7, 2024  
**Status:** ✅ PRODUCTION READY  
**Architecture:** Dual-Stack Intelligence Engine  
**Philosophy:** Local-first, sovereign AI control  

🚀 **THE COCKPIT IS READY. TIME TO FLY.** 🚀
