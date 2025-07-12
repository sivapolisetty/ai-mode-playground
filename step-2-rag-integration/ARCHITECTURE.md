# Step 2: RAG Integration Architecture

## How Step 2 Extends Step 1

### Layered Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    STEP 2: RAG INTEGRATION                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Enhanced Agent │  │   RAG Service   │  │ Knowledge Base  │ │
│  │                 │  │                 │  │                 │ │
│  │ • Query Router  │  │ • Vector Search │  │ • FAQ Data      │ │
│  │ • Strategy Mgr  │  │ • Semantic Sim  │  │ • Business Rules│ │
│  │ • Hybrid Resp   │  │ • Classification│  │ • Qdrant DB     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     STEP 1: BASIC AI MODE                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Simple Agent   │  │   MCP Tools     │  │ LLM Integration │ │
│  │                 │  │                 │  │                 │ │
│  │ • Basic Routing │  │ • Product APIs  │  │ • Ollama/OpenR  │ │
│  │ • Tool Exec     │  │ • Customer APIs │  │ • Session Mgmt  │ │
│  │ • Response Gen  │  │ • Order APIs    │  │ • Observability │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                  TRADITIONAL E-COMMERCE API                 │
└─────────────────────────────────────────────────────────────┘
```

## Component Inheritance and Extensions

### 1. Core Components from Step 1 (Reused)

#### **LLM Configuration** 
```
step-1-basic-ai/ai-backend/config/llm_config.py
                    ↓ (Enhanced)
step-2-rag-integration/ai-backend/config/llm_config.py
```
- **Base**: Ollama and OpenRouter support
- **Enhancement**: Standardized to Gemma2:12B for consistency

#### **MCP Tools**
```
step-1-basic-ai/ai-backend/tools/mcp_tools.py
                    ↓ (Extended)
step-2-rag-integration/ai-backend/tools/mcp_tools.py
```
- **Base**: Product search, customer lookup, order management
- **Extensions**: Enhanced filtering, pagination, metadata

#### **Logging Configuration**
```
step-1-basic-ai/ai-backend/config/logging_config.py
                    ↓ (Reused)
step-2-rag-integration/ai-backend/config/logging_config.py
```
- **Same**: Loguru-based structured logging
- **Consistent**: Same format and configuration

### 2. Core Components Enhanced in Step 2

#### **Agent Architecture Evolution**
```
SimpleAgent (Step 1)           →  EnhancedAgent (Step 2)
├── process_query()           →  ├── process_query() + RAG integration
├── execute_tools()           →  ├── execute_tools() (inherited)
├── format_response()         →  ├── format_response() + knowledge context
└── session management        →  └── session management + knowledge context
                                  ├── determine_routing_strategy() (NEW)
                                  ├── create_execution_plan() (NEW)
                                  └── hybrid response generation (NEW)
```

#### **Server Architecture Evolution**
```
FastAPI Server (Step 1)       →  FastAPI Server (Step 2)
├── /chat endpoint            →  ├── /chat endpoint (enhanced)
├── /health endpoint          →  ├── /health endpoint + RAG status
├── /tools endpoint           →  ├── /tools endpoint + knowledge tools
└── Basic error handling      →  └── Enhanced error handling
                                  ├── /knowledge/search (NEW)
                                  ├── /knowledge/suggestions (NEW)
                                  └── /knowledge/stats (NEW)
```

### 3. New Components in Step 2

#### **RAG Service Layer**
```
NEW: rag-service/
├── rag_service.py              # Core RAG functionality
├── seeder.py                   # Knowledge base population
└── requirements.txt            # RAG-specific dependencies
```

#### **Knowledge Base**
```
NEW: knowledge/
├── faq.json                    # Customer FAQ entries
├── business_rules.json         # Business policies and rules
└── README.md                   # Product owner documentation
```

#### **Vector Database**
```
NEW: docker-compose.qdrant.yml  # Qdrant vector database
```

## Data Flow Comparison

### Step 1: Basic AI Mode Flow
```
User Query → Simple Agent → Tool Selection → API Call → Response
```

### Step 2: RAG Integration Flow
```
User Query → Enhanced Agent → Query Classification → Routing Decision
                ↓                        ↓                ↓
            Knowledge Search    +    Tool Execution    →    Hybrid Response
                ↓                        ↓
            Qdrant Vector DB         Traditional API
```

## Key Architectural Principles

### 1. **Backward Compatibility**
- All Step 1 functionality preserved
- Existing MCP tools continue to work
- Same LLM configuration interface
- Consistent API endpoints

### 2. **Layered Enhancement**
- RAG capabilities added as new layer
- Original agent logic extended, not replaced
- Knowledge base separate from transactional data
- Clean separation of concerns

### 3. **Modular Design**
- RAG service can be disabled/enabled
- Knowledge base independently updatable
- Vector database containerized
- Each component has clear responsibilities

## Configuration Inheritance

### Environment Variables
```bash
# From Step 1 (Inherited)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma2:12b              # Standardized in Step 2
TRADITIONAL_API_URL=http://localhost:4000
PORT=8001                           # Different port for Step 2

# New in Step 2
QDRANT_HOST=localhost
QDRANT_PORT=6333
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Dependency Management
```
Step 1 Dependencies
├── FastAPI, Uvicorn (API server)
├── LangChain (LLM orchestration)
├── Ollama/OpenAI (LLM providers)
└── HTTPx (API client)

Step 2 Additional Dependencies
├── Qdrant Client (vector database)
├── Sentence Transformers (embeddings)
├── NumPy, Pandas (data processing)
└── AIOFiles (async file operations)
```

## Migration Path

### From Step 1 to Step 2
1. **Copy Step 1 components** with enhancements
2. **Add RAG service layer** for knowledge processing
3. **Extend agent capabilities** for hybrid responses
4. **Add vector database** for semantic search
5. **Create knowledge base** with business-friendly format

### Compatibility Matrix
| Component | Step 1 | Step 2 | Compatibility |
|-----------|--------|--------|---------------|
| LLM Config | ✓ | ✓ (Enhanced) | Backward Compatible |
| MCP Tools | ✓ | ✓ (Extended) | Fully Compatible |
| Simple Agent | ✓ | → Enhanced Agent | API Compatible |
| Session Management | ✓ | ✓ (Extended) | Data Compatible |
| Observability | ✓ | ✓ (Enhanced) | Fully Compatible |

## Deployment Considerations

### Service Dependencies
```
Step 1 Dependencies:
├── Traditional E-commerce API (Port 4000)
├── Ollama Service (Port 11434)
└── LangFuse (Optional, Port 3001)

Step 2 Additional Dependencies:
├── Qdrant Vector DB (Port 6333)
└── Enhanced AI Backend (Port 8001)
```

### Resource Requirements
```
Step 1: Basic AI Mode
├── CPU: 2-4 cores
├── RAM: 4-8 GB
└── Storage: 2-5 GB (for LLM models)

Step 2: RAG Integration
├── CPU: 4-8 cores (additional for embeddings)
├── RAM: 8-16 GB (vector operations + knowledge base)
└── Storage: 5-10 GB (models + vector database)
```

This architecture ensures that Step 2 builds cleanly upon Step 1 while adding powerful RAG capabilities in a modular, maintainable way.