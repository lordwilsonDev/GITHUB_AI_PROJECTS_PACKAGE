#!/usr/bin/env python3
"""
User Satisfaction Analyzer

Analyzes user satisfaction through feedback, interaction patterns,
and task completion metrics.

Features:
- Track explicit user feedback
- Analyze implicit satisfaction signals
- Monitor satisfaction trends over time
- Identify satisfaction drivers and detractors
- Generate satisfaction reports
- Recommend improvements based on feedback
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict, Counter


class UserSatisfactionAnalyzer:
    """Analyzes and tracks user satisfaction metrics."""
    
    def __init__(self, base_dir: str = "~/vy-nexus/data/user_satisfaction"):
        self.base_dir = Path(base_dir).expanduser()
        self.feedback_file = self.base_dir / "feedback.json"
        self.interactions_file = self.base_dir / "interactions.json"
        self.satisfaction_scores_file = self.base_dir / "satisfaction_scores.json"
        self.sentiment_file = self.base_dir / "sentiment_analysis.json"
        self.insights_file = self.base_dir / "insights.json"
        
        # Create directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.feedback = self._load_feedback()
        self.interactions = self._load_interactions()
        self.satisfaction_scores = self._load_satisfaction_scores()
        self.sentiment_data = self._load_sentiment()
        self.insights = self._load_insights()
    
    def _load_feedback(self) -> List[Dict]:
        """Load user feedback history."""
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_feedback(self):
        """Save user feedback history."""
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback, f, indent=2)
    
    def _load_interactions(self) -> List[Dict]:
        """Load interaction history."""
        if self.interactions_file.exists():
            with open(self.interactions_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_interactions(self):
        """Save interaction history."""
        with open(self.interactions_file, 'w') as f:
            json.dump(self.interactions, f, indent=2)
    
    def _load_satisfaction_scores(self) -> Dict:
        """Load satisfaction scores."""
        if self.satisfaction_scores_file.exists():
            with open(self.satisfaction_scores_file, 'r') as f:
                return json.load(f)
        return {
            "overall_score": 0,
            "category_scores": {},
            "trend_data": [],
            "last_updated": None
        }
    
    def _save_satisfaction_scores(self):
        """Save satisfaction scores."""
        self.satisfaction_scores["last_updated"] = datetime.now().isoformat()
        with open(self.satisfaction_scores_file, 'w') as f:
            json.dump(self.satisfaction_scores, f, indent=2)
    
    def _load_sentiment(self) -> Dict:
        """Load sentiment analysis data."""
        if self.sentiment_file.exists():
            with open(self.sentiment_file, 'r') as f:
                return json.load(f)
        return {
            "sentiment_history": [],
            "last_analyzed": None
        }
    
    def _save_sentiment(self):
        """Save sentiment analysis data."""
        self.sentiment_data["last_analyzed"] = datetime.now().isoformat()
        with open(self.sentiment_file, 'w') as f:
            json.dump(self.sentiment_data, f, indent=2)
    
    def _load_insights(self) -> Dict:
        """Load satisfaction insights."""
        if self.insights_file.exists():
            with open(self.insights_file, 'r') as f:
                return json.load(f)
        return {
            "insights": [],
            "recommendations": [],
            "last_generated": None
        }
    
    def _save_insights(self):
        """Save satisfaction insights."""
        self.insights["last_generated"] = datetime.now().isoformat()
        with open(self.insights_file, 'w') as f:
            json.dump(self.insights, f, indent=2)
    
    def record_explicit_feedback(self, rating: int,
                                category: str,
                                comment: str = "",
                                context: Dict = None) -> Dict:
        """Record explicit user feedback (ratings, comments)."""
        if not 1 <= rating <= 5:
            return {"success": False, "error": "Rating must be between 1 and 5"}
        
        feedback_entry = {
            "feedback_id": f"feedback_{len(self.feedback) + 1}",
            "rating": rating,
            "category": category,
            "comment": comment,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "sentiment": self._analyze_comment_sentiment(comment)
        }
        
        self.feedback.append(feedback_entry)
        self._save_feedback()
        
        # Update satisfaction scores
        self._update_satisfaction_scores()
        
        return {
            "success": True,
            "feedback_id": feedback_entry["feedback_id"]
        }
    
    def _analyze_comment_sentiment(self, comment: str) -> str:
        """Analyze sentiment of comment text."""
        if not comment:
            return "neutral"
        
        comment_lower = comment.lower()
        
        # Positive indicators
        positive_words = [
            "great", "excellent", "amazing", "love", "perfect",
            "helpful", "fantastic", "wonderful", "awesome", "good"
        ]
        
        # Negative indicators
        negative_words = [
            "bad", "terrible", "awful", "hate", "poor",
            "useless", "frustrating", "disappointed", "slow", "broken"
        ]
        
        positive_count = sum(1 for word in positive_words if word in comment_lower)
        negative_count = sum(1 for word in negative_words if word in comment_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def record_interaction(self, interaction_type: str,
                          task_completed: bool,
                          duration: float,
                          user_effort: str = "medium",
                          context: Dict = None) -> Dict:
        """Record user interaction for implicit satisfaction signals."""
        if user_effort not in ["low", "medium", "high"]:
            return {"success": False, "error": "Invalid user_effort value"}
        
        interaction_entry = {
            "interaction_id": f"interaction_{len(self.interactions) + 1}",
            "interaction_type": interaction_type,
            "task_completed": task_completed,
            "duration": duration,
            "user_effort": user_effort,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "satisfaction_signal": self._calculate_implicit_satisfaction(
                task_completed, duration, user_effort
            )
        }
        
        self.interactions.append(interaction_entry)
        self._save_interactions()
        
        # Update satisfaction scores
        self._update_satisfaction_scores()
        
        return {
            "success": True,
            "interaction_id": interaction_entry["interaction_id"]
        }
    
    def _calculate_implicit_satisfaction(self, completed: bool,
                                        duration: float,
                                        effort: str) -> float:
        """Calculate implicit satisfaction from interaction signals."""
        score = 0.0
        
        # Task completion (40% weight)
        if completed:
            score += 40
        
        # Duration efficiency (30% weight)
        # Assume optimal duration is between 10-300 seconds
        if 10 <= duration <= 300:
            score += 30
        elif duration < 10:
            score += 20  # Too fast might indicate issues
        else:
            score += 10  # Too slow indicates friction
        
        # User effort (30% weight)
        effort_scores = {"low": 30, "medium": 20, "high": 10}
        score += effort_scores.get(effort, 15)
        
        return score
    
    def _update_satisfaction_scores(self):
        """Update overall satisfaction scores."""
        # Calculate from explicit feedback
        if self.feedback:
            recent_feedback = self.feedback[-50:]  # Last 50 feedback items
            avg_rating = statistics.mean(f["rating"] for f in recent_feedback)
            explicit_score = (avg_rating / 5) * 100
        else:
            explicit_score = 0
        
        # Calculate from implicit signals
        if self.interactions:
            recent_interactions = self.interactions[-100:]  # Last 100 interactions
            avg_implicit = statistics.mean(
                i["satisfaction_signal"] for i in recent_interactions
            )
            implicit_score = avg_implicit
        else:
            implicit_score = 0
        
        # Combined score (60% explicit, 40% implicit)
        if self.feedback and self.interactions:
            overall_score = (explicit_score * 0.6) + (implicit_score * 0.4)
        elif self.feedback:
            overall_score = explicit_score
        elif self.interactions:
            overall_score = implicit_score
        else:
            overall_score = 0
        
        self.satisfaction_scores["overall_score"] = overall_score
        
        # Update category scores
        self._update_category_scores()
        
        # Update trend data
        self.satisfaction_scores["trend_data"].append({
            "timestamp": datetime.now().isoformat(),
            "score": overall_score
        })
        
        # Keep only last 100 trend points
        self.satisfaction_scores["trend_data"] = \
            self.satisfaction_scores["trend_data"][-100:]
        
        self._save_satisfaction_scores()
    
    def _update_category_scores(self):
        """Update satisfaction scores by category."""
        category_ratings = defaultdict(list)
        
        for feedback in self.feedback:
            category = feedback.get("category", "general")
            category_ratings[category].append(feedback["rating"])
        
        category_scores = {}
        for category, ratings in category_ratings.items():
            avg_rating = statistics.mean(ratings)
            category_scores[category] = (avg_rating / 5) * 100
        
        self.satisfaction_scores["category_scores"] = category_scores
    
    def analyze_satisfaction_trends(self, days: int = 30) -> Dict:
        """Analyze satisfaction trends over time."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent feedback
        recent_feedback = [
            f for f in self.feedback
            if datetime.fromisoformat(f["timestamp"]) > cutoff_date
        ]
        
        # Filter recent interactions
        recent_interactions = [
            i for i in self.interactions
            if datetime.fromisoformat(i["timestamp"]) > cutoff_date
        ]
        
        if not recent_feedback and not recent_interactions:
            return {
                "success": True,
                "message": "No recent data found",
                "trends": {}
            }
        
        # Calculate trend metrics
        trends = {
            "period_days": days,
            "feedback_count": len(recent_feedback),
            "interaction_count": len(recent_interactions)
        }
        
        # Feedback trends
        if recent_feedback:
            avg_rating = statistics.mean(f["rating"] for f in recent_feedback)
            sentiment_counts = Counter(f["sentiment"] for f in recent_feedback)
            
            trends["avg_rating"] = avg_rating
            trends["sentiment_distribution"] = dict(sentiment_counts)
            
            # Compare to overall average
            if len(self.feedback) > len(recent_feedback):
                overall_avg = statistics.mean(f["rating"] for f in self.feedback)
                trends["rating_change"] = avg_rating - overall_avg
            else:
                trends["rating_change"] = 0
        
        # Interaction trends
        if recent_interactions:
            completion_rate = sum(
                1 for i in recent_interactions if i["task_completed"]
            ) / len(recent_interactions) * 100
            
            avg_duration = statistics.mean(
                i["duration"] for i in recent_interactions
            )
            
            effort_counts = Counter(
                i["user_effort"] for i in recent_interactions
            )
            
            trends["completion_rate"] = completion_rate
            trends["avg_duration"] = avg_duration
            trends["effort_distribution"] = dict(effort_counts)
        
        return {
            "success": True,
            "trends": trends
        }
    
    def identify_satisfaction_drivers(self) -> Dict:
        """Identify key drivers of satisfaction and dissatisfaction."""
        drivers = {
            "positive_drivers": [],
            "negative_drivers": [],
            "neutral_factors": []
        }
        
        # Analyze feedback by category
        category_analysis = defaultdict(lambda: {
            "ratings": [],
            "comments": [],
            "sentiment": []
        })
        
        for feedback in self.feedback:
            category = feedback.get("category", "general")
            category_analysis[category]["ratings"].append(feedback["rating"])
            category_analysis[category]["comments"].append(feedback.get("comment", ""))
            category_analysis[category]["sentiment"].append(feedback["sentiment"])
        
        # Identify drivers
        for category, data in category_analysis.items():
            if not data["ratings"]:
                continue
            
            avg_rating = statistics.mean(data["ratings"])
            positive_sentiment = data["sentiment"].count("positive")
            negative_sentiment = data["sentiment"].count("negative")
            
            driver_info = {
                "category": category,
                "avg_rating": avg_rating,
                "feedback_count": len(data["ratings"]),
                "positive_mentions": positive_sentiment,
                "negative_mentions": negative_sentiment
            }
            
            if avg_rating >= 4.0:
                drivers["positive_drivers"].append(driver_info)
            elif avg_rating <= 2.5:
                drivers["negative_drivers"].append(driver_info)
            else:
                drivers["neutral_factors"].append(driver_info)
        
        # Sort by impact (feedback count)
        for key in drivers:
            drivers[key].sort(key=lambda x: x["feedback_count"], reverse=True)
        
        return {
            "success": True,
            "drivers": drivers
        }
    
    def generate_insights(self) -> Dict:
        """Generate actionable insights from satisfaction data."""
        insights = []
        recommendations = []
        
        # Overall satisfaction insight
        overall_score = self.satisfaction_scores["overall_score"]
        if overall_score >= 80:
            insights.append({
                "type": "positive",
                "insight": f"High user satisfaction ({overall_score:.1f}/100)",
                "priority": "low"
            })
        elif overall_score >= 60:
            insights.append({
                "type": "neutral",
                "insight": f"Moderate user satisfaction ({overall_score:.1f}/100)",
                "priority": "medium"
            })
            recommendations.append({
                "recommendation": "Focus on improving user experience in key areas",
                "priority": "medium"
            })
        else:
            insights.append({
                "type": "negative",
                "insight": f"Low user satisfaction ({overall_score:.1f}/100)",
                "priority": "high"
            })
            recommendations.append({
                "recommendation": "Urgent: Address major satisfaction issues",
                "priority": "high"
            })
        
        # Category-specific insights
        for category, score in self.satisfaction_scores["category_scores"].items():
            if score < 60:
                insights.append({
                    "type": "negative",
                    "insight": f"Low satisfaction in {category} ({score:.1f}/100)",
                    "priority": "high"
                })
                recommendations.append({
                    "recommendation": f"Improve {category} functionality and user experience",
                    "priority": "high"
                })
        
        # Trend insights
        if len(self.satisfaction_scores["trend_data"]) >= 10:
            recent_scores = [
                t["score"] for t in self.satisfaction_scores["trend_data"][-10:]
            ]
            older_scores = [
                t["score"] for t in self.satisfaction_scores["trend_data"][-20:-10]
            ] if len(self.satisfaction_scores["trend_data"]) >= 20 else recent_scores
            
            recent_avg = statistics.mean(recent_scores)
            older_avg = statistics.mean(older_scores)
            
            if recent_avg > older_avg + 5:
                insights.append({
                    "type": "positive",
                    "insight": "Satisfaction is improving over time",
                    "priority": "low"
                })
            elif recent_avg < older_avg - 5:
                insights.append({
                    "type": "negative",
                    "insight": "Satisfaction is declining over time",
                    "priority": "high"
                })
                recommendations.append({
                    "recommendation": "Investigate recent changes that may have impacted satisfaction",
                    "priority": "high"
                })
        
        # Interaction insights
        if self.interactions:
            recent_interactions = self.interactions[-50:]
            completion_rate = sum(
                1 for i in recent_interactions if i["task_completed"]
            ) / len(recent_interactions) * 100
            
            if completion_rate < 70:
                insights.append({
                    "type": "negative",
                    "insight": f"Low task completion rate ({completion_rate:.1f}%)",
                    "priority": "high"
                })
                recommendations.append({
                    "recommendation": "Simplify workflows and reduce friction in task completion",
                    "priority": "high"
                })
        
        self.insights["insights"] = insights
        self.insights["recommendations"] = recommendations
        self._save_insights()
        
        return {
            "success": True,
            "insights": insights,
            "recommendations": recommendations
        }
    
    def get_satisfaction_report(self) -> Dict:
        """Get comprehensive satisfaction report."""
        # Get recent trends
        trends = self.analyze_satisfaction_trends(days=30)
        
        # Get drivers
        drivers = self.identify_satisfaction_drivers()
        
        # Get insights
        insights = self.generate_insights()
        
        return {
            "success": True,
            "overall_score": self.satisfaction_scores["overall_score"],
            "category_scores": self.satisfaction_scores["category_scores"],
            "trends": trends.get("trends", {}),
            "drivers": drivers.get("drivers", {}),
            "insights": insights.get("insights", []),
            "recommendations": insights.get("recommendations", []),
            "data_summary": {
                "total_feedback": len(self.feedback),
                "total_interactions": len(self.interactions),
                "trend_points": len(self.satisfaction_scores["trend_data"])
            }
        }
    
    def get_feedback_summary(self, category: str = None,
                           days: int = None) -> Dict:
        """Get summary of user feedback."""
        feedback_list = self.feedback
        
        # Filter by category
        if category:
            feedback_list = [f for f in feedback_list if f.get("category") == category]
        
        # Filter by time period
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            feedback_list = [
                f for f in feedback_list
                if datetime.fromisoformat(f["timestamp"]) > cutoff_date
            ]
        
        if not feedback_list:
            return {
                "success": True,
                "message": "No feedback found",
                "summary": {}
            }
        
        # Calculate summary statistics
        ratings = [f["rating"] for f in feedback_list]
        sentiments = [f["sentiment"] for f in feedback_list]
        
        summary = {
            "total_feedback": len(feedback_list),
            "avg_rating": statistics.mean(ratings),
            "rating_distribution": dict(Counter(ratings)),
            "sentiment_distribution": dict(Counter(sentiments)),
            "recent_comments": [
                {
                    "rating": f["rating"],
                    "comment": f.get("comment", ""),
                    "category": f.get("category", "general"),
                    "timestamp": f["timestamp"]
                }
                for f in feedback_list[-10:]
            ]
        }
        
        return {
            "success": True,
            "summary": summary
        }


def test_user_satisfaction_analyzer():
    """Test the user satisfaction analyzer."""
    analyzer = UserSatisfactionAnalyzer()
    
    # Record explicit feedback
    print("Recording explicit feedback...")
    analyzer.record_explicit_feedback(
        5, "performance", "System is very fast and responsive!"
    )
    analyzer.record_explicit_feedback(
        4, "usability", "Easy to use, but could be more intuitive"
    )
    analyzer.record_explicit_feedback(
        2, "reliability", "System crashed twice today, very frustrating"
    )
    analyzer.record_explicit_feedback(
        5, "features", "Love the new automation features!"
    )
    
    # Record interactions
    print("\nRecording interactions...")
    analyzer.record_interaction("task_completion", True, 45.5, "low")
    analyzer.record_interaction("task_completion", True, 120.0, "medium")
    analyzer.record_interaction("task_completion", False, 300.0, "high")
    analyzer.record_interaction("task_completion", True, 60.0, "low")
    
    # Analyze trends
    print("\nAnalyzing satisfaction trends...")
    trends = analyzer.analyze_satisfaction_trends(days=30)
    if "trends" in trends:
        print(f"Average rating: {trends['trends'].get('avg_rating', 0):.2f}")
        print(f"Completion rate: {trends['trends'].get('completion_rate', 0):.1f}%")
    
    # Identify drivers
    print("\nIdentifying satisfaction drivers...")
    drivers = analyzer.identify_satisfaction_drivers()
    print(f"Positive drivers: {len(drivers['drivers']['positive_drivers'])}")
    print(f"Negative drivers: {len(drivers['drivers']['negative_drivers'])}")
    
    # Generate insights
    print("\nGenerating insights...")
    insights = analyzer.generate_insights()
    print(f"Total insights: {len(insights['insights'])}")
    for insight in insights['insights'][:3]:
        print(f"  [{insight['type'].upper()}] {insight['insight']}")
    
    # Get satisfaction report
    print("\nSatisfaction Report:")
    report = analyzer.get_satisfaction_report()
    print(f"Overall score: {report['overall_score']:.1f}/100")
    print(f"Category scores:")
    for category, score in report['category_scores'].items():
        print(f"  - {category}: {score:.1f}/100")
    
    print(f"\nRecommendations:")
    for rec in report['recommendations'][:3]:
        print(f"  [{rec['priority'].upper()}] {rec['recommendation']}")
    
    # Get feedback summary
    print("\nFeedback Summary:")
    summary = analyzer.get_feedback_summary()
    if "summary" in summary:
        print(f"Total feedback: {summary['summary']['total_feedback']}")
        print(f"Average rating: {summary['summary']['avg_rating']:.2f}/5")


if __name__ == "__main__":
    test_user_satisfaction_analyzer()
