#!/bin/bash

# LCRS System Setup Script
echo "🚀 Setting up LCRS (Love, Care, Relationship, Safety) System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual API keys before continuing"
else
    echo "✅ .env file already exists"
fi

# Build and start services
echo "🐳 Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if API is responding
echo "🔍 Testing API health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ LCRS API is running successfully!"
    echo "📊 API Documentation: http://localhost:8000/docs"
    echo "💚 Health Check: http://localhost:8000/health"
    echo "📈 Grafana Dashboard: http://localhost:3000 (admin/admin)"
else
    echo "❌ API health check failed. Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "🎉 LCRS System setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Test the emotion analysis: curl -X POST http://localhost:8000/api/v1/analyze-emotion -d '{"message": "I am frustrated with my setup"}' -H 'Content-Type: application/json'"
echo "3. Set up your Zapier integrations"
echo ""
