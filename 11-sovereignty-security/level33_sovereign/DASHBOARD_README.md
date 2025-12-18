# Level 33 Web Dashboard

## 🎯 Overview

Comprehensive web interface for monitoring and controlling the Level 33 Sovereign Architecture.

## 🚀 Quick Start

```bash
cd ~/level33_sovereign
make dashboard
```

Open browser to: **http://localhost:8000**

## 📊 Features

### 1. Dashboard Home
- Real-time system stats (CPU, Memory, Disk)
- Ollama service status
- Recent activities feed
- Quick action buttons
- 24-hour metrics chart

### 2. Activities Monitor
- Complete activity log
- Filter and search
- Status tracking
- Duration metrics

### 3. Metrics Visualization
- Performance graphs
- Time-series charts
- Custom date ranges
- Multiple metrics overlay

### 4. Automation Control
- Visual automation cards
- One-click execution
- Run statistics
- Success/failure tracking

### 5. LLM Interaction Logs
- Query history
- Token usage tracking
- Response times
- Success rates

### 6. Configuration Viewer
- Current settings display
- YAML format
- Sanitized sensitive data

### 7. System Health
- Health check status
- Database connectivity
- Service monitoring
- Resource warnings

## 🏗️ Architecture

### Backend: FastAPI
- RESTful API endpoints
- WebSocket real-time updates
- Database integration
- Auto-generated docs at `/docs`

### Frontend: HTML + JavaScript
- Single-page application
- Chart.js visualizations
- Dark theme
- Responsive design

## 📦 Installation

```bash
# Install dependencies
pip install fastapi uvicorn websockets psutil

# Or use requirements file
pip install -r requirements-dashboard.txt
```

## 🔌 API Endpoints

```
GET  /                          - Dashboard home
GET  /api/status                - System status
GET  /api/activities            - Activity log
GET  /api/metrics               - Performance metrics
GET  /api/automations           - List automations
POST /api/automations/{id}/run  - Run automation
GET  /api/llm/interactions      - LLM history
GET  /api/config                - Configuration
GET  /api/health                - Health check
WS   /ws                        - WebSocket
```

**API Docs:** http://localhost:8000/docs

## 🎨 Color Scheme

- Primary: #2563eb (Blue)
- Success: #10b981 (Green)
- Warning: #f59e0b (Orange)
- Error: #ef4444 (Red)
- Background: #1f2937 (Dark Gray)
- Text: #f3f4f6 (Light Gray)

## 🔌 Real-Time Updates

- WebSocket connection for live data
- Auto-refresh every 30 seconds
- Manual refresh button
- Automatic reconnection

## 🐛 Troubleshooting

### Port Already in Use
```bash
lsof -i :8000
kill -9 <PID>
```

### Missing Dependencies
```bash
pip install fastapi uvicorn websockets psutil
```

### No Data Showing
```bash
# Run automations to generate data
make health
make workspace
```

## 📈 Usage Examples

### Monitor System
1. Open http://localhost:8000
2. View real-time stats
3. Check health status

### Run Automation
1. Click "Automations"
2. Select automation
3. Click "Run"
4. Check "Activities" for status

### View Metrics
1. Click "Metrics"
2. View performance graphs
3. Analyze trends

## 🚀 Advanced

### Custom Metrics
```python
from core import get_database
db = get_database()
db.log_metric("custom_metric", 42.5, "units")
```

### API Integration
```bash
curl http://localhost:8000/api/status
curl -X POST http://localhost:8000/api/automations/workspace_launcher/run
```

## 📚 Documentation

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- This README: DASHBOARD_README.md

---

**Status:** ✅ Production Ready
**Version:** 1.0.0
**Port:** 8000
