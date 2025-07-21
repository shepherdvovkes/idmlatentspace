#!/bin/bash

# Quick start script - assumes dependencies are already installed
echo "🚀 Quick starting IDM Latent Space Platform..."

# Activate virtual environment if not already active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "⚠️  Virtual environment not found. Run ./startnew.sh first."
        exit 1
    fi
fi

# Kill any existing processes
pkill -f "uvicorn.*app.main" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true

# Create logs directory if it doesn't exist
mkdir -p logs

# Start backend
echo "🖥️  Starting backend..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Start frontend
echo "🎨 Starting frontend..."
cd frontend && BROWSER=none PORT=3000 npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Function to cleanup
cleanup() {
    echo -e "\n🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    pkill -f "uvicorn.*app.main" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "✅ Services starting..."
echo "📖 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

wait