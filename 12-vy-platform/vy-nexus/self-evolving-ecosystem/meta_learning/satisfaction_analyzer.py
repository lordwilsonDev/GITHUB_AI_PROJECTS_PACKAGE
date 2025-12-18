#!/usr/bin/env python3
"""
Satisfaction Analyzer
Analyzes user satisfaction and feedback to improve system performance
Part of the Self-Evolving AI Ecosystem
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import statistics
import re

class SatisfactionAnalyzer:
    """Analyzes user satisfaction metrics and feedback"""
    
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
        self.data_dir = self.base_dir / "data" / "satisfaction"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Tracking files
        self.feedback_file = self.data_dir / "feedback.jsonl"
        self.ratings_file = self.data_dir / "ratings.jsonl"
        self.sentiment_file = self.data_dir / "sentiment_analysis.jsonl"
        self.satisfaction_scores_file = self.data_dir / "satisfaction_scores.jsonl"
        
        # Feedback categories
        self.feedback_categories = [
            "task_completion",
            "response_quality",
            "speed",
            "accuracy",
            "communication",
            "understanding",
            "helpfulness",
            "general"
        ]
        
        # Sentiment keywords
        self.positive_keywords = [
            "great", "excellent", "perfect", "amazing", "wonderful",
            "helpful", "good", "nice", "thanks", "thank you",
            "appreciate", "love", "awesome", "fantastic", "brilliant"
        ]
        
        self.negative_keywords = [
            "bad", "poor", "terrible", "awful", "horrible",
            "wrong", "error", "failed", "broken", "issue",
            "problem", "slow", "confusing", "frustrated", "annoying"
        ]
        
        # Satisfaction thresholds
        self.thresholds = {
            "excellent": 4.5,
            "good": 3.5,
            "acceptable": 2.5,
            "poor": 1.5
        }
        
        self._initialized = True
    
    def record_feedback(
        self,
        feedback_id: str,
        category: str,
        feedback_text: str,
        context: Optional[str] = None,
        task_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Record user feedback"""
        
        if category not in self.feedback_categories:
            category = "general"
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(feedback_text)
        
        feedback = {
            "feedback_id": feedback_id,
            "category": category,
            "feedback_text": feedback_text,
            "context": context,
            "task_id": task_id,
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Save feedback
        with open(self.feedback_file, 'a') as f:
            f.write(json.dumps(feedback) + '\n')
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "sentiment": sentiment
        }
    
    def record_rating(
        self,
        rating_id: str,
        category: str,
        rating: float,  # 1-5 scale
        task_id: Optional[str] = None,
        comment: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Record a user rating"""
        
        if not 1 <= rating <= 5:
            return {
                "success": False,
                "error": "Rating must be between 1 and 5"
            }
        
        rating_record = {
            "rating_id": rating_id,
            "category": category,
            "rating": rating,
            "task_id": task_id,
            "comment": comment,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Save rating
        with open(self.ratings_file, 'a') as f:
            f.write(json.dumps(rating_record) + '\n')
        
        return {
            "success": True,
            "rating_id": rating_id
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        
        text_lower = text.lower()
        
        # Count positive and negative keywords
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        # Calculate sentiment score (-1 to 1)
        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / total_keywords
        
        # Determine sentiment label
        if sentiment_score > 0.3:
            sentiment_label = "positive"
        elif sentiment_score < -0.3:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        return {
            "score": sentiment_score,
            "label": sentiment_label,
            "positive_keywords": positive_count,
            "negative_keywords": negative_count
        }
    
    def calculate_satisfaction_score(
        self,
        category: Optional[str] = None,
        time_window_hours: int = 168  # 1 week default
    ) -> Dict[str, Any]:
        """Calculate overall satisfaction score"""
        
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Get ratings within time window
        ratings = self._get_ratings(cutoff_time, category)
        
        # Get feedback within time window
        feedback = self._get_feedback(cutoff_time, category)
        
        if not ratings and not feedback:
            return {
                "success": True,
                "score": None,
                "message": "No data in time window"
            }
        
        # Calculate rating-based score
        rating_score = None
        if ratings:
            rating_values = [r.get("rating", 0) for r in ratings]
            rating_score = statistics.mean(rating_values)
        
        # Calculate sentiment-based score
        sentiment_score = None
        if feedback:
            sentiment_values = [f.get("sentiment", {}).get("score", 0) for f in feedback]
            # Convert from -1 to 1 scale to 1 to 5 scale
            sentiment_score = statistics.mean([(s + 1) * 2 + 1 for s in sentiment_values])
        
        # Combine scores
        if rating_score and sentiment_score:
            overall_score = (rating_score * 0.7 + sentiment_score * 0.3)
        elif rating_score:
            overall_score = rating_score
        else:
            overall_score = sentiment_score
        
        # Determine satisfaction level
        if overall_score >= self.thresholds["excellent"]:
            level = "excellent"
        elif overall_score >= self.thresholds["good"]:
            level = "good"
        elif overall_score >= self.thresholds["acceptable"]:
            level = "acceptable"
        else:
            level = "poor"
        
        score_data = {
            "category": category or "overall",
            "time_window_hours": time_window_hours,
            "overall_score": overall_score,
            "rating_score": rating_score,
            "sentiment_score": sentiment_score,
            "satisfaction_level": level,
            "total_ratings": len(ratings),
            "total_feedback": len(feedback),
            "calculated_at": datetime.now().isoformat()
        }
        
        # Save score
        with open(self.satisfaction_scores_file, 'a') as f:
            f.write(json.dumps(score_data) + '\n')
        
        return {
            "success": True,
            "score_data": score_data
        }
    
    def analyze_feedback_trends(
        self,
        time_window_hours: int = 168
    ) -> Dict[str, Any]:
        """Analyze trends in user feedback"""
        
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        feedback = self._get_feedback(cutoff_time)
        
        if not feedback:
            return {
                "success": True,
                "trends": None,
                "message": "No feedback in time window"
            }
        
        # Analyze by category
        by_category = defaultdict(list)
        for f in feedback:
            category = f.get("category", "general")
            by_category[category].append(f)
        
        category_analysis = {}
        for category, items in by_category.items():
            sentiments = [i.get("sentiment", {}).get("label", "neutral") for i in items]
            category_analysis[category] = {
                "total": len(items),
                "positive": sentiments.count("positive"),
                "negative": sentiments.count("negative"),
                "neutral": sentiments.count("neutral")
            }
        
        # Analyze temporal trend
        sorted_feedback = sorted(feedback, key=lambda x: x.get("timestamp", ""))
        mid_point = len(sorted_feedback) // 2
        
        early_feedback = sorted_feedback[:mid_point]
        late_feedback = sorted_feedback[mid_point:]
        
        early_sentiment = self._calculate_avg_sentiment(early_feedback)
        late_sentiment = self._calculate_avg_sentiment(late_feedback)
        
        trend_direction = "improving" if late_sentiment > early_sentiment + 0.1 else \
                         "declining" if late_sentiment < early_sentiment - 0.1 else "stable"
        
        # Extract common themes
        themes = self._extract_themes(feedback)
        
        trends = {
            "by_category": category_analysis,
            "temporal_trend": {
                "early_sentiment": early_sentiment,
                "late_sentiment": late_sentiment,
                "direction": trend_direction
            },
            "common_themes": themes,
            "analyzed_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "trends": trends
        }
    
    def _calculate_avg_sentiment(self, feedback: List[Dict]) -> float:
        """Calculate average sentiment score"""
        if not feedback:
            return 0.0
        
        scores = [f.get("sentiment", {}).get("score", 0) for f in feedback]
        return statistics.mean(scores)
    
    def _extract_themes(self, feedback: List[Dict]) -> List[Dict[str, Any]]:
        """Extract common themes from feedback"""
        
        # Count word frequencies (simple approach)
        word_counts = defaultdict(int)
        
        for f in feedback:
            text = f.get("feedback_text", "").lower()
            # Remove common words and extract meaningful terms
            words = re.findall(r'\b\w{4,}\b', text)  # Words with 4+ characters
            
            for word in words:
                if word not in ['this', 'that', 'with', 'from', 'have', 'been', 'were', 'would', 'could', 'should']:
                    word_counts[word] += 1
        
        # Get top themes
        top_themes = sorted(
            word_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return [
            {"theme": word, "count": count}
            for word, count in top_themes
        ]
    
    def identify_improvement_areas(
        self,
        time_window_hours: int = 168
    ) -> Dict[str, Any]:
        """Identify areas needing improvement based on feedback"""
        
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Get all feedback and ratings
        feedback = self._get_feedback(cutoff_time)
        ratings = self._get_ratings(cutoff_time)
        
        improvement_areas = []
        
        # Analyze ratings by category
        ratings_by_category = defaultdict(list)
        for r in ratings:
            category = r.get("category", "general")
            ratings_by_category[category].append(r.get("rating", 0))
        
        for category, rating_values in ratings_by_category.items():
            avg_rating = statistics.mean(rating_values)
            
            if avg_rating < self.thresholds["acceptable"]:
                improvement_areas.append({
                    "category": category,
                    "type": "low_rating",
                    "severity": "high" if avg_rating < self.thresholds["poor"] else "medium",
                    "avg_rating": avg_rating,
                    "sample_count": len(rating_values),
                    "recommendation": f"Focus on improving {category} - average rating is {avg_rating:.2f}/5.0"
                })
        
        # Analyze negative feedback
        negative_feedback = [f for f in feedback if f.get("sentiment", {}).get("label") == "negative"]
        
        if len(negative_feedback) > len(feedback) * 0.3:  # More than 30% negative
            negative_by_category = defaultdict(int)
            for f in negative_feedback:
                category = f.get("category", "general")
                negative_by_category[category] += 1
            
            for category, count in negative_by_category.items():
                if count >= 3:  # At least 3 negative feedback items
                    improvement_areas.append({
                        "category": category,
                        "type": "negative_feedback",
                        "severity": "high" if count >= 5 else "medium",
                        "negative_count": count,
                        "recommendation": f"Address negative feedback in {category} - {count} negative comments"
                    })
        
        # Sort by severity
        improvement_areas.sort(key=lambda x: 0 if x["severity"] == "high" else 1)
        
        return {
            "success": True,
            "improvement_areas": improvement_areas,
            "total_areas": len(improvement_areas)
        }
    
    def generate_satisfaction_report(
        self,
        time_window_hours: int = 168
    ) -> Dict[str, Any]:
        """Generate comprehensive satisfaction report"""
        
        # Calculate overall satisfaction
        overall_satisfaction = self.calculate_satisfaction_score(
            time_window_hours=time_window_hours
        )
        
        # Calculate satisfaction by category
        category_satisfaction = {}
        for category in self.feedback_categories:
            result = self.calculate_satisfaction_score(
                category=category,
                time_window_hours=time_window_hours
            )
            if result.get("score_data"):
                category_satisfaction[category] = result["score_data"]
        
        # Analyze trends
        trends = self.analyze_feedback_trends(time_window_hours)
        
        # Identify improvement areas
        improvements = self.identify_improvement_areas(time_window_hours)
        
        report = {
            "overall_satisfaction": overall_satisfaction.get("score_data"),
            "category_satisfaction": category_satisfaction,
            "trends": trends.get("trends"),
            "improvement_areas": improvements.get("improvement_areas"),
            "time_window_hours": time_window_hours,
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "report": report
        }
    
    def _get_feedback(
        self,
        cutoff_time: datetime,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Get feedback after cutoff time"""
        
        feedback = []
        
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    item = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(item.get("timestamp", ""))
                    
                    if timestamp >= cutoff_time:
                        if category is None or item.get("category") == category:
                            feedback.append(item)
        
        return feedback
    
    def _get_ratings(
        self,
        cutoff_time: datetime,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Get ratings after cutoff time"""
        
        ratings = []
        
        if self.ratings_file.exists():
            with open(self.ratings_file, 'r') as f:
                for line in f:
                    item = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(item.get("timestamp", ""))
                    
                    if timestamp >= cutoff_time:
                        if category is None or item.get("category") == category:
                            ratings.append(item)
        
        return ratings
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get satisfaction statistics"""
        
        stats = {
            "total_feedback": 0,
            "total_ratings": 0,
            "sentiment_distribution": {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            },
            "avg_rating": 0,
            "by_category": {}
        }
        
        # Count feedback
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    feedback = json.loads(line.strip())
                    stats["total_feedback"] += 1
                    
                    sentiment = feedback.get("sentiment", {}).get("label", "neutral")
                    stats["sentiment_distribution"][sentiment] += 1
                    
                    category = feedback.get("category", "general")
                    if category not in stats["by_category"]:
                        stats["by_category"][category] = {
                            "feedback_count": 0,
                            "rating_count": 0
                        }
                    stats["by_category"][category]["feedback_count"] += 1
        
        # Count ratings
        rating_values = []
        if self.ratings_file.exists():
            with open(self.ratings_file, 'r') as f:
                for line in f:
                    rating = json.loads(line.strip())
                    stats["total_ratings"] += 1
                    rating_values.append(rating.get("rating", 0))
                    
                    category = rating.get("category", "general")
                    if category not in stats["by_category"]:
                        stats["by_category"][category] = {
                            "feedback_count": 0,
                            "rating_count": 0
                        }
                    stats["by_category"][category]["rating_count"] += 1
        
        if rating_values:
            stats["avg_rating"] = statistics.mean(rating_values)
        
        return stats

def get_analyzer() -> SatisfactionAnalyzer:
    """Get the singleton SatisfactionAnalyzer instance"""
    return SatisfactionAnalyzer()

if __name__ == "__main__":
    # Example usage
    analyzer = get_analyzer()
    
    # Record test feedback
    analyzer.record_feedback(
        feedback_id="fb_001",
        category="task_completion",
        feedback_text="Great job! The task was completed perfectly.",
        context="test_context"
    )
    
    # Record test rating
    analyzer.record_rating(
        rating_id="rating_001",
        category="task_completion",
        rating=5.0,
        comment="Excellent work"
    )
    
    print(f"Statistics: {json.dumps(analyzer.get_statistics(), indent=2)}")
