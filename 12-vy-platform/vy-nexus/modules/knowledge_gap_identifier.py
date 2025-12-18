"""
Knowledge Gap Identifier Module

This module identifies gaps in the system's knowledge base by analyzing:
- Missing information in knowledge domains
- Unanswered questions and failed queries
- Low-confidence predictions and decisions
- Areas with insufficient training data
- Topics requiring deeper understanding
- Skills and capabilities that need development

Author: VY Self-Evolving AI System
Created: December 15, 2025
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class KnowledgeGap:
    """Represents an identified knowledge gap"""
    gap_id: str
    domain: str
    category: str
    description: str
    severity: str  # critical, high, medium, low
    confidence: float
    evidence: List[Dict[str, Any]]
    impact_score: float
    priority: int
    suggested_actions: List[str]
    related_gaps: List[str]
    identified_at: str
    status: str  # new, acknowledged, in_progress, resolved


@dataclass
class GapAnalysis:
    """Results of gap analysis"""
    analysis_id: str
    total_gaps: int
    critical_gaps: int
    high_priority_gaps: int
    domains_affected: List[str]
    top_gaps: List[KnowledgeGap]
    recommendations: List[str]
    analyzed_at: str


class KnowledgeGapIdentifier:
    """Identifies and tracks knowledge gaps in the system"""
    
    def __init__(self, db_path: str = "data/knowledge_gaps.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Knowledge domains to monitor
        self.domains = [
            "technical_skills",
            "domain_expertise",
            "user_preferences",
            "task_execution",
            "problem_solving",
            "communication",
            "automation",
            "optimization",
            "learning_methods",
            "tools_and_platforms"
        ]
        
        # Gap categories
        self.categories = [
            "missing_information",
            "insufficient_data",
            "low_confidence",
            "failed_attempts",
            "unanswered_questions",
            "skill_deficiency",
            "knowledge_obsolescence",
            "integration_gap"
        ]
    
    def _init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Knowledge gaps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_gaps (
                gap_id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT NOT NULL,
                confidence REAL NOT NULL,
                evidence TEXT NOT NULL,
                impact_score REAL NOT NULL,
                priority INTEGER NOT NULL,
                suggested_actions TEXT NOT NULL,
                related_gaps TEXT NOT NULL,
                identified_at TEXT NOT NULL,
                status TEXT NOT NULL,
                resolved_at TEXT
            )
        ''')
        
        # Gap evidence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gap_evidence (
                evidence_id TEXT PRIMARY KEY,
                gap_id TEXT NOT NULL,
                evidence_type TEXT NOT NULL,
                source TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (gap_id) REFERENCES knowledge_gaps (gap_id)
            )
        ''')
        
        # Gap analysis history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gap_analyses (
                analysis_id TEXT PRIMARY KEY,
                total_gaps INTEGER NOT NULL,
                critical_gaps INTEGER NOT NULL,
                high_priority_gaps INTEGER NOT NULL,
                domains_affected TEXT NOT NULL,
                top_gaps TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                analyzed_at TEXT NOT NULL
            )
        ''')
        
        # Failed queries/tasks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failed_attempts (
                attempt_id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                query TEXT NOT NULL,
                failure_reason TEXT NOT NULL,
                context TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                analyzed BOOLEAN DEFAULT 0
            )
        ''')
        
        # Low confidence decisions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS low_confidence_decisions (
                decision_id TEXT PRIMARY KEY,
                decision_type TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                context TEXT NOT NULL,
                outcome TEXT,
                timestamp TEXT NOT NULL,
                analyzed BOOLEAN DEFAULT 0
            )
        ''')
        
        # Knowledge domain coverage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domain_coverage (
                domain TEXT PRIMARY KEY,
                coverage_score REAL NOT NULL,
                total_topics INTEGER NOT NULL,
                covered_topics INTEGER NOT NULL,
                missing_topics TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def identify_gaps(self, analysis_scope: str = "comprehensive") -> GapAnalysis:
        """
        Identify knowledge gaps across all domains
        
        Args:
            analysis_scope: 'comprehensive', 'quick', or 'targeted'
        """
        logger.info(f"Starting {analysis_scope} gap analysis...")
        
        gaps = []
        
        # Analyze different sources of gaps
        gaps.extend(self._analyze_failed_attempts())
        gaps.extend(self._analyze_low_confidence_decisions())
        gaps.extend(self._analyze_domain_coverage())
        gaps.extend(self._analyze_unanswered_questions())
        gaps.extend(self._analyze_skill_deficiencies())
        
        # Deduplicate and prioritize
        unique_gaps = self._deduplicate_gaps(gaps)
        prioritized_gaps = self._prioritize_gaps(unique_gaps)
        
        # Save gaps to database
        for gap in prioritized_gaps:
            self._save_gap(gap)
        
        # Create analysis report
        analysis = self._create_analysis_report(prioritized_gaps)
        self._save_analysis(analysis)
        
        logger.info(f"Gap analysis complete. Found {len(prioritized_gaps)} gaps.")
        return analysis
    
    def _analyze_failed_attempts(self) -> List[KnowledgeGap]:
        """Analyze failed attempts to identify knowledge gaps"""
        gaps = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent failed attempts
        cursor.execute('''
            SELECT attempt_id, task_type, query, failure_reason, context, timestamp
            FROM failed_attempts
            WHERE analyzed = 0
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        
        failed_attempts = cursor.fetchall()
        
        # Group by failure patterns
        failure_patterns = defaultdict(list)
        for attempt in failed_attempts:
            attempt_id, task_type, query, reason, context, timestamp = attempt
            pattern_key = f"{task_type}:{reason}"
            failure_patterns[pattern_key].append({
                'attempt_id': attempt_id,
                'query': query,
                'context': json.loads(context) if context else {},
                'timestamp': timestamp
            })
        
        # Create gaps from patterns
        for pattern, attempts in failure_patterns.items():
            if len(attempts) >= 3:  # Pattern threshold
                task_type, reason = pattern.split(':', 1)
                gap = KnowledgeGap(
                    gap_id=f"gap_failed_{hash(pattern)}_{datetime.now().timestamp()}",
                    domain=self._infer_domain(task_type),
                    category="failed_attempts",
                    description=f"Repeated failures in {task_type}: {reason}",
                    severity=self._calculate_severity(len(attempts)),
                    confidence=min(0.9, len(attempts) / 10),
                    evidence=[{'type': 'failed_attempt', 'data': a} for a in attempts[:5]],
                    impact_score=len(attempts) * 0.1,
                    priority=self._calculate_priority(len(attempts), task_type),
                    suggested_actions=[
                        f"Research best practices for {task_type}",
                        f"Analyze root cause of {reason}",
                        "Develop training data for this scenario",
                        "Create fallback strategies"
                    ],
                    related_gaps=[],
                    identified_at=datetime.now().isoformat(),
                    status="new"
                )
                gaps.append(gap)
        
        conn.close()
        return gaps
    
    def _analyze_low_confidence_decisions(self) -> List[KnowledgeGap]:
        """Analyze low confidence decisions to identify gaps"""
        gaps = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent low confidence decisions
        cursor.execute('''
            SELECT decision_id, decision_type, confidence_score, context, outcome, timestamp
            FROM low_confidence_decisions
            WHERE analyzed = 0 AND confidence_score < 0.6
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        
        decisions = cursor.fetchall()
        
        # Group by decision type
        decision_patterns = defaultdict(list)
        for decision in decisions:
            dec_id, dec_type, conf, context, outcome, timestamp = decision
            decision_patterns[dec_type].append({
                'decision_id': dec_id,
                'confidence': conf,
                'context': json.loads(context) if context else {},
                'outcome': outcome,
                'timestamp': timestamp
            })
        
        # Create gaps from patterns
        for dec_type, decisions_list in decision_patterns.items():
            if len(decisions_list) >= 3:
                avg_confidence = sum(d['confidence'] for d in decisions_list) / len(decisions_list)
                gap = KnowledgeGap(
                    gap_id=f"gap_lowconf_{hash(dec_type)}_{datetime.now().timestamp()}",
                    domain=self._infer_domain(dec_type),
                    category="low_confidence",
                    description=f"Low confidence in {dec_type} decisions (avg: {avg_confidence:.2f})",
                    severity="high" if avg_confidence < 0.4 else "medium",
                    confidence=0.8,
                    evidence=[{'type': 'low_confidence_decision', 'data': d} for d in decisions_list[:5]],
                    impact_score=(1 - avg_confidence) * len(decisions_list) * 0.1,
                    priority=self._calculate_priority(len(decisions_list), dec_type),
                    suggested_actions=[
                        f"Gather more training data for {dec_type}",
                        "Improve decision-making algorithms",
                        "Seek expert guidance on this topic",
                        "Implement confidence boosting strategies"
                    ],
                    related_gaps=[],
                    identified_at=datetime.now().isoformat(),
                    status="new"
                )
                gaps.append(gap)
        
        conn.close()
        return gaps
    
    def _analyze_domain_coverage(self) -> List[KnowledgeGap]:
        """Analyze domain coverage to identify gaps"""
        gaps = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for domain in self.domains:
            cursor.execute('''
                SELECT coverage_score, total_topics, covered_topics, missing_topics
                FROM domain_coverage
                WHERE domain = ?
            ''', (domain,))
            
            result = cursor.fetchone()
            if result:
                coverage, total, covered, missing = result
                missing_list = json.loads(missing) if missing else []
                
                if coverage < 0.7 and missing_list:  # Coverage threshold
                    gap = KnowledgeGap(
                        gap_id=f"gap_coverage_{domain}_{datetime.now().timestamp()}",
                        domain=domain,
                        category="insufficient_data",
                        description=f"Low coverage in {domain}: {coverage:.1%} ({covered}/{total} topics)",
                        severity="high" if coverage < 0.5 else "medium",
                        confidence=0.9,
                        evidence=[{
                            'type': 'coverage_analysis',
                            'data': {
                                'coverage': coverage,
                                'missing_topics': missing_list[:10]
                            }
                        }],
                        impact_score=(1 - coverage) * 10,
                        priority=1 if coverage < 0.5 else 2,
                        suggested_actions=[
                            f"Study missing topics in {domain}",
                            "Gather resources and documentation",
                            "Practice with real-world examples",
                            "Build knowledge base entries"
                        ],
                        related_gaps=[],
                        identified_at=datetime.now().isoformat(),
                        status="new"
                    )
                    gaps.append(gap)
        
        conn.close()
        return gaps
    
    def _analyze_unanswered_questions(self) -> List[KnowledgeGap]:
        """Analyze unanswered questions to identify gaps"""
        gaps = []
        # This would integrate with a question tracking system
        # Placeholder for now
        return gaps
    
    def _analyze_skill_deficiencies(self) -> List[KnowledgeGap]:
        """Analyze skill deficiencies to identify gaps"""
        gaps = []
        # This would integrate with a skill assessment system
        # Placeholder for now
        return gaps
    
    def _infer_domain(self, task_type: str) -> str:
        """Infer knowledge domain from task type"""
        task_lower = task_type.lower()
        
        if any(word in task_lower for word in ['code', 'program', 'script', 'debug']):
            return "technical_skills"
        elif any(word in task_lower for word in ['automate', 'workflow', 'process']):
            return "automation"
        elif any(word in task_lower for word in ['optimize', 'improve', 'enhance']):
            return "optimization"
        elif any(word in task_lower for word in ['communicate', 'explain', 'describe']):
            return "communication"
        elif any(word in task_lower for word in ['learn', 'study', 'research']):
            return "learning_methods"
        else:
            return "task_execution"
    
    def _calculate_severity(self, occurrence_count: int) -> str:
        """Calculate severity based on occurrence count"""
        if occurrence_count >= 10:
            return "critical"
        elif occurrence_count >= 5:
            return "high"
        elif occurrence_count >= 3:
            return "medium"
        else:
            return "low"
    
    def _calculate_priority(self, count: int, task_type: str) -> int:
        """Calculate priority (1=highest, 5=lowest)"""
        base_priority = 3
        
        # Adjust based on count
        if count >= 10:
            base_priority -= 2
        elif count >= 5:
            base_priority -= 1
        
        # Adjust based on task importance
        critical_tasks = ['security', 'data', 'user', 'critical']
        if any(word in task_type.lower() for word in critical_tasks):
            base_priority -= 1
        
        return max(1, min(5, base_priority))
    
    def _deduplicate_gaps(self, gaps: List[KnowledgeGap]) -> List[KnowledgeGap]:
        """Remove duplicate gaps"""
        unique_gaps = {}
        
        for gap in gaps:
            # Create a signature for the gap
            signature = f"{gap.domain}:{gap.category}:{gap.description[:50]}"
            
            if signature not in unique_gaps:
                unique_gaps[signature] = gap
            else:
                # Merge evidence if duplicate found
                existing = unique_gaps[signature]
                existing.evidence.extend(gap.evidence)
                existing.confidence = max(existing.confidence, gap.confidence)
                existing.impact_score = max(existing.impact_score, gap.impact_score)
        
        return list(unique_gaps.values())
    
    def _prioritize_gaps(self, gaps: List[KnowledgeGap]) -> List[KnowledgeGap]:
        """Prioritize gaps by severity and impact"""
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        
        return sorted(gaps, key=lambda g: (
            severity_order.get(g.severity, 4),
            g.priority,
            -g.impact_score,
            -g.confidence
        ))
    
    def _create_analysis_report(self, gaps: List[KnowledgeGap]) -> GapAnalysis:
        """Create comprehensive gap analysis report"""
        critical_gaps = [g for g in gaps if g.severity == 'critical']
        high_priority = [g for g in gaps if g.priority <= 2]
        domains = list(set(g.domain for g in gaps))
        
        # Generate recommendations
        recommendations = []
        if critical_gaps:
            recommendations.append(f"Address {len(critical_gaps)} critical gaps immediately")
        if high_priority:
            recommendations.append(f"Prioritize {len(high_priority)} high-priority gaps")
        
        # Domain-specific recommendations
        domain_gaps = defaultdict(int)
        for gap in gaps:
            domain_gaps[gap.domain] += 1
        
        for domain, count in sorted(domain_gaps.items(), key=lambda x: -x[1])[:3]:
            recommendations.append(f"Focus on {domain} domain ({count} gaps identified)")
        
        return GapAnalysis(
            analysis_id=f"analysis_{datetime.now().timestamp()}",
            total_gaps=len(gaps),
            critical_gaps=len(critical_gaps),
            high_priority_gaps=len(high_priority),
            domains_affected=domains,
            top_gaps=gaps[:10],
            recommendations=recommendations,
            analyzed_at=datetime.now().isoformat()
        )
    
    def _save_gap(self, gap: KnowledgeGap):
        """Save knowledge gap to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO knowledge_gaps
                (gap_id, domain, category, description, severity, confidence,
                 evidence, impact_score, priority, suggested_actions, related_gaps,
                 identified_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                gap.gap_id,
                gap.domain,
                gap.category,
                gap.description,
                gap.severity,
                gap.confidence,
                json.dumps(gap.evidence),
                gap.impact_score,
                gap.priority,
                json.dumps(gap.suggested_actions),
                json.dumps(gap.related_gaps),
                gap.identified_at,
                gap.status
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving gap: {e}")
        finally:
            conn.close()
    
    def _save_analysis(self, analysis: GapAnalysis):
        """Save gap analysis to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO gap_analyses
                (analysis_id, total_gaps, critical_gaps, high_priority_gaps,
                 domains_affected, top_gaps, recommendations, analyzed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis.analysis_id,
                analysis.total_gaps,
                analysis.critical_gaps,
                analysis.high_priority_gaps,
                json.dumps(analysis.domains_affected),
                json.dumps([asdict(g) for g in analysis.top_gaps]),
                json.dumps(analysis.recommendations),
                analysis.analyzed_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
        finally:
            conn.close()
    
    def record_failed_attempt(self, task_type: str, query: str, 
                            failure_reason: str, context: Dict[str, Any]):
        """Record a failed attempt for gap analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        attempt_id = f"attempt_{datetime.now().timestamp()}"
        cursor.execute('''
            INSERT INTO failed_attempts
            (attempt_id, task_type, query, failure_reason, context, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            attempt_id,
            task_type,
            query,
            failure_reason,
            json.dumps(context),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def record_low_confidence_decision(self, decision_type: str, 
                                      confidence_score: float,
                                      context: Dict[str, Any],
                                      outcome: Optional[str] = None):
        """Record a low confidence decision for gap analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        decision_id = f"decision_{datetime.now().timestamp()}"
        cursor.execute('''
            INSERT INTO low_confidence_decisions
            (decision_id, decision_type, confidence_score, context, outcome, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            decision_id,
            decision_type,
            confidence_score,
            json.dumps(context),
            outcome,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def update_domain_coverage(self, domain: str, coverage_score: float,
                              total_topics: int, covered_topics: int,
                              missing_topics: List[str]):
        """Update domain coverage information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO domain_coverage
            (domain, coverage_score, total_topics, covered_topics, missing_topics, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            domain,
            coverage_score,
            total_topics,
            covered_topics,
            json.dumps(missing_topics),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_gaps_by_domain(self, domain: str) -> List[KnowledgeGap]:
        """Get all gaps for a specific domain"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gap_id, domain, category, description, severity, confidence,
                   evidence, impact_score, priority, suggested_actions, related_gaps,
                   identified_at, status
            FROM knowledge_gaps
            WHERE domain = ? AND status != 'resolved'
            ORDER BY priority, impact_score DESC
        ''', (domain,))
        
        gaps = []
        for row in cursor.fetchall():
            gap = KnowledgeGap(
                gap_id=row[0],
                domain=row[1],
                category=row[2],
                description=row[3],
                severity=row[4],
                confidence=row[5],
                evidence=json.loads(row[6]),
                impact_score=row[7],
                priority=row[8],
                suggested_actions=json.loads(row[9]),
                related_gaps=json.loads(row[10]),
                identified_at=row[11],
                status=row[12]
            )
            gaps.append(gap)
        
        conn.close()
        return gaps
    
    def get_critical_gaps(self) -> List[KnowledgeGap]:
        """Get all critical gaps"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gap_id, domain, category, description, severity, confidence,
                   evidence, impact_score, priority, suggested_actions, related_gaps,
                   identified_at, status
            FROM knowledge_gaps
            WHERE severity = 'critical' AND status != 'resolved'
            ORDER BY priority, impact_score DESC
        ''', ())
        
        gaps = []
        for row in cursor.fetchall():
            gap = KnowledgeGap(
                gap_id=row[0],
                domain=row[1],
                category=row[2],
                description=row[3],
                severity=row[4],
                confidence=row[5],
                evidence=json.loads(row[6]),
                impact_score=row[7],
                priority=row[8],
                suggested_actions=json.loads(row[9]),
                related_gaps=json.loads(row[10]),
                identified_at=row[11],
                status=row[12]
            )
            gaps.append(gap)
        
        conn.close()
        return gaps
    
    def resolve_gap(self, gap_id: str, resolution_notes: str):
        """Mark a gap as resolved"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE knowledge_gaps
            SET status = 'resolved', resolved_at = ?
            WHERE gap_id = ?
        ''', (datetime.now().isoformat(), gap_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Gap {gap_id} marked as resolved: {resolution_notes}")
    
    def generate_learning_plan(self, max_gaps: int = 10) -> Dict[str, Any]:
        """Generate a learning plan to address knowledge gaps"""
        gaps = self.get_critical_gaps()
        
        if not gaps:
            # Get high priority gaps if no critical ones
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT gap_id, domain, category, description, severity, confidence,
                       evidence, impact_score, priority, suggested_actions, related_gaps,
                       identified_at, status
                FROM knowledge_gaps
                WHERE priority <= 2 AND status != 'resolved'
                ORDER BY priority, impact_score DESC
                LIMIT ?
            ''', (max_gaps,))
            
            for row in cursor.fetchall():
                gap = KnowledgeGap(
                    gap_id=row[0],
                    domain=row[1],
                    category=row[2],
                    description=row[3],
                    severity=row[4],
                    confidence=row[5],
                    evidence=json.loads(row[6]),
                    impact_score=row[7],
                    priority=row[8],
                    suggested_actions=json.loads(row[9]),
                    related_gaps=json.loads(row[10]),
                    identified_at=row[11],
                    status=row[12]
                )
                gaps.append(gap)
            conn.close()
        
        # Group by domain
        domain_plans = defaultdict(list)
        for gap in gaps[:max_gaps]:
            domain_plans[gap.domain].append({
                'gap_id': gap.gap_id,
                'description': gap.description,
                'actions': gap.suggested_actions,
                'priority': gap.priority
            })
        
        return {
            'plan_id': f"plan_{datetime.now().timestamp()}",
            'created_at': datetime.now().isoformat(),
            'total_gaps_addressed': len(gaps[:max_gaps]),
            'domains': dict(domain_plans),
            'estimated_effort': len(gaps[:max_gaps]) * 2,  # hours
            'priority_order': [gap.gap_id for gap in gaps[:max_gaps]]
        }


if __name__ == "__main__":
    # Test the knowledge gap identifier
    identifier = KnowledgeGapIdentifier()
    
    # Record some test data
    identifier.record_failed_attempt(
        task_type="code_debugging",
        query="Fix Python syntax error",
        failure_reason="Unable to identify error location",
        context={"language": "python", "complexity": "medium"}
    )
    
    identifier.record_low_confidence_decision(
        decision_type="task_prioritization",
        confidence_score=0.45,
        context={"tasks": 5, "urgency": "high"},
        outcome="suboptimal"
    )
    
    identifier.update_domain_coverage(
        domain="technical_skills",
        coverage_score=0.65,
        total_topics=100,
        covered_topics=65,
        missing_topics=["advanced_algorithms", "system_design", "performance_optimization"]
    )
    
    # Run gap analysis
    analysis = identifier.identify_gaps()
    
    print(f"\n=== Knowledge Gap Analysis ===")
    print(f"Total Gaps: {analysis.total_gaps}")
    print(f"Critical Gaps: {analysis.critical_gaps}")
    print(f"High Priority Gaps: {analysis.high_priority_gaps}")
    print(f"Domains Affected: {', '.join(analysis.domains_affected)}")
    print(f"\nTop 5 Gaps:")
    for i, gap in enumerate(analysis.top_gaps[:5], 1):
        print(f"{i}. [{gap.severity.upper()}] {gap.description}")
        print(f"   Domain: {gap.domain} | Priority: {gap.priority} | Impact: {gap.impact_score:.2f}")
    
    print(f"\nRecommendations:")
    for rec in analysis.recommendations:
        print(f"- {rec}")
    
    # Generate learning plan
    plan = identifier.generate_learning_plan(max_gaps=5)
    print(f"\n=== Learning Plan ===")
    print(f"Gaps to Address: {plan['total_gaps_addressed']}")
    print(f"Estimated Effort: {plan['estimated_effort']} hours")
    print(f"\nBy Domain:")
    for domain, gaps in plan['domains'].items():
        print(f"\n{domain.upper()}:")
        for gap in gaps:
            print(f"  - {gap['description']}")
            print(f"    Actions: {', '.join(gap['actions'][:2])}")
