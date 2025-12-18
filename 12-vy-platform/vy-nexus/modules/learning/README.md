# User Interaction Monitor

## Overview

The User Interaction Monitor is a core component of the VY-NEXUS Self-Evolving AI Ecosystem. It tracks and learns from all user interactions with the system while respecting privacy and security.

## Features

### Data Collection
- **Command Pattern Tracking**: Records all CLI commands and API requests
- **Success/Failure Monitoring**: Tracks outcome of each interaction
- **Timing Analysis**: Measures execution duration for performance insights
- **Error Pattern Detection**: Identifies common failure modes
- **Metadata Storage**: Captures contextual information

### Privacy & Security
- **Anonymization**: User IDs are hashed before storage
- **No PII Collection**: System does not collect personally identifiable information
- **Data Retention**: Automatic cleanup after 90 days
- **Encrypted Storage**: Sensitive data is encrypted at rest
- **User Opt-Out**: Users can disable monitoring

### Performance
- **Batched Writes**: Interactions buffered and written in batches
- **Background Flushing**: Data persisted every 60 seconds
- **Thread-Safe**: Concurrent interaction recording supported
- **Low Overhead**: Minimal impact on system performance (<5%)

## Architecture

```
User Interaction
      ↓
[CLI/API Hooks]
      ↓
[UserInteractionMonitor]
      │
      ├──> [In-Memory Buffer] (1000 interactions)
      │
      ├──> [Background Flush Thread] (every 60s)
      │
      └──> [Disk Storage] (JSONL files)
            │
            ├──> interactions_YYYY-MM-DD.jsonl
            ├──> user_profiles.json
            └──> patterns.json
```

## Installation

### Prerequisites
- Python 3.8+
- Write access to `~/vy_data/interactions/`
- Write access to `~/vy_logs/`

### Setup

```bash
# Create required directories
mkdir -p ~/vy_data/interactions
mkdir -p ~/vy_logs

# No additional dependencies required (uses Python stdlib only)
```

## Usage

### Basic Usage

```python
from learning.user_interaction_monitor import (
    get_monitor,
    InteractionType,
    InteractionStatus
)

# Get singleton monitor instance
monitor = get_monitor()

# Record an interaction
monitor.record_interaction(
    interaction_type=InteractionType.CLI_COMMAND,
    command="status",
    status=InteractionStatus.SUCCESS,
    duration_ms=45.5,
    user_id="user123"  # Optional, will be anonymized
)

# Get statistics
stats = monitor.get_statistics()
print(f"Total interactions: {stats['total_interactions']}")
print(f"Success rate: {stats['successful_interactions'] / stats['total_interactions']}")

# Analyze recent interactions
analysis = monitor.analyze_recent_interactions(hours=24)
print(f"Commands in last 24h: {analysis['command_frequency']}")
print(f"Success rate: {analysis['success_rate']}")
```

### CLI Integration

```python
from integration.cli_hooks import track_cli_command

# Using decorator
@track_cli_command("my_command")
def handle_my_command():
    # Your command implementation
    return "Success"

# Using middleware
from integration.cli_hooks import CLIMonitoringMiddleware

middleware = CLIMonitoringMiddleware()

# Before command
context = middleware.before_command("status", [], {})

# Execute command
try:
    result = execute_command()
    middleware.after_command(context, success=True)
except Exception as e:
    middleware.after_command(context, success=False, error=e)
```

### API Integration

```python
from integration.api_hooks import create_flask_middleware
from flask import Flask

app = Flask(__name__)

# Add monitoring middleware
create_flask_middleware(app)

# All API requests will now be tracked automatically
```

### Manual Recording

```python
from integration.cli_hooks import record_cli_interaction

record_cli_interaction(
    command="custom_command",
    success=True,
    duration_ms=123.4,
    error=None,
    metadata={"custom_field": "value"}
)
```

## Data Models

### Interaction

Represents a single user interaction:

```python
@dataclass
class Interaction:
    timestamp: str              # ISO 8601 format
    interaction_type: str       # cli_command, api_request, etc.
    command: str                # Command name (anonymized)
    status: str                 # success, failure, error, timeout
    duration_ms: float          # Execution time in milliseconds
    error_message: Optional[str]  # Error details if failed
    metadata: Dict[str, Any]    # Additional context
    session_id: Optional[str]   # Session identifier
    user_hash: Optional[str]    # Anonymized user ID
```

### InteractionPattern

Represents a detected pattern:

```python
@dataclass
class InteractionPattern:
    pattern_id: str             # Unique identifier
    pattern_type: str           # Type of pattern
    frequency: int              # How often pattern occurs
    first_seen: str             # First occurrence timestamp
    last_seen: str              # Last occurrence timestamp
    confidence: float           # Confidence score (0-1)
    description: str            # Human-readable description
    examples: List[str]         # Example interactions
```

### UserProfile

Aggregated user behavior profile:

```python
@dataclass
class UserProfile:
    user_hash: str                      # Anonymized user ID
    total_interactions: int             # Total interaction count
    success_rate: float                 # Success percentage
    avg_session_duration_minutes: float # Average session length
    peak_usage_hours: List[int]         # Hours of peak activity
    common_commands: List[str]          # Most used commands
    common_errors: List[str]            # Frequent errors
    preferred_experts: List[str]        # Preferred expert types
    last_updated: str                   # Last profile update
```

## API Reference

### UserInteractionMonitor

#### Methods

**`start()`**
- Starts background monitoring thread
- Begins periodic flushing to disk

**`stop()`**
- Stops monitoring and flushes remaining data
- Joins background thread

**`record_interaction(...)`**
- Records a single user interaction
- Returns: timestamp of recorded interaction
- Thread-safe

**`get_patterns(min_frequency=3)`**
- Returns detected patterns
- Args: `min_frequency` - minimum occurrences to include
- Returns: List of InteractionPattern objects

**`get_user_profile(user_id)`**
- Returns user behavior profile
- Args: `user_id` - user identifier (will be anonymized)
- Returns: UserProfile object or None

**`get_statistics()`**
- Returns monitoring statistics
- Returns: Dict with counts and metrics

**`analyze_recent_interactions(hours=24)`**
- Analyzes interactions within time window
- Args: `hours` - time window in hours
- Returns: Dict with analysis results

## Storage Format

### Interaction Files

Location: `~/vy_data/interactions/interactions_YYYY-MM-DD.jsonl`

Format: JSON Lines (one JSON object per line)

```json
{"timestamp": "2025-12-15T10:30:45.123456", "interaction_type": "cli_command", "command": "status", "status": "success", "duration_ms": 45.5, "error_message": null, "metadata": {}, "session_id": "2025121510", "user_hash": "a1b2c3d4e5f6g7h8"}
```

### User Profiles

Location: `~/vy_data/interactions/user_profiles.json`

Format: JSON object with user_hash as keys

```json
{
  "a1b2c3d4e5f6g7h8": {
    "user_hash": "a1b2c3d4e5f6g7h8",
    "total_interactions": 150,
    "success_rate": 0.95,
    "avg_session_duration_minutes": 12.5,
    "peak_usage_hours": [9, 10, 14, 15],
    "common_commands": ["status", "query", "experts"],
    "common_errors": ["timeout"],
    "preferred_experts": ["code_expert", "research_expert"],
    "last_updated": "2025-12-15T10:30:45.123456"
  }
}
```

### Patterns

Location: `~/vy_data/interactions/patterns.json`

Format: JSON object with pattern_id as keys

```json
{
  "pattern_001": {
    "pattern_id": "pattern_001",
    "pattern_type": "repetitive_command",
    "frequency": 25,
    "first_seen": "2025-12-10T08:00:00",
    "last_seen": "2025-12-15T10:30:00",
    "confidence": 0.92,
    "description": "User frequently checks system status",
    "examples": ["status", "status", "status"]
  }
}
```

## Configuration

Edit constants in `user_interaction_monitor.py`:

```python
# Data retention (days)
RETENTION_DAYS = 90

# Privacy settings
ANONYMIZE_DATA = True
COLLECT_PII = False

# Performance settings
BATCH_SIZE = 100
FLUSH_INTERVAL_SECONDS = 60
```

## Testing

### Run Tests

```bash
# Run all tests
python tests/test_user_interaction_monitor.py

# Run specific test
python tests/test_user_interaction_monitor.py TestUserInteractionMonitor.test_record_interaction

# Run with verbose output
python tests/test_user_interaction_monitor.py -v
```

### Manual Testing

```bash
# Test basic functionality
python modules/learning/user_interaction_monitor.py test

# View statistics
python modules/learning/user_interaction_monitor.py stats

# Analyze recent interactions
python modules/learning/user_interaction_monitor.py analyze 24
```

## Performance Metrics

- **Recording Overhead**: <1ms per interaction
- **Memory Usage**: ~100KB for 1000 buffered interactions
- **Disk I/O**: Batched writes every 60 seconds
- **CPU Impact**: <1% during normal operation
- **Thread Safety**: Lock-based synchronization

## Troubleshooting

### Issue: Interactions not being recorded

**Solution**: Check that monitor is started:
```python
monitor = get_monitor()
monitor.start()  # Ensure this is called
```

### Issue: High memory usage

**Solution**: Reduce buffer size:
```python
BATCH_SIZE = 50  # Reduce from 100
```

### Issue: Data not flushing to disk

**Solution**: Check directory permissions:
```bash
ls -la ~/vy_data/interactions/
# Should be writable by current user
```

### Issue: Thread errors on shutdown

**Solution**: Ensure proper cleanup:
```python
import atexit
from learning.user_interaction_monitor import stop_monitor

atexit.register(stop_monitor)
```

## Integration with Existing Systems

### Living Memory

Interaction data can be ingested into Living Memory for long-term pattern recognition:

```python
from living_memory_engine import LivingMemory

memory = LivingMemory()
analysis = monitor.analyze_recent_interactions(hours=24)
memory.ingest("user_patterns", analysis)
```

### NEXUS Core

Patterns can be fed to NEXUS for cross-domain synthesis:

```python
from nexus_core import NexusCore

nexus = NexusCore()
patterns = monitor.get_patterns(min_frequency=5)
nexus.analyze_patterns(patterns)
```

### Journalist Service

All monitoring activity is logged to the system journal:

```python
# Logs automatically written to:
# - ~/vy_logs/interaction_monitor.log
# - ~/research_logs/system_journal.md
```

## Roadmap

### Version 1.1 (Planned)
- [ ] Real-time pattern detection
- [ ] Anomaly detection
- [ ] Predictive analytics
- [ ] User segmentation
- [ ] A/B testing support

### Version 1.2 (Planned)
- [ ] Machine learning integration
- [ ] Advanced privacy controls
- [ ] Multi-user support
- [ ] Dashboard visualization
- [ ] Export to external analytics

## License

Proprietary - VY-NEXUS Self-Evolving AI Ecosystem

## Support

For issues or questions, check:
- System logs: `~/vy_logs/interaction_monitor.log`
- System journal: `~/research_logs/system_journal.md`
- Test suite: `tests/test_user_interaction_monitor.py`

---

**Version**: 1.0.0  
**Last Updated**: December 15, 2025  
**Status**: Production Ready
