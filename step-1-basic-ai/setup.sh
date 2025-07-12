#!/bin/bash

# Step 1: Basic AI Mode Setup Script
# This script sets up the basic AI mode with LLM flexibility

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

# Function to check Python version
check_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        
        # Check if Python version is 3.8 or higher using Python itself
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Function to setup virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_success "Pip upgraded"
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Install shared common dependencies first
    print_status "Installing shared common dependencies..."
    if pip install -r ../shared/requirements-common.txt; then
        print_success "Shared dependencies installed"
    else
        print_warning "Some shared packages failed to install. Trying with --no-cache-dir..."
        if pip install --no-cache-dir -r ../shared/requirements-common.txt; then
            print_success "Shared dependencies installed (with --no-cache-dir)"
        else
            print_error "Shared dependencies failed. Please install Rust compiler:"
            print_error "  brew install rust  # on macOS"
            print_error "  or visit https://rustup.rs for other platforms"
            print_error "Then try running the setup again."
            return 1
        fi
    fi
    
    # Check if there are step-specific requirements
    if [ -f "ai-backend/requirements.txt" ]; then
        cd ai-backend
        
        # Check if there are actual dependencies (not just comments)
        if grep -v '^#' requirements.txt | grep -v '^$' | head -1 | grep -q '\S'; then
            print_status "Installing step-specific dependencies..."
            if pip install -r requirements.txt; then
                print_success "Step-specific dependencies installed"
            else
                print_warning "Step-specific packages failed to install"
            fi
        else
            print_status "No step-specific dependencies needed"
        fi
        
        cd ..
        print_success "Python dependencies installation complete"
    else
        print_warning "No step-specific requirements.txt found"
    fi
}

# Function to setup environment configuration
setup_env_config() {
    print_status "Setting up environment configuration..."
    
    cd ai-backend
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Environment file created from template"
        
        echo
        print_warning "Please configure your .env file with your preferred LLM provider:"
        echo "  • For Ollama (local): Set LLM_PROVIDER=ollama"
        echo "  • For OpenRouter (cloud): Set LLM_PROVIDER=openrouter and add API key"
        echo
        
        read -p "Do you want to configure LLM provider now? (y/n): " configure_llm
        
        if [[ $configure_llm =~ ^[Yy]$ ]]; then
            configure_llm_provider
            echo
            configure_langfuse
        else
            print_warning "You can configure LLM provider later by editing ai-backend/.env"
        fi
    else
        print_warning ".env file already exists"
    fi
    
    cd ..
}

# Function to configure LLM provider
configure_llm_provider() {
    echo
    print_status "LLM Provider Configuration"
    echo "1) Ollama (Local - Private, Free)"
    echo "2) OpenRouter (Cloud - Scalable, Paid)"
    echo
    
    read -p "Choose LLM provider (1 or 2): " llm_choice
    
    case $llm_choice in
        1)
            configure_ollama
            ;;
        2)
            configure_openrouter
            ;;
        *)
            print_warning "Invalid choice. Using default Ollama configuration."
            configure_ollama
            ;;
    esac
}

# Function to configure Ollama
configure_ollama() {
    print_status "Configuring Ollama (Local LLM)..."
    
    # Update .env for Ollama
    sed -i.bak 's/LLM_PROVIDER=.*/LLM_PROVIDER=ollama/' .env
    
    # Standardize to Gemma2:12B for consistency across all steps
    echo
    print_status "Using standardized Gemma2 12B model for consistency"
    OLLAMA_MODEL="gemma2:12b"
    
    # Option to override if needed
    read -p "Use different model? (y/n, default: n): " use_different
    
    if [[ $use_different =~ ^[Yy]$ ]]; then
        echo "1) gemma2:2b (Faster, lower memory usage)"
        echo "2) gemma2:9b (Good balance)"
        echo "3) gemma2:12b (Best quality - recommended)"
        echo
        
        read -p "Choose model (1-3, default: 3): " model_choice
        
        case $model_choice in
            1)
                OLLAMA_MODEL="gemma2:2b"
                ;;
            2)
                OLLAMA_MODEL="gemma2:9b"
                ;;
            *)
                OLLAMA_MODEL="gemma2:12b"
                ;;
        esac
    fi
    
    sed -i.bak "s/OLLAMA_MODEL=.*/OLLAMA_MODEL=$OLLAMA_MODEL/" .env
    
    print_success "Ollama configuration updated in .env with model: $OLLAMA_MODEL"
    
    # Check if Ollama is installed
    if command_exists ollama; then
        print_success "Ollama is installed"
        
        # Check if Ollama service is running
        if pgrep -f "ollama serve" > /dev/null; then
            print_success "Ollama service is running"
        else
            print_status "Starting Ollama service..."
            ollama serve &
            sleep 2
            print_success "Ollama service started"
        fi
        
        # Check if selected Gemma model is available
        if ollama list | grep -q "$OLLAMA_MODEL"; then
            print_success "$OLLAMA_MODEL model is available"
        else
            print_status "Downloading $OLLAMA_MODEL model (this may take a while)..."
            ollama pull "$OLLAMA_MODEL"
            print_success "$OLLAMA_MODEL model downloaded"
        fi
    else
        print_warning "Ollama not found. Installing Ollama..."
        install_ollama
    fi
}

# Function to install Ollama
install_ollama() {
    print_status "Installing Ollama..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install ollama
        else
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        print_error "Unsupported OS for automatic Ollama installation"
        print_warning "Please install Ollama manually from https://ollama.ai"
        return 1
    fi
    
    print_success "Ollama installed"
    
    # Start Ollama service
    ollama serve &
    sleep 2
    
    # Pull Gemma model (default to 2:12b)
    print_status "Downloading Gemma2 12B model..."
    ollama pull gemma2:12b
    print_success "Gemma2 12B model ready"
}

# Function to configure OpenRouter
configure_openrouter() {
    print_status "Configuring OpenRouter (Cloud LLM)..."
    
    # Update .env for OpenRouter
    sed -i.bak 's/LLM_PROVIDER=.*/LLM_PROVIDER=openrouter/' .env
    
    echo
    read -p "Enter your OpenRouter API key: " openrouter_key
    
    if [ -n "$openrouter_key" ]; then
        sed -i.bak "s/OPENROUTER_API_KEY=.*/OPENROUTER_API_KEY=$openrouter_key/" .env
        print_success "OpenRouter API key configured"
    else
        print_warning "No API key provided. Please update OPENROUTER_API_KEY in .env file"
    fi
    
    # Ask for model preference
    echo
    print_status "Available OpenRouter models:"
    echo "1) google/gemini-2.5-flash (Fast, Good)"
    echo "2) google/gemini-2.0-flash-exp (Experimental, Advanced)"
    echo "3) anthropic/claude-3.5-sonnet (High Quality)"
    echo
    
    read -p "Choose model (1-3, default: 1): " model_choice
    
    case $model_choice in
        2)
            sed -i.bak 's/OPENROUTER_MODEL=.*/OPENROUTER_MODEL=google\/gemini-2.0-flash-exp/' .env
            ;;
        3)
            sed -i.bak 's/OPENROUTER_MODEL=.*/OPENROUTER_MODEL=anthropic\/claude-3.5-sonnet/' .env
            ;;
        *)
            sed -i.bak 's/OPENROUTER_MODEL=.*/OPENROUTER_MODEL=google\/gemini-2.5-flash/' .env
            ;;
    esac
    
    print_success "OpenRouter configuration complete"
}

# Function to configure LangFuse
configure_langfuse() {
    print_status "Setting up LangFuse for observability..."
    
    echo
    read -p "Do you want to start LangFuse with the application? (y/n, default: y): " start_langfuse
    
    if [[ $start_langfuse =~ ^[Nn]$ ]]; then
        print_status "Skipping LangFuse setup"
        return 0
    fi
    
    setup_langfuse_docker
}


# Function to setup LangFuse with Docker
setup_langfuse_docker() {
    print_status "Setting up LangFuse with Docker..."
    
    # Check if Docker is available
    if ! command_exists docker; then
        print_error "Docker not found. Please install Docker first."
        return 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker and try again."
        print_warning "To start Docker:"
        echo "  • Open Docker Desktop application"
        echo "  • Or run: sudo systemctl start docker (on Linux)"
        return 1
    fi
    
    # Check if observability directory exists
    if [ ! -d "../../observability" ]; then
        print_error "Observability directory not found. Please run this from the correct location."
        return 1
    fi
    
    # Start LangFuse using the observability docker-compose
    print_status "Starting LangFuse with Docker..."
    cd ../../observability
    docker-compose -f docker-compose.langfuse.yml up -d
    cd - > /dev/null
    
    if [ $? -eq 0 ]; then
        print_success "LangFuse started successfully!"
        echo
        print_status "LangFuse is available at: http://localhost:3001"
        print_status "Create an account and get your API keys from the settings."
        echo
        
        # Set default configuration
        # Update .env with local LangFuse settings
        if grep -q "LANGFUSE_HOST=" .env; then
            sed -i.bak "s|LANGFUSE_HOST=.*|LANGFUSE_HOST=http://localhost:3001|" .env
        else
            echo "" >> .env
            echo "# LangFuse Configuration" >> .env
            echo "LANGFUSE_HOST=http://localhost:3001" >> .env
        fi
        
        print_success "LangFuse Docker setup completed!"
        echo
        print_status "LangFuse will be available at: http://localhost:3001"
        print_status "Create an account there and get your API keys, then add them to .env:"
        echo "  LANGFUSE_SECRET_KEY=your-secret-key"
        echo "  LANGFUSE_PUBLIC_KEY=your-public-key"
    else
        print_error "Failed to start LangFuse with Docker"
        return 1
    fi
}

# Function to start the server
start_server() {
    print_status "Starting AI Backend Server..."
    
    cd ai-backend
    
    # Check if virtual environment is activated
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Virtual environment is active"
    else
        print_warning "Activating virtual environment..."
        source ../venv/bin/activate
    fi
    
    # Check if traditional backend is running
    if curl -s http://localhost:4000/health > /dev/null; then
        print_success "Traditional backend is running"
    else
        print_warning "Traditional backend not detected at http://localhost:4000"
        print_warning "Make sure to start your traditional e-commerce backend first"
    fi
    
    print_status "Starting server on http://localhost:8001..."
    python server.py
}

# Function to run demo
run_demo() {
    print_status "Running Step 1 Demo..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run demo script
    python demo.py
}

# Function to run tests
run_tests() {
    print_status "Running basic connectivity tests..."
    
    # Test health endpoint
    if curl -s http://localhost:8001/health > /dev/null; then
        print_success "Health endpoint is accessible"
    else
        print_error "Health endpoint not accessible"
        return 1
    fi
    
    # Test tools endpoint
    if curl -s http://localhost:8001/tools > /dev/null; then
        print_success "Tools endpoint is accessible"
    else
        print_error "Tools endpoint not accessible"
        return 1
    fi
    
    # Test chat endpoint
    response=$(curl -s -X POST http://localhost:8001/chat \
        -H "Content-Type: application/json" \
        -d '{"message": "hello"}')
    
    if echo "$response" | grep -q "message"; then
        print_success "Chat endpoint is working"
    else
        print_error "Chat endpoint not working"
        return 1
    fi
    
    print_success "All tests passed!"
}

# Main function
main() {
    echo
    print_status "🚀 Step 1: Basic AI Mode Setup"
    print_status "================================"
    echo
    
    # Check requirements
    print_status "Checking requirements..."
    
    if ! check_python; then
        print_error "Python 3.8+ is required"
        exit 1
    fi
    
    # Setup based on command line argument
    case "${1:-setup}" in
        "setup")
            setup_venv
            install_python_deps
            setup_env_config
            
            # Offer LangFuse configuration if not already done
            if [ -f "ai-backend/.env" ] && ! grep -q "LANGFUSE_" ai-backend/.env; then
                echo
                read -p "Do you want to configure LangFuse for enhanced observability? (y/n): " configure_langfuse_now
                if [[ $configure_langfuse_now =~ ^[Yy]$ ]]; then
                    cd ai-backend
                    configure_langfuse
                    cd ..
                fi
            fi
            
            print_success "Setup complete!"
            echo
            print_status "Next steps:"
            echo "  1. Run: ./setup.sh start    # Start the server"
            echo "  2. Run: ./setup.sh demo     # Run demo"
            echo "  3. Run: ./setup.sh test     # Run tests"
            ;;
        "start")
            start_server
            ;;
        "demo")
            run_demo
            ;;
        "test")
            run_tests
            ;;
        "help")
            echo "Usage: ./setup.sh [command]"
            echo
            echo "Commands:"
            echo "  setup    Setup environment and dependencies (default)"
            echo "  start    Start the AI backend server"
            echo "  demo     Run interactive demo"
            echo "  test     Run connectivity tests"
            echo "  help     Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Run './setup.sh help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"