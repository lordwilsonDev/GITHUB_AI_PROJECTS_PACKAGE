#!/usr/bin/env python3
"""
Search Methodology Refiner
Refines and optimizes search strategies based on results and feedback
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict
import re

@dataclass
class SearchQuery:
    """Represents a search query"""
    id: str
    query: str
    search_type: str  # web, local, knowledge_base, code, documentation
    timestamp: str
    context: str
    filters: Dict[str, Any] = field(default_factory=dict)
    refinements: List[str] = field(default_factory=list)
    
@dataclass
class SearchResult:
    """Represents search results"""
    query_id: str
    results_count: int
    relevant_count: int
    execution_time: float
    sources: List[str]
    quality_score: float  # 0-10
    user_satisfaction: Optional[float] = None  # 0-10
    clicked_results: List[int] = field(default_factory=list)
    feedback: Optional[str] = None

@dataclass
class SearchStrategy:
    """Represents a search strategy"""
    name: str
    description: str
    applicable_contexts: List[str]
    query_patterns: List[str]
    filters: Dict[str, Any]
    ranking_criteria: List[str]
    success_rate: float = 0.0
    avg_quality_score: float = 0.0
    usage_count: int = 0
    
class SearchMethodologyRefiner:
    """Refines search methodologies based on outcomes"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data/search")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.queries_file = self.base_dir / "queries.jsonl"
        self.results_file = self.base_dir / "results.jsonl"
        self.strategies_file = self.base_dir / "strategies.jsonl"
        self.refinements_file = self.base_dir / "refinements.jsonl"
        
        self.queries: Dict[str, SearchQuery] = {}
        self.results: Dict[str, SearchResult] = {}
        self.strategies: Dict[str, SearchStrategy] = {}
        
        self._initialize_default_strategies()
        self.load_search_data()
        
        self._initialized = True
    
    def _initialize_default_strategies(self):
        """Initialize default search strategies"""
        self.strategies = {
            "broad_exploratory": SearchStrategy(
                name="Broad Exploratory",
                description="Wide search for initial exploration",
                applicable_contexts=["research", "discovery", "learning"],
                query_patterns=["general terms", "broad concepts"],
                filters={"max_results": 50, "diversity": "high"},
                ranking_criteria=["relevance", "diversity", "recency"]
            ),
            "precise_targeted": SearchStrategy(
                name="Precise Targeted",
                description="Narrow search for specific information",
                applicable_contexts=["troubleshooting", "specific_answer", "verification"],
                query_patterns=["specific terms", "exact phrases", "technical terms"],
                filters={"max_results": 10, "precision": "high"},
                ranking_criteria=["exact_match", "authority", "relevance"]
            ),
            "iterative_refinement": SearchStrategy(
                name="Iterative Refinement",
                description="Progressive refinement based on initial results",
                applicable_contexts=["complex_research", "multi_faceted"],
                query_patterns=["initial broad", "then narrow", "add filters"],
                filters={"iterations": 3, "refinement_threshold": 0.7},
                ranking_criteria=["relevance", "comprehensiveness"]
            ),
            "semantic_contextual": SearchStrategy(
                name="Semantic Contextual",
                description="Search using semantic understanding and context",
                applicable_contexts=["natural_language", "conceptual"],
                query_patterns=["natural language", "questions", "descriptions"],
                filters={"semantic_matching": True, "context_aware": True},
                ranking_criteria=["semantic_similarity", "context_relevance"]
            ),
            "multi_source_aggregation": SearchStrategy(
                name="Multi-Source Aggregation",
                description="Search across multiple sources and aggregate",
                applicable_contexts=["comprehensive_research", "verification"],
                query_patterns=["same query multiple sources"],
                filters={"sources": ["web", "local", "knowledge_base"], "aggregate": True},
                ranking_criteria=["source_diversity", "consensus", "authority"]
            )
        }
    
    def load_search_data(self):
        """Load search data from storage"""
        # Load queries
        if self.queries_file.exists():
            with open(self.queries_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if 'filters' not in data:
                            data['filters'] = {}
                        if 'refinements' not in data:
                            data['refinements'] = []
                        query = SearchQuery(**data)
                        self.queries[query.id] = query
        
        # Load results
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if 'clicked_results' not in data:
                            data['clicked_results'] = []
                        result = SearchResult(**data)
                        self.results[result.query_id] = result
        
        # Load custom strategies
        if self.strategies_file.exists():
            with open(self.strategies_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        strategy = SearchStrategy(**data)
                        self.strategies[strategy.name] = strategy
    
    def record_search(self, query: str, search_type: str, context: str,
                     filters: Dict[str, Any] = None) -> SearchQuery:
        """Record a search query"""
        query_id = f"query_{datetime.now().timestamp()}"
        
        search_query = SearchQuery(
            id=query_id,
            query=query,
            search_type=search_type,
            timestamp=datetime.now().isoformat(),
            context=context,
            filters=filters or {},
            refinements=[]
        )
        
        self.queries[query_id] = search_query
        
        with open(self.queries_file, 'a') as f:
            f.write(json.dumps(asdict(search_query)) + '\n')
        
        return search_query
    
    def record_results(self, query_id: str, results_count: int,
                      relevant_count: int, execution_time: float,
                      sources: List[str], quality_score: float) -> SearchResult:
        """Record search results"""
        result = SearchResult(
            query_id=query_id,
            results_count=results_count,
            relevant_count=relevant_count,
            execution_time=execution_time,
            sources=sources,
            quality_score=quality_score
        )
        
        self.results[query_id] = result
        
        with open(self.results_file, 'a') as f:
            f.write(json.dumps(asdict(result)) + '\n')
        
        return result
    
    def record_user_feedback(self, query_id: str, satisfaction: float,
                           clicked_results: List[int] = None,
                           feedback: str = None):
        """Record user feedback on search results"""
        if query_id not in self.results:
            return False
        
        result = self.results[query_id]
        result.user_satisfaction = satisfaction
        if clicked_results:
            result.clicked_results = clicked_results
        if feedback:
            result.feedback = feedback
        
        # Re-save result
        with open(self.results_file, 'a') as f:
            f.write(json.dumps(asdict(result)) + '\n')
        
        # Learn from feedback
        self._learn_from_feedback(query_id, satisfaction, clicked_results, feedback)
        
        return True
    
    def refine_query(self, query_id: str, refinement_type: str,
                    refinement_value: Any) -> Optional[SearchQuery]:
        """Refine a search query"""
        if query_id not in self.queries:
            return None
        
        query = self.queries[query_id]
        
        refinement_desc = f"{refinement_type}: {refinement_value}"
        query.refinements.append(refinement_desc)
        
        # Apply refinement
        if refinement_type == "add_term":
            query.query += f" {refinement_value}"
        elif refinement_type == "exclude_term":
            query.query += f" -{refinement_value}"
        elif refinement_type == "exact_phrase":
            query.query = f'"{refinement_value}"'
        elif refinement_type == "add_filter":
            query.filters.update(refinement_value)
        elif refinement_type == "narrow_context":
            query.context = refinement_value
        
        # Record refinement
        refinement_record = {
            "timestamp": datetime.now().isoformat(),
            "query_id": query_id,
            "type": refinement_type,
            "value": str(refinement_value),
            "resulting_query": query.query
        }
        
        with open(self.refinements_file, 'a') as f:
            f.write(json.dumps(refinement_record) + '\n')
        
        return query
    
    def suggest_query_improvements(self, query: str, context: str) -> List[str]:
        """Suggest improvements to a search query"""
        suggestions = []
        
        # Check query length
        word_count = len(query.split())
        if word_count < 2:
            suggestions.append("Add more specific terms to narrow results")
        elif word_count > 10:
            suggestions.append("Consider simplifying query - too many terms may reduce relevance")
        
        # Check for common issues
        if query.isupper():
            suggestions.append("Use mixed case for better matching")
        
        if not any(char.isalpha() for char in query):
            suggestions.append("Add descriptive terms to improve results")
        
        # Context-specific suggestions
        if context == "troubleshooting":
            if "error" not in query.lower() and "issue" not in query.lower():
                suggestions.append("Include error messages or specific symptoms")
        
        if context == "research":
            if not any(word in query.lower() for word in ["how", "what", "why", "when"]):
                suggestions.append("Frame as a question for better semantic matching")
        
        # Learn from past successful queries
        similar_successful = self._find_similar_successful_queries(query, context)
        if similar_successful:
            suggestions.append(f"Similar successful query used: '{similar_successful[0]}'")
        
        return suggestions
    
    def _find_similar_successful_queries(self, query: str, context: str,
                                        limit: int = 3) -> List[str]:
        """Find similar queries that were successful"""
        successful = []
        query_words = set(query.lower().split())
        
        for qid, q in self.queries.items():
            if q.context == context and qid in self.results:
                result = self.results[qid]
                if result.user_satisfaction and result.user_satisfaction >= 7.0:
                    # Calculate similarity
                    q_words = set(q.query.lower().split())
                    overlap = len(query_words & q_words)
                    if overlap >= 2:  # At least 2 words in common
                        successful.append((q.query, overlap))
        
        # Sort by overlap and return top queries
        successful.sort(key=lambda x: x[1], reverse=True)
        return [q for q, _ in successful[:limit]]
    
    def select_strategy(self, context: str, query_complexity: str = "medium") -> SearchStrategy:
        """Select best search strategy for context"""
        # Find applicable strategies
        applicable = [
            s for s in self.strategies.values()
            if context in s.applicable_contexts
        ]
        
        if not applicable:
            # Default to broad exploratory
            return self.strategies["broad_exploratory"]
        
        # Select based on success rate and quality
        if len(applicable) == 1:
            return applicable[0]
        
        # Score strategies
        scored = []
        for strategy in applicable:
            score = (
                strategy.success_rate * 0.5 +
                (strategy.avg_quality_score / 10) * 0.3 +
                (min(strategy.usage_count, 100) / 100) * 0.2
            )
            scored.append((strategy, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0]
    
    def update_strategy_performance(self, strategy_name: str,
                                   success: bool, quality_score: float):
        """Update strategy performance metrics"""
        if strategy_name not in self.strategies:
            return
        
        strategy = self.strategies[strategy_name]
        strategy.usage_count += 1
        
        # Update success rate
        total_successes = strategy.success_rate * (strategy.usage_count - 1)
        total_successes += 1 if success else 0
        strategy.success_rate = total_successes / strategy.usage_count
        
        # Update average quality score
        total_quality = strategy.avg_quality_score * (strategy.usage_count - 1)
        strategy.avg_quality_score = (total_quality + quality_score) / strategy.usage_count
        
        # Save updated strategy
        with open(self.strategies_file, 'a') as f:
            f.write(json.dumps(asdict(strategy)) + '\n')
    
    def _learn_from_feedback(self, query_id: str, satisfaction: float,
                           clicked_results: List[int], feedback: str):
        """Learn from user feedback to improve future searches"""
        if query_id not in self.queries:
            return
        
        query = self.queries[query_id]
        
        # Analyze what worked
        if satisfaction >= 7.0:
            # Successful search - reinforce this approach
            # Extract successful patterns
            if query.query:
                # Could implement pattern extraction here
                pass
        else:
            # Unsuccessful search - learn what to avoid
            if feedback:
                # Analyze feedback for improvement hints
                if "too many" in feedback.lower():
                    # Learn to narrow searches
                    pass
                elif "not enough" in feedback.lower() or "missing" in feedback.lower():
                    # Learn to broaden searches
                    pass
    
    def analyze_search_patterns(self, days: int = 30) -> Dict:
        """Analyze search patterns over time"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        recent_queries = [
            q for q in self.queries.values()
            if datetime.fromisoformat(q.timestamp) > cutoff_time
        ]
        
        if not recent_queries:
            return {"message": "No recent search data"}
        
        # Analyze patterns
        by_type = defaultdict(int)
        by_context = defaultdict(int)
        total_refinements = 0
        
        for query in recent_queries:
            by_type[query.search_type] += 1
            by_context[query.context] += 1
            total_refinements += len(query.refinements)
        
        # Analyze results quality
        recent_results = [
            r for qid, r in self.results.items()
            if qid in [q.id for q in recent_queries]
        ]
        
        avg_quality = 0
        avg_satisfaction = 0
        satisfaction_count = 0
        
        for result in recent_results:
            avg_quality += result.quality_score
            if result.user_satisfaction is not None:
                avg_satisfaction += result.user_satisfaction
                satisfaction_count += 1
        
        if recent_results:
            avg_quality /= len(recent_results)
        if satisfaction_count > 0:
            avg_satisfaction /= satisfaction_count
        
        return {
            "time_period_days": days,
            "total_searches": len(recent_queries),
            "by_type": dict(by_type),
            "by_context": dict(by_context),
            "avg_refinements_per_query": round(total_refinements / len(recent_queries), 2),
            "avg_quality_score": round(avg_quality, 2),
            "avg_user_satisfaction": round(avg_satisfaction, 2),
            "satisfaction_response_rate": round(satisfaction_count / len(recent_results) * 100, 2) if recent_results else 0
        }
    
    def get_search_recommendations(self) -> List[str]:
        """Get recommendations for improving search methodology"""
        recommendations = []
        
        analysis = self.analyze_search_patterns(days=7)
        
        if analysis.get("avg_quality_score", 10) < 6.0:
            recommendations.append("Search quality is below target - review query formulation strategies")
        
        if analysis.get("avg_user_satisfaction", 10) < 7.0:
            recommendations.append("User satisfaction with searches is low - consider refining result ranking")
        
        if analysis.get("avg_refinements_per_query", 0) > 2.0:
            recommendations.append("High refinement rate - improve initial query quality")
        
        # Strategy-specific recommendations
        for strategy in self.strategies.values():
            if strategy.usage_count > 10 and strategy.success_rate < 0.6:
                recommendations.append(f"Strategy '{strategy.name}' has low success rate - review and refine")
        
        if not recommendations:
            recommendations.append("Search methodology is performing well - maintain current approach")
        
        return recommendations
    
    def get_search_stats(self) -> Dict:
        """Get statistics about search activity"""
        return {
            "total_queries": len(self.queries),
            "total_results_recorded": len(self.results),
            "total_strategies": len(self.strategies),
            "recent_analysis": self.analyze_search_patterns(days=7),
            "strategy_performance": {
                name: {
                    "success_rate": round(s.success_rate * 100, 2),
                    "avg_quality": round(s.avg_quality_score, 2),
                    "usage_count": s.usage_count
                }
                for name, s in self.strategies.items()
            }
        }
    
    def export_search_insights(self) -> Dict:
        """Export search insights and learnings"""
        return {
            "generated_at": datetime.now().isoformat(),
            "stats": self.get_search_stats(),
            "recommendations": self.get_search_recommendations(),
            "top_strategies": [
                {
                    "name": s.name,
                    "success_rate": round(s.success_rate * 100, 2),
                    "avg_quality": round(s.avg_quality_score, 2)
                }
                for s in sorted(self.strategies.values(),
                              key=lambda x: x.success_rate,
                              reverse=True)[:5]
            ]
        }

def get_refiner() -> SearchMethodologyRefiner:
    """Get singleton instance of search methodology refiner"""
    return SearchMethodologyRefiner()

if __name__ == "__main__":
    # Example usage
    refiner = get_refiner()
    
    # Record a search
    query = refiner.record_search(
        query="python async programming best practices",
        search_type="web",
        context="research",
        filters={"language": "en", "recency": "1year"}
    )
    print(f"Recorded query: {query.id}")
    
    # Record results
    result = refiner.record_results(
        query_id=query.id,
        results_count=25,
        relevant_count=18,
        execution_time=1.2,
        sources=["web"],
        quality_score=7.5
    )
    print(f"Recorded results: {result.results_count} total, {result.relevant_count} relevant")
    
    # Get suggestions
    suggestions = refiner.suggest_query_improvements(
        "error",
        "troubleshooting"
    )
    print(f"Suggestions: {suggestions}")
    
    # Get stats
    stats = refiner.get_search_stats()
    print(f"Search stats: {stats}")
