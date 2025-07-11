#!/bin/bash

# Master Setup Script for AI Mode Playground
# This script helps you set up any step of the AI mode integration series

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_title() {
    echo -e "${CYAN}$1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to display header
display_header() {
    echo
    print_title "🚀 AI Mode Playground - Master Setup"
    print_title "===================================="
    echo
    print_status "This script helps you set up any step of the AI mode integration series"
    echo
}

# Function to display step information
display_step_info() {
    echo
    print_title "📚 Available Steps:"
    echo
    echo "1️⃣  Step 1: Basic AI Mode"
    echo "   • Simple LangChain + MCP server integration"
    echo "   • LLM flexibility (Ollama/OpenRouter)"
    echo "   • Basic tool routing and chat interface"
    echo
    echo "2️⃣  Step 2: RAG Integration"
    echo "   • Query routing (FAQ vs transactional)"
    echo "   • Vector database for knowledge base"
    echo "   • Hybrid AI capabilities"
    echo
    echo "3️⃣  Step 3: Multi-Agent Architecture"
    echo "   • Semantic orchestrator + planning + execution"
    echo "   • Complex multi-step workflows"
    echo "   • Agent coordination system"
    echo
    echo "4️⃣  Step 4: Dynamic UI Generation"
    echo "   • AI-generated UI components"
    echo "   • Context-aware layout adaptation"
    echo "   • Real-time UI optimization"
    echo
    echo "5️⃣  Step 5: Context Engineering"
    echo "   • Advanced memory management"
    echo "   • Emotional intelligence"
    echo "   • Personalized experiences"
    echo
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    local requirements_met=true
    
    # Check Python
    if command_exists python3; then
        local python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        
        # Check if Python version is 3.8 or higher using Python itself
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python $python_version ✓"
        else
            print_error "Python 3.8+ required, found $python_version"
            requirements_met=false
        fi
    else
        print_error "Python 3 not found"
        requirements_met=false
    fi
    
    # Check Git
    if command_exists git; then
        print_success "Git ✓"
    else
        print_warning "Git not found (optional)"
    fi
    
    # Check curl
    if command_exists curl; then
        print_success "curl ✓"
    else
        print_error "curl not found (required for testing)"
        requirements_met=false
    fi
    
    # Check bc for version comparison
    if command_exists bc; then
        print_success "bc ✓"
    else
        print_warning "bc not found (used for version comparison)"
    fi
    
    if [ "$requirements_met" = false ]; then
        print_error "Some requirements are not met. Please install missing dependencies."
        exit 1
    fi
    
    print_success "All requirements met!"
}

# Function to check step prerequisites
check_step_prerequisites() {
    local step=$1
    
    print_status "Checking prerequisites for Step $step..."
    
    case $step in
        1)
            print_success "No additional prerequisites for Step 1"
            ;;
        2)
            print_status "Step 2 requires vector database (Chroma or Pinecone)"
            ;;
        3)
            if command_exists redis-server; then
                print_success "Redis available for Step 3"
            else
                print_warning "Redis not found. Will be installed during setup."
            fi
            ;;
        4)
            if command_exists node; then
                print_success "Node.js available for Step 4"
            else
                print_warning "Node.js not found. Will be installed during setup."
            fi
            ;;
        5)
            local postgres_available=false
            local redis_available=false
            
            if command_exists psql; then
                postgres_available=true
                print_success "PostgreSQL available for Step 5"
            else
                print_warning "PostgreSQL not found. Will be installed during setup."
            fi
            
            if command_exists redis-server; then
                redis_available=true
                print_success "Redis available for Step 5"
            else
                print_warning "Redis not found. Will be installed during setup."
            fi
            ;;
    esac
}

# Function to setup a specific step
setup_step() {
    local step=$1
    local step_dir="step-$step-"
    
    case $step in
        1)
            step_dir="step-1-basic-ai"
            ;;
        2)
            step_dir="step-2-rag-integration"
            ;;
        3)
            step_dir="step-3-multi-agent"
            ;;
        4)
            step_dir="step-4-dynamic-ui"
            ;;
        5)
            step_dir="step-5-context-engineering"
            ;;
        *)
            print_error "Invalid step: $step"
            return 1
            ;;
    esac
    
    if [ ! -d "$step_dir" ]; then
        print_error "Step $step directory not found: $step_dir"
        return 1
    fi
    
    if [ ! -f "$step_dir/setup.sh" ]; then
        print_error "Setup script not found: $step_dir/setup.sh"
        return 1
    fi
    
    print_status "Setting up Step $step..."
    
    # Check prerequisites
    check_step_prerequisites $step
    
    # Change to step directory and run setup
    cd "$step_dir"
    
    print_status "Running setup script for Step $step..."
    ./setup.sh setup
    
    cd ..
    
    print_success "Step $step setup complete!"
}

# Function to start a specific step
start_step() {
    local step=$1
    local step_dir="step-$step-"
    
    case $step in
        1) step_dir="step-1-basic-ai" ;;
        2) step_dir="step-2-rag-integration" ;;
        3) step_dir="step-3-multi-agent" ;;
        4) step_dir="step-4-dynamic-ui" ;;
        5) step_dir="step-5-context-engineering" ;;
        *)
            print_error "Invalid step: $step"
            return 1
            ;;
    esac
    
    if [ ! -d "$step_dir" ]; then
        print_error "Step $step directory not found: $step_dir"
        return 1
    fi
    
    cd "$step_dir"
    print_status "Starting Step $step server..."
    ./setup.sh start
}

# Function to run demo for a specific step
demo_step() {
    local step=$1
    local step_dir="step-$step-"
    
    case $step in
        1) step_dir="step-1-basic-ai" ;;
        2) step_dir="step-2-rag-integration" ;;
        3) step_dir="step-3-multi-agent" ;;
        4) step_dir="step-4-dynamic-ui" ;;
        5) step_dir="step-5-context-engineering" ;;
        *)
            print_error "Invalid step: $step"
            return 1
            ;;
    esac
    
    if [ ! -d "$step_dir" ]; then
        print_error "Step $step directory not found: $step_dir"
        return 1
    fi
    
    cd "$step_dir"
    print_status "Running Step $step demo..."
    ./setup.sh demo
}

# Function to test a specific step
test_step() {
    local step=$1
    local step_dir="step-$step-"
    
    case $step in
        1) step_dir="step-1-basic-ai" ;;
        2) step_dir="step-2-rag-integration" ;;
        3) step_dir="step-3-multi-agent" ;;
        4) step_dir="step-4-dynamic-ui" ;;
        5) step_dir="step-5-context-engineering" ;;
        *)
            print_error "Invalid step: $step"
            return 1
            ;;
    esac
    
    if [ ! -d "$step_dir" ]; then
        print_error "Step $step directory not found: $step_dir"
        return 1
    fi
    
    cd "$step_dir"
    print_status "Testing Step $step..."
    ./setup.sh test
}

# Function to show interactive menu
show_menu() {
    while true; do
        echo
        print_title "🎯 What would you like to do?"
        echo
        echo "1) Setup a step"
        echo "2) Start a step server"
        echo "3) Run a step demo"
        echo "4) Test a step"
        echo "5) Check requirements"
        echo "6) Show step information"
        echo "7) Exit"
        echo
        
        read -p "Enter your choice (1-7): " choice
        
        case $choice in
            1)
                echo
                read -p "Which step would you like to setup? (1-5): " step
                if [[ $step =~ ^[1-5]$ ]]; then
                    setup_step $step
                else
                    print_error "Invalid step. Please enter 1-5."
                fi
                ;;
            2)
                echo
                read -p "Which step would you like to start? (1-5): " step
                if [[ $step =~ ^[1-5]$ ]]; then
                    start_step $step
                else
                    print_error "Invalid step. Please enter 1-5."
                fi
                ;;
            3)
                echo
                read -p "Which step demo would you like to run? (1-5): " step
                if [[ $step =~ ^[1-5]$ ]]; then
                    demo_step $step
                else
                    print_error "Invalid step. Please enter 1-5."
                fi
                ;;
            4)
                echo
                read -p "Which step would you like to test? (1-5): " step
                if [[ $step =~ ^[1-5]$ ]]; then
                    test_step $step
                else
                    print_error "Invalid step. Please enter 1-5."
                fi
                ;;
            5)
                check_requirements
                ;;
            6)
                display_step_info
                ;;
            7)
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please enter 1-7."
                ;;
        esac
    done
}

# Function to setup all steps
setup_all() {
    print_status "Setting up all steps..."
    
    for step in {1..5}; do
        print_status "Setting up Step $step..."
        setup_step $step
        print_success "Step $step setup complete!"
        echo
    done
    
    print_success "All steps setup complete!"
}

# Main function
main() {
    display_header
    
    # Check basic requirements
    check_requirements
    
    # Handle command line arguments
    case "${1:-menu}" in
        "menu")
            display_step_info
            show_menu
            ;;
        "setup")
            if [ -n "$2" ]; then
                if [[ $2 =~ ^[1-5]$ ]]; then
                    setup_step $2
                elif [ "$2" = "all" ]; then
                    setup_all
                else
                    print_error "Invalid step: $2"
                    exit 1
                fi
            else
                print_error "Please specify a step number (1-5) or 'all'"
                exit 1
            fi
            ;;
        "start")
            if [ -n "$2" ] && [[ $2 =~ ^[1-5]$ ]]; then
                start_step $2
            else
                print_error "Please specify a step number (1-5)"
                exit 1
            fi
            ;;
        "demo")
            if [ -n "$2" ] && [[ $2 =~ ^[1-5]$ ]]; then
                demo_step $2
            else
                print_error "Please specify a step number (1-5)"
                exit 1
            fi
            ;;
        "test")
            if [ -n "$2" ] && [[ $2 =~ ^[1-5]$ ]]; then
                test_step $2
            else
                print_error "Please specify a step number (1-5)"
                exit 1
            fi
            ;;
        "info")
            display_step_info
            ;;
        "help")
            echo "Usage: ./master-setup.sh [command] [step]"
            echo
            echo "Commands:"
            echo "  menu           Show interactive menu (default)"
            echo "  setup <step>   Setup specific step (1-5) or 'all'"
            echo "  start <step>   Start specific step server (1-5)"
            echo "  demo <step>    Run demo for specific step (1-5)"
            echo "  test <step>    Test specific step (1-5)"
            echo "  info           Show step information"
            echo "  help           Show this help message"
            echo
            echo "Examples:"
            echo "  ./master-setup.sh setup 1      # Setup Step 1"
            echo "  ./master-setup.sh setup all    # Setup all steps"
            echo "  ./master-setup.sh start 2      # Start Step 2 server"
            echo "  ./master-setup.sh demo 3       # Run Step 3 demo"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Run './master-setup.sh help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"