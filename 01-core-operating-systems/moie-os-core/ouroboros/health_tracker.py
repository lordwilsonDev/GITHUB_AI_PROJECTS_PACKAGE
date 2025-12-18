"""Component Health Tracking System"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class ComponentHealth:
    """Tracks health metrics for a system component"""
    component_id: str
    component_type: str  # 'module', 'function', 'class', 'file'
    path: str
    
    # VDR metrics
    vitality: float = 0.0
    density: float = 1.0
    vdr: float = 0.0
    sem: float = 0.0
    
    # Usage tracking
    last_used: Optional[datetime] = None
    usage_count: int = 0
    creation_date: datetime = field(default_factory=datetime.now)
    
    # Health status
    is_healthy: bool = True
    warnings: List[str] = field(default_factory=list)
    
    # Purgatory tracking
    purgatory_date: Optional[datetime] = None
    revival_count: int = 0
    
    def update_vdr(self, vitality: float, density: float, alpha: float = 1.5):
        """Update VDR metrics"""
        self.vitality = vitality
        self.density = max(density, 1e-6)
        self.vdr = vitality / (self.density ** alpha)
        self.sem = self.vdr / (1.0 + self.vdr)
        self.is_healthy = self.vdr >= 0.1 and self.sem >= 0.05
    
    def record_usage(self):
        """Record component usage"""
        self.last_used = datetime.now()
        self.usage_count += 1
    
    def days_since_last_use(self) -> Optional[float]:
        """Calculate days since last use"""
        if self.last_used is None:
            return None
        return (datetime.now() - self.last_used).total_seconds() / 86400
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'component_id': self.component_id,
            'component_type': self.component_type,
            'path': self.path,
            'vitality': self.vitality,
            'density': self.density,
            'vdr': self.vdr,
            'sem': self.sem,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count,
            'creation_date': self.creation_date.isoformat(),
            'is_healthy': self.is_healthy,
            'warnings': self.warnings,
            'purgatory_date': self.purgatory_date.isoformat() if self.purgatory_date else None,
            'revival_count': self.revival_count,
        }


class HealthTracker:
    """Tracks health of all system components"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.components: Dict[str, ComponentHealth] = {}
        self.storage_path = storage_path or Path.home() / '.moie_os' / 'health_tracker.json'
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.load()
    
    def register_component(self, component_id: str, component_type: str, path: str) -> ComponentHealth:
        """Register a new component for tracking"""
        if component_id in self.components:
            return self.components[component_id]
        
        component = ComponentHealth(
            component_id=component_id,
            component_type=component_type,
            path=path,
        )
        self.components[component_id] = component
        self.save()
        return component
    
    def update_component_vdr(self, component_id: str, vitality: float, density: float):
        """Update VDR metrics for a component"""
        if component_id not in self.components:
            raise ValueError(f"Component {component_id} not registered")
        
        self.components[component_id].update_vdr(vitality, density)
        self.save()
    
    def record_usage(self, component_id: str):
        """Record component usage"""
        if component_id in self.components:
            self.components[component_id].record_usage()
            self.save()
    
    def get_unhealthy_components(self, min_vdr: float = 0.1) -> List[ComponentHealth]:
        """Get list of unhealthy components"""
        return [
            comp for comp in self.components.values()
            if comp.vdr < min_vdr
        ]
    
    def get_stale_components(self, days: int = 30) -> List[ComponentHealth]:
        """Get components not used in N days"""
        stale = []
        for comp in self.components.values():
            days_since = comp.days_since_last_use()
            if days_since is not None and days_since > days:
                stale.append(comp)
        return stale
    
    def get_candidates_for_purgatory(self, min_vdr: float = 0.1, stale_days: int = 30) -> List[ComponentHealth]:
        """Get components that should be moved to purgatory"""
        candidates = []
        for comp in self.components.values():
            # Already in purgatory
            if comp.purgatory_date is not None:
                continue
            
            # Low VDR
            if comp.vdr < min_vdr:
                candidates.append(comp)
                continue
            
            # Stale
            days_since = comp.days_since_last_use()
            if days_since is not None and days_since > stale_days:
                candidates.append(comp)
        
        return candidates
    
    def get_health_summary(self) -> dict:
        """Get overall health summary"""
        total = len(self.components)
        healthy = sum(1 for c in self.components.values() if c.is_healthy)
        in_purgatory = sum(1 for c in self.components.values() if c.purgatory_date is not None)
        
        avg_vdr = sum(c.vdr for c in self.components.values()) / total if total > 0 else 0
        avg_sem = sum(c.sem for c in self.components.values()) / total if total > 0 else 0
        
        return {
            'total_components': total,
            'healthy': healthy,
            'unhealthy': total - healthy,
            'in_purgatory': in_purgatory,
            'avg_vdr': avg_vdr,
            'avg_sem': avg_sem,
            'health_percentage': (healthy / total * 100) if total > 0 else 0,
        }
    
    def save(self):
        """Save health data to disk"""
        data = {
            'components': {cid: comp.to_dict() for cid, comp in self.components.items()},
            'last_updated': datetime.now().isoformat(),
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load health data from disk"""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            for cid, comp_data in data.get('components', {}).items():
                comp = ComponentHealth(
                    component_id=comp_data['component_id'],
                    component_type=comp_data['component_type'],
                    path=comp_data['path'],
                    vitality=comp_data['vitality'],
                    density=comp_data['density'],
                    vdr=comp_data['vdr'],
                    sem=comp_data['sem'],
                    usage_count=comp_data['usage_count'],
                    is_healthy=comp_data['is_healthy'],
                    warnings=comp_data['warnings'],
                    revival_count=comp_data['revival_count'],
                )
                
                if comp_data['last_used']:
                    comp.last_used = datetime.fromisoformat(comp_data['last_used'])
                if comp_data['creation_date']:
                    comp.creation_date = datetime.fromisoformat(comp_data['creation_date'])
                if comp_data['purgatory_date']:
                    comp.purgatory_date = datetime.fromisoformat(comp_data['purgatory_date'])
                
                self.components[cid] = comp
        except Exception as e:
            print(f"Warning: Could not load health tracker data: {e}")
