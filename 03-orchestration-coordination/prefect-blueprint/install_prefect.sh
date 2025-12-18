#!/bin/bash

# Activate virtual environment and install Prefect 3
cd /Users/lordwilson/prefect-blueprint
source .venv/bin/activate
pip install -U prefect
prefect version
