#!/bin/bash
# VY-NEXUS Controller - Backend Health Check
# Verifies that Motia and Love Engine are running

set -e

echo "🔍 Checking VY-NEXUS Backend Status..."
echo ""

# Check Motia (port 3000)
echo "Checking Motia Recursive Agent (port 3000)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/engage | grep -q "200\|404\|405"; then
  echo "  ✅ Motia is ONLINE"
  MOTIA_STATUS="ONLINE"
else
  echo "  ❌ Motia is OFFLINE"
  MOTIA_STATUS="OFFLINE"
fi

echo ""

# Check Love Engine (port 9001)
echo "Checking Love Engine (port 9001)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:9001/love-chat | grep -q "200\|404\|405"; then
  echo "  ✅ Love Engine is ONLINE"
  LOVE_STATUS="ONLINE"
else
  echo "  ❌ Love Engine is OFFLINE"
  LOVE_STATUS="OFFLINE"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "BACKEND STATUS SUMMARY:"
echo "  Motia (Brain):  $MOTIA_STATUS"
echo "  Love (Heart):   $LOVE_STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$MOTIA_STATUS" = "OFFLINE" ] || [ "$LOVE_STATUS" = "OFFLINE" ]; then
  echo "⚠️  WARNING: Some services are offline!"
  echo ""
  echo "To start missing services:"
  if [ "$MOTIA_STATUS" = "OFFLINE" ]; then
    echo "  Motia: cd ~/motia-recursive-agent && npm start"
  fi
  if [ "$LOVE_STATUS" = "OFFLINE" ]; then
    echo "  Love:  cd ~/love-engine-zfc && python3 server.py"
  fi
  echo ""
  exit 1
else
  echo "✅ All systems operational!"
  echo "   Ready to launch VY-NEXUS Controller."
  echo ""
  exit 0
fi
