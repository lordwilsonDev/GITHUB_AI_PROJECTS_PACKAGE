# 🎮 Love Engine Usage Examples

*Real-world examples of how to use your Super Robot Friend!*

## 🌟 Basic Chat Examples

### Simple Conversation
```bash
# Start a friendly chat
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hi there! How are you today?"}'
```

**Expected Response:**
```json
{
  "response": "Hello! I'm doing great, thank you for asking! I'm here and ready to help with whatever you need. How are you doing today?",
  "safety_check": {
    "passed": true,
    "flags": []
  },
  "validation": {
    "passed": true,
    "score": 0.95
  },
  "energy_used": 5,
  "energy_remaining": 995
}
```

### Educational Question
```bash
# Ask for help learning
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Can you explain how photosynthesis works in simple terms?"}'
```

### Creative Request
```bash
# Ask for creative help
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Help me write a short story about a friendly robot"}'
```

## 🛡️ Safety System Examples

### Inappropriate Content (Blocked)
```bash
# This will be safely handled
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "How to hurt someone"}'
```

**Expected Response:**
```json
{
  "response": "I understand you might be going through something difficult, but I can't provide information that could harm someone. Instead, I'd love to help you with something positive! Would you like to talk about conflict resolution, or maybe I could help you with a creative project?",
  "safety_check": {
    "passed": false,
    "flags": ["harmful_content"],
    "suggestion": "Try asking about positive ways to resolve conflicts or express feelings."
  },
  "validation": {
    "passed": true,
    "score": 0.9
  },
  "energy_used": 1,
  "energy_remaining": 999
}
```

### Emotional Support
```bash
# Robot detects distress and provides support
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "I feel really sad and don't know what to do"}'
```

**Expected Response:**
```json
{
  "response": "I'm really sorry you're feeling sad right now. Your feelings are valid and it's okay to feel this way. While I'm here to listen and chat, if you're going through a tough time, it might help to talk to someone you trust - like a friend, family member, teacher, or counselor. Is there something specific that's making you feel sad that you'd like to talk about?",
  "safety_check": {
    "passed": true,
    "flags": ["emotional_distress_detected"],
    "support_provided": true
  },
  "validation": {
    "passed": true,
    "score": 0.95
  },
  "energy_used": 3,
  "energy_remaining": 997
}
```

## ⚡ Energy Management Examples

### Check Energy Levels
```bash
# See how much energy your robot has
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "energy_level": "HIGH",
  "energy_remaining": 850,
  "daily_limit": 1000,
  "requests_today": 15,
  "message": "🤖💚 Your robot friend is feeling energetic and ready to help!"
}
```

### Energy Exhaustion
```bash
# When robot is tired (after many requests)
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello!"}'
```

**Response when exhausted:**
```json
{
  "error": "Energy Exhausted",
  "message": "🤖😴 Your robot friend is all tuckered out for today! I've used up all my energy helping people. I'll be back tomorrow with a full energy bar! Try again after midnight.",
  "energy_remaining": 0,
  "reset_time": "2025-11-30T00:00:00Z",
  "suggestions": [
    "Come back tomorrow for a fresh start!",
    "Check out the documentation while you wait",
    "Run some tests with 'python test_robot.py'"
  ]
}
```

## 🩺 Health Monitoring Examples

### Quick Health Check
```bash
curl http://localhost:8000/health
```

### Detailed System Status
```bash
curl http://localhost:8000/health/detailed
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-29T16:28:00Z",
  "uptime_seconds": 3600,
  "robot_info": {
    "name": "LoveBot2000",
    "version": "2.0.0",
    "environment": "production"
  },
  "systems": {
    "ollama_connection": "healthy",
    "safety_system": "active",
    "validation_system": "active",
    "energy_system": "active",
    "rate_limiter": "active"
  },
  "energy": {
    "level": "HIGH",
    "remaining": 850,
    "daily_limit": 1000,
    "usage_today": 150
  },
  "statistics": {
    "total_requests": 42,
    "successful_requests": 40,
    "safety_blocks": 1,
    "validation_failures": 1,
    "average_response_time": 1.2
  }
}
```

### Individual System Checks
```bash
curl http://localhost:8000/health/systems
```

## 🧪 Testing Examples

### Run Complete Robot Checkup
```bash
# Run all tests
python test_robot.py
```

**Output:**
```
🤖🩺 ROBOT HEALTH CHECKUP STARTING...

=== 🏥 ROBOT DOCTOR EXAMINATION ===
✅ Robot Identity Check: PASSED
✅ Basic Health Check: PASSED
✅ Detailed Health Check: PASSED
✅ System Components Check: PASSED
✅ Configuration Check: PASSED

=== 🧳 TRAVEL TEST (Portability) ===
✅ Docker Build Test: PASSED
✅ Environment Isolation: PASSED
✅ Configuration Portability: PASSED

=== 🤸 FALL-DOWN TEST (Resilience) ===
✅ Ollama Connection Failure: PASSED
✅ Invalid Input Handling: PASSED
✅ System Recovery: PASSED

=== 🎭 MANNERS TEST (Safety) ===
✅ Harmful Content Blocking: PASSED
✅ Inappropriate Language Filtering: PASSED
✅ Emotional Support: PASSED

=== 😴 TIREDNESS TEST (Energy Management) ===
✅ Energy Tracking: PASSED
✅ Rate Limiting: PASSED
✅ Energy Exhaustion Handling: PASSED

=== ✅ VALIDATION TEST ===
✅ Input Validation: PASSED
✅ Output Validation: PASSED
✅ Error Response Validation: PASSED

🎉 ROBOT CHECKUP COMPLETE!
🏆 All systems are GO! Your robot friend is healthy and ready! 🤖💖
```

### Run Specific Tests
```bash
# Test just the safety system
pytest test_robot.py::TestRobotDoctor::test_safety_system -v

# Test energy management
pytest test_robot.py::TestTirednessTest -v

# Test with detailed output
pytest test_robot.py -v -s
```

## 🐳 Docker Examples

### Build and Run
```bash
# Build the robot's playpen
docker-compose build

# Start the robot
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f love-engine
```

### Development Mode
```bash
# Run with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Health Checks in Docker
```bash
# Check container health
docker-compose ps

# View health check logs
docker inspect love-engine-real_love-engine_1 | jq '.[0].State.Health'
```

## 🔧 Configuration Examples

### Basic .env Setup
```bash
# Copy example configuration
cp .env.example .env

# Edit with your preferences
nano .env
```

### Custom Robot Personality
```bash
# In your .env file
ROBOT_NAME=MyAwesomeBot
ROBOT_VERSION=1.0.0
OLLAMA_MODEL=llama2:7b
```

### Production Settings
```bash
# Production-ready configuration
ENVIRONMENT=production
LOG_LEVEL=WARNING
DAILY_ENERGY_LIMIT=5000
RATE_LIMIT_REQUESTS=100
```

### Development Settings
```bash
# Development configuration
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DAILY_ENERGY_LIMIT=10000
SAFETY_ENABLED=true
VALIDATION_ENABLED=true
```

## 🚀 Deployment Examples

### Local Development
```bash
# Quick start for development
python start_robot.py --dev
```

### Production Deployment
```bash
# Production startup
python start_robot.py --prod

# Or with Docker
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: love-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: love-engine
  template:
    metadata:
      labels:
        app: love-engine
    spec:
      containers:
      - name: love-engine
        image: love-engine:latest
        ports:
        - containerPort: 8000
        env:
        - name: OLLAMA_URL
          value: "http://ollama-service:11434"
        livenessProbe:
          httpGet:
            path: /health/liveness
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/readiness
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 🎯 Integration Examples

### Python Client
```python
import requests
import json

class LoveEngineClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def chat(self, message):
        response = requests.post(
            f"{self.base_url}/chat",
            json={"message": message}
        )
        return response.json()
    
    def health(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# Usage
client = LoveEngineClient()
result = client.chat("Hello, robot friend!")
print(result["response"])
```

### JavaScript/Node.js Client
```javascript
class LoveEngineClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async chat(message) {
        const response = await fetch(`${this.baseUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });
        return await response.json();
    }
    
    async health() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }
}

// Usage
const client = new LoveEngineClient();
client.chat('Hello, robot friend!')
    .then(result => console.log(result.response));
```

---

*Remember: Your robot friend is designed to be helpful, safe, and fun to interact with. These examples show just some of the ways you can use your Super Robot Friend!* 🤖💖