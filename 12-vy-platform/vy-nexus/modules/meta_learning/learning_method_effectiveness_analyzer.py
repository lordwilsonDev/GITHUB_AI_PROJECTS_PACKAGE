#!/usr/bin/env python3
"""
Learning Method Effectiveness Analyzer

Analyzes the effectiveness of different learning methods and strategies
to optimize the learning process itself (meta-learning).

Features:
- Track learning method performance
- Compare learning strategies
- Identify most effective approaches
- Optimize learning parameters
- Generate effectiveness reports
- Recommend best practices
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict


class LearningMethodEffectivenessAnalyzer:
    """Analyzes and optimizes learning method effectiveness."""
    
    def __init__(self, base_dir: str = "~/vy-nexus/data/meta_learning"):
        self.base_dir = Path(base_dir).expanduser()
        self.methods_file = self.base_dir / "learning_methods.json"
        self.effectiveness_file = self.base_dir / "method_effectiveness.json"
        self.experiments_file = self.base_dir / "learning_experiments.json"
        self.recommendations_file = self.base_dir / "method_recommendations.json"
        
        # Create directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.methods = self._load_methods()
        self.effectiveness_data = self._load_effectiveness()
        self.experiments = self._load_experiments()
        self.recommendations = self._load_recommendations()
    
    def _load_methods(self) -> Dict:
        """Load learning methods registry."""
        if self.methods_file.exists():
            with open(self.methods_file, 'r') as f:
                return json.load(f)
        return {
            "methods": {},
            "categories": [
                "supervised",
                "unsupervised",
                "reinforcement",
                "transfer",
                "active",
                "meta"
            ],
            "last_updated": None
        }
    
    def _save_methods(self):
        """Save learning methods registry."""
        self.methods["last_updated"] = datetime.now().isoformat()
        with open(self.methods_file, 'w') as f:
            json.dump(self.methods, f, indent=2)
    
    def _load_effectiveness(self) -> Dict:
        """Load effectiveness data."""
        if self.effectiveness_file.exists():
            with open(self.effectiveness_file, 'r') as f:
                return json.load(f)
        return {
            "method_scores": {},
            "comparative_analysis": {},
            "last_updated": None
        }
    
    def _save_effectiveness(self):
        """Save effectiveness data."""
        self.effectiveness_data["last_updated"] = datetime.now().isoformat()
        with open(self.effectiveness_file, 'w') as f:
            json.dump(self.effectiveness_data, f, indent=2)
    
    def _load_experiments(self) -> List[Dict]:
        """Load learning experiments."""
        if self.experiments_file.exists():
            with open(self.experiments_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_experiments(self):
        """Save learning experiments."""
        with open(self.experiments_file, 'w') as f:
            json.dump(self.experiments, f, indent=2)
    
    def _load_recommendations(self) -> Dict:
        """Load method recommendations."""
        if self.recommendations_file.exists():
            with open(self.recommendations_file, 'r') as f:
                return json.load(f)
        return {
            "recommendations": [],
            "last_generated": None
        }
    
    def _save_recommendations(self):
        """Save method recommendations."""
        self.recommendations["last_generated"] = datetime.now().isoformat()
        with open(self.recommendations_file, 'w') as f:
            json.dump(self.recommendations, f, indent=2)
    
    def register_learning_method(self, method_id: str,
                                name: str,
                                category: str,
                                description: str = "",
                                parameters: Dict = None,
                                metadata: Dict = None) -> Dict:
        """Register a new learning method."""
        if method_id in self.methods["methods"]:
            return {"success": False, "error": "Method already registered"}
        
        if category not in self.methods["categories"]:
            return {"success": False, "error": f"Invalid category: {category}"}
        
        self.methods["methods"][method_id] = {
            "name": name,
            "category": category,
            "description": description,
            "parameters": parameters or {},
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "usage_count": 0,
            "total_learning_time": 0,
            "success_count": 0,
            "failure_count": 0
        }
        
        self._save_methods()
        
        return {
            "success": True,
            "method_id": method_id
        }
    
    def record_learning_session(self, method_id: str,
                               task_type: str,
                               duration_seconds: float,
                               success: bool,
                               metrics: Dict = None) -> Dict:
        """Record a learning session using a specific method."""
        if method_id not in self.methods["methods"]:
            return {"success": False, "error": "Method not found"}
        
        # Update method statistics
        method = self.methods["methods"][method_id]
        method["usage_count"] += 1
        method["total_learning_time"] += duration_seconds
        
        if success:
            method["success_count"] += 1
        else:
            method["failure_count"] += 1
        
        self._save_methods()
        
        # Record experiment
        experiment = {
            "experiment_id": f"exp_{len(self.experiments) + 1}",
            "method_id": method_id,
            "task_type": task_type,
            "duration_seconds": duration_seconds,
            "success": success,
            "metrics": metrics or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.experiments.append(experiment)
        self._save_experiments()
        
        # Update effectiveness scores
        self._update_effectiveness_scores(method_id)
        
        return {
            "success": True,
            "experiment_id": experiment["experiment_id"]
        }
    
    def _update_effectiveness_scores(self, method_id: str):
        """Update effectiveness scores for a method."""
        method = self.methods["methods"][method_id]
        
        # Calculate success rate
        total_attempts = method["success_count"] + method["failure_count"]
        success_rate = 0
        if total_attempts > 0:
            success_rate = (method["success_count"] / total_attempts) * 100
        
        # Calculate average learning time
        avg_time = 0
        if method["usage_count"] > 0:
            avg_time = method["total_learning_time"] / method["usage_count"]
        
        # Calculate efficiency score (success rate / time)
        efficiency = 0
        if avg_time > 0:
            efficiency = success_rate / (avg_time / 60)  # per minute
        
        # Get recent performance (last 10 sessions)
        recent_sessions = [
            exp for exp in self.experiments[-50:]
            if exp["method_id"] == method_id
        ][-10:]
        
        recent_success_rate = 0
        if recent_sessions:
            recent_successes = sum(1 for s in recent_sessions if s["success"])
            recent_success_rate = (recent_successes / len(recent_sessions)) * 100
        
        # Calculate overall effectiveness score
        effectiveness_score = (
            success_rate * 0.4 +  # 40% weight on overall success
            recent_success_rate * 0.3 +  # 30% weight on recent performance
            min(efficiency * 10, 100) * 0.3  # 30% weight on efficiency
        )
        
        # Store effectiveness data
        self.effectiveness_data["method_scores"][method_id] = {
            "success_rate": success_rate,
            "avg_learning_time": avg_time,
            "efficiency": efficiency,
            "recent_success_rate": recent_success_rate,
            "effectiveness_score": effectiveness_score,
            "usage_count": method["usage_count"],
            "last_updated": datetime.now().isoformat()
        }
        
        self._save_effectiveness()
    
    def compare_methods(self, method_ids: List[str],
                       task_type: str = None) -> Dict:
        """Compare effectiveness of multiple learning methods."""
        if not method_ids:
            return {"success": False, "error": "No methods specified"}
        
        # Validate methods exist
        for method_id in method_ids:
            if method_id not in self.methods["methods"]:
                return {"success": False, "error": f"Method not found: {method_id}"}
        
        comparison = {
            "methods": {},
            "rankings": {},
            "recommendations": []
        }
        
        # Get experiments for comparison
        relevant_experiments = self.experiments
        if task_type:
            relevant_experiments = [
                exp for exp in self.experiments
                if exp["task_type"] == task_type
            ]
        
        # Analyze each method
        for method_id in method_ids:
            method = self.methods["methods"][method_id]
            effectiveness = self.effectiveness_data["method_scores"].get(
                method_id,
                {"effectiveness_score": 0}
            )
            
            # Get method-specific experiments
            method_experiments = [
                exp for exp in relevant_experiments
                if exp["method_id"] == method_id
            ]
            
            # Calculate task-specific metrics
            task_success_rate = 0
            task_avg_time = 0
            
            if method_experiments:
                successes = sum(1 for exp in method_experiments if exp["success"])
                task_success_rate = (successes / len(method_experiments)) * 100
                task_avg_time = statistics.mean(
                    exp["duration_seconds"] for exp in method_experiments
                )
            
            comparison["methods"][method_id] = {
                "name": method["name"],
                "category": method["category"],
                "overall_effectiveness": effectiveness.get("effectiveness_score", 0),
                "task_success_rate": task_success_rate,
                "task_avg_time": task_avg_time,
                "total_usage": len(method_experiments)
            }
        
        # Rank methods
        comparison["rankings"] = self._rank_methods(comparison["methods"])
        
        # Generate recommendations
        comparison["recommendations"] = self._generate_comparison_recommendations(
            comparison["methods"],
            comparison["rankings"]
        )
        
        return {
            "success": True,
            "comparison": comparison,
            "task_type": task_type
        }
    
    def _rank_methods(self, methods_data: Dict) -> Dict:
        """Rank methods by different criteria."""
        rankings = {
            "by_effectiveness": [],
            "by_success_rate": [],
            "by_speed": [],
            "by_usage": []
        }
        
        # Sort by effectiveness
        rankings["by_effectiveness"] = sorted(
            methods_data.items(),
            key=lambda x: x[1]["overall_effectiveness"],
            reverse=True
        )
        
        # Sort by success rate
        rankings["by_success_rate"] = sorted(
            methods_data.items(),
            key=lambda x: x[1]["task_success_rate"],
            reverse=True
        )
        
        # Sort by speed (lower time is better)
        rankings["by_speed"] = sorted(
            methods_data.items(),
            key=lambda x: x[1]["task_avg_time"] if x[1]["task_avg_time"] > 0 else float('inf')
        )
        
        # Sort by usage
        rankings["by_usage"] = sorted(
            methods_data.items(),
            key=lambda x: x[1]["total_usage"],
            reverse=True
        )
        
        return rankings
    
    def _generate_comparison_recommendations(self, methods_data: Dict,
                                            rankings: Dict) -> List[str]:
        """Generate recommendations based on method comparison."""
        recommendations = []
        
        # Best overall method
        if rankings["by_effectiveness"]:
            best_method = rankings["by_effectiveness"][0]
            recommendations.append(
                f"Most effective method: {methods_data[best_method[0]]['name']} "
                f"(score: {best_method[1]['overall_effectiveness']:.1f})"
            )
        
        # Fastest method
        if rankings["by_speed"]:
            fastest = rankings["by_speed"][0]
            if fastest[1]["task_avg_time"] > 0:
                recommendations.append(
                    f"Fastest method: {methods_data[fastest[0]]['name']} "
                    f"(avg: {fastest[1]['task_avg_time']:.1f}s)"
                )
        
        # Most reliable method
        if rankings["by_success_rate"]:
            most_reliable = rankings["by_success_rate"][0]
            if most_reliable[1]["task_success_rate"] > 0:
                recommendations.append(
                    f"Most reliable method: {methods_data[most_reliable[0]]['name']} "
                    f"(success rate: {most_reliable[1]['task_success_rate']:.1f}%)"
                )
        
        return recommendations
    
    def analyze_learning_trends(self, days: int = 30) -> Dict:
        """Analyze learning trends over time."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent experiments
        recent_experiments = [
            exp for exp in self.experiments
            if datetime.fromisoformat(exp["timestamp"]) > cutoff_date
        ]
        
        if not recent_experiments:
            return {
                "success": True,
                "message": "No recent experiments found",
                "trends": {}
            }
        
        # Analyze by method
        method_trends = defaultdict(lambda: {
            "count": 0,
            "successes": 0,
            "total_time": 0
        })
        
        for exp in recent_experiments:
            method_id = exp["method_id"]
            method_trends[method_id]["count"] += 1
            if exp["success"]:
                method_trends[method_id]["successes"] += 1
            method_trends[method_id]["total_time"] += exp["duration_seconds"]
        
        # Calculate trend metrics
        trends = {}
        for method_id, data in method_trends.items():
            if method_id in self.methods["methods"]:
                method_name = self.methods["methods"][method_id]["name"]
                success_rate = (data["successes"] / data["count"]) * 100
                avg_time = data["total_time"] / data["count"]
                
                trends[method_id] = {
                    "name": method_name,
                    "usage_count": data["count"],
                    "success_rate": success_rate,
                    "avg_time": avg_time
                }
        
        # Identify improving/declining methods
        improving = []
        declining = []
        
        for method_id, trend_data in trends.items():
            if method_id in self.effectiveness_data["method_scores"]:
                overall_rate = self.effectiveness_data["method_scores"][method_id]["success_rate"]
                recent_rate = trend_data["success_rate"]
                
                if recent_rate > overall_rate + 5:  # 5% improvement
                    improving.append(method_id)
                elif recent_rate < overall_rate - 5:  # 5% decline
                    declining.append(method_id)
        
        return {
            "success": True,
            "period_days": days,
            "total_experiments": len(recent_experiments),
            "trends": trends,
            "improving_methods": improving,
            "declining_methods": declining
        }
    
    def generate_recommendations(self, context: Dict = None) -> Dict:
        """Generate recommendations for optimal learning methods."""
        recommendations = []
        
        # Get top performing methods
        top_methods = sorted(
            self.effectiveness_data["method_scores"].items(),
            key=lambda x: x[1]["effectiveness_score"],
            reverse=True
        )[:5]
        
        for method_id, scores in top_methods:
            if method_id in self.methods["methods"]:
                method = self.methods["methods"][method_id]
                recommendations.append({
                    "method_id": method_id,
                    "name": method["name"],
                    "category": method["category"],
                    "effectiveness_score": scores["effectiveness_score"],
                    "success_rate": scores["success_rate"],
                    "recommendation": self._generate_method_recommendation(
                        method, scores
                    )
                })
        
        # Identify underutilized effective methods
        underutilized = []
        for method_id, scores in self.effectiveness_data["method_scores"].items():
            if (scores["effectiveness_score"] > 70 and 
                scores["usage_count"] < 10):
                if method_id in self.methods["methods"]:
                    underutilized.append({
                        "method_id": method_id,
                        "name": self.methods["methods"][method_id]["name"],
                        "effectiveness_score": scores["effectiveness_score"]
                    })
        
        self.recommendations["recommendations"] = recommendations
        self.recommendations["underutilized_methods"] = underutilized
        self._save_recommendations()
        
        return {
            "success": True,
            "top_recommendations": recommendations,
            "underutilized_methods": underutilized
        }
    
    def _generate_method_recommendation(self, method: Dict, scores: Dict) -> str:
        """Generate specific recommendation for a method."""
        if scores["effectiveness_score"] > 80:
            return f"Highly effective - use for {method['category']} learning tasks"
        elif scores["effectiveness_score"] > 60:
            return f"Good performance - suitable for most {method['category']} tasks"
        elif scores["success_rate"] > 70 and scores["efficiency"] < 1:
            return "Reliable but slow - use for complex tasks where accuracy matters"
        else:
            return "Consider alternatives or optimize parameters"
    
    def get_method_report(self, method_id: str) -> Dict:
        """Get detailed report for a specific method."""
        if method_id not in self.methods["methods"]:
            return {"success": False, "error": "Method not found"}
        
        method = self.methods["methods"][method_id]
        effectiveness = self.effectiveness_data["method_scores"].get(
            method_id,
            {}
        )
        
        # Get method experiments
        method_experiments = [
            exp for exp in self.experiments
            if exp["method_id"] == method_id
        ]
        
        # Analyze by task type
        task_performance = defaultdict(lambda: {"count": 0, "successes": 0})
        for exp in method_experiments:
            task_type = exp["task_type"]
            task_performance[task_type]["count"] += 1
            if exp["success"]:
                task_performance[task_type]["successes"] += 1
        
        task_breakdown = {}
        for task_type, data in task_performance.items():
            task_breakdown[task_type] = {
                "count": data["count"],
                "success_rate": (data["successes"] / data["count"]) * 100
            }
        
        return {
            "success": True,
            "method_id": method_id,
            "name": method["name"],
            "category": method["category"],
            "description": method["description"],
            "effectiveness_scores": effectiveness,
            "total_experiments": len(method_experiments),
            "task_breakdown": task_breakdown
        }
    
    def list_methods(self, category: str = None,
                    min_effectiveness: float = 0) -> List[Dict]:
        """List learning methods with optional filtering."""
        methods = []
        
        for method_id, method in self.methods["methods"].items():
            # Filter by category
            if category and method["category"] != category:
                continue
            
            # Get effectiveness score
            effectiveness = self.effectiveness_data["method_scores"].get(
                method_id,
                {"effectiveness_score": 0}
            )
            
            # Filter by effectiveness
            if effectiveness["effectiveness_score"] < min_effectiveness:
                continue
            
            methods.append({
                "method_id": method_id,
                "name": method["name"],
                "category": method["category"],
                "effectiveness_score": effectiveness["effectiveness_score"],
                "usage_count": method["usage_count"],
                "success_rate": effectiveness.get("success_rate", 0)
            })
        
        # Sort by effectiveness
        methods.sort(key=lambda x: x["effectiveness_score"], reverse=True)
        
        return methods


def test_learning_method_effectiveness_analyzer():
    """Test the learning method effectiveness analyzer."""
    analyzer = LearningMethodEffectivenessAnalyzer()
    
    # Register learning methods
    print("Registering learning methods...")
    analyzer.register_learning_method(
        "pattern_recognition",
        "Pattern Recognition Learning",
        "supervised",
        "Learn from labeled examples and patterns"
    )
    analyzer.register_learning_method(
        "trial_error",
        "Trial and Error",
        "reinforcement",
        "Learn through experimentation and feedback"
    )
    analyzer.register_learning_method(
        "knowledge_transfer",
        "Knowledge Transfer",
        "transfer",
        "Apply knowledge from related domains"
    )
    
    # Record learning sessions
    print("\nRecording learning sessions...")
    sessions = [
        ("pattern_recognition", "classification", 120, True),
        ("pattern_recognition", "classification", 110, True),
        ("pattern_recognition", "regression", 150, False),
        ("trial_error", "optimization", 200, True),
        ("trial_error", "optimization", 180, True),
        ("knowledge_transfer", "classification", 90, True),
    ]
    
    for method_id, task_type, duration, success in sessions:
        analyzer.record_learning_session(method_id, task_type, duration, success)
    
    # Compare methods
    print("\nComparing methods...")
    comparison = analyzer.compare_methods(
        ["pattern_recognition", "trial_error", "knowledge_transfer"],
        task_type="classification"
    )
    print(f"Comparison: {len(comparison['comparison']['methods'])} methods analyzed")
    for rec in comparison['comparison']['recommendations']:
        print(f"  - {rec}")
    
    # Analyze trends
    print("\nAnalyzing trends...")
    trends = analyzer.analyze_learning_trends(days=30)
    print(f"Total experiments: {trends['total_experiments']}")
    print(f"Methods tracked: {len(trends['trends'])}")
    
    # Generate recommendations
    print("\nGenerating recommendations...")
    recommendations = analyzer.generate_recommendations()
    print(f"Top recommendations: {len(recommendations['top_recommendations'])}")
    for rec in recommendations['top_recommendations'][:3]:
        print(f"  - {rec['name']}: {rec['recommendation']}")
    
    # Get method report
    print("\nMethod report for pattern_recognition:")
    report = analyzer.get_method_report("pattern_recognition")
    print(f"Total experiments: {report['total_experiments']}")
    print(f"Effectiveness score: {report['effectiveness_scores'].get('effectiveness_score', 0):.1f}")
    
    # List methods
    print("\nAll methods:")
    methods = analyzer.list_methods()
    for method in methods:
        print(f"  - {method['name']}: {method['effectiveness_score']:.1f} (used {method['usage_count']} times)")


if __name__ == "__main__":
    test_learning_method_effectiveness_analyzer()
