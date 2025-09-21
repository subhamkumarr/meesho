#!/bin/bash

# Local development runner for CatalogAI
set -e

echo "🚀 Starting CatalogAI local development servers..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Check if virtual environment exists
if [ ! -d "../backend/venv" ]; then
    echo "❌ Backend virtual environment not found. Run dev_setup.sh first."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "../frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not found. Run dev_setup.sh first."
    exit 1
fi

# Start backend
echo "🐍 Starting backend server..."
cd ../backend
source venv/bin/activate

# Set environment variables
export PYTHONPATH=$(pwd)
export DB_URL="sqlite:///app.db"
export THRESH_AUTH="0.15"
export THRESH_SYN="0.70"
export MAX_IMAGE_MB="8"
export LOG_LEVEL="INFO"

# Start backend in background
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
        echo "✅ Backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        exit 1
    fi
    sleep 1
done

# Start frontend
echo "⚛️  Starting frontend server..."
cd ../frontend

# Set environment variables
export NEXT_PUBLIC_API_BASE="http://localhost:8000"

# Start frontend in background
npm run dev &
FRONTEND_PID=$!

echo "✅ Frontend started (PID: $FRONTEND_PID)"

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000/ > /dev/null 2>&1; then
        echo "✅ Frontend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start"
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎉 CatalogAI is running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
while true; do
    sleep 1
done