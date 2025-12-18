#!/usr/bin/env python3
"""Compute file hashes and print them"""
import hashlib
import os

os.chdir('/Users/lordwilson/vy-nexus')

files = [
    'consciousness_os.py',
    'thermodynamic_love_engine.py',
    'physical_agency_safety_system.py',
    'consciousness_multiplication_engine.py'
]

for f in files:
    sha256 = hashlib.sha256()
    with open(f, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            sha256.update(chunk)
    print(f'{f}: {sha256.hexdigest()}')
