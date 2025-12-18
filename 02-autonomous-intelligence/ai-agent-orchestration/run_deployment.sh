#!/bin/bash
cd /Users/lordwilson/ai-agent-orchestration
chmod +x EXECUTE_DEPLOYMENT.sh
./EXECUTE_DEPLOYMENT.sh 2>&1 | tee deployment_output.log
