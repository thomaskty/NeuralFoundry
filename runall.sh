#!/bin/bash

# Activate virtual environment first
source .venv/bin/activate

# Start backend in background
echo "🚀 Starting backend..."
python -m uvicorn app.main:app --reload &
BACKEND_PID=$!

# Start frontend in background
echo "🎨 Starting frontend..."
cd frontend && npm run dev &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Trap Ctrl+C
trap cleanup INT

# Wait for both
wait $BACKEND_PID $FRONTEND_PID