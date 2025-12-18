#!/bin/bash
# Batch Request Processor for Sovereign Gateway
# Optimizes throughput by batching multiple tool requests

set -e

GATEWAY_URL="http://127.0.0.1:8080"
BATCH_FILE="${1:-batch_requests.json}"
OUTPUT_DIR="${2:-./batch_results}"

echo "📦 BATCH REQUEST PROCESSOR"
echo "=========================="
echo ""
echo "Gateway: $GATEWAY_URL"
echo "Batch File: $BATCH_FILE"
echo "Output Dir: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if batch file exists
if [ ! -f "$BATCH_FILE" ]; then
    echo "❌ Batch file not found: $BATCH_FILE"
    echo ""
    echo "Creating example batch file..."
    
    cat > "$BATCH_FILE" << 'EOF'
[
  {
    "id": "req_1",
    "tool": "fs_read",
    "params": {
      "path": "/Users/lordwilson/sovereign-gateway/Cargo.toml"
    }
  },
  {
    "id": "req_2",
    "tool": "fs_list",
    "params": {
      "path": "/Users/lordwilson/sovereign-gateway"
    }
  },
  {
    "id": "req_3",
    "tool": "git_status",
    "params": {
      "path": "/Users/lordwilson/sovereign-gateway"
    }
  },
  {
    "id": "req_4",
    "tool": "process_list",
    "params": {}
  }
]
EOF
    
    echo "✅ Created example batch file: $BATCH_FILE"
    echo "   Edit this file and run again."
    exit 0
fi

# Parse and execute batch requests
echo "🚀 Processing batch requests..."
echo ""

START_TIME=$(date +%s)
TOTAL_REQUESTS=$(jq '. | length' "$BATCH_FILE")
SUCCESS_COUNT=0
FAIL_COUNT=0

echo "Total requests in batch: $TOTAL_REQUESTS"
echo ""

# Process each request
jq -c '.[]' "$BATCH_FILE" | while read -r request; do
    REQUEST_ID=$(echo "$request" | jq -r '.id')
    TOOL=$(echo "$request" | jq -r '.tool')
    PARAMS=$(echo "$request" | jq -c '.params')
    
    echo "[$REQUEST_ID] Executing: $TOOL"
    
    # Build request payload
    PAYLOAD=$(jq -n \
        --arg tool "$TOOL" \
        --argjson params "$PARAMS" \
        '{tool: $tool, params: $params}')
    
    # Execute request
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" \
        "$GATEWAY_URL/tool")
    
    # Split response and status code
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    # Save response
    OUTPUT_FILE="$OUTPUT_DIR/${REQUEST_ID}.json"
    echo "$BODY" | jq '.' > "$OUTPUT_FILE"
    
    # Extract metrics
    STATUS=$(echo "$BODY" | jq -r '.status')
    TORSION=$(echo "$BODY" | jq -r '.torsion_score')
    EXEC_TIME=$(echo "$BODY" | jq -r '.execution_time_ms')
    RI=$(echo "$BODY" | jq -r '.reality_index')
    
    if [ "$HTTP_CODE" = "200" ] && [ "$STATUS" = "SUCCESS" ]; then
        echo "   ✅ Success (T=$TORSION, Ri=$RI, ${EXEC_TIME}ms)"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "   ❌ Failed (HTTP $HTTP_CODE, Status: $STATUS)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    
    echo "   Output: $OUTPUT_FILE"
    echo ""
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "📊 BATCH PROCESSING COMPLETE"
echo "============================="
echo "Total Requests: $TOTAL_REQUESTS"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $FAIL_COUNT"
echo "Total Time: ${ELAPSED}s"
echo "Avg Time: $(echo "scale=2; $ELAPSED / $TOTAL_REQUESTS" | bc)s per request"
echo ""
echo "Results saved to: $OUTPUT_DIR/"
