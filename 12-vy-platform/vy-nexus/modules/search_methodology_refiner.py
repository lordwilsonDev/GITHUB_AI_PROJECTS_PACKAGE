"""
Search/Research Methodology Refiner Module

This module continuously improves search and research methodologies by:
- Analyzing search effectiveness
- Learning from successful searches
- Optimizing search strategies
- Adapting to different information sources
- Refining query formulation
- Tracking research patterns

Author: Vy Self-Evolving AI Ecosystem
Phase: 4 - Real-Time Adaptation System
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import re
from collections import Counter


class SearchType(Enum):
    """Types of searches"""
    WEB_SEARCH = "web_search"
    DATABASE_QUERY = "database_query"
    FILE_SEARCH = "file_search"
    API_QUERY = "api_query"
    KNOWLEDGE_BASE = "knowledge_base"


class SearchOutcome(Enum):
    """Search result outcomes"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    NO_RESULTS = "no_results"
    TOO_MANY_RESULTS = "too_many_results"


@dataclass
class SearchQuery:
    """Search query representation"""
    query_id: str
    query_text: str
    search_type: str
    context: str
    filters: Dict
    timestamp: str
    user_id: str


@dataclass
class SearchResult:
    """Search result representation"""
    result_id: str
    query_id: str
    results_count: int
    relevant_count: int
    execution_time: float  # seconds
    outcome: str
    quality_score: float  # 0.0 to 1.0
    user_feedback: Optional[str]
    timestamp: str


@dataclass
class SearchStrategy:
    """Search strategy definition"""
    strategy_id: str
    name: str
    search_type: str
    query_template: str
    filters_template: Dict
    success_rate: float
    avg_quality_score: float
    usage_count: int
    created_at: str
    updated_at: str


@dataclass
class QueryRefinement:
    """Query refinement suggestion"""
    original_query: str
    refined_query: str
    refinement_type: str  # expansion, narrowing, reformulation
    expected_improvement: float
    reasoning: str


class QueryAnalyzer:
    """Analyzes and improves search queries"""
    
    def __init__(self):
        self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                          'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are'}
        
        self.query_operators = {
            'AND': ' AND ',
            'OR': ' OR ',
            'NOT': ' NOT ',
            'NEAR': ' NEAR ',
            'quotes': '"{}"'
        }
    
    def analyze_query_quality(self, query: str) -> Dict:
        """Analyze query quality and suggest improvements"""
        analysis = {
            'length': len(query.split()),
            'has_operators': self._has_boolean_operators(query),
            'has_quotes': '"' in query,
            'specificity_score': self._calculate_specificity(query),
            'clarity_score': self._calculate_clarity(query),
            'suggestions': []
        }
        
        # Generate suggestions
        if analysis['length'] < 3:
            analysis['suggestions'].append({
                'type': 'expansion',
                'message': 'Query is too short. Add more specific terms.'
            })
        
        if analysis['length'] > 15:
            analysis['suggestions'].append({
                'type': 'narrowing',
                'message': 'Query is too long. Focus on key terms.'
            })
        
        if not analysis['has_operators'] and analysis['length'] > 5:
            analysis['suggestions'].append({
                'type': 'operators',
                'message': 'Consider using boolean operators (AND, OR, NOT).'
            })
        
        if analysis['specificity_score'] < 0.5:
            analysis['suggestions'].append({
                'type': 'specificity',
                'message': 'Add more specific terms to narrow results.'
            })
        
        return analysis
    
    def _has_boolean_operators(self, query: str) -> bool:
        """Check if query uses boolean operators"""
        return any(op in query.upper() for op in ['AND', 'OR', 'NOT'])
    
    def _calculate_specificity(self, query: str) -> float:
        """Calculate query specificity (0.0 to 1.0)"""
        words = query.lower().split()
        
        # Remove stop words
        meaningful_words = [w for w in words if w not in self.stop_words]
        
        if not words:
            return 0.0
        
        # Specificity based on ratio of meaningful words
        specificity = len(meaningful_words) / len(words)
        
        # Bonus for longer meaningful words (more specific)
        avg_word_length = sum(len(w) for w in meaningful_words) / max(len(meaningful_words), 1)
        length_bonus = min(0.3, (avg_word_length - 4) * 0.1)
        
        return min(1.0, specificity + length_bonus)
    
    def _calculate_clarity(self, query: str) -> float:
        """Calculate query clarity (0.0 to 1.0)"""
        # Clarity based on structure and coherence
        score = 0.5  # Base score
        
        # Bonus for proper capitalization
        if query[0].isupper():
            score += 0.1
        
        # Bonus for using quotes (exact phrases)
        if '"' in query:
            score += 0.2
        
        # Penalty for excessive punctuation
        punct_count = sum(1 for c in query if c in '!?.,;:')
        if punct_count > len(query.split()) * 0.5:
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def refine_query(self, query: str, context: str, 
                    previous_results: Optional[SearchResult] = None) -> QueryRefinement:
        """Refine query based on context and previous results"""
        
        if previous_results:
            if previous_results.outcome == SearchOutcome.NO_RESULTS.value:
                # Expand query
                return self._expand_query(query, context)
            elif previous_results.outcome == SearchOutcome.TOO_MANY_RESULTS.value:
                # Narrow query
                return self._narrow_query(query, context)
            elif previous_results.quality_score < 0.5:
                # Reformulate query
                return self._reformulate_query(query, context)
        
        # Default: optimize query
        return self._optimize_query(query, context)
    
    def _expand_query(self, query: str, context: str) -> QueryRefinement:
        """Expand query to get more results"""
        words = query.split()
        
        # Add OR operators between terms
        refined = ' OR '.join(words)
        
        # Add context-related terms
        if context and context not in query.lower():
            refined = f"{query} OR {context}"
        
        return QueryRefinement(
            original_query=query,
            refined_query=refined,
            refinement_type="expansion",
            expected_improvement=0.6,
            reasoning="Expanded query with OR operators to increase result coverage"
        )
    
    def _narrow_query(self, query: str, context: str) -> QueryRefinement:
        """Narrow query to reduce results"""
        words = query.split()
        
        # Add AND operators between terms
        refined = ' AND '.join(words)
        
        # Add quotes for exact phrases
        if len(words) >= 2:
            refined = f'"{query}"'
        
        # Add context as filter
        if context and context not in query.lower():
            refined = f"{refined} AND {context}"
        
        return QueryRefinement(
            original_query=query,
            refined_query=refined,
            refinement_type="narrowing",
            expected_improvement=0.7,
            reasoning="Narrowed query with AND operators and exact phrases"
        )
    
    def _reformulate_query(self, query: str, context: str) -> QueryRefinement:
        """Reformulate query for better results"""
        # Remove stop words
        words = [w for w in query.lower().split() if w not in self.stop_words]
        
        # Reconstruct with key terms
        refined = ' '.join(words)
        
        # Add context
        if context and context not in refined:
            refined = f"{context} {refined}"
        
        return QueryRefinement(
            original_query=query,
            refined_query=refined,
            refinement_type="reformulation",
            expected_improvement=0.65,
            reasoning="Reformulated query by removing stop words and adding context"
        )
    
    def _optimize_query(self, query: str, context: str) -> QueryRefinement:
        """General query optimization"""
        # Remove extra spaces
        refined = ' '.join(query.split())
        
        # Capitalize first letter
        if refined:
            refined = refined[0].upper() + refined[1:]
        
        return QueryRefinement(
            original_query=query,
            refined_query=refined,
            refinement_type="optimization",
            expected_improvement=0.55,
            reasoning="Optimized query formatting"
        )


class SearchMethodologyManager:
    """Manages search methodologies and strategies"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.analyzer = QueryAnalyzer()
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search queries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_queries (
                query_id TEXT PRIMARY KEY,
                query_text TEXT,
                search_type TEXT,
                context TEXT,
                filters TEXT,
                timestamp TEXT,
                user_id TEXT
            )
        ''')
        
        # Search results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_results (
                result_id TEXT PRIMARY KEY,
                query_id TEXT,
                results_count INTEGER,
                relevant_count INTEGER,
                execution_time REAL,
                outcome TEXT,
                quality_score REAL,
                user_feedback TEXT,
                timestamp TEXT
            )
        ''')
        
        # Search strategies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_strategies (
                strategy_id TEXT PRIMARY KEY,
                name TEXT,
                search_type TEXT,
                query_template TEXT,
                filters_template TEXT,
                success_rate REAL,
                avg_quality_score REAL,
                usage_count INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Query refinements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_refinements (
                refinement_id TEXT PRIMARY KEY,
                original_query_id TEXT,
                refined_query_id TEXT,
                refinement_type TEXT,
                improvement_achieved REAL,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_search(self, query: SearchQuery, result: SearchResult):
        """Record search query and result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Record query
        cursor.execute('''
            INSERT INTO search_queries
            (query_id, query_text, search_type, context, filters, timestamp, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            query.query_id, query.query_text, query.search_type,
            query.context, json.dumps(query.filters), query.timestamp,
            query.user_id
        ))
        
        # Record result
        cursor.execute('''
            INSERT INTO search_results
            (result_id, query_id, results_count, relevant_count, execution_time,
             outcome, quality_score, user_feedback, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.result_id, result.query_id, result.results_count,
            result.relevant_count, result.execution_time, result.outcome,
            result.quality_score, result.user_feedback, result.timestamp
        ))
        
        conn.commit()
        conn.close()
    
    def get_best_strategy(self, search_type: str, context: str) -> Optional[SearchStrategy]:
        """Get best performing strategy for search type and context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM search_strategies
            WHERE search_type = ?
            ORDER BY success_rate DESC, avg_quality_score DESC
            LIMIT 1
        ''', (search_type,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return SearchStrategy(
                strategy_id=row[0], name=row[1], search_type=row[2],
                query_template=row[3], filters_template=json.loads(row[4]),
                success_rate=row[5], avg_quality_score=row[6],
                usage_count=row[7], created_at=row[8], updated_at=row[9]
            )
        return None
    
    def create_strategy(self, strategy: SearchStrategy) -> str:
        """Create new search strategy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_strategies
            (strategy_id, name, search_type, query_template, filters_template,
             success_rate, avg_quality_score, usage_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            strategy.strategy_id, strategy.name, strategy.search_type,
            strategy.query_template, json.dumps(strategy.filters_template),
            strategy.success_rate, strategy.avg_quality_score,
            strategy.usage_count, strategy.created_at, strategy.updated_at
        ))
        
        conn.commit()
        conn.close()
        
        return strategy.strategy_id
    
    def update_strategy_performance(self, strategy_id: str, 
                                   quality_score: float, success: bool):
        """Update strategy performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current stats
        cursor.execute('''
            SELECT success_rate, avg_quality_score, usage_count
            FROM search_strategies
            WHERE strategy_id = ?
        ''', (strategy_id,))
        
        result = cursor.fetchone()
        if result:
            current_success_rate, current_quality, usage_count = result
            
            # Calculate new metrics
            new_usage_count = usage_count + 1
            new_success_rate = (
                (current_success_rate * usage_count + (1.0 if success else 0.0)) /
                new_usage_count
            )
            new_quality = (
                (current_quality * usage_count + quality_score) /
                new_usage_count
            )
            
            # Update
            cursor.execute('''
                UPDATE search_strategies
                SET success_rate = ?, avg_quality_score = ?, 
                    usage_count = ?, updated_at = ?
                WHERE strategy_id = ?
            ''', (
                new_success_rate, new_quality, new_usage_count,
                datetime.now().isoformat(), strategy_id
            ))
        
        conn.commit()
        conn.close()
    
    def analyze_search_patterns(self, user_id: str, days: int = 30) -> Dict:
        """Analyze search patterns for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get search statistics
        cursor.execute('''
            SELECT 
                sq.search_type,
                COUNT(*) as total_searches,
                AVG(sr.quality_score) as avg_quality,
                AVG(sr.execution_time) as avg_time,
                SUM(CASE WHEN sr.outcome = 'success' THEN 1 ELSE 0 END) as successes
            FROM search_queries sq
            JOIN search_results sr ON sq.query_id = sr.query_id
            WHERE sq.user_id = ? AND sq.timestamp > ?
            GROUP BY sq.search_type
        ''', (user_id, cutoff))
        
        patterns = {}
        for row in cursor.fetchall():
            search_type, total, avg_quality, avg_time, successes = row
            patterns[search_type] = {
                'total_searches': total,
                'avg_quality_score': avg_quality or 0.0,
                'avg_execution_time': avg_time or 0.0,
                'success_rate': (successes / total) if total > 0 else 0.0
            }
        
        # Get most common contexts
        cursor.execute('''
            SELECT context, COUNT(*) as count
            FROM search_queries
            WHERE user_id = ? AND timestamp > ?
            GROUP BY context
            ORDER BY count DESC
            LIMIT 5
        ''', (user_id, cutoff))
        
        common_contexts = [{'context': row[0], 'count': row[1]} 
                          for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'patterns_by_type': patterns,
            'common_contexts': common_contexts,
            'period_days': days,
            'generated_at': datetime.now().isoformat()
        }


class SearchMethodologyRefiner:
    """Main class for refining search methodologies"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.manager = SearchMethodologyManager(db_path)
        self.analyzer = QueryAnalyzer()
    
    def optimize_search(self, query_text: str, search_type: str, 
                       context: str, user_id: str) -> Dict:
        """Optimize search query and strategy"""
        # Analyze query quality
        quality_analysis = self.analyzer.analyze_query_quality(query_text)
        
        # Get best strategy for this search type
        strategy = self.manager.get_best_strategy(search_type, context)
        
        # Refine query if needed
        refinement = None
        if quality_analysis['specificity_score'] < 0.6:
            refinement = self.analyzer.refine_query(query_text, context)
        
        return {
            'original_query': query_text,
            'refined_query': refinement.refined_query if refinement else query_text,
            'quality_analysis': quality_analysis,
            'recommended_strategy': asdict(strategy) if strategy else None,
            'refinement': asdict(refinement) if refinement else None
        }
    
    def learn_from_search(self, query: SearchQuery, result: SearchResult):
        """Learn from search execution"""
        # Record the search
        self.manager.record_search(query, result)
        
        # If search was successful, potentially create/update strategy
        if result.outcome == SearchOutcome.SUCCESS.value and result.quality_score >= 0.7:
            self._create_or_update_strategy(query, result)
    
    def _create_or_update_strategy(self, query: SearchQuery, result: SearchResult):
        """Create or update search strategy based on successful search"""
        # Check if similar strategy exists
        existing = self.manager.get_best_strategy(query.search_type, query.context)
        
        if existing:
            # Update existing strategy
            self.manager.update_strategy_performance(
                existing.strategy_id,
                result.quality_score,
                result.outcome == SearchOutcome.SUCCESS.value
            )
        else:
            # Create new strategy
            strategy = SearchStrategy(
                strategy_id=f"strat_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                name=f"{query.search_type}_{query.context}",
                search_type=query.search_type,
                query_template=query.query_text,
                filters_template=query.filters,
                success_rate=1.0,
                avg_quality_score=result.quality_score,
                usage_count=1,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            self.manager.create_strategy(strategy)
    
    def get_search_recommendations(self, user_id: str) -> Dict:
        """Get personalized search recommendations"""
        # Analyze user's search patterns
        patterns = self.manager.analyze_search_patterns(user_id)
        
        recommendations = {
            'improve_areas': [],
            'best_practices': [],
            'suggested_strategies': []
        }
        
        # Identify areas for improvement
        for search_type, stats in patterns['patterns_by_type'].items():
            if stats['success_rate'] < 0.6:
                recommendations['improve_areas'].append({
                    'search_type': search_type,
                    'current_success_rate': stats['success_rate'],
                    'suggestion': 'Consider refining queries or using advanced operators'
                })
            
            if stats['avg_quality_score'] < 0.5:
                recommendations['improve_areas'].append({
                    'search_type': search_type,
                    'current_quality': stats['avg_quality_score'],
                    'suggestion': 'Try narrowing search scope or adding more specific terms'
                })
        
        # Add best practices
        recommendations['best_practices'] = [
            'Use boolean operators (AND, OR, NOT) for complex searches',
            'Put exact phrases in quotes',
            'Start with specific terms and broaden if needed',
            'Use filters to narrow results',
            'Review and refine based on initial results'
        ]
        
        return recommendations
    
    def get_methodology_report(self, user_id: str, days: int = 30) -> Dict:
        """Generate comprehensive methodology report"""
        patterns = self.manager.analyze_search_patterns(user_id, days)
        recommendations = self.get_search_recommendations(user_id)
        
        return {
            'user_id': user_id,
            'period_days': days,
            'search_patterns': patterns,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    # Initialize refiner
    refiner = SearchMethodologyRefiner("test_search.db")
    
    # Optimize a search
    optimization = refiner.optimize_search(
        query_text="python data analysis",
        search_type=SearchType.WEB_SEARCH.value,
        context="programming",
        user_id="user123"
    )
    
    print("Search Optimization:")
    print(f"Original: {optimization['original_query']}")
    print(f"Refined: {optimization['refined_query']}")
    print(f"Quality Analysis: {optimization['quality_analysis']}")
    
    # Simulate search execution
    query = SearchQuery(
        query_id="q001",
        query_text=optimization['refined_query'],
        search_type=SearchType.WEB_SEARCH.value,
        context="programming",
        filters={},
        timestamp=datetime.now().isoformat(),
        user_id="user123"
    )
    
    result = SearchResult(
        result_id="r001",
        query_id="q001",
        results_count=25,
        relevant_count=20,
        execution_time=0.5,
        outcome=SearchOutcome.SUCCESS.value,
        quality_score=0.8,
        user_feedback="Good results",
        timestamp=datetime.now().isoformat()
    )
    
    # Learn from search
    refiner.learn_from_search(query, result)
    
    # Get recommendations
    recommendations = refiner.get_search_recommendations("user123")
    print(f"\nRecommendations: {json.dumps(recommendations, indent=2)}")
