#!/bin/bash

# Redeploy production-etl with updated schedule
cd /Users/lordwilson/prefect-blueprint
source .venv/bin/activate
prefect deploy --name production-etl --no-prompt
