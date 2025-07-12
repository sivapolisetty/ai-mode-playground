# Observability Setup

This directory contains observability tools and configurations used across all AI mode steps.

## LangFuse Integration

LangFuse provides comprehensive tracing and monitoring for LLM applications.

### Quick Start

1. Start LangFuse services:
```bash
docker-compose -f docker-compose.langfuse.yml up -d
```

2. Access LangFuse dashboard at http://localhost:3001

3. Configure your AI backend with LangFuse credentials:
```bash
export LANGFUSE_PUBLIC_KEY="your_public_key"
export LANGFUSE_SECRET_KEY="your_secret_key"
export LANGFUSE_HOST="http://localhost:3001"
```

### Features Tracked

- **Traces**: Complete conversation flows
- **Generations**: LLM requests and responses
- **Tools**: Function calls and results
- **Performance**: Response times and token usage
- **Errors**: Failed operations and debugging info

### Used Across Steps

- Step 1: Basic AI mode tracing
- Step 2: RAG pipeline monitoring
- Step 3: Multi-agent coordination tracking
- Step 4: UI generation analytics
- Step 5: Context engine performance

## Alternative: Disable Observability

For simplified testing, you can disable LangFuse by setting:
```bash
export LANGFUSE_ENABLED=false
```

The AI backend will still function normally without tracing.