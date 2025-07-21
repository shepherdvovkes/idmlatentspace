#!/bin/bash

# Simple IDM Latent Space Startup Script
echo "🚀 Starting IDM Latent Space Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running processes exist
cleanup_existing() {
    echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
    pkill -f "uvicorn.*app.main" || true
    pkill -f "react-scripts start" || true
    pkill -f "npm.*start" || true
}

# Function to check if port is in use
port_in_use() {
    ss -tlnp 2>/dev/null | grep -q ":$1 "
}

cleanup_existing

# Install Python dependencies if needed
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install -r requirements.txt --break-system-packages --user --quiet

# Install Node.js dependencies if needed
echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install --legacy-peer-deps --silent
fi
cd ..

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p uploads models datasets cache logs

# Check ports
if port_in_use 8000; then
    echo -e "${RED}❌ Port 8000 is already in use.${NC}"
fi

if port_in_use 3000; then
    echo -e "${RED}❌ Port 3000 is already in use.${NC}"
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        pkill -f "uvicorn.*app.main" || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        pkill -f "react-scripts start" || true
    fi
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

# Wait and check if services are running
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

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