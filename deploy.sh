#!/bin/bash

# CubePlus Trading Simulator - Production Deployment Script

set -e

echo "🚀 Starting CubePlus Trading Simulator deployment..."

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

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs ssl

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.production template..."
    cp .env.production .env
    echo "📝 Please edit .env file with your actual configuration before continuing."
    echo "Press any key to continue after editing .env file..."
    read -n 1 -s
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🗄️  Starting PostgreSQL database..."
docker-compose up -d db

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🚀 Starting application..."
docker-compose up -d app

echo "🌐 Starting nginx reverse proxy..."
docker-compose up -d nginx

echo "✅ Deployment completed!"
echo ""
echo "🌍 Application is now running at:"
echo "   Local: http://localhost"
echo "   Network: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "📊 Admin Panel: http://localhost/admin"
echo "   Username: admin@cubeplus.com"
echo "   Password: admin123"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart: docker-compose restart"
echo "   Update: git pull && docker-compose build && docker-compose up -d"