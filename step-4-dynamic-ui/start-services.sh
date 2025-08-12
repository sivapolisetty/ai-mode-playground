#!/bin/bash

# Step 4 Dynamic UI - Complete Services Startup Script
# This script starts all required services for Step 4 Dynamic UI POC

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_service() {
    echo -e "${PURPLE}[SERVICE]${NC} $1"
}

# Function to check if port is in use
check_port() {
    if lsof -i:$1 >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start after $((max_attempts * 2)) seconds"
    return 1
}

# Function to start Qdrant
start_qdrant() {
    print_service "Starting Qdrant Vector Database..."
    
    if check_port 6333; then
        print_warning "Qdrant is already running on port 6333"
        return 0
    fi
    
    print_status "Starting Qdrant container..."
    docker-compose -f docker-compose.qdrant.yml up -d
    
    if [ $? -eq 0 ]; then
        print_success "Qdrant container started"
    else
        print_error "Failed to start Qdrant container"
        return 1
    fi
    
    # Wait for Qdrant to be ready
    wait_for_service "http://localhost:6333/health" "Qdrant"
    
    print_success "Qdrant Vector Database ready at: http://localhost:6333"
    print_status "Qdrant Dashboard: http://localhost:6333/dashboard"
}

# Function to seed knowledge base
seed_knowledge_base() {
    print_service "Seeding Knowledge Base..."
    
    print_status "Activating virtual environment..."
    
    print_status "Running knowledge base seeder..."
    cd rag-service
    
    if ../venv/bin/python seeder.py; then
        print_success "Knowledge base seeded successfully"
        print_status "FAQ and business rules loaded into Qdrant"
    else
        print_error "Failed to seed knowledge base"
        cd ..
        return 1
    fi
    
    cd ..
}

# Function to start AI Backend
start_ai_backend() {
    print_service "Starting Step 4 AI Backend (Dynamic UI Generation)..."
    
    if check_port 8001; then
        print_warning "Port 8001 is already in use. Stopping existing service..."
        # Kill existing AI backend process
        pkill -f "python.*server.py" || true
        # Also kill by PID file if it exists
        if [ -f ".ai_backend.pid" ]; then
            AI_PID=$(cat .ai_backend.pid)
            if kill -0 $AI_PID 2>/dev/null; then
                kill $AI_PID
                print_status "Stopped AI backend process $AI_PID"
            fi
            rm -f .ai_backend.pid
        fi
        # Wait a moment for process to stop
        sleep 3
        
        # Check if port is still in use
        if check_port 8001; then
            print_error "Could not stop existing service on port 8001. Please manually stop it."
            return 1
        else
            print_success "Existing AI backend stopped successfully"
        fi
    fi
    
    print_status "Starting AI backend server..."
    cd ai-backend
    
    # Load LangFuse environment variables
    if [ -f ".env.langfuse" ]; then
        print_status "Loading LangFuse environment variables..."
        export $(cat .env.langfuse | grep -v '^#' | xargs)
    fi
    
    # Start in background
    nohup ../venv/bin/python server.py > ../ai-backend.log 2>&1 &
    AI_BACKEND_PID=$!
    
    cd ..
    
    # Wait for AI backend to be ready
    wait_for_service "http://localhost:8001/health" "AI Backend"
    
    print_success "Step 4 AI Backend ready at: http://localhost:8001"
    print_status "Features: Enhanced AI agent + RAG + Dynamic UI Generation"
    print_status "Logs: tail -f ai-backend.log"
    
    # Save PID for cleanup
    echo $AI_BACKEND_PID > .ai_backend.pid
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        return 1
    fi
    
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker daemon is not running"
        return 1
    fi
    
    # Check Python virtual environment
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Run './setup.sh setup' first."
        return 1
    fi
    
    # Check traditional backend
    if check_port 4000; then
        print_success "Traditional backend is running on port 4000"
    else
        print_warning "Traditional backend not running on port 4000"
        print_status "Please start it with: npm run dev"
    fi
    
    print_success "Prerequisites check completed"
}

# Function to show service status
show_status() {
    echo
    print_service "Service Status Summary"
    print_status "========================"
    
    # Check each service
    if check_port 4000; then
        print_success "✅ Traditional Backend: http://localhost:4000"
    else
        print_warning "❌ Traditional Backend: Not running (start with: npm run dev)"
    fi
    
    if check_port 6333; then
        print_success "✅ Qdrant Vector DB: http://localhost:6333"
        print_status "   Dashboard: http://localhost:6333/dashboard"
    else
        print_warning "❌ Qdrant Vector DB: Not running"
    fi
    
    if check_port 3001; then
        print_success "✅ LangFuse Observability: http://localhost:3001"
        print_status "   Agent traces, RAG analysis, UI generation monitoring"
    else
        print_error "❌ LangFuse: Not running (REQUIRED)"
        print_error "   Start LangFuse first: ./langfuse start"
    fi
    
    if check_port 8001; then
        print_success "✅ Step 4 AI Backend: http://localhost:8001"
    else
        print_warning "❌ Step 4 AI Backend: Not running"
    fi
    
    echo
    print_status "Test Dynamic UI Generation:"
    echo "curl -X POST http://localhost:8001/chat -H 'Content-Type: application/json' -d '{\"message\": \"Show me iPhone products\"}'"
    echo
    
    print_status "Available Endpoints:"
    echo "• Chat: http://localhost:8001/chat"
    echo "• Health: http://localhost:8001/health"
    echo "• UI Components: http://localhost:8001/ui/components"
    echo "• Knowledge Search: http://localhost:8001/knowledge/search"
    echo
}

# Function to stop services
stop_services() {
    print_service "Stopping Step 4 Services..."
    
    # Stop AI Backend by PID file
    if [ -f ".ai_backend.pid" ]; then
        AI_PID=$(cat .ai_backend.pid)
        if kill -0 $AI_PID 2>/dev/null; then
            kill $AI_PID
            print_success "AI Backend stopped (PID: $AI_PID)"
        fi
        rm -f .ai_backend.pid
    fi
    
    # Also kill any remaining Python server processes
    if pkill -f "python.*server.py"; then
        print_success "Stopped additional Python server processes"
    fi
    
    # Wait for processes to stop
    sleep 2
    
    # Stop Docker containers
    print_status "Stopping Docker containers..."
    docker-compose -f docker-compose.qdrant.yml down > /dev/null 2>&1
    
    # Stop LangFuse using dedicated manager
    if [ -f "$LANGFUSE_MANAGER" ]; then
        print_status "Stopping LangFuse via dedicated manager..."
        "$LANGFUSE_MANAGER" stop > /dev/null 2>&1
        print_status "LangFuse stopped via dedicated manager"
    fi
    
    print_success "Services stopped"
}

# LangFuse Manager Path
LANGFUSE_MANAGER="ai-backend/shared/observability/langfuse_manager.sh"

# Function to check existing LangFuse using dedicated manager
check_existing_langfuse() {
    print_service "Checking LangFuse via dedicated manager..."
    
    if [ -f "$LANGFUSE_MANAGER" ]; then
        "$LANGFUSE_MANAGER" health
        return $?
    else
        print_error "LangFuse manager script not found: $LANGFUSE_MANAGER"
        return 1
    fi
}

# Function to start LangFuse using dedicated manager
start_langfuse_with_manager() {
    print_service "Starting LangFuse via dedicated manager..."
    
    if [ -f "$LANGFUSE_MANAGER" ]; then
        "$LANGFUSE_MANAGER" start
        return $?
    else
        print_error "LangFuse manager script not found: $LANGFUSE_MANAGER"
        return 1
    fi
}

# Function to start LangFuse only using dedicated manager
start_langfuse_only() {
    print_service "🚀 Delegating to LangFuse Manager"
    print_service "================================="
    echo
    
    if [ -f "$LANGFUSE_MANAGER" ]; then
        # Use the dedicated LangFuse manager
        "$LANGFUSE_MANAGER" start
        if [ $? -eq 0 ]; then
            print_success "✨ Use dedicated LangFuse manager for all observability operations:"
            print_status "   $LANGFUSE_MANAGER status    # Check LangFuse status"
            print_status "   $LANGFUSE_MANAGER logs      # View LangFuse logs"
            print_status "   $LANGFUSE_MANAGER stop      # Stop LangFuse"
            echo
            return 0
        else
            return 1
        fi
    else
        print_error "LangFuse manager not found: $LANGFUSE_MANAGER"
        return 1
    fi
}

# Function to start all services including LangFuse
start_with_observability() {
    print_service "🚀 Step 4 Dynamic UI - Starting All Services (with LangFuse)"
    print_service "==========================================================="
    echo
    
    check_prerequisites || return 1
    start_qdrant || return 1
    start_langfuse_with_manager || print_warning "Continuing without LangFuse observability"
    seed_knowledge_base || return 1
    start_ai_backend || return 1
    
    show_status
    
    print_success "🎉 All Step 4 services are running (including LangFuse observability)!"
    echo
    print_status "🔍 Agent Behavior Analysis:"
    print_status "• LangFuse Dashboard: http://localhost:3001"
    print_status "• View agent traces, RAG operations, and UI generation patterns"
    print_status "• Monitor query classification and tool routing decisions"
    print_status "• Project: ui-agent (cme69v2i5000610rxp11ozgcv)"
    echo
    print_status "To stop services, run: ./start-services.sh stop"
    print_status "To check status, run: ./start-services.sh status"
    echo
    print_status "Keep this terminal open or services will stop."
    print_status "Press Ctrl+C to stop all services."
    
    # Wait for interrupt
    trap 'stop_services; exit 0' INT TERM
    
    while true; do
        sleep 10
        # Check if AI backend is still running
        if [ -f ".ai_backend.pid" ]; then
            AI_PID=$(cat .ai_backend.pid)
            if ! kill -0 $AI_PID 2>/dev/null; then
                print_error "AI Backend stopped unexpectedly"
                break
            fi
        fi
    done
}

# Function to start Step 4 services (requires LangFuse to be already running)
start_minimal() {
    print_service "🚀 Step 4 Dynamic UI - Starting Core Services"
    print_service "============================================="
    echo
    
    # Check if LangFuse is running first (STRICTLY REQUIRED)
    if check_port 3001; then
        print_success "✅ LangFuse detected on port 3001"
    else
        print_error "❌ LangFuse is not running. LangFuse is REQUIRED and must be started first."
        print_error "   Start LangFuse: ./langfuse start"
        print_error "   Or use: ./start-services.sh langfuse-only"
        print_error "🚫 Cannot proceed without LangFuse observability platform."
        return 1
    fi
    
    check_prerequisites || return 1
    start_qdrant || return 1
    seed_knowledge_base || return 1
    start_ai_backend || return 1
    
    show_status
    
    print_success "🎉 Step 4 services are running with LangFuse observability!"
    echo
    print_status "To stop services, run: ./start-services.sh stop"
    print_status "To check status, run: ./start-services.sh status"
    echo
    print_status "Keep this terminal open or services will stop."
    print_status "Press Ctrl+C to stop all services."
    
    # Wait for interrupt
    trap 'stop_services; exit 0' INT TERM
    
    while true; do
        sleep 10
        # Check if AI backend is still running
        if [ -f ".ai_backend.pid" ]; then
            AI_PID=$(cat .ai_backend.pid)
            if ! kill -0 $AI_PID 2>/dev/null; then
                print_error "AI Backend stopped unexpectedly"
                break
            fi
        fi
    done
}

# Function to enforce LangFuse requirement (replaces start_without_langfuse)
enforce_langfuse_requirement() {
    print_error "🚫 LangFuse observability is REQUIRED for Step 4 Dynamic UI"
    print_error "   Step 4 cannot operate without observability and tracing."
    print_error "   This is a core architectural requirement."
    echo
    print_status "To start LangFuse observability:"
    print_status "   ./langfuse start"
    print_status "   OR: ./start-services.sh langfuse-only"
    echo
    print_status "Then start Step 4 services:"
    print_status "   ./start-services.sh start"
    echo
    exit 1
}

# Main function
main() {
    case "${1:-start}" in
        "start")
            start_minimal
            ;;
        "no-langfuse")
            print_error "❌ 'no-langfuse' mode has been removed."
            print_error "   LangFuse observability is now REQUIRED for Step 4."
            print_error "   Start LangFuse first: ./langfuse start"
            exit 1
            ;;
        "langfuse-only")
            start_langfuse_only
            ;;
        "full"|"observability"|"langfuse")
            start_with_observability
            ;;
        "stop")
            stop_services
            ;;
        "status")
            show_status
            ;;
        "restart")
            print_service "Restarting Step 4 Services..."
            stop_services
            sleep 3
            print_status "Starting services again..."
            start_minimal
            ;;
        "restart-full")
            print_service "Restarting All Step 4 Services (with LangFuse)..."
            stop_services
            sleep 3
            print_status "Starting all services again..."
            start_with_observability
            ;;
        "qdrant")
            start_qdrant
            ;;
        "seed")
            seed_knowledge_base
            ;;
        "ai")
            start_ai_backend
            show_status
            ;;
        "help")
            echo "Usage: ./start-services.sh [command]"
            echo
            echo "Commands:"
            echo "  start         Start Step 4 services (REQUIRES LangFuse running on port 3001)"
            echo "  langfuse-only Start ONLY LangFuse observability platform"
            echo "  full          Start all services including LangFuse observability"
            echo "  stop          Stop all services"
            echo "  status        Show service status"
            echo "  restart       Restart Step 4 services"
            echo "  restart-full  Restart all services including LangFuse"
            echo "  qdrant        Start only Qdrant"
            echo "  seed          Seed knowledge base"
            echo "  ai            Start only AI backend"
            echo "  help          Show this help"
            echo
            echo "⚠️  IMPORTANT: LangFuse observability is REQUIRED for all Step 4 operations."
            echo
            echo "Recommended workflow:"
            echo "  1. ./start-services.sh langfuse-only    (in terminal 1)"
            echo "  2. ./start-services.sh start            (in terminal 2)"
            echo
            echo "Or start everything together:"
            echo "  ./start-services.sh full"
            echo
            echo "Dedicated LangFuse Management:"
            echo "  ./langfuse start     # Start LangFuse only (convenient shortcut)"
            echo "  ./langfuse status    # Check LangFuse status"
            echo "  ./langfuse stop      # Stop LangFuse"
            echo "  ./langfuse logs      # View LangFuse logs"
            echo
            echo "Full path: $LANGFUSE_MANAGER [command]"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Run './start-services.sh help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"