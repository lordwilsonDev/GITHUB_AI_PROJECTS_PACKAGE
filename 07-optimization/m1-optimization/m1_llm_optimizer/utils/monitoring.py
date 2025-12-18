#!/usr/bin/env python3
"""
Monitoring and Verification Utilities
Provides real-time monitoring and verification of optimizations
"""

import subprocess
import psutil
import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Real-time system monitoring for LLM inference"""
    
    def __init__(self):
        self.baseline = None
        self.samples = []
        
    def capture_baseline(self) -> Dict:
        """Capture baseline system state"""
        baseline = {
            'timestamp': datetime.now().isoformat(),
            'memory': self._get_memory_stats(),
            'cpu': self._get_cpu_stats(),
            'processes': self._get_top_processes(5),
        }
        
        self.baseline = baseline
        logger.info("Baseline captured")
        return baseline
    
    def _get_memory_stats(self) -> Dict:
        """Get current memory statistics"""
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_gb': round(vm.total / (1024**3), 2),
            'available_gb': round(vm.available / (1024**3), 2),
            'used_gb': round(vm.used / (1024**3), 2),
            'percent': vm.percent,
            'swap_used_gb': round(swap.used / (1024**3), 2),
            'swap_percent': swap.percent,
        }
    
    def _get_cpu_stats(self) -> Dict:
        """Get current CPU statistics"""
        return {
            'percent': psutil.cpu_percent(interval=1),
            'per_cpu': psutil.cpu_percent(interval=1, percpu=True),
            'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
        }
    
    def _get_top_processes(self, n=5) -> List[Dict]:
        """Get top N processes by memory usage"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'memory_percent': round(proc.info['memory_percent'], 2),
                    'cpu_percent': round(proc.info['cpu_percent'], 2),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        return processes[:n]
    
    def monitor_inference_session(self, duration_seconds=300, interval=5) -> List[Dict]:
        """Monitor system during inference session"""
        logger.info(f"Starting monitoring for {duration_seconds} seconds...")
        
        start_time = time.time()
        samples = []
        
        while time.time() - start_time < duration_seconds:
            sample = {
                'timestamp': time.time() - start_time,
                'memory': self._get_memory_stats(),
                'cpu': self._get_cpu_stats(),
            }
            samples.append(sample)
            self.samples.append(sample)
            
            logger.info(f"Sample at {sample['timestamp']:.1f}s: "
                       f"Memory={sample['memory']['percent']:.1f}%, "
                       f"CPU={sample['cpu']['percent']:.1f}%")
            
            time.sleep(interval)
        
        return samples
    
    def analyze_samples(self) -> Dict:
        """Analyze collected samples"""
        if not self.samples:
            return {'error': 'No samples collected'}
        
        memory_percents = [s['memory']['percent'] for s in self.samples]
        cpu_percents = [s['cpu']['percent'] for s in self.samples]
        
        analysis = {
            'memory': {
                'min': min(memory_percents),
                'max': max(memory_percents),
                'avg': sum(memory_percents) / len(memory_percents),
                'trend': 'increasing' if memory_percents[-1] > memory_percents[0] else 'stable',
            },
            'cpu': {
                'min': min(cpu_percents),
                'max': max(cpu_percents),
                'avg': sum(cpu_percents) / len(cpu_percents),
            },
            'stability': self._assess_stability(memory_percents, cpu_percents),
        }
        
        return analysis
    
    def _assess_stability(self, memory_percents: List[float], cpu_percents: List[float]) -> str:
        """Assess system stability"""
        memory_variance = max(memory_percents) - min(memory_percents)
        
        if memory_variance > 20:
            return 'UNSTABLE - High memory variance'
        elif max(memory_percents) > 90:
            return 'CRITICAL - Memory pressure too high'
        elif max(memory_percents) > 80:
            return 'WARNING - High memory usage'
        else:
            return 'STABLE'
    
    def export_samples(self, output_path: Path) -> bool:
        """Export samples to JSON file"""
        try:
            data = {
                'baseline': self.baseline,
                'samples': self.samples,
                'analysis': self.analyze_samples(),
            }
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Samples exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export samples: {e}")
            return False


class OptimizationVerifier:
    """Verifies that optimizations have been applied correctly"""
    
    def __init__(self):
        self.checks = []
        
    def verify_all(self) -> Dict:
        """Run all verification checks"""
        results = {
            'os_optimizations': self.verify_os_optimizations(),
            'ollama_config': self.verify_ollama_config(),
            'python_env': self.verify_python_environment(),
            'process_priority': self.verify_process_priority(),
        }
        
        return results
    
    def verify_os_optimizations(self) -> Dict:
        """Verify OS-level optimizations"""
        checks = {}
        
        # Check transparency
        result = subprocess.run(
            ['defaults', 'read', 'com.apple.universalaccess', 'reduceTransparency'],
            capture_output=True, text=True
        )
        checks['reduce_transparency'] = result.returncode == 0 and '1' in result.stdout
        
        # Check window animations
        result = subprocess.run(
            ['defaults', 'read', 'NSGlobalDomain', 'NSAutomaticWindowAnimationsEnabled'],
            capture_output=True, text=True
        )
        checks['animations_disabled'] = result.returncode == 0 and '0' in result.stdout
        
        # Check App Nap
        result = subprocess.run(
            ['defaults', 'read', 'NSGlobalDomain', 'NSAppSleepDisabled'],
            capture_output=True, text=True
        )
        checks['app_nap_disabled'] = result.returncode == 0 and '1' in result.stdout
        
        # Check Spotlight status
        result = subprocess.run(
            ['mdutil', '-s', '/'],
            capture_output=True, text=True
        )
        checks['spotlight_status'] = 'disabled' if 'disabled' in result.stdout.lower() else 'enabled'
        
        return checks
    
    def verify_ollama_config(self) -> Dict:
        """Verify Ollama configuration"""
        checks = {}
        
        # Check if Ollama is installed
        result = subprocess.run(
            ['which', 'ollama'],
            capture_output=True, text=True
        )
        checks['ollama_installed'] = result.returncode == 0
        
        if checks['ollama_installed']:
            # Check if Ollama is running
            result = subprocess.run(
                ['pgrep', '-x', 'ollama'],
                capture_output=True, text=True
            )
            checks['ollama_running'] = result.returncode == 0
            
            # Try to get environment variables (may not work for background service)
            env_vars = ['OLLAMA_NUM_PARALLEL', 'OLLAMA_MAX_LOADED_MODELS', 'OLLAMA_KEEP_ALIVE']
            checks['env_vars'] = {}
            
            for var in env_vars:
                value = os.environ.get(var)
                checks['env_vars'][var] = value if value else 'not set'
        
        return checks
    
    def verify_python_environment(self) -> Dict:
        """Verify Python environment"""
        checks = {}
        
        # Check uv
        result = subprocess.run(
            ['which', 'uv'],
            capture_output=True, text=True
        )
        checks['uv_installed'] = result.returncode == 0
        
        # Check PyTorch
        try:
            import torch
            checks['pytorch_installed'] = True
            checks['pytorch_version'] = torch.__version__
            checks['mps_available'] = torch.backends.mps.is_available()
        except ImportError:
            checks['pytorch_installed'] = False
            checks['mps_available'] = False
        
        # Check MLX
        try:
            import mlx
            checks['mlx_installed'] = True
        except ImportError:
            checks['mlx_installed'] = False
        
        return checks
    
    def verify_process_priority(self) -> Dict:
        """Verify process priorities"""
        checks = {}
        
        # Check if Ollama is running with high priority
        try:
            for proc in psutil.process_iter(['name', 'pid', 'nice']):
                if proc.info['name'] == 'ollama':
                    checks['ollama_priority'] = {
                        'pid': proc.info['pid'],
                        'nice': proc.info['nice'],
                        'optimized': proc.info['nice'] < 0  # Lower nice = higher priority
                    }
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return checks
    
    def print_verification_report(self, results: Dict):
        """Print formatted verification report"""
        print("\n" + "="*70)
        print("OPTIMIZATION VERIFICATION REPORT")
        print("="*70)
        
        # OS Optimizations
        print("\nOS Optimizations:")
        os_opts = results.get('os_optimizations', {})
        self._print_check("Reduce Transparency", os_opts.get('reduce_transparency', False))
        self._print_check("Animations Disabled", os_opts.get('animations_disabled', False))
        self._print_check("App Nap Disabled", os_opts.get('app_nap_disabled', False))
        print(f"  Spotlight: {os_opts.get('spotlight_status', 'unknown')}")
        
        # Ollama Config
        print("\nOllama Configuration:")
        ollama = results.get('ollama_config', {})
        self._print_check("Ollama Installed", ollama.get('ollama_installed', False))
        self._print_check("Ollama Running", ollama.get('ollama_running', False))
        
        if 'env_vars' in ollama:
            print("  Environment Variables:")
            for var, value in ollama['env_vars'].items():
                print(f"    {var}: {value}")
        
        # Python Environment
        print("\nPython Environment:")
        python = results.get('python_env', {})
        self._print_check("uv Installed", python.get('uv_installed', False))
        self._print_check("PyTorch Installed", python.get('pytorch_installed', False))
        self._print_check("MPS Available", python.get('mps_available', False))
        self._print_check("MLX Installed", python.get('mlx_installed', False))
        
        # Process Priority
        print("\nProcess Priority:")
        priority = results.get('process_priority', {})
        if 'ollama_priority' in priority:
            opt = priority['ollama_priority']
            self._print_check(f"Ollama Optimized (PID {opt['pid']})", opt.get('optimized', False))
        else:
            print("  Ollama process not found")
        
        print("\n" + "="*70 + "\n")
    
    def _print_check(self, name: str, passed: bool):
        """Print a check result"""
        symbol = "✓" if passed else "✗"
        print(f"  {symbol} {name}")


class PerformanceBenchmark:
    """Benchmark LLM inference performance"""
    
    def __init__(self):
        self.results = {}
        
    def benchmark_ollama(self, model: str, prompt: str = "Hello, how are you?") -> Dict:
        """Benchmark Ollama inference speed"""
        logger.info(f"Benchmarking {model}...")
        
        try:
            import requests
            
            start_time = time.time()
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                },
                timeout=60
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    'model': model,
                    'success': True,
                    'total_duration_s': round(end_time - start_time, 2),
                    'eval_count': data.get('eval_count', 0),
                    'eval_duration_s': data.get('eval_duration', 0) / 1e9,
                    'tokens_per_second': 0,
                }
                
                if result['eval_duration_s'] > 0:
                    result['tokens_per_second'] = round(
                        result['eval_count'] / result['eval_duration_s'], 2
                    )
                
                logger.info(f"Benchmark complete: {result['tokens_per_second']} tokens/s")
                return result
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def compare_before_after(self, before: Dict, after: Dict) -> Dict:
        """Compare performance before and after optimization"""
        if not before.get('success') or not after.get('success'):
            return {'error': 'Invalid benchmark data'}
        
        improvement = {
            'tokens_per_second': {
                'before': before['tokens_per_second'],
                'after': after['tokens_per_second'],
                'improvement_percent': round(
                    ((after['tokens_per_second'] - before['tokens_per_second']) / 
                     before['tokens_per_second']) * 100, 2
                )
            },
            'total_duration': {
                'before': before['total_duration_s'],
                'after': after['total_duration_s'],
                'improvement_percent': round(
                    ((before['total_duration_s'] - after['total_duration_s']) / 
                     before['total_duration_s']) * 100, 2
                )
            }
        }
        
        return improvement
