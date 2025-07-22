#!/bin/bash

# Simple backend startup script

echo "Starting IDM Latent Space Backend..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Using existing virtual environment"
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install missing dependencies if needed
echo "Installing core dependencies..."
pip install -q fastapi uvicorn[standard] python-multipart sqlalchemy alembic aiosqlite python-jose[cryptography] passlib[bcrypt] python-dotenv pydantic pydantic-settings structlog aiofiles psutil prometheus-client email-validator numpy 2>/dev/null

# Create necessary directories
mkdir -p logs uploads models datasets cache

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DEBUG=True
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite+aiosqlite:///./idm_latent_space.db
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
EOF
fi

# Start the backend
echo "Starting backend server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload