#!/usr/bin/env python3
"""
Platform Integration Explorer

Discovers, tracks, and manages platform integrations.
Provides recommendations for integration opportunities.

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from enum import Enum


class IntegrationType(Enum):
    """Types of integrations."""
    API = "api"
    WEBHOOK = "webhook"
    OAUTH = "oauth"
    DATABASE = "database"
    FILE_SYNC = "file_sync"
    MESSAGING = "messaging"
    AUTOMATION = "automation"
    PLUGIN = "plugin"


class IntegrationStatus(Enum):
    """Integration status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    DEPRECATED = "deprecated"
    PLANNED = "planned"


class PlatformIntegrationExplorer:
    """
    System for exploring and managing platform integrations.
    
    Features:
    - Integration discovery and cataloging
    - Capability tracking
    - Usage monitoring
    - Opportunity identification
    - Recommendation generation
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/technical_learning"):
        """
        Initialize the platform integration explorer.
        
        Args:
            data_dir: Directory to store integration data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.platforms_file = os.path.join(self.data_dir, "platforms.json")
        self.integrations_file = os.path.join(self.data_dir, "integrations.json")
        self.usage_file = os.path.join(self.data_dir, "integration_usage.json")
        self.opportunities_file = os.path.join(self.data_dir, "integration_opportunities.json")
        self.recommendations_file = os.path.join(self.data_dir, "integration_recommendations.json")
        
        self.platforms = self._load_platforms()
        self.integrations = self._load_integrations()
        self.usage_history = self._load_usage()
        self.opportunities = self._load_opportunities()
        self.recommendations = self._load_recommendations()
    
    def _load_platforms(self) -> Dict[str, Any]:
        """Load platforms catalog."""
        if os.path.exists(self.platforms_file):
            with open(self.platforms_file, 'r') as f:
                return json.load(f)
        
        return {
            "platforms": {},
            "metadata": {
                "total_platforms": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def _save_platforms(self):
        """Save platforms catalog."""
        self.platforms["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.platforms_file, 'w') as f:
            json.dump(self.platforms, f, indent=2)
    
    def _load_integrations(self) -> Dict[str, Any]:
        """Load integrations."""
        if os.path.exists(self.integrations_file):
            with open(self.integrations_file, 'r') as f:
                return json.load(f)
        return {"integrations": []}
    
    def _save_integrations(self):
        """Save integrations."""
        with open(self.integrations_file, 'w') as f:
            json.dump(self.integrations, f, indent=2)
    
    def _load_usage(self) -> Dict[str, Any]:
        """Load usage history."""
        if os.path.exists(self.usage_file):
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        return {"usage_events": []}
    
    def _save_usage(self):
        """Save usage history."""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage_history, f, indent=2)
    
    def _load_opportunities(self) -> Dict[str, Any]:
        """Load integration opportunities."""
        if os.path.exists(self.opportunities_file):
            with open(self.opportunities_file, 'r') as f:
                return json.load(f)
        return {"opportunities": []}
    
    def _save_opportunities(self):
        """Save opportunities."""
        with open(self.opportunities_file, 'w') as f:
            json.dump(self.opportunities, f, indent=2)
    
    def _load_recommendations(self) -> Dict[str, Any]:
        """Load recommendations."""
        if os.path.exists(self.recommendations_file):
            with open(self.recommendations_file, 'r') as f:
                return json.load(f)
        return {"recommendations": []}
    
    def _save_recommendations(self):
        """Save recommendations."""
        with open(self.recommendations_file, 'w') as f:
            json.dump(self.recommendations, f, indent=2)
    
    def register_platform(self,
                         platform_id: str,
                         name: str,
                         category: str,
                         capabilities: List[str],
                         api_available: bool = False,
                         webhook_support: bool = False,
                         oauth_support: bool = False,
                         documentation_url: str = "") -> Dict[str, Any]:
        """
        Register a new platform.
        
        Args:
            platform_id: Unique identifier
            name: Platform name
            category: Platform category
            capabilities: List of capabilities
            api_available: Whether API is available
            webhook_support: Whether webhooks are supported
            oauth_support: Whether OAuth is supported
            documentation_url: URL to documentation
        
        Returns:
            Platform record
        """
        platform = {
            "name": name,
            "category": category,
            "capabilities": capabilities,
            "api_available": api_available,
            "webhook_support": webhook_support,
            "oauth_support": oauth_support,
            "documentation_url": documentation_url,
            "integration_count": 0,
            "usage_count": 0,
            "registered_at": datetime.now().isoformat()
        }
        
        self.platforms["platforms"][platform_id] = platform
        self.platforms["metadata"]["total_platforms"] += 1
        self._save_platforms()
        
        return platform
    
    def create_integration(self,
                          platform_id: str,
                          integration_type: str,
                          purpose: str,
                          capabilities_used: List[str],
                          configuration: Dict[str, Any] = None,
                          status: str = "active") -> Dict[str, Any]:
        """
        Create a new integration.
        
        Args:
            platform_id: Platform to integrate with
            integration_type: Type of integration
            purpose: Purpose of integration
            capabilities_used: Capabilities being used
            configuration: Integration configuration
            status: Integration status
        
        Returns:
            Integration record
        """
        integration = {
            "integration_id": f"int_{len(self.integrations['integrations']) + 1:06d}",
            "platform_id": platform_id,
            "integration_type": integration_type,
            "purpose": purpose,
            "capabilities_used": capabilities_used,
            "configuration": configuration or {},
            "status": status,
            "usage_count": 0,
            "success_rate": 0.0,
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        
        self.integrations["integrations"].append(integration)
        self._save_integrations()
        
        # Update platform integration count
        if platform_id in self.platforms["platforms"]:
            self.platforms["platforms"][platform_id]["integration_count"] += 1
            self._save_platforms()
        
        return integration
    
    def record_usage(self,
                    integration_id: str,
                    operation: str,
                    success: bool,
                    duration_ms: float,
                    data_transferred: int = 0,
                    error_message: str = "") -> Dict[str, Any]:
        """
        Record integration usage.
        
        Args:
            integration_id: Integration used
            operation: Operation performed
            success: Whether operation succeeded
            duration_ms: Duration in milliseconds
            data_transferred: Amount of data transferred (bytes)
            error_message: Error message if failed
        
        Returns:
            Usage event record
        """
        event = {
            "event_id": f"usage_{len(self.usage_history['usage_events']) + 1:06d}",
            "integration_id": integration_id,
            "operation": operation,
            "success": success,
            "duration_ms": duration_ms,
            "data_transferred": data_transferred,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        self.usage_history["usage_events"].append(event)
        self._save_usage()
        
        # Update integration stats
        for integration in self.integrations["integrations"]:
            if integration["integration_id"] == integration_id:
                integration["usage_count"] += 1
                integration["last_used"] = datetime.now().isoformat()
                
                # Calculate success rate
                usage_events = [e for e in self.usage_history["usage_events"]
                              if e["integration_id"] == integration_id]
                success_count = sum(1 for e in usage_events if e["success"])
                integration["success_rate"] = (success_count / len(usage_events) * 100) if usage_events else 0.0
                
                self._save_integrations()
                break
        
        return event
    
    def identify_opportunity(self,
                           platform_id: str,
                           opportunity_type: str,
                           description: str,
                           potential_benefit: str,
                           effort_estimate: str = "medium",
                           priority: str = "medium") -> Dict[str, Any]:
        """
        Identify integration opportunity.
        
        Args:
            platform_id: Platform for opportunity
            opportunity_type: Type of opportunity
            description: Description
            potential_benefit: Expected benefit
            effort_estimate: Estimated effort
            priority: Priority level
        
        Returns:
            Opportunity record
        """
        opportunity = {
            "opportunity_id": f"opp_{len(self.opportunities['opportunities']) + 1:06d}",
            "platform_id": platform_id,
            "opportunity_type": opportunity_type,
            "description": description,
            "potential_benefit": potential_benefit,
            "effort_estimate": effort_estimate,
            "priority": priority,
            "status": "identified",
            "identified_at": datetime.now().isoformat()
        }
        
        self.opportunities["opportunities"].append(opportunity)
        self._save_opportunities()
        
        return opportunity
    
    def generate_recommendation(self,
                              use_case: str,
                              requirements: List[str],
                              constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate integration recommendation.
        
        Args:
            use_case: Use case description
            requirements: List of requirements
            constraints: Constraints (e.g., {"budget": "free", "complexity": "low"})
        
        Returns:
            Recommendation with suggested platforms/integrations
        """
        constraints = constraints or {}
        
        # Find matching platforms
        candidates = []
        for platform_id, platform in self.platforms["platforms"].items():
            match_score = 0.0
            
            # Check capability match
            for req in requirements:
                if req in platform["capabilities"]:
                    match_score += 2.0
            
            # Consider API availability
            if platform["api_available"]:
                match_score += 1.0
            
            # Consider existing integrations
            if platform["integration_count"] > 0:
                match_score += 0.5
            
            # Apply constraints
            if "api_required" in constraints and constraints["api_required"]:
                if not platform["api_available"]:
                    match_score *= 0.3
            
            if match_score > 0:
                candidates.append({
                    "platform_id": platform_id,
                    "name": platform["name"],
                    "match_score": match_score,
                    "capabilities": platform["capabilities"],
                    "api_available": platform["api_available"]
                })
        
        candidates.sort(key=lambda x: x["match_score"], reverse=True)
        
        recommendation = {
            "recommendation_id": f"rec_{len(self.recommendations['recommendations']) + 1:06d}",
            "use_case": use_case,
            "requirements": requirements,
            "constraints": constraints,
            "recommended_platforms": candidates[:5],
            "generated_at": datetime.now().isoformat()
        }
        
        self.recommendations["recommendations"].append(recommendation)
        self._save_recommendations()
        
        return recommendation
    
    def get_platform_info(self, platform_id: str) -> Dict[str, Any]:
        """Get detailed platform information."""
        if platform_id not in self.platforms["platforms"]:
            return {"error": "Platform not found"}
        
        platform = self.platforms["platforms"][platform_id].copy()
        
        # Add integration details
        platform_integrations = [i for i in self.integrations["integrations"]
                                if i["platform_id"] == platform_id]
        platform["integrations"] = platform_integrations
        
        return platform
    
    def get_integration_info(self, integration_id: str) -> Dict[str, Any]:
        """Get detailed integration information."""
        for integration in self.integrations["integrations"]:
            if integration["integration_id"] == integration_id:
                info = integration.copy()
                
                # Add usage statistics
                usage_events = [e for e in self.usage_history["usage_events"]
                              if e["integration_id"] == integration_id]
                
                info["total_usage_events"] = len(usage_events)
                
                if usage_events:
                    avg_duration = sum(e["duration_ms"] for e in usage_events) / len(usage_events)
                    info["average_duration_ms"] = avg_duration
                    
                    total_data = sum(e["data_transferred"] for e in usage_events)
                    info["total_data_transferred"] = total_data
                
                return info
        
        return {"error": "Integration not found"}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        total_platforms = self.platforms["metadata"]["total_platforms"]
        total_integrations = len(self.integrations["integrations"])
        total_usage = len(self.usage_history["usage_events"])
        total_opportunities = len(self.opportunities["opportunities"])
        
        # Calculate success rate
        if total_usage > 0:
            success_count = sum(1 for e in self.usage_history["usage_events"] if e["success"])
            overall_success_rate = (success_count / total_usage * 100)
        else:
            overall_success_rate = 0.0
        
        # Find most used integration
        usage_counts = defaultdict(int)
        for event in self.usage_history["usage_events"]:
            usage_counts[event["integration_id"]] += 1
        
        most_used = max(usage_counts.items(), key=lambda x: x[1]) if usage_counts else (None, 0)
        
        # Count active integrations
        active_integrations = sum(1 for i in self.integrations["integrations"]
                                 if i["status"] == "active")
        
        return {
            "total_platforms": total_platforms,
            "total_integrations": total_integrations,
            "active_integrations": active_integrations,
            "total_usage_events": total_usage,
            "overall_success_rate": overall_success_rate,
            "total_opportunities": total_opportunities,
            "most_used_integration": most_used[0],
            "most_used_count": most_used[1]
        }


def test_platform_integration_explorer():
    """Test the platform integration explorer."""
    print("=" * 60)
    print("Testing Platform Integration Explorer")
    print("=" * 60)
    
    explorer = PlatformIntegrationExplorer()
    
    # Test 1: Register platform
    print("\n1. Testing platform registration...")
    platform = explorer.register_platform(
        "github",
        name="GitHub",
        category="development",
        capabilities=["code_hosting", "version_control", "ci_cd", "issue_tracking"],
        api_available=True,
        webhook_support=True,
        oauth_support=True,
        documentation_url="https://docs.github.com/en/rest"
    )
    print(f"   Platform: {platform['name']}")
    print(f"   API available: {platform['api_available']}")
    print(f"   Capabilities: {len(platform['capabilities'])}")
    
    # Test 2: Create integration
    print("\n2. Testing integration creation...")
    integration = explorer.create_integration(
        "github",
        integration_type="api",
        purpose="Automated repository management",
        capabilities_used=["code_hosting", "version_control"],
        configuration={"auth_type": "oauth", "scope": "repo"},
        status="active"
    )
    print(f"   Integration ID: {integration['integration_id']}")
    print(f"   Type: {integration['integration_type']}")
    print(f"   Status: {integration['status']}")
    
    # Test 3: Record usage
    print("\n3. Testing usage recording...")
    event = explorer.record_usage(
        integration['integration_id'],
        operation="create_repository",
        success=True,
        duration_ms=250.5,
        data_transferred=1024
    )
    print(f"   Event ID: {event['event_id']}")
    print(f"   Operation: {event['operation']}")
    print(f"   Success: {event['success']}")
    print(f"   Duration: {event['duration_ms']}ms")
    
    # Test 4: Identify opportunity
    print("\n4. Testing opportunity identification...")
    opportunity = explorer.identify_opportunity(
        "github",
        opportunity_type="automation",
        description="Automate PR reviews using AI",
        potential_benefit="Faster code review process",
        effort_estimate="high",
        priority="medium"
    )
    print(f"   Opportunity ID: {opportunity['opportunity_id']}")
    print(f"   Description: {opportunity['description']}")
    print(f"   Priority: {opportunity['priority']}")
    
    # Test 5: Generate recommendation
    print("\n5. Testing recommendation generation...")
    recommendation = explorer.generate_recommendation(
        use_case="Project management automation",
        requirements=["issue_tracking", "ci_cd"],
        constraints={"api_required": True}
    )
    print(f"   Recommendation ID: {recommendation['recommendation_id']}")
    print(f"   Recommended platforms: {len(recommendation['recommended_platforms'])}")
    if recommendation["recommended_platforms"]:
        top = recommendation["recommended_platforms"][0]
        print(f"   Top recommendation: {top['name']} (Score: {top['match_score']})")
    
    # Test 6: Get platform info
    print("\n6. Testing platform info retrieval...")
    info = explorer.get_platform_info("github")
    print(f"   Platform: {info['name']}")
    print(f"   Category: {info['category']}")
    print(f"   Integration count: {info['integration_count']}")
    print(f"   Integrations: {len(info['integrations'])}")
    
    # Test 7: Get integration info
    print("\n7. Testing integration info retrieval...")
    int_info = explorer.get_integration_info(integration['integration_id'])
    print(f"   Integration: {int_info['integration_id']}")
    print(f"   Purpose: {int_info['purpose']}")
    print(f"   Usage count: {int_info['usage_count']}")
    print(f"   Success rate: {int_info['success_rate']:.1f}%")
    
    # Test 8: Get statistics
    print("\n8. Testing statistics...")
    stats = explorer.get_statistics()
    print(f"   Total platforms: {stats['total_platforms']}")
    print(f"   Total integrations: {stats['total_integrations']}")
    print(f"   Active integrations: {stats['active_integrations']}")
    print(f"   Overall success rate: {stats['overall_success_rate']:.1f}%")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_platform_integration_explorer()
