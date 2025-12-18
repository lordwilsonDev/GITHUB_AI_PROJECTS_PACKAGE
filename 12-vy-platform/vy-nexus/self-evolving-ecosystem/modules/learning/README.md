# Learning Modules

This directory contains modules for the Continuous Learning Engine of the self-evolving AI ecosystem.

## Modules

### 1. Interaction Monitor (`interaction_monitor.py`)
**Purpose:** Monitor and track all user interactions

**Features:**
- Record task requests with priority and tags
- Track user feedback (positive, negative, suggestions)
- Log questions and clarifications
- Store user preferences
- Session management
- Interaction statistics

**Usage:**
```python
from interaction_monitor import get_monitor

monitor = get_monitor()
monitor.record_task_request(
    "Create a new feature",
    priority="high",
    tags=["development", "feature"]
)
```

### 2. Pattern Analyzer (`pattern_analyzer.py`)
**Purpose:** Analyze user interaction patterns to identify behavioral trends

**Features:**
- Temporal pattern analysis (peak hours, days)
- Task pattern analysis (priorities, complexity)
- Feedback pattern analysis (sentiment)
- Preference pattern analysis
- Behavioral insights generation

**Usage:**
```python
from pattern_analyzer import get_analyzer

analyzer = get_analyzer()
patterns = analyzer.identify_behavioral_patterns()
```

### 3. Success Tracker (`success_tracker.py`)
**Purpose:** Track task outcomes to learn from successes and failures

**Features:**
- Record successes, failures, and partial successes
- Calculate success rates
- Identify common failure patterns
- Track successful approaches
- Performance trend analysis
- Automated learning from outcomes

**Usage:**
```python
from success_tracker import get_tracker

tracker = get_tracker()
tracker.record_success(
    task_id="task_001",
    task_description="Deploy feature",
    execution_time=120.5,
    approach="automated_deployment"
)
```

### 4. Preference Learner (`preference_learner.py`)
**Purpose:** Learn and apply user preferences from interactions

**Features:**
- Explicit preference setting
- Pattern-based preference inference
- Communication style learning
- Workflow preference learning
- Timing preference learning
- Confidence tracking
- Preference export/import

**Usage:**
```python
from preference_learner import get_learner

learner = get_learner()
learner.set_preference("communication", "style", "concise")
style = learner.get_preference("communication", "style")
```

## Data Storage

All modules store data in `/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data/`:

- `interactions/` - User interaction logs
- `patterns/` - Identified behavioral patterns
- `outcomes/` - Task outcome records and learnings
- `preferences/` - User preferences and history

## Integration

These modules work together to create a comprehensive learning system:

1. **Interaction Monitor** captures all user interactions
2. **Pattern Analyzer** identifies trends and patterns
3. **Success Tracker** learns from task outcomes
4. **Preference Learner** adapts to user preferences

The orchestrator coordinates these modules to continuously improve system performance.

## Testing

Each module includes a `__main__` block for standalone testing:

```bash
python3 interaction_monitor.py
python3 pattern_analyzer.py
python3 success_tracker.py
python3 preference_learner.py
```

## Future Enhancements

- Real-time pattern detection
- Predictive preference inference
- Cross-module learning integration
- Advanced ML-based pattern recognition
- Automated A/B testing of approaches
