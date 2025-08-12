# Step 4 Observability

This directory contains the observability infrastructure for Step 4 Dynamic UI, with **LangFuse** as the primary observability platform.

## Architecture

The observability system has been **architecturally separated** from the main Step 4 application per user requirements:

- **LangFuse runs independently** as a prerequisite service
- **Step 4 validates LangFuse connection** before startup
- **Dedicated management script** for all LangFuse operations
- **Fallback mode** when LangFuse is unavailable (SKIP_LANGFUSE=true)

## Components

### 1. LangFuse Manager (`langfuse_manager.sh`)

**Dedicated script for all LangFuse observability management:**

```bash
# Start LangFuse observability platform
./langfuse_manager.sh start

# Check LangFuse status and health
./langfuse_manager.sh status

# View real-time logs
./langfuse_manager.sh logs

# Stop LangFuse
./langfuse_manager.sh stop

# Complete cleanup (remove containers/volumes)
./langfuse_manager.sh cleanup
```

**Key Features:**
- ✅ Auto-detects docker-compose configuration (`langfuse-v2.yml` or `langfuse.yml`)
- ✅ Health checking with API validation
- ✅ Service readiness waiting with timeout
- ✅ Real-time log viewing
- ✅ Complete cleanup functionality
- ✅ Colored output for clear status indication

### 2. LangFuse Decorator (`langfuse_decorator.py`)

**@observe() decorator approach for clean, distributed tracing:**

```python
from shared.observability.langfuse_decorator import trace_conversation, trace_agent_operation

# Trace entire conversations
@trace_conversation(name="step4_dynamic_ui", user_id="user123")
async def process_query(message, context):
    # Your agent logic here
    pass

# Trace individual operations
@trace_agent_operation("query_classification")
async def classify_query(query):
    # Classification logic
    pass
```

**Available Decorators:**
- `@trace_conversation()` - Trace complete AI conversations
- `@trace_agent_operation()` - Trace individual agent operations  
- `@trace_tool_execution()` - Trace MCP tool calls
- `@trace_llm_generation()` - Trace LLM interactions
- `@trace_ui_generation()` - Trace UI component generation
- `@trace_rag_operation()` - Trace RAG/vector search operations

### 3. LangFuse Client (`langfuse_client.py`)

**Direct client for manual trace management:**

```python
from shared.observability.langfuse_client import langfuse_client

# Create traces manually
trace_id = langfuse_client.create_trace(
    user_message="Show me iPhone models",
    session_id="session_123",
    metadata={"source": "api"}
)

# Log conversation end
langfuse_client.log_conversation_end(
    trace_id=trace_id,
    response="Here are the iPhone models...",
    response_type="enhanced_with_ui"
)
```

## Usage Patterns

### 1. Prerequisites-First Approach

**Recommended workflow for production:**

```bash
# Terminal 1: Start LangFuse first
./langfuse start

# Terminal 2: Start Step 4 (validates LangFuse connection)
./start-services.sh start
```

### 2. Integrated Approach

**Start everything together:**

```bash
# Starts LangFuse + Step 4 in one command
./start-services.sh full
```

### 3. Development Without Observability

**When LangFuse isn't needed:**

```bash
# Skip LangFuse completely
./start-services.sh no-langfuse

# Or set environment variable
SKIP_LANGFUSE=true python server.py
```

## Configuration

### Environment Variables

```bash
# LangFuse connection (loaded from .env.langfuse)
LANGFUSE_HOST=http://localhost:3001
LANGFUSE_PUBLIC_KEY=pk-lf-862b860f-83d4-4537-96c1-0cfba9ce0748
LANGFUSE_SECRET_KEY=sk-lf-9720fd8e-1370-4b4d-adcf-3c83f637ad84

# Skip LangFuse (development mode)
SKIP_LANGFUSE=true
```

### LangFuse Project

- **Dashboard**: http://localhost:3001
- **Project**: ui-agent (`cme69v2i5000610rxp11ozgcv`)
- **Features**: Agent tracing, RAG analysis, UI generation monitoring

## Integration Points

### 1. Server Startup Validation

```python
# server.py checks LangFuse before starting
if not langfuse_config.is_langfuse_available():
    if not os.getenv("SKIP_LANGFUSE", "false").lower() == "true":
        logger.error("🚫 Stopping startup. LangFuse connection required.")
        sys.exit(1)
```

### 2. Automatic Trace Creation

```python
# Every chat request creates a trace
trace_id = langfuse_client.create_trace(
    user_message=request.message,
    session_id=session_id,
    metadata=request.context
) or str(uuid.uuid4())  # Fallback UUID if LangFuse unavailable
```

### 3. Comprehensive Observability

**What gets traced:**
- ✅ Complete conversation flows
- ✅ Query classification and intent detection
- ✅ MCP tool executions (product search, orders, etc.)
- ✅ RAG operations (knowledge base searches)  
- ✅ LLM generation calls
- ✅ UI component generation
- ✅ Response formatting and validation

## Troubleshooting

### Common Issues

1. **LangFuse not starting**: Check Docker daemon and port 3001 availability
2. **API connection failed**: Verify credentials in `.env.langfuse`
3. **Traces not appearing**: Ensure SDK v2 compatibility (not v3)
4. **Port conflicts**: Stop existing LangFuse instances

### Debug Commands

```bash
# Check LangFuse health
./langfuse health

# View real-time logs
./langfuse logs

# Test API connection
curl http://localhost:3001/api/public/health

# Check running containers
docker ps | grep langfuse
```

### Recovery

```bash
# Complete cleanup and restart
./langfuse cleanup
./langfuse start

# Force container restart
docker-compose -f docker-compose.langfuse-v2.yml restart
```

## Development Notes

- **SDK Version**: Uses LangFuse SDK v2.60.9 (compatible with platform v2.82.0)
- **No OpenTelemetry**: Removed OTEL configuration to avoid conflicts
- **Graceful Fallback**: System continues without observability if LangFuse unavailable
- **Separation of Concerns**: LangFuse completely separated from Step 4 startup
- **Health Checking**: Robust validation before service dependencies

This observability architecture ensures **production-ready monitoring** while maintaining **development flexibility** and **architectural cleanliness**.