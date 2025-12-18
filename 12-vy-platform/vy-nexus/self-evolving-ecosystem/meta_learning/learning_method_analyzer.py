#!/usr/bin/env python3
"""
Learning Method Analyzer
Analyzes effectiveness of different learning methods and strategies
Part of the Self-Evolving AI Ecosystem
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import statistics

class LearningMethodAnalyzer:
    """Analyzes and optimizes learning methods"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem")
        self.data_dir = self.base_dir / "data" / "meta_learning"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Learning method tracking
        self.methods_file = self.data_dir / "learning_methods.jsonl"
        self.experiments_file = self.data_dir / "learning_experiments.jsonl"
        self.effectiveness_file = self.data_dir / "method_effectiveness.jsonl"
        
        # Learning method categories
        self.method_categories = {
            "observation": "Learning by observing user behavior",
            "feedback": "Learning from explicit user feedback",
            "experimentation": "Learning through A/B testing and experiments",
            "pattern_recognition": "Learning by identifying patterns in data",
            "reinforcement": "Learning from success/failure outcomes",
            "transfer": "Applying knowledge from one domain to another",
            "collaborative": "Learning from other AI instances or users",
            "self_reflection": "Learning by analyzing own performance"
        }
        
        # Effectiveness metrics
        self.effectiveness_metrics = [
            "accuracy",
            "speed",
            "retention",
            "applicability",
            "scalability",
            "user_satisfaction"
        ]
        
        self._initialized = True
    
    def register_learning_method(
        self,
        method_id: str,
        name: str,
        category: str,
        description: str,
        parameters: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Register a learning method for analysis"""
        
        if category not in self.method_categories:
            return {
                "success": False,
                "error": f"Invalid category: {category}"
            }
        
        method = {
            "method_id": method_id,
            "name": name,
            "category": category,
            "description": description,
            "parameters": parameters or {},
            "registered_at": datetime.now().isoformat(),
            "usage_count": 0,
            "total_learning_instances": 0,
            "metadata": metadata or {}
        }
        
        # Save method
        with open(self.methods_file, 'a') as f:
            f.write(json.dumps(method) + '\n')
        
        return {
            "success": True,
            "method_id": method_id,
            "method": method
        }
    
    def record_learning_instance(
        self,
        method_id: str,
        context: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        success: bool,
        metrics: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Record a learning instance for analysis"""
        
        instance = {
            "instance_id": f"learn_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "method_id": method_id,
            "context": context,
            "input_data": input_data,
            "output_data": output_data,
            "success": success,
            "metrics": metrics or {},
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Save instance
        with open(self.experiments_file, 'a') as f:
            f.write(json.dumps(instance) + '\n')
        
        # Update method usage
        method = self._load_method(method_id)
        if method:
            method["usage_count"] = method.get("usage_count", 0) + 1
            method["total_learning_instances"] = method.get("total_learning_instances", 0) + 1
            method["last_used"] = datetime.now().isoformat()
            
            with open(self.methods_file, 'a') as f:
                f.write(json.dumps(method) + '\n')
        
        return {
            "success": True,
            "instance_id": instance["instance_id"]
        }
    
    def analyze_method_effectiveness(
        self,
        method_id: str,
        time_window_hours: int = 168  # 1 week default
    ) -> Dict[str, Any]:
        """Analyze effectiveness of a learning method"""
        
        method = self._load_method(method_id)
        if not method:
            return {"success": False, "error": "Method not found"}
        
        # Get learning instances within time window
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        instances = self._get_method_instances(method_id, cutoff_time)
        
        if not instances:
            return {
                "success": True,
                "method_id": method_id,
                "effectiveness": None,
                "message": "No learning instances in time window"
            }
        
        # Calculate effectiveness metrics
        effectiveness = self._calculate_effectiveness(instances)
        
        # Calculate trends
        trends = self._calculate_trends(instances)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(method, effectiveness, trends)
        
        # Save effectiveness analysis
        analysis = {
            "method_id": method_id,
            "time_window_hours": time_window_hours,
            "instance_count": len(instances),
            "effectiveness": effectiveness,
            "trends": trends,
            "recommendations": recommendations,
            "analyzed_at": datetime.now().isoformat()
        }
        
        with open(self.effectiveness_file, 'a') as f:
            f.write(json.dumps(analysis) + '\n')
        
        return {
            "success": True,
            "method_id": method_id,
            "analysis": analysis
        }
    
    def _calculate_effectiveness(self, instances: List[Dict]) -> Dict[str, Any]:
        """Calculate effectiveness metrics from instances"""
        
        total = len(instances)
        successful = sum(1 for i in instances if i.get("success"))
        
        effectiveness = {
            "success_rate": successful / total if total > 0 else 0,
            "total_instances": total,
            "successful_instances": successful,
            "failed_instances": total - successful
        }
        
        # Aggregate custom metrics
        metric_values = defaultdict(list)
        for instance in instances:
            for metric, value in instance.get("metrics", {}).items():
                if isinstance(value, (int, float)):
                    metric_values[metric].append(value)
        
        # Calculate statistics for each metric
        for metric, values in metric_values.items():
            if values:
                effectiveness[f"{metric}_mean"] = statistics.mean(values)
                effectiveness[f"{metric}_median"] = statistics.median(values)
                if len(values) > 1:
                    effectiveness[f"{metric}_stdev"] = statistics.stdev(values)
        
        # Calculate learning speed (time to success)
        success_times = []
        for i, instance in enumerate(instances):
            if instance.get("success"):
                success_times.append(i + 1)  # Position in sequence
        
        if success_times:
            effectiveness["avg_time_to_success"] = statistics.mean(success_times)
        
        return effectiveness
    
    def _calculate_trends(self, instances: List[Dict]) -> Dict[str, Any]:
        """Calculate trends in learning effectiveness over time"""
        
        if len(instances) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort by timestamp
        sorted_instances = sorted(instances, key=lambda x: x.get("timestamp", ""))
        
        # Split into early and late periods
        mid_point = len(sorted_instances) // 2
        early_instances = sorted_instances[:mid_point]
        late_instances = sorted_instances[mid_point:]
        
        # Calculate success rates for each period
        early_success_rate = sum(1 for i in early_instances if i.get("success")) / len(early_instances)
        late_success_rate = sum(1 for i in late_instances if i.get("success")) / len(late_instances)
        
        # Determine trend
        improvement = late_success_rate - early_success_rate
        
        trend = {
            "early_success_rate": early_success_rate,
            "late_success_rate": late_success_rate,
            "improvement": improvement,
            "trend_direction": "improving" if improvement > 0.05 else "declining" if improvement < -0.05 else "stable"
        }
        
        return trend
    
    def _generate_recommendations(self, method: Dict, effectiveness: Dict, trends: Dict) -> List[str]:
        """Generate recommendations for improving learning method"""
        
        recommendations = []
        
        success_rate = effectiveness.get("success_rate", 0)
        trend_direction = trends.get("trend_direction", "unknown")
        
        # Success rate recommendations
        if success_rate < 0.5:
            recommendations.append("Low success rate - consider revising method parameters or approach")
        elif success_rate > 0.8:
            recommendations.append("High success rate - method is effective, consider expanding usage")
        
        # Trend recommendations
        if trend_direction == "declining":
            recommendations.append("Performance declining - investigate recent changes or environmental factors")
        elif trend_direction == "improving":
            recommendations.append("Performance improving - continue current approach and monitor")
        
        # Instance count recommendations
        total_instances = effectiveness.get("total_instances", 0)
        if total_instances < 10:
            recommendations.append("Limited data - collect more instances for reliable analysis")
        
        # Variability recommendations
        for metric in self.effectiveness_metrics:
            stdev_key = f"{metric}_stdev"
            mean_key = f"{metric}_mean"
            
            if stdev_key in effectiveness and mean_key in effectiveness:
                mean = effectiveness[mean_key]
                stdev = effectiveness[stdev_key]
                
                if mean > 0 and (stdev / mean) > 0.5:
                    recommendations.append(f"High variability in {metric} - consider standardizing approach")
        
        if not recommendations:
            recommendations.append("Method performing adequately - continue monitoring")
        
        return recommendations
    
    def compare_methods(
        self,
        method_ids: List[str],
        time_window_hours: int = 168
    ) -> Dict[str, Any]:
        """Compare effectiveness of multiple learning methods"""
        
        comparisons = []
        
        for method_id in method_ids:
            analysis = self.analyze_method_effectiveness(method_id, time_window_hours)
            if analysis.get("success") and analysis.get("analysis"):
                comparisons.append({
                    "method_id": method_id,
                    "analysis": analysis["analysis"]
                })
        
        if not comparisons:
            return {
                "success": False,
                "error": "No valid method analyses available"
            }
        
        # Rank methods by success rate
        ranked = sorted(
            comparisons,
            key=lambda x: x["analysis"]["effectiveness"].get("success_rate", 0),
            reverse=True
        )
        
        # Identify best and worst performers
        best_method = ranked[0] if ranked else None
        worst_method = ranked[-1] if ranked else None
        
        return {
            "success": True,
            "comparisons": comparisons,
            "ranked": ranked,
            "best_method": best_method["method_id"] if best_method else None,
            "worst_method": worst_method["method_id"] if worst_method else None,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def get_optimal_method_for_context(
        self,
        context: str,
        min_instances: int = 5
    ) -> Optional[str]:
        """Get the most effective learning method for a given context"""
        
        # Get all instances for this context
        context_instances = defaultdict(list)
        
        if self.experiments_file.exists():
            with open(self.experiments_file, 'r') as f:
                for line in f:
                    instance = json.loads(line.strip())
                    if instance.get("context") == context:
                        method_id = instance.get("method_id")
                        context_instances[method_id].append(instance)
        
        # Calculate success rates for each method
        method_scores = {}
        for method_id, instances in context_instances.items():
            if len(instances) >= min_instances:
                success_rate = sum(1 for i in instances if i.get("success")) / len(instances)
                method_scores[method_id] = success_rate
        
        if not method_scores:
            return None
        
        # Return method with highest success rate
        return max(method_scores.items(), key=lambda x: x[1])[0]
    
    def _get_method_instances(
        self,
        method_id: str,
        cutoff_time: datetime
    ) -> List[Dict]:
        """Get learning instances for a method after cutoff time"""
        
        instances = []
        
        if self.experiments_file.exists():
            with open(self.experiments_file, 'r') as f:
                for line in f:
                    instance = json.loads(line.strip())
                    if instance.get("method_id") == method_id:
                        timestamp = datetime.fromisoformat(instance.get("timestamp", ""))
                        if timestamp >= cutoff_time:
                            instances.append(instance)
        
        return instances
    
    def _load_method(self, method_id: str) -> Optional[Dict]:
        """Load a learning method by ID"""
        
        if not self.methods_file.exists():
            return None
        
        methods = []
        with open(self.methods_file, 'r') as f:
            for line in f:
                method = json.loads(line.strip())
                if method.get("method_id") == method_id:
                    methods.append(method)
        
        if not methods:
            return None
        
        # Return most recent version
        return max(methods, key=lambda x: x.get("registered_at", ""))
    
    def get_all_methods(self) -> List[Dict[str, Any]]:
        """Get all registered learning methods"""
        
        methods = {}
        
        if self.methods_file.exists():
            with open(self.methods_file, 'r') as f:
                for line in f:
                    method = json.loads(line.strip())
                    method_id = method.get("method_id")
                    
                    # Keep only latest version
                    if method_id not in methods or \
                       method.get("registered_at", "") > methods[method_id].get("registered_at", ""):
                        methods[method_id] = method
        
        return list(methods.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning method statistics"""
        
        stats = {
            "total_methods": 0,
            "by_category": {},
            "total_learning_instances": 0,
            "most_used_methods": [],
            "most_effective_methods": []
        }
        
        methods = self.get_all_methods()
        stats["total_methods"] = len(methods)
        
        for method in methods:
            category = method.get("category", "unknown")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            stats["total_learning_instances"] += method.get("total_learning_instances", 0)
        
        # Most used methods
        most_used = sorted(
            methods,
            key=lambda x: x.get("usage_count", 0),
            reverse=True
        )[:5]
        
        stats["most_used_methods"] = [
            {
                "method_id": m["method_id"],
                "name": m["name"],
                "usage_count": m.get("usage_count", 0)
            }
            for m in most_used
        ]
        
        # Analyze effectiveness for top methods
        effectiveness_scores = []
        for method in methods:
            if method.get("total_learning_instances", 0) >= 5:
                analysis = self.analyze_method_effectiveness(method["method_id"])
                if analysis.get("success") and analysis.get("analysis"):
                    effectiveness = analysis["analysis"]["effectiveness"]
                    effectiveness_scores.append({
                        "method_id": method["method_id"],
                        "name": method["name"],
                        "success_rate": effectiveness.get("success_rate", 0)
                    })
        
        stats["most_effective_methods"] = sorted(
            effectiveness_scores,
            key=lambda x: x["success_rate"],
            reverse=True
        )[:5]
        
        return stats

def get_analyzer() -> LearningMethodAnalyzer:
    """Get the singleton LearningMethodAnalyzer instance"""
    return LearningMethodAnalyzer()

if __name__ == "__main__":
    # Example usage
    analyzer = get_analyzer()
    
    # Register a test learning method
    result = analyzer.register_learning_method(
        method_id="observation_001",
        name="User Behavior Observation",
        category="observation",
        description="Learn by observing user interaction patterns"
    )
    
    print(f"Method registered: {json.dumps(result, indent=2)}")
    print(f"\nStatistics: {json.dumps(analyzer.get_statistics(), indent=2)}")
