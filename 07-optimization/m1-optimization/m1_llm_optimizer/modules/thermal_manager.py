#!/usr/bin/env python3
"""
Thermal Management Module
Monitors and manages thermal performance for sustained LLM inference
"""

import subprocess
import time
import os
from pathlib import Path
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class ThermalManager:
    """Manages thermal performance and fan control"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.thermal_data = {}
        
    def check_thermal_state(self) -> Dict:
        """Check current thermal state"""
        thermal_info = {
            'available': False,
            'method': None,
            'data': {}
        }
        
        # Try powermetrics (requires sudo)
        if self._check_powermetrics():
            thermal_info['available'] = True
            thermal_info['method'] = 'powermetrics'
            thermal_info['data'] = self._get_powermetrics_thermal()
        
        # Try sysctl for basic info
        thermal_info['sysctl'] = self._get_sysctl_thermal()
        
        return thermal_info
    
    def _check_powermetrics(self) -> bool:
        """Check if powermetrics is available"""
        try:
            result = subprocess.run(
                ['sudo', '-n', 'powermetrics', '--help'],
                capture_output=True, text=True, timeout=2
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False
    
    def _get_powermetrics_thermal(self) -> Dict:
        """Get thermal data from powermetrics"""
        try:
            result = subprocess.run(
                ['sudo', '-n', 'powermetrics', '--samplers', 'thermal', '-n', '1', '-i', '1000'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                return {'raw': result.stdout}
            else:
                return {'error': 'powermetrics requires sudo'}
                
        except subprocess.TimeoutExpired:
            return {'error': 'timeout'}
        except Exception as e:
            return {'error': str(e)}
    
    def _get_sysctl_thermal(self) -> Dict:
        """Get basic thermal info from sysctl"""
        thermal_data = {}
        
        # Try to get CPU temperature (may not be available on all systems)
        sysctl_keys = [
            'machdep.xcpm.cpu_thermal_level',
            'machdep.xcpm.gpu_thermal_level',
        ]
        
        for key in sysctl_keys:
            try:
                result = subprocess.run(
                    ['sysctl', '-n', key],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    thermal_data[key] = result.stdout.strip()
            except Exception:
                pass
        
        return thermal_data
    
    def monitor_thermal_during_inference(self, duration_seconds=60, interval=5) -> List[Dict]:
        """Monitor thermal state during inference"""
        logger.info(f"Monitoring thermal state for {duration_seconds} seconds...")
        
        samples = []
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            sample = {
                'timestamp': time.time() - start_time,
                'thermal': self.check_thermal_state()
            }
            samples.append(sample)
            
            logger.info(f"Sample at {sample['timestamp']:.1f}s")
            time.sleep(interval)
        
        return samples
    
    def generate_fan_control_guide(self, output_path: Path) -> bool:
        """Generate guide for fan control setup"""
        guide_content = """# Thermal Management Guide for M1 LLM Inference

## Overview
Sustained LLM inference generates significant heat. Proper thermal management
prevents throttling and maintains consistent performance.

## Understanding Thermal Throttling

### M1 Thermal Characteristics:
- **Throttling Temperature**: ~90-100°C
- **MacBook Air**: Passive cooling (no fan)
- **MacBook Pro/Mac Mini**: Active cooling (fan-based)

### Signs of Throttling:
- Sudden drop in tokens/second
- Increased inference latency
- System becoming unresponsive

## Fan Control Solutions

### Option 1: Macs Fan Control (Recommended)

**Download**: https://crystalidea.com/macs-fan-control

**Setup Steps**:
1. Install Macs Fan Control
2. Open the application
3. Select "Custom" fan curve
4. Set sensor to "CPU Efficiency Core" or "GPU"
5. Configure fan curve:
   - Minimum: 3000 RPM (50% of max)
   - Start ramping at: 60°C
   - Maximum at: 85°C

**Benefits**:
- Prevents heat soak
- Maintains consistent performance
- Reduces thermal throttling

**Trade-off**:
- Increased fan noise
- Slightly higher power consumption

### Option 2: Command Line (Advanced)

Macs Fan Control can be controlled via command line:

```bash
# Start with custom profile
/Applications/Macs\\ Fan\\ Control.app/Contents/MacOS/Macs\\ Fan\\ Control /minimized
```

### Option 3: SMC Fan Control

Alternative open-source tool:
- **Download**: https://github.com/hholtmann/smcFanControl
- Similar functionality to Macs Fan Control
- Free and open source

## Passive Cooling (MacBook Air)

### Limitations:
- No fan means limited sustained performance
- Thermal throttling will occur during long inference

### Optimization Strategies:
1. **Elevate the laptop**: Improve airflow underneath
2. **Use cooling pad**: External cooling solution
3. **Limit inference duration**: Take breaks to cool down
4. **Use smaller models**: Reduce computational load
5. **Lower ambient temperature**: Work in cooler environment

## Monitoring Thermal State

### Using Activity Monitor:
1. Open Activity Monitor
2. Window → CPU History
3. Watch for sudden drops in CPU usage (indicates throttling)

### Using Terminal:

```bash
# Check thermal levels (requires sudo)
sudo powermetrics --samplers thermal -n 1

# Monitor CPU frequency
sysctl -n machdep.cpu.brand_string
```

### Using This Optimizer:

```bash
# Monitor thermal state
python3 m1_optimizer.py --monitor-thermal
```

## Best Practices

### For Long Inference Sessions:
1. Set aggressive fan curve before starting
2. Monitor temperature during first 10 minutes
3. Adjust fan curve if temperature exceeds 85°C
4. Ensure adequate ventilation around device

### For MacBook Air Users:
1. Use external cooling pad
2. Limit context window to reduce load
3. Use Q4 quantization (lower compute)
4. Take cooling breaks every 30 minutes

### For Mac Mini/MacBook Pro:
1. Set minimum fan speed to 3000 RPM
2. Place in well-ventilated area
3. Avoid enclosed spaces
4. Clean dust from vents regularly

## Thermal Optimization Checklist

- [ ] Install fan control software
- [ ] Configure custom fan curve
- [ ] Test thermal performance with sample inference
- [ ] Monitor temperature during first real workload
- [ ] Adjust fan curve based on results
- [ ] Ensure physical ventilation is adequate
- [ ] Set up thermal monitoring alerts (if available)

## Troubleshooting

### Problem: System still throttles despite fan control
**Solutions**:
- Increase minimum fan speed
- Lower fan curve trigger temperature
- Check for dust buildup in vents
- Verify thermal paste (for older devices)

### Problem: Fan too loud
**Solutions**:
- Reduce minimum fan speed slightly
- Use noise-canceling headphones
- Schedule intensive tasks for times when noise is acceptable

### Problem: MacBook Air throttles quickly
**Solutions**:
- This is expected behavior
- Use external cooling
- Reduce model size
- Limit inference duration

## Performance Impact

### With Proper Thermal Management:
- Consistent tokens/second throughout session
- No sudden performance drops
- Predictable inference times

### Without Thermal Management:
- Initial high performance
- Gradual degradation after 5-10 minutes
- Severe throttling after 15-20 minutes
- Up to 50% performance loss

## Conclusion

Thermal management is critical for sustained LLM inference on M1 systems.
Proper fan control can maintain peak performance indefinitely, while passive
cooling or inadequate fan curves lead to significant throttling.

For production workloads, invest in proper thermal management tools and
monitor performance during initial deployment.
"""
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create thermal guide at {output_path}")
            return True
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(guide_content)
            logger.info(f"✓ Created thermal management guide: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create thermal guide: {e}")
            return False
    
    def generate_monitoring_script(self, output_path: Path) -> bool:
        """Generate thermal monitoring script"""
        script_content = """#!/usr/bin/env python3
"""
Thermal Monitoring Script
Monitors system temperature during LLM inference
"""

import subprocess
import time
import sys
from datetime import datetime


def get_thermal_level():
    """Get thermal level from sysctl"""
    try:
        result = subprocess.run(
            ['sysctl', '-n', 'machdep.xcpm.cpu_thermal_level'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except:
        pass
    return None


def get_cpu_usage():
    """Get CPU usage percentage"""
    try:
        result = subprocess.run(
            ['ps', '-A', '-o', '%cpu'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\\n')[1:]  # Skip header
            total = sum(float(line.strip()) for line in lines if line.strip())
            return round(total, 1)
    except:
        pass
    return None


def monitor(duration_minutes=10, interval_seconds=5):
    """Monitor thermal state"""
    print("="*70)
    print("THERMAL MONITORING")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Interval: {interval_seconds} seconds")
    print("="*70)
    print()
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    print(f"{'Time':<12} {'Thermal Level':<15} {'CPU Usage':<12} {'Status'}")
    print("-"*70)
    
    max_thermal = 0
    throttle_detected = False
    
    while time.time() < end_time:
        current_time = datetime.now().strftime("%H:%M:%S")
        thermal_level = get_thermal_level()
        cpu_usage = get_cpu_usage()
        
        if thermal_level is not None:
            max_thermal = max(max_thermal, thermal_level)
            
            # Determine status
            if thermal_level >= 80:
                status = "⚠️  CRITICAL"
                throttle_detected = True
            elif thermal_level >= 60:
                status = "⚠️  HIGH"
            elif thermal_level >= 40:
                status = "✓ MODERATE"
            else:
                status = "✓ NORMAL"
            
            print(f"{current_time:<12} {thermal_level:<15} {cpu_usage or 'N/A':<12} {status}")
        else:
            print(f"{current_time:<12} {'N/A':<15} {cpu_usage or 'N/A':<12} {'Unknown'}")
        
        time.sleep(interval_seconds)
    
    print("\\n" + "="*70)
    print("MONITORING COMPLETE")
    print("="*70)
    print(f"Maximum thermal level: {max_thermal}")
    
    if throttle_detected:
        print("⚠️  WARNING: High thermal levels detected!")
        print("Recommendation: Improve cooling or reduce workload")
    else:
        print("✓ Thermal levels within acceptable range")
    
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor thermal state')
    parser.add_argument('--duration', type=int, default=10, help='Duration in minutes')
    parser.add_argument('--interval', type=int, default=5, help='Interval in seconds')
    
    args = parser.parse_args()
    
    try:
        monitor(args.duration, args.interval)
    except KeyboardInterrupt:
        print("\\n\\nMonitoring stopped by user")
        sys.exit(0)
"""
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create monitoring script at {output_path}")
            return True
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(script_content)
            os.chmod(output_path, 0o755)
            logger.info(f"✓ Created monitoring script: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create monitoring script: {e}")
            return False
    
    def print_thermal_recommendations(self, device_type='unknown'):
        """Print thermal management recommendations"""
        print("\n" + "="*70)
        print("THERMAL MANAGEMENT RECOMMENDATIONS")
        print("="*70)
        
        if device_type.lower() == 'macbook air':
            print("\nDevice: MacBook Air (Passive Cooling)")
            print("\nChallenges:")
            print("  • No fan - relies on heat dissipation through chassis")
            print("  • Will throttle during sustained workloads")
            print("  • Performance degrades after 10-15 minutes")
            print("\nRecommendations:")
            print("  1. Use external cooling pad")
            print("  2. Elevate laptop for better airflow")
            print("  3. Use smaller models (3B-7B max)")
            print("  4. Limit context window to 2048 tokens")
            print("  5. Take cooling breaks every 20-30 minutes")
            print("  6. Work in cooler environment")
        else:
            print("\nDevice: Mac Mini / MacBook Pro (Active Cooling)")
            print("\nAdvantages:")
            print("  • Fan-based cooling allows sustained performance")
            print("  • Can maintain peak performance with proper fan control")
            print("\nRecommendations:")
            print("  1. Install Macs Fan Control or similar tool")
            print("  2. Set minimum fan speed to 3000 RPM (50%)")
            print("  3. Configure fan curve to ramp up at 60°C")
            print("  4. Ensure adequate ventilation around device")
            print("  5. Clean dust from vents regularly")
        
        print("\nGeneral Best Practices:")
        print("  • Monitor thermal state during first inference session")
        print("  • Adjust settings based on observed temperatures")
        print("  • Use Q4 quantization to reduce thermal load")
        print("  • Avoid enclosed spaces or laptop stands that block vents")
        
        print("\n" + "="*70 + "\n")
