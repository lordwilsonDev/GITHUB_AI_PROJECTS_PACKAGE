"""
System Capability Upgrader Module

This module manages the upgrade and enhancement of system capabilities over time.
It identifies capability gaps, plans upgrades, and safely implements new features
and improvements to the vy-nexus platform.

Features:
- Capability assessment and gap analysis
- Upgrade planning and scheduling
- Safe capability deployment with rollback
- Dependency management for new capabilities
- Performance impact analysis
- Capability versioning and compatibility

Author: Vy Self-Evolving AI Ecosystem
Phase: 5 - Process Implementation & Deployment
"""

import sqlite3
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import importlib
import sys


class CapabilityStatus(Enum):
    """Status of a capability"""
    AVAILABLE = "available"
    PLANNED = "planned"
    IN_DEVELOPMENT = "in_development"
    TESTING = "testing"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"


class UpgradeType(Enum):
    """Type of capability upgrade"""
    NEW_FEATURE = "new_feature"
    ENHANCEMENT = "enhancement"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"
    BUG_FIX = "bug_fix"


class UpgradePriority(Enum):
    """Priority level for upgrades"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


@dataclass
class Capability:
    """System capability definition"""
    capability_id: str
    name: str
    description: str
    category: str
    version: str
    status: str
    dependencies: List[str]
    requirements: Dict[str, Any]
    performance_metrics: Dict[str, float]
    created_at: str
    updated_at: str


@dataclass
class CapabilityUpgrade:
    """Capability upgrade plan"""
    upgrade_id: str
    capability_id: str
    upgrade_type: str
    priority: str
    from_version: str
    to_version: str
    changes: Dict[str, Any]
    impact_analysis: Dict[str, Any]
    scheduled_date: Optional[str]
    completed_date: Optional[str]
    status: str
    rollback_plan: Dict[str, Any]


@dataclass
class CapabilityGap:
    """Identified capability gap"""
    gap_id: str
    description: str
    severity: str
    affected_areas: List[str]
    proposed_solution: str
    estimated_effort: str
    identified_at: str


class SystemCapabilityUpgrader:
    """
    Manages system capability upgrades and enhancements
    """
    
    def __init__(self, db_path: str = "~/vy-nexus/data/capabilities.db"):
        """
        Initialize system capability upgrader
        
        Args:
            db_path: Path to capabilities database
        """
        self.db_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Capabilities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capabilities (
                capability_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                version TEXT NOT NULL,
                status TEXT NOT NULL,
                dependencies TEXT,
                requirements TEXT,
                performance_metrics TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Capability upgrades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capability_upgrades (
                upgrade_id TEXT PRIMARY KEY,
                capability_id TEXT NOT NULL,
                upgrade_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                from_version TEXT NOT NULL,
                to_version TEXT NOT NULL,
                changes TEXT NOT NULL,
                impact_analysis TEXT,
                scheduled_date TEXT,
                completed_date TEXT,
                status TEXT NOT NULL,
                rollback_plan TEXT,
                FOREIGN KEY (capability_id) REFERENCES capabilities(capability_id)
            )
        ''')
        
        # Capability gaps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capability_gaps (
                gap_id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                severity TEXT NOT NULL,
                affected_areas TEXT,
                proposed_solution TEXT,
                estimated_effort TEXT,
                identified_at TEXT NOT NULL
            )
        ''')
        
        # Capability dependencies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capability_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                capability_id TEXT NOT NULL,
                depends_on TEXT NOT NULL,
                dependency_type TEXT,
                required_version TEXT,
                FOREIGN KEY (capability_id) REFERENCES capabilities(capability_id)
            )
        ''')
        
        # Upgrade history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS upgrade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upgrade_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT,
                success INTEGER,
                FOREIGN KEY (upgrade_id) REFERENCES capability_upgrades(upgrade_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_capability(self, name: str, description: str, category: str,
                          version: str = "1.0.0",
                          dependencies: List[str] = None,
                          requirements: Dict[str, Any] = None) -> Capability:
        """
        Register a new system capability
        
        Args:
            name: Capability name
            description: Capability description
            category: Capability category
            version: Initial version
            dependencies: List of dependency capability IDs
            requirements: System requirements
            
        Returns:
            Capability object
        """
        capability_id = hashlib.sha256(
            f"{name}:{category}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        capability = Capability(
            capability_id=capability_id,
            name=name,
            description=description,
            category=category,
            version=version,
            status=CapabilityStatus.AVAILABLE.value,
            dependencies=dependencies or [],
            requirements=requirements or {},
            performance_metrics={},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self._save_capability(capability)
        
        # Register dependencies
        if dependencies:
            for dep in dependencies:
                self._add_dependency(capability_id, dep)
        
        return capability
    
    def assess_capabilities(self) -> Dict[str, Any]:
        """
        Assess current system capabilities
        
        Returns:
            Assessment report
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count capabilities by status
        cursor.execute('''
            SELECT status, COUNT(*) FROM capabilities GROUP BY status
        ''')
        status_counts = dict(cursor.fetchall())
        
        # Count capabilities by category
        cursor.execute('''
            SELECT category, COUNT(*) FROM capabilities GROUP BY category
        ''')
        category_counts = dict(cursor.fetchall())
        
        # Get recent upgrades
        cursor.execute('''
            SELECT COUNT(*) FROM capability_upgrades
            WHERE completed_date >= ?
        ''', ((datetime.now() - timedelta(days=30)).isoformat(),))
        recent_upgrades = cursor.fetchone()[0]
        
        # Get pending upgrades
        cursor.execute('''
            SELECT COUNT(*) FROM capability_upgrades
            WHERE status IN ('planned', 'in_development', 'testing')
        ''')
        pending_upgrades = cursor.fetchone()[0]
        
        # Get capability gaps
        cursor.execute('''
            SELECT COUNT(*) FROM capability_gaps
        ''')
        gap_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_capabilities': sum(status_counts.values()),
            'by_status': status_counts,
            'by_category': category_counts,
            'recent_upgrades_30d': recent_upgrades,
            'pending_upgrades': pending_upgrades,
            'identified_gaps': gap_count,
            'assessment_date': datetime.now().isoformat()
        }
    
    def identify_gaps(self, required_capabilities: List[str]) -> List[CapabilityGap]:
        """
        Identify capability gaps
        
        Args:
            required_capabilities: List of required capability names
            
        Returns:
            List of identified gaps
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        gaps = []
        
        for req_cap in required_capabilities:
            cursor.execute('''
                SELECT capability_id FROM capabilities WHERE name = ?
            ''', (req_cap,))
            
            if not cursor.fetchone():
                gap_id = hashlib.sha256(
                    f"gap:{req_cap}:{datetime.now().isoformat()}".encode()
                ).hexdigest()[:16]
                
                gap = CapabilityGap(
                    gap_id=gap_id,
                    description=f"Missing capability: {req_cap}",
                    severity="high",
                    affected_areas=["system_functionality"],
                    proposed_solution=f"Develop and deploy {req_cap} capability",
                    estimated_effort="medium",
                    identified_at=datetime.now().isoformat()
                )
                
                gaps.append(gap)
                self._save_gap(gap)
        
        conn.close()
        return gaps
    
    def plan_upgrade(self, capability_id: str, upgrade_type: UpgradeType,
                    priority: UpgradePriority, to_version: str,
                    changes: Dict[str, Any],
                    scheduled_date: Optional[str] = None) -> CapabilityUpgrade:
        """
        Plan a capability upgrade
        
        Args:
            capability_id: Capability to upgrade
            upgrade_type: Type of upgrade
            priority: Upgrade priority
            to_version: Target version
            changes: Planned changes
            scheduled_date: When to perform upgrade
            
        Returns:
            CapabilityUpgrade object
        """
        capability = self._get_capability(capability_id)
        if not capability:
            raise ValueError(f"Capability {capability_id} not found")
        
        # Analyze impact
        impact_analysis = self._analyze_upgrade_impact(capability_id, changes)
        
        # Create rollback plan
        rollback_plan = {
            'restore_version': capability.version,
            'backup_required': True,
            'rollback_steps': [
                'Stop affected services',
                'Restore previous version',
                'Verify functionality',
                'Restart services'
            ]
        }
        
        upgrade_id = hashlib.sha256(
            f"{capability_id}:{to_version}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        upgrade = CapabilityUpgrade(
            upgrade_id=upgrade_id,
            capability_id=capability_id,
            upgrade_type=upgrade_type.value,
            priority=priority.value,
            from_version=capability.version,
            to_version=to_version,
            changes=changes,
            impact_analysis=impact_analysis,
            scheduled_date=scheduled_date,
            completed_date=None,
            status="planned",
            rollback_plan=rollback_plan
        )
        
        self._save_upgrade(upgrade)
        self._log_upgrade_action(upgrade_id, "planned", "Upgrade planned")
        
        return upgrade
    
    def execute_upgrade(self, upgrade_id: str) -> bool:
        """
        Execute a planned upgrade
        
        Args:
            upgrade_id: Upgrade to execute
            
        Returns:
            True if successful
        """
        upgrade = self._get_upgrade(upgrade_id)
        if not upgrade or upgrade.status != "planned":
            return False
        
        capability = self._get_capability(upgrade.capability_id)
        if not capability:
            return False
        
        try:
            # Update status
            upgrade.status = "in_development"
            self._save_upgrade(upgrade)
            self._log_upgrade_action(upgrade_id, "started", "Upgrade execution started")
            
            # Check dependencies
            if not self._check_dependencies(capability.capability_id):
                raise Exception("Dependency check failed")
            
            # Apply changes
            self._apply_upgrade_changes(capability, upgrade.changes)
            
            # Update capability version
            capability.version = upgrade.to_version
            capability.updated_at = datetime.now().isoformat()
            self._save_capability(capability)
            
            # Mark upgrade complete
            upgrade.status = "deployed"
            upgrade.completed_date = datetime.now().isoformat()
            self._save_upgrade(upgrade)
            self._log_upgrade_action(upgrade_id, "completed", "Upgrade completed successfully", success=True)
            
            return True
            
        except Exception as e:
            upgrade.status = "failed"
            self._save_upgrade(upgrade)
            self._log_upgrade_action(upgrade_id, "failed", str(e), success=False)
            return False
    
    def rollback_upgrade(self, upgrade_id: str) -> bool:
        """
        Rollback a capability upgrade
        
        Args:
            upgrade_id: Upgrade to rollback
            
        Returns:
            True if successful
        """
        upgrade = self._get_upgrade(upgrade_id)
        if not upgrade:
            return False
        
        capability = self._get_capability(upgrade.capability_id)
        if not capability:
            return False
        
        try:
            # Restore previous version
            capability.version = upgrade.from_version
            capability.updated_at = datetime.now().isoformat()
            self._save_capability(capability)
            
            # Update upgrade status
            upgrade.status = "rolled_back"
            self._save_upgrade(upgrade)
            self._log_upgrade_action(upgrade_id, "rolled_back", "Upgrade rolled back", success=True)
            
            return True
            
        except Exception as e:
            self._log_upgrade_action(upgrade_id, "rollback_failed", str(e), success=False)
            return False
    
    def get_upgrade_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get recommended capability upgrades
        
        Returns:
            List of upgrade recommendations
        """
        recommendations = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find capabilities that haven't been updated recently
        cutoff = (datetime.now() - timedelta(days=90)).isoformat()
        cursor.execute('''
            SELECT capability_id, name, version, updated_at
            FROM capabilities
            WHERE updated_at < ? AND status = 'deployed'
        ''', (cutoff,))
        
        for row in cursor.fetchall():
            recommendations.append({
                'capability_id': row[0],
                'name': row[1],
                'current_version': row[2],
                'last_updated': row[3],
                'reason': 'Not updated in 90+ days',
                'priority': 'medium',
                'suggested_upgrade': 'performance_review'
            })
        
        conn.close()
        return recommendations
    
    def get_capability_dependencies(self, capability_id: str) -> List[str]:
        """
        Get dependencies for a capability
        
        Args:
            capability_id: Capability ID
            
        Returns:
            List of dependency IDs
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT depends_on FROM capability_dependencies
            WHERE capability_id = ?
        ''', (capability_id,))
        
        deps = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return deps
    
    def _analyze_upgrade_impact(self, capability_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze impact of upgrade"""
        # Get dependent capabilities
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT capability_id FROM capability_dependencies
            WHERE depends_on = ?
        ''', (capability_id,))
        
        affected_capabilities = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return {
            'affected_capabilities': affected_capabilities,
            'breaking_changes': changes.get('breaking_changes', False),
            'performance_impact': changes.get('performance_impact', 'neutral'),
            'downtime_required': changes.get('downtime_required', False),
            'risk_level': self._calculate_risk_level(changes)
        }
    
    def _calculate_risk_level(self, changes: Dict[str, Any]) -> str:
        """Calculate risk level of changes"""
        if changes.get('breaking_changes'):
            return 'high'
        elif changes.get('downtime_required'):
            return 'medium'
        elif changes.get('performance_impact') == 'negative':
            return 'medium'
        else:
            return 'low'
    
    def _check_dependencies(self, capability_id: str) -> bool:
        """Check if all dependencies are satisfied"""
        deps = self.get_capability_dependencies(capability_id)
        
        for dep_id in deps:
            dep = self._get_capability(dep_id)
            if not dep or dep.status not in ['available', 'deployed']:
                return False
        
        return True
    
    def _apply_upgrade_changes(self, capability: Capability, changes: Dict[str, Any]):
        """Apply upgrade changes to capability"""
        # Update capability attributes based on changes
        if 'requirements' in changes:
            capability.requirements.update(changes['requirements'])
        
        if 'performance_metrics' in changes:
            capability.performance_metrics.update(changes['performance_metrics'])
        
        # In a real implementation, this would apply actual code/config changes
    
    def _add_dependency(self, capability_id: str, depends_on: str):
        """Add capability dependency"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO capability_dependencies
            (capability_id, depends_on, dependency_type)
            VALUES (?, ?, ?)
        ''', (capability_id, depends_on, 'required'))
        
        conn.commit()
        conn.close()
    
    def _save_capability(self, capability: Capability):
        """Save capability to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO capabilities
            (capability_id, name, description, category, version, status,
             dependencies, requirements, performance_metrics, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            capability.capability_id,
            capability.name,
            capability.description,
            capability.category,
            capability.version,
            capability.status,
            json.dumps(capability.dependencies),
            json.dumps(capability.requirements),
            json.dumps(capability.performance_metrics),
            capability.created_at,
            capability.updated_at
        ))
        
        conn.commit()
        conn.close()
    
    def _get_capability(self, capability_id: str) -> Optional[Capability]:
        """Get capability from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM capabilities WHERE capability_id = ?
        ''', (capability_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Capability(
                capability_id=row[0],
                name=row[1],
                description=row[2],
                category=row[3],
                version=row[4],
                status=row[5],
                dependencies=json.loads(row[6]),
                requirements=json.loads(row[7]),
                performance_metrics=json.loads(row[8]),
                created_at=row[9],
                updated_at=row[10]
            )
        
        return None
    
    def _save_upgrade(self, upgrade: CapabilityUpgrade):
        """Save upgrade to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO capability_upgrades
            (upgrade_id, capability_id, upgrade_type, priority, from_version,
             to_version, changes, impact_analysis, scheduled_date, completed_date,
             status, rollback_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            upgrade.upgrade_id,
            upgrade.capability_id,
            upgrade.upgrade_type,
            upgrade.priority,
            upgrade.from_version,
            upgrade.to_version,
            json.dumps(upgrade.changes),
            json.dumps(upgrade.impact_analysis),
            upgrade.scheduled_date,
            upgrade.completed_date,
            upgrade.status,
            json.dumps(upgrade.rollback_plan)
        ))
        
        conn.commit()
        conn.close()
    
    def _get_upgrade(self, upgrade_id: str) -> Optional[CapabilityUpgrade]:
        """Get upgrade from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM capability_upgrades WHERE upgrade_id = ?
        ''', (upgrade_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return CapabilityUpgrade(
                upgrade_id=row[0],
                capability_id=row[1],
                upgrade_type=row[2],
                priority=row[3],
                from_version=row[4],
                to_version=row[5],
                changes=json.loads(row[6]),
                impact_analysis=json.loads(row[7]) if row[7] else {},
                scheduled_date=row[8],
                completed_date=row[9],
                status=row[10],
                rollback_plan=json.loads(row[11]) if row[11] else {}
            )
        
        return None
    
    def _save_gap(self, gap: CapabilityGap):
        """Save capability gap to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO capability_gaps
            (gap_id, description, severity, affected_areas, proposed_solution,
             estimated_effort, identified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            gap.gap_id,
            gap.description,
            gap.severity,
            json.dumps(gap.affected_areas),
            gap.proposed_solution,
            gap.estimated_effort,
            gap.identified_at
        ))
        
        conn.commit()
        conn.close()
    
    def _log_upgrade_action(self, upgrade_id: str, action: str, details: str, success: bool = True):
        """Log upgrade action to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO upgrade_history
            (upgrade_id, action, timestamp, details, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            upgrade_id,
            action,
            datetime.now().isoformat(),
            details,
            1 if success else 0
        ))
        
        conn.commit()
        conn.close()


if __name__ == "__main__":
    # Example usage
    upgrader = SystemCapabilityUpgrader()
    
    # Register a capability
    capability = upgrader.register_capability(
        name="Advanced Pattern Recognition",
        description="Enhanced pattern recognition with ML",
        category="learning",
        version="1.0.0",
        requirements={'python_version': '3.8+', 'memory_mb': 512}
    )
    
    print(f"Registered capability: {capability.name}")
    
    # Assess capabilities
    assessment = upgrader.assess_capabilities()
    print(f"\nCapability assessment: {assessment}")
    
    # Plan an upgrade
    upgrade = upgrader.plan_upgrade(
        capability_id=capability.capability_id,
        upgrade_type=UpgradeType.ENHANCEMENT,
        priority=UpgradePriority.HIGH,
        to_version="1.1.0",
        changes={
            'performance_impact': 'positive',
            'breaking_changes': False,
            'new_features': ['real-time learning', 'adaptive algorithms']
        }
    )
    
    print(f"\nPlanned upgrade: {upgrade.upgrade_id}")
    print(f"Impact analysis: {upgrade.impact_analysis}")
