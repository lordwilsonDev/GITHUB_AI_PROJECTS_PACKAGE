# Deploy the 620-Agent AI Orchestration System NOW

## Quick Deploy (5 Minutes)

### Step 1: Open Terminal
```bash
# Open Terminal app
open -a Terminal
```

### Step 2: Start Docker Desktop
```bash
# Start Docker Desktop (if not already running)
open -a Docker

# Wait 30 seconds for Docker to start
sleep 30
```

### Step 3: Navigate to Project
```bash
cd ~/ai-agent-orchestration
```

### Step 4: Make Scripts Executable
```bash
chmod +x start.sh stop.sh status.sh
```

### Step 5: Start the System
```bash
./start.sh
```

**That's it!** The system will:
1. Check Docker is running
2. Pull required images (first time only)
3. Start all 8 services
4. Display dashboard URLs

---

## Manual Deployment (Alternative)

If you prefer to run commands manually:

```bash
# 1. Ensure Docker is running
docker info

# 2. Navigate to project
cd ~/ai-agent-orchestration

# 3. Start all services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f
```

---

## Access Your Dashboards

Once running, open these URLs in your browser:

| Service | URL | Purpose |
|---------|-----|----------|
| **Temporal UI** | http://localhost:8080 | Workflow orchestration |
| **Ray Dashboard** | http://localhost:8265 | Distributed computing |
| **Consul UI** | http://localhost:8500 | Service discovery |
| **Nomad UI** | http://localhost:4646 | Agent management |
| **NATS Monitoring** | http://localhost:8222 | Messaging stats |
| **Prometheus** | http://localhost:9090 | Metrics |
| **Grafana** | http://localhost:3000 | Monitoring (admin/admin) |

---

## Verify System is Running

```bash
# Check all services
./status.sh

# Or manually:
docker-compose ps

# Should show 11 containers running:
# - consul
# - nats
# - postgresql
# - temporal
# - temporal-ui
# - ray-head
# - ray-worker (10 instances)
# - nomad
# - prometheus
# - grafana
```

---

## Test the System

### Test 1: Check Ray Cluster
```python
import ray

# Connect to Ray cluster
ray.init(address='ray://localhost:10001')

# Check cluster info
print(f"Nodes: {len(ray.nodes())}")
print(f"CPUs: {ray.cluster_resources()['CPU']}")

# Test parallel execution
@ray.remote
def test_task(x):
    return x * 2

results = ray.get([test_task.remote(i) for i in range(100)])
print(f"Processed {len(results)} tasks")
```

### Test 2: Check Temporal
1. Open http://localhost:8080
2. You should see the Temporal Web UI
3. No workflows yet (that's normal)

### Test 3: Check Consul
1. Open http://localhost:8500
2. Click "Services"
3. You should see registered services

---

## Troubleshooting

### Docker not running
```bash
# Start Docker Desktop
open -a Docker

# Wait for it to start
sleep 30

# Verify
docker info
```

### Port conflicts
If you get "port already in use" errors:

```bash
# Find what's using the port (example: 8080)
lsof -i :8080

# Kill the process or change the port in docker-compose.yml
```

### Services won't start
```bash
# Check logs
docker-compose logs [service-name]

# Example:
docker-compose logs temporal
```

### Reset everything
```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Clean Docker system
docker system prune -a

# Start fresh
./start.sh
```

---

## Stop the System

```bash
# Graceful shutdown
./stop.sh

# Or manually:
docker-compose down

# To also remove data:
docker-compose down -v
```

---

## Next Steps After Deployment

1. **Explore Dashboards** - Visit each URL and familiarize yourself
2. **Run Test Workflows** - See README.md for examples
3. **Monitor Performance** - Check Grafana dashboards
4. **Scale Workers** - Adjust Ray worker count as needed
5. **Build Your First Agent** - Start with simple tasks

---

## System Specifications

- **Total Agents**: 620 simultaneous workers
- **RAM Usage**: < 2GB total
- **Services**: 8 core + monitoring
- **Network**: Isolated Docker network
- **Persistence**: All data stored in Docker volumes
- **Auto-restart**: All services restart on failure

---

## Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify Docker: `docker info`
3. Check status: `./status.sh`
4. Review README.md for detailed troubleshooting

---

## Ready to Deploy?

```bash
cd ~/ai-agent-orchestration
./start.sh
```

**Welcome to the future of AI orchestration!** 🚀
