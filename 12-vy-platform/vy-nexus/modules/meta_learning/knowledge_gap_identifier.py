#!/usr/bin/env python3
"""
Knowledge Gap Identifier

Identifies gaps in the system's knowledge base and prioritizes
areas for learning and improvement.

Features:
- Detect knowledge gaps from failed tasks
- Analyze query patterns for missing knowledge
- Prioritize learning opportunities
- Track knowledge coverage by domain
- Generate learning roadmaps
- Monitor gap closure progress
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from pathlib import Path
from collections import defaultdict, Counter


class KnowledgeGapIdentifier:
    """Identifies and prioritizes knowledge gaps for learning."""
    
    def __init__(self, base_dir: str = "~/vy-nexus/data/knowledge_gaps"):
        self.base_dir = Path(base_dir).expanduser()
        self.gaps_file = self.base_dir / "identified_gaps.json"
        self.domains_file = self.base_dir / "knowledge_domains.json"
        self.coverage_file = self.base_dir / "knowledge_coverage.json"
        self.roadmap_file = self.base_dir / "learning_roadmap.json"
        self.queries_file = self.base_dir / "query_analysis.json"
        
        # Create directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.gaps = self._load_gaps()
        self.domains = self._load_domains()
        self.coverage = self._load_coverage()
        self.roadmap = self._load_roadmap()
        self.query_history = self._load_queries()
    
    def _load_gaps(self) -> Dict:
        """Load identified knowledge gaps."""
        if self.gaps_file.exists():
            with open(self.gaps_file, 'r') as f:
                return json.load(f)
        return {
            "gaps": {},
            "last_updated": None
        }
    
    def _save_gaps(self):
        """Save identified knowledge gaps."""
        self.gaps["last_updated"] = datetime.now().isoformat()
        with open(self.gaps_file, 'w') as f:
            json.dump(self.gaps, f, indent=2)
    
    def _load_domains(self) -> Dict:
        """Load knowledge domain definitions."""
        if self.domains_file.exists():
            with open(self.domains_file, 'r') as f:
                return json.load(f)
        return {
            "domains": {
                "programming": {
                    "topics": ["python", "javascript", "apis", "databases"],
                    "priority": "high"
                },
                "ai_ml": {
                    "topics": ["machine_learning", "nlp", "computer_vision", "deep_learning"],
                    "priority": "high"
                },
                "productivity": {
                    "topics": ["automation", "workflows", "time_management", "tools"],
                    "priority": "medium"
                },
                "business": {
                    "topics": ["strategy", "operations", "marketing", "finance"],
                    "priority": "medium"
                },
                "general": {
                    "topics": ["communication", "problem_solving", "research"],
                    "priority": "low"
                }
            },
            "last_updated": None
        }
    
    def _save_domains(self):
        """Save knowledge domain definitions."""
        self.domains["last_updated"] = datetime.now().isoformat()
        with open(self.domains_file, 'w') as f:
            json.dump(self.domains, f, indent=2)
    
    def _load_coverage(self) -> Dict:
        """Load knowledge coverage data."""
        if self.coverage_file.exists():
            with open(self.coverage_file, 'r') as f:
                return json.load(f)
        return {
            "domain_coverage": {},
            "topic_coverage": {},
            "last_updated": None
        }
    
    def _save_coverage(self):
        """Save knowledge coverage data."""
        self.coverage["last_updated"] = datetime.now().isoformat()
        with open(self.coverage_file, 'w') as f:
            json.dump(self.coverage, f, indent=2)
    
    def _load_roadmap(self) -> Dict:
        """Load learning roadmap."""
        if self.roadmap_file.exists():
            with open(self.roadmap_file, 'r') as f:
                return json.load(f)
        return {
            "roadmap": [],
            "last_generated": None
        }
    
    def _save_roadmap(self):
        """Save learning roadmap."""
        self.roadmap["last_generated"] = datetime.now().isoformat()
        with open(self.roadmap_file, 'w') as f:
            json.dump(self.roadmap, f, indent=2)
    
    def _load_queries(self) -> List[Dict]:
        """Load query history."""
        if self.queries_file.exists():
            with open(self.queries_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_queries(self):
        """Save query history."""
        with open(self.queries_file, 'w') as f:
            json.dump(self.query_history, f, indent=2)
    
    def record_failed_task(self, task_description: str,
                          failure_reason: str,
                          domain: str = "general",
                          context: Dict = None) -> Dict:
        """Record a failed task to identify knowledge gaps."""
        gap_id = f"gap_{len(self.gaps['gaps']) + 1}"
        
        # Extract potential knowledge gaps from failure
        identified_gaps = self._extract_gaps_from_failure(
            task_description,
            failure_reason
        )
        
        gap_entry = {
            "gap_id": gap_id,
            "task_description": task_description,
            "failure_reason": failure_reason,
            "domain": domain,
            "identified_gaps": identified_gaps,
            "context": context or {},
            "identified_at": datetime.now().isoformat(),
            "status": "open",
            "priority": self._calculate_gap_priority(domain, identified_gaps),
            "learning_attempts": 0,
            "resolved": False
        }
        
        self.gaps["gaps"][gap_id] = gap_entry
        self._save_gaps()
        
        # Update coverage
        self._update_coverage(domain, identified_gaps, "gap_identified")
        
        return {
            "success": True,
            "gap_id": gap_id,
            "identified_gaps": identified_gaps
        }
    
    def _extract_gaps_from_failure(self, task: str, reason: str) -> List[str]:
        """Extract specific knowledge gaps from failure information."""
        gaps = []
        
        # Common patterns indicating knowledge gaps
        patterns = {
            r"don't know (how to|about) ([\w\s]+)": "knowledge_of_{}",
            r"unfamiliar with ([\w\s]+)": "understanding_{}",
            r"no experience (with|in) ([\w\s]+)": "experience_with_{}",
            r"unable to ([\w\s]+)": "ability_to_{}",
            r"missing ([\w\s]+) knowledge": "knowledge_of_{}",
            r"lack (of )?([\w\s]+) skills": "skills_in_{}",
        }
        
        combined_text = f"{task} {reason}".lower()
        
        for pattern, gap_template in patterns.items():
            matches = re.findall(pattern, combined_text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[-1]  # Get last group
                gap = gap_template.format(match.strip().replace(' ', '_'))
                gaps.append(gap)
        
        # If no specific gaps found, create general gap
        if not gaps:
            gaps.append(f"general_{task[:30].replace(' ', '_')}")
        
        return gaps
    
    def _calculate_gap_priority(self, domain: str, gaps: List[str]) -> str:
        """Calculate priority for addressing a knowledge gap."""
        # Base priority on domain
        domain_priority = self.domains["domains"].get(
            domain,
            {"priority": "low"}
        )["priority"]
        
        # Check if gap appears frequently
        gap_frequency = sum(
            1 for g in self.gaps["gaps"].values()
            if any(gap in g["identified_gaps"] for gap in gaps)
        )
        
        # Adjust priority based on frequency
        if gap_frequency > 5:
            return "critical"
        elif gap_frequency > 2 or domain_priority == "high":
            return "high"
        elif domain_priority == "medium":
            return "medium"
        else:
            return "low"
    
    def record_query(self, query: str,
                    answered: bool,
                    confidence: float = 0.0,
                    domain: str = "general") -> Dict:
        """Record a query to analyze knowledge patterns."""
        query_entry = {
            "query_id": f"query_{len(self.query_history) + 1}",
            "query": query,
            "answered": answered,
            "confidence": confidence,
            "domain": domain,
            "timestamp": datetime.now().isoformat()
        }
        
        self.query_history.append(query_entry)
        self._save_queries()
        
        # If query couldn't be answered well, identify gap
        if not answered or confidence < 0.5:
            self.record_failed_task(
                f"Answer query: {query}",
                "Insufficient knowledge or low confidence",
                domain
            )
        
        return {
            "success": True,
            "query_id": query_entry["query_id"]
        }
    
    def analyze_query_patterns(self, days: int = 30) -> Dict:
        """Analyze query patterns to identify knowledge gaps."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent queries
        recent_queries = [
            q for q in self.query_history
            if datetime.fromisoformat(q["timestamp"]) > cutoff_date
        ]
        
        if not recent_queries:
            return {
                "success": True,
                "message": "No recent queries found",
                "patterns": {}
            }
        
        # Analyze by domain
        domain_stats = defaultdict(lambda: {
            "total": 0,
            "answered": 0,
            "unanswered": 0,
            "avg_confidence": []
        })
        
        for query in recent_queries:
            domain = query["domain"]
            domain_stats[domain]["total"] += 1
            
            if query["answered"]:
                domain_stats[domain]["answered"] += 1
            else:
                domain_stats[domain]["unanswered"] += 1
            
            domain_stats[domain]["avg_confidence"].append(query["confidence"])
        
        # Calculate statistics
        patterns = {}
        for domain, stats in domain_stats.items():
            avg_conf = sum(stats["avg_confidence"]) / len(stats["avg_confidence"])
            answer_rate = (stats["answered"] / stats["total"]) * 100
            
            patterns[domain] = {
                "total_queries": stats["total"],
                "answer_rate": answer_rate,
                "avg_confidence": avg_conf,
                "needs_improvement": answer_rate < 80 or avg_conf < 0.7
            }
        
        # Identify weak domains
        weak_domains = [
            domain for domain, data in patterns.items()
            if data["needs_improvement"]
        ]
        
        return {
            "success": True,
            "period_days": days,
            "total_queries": len(recent_queries),
            "patterns": patterns,
            "weak_domains": weak_domains
        }
    
    def _update_coverage(self, domain: str, topics: List[str], event_type: str):
        """Update knowledge coverage tracking."""
        # Initialize domain coverage if needed
        if domain not in self.coverage["domain_coverage"]:
            self.coverage["domain_coverage"][domain] = {
                "gaps_identified": 0,
                "gaps_resolved": 0,
                "coverage_score": 100.0
            }
        
        # Update based on event type
        if event_type == "gap_identified":
            self.coverage["domain_coverage"][domain]["gaps_identified"] += 1
        elif event_type == "gap_resolved":
            self.coverage["domain_coverage"][domain]["gaps_resolved"] += 1
        
        # Recalculate coverage score
        domain_data = self.coverage["domain_coverage"][domain]
        total_gaps = domain_data["gaps_identified"]
        resolved_gaps = domain_data["gaps_resolved"]
        
        if total_gaps > 0:
            coverage = (resolved_gaps / total_gaps) * 100
            # Penalize for unresolved gaps
            penalty = min((total_gaps - resolved_gaps) * 2, 50)
            domain_data["coverage_score"] = max(coverage - penalty, 0)
        
        # Update topic coverage
        for topic in topics:
            if topic not in self.coverage["topic_coverage"]:
                self.coverage["topic_coverage"][topic] = {
                    "domain": domain,
                    "gaps_count": 0,
                    "last_encountered": None
                }
            
            self.coverage["topic_coverage"][topic]["gaps_count"] += 1
            self.coverage["topic_coverage"][topic]["last_encountered"] = datetime.now().isoformat()
        
        self._save_coverage()
    
    def mark_gap_resolved(self, gap_id: str, resolution_notes: str = "") -> Dict:
        """Mark a knowledge gap as resolved."""
        if gap_id not in self.gaps["gaps"]:
            return {"success": False, "error": "Gap not found"}
        
        gap = self.gaps["gaps"][gap_id]
        gap["status"] = "resolved"
        gap["resolved"] = True
        gap["resolved_at"] = datetime.now().isoformat()
        gap["resolution_notes"] = resolution_notes
        
        self._save_gaps()
        
        # Update coverage
        self._update_coverage(
            gap["domain"],
            gap["identified_gaps"],
            "gap_resolved"
        )
        
        return {
            "success": True,
            "gap_id": gap_id
        }
    
    def generate_learning_roadmap(self, max_items: int = 20) -> Dict:
        """Generate a prioritized learning roadmap."""
        # Get all open gaps
        open_gaps = [
            (gap_id, gap) for gap_id, gap in self.gaps["gaps"].items()
            if not gap["resolved"]
        ]
        
        # Priority order
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        
        # Sort by priority and frequency
        sorted_gaps = sorted(
            open_gaps,
            key=lambda x: (priority_order.get(x[1]["priority"], 4), x[1]["identified_at"])
        )
        
        # Group by domain
        roadmap_by_domain = defaultdict(list)
        
        for gap_id, gap in sorted_gaps[:max_items]:
            roadmap_by_domain[gap["domain"]].append({
                "gap_id": gap_id,
                "description": gap["task_description"],
                "priority": gap["priority"],
                "identified_gaps": gap["identified_gaps"],
                "identified_at": gap["identified_at"]
            })
        
        # Create structured roadmap
        roadmap = []
        for domain, gaps in roadmap_by_domain.items():
            roadmap.append({
                "domain": domain,
                "priority": self.domains["domains"].get(domain, {}).get("priority", "low"),
                "gaps_count": len(gaps),
                "learning_items": gaps
            })
        
        # Sort domains by priority
        domain_priority_order = {"high": 0, "medium": 1, "low": 2}
        roadmap.sort(key=lambda x: domain_priority_order.get(x["priority"], 3))
        
        self.roadmap["roadmap"] = roadmap
        self._save_roadmap()
        
        return {
            "success": True,
            "roadmap": roadmap,
            "total_items": sum(len(d["learning_items"]) for d in roadmap)
        }
    
    def get_coverage_report(self) -> Dict:
        """Get knowledge coverage report."""
        # Calculate overall coverage
        domain_scores = [
            data["coverage_score"]
            for data in self.coverage["domain_coverage"].values()
        ]
        
        overall_coverage = sum(domain_scores) / len(domain_scores) if domain_scores else 100.0
        
        # Identify weakest domains
        weakest_domains = sorted(
            self.coverage["domain_coverage"].items(),
            key=lambda x: x[1]["coverage_score"]
        )[:5]
        
        # Identify most problematic topics
        problematic_topics = sorted(
            self.coverage["topic_coverage"].items(),
            key=lambda x: x[1]["gaps_count"],
            reverse=True
        )[:10]
        
        return {
            "success": True,
            "overall_coverage": overall_coverage,
            "domain_coverage": self.coverage["domain_coverage"],
            "weakest_domains": [
                {"domain": d[0], "score": d[1]["coverage_score"]}
                for d in weakest_domains
            ],
            "problematic_topics": [
                {"topic": t[0], "gaps_count": t[1]["gaps_count"], "domain": t[1]["domain"]}
                for t in problematic_topics
            ]
        }
    
    def get_gap_statistics(self) -> Dict:
        """Get statistics about knowledge gaps."""
        total_gaps = len(self.gaps["gaps"])
        resolved_gaps = sum(1 for g in self.gaps["gaps"].values() if g["resolved"])
        open_gaps = total_gaps - resolved_gaps
        
        # Count by priority
        by_priority = Counter(
            g["priority"] for g in self.gaps["gaps"].values()
            if not g["resolved"]
        )
        
        # Count by domain
        by_domain = Counter(
            g["domain"] for g in self.gaps["gaps"].values()
            if not g["resolved"]
        )
        
        return {
            "success": True,
            "total_gaps": total_gaps,
            "resolved_gaps": resolved_gaps,
            "open_gaps": open_gaps,
            "resolution_rate": (resolved_gaps / total_gaps * 100) if total_gaps > 0 else 0,
            "by_priority": dict(by_priority),
            "by_domain": dict(by_domain)
        }
    
    def list_gaps(self, domain: str = None,
                 priority: str = None,
                 resolved: bool = None) -> List[Dict]:
        """List knowledge gaps with optional filtering."""
        gaps = []
        
        for gap_id, gap in self.gaps["gaps"].items():
            # Apply filters
            if domain and gap["domain"] != domain:
                continue
            if priority and gap["priority"] != priority:
                continue
            if resolved is not None and gap["resolved"] != resolved:
                continue
            
            gaps.append({
                "gap_id": gap_id,
                "task_description": gap["task_description"],
                "domain": gap["domain"],
                "priority": gap["priority"],
                "identified_gaps": gap["identified_gaps"],
                "resolved": gap["resolved"],
                "identified_at": gap["identified_at"]
            })
        
        # Sort by priority and date
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        gaps.sort(key=lambda x: (priority_order.get(x["priority"], 4), x["identified_at"]))
        
        return gaps


def test_knowledge_gap_identifier():
    """Test the knowledge gap identifier."""
    identifier = KnowledgeGapIdentifier()
    
    # Record failed tasks
    print("Recording failed tasks...")
    identifier.record_failed_task(
        "Implement neural network from scratch",
        "Don't know how to implement backpropagation algorithm",
        "ai_ml"
    )
    identifier.record_failed_task(
        "Optimize database queries",
        "Unfamiliar with query optimization techniques",
        "programming"
    )
    identifier.record_failed_task(
        "Create marketing strategy",
        "No experience with digital marketing",
        "business"
    )
    
    # Record queries
    print("\nRecording queries...")
    identifier.record_query("How does gradient descent work?", True, 0.8, "ai_ml")
    identifier.record_query("What is database indexing?", False, 0.3, "programming")
    identifier.record_query("Explain SEO best practices", False, 0.4, "business")
    
    # Analyze query patterns
    print("\nAnalyzing query patterns...")
    patterns = identifier.analyze_query_patterns(days=30)
    print(f"Total queries: {patterns['total_queries']}")
    print(f"Weak domains: {patterns['weak_domains']}")
    
    # Generate learning roadmap
    print("\nGenerating learning roadmap...")
    roadmap = identifier.generate_learning_roadmap()
    print(f"Total learning items: {roadmap['total_items']}")
    for domain_plan in roadmap['roadmap']:
        print(f"  - {domain_plan['domain']}: {domain_plan['gaps_count']} items (priority: {domain_plan['priority']})")
    
    # Get coverage report
    print("\nCoverage report:")
    coverage = identifier.get_coverage_report()
    print(f"Overall coverage: {coverage['overall_coverage']:.1f}%")
    print(f"Weakest domains:")
    for domain in coverage['weakest_domains'][:3]:
        print(f"  - {domain['domain']}: {domain['score']:.1f}%")
    
    # Get gap statistics
    print("\nGap statistics:")
    stats = identifier.get_gap_statistics()
    print(f"Total gaps: {stats['total_gaps']}")
    print(f"Open gaps: {stats['open_gaps']}")
    print(f"Resolution rate: {stats['resolution_rate']:.1f}%")
    print(f"By priority: {stats['by_priority']}")
    
    # List high priority gaps
    print("\nHigh priority gaps:")
    high_priority = identifier.list_gaps(priority="high", resolved=False)
    for gap in high_priority[:3]:
        print(f"  - {gap['task_description']} ({gap['domain']})")


if __name__ == "__main__":
    test_knowledge_gap_identifier()
