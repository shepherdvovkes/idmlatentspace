#!/bin/bash

# IDM Latent Space - Startup Script
echo "🚀 Starting IDM Latent Space Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null
}

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is required but not installed.${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is required but not installed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All dependencies found${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env file with your configuration${NC}"
fi

# Check ports
if port_in_use 8000; then
    echo -e "${RED}❌ Port 8000 is already in use. Please stop the service using it.${NC}"
    exit 1
fi

if port_in_use 3000; then
    echo -e "${RED}❌ Port 3000 is already in use. Please stop the service using it.${NC}"
    exit 1
fi

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Install Node.js dependencies
echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"
cd frontend
npm install
cd ..

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p uploads models datasets cache logs

# Start Redis (if not running)
if ! port_in_use 6379; then
    echo -e "${BLUE}🔄 Starting Redis...${NC}"
    if command_exists redis-server; then
        redis-server --daemonize yes
    else
        echo -e "${YELLOW}⚠️  Redis not found. Install Redis or use external Redis server.${NC}"
    fi
fi

# Start PostgreSQL (if not running) - Optional
if ! port_in_use 5432; then
    echo -e "${YELLOW}⚠️  PostgreSQL not detected on port 5432. Make sure your database is running.${NC}"
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    if [ ! -z "$WORKER_PID" ]; then
        kill $WORKER_PID 2>/dev/null
    fi
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Start backend
echo -e "${BLUE}🖥️  Starting backend server...${NC}"
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Celery worker (if Celery is available)
if command_exists celery; then
    echo -e "${BLUE}⚙️  Starting background worker...${NC}"
    celery -A app.worker worker --loglevel=info &
    WORKER_PID=$!
fi

# Start frontend
echo -e "${BLUE}🎨 Starting frontend server...${NC}"
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait a bit and check if services are running
sleep 5

if port_in_use 8000; then
    echo -e "${GREEN}✅ Backend server running on http://localhost:8000${NC}"
    echo -e "${GREEN}📚 API Documentation: http://localhost:8000/docs${NC}"
else
    echo -e "${RED}❌ Backend server failed to start${NC}"
fi

if port_in_use 3000; then
    echo -e "${GREEN}✅ Frontend server running on http://localhost:3000${NC}"
else
    echo -e "${RED}❌ Frontend server failed to start${NC}"
fi

echo -e "\n${GREEN}🎉 IDM Latent Space Platform is running!${NC}"
echo -e "${BLUE}📖 Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}🔧 Backend API: http://localhost:8000${NC}"
echo -e "${BLUE}📚 API Docs: http://localhost:8000/docs${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for user to stop
wait