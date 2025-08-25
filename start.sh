#!/bin/bash

echo "Starting AISEO Multi-LLM Query Tool..."
echo "======================================="
echo ""

# Check if backend is already running
if lsof -i:5555 > /dev/null 2>&1; then
    echo "✓ Backend already running on port 5555"
else
    echo "Starting backend server..."
    cd backend
    python3 app.py &
    BACKEND_PID=$!
    cd ..
    sleep 3
    echo "✓ Backend started (PID: $BACKEND_PID)"
fi

echo ""
echo "Starting frontend server..."
cd frontend

# Check if npm dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Try to run with Vite, fallback to simple server if it fails
echo "Attempting to start frontend with Vite..."
npm run dev 2>/dev/null &
FRONTEND_PID=$!

sleep 3

# Check if Vite started successfully
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo "Vite failed to start. Using simple HTTP server instead..."
    # Build the frontend first
    echo "Building frontend..."
    npm run build 2>/dev/null || echo "Build failed, using development mode"
    
    # Start a simple Python HTTP server for the dist folder
    if [ -d "dist" ]; then
        cd dist
        python3 -m http.server 5173 &
        FRONTEND_PID=$!
        echo "✓ Frontend started with simple server (PID: $FRONTEND_PID)"
    else
        # If no dist folder, try to serve the dev files
        python3 -m http.server 5173 &
        FRONTEND_PID=$!
        echo "✓ Frontend started in development mode (PID: $FRONTEND_PID)"
    fi
else
    echo "✓ Frontend started with Vite (PID: $FRONTEND_PID)"
fi

echo ""
echo "======================================="
echo "AISEO UI is now running!"
echo ""
echo "Backend API: http://localhost:5555"
echo "Frontend UI: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "======================================="

# Wait for Ctrl+C
trap 'echo "Shutting down..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
wait