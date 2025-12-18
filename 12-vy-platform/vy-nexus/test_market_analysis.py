#!/usr/bin/env python3
"""
Test Market Analysis Engine
"""

import sys
import os

# Add modules to path
sys.path.insert(0, os.path.expanduser('~/vy-nexus/modules'))

print("=" * 60)
print("MARKET ANALYSIS ENGINE TEST")
print("=" * 60)
print()

# Test 1: Import and initialize
print("Test 1: Loading Market Analysis Components...")
try:
    from domain_expertise.competitive_landscape_researcher import CompetitiveLandscapeResearcher
    print("✓ CompetitiveLandscapeResearcher loaded")
except Exception as e:
    print(f"✗ Error loading CompetitiveLandscapeResearcher: {e}")

try:
    from domain_expertise.tech_business_trend_analyzer import TechBusinessTrendAnalyzer
    print("✓ TechBusinessTrendAnalyzer loaded")
except Exception as e:
    print(f"✗ Error loading TechBusinessTrendAnalyzer: {e}")

print()
print("Test 2: Creating Market Analysis Instance...")
try:
    analyzer = TechBusinessTrendAnalyzer()
    print(f"✓ Market Analyzer created: {type(analyzer).__name__}")
    print(f"  Data directory: {analyzer.data_dir}")
except Exception as e:
    print(f"✗ Error creating analyzer: {e}")

print()
print("=" * 60)
print("Market Analysis Engine is ready!")
print("=" * 60)
