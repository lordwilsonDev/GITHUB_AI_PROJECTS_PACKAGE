#!/usr/bin/env python3
"""
Tool Discovery System
Discovers, evaluates, and tracks new tools, technologies, and integrations
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Tool:
    """Represents a discovered tool"""
    name: str
    category: str  # automation, productivity, development, ai, integration, etc.
    description: str
    discovered_date: str
    source: str  # web_search, user_mention, api_discovery, etc.
    evaluation_status: str  # discovered, evaluating, tested, approved, rejected
    capabilities: List[str]
    integration_potential: str  # high, medium, low
    learning_priority: int  # 1-10
    use_cases: List[str]
    documentation_url: Optional[str] = None
    api_available: bool = False
    cost: str = "unknown"  # free, paid, freemium, unknown
    notes: str = ""
    evaluation_results: Optional[Dict] = None
    
class ToolDiscoverySystem:
    """Manages tool discovery and evaluation"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data/tools")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.tools_file = self.base_dir / "discovered_tools.jsonl"
        self.evaluations_file = self.base_dir / "tool_evaluations.jsonl"
        self.integrations_file = self.base_dir / "integration_opportunities.jsonl"
        
        self.tools: Dict[str, Tool] = {}
        self.load_tools()
        
        self._initialized = True
    
    def load_tools(self):
        """Load discovered tools from storage"""
        if self.tools_file.exists():
            with open(self.tools_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        tool = Tool(**data)
                        self.tools[tool.name] = tool
    
    def discover_tool(self, name: str, category: str, description: str,
                     source: str, capabilities: List[str],
                     integration_potential: str = "medium",
                     learning_priority: int = 5,
                     use_cases: List[str] = None,
                     **kwargs) -> Tool:
        """Record a newly discovered tool"""
        
        if name in self.tools:
            # Update existing tool
            return self.update_tool(name, **kwargs)
        
        tool = Tool(
            name=name,
            category=category,
            description=description,
            discovered_date=datetime.now().isoformat(),
            source=source,
            evaluation_status="discovered",
            capabilities=capabilities,
            integration_potential=integration_potential,
            learning_priority=learning_priority,
            use_cases=use_cases or [],
            **kwargs
        )
        
        self.tools[name] = tool
        self._save_tool(tool)
        
        return tool
    
    def update_tool(self, name: str, **updates) -> Optional[Tool]:
        """Update tool information"""
        if name not in self.tools:
            return None
        
        tool = self.tools[name]
        for key, value in updates.items():
            if hasattr(tool, key) and value is not None:
                setattr(tool, key, value)
        
        self._save_tool(tool)
        return tool
    
    def evaluate_tool(self, name: str, evaluation_results: Dict,
                     new_status: str = "evaluated") -> bool:
        """Record tool evaluation results"""
        if name not in self.tools:
            return False
        
        tool = self.tools[name]
        tool.evaluation_results = evaluation_results
        tool.evaluation_status = new_status
        
        # Save evaluation
        evaluation_record = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": name,
            "results": evaluation_results,
            "status": new_status
        }
        
        with open(self.evaluations_file, 'a') as f:
            f.write(json.dumps(evaluation_record) + '\n')
        
        self._save_tool(tool)
        return True
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get all tools in a category"""
        return [t for t in self.tools.values() if t.category == category]
    
    def get_tools_by_status(self, status: str) -> List[Tool]:
        """Get all tools with a specific status"""
        return [t for t in self.tools.values() if t.evaluation_status == status]
    
    def get_high_priority_tools(self, min_priority: int = 7) -> List[Tool]:
        """Get tools with high learning priority"""
        return sorted(
            [t for t in self.tools.values() if t.learning_priority >= min_priority],
            key=lambda x: x.learning_priority,
            reverse=True
        )
    
    def get_integration_candidates(self) -> List[Tool]:
        """Get tools with high integration potential"""
        return [t for t in self.tools.values() 
                if t.integration_potential == "high" 
                and t.evaluation_status in ["tested", "approved"]]
    
    def record_integration_opportunity(self, tool_name: str, 
                                      opportunity_type: str,
                                      description: str,
                                      estimated_impact: str,
                                      implementation_complexity: str,
                                      use_cases: List[str]):
        """Record a potential integration opportunity"""
        opportunity = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "type": opportunity_type,
            "description": description,
            "estimated_impact": estimated_impact,
            "implementation_complexity": implementation_complexity,
            "use_cases": use_cases
        }
        
        with open(self.integrations_file, 'a') as f:
            f.write(json.dumps(opportunity) + '\n')
    
    def get_discovery_stats(self) -> Dict:
        """Get statistics about tool discovery"""
        total = len(self.tools)
        by_category = {}
        by_status = {}
        
        for tool in self.tools.values():
            by_category[tool.category] = by_category.get(tool.category, 0) + 1
            by_status[tool.evaluation_status] = by_status.get(tool.evaluation_status, 0) + 1
        
        return {
            "total_tools": total,
            "by_category": by_category,
            "by_status": by_status,
            "high_priority_count": len(self.get_high_priority_tools()),
            "integration_ready": len(self.get_integration_candidates())
        }
    
    def _save_tool(self, tool: Tool):
        """Save tool to storage"""
        with open(self.tools_file, 'a') as f:
            f.write(json.dumps(asdict(tool)) + '\n')
    
    def export_tool_catalog(self) -> Dict:
        """Export complete tool catalog"""
        return {
            "generated_at": datetime.now().isoformat(),
            "total_tools": len(self.tools),
            "tools": [asdict(t) for t in self.tools.values()],
            "stats": self.get_discovery_stats()
        }

def get_discovery_system() -> ToolDiscoverySystem:
    """Get singleton instance of tool discovery system"""
    return ToolDiscoverySystem()

if __name__ == "__main__":
    # Example usage
    system = get_discovery_system()
    
    # Discover a new tool
    tool = system.discover_tool(
        name="Zapier",
        category="automation",
        description="Automation platform connecting apps and services",
        source="web_search",
        capabilities=["workflow_automation", "api_integration", "triggers", "actions"],
        integration_potential="high",
        learning_priority=8,
        use_cases=["automate_repetitive_tasks", "connect_services", "data_sync"],
        api_available=True,
        cost="freemium",
        documentation_url="https://zapier.com/docs"
    )
    
    print(f"Discovered tool: {tool.name}")
    print(f"Stats: {system.get_discovery_stats()}")
