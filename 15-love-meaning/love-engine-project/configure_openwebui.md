# Configuring Open WebUI to Connect to Love Engine

## Overview
Open WebUI supports OpenAI-compatible API integration, which allows us to connect it to our Love Engine as a custom backend.

## Prerequisites
1. Open WebUI running at http://localhost:3000
2. Love Engine running at http://localhost:9000
3. Ollama running at http://localhost:11434

## Configuration Steps

### Step 1: Access Open WebUI Admin Settings
1. Open your browser and go to http://localhost:3000
2. Create your admin account (first user becomes admin)
3. Navigate to Settings (gear icon) → Admin Settings

### Step 2: Configure Custom API Backend
1. In Admin Settings, look for "Models" or "API Configuration"
2. Add a new OpenAI-compatible API endpoint:
   - **Name**: Love Engine
   - **Base URL**: http://host.docker.internal:9000
   - **API Key**: (leave blank or use a dummy key)
   - **Model**: love-chat

### Step 3: Alternative Configuration via Environment Variables
If running Open WebUI with Docker, you can also configure it during startup:

```bash
docker run -d -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:9000 \
  -e OPENAI_API_KEY=dummy \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

### Step 4: Test the Connection
1. In Open WebUI, select the "Love Engine" model from the dropdown
2. Send a test message: "Hello, how are you?"
3. Verify you receive a response processed through the Love Engine

## Network Configuration Notes

### Docker Networking
- Use `host.docker.internal:9000` when Open WebUI runs in Docker
- Use `localhost:9000` when both run on the host machine

### Love Engine API Compatibility
The Love Engine needs to be OpenAI-compatible. Our current implementation at `/love-chat` needs to be adapted to match OpenAI's `/v1/chat/completions` endpoint format.

## Troubleshooting

### Common Issues
1. **Connection Refused**: Ensure Love Engine is running on port 9000
2. **API Format Mismatch**: Verify Love Engine returns OpenAI-compatible responses
3. **Docker Network Issues**: Use `host.docker.internal` instead of `localhost`

### Verification Commands
```bash
# Test Love Engine directly
curl -X POST http://localhost:9000/love-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Test from Docker container
docker exec open-webui curl http://host.docker.internal:9000/health
```

## Expected Workflow
1. User types message in Open WebUI
2. Open WebUI sends request to Love Engine at `/love-chat`
3. Love Engine processes message through:
   - Love vector computation
   - Ollama model generation (tinyllama:latest)
   - Safety evaluation
   - Thermodynamic adjustments
4. Love Engine returns adjusted response
5. Open WebUI displays the "love-filtered" response to user

This creates the complete pipeline: **Open WebUI → Love Engine → Ollama → Love Engine → Open WebUI**
