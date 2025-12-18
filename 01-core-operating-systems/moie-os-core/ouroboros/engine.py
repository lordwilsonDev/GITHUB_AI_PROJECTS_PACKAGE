"""Ouroboros Engine - Self-Pruning System via Via Negativa"""

from typing import List, Dict, Optional, Callable
from datetime import datetime
from pathlib import Path
import time

from .health_tracker import HealthTracker, ComponentHealth
from .purgatory import Purgatory, PurgatoryEntry


class OuroborosEngine:
    """Self-pruning engine that improves system by deletion
    
    Philosophy: Via Negativa - the system gets better by removing
    low-value components, not by adding more.
    
    Process:
    1. Monitor component health (VDR metrics)
    2. Identify low-VDR or stale components
    3. Move to purgatory (grace period)
    4. Permanently delete if not revived
    5. System becomes leaner and more efficient
    """
    
    def __init__(
        self,
        health_tracker: Optional[HealthTracker] = None,
        purgatory: Optional[Purgatory] = None,
        min_vdr: float = 0.1,
        stale_days: int = 30,
        grace_period_days: int = 30,
    ):
        self.health_tracker = health_tracker or HealthTracker()
        self.purgatory = purgatory or Purgatory(grace_period_days=grace_period_days)
        
        self.min_vdr = min_vdr
        self.stale_days = stale_days
        self.grace_period_days = grace_period_days
        
        self.is_running = False
        self.last_scan_time: Optional[datetime] = None
        self.scan_count = 0
        
        # Callbacks
        self.on_component_purged: Optional[Callable[[ComponentHealth], None]] = None
        self.on_component_deleted: Optional[Callable[[str], None]] = None
        self.on_component_revived: Optional[Callable[[str], None]] = None
    
    def scan_and_prune(self, dry_run: bool = False) -> Dict[str, any]:
        """Scan system and prune low-value components
        
        Args:
            dry_run: If True, only report what would be done without actually doing it
        
        Returns:
            Dictionary with scan results
        """
        self.scan_count += 1
        self.last_scan_time = datetime.now()
        
        results = {
            'scan_time': self.last_scan_time.isoformat(),
            'scan_count': self.scan_count,
            'dry_run': dry_run,
            'candidates_found': 0,
            'components_purged': 0,
            'components_deleted': 0,
            'candidates': [],
            'purged': [],
            'deleted': [],
        }
        
        # Step 1: Find candidates for purgatory
        candidates = self.health_tracker.get_candidates_for_purgatory(
            min_vdr=self.min_vdr,
            stale_days=self.stale_days,
        )
        
        results['candidates_found'] = len(candidates)
        results['candidates'] = [
            {
                'component_id': c.component_id,
                'vdr': c.vdr,
                'days_since_use': c.days_since_last_use(),
                'reason': self._get_purge_reason(c),
            }
            for c in candidates
        ]
        
        # Step 2: Move candidates to purgatory
        if not dry_run:
            for component in candidates:
                reason = self._get_purge_reason(component)
                entry = self.purgatory.send_to_purgatory(
                    component_id=component.component_id,
                    original_path=component.path,
                    reason=reason,
                    vdr=component.vdr,
                )
                
                # Update component health
                component.purgatory_date = entry.purged_date
                
                results['components_purged'] += 1
                results['purged'].append({
                    'component_id': component.component_id,
                    'reason': reason,
                    'vdr': component.vdr,
                })
                
                if self.on_component_purged:
                    self.on_component_purged(component)
        
        # Step 3: Cleanup expired purgatory entries
        if not dry_run:
            deleted = self.purgatory.cleanup_expired()
            results['components_deleted'] = len(deleted)
            results['deleted'] = deleted
            
            for component_id in deleted:
                if self.on_component_deleted:
                    self.on_component_deleted(component_id)
        
        return results
    
    def _get_purge_reason(self, component: ComponentHealth) -> str:
        """Determine reason for purging component"""
        reasons = []
        
        if component.vdr < self.min_vdr:
            reasons.append(f"Low VDR ({component.vdr:.3f} < {self.min_vdr})")
        
        days_since = component.days_since_last_use()
        if days_since is not None and days_since > self.stale_days:
            reasons.append(f"Stale ({days_since:.0f} days since last use)")
        
        if not component.is_healthy:
            reasons.append("Unhealthy status")
        
        if component.warnings:
            reasons.append(f"{len(component.warnings)} warnings")
        
        return "; ".join(reasons) if reasons else "Unknown"
    
    def revive_component(self, component_id: str) -> bool:
        """Revive a component from purgatory
        
        This is called when a component is needed again,
        proving it has value and should not be deleted.
        """
        success = self.purgatory.revive(component_id)
        
        if success:
            # Update health tracker
            if component_id in self.health_tracker.components:
                comp = self.health_tracker.components[component_id]
                comp.purgatory_date = None
                comp.revival_count += 1
                comp.record_usage()
                self.health_tracker.save()
            
            if self.on_component_revived:
                self.on_component_revived(component_id)
        
        return success
    
    def force_delete(self, component_id: str) -> bool:
        """Force permanent deletion of a component"""
        success = self.purgatory.permanently_delete(component_id)
        
        if success and self.on_component_deleted:
            self.on_component_deleted(component_id)
        
        return success
    
    def get_system_health(self) -> dict:
        """Get overall system health metrics"""
        health_summary = self.health_tracker.get_health_summary()
        purgatory_summary = self.purgatory.get_summary()
        
        return {
            'health': health_summary,
            'purgatory': purgatory_summary,
            'ouroboros': {
                'is_running': self.is_running,
                'last_scan': self.last_scan_time.isoformat() if self.last_scan_time else None,
                'scan_count': self.scan_count,
                'min_vdr_threshold': self.min_vdr,
                'stale_days_threshold': self.stale_days,
                'grace_period_days': self.grace_period_days,
            },
        }
    
    def get_recommendations(self) -> List[dict]:
        """Get recommendations for system improvement"""
        recommendations = []
        
        health = self.health_tracker.get_health_summary()
        
        # Low overall health
        if health['health_percentage'] < 70:
            recommendations.append({
                'priority': 'high',
                'category': 'system_health',
                'message': f"System health is low ({health['health_percentage']:.1f}%). Run scan_and_prune() to clean up.",
                'action': 'scan_and_prune',
            })
        
        # Many unhealthy components
        if health['unhealthy'] > 5:
            recommendations.append({
                'priority': 'medium',
                'category': 'unhealthy_components',
                'message': f"{health['unhealthy']} unhealthy components detected. Consider reviewing and pruning.",
                'action': 'review_unhealthy',
            })
        
        # Low average VDR
        if health['avg_vdr'] < 0.3:
            recommendations.append({
                'priority': 'high',
                'category': 'low_vdr',
                'message': f"Average VDR is low ({health['avg_vdr']:.3f}). System complexity may be too high.",
                'action': 'reduce_complexity',
            })
        
        # Purgatory cleanup
        purgatory = self.purgatory.get_summary()
        if purgatory['expiring_soon'] > 0:
            recommendations.append({
                'priority': 'low',
                'category': 'purgatory',
                'message': f"{purgatory['expiring_soon']} components expiring soon. Review for revival or let expire.",
                'action': 'review_purgatory',
            })
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate a human-readable report"""
        health = self.get_system_health()
        recommendations = self.get_recommendations()
        
        report = []
        report.append("=" * 60)
        report.append("OUROBOROS SYSTEM HEALTH REPORT")
        report.append("=" * 60)
        report.append("")
        
        # System Health
        report.append("📊 SYSTEM HEALTH:")
        h = health['health']
        report.append(f"  Total Components: {h['total_components']}")
        report.append(f"  Healthy: {h['healthy']} ({h['health_percentage']:.1f}%)")
        report.append(f"  Unhealthy: {h['unhealthy']}")
        report.append(f"  In Purgatory: {h['in_purgatory']}")
        report.append(f"  Average VDR: {h['avg_vdr']:.3f}")
        report.append(f"  Average SEM: {h['avg_sem']:.3f}")
        report.append("")
        
        # Purgatory
        report.append("🔥 PURGATORY:")
        p = health['purgatory']
        report.append(f"  Total Entries: {p['total_entries']}")
        if p['total_entries'] > 0:
            report.append(f"  Average VDR at Purge: {p['avg_vdr']:.3f}")
            report.append(f"  Expiring Soon (< 7 days): {p['expiring_soon']}")
            report.append(f"  Avg Days Until Deletion: {p['avg_days_until_deletion']:.1f}")
        report.append("")
        
        # Ouroboros Status
        report.append("🐍 OUROBOROS STATUS:")
        o = health['ouroboros']
        report.append(f"  Running: {o['is_running']}")
        report.append(f"  Last Scan: {o['last_scan'] or 'Never'}")
        report.append(f"  Total Scans: {o['scan_count']}")
        report.append(f"  VDR Threshold: {o['min_vdr_threshold']}")
        report.append(f"  Stale Threshold: {o['stale_days_threshold']} days")
        report.append(f"  Grace Period: {o['grace_period_days']} days")
        report.append("")
        
        # Recommendations
        if recommendations:
            report.append("💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '⚪')
                report.append(f"  {i}. {priority_emoji} [{rec['priority'].upper()}] {rec['message']}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
