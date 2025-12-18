#!/usr/bin/env python3
"""
Improvement Documentation
Documents all improvements with before/after comparisons and impact analysis
Part of the Self-Evolving AI Ecosystem
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

class ImprovementDocumentation:
    """Documents system improvements"""
    
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
        self.docs_dir = self.base_dir / "documentation" / "improvements"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_dir = self.base_dir / "data" / "improvements"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Documentation file
        self.improvements_file = self.data_dir / "improvements.jsonl"
        
        # Improvement categories
        self.categories = [
            "performance",
            "usability",
            "reliability",
            "efficiency",
            "automation",
            "learning",
            "security",
            "scalability"
        ]
        
        self._initialized = True
    
    def document_improvement(
        self,
        improvement_id: str,
        title: str,
        category: str,
        description: str,
        before_state: Dict[str, Any],
        after_state: Dict[str, Any],
        implementation_details: str,
        impact_analysis: Dict[str, Any],
        rollback_procedure: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Document an improvement"""
        
        if category not in self.categories:
            category = "other"
        
        improvement = {
            "improvement_id": improvement_id,
            "title": title,
            "category": category,
            "description": description,
            "before_state": before_state,
            "after_state": after_state,
            "implementation_details": implementation_details,
            "impact_analysis": impact_analysis,
            "rollback_procedure": rollback_procedure,
            "documented_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Save improvement
        with open(self.improvements_file, 'a') as f:
            f.write(json.dumps(improvement) + '\n')
        
        # Generate detailed documentation
        doc_file = self.docs_dir / f"{improvement_id}.md"
        self._generate_markdown_doc(improvement, doc_file)
        
        return {
            "success": True,
            "improvement_id": improvement_id,
            "doc_file": str(doc_file)
        }
    
    def _generate_markdown_doc(
        self,
        improvement: Dict[str, Any],
        output_file: Path
    ) -> None:
        """Generate markdown documentation for an improvement"""
        
        lines = []
        lines.append(f"# {improvement['title']}")
        lines.append("")
        lines.append(f"**Improvement ID:** `{improvement['improvement_id']}`")
        lines.append(f"**Category:** {improvement['category']}")
        lines.append(f"**Documented:** {improvement['documented_at']}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Description
        lines.append("## Description")
        lines.append("")
        lines.append(improvement['description'])
        lines.append("")
        
        # Before State
        lines.append("## Before State")
        lines.append("")
        before = improvement['before_state']
        for key, value in before.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")
        
        # After State
        lines.append("## After State")
        lines.append("")
        after = improvement['after_state']
        for key, value in after.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")
        
        # Comparison
        lines.append("## Comparison")
        lines.append("")
        lines.append("| Metric | Before | After | Change |")
        lines.append("|--------|--------|-------|--------|")
        
        for key in before.keys():
            if key in after:
                before_val = before[key]
                after_val = after[key]
                
                # Try to calculate change
                try:
                    if isinstance(before_val, (int, float)) and isinstance(after_val, (int, float)):
                        if before_val != 0:
                            change_pct = ((after_val - before_val) / before_val) * 100
                            change_str = f"{change_pct:+.1f}%"
                        else:
                            change_str = "N/A"
                    else:
                        change_str = "N/A"
                except:
                    change_str = "N/A"
                
                lines.append(f"| {key} | {before_val} | {after_val} | {change_str} |")
        
        lines.append("")
        
        # Implementation Details
        lines.append("## Implementation Details")
        lines.append("")
        lines.append(improvement['implementation_details'])
        lines.append("")
        
        # Impact Analysis
        lines.append("## Impact Analysis")
        lines.append("")
        impact = improvement['impact_analysis']
        for key, value in impact.items():
            lines.append(f"### {key.replace('_', ' ').title()}")
            lines.append("")
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    lines.append(f"- **{sub_key}:** {sub_value}")
            else:
                lines.append(str(value))
            lines.append("")
        
        # Rollback Procedure
        if improvement.get('rollback_procedure'):
            lines.append("## Rollback Procedure")
            lines.append("")
            lines.append(improvement['rollback_procedure'])
            lines.append("")
        
        # Metadata
        if improvement.get('metadata'):
            lines.append("## Additional Information")
            lines.append("")
            for key, value in improvement['metadata'].items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write('\n'.join(lines))
    
    def get_improvement(
        self,
        improvement_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific improvement by ID"""
        
        if not self.improvements_file.exists():
            return None
        
        with open(self.improvements_file, 'r') as f:
            for line in f:
                improvement = json.loads(line.strip())
                if improvement.get('improvement_id') == improvement_id:
                    return improvement
        
        return None
    
    def list_improvements(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List improvements, optionally filtered by category"""
        
        improvements = []
        
        if not self.improvements_file.exists():
            return improvements
        
        with open(self.improvements_file, 'r') as f:
            for line in f:
                improvement = json.loads(line.strip())
                
                if category is None or improvement.get('category') == category:
                    improvements.append(improvement)
        
        # Sort by date (newest first)
        improvements.sort(
            key=lambda x: x.get('documented_at', ''),
            reverse=True
        )
        
        if limit:
            improvements = improvements[:limit]
        
        return improvements
    
    def generate_summary_report(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate summary report of improvements"""
        
        improvements = self.list_improvements(category=category)
        
        if not improvements:
            return {
                "success": True,
                "total": 0,
                "message": "No improvements found"
            }
        
        # Categorize improvements
        by_category = defaultdict(int)
        for imp in improvements:
            by_category[imp.get('category', 'other')] += 1
        
        # Calculate total impact
        total_impact = {
            "time_saved_hours": 0,
            "cost_saved": 0,
            "performance_improvement_percent": [],
            "user_satisfaction_improvement": []
        }
        
        for imp in improvements:
            impact = imp.get('impact_analysis', {})
            
            if 'time_saved_hours' in impact:
                total_impact['time_saved_hours'] += impact['time_saved_hours']
            
            if 'cost_saved' in impact:
                total_impact['cost_saved'] += impact['cost_saved']
            
            if 'performance_improvement_percent' in impact:
                total_impact['performance_improvement_percent'].append(
                    impact['performance_improvement_percent']
                )
            
            if 'user_satisfaction_improvement' in impact:
                total_impact['user_satisfaction_improvement'].append(
                    impact['user_satisfaction_improvement']
                )
        
        # Calculate averages
        if total_impact['performance_improvement_percent']:
            import statistics
            total_impact['avg_performance_improvement'] = statistics.mean(
                total_impact['performance_improvement_percent']
            )
            del total_impact['performance_improvement_percent']
        
        if total_impact['user_satisfaction_improvement']:
            import statistics
            total_impact['avg_satisfaction_improvement'] = statistics.mean(
                total_impact['user_satisfaction_improvement']
            )
            del total_impact['user_satisfaction_improvement']
        
        report = {
            "total_improvements": len(improvements),
            "by_category": dict(by_category),
            "total_impact": total_impact,
            "recent_improvements": [
                {
                    "id": imp['improvement_id'],
                    "title": imp['title'],
                    "category": imp['category'],
                    "date": imp['documented_at']
                }
                for imp in improvements[:10]
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "report": report
        }
    
    def export_improvements(
        self,
        output_file: Path,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export improvements to file"""
        
        improvements = self.list_improvements()
        
        if format == "json":
            with open(output_file, 'w') as f:
                json.dump(improvements, f, indent=2)
        elif format == "markdown":
            lines = []
            lines.append("# Improvements Documentation")
            lines.append("")
            lines.append(f"Total Improvements: {len(improvements)}")
            lines.append("")
            
            for imp in improvements:
                lines.append(f"## {imp['title']}")
                lines.append("")
                lines.append(f"- **ID:** {imp['improvement_id']}")
                lines.append(f"- **Category:** {imp['category']}")
                lines.append(f"- **Date:** {imp['documented_at']}")
                lines.append("")
                lines.append(imp['description'])
                lines.append("")
                lines.append("---")
                lines.append("")
            
            with open(output_file, 'w') as f:
                f.write('\n'.join(lines))
        
        return {
            "success": True,
            "exported_count": len(improvements),
            "output_file": str(output_file)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get improvement documentation statistics"""
        
        stats = {
            "total_improvements": 0,
            "by_category": {},
            "total_docs": 0
        }
        
        improvements = self.list_improvements()
        stats["total_improvements"] = len(improvements)
        
        # Count by category
        by_category = defaultdict(int)
        for imp in improvements:
            by_category[imp.get('category', 'other')] += 1
        stats["by_category"] = dict(by_category)
        
        # Count documentation files
        if self.docs_dir.exists():
            stats["total_docs"] = len(list(self.docs_dir.glob("*.md")))
        
        return stats

def get_documenter() -> ImprovementDocumentation:
    """Get the singleton ImprovementDocumentation instance"""
    return ImprovementDocumentation()

if __name__ == "__main__":
    # Example usage
    documenter = get_documenter()
    
    # Document a test improvement
    result = documenter.document_improvement(
        improvement_id="imp_001",
        title="Optimized Database Query Performance",
        category="performance",
        description="Improved database query performance by adding indexes and optimizing query structure.",
        before_state={
            "avg_query_time_ms": 250,
            "queries_per_second": 40,
            "cpu_usage_percent": 75
        },
        after_state={
            "avg_query_time_ms": 50,
            "queries_per_second": 200,
            "cpu_usage_percent": 30
        },
        implementation_details="Added composite indexes on frequently queried columns. Rewrote N+1 queries to use joins. Implemented query result caching.",
        impact_analysis={
            "performance_improvement_percent": 80,
            "time_saved_hours": 10,
            "user_satisfaction_improvement": 1.5
        },
        rollback_procedure="Drop the new indexes and revert to previous query structure. Clear cache."
    )
    
    print(f"Documentation result: {json.dumps(result, indent=2)}")
    print(f"\nStatistics: {json.dumps(documenter.get_statistics(), indent=2)}")
