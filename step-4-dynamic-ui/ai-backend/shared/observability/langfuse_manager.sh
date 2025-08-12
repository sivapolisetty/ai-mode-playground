#!/bin/bash

# LangFuse Observability Management Script
# Dedicated script for managing LangFuse observability platform
# Part of Step 4 Dynamic UI - separated from main application startup

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
    echo -e "${PURPLE}[LANGFUSE]${NC} $1"
}

# Get the Step 4 root directory (3 levels up from shared/observability/)
STEP4_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

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

# Function to check LangFuse health
check_langfuse_health() {
    print_service "Checking LangFuse Health..."
    
    if check_port 3000; then
        print_success "✅ LangFuse is running on port 3000"
        
        # Test API endpoint
        if curl -s "http://localhost:3000/api/public/health" > /dev/null 2>&1; then
            print_success "✅ LangFuse API is responding"
            return 0
        else
            print_warning "⚠️  LangFuse port is open but API not responding"
            return 1
        fi
    else
        print_warning "❌ LangFuse is not running on port 3000"
        return 1
    fi
}

# Function to start LangFuse
start_langfuse() {
    print_service "🚀 Starting LangFuse Observability Platform"
    print_service "==========================================="
    echo
    
    # Check if already running
    if check_langfuse_health; then
        print_success "🎉 LangFuse is already running!"
        show_langfuse_info
        return 0
    fi
    
    print_status "Detecting LangFuse configuration..."
    
    # Find available docker-compose file
    cd "$STEP4_ROOT"
    
    if [ -f "docker-compose.langfuse-v2.yml" ]; then
        LANGFUSE_COMPOSE="docker-compose.langfuse-v2.yml"
        print_status "Using LangFuse v2 configuration"
    elif [ -f "docker-compose.langfuse.yml" ]; then
        LANGFUSE_COMPOSE="docker-compose.langfuse.yml"
        print_status "Using default LangFuse configuration"
    else
        print_error "❌ No LangFuse docker-compose configuration found"
        print_error "   Expected: docker-compose.langfuse-v2.yml or docker-compose.langfuse.yml"
        return 1
    fi
    
    print_status "Starting LangFuse containers with $LANGFUSE_COMPOSE..."
    docker-compose -f "$LANGFUSE_COMPOSE" up -d
    
    if [ $? -eq 0 ]; then
        print_success "✅ LangFuse containers started"
        
        # Wait for service to be ready
        wait_for_service "http://localhost:3000/api/public/health" "LangFuse"
        
        if [ $? -eq 0 ]; then
            print_success "🎉 LangFuse is ready!"
            show_langfuse_info
            return 0
        else
            print_error "❌ LangFuse failed to become ready"
            return 1
        fi
    else
        print_error "❌ Failed to start LangFuse containers"
        return 1
    fi
}

# Function to stop LangFuse
stop_langfuse() {
    print_service "🛑 Stopping LangFuse Observability Platform"
    print_service "==========================================="
    echo
    
    cd "$STEP4_ROOT"
    
    # Stop all possible LangFuse configurations
    if [ -f "docker-compose.langfuse-v2.yml" ]; then
        print_status "Stopping LangFuse v2 containers..."
        docker-compose -f docker-compose.langfuse-v2.yml down > /dev/null 2>&1
    fi
    
    if [ -f "docker-compose.langfuse.yml" ]; then
        print_status "Stopping default LangFuse containers..."
        docker-compose -f docker-compose.langfuse.yml down > /dev/null 2>&1
    fi
    
    # Wait a moment for containers to stop
    sleep 3
    
    if check_port 3000; then
        print_warning "⚠️  Port 3000 still in use - some containers may still be running"
        return 1
    else
        print_success "✅ LangFuse stopped successfully"
        return 0
    fi
}

# Function to restart LangFuse
restart_langfuse() {
    print_service "🔄 Restarting LangFuse Observability Platform"
    print_service "============================================="
    echo
    
    stop_langfuse
    sleep 3
    start_langfuse
}

# Function to show LangFuse information
show_langfuse_info() {
    echo
    print_success "🎉 LangFuse Observability Platform Ready!"
    echo
    print_status "📊 Dashboard: http://localhost:3000"
    print_status "🔗 Project: step4-dynamic-ui"
    print_status "📝 Features: Agent tracing, RAG analysis, UI generation monitoring"
    echo
    print_status "🔑 API Configuration:"
    print_status "   Public Key: pk-lf-2dece1a4-10e4-4113-a823-105c85e9ce9e"
    print_status "   Secret Key: sk-lf-4a73a915-faee-4483-ac0d-79e5fc52d002"
    print_status "   Host: http://localhost:3000"
    echo
    print_status "✨ Now you can start Step 4 with observability:"
    print_status "   cd $STEP4_ROOT"
    print_status "   ./start-services.sh start"
    echo
}

# Function to show LangFuse status
show_status() {
    print_service "📊 LangFuse Status"
    print_service "=================="
    echo
    
    if check_langfuse_health; then
        print_success "✅ LangFuse: Running on port 3000"
        print_status "   Dashboard: http://localhost:3000"
        print_status "   API Health: http://localhost:3000/api/public/health"
        echo
        
        # Test API connection with credentials
        print_status "🔍 Testing API connection..."
        if curl -s -H "Content-Type: application/json" "http://localhost:3000/api/public/health" | grep -q "ok"; then
            print_success "✅ API connection successful"
        else
            print_warning "⚠️  API connection test failed"
        fi
        echo
        
        print_status "🚀 Ready for Step 4 integration"
    else
        print_warning "❌ LangFuse: Not running"
        echo
        print_status "To start LangFuse:"
        print_status "   $0 start"
        echo
    fi
}

# Function to view logs
view_logs() {
    print_service "📜 LangFuse Container Logs"
    print_service "=========================="
    echo
    
    cd "$STEP4_ROOT"
    
    if [ -f "docker-compose.langfuse-v2.yml" ]; then
        docker-compose -f docker-compose.langfuse-v2.yml logs --tail=50 -f
    elif [ -f "docker-compose.langfuse.yml" ]; then
        docker-compose -f docker-compose.langfuse.yml logs --tail=50 -f
    else
        print_error "No LangFuse configuration found"
        return 1
    fi
}

# Function to cleanup (remove containers and volumes)
cleanup_langfuse() {
    print_service "🧹 Cleaning Up LangFuse"
    print_service "======================="
    echo
    
    cd "$STEP4_ROOT"
    
    print_status "Stopping and removing containers..."
    if [ -f "docker-compose.langfuse-v2.yml" ]; then
        docker-compose -f docker-compose.langfuse-v2.yml down --volumes --remove-orphans
    fi
    
    if [ -f "docker-compose.langfuse.yml" ]; then
        docker-compose -f docker-compose.langfuse.yml down --volumes --remove-orphans
    fi
    
    print_status "Removing LangFuse-related Docker resources..."
    
    # Remove LangFuse images (optional - uncomment if needed)
    # docker rmi $(docker images | grep langfuse | awk '{print $3}') 2>/dev/null || true
    
    print_success "✅ LangFuse cleanup completed"
    echo
    print_status "To start fresh: $0 start"
}

# Main function
main() {
    case "${1:-help}" in
        "start")
            start_langfuse
            ;;
        "stop")
            stop_langfuse
            ;;
        "restart")
            restart_langfuse
            ;;
        "status")
            show_status
            ;;
        "health")
            check_langfuse_health
            ;;
        "logs")
            view_logs
            ;;
        "cleanup")
            cleanup_langfuse
            ;;
        "info")
            show_langfuse_info
            ;;
        "help"|*)
            echo "LangFuse Observability Management Script"
            echo "========================================"
            echo
            echo "Usage: $0 [command]"
            echo
            echo "Commands:"
            echo "  start      Start LangFuse observability platform"
            echo "  stop       Stop LangFuse containers"
            echo "  restart    Restart LangFuse platform"
            echo "  status     Show LangFuse status and connection info"
            echo "  health     Check if LangFuse is healthy"
            echo "  logs       View LangFuse container logs (follow mode)"
            echo "  cleanup    Stop and remove all LangFuse containers/volumes"
            echo "  info       Show connection and project information"
            echo "  help       Show this help"
            echo
            echo "Examples:"
            echo "  $0 start     # Start LangFuse for Step 4 observability"
            echo "  $0 status    # Check if LangFuse is running"
            echo "  $0 logs      # View real-time logs"
            echo
            echo "After starting LangFuse, you can start Step 4 with:"
            echo "  cd $STEP4_ROOT && ./start-services.sh start"
            echo
            ;;
    esac
}

# Run main function with all arguments
main "$@"