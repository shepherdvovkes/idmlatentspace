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

# Clean up any existing processes
echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
pkill -f "uvicorn.*app.main" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install -r requirements.txt --break-system-packages --user --quiet

# Install Node.js dependencies
echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install --legacy-peer-deps --silent
fi
cd ..

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p uploads models datasets cache logs

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    pkill -f "uvicorn.*app.main" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start backend
echo -e "${BLUE}🖥️  Starting backend server...${NC}"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
sleep 5

# Start frontend
echo -e "${BLUE}🎨 Starting frontend server...${NC}"
cd frontend
BROWSER=none npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo -e "${YELLOW}⏳ Waiting for frontend to start...${NC}"
sleep 10

# Check services
echo -e "${YELLOW}📊 Checking services...${NC}"
sleep 5

# Test backend
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend server running on http://localhost:8000${NC}"
    echo -e "${GREEN}📚 API Documentation: http://localhost:8000/docs${NC}"
else
    echo -e "${RED}❌ Backend server failed to start${NC}"
fi

# Test frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend server running on http://localhost:3000${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend server starting (may take a few more seconds)${NC}"
fi

echo -e "\n${GREEN}🎉 IDM Latent Space Platform is running!${NC}"
echo -e "${BLUE}📖 Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}🔧 Backend API: http://localhost:8000${NC}"
echo -e "${BLUE}📚 API Docs: http://localhost:8000/docs${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for user to stop
wait