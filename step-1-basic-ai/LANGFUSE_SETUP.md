# LangFuse Integration Setup

This guide explains how to set up LangFuse for observability of your basic AI mode implementation.

## What is LangFuse?

LangFuse is an open-source observability platform for LLM applications that provides:

- **LLM Call Tracking**: Monitor prompts, responses, and token usage
- **Tool Execution Logging**: Track all tool calls with parameters and results
- **Performance Metrics**: Response times and success rates
- **Simple Web UI**: Easy-to-use dashboard for debugging

## Quick Setup

### Step 1: Run Local LangFuse (Included in setup script)

The setup script automatically configures LangFuse for you:

```bash
./setup.sh setup
# Choose 'y' when asked about LangFuse configuration
```

This will:
- Start LangFuse locally on http://localhost:3000
- Create API keys automatically 
- Configure the .env file

### Step 2: Access LangFuse Dashboard

1. Open http://localhost:3000 in your browser
2. Create an account (any email/password works locally)
3. View your AI interactions in real-time

## Manual Configuration

If you need to configure manually:

```bash
cd step-1-basic-ai/ai-backend

# Edit .env and add:
LANGFUSE_SECRET_KEY=sk-lf-d70ed921-ef51-46d4-8ad7-9e400800bf43
LANGFUSE_PUBLIC_KEY=pk-lf-f004239e-b87e-4e2c-87e1-f904947ab4bd
LANGFUSE_HOST=http://localhost:3000
```

## What You'll See in LangFuse

### LLM Interactions
- **Prompts**: Exact prompts sent to the model
- **Responses**: Complete model responses  
- **Token Usage**: Input/output token counts
- **Timing**: Response latency for each call

### Tool Executions
- **Tool Calls**: Which tools were called and why
- **Parameters**: Exact parameters passed to each tool
- **Results**: Complete tool response data
- **Success/Failure**: Error tracking and debugging

### Session Flow
When you ask "What's the price of iPhone 15 Pro?", you'll see:

1. **User Query**: Original question received
2. **Tool Planning**: LLM decides to call search_products
3. **Tool Execution**: search_products called with query parameters
4. **Response Generation**: LLM formats the final response

## Troubleshooting

### 1. No Traces in UI
```bash
# Check if LangFuse client is working
cd step-1-basic-ai/ai-backend
python test_langfuse.py
```

### 2. Connection Issues
- Verify LangFuse is running on http://localhost:3000
- Check .env file has correct credentials
- Ensure no firewall blocking port 3000

### 3. Missing Data
- LangFuse traces appear with a slight delay (~2-3 seconds)
- Refresh the browser page if traces don't appear immediately
- Check server logs for any LangFuse-related errors

This simple setup gives you complete visibility into your AI application!