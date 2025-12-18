"""Purgatory System - Temporary storage for low-VDR components"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
import shutil
from dataclasses import dataclass


@dataclass
class PurgatoryEntry:
    """Entry in purgatory"""
    component_id: str
    original_path: str
    purgatory_path: str
    reason: str
    vdr_at_purge: float
    purged_date: datetime
    deletion_date: datetime  # When it will be permanently deleted
    revival_count: int = 0
    
    def days_until_deletion(self) -> float:
        """Days until permanent deletion"""
        return (self.deletion_date - datetime.now()).total_seconds() / 86400
    
    def to_dict(self) -> dict:
        return {
            'component_id': self.component_id,
            'original_path': self.original_path,
            'purgatory_path': self.purgatory_path,
            'reason': self.reason,
            'vdr_at_purge': self.vdr_at_purge,
            'purged_date': self.purged_date.isoformat(),
            'deletion_date': self.deletion_date.isoformat(),
            'revival_count': self.revival_count,
        }


class Purgatory:
    """Manages components in purgatory before permanent deletion"""
    
    def __init__(self, purgatory_dir: Optional[Path] = None, grace_period_days: int = 30):
        self.purgatory_dir = purgatory_dir or Path.home() / '.moie_os' / 'purgatory'
        self.purgatory_dir.mkdir(parents=True, exist_ok=True)
        
        self.grace_period_days = grace_period_days
        self.entries: Dict[str, PurgatoryEntry] = {}
        self.manifest_path = self.purgatory_dir / 'manifest.json'
        
        self.load_manifest()
    
    def send_to_purgatory(self, component_id: str, original_path: str, reason: str, vdr: float) -> PurgatoryEntry:
        """Move a component to purgatory"""
        # Create purgatory path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_id = component_id.replace('/', '_').replace('.', '_')
        purgatory_path = self.purgatory_dir / f"{safe_id}_{timestamp}"
        
        # Copy file/directory to purgatory
        original = Path(original_path)
        if original.exists():
            if original.is_file():
                shutil.copy2(original, purgatory_path)
            else:
                shutil.copytree(original, purgatory_path)
        
        # Create entry
        entry = PurgatoryEntry(
            component_id=component_id,
            original_path=original_path,
            purgatory_path=str(purgatory_path),
            reason=reason,
            vdr_at_purge=vdr,
            purged_date=datetime.now(),
            deletion_date=datetime.now() + timedelta(days=self.grace_period_days),
        )
        
        self.entries[component_id] = entry
        self.save_manifest()
        
        return entry
    
    def revive(self, component_id: str) -> bool:
        """Revive a component from purgatory"""
        if component_id not in self.entries:
            return False
        
        entry = self.entries[component_id]
        
        # Restore file/directory
        purgatory_path = Path(entry.purgatory_path)
        original_path = Path(entry.original_path)
        
        if not purgatory_path.exists():
            return False
        
        # Ensure parent directory exists
        original_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Restore
        if purgatory_path.is_file():
            shutil.copy2(purgatory_path, original_path)
        else:
            if original_path.exists():
                shutil.rmtree(original_path)
            shutil.copytree(purgatory_path, original_path)
        
        # Update revival count
        entry.revival_count += 1
        
        # Remove from purgatory
        del self.entries[component_id]
        self.save_manifest()
        
        # Clean up purgatory copy
        if purgatory_path.is_file():
            purgatory_path.unlink()
        else:
            shutil.rmtree(purgatory_path)
        
        return True
    
    def permanently_delete(self, component_id: str) -> bool:
        """Permanently delete a component from purgatory"""
        if component_id not in self.entries:
            return False
        
        entry = self.entries[component_id]
        purgatory_path = Path(entry.purgatory_path)
        
        # Delete from purgatory
        if purgatory_path.exists():
            if purgatory_path.is_file():
                purgatory_path.unlink()
            else:
                shutil.rmtree(purgatory_path)
        
        # Remove from manifest
        del self.entries[component_id]
        self.save_manifest()
        
        return True
    
    def cleanup_expired(self) -> List[str]:
        """Delete components past their grace period"""
        deleted = []
        now = datetime.now()
        
        for component_id, entry in list(self.entries.items()):
            if now >= entry.deletion_date:
                if self.permanently_delete(component_id):
                    deleted.append(component_id)
        
        return deleted
    
    def get_entries_by_urgency(self) -> List[PurgatoryEntry]:
        """Get entries sorted by days until deletion"""
        return sorted(
            self.entries.values(),
            key=lambda e: e.days_until_deletion()
        )
    
    def get_summary(self) -> dict:
        """Get purgatory summary"""
        total = len(self.entries)
        
        if total == 0:
            return {
                'total_entries': 0,
                'avg_vdr': 0,
                'expiring_soon': 0,
                'avg_days_until_deletion': 0,
            }
        
        avg_vdr = sum(e.vdr_at_purge for e in self.entries.values()) / total
        expiring_soon = sum(1 for e in self.entries.values() if e.days_until_deletion() < 7)
        avg_days = sum(e.days_until_deletion() for e in self.entries.values()) / total
        
        return {
            'total_entries': total,
            'avg_vdr': avg_vdr,
            'expiring_soon': expiring_soon,
            'avg_days_until_deletion': avg_days,
        }
    
    def save_manifest(self):
        """Save purgatory manifest"""
        data = {
            'entries': {cid: entry.to_dict() for cid, entry in self.entries.items()},
            'grace_period_days': self.grace_period_days,
            'last_updated': datetime.now().isoformat(),
        }
        with open(self.manifest_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_manifest(self):
        """Load purgatory manifest"""
        if not self.manifest_path.exists():
            return
        
        try:
            with open(self.manifest_path, 'r') as f:
                data = json.load(f)
            
            self.grace_period_days = data.get('grace_period_days', 30)
            
            for cid, entry_data in data.get('entries', {}).items():
                entry = PurgatoryEntry(
                    component_id=entry_data['component_id'],
                    original_path=entry_data['original_path'],
                    purgatory_path=entry_data['purgatory_path'],
                    reason=entry_data['reason'],
                    vdr_at_purge=entry_data['vdr_at_purge'],
                    purged_date=datetime.fromisoformat(entry_data['purged_date']),
                    deletion_date=datetime.fromisoformat(entry_data['deletion_date']),
                    revival_count=entry_data.get('revival_count', 0),
                )
                self.entries[cid] = entry
        except Exception as e:
            print(f"Warning: Could not load purgatory manifest: {e}")
