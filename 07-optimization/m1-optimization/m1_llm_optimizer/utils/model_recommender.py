#!/usr/bin/env python3
"""
Model Recommendation Engine
Provides intelligent model recommendations based on system constraints
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ModelRecommendationEngine:
    """Intelligent model recommendation based on hardware constraints"""
    
    def __init__(self, ram_gb: float):
        self.ram_gb = ram_gb
        self.model_database = self._load_model_database()
        
    def _load_model_database(self) -> Dict:
        """Load comprehensive model database"""
        return {
            'llama3.2:3b': {
                'parameters': '3B',
                'quantizations': {
                    'q4_K_M': {'size_gb': 2.0, 'quality': 'good'},
                    'q5_K_M': {'size_gb': 2.5, 'quality': 'very_good'},
                    'q8_0': {'size_gb': 3.0, 'quality': 'excellent'},
                },
                'use_cases': ['general', 'chat', 'quick_queries'],
                'speed': 'very_fast',
                'min_ram_gb': 4,
            },
            'phi3:3.8b': {
                'parameters': '3.8B',
                'quantizations': {
                    'q4_K_M': {'size_gb': 2.3, 'quality': 'good'},
                    'q5_K_M': {'size_gb': 2.8, 'quality': 'very_good'},
                },
                'use_cases': ['reasoning', 'chat', 'analysis'],
                'speed': 'fast',
                'min_ram_gb': 6,
            },
            'mistral:7b': {
                'parameters': '7B',
                'quantizations': {
                    'q4_K_M': {'size_gb': 4.1, 'quality': 'good'},
                    'q5_K_M': {'size_gb': 5.0, 'quality': 'very_good'},
                    'q8_0': {'size_gb': 7.7, 'quality': 'excellent'},
                },
                'use_cases': ['reasoning', 'code', 'analysis'],
                'speed': 'moderate',
                'min_ram_gb': 8,
            },
            'llama3.1:8b': {
                'parameters': '8B',
                'quantizations': {
                    'q4_K_M': {'size_gb': 4.7, 'quality': 'good'},
                    'q5_K_M': {'size_gb': 5.5, 'quality': 'very_good'},
                    'q8_0': {'size_gb': 8.5, 'quality': 'excellent'},
                },
                'use_cases': ['general', 'chat', 'reasoning'],
                'speed': 'moderate',
                'min_ram_gb': 10,
            },
            'codellama:7b': {
                'parameters': '7B',
                'quantizations': {
                    'q4_K_M': {'size_gb': 4.0, 'quality': 'good'},
                    'q5_K_M': {'size_gb': 5.0, 'quality': 'very_good'},
                },
                'use_cases': ['code', 'programming', 'debugging'],
                'speed': 'moderate',
                'min_ram_gb': 8,
            },
            'codellama:13b': {
                'parameters': '13B',
                'quantizations': {
                    'q4_K_M': {'size_gb': 7.4, 'quality': 'good'},
                    'q5_K_M': {'size_gb': 9.0, 'quality': 'very_good'},
                },
                'use_cases': ['code', 'advanced_programming'],
                'speed': 'slow',
                'min_ram_gb': 16,
            },
            'mixtral:8x7b': {
                'parameters': '47B (8x7B MoE)',
                'quantizations': {
                    'q4_K_M': {'size_gb': 26.0, 'quality': 'good'},
                },
                'use_cases': ['advanced_reasoning', 'complex_tasks'],
                'speed': 'slow',
                'min_ram_gb': 32,
            },
            'gemma2:9b': {
                'parameters': '9B',
                'quantizations': {
                    'q4_K_M': {'size_gb': 5.5, 'quality': 'good'},
                    'q5_K_M': {'size_gb': 6.5, 'quality': 'very_good'},
                },
                'use_cases': ['general', 'reasoning'],
                'speed': 'moderate',
                'min_ram_gb': 12,
            },
        }
    
    def get_recommendations(self, use_case: Optional[str] = None, max_models: int = 5) -> List[Dict]:
        """Get model recommendations based on RAM and use case"""
        recommendations = []
        
        # Calculate available RAM for model (accounting for OS overhead)
        if self.ram_gb <= 8:
            available_ram = self.ram_gb - 2.5  # Conservative overhead
            max_context = 2048
        elif self.ram_gb <= 16:
            available_ram = self.ram_gb - 3.0
            max_context = 4096
        else:
            available_ram = self.ram_gb - 4.0
            max_context = 8192
        
        for model_name, model_info in self.model_database.items():
            # Check if model meets minimum RAM requirement
            if model_info['min_ram_gb'] > self.ram_gb:
                continue
            
            # Filter by use case if specified
            if use_case and use_case not in model_info['use_cases']:
                continue
            
            # Find best quantization that fits
            best_quant = None
            for quant_name, quant_info in model_info['quantizations'].items():
                if quant_info['size_gb'] <= available_ram:
                    if best_quant is None or quant_info['quality'] > best_quant['quality']:
                        best_quant = {
                            'name': quant_name,
                            **quant_info
                        }
            
            if best_quant:
                recommendations.append({
                    'model': model_name,
                    'full_name': f"{model_name}-{best_quant['name']}",
                    'parameters': model_info['parameters'],
                    'quantization': best_quant['name'],
                    'size_gb': best_quant['size_gb'],
                    'quality': best_quant['quality'],
                    'use_cases': model_info['use_cases'],
                    'speed': model_info['speed'],
                    'recommended_context': max_context,
                    'pull_command': f"ollama pull {model_name}",
                })
        
        # Sort by quality and size
        recommendations.sort(key=lambda x: (x['quality'], -x['size_gb']), reverse=True)
        
        return recommendations[:max_models]
    
    def get_recommendation_by_use_case(self) -> Dict[str, List[Dict]]:
        """Get recommendations organized by use case"""
        use_cases = ['general', 'chat', 'code', 'reasoning', 'analysis']
        
        recommendations = {}
        for use_case in use_cases:
            recommendations[use_case] = self.get_recommendations(use_case=use_case, max_models=3)
        
        return recommendations
    
    def calculate_context_window_overhead(self, context_size: int) -> float:
        """Calculate RAM overhead for context window"""
        # Approximate: 1 token ≈ 2 bytes in KV cache
        # This is a rough estimate and varies by model
        return (context_size * 2) / (1024**3)  # Convert to GB
    
    def recommend_context_size(self, model_size_gb: float) -> int:
        """Recommend safe context window size"""
        available_for_context = self.ram_gb - model_size_gb - 2.0  # OS overhead
        
        if available_for_context < 0.5:
            return 1024
        elif available_for_context < 1.0:
            return 2048
        elif available_for_context < 2.0:
            return 4096
        elif available_for_context < 4.0:
            return 8192
        else:
            return 16384
    
    def print_recommendations(self, recommendations: List[Dict]):
        """Print formatted recommendations"""
        print("\n" + "="*70)
        print(f"MODEL RECOMMENDATIONS FOR {self.ram_gb}GB RAM")
        print("="*70)
        
        if not recommendations:
            print("\nNo suitable models found for your RAM configuration.")
            print("Consider upgrading RAM or using cloud-based LLM services.")
            print("\n" + "="*70 + "\n")
            return
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['model']} ({rec['parameters']})")
            print(f"   Quantization: {rec['quantization']}")
            print(f"   Size: {rec['size_gb']}GB")
            print(f"   Quality: {rec['quality']}")
            print(f"   Speed: {rec['speed']}")
            print(f"   Use Cases: {', '.join(rec['use_cases'])}")
            print(f"   Recommended Context: {rec['recommended_context']} tokens")
            print(f"   Pull Command: {rec['pull_command']}")
        
        print("\n" + "="*70)
        print("\nIMPORTANT NOTES:")
        
        if self.ram_gb <= 8:
            print("  ⚠️  8GB RAM: Stick to Q4_K_M quantization")
            print("  ⚠️  Avoid models larger than 7B parameters")
            print("  ⚠️  Keep context window at 2048 tokens or less")
            print("  ⚠️  Close all unnecessary applications before inference")
        elif self.ram_gb <= 16:
            print("  ✓ 16GB RAM: Q5_K_M quantization is safe")
            print("  ✓ 7B-8B models work well")
            print("  ✓ Context up to 4096 tokens is safe")
            print("  • Monitor memory pressure during first use")
        else:
            print("  ✓ >16GB RAM: Q8_0 quantization available")
            print("  ✓ Can use larger models (13B+)")
            print("  ✓ Context up to 8192 tokens is safe")
            print("  ✓ Can experiment with multiple loaded models")
        
        print("\n" + "="*70 + "\n")
    
    def print_use_case_recommendations(self):
        """Print recommendations organized by use case"""
        recommendations = self.get_recommendation_by_use_case()
        
        print("\n" + "="*70)
        print(f"MODEL RECOMMENDATIONS BY USE CASE ({self.ram_gb}GB RAM)")
        print("="*70)
        
        for use_case, models in recommendations.items():
            if models:
                print(f"\n{use_case.upper().replace('_', ' ')}:")
                for model in models:
                    print(f"  • {model['model']} ({model['quantization']}) - {model['size_gb']}GB")
        
        print("\n" + "="*70 + "\n")
    
    def export_recommendations(self, output_path: Path) -> bool:
        """Export recommendations to JSON file"""
        try:
            recommendations = self.get_recommendations(max_models=10)
            
            data = {
                'system_ram_gb': self.ram_gb,
                'recommendations': recommendations,
                'use_case_recommendations': self.get_recommendation_by_use_case(),
            }
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Recommendations exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export recommendations: {e}")
            return False


def main():
    """Main model recommender utility"""
    import argparse
    import subprocess
    
    parser = argparse.ArgumentParser(description='M1 Model Recommendation Engine')
    parser.add_argument('--ram', type=float, help='RAM in GB (auto-detected if not specified)')
    parser.add_argument('--use-case', choices=['general', 'chat', 'code', 'reasoning', 'analysis'],
                       help='Filter by use case')
    parser.add_argument('--by-use-case', action='store_true', help='Show recommendations by use case')
    parser.add_argument('--export', metavar='FILE', help='Export recommendations to JSON file')
    
    args = parser.parse_args()
    
    # Auto-detect RAM if not specified
    if args.ram:
        ram_gb = args.ram
    else:
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'hw.memsize'],
                capture_output=True, text=True, check=True
            )
            ram_gb = int(result.stdout.strip()) / (1024**3)
        except:
            print("Error: Could not detect RAM. Please specify with --ram")
            return
    
    engine = ModelRecommendationEngine(ram_gb)
    
    if args.by_use_case:
        engine.print_use_case_recommendations()
    else:
        recommendations = engine.get_recommendations(use_case=args.use_case)
        engine.print_recommendations(recommendations)
    
    if args.export:
        engine.export_recommendations(Path(args.export))


if __name__ == '__main__':
    main()
