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
    
    if check_port 3000; then
        print_success "✅ LangFuse Observability: http://localhost:3000"
        print_status "   Agent traces, RAG analysis, UI generation monitoring"
    else
        print_warning "❌ LangFuse: Not running (optional)"
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
    
    if [ -f "docker-compose.langfuse.yml" ]; then
        docker-compose -f docker-compose.langfuse.yml down > /dev/null 2>&1
        print_status "LangFuse containers stopped"
    fi
    
    print_success "Services stopped"
}

# Function to check existing LangFuse (running on port 3000)
check_existing_langfuse() {
    print_service "Checking Existing LangFuse Observability Platform..."
    
    if check_port 3000; then
        print_success "LangFuse is running on port 3000"
        print_status "Dashboard: http://localhost:3000"
        return 0
    else
        print_warning "LangFuse not found on port 3000. Please start your existing LangFuse instance."
        return 1
    fi
    
    # Check if LangFuse docker-compose exists
    if [ ! -f "docker-compose.langfuse.yml" ]; then
        print_status "Creating LangFuse docker-compose configuration..."
        cat > docker-compose.langfuse.yml << 'EOF'
version: '3.8'

services:
  langfuse-db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: langfuse
      POSTGRES_DB: langfuse
    volumes:
      - langfuse_db:/var/lib/postgresql/data
    ports:
      - "5433:5432"  # Use different port to avoid conflicts

  langfuse:
    image: ghcr.io/langfuse/langfuse:latest
    restart: always
    depends_on:
      - langfuse-db
    ports:
      - "3001:3000"
    environment:
      DATABASE_URL: postgresql://langfuse:langfuse@langfuse-db:5432/langfuse
      NEXTAUTH_SECRET: your-secret-key-here-step4-ui
      NEXTAUTH_URL: http://localhost:3001
      TELEMETRY_ENABLED: false
      LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES: true
    volumes:
      - langfuse_uploads:/app/uploads

volumes:
  langfuse_db:
  langfuse_uploads:
EOF
        print_success "LangFuse configuration created (PostgreSQL on port 5433)"
    fi
    
    print_status "Starting LangFuse containers..."
    docker-compose -f docker-compose.langfuse.yml up -d
    
    if [ $? -eq 0 ]; then
        print_success "LangFuse containers started"
        wait_for_service "http://localhost:3001" "LangFuse"
        print_success "LangFuse ready at: http://localhost:3001"
        print_status "Default credentials will be created on first visit"
        print_status "Features: Agent tracing, RAG analysis, UI generation monitoring"
    else
        print_warning "LangFuse failed to start (optional service, continuing without it)"
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
    check_existing_langfuse || print_warning "Continuing without LangFuse observability"
    seed_knowledge_base || return 1
    start_ai_backend || return 1
    
    show_status
    
    print_success "🎉 All Step 4 services are running (including LangFuse observability)!"
    echo
    print_status "🔍 Agent Behavior Analysis:"
    print_status "• LangFuse Dashboard: http://localhost:3000"
    print_status "• View agent traces, RAG operations, and UI generation patterns"
    print_status "• Monitor query classification and tool routing decisions"
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

# Function to start minimal services (no LangFuse)
start_minimal() {
    print_service "🚀 Step 4 Dynamic UI - Starting Core Services"
    print_service "============================================="
    echo
    
    check_prerequisites || return 1
    start_qdrant || return 1
    seed_knowledge_base || return 1
    start_ai_backend || return 1
    
    show_status
    
    print_success "🎉 Step 4 services are running!"
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

# Main function
main() {
    case "${1:-start}" in
        "start")
            start_minimal
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
            echo "  start         Start core services (Qdrant + AI Backend)"
            echo "  full          Start all services including LangFuse observability"
            echo "  langfuse      Same as 'full' - starts with LangFuse"
            echo "  stop          Stop all services"
            echo "  status        Show service status"
            echo "  restart       Restart core services (stops existing automatically)"
            echo "  restart-full  Restart all services including LangFuse"
            echo "  qdrant        Start only Qdrant"
            echo "  seed          Seed knowledge base"
            echo "  ai            Start only AI backend"
            echo "  help          Show this help"
            echo
            echo "For agent behavior analysis, use: ./start-services.sh full"
            echo "If services are already running, use: ./start-services.sh restart"
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