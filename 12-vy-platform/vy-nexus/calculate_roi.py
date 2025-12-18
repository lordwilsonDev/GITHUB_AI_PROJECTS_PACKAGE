#!/usr/bin/env python3
"""Calculate ROI for efficiency improvements"""

import sys

def calculate_roi(time_to_implement_min, time_saved_per_use_min, expected_uses):
    """
    Calculate ROI for an efficiency improvement
    
    Args:
        time_to_implement_min: Time to implement in minutes
        time_saved_per_use_min: Time saved per use in minutes
        expected_uses: Expected number of uses
    
    Returns:
        dict with break_even_uses, total_time_saved, roi_percentage
    """
    if time_saved_per_use_min <= 0:
        return {
            'break_even_uses': float('inf'),
            'total_time_saved_min': -time_to_implement_min,
            'roi_percentage': -100
        }
    
    break_even = time_to_implement_min / time_saved_per_use_min
    total_saved = (time_saved_per_use_min * expected_uses) - time_to_implement_min
    roi_pct = (total_saved / time_to_implement_min * 100) if time_to_implement_min > 0 else 0
    
    return {
        'break_even_uses': break_even,
        'total_time_saved_min': total_saved,
        'roi_percentage': roi_pct
    }

def format_time(minutes):
    """Format minutes into human-readable time"""
    if minutes < 0:
        return f"-{format_time(-minutes)}"
    if minutes < 60:
        return f"{minutes:.0f} min"
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.1f} hours"
    days = hours / 24
    return f"{days:.1f} days"

def main():
    if len(sys.argv) == 1:
        # Interactive mode
        print("📊 EFFICIENCY IMPROVEMENT ROI CALCULATOR\n")
        print("Enter details for your efficiency improvement:\n")
        
        try:
            time_to_implement = float(input("Time to implement (minutes): "))
            time_saved_per_use = float(input("Time saved per use (minutes): "))
            expected_uses = int(input("Expected number of uses: "))
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Invalid input. Exiting.")
            sys.exit(1)
        
        roi = calculate_roi(time_to_implement, time_saved_per_use, expected_uses)
        
        print(f"\n{'='*70}")
        print("\n📊 RESULTS:\n")
        print(f"  Time to implement: {format_time(time_to_implement)}")
        print(f"  Time saved per use: {format_time(time_saved_per_use)}")
        print(f"  Expected uses: {expected_uses}")
        print(f"\n  Break-even point: {roi['break_even_uses']:.1f} uses")
        print(f"  Total time saved: {format_time(roi['total_time_saved_min'])}")
        print(f"  ROI: {roi['roi_percentage']:.0f}%")
        
        if roi['roi_percentage'] > 500:
            print("\n✅ EXCELLENT ROI - Highly recommended!")
        elif roi['roi_percentage'] > 200:
            print("\n✅ GOOD ROI - Recommended")
        elif roi['roi_percentage'] > 0:
            print("\n🟡 POSITIVE ROI - Consider implementing")
        else:
            print("\n❌ NEGATIVE ROI - Not recommended")
        
    elif len(sys.argv) == 4:
        # Command-line mode
        try:
            time_to_implement = float(sys.argv[1])
            time_saved_per_use = float(sys.argv[2])
            expected_uses = int(sys.argv[3])
        except ValueError:
            print("Usage: python3 calculate_roi.py <time_to_implement> <time_saved_per_use> <expected_uses>")
            print("All times in minutes.")
            sys.exit(1)
        
        roi = calculate_roi(time_to_implement, time_saved_per_use, expected_uses)
        
        print(f"Break-even: {roi['break_even_uses']:.1f} uses")
        print(f"Total saved: {format_time(roi['total_time_saved_min'])}")
        print(f"ROI: {roi['roi_percentage']:.0f}%")
    else:
        print("Usage: python3 calculate_roi.py [<time_to_implement> <time_saved_per_use> <expected_uses>]")
        print("\nRun without arguments for interactive mode.")
        print("\nExample:")
        print("  python3 calculate_roi.py 30 7 50")
        print("  (30 min to implement, 7 min saved per use, 50 expected uses)")
        sys.exit(1)

if __name__ == "__main__":
    main()
