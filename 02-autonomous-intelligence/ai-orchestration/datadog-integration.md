# Datadog Integration for AI Agent Orchestration

Unified observability across infrastructure metrics, APM traces, and AI-specific telemetry.

## Prerequisites

- Datadog Agent installed (visible in Applications list)
- Datadog API key configured
- Services running (Nomad, NATS, Consul, Temporal, Ray)

## Integration Setup

### 1. Ray Integration

Ray exposes OpenMetrics endpoint on port 8080 with official Datadog integration.

**Enable Ray metrics:**
```python
import ray

ray.init(
    _system_config={
        "metrics_export_port": 8080,
        "enable_timeline": True,
    }
)
```

**Configure Datadog Agent:**
```yaml
# /opt/datadog-agent/etc/conf.d/ray.d/conf.yaml
init_config:

instances:
  - openmetrics_endpoint: http://localhost:8080/metrics
    namespace: "ray"
    metrics:
      - ray_*
```

**Restart Datadog Agent:**
```bash
sudo launchctl stop com.datadoghq.agent
sudo launchctl start com.datadoghq.agent
```

### 2. NATS Integration

NATS provides Prometheus-compatible metrics endpoint.

**Enable NATS monitoring:**
```bash
# Start NATS with monitoring enabled
nats-server -js -m 8222
```

**Configure Datadog Agent:**
```yaml
# /opt/datadog-agent/etc/conf.d/nats.d/conf.yaml
init_config:

instances:
  - url: http://localhost:8222
    tags:
      - service:nats
      - env:production
```

### 3. Consul Integration

Official Datadog-Consul integration available.

**Configure Datadog Agent:**
```yaml
# /opt/datadog-agent/etc/conf.d/consul.d/conf.yaml
init_config:

instances:
  - url: http://localhost:8500
    catalog_checks: true
    new_leader_checks: true
    tags:
      - service:consul
```

### 4. Nomad Integration

Nomad exposes metrics via telemetry endpoint.

**Enable Nomad telemetry:**
```hcl
# nomad-config.hcl
telemetry {
  publish_allocation_metrics = true
  publish_node_metrics       = true
  prometheus_metrics         = true
}
```

**Configure Datadog Agent:**
```yaml
# /opt/datadog-agent/etc/conf.d/nomad.d/conf.yaml
init_config:

instances:
  - url: http://localhost:4646
    tags:
      - service:nomad
```

### 5. Temporal Integration

Temporal provides Prometheus metrics.

**Configure Datadog Agent:**
```yaml
# /opt/datadog-agent/etc/conf.d/temporal.d/conf.yaml
init_config:

instances:
  - prometheus_url: http://localhost:8000/metrics
    namespace: "temporal"
    metrics:
      - temporal_*
    tags:
      - service:temporal
```

## AI-Specific Observability

### LLM Observability with Datadog

**Install Datadog LLM Observability:**
```bash
pip3 install ddtrace
```

**Instrument LangGraph workflows:**
```python
from ddtrace.llmobs import LLMObs

# Initialize LLM Observability
LLMObs.enable(
    ml_app="ai-agent-orchestration",
    api_key="<DATADOG_API_KEY>",
    site="datadoghq.com",
    env="production",
)

# Instrument workflow
from langgraph.graph import StateGraph

workflow = StateGraph(AgentState)
# LLMObs automatically traces LangGraph executions
```

**Track custom metrics:**
```python
from ddtrace import tracer
from datadog import statsd

# Token usage
statsd.histogram('ai.agent.tokens.input', input_tokens)
statsd.histogram('ai.agent.tokens.output', output_tokens)

# Task completion
statsd.increment('ai.agent.tasks.completed', tags=['agent_id:001'])

# Hallucination detection
statsd.increment('ai.agent.hallucinations', tags=['severity:high'])

# Tool selection
statsd.increment('ai.agent.tool.selected', tags=['tool:search'])
```

### Open-Source Alternative: Langfuse

**Install Langfuse:**
```bash
pip3 install langfuse
```

**Integrate with LangGraph:**
```python
from langfuse.callback import CallbackHandler
from langgraph.graph import StateGraph

langfuse_handler = CallbackHandler(
    public_key="<PUBLIC_KEY>",
    secret_key="<SECRET_KEY>",
    host="https://cloud.langfuse.com"
)

# Add to workflow config
config = {
    "callbacks": [langfuse_handler],
    "configurable": {"thread_id": "agent-001"}
}

result = workflow.invoke(initial_state, config)
```

## Critical Metrics to Monitor

### Infrastructure Metrics

**Ray:**
- `ray.cluster.active_nodes` - Cluster health
- `ray.object_store.memory_used` - Memory pressure
- `ray.tasks.running` - Task queue depth
- `ray.actors.alive` - Agent health

**NATS:**
- `nats.jetstream.messages.stored` - Message backlog
- `nats.jetstream.consumers.active` - Consumer health
- `nats.connections.total` - Connection pool
- `nats.messages.in_rate` - Throughput

**Nomad:**
- `nomad.client.allocations.running` - Active agents
- `nomad.client.host.memory.used` - Memory usage
- `nomad.client.host.cpu.total` - CPU usage
- `nomad.nomad.job.eval.wait` - Scheduling latency

**Consul:**
- `consul.catalog.services` - Service registry
- `consul.health.service.query` - Health check latency
- `consul.serf.member.flap` - Network stability

**Temporal:**
- `temporal.workflow.running` - Active workflows
- `temporal.workflow.failed` - Failure rate
- `temporal.activity.execution.latency` - Activity performance
- `temporal.workflow.task_queue.depth` - Queue backlog

### AI-Specific Metrics

**Token Usage (explains 80% of performance variance):**
- Input tokens per request
- Output tokens per request
- Total tokens per agent
- Cost per agent

**Agent Performance:**
- Task completion rate
- Average task duration
- Success rate by task type
- Retry rate

**Safety Metrics:**
- Hallucination detection rate
- Human approval requests
- Modification rejections
- Safety gate triggers

**Tool Usage:**
- Tool selection frequency
- Tool execution latency
- Tool failure rate
- Tool cost

## Dashboard Configuration

### Recommended Dashboards

1. **Infrastructure Overview**
   - Ray cluster health
   - NATS message throughput
   - Nomad allocation status
   - Consul service health
   - Temporal workflow status

2. **AI Agent Performance**
   - Token usage trends
   - Task completion rates
   - Agent decision paths
   - Tool selection patterns

3. **Safety & Compliance**
   - Hallucination rates
   - Human approval queue
   - Modification audit log
   - Safety gate triggers

4. **Resource Utilization**
   - Memory usage by agent
   - CPU usage by agent
   - GPU utilization (if applicable)
   - Network throughput

### Alert Configuration

**Critical Alerts:**
```yaml
# High hallucination rate
- name: "High Hallucination Rate"
  query: "avg(last_5m):sum:ai.agent.hallucinations{*} > 10"
  message: "Hallucination rate exceeded threshold"
  priority: P1

# Workflow failures
- name: "Temporal Workflow Failures"
  query: "avg(last_5m):sum:temporal.workflow.failed{*} > 5"
  message: "Multiple workflow failures detected"
  priority: P1

# Memory pressure
- name: "Ray Object Store Memory Pressure"
  query: "avg(last_5m):ray.object_store.memory_used / ray.object_store.memory_total > 0.9"
  message: "Ray object store near capacity"
  priority: P2

# Message backlog
- name: "NATS Message Backlog"
  query: "avg(last_5m):sum:nats.jetstream.messages.stored{*} > 10000"
  message: "Large message backlog in NATS"
  priority: P2
```

## OpenTelemetry Integration

For framework-agnostic telemetry:

**Install OpenTelemetry:**
```bash
pip3 install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
```

**Configure OTLP exporter:**
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Set up tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure OTLP exporter (sends to Datadog)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",  # Datadog Agent OTLP endpoint
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

# Instrument code
with tracer.start_as_current_span("agent_task"):
    # Agent work here
    pass
```

## Verification

**Check Datadog Agent status:**
```bash
datadog-agent status
```

**Verify integrations:**
```bash
datadog-agent check ray
datadog-agent check nats
datadog-agent check consul
datadog-agent check nomad
```

**View metrics in Datadog:**
1. Navigate to Metrics Explorer
2. Search for `ray.*`, `nats.*`, `consul.*`, `nomad.*`, `temporal.*`
3. Create custom dashboards
4. Set up alerts

## Cost Optimization

**Reduce metric cardinality:**
- Limit tag combinations
- Sample high-frequency metrics
- Use metric aggregation

**Optimize trace sampling:**
```python
from ddtrace import tracer

# Sample 10% of traces
tracer.configure(
    sampler={
        'sample_rate': 0.1,
    }
)
```

**Use metric summaries:**
```python
# Instead of individual events
statsd.histogram('ai.agent.task.duration', duration)

# Use summaries for high-volume metrics
statsd.distribution('ai.agent.tokens', token_count)
```

## Resources

- [Datadog Ray Integration](https://docs.datadoghq.com/integrations/ray/)
- [Datadog LLM Observability](https://docs.datadoghq.com/llm_observability/)
- [OpenTelemetry GenAI Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Langfuse Documentation](https://langfuse.com/docs)

---

**Note:** Datadog Agent must be running for integrations to work. Check status with `datadog-agent status`.
