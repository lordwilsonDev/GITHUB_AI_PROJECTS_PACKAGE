#!/usr/bin/env python3
"""
Python Environment Optimizer Module
Optimizes Python environment for M1 LLM inference using uv and MLX
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PythonEnvironmentOptimizer:
    """Optimizes Python environment for M1 systems"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.uv_installed = False
        self.pytorch_mps = False
        self.mlx_installed = False
        
    def check_environment(self) -> Dict:
        """Check current Python environment status"""
        env_status = {
            'python_version': sys.version,
            'python_path': sys.executable,
            'uv_installed': self._check_uv(),
            'pytorch_installed': self._check_pytorch(),
            'pytorch_mps': self._check_pytorch_mps(),
            'mlx_installed': self._check_mlx(),
            'pip_version': self._get_pip_version(),
        }
        
        return env_status
    
    def _check_uv(self) -> bool:
        """Check if uv is installed"""
        try:
            result = subprocess.run(
                ['which', 'uv'],
                capture_output=True, text=True
            )
            self.uv_installed = result.returncode == 0
            
            if self.uv_installed:
                version_result = subprocess.run(
                    ['uv', '--version'],
                    capture_output=True, text=True
                )
                logger.info(f"uv found: {version_result.stdout.strip()}")
            
            return self.uv_installed
        except Exception as e:
            logger.debug(f"Error checking uv: {e}")
            return False
    
    def _check_pytorch(self) -> bool:
        """Check if PyTorch is installed"""
        try:
            import torch
            logger.info(f"PyTorch version: {torch.__version__}")
            return True
        except ImportError:
            return False
    
    def _check_pytorch_mps(self) -> bool:
        """Check if PyTorch MPS backend is available"""
        try:
            import torch
            self.pytorch_mps = torch.backends.mps.is_available()
            if self.pytorch_mps:
                logger.info("✓ PyTorch MPS backend is available")
            else:
                logger.warning("✗ PyTorch MPS backend not available")
            return self.pytorch_mps
        except ImportError:
            return False
    
    def _check_mlx(self) -> bool:
        """Check if MLX is installed"""
        try:
            import mlx
            logger.info(f"MLX version: {mlx.__version__}")
            self.mlx_installed = True
            return True
        except ImportError:
            return False
    
    def _get_pip_version(self) -> Optional[str]:
        """Get pip version"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', '--version'],
                capture_output=True, text=True
            )
            return result.stdout.strip()
        except Exception:
            return None
    
    def install_uv(self) -> bool:
        """Install uv package manager"""
        if self.dry_run:
            logger.info("[DRY RUN] Would install uv")
            return True
        
        logger.info("Installing uv...")
        
        try:
            # Install uv using the official installer
            result = subprocess.run(
                ['curl', '-LsSf', 'https://astral.sh/uv/install.sh'],
                capture_output=True, text=True, check=True
            )
            
            install_script = result.stdout
            
            # Execute the install script
            subprocess.run(
                ['sh', '-c', install_script],
                check=True
            )
            
            logger.info("✓ uv installed successfully")
            logger.info("Note: You may need to restart your shell or run: source ~/.bashrc")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to install uv: {e}")
            return False
    
    def setup_optimized_venv(self, venv_path: Path, use_uv=True) -> bool:
        """Create optimized virtual environment"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create venv at {venv_path}")
            return True
        
        logger.info(f"Creating optimized virtual environment at {venv_path}...")
        
        try:
            if use_uv and self.uv_installed:
                # Use uv for faster environment creation
                subprocess.run(
                    ['uv', 'venv', str(venv_path)],
                    check=True
                )
                logger.info("✓ Created venv with uv (fast)")
            else:
                # Fallback to standard venv
                subprocess.run(
                    [sys.executable, '-m', 'venv', str(venv_path)],
                    check=True
                )
                logger.info("✓ Created venv with standard Python")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to create venv: {e}")
            return False
    
    def install_pytorch_mps(self, venv_path: Optional[Path] = None) -> bool:
        """Install PyTorch with MPS support"""
        if self.dry_run:
            logger.info("[DRY RUN] Would install PyTorch with MPS support")
            return True
        
        logger.info("Installing PyTorch with MPS support...")
        
        # Determine pip command
        if venv_path:
            pip_cmd = [str(venv_path / 'bin' / 'python'), '-m', 'pip']
        else:
            pip_cmd = [sys.executable, '-m', 'pip']
        
        # Use uv if available
        if self.uv_installed:
            if venv_path:
                pip_cmd = ['uv', 'pip', 'install', '--python', str(venv_path / 'bin' / 'python')]
            else:
                pip_cmd = ['uv', 'pip', 'install']
        
        try:
            # Install PyTorch
            if self.uv_installed:
                subprocess.run(
                    pip_cmd + ['torch', 'torchvision'],
                    check=True
                )
            else:
                subprocess.run(
                    pip_cmd + ['install', 'torch', 'torchvision'],
                    check=True
                )
            
            logger.info("✓ PyTorch installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to install PyTorch: {e}")
            return False
    
    def install_mlx(self, venv_path: Optional[Path] = None) -> bool:
        """Install Apple MLX framework"""
        if self.dry_run:
            logger.info("[DRY RUN] Would install MLX")
            return True
        
        logger.info("Installing Apple MLX...")
        
        # Determine pip command
        if venv_path:
            pip_cmd = [str(venv_path / 'bin' / 'python'), '-m', 'pip']
        else:
            pip_cmd = [sys.executable, '-m', 'pip']
        
        # Use uv if available
        if self.uv_installed:
            if venv_path:
                pip_cmd = ['uv', 'pip', 'install', '--python', str(venv_path / 'bin' / 'python')]
            else:
                pip_cmd = ['uv', 'pip', 'install']
        
        try:
            # Install MLX and mlx-lm
            packages = ['mlx', 'mlx-lm']
            
            if self.uv_installed:
                subprocess.run(
                    pip_cmd + packages,
                    check=True
                )
            else:
                subprocess.run(
                    pip_cmd + ['install'] + packages,
                    check=True
                )
            
            logger.info("✓ MLX installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to install MLX: {e}")
            return False
    
    def install_common_packages(self, venv_path: Optional[Path] = None) -> bool:
        """Install common packages for LLM development"""
        if self.dry_run:
            logger.info("[DRY RUN] Would install common packages")
            return True
        
        logger.info("Installing common LLM packages...")
        
        packages = [
            'requests',
            'numpy',
            'pandas',
            'transformers',
            'sentencepiece',
            'protobuf',
            'accelerate',
        ]
        
        # Determine pip command
        if venv_path:
            pip_cmd = [str(venv_path / 'bin' / 'python'), '-m', 'pip']
        else:
            pip_cmd = [sys.executable, '-m', 'pip']
        
        # Use uv if available
        if self.uv_installed:
            if venv_path:
                pip_cmd = ['uv', 'pip', 'install', '--python', str(venv_path / 'bin' / 'python')]
            else:
                pip_cmd = ['uv', 'pip', 'install']
        
        try:
            if self.uv_installed:
                subprocess.run(
                    pip_cmd + packages,
                    check=True
                )
            else:
                subprocess.run(
                    pip_cmd + ['install'] + packages,
                    check=True
                )
            
            logger.info("✓ Common packages installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to install packages: {e}")
            return False
    
    def generate_test_script(self, output_path: Path) -> bool:
        """Generate test script to verify MPS/MLX functionality"""
        test_script = """#!/usr/bin/env python3
"""
M1 Optimization Test Script
Tests PyTorch MPS and MLX functionality
"""

import sys

print("="*70)
print("M1 OPTIMIZATION TEST")
print("="*70)

# Test PyTorch MPS
print("\nTesting PyTorch MPS...")
try:
    import torch
    print(f"  PyTorch version: {torch.__version__}")
    
    if torch.backends.mps.is_available():
        print("  ✓ MPS backend is available")
        
        # Test MPS device
        mps_device = torch.device("mps")
        x = torch.ones(5, device=mps_device)
        print(f"  ✓ Created tensor on MPS: {x}")
        
        # Test computation
        y = x * 2
        print(f"  ✓ MPS computation successful: {y}")
        
        print("  ✓ PyTorch MPS is working correctly!")
    else:
        print("  ✗ MPS backend not available")
        print("  Note: Ensure you have PyTorch 1.12+ installed")
except ImportError:
    print("  ✗ PyTorch not installed")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test MLX
print("\nTesting Apple MLX...")
try:
    import mlx.core as mx
    print(f"  MLX version: {mx.__version__ if hasattr(mx, '__version__') else 'installed'}")
    
    # Test MLX array
    a = mx.array([1, 2, 3, 4])
    print(f"  ✓ Created MLX array: {a}")
    
    # Test computation
    b = a * 2
    print(f"  ✓ MLX computation successful: {b}")
    
    print("  ✓ MLX is working correctly!")
except ImportError:
    print("  ✗ MLX not installed")
    print("  Install with: pip install mlx")
except Exception as e:
    print(f"  ✗ Error: {e}")

# System info
print("\nSystem Information:")
print(f"  Python: {sys.version}")
print(f"  Executable: {sys.executable}")

print("\n" + "="*70)
print("Test complete!")
print("="*70 + "\n")
"""
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create test script at {output_path}")
            return True
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(test_script)
            os.chmod(output_path, 0o755)
            logger.info(f"✓ Created test script: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create test script: {e}")
            return False
    
    def generate_requirements_txt(self, output_path: Path, include_mlx=True) -> bool:
        """Generate optimized requirements.txt"""
        requirements = [
            "# M1 Optimized Python Requirements",
            "# Generated by M1 LLM Optimizer",
            "",
            "# Core ML frameworks",
            "torch>=2.0.0",
            "torchvision>=0.15.0",
        ]
        
        if include_mlx:
            requirements.extend([
                "mlx>=0.0.1",
                "mlx-lm>=0.0.1",
            ])
        
        requirements.extend([
            "",
            "# LLM libraries",
            "transformers>=4.30.0",
            "sentencepiece>=0.1.99",
            "protobuf>=3.20.0",
            "accelerate>=0.20.0",
            "",
            "# Utilities",
            "requests>=2.31.0",
            "numpy>=1.24.0",
            "pandas>=2.0.0",
            "",
            "# Optional: API clients",
            "# openai>=1.0.0",
            "# anthropic>=0.3.0",
        ])
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create requirements.txt at {output_path}")
            return True
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write('\n'.join(requirements))
            logger.info(f"✓ Created requirements.txt: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create requirements.txt: {e}")
            return False
    
    def print_environment_report(self, env_status: Dict):
        """Print formatted environment report"""
        print("\n" + "="*70)
        print("PYTHON ENVIRONMENT STATUS")
        print("="*70)
        
        print(f"\nPython Version: {env_status['python_version'].split()[0]}")
        print(f"Python Path: {env_status['python_path']}")
        
        print("\nPackage Manager:")
        if env_status['uv_installed']:
            print("  ✓ uv is installed (recommended)")
        else:
            print("  ✗ uv not installed (using pip)")
            print("  Recommendation: Install uv for 8-10x faster package management")
        
        print("\nML Frameworks:")
        if env_status['pytorch_installed']:
            print("  ✓ PyTorch is installed")
            if env_status['pytorch_mps']:
                print("    ✓ MPS backend available (GPU acceleration enabled)")
            else:
                print("    ✗ MPS backend not available (CPU only)")
        else:
            print("  ✗ PyTorch not installed")
        
        if env_status['mlx_installed']:
            print("  ✓ MLX is installed (native M1 framework)")
        else:
            print("  ✗ MLX not installed")
            print("  Recommendation: Install MLX for native M1 performance")
        
        print("\n" + "="*70 + "\n")
