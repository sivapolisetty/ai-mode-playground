# Test Queries for Simplified Multi-Agent Architecture

## 🎯 Test the Strategy Engine (Your Main Use Case)

### 1. **Address Change - Cancel & Reorder Strategy**
```
"I want to change my delivery address but my iPhone 15 Pro order was already shipped. Can you change it to Oak Street Tree Apartment?"
```
**Expected Result:**
- Strategy engine selects "Cancel and Reorder with Gift Card"
- UnifiedBusinessAgent cancels order
- Creates gift card for full amount
- Creates new order with new address
- Applies gift card as payment

### 2. **Address Change - Standard Update**
```
"I just placed an order 1 hour ago for iPhone 15 Pro, can I change the delivery address to Oak Street Tree Apartment?"
```
**Expected Result:**
- Strategy engine selects "Standard Address Change"
- UnifiedBusinessAgent updates order directly
- Validates new address
- Recalculates shipping

### 3. **Address Completion Test**
```
"Place order for iPhone 15 Pro to Oak Street Tree Apartment address, possible to get in 2 days?"
```
**Expected Result:**
- Smart address extraction detects "Oak Street Tree Apartment"
- Asks for missing address details (city, state, zip, unit number)
- Offers 2-day delivery options

## 🛍️ Test Unified Business Agent Capabilities

### 4. **Complete Order Flow**
```
"I want to buy an iPhone 15 Pro and have it delivered to my home address with express shipping"
```
**Expected Result:**
- Product search → inventory check → address retrieval → shipping calculation → order creation → confirmation

### 5. **Product Availability**
```
"Do you have iPhone 15 Pro in stock? How quickly can it be delivered?"
```
**Expected Result:**
- Product search and availability check
- Delivery time estimates
- Shipping options

### 6. **Customer Profile Test**
```
"What's my order history and saved addresses?"
```
**Expected Result:**
- Customer authentication
- Profile retrieval with addresses and order history

## 🔄 Test Dynamic Workflows

### 7. **Complex Address Scenario**
```
"I need to change the delivery address for my recent order. The new address is 456 Oak Street Tree Apartment, unit 5B, but I'm not sure if changes are allowed since I ordered yesterday."
```
**Expected Result:**
- Strategy evaluation based on order timing
- Either standard update or cancel/reorder strategy
- Smart address completion for apartment details

### 8. **International Shipping**
```
"Can I change my delivery address to an international location? The order is for iPhone 15 Pro to London, UK."
```
**Expected Result:**
- Strategy engine detects international change
- Applies international shipping strategy
- Calculates customs and additional fees

## 🧠 Test Strategy Flexibility

### 9. **Priority Customer**
```
"I'm a premium customer with a $2000 order. I need to change the delivery address even though it's outside the normal change window."
```
**Expected Result:**
- Strategy engine could select priority customer strategy
- Override standard restrictions
- Apply expedited processing

### 10. **Business Rules Validation**
```
"I want to order 50 iPhone 15 Pro units for my company and have them delivered to different addresses."
```
**Expected Result:**
- Rules agent validates large order
- Checks business rules for bulk orders
- Handles multiple delivery addresses

## 🚀 Quick Start Test Commands

### Using curl (if server is running):
```bash
# Test address change strategy
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to change my delivery address but my order was already shipped",
    "context": {"customer_email": "john@example.com"}
  }'

# Test order placement with address completion
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Place order for iPhone 15 Pro to Oak Street Tree Apartment, get in 2 days",
    "context": {"customer_email": "john@example.com"}
  }'
```

### Using the UI (if available):
1. Start the server: `./setup.sh start`
2. Open the UI at `http://localhost:3000` 
3. Try any of the test queries above

## 🔍 What to Look For

### ✅ **Strategy Engine Working:**
- Different responses based on order status/timing
- "Cancel and reorder" for shipped orders
- Direct updates for recent orders

### ✅ **Address Intelligence:**
- Recognizes "Oak Street Tree Apartment"
- Asks for missing details (city, state, zip, unit)
- Smart completion with customer data

### ✅ **Unified Agent:**
- Single agent handles customer + product + order + shipping
- Fewer inter-agent calls in debug logs
- Consolidated responses

### ✅ **Business Flexibility:**
- Different strategies selected automatically
- No hard-coded limitations
- Product owner can add new strategies by editing JSON

## 🐛 Debug Information

### Check Logs For:
```
"Selected strategy: Cancel and Reorder with Gift Card"
"Executing strategy step: Cancel the existing order"
"Gift card created for $999.99"
"Simplified agent structure registered successfully"
"UnifiedBusinessAgent: 15 capabilities"
```

### Agent Activity:
- Should see `unified_business_agent` in logs instead of separate `customer_agent`, `product_agent`, etc.
- Strategy evaluation happening in `rules_agent`
- Dynamic workflow execution in orchestrator

Use these queries to verify the simplified architecture is working correctly! 🎯