#!/bin/bash
# Shortcut: Smart Screenshot
# ID: shortcut_2_20251215_222527
# Generated: 2025-12-15T22:25:27.405220

# Log usage
echo "$(date -Iseconds),shortcut_2_20251215_222527,Smart Screenshot" >> ~/vy-nexus/logs/shortcut_usage.log

# Execute command
screencapture -i ~/Desktop/screenshot_$(date +%Y%m%d_%H%M%S).png
