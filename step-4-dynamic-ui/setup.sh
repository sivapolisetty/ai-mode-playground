#!/bin/bash

# Step 2: RAG Integration Setup Script
# This script sets up the RAG integration with Qdrant vector database

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

# Function to check Docker
check_docker() {
    if ! command_exists docker; then
        print_error "Docker not found. Please install Docker first."
        return 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker."
        return 1
    fi
    
    print_success "Docker is available and running"
    return 0
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
    
    # Check Python version and warn if 3.13+
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)"; then
        print_warning "Python 3.13+ detected. Some packages may have compatibility issues."
        print_status "Using latest compatible versions..."
    fi
    
    # Install shared common dependencies first
    print_status "Installing shared common dependencies..."
    if pip install -r ../shared/requirements-common.txt; then
        print_success "Shared dependencies installed"
    else
        print_warning "Some shared packages failed to install. Trying with --no-cache-dir..."
        if pip install --no-cache-dir -r ../shared/requirements-common.txt; then
            print_success "Shared dependencies installed (with --no-cache-dir)"
        else
            print_warning "Shared dependencies failed. Continuing with core dependencies..."
        fi
    fi
    
    # Install RAG service dependencies
    print_status "Installing RAG service dependencies..."
    cd rag-service
    if pip install -r requirements.txt; then
        print_success "RAG service dependencies installed"
    else
        print_warning "Some packages failed. Trying individual installation..."
        pip install --no-cache-dir qdrant-client==1.14.3
        pip install --no-cache-dir sentence-transformers
        pip install --no-cache-dir python-dotenv loguru
        print_success "Core RAG dependencies installed"
    fi
    cd ..
    
    # Install AI backend dependencies
    print_status "Installing AI backend dependencies..."
    cd ai-backend
    if pip install -r requirements.txt; then
        print_success "AI backend dependencies installed"
    else
        print_warning "Some packages failed. Trying core dependencies..."
        pip install --no-cache-dir fastapi uvicorn pydantic python-dotenv httpx
        pip install --no-cache-dir qdrant-client==1.14.3 loguru
        print_success "Core AI backend dependencies installed"
    fi
    cd ..
    
    print_success "Python dependencies installation completed"
}

# Function to setup Qdrant
setup_qdrant() {
    print_status "Setting up Qdrant vector database..."
    
    # Start Qdrant with Docker
    print_status "Starting Qdrant container..."
    docker-compose -f docker-compose.qdrant.yml up -d
    
    if [ $? -eq 0 ]; then
        print_success "Qdrant container started successfully"
        print_status "Qdrant is available at: http://localhost:6333"
        
        # Wait for Qdrant to be ready
        print_status "Waiting for Qdrant to be ready..."
        sleep 10
        
        # Test Qdrant connection
        for i in {1..10}; do
            if curl -s http://localhost:6333/health > /dev/null; then
                print_success "Qdrant is healthy and ready"
                break
            else
                print_status "Waiting for Qdrant... ($i/10)"
                sleep 5
            fi
        done
        
        return 0
    else
        print_error "Failed to start Qdrant container"
        return 1
    fi
}

# Function to seed knowledge base
seed_knowledge_base() {
    print_status "Seeding knowledge base into Qdrant..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run seeder
    cd rag-service
    python seeder.py
    
    if [ $? -eq 0 ]; then
        print_success "Knowledge base seeded successfully"
        print_status "FAQ and business rules loaded into Qdrant"
    else
        print_error "Failed to seed knowledge base"
        return 1
    fi
    
    cd ..
}

# Function to setup environment configuration
setup_env_config() {
    print_status "Setting up environment configuration..."
    
    cd ai-backend
    
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma2:12b
OLLAMA_TEMPERATURE=0.1
OLLAMA_TOP_P=0.9
OLLAMA_MAX_TOKENS=2048

# OpenRouter Configuration (alternative)
OPENROUTER_API_KEY=
OPENROUTER_MODEL=google/gemini-2.0-flash-exp
OPENROUTER_TEMPERATURE=0.1
OPENROUTER_MAX_TOKENS=2048

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Traditional API Configuration
TRADITIONAL_API_URL=http://localhost:4000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=detailed

# LangFuse Configuration (optional)
LANGFUSE_HOST=http://localhost:3001
LANGFUSE_SECRET_KEY=
LANGFUSE_PUBLIC_KEY=

# Server Configuration
PORT=8001
EOF
        print_success "Environment file created"
        
        echo
        print_warning "Please configure your .env file with your preferred LLM provider:"
        echo "  • For Ollama (local): Set LLM_PROVIDER=ollama"
        echo "  • For OpenRouter (cloud): Set LLM_PROVIDER=openrouter and add API key"
        echo
        
        read -p "Do you want to configure LLM provider now? (y/n): " configure_llm
        
        if [[ $configure_llm =~ ^[Yy]$ ]]; then
            configure_llm_provider
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
        
        # Check if Gemma model is available
        if ollama list | grep -q "gemma2:12b"; then
            print_success "Gemma2 12B model is available"
        else
            print_status "Downloading Gemma2 12B model (this may take a while)..."
            ollama pull gemma2:12b
            print_success "Gemma2 12B model downloaded"
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
    
    # Pull Gemma model
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
    
    print_success "OpenRouter configuration complete"
}

# Function to start the services
start_services() {
    print_status "Starting all services..."
    
    # Start Qdrant if not running
    if ! curl -s http://localhost:6333/health > /dev/null; then
        print_status "Starting Qdrant..."
        docker-compose -f docker-compose.qdrant.yml up -d
        sleep 5
    fi
    
    # Check if traditional backend is running
    if curl -s http://localhost:4000/health > /dev/null; then
        print_success "Traditional backend is running"
    else
        print_warning "Traditional backend not detected at http://localhost:4000"
        print_warning "Make sure to start your traditional e-commerce backend first"
    fi
    
    # Start AI backend
    cd ai-backend
    
    # Check if virtual environment is activated
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Virtual environment is active"
    else
        print_warning "Activating virtual environment..."
        source ../venv/bin/activate
    fi
    
    print_status "Starting AI backend server on http://localhost:8001..."
    python server.py
}

# Function to run tests
run_tests() {
    print_status "Running RAG integration tests..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Test Qdrant connection
    if curl -s http://localhost:6333/health > /dev/null; then
        print_success "Qdrant is accessible"
    else
        print_error "Qdrant is not accessible"
        return 1
    fi
    
    # Test RAG service
    cd rag-service
    python -c "
import asyncio
from rag_service import RAGService

async def test_rag():
    rag = RAGService()
    health = await rag.health_check()
    print(f'RAG Service Status: {health[\"status\"]}')
    
    response = await rag.process_query('What is your return policy?')
    print(f'Test query results: {len(response.results)} results')
    
asyncio.run(test_rag())
"
    
    if [ $? -eq 0 ]; then
        print_success "RAG service tests passed"
    else
        print_error "RAG service tests failed"
        return 1
    fi
    
    cd ..
    
    # Test AI backend health
    if curl -s http://localhost:8001/health > /dev/null; then
        print_success "AI backend is accessible"
    else
        print_error "AI backend is not accessible"
        return 1
    fi
    
    # Test chat endpoint
    response=$(curl -s -X POST http://localhost:8001/chat \
        -H "Content-Type: application/json" \
        -d '{"message": "What is your shipping policy?"}')
    
    if echo "$response" | grep -q "message"; then
        print_success "Chat endpoint is working"
    else
        print_error "Chat endpoint not working"
        return 1
    fi
    
    # Test knowledge search
    response=$(curl -s -X POST http://localhost:8001/knowledge/search \
        -H "Content-Type: application/json" \
        -d '{"query": "return policy", "type": "faq"}')
    
    if echo "$response" | grep -q "results"; then
        print_success "Knowledge search is working"
    else
        print_error "Knowledge search not working"
        return 1
    fi
    
    print_success "All tests passed!"
}

# Function to show demo
show_demo() {
    print_status "RAG Integration Demo"
    print_status "===================="
    echo
    
    print_status "Available endpoints:"
    echo "  • Chat: http://localhost:8001/chat"
    echo "  • Knowledge Search: http://localhost:8001/knowledge/search"
    echo "  • Suggestions: http://localhost:8001/knowledge/suggestions"
    echo "  • Health: http://localhost:8001/health"
    echo "  • Qdrant UI: http://localhost:6333/dashboard"
    echo
    
    print_status "Example queries to try:"
    echo "  • 'What is your return policy?' (FAQ)"
    echo "  • 'How do I track my order?' (FAQ)"
    echo "  • 'What are the shipping rules?' (Business Rules)"
    echo "  • 'Find me laptops under $1000' (Transactional)"
    echo "  • 'Can I return my laptop if I don't like it?' (Hybrid)"
    echo
    
    print_status "The system will automatically:"
    echo "  • Classify queries as FAQ, Business Rules, or Transactional"
    echo "  • Route to appropriate knowledge base or tools"
    echo "  • Combine knowledge base with transactional data when needed"
    echo "  • Provide conversational responses with source attribution"
}

# Main function
main() {
    echo
    print_status "🚀 Step 2: RAG Integration Setup"
    print_status "================================="
    echo
    
    # Check requirements
    print_status "Checking requirements..."
    
    if ! check_python; then
        print_error "Python 3.8+ is required"
        exit 1
    fi
    
    if ! check_docker; then
        print_error "Docker is required"
        exit 1
    fi
    
    # Setup based on command line argument
    case "${1:-setup}" in
        "setup")
            setup_venv
            install_python_deps
            setup_qdrant
            setup_env_config
            seed_knowledge_base
            
            print_success "Setup complete!"
            echo
            print_status "Next steps:"
            echo "  1. Run: ./setup.sh start    # Start all services"
            echo "  2. Run: ./setup.sh test     # Run tests"
            echo "  3. Run: ./setup.sh demo     # Show demo info"
            ;;
        "start")
            start_services
            ;;
        "test")
            run_tests
            ;;
        "demo")
            show_demo
            ;;
        "seed")
            seed_knowledge_base
            ;;
        "help")
            echo "Usage: ./setup.sh [command]"
            echo
            echo "Commands:"
            echo "  setup    Setup environment and dependencies (default)"
            echo "  start    Start all services (Qdrant + AI backend)"
            echo "  test     Run integration tests"
            echo "  demo     Show demo information"
            echo "  seed     Seed knowledge base into Qdrant"
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