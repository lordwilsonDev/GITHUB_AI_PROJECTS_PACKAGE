#!/usr/bin/env python3
"""
Learning Method Analyzer

Analyzes the effectiveness of different learning methods and strategies.
Tracks which learning approaches work best for different types of knowledge.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import statistics

class LearningMethodAnalyzer:
    """Analyzes learning method effectiveness and optimizes learning strategies."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/meta_learning"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.methods_file = os.path.join(self.data_dir, "learning_methods.json")
        self.sessions_file = os.path.join(self.data_dir, "learning_sessions.json")
        self.effectiveness_file = os.path.join(self.data_dir, "method_effectiveness.json")
        self.recommendations_file = os.path.join(self.data_dir, "learning_recommendations.json")
        
        self.methods = self._load_methods()
        self.sessions = self._load_sessions()
        self.effectiveness = self._load_effectiveness()
        self.recommendations = self._load_recommendations()
    
    def _load_methods(self) -> Dict:
        """Load learning methods from file."""
        if os.path.exists(self.methods_file):
            with open(self.methods_file, 'r') as f:
                return json.load(f)
        return {
            "methods": [],
            "categories": [
                "observation",
                "experimentation",
                "documentation_review",
                "pattern_analysis",
                "trial_and_error",
                "guided_learning",
                "peer_learning",
                "self_reflection"
            ]
        }
    
    def _load_sessions(self) -> Dict:
        """Load learning sessions from file."""
        if os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        return {"sessions": []}
    
    def _load_effectiveness(self) -> Dict:
        """Load method effectiveness data from file."""
        if os.path.exists(self.effectiveness_file):
            with open(self.effectiveness_file, 'r') as f:
                return json.load(f)
        return {"effectiveness_scores": {}}
    
    def _load_recommendations(self) -> Dict:
        """Load learning recommendations from file."""
        if os.path.exists(self.recommendations_file):
            with open(self.recommendations_file, 'r') as f:
                return json.load(f)
        return {"recommendations": []}
    
    def _save_methods(self):
        """Save learning methods to file."""
        with open(self.methods_file, 'w') as f:
            json.dump(self.methods, f, indent=2)
    
    def _save_sessions(self):
        """Save learning sessions to file."""
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def _save_effectiveness(self):
        """Save method effectiveness data to file."""
        with open(self.effectiveness_file, 'w') as f:
            json.dump(self.effectiveness, f, indent=2)
    
    def _save_recommendations(self):
        """Save learning recommendations to file."""
        with open(self.recommendations_file, 'w') as f:
            json.dump(self.recommendations, f, indent=2)
    
    def register_learning_method(self, method_id: str, name: str, 
                                category: str, description: str,
                                characteristics: Dict[str, Any]) -> Dict:
        """Register a new learning method."""
        method = {
            "id": method_id,
            "name": name,
            "category": category,
            "description": description,
            "characteristics": characteristics,
            "registered_at": datetime.now().isoformat(),
            "usage_count": 0,
            "success_count": 0,
            "total_learning_time": 0,
            "knowledge_retained": []
        }
        
        self.methods["methods"].append(method)
        self._save_methods()
        
        return method
    
    def record_learning_session(self, method_id: str, topic: str,
                               duration_minutes: int, success: bool,
                               knowledge_gained: List[str],
                               retention_score: float,
                               difficulty: str,
                               context: Dict[str, Any]) -> Dict:
        """Record a learning session using a specific method."""
        session = {
            "id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "method_id": method_id,
            "topic": topic,
            "duration_minutes": duration_minutes,
            "success": success,
            "knowledge_gained": knowledge_gained,
            "retention_score": retention_score,  # 0.0 to 1.0
            "difficulty": difficulty,  # easy, medium, hard
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        self.sessions["sessions"].append(session)
        self._save_sessions()
        
        # Update method statistics
        self._update_method_stats(method_id, duration_minutes, success, retention_score)
        
        return session
    
    def _update_method_stats(self, method_id: str, duration: int, 
                            success: bool, retention: float):
        """Update statistics for a learning method."""
        for method in self.methods["methods"]:
            if method["id"] == method_id:
                method["usage_count"] += 1
                method["total_learning_time"] += duration
                if success:
                    method["success_count"] += 1
                method["knowledge_retained"].append(retention)
                self._save_methods()
                break
    
    def analyze_method_effectiveness(self) -> Dict:
        """Analyze the effectiveness of all learning methods."""
        effectiveness = {}
        
        for method in self.methods["methods"]:
            method_id = method["id"]
            sessions = [s for s in self.sessions["sessions"] 
                       if s["method_id"] == method_id]
            
            if not sessions:
                continue
            
            # Calculate metrics
            success_rate = method["success_count"] / method["usage_count"] if method["usage_count"] > 0 else 0
            avg_retention = statistics.mean(method["knowledge_retained"]) if method["knowledge_retained"] else 0
            avg_duration = method["total_learning_time"] / method["usage_count"] if method["usage_count"] > 0 else 0
            
            # Calculate efficiency (retention per minute)
            efficiency = avg_retention / avg_duration if avg_duration > 0 else 0
            
            # Analyze by difficulty
            difficulty_performance = self._analyze_by_difficulty(sessions)
            
            # Analyze by topic type
            topic_performance = self._analyze_by_topic(sessions)
            
            # Calculate overall effectiveness score (0-100)
            effectiveness_score = (
                success_rate * 30 +  # 30% weight
                avg_retention * 40 +  # 40% weight
                min(efficiency * 100, 30)  # 30% weight, capped
            )
            
            effectiveness[method_id] = {
                "method_name": method["name"],
                "category": method["category"],
                "usage_count": method["usage_count"],
                "success_rate": round(success_rate, 3),
                "avg_retention": round(avg_retention, 3),
                "avg_duration_minutes": round(avg_duration, 2),
                "efficiency": round(efficiency, 4),
                "effectiveness_score": round(effectiveness_score, 2),
                "difficulty_performance": difficulty_performance,
                "topic_performance": topic_performance,
                "last_used": sessions[-1]["timestamp"] if sessions else None
            }
        
        self.effectiveness["effectiveness_scores"] = effectiveness
        self.effectiveness["last_analyzed"] = datetime.now().isoformat()
        self._save_effectiveness()
        
        return effectiveness
    
    def _analyze_by_difficulty(self, sessions: List[Dict]) -> Dict:
        """Analyze method performance by difficulty level."""
        by_difficulty = defaultdict(lambda: {"count": 0, "successes": 0, "retentions": []})
        
        for session in sessions:
            difficulty = session["difficulty"]
            by_difficulty[difficulty]["count"] += 1
            if session["success"]:
                by_difficulty[difficulty]["successes"] += 1
            by_difficulty[difficulty]["retentions"].append(session["retention_score"])
        
        result = {}
        for difficulty, data in by_difficulty.items():
            result[difficulty] = {
                "count": data["count"],
                "success_rate": round(data["successes"] / data["count"], 3) if data["count"] > 0 else 0,
                "avg_retention": round(statistics.mean(data["retentions"]), 3) if data["retentions"] else 0
            }
        
        return result
    
    def _analyze_by_topic(self, sessions: List[Dict]) -> Dict:
        """Analyze method performance by topic type."""
        by_topic = defaultdict(lambda: {"count": 0, "successes": 0, "retentions": []})
        
        for session in sessions:
            topic = session["topic"]
            by_topic[topic]["count"] += 1
            if session["success"]:
                by_topic[topic]["successes"] += 1
            by_topic[topic]["retentions"].append(session["retention_score"])
        
        result = {}
        for topic, data in by_topic.items():
            result[topic] = {
                "count": data["count"],
                "success_rate": round(data["successes"] / data["count"], 3) if data["count"] > 0 else 0,
                "avg_retention": round(statistics.mean(data["retentions"]), 3) if data["retentions"] else 0
            }
        
        return result
    
    def compare_methods(self, method_ids: List[str]) -> Dict:
        """Compare multiple learning methods."""
        if not self.effectiveness.get("effectiveness_scores"):
            self.analyze_method_effectiveness()
        
        comparison = {
            "methods": [],
            "winner": None,
            "comparison_date": datetime.now().isoformat()
        }
        
        scores = []
        for method_id in method_ids:
            if method_id in self.effectiveness["effectiveness_scores"]:
                method_data = self.effectiveness["effectiveness_scores"][method_id]
                comparison["methods"].append(method_data)
                scores.append((method_id, method_data["effectiveness_score"]))
        
        if scores:
            winner_id, winner_score = max(scores, key=lambda x: x[1])
            comparison["winner"] = {
                "method_id": winner_id,
                "score": winner_score
            }
        
        return comparison
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate recommendations for optimizing learning methods."""
        if not self.effectiveness.get("effectiveness_scores"):
            self.analyze_method_effectiveness()
        
        recommendations = []
        effectiveness = self.effectiveness["effectiveness_scores"]
        
        # Find best and worst performing methods
        if effectiveness:
            sorted_methods = sorted(
                effectiveness.items(),
                key=lambda x: x[1]["effectiveness_score"],
                reverse=True
            )
            
            best_method = sorted_methods[0]
            worst_method = sorted_methods[-1]
            
            # Recommend using best method more
            if best_method[1]["effectiveness_score"] > 70:
                recommendations.append({
                    "type": "increase_usage",
                    "priority": "high",
                    "method_id": best_method[0],
                    "method_name": best_method[1]["method_name"],
                    "reason": f"High effectiveness score of {best_method[1]['effectiveness_score']}",
                    "suggestion": f"Use '{best_method[1]['method_name']}' more frequently for learning tasks"
                })
            
            # Recommend improving or replacing worst method
            if worst_method[1]["effectiveness_score"] < 40 and worst_method[1]["usage_count"] > 3:
                recommendations.append({
                    "type": "improve_or_replace",
                    "priority": "medium",
                    "method_id": worst_method[0],
                    "method_name": worst_method[1]["method_name"],
                    "reason": f"Low effectiveness score of {worst_method[1]['effectiveness_score']}",
                    "suggestion": f"Consider improving or replacing '{worst_method[1]['method_name']}'"
                })
            
            # Find underutilized effective methods
            for method_id, data in effectiveness.items():
                if data["effectiveness_score"] > 60 and data["usage_count"] < 5:
                    recommendations.append({
                        "type": "underutilized",
                        "priority": "medium",
                        "method_id": method_id,
                        "method_name": data["method_name"],
                        "reason": f"Good effectiveness ({data['effectiveness_score']}) but low usage ({data['usage_count']})",
                        "suggestion": f"Try using '{data['method_name']}' more often"
                    })
            
            # Recommend methods for specific difficulties
            for method_id, data in effectiveness.items():
                for difficulty, perf in data.get("difficulty_performance", {}).items():
                    if perf["success_rate"] > 0.8 and perf["count"] >= 2:
                        recommendations.append({
                            "type": "difficulty_specialist",
                            "priority": "low",
                            "method_id": method_id,
                            "method_name": data["method_name"],
                            "reason": f"Excellent performance on {difficulty} topics ({perf['success_rate']:.1%} success rate)",
                            "suggestion": f"Use '{data['method_name']}' for {difficulty} learning tasks"
                        })
        
        self.recommendations["recommendations"] = recommendations
        self.recommendations["generated_at"] = datetime.now().isoformat()
        self._save_recommendations()
        
        return recommendations
    
    def get_best_method_for_context(self, difficulty: str, topic: str = None) -> Optional[Dict]:
        """Get the best learning method for a specific context."""
        if not self.effectiveness.get("effectiveness_scores"):
            self.analyze_method_effectiveness()
        
        candidates = []
        
        for method_id, data in self.effectiveness["effectiveness_scores"].items():
            # Check difficulty performance
            difficulty_perf = data.get("difficulty_performance", {}).get(difficulty)
            if difficulty_perf and difficulty_perf["count"] >= 2:
                score = difficulty_perf["success_rate"] * 0.6 + difficulty_perf["avg_retention"] * 0.4
                candidates.append((method_id, data, score))
        
        if candidates:
            best = max(candidates, key=lambda x: x[2])
            return {
                "method_id": best[0],
                "method_name": best[1]["method_name"],
                "category": best[1]["category"],
                "predicted_success_rate": best[2],
                "reason": f"Best performance for {difficulty} difficulty tasks"
            }
        
        return None
    
    def generate_report(self) -> str:
        """Generate a comprehensive learning method analysis report."""
        effectiveness = self.analyze_method_effectiveness()
        recommendations = self.generate_recommendations()
        
        report = []
        report.append("=" * 60)
        report.append("LEARNING METHOD ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        report.append("## Summary")
        report.append(f"Total methods tracked: {len(self.methods['methods'])}")
        report.append(f"Total learning sessions: {len(self.sessions['sessions'])}")
        report.append(f"Methods analyzed: {len(effectiveness)}")
        report.append("")
        
        # Method effectiveness rankings
        if effectiveness:
            report.append("## Method Effectiveness Rankings")
            sorted_methods = sorted(
                effectiveness.items(),
                key=lambda x: x[1]["effectiveness_score"],
                reverse=True
            )
            
            for i, (method_id, data) in enumerate(sorted_methods, 1):
                report.append(f"{i}. {data['method_name']} (Score: {data['effectiveness_score']})")
                report.append(f"   - Category: {data['category']}")
                report.append(f"   - Success Rate: {data['success_rate']:.1%}")
                report.append(f"   - Avg Retention: {data['avg_retention']:.1%}")
                report.append(f"   - Efficiency: {data['efficiency']:.4f} retention/min")
                report.append(f"   - Usage: {data['usage_count']} sessions")
                report.append("")
        
        # Recommendations
        if recommendations:
            report.append("## Recommendations")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. [{rec['priority'].upper()}] {rec['type']}")
                report.append(f"   Method: {rec['method_name']}")
                report.append(f"   Reason: {rec['reason']}")
                report.append(f"   Suggestion: {rec['suggestion']}")
                report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """Test the learning method analyzer."""
    analyzer = LearningMethodAnalyzer()
    
    print("Testing Learning Method Analyzer...\n")
    
    # Register learning methods
    print("1. Registering learning methods...")
    methods = [
        {
            "id": "obs_001",
            "name": "Direct Observation",
            "category": "observation",
            "description": "Learning by watching and observing",
            "characteristics": {"passive": True, "time_efficient": True}
        },
        {
            "id": "exp_001",
            "name": "Hands-on Experimentation",
            "category": "experimentation",
            "description": "Learning by doing and experimenting",
            "characteristics": {"active": True, "retention_high": True}
        },
        {
            "id": "doc_001",
            "name": "Documentation Study",
            "category": "documentation_review",
            "description": "Learning from written documentation",
            "characteristics": {"structured": True, "comprehensive": True}
        }
    ]
    
    for method in methods:
        analyzer.register_learning_method(
            method["id"], method["name"], method["category"],
            method["description"], method["characteristics"]
        )
    print(f"✓ Registered {len(methods)} methods")
    print("")
    
    # Record learning sessions
    print("2. Recording learning sessions...")
    sessions = [
        {
            "method_id": "obs_001",
            "topic": "Python syntax",
            "duration_minutes": 30,
            "success": True,
            "knowledge_gained": ["list comprehensions", "decorators"],
            "retention_score": 0.7,
            "difficulty": "medium",
            "context": {"environment": "tutorial"}
        },
        {
            "method_id": "exp_001",
            "topic": "API integration",
            "duration_minutes": 60,
            "success": True,
            "knowledge_gained": ["REST APIs", "authentication"],
            "retention_score": 0.9,
            "difficulty": "hard",
            "context": {"environment": "project"}
        },
        {
            "method_id": "doc_001",
            "topic": "Framework basics",
            "duration_minutes": 45,
            "success": True,
            "knowledge_gained": ["routing", "middleware"],
            "retention_score": 0.6,
            "difficulty": "easy",
            "context": {"environment": "documentation"}
        },
        {
            "method_id": "exp_001",
            "topic": "Database queries",
            "duration_minutes": 40,
            "success": False,
            "knowledge_gained": ["SQL basics"],
            "retention_score": 0.4,
            "difficulty": "medium",
            "context": {"environment": "project"}
        }
    ]
    
    for session in sessions:
        analyzer.record_learning_session(**session)
    print(f"✓ Recorded {len(sessions)} learning sessions")
    print("")
    
    # Analyze effectiveness
    print("3. Analyzing method effectiveness...")
    effectiveness = analyzer.analyze_method_effectiveness()
    print(f"✓ Analyzed {len(effectiveness)} methods")
    for method_id, data in effectiveness.items():
        print(f"  - {data['method_name']}: Score {data['effectiveness_score']}, Success rate {data['success_rate']:.1%}")
    print("")
    
    # Generate recommendations
    print("4. Generating recommendations...")
    recommendations = analyzer.generate_recommendations()
    print(f"✓ Generated {len(recommendations)} recommendations")
    for rec in recommendations:
        print(f"  - [{rec['priority']}] {rec['suggestion']}")
    print("")
    
    # Get best method for context
    print("5. Finding best method for hard difficulty...")
    best = analyzer.get_best_method_for_context("hard")
    if best:
        print(f"✓ Best method: {best['method_name']}")
        print(f"  Reason: {best['reason']}")
    print("")
    
    # Generate report
    print("6. Generating full report...")
    report = analyzer.generate_report()
    print("✓ Report generated")
    print("")
    print(report)
    
    print("\n✅ Learning method analyzer is operational!")

if __name__ == "__main__":
    main()
