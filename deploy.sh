#!/bin/bash

# Jira-Figma Analyzer Deployment Script
set -e

echo "🚀 Starting Jira-Figma Analyzer Deployment..."

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

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.production .env
    echo "📝 Please edit .env file with your API keys before continuing."
    echo "   - OPENAI_API_KEY=your_openai_api_key_here"
    echo "   - FIGMA_ACCESS_TOKEN=your_figma_token_here"
    read -p "Press Enter after updating .env file..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p analysis_outputs logs ssl

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 30

# Check if the application is running
if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo "🌐 Access your application at: http://localhost:8501"
    echo "📊 Health check: http://localhost:8501/_stcore/health"
else
    echo "❌ Application failed to start. Checking logs..."
    docker-compose logs
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop app: docker-compose down"
echo "   Restart app: docker-compose restart"
echo "   Update app: docker-compose pull && docker-compose up -d"
