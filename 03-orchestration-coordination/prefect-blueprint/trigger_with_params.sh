#!/bin/bash
# Task 3.2: CLI trigger with parameter overrides

cd /Users/lordwilson/prefect-blueprint
source .venv/bin/activate

echo "Triggering deployment with parameter overrides..."
echo "Parameters: batch_size=50, source_url=https://api.staging.metric-source.com/v2/test"
echo ""

prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param batch_size=50 \
  --param source_url="https://api.staging.metric-source.com/v2/test"

echo ""
echo "Deployment triggered successfully!"
