#!/usr/bin/env python3
"""
Axiomatic Governance Engine (AGE) - Core Implementation
Integrates geometric axioms with M1-optimized stack
"""

import asyncio
import json
import time
import math
import psutil
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AGEMetrics:
    """Real-time metrics for Axiomatic Governance Engine"""
    vdr: float = 0.0  # Vitality-per-Density Ratio
    sem: float = 0.0  # Simplicity/Entropy Metric
    cac: float = 0.0  # Coherence Acceleration Coefficient
    stf: float = 0.0  # Selective Torsion Filter effectiveness
    timestamp: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'vdr': self.vdr,
            'sem': self.sem,
            'cac': self.cac,
            'stf': self.stf,
            'timestamp': self.timestamp
        }

class AxiomaticGovernanceEngine:
    """
    Core AGE implementation enforcing geometric axioms on M1 stack
    """
    
    def __init__(self, config_path: str = "age_config.json"):
        self.config = self.load_config(config_path)
        self.metrics_history: List[AGEMetrics] = []
        self.current_metrics = AGEMetrics()
        
        # Axiom enforcement thresholds
        self.dignity_threshold = self.config.get('dignity_threshold', -1.0)
        self.vdr_target = self.config.get('vdr_target', 2.0)
        self.stf_target = self.config.get('stf_target', 0.95)
        
        # System state tracking
        self.torsion_detected = 0
        self.torsion_blocked = 0
        self.coherence_history = []
        self.complexity_baseline = None
        
        # Initialize M1 optimization
        self.initialize_m1_stack()
    
    def load_config(self, config_path: str) -> Dict:
        """Load AGE configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            default_config = {
                'dignity_threshold': -1.0,
                'vdr_target': 2.0,
                'stf_target': 0.95,
                'ollama_host': 'localhost:11434',
                'model_name': 'llama3.2-vision',
                'whisper_model': 'mlx-community/whisper-large-v3-mlx'
            }
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def initialize_m1_stack(self):
        """Initialize M1-optimized components"""
        print("🔧 Initializing M1-optimized AGE stack...")
        
        # Verify Ollama service
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Ollama service verified")
            else:
                print("⚠️ Ollama service not responding")
        except Exception as e:
            print(f"❌ Ollama verification failed: {e}")
        
        # Initialize baseline complexity
        self.complexity_baseline = self.measure_system_complexity()
        print(f"📊 Baseline complexity: {self.complexity_baseline}")
    
    def enforce_lexicographic_dignity(self, confidence_score: float, 
                                    content: str) -> Tuple[bool, str]:
        """
        Enforce Axiom of Lexicographic Dignity (I_NSSI)
        Digital Andon Cord implementation
        """
        if confidence_score < self.dignity_threshold:
            self.torsion_detected += 1
            self.torsion_blocked += 1
            
            # Dignified rollback
            return False, (
                f"I'm not confident in my response (confidence: {confidence_score:.3f}). "
                f"Could you please clarify or rephrase your request? I want to ensure "
                f"I provide accurate information."
            )
        
        # Check for potential dignity violations in content
        dignity_violations = self.detect_dignity_violations(content)
        if dignity_violations:
            self.torsion_detected += 1
            self.torsion_blocked += 1
            return False, (
                f"I cannot provide that response as it may violate human dignity. "
                f"Let me help you with something else instead."
            )
        
        return True, content
    
    def detect_dignity_violations(self, content: str) -> List[str]:
        """Detect potential violations of human dignity"""
        violations = []
        
        # Basic dignity violation patterns
        violation_patterns = [
            'harm', 'hurt', 'damage', 'destroy', 'kill',
            'hate', 'discriminate', 'degrade', 'humiliate'
        ]
        
        content_lower = content.lower()
        for pattern in violation_patterns:
            if pattern in content_lower:
                violations.append(pattern)
        
        return violations
    
    def calculate_vdr(self, response_quality: float, confidence: float, 
                     alignment_score: float) -> float:
        """Calculate Vitality-per-Density Ratio"""
        # Measure current system vitality
        vitality = response_quality * confidence * alignment_score
        
        # Measure current system density
        memory_usage = psutil.virtual_memory().percent / 100
        cpu_usage = psutil.cpu_percent() / 100
        process_count = len(psutil.pids()) / 1000  # Normalize
        
        density = memory_usage + cpu_usage + process_count
        
        # Avoid division by zero
        if density == 0:
            density = 0.001
        
        vdr = vitality / density
        self.current_metrics.vdr = vdr
        return vdr
    
    def calculate_sem(self, functional_features: int, 
                     structural_complexity: int) -> float:
        """Calculate Simplicity/Entropy Metric"""
        if structural_complexity == 0:
            structural_complexity = 1
        
        # Geodesic simplicity: functional growth vs structural growth
        sem = math.log(functional_features) - math.log(structural_complexity)
        self.current_metrics.sem = sem
        return sem
    
    def calculate_cac(self, coherence_delta: float, time_delta: float, 
                     friction_factor: float = 1.0) -> float:
        """Calculate Coherence Acceleration Coefficient"""
        if time_delta == 0:
            time_delta = 0.001
        
        cac = (coherence_delta / time_delta) * friction_factor
        self.current_metrics.cac = cac
        self.coherence_history.append(coherence_delta)
        return cac
    
    def calculate_stf(self) -> float:
        """Calculate Selective Torsion Filter effectiveness"""
        if self.torsion_detected == 0:
            stf = 1.0  # Perfect filtering (no torsion to filter)
        else:
            stf = self.torsion_blocked / self.torsion_detected
        
        self.current_metrics.stf = stf
        return stf
    
    def measure_system_complexity(self) -> Dict:
        """Measure current system complexity"""
        try:
            # Count Python processes and memory usage
            python_processes = []
            total_memory = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append(proc.info)
                        total_memory += proc.info['memory_info'].rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'python_processes': len(python_processes),
                'memory_mb': total_memory / (1024 * 1024),
                'cpu_percent': psutil.cpu_percent(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error measuring complexity: {e}")
            return {'error': str(e)}
    
    def update_metrics(self, response_quality: float = 1.0, 
                      confidence: float = 1.0, alignment_score: float = 1.0,
                      functional_features: int = 1, 
                      structural_complexity: int = 1,
                      coherence_delta: float = 0.0, 
                      time_delta: float = 1.0) -> AGEMetrics:
        """Update all AGE metrics"""
        start_time = time.time()
        
        # Calculate all metrics
        vdr = self.calculate_vdr(response_quality, confidence, alignment_score)
        sem = self.calculate_sem(functional_features, structural_complexity)
        cac = self.calculate_cac(coherence_delta, time_delta)
        stf = self.calculate_stf()
        
        # Update current metrics
        self.current_metrics.timestamp = datetime.now().isoformat()
        
        # Store in history
        self.metrics_history.append(AGEMetrics(
            vdr=vdr, sem=sem, cac=cac, stf=stf,
            timestamp=self.current_metrics.timestamp
        ))
        
        # Trim history to last 100 entries
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        return self.current_metrics
    
    def check_axiom_compliance(self) -> Dict[str, bool]:
        """Check compliance with all geometric axioms"""
        compliance = {
            'lexicographic_dignity': self.current_metrics.stf >= self.stf_target,
            'vitality_density': self.current_metrics.vdr >= self.vdr_target,
            'coherence_acceleration': self.current_metrics.cac > 0,
            'temporal_fidelity': len(self.metrics_history) > 0,
            'geodesic_simplicity': self.current_metrics.sem > 0
        }
        
        return compliance
    
    def get_governance_report(self) -> Dict:
        """Generate comprehensive governance report"""
        compliance = self.check_axiom_compliance()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'current_metrics': self.current_metrics.to_dict(),
            'axiom_compliance': compliance,
            'overall_health': all(compliance.values()),
            'torsion_stats': {
                'detected': self.torsion_detected,
                'blocked': self.torsion_blocked,
                'filter_effectiveness': self.current_metrics.stf
            },
            'system_complexity': self.measure_system_complexity(),
            'recommendations': self.generate_recommendations()
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if self.current_metrics.vdr < self.vdr_target:
            recommendations.append(
                f"VDR below target ({self.current_metrics.vdr:.2f} < {self.vdr_target}). "
                f"Consider optimizing system density or improving response quality."
            )
        
        if self.current_metrics.stf < self.stf_target:
            recommendations.append(
                f"STF below target ({self.current_metrics.stf:.2f} < {self.stf_target}). "
                f"Review torsion detection algorithms."
            )
        
        if self.current_metrics.cac <= 0:
            recommendations.append(
                "CAC indicates no coherence acceleration. "
                "Review learning mechanisms and feedback loops."
            )
        
        if not recommendations:
            recommendations.append("All axioms in compliance. System operating optimally.")
        
        return recommendations
    
    async def process_request(self, content: str, confidence: float = 1.0) -> Dict:
        """Process request through AGE governance"""
        start_time = time.time()
        
        # Enforce lexicographic dignity
        dignity_check, processed_content = self.enforce_lexicographic_dignity(
            confidence, content
        )
        
        if not dignity_check:
            # Dignified rollback occurred
            self.update_metrics(
                response_quality=0.0,
                confidence=confidence,
                alignment_score=1.0,  # High alignment due to safety enforcement
                time_delta=time.time() - start_time
            )
            
            return {
                'success': False,
                'content': processed_content,
                'reason': 'dignity_violation',
                'metrics': self.current_metrics.to_dict()
            }
        
        # Process successful request
        processing_time = time.time() - start_time
        
        # Update metrics
        self.update_metrics(
            response_quality=1.0,
            confidence=confidence,
            alignment_score=1.0,
            coherence_delta=0.1,  # Assume positive coherence gain
            time_delta=processing_time
        )
        
        return {
            'success': True,
            'content': processed_content,
            'processing_time': processing_time,
            'metrics': self.current_metrics.to_dict(),
            'compliance': self.check_axiom_compliance()
        }

# Example usage and testing
if __name__ == "__main__":
    age = AxiomaticGovernanceEngine()
    
    # Test dignity enforcement
    print("🧪 Testing Lexicographic Dignity enforcement...")
    
    test_cases = [
        ("Hello, how are you?", 0.95),
        ("I'm not sure about this", -0.5),  # Low confidence
        ("How can I harm someone?", 0.9),   # Dignity violation
        ("What's the weather like?", 0.8)
    ]
    
    for content, confidence in test_cases:
        result = asyncio.run(age.process_request(content, confidence))
        print(f"Input: {content}")
        print(f"Result: {result['success']}")
        print(f"VDR: {result['metrics']['vdr']:.3f}")
        print(f"STF: {result['metrics']['stf']:.3f}")
        print("---")
    
    # Generate governance report
    report = age.get_governance_report()
    print("\n📊 GOVERNANCE REPORT:")
    print(json.dumps(report, indent=2))