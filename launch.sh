#!/bin/bash

echo "=========================================="
echo "   AISEO Multi-LLM Query Tool Launcher   "
echo "=========================================="
echo ""

# Kill any existing processes on the ports
echo "Cleaning up any existing processes..."
lsof -ti:5555 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null

# Start backend
echo "Starting backend server..."
cd backend
python3 app.py > backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 2

# Check if backend started
if ps -p $BACKEND_PID > /dev/null; then
    echo "✓ Backend started (PID: $BACKEND_PID)"
else
    echo "✗ Backend failed to start. Check backend/backend.log for details."
    exit 1
fi

# Start frontend simple server
echo "Starting frontend server..."
cd frontend
python3 -m http.server 8080 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "            🚀 READY TO USE!              "
echo "=========================================="
echo ""
echo "Backend API: http://localhost:5555/api/health"
echo "Frontend UI: http://localhost:8080"
echo ""
echo "Note: Open http://localhost:8080 in your browser"
echo "      The UI will connect to the backend API"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "=========================================="

# Trap Ctrl+C and cleanup
trap 'echo ""; echo "Shutting down..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT

# Keep script running
wait