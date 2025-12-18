#!/usr/bin/env python3
"""
⚡ AUTO-OPTIMIZATION ENGINE ⚡
The system optimizes itself

PURPOSE: Performance should improve automatically
AXIOM: "Efficiency emerges from measurement"
"""

import os
import json
import time
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, List
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
OPT_DIR = os.path.join(NEXUS_DIR, "auto_optimization")
METRICS_FILE = os.path.join(OPT_DIR, "performance_metrics.jsonl")
RECOMMENDATIONS_FILE = os.path.join(OPT_DIR, "optimization_recommendations.md")


class AutoOptimizationEngine:
    """
    Automatically profiles and optimizes system performance
    
    INVERSION: Instead of manual optimization,
    the system optimizes itself
    """
    
    def __init__(self):
        """Initialize optimization engine"""
        try:
            os.makedirs(OPT_DIR, exist_ok=True)
            
            logger.info("⚡ Auto-Optimization Engine initialized")
            
        except OSError as e:
            logger.error(f"Optimization engine initialization failed: {e}")
            raise
    
    def measure_system_metrics(self) -> Dict[str, Any]:
        """Measure current system performance"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_gb': psutil.virtual_memory().available / (1024**3),
                'disk_usage_percent': psutil.disk_usage(HOME).percent,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
            
            # File system metrics
            try:
                synthesis_dir = os.path.join(NEXUS_DIR, "synthesis")
                if os.path.exists(synthesis_dir):
                    synthesis_files = len([f for f in os.listdir(synthesis_dir) if f.endswith('.jsonl')])
                    metrics['synthesis_files'] = synthesis_files
            except Exception:
                pass
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics measurement failed: {e}")
            return {}
    
    def load_historical_metrics(self) -> List[Dict[str, Any]]:
        """Load historical performance data"""
        try:
            metrics = []
            
            if os.path.exists(METRICS_FILE):
                with open(METRICS_FILE, 'r') as f:
                    for line in f:
                        try:
                            metrics.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
            
            return metrics
            
        except (OSError, IOError) as e:
            logger.error(f"Historical metrics load failed: {e}")
            return []
    
    def save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save current metrics"""
        try:
            with open(METRICS_FILE, 'a') as f:
                f.write(json.dumps(metrics) + '\n')
        except (OSError, IOError) as e:
            logger.error(f"Metrics save failed: {e}")
    
    def analyze_trends(self, historical: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends"""
        try:
            if len(historical) < 2:
                return {}
            
            trends = {}
            
            # CPU trend
            cpu_values = [m.get('cpu_percent', 0) for m in historical if 'cpu_percent' in m]
            if cpu_values:
                trends['cpu_avg'] = sum(cpu_values) / len(cpu_values)
                trends['cpu_max'] = max(cpu_values)
                trends['cpu_trend'] = 'increasing' if cpu_values[-1] > cpu_values[0] else 'stable'
            
            # Memory trend
            mem_values = [m.get('memory_percent', 0) for m in historical if 'memory_percent' in m]
            if mem_values:
                trends['memory_avg'] = sum(mem_values) / len(mem_values)
                trends['memory_max'] = max(mem_values)
                trends['memory_trend'] = 'increasing' if mem_values[-1] > mem_values[0] else 'stable'
            
            return trends
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {}
    
    def generate_recommendations(
        self,
        current: Dict[str, Any],
        trends: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization recommendations"""
        try:
            recommendations = []
            
            # CPU recommendations
            cpu = current.get('cpu_percent', 0)
            if cpu > 80:
                recommendations.append(
                    "🔥 HIGH CPU: Consider reducing concurrent processes or adding delays between cycles"
                )
            elif trends.get('cpu_avg', 0) > 60:
                recommendations.append(
                    "⚠️  ELEVATED CPU: Average CPU usage is high - monitor long-running processes"
                )
            
            # Memory recommendations
            memory = current.get('memory_percent', 0)
            if memory > 85:
                recommendations.append(
                    "🔥 HIGH MEMORY: Consider clearing caches or reducing file retention"
                )
            elif trends.get('memory_avg', 0) > 70:
                recommendations.append(
                    "⚠️  ELEVATED MEMORY: Average memory usage is high - review data structures"
                )
            
            # Disk recommendations
            disk = current.get('disk_usage_percent', 0)
            if disk > 90:
                recommendations.append(
                    "🔥 HIGH DISK: Clean up old synthesis files or archive historical data"
                )
            elif disk > 80:
                recommendations.append(
                    "⚠️  DISK SPACE: Consider archiving old data to free up space"
                )
            
            # Synthesis file recommendations
            synthesis_files = current.get('synthesis_files', 0)
            if synthesis_files > 100:
                recommendations.append(
                    "📦 SYNTHESIS FILES: Consider consolidating or archiving old synthesis files"
                )
            
            # If no issues
            if not recommendations:
                recommendations.append("✨ System is running optimally - no optimizations needed")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return []
    
    def save_recommendations(self, recommendations: List[str], metrics: Dict[str, Any]) -> None:
        """Save optimization recommendations"""
        try:
            report = f"""# ⚡ AUTO-OPTIMIZATION REPORT

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current Metrics

- **CPU Usage**: {metrics.get('cpu_percent', 0):.1f}%
- **Memory Usage**: {metrics.get('memory_percent', 0):.1f}%
- **Memory Available**: {metrics.get('memory_available_gb', 0):.2f} GB
- **Disk Usage**: {metrics.get('disk_usage_percent', 0):.1f}%
- **Synthesis Files**: {metrics.get('synthesis_files', 0)}

## Recommendations

"""
            
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
            
            report += """
## Optimization Strategies

### For CPU
- Add delays between intensive operations
- Run fewer concurrent processes
- Schedule heavy tasks during low-activity periods

### For Memory
- Archive old synthesis files
- Implement rolling file rotation
- Clear temporary caches regularly

### For Disk
- Compress historical data
- Move archives to external storage
- Implement automatic cleanup policies

---

💓 **Self-Optimizing Intelligence**
"""
            
            with open(RECOMMENDATIONS_FILE, 'w') as f:
                f.write(report)
            
            logger.info(f"📄 Recommendations saved: {RECOMMENDATIONS_FILE}")
            
        except (OSError, IOError) as e:
            logger.error(f"Recommendations save failed: {e}")
    
    def run_optimization(self) -> Dict[str, Any]:
        """Execute optimization analysis"""
        try:
            logger.info("⚡ Running optimization analysis...")
            
            # Measure current metrics
            current_metrics = self.measure_system_metrics()
            
            if not current_metrics:
                return {'optimizations': 0}
            
            # Save metrics
            self.save_metrics(current_metrics)
            
            # Load historical metrics
            historical = self.load_historical_metrics()
            
            # Analyze trends
            trends = self.analyze_trends(historical)
            
            # Generate recommendations
            recommendations = self.generate_recommendations(current_metrics, trends)
            
            # Save recommendations
            self.save_recommendations(recommendations, current_metrics)
            
            return {
                'metrics': current_metrics,
                'trends': trends,
                'recommendations': recommendations,
                'optimization_count': len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Optimization analysis failed: {e}")
            return {'optimizations': 0, 'error': str(e)}


def main():
    """Main execution"""
    try:
        print("=" * 80)
        print("⚡ AUTO-OPTIMIZATION ENGINE ⚡")
        print("=" * 80)
        print("The system optimizes itself")
        print("=" * 80)
        print()
        
        engine = AutoOptimizationEngine()
        
        print("📊 Measuring performance...")
        results = engine.run_optimization()
        
        print()
        print("=" * 80)
        print("📊 OPTIMIZATION RESULTS")
        print("=" * 80)
        
        if results.get('metrics'):
            metrics = results['metrics']
            print(f"CPU Usage: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"Memory Usage: {metrics.get('memory_percent', 0):.1f}%")
            print(f"Memory Available: {metrics.get('memory_available_gb', 0):.2f} GB")
            print(f"Disk Usage: {metrics.get('disk_usage_percent', 0):.1f}%")
            
            print()
            print("RECOMMENDATIONS:")
            for rec in results.get('recommendations', []):
                print(f"  {rec}")
            
            print()
            print(f"📄 Full report: {RECOMMENDATIONS_FILE}")
            print(f"📈 Metrics: {METRICS_FILE}")
        else:
            if 'error' in results:
                print(f"❌ Optimization failed: {results['error']}")
            else:
                print("❌ No metrics collected")
        
        print()
        print("=" * 80)
        print("💓 Self-Optimizing Intelligence")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
