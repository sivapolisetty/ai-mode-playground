#!/bin/bash

# LangFuse Setup Script
# This script sets up LangFuse for observability and tracing

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
setup_langfuse() {
    print_status "Setting up LangFuse for observability..."
    
    # Check if Docker is available
    if ! command_exists docker; then
        print_error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Get a copy of the latest Langfuse repository
    print_status "Cloning LangFuse repository..."
    if [ -d "langfuse" ]; then
        print_warning "LangFuse directory already exists. Pulling latest changes..."
        cd langfuse
        git pull origin main
        cd ..
    else
        git clone https://github.com/langfuse/langfuse.git
    fi
    
    # Navigate to langfuse directory
    cd langfuse
    
    # Run the langfuse docker compose
    print_status "Starting LangFuse with Docker Compose..."
    docker compose up -d
    
    if [ $? -eq 0 ]; then
        print_success "LangFuse started successfully!"
        echo
        print_status "LangFuse is available at: http://localhost:3000"
        print_status "Create an account and get your API keys from the settings."
        echo
        print_status "After getting your API keys, add them to your .env file:"
        echo "  LANGFUSE_SECRET_KEY=your-secret-key"
        echo "  LANGFUSE_PUBLIC_KEY=your-public-key"
        echo "  LANGFUSE_HOST=http://localhost:3000"
    else
        print_error "Failed to start LangFuse with Docker Compose"
        exit 1
    fi
    
    cd ..
}

# Function to stop LangFuse
stop_langfuse() {
    print_status "Stopping LangFuse..."
    
    if [ -d "langfuse" ]; then
        cd langfuse
        docker compose down
        print_success "LangFuse stopped"
        cd ..
    else
        print_warning "LangFuse directory not found"
    fi
}

# Function to show LangFuse status
status_langfuse() {
    print_status "Checking LangFuse status..."
    
    if [ -d "langfuse" ]; then
        cd langfuse
        docker compose ps
        cd ..
    else
        print_warning "LangFuse directory not found"
    fi
}

# Main function
main() {
    echo
    print_status "🔍 LangFuse Setup Script"
    print_status "========================"
    echo
    
    case "${1:-setup}" in
        "setup")
            setup_langfuse
            ;;
        "start")
            if [ -d "langfuse" ]; then
                cd langfuse
                docker compose up -d
                print_success "LangFuse started"
                cd ..
            else
                print_error "LangFuse not found. Run './setup-langfuse.sh setup' first"
            fi
            ;;
        "stop")
            stop_langfuse
            ;;
        "status")
            status_langfuse
            ;;
        "help")
            echo "Usage: ./setup-langfuse.sh [command]"
            echo
            echo "Commands:"
            echo "  setup    Clone and setup LangFuse (default)"
            echo "  start    Start LangFuse services"
            echo "  stop     Stop LangFuse services"
            echo "  status   Show LangFuse service status"
            echo "  help     Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Run './setup-langfuse.sh help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"