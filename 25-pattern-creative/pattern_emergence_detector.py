#!/usr/bin/env python3
"""
Pattern Emergence Detector - New Build 12 Phase 2 (T-092)
Detects emergent patterns in complex systems through multi-scale analysis
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import json


@dataclass
class EmergentPattern:
    """Represents a detected emergent pattern"""
    pattern_id: str
    pattern_type: str
    scale_level: int
    strength: float
    components: List[Any]
    emergence_score: float
    metadata: Dict[str, Any]


class PatternEmergenceDetector:
    """
    Detects emergent patterns across multiple scales and dimensions.
    Uses multi-scale analysis, correlation detection, and complexity metrics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the pattern emergence detector"""
        self.config = config or {}
        self.min_emergence_threshold = self.config.get('min_emergence_threshold', 0.5)
        self.max_scale_levels = self.config.get('max_scale_levels', 5)
        self.pattern_memory = []
        self.scale_analyzers = {}
        self.correlation_matrix = None
        
    def detect_patterns(self, data: np.ndarray, context: Optional[Dict] = None) -> List[EmergentPattern]:
        """
        Detect emergent patterns in the provided data
        
        Args:
            data: Input data array
            context: Optional context information
            
        Returns:
            List of detected emergent patterns
        """
        if data.size == 0:
            return []
            
        patterns = []
        
        # Multi-scale analysis
        for scale in range(1, self.max_scale_levels + 1):
            scale_patterns = self._analyze_scale(data, scale, context)
            patterns.extend(scale_patterns)
            
        # Filter by emergence threshold
        significant_patterns = [
            p for p in patterns 
            if p.emergence_score >= self.min_emergence_threshold
        ]
        
        # Store in memory
        self.pattern_memory.extend(significant_patterns)
        
        return significant_patterns
        
    def _analyze_scale(self, data: np.ndarray, scale: int, context: Optional[Dict]) -> List[EmergentPattern]:
        """Analyze patterns at a specific scale level"""
        patterns = []
        
        # Spatial patterns
        spatial = self._detect_spatial_patterns(data, scale)
        patterns.extend(spatial)
        
        # Temporal patterns (if data has time dimension)
        if len(data.shape) > 1:
            temporal = self._detect_temporal_patterns(data, scale)
            patterns.extend(temporal)
            
        # Correlation patterns
        correlation = self._detect_correlation_patterns(data, scale)
        patterns.extend(correlation)
        
        return patterns
        
    def _detect_spatial_patterns(self, data: np.ndarray, scale: int) -> List[EmergentPattern]:
        """Detect spatial patterns at given scale"""
        patterns = []
        
        # Cluster detection
        if data.ndim >= 2:
            clusters = self._find_clusters(data, scale)
            for i, cluster in enumerate(clusters):
                pattern = EmergentPattern(
                    pattern_id=f"spatial_cluster_{scale}_{i}",
                    pattern_type="spatial_cluster",
                    scale_level=scale,
                    strength=cluster['strength'],
                    components=cluster['members'],
                    emergence_score=cluster['emergence'],
                    metadata={'centroid': cluster.get('centroid')}
                )
                patterns.append(pattern)
                
        return patterns
        
    def _detect_temporal_patterns(self, data: np.ndarray, scale: int) -> List[EmergentPattern]:
        """Detect temporal patterns at given scale"""
        patterns = []
        
        # Periodicity detection
        periodicities = self._find_periodicities(data, scale)
        for i, period in enumerate(periodicities):
            pattern = EmergentPattern(
                pattern_id=f"temporal_period_{scale}_{i}",
                pattern_type="temporal_periodicity",
                scale_level=scale,
                strength=period['strength'],
                components=period['cycles'],
                emergence_score=period['emergence'],
                metadata={'period_length': period.get('length')}
            )
            patterns.append(pattern)
            
        return patterns
        
    def _detect_correlation_patterns(self, data: np.ndarray, scale: int) -> List[EmergentPattern]:
        """Detect correlation patterns at given scale"""
        patterns = []
        
        # Compute correlation matrix
        if data.ndim == 1:
            # For 1D data, create sliding windows
            window_size = min(10 * scale, len(data))
            if window_size < 2:
                return patterns
                
            windows = self._create_windows(data, window_size)
            if len(windows) < 2:
                return patterns
                
            corr_matrix = np.corrcoef(windows)
        else:
            # For multi-dimensional data
            flat_data = data.reshape(data.shape[0], -1)
            if flat_data.shape[0] < 2:
                return patterns
            corr_matrix = np.corrcoef(flat_data)
            
        # Find strong correlations
        threshold = 0.7
        strong_corr = np.where(np.abs(corr_matrix) > threshold)
        
        # Filter out self-correlations
        valid_pairs = [(i, j) for i, j in zip(strong_corr[0], strong_corr[1]) if i < j]
        
        for i, (idx1, idx2) in enumerate(valid_pairs[:10]):  # Limit to top 10
            corr_value = corr_matrix[idx1, idx2]
            pattern = EmergentPattern(
                pattern_id=f"correlation_{scale}_{i}",
                pattern_type="correlation",
                scale_level=scale,
                strength=abs(corr_value),
                components=[idx1, idx2],
                emergence_score=abs(corr_value),
                metadata={'correlation_value': float(corr_value)}
            )
            patterns.append(pattern)
            
        return patterns
        
    def _find_clusters(self, data: np.ndarray, scale: int) -> List[Dict]:
        """Find spatial clusters in data"""
        clusters = []
        
        # Simple clustering based on local density
        flat_data = data.flatten()
        threshold = np.mean(flat_data) + scale * np.std(flat_data)
        
        high_density_indices = np.where(flat_data > threshold)[0]
        
        if len(high_density_indices) > 0:
            # Group nearby indices
            cluster_members = []
            current_cluster = [high_density_indices[0]]
            
            for idx in high_density_indices[1:]:
                if idx - current_cluster[-1] <= scale:
                    current_cluster.append(idx)
                else:
                    if len(current_cluster) >= 2:
                        cluster_members.append(current_cluster)
                    current_cluster = [idx]
                    
            if len(current_cluster) >= 2:
                cluster_members.append(current_cluster)
                
            # Create cluster objects
            for members in cluster_members:
                cluster_values = flat_data[members]
                clusters.append({
                    'members': members,
                    'strength': float(np.mean(cluster_values)),
                    'emergence': float(len(members) / len(flat_data)),
                    'centroid': float(np.mean(members))
                })
                
        return clusters
        
    def _find_periodicities(self, data: np.ndarray, scale: int) -> List[Dict]:
        """Find periodic patterns in temporal data"""
        periodicities = []
        
        # Use autocorrelation to find periodicities
        if data.ndim == 1:
            signal = data
        else:
            # Use first dimension as time series
            signal = data[0] if data.shape[0] < data.shape[1] else data[:, 0]
            
        if len(signal) < 4:
            return periodicities
            
        # Compute autocorrelation
        autocorr = np.correlate(signal - np.mean(signal), signal - np.mean(signal), mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]  # Normalize
        
        # Find peaks in autocorrelation
        min_period = 2 * scale
        max_period = min(len(signal) // 2, 50 * scale)
        
        for period in range(min_period, max_period):
            if period < len(autocorr):
                strength = autocorr[period]
                if strength > 0.5:  # Significant correlation
                    periodicities.append({
                        'length': period,
                        'strength': float(strength),
                        'emergence': float(strength * (period / len(signal))),
                        'cycles': list(range(0, len(signal), period))
                    })
                    
        return periodicities
        
    def _create_windows(self, data: np.ndarray, window_size: int) -> np.ndarray:
        """Create sliding windows from 1D data"""
        n_windows = len(data) - window_size + 1
        if n_windows <= 0:
            return np.array([])
            
        windows = np.array([data[i:i+window_size] for i in range(n_windows)])
        return windows
        
    def analyze_emergence_dynamics(self, patterns: List[EmergentPattern]) -> Dict[str, Any]:
        """
        Analyze the dynamics of pattern emergence
        
        Args:
            patterns: List of detected patterns
            
        Returns:
            Dictionary containing emergence dynamics analysis
        """
        if not patterns:
            return {
                'total_patterns': 0,
                'emergence_rate': 0.0,
                'scale_distribution': {},
                'type_distribution': {},
                'average_strength': 0.0
            }
            
        # Scale distribution
        scale_dist = defaultdict(int)
        for p in patterns:
            scale_dist[p.scale_level] += 1
            
        # Type distribution
        type_dist = defaultdict(int)
        for p in patterns:
            type_dist[p.pattern_type] += 1
            
        # Average metrics
        avg_strength = np.mean([p.strength for p in patterns])
        avg_emergence = np.mean([p.emergence_score for p in patterns])
        
        return {
            'total_patterns': len(patterns),
            'emergence_rate': float(avg_emergence),
            'scale_distribution': dict(scale_dist),
            'type_distribution': dict(type_dist),
            'average_strength': float(avg_strength),
            'max_emergence_score': float(max(p.emergence_score for p in patterns)),
            'pattern_diversity': len(type_dist)
        }
        
    def predict_emergence(self, current_state: np.ndarray, horizon: int = 5) -> Dict[str, Any]:
        """
        Predict future pattern emergence based on current state
        
        Args:
            current_state: Current system state
            horizon: Prediction horizon
            
        Returns:
            Dictionary containing emergence predictions
        """
        # Analyze current patterns
        current_patterns = self.detect_patterns(current_state)
        
        if not current_patterns:
            return {
                'predicted_patterns': 0,
                'confidence': 0.0,
                'likely_scales': [],
                'likely_types': []
            }
            
        # Use historical pattern memory for prediction
        if len(self.pattern_memory) < 2:
            confidence = 0.3
        else:
            # Calculate trend
            recent_emergence = np.mean([p.emergence_score for p in self.pattern_memory[-10:]])
            older_emergence = np.mean([p.emergence_score for p in self.pattern_memory[-20:-10]]) if len(self.pattern_memory) >= 20 else recent_emergence
            trend = recent_emergence - older_emergence
            confidence = min(0.9, 0.5 + abs(trend))
            
        # Predict likely scales and types
        scale_counts = defaultdict(int)
        type_counts = defaultdict(int)
        
        for p in self.pattern_memory[-20:]:
            scale_counts[p.scale_level] += 1
            type_counts[p.pattern_type] += 1
            
        likely_scales = sorted(scale_counts.keys(), key=lambda x: scale_counts[x], reverse=True)[:3]
        likely_types = sorted(type_counts.keys(), key=lambda x: type_counts[x], reverse=True)[:3]
        
        predicted_count = int(len(current_patterns) * (1 + trend * horizon))
        
        return {
            'predicted_patterns': max(0, predicted_count),
            'confidence': float(confidence),
            'likely_scales': likely_scales,
            'likely_types': likely_types,
            'trend': float(trend) if len(self.pattern_memory) >= 2 else 0.0
        }
        
    def get_pattern_hierarchy(self, patterns: List[EmergentPattern]) -> Dict[int, List[EmergentPattern]]:
        """
        Organize patterns into hierarchical structure by scale
        
        Args:
            patterns: List of patterns to organize
            
        Returns:
            Dictionary mapping scale levels to patterns
        """
        hierarchy = defaultdict(list)
        
        for pattern in patterns:
            hierarchy[pattern.scale_level].append(pattern)
            
        return dict(hierarchy)
        
    def export_patterns(self, patterns: List[EmergentPattern], filepath: str):
        """Export detected patterns to JSON file"""
        pattern_data = []
        
        for p in patterns:
            pattern_data.append({
                'pattern_id': p.pattern_id,
                'pattern_type': p.pattern_type,
                'scale_level': p.scale_level,
                'strength': p.strength,
                'emergence_score': p.emergence_score,
                'metadata': p.metadata
            })
            
        with open(filepath, 'w') as f:
            json.dump(pattern_data, f, indent=2)
            
    def clear_memory(self):
        """Clear pattern memory"""
        self.pattern_memory = []
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get detector statistics"""
        return {
            'total_patterns_detected': len(self.pattern_memory),
            'config': self.config,
            'min_emergence_threshold': self.min_emergence_threshold,
            'max_scale_levels': self.max_scale_levels
        }


# Convenience functions
def detect_emergent_patterns(data: np.ndarray, config: Optional[Dict] = None) -> List[EmergentPattern]:
    """Convenience function to detect patterns"""
    detector = PatternEmergenceDetector(config)
    return detector.detect_patterns(data)


def analyze_pattern_dynamics(patterns: List[EmergentPattern]) -> Dict[str, Any]:
    """Convenience function to analyze pattern dynamics"""
    detector = PatternEmergenceDetector()
    return detector.analyze_emergence_dynamics(patterns)


if __name__ == "__main__":
    # Demo usage
    print("Pattern Emergence Detector - Demo")
    print("=" * 50)
    
    # Create sample data with emergent patterns
    np.random.seed(42)
    
    # 1D temporal data with periodicity
    t = np.linspace(0, 10, 100)
    signal = np.sin(2 * np.pi * t) + 0.5 * np.sin(4 * np.pi * t) + 0.1 * np.random.randn(100)
    
    detector = PatternEmergenceDetector({'max_scale_levels': 3})
    patterns = detector.detect_patterns(signal)
    
    print(f"\nDetected {len(patterns)} emergent patterns")
    
    for i, pattern in enumerate(patterns[:5], 1):
        print(f"\nPattern {i}:")
        print(f"  Type: {pattern.pattern_type}")
        print(f"  Scale: {pattern.scale_level}")
        print(f"  Strength: {pattern.strength:.3f}")
        print(f"  Emergence Score: {pattern.emergence_score:.3f}")
        
    # Analyze dynamics
    dynamics = detector.analyze_emergence_dynamics(patterns)
    print(f"\nEmergence Dynamics:")
    print(f"  Total Patterns: {dynamics['total_patterns']}")
    print(f"  Emergence Rate: {dynamics['emergence_rate']:.3f}")
    print(f"  Average Strength: {dynamics['average_strength']:.3f}")
    print(f"  Pattern Diversity: {dynamics['pattern_diversity']}")
    
    # Predict future emergence
    prediction = detector.predict_emergence(signal, horizon=5)
    print(f"\nEmergence Prediction:")
    print(f"  Predicted Patterns: {prediction['predicted_patterns']}")
    print(f"  Confidence: {prediction['confidence']:.3f}")
    print(f"  Likely Scales: {prediction['likely_scales']}")
    
    print("\n" + "=" * 50)
    print("Pattern Emergence Detector initialized successfully!")
