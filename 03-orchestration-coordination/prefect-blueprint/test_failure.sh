#!/bin/bash
# Task 3.7: Test failure handling with invalid params
# This tests the retry mechanism and Pydantic validation

cd /Users/lordwilson/prefect-blueprint
source .venv/bin/activate

echo "Testing failure handling with invalid source_url..."
echo "This should trigger connection errors and demonstrate retry mechanism"
echo ""

prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param source_url="invalid://url"

echo ""
echo "Deployment triggered with invalid URL. Check UI for retry behavior."
echo "Expected: Task will fail, retry 3 times with 2-second delays, then mark as Failed."
