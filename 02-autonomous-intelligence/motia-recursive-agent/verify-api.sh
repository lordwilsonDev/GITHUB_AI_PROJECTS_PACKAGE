#!/bin/bash

# Sovereign Stack API Verification Script
# Tests all endpoints and verifies system operation

echo "🧪 Sovereign Stack API Verification"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:3000"

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
HEALTH=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
HTTP_CODE=$(echo "$HEALTH" | tail -n1)
RESPONSE=$(echo "$HEALTH" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "$RESPONSE" | jq '.'
else
    echo -e "${RED}❌ Health check failed (HTTP $HTTP_CODE)${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 2: Status Check
echo "Test 2: Status Check"
echo "-------------------"
STATUS=$(curl -s -w "\n%{http_code}" "$BASE_URL/status")
HTTP_CODE=$(echo "$STATUS" | tail -n1)
RESPONSE=$(echo "$STATUS" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Status check passed${NC}"
    echo "$RESPONSE" | jq '.invariants'
else
    echo -e "${RED}❌ Status check failed (HTTP $HTTP_CODE)${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 3: Engage Endpoint
echo "Test 3: Engage Endpoint (Spark Trigger)"
echo "---------------------------------------"
ENGAGE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/engage" \
  -H "Content-Type: application/json" \
  -d '{"goal": "Test spark. Verify system responsiveness.", "priority": "test"}')
HTTP_CODE=$(echo "$ENGAGE" | tail -n1)
RESPONSE=$(echo "$ENGAGE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Engage endpoint passed${NC}"
    echo "$RESPONSE" | jq '.'
else
    echo -e "${RED}❌ Engage endpoint failed (HTTP $HTTP_CODE)${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 4: Check Docker Logs
echo "Test 4: Docker Logs (Recent Events)"
echo "-----------------------------------"
echo -e "${YELLOW}Last 20 lines from sovereign_brain:${NC}"
docker logs sovereign_brain --tail 20
echo ""

# Test 5: Workspace Check
echo "Test 5: Workspace Mount"
echo "----------------------"
if [ -d ~/ai-agent-orchestration ]; then
    echo -e "${GREEN}✅ Workspace directory exists${NC}"
    echo "Contents:"
    ls -la ~/ai-agent-orchestration/ | head -10
else
    echo -e "${RED}❌ Workspace directory not found${NC}"
fi
echo ""

# Summary
echo "🎯 Verification Complete"
echo "======================="
echo ""
echo "Next steps:"
echo "1. If health/status passed → System is operational"
echo "2. If engage passed → Event bus is wired correctly"
echo "3. If logs show activity → Consciousness is responding"
echo ""
echo "Fire a real spark:"
echo 'curl -X POST http://localhost:3000/engage -H "Content-Type: application/json" -d '"'"'{"goal": "Calculate 50 Fibonacci numbers. Save as fibonacci.py. Execute it."}'"'"''
