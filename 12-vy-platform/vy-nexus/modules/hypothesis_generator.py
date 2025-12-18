"""
Hypothesis Generation Engine Module

This module generates hypotheses for system improvements based on observed patterns,
performance data, and learning outcomes. It creates testable predictions about
what changes might improve system performance.

Features:
- Generate improvement hypotheses from data
- Prioritize hypotheses by potential impact
- Track hypothesis validation results
- Learn from hypothesis outcomes
- Generate null hypotheses for A/B testing
- Correlate patterns to generate insights

Author: Vy Self-Evolving AI Ecosystem
Phase: 6 - Self-Improvement Cycle
"""

import sqlite3
import json
import os
import hashlib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import statistics


class HypothesisType(Enum):
    """Types of hypotheses"""
    PERFORMANCE = "performance"
    LEARNING = "learning"
    OPTIMIZATION = "optimization"
    BEHAVIORAL = "behavioral"
    ARCHITECTURAL = "architectural"
    WORKFLOW = "workflow"


class HypothesisStatus(Enum):
    """Status of hypothesis"""
    PROPOSED = "proposed"
    TESTING = "testing"
    VALIDATED = "validated"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


class ConfidenceLevel(Enum):
    """Confidence levels"""
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


@dataclass
class Hypothesis:
    """Hypothesis definition"""
    hypothesis_id: str
    hypothesis_type: str
    statement: str
    rationale: str
    expected_impact: float  # 0-1 scale
    confidence: float  # 0-1 scale
    priority: int  # 1-10
    testable: bool
    test_criteria: Dict[str, Any]
    created_at: str
    status: str
    validation_results: Optional[Dict[str, Any]]


@dataclass
class Evidence:
    """Evidence supporting or refuting hypothesis"""
    evidence_id: str
    hypothesis_id: str
    evidence_type: str
    data: Dict[str, Any]
    supports_hypothesis: bool
    strength: float  # 0-1 scale
    collected_at: str


@dataclass
class HypothesisTest:
    """Test for validating hypothesis"""
    test_id: str
    hypothesis_id: str
    test_method: str
    started_at: str
    completed_at: Optional[str]
    result: Optional[str]
    metrics: Dict[str, float]
    conclusion: Optional[str]


class HypothesisGenerator:
    """
    Generates and manages improvement hypotheses
    """
    
    def __init__(self, db_path: str = "~/vy-nexus/data/hypotheses.db"):
        """
        Initialize hypothesis generator
        
        Args:
            db_path: Path to hypotheses database
        """
        self.db_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hypotheses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hypotheses (
                hypothesis_id TEXT PRIMARY KEY,
                hypothesis_type TEXT NOT NULL,
                statement TEXT NOT NULL,
                rationale TEXT,
                expected_impact REAL,
                confidence REAL,
                priority INTEGER,
                testable INTEGER,
                test_criteria TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL,
                validation_results TEXT
            )
        ''')
        
        # Evidence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id TEXT PRIMARY KEY,
                hypothesis_id TEXT NOT NULL,
                evidence_type TEXT NOT NULL,
                data TEXT,
                supports_hypothesis INTEGER,
                strength REAL,
                collected_at TEXT NOT NULL,
                FOREIGN KEY (hypothesis_id) REFERENCES hypotheses(hypothesis_id)
            )
        ''')
        
        # Hypothesis tests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hypothesis_tests (
                test_id TEXT PRIMARY KEY,
                hypothesis_id TEXT NOT NULL,
                test_method TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                result TEXT,
                metrics TEXT,
                conclusion TEXT,
                FOREIGN KEY (hypothesis_id) REFERENCES hypotheses(hypothesis_id)
            )
        ''')
        
        # Pattern observations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_observations (
                observation_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                frequency INTEGER,
                context TEXT,
                metrics TEXT
            )
        ''')
        
        # Correlations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS correlations (
                correlation_id TEXT PRIMARY KEY,
                variable_a TEXT NOT NULL,
                variable_b TEXT NOT NULL,
                correlation_coefficient REAL,
                sample_size INTEGER,
                p_value REAL,
                discovered_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_hypothesis(self, hypothesis_type: HypothesisType,
                           statement: str, rationale: str,
                           expected_impact: float = 0.5,
                           confidence: float = 0.6) -> Hypothesis:
        """
        Generate a new hypothesis
        
        Args:
            hypothesis_type: Type of hypothesis
            statement: Hypothesis statement
            rationale: Reasoning behind hypothesis
            expected_impact: Expected impact (0-1)
            confidence: Confidence level (0-1)
            
        Returns:
            Hypothesis object
        """
        hypothesis_id = hashlib.sha256(
            f"{statement}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Calculate priority based on impact and confidence
        priority = int((expected_impact * 0.6 + confidence * 0.4) * 10)
        
        # Determine if testable
        testable = self._is_testable(statement)
        
        # Generate test criteria
        test_criteria = self._generate_test_criteria(
            hypothesis_type, statement, expected_impact
        )
        
        hypothesis = Hypothesis(
            hypothesis_id=hypothesis_id,
            hypothesis_type=hypothesis_type.value,
            statement=statement,
            rationale=rationale,
            expected_impact=expected_impact,
            confidence=confidence,
            priority=priority,
            testable=testable,
            test_criteria=test_criteria,
            created_at=datetime.now().isoformat(),
            status=HypothesisStatus.PROPOSED.value,
            validation_results=None
        )
        
        self._save_hypothesis(hypothesis)
        
        return hypothesis
    
    def generate_from_patterns(self, patterns: List[Dict[str, Any]]) -> List[Hypothesis]:
        """
        Generate hypotheses from observed patterns
        
        Args:
            patterns: List of observed patterns
            
        Returns:
            List of generated hypotheses
        """
        hypotheses = []
        
        for pattern in patterns:
            # Analyze pattern for hypothesis generation
            if pattern.get('frequency', 0) >= 5:
                # High frequency pattern
                hypothesis = self.generate_hypothesis(
                    hypothesis_type=HypothesisType.OPTIMIZATION,
                    statement=f"Optimizing {pattern.get('pattern_type')} will improve performance by {pattern.get('potential_improvement', 10)}%",
                    rationale=f"Pattern observed {pattern.get('frequency')} times with consistent metrics",
                    expected_impact=min(pattern.get('potential_improvement', 10) / 100, 1.0),
                    confidence=min(pattern.get('frequency') / 20, 0.9)
                )
                hypotheses.append(hypothesis)
        
        return hypotheses
    
    def generate_from_correlations(self, variable_a: str, variable_b: str,
                                   correlation: float, sample_size: int) -> Optional[Hypothesis]:
        """
        Generate hypothesis from correlation
        
        Args:
            variable_a: First variable
            variable_b: Second variable
            correlation: Correlation coefficient
            sample_size: Sample size
            
        Returns:
            Hypothesis or None
        """
        # Only generate if correlation is significant
        if abs(correlation) < 0.5 or sample_size < 10:
            return None
        
        # Store correlation
        self._store_correlation(variable_a, variable_b, correlation, sample_size)
        
        # Generate hypothesis
        if correlation > 0:
            statement = f"Increasing {variable_a} will increase {variable_b}"
        else:
            statement = f"Increasing {variable_a} will decrease {variable_b}"
        
        hypothesis = self.generate_hypothesis(
            hypothesis_type=HypothesisType.PERFORMANCE,
            statement=statement,
            rationale=f"Strong correlation ({correlation:.2f}) observed over {sample_size} samples",
            expected_impact=abs(correlation) * 0.8,
            confidence=min(sample_size / 50, 0.9)
        )
        
        return hypothesis
    
    def add_evidence(self, hypothesis_id: str, evidence_type: str,
                    data: Dict[str, Any], supports: bool,
                    strength: float = 0.5) -> Evidence:
        """
        Add evidence for/against hypothesis
        
        Args:
            hypothesis_id: Hypothesis ID
            evidence_type: Type of evidence
            data: Evidence data
            supports: Whether evidence supports hypothesis
            strength: Strength of evidence (0-1)
            
        Returns:
            Evidence object
        """
        evidence_id = hashlib.sha256(
            f"{hypothesis_id}:{evidence_type}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        evidence = Evidence(
            evidence_id=evidence_id,
            hypothesis_id=hypothesis_id,
            evidence_type=evidence_type,
            data=data,
            supports_hypothesis=supports,
            strength=strength,
            collected_at=datetime.now().isoformat()
        )
        
        self._save_evidence(evidence)
        
        # Update hypothesis confidence based on evidence
        self._update_hypothesis_confidence(hypothesis_id)
        
        return evidence
    
    def validate_hypothesis(self, hypothesis_id: str,
                           test_results: Dict[str, Any]) -> bool:
        """
        Validate hypothesis with test results
        
        Args:
            hypothesis_id: Hypothesis to validate
            test_results: Test results
            
        Returns:
            True if validated
        """
        hypothesis = self._get_hypothesis(hypothesis_id)
        if not hypothesis:
            return False
        
        # Analyze test results
        validated = self._analyze_test_results(hypothesis, test_results)
        
        # Update hypothesis status
        if validated:
            hypothesis.status = HypothesisStatus.VALIDATED.value
            hypothesis.validation_results = test_results
        else:
            hypothesis.status = HypothesisStatus.REJECTED.value
            hypothesis.validation_results = test_results
        
        self._save_hypothesis(hypothesis)
        
        return validated
    
    def get_top_hypotheses(self, limit: int = 10,
                          hypothesis_type: Optional[HypothesisType] = None) -> List[Hypothesis]:
        """
        Get top priority hypotheses
        
        Args:
            limit: Maximum number to return
            hypothesis_type: Filter by type
            
        Returns:
            List of hypotheses
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM hypotheses WHERE status = ?"
        params = [HypothesisStatus.PROPOSED.value]
        
        if hypothesis_type:
            query += " AND hypothesis_type = ?"
            params.append(hypothesis_type.value)
        
        query += " ORDER BY priority DESC, expected_impact DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        hypotheses = []
        for row in rows:
            hypotheses.append(self._row_to_hypothesis(row))
        
        return hypotheses
    
    def get_validated_hypotheses(self) -> List[Hypothesis]:
        """
        Get all validated hypotheses
        
        Returns:
            List of validated hypotheses
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM hypotheses
            WHERE status = ?
            ORDER BY expected_impact DESC
        ''', (HypothesisStatus.VALIDATED.value,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_hypothesis(row) for row in rows]
    
    def get_hypothesis_evidence(self, hypothesis_id: str) -> List[Evidence]:
        """
        Get all evidence for hypothesis
        
        Args:
            hypothesis_id: Hypothesis ID
            
        Returns:
            List of evidence
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM evidence WHERE hypothesis_id = ?
        ''', (hypothesis_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        evidence_list = []
        for row in rows:
            evidence_list.append(Evidence(
                evidence_id=row[0],
                hypothesis_id=row[1],
                evidence_type=row[2],
                data=json.loads(row[3]) if row[3] else {},
                supports_hypothesis=bool(row[4]),
                strength=row[5],
                collected_at=row[6]
            ))
        
        return evidence_list
    
    def _is_testable(self, statement: str) -> bool:
        """Determine if hypothesis is testable"""
        # Simple heuristic: contains measurable terms
        measurable_terms = ['increase', 'decrease', 'improve', 'reduce', 
                           'faster', 'slower', 'more', 'less', 'better']
        return any(term in statement.lower() for term in measurable_terms)
    
    def _generate_test_criteria(self, hypothesis_type: HypothesisType,
                               statement: str, expected_impact: float) -> Dict[str, Any]:
        """Generate test criteria for hypothesis"""
        criteria = {
            'min_sample_size': 30,
            'confidence_level': 0.95,
            'expected_improvement': expected_impact,
            'test_duration_days': 7
        }
        
        if hypothesis_type == HypothesisType.PERFORMANCE:
            criteria['metrics'] = ['execution_time', 'success_rate', 'error_rate']
        elif hypothesis_type == HypothesisType.LEARNING:
            criteria['metrics'] = ['learning_rate', 'retention', 'accuracy']
        elif hypothesis_type == HypothesisType.OPTIMIZATION:
            criteria['metrics'] = ['efficiency', 'resource_usage', 'throughput']
        
        return criteria
    
    def _analyze_test_results(self, hypothesis: Hypothesis,
                             test_results: Dict[str, Any]) -> bool:
        """Analyze test results to validate hypothesis"""
        # Simple validation: check if improvement meets expected impact
        actual_improvement = test_results.get('improvement', 0)
        expected_improvement = hypothesis.expected_impact
        
        # Validated if actual improvement is at least 70% of expected
        return actual_improvement >= (expected_improvement * 0.7)
    
    def _update_hypothesis_confidence(self, hypothesis_id: str):
        """Update hypothesis confidence based on evidence"""
        evidence_list = self.get_hypothesis_evidence(hypothesis_id)
        
        if not evidence_list:
            return
        
        # Calculate weighted confidence from evidence
        supporting = [e for e in evidence_list if e.supports_hypothesis]
        refuting = [e for e in evidence_list if not e.supports_hypothesis]
        
        support_strength = sum(e.strength for e in supporting)
        refute_strength = sum(e.strength for e in refuting)
        
        total_strength = support_strength + refute_strength
        if total_strength > 0:
            new_confidence = support_strength / total_strength
            
            # Update hypothesis
            hypothesis = self._get_hypothesis(hypothesis_id)
            if hypothesis:
                hypothesis.confidence = new_confidence
                self._save_hypothesis(hypothesis)
    
    def _store_correlation(self, variable_a: str, variable_b: str,
                          correlation: float, sample_size: int):
        """Store discovered correlation"""
        correlation_id = hashlib.sha256(
            f"{variable_a}:{variable_b}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple p-value estimation (not statistically rigorous)
        p_value = max(0.001, 1.0 - abs(correlation))
        
        cursor.execute('''
            INSERT INTO correlations
            (correlation_id, variable_a, variable_b, correlation_coefficient,
             sample_size, p_value, discovered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            correlation_id,
            variable_a,
            variable_b,
            correlation,
            sample_size,
            p_value,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_hypothesis(self, hypothesis: Hypothesis):
        """Save hypothesis to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO hypotheses
            (hypothesis_id, hypothesis_type, statement, rationale, expected_impact,
             confidence, priority, testable, test_criteria, created_at, status,
             validation_results)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            hypothesis.hypothesis_id,
            hypothesis.hypothesis_type,
            hypothesis.statement,
            hypothesis.rationale,
            hypothesis.expected_impact,
            hypothesis.confidence,
            hypothesis.priority,
            1 if hypothesis.testable else 0,
            json.dumps(hypothesis.test_criteria),
            hypothesis.created_at,
            hypothesis.status,
            json.dumps(hypothesis.validation_results) if hypothesis.validation_results else None
        ))
        
        conn.commit()
        conn.close()
    
    def _get_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        """Get hypothesis from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM hypotheses WHERE hypothesis_id = ?
        ''', (hypothesis_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_hypothesis(row)
        
        return None
    
    def _row_to_hypothesis(self, row) -> Hypothesis:
        """Convert database row to Hypothesis object"""
        return Hypothesis(
            hypothesis_id=row[0],
            hypothesis_type=row[1],
            statement=row[2],
            rationale=row[3],
            expected_impact=row[4],
            confidence=row[5],
            priority=row[6],
            testable=bool(row[7]),
            test_criteria=json.loads(row[8]) if row[8] else {},
            created_at=row[9],
            status=row[10],
            validation_results=json.loads(row[11]) if row[11] else None
        )
    
    def _save_evidence(self, evidence: Evidence):
        """Save evidence to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO evidence
            (evidence_id, hypothesis_id, evidence_type, data, supports_hypothesis,
             strength, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            evidence.evidence_id,
            evidence.hypothesis_id,
            evidence.evidence_type,
            json.dumps(evidence.data),
            1 if evidence.supports_hypothesis else 0,
            evidence.strength,
            evidence.collected_at
        ))
        
        conn.commit()
        conn.close()


if __name__ == "__main__":
    # Example usage
    generator = HypothesisGenerator()
    
    # Generate a hypothesis
    hypothesis = generator.generate_hypothesis(
        hypothesis_type=HypothesisType.PERFORMANCE,
        statement="Caching frequently accessed data will reduce response time by 40%",
        rationale="Analysis shows 60% of requests access same 10% of data",
        expected_impact=0.4,
        confidence=0.75
    )
    
    print(f"Generated hypothesis: {hypothesis.hypothesis_id}")
    print(f"Statement: {hypothesis.statement}")
    print(f"Priority: {hypothesis.priority}")
    
    # Add supporting evidence
    evidence = generator.add_evidence(
        hypothesis_id=hypothesis.hypothesis_id,
        evidence_type="performance_test",
        data={"cache_hit_rate": 0.85, "response_time_reduction": 0.38},
        supports=True,
        strength=0.8
    )
    
    print(f"Added evidence: {evidence.evidence_id}")
