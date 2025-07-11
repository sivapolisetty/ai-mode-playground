@echo off
echo 🚀 Starting Intelligent UI Application...
echo ======================================

REM Create logs directory
if not exist "logs" mkdir logs

echo ℹ️ intelligent-ui-backend runs as separate service
echo    Start it manually: cd intelligent-ui-backend && python main.py
echo.

echo 🌐 Starting traditional website (port 3000)...
start "Traditional Website" cmd /k "npm install && npm run dev"

echo ⏳ Waiting for traditional website to start...
timeout /t 3 /nobreak >nul

echo ⚛️ Starting AI frontend (port 3001)...
start "AI Frontend" cmd /k "cd intelligent-ui-frontend && npm install && npm run dev"

echo ⏳ Waiting for AI frontend to start...
timeout /t 3 /nobreak >nul

echo.
echo 🌐 Access URLs:
echo    • Traditional Website: http://localhost:3000
echo    • Traditional Admin:   http://localhost:3000/admin
echo    • AI Mode Interface:   http://localhost:3001
echo.
echo 🤖 Intelligent UI Backend (Separate Service):
echo    • Backend API:         http://localhost:8001  
echo    • API Documentation:   http://localhost:8001/docs
echo    • Health Check:        http://localhost:8001/health
echo    • Start Command:       cd intelligent-ui-backend && python main.py
echo.
echo 📋 Quick Test:
echo    1. Start backend: cd intelligent-ui-backend && python main.py
echo    2. Visit http://localhost:3000 for traditional e-commerce
echo    3. Visit http://localhost:3000/admin for admin interface
echo    4. Click 'AI Mode' button to open http://localhost:3001
echo    5. In AI mode, try: 'I want to return my order from last week'
echo.
echo ✅ All services started!
echo 🛑 Close the terminal windows to stop services
echo.
pause