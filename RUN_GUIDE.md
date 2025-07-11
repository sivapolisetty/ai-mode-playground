# How to Run the Intelligent UI Application

## Prerequisites

### System Requirements
- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **npm or yarn** (package manager)

### Environment Setup
1. Clone or navigate to the project directory
2. Set up your OpenRouter API key (get from https://openrouter.ai/)

## 🚀 Quick Start

### ⚠️ Important: Intelligent UI Backend runs as separate service

The `intelligent-ui-backend` now runs as a **separate service** and is not included in the main start-all scripts. This provides better isolation and monitoring capabilities.

### Option 1: Start All Services (Recommended)

1. **Start the Intelligent UI Backend** (separate terminal):
   ```bash
   cd intelligent-ui-backend
   ./start-backend.sh        # Linux/Mac
   # OR
   start-backend.bat         # Windows
   ```

2. **Start the main application services**:
   ```bash
   ./start-all.sh           # Linux/Mac  
   # OR
   start-all.bat            # Windows
   ```

### Option 2: Manual Service Startup

#### 1. Start Intelligent UI Backend (Terminal 1)
```bash
cd intelligent-ui-backend
source venv/bin/activate           # Linux/Mac
# OR
venv\Scripts\activate              # Windows

pip install -r requirements.txt
python main.py
```

#### 2. Start Traditional Website (Terminal 2)  
```bash
npm install
npm run dev                        # Runs on port 3000
```

#### 3. Start AI Frontend (Terminal 3)
```bash
cd intelligent-ui-frontend
npm install  
npm run dev                        # Runs on port 3001
```

## 🌐 Service URLs

After starting all services:

### Main Application
- **Traditional Website**: http://localhost:3000
- **Traditional Admin**: http://localhost:3000/admin  
- **AI Mode Interface**: http://localhost:3001

### Intelligent UI Backend (Separate Service)
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 🔧 Backend Monitoring & Testing

The intelligent-ui-backend includes enhanced logging and monitoring tools:

### Real-time Log Monitoring
```bash
cd intelligent-ui-backend
python view_logs.py                # Real-time colored logs
python view_logs.py --summary      # Log statistics
```

### Test Agent Activity
```bash
cd intelligent-ui-backend
python test_agent_activity.py --quick       # Quick test
python test_agent_activity.py --continuous  # Continuous monitoring
```

### Example API Request
```bash
curl -X POST http://localhost:8001/api/intelligent/process \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "user_input": "I want to return my order from last week", 
    "context": {"customerId": "CUST-001"}
  }'
```

### Option 2: Manual Step-by-Step

## 📋 Step-by-Step Setup

### 1. Backend Setup (Python)

```bash
# Navigate to backend directory
cd intelligent-ui-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # If you have an example file
# Or create .env file with your settings:
```

**Create `.env` file:**
```env
# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Model Configuration
LLM_MODEL=anthropic/claude-3-haiku-20240307
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1000

# Server Configuration
HOST=localhost
PORT=8001
DEBUG=True
ENVIRONMENT=development

# Traditional API Configuration
TRADITIONAL_API_URL=http://localhost:3000

# Session Configuration
SESSION_SECRET_KEY=dev-secret-key-change-in-production
SESSION_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

```bash
# Start backend server
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://localhost:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. Frontend Setup (React)

Open a new terminal:

```bash
# Navigate to frontend directory
cd intelligent-ui-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
  VITE v4.5.0  ready in 1230 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### 3. Traditional Website Setup

Open a new terminal in the main project directory:

```bash
# If you have a separate traditional website
# Navigate to main project directory
cd /root/projects/IUI/AgenticDynamicUIApp

# Install dependencies (if package.json exists)
npm install

# Start traditional website
npm run dev
```

## 🌐 Access URLs

Once all services are running:

| Service | URL | Purpose |
|---------|-----|---------|
| **Main Website** | http://localhost:3000 | Traditional e-commerce site with AI mode toggle |
| **Backend API** | http://localhost:8001 | REST API endpoints |
| **API Health Check** | http://localhost:8001/health | Backend status |
| **API Docs** | http://localhost:8001/docs | Interactive API documentation |

## 🔧 Development Workflow

### Testing the Integration

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8001/health
   # Expected: {"status": "healthy"}
   ```

2. **Frontend Connection:**
   - Visit http://localhost:5173
   - Should show "Connected" status
   - If shows "Connecting...", check backend is running

3. **Full Flow Test:**
   - Go to http://localhost:3000 (traditional site)
   - Click "Switch to AI Mode"
   - Try: "I want to return my order from last week"

### Common Development Commands

**Backend:**
```bash
# Install new packages
pip install package_name
pip freeze > requirements.txt

# Run with different port
PORT=8002 python main.py

# Run with debug logging
LOG_LEVEL=DEBUG python main.py
```

**Frontend:**
```bash
# Install new packages
npm install package_name

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

## 🐛 Troubleshooting

### Backend Issues

**Problem:** `ImportError: No module named 'fastapi'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Problem:** `OpenRouter API key not found`
```bash
# Solution: Check .env file
cat .env | grep OPENROUTER_API_KEY
```

**Problem:** `Port 8001 already in use`
```bash
# Solution: Use different port
PORT=8002 python main.py
```

### Frontend Issues

**Problem:** `npm: command not found`
```bash
# Solution: Install Node.js
# Visit https://nodejs.org/
```

**Problem:** `Module not found: uuid`
```bash
# Solution: Install missing types
npm install --save-dev @types/uuid
```

**Problem:** `Connection failed to backend`
- Check backend is running on port 8001
- Check CORS settings in backend .env
- Check Vite proxy configuration

### Integration Issues

**Problem:** `CORS error when calling API`
```bash
# Solution: Update backend .env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Problem:** `404 Not Found for API calls`
- Check backend routes in `src/api/main.py`
- Verify frontend API client URLs
- Check Vite proxy configuration

## 📊 Monitoring & Logs

### Backend Logs
```bash
# View logs with timestamp
python main.py | ts

# Save logs to file
python main.py > backend.log 2>&1
```

### Frontend Logs
- Open browser developer tools (F12)
- Check Console tab for errors
- Check Network tab for API calls

## 🚀 Production Deployment

### Backend Production
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Production
```bash
# Build for production
npm run build

# Serve static files
npm install -g serve
serve -s dist -p 3000
```

## 🔒 Security Notes

- **Never commit `.env` files** with real API keys
- **Use environment variables** in production
- **Set up proper CORS** for production domains
- **Use HTTPS** in production
- **Implement rate limiting** for API endpoints

## 📱 Quick Commands Summary

```bash
# Start everything (3 terminals)
Terminal 1: cd intelligent-ui-backend && python main.py
Terminal 2: cd intelligent-ui-frontend && npm run dev  
Terminal 3: cd . && npm run dev

# Or use the start scripts
chmod +x start-all.sh
./start-all.sh
```

---

**Next Steps:**
1. Start all services using the guide above
2. Test the integration by switching between traditional and AI modes
3. Try the example use cases: returns, product search, order status
4. Check the logs for any errors and resolve them