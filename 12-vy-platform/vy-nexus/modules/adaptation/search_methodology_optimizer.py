#!/usr/bin/env python3
"""
Search Methodology Optimizer

Optimizes search strategies and methodologies based on success rates,
user feedback, and result quality analysis.

Features:
- Multi-strategy search optimization
- Query refinement and expansion
- Result quality scoring
- Search pattern learning
- Source reliability tracking
- Performance-based strategy selection
- A/B testing for search methods
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import re


class SearchMethodologyOptimizer:
    """Optimizes search methodologies based on performance data."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/search_optimization"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Data files
        self.strategies_file = os.path.join(self.data_dir, "search_strategies.json")
        self.performance_file = os.path.join(self.data_dir, "strategy_performance.json")
        self.queries_file = os.path.join(self.data_dir, "query_history.json")
        self.sources_file = os.path.join(self.data_dir, "source_reliability.json")
        self.patterns_file = os.path.join(self.data_dir, "search_patterns.json")
        
        # Load data
        self.strategies = self._load_json(self.strategies_file, self._default_strategies())
        self.performance = self._load_json(self.performance_file, {})
        self.query_history = self._load_json(self.queries_file, [])
        self.source_reliability = self._load_json(self.sources_file, {})
        self.search_patterns = self._load_json(self.patterns_file, {})
    
    def _load_json(self, filepath: str, default):
        """Load JSON file or return default."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def _save_json(self, filepath: str, data):
        """Save data to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _default_strategies(self) -> Dict:
        """Return default search strategies."""
        return {
            "direct_search": {
                "name": "Direct Search",
                "description": "Search with original query",
                "enabled": True,
                "priority": 1,
                "success_rate": 0.7,
                "avg_quality": 0.6,
                "use_count": 0
            },
            "expanded_search": {
                "name": "Expanded Search",
                "description": "Add synonyms and related terms",
                "enabled": True,
                "priority": 2,
                "success_rate": 0.75,
                "avg_quality": 0.7,
                "use_count": 0
            },
            "refined_search": {
                "name": "Refined Search",
                "description": "Use more specific terms",
                "enabled": True,
                "priority": 3,
                "success_rate": 0.8,
                "avg_quality": 0.75,
                "use_count": 0
            },
            "boolean_search": {
                "name": "Boolean Search",
                "description": "Use AND, OR, NOT operators",
                "enabled": True,
                "priority": 4,
                "success_rate": 0.65,
                "avg_quality": 0.65,
                "use_count": 0
            },
            "phrase_search": {
                "name": "Phrase Search",
                "description": "Search for exact phrases",
                "enabled": True,
                "priority": 5,
                "success_rate": 0.7,
                "avg_quality": 0.8,
                "use_count": 0
            },
            "contextual_search": {
                "name": "Contextual Search",
                "description": "Add context from previous queries",
                "enabled": True,
                "priority": 6,
                "success_rate": 0.72,
                "avg_quality": 0.73,
                "use_count": 0
            },
            "multi_source_search": {
                "name": "Multi-Source Search",
                "description": "Search across multiple sources",
                "enabled": True,
                "priority": 7,
                "success_rate": 0.85,
                "avg_quality": 0.8,
                "use_count": 0
            },
            "semantic_search": {
                "name": "Semantic Search",
                "description": "Search by meaning, not just keywords",
                "enabled": True,
                "priority": 8,
                "success_rate": 0.78,
                "avg_quality": 0.82,
                "use_count": 0
            }
        }
    
    def optimize_query(self, query: str, context: Dict = None) -> Dict:
        """
        Optimize a search query using best strategies.
        
        Args:
            query: Original search query
            context: Additional context (previous queries, task type, etc.)
        
        Returns:
            Optimized query information
        """
        context = context or {}
        
        # Select best strategy based on performance
        strategy = self._select_best_strategy(query, context)
        
        # Apply strategy to optimize query
        optimized = self._apply_strategy(query, strategy, context)
        
        # Record query
        query_record = {
            "original_query": query,
            "optimized_query": optimized["query"],
            "strategy": strategy,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "query_id": len(self.query_history)
        }
        
        self.query_history.append(query_record)
        
        # Keep only last 1000 queries
        if len(self.query_history) > 1000:
            self.query_history = self.query_history[-1000:]
        
        self._save_json(self.queries_file, self.query_history)
        
        return {
            "query_id": query_record["query_id"],
            "original": query,
            "optimized": optimized["query"],
            "strategy": strategy,
            "suggestions": optimized.get("suggestions", []),
            "filters": optimized.get("filters", {})
        }
    
    def _select_best_strategy(self, query: str, context: Dict) -> str:
        """
        Select best search strategy based on query and context.
        
        Args:
            query: Search query
            context: Query context
        
        Returns:
            Strategy name
        """
        # Calculate scores for each strategy
        scores = {}
        
        for strategy_name, strategy_data in self.strategies.items():
            if not strategy_data["enabled"]:
                continue
            
            score = 0.0
            
            # Base score from success rate and quality
            score += strategy_data["success_rate"] * 0.4
            score += strategy_data["avg_quality"] * 0.4
            
            # Priority bonus (lower priority number = higher bonus)
            score += (10 - strategy_data["priority"]) * 0.02
            
            # Context-based adjustments
            if context.get("requires_precision"):
                if strategy_name in ["phrase_search", "refined_search"]:
                    score += 0.2
            
            if context.get("broad_search"):
                if strategy_name in ["expanded_search", "multi_source_search"]:
                    score += 0.2
            
            if context.get("previous_failed"):
                if strategy_name in ["semantic_search", "contextual_search"]:
                    score += 0.15
            
            # Query characteristics
            if len(query.split()) <= 2:
                if strategy_name == "expanded_search":
                    score += 0.1
            elif len(query.split()) >= 5:
                if strategy_name == "refined_search":
                    score += 0.1
            
            scores[strategy_name] = score
        
        # Select strategy with highest score
        best_strategy = max(scores.items(), key=lambda x: x[1])[0]
        
        return best_strategy
    
    def _apply_strategy(self, query: str, strategy: str, context: Dict) -> Dict:
        """
        Apply search strategy to query.
        
        Args:
            query: Original query
            strategy: Strategy to apply
            context: Query context
        
        Returns:
            Optimized query data
        """
        result = {
            "query": query,
            "suggestions": [],
            "filters": {}
        }
        
        if strategy == "direct_search":
            result["query"] = query
        
        elif strategy == "expanded_search":
            result["query"] = self._expand_query(query)
            result["suggestions"] = self._get_synonyms(query)
        
        elif strategy == "refined_search":
            result["query"] = self._refine_query(query)
            result["filters"] = self._suggest_filters(query)
        
        elif strategy == "boolean_search":
            result["query"] = self._add_boolean_operators(query)
        
        elif strategy == "phrase_search":
            result["query"] = self._create_phrase_search(query)
        
        elif strategy == "contextual_search":
            result["query"] = self._add_context(query, context)
        
        elif strategy == "multi_source_search":
            result["query"] = query
            result["sources"] = self._get_best_sources(query)
        
        elif strategy == "semantic_search":
            result["query"] = self._semantic_expansion(query)
            result["suggestions"] = self._get_related_concepts(query)
        
        # Update strategy usage
        self.strategies[strategy]["use_count"] += 1
        self._save_json(self.strategies_file, self.strategies)
        
        return result
    
    def _expand_query(self, query: str) -> str:
        """Expand query with related terms."""
        words = query.split()
        expanded = []
        
        for word in words:
            expanded.append(word)
            # Add common variations
            if word.endswith('ing'):
                expanded.append(word[:-3])  # Remove 'ing'
            elif word.endswith('ed'):
                expanded.append(word[:-2])  # Remove 'ed'
        
        return ' OR '.join(expanded)
    
    def _refine_query(self, query: str) -> str:
        """Refine query to be more specific."""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = [w for w in query.split() if w.lower() not in stop_words]
        return ' '.join(words)
    
    def _add_boolean_operators(self, query: str) -> str:
        """Add boolean operators to query."""
        words = query.split()
        if len(words) <= 1:
            return query
        return ' AND '.join(words)
    
    def _create_phrase_search(self, query: str) -> str:
        """Create phrase search query."""
        return f'"{query}"'
    
    def _add_context(self, query: str, context: Dict) -> str:
        """Add context to query."""
        contextual_query = query
        
        if context.get("previous_query"):
            contextual_query = f"{context['previous_query']} {query}"
        
        if context.get("domain"):
            contextual_query = f"{contextual_query} {context['domain']}"
        
        return contextual_query
    
    def _semantic_expansion(self, query: str) -> str:
        """Expand query semantically."""
        # Simple semantic expansion (in production, use NLP models)
        semantic_map = {
            'fast': ['quick', 'rapid', 'speedy'],
            'slow': ['sluggish', 'gradual'],
            'good': ['excellent', 'great', 'quality'],
            'bad': ['poor', 'inferior'],
            'big': ['large', 'huge', 'massive'],
            'small': ['tiny', 'little', 'compact']
        }
        
        words = query.lower().split()
        expanded = []
        
        for word in words:
            expanded.append(word)
            if word in semantic_map:
                expanded.extend(semantic_map[word][:2])  # Add top 2 synonyms
        
        return ' '.join(expanded)
    
    def _get_synonyms(self, query: str) -> List[str]:
        """Get synonym suggestions."""
        # Simplified synonym generation
        return [f"{query} alternative", f"{query} similar", f"{query} related"]
    
    def _suggest_filters(self, query: str) -> Dict:
        """Suggest search filters."""
        filters = {}
        
        # Date filters
        if any(word in query.lower() for word in ['recent', 'latest', 'new']):
            filters['date'] = 'last_month'
        
        # Type filters
        if any(word in query.lower() for word in ['tutorial', 'guide', 'how to']):
            filters['type'] = 'educational'
        
        return filters
    
    def _get_best_sources(self, query: str) -> List[str]:
        """Get best sources for query."""
        # Return sources sorted by reliability
        sources = sorted(
            self.source_reliability.items(),
            key=lambda x: x[1].get('reliability_score', 0.5),
            reverse=True
        )
        return [s[0] for s in sources[:5]]
    
    def _get_related_concepts(self, query: str) -> List[str]:
        """Get related concepts."""
        # Check search patterns for related queries
        related = []
        query_lower = query.lower()
        
        for pattern_key, pattern_data in self.search_patterns.items():
            if query_lower in pattern_key.lower():
                related.extend(pattern_data.get('related_queries', [])[:3])
        
        return related[:5]
    
    def record_search_result(self, query_id: int, results: List[Dict], user_feedback: Dict = None):
        """
        Record search results and feedback.
        
        Args:
            query_id: Query identifier
            results: Search results
            user_feedback: User feedback on results
        """
        if query_id >= len(self.query_history):
            return
        
        query_record = self.query_history[query_id]
        strategy = query_record["strategy"]
        
        # Calculate result quality
        quality_score = self._calculate_quality_score(results, user_feedback)
        
        # Update strategy performance
        if strategy not in self.performance:
            self.performance[strategy] = {
                "total_searches": 0,
                "successful_searches": 0,
                "quality_scores": [],
                "avg_quality": 0.0,
                "success_rate": 0.0
            }
        
        perf = self.performance[strategy]
        perf["total_searches"] += 1
        
        # Determine if search was successful
        is_successful = quality_score > 0.5 or (user_feedback and user_feedback.get('satisfied', False))
        
        if is_successful:
            perf["successful_searches"] += 1
        
        perf["quality_scores"].append(quality_score)
        
        # Keep only last 100 scores
        if len(perf["quality_scores"]) > 100:
            perf["quality_scores"] = perf["quality_scores"][-100:]
        
        # Update averages
        perf["success_rate"] = perf["successful_searches"] / perf["total_searches"]
        perf["avg_quality"] = sum(perf["quality_scores"]) / len(perf["quality_scores"])
        
        # Update strategy data
        self.strategies[strategy]["success_rate"] = perf["success_rate"]
        self.strategies[strategy]["avg_quality"] = perf["avg_quality"]
        
        # Update source reliability
        for result in results:
            source = result.get('source', 'unknown')
            self._update_source_reliability(source, quality_score, user_feedback)
        
        # Learn search patterns
        self._learn_search_pattern(query_record, results, user_feedback)
        
        # Save all data
        self._save_all()
    
    def _calculate_quality_score(self, results: List[Dict], user_feedback: Dict = None) -> float:
        """Calculate quality score for search results."""
        if not results:
            return 0.0
        
        score = 0.0
        
        # Base score from number of results
        if len(results) > 0:
            score += 0.3
        if len(results) >= 5:
            score += 0.2
        
        # Score from result relevance (if available)
        if results and 'relevance' in results[0]:
            avg_relevance = sum(r.get('relevance', 0) for r in results) / len(results)
            score += avg_relevance * 0.3
        
        # Score from user feedback
        if user_feedback:
            if user_feedback.get('satisfied'):
                score += 0.3
            if user_feedback.get('clicked_result'):
                score += 0.2
            if user_feedback.get('rating'):
                score += user_feedback['rating'] / 10 * 0.2
        
        return min(score, 1.0)
    
    def _update_source_reliability(self, source: str, quality_score: float, user_feedback: Dict = None):
        """Update source reliability score."""
        if source not in self.source_reliability:
            self.source_reliability[source] = {
                "reliability_score": 0.5,
                "total_results": 0,
                "quality_scores": [],
                "last_updated": datetime.now().isoformat()
            }
        
        src = self.source_reliability[source]
        src["total_results"] += 1
        src["quality_scores"].append(quality_score)
        
        # Keep only last 50 scores
        if len(src["quality_scores"]) > 50:
            src["quality_scores"] = src["quality_scores"][-50:]
        
        # Update reliability score
        src["reliability_score"] = sum(src["quality_scores"]) / len(src["quality_scores"])
        src["last_updated"] = datetime.now().isoformat()
    
    def _learn_search_pattern(self, query_record: Dict, results: List[Dict], user_feedback: Dict = None):
        """Learn patterns from search behavior."""
        query = query_record["original_query"].lower()
        
        if query not in self.search_patterns:
            self.search_patterns[query] = {
                "search_count": 0,
                "successful_strategies": [],
                "related_queries": [],
                "best_sources": []
            }
        
        pattern = self.search_patterns[query]
        pattern["search_count"] += 1
        
        # Record successful strategy
        if user_feedback and user_feedback.get('satisfied'):
            strategy = query_record["strategy"]
            if strategy not in pattern["successful_strategies"]:
                pattern["successful_strategies"].append(strategy)
        
        # Record best sources
        for result in results:
            source = result.get('source')
            if source and source not in pattern["best_sources"]:
                pattern["best_sources"].append(source)
        
        # Keep only top 5 sources
        pattern["best_sources"] = pattern["best_sources"][:5]
    
    def _save_all(self):
        """Save all data files."""
        self._save_json(self.strategies_file, self.strategies)
        self._save_json(self.performance_file, self.performance)
        self._save_json(self.queries_file, self.query_history)
        self._save_json(self.sources_file, self.source_reliability)
        self._save_json(self.patterns_file, self.search_patterns)
    
    def get_statistics(self) -> Dict:
        """Get search optimization statistics."""
        total_searches = sum(s["use_count"] for s in self.strategies.values())
        
        return {
            "total_searches": total_searches,
            "total_queries": len(self.query_history),
            "strategies_enabled": sum(1 for s in self.strategies.values() if s["enabled"]),
            "tracked_sources": len(self.source_reliability),
            "learned_patterns": len(self.search_patterns),
            "best_strategy": max(self.strategies.items(), key=lambda x: x[1]["success_rate"])[0] if self.strategies else None,
            "avg_success_rate": sum(s["success_rate"] for s in self.strategies.values()) / len(self.strategies),
            "top_sources": sorted(self.source_reliability.items(), key=lambda x: x[1]["reliability_score"], reverse=True)[:5]
        }
    
    def get_recommendations(self, query: str) -> Dict:
        """Get search recommendations for a query."""
        query_lower = query.lower()
        
        recommendations = {
            "suggested_strategy": self._select_best_strategy(query, {}),
            "query_variations": [],
            "recommended_sources": [],
            "related_searches": []
        }
        
        # Check if we've seen similar queries
        if query_lower in self.search_patterns:
            pattern = self.search_patterns[query_lower]
            recommendations["recommended_sources"] = pattern["best_sources"]
            recommendations["related_searches"] = pattern["related_queries"]
        
        # Generate query variations
        for strategy_name in ["expanded_search", "refined_search", "phrase_search"]:
            if self.strategies[strategy_name]["enabled"]:
                optimized = self._apply_strategy(query, strategy_name, {})
                recommendations["query_variations"].append({
                    "strategy": strategy_name,
                    "query": optimized["query"]
                })
        
        return recommendations


def test_search_methodology_optimizer():
    """Test the search methodology optimizer."""
    print("Testing Search Methodology Optimizer...")
    
    optimizer = SearchMethodologyOptimizer()
    
    # Test query optimization
    print("\n1. Optimizing queries...")
    result1 = optimizer.optimize_query("python automation tutorial")
    print(f"   Original: {result1['original']}")
    print(f"   Optimized: {result1['optimized']}")
    print(f"   Strategy: {result1['strategy']}")
    
    result2 = optimizer.optimize_query("fast data processing", context={"requires_precision": True})
    print(f"\n   Original: {result2['original']}")
    print(f"   Optimized: {result2['optimized']}")
    print(f"   Strategy: {result2['strategy']}")
    
    # Test recording results
    print("\n2. Recording search results...")
    mock_results = [
        {"title": "Result 1", "source": "stackoverflow", "relevance": 0.9},
        {"title": "Result 2", "source": "github", "relevance": 0.8}
    ]
    optimizer.record_search_result(
        result1['query_id'],
        mock_results,
        user_feedback={"satisfied": True, "clicked_result": True, "rating": 8}
    )
    print("   Results recorded successfully")
    
    # Test recommendations
    print("\n3. Getting recommendations...")
    recommendations = optimizer.get_recommendations("machine learning basics")
    print(f"   Suggested strategy: {recommendations['suggested_strategy']}")
    print(f"   Query variations: {len(recommendations['query_variations'])}")
    
    # Test statistics
    print("\n4. Search optimization statistics:")
    stats = optimizer.get_statistics()
    print(f"   Total searches: {stats['total_searches']}")
    print(f"   Total queries: {stats['total_queries']}")
    print(f"   Strategies enabled: {stats['strategies_enabled']}")
    print(f"   Best strategy: {stats['best_strategy']}")
    print(f"   Average success rate: {stats['avg_success_rate']:.2%}")
    
    print("\n✅ Search Methodology Optimizer test complete!")


if __name__ == "__main__":
    test_search_methodology_optimizer()
