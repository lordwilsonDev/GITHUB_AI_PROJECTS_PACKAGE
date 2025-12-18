# 💾 Data Persistence Layer
## Self-Evolving AI Ecosystem

---

## Overview

Robust data persistence layer with comprehensive backup and rollback mechanisms. Handles all learning data, patterns, optimizations, and system state with version control.

---

## Features

### 📊 Data Storage
- **Learning Patterns**: Store and retrieve learned patterns with confidence scores
- **User Interactions**: Track all user interactions for learning
- **Optimizations**: Record optimization results and improvements
- **System State**: Snapshot system state for recovery

### 🔄 Version Control
- **Version History**: Track all changes to data
- **Rollback Support**: Restore previous versions of records
- **Change Tracking**: Audit trail of all modifications

### 💾 Backup System
- **Automatic Backups**: Scheduled daily, weekly, monthly backups
- **Manual Snapshots**: Create backups on demand
- **Compression**: Optional gzip compression for space efficiency
- **Checksum Verification**: Ensure backup integrity
- **Retention Policy**: Automatic cleanup of old backups

### 🔒 Safety Features
- **Thread-Safe**: Concurrent access protection
- **Transaction Support**: Atomic operations
- **Checksum Validation**: Data integrity verification
- **Safety Backups**: Automatic backup before restore operations

---

## Usage

### Initialize Persistence Layer

```python
from shared.database import get_persistence_layer

persistence = get_persistence_layer()
```

### Save Learning Patterns

```python
persistence.save_learning_pattern(
    pattern_id="pattern_001",
    pattern_type="user_preference",
    feature="learning-engine",
    confidence=0.85,
    data={
        'preference': 'morning_tasks',
        'frequency': 0.9,
        'context': 'productivity'
    },
    metadata={'source': 'interaction_analysis'}
)
```

### Retrieve Learning Patterns

```python
# Get all patterns for a feature
patterns = persistence.get_learning_patterns(
    feature="learning-engine",
    min_confidence=0.7,
    limit=100
)

# Filter by pattern type
user_prefs = persistence.get_learning_patterns(
    feature="learning-engine",
    pattern_type="user_preference",
    min_confidence=0.8
)
```

### Save User Interactions

```python
persistence.save_interaction(
    interaction_id="interaction_001",
    interaction_type="task_completion",
    feature="process-optimization",
    data={
        'task': 'data_analysis',
        'duration_ms': 1250,
        'method': 'automated'
    },
    success=True,
    metadata={'user_id': 'user_001'}
)
```

### Retrieve Interactions

```python
# Get recent interactions
interactions = persistence.get_interactions(
    feature="process-optimization",
    hours=24,
    success_only=True,
    limit=1000
)
```

### Save Optimizations

```python
persistence.save_optimization(
    optimization_id="opt_001",
    optimization_type="task_scheduling",
    feature="process-optimization",
    before_metric=45.2,
    after_metric=38.7,
    data={
        'algorithm': 'priority_queue_v2',
        'parameters': {'threshold': 0.8}
    },
    metadata={'test_samples': 1000}
)

# Mark optimization as applied
persistence.apply_optimization("opt_001")
```

### System State Management

```python
# Save system state
persistence.save_system_state(
    state_id="state_001",
    feature="learning-engine",
    state_type="configuration",
    state_data={
        'learning_rate': 0.01,
        'batch_size': 32,
        'enabled_features': ['pattern_recognition', 'trend_analysis']
    },
    metadata={'version': '1.0.0'}
)

# Retrieve system state
state = persistence.get_system_state("state_001")
```

### Backup Operations

```python
# Create manual backup
backup_id = persistence.create_backup(
    backup_type="manual",
    compress=True
)
print(f"Backup created: {backup_id}")

# Create scheduled backups
daily_backup = persistence.create_backup(backup_type="daily", compress=True)
weekly_backup = persistence.create_backup(backup_type="weekly", compress=True)
monthly_backup = persistence.create_backup(backup_type="monthly", compress=True)
```

### Restore from Backup

```python
# Restore from specific backup
try:
    persistence.restore_backup(backup_id)
    print("Backup restored successfully")
except Exception as e:
    print(f"Restore failed: {e}")
```

### Rollback to Previous Version

```python
# Rollback to previous version
success = persistence.rollback_to_version(
    table_name="learning_patterns",
    record_id="pattern_001"
)

# Rollback to specific timestamp
success = persistence.rollback_to_version(
    table_name="learning_patterns",
    record_id="pattern_001",
    timestamp="2025-12-15T00:00:00"
)
```

### Cleanup Old Backups

```python
# Clean up old backups based on retention policy
persistence.cleanup_old_backups(
    keep_daily=7,      # Keep last 7 daily backups
    keep_weekly=4,     # Keep last 4 weekly backups
    keep_monthly=12    # Keep last 12 monthly backups
)
```

---

## Database Schema

### Learning Patterns Table
```sql
CREATE TABLE learning_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT UNIQUE NOT NULL,
    pattern_type TEXT NOT NULL,
    feature TEXT NOT NULL,
    confidence REAL NOT NULL,
    data TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
)
```

### User Interactions Table
```sql
CREATE TABLE user_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id TEXT UNIQUE NOT NULL,
    interaction_type TEXT NOT NULL,
    feature TEXT NOT NULL,
    data TEXT NOT NULL,
    success BOOLEAN,
    timestamp TEXT NOT NULL,
    metadata TEXT
)
```

### Optimizations Table
```sql
CREATE TABLE optimizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    optimization_id TEXT UNIQUE NOT NULL,
    optimization_type TEXT NOT NULL,
    feature TEXT NOT NULL,
    before_metric REAL NOT NULL,
    after_metric REAL NOT NULL,
    improvement_percent REAL,
    status TEXT DEFAULT 'pending',
    applied_at TEXT,
    data TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### System State Table
```sql
CREATE TABLE system_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_id TEXT UNIQUE NOT NULL,
    feature TEXT NOT NULL,
    state_type TEXT NOT NULL,
    state_data TEXT NOT NULL,
    checksum TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metadata TEXT
)
```

### Version History Table
```sql
CREATE TABLE version_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id TEXT UNIQUE NOT NULL,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    data_before TEXT,
    data_after TEXT,
    timestamp TEXT NOT NULL,
    metadata TEXT
)
```

### Backup History Table
```sql
CREATE TABLE backup_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_id TEXT UNIQUE NOT NULL,
    backup_type TEXT NOT NULL,
    backup_path TEXT NOT NULL,
    checksum TEXT NOT NULL,
    size_bytes INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
)
```

---

## Backup Structure

```
data/backups/
├── daily/              # Daily backups (keep last 7)
│   ├── backup_20251215_000000.db.gz
│   └── ...
├── weekly/             # Weekly backups (keep last 4)
│   ├── backup_20251208_000000.db.gz
│   └── ...
├── monthly/            # Monthly backups (keep last 12)
│   ├── backup_20251201_000000.db.gz
│   └── ...
└── snapshots/          # Manual snapshots
    ├── backup_20251215_120000.db.gz
    └── ...
```

---

## Best Practices

### 1. Regular Backups
- Schedule daily backups during low-usage periods
- Create manual snapshots before major changes
- Test restore procedures regularly

### 2. Version Control
- All critical data changes are versioned automatically
- Use rollback for quick recovery from errors
- Review version history for audit trails

### 3. Data Integrity
- Checksums are verified on all backups
- Safety backups created before restore operations
- Transaction support ensures atomic operations

### 4. Performance
- Indexes optimize query performance
- Thread-safe operations prevent race conditions
- Connection pooling for efficiency

### 5. Retention Policy
- Keep 7 daily backups
- Keep 4 weekly backups
- Keep 12 monthly backups
- Clean up old backups regularly

---

## Error Handling

### Backup Failures
```python
try:
    backup_id = persistence.create_backup()
except Exception as e:
    logger.error(f"Backup failed: {e}")
    # Handle backup failure
```

### Restore Failures
```python
try:
    persistence.restore_backup(backup_id)
except FileNotFoundError:
    logger.error("Backup file not found")
except ValueError as e:
    logger.error(f"Checksum verification failed: {e}")
```

### Rollback Failures
```python
success = persistence.rollback_to_version(table, record_id)
if not success:
    logger.warning("No previous version available for rollback")
```

---

## Monitoring

The persistence layer integrates with the metrics system:

```python
from shared.metrics import get_metrics_collector

metrics = get_metrics_collector()

# Metrics are automatically recorded for:
# - Backup creation time
# - Backup size
# - Restore operations
# - Query performance
# - Storage usage
```

---

**Created:** December 15, 2025
**Status:** Production Ready
**Version:** 1.0.0
