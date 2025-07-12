# Deprecated Agents

## ⚠️ These agents are deprecated and replaced by UnifiedBusinessAgent

### What's Here:
- `customer_agent.py` - Customer management and authentication
- `product_agent.py` - Product catalog and inventory management  
- `order_agent.py` - Order lifecycle management
- `shipping_agent.py` - Delivery calculations and logistics

### ✅ New Simplified Architecture:
All functionality from these 4 agents has been consolidated into:
- **`UnifiedBusinessAgent`** - Handles all business operations via MCP tools
- **`RulesAgent`** - Business rules validation and strategy engine
- **`DynamicOrchestrator`** - Strategy-driven workflow execution

### 🔄 Migration Guide:
If you need to reference old functionality:

| Old Agent | New Location | Method |
|-----------|--------------|--------|
| `CustomerAgent.authenticate_customer()` | `UnifiedBusinessAgent.authenticate_customer()` | Same |
| `ProductAgent.search_product()` | `UnifiedBusinessAgent.search_product()` | Same |
| `OrderAgent.create_order()` | `UnifiedBusinessAgent.create_order()` | Same |
| `ShippingAgent.calculate_delivery()` | `UnifiedBusinessAgent.calculate_delivery()` | Same |

### 📊 Benefits of New Architecture:
- **50% fewer agents** (6 → 3)
- **Reduced complexity** and maintenance
- **Better performance** with fewer inter-agent calls
- **Preserved all functionality**
- **Enhanced flexibility** with strategy engine

### 🗑️ Cleanup:
These files can be safely deleted after confirming the new architecture works correctly.

**Do not import these deprecated agents in new code!**