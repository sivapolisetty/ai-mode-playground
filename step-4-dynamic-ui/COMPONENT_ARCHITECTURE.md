# Step 4: Component Architecture - Intelligent Orchestration System

## High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             STEP 4: DYNAMIC UI SYSTEM                          │
│                        Intelligent LLM-Driven Orchestration                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────────────────────────────────────────────┐
│  React Client   │    │                AI Backend Server                        │
│   Port: 5173    │◄───┤                Port: 8001                              │
└─────────────────┘    └─────────────────────────────────────────────────────────┘
                                                │
                       ┌────────────────────────┼────────────────────────┐
                       │                        │                        │
              ┌────────▼────────┐    ┌─────────▼─────────┐    ┌─────────▼─────────┐
              │ Traditional API │    │   Ollama LLM      │    │  Qdrant Vector   │
              │ Express+SQLite  │    │   Gemma 3:12B     │    │     Database     │
              │   Port: 4000    │    │   Port: 11434     │    │   Port: 6333     │
              └─────────────────┘    └───────────────────┘    └───────────────────┘
```

## Detailed Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            AI BACKEND SERVER (FastAPI)                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   /chat         │  │   /health       │  │   /ui/*         │                │
│  │   Endpoint      │  │   Endpoint      │  │   Endpoints     │                │
│  └─────────┬───────┘  └─────────────────┘  └─────────────────┘                │
│            │                                                                   │
│  ┌─────────▼─────────┐                                                         │
│  │  Enhanced Agent   │  ◄─── Main Orchestration Controller                    │
│  │  • Query routing  │                                                         │
│  │  • Session mgmt   │                                                         │
│  │  • Fallbacks     │                                                         │
│  └─────────┬─────────┘                                                         │
└────────────┼─────────────────────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────────────────────┐
│                        INTELLIGENT ORCHESTRATION LAYER                      │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐   │
│  │ IntelligentOrch     │  │  IntentClassifier   │  │  ContextResolver    │   │
│  │ • LLM planning      │  │  • Query analysis   │  │  • Temporal refs    │   │
│  │ • Tool coordination │  │  • Entity extract   │  │  • Session context  │   │
│  │ • Multi-tool flows  │  │  • Confidence score │  │  • Customer ID      │   │
│  │ • Response synthesis│  └─────────┬───────────┘  └─────────┬───────────┘   │
│  └─────────┬───────────┘            │                        │               │
│            │            ┌───────────▼────────────────────────▼───────────┐   │
│            │            │           Ollama LLM Engine                    │   │
│            │            │         • Intent understanding                 │   │
│            │            │         • Tool selection logic                │   │
│            │            │         • Response generation                 │   │
│            │            └────────────────────────────────────────────────┘   │
└────────────┼──────────────────────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────────────────────┐
│                                MCP TOOLS LAYER                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                            MCPTools                                    │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │ │
│  │  │ Product Search  │  │ Customer Ops    │  │ Order Management │        │ │
│  │  │ • Smart search  │  │ • Get info      │  │ • Create order   │        │ │
│  │  │ • Price filters │  │ • Update data   │  │ • Track status   │        │ │
│  │  │ • Brand filters │  │ • Order history │  │ • Cancel orders  │        │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │ │
│  │                                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐                             │ │
│  │  │ Semantic        │  │ Price           │                             │ │
│  │  │ Expansion       │  │ Extraction      │                             │ │
│  │  │ laptop→macbook  │  │ "$2000"→filter  │                             │ │
│  │  └─────────────────┘  └─────────────────┘                             │ │
│  └─────────────────────────────────┬───────────────────────────────────────┘ │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │       Traditional API          │
                    │     Express + SQLite           │
                    │   • Products • Orders          │
                    │   • Customers • Categories     │
                    └─────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DYNAMIC UI GENERATION LAYER                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         UIComponentTools                                │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ Component       │  │ Layout          │  │ Action          │        │   │
│  │  │ Selection       │  │ Strategy        │  │ Generation      │        │   │
│  │  │ • Product cards │  │ • Grid layout   │  │ • View Details  │        │   │
│  │  │ • Order views   │  │ • List layout   │  │ • Add to Cart   │        │   │
│  │  │ • Comparison UI │  │ • Comparison    │  │ • Track Order   │        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  └─────────────────────────────────┬───────────────────────────────────────┘   │
│                                    │                                           │
│  ┌─────────────────────────────────▼───────────────────────────────────────┐   │
│  │                      COMPONENT REGISTRY SYSTEM                          │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ ComponentScanner │  │ ComponentCache  │  │ ComponentWatcher │        │   │
│  │  │ • AST parsing   │  │ • Memory cache   │  │ • File monitoring│        │   │
│  │  │ • Prop extract  │  │ • Performance   │  │ • Auto-refresh   │        │   │
│  │  │ • Type analysis │  │ • Hot reload     │  │ • Change detect  │        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                           │
│                    ┌───────────────▼───────────────┐                           │
│                    │    React Component Files      │                           │
│                    │   client/src/components/ui/   │                           │
│                    │ • Button • Card • Input       │                           │
│                    │ • Dialog • Table • Form       │                           │
│                    └───────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              RAG KNOWLEDGE LAYER                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                              RAGService                                  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ Query           │  │ Semantic        │  │ Hybrid          │        │   │
│  │  │ Classification  │  │ Search          │  │ Response        │        │   │
│  │  │ • FAQ queries   │  │ • Vector DB     │  │ • Knowledge +   │        │   │
│  │  │ • Business rules│  │ • Embeddings    │  │   Transactional │        │   │
│  │  │ • Transactional │  │ • Similarity    │  │ • Context aware │        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  └─────────────────────────────────┬───────────────────────────────────────┘   │
│                                    │                                           │
│  ┌─────────────────────────────────▼───────────────────────────────────────┐   │
│  │                         KNOWLEDGE BASES                                  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ FAQ Knowledge   │  │ Business Rules  │  │ UI Patterns     │        │   │
│  │  │ • Common Qs     │  │ • Policies      │  │ • Component     │        │   │
│  │  │ • Help topics   │  │ • Constraints   │  │   usage guides  │        │   │
│  │  │ • Support info  │  │ • Workflows     │  │ • Best practices│        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                           │
│                    ┌───────────────▼───────────────┐                           │
│                    │        Qdrant Vector DB       │                           │
│                    │      Semantic Embeddings      │                           │
│                    │    • FAQ vectors              │                           │
│                    │    • Business rule vectors    │                           │
│                    └───────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Request Flow Architecture

```
USER QUERY: "Find laptops under $2000"
│
├── 1. FastAPI Endpoint (/chat)
│   └── Request validation & routing
│
├── 2. Enhanced Agent
│   ├── Try: process_query_with_orchestration()
│   └── Fallback: traditional processing
│
├── 3. Intelligent Orchestration
│   ├── A. Intent Classification
│   │   ├── Query: "Find laptops under $2000"
│   │   ├── LLM Analysis → Intent: "product_search" 
│   │   └── Confidence: 0.95
│   │
│   ├── B. Context Resolution  
│   │   ├── Session context: customer_id, preferences
│   │   ├── Temporal refs: "last", "recent" → specific entities
│   │   └── Execution context: {customer_id: "cust_001"}
│   │
│   ├── C. Execution Planning
│   │   ├── LLM decides: use "search_products" tool
│   │   ├── Parameters: {query: "laptops", max_price: 2000}
│   │   └── Reasoning: "Product search with price constraint"
│   │
│   ├── D. Tool Execution
│   │   ├── Call: MCPTools.search_products()
│   │   ├── Semantic expansion: laptop → [macbook, notebook]
│   │   ├── Price extraction: "$2000" → max_price filter
│   │   ├── API call: Traditional API /products
│   │   └── Result: [MacBook Air M2: $1199.99]
│   │
│   ├── E. UI Generation
│   │   ├── Analyze results: 1 product found
│   │   ├── Select template: Product card
│   │   ├── Generate props: {title, price, image, actions}
│   │   └── Actions: [View Details, Add to Cart]
│   │
│   └── F. Response Synthesis
│       ├── LLM synthesizes natural response
│       ├── Combines: tool results + UI components
│       └── Result: {message, ui_components, orchestration}
│
├── 4. Response Assembly
│   ├── Message: "I found one laptop under $2000..."
│   ├── UI Components: [ProductCard with actions]
│   ├── Debug info: {tools_used, reasoning, timing}
│   └── Processing type: "orchestration"
│
└── 5. Client Response
    ├── Natural language response
    ├── Dynamic UI components
    └── Interactive actions
```

## Key Architectural Principles

### 🧠 **Intelligence-First Design**
- LLM makes all routing decisions
- No hardcoded business logic
- Dynamic parameter extraction

### 🔗 **Orchestration Pattern**  
- Multi-tool coordination
- Sequential and parallel execution
- Intelligent result synthesis

### 🎨 **Dynamic UI Generation**
- Context-aware component selection
- Automatic prop generation
- Action-driven interactions

### 🔄 **Graceful Degradation**
- Orchestration → Intent Classification → RAG → Direct
- Always returns a response
- Performance-optimized fallbacks

### ⚡ **Performance Optimization**
- Component caching system
- Hot reload capabilities  
- Parallel tool execution
- Smart session management

## Scalability & Extensions

### **Horizontal Scaling**
```
Load Balancer → [AI Backend 1, AI Backend 2, AI Backend 3]
                     ↓           ↓           ↓
                Shared Ollama LLM Service
                     ↓           ↓           ↓  
                Shared Qdrant Vector DB
```

### **New Tool Integration**
```python
# Add to MCPTools
async def new_business_tool(self, params): 
    # Implementation

# LLM automatically discovers and uses it
# No code changes needed for orchestration
```

### **UI Component Extensions**
```typescript
// Add new component to /components/ui/
export const NewComponent = (props) => { ... }

// ComponentScanner automatically discovers
// UIComponentTools automatically uses
```

This architecture represents the **evolution from static business logic to dynamic, LLM-driven intelligence** where the system can adapt to any business requirement without code changes.