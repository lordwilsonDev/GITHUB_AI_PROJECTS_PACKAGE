#!/usr/bin/env python3
"""
Direct Genesis Block Generation
Executes the genesis creation and saves output
"""

import sys
import os

# Change to vy-nexus directory
os.chdir('/Users/lordwilson/vy-nexus')

# Import and execute the genesis creation
exec(open('create_genesis_block.py').read())
