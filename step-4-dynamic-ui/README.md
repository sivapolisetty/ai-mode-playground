# Step 4: Dynamic UI Generation with LLM

## Overview

Step 4 revolutionizes AI interaction by adding **LLM-Generated Dynamic UI** capabilities, building on the RAG foundation from Step 2. Instead of static text responses, the LLM intelligently generates interactive UI components in real-time.

## Architecture: Building on Step 1

### Step 1 Foundation (Inherited)
- ✅ **Simple Agent**: Basic query processing and tool routing
- ✅ **MCP Tools**: Product search, customer lookup, order management  
- ✅ **LLM Integration**: Ollama and OpenRouter support
- ✅ **Session Management**: In-memory conversation state
- ✅ **Observability**: LangFuse tracing and logging

### Step 2 Enhancements (New Layer)
- 🆕 **Enhanced Agent**: Extends Simple Agent with query classification
- 🆕 **RAG Service**: Semantic search and knowledge retrieval
- 🆕 **Vector Database**: Qdrant for fast similarity search
- 🆕 **Knowledge Base**: FAQ and business rules in business-friendly format
- 🆕 **Hybrid Responses**: Combines knowledge with real-time transactional data

This allows the AI to handle both transactional queries AND knowledge-based questions by combining:

- **Vector database** (Qdrant) for semantic search
- **FAQ knowledge base** for customer service questions
- **Business rules** for policy and procedure queries
- **Query classification** to route between knowledge base and transactional tools
- **Hybrid responses** that combine knowledge with real-time data

## Key Features

### 🧠 Enhanced AI Agent
- **Query Classification**: Automatically determines if queries are FAQ, Business Rules, Transactional, or Mixed
- **Intelligent Routing**: Routes queries to appropriate knowledge base or transactional tools
- **Hybrid Responses**: Combines knowledge base information with real-time transactional data
- **Context Awareness**: Maintains conversation context across knowledge and transactional domains

### 🔍 RAG Service
- **Semantic Search**: Uses sentence transformers for semantic understanding
- **Dual Knowledge Base**: Separate collections for FAQ and business rules
- **Confidence Scoring**: Provides relevance scores for search results
- **Query Suggestions**: Offers similar questions for better user experience

### 🗄️ Qdrant Vector Database
- **High Performance**: Fast vector similarity search
- **Scalable**: Handles large knowledge bases efficiently
- **Persistent**: Data survives restarts
- **Web UI**: Built-in dashboard for vector database management

### 📚 Knowledge Base
- **15 FAQ entries** covering shipping, returns, payments, accounts, support
- **10 Business rules** covering pricing, discounts, inventory, security policies
- **Rich Metadata**: Categories, tags, priorities, and conditions
- **Expandable**: Easy to add new knowledge items

## Architecture

```
User Query → Query Classification → Route Decision
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   FAQ Query     │  Business Rule  │  Transactional  │
│                 │     Query       │     Query       │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌─────────────┐ │
│ │ RAG Service │ │ │ RAG Service │ │ │ MCP Tools   │ │
│ │ (FAQ)       │ │ │ (Rules)     │ │ │             │ │
│ └─────────────┘ │ └─────────────┘ │ └─────────────┘ │
│        ↓        │        ↓        │        ↓        │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌─────────────┐ │
│ │ Qdrant      │ │ │ Qdrant      │ │ │ Traditional │ │
│ │ (FAQ)       │ │ │ (Rules)     │ │ │ API         │ │
│ └─────────────┘ │ └─────────────┘ │ └─────────────┘ │
└─────────────────┴─────────────────┴─────────────────┘
                           ↓
                   Response Generation
                   (Combining all sources)
```

## Quick Start

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Traditional e-commerce backend running on port 4000

### Setup
```bash
# Clone and navigate to step-2
cd step-2-rag-integration

# Run setup (installs dependencies, starts Qdrant, seeds knowledge base)
./setup.sh setup

# Start all services
./setup.sh start
```

### Test the Integration
```bash
# Run all tests
./setup.sh test

# Show demo information
./setup.sh demo
```

## Usage Examples

### 1. FAQ Query
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your return policy?"}'
```

**Response**: AI uses FAQ knowledge base to provide detailed return policy information.

### 2. Business Rules Query
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the rules for free shipping?"}'
```

**Response**: AI searches business rules to explain free shipping thresholds and conditions.

### 3. Transactional Query
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find me laptops under $1000"}'
```

**Response**: AI routes to transactional tools to search product catalog.

### 4. Hybrid Query
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Can I return this MacBook if I don\'t like it?"}'
```

**Response**: AI combines product information with return policy from knowledge base.

## Knowledge Base Management

### Direct Knowledge Search
```bash
# Search FAQ only
curl -X POST http://localhost:8001/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "shipping", "type": "faq", "limit": 3}'

# Search business rules only
curl -X POST http://localhost:8001/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "discount", "type": "business_rules", "limit": 3}'

# Auto-detect type
curl -X POST http://localhost:8001/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "return policy", "type": "auto"}'
```

### Get Query Suggestions
```bash
curl "http://localhost:8001/knowledge/suggestions?query=shipping&limit=3"
```

### Knowledge Base Statistics
```bash
curl http://localhost:8001/knowledge/stats
```

## Configuration

### Environment Variables (.env)
```bash
# LLM Configuration (Standardized)
LLM_PROVIDER=ollama                    # ollama or openrouter
OLLAMA_MODEL=gemma2:12b               # Standardized to 12B for consistency
OPENROUTER_API_KEY=your_key_here      # Cloud API key

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
EMBEDDING_MODEL=all-MiniLM-L6-v2      # Sentence transformer model

# Traditional API
TRADITIONAL_API_URL=http://localhost:4000

# Server Configuration
PORT=8001
```

### Adding New Knowledge
1. **Add FAQ entries** to `knowledge/faq.json`
2. **Add business rules** to `knowledge/business_rules.json`
3. **Re-seed the database**: `./setup.sh seed`

## API Endpoints

### Chat Endpoint
- **POST** `/chat` - Enhanced chat with RAG capabilities
- **GET** `/health` - Health check including RAG service status

### Knowledge Endpoints
- **POST** `/knowledge/search` - Direct knowledge base search
- **GET** `/knowledge/suggestions` - Get similar questions
- **GET** `/knowledge/stats` - Knowledge base statistics

### Utility Endpoints
- **GET** `/tools` - List available tools (transactional + knowledge)
- **GET** `/` - Service information and capabilities

## Development

### Adding New Query Types
1. **Update query classification** in `rag_service.py`
2. **Add routing logic** in `enhanced_agent.py`
3. **Create execution plan** for new query type

### Extending Knowledge Base
1. **Add new collections** in `seeder.py`
2. **Update search methods** in `rag_service.py`
3. **Modify response formatting** in `enhanced_agent.py`

## Monitoring

### Qdrant Dashboard
- **URL**: http://localhost:6333/dashboard
- **View collections**: FAQ and business rules
- **Monitor performance**: Query times and vector counts

### LangFuse Tracing (Optional)
- **URL**: http://localhost:3001 (if configured)
- **Trace conversations**: Complete RAG pipeline
- **Monitor performance**: Query classification and routing

## Troubleshooting

### Common Issues
1. **Qdrant not accessible**: Check Docker container with `docker ps`
2. **Knowledge base empty**: Run `./setup.sh seed` to load data
3. **Low search confidence**: Verify embedding model is downloaded
4. **LLM not responding**: Check Ollama service or OpenRouter API key

### Debug Commands
```bash
# Check Qdrant health
curl http://localhost:6333/health

# Check collections
curl http://localhost:6333/collections

# Test embedding model
cd rag-service && python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model loaded successfully')
"
```

## What's Next

Step 2 provides a solid foundation for knowledge-based AI interactions. The next steps in the series will add:

- **Step 3**: Multi-agent architecture for complex workflows
- **Step 4**: AI-generated dynamic UI components
- **Step 5**: Advanced context engineering and memory management

This RAG integration demonstrates how AI can intelligently combine structured knowledge with real-time data to provide comprehensive, contextual responses to user queries.