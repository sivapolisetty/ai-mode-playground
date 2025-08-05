# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **5-step AI integration playground** demonstrating the progressive evolution from traditional e-commerce to AI-powered conversational experiences. Each step builds upon the previous one, adding new AI capabilities while maintaining backward compatibility.

### Architecture Progression
- **Traditional E-commerce** (React + Node.js + REST API + SQLite)
- **Step 1**: Basic AI mode with LangChain and MCP tools
- **Step 2**: RAG integration with vector database and knowledge base
- **Step 3**: Multi-agent architecture with unified business agents
- **Step 4**: Dynamic UI generation with LLM-generated components
- **Step 5**: Advanced context engineering (planned)

## Common Development Commands

### Frontend (React + Vite)
```bash
# Development server
npm run dev

# Build for production
npm run build

# Type checking
npm run check

# Database operations
npm run db:push
```

### AI Backend Services (Python FastAPI)
```bash
# Each step has its own setup script
cd step-N-*/
./setup.sh setup    # Install dependencies and configure
./setup.sh start    # Start all services
./setup.sh test     # Run integration tests
./setup.sh demo     # Show usage examples
./setup.sh clean    # Clean up services

# Manual Python environment management
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r ../shared/requirements-common.txt
```

### Traditional E-commerce Backend
```bash
# Start the backend API server (REST API)
npm run dev  # Runs on port 4000
```

## Architecture Overview

### Multi-Layered Design
Each step extends the previous functionality:

```
┌─────────────────────────────────────────────────────────┐
│                    STEP 4: DYNAMIC UI                  │
│  • LLM-generated UI components                         │
│  • Component scanning and caching                      │
│  • Prompt management system                            │
├─────────────────────────────────────────────────────────┤
│                  STEP 3: MULTI-AGENT                   │
│  • UnifiedBusinessAgent (consolidated operations)      │
│  • RulesAgent (business logic with RAG)                │
│  • DynamicOrchestrator (workflow coordination)         │
├─────────────────────────────────────────────────────────┤
│                   STEP 2: RAG INTEGRATION              │
│  • Enhanced Agent with query classification            │
│  • Qdrant vector database for semantic search          │
│  • Knowledge base (FAQ + business rules)               │
│  • Hybrid responses (knowledge + transactional)        │
├─────────────────────────────────────────────────────────┤
│                    STEP 1: BASIC AI                    │
│  • Simple Agent with tool routing                      │
│  • MCP Tools (product, customer, order APIs)           │
│  • LLM Integration (Ollama/OpenRouter)                 │
│  • Session management and observability                │
├─────────────────────────────────────────────────────────┤
│                TRADITIONAL E-COMMERCE API              │
│  • REST API with Express                               │
│  • SQLite database with Drizzle ORM                    │
│  • React frontend with Radix UI components             │
└─────────────────────────────────────────────────────────┘
```

### Service Ports
- **Frontend**: 5173 (Vite dev server)
- **Traditional API**: 4000 (REST API)
- **Step 1 AI Backend**: 8000
- **Step 2 AI Backend**: 8001
- **Step 3 AI Backend**: 8002
- **Step 4 AI Backend**: 8003
- **Qdrant Vector DB**: 6333 (Steps 2+)
- **LangFuse Observability**: 3001 (optional)

## Key Components and Patterns

### MCP Tools Architecture
All AI backends use **Model Context Protocol (MCP)** tools for consistent API integration:
- `search_products()` - Product catalog search with filtering
- `get_customer_info()` - Customer authentication and profile
- `create_order()` - Order management lifecycle
- `calculate_delivery()` - Shipping and delivery logic
- `send_notification()` - Customer communications

### LLM Configuration
Environment-based LLM selection across all steps:
```bash
# Local deployment (privacy-focused)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma2:12b

# Cloud deployment (scalable)
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=google/gemini-2.5-flash
```

### Knowledge Base Management (Steps 2+)
- **FAQ Collection**: Customer service questions
- **Business Rules**: Policies, pricing, discounts
- **Vector Embeddings**: Semantic search with sentence transformers
- **Hybrid Responses**: Combine knowledge with real-time data

### Agent Architecture (Step 3+)
Simplified from 6 specialized agents to 3 core agents:
- **UnifiedBusinessAgent**: Handles all MCP tool operations
- **RulesAgent**: Business logic with RAG integration
- **DynamicOrchestrator**: Workflow coordination and strategy execution

## Development Workflow

### Adding New Features
1. **Start with the appropriate step** - Don't modify earlier steps unnecessarily
2. **Follow the layered architecture** - Each step extends, doesn't replace
3. **Test integration thoroughly** - Use provided test suites
4. **Maintain backward compatibility** - Earlier steps should continue working

### Working with AI Backends
1. **Use setup scripts** - They handle dependencies and configuration
2. **Check service health** - All backends expose `/health` endpoints
3. **Monitor with LangFuse** - Optional but recommended for tracing
4. **Test with curl/httpie** - Each step includes API examples

### Database Operations
```bash
# Traditional e-commerce database
npm run db:push  # Apply schema changes

# Vector database (Qdrant) - Steps 2+
curl http://localhost:6333/health
curl http://localhost:6333/collections
```

### Testing Strategy
Each step includes comprehensive testing:
```bash
./setup.sh test  # Integration tests for AI backend
npm test         # Frontend unit tests (if available)
pytest tests/    # Python unit tests (if available)
```

## Important Notes

### Multi-Step Compatibility
- Each step is **independent** but builds on shared foundations
- **Don't break backward compatibility** when modifying shared components
- **Test across steps** when changing shared dependencies

### LLM Model Consistency
- Steps 2+ standardize on **Gemma2:12B** for consistency
- Local models prioritize privacy and cost-effectiveness
- Cloud models provide advanced capabilities and scale

### Knowledge Base Updates
When modifying knowledge bases (Steps 2+):
1. Edit JSON files in `knowledge/` directory
2. Run `./setup.sh seed` to update vector database
3. Test with `/knowledge/search` endpoint

### Component Scanning (Step 4)
The dynamic UI system scans React components automatically:
- Components in `client/src/components/` are indexed
- Metadata is cached for performance
- LLM generates UI based on available components

## Troubleshooting

### Common Issues
1. **Port conflicts**: Each step uses different ports
2. **Python dependencies**: Use virtual environments consistently
3. **Vector database**: Ensure Docker is running for Qdrant
4. **LLM connectivity**: Check Ollama service or API keys

### Debug Commands
```bash
# Check service status
curl http://localhost:PORT/health

# View logs
tail -f ai-backend/logs/app.log

# Test vector database
curl http://localhost:6333/collections

# Validate LLM connection
cd step-N-*/ai-backend && python -c "from config.llm_config import get_llm; print(get_llm())"
```

This playground demonstrates practical AI integration patterns for production applications, with each step adding increasing sophistication while maintaining real-world applicability.