#!/bin/bash

echo "🚀 Starting IDM Latent Space Platform..."

# Kill existing processes
pkill -f "uvicorn.*app.main" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true

# Start backend
echo "🖥️  Starting backend server..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend
sleep 3

# Start frontend  
echo "🎨 Starting frontend server..."
cd frontend
BROWSER=none npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Services starting..."
echo "📖 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

# Cleanup function
cleanup() {
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    pkill -f "uvicorn.*app.main" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

# Wait for user input
wait