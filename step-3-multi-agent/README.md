# Step 3: Multi-Agent Architecture

## Overview

Step 3 builds upon Step 2's RAG integration by adding **Multi-Agent Architecture** with specialized agents that have deep domain expertise. This creates a sophisticated system where multiple AI agents coordinate to handle complex workflows like placing orders, changing addresses, and managing customer interactions.

## Architecture: Building on Step 2

### Step 2 Foundation (Inherited)
- ✅ **Enhanced Agent**: Query classification and RAG integration
- ✅ **RAG Service**: Semantic search and knowledge retrieval
- ✅ **Vector Database**: Qdrant for fast similarity search
- ✅ **Knowledge Base**: FAQ and business rules
- ✅ **MCP Tools**: Product search, customer lookup, order management
- ✅ **LLM Integration**: Ollama and OpenRouter support

### Step 3 Enhancements (New Layer)
- 🆕 **Agent Orchestrator**: Coordinates complex multi-agent workflows
- 🆕 **Product Agent**: Deep product catalog and inventory expertise
- 🆕 **Customer Agent**: Customer management and authentication expertise
- 🆕 **Order Agent**: Order lifecycle and processing expertise
- 🆕 **Shipping Agent**: Delivery and logistics expertise
- 🆕 **Rules Agent**: Business rules validation and compliance

## Key Features

### 🎯 Specialized Agents
Each agent has deep domain expertise and specific responsibilities:

#### **Product Agent**
- Product catalog search and filtering
- Inventory availability checking
- Product recommendation engine
- Pricing and variant management
- Stock reservation and allocation

#### **Customer Agent**
- Customer authentication and profiles
- Address book management (home, work, billing)
- Payment method management
- Order history and preferences
- Customer communication and notifications

#### **Order Agent**
- Order creation and validation
- Order lifecycle management
- Status tracking and updates
- Order modifications (address, items, cancellation)
- Fulfillment coordination

#### **Shipping Agent**
- Address validation and geocoding
- Delivery time estimation
- Shipping cost calculation
- Carrier selection and tracking
- Route optimization

#### **Rules Agent**
- Business rules validation using RAG
- Policy enforcement and compliance
- Exception handling and approvals
- Constraint checking

### 🔄 Agent Orchestrator
- **Workflow Coordination**: Manages complex multi-step processes
- **Agent Communication**: Facilitates inter-agent data exchange
- **State Management**: Tracks workflow progress and context
- **Error Handling**: Manages failures and rollback scenarios
- **Performance Monitoring**: Tracks agent performance and bottlenecks

## Complex Workflow Examples

### 1. Place Order Workflow
```
User: "Place order for iPhone 15 Pro to home address, possible to get in 2 days?"

Agent Orchestrator:
├── Product Agent → Search iPhone 15 Pro variants, check inventory
├── Customer Agent → Get customer profile, authenticate, fetch home address
├── Shipping Agent → Calculate delivery options to home, check 2-day availability
├── Rules Agent → Validate order constraints, check business rules
├── Product Agent → Reserve inventory for customer
├── Order Agent → Create order with validated details
└── Customer Agent → Send order confirmation
```

### 2. Address Change Workflow
```
User: "Change delivery address for order #12345"

Agent Orchestrator:
├── Customer Agent → Authenticate customer, verify order ownership
├── Order Agent → Fetch order details, check current status
├── Rules Agent → Check if address change is allowed (RAG policy lookup)
├── Shipping Agent → Validate new address, recalculate delivery
├── Order Agent → Update order with new address and delivery details
└── Customer Agent → Notify customer of changes
```

### 3. Product Inquiry Workflow
```
User: "Do you have MacBook Pro M3 in stock with delivery to NYC?"

Agent Orchestrator:
├── Product Agent → Search MacBook Pro M3 variants, check stock levels
├── Customer Agent → Get customer location context
├── Shipping Agent → Calculate delivery options to NYC
└── Product Agent → Provide availability with delivery estimates
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    STEP 3: MULTI-AGENT SYSTEM              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Agent Orchestr. │  │ Product Agent   │  │ Customer Agent  │ │
│  │ • Workflow Mgmt │  │ • Inventory Chk │  │ • Profile Mgmt  │ │
│  │ • Agent Routing │  │ • Product Info  │  │ • Auth & Access │ │
│  │ • State Mgmt    │  │ • Availability  │  │ • Preferences   │ │
│  │ • Error Handling│  │ • Reservations  │  │ • Communications│ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Order Agent    │  │ Shipping Agent  │  │  Rules Agent    │ │
│  │ • Order Process │  │ • Address Mgmt  │  │ • Policy Check  │ │
│  │ • Status Track  │  │ • Delivery Opt  │  │ • Validation    │ │
│  │ • Modifications │  │ • Time Estimates│  │ • Compliance    │ │
│  │ • Fulfillment   │  │ • Cost Calc     │  │ • Exception Mgmt│ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     STEP 2: RAG INTEGRATION                │
│           (Enhanced Agent + Knowledge Base + Vector DB)     │
├─────────────────────────────────────────────────────────────┤
│                     STEP 1: BASIC AI MODE                  │
│              (Simple Agent + MCP Tools + LLM)              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- All Step 2 prerequisites (Python 3.8+, Docker, Traditional API)
- Qdrant vector database running
- Knowledge base seeded

### Setup
```bash
# Clone and navigate to step-3
cd step-3-multi-agent

# Run setup (installs dependencies, configures multi-agent system)
./setup.sh setup

# Start all services
./setup.sh start
```

### Test Multi-Agent Workflows
```bash
# Test product + delivery workflow
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Place order for iPhone 15 Pro to home address, possible to get in 2 days?"}'

# Test address change workflow  
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Change delivery address for order 12345"}'

# Test complex product inquiry
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Do you have MacBook Pro M3 in stock with delivery to NYC?"}'
```

## Agent Communication

### Inter-Agent Message Format
```json
{
  "from_agent": "product_agent",
  "to_agent": "shipping_agent", 
  "workflow_id": "order_12345",
  "action": "calculate_delivery",
  "data": {
    "product_id": "iphone_15_pro",
    "destination": "home_address",
    "customer_id": "cust_456"
  },
  "context": {
    "urgency": "2_day_delivery_requested"
  }
}
```

### Workflow State Management
```json
{
  "workflow_id": "order_12345",
  "status": "in_progress",
  "current_step": "inventory_check",
  "completed_steps": ["authentication", "product_search"],
  "pending_steps": ["shipping_calculation", "order_creation"],
  "agent_context": {
    "customer_agent": {"customer_id": "cust_456"},
    "product_agent": {"reserved_items": ["iphone_15_pro"]},
    "shipping_agent": {"delivery_window": "2_days"}
  }
}
```

## Configuration

### Environment Variables (.env)
```bash
# Inherited from Step 2
LLM_PROVIDER=ollama
OLLAMA_MODEL=gemma3:12b
QDRANT_HOST=localhost
QDRANT_PORT=6333
TRADITIONAL_API_URL=http://localhost:4000
PORT=8001

# New Multi-Agent Configuration
AGENT_ORCHESTRATOR_ENABLED=true
MAX_WORKFLOW_STEPS=20
AGENT_TIMEOUT_SECONDS=30
WORKFLOW_STATE_TTL_HOURS=24
ENABLE_AGENT_MONITORING=true
```

## API Endpoints

### Multi-Agent Endpoints
- **POST** `/workflows/create` - Create new multi-agent workflow
- **GET** `/workflows/{workflow_id}/status` - Get workflow status
- **POST** `/workflows/{workflow_id}/cancel` - Cancel running workflow
- **GET** `/agents/status` - Get all agent statuses
- **POST** `/agents/{agent_name}/health` - Check specific agent health

### Enhanced Chat Endpoint
- **POST** `/chat` - Enhanced chat with multi-agent orchestration
- **GET** `/chat/workflows` - List active chat workflows

## Development

### Adding New Agents
1. **Create agent class** extending `BaseAgent`
2. **Define agent capabilities** and expertise domain
3. **Register agent** with orchestrator
4. **Implement agent communication** protocols
5. **Add agent to workflow** definitions

### Creating New Workflows
1. **Define workflow steps** and dependencies
2. **Map steps to agents** and capabilities
3. **Implement error handling** and rollback
4. **Add workflow monitoring** and logging

## Monitoring

### Agent Performance Dashboard
- **Response Times**: Track agent performance
- **Success Rates**: Monitor workflow completion
- **Error Patterns**: Identify common failures
- **Resource Usage**: Track system utilization

### Workflow Analytics
- **Popular Workflows**: Most used multi-agent flows
- **Bottlenecks**: Identify slow workflow steps
- **Agent Utilization**: Track agent workload distribution

## What's Next

Step 3 establishes sophisticated multi-agent coordination. The next steps will add:

- **Step 4**: AI-generated dynamic UI components
- **Step 5**: Advanced context engineering and memory management
- **Step 6**: Real-time collaboration and streaming responses

This multi-agent architecture demonstrates how AI can coordinate complex business processes through specialized, domain-expert agents working together seamlessly.