#!/bin/bash

# Tampa Bay Credit Repair - Local Startup Script

echo "🚀 Starting Tampa Bay Credit Repair..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Error: Docker is not running!"
  echo "👉 Please start Docker Desktop and run this script again."
  echo ""
  echo "💡 ALTERNATIVE: You can run the frontend only (with mock data) by running:"
  echo "   cd apps/web && npm run dev"
  exit 1
fi

echo "🐳 Docker is running. Building and starting services..."
docker-compose up --build
