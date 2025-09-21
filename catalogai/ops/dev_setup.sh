#!/bin/bash

# Development setup script for CatalogAI
set -e

echo "🚀 Setting up CatalogAI development environment..."

# Check if Python 3.11+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ $(echo "$PYTHON_VERSION < 3.11" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.11+ is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2)
echo "✅ Node.js $NODE_VERSION found"

# Setup backend
echo "📦 Setting up backend..."
cd ../backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp ../.env.example .env
fi

# Run initial model training
echo "🤖 Training initial model..."
cd ../data/seeds
python seed_run.py

# Return to backend and train model
cd ../../backend
python -c "
import sys
sys.path.append('.')
from pathlib import Path
from app.pipeline.classifier import train
seed_dir = Path('../data/seeds')
if seed_dir.exists():
    print('Training model...')
    metrics = train(seed_dir)
    print(f'Model trained with accuracy: {metrics.get(\"accuracy\", \"unknown\")}')
else:
    print('Seed directory not found')
"

echo "✅ Backend setup complete"

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    echo "NEXT_PUBLIC_API_BASE=http://localhost:8000" > .env.local
fi

echo "✅ Frontend setup complete"

# Return to root
cd ..

echo "🎉 Development environment setup complete!"
echo ""
echo "To start development:"
echo "1. Backend: cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "Or use the run_local.sh script to start both services."