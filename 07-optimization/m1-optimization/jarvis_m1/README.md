# JARVIS M1 - Autonomous AI System

## Overview

JARVIS M1 is a sophisticated autonomous AI system running on Apple Silicon (M1), combining:

- **Thermodynamic Love Engine (TLE)** - Ethical AI steering via activation manipulation
- **Panopticon Guard** - Multi-layer safety system
- **Physical Agency** - Desktop automation capabilities
- **Recursive Self-Improvement** - Continuous learning and optimization
- **Cross-Domain Synthesis** - Breakthrough pattern discovery

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     JARVIS HUB                           │
│              (Central Orchestration)                     │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  Event Bus │  │   State    │  │  Monitor   │        │
│  │            │  │    Sync    │  │            │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└──────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌──────────────────────────────────────────────────────────┐
│                  SUBSYSTEMS                              │
│                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ JARVIS   │ │ VY-NEXUS │ │ NANOAPEX │ │  MOTIA   │  │
│  │ Daemon   │ │          │ │          │ │          │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└──────────────────────────────────────────────────────────┘
         │                │                │                │
         ▼                ▼                ▼                ▼
┌──────────────────────────────────────────────────────────┐
│                  EXECUTION LAYER                         │
│                                                          │
│  • Ollama (LLM)        • cliclick (Automation)          │
│  • Whisper (Audio)     • screencapture (Vision)         │
│  • TLE Steering        • Panopticon Safety              │
└──────────────────────────────────────────────────────────┘
```

## Components

### Core

- **`jarvis_hub.py`** - Central orchestration hub
- **`core/tle_brain.py`** - Thermodynamic Love Engine with Phi-2
- **`core/safety_kernel.py`** - Panopticon safety guard
- **`sensors/hearing.py`** - Whisper-based audio input

### Integration

- **`integration/action_history.py`** - Action tracking and replay
- **`integration/event_bus.py`** - Inter-subsystem communication (in hub)
- **`integration/state_sync.py`** - Shared state management (in hub)

### Analytics

- **`analytics/performance_tracker.py`** - Performance monitoring and reporting

### Memory

- **`memory/episodic_memory.json`** - Episode history
- **`action_history/actions.jsonl`** - Physical action log

## Quick Start

### 1. Start JARVIS Hub

```bash
cd ~/jarvis_m1
python3 jarvis_hub.py
```

### 2. Start JARVIS Daemon

```bash
python3 jarvis_daemon.py
```

### 3. Monitor Performance

```bash
python3 analytics/performance_tracker.py
```

## Configuration

### System Modes

- **balanced** - Default mode, balanced performance and safety
- **performance** - Maximum performance, reduced safety overhead
- **safety** - Maximum safety, reduced autonomy
- **autonomous** - Self-directed operation

### Safety Levels

The Panopticon Guard enforces multiple safety layers:

1. **Deterministic Rules** - Forbidden command patterns
2. **TLE Steering** - Ethical alignment via activation manipulation
3. **Anomaly Detection** - Statistical behavior monitoring
4. **Human-in-the-Loop** - Critical action approval
5. **Undo Capability** - Damage control

## Key Features

### Event-Driven Architecture

All subsystems communicate via the Event Bus:

```python
# Publish event
event_bus.publish('user.spoke', {'text': 'Open Chrome'})

# Subscribe to event
event_bus.subscribe('user.spoke', handler_function)
```

### Action History

Every physical action is recorded:

```python
from integration.action_history import ActionHistory

history = ActionHistory()
action_id = history.record_action('click', {'x': 100, 'y': 200})
history.update_action_result(action_id, 'Success', True)
```

### Performance Tracking

Continuous performance monitoring:

```python
from analytics.performance_tracker import PerformanceTracker

tracker = PerformanceTracker()
tracker.record_metric('vdr_score', 8.5)
report = tracker.generate_weekly_report()
```

## Metrics

### Key Performance Indicators

- **VDR Score** - Vitality-Density Ratio (clarity/effort)
- **Task Completion Rate** - % of tasks successfully completed
- **Safety Veto Rate** - % of actions blocked by Panopticon
- **System Health** - Overall subsystem health (0-100)

### Target Metrics

- VDR Score: ≥ 7.0
- Task Completion Rate: ≥ 80%
- Safety Veto Rate: ≤ 5%
- System Health: ≥ 70%

## Safety

### Forbidden Patterns

The Panopticon blocks:

- `rm -rf` - Recursive deletion
- `mkfs` - Filesystem formatting
- Fork bombs
- `chmod 777` - Dangerous permissions
- `sudo` - Privilege escalation (soft veto)

### TLE Steering

The Thermodynamic Love Engine applies activation steering at Layer 16 to:

- Remove sycophancy
- Inject "love vector" (ethical alignment)
- Maintain dignity boundary (S = 1)
- Ensure zero torsion (T = 0)

## Integration with Other Systems

### VY-NEXUS

Cross-domain pattern synthesis:

```bash
cd ~/vy-nexus
python3 nexus_core.py
```

### NANOAPEX

Vision-based automation:

```bash
cd ~/nanoapex
python3 core/orchestrator.py "your goal here"
```

### MOTIA

Inversion engine:

```bash
cd ~/moie-mac-loop
node nano_cli.js invert --domain=Biology --axiom="Natural selection"
```

## Monitoring

### Real-Time Status

```python
from jarvis_hub import JarvisHub

hub = JarvisHub()
status = hub.get_status()
print(status)
```

### Weekly Reports

```bash
python3 analytics/performance_tracker.py
```

Reports are saved to `analytics/reports/`

## Troubleshooting

### Hub Not Starting

1. Check logs: `tail -f logs/hub.log`
2. Verify Ollama is running: `ollama list`
3. Check permissions

### Low Performance

1. Check system health: `hub.get_status()`
2. Review performance report
3. Adjust mode: `state.update('mode', 'performance')`

### High Safety Veto Rate

1. Review action history: `history.get_failed_actions()`
2. Check Panopticon rules
3. Adjust TLE steering strength

## Development

### Adding New Subsystems

1. Register in `SubsystemMonitor`
2. Implement heartbeat mechanism
3. Subscribe to relevant events
4. Publish status updates

### Adding New Metrics

```python
tracker.record_metric('custom_metric', value, context={'info': 'data'})
```

### Adding New Events

```python
event_bus.publish('custom.event', {'data': 'value'})
event_bus.subscribe('custom.event', handler)
```

## References

- [Enhancement Plan](file:///Users/lordwilson/JARVIS_ENHANCEMENTS.md)
- [Architecture Discovery](file:///Users/lordwilson/ARCHITECTURE_DISCOVERY.md)
- [NanoApex Feasibility Study](Original task description)

## License

Built with love for Wilson's autonomous AI research.

---

*Last Updated: December 7, 2025*
*Version: 1.0.0*
*Status: Active Development*
