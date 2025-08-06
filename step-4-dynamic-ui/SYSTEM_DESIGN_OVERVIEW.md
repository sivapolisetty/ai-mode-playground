# Step 4: System Design Overview - Intelligent Orchestration

## Component Relationship Diagram

```
                    ┌─────────────────────────────────────────┐
                    │           REACT CLIENT                  │
                    │         (Port: 5173)                    │
                    └─────────────┬───────────────────────────┘
                                  │ HTTP Requests
                                  │
    ┌─────────────────────────────▼───────────────────────────────┐
    │                  FASTAPI SERVER                             │
    │                  (Port: 8001)                               │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
    │  │/chat        │  │/health      │  │/ui/*                │ │
    │  │endpoint     │  │endpoint     │  │endpoints            │ │
    │  └─────────────┘  └─────────────┘  └─────────────────────┘ │
    │                           │                                 │
    │  ┌───────────────────────▼──────────────────────────────┐  │
    │  │             ENHANCED AGENT                           │  │
    │  │   • Request routing & orchestration                  │  │
    │  │   • Session management                               │  │
    │  │   • Fallback handling                                │  │
    │  └─────────────┬────────────────────────────────────────┘  │
    └────────────────┼─────────────────────────────────────────────┘
                     │
    ┌────────────────▼─────────────────────────────────────────────┐
    │              INTELLIGENCE LAYER                              │
    │                                                              │
    │  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐│
    │  │ INTELLIGENT     │   │ INTENT          │   │ CONTEXT     ││
    │  │ ORCHESTRATOR    │◄──┤ CLASSIFIER      │◄──┤ RESOLVER    ││
    │  │                 │   │                 │   │             ││
    │  │• LLM planning   │   │• Query analysis │   │• Temporal   ││
    │  │• Tool selection │   │• Entity extract │   │  resolution ││
    │  │• Multi-tool     │   │• Confidence     │   │• Session    ││
    │  │  coordination   │   │  scoring        │   │  context    ││
    │  │• Response       │   │                 │   │             ││
    │  │  synthesis      │   │                 │   │             ││
    │  └─────────┬───────┘   └─────────────────┘   └─────────────┘│
    └────────────┼──────────────────────────────────────────────────┘
                 │                    ┌─────────────────────────────┐
                 │◄───────────────────┤      OLLAMA LLM             │
                 │                    │    (Port: 11434)            │
                 │                    │  • Intent understanding     │
                 │                    │  • Tool selection logic     │
                 │                    │  • Response generation      │
                 │                    └─────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────────────────────────┐
    │                    TOOL EXECUTION LAYER                       │
    │                                                               │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │                    MCP TOOLS                            │ │
    │  │                                                         │ │
    │  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │ │
    │  │ │ Product     │ │ Customer    │ │ Order Management    │ │ │
    │  │ │ Search      │ │ Operations  │ │                     │ │ │
    │  │ └─────────────┘ └─────────────┘ └─────────────────────┘ │ │
    │  │                                                         │ │
    │  │ ┌─────────────┐ ┌─────────────────────────────────────┐ │ │
    │  │ │ Semantic    │ │ Price Constraint Extraction         │ │ │
    │  │ │ Expansion   │ │ "under $2000" → max_price: 2000     │ │ │
    │  │ └─────────────┘ └─────────────────────────────────────┘ │ │
    │  └─────────────────────┬───────────────────────────────────┘ │
    └────────────────────────┼─────────────────────────────────────┘
                             │
           ┌─────────────────▼─────────────────┐
           │      TRADITIONAL API              │
           │    (Express + SQLite)             │
           │      (Port: 4000)                 │
           │                                   │
           │ ┌─────────┐ ┌─────────┐ ┌───────┐ │
           │ │Products │ │Customers│ │Orders │ │
           │ └─────────┘ └─────────┘ └───────┘ │
           └───────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │                UI GENERATION LAYER                          │
    │                                                             │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │               UI COMPONENT TOOLS                    │   │
    │  │                                                     │   │
    │  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐ │   │
    │  │ │ Component   │ │ Layout      │ │ Action          │ │   │
    │  │ │ Selection   │ │ Strategy    │ │ Generation      │ │   │
    │  │ └─────────────┘ └─────────────┘ └─────────────────┘ │   │
    │  └─────────────────────┬───────────────────────────────┘   │
    │                        │                                   │
    │  ┌─────────────────────▼───────────────────────────────┐   │
    │  │            COMPONENT REGISTRY                       │   │
    │  │                                                     │   │
    │  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐ │   │
    │  │ │ Component   │ │ Component   │ │ Component       │ │   │
    │  │ │ Scanner     │ │ Cache       │ │ Watcher         │ │   │
    │  │ └─────────────┘ └─────────────┘ └─────────────────┘ │   │
    │  └─────────────────────┬───────────────────────────────┘   │
    └────────────────────────┼─────────────────────────────────────┘
                             │
           ┌─────────────────▼─────────────────┐
           │    REACT COMPONENTS               │
           │  client/src/components/ui/        │
           │                                   │
           │ ┌─────────┐ ┌─────────┐ ┌───────┐ │
           │ │ Button  │ │  Card   │ │ Input │ │
           │ │ Dialog  │ │  Table  │ │ Form  │ │
           │ └─────────┘ └─────────┘ └───────┘ │
           └───────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │                 KNOWLEDGE LAYER                             │
    │                                                             │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │                 RAG SERVICE                         │   │
    │  │                                                     │   │
    │  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐ │   │
    │  │ │ Query       │ │ Semantic    │ │ Hybrid          │ │   │
    │  │ │ Classifier  │ │ Search      │ │ Response        │ │   │
    │  │ └─────────────┘ └─────────────┘ └─────────────────┘ │   │
    │  └─────────────────────┬───────────────────────────────┘   │
    │                        │                                   │
    │  ┌─────────────────────▼───────────────────────────────┐   │
    │  │              KNOWLEDGE BASES                        │   │
    │  │                                                     │   │
    │  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐ │   │
    │  │ │ FAQ         │ │ Business    │ │ UI Patterns     │ │   │
    │  │ │ Knowledge   │ │ Rules       │ │                 │ │   │
    │  │ └─────────────┘ └─────────────┘ └─────────────────┘ │   │
    │  └─────────────────────┬───────────────────────────────┘   │
    └────────────────────────┼─────────────────────────────────────┘
                             │
           ┌─────────────────▼─────────────────┐
           │       QDRANT VECTOR DB            │
           │       (Port: 6333)                │
           │                                   │
           │ ┌─────────┐ ┌─────────┐ ┌───────┐ │
           │ │FAQ      │ │Business │ │ UI    │ │
           │ │Vectors  │ │Vectors  │ │Vectors│ │
           │ └─────────┘ └─────────┘ └───────┘ │
           └───────────────────────────────────┘
```

## Core System Interactions

### **1. Request Processing Flow**
```
Client Request → FastAPI → Enhanced Agent → Intelligent Orchestrator
    ↓
LLM Analysis (Intent + Context) → Tool Selection → Execution Plan
    ↓  
MCP Tools → Traditional API → Data Retrieval
    ↓
UI Component Generation → Response Synthesis → Client Response
```

### **2. Intelligence Decision Points**

| Decision Point | Component | Logic |
|---------------|-----------|--------|
| **Query Understanding** | IntentClassifier | LLM analyzes user intent |
| **Tool Selection** | IntelligentOrchestrator | LLM chooses appropriate tools |
| **Parameter Extraction** | MCPTools | Smart parsing (prices, constraints) |
| **UI Component Choice** | UIComponentTools | Context-based selection |
| **Response Synthesis** | IntelligentOrchestrator | LLM combines results |

### **3. Data Flow Patterns**

#### **Single Tool Scenario:**
```
"Find laptops under $2000"
    ↓
Intent: product_search → search_products → MacBook Air M2
    ↓
UI: ProductCard + Actions → "I found one laptop for $1199.99"
```

#### **Multi-Tool Scenario:**
```
"Compare iPhone 15 Pro and Samsung Galaxy S24"
    ↓
Intent: product_comparison → [search_products, search_products]
    ↓
UI: [ProductCard, ProductCard] → "Here's a comparison..."
```

#### **Context-Aware Scenario:**
```
"Track my last order" (with customer_id in session)
    ↓
Intent: order_tracking → [get_customer_orders, track_order]
    ↓
UI: OrderTrackingCard → "Your last order is..."
```

## Key Architectural Advantages

### **🧠 Intelligence-First**
- **No hardcoded business logic** - LLM decides everything
- **Natural language understanding** - Handles diverse query patterns
- **Context-aware processing** - Uses session and customer data

### **🔗 Orchestration Excellence**
- **Multi-tool coordination** - Complex workflows handled automatically
- **Parallel execution** - Multiple tools can run concurrently
- **Intelligent synthesis** - LLM combines results meaningfully

### **🎨 Dynamic UI**
- **Context-based components** - UI adapts to query and results
- **Automatic prop generation** - Components populated intelligently
- **Action-driven interactions** - Buttons and links generated dynamically

### **⚡ Performance & Scalability**
- **Component caching** - AST parsing cached for performance
- **Graceful degradation** - Multiple fallback layers
- **Stateless design** - Horizontally scalable architecture

### **🔄 Extensibility**
- **New tools** - Easy to add without code changes
- **New UI components** - Automatically discovered and used
- **New query patterns** - LLM adapts without training

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API Gateway** | FastAPI | Async request handling |
| **Intelligence** | Ollama (Gemma 3:12B) | LLM reasoning engine |
| **Data Store** | SQLite + Express | Traditional data persistence |
| **Vector Search** | Qdrant | Semantic knowledge search |
| **Component Analysis** | Python AST | React component parsing |
| **UI Framework** | React + Radix UI | Frontend components |
| **Caching** | In-memory + File | Performance optimization |

## Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Development   │    │     Staging     │    │   Production    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Local Ollama  │    │ • Cloud LLM     │    │ • Load Balanced │
│ • SQLite        │    │ • PostgreSQL    │    │ • Redis Cache   │
│ • File Cache    │    │ • Redis Cache   │    │ • CDN Assets    │
│ • Hot Reload    │    │ • Docker        │    │ • Auto Scale    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

This architecture represents a **fundamental paradigm shift** from traditional static business logic to **dynamic, LLM-driven intelligence** where the system can adapt to any business requirement without code modifications.

The key innovation is the **Intelligent Orchestration Layer** that replaces hardcoded routing with LLM-based decision making, enabling true business agility and unlimited query pattern support.