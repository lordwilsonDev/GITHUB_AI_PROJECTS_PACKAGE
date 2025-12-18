# 📊 Metrics Tracking System
## Self-Evolving AI Ecosystem

---

## Overview

Comprehensive metrics tracking system with detailed monitoring of system performance and user satisfaction. Provides both basic and advanced metrics collection with analytics capabilities.

---

## Components

### 1. Basic Metrics Collector (`metrics_collector.py`)

Core metrics collection for:
- Performance metrics
- Learning metrics
- Optimization metrics

### 2. Advanced Metrics Tracker (`advanced_metrics.py`)

Detailed tracking for:
- **System Performance**: Response times, throughput, latency
- **User Satisfaction**: Satisfaction scores, feedback, ratings
- **Feature Usage**: Usage patterns, success rates, durations
- **Learning Effectiveness**: Accuracy, confidence, improvement rates
- **Optimization Impact**: Before/after comparisons, user impact
- **Resource Utilization**: CPU, memory, storage usage
- **Error Metrics**: Error rates, recovery success, severity

---

## Usage

### Basic Metrics

```python
from shared.metrics import get_metrics_collector

metrics = get_metrics_collector()

# Record performance metric
metrics.record_performance_metric(
    'learning-engine',
    'response_time_ms',
    125.5,
    {'algorithm': 'pattern_recognition_v2'}
)

# Record learning metric
metrics.record_learning_metric(
    'learning-engine',
    'accuracy',
    0.92,
    {'training_samples': 1000}
)

# Get statistics
stats = metrics.get_metric_statistics(
    'learning-engine',
    'accuracy',
    hours=24
)
```

### Advanced Metrics

```python
from shared.metrics import get_advanced_metrics

advanced = get_advanced_metrics()

# Record system performance
advanced.record_performance_metric(
    feature="learning-engine",
    metric_category="response_time",
    metric_name="pattern_recognition_ms",
    value=125.5,
    unit="milliseconds",
    context="production"
)

# Record user satisfaction
advanced.record_satisfaction(
    feature="learning-engine",
    satisfaction_type="accuracy",
    score=0.92,  # 0.0 to 1.0 or 1-5 scale
    feedback="Pattern recognition is very accurate",
    interaction_id="interaction_001"
)

# Record feature usage
advanced.record_feature_usage(
    feature="learning-engine",
    action="recognize_pattern",
    duration_ms=125.5,
    success=True,
    user_context="morning_session"
)

# Record learning effectiveness
advanced.record_learning_effectiveness(
    feature="learning-engine",
    learning_type="pattern_recognition",
    accuracy=0.92,
    confidence=0.88,
    sample_size=1000,
    improvement_rate=0.05
)

# Record optimization impact
advanced.record_optimization_impact(
    feature="process-optimization",
    optimization_id="opt_001",
    impact_category="task_completion_time",
    before_value=45.2,
    after_value=38.7,
    user_impact_score=0.85
)

# Record resource utilization
advanced.record_resource_utilization(
    resource_type="memory",
    resource_name="learning_engine_cache",
    utilization_percent=65.5,
    allocated=1024.0,
    used=670.0,
    unit="MB"
)

# Record errors
advanced.record_error(
    feature="learning-engine",
    error_type="PatternRecognitionError",
    error_severity="warning",
    error_message="Low confidence pattern detected",
    recovery_attempted=True,
    recovery_successful=True,
    impact_level="low"
)
```

### Get Metrics

```python
# Get performance metrics
perf_metrics = advanced.get_performance_metrics(
    feature="learning-engine",
    metric_category="response_time",
    hours=24,
    limit=1000
)

# Get satisfaction statistics
sat_stats = advanced.get_satisfaction_metrics(
    feature="learning-engine",
    satisfaction_type="accuracy",
    hours=24
)
print(f"Average satisfaction: {sat_stats['avg_score']:.2f}")
print(f"Satisfaction rate: {sat_stats['satisfaction_rate']:.2%}")

# Get feature usage stats
usage_stats = advanced.get_feature_usage_stats(
    feature="learning-engine",
    hours=24
)
print(f"Total usage: {usage_stats['total_usage']}")
print(f"Success rate: {usage_stats['success_rate']:.2%}")
print(f"Avg duration: {usage_stats['avg_duration_ms']:.2f}ms")

# Get error statistics
error_stats = advanced.get_error_stats(
    feature="learning-engine",
    hours=24
)
print(f"Total errors: {error_stats['total_errors']}")
print(f"Recovery rate: {error_stats['recovery_rate']:.2%}")
```

### Comprehensive Dashboard

```python
# Get complete dashboard for a feature
dashboard = advanced.get_comprehensive_dashboard(
    feature="learning-engine",
    hours=24
)

print(json.dumps(dashboard, indent=2))

# Dashboard includes:
# - Performance metrics by category
# - User satisfaction statistics
# - Feature usage statistics
# - Error statistics
```

### Daily Aggregation

```python
# Aggregate metrics for analysis
advanced.aggregate_daily_metrics()  # Today
advanced.aggregate_daily_metrics(date="2025-12-14")  # Specific date
```

---

## Metric Categories

### System Performance
- **response_time**: API/function response times
- **throughput**: Requests/operations per second
- **latency**: Network/processing latency
- **cpu_usage**: CPU utilization
- **memory_usage**: Memory consumption
- **disk_io**: Disk I/O operations

### User Satisfaction
- **task_completion**: Task completion satisfaction
- **ease_of_use**: Usability satisfaction
- **accuracy**: Result accuracy satisfaction
- **speed**: Performance satisfaction
- **overall**: Overall satisfaction

### Feature Usage
- **action**: Specific feature actions
- **duration_ms**: Action duration
- **success**: Success/failure status
- **user_context**: User context information

### Learning Effectiveness
- **pattern_recognition**: Pattern learning accuracy
- **prediction**: Prediction accuracy
- **classification**: Classification accuracy
- **improvement_rate**: Learning improvement over time

### Optimization Impact
- **task_completion_time**: Time improvements
- **resource_usage**: Resource optimization
- **accuracy**: Accuracy improvements
- **user_experience**: UX improvements

### Resource Utilization
- **cpu**: CPU usage
- **memory**: Memory usage
- **disk**: Disk usage
- **network**: Network usage
- **cache**: Cache utilization

### Error Metrics
- **error_type**: Type of error
- **error_severity**: critical, error, warning, info
- **recovery_attempted**: Whether recovery was tried
- **recovery_successful**: Whether recovery succeeded
- **impact_level**: high, medium, low

---

## Database Schema

### System Performance Table
```sql
CREATE TABLE system_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    feature TEXT NOT NULL,
    metric_category TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    context TEXT,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### User Satisfaction Table
```sql
CREATE TABLE user_satisfaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    feature TEXT NOT NULL,
    satisfaction_type TEXT NOT NULL,
    score REAL NOT NULL,
    feedback TEXT,
    interaction_id TEXT,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### Feature Usage Table
```sql
CREATE TABLE feature_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    feature TEXT NOT NULL,
    action TEXT NOT NULL,
    duration_ms REAL,
    success BOOLEAN,
    error_type TEXT,
    user_context TEXT,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### Daily Aggregates Table
```sql
CREATE TABLE daily_aggregates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    feature TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    avg_value REAL,
    min_value REAL,
    max_value REAL,
    stddev REAL,
    count INTEGER,
    percentile_50 REAL,
    percentile_95 REAL,
    percentile_99 REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, feature, metric_type, metric_name)
)
```

---

## Best Practices

### 1. Metric Recording
- Record metrics at appropriate granularity
- Include relevant context and metadata
- Use consistent naming conventions
- Record both success and failure cases

### 2. Performance Monitoring
- Track response times for all operations
- Monitor resource utilization continuously
- Set up alerts for threshold violations
- Analyze trends over time

### 3. User Satisfaction
- Collect satisfaction scores regularly
- Gather qualitative feedback
- Link satisfaction to specific interactions
- Track satisfaction trends

### 4. Error Tracking
- Record all errors with context
- Track recovery attempts and success
- Categorize by severity
- Monitor error trends

### 5. Data Analysis
- Aggregate metrics daily for trends
- Calculate percentiles for SLAs
- Compare metrics across features
- Identify correlations

---

## Integration Examples

### With Learning Engine
```python
from shared.metrics import get_advanced_metrics

metrics = get_advanced_metrics()

# Track pattern recognition
start = time.time()
pattern = recognize_pattern(data)
duration = (time.time() - start) * 1000

metrics.record_performance_metric(
    feature="learning-engine",
    metric_category="response_time",
    metric_name="pattern_recognition_ms",
    value=duration,
    unit="milliseconds"
)

metrics.record_learning_effectiveness(
    feature="learning-engine",
    learning_type="pattern_recognition",
    accuracy=pattern.accuracy,
    confidence=pattern.confidence,
    sample_size=len(data)
)
```

### With Optimization System
```python
# Before optimization
before_time = measure_task_time()

# Apply optimization
apply_optimization(opt_id)

# After optimization
after_time = measure_task_time()

metrics.record_optimization_impact(
    feature="process-optimization",
    optimization_id=opt_id,
    impact_category="task_completion_time",
    before_value=before_time,
    after_value=after_time,
    user_impact_score=calculate_user_impact()
)
```

---

## Monitoring & Alerts

### Set Up Monitoring
```python
# Get dashboard periodically
import schedule

def monitor_system():
    dashboard = advanced.get_comprehensive_dashboard(hours=1)
    
    # Check thresholds
    if dashboard['errors']['total_errors'] > 10:
        send_alert("High error rate detected")
    
    if dashboard['satisfaction']['avg_score'] < 0.7:
        send_alert("Low user satisfaction")
    
    if dashboard['performance']['categories'].get('response_time', {}).get('avg', 0) > 1000:
        send_alert("High response times")

schedule.every(5).minutes.do(monitor_system)
```

---

**Created:** December 15, 2025
**Status:** Production Ready
**Version:** 1.0.0
