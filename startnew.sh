#!/bin/bash

# IDM Latent Space - Enhanced Startup Script
echo "🚀 Starting IDM Latent Space Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print colored status
print_status() {
    echo -e "${2}${1}${NC}"
}

# Function to handle errors
handle_error() {
    print_status "❌ Error: $1" "$RED"
    exit 1
}

# Check if we're in the correct directory
if [ ! -f "app/main.py" ]; then
    handle_error "Please run this script from the project root directory"
fi

# Check dependencies
print_status "📋 Checking system dependencies..." "$BLUE"

if ! command_exists python3; then
    handle_error "Python 3 is required but not installed. Please install Python 3.8 or higher."
fi

if ! command_exists node; then
    handle_error "Node.js is required but not installed. Please install Node.js 16 or higher."
fi

if ! command_exists npm; then
    handle_error "npm is required but not installed. Please install npm."
fi

print_status "✅ All system dependencies found" "$GREEN"

# Clean up any existing processes
print_status "🧹 Cleaning up existing processes..." "$YELLOW"
pkill -f "uvicorn.*app.main" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
sleep 2

# Setup Python virtual environment
print_status "🐍 Setting up Python environment..." "$BLUE"

# Check if we're already in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_status "✅ Using existing virtual environment: $VIRTUAL_ENV" "$GREEN"
else
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "📦 Creating virtual environment..." "$YELLOW"
        python3 -m venv venv || handle_error "Failed to create virtual environment"
    fi
    
    # Activate virtual environment
    print_status "🔌 Activating virtual environment..." "$YELLOW"
    source venv/bin/activate || handle_error "Failed to activate virtual environment"
fi

# Upgrade pip
print_status "⬆️  Upgrading pip..." "$BLUE"
python -m pip install --upgrade pip --quiet

# Install Python dependencies
print_status "📦 Installing Python dependencies..." "$BLUE"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet || handle_error "Failed to install Python dependencies"
    print_status "✅ Python dependencies installed" "$GREEN"
else
    handle_error "requirements.txt not found"
fi

# Setup frontend
print_status "🎨 Setting up frontend..." "$BLUE"
cd frontend || handle_error "Frontend directory not found"

# Install Node.js dependencies
if [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
    print_status "📦 Installing Node.js dependencies (this may take a while)..." "$YELLOW"
    npm install --legacy-peer-deps || handle_error "Failed to install Node.js dependencies"
    print_status "✅ Node.js dependencies installed" "$GREEN"
else
    print_status "✅ Node.js dependencies already installed" "$GREEN"
fi

cd ..

# Create necessary directories
print_status "📁 Creating necessary directories..." "$BLUE"
mkdir -p uploads models datasets cache logs
mkdir -p app/static app/templates

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "🔐 Creating .env file..." "$YELLOW"
    cat > .env << EOF
# Environment variables
DEBUG=True
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:///./idm_latent_space.db
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
EOF
    print_status "✅ .env file created" "$GREEN"
fi

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
    print_status "✅ Cleanup complete" "$GREEN"
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start backend
print_status "🖥️  Starting backend server..." "$BLUE"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
print_status "⏳ Waiting for backend to start..." "$YELLOW"
for i in {1..30}; do
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        print_status "✅ Backend server is running!" "$GREEN"
        break
    fi
    if [ $i -eq 30 ]; then
        print_status "❌ Backend server failed to start. Check logs/backend.log for details." "$RED"
        tail -n 20 logs/backend.log
        exit 1
    fi
    sleep 1
done

# Start frontend
print_status "🎨 Starting frontend server..." "$BLUE"
cd frontend
BROWSER=none PORT=3000 npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
print_status "⏳ Waiting for frontend to start (this may take up to 60 seconds)..." "$YELLOW"
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_status "✅ Frontend server is running!" "$GREEN"
        break
    fi
    if [ $i -eq 60 ]; then
        print_status "⚠️  Frontend is taking longer than expected. It may still be starting..." "$YELLOW"
    fi
    sleep 1
done

# Display status
echo ""
print_status "═══════════════════════════════════════════════════════" "$CYAN"
print_status "🎉 IDM Latent Space Platform is running!" "$GREEN"
print_status "═══════════════════════════════════════════════════════" "$CYAN"
echo ""
print_status "📖 Frontend: http://localhost:3000" "$BLUE"
print_status "🔧 Backend API: http://localhost:8000" "$BLUE"
print_status "📚 API Documentation: http://localhost:8000/docs" "$BLUE"
print_status "📊 API Interactive: http://localhost:8000/redoc" "$BLUE"
echo ""
print_status "📝 Logs:" "$YELLOW"
print_status "   Backend: logs/backend.log" "$YELLOW"
print_status "   Frontend: logs/frontend.log" "$YELLOW"
echo ""
print_status "Press Ctrl+C to stop all services" "$YELLOW"
print_status "═══════════════════════════════════════════════════════" "$CYAN"

# Keep script running
wait