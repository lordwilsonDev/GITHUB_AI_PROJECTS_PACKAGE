#!/usr/bin/env python3
"""
Tech/Business Trend Analyzer

Analyzes and tracks trends in:
- Technology developments
- Business strategies
- Industry movements
- Market dynamics
- Innovation patterns

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import re


class TechBusinessTrendAnalyzer:
    """
    Analyzes technology and business trends.
    
    Features:
    - Trend identification and tracking
    - Momentum calculation
    - Impact assessment
    - Prediction generation
    - Competitive intelligence
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/trends"):
        """
        Initialize the trend analyzer.
        
        Args:
            data_dir: Directory to store trend data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.trends_file = os.path.join(self.data_dir, "trends.json")
        self.signals_file = os.path.join(self.data_dir, "signals.json")
        self.predictions_file = os.path.join(self.data_dir, "predictions.json")
        self.categories_file = os.path.join(self.data_dir, "categories.json")
        
        self.trends = self._load_trends()
        self.signals = self._load_signals()
        self.predictions = self._load_predictions()
        self.categories = self._load_categories()
    
    def _load_trends(self) -> Dict[str, Any]:
        """Load trends from file."""
        if os.path.exists(self.trends_file):
            with open(self.trends_file, 'r') as f:
                return json.load(f)
        return {"trends": [], "metadata": {"total_trends": 0}}
    
    def _save_trends(self):
        """Save trends to file."""
        with open(self.trends_file, 'w') as f:
            json.dump(self.trends, f, indent=2)
    
    def _load_signals(self) -> Dict[str, Any]:
        """Load signals from file."""
        if os.path.exists(self.signals_file):
            with open(self.signals_file, 'r') as f:
                return json.load(f)
        return {"signals": []}
    
    def _save_signals(self):
        """Save signals to file."""
        with open(self.signals_file, 'w') as f:
            json.dump(self.signals, f, indent=2)
    
    def _load_predictions(self) -> Dict[str, Any]:
        """Load predictions from file."""
        if os.path.exists(self.predictions_file):
            with open(self.predictions_file, 'r') as f:
                return json.load(f)
        return {"predictions": []}
    
    def _save_predictions(self):
        """Save predictions to file."""
        with open(self.predictions_file, 'w') as f:
            json.dump(self.predictions, f, indent=2)
    
    def _load_categories(self) -> Dict[str, Any]:
        """Load trend categories."""
        if os.path.exists(self.categories_file):
            with open(self.categories_file, 'r') as f:
                return json.load(f)
        
        categories = {
            "technology": {
                "ai_ml": ["machine_learning", "deep_learning", "nlp", "computer_vision"],
                "cloud": ["serverless", "kubernetes", "microservices", "edge_computing"],
                "web": ["web3", "progressive_web_apps", "jamstack", "webassembly"],
                "mobile": ["cross_platform", "5g", "ar_vr", "mobile_first"],
                "data": ["big_data", "data_lakes", "real_time_analytics", "data_mesh"]
            },
            "business": {
                "strategy": ["digital_transformation", "platform_business", "ecosystem", "agile"],
                "operations": ["automation", "remote_work", "hybrid_model", "sustainability"],
                "customer": ["personalization", "omnichannel", "customer_experience", "self_service"],
                "innovation": ["open_innovation", "lean_startup", "design_thinking", "mvp"]
            },
            "industry": {
                "fintech": ["defi", "neobanks", "embedded_finance", "open_banking"],
                "healthtech": ["telemedicine", "wearables", "precision_medicine", "health_ai"],
                "edtech": ["online_learning", "adaptive_learning", "microlearning", "gamification"],
                "retail": ["ecommerce", "social_commerce", "direct_to_consumer", "subscription"]
            }
        }
        
        with open(self.categories_file, 'w') as f:
            json.dump(categories, f, indent=2)
        
        return categories
    
    def add_signal(self,
                  signal_type: str,
                  content: str,
                  source: str,
                  category: str,
                  subcategory: str = None,
                  metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add a trend signal (observation, news, data point).
        
        Args:
            signal_type: Type of signal (news, data, observation, research)
            content: Signal content
            source: Source of signal
            category: Main category
            subcategory: Subcategory
            metadata: Additional metadata
        
        Returns:
            Created signal
        """
        signal_id = f"signal_{len(self.signals['signals']) + 1:06d}"
        
        signal = {
            "signal_id": signal_id,
            "signal_type": signal_type,
            "content": content,
            "source": source,
            "category": category,
            "subcategory": subcategory,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "processed": False,
            "related_trends": []
        }
        
        self.signals["signals"].append(signal)
        self._save_signals()
        
        # Try to match with existing trends
        self._match_signal_to_trends(signal_id)
        
        return signal
    
    def _match_signal_to_trends(self, signal_id: str):
        """
        Match a signal to existing trends.
        
        Args:
            signal_id: ID of signal
        """
        signal = self._get_signal(signal_id)
        if not signal:
            return
        
        # Find trends in same category
        matching_trends = [
            t for t in self.trends["trends"]
            if t["category"] == signal["category"] and t["status"] == "active"
        ]
        
        # Simple keyword matching
        signal_keywords = set(re.findall(r'\w+', signal["content"].lower()))
        
        for trend in matching_trends:
            trend_keywords = set(re.findall(r'\w+', trend["name"].lower()))
            
            # If significant overlap, link them
            overlap = len(signal_keywords & trend_keywords)
            if overlap >= 2:
                signal["related_trends"].append(trend["trend_id"])
                
                # Add signal to trend
                if "signals" not in trend:
                    trend["signals"] = []
                trend["signals"].append(signal_id)
                
                # Update trend momentum
                self._update_trend_momentum(trend["trend_id"])
        
        signal["processed"] = True
        self._save_signals()
        self._save_trends()
    
    def create_trend(self,
                    name: str,
                    description: str,
                    category: str,
                    subcategory: str = None,
                    initial_momentum: float = 0.5,
                    tags: List[str] = None) -> Dict[str, Any]:
        """
        Create a new trend to track.
        
        Args:
            name: Trend name
            description: Trend description
            category: Main category
            subcategory: Subcategory
            initial_momentum: Initial momentum score (0-1)
            tags: Associated tags
        
        Returns:
            Created trend
        """
        trend_id = f"trend_{len(self.trends['trends']) + 1:06d}"
        
        trend = {
            "trend_id": trend_id,
            "name": name,
            "description": description,
            "category": category,
            "subcategory": subcategory,
            "status": "active",
            "momentum": initial_momentum,
            "momentum_history": [{"timestamp": datetime.now().isoformat(), "value": initial_momentum}],
            "impact_score": 0.5,
            "maturity_stage": "emerging",
            "tags": tags or [],
            "signals": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_signal_at": None
        }
        
        self.trends["trends"].append(trend)
        self.trends["metadata"]["total_trends"] += 1
        self._save_trends()
        
        return trend
    
    def _update_trend_momentum(self, trend_id: str):
        """
        Update trend momentum based on signal frequency.
        
        Args:
            trend_id: ID of trend
        """
        trend = self._get_trend(trend_id)
        if not trend:
            return
        
        # Count recent signals (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_signals = 0
        
        for signal_id in trend.get("signals", []):
            signal = self._get_signal(signal_id)
            if signal:
                signal_date = datetime.fromisoformat(signal["timestamp"])
                if signal_date > cutoff_date:
                    recent_signals += 1
        
        # Calculate momentum (0-1 scale)
        # More signals = higher momentum
        new_momentum = min(recent_signals / 10.0, 1.0)
        
        # Smooth with previous momentum (70% new, 30% old)
        old_momentum = trend["momentum"]
        trend["momentum"] = (new_momentum * 0.7) + (old_momentum * 0.3)
        
        # Update momentum history
        trend["momentum_history"].append({
            "timestamp": datetime.now().isoformat(),
            "value": trend["momentum"]
        })
        
        # Keep only last 50 history points
        if len(trend["momentum_history"]) > 50:
            trend["momentum_history"] = trend["momentum_history"][-50:]
        
        # Update maturity stage based on momentum and age
        self._update_maturity_stage(trend_id)
        
        trend["updated_at"] = datetime.now().isoformat()
        trend["last_signal_at"] = datetime.now().isoformat()
        self._save_trends()
    
    def _update_maturity_stage(self, trend_id: str):
        """
        Update trend maturity stage.
        
        Args:
            trend_id: ID of trend
        """
        trend = self._get_trend(trend_id)
        if not trend:
            return
        
        created = datetime.fromisoformat(trend["created_at"])
        age_days = (datetime.now() - created).days
        momentum = trend["momentum"]
        
        # Determine maturity stage
        if age_days < 30 and momentum < 0.5:
            stage = "emerging"
        elif age_days < 90 and momentum >= 0.5:
            stage = "growing"
        elif momentum >= 0.7:
            stage = "mainstream"
        elif momentum < 0.3:
            stage = "declining"
        else:
            stage = "mature"
        
        trend["maturity_stage"] = stage
    
    def calculate_impact_score(self, trend_id: str) -> float:
        """
        Calculate potential impact score for a trend.
        
        Args:
            trend_id: ID of trend
        
        Returns:
            Impact score (0-1)
        """
        trend = self._get_trend(trend_id)
        if not trend:
            return 0.0
        
        # Factors:
        # 1. Momentum (40%)
        momentum_score = trend["momentum"]
        
        # 2. Signal diversity (30%) - more diverse sources = higher impact
        signal_sources = set()
        for signal_id in trend.get("signals", []):
            signal = self._get_signal(signal_id)
            if signal:
                signal_sources.add(signal["source"])
        diversity_score = min(len(signal_sources) / 5.0, 1.0)
        
        # 3. Recency (30%) - recent activity = higher impact
        if trend["last_signal_at"]:
            last_signal = datetime.fromisoformat(trend["last_signal_at"])
            days_since = (datetime.now() - last_signal).days
            recency_score = max(0, 1.0 - (days_since / 30.0))
        else:
            recency_score = 0.0
        
        impact_score = (
            momentum_score * 0.4 +
            diversity_score * 0.3 +
            recency_score * 0.3
        )
        
        trend["impact_score"] = round(impact_score, 3)
        self._save_trends()
        
        return impact_score
    
    def generate_prediction(self,
                          trend_id: str,
                          timeframe: str = "3_months") -> Dict[str, Any]:
        """
        Generate prediction for trend trajectory.
        
        Args:
            trend_id: ID of trend
            timeframe: Prediction timeframe
        
        Returns:
            Prediction dictionary
        """
        trend = self._get_trend(trend_id)
        if not trend:
            return {}
        
        # Analyze momentum history
        history = trend["momentum_history"]
        if len(history) < 3:
            return {"error": "Insufficient data for prediction"}
        
        # Simple trend analysis
        recent_values = [h["value"] for h in history[-5:]]
        avg_momentum = sum(recent_values) / len(recent_values)
        
        # Calculate trend direction
        if len(recent_values) >= 2:
            trend_direction = recent_values[-1] - recent_values[0]
        else:
            trend_direction = 0
        
        # Predict future momentum
        if trend_direction > 0.1:
            prediction = "accelerating"
            confidence = min(0.9, avg_momentum + 0.2)
        elif trend_direction < -0.1:
            prediction = "declining"
            confidence = min(0.9, 1.0 - avg_momentum + 0.2)
        else:
            prediction = "stable"
            confidence = 0.7
        
        prediction_obj = {
            "prediction_id": f"pred_{len(self.predictions['predictions']) + 1:06d}",
            "trend_id": trend_id,
            "trend_name": trend["name"],
            "timeframe": timeframe,
            "prediction": prediction,
            "confidence": round(confidence, 2),
            "current_momentum": trend["momentum"],
            "predicted_momentum": round(min(1.0, max(0.0, avg_momentum + trend_direction)), 2),
            "reasoning": self._generate_reasoning(trend, prediction),
            "created_at": datetime.now().isoformat()
        }
        
        self.predictions["predictions"].append(prediction_obj)
        self._save_predictions()
        
        return prediction_obj
    
    def _generate_reasoning(self, trend: Dict[str, Any], prediction: str) -> str:
        """
        Generate reasoning for prediction.
        
        Args:
            trend: Trend dictionary
            prediction: Prediction type
        
        Returns:
            Reasoning text
        """
        signal_count = len(trend.get("signals", []))
        momentum = trend["momentum"]
        stage = trend["maturity_stage"]
        
        if prediction == "accelerating":
            return f"Trend shows {signal_count} signals with {momentum:.1%} momentum in {stage} stage, indicating growth."
        elif prediction == "declining":
            return f"Trend has {signal_count} signals with declining {momentum:.1%} momentum, suggesting maturation or decline."
        else:
            return f"Trend maintains stable {momentum:.1%} momentum with {signal_count} signals in {stage} stage."
    
    def get_trending_topics(self, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get currently trending topics.
        
        Args:
            category: Filter by category
            limit: Maximum number of results
        
        Returns:
            List of trending topics
        """
        trends = self.trends["trends"]
        
        # Filter by category if specified
        if category:
            trends = [t for t in trends if t["category"] == category]
        
        # Filter active trends
        trends = [t for t in trends if t["status"] == "active"]
        
        # Update impact scores
        for trend in trends:
            self.calculate_impact_score(trend["trend_id"])
        
        # Sort by momentum and impact
        trends.sort(key=lambda x: (x["momentum"] * 0.6 + x["impact_score"] * 0.4), reverse=True)
        
        return trends[:limit]
    
    def get_emerging_trends(self, min_momentum: float = 0.4) -> List[Dict[str, Any]]:
        """
        Get emerging trends with growth potential.
        
        Args:
            min_momentum: Minimum momentum threshold
        
        Returns:
            List of emerging trends
        """
        emerging = [
            t for t in self.trends["trends"]
            if t["maturity_stage"] == "emerging" and
               t["momentum"] >= min_momentum and
               t["status"] == "active"
        ]
        
        # Sort by momentum
        emerging.sort(key=lambda x: x["momentum"], reverse=True)
        
        return emerging
    
    def analyze_category(self, category: str) -> Dict[str, Any]:
        """
        Analyze trends in a specific category.
        
        Args:
            category: Category to analyze
        
        Returns:
            Category analysis
        """
        category_trends = [t for t in self.trends["trends"] if t["category"] == category]
        
        if not category_trends:
            return {"error": "No trends found in category"}
        
        # Calculate statistics
        total_trends = len(category_trends)
        active_trends = len([t for t in category_trends if t["status"] == "active"])
        avg_momentum = sum(t["momentum"] for t in category_trends) / total_trends
        
        # Count by maturity stage
        stage_counts = defaultdict(int)
        for trend in category_trends:
            stage_counts[trend["maturity_stage"]] += 1
        
        # Get top trends
        top_trends = sorted(category_trends, key=lambda x: x["momentum"], reverse=True)[:5]
        
        return {
            "category": category,
            "total_trends": total_trends,
            "active_trends": active_trends,
            "average_momentum": round(avg_momentum, 3),
            "maturity_distribution": dict(stage_counts),
            "top_trends": [{
                "name": t["name"],
                "momentum": t["momentum"],
                "stage": t["maturity_stage"]
            } for t in top_trends]
        }
    
    def _get_trend(self, trend_id: str) -> Optional[Dict[str, Any]]:
        """Get trend by ID."""
        for trend in self.trends["trends"]:
            if trend["trend_id"] == trend_id:
                return trend
        return None
    
    def _get_signal(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """Get signal by ID."""
        for signal in self.signals["signals"]:
            if signal["signal_id"] == signal_id:
                return signal
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get trend analysis statistics.
        
        Returns:
            Statistics dictionary
        """
        trends = self.trends["trends"]
        signals = self.signals["signals"]
        
        return {
            "total_trends": len(trends),
            "active_trends": len([t for t in trends if t["status"] == "active"]),
            "total_signals": len(signals),
            "processed_signals": len([s for s in signals if s["processed"]]),
            "total_predictions": len(self.predictions["predictions"]),
            "categories_tracked": len(set(t["category"] for t in trends)),
            "average_momentum": round(sum(t["momentum"] for t in trends) / len(trends), 3) if trends else 0
        }


def test_tech_business_trend_analyzer():
    """Test the trend analyzer."""
    print("Testing Tech/Business Trend Analyzer...")
    print("=" * 60)
    
    analyzer = TechBusinessTrendAnalyzer()
    
    # Test 1: Create trends
    print("\n1. Creating trends...")
    trend1 = analyzer.create_trend(
        name="AI Agents",
        description="Autonomous AI agents for task automation",
        category="technology",
        subcategory="ai_ml",
        initial_momentum=0.7,
        tags=["ai", "automation", "agents"]
    )
    print(f"   Created: {trend1['name']} (Momentum: {trend1['momentum']})")
    
    # Test 2: Add signals
    print("\n2. Adding signals...")
    signal1 = analyzer.add_signal(
        signal_type="news",
        content="Major tech company launches AI agent platform",
        source="TechCrunch",
        category="technology",
        subcategory="ai_ml"
    )
    print(f"   Added signal: {signal1['signal_id']}")
    
    # Test 3: Calculate impact
    print("\n3. Calculating impact score...")
    impact = analyzer.calculate_impact_score(trend1["trend_id"])
    print(f"   Impact score: {impact:.3f}")
    
    # Test 4: Generate prediction
    print("\n4. Generating prediction...")
    prediction = analyzer.generate_prediction(trend1["trend_id"])
    print(f"   Prediction: {prediction.get('prediction', 'N/A')}")
    print(f"   Confidence: {prediction.get('confidence', 0):.2f}")
    
    # Test 5: Get trending topics
    print("\n5. Getting trending topics...")
    trending = analyzer.get_trending_topics(limit=5)
    print(f"   Found {len(trending)} trending topics")
    
    # Test 6: Analyze category
    print("\n6. Analyzing category...")
    analysis = analyzer.analyze_category("technology")
    print(f"   Total trends: {analysis.get('total_trends', 0)}")
    print(f"   Average momentum: {analysis.get('average_momentum', 0):.3f}")
    
    # Test 7: Get statistics
    print("\n7. Getting statistics...")
    stats = analyzer.get_statistics()
    print(f"   Total trends: {stats['total_trends']}")
    print(f"   Total signals: {stats['total_signals']}")
    print(f"   Categories tracked: {stats['categories_tracked']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_tech_business_trend_analyzer()
