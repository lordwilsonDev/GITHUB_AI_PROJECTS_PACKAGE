# AI Orchestration System Components

## Core Infrastructure Components

### 1. Temporal - Workflow Orchestration Engine
**Purpose**: Durable workflow execution and crash recovery

**Key Features**:
- Persistent workflow state across failures
- Automatic retry and recovery
- Long-running workflow support (days, weeks, months)
- Event-driven architecture
- Signals & Queries for inter-agent communication
- Complete audit trail and observability

**Docker Image**: `temporalio/auto-setup:latest`
**Dependencies**: PostgreSQL database
**Ports**:
- 7233: gRPC API
- 8080: Web UI (via temporal-ui)

**Use Cases**:
- Orchestrating multi-step agent workflows
- Managing agent task delegation
- Ensuring workflow completion despite failures
- Coordinating 620 agents across complex tasks

---

### 2. Ray - Distributed Computing Framework
**Purpose**: Parallel task processing and distributed execution

**Key Features**:
- Horizontal scaling across multiple nodes
- Efficient resource allocation
- Task parallelization
- Shared memory for fast data access
- Built-in dashboard for monitoring
- Python-native API

**Docker Image**: `rayproject/ray:latest`
**Architecture**: Head node + Worker nodes
**Ports**:
- 6379: Redis (cluster coordination)
- 8265: Dashboard
- 10001: Client connection port

**Use Cases**:
- Distributing 620 agents across worker nodes
- Parallel execution of agent tasks
- Resource management and load balancing
- High-performance computing for AI workloads

**Scaling**: 
- 10 worker nodes × 62 agents each = 620 total agents
- Each worker: 4 CPUs, 4GB RAM
- Shared memory (shm_size: 2g) for efficiency

---

### 3. Nomad - Agent Lifecycle Management
**Purpose**: Container orchestration and agent deployment

**Key Features**:
- Automatic agent restart on failure
- Resource allocation and scheduling
- Health monitoring
- Integration with Consul for service discovery
- Docker driver support
- Job scheduling and management

**Docker Image**: `hashicorp/nomad:latest`
**Ports**:
- 4646: HTTP API & Web UI
- 4647: RPC
- 4648: Serf (gossip protocol)

**Use Cases**:
- Managing agent lifecycle (start, stop, restart)
- Ensuring agents auto-recover from crashes
- Scheduling agent tasks
- Resource allocation across agents

---

### 4. NATS - High-Speed Messaging System
**Purpose**: Inter-agent communication and message passing

**Key Features**:
- Pub/Sub messaging
- Request/Reply patterns
- JetStream for message persistence
- Extremely low latency (microseconds)
- Lightweight and efficient
- Horizontal scalability

**Docker Image**: `nats:latest`
**Ports**:
- 4222: Client connections
- 8222: Monitoring/metrics
- 6222: Cluster routes

**Use Cases**:
- Real-time agent-to-agent communication
- Event broadcasting across agent network
- Task queue management
- Coordination signals between agents

**Configuration**: JetStream enabled for durable messaging

---

### 5. Consul - Service Discovery & Configuration
**Purpose**: Service registry and health monitoring

**Key Features**:
- Service discovery and registration
- Health checking
- Key/value store for configuration
- DNS interface
- Multi-datacenter support
- Integration with Nomad

**Docker Image**: `consul:1.12`
**Ports**:
- 8500: HTTP API & Web UI
- 8600: DNS

**Use Cases**:
- Agent registry and discovery
- Health monitoring of all 620 agents
- Configuration management
- Service mesh for agent communication

---

## Supporting Components

### 6. PostgreSQL - Database
**Purpose**: Persistent storage for Temporal workflows

**Docker Image**: `postgres:13`
**Configuration**:
- User: temporal
- Password: temporal
- Stores workflow history and state

---

### 7. Prometheus - Metrics Collection
**Purpose**: System monitoring and metrics aggregation

**Docker Image**: `prom/prometheus:latest`
**Port**: 9090

**Monitors**:
- Consul health
- NATS performance
- Ray cluster status
- Nomad job metrics

---

### 8. Grafana - Visualization Dashboard
**Purpose**: Real-time monitoring and alerting

**Docker Image**: `grafana/grafana:latest`
**Port**: 3000
**Default Credentials**: admin/admin

**Dashboards**:
- Agent performance metrics
- System resource usage
- Workflow execution status
- Message throughput

---

## Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User/Application                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │    Temporal    │ ◄─── Workflow Orchestration
              │  (Coordinator) │
              └────────┬───────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌────────┐   ┌─────────┐   ┌─────────┐
    │  Ray   │   │  Nomad  │   │  NATS   │
    │ (Exec) │   │ (Mgmt)  │   │  (Msg)  │
    └────┬───┘   └────┬────┘   └────┬────┘
         │            │             │
         └────────────┼─────────────┘
                      ▼
              ┌───────────────┐
              │    Consul     │ ◄─── Service Discovery
              │  (Registry)   │
              └───────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
    [Agent 1]    [Agent 2]  ... [Agent 620]
```

## System Requirements

**Minimum**:
- Docker Desktop
- 8GB RAM
- 20GB disk space
- macOS (optimized for Mac Mini)

**Recommended**:
- 16GB RAM
- 50GB disk space
- SSD storage

**Resource Usage**:
- Total system: < 2GB RAM
- Cost: Pennies per day (24/7 operation)
- Highly efficient for 620 agents

## Deployment Architecture

**Network**: Custom bridge network (172.20.0.0/16)
**Volumes**: Persistent storage for:
- Consul data
- PostgreSQL data
- Nomad data
- Prometheus metrics
- Grafana dashboards

**Restart Policy**: All services set to `always` for 24/7 operation

## Scalability

**Current Configuration**:
- 10 Ray worker nodes
- 62 agents per worker
- Total: 620 simultaneous agents

**To Scale**:
1. Increase Ray worker replicas in docker-compose.yml
2. Adjust CPU/memory limits per worker
3. Monitor with Prometheus/Grafana
4. Scale horizontally as needed

## Security Considerations

- All services run in isolated Docker network
- No external exposure except defined ports
- Passwords configurable via environment variables
- Privileged mode only for Nomad (required for Docker driver)

## Next Steps

1. ✅ Components identified and documented
2. ⏭️ Deploy system with `docker-compose up -d`
3. ⏭️ Verify all services are running
4. ⏭️ Test basic workflow
5. ⏭️ Scale to full 620 agents
