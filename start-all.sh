#!/bin/bash

echo "🚀 Starting Intelligent UI Application..."
echo "======================================"

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping all services..."
    if [ ! -z "$TRADITIONAL_PID" ]; then
        kill $TRADITIONAL_PID 2>/dev/null
    fi
    if [ ! -z "$AI_FRONTEND_PID" ]; then
        kill $AI_FRONTEND_PID 2>/dev/null
    fi
    echo "✅ All services stopped"
    echo "ℹ️  Note: intelligent-ui-backend runs as separate service"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Note about separate backend service
echo "ℹ️  intelligent-ui-backend runs as separate service"
echo "   Start it manually with: cd intelligent-ui-backend && python main.py"
echo ""

# Start traditional website (port 3000)
echo "🌐 Starting traditional website..."

# Install dependencies for traditional website
echo "📦 Installing traditional website dependencies..."
npm install > /dev/null 2>&1

# Start traditional website in background
echo "🔄 Starting traditional website server..."
npm run dev > logs/traditional.log 2>&1 &
TRADITIONAL_PID=$!

# Start AI frontend (port 3001)
echo "⚛️  Starting AI frontend..."
cd intelligent-ui-frontend

# Install dependencies
echo "📦 Installing AI frontend dependencies..."
npm install > /dev/null 2>&1

# Start AI frontend in background
echo "🔄 Starting AI frontend server..."
npm run dev > ../logs/ai-frontend.log 2>&1 &
AI_FRONTEND_PID=$!

# Wait for frontends to start
sleep 5

# Create logs directory if it doesn't exist
cd ..
mkdir -p logs

# Check if services are running
echo ""
echo "🔍 Checking services..."

# Check backend (separate service)
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Backend: Running on http://localhost:8001 (separate service)"
else
    echo "ℹ️  Backend: Not running (start separately: cd intelligent-ui-backend && python main.py)"
fi

# Check traditional website
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Traditional Website: Running on http://localhost:3000"
else
    echo "❌ Traditional Website: Failed to start"
fi

# Check AI frontend
if curl -s http://localhost:3001 > /dev/null; then
    echo "✅ AI Frontend: Running on http://localhost:3001"
else
    echo "❌ AI Frontend: Failed to start"
fi

echo ""
echo "🌐 Access URLs:"
echo "   • Traditional Website: http://localhost:3000"
echo "   • Traditional Admin:   http://localhost:3000/admin"
echo "   • AI Mode Interface:   http://localhost:3001"
echo ""
echo "🤖 Intelligent UI Backend (Separate Service):"
echo "   • Backend API:         http://localhost:8001"
echo "   • API Documentation:   http://localhost:8001/docs"
echo "   • Health Check:        http://localhost:8001/health"
echo "   • Start Command:       cd intelligent-ui-backend && python main.py"
echo ""
echo "📋 Quick Test:"
echo "   1. Start backend: cd intelligent-ui-backend && python main.py"
echo "   2. Visit http://localhost:3000 for traditional e-commerce"
echo "   3. Visit http://localhost:3000/admin for admin interface"
echo "   4. Click 'AI Mode' button to open http://localhost:3001"
echo "   5. In AI mode, try: 'I want to return my order from last week'"
echo ""
echo "📝 Logs:"
echo "   • Traditional: tail -f logs/traditional.log"
echo "   • AI Frontend: tail -f logs/ai-frontend.log"
echo "   • Backend:     cd intelligent-ui-backend && python view_logs.py"
echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo ""

# Keep script running and wait for interrupt
wait