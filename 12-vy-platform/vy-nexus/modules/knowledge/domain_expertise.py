#!/usr/bin/env python3
"""
Domain Expertise Development System

This module manages domain-specific expertise development, including:
- Deep-diving into industry trends and developments
- Studying specific domains to provide better insights
- Learning about user's business and related strategies
- Researching competitive landscapes
- Developing expertise in user's specific use cases
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


class DomainExpertiseSystem:
    """Manages domain-specific expertise and knowledge development."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/knowledge"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.domains_file = self.data_dir / "domains.json"
        self.research_file = self.data_dir / "domain_research.json"
        self.insights_file = self.data_dir / "domain_insights.json"
        self.trends_file = self.data_dir / "industry_trends.json"
        
        # Load data
        self.domains = self._load_json(self.domains_file, {})
        self.research = self._load_json(self.research_file, {})
        self.insights = self._load_json(self.insights_file, {})
        self.trends = self._load_json(self.trends_file, {})
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON data from file."""
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save JSON data to file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_domain(self, domain_id: str, name: str, category: str,
                   description: str, priority: str = 'medium') -> Dict:
        """Add a new domain to develop expertise in."""
        domain = {
            'domain_id': domain_id,
            'name': name,
            'category': category,  # technology, business, industry, user_specific
            'description': description,
            'priority': priority,  # low, medium, high, critical
            'expertise_level': 0,  # 0-100
            'status': 'active',  # active, paused, mastered
            'key_topics': [],
            'research_count': 0,
            'insight_count': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.domains[domain_id] = domain
        self._save_json(self.domains_file, self.domains)
        return domain
    
    def add_research(self, research_id: str, domain_id: str, topic: str,
                    findings: List[str], sources: List[str] = None) -> Dict:
        """Add research findings for a domain."""
        research = {
            'research_id': research_id,
            'domain_id': domain_id,
            'topic': topic,
            'findings': findings,
            'sources': sources or [],
            'confidence': 'medium',  # low, medium, high
            'relevance': 'high',  # low, medium, high
            'timestamp': datetime.now().isoformat()
        }
        
        self.research[research_id] = research
        
        # Update domain
        if domain_id in self.domains:
            self.domains[domain_id]['research_count'] += 1
            if topic not in self.domains[domain_id]['key_topics']:
                self.domains[domain_id]['key_topics'].append(topic)
            self.domains[domain_id]['updated_at'] = datetime.now().isoformat()
            self._save_json(self.domains_file, self.domains)
        
        self._save_json(self.research_file, self.research)
        return research
    
    def add_insight(self, insight_id: str, domain_id: str, title: str,
                   description: str, actionable: bool = True) -> Dict:
        """Add an insight derived from domain research."""
        insight = {
            'insight_id': insight_id,
            'domain_id': domain_id,
            'title': title,
            'description': description,
            'actionable': actionable,
            'applied': False,
            'impact': None,  # Will be set when applied
            'tags': [],
            'timestamp': datetime.now().isoformat()
        }
        
        self.insights[insight_id] = insight
        
        # Update domain
        if domain_id in self.domains:
            self.domains[domain_id]['insight_count'] += 1
            # Increase expertise level with each insight
            self.domains[domain_id]['expertise_level'] = min(
                100,
                self.domains[domain_id]['expertise_level'] + 5
            )
            self.domains[domain_id]['updated_at'] = datetime.now().isoformat()
            self._save_json(self.domains_file, self.domains)
        
        self._save_json(self.insights_file, self.insights)
        return insight
    
    def track_trend(self, trend_id: str, domain_id: str, trend_name: str,
                   description: str, impact: str = 'medium') -> Dict:
        """Track an industry trend."""
        trend = {
            'trend_id': trend_id,
            'domain_id': domain_id,
            'name': trend_name,
            'description': description,
            'impact': impact,  # low, medium, high, transformative
            'stage': 'emerging',  # emerging, growing, mainstream, declining
            'relevance_score': 0,
            'observations': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.trends[trend_id] = trend
        self._save_json(self.trends_file, self.trends)
        return trend
    
    def add_trend_observation(self, trend_id: str, observation: str,
                            evidence: List[str] = None) -> Dict:
        """Add an observation about a trend."""
        if trend_id not in self.trends:
            return None
        
        obs = {
            'observation': observation,
            'evidence': evidence or [],
            'timestamp': datetime.now().isoformat()
        }
        
        self.trends[trend_id]['observations'].append(obs)
        
        # Update relevance score based on observation count
        obs_count = len(self.trends[trend_id]['observations'])
        self.trends[trend_id]['relevance_score'] = min(100, obs_count * 10)
        
        # Update stage based on observations
        if obs_count >= 10:
            self.trends[trend_id]['stage'] = 'mainstream'
        elif obs_count >= 5:
            self.trends[trend_id]['stage'] = 'growing'
        
        self.trends[trend_id]['updated_at'] = datetime.now().isoformat()
        self._save_json(self.trends_file, self.trends)
        
        return self.trends[trend_id]
    
    def get_domain_summary(self, domain_id: str) -> Optional[Dict]:
        """Get a comprehensive summary of a domain."""
        if domain_id not in self.domains:
            return None
        
        domain = self.domains[domain_id].copy()
        
        # Add related research
        domain['research'] = [
            r for r_id, r in self.research.items()
            if r['domain_id'] == domain_id
        ]
        
        # Add related insights
        domain['insights'] = [
            i for i_id, i in self.insights.items()
            if i['domain_id'] == domain_id
        ]
        
        # Add related trends
        domain['trends'] = [
            t for t_id, t in self.trends.items()
            if t['domain_id'] == domain_id
        ]
        
        return domain
    
    def get_expertise_recommendations(self) -> List[Dict]:
        """Get recommendations for domains to focus on."""
        recommendations = []
        
        for domain_id, domain in self.domains.items():
            if domain['status'] == 'active':
                score = 0
                
                # Priority scoring
                priority_scores = {
                    'critical': 40,
                    'high': 30,
                    'medium': 20,
                    'low': 10
                }
                score += priority_scores.get(domain['priority'], 0)
                
                # Inverse expertise level (focus on less developed areas)
                score += (100 - domain['expertise_level']) * 0.3
                
                # Recent activity bonus
                updated = datetime.fromisoformat(domain['updated_at'])
                days_since_update = (datetime.now() - updated).days
                if days_since_update < 7:
                    score += 20
                elif days_since_update < 30:
                    score += 10
                
                recommendations.append({
                    'domain_id': domain_id,
                    'name': domain['name'],
                    'category': domain['category'],
                    'expertise_level': domain['expertise_level'],
                    'priority': domain['priority'],
                    'score': round(score, 2),
                    'reason': self._get_recommendation_reason(domain, days_since_update)
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5]  # Top 5
    
    def _get_recommendation_reason(self, domain: Dict, days_since_update: int) -> str:
        """Generate a reason for recommending a domain."""
        if domain['priority'] == 'critical':
            return f"Critical priority domain - requires immediate attention"
        elif domain['expertise_level'] < 30:
            return f"Low expertise level ({domain['expertise_level']}%) - needs development"
        elif days_since_update > 30:
            return f"No recent activity ({days_since_update} days) - needs refresh"
        else:
            return f"Active domain with {domain['priority']} priority"
    
    def get_trending_topics(self, min_relevance: int = 50) -> List[Dict]:
        """Get trending topics across all domains."""
        trending = []
        
        for trend_id, trend in self.trends.items():
            if trend['relevance_score'] >= min_relevance:
                trending.append({
                    'trend_id': trend_id,
                    'name': trend['name'],
                    'domain_id': trend['domain_id'],
                    'impact': trend['impact'],
                    'stage': trend['stage'],
                    'relevance_score': trend['relevance_score'],
                    'observation_count': len(trend['observations'])
                })
        
        # Sort by relevance score
        trending.sort(key=lambda x: x['relevance_score'], reverse=True)
        return trending
    
    def get_actionable_insights(self, domain_id: str = None) -> List[Dict]:
        """Get actionable insights that haven't been applied yet."""
        actionable = []
        
        for insight_id, insight in self.insights.items():
            if insight['actionable'] and not insight['applied']:
                if domain_id is None or insight['domain_id'] == domain_id:
                    actionable.append({
                        'insight_id': insight_id,
                        'title': insight['title'],
                        'description': insight['description'],
                        'domain_id': insight['domain_id']
                    })
        
        return actionable
    
    def get_statistics(self) -> Dict:
        """Get overall domain expertise statistics."""
        total_domains = len(self.domains)
        active_domains = sum(1 for d in self.domains.values() if d['status'] == 'active')
        mastered_domains = sum(1 for d in self.domains.values() if d['status'] == 'mastered')
        
        avg_expertise = sum(d['expertise_level'] for d in self.domains.values()) / max(total_domains, 1)
        
        total_research = len(self.research)
        total_insights = len(self.insights)
        total_trends = len(self.trends)
        
        actionable_insights = len(self.get_actionable_insights())
        
        return {
            'total_domains': total_domains,
            'active_domains': active_domains,
            'mastered_domains': mastered_domains,
            'average_expertise': round(avg_expertise, 2),
            'total_research': total_research,
            'total_insights': total_insights,
            'total_trends': total_trends,
            'actionable_insights': actionable_insights
        }


def main():
    """Test the domain expertise system."""
    print("Testing Domain Expertise Development System...")
    print("=" * 50)
    
    system = DomainExpertiseSystem()
    
    # Test 1: Add domains
    print("\n1. Adding domains...")
    domain1 = system.add_domain(
        'ai_automation',
        'AI & Automation',
        'technology',
        'Artificial intelligence and automation technologies',
        'critical'
    )
    print(f"   Added domain: {domain1['name']} (Priority: {domain1['priority']})")
    
    domain2 = system.add_domain(
        'productivity',
        'Productivity Systems',
        'business',
        'Productivity methodologies and systems',
        'high'
    )
    print(f"   Added domain: {domain2['name']} (Priority: {domain2['priority']})")
    
    # Test 2: Add research
    print("\n2. Adding research findings...")
    research = system.add_research(
        'res_001',
        'ai_automation',
        'Agentic AI Systems',
        [
            'Agentic AI can autonomously complete complex tasks',
            'Multi-agent systems show promise for collaborative work',
            'Tool use is critical for practical AI agents'
        ],
        ['Research paper: Agentic AI 2024', 'Industry report']
    )
    print(f"   Added research: {research['topic']}")
    print(f"   Findings: {len(research['findings'])} key findings")
    
    # Test 3: Add insights
    print("\n3. Adding insights...")
    insight = system.add_insight(
        'ins_001',
        'ai_automation',
        'Implement Multi-Agent Collaboration',
        'Multiple AI agents working together can solve complex problems more effectively than single agents',
        actionable=True
    )
    print(f"   Added insight: {insight['title']}")
    print(f"   Domain expertise increased to: {system.domains['ai_automation']['expertise_level']}%")
    
    # Test 4: Track trends
    print("\n4. Tracking industry trends...")
    trend = system.track_trend(
        'trend_001',
        'ai_automation',
        'Agentic AI Adoption',
        'Rapid adoption of agentic AI systems across industries',
        'transformative'
    )
    print(f"   Tracking trend: {trend['name']}")
    print(f"   Impact: {trend['impact']}")
    
    # Test 5: Add trend observations
    print("\n5. Adding trend observations...")
    updated_trend = system.add_trend_observation(
        'trend_001',
        'Major tech companies announcing agentic AI products',
        ['Company A launches AI agent', 'Company B announces agent platform']
    )
    print(f"   Added observation to: {updated_trend['name']}")
    print(f"   Relevance score: {updated_trend['relevance_score']}")
    print(f"   Stage: {updated_trend['stage']}")
    
    # Test 6: Get recommendations
    print("\n6. Getting expertise recommendations...")
    recommendations = system.get_expertise_recommendations()
    print(f"   Top recommendations:")
    for rec in recommendations:
        print(f"   - {rec['name']} (score: {rec['score']})")
        print(f"     Expertise: {rec['expertise_level']}%, Priority: {rec['priority']}")
        print(f"     Reason: {rec['reason']}")
    
    # Test 7: Get actionable insights
    print("\n7. Getting actionable insights...")
    actionable = system.get_actionable_insights()
    print(f"   Actionable insights: {len(actionable)}")
    for ins in actionable:
        print(f"   - {ins['title']}")
    
    # Test 8: Get statistics
    print("\n8. Getting statistics...")
    stats = system.get_statistics()
    print(f"   Total domains: {stats['total_domains']}")
    print(f"   Active domains: {stats['active_domains']}")
    print(f"   Average expertise: {stats['average_expertise']}%")
    print(f"   Total research: {stats['total_research']}")
    print(f"   Total insights: {stats['total_insights']}")
    print(f"   Actionable insights: {stats['actionable_insights']}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
