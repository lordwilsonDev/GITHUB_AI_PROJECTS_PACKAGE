# AI Agent Orchestration - Docker Setup

## System Status

### Docker Compose Configuration Created
Location: `/Users/lordwilson/ai-orchestration/docker-compose.yml`

### Services Configured

1. **PostgreSQL** (Port 5432)
   - Database for Temporal persistence
   - Auto-restart enabled

2. **Temporal Server** (Ports 7233, 8080)
   - Workflow orchestration engine
   - Web UI: http://localhost:8080
   - gRPC API: localhost:7233

3. **NATS** (Ports 4222, 8222, 6222)
   - Message bus for agent communication
   - JetStream enabled for persistence
   - Monitoring UI: http://localhost:8222

4. **Consul** (Ports 8500, 8600)
   - Service discovery and health checks
   - Web UI: http://localhost:8500

5. **Ray** (Ports 6379, 8265)
   - Distributed task processing
   - Dashboard: http://localhost:8265
   - Manages 620 agent workers

## Quick Start Commands

### Start All Services
```bash
cd ~/ai-orchestration
docker-compose up -d
```

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f temporal
docker-compose logs -f nats
docker-compose logs -f ray-head
```

### Stop All Services
```bash
docker-compose down
```

### Stop and Remove Volumes (Clean Reset)
```bash
docker-compose down -v
```

## Service URLs

- **Temporal Web UI**: http://localhost:8080
- **NATS Monitoring**: http://localhost:8222
- **Consul UI**: http://localhost:8500
- **Ray Dashboard**: http://localhost:8265

## Resource Usage

Expected RAM usage:
- PostgreSQL: ~200MB
- Temporal: ~300MB
- NATS: ~50MB
- Consul: ~150MB
- Ray: ~600MB
- **Total**: ~1.3GB (well under 2GB limit)

## Verification Steps

1. Start services: `docker-compose up -d`
2. Wait 30 seconds for initialization
3. Check all containers running: `docker-compose ps`
4. Access Temporal UI: http://localhost:8080
5. Access Ray Dashboard: http://localhost:8265
6. Access Consul UI: http://localhost:8500

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]
```

### Port already in use
```bash
# Find process using port
lsof -i :8080

# Kill process or change port in docker-compose.yml
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
```

## Next Steps

1. ✅ Docker Compose file created
2. ⏳ Start Docker containers
3. ⏳ Verify all services running
4. ⏳ Deploy agent framework
5. ⏳ Test with sample workflow
