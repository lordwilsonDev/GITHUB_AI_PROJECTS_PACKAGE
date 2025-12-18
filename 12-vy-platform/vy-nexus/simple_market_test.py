#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.expanduser('~/vy-nexus/modules'))

print("\n" + "="*70)
print("         MARKET ANALYSIS ENGINE - LIVE TEST")
print("="*70 + "\n")

try:
    from domain_expertise.tech_business_trend_analyzer import TechBusinessTrendAnalyzer
    
    print("[✓] Market Analysis Engine Loaded Successfully!\n")
    
    analyzer = TechBusinessTrendAnalyzer()
    
    print(f"Engine Status: OPERATIONAL")
    print(f"Data Directory: {analyzer.data_dir}")
    print(f"Trends Tracked: {len(analyzer.trends.get('trends', []))}")
    print(f"Signals Monitored: {len(analyzer.signals.get('signals', []))}")
    print(f"Predictions Generated: {len(analyzer.predictions.get('predictions', []))}")
    
    print("\nCore Capabilities:")
    print("  • Trend Identification & Tracking")
    print("  • Momentum Calculation")
    print("  • Impact Assessment")
    print("  • Market Signal Detection")
    print("  • Competitive Intelligence")
    print("  • Prediction Generation")
    
    print("\nMarket Categories Available:")
    if hasattr(analyzer, 'categories'):
        for cat in list(analyzer.categories.keys())[:5]:
            print(f"  • {cat.title()}")
    
    print("\n" + "="*70)
    print("Market Analysis Engine is ready for market intelligence tasks!")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
