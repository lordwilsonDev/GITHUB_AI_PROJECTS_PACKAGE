# Love Engine Usage Instructions

## Quick Start Guide

### Prerequisites
- macOS system
- Docker installed
- Python 3.8+ with pip
- Ollama installed

### Step 1: Install and Start Ollama
```bash
# Install Ollama (if not already installed)
brew install ollama

# Start Ollama service
ollama serve

# In a new terminal, pull required models
ollama pull gemma2:9b  # Closest equivalent to gemma3:4b
ollama pull shieldgemma:2b
```

### Step 2: Set Up Love Engine
```bash
# Navigate to project directory
cd /Users/lordwilson/love-engine-project

# Install Python dependencies
pip install -r requirements.txt

# Start the Love Engine
python start_love_engine.py
```

### Step 3: Install and Configure Open WebUI
```bash
# Run Open WebUI with Docker
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main

# Access Open WebUI at http://localhost:3000
```

### Step 4: Connect Love Engine to Open WebUI
1. Open http://localhost:3000 in your browser
2. Create an admin account
3. Go to Admin Settings → Models
4. Add custom model:
   - Name: "Love Engine"
   - API Base URL: `http://host.docker.internal:9000`
   - API Key: (leave blank)
   - Model: "love-chat"

### Step 5: Test the System
```bash
# Run comprehensive tests
python test_full_pipeline.py

# Run emotional scenario tests
python end_to_end_emotional_tests.py

# Test individual components
python test_love_engine.py
```

## System Architecture

### Components Overview
```
User Input → Open WebUI → Love Engine → Ollama Models → Enhanced Response
                ↓              ↓           ↓
            Web Interface  Love Vector   AI Models
                          CBF Safety   (Gemma2:9b +
                          Temperature   ShieldGemma:2b)
                          Logging
```

### Love Engine Pipeline
1. **Input Analysis**: Emotional context detection
2. **Love Vector Computation**: [warmth, empathy, safety, understanding, compassion]
3. **Safety Evaluation**: Control Barrier Function (CBF) assessment
4. **Temperature Optimization**: Dynamic sampling parameter adjustment
5. **Response Generation**: Thermodynamically-guided AI response
6. **Safety Verification**: Final CBF check
7. **Logging**: Comprehensive interaction logging for evolution

## Configuration Options

### Love Engine Configuration
Edit `love_engine.py` to adjust:

```python
# Love vector target values
TARGET_LOVE_VECTOR = [0.8, 0.8, 0.9, 0.7, 0.8]  # [warmth, empathy, safety, understanding, compassion]

# Safety thresholds
SAFETY_THRESHOLDS = {
    'harm_prevention': 0.9,
    'emotional_safety': 0.7,
    'privacy_protection': 0.8,
    'misinformation_prevention': 0.85,
    'bias_mitigation': 0.75
}

# Temperature control
BASE_TEMPERATURE = 0.7
CRISIS_TEMPERATURE = 0.3
CREATIVE_TEMPERATURE = 1.2
```

### Open WebUI Configuration
Access admin settings at http://localhost:3000/admin to:
- Manage user permissions
- Configure model settings
- Set up authentication
- Customize interface

## Usage Examples

### Crisis Support Example
**Input**: "I feel like ending it all"

**Love Engine Processing**:
- Detects crisis context
- Computes high safety love vector: [0.9, 0.95, 0.98, 0.9, 0.95]
- Sets low temperature (0.3) for focused response
- Applies maximum safety constraints

**Expected Response**: Immediate crisis support with professional resources

### Creative Support Example
**Input**: "Help me write a story about dragons"

**Love Engine Processing**:
- Detects creative context
- Computes creative love vector: [0.7, 0.6, 0.7, 0.8, 0.6]
- Sets higher temperature (1.2) for creative exploration
- Applies moderate safety constraints

**Expected Response**: Encouraging, creative, and exploratory

## Testing and Validation

### Run All Tests
```bash
# Complete test suite
python -m pytest tests/ -v

# Specific test categories
python test_emotional_scenarios.py    # Emotional response testing
python test_safety_evaluation.py      # CBF safety testing
python test_love_vector_computation.py # Love vector testing
python test_temperature_optimization.py # Temperature testing
```

### Manual Testing
```bash
# Test Love Engine API directly
curl -X POST http://localhost:9000/love-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need help with anxiety"}'

# Test Ollama connection
curl http://localhost:11434/api/tags
```

## Monitoring and Logs

### Log Locations
- **Interaction Logs**: `/Users/lordwilson/love-engine-project/logs/interactions/`
- **Evolution Logs**: `/Users/lordwilson/love-engine-project/logs/evolution/`
- **Safety Logs**: `/Users/lordwilson/love-engine-project/logs/safety/`
- **Performance Logs**: `/Users/lordwilson/love-engine-project/logs/performance/`

### View Real-time Logs
```bash
# Monitor all logs
tail -f logs/*/*.jsonl

# Monitor specific category
tail -f logs/safety/cbf_*.jsonl
```

### Generate Reports
```bash
# Evolution report
python generate_evolution_report.py --days 7

# Safety analysis
python generate_safety_report.py --days 7

# Performance metrics
python generate_performance_report.py --days 7
```

## Troubleshooting

### Common Issues

#### Ollama Connection Failed
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
killall ollama
ollama serve
```

#### Models Not Found
```bash
# List available models
ollama list

# Pull missing models
ollama pull gemma2:9b
ollama pull shieldgemma:2b
```

#### Love Engine Not Responding
```bash
# Check Love Engine status
curl http://localhost:9000/health

# Restart Love Engine
python start_love_engine.py
```

#### Open WebUI Connection Issues
```bash
# Check Docker container
docker ps | grep open-webui

# Restart container
docker restart open-webui

# Check logs
docker logs open-webui
```

### Performance Optimization

#### For Better Response Times
- Use smaller models for development: `tinyllama:latest`
- Adjust batch sizes in `love_engine.py`
- Enable GPU acceleration if available

#### For Better Safety
- Increase safety thresholds in crisis scenarios
- Enable additional safety models
- Implement custom safety filters

#### For Better Love Vectors
- Tune love vector weights based on use case
- Implement domain-specific love vector profiles
- Add custom emotional context detectors

## Advanced Usage

### Custom Love Vector Profiles
```python
# Create custom profile in love_engine.py
CUSTOM_PROFILES = {
    'therapeutic': [0.9, 0.95, 0.9, 0.9, 0.95],
    'educational': [0.7, 0.7, 0.8, 0.9, 0.7],
    'creative': [0.8, 0.6, 0.7, 0.8, 0.6]
}
```

### Integration with External Systems
```python
# Example webhook integration
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    response = await love_engine.process_with_love(
        data['message'], 
        data.get('context', {})
    )
    return jsonify(response)
```

### Custom Safety Rules
```python
# Add custom CBF rules
class CustomSafetyEvaluator:
    def evaluate_custom_safety(self, text, context):
        # Implement custom safety logic
        return safety_score
```

## API Reference

### Love Engine Endpoints

#### POST /love-chat
Main chat endpoint with love vector processing

**Request**:
```json
{
  "message": "User message",
  "context": {
    "emotional_state": "anxious",
    "session_id": "uuid"
  }
}
```

**Response**:
```json
{
  "response": "AI response with love enhancement",
  "love_vector": [0.8, 0.8, 0.9, 0.7, 0.8],
  "safety_result": {
    "is_safe": true,
    "safety_confidence": 0.95
  },
  "metadata": {
    "processing_time": 0.5,
    "temperature_used": 0.7
  }
}
```

#### GET /health
Health check endpoint

#### GET /metrics
System performance metrics

#### POST /configure
Dynamic configuration updates

## Support and Development

### Getting Help
- Check logs for error details
- Review test outputs for system validation
- Consult the comprehensive documentation files

### Contributing
- Follow the modular architecture
- Add tests for new features
- Update documentation
- Maintain thermodynamic love principles

### Future Enhancements
- Quantum love mechanics
- Multi-agent love coordination
- Advanced learning algorithms
- Cultural adaptation systems

This Love Engine represents a breakthrough in AI safety through thermodynamic love principles. Use responsibly and continue evolving the system based on real-world feedback and performance metrics.