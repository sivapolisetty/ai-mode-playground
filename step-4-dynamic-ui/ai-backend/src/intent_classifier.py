"""
Intent Classification System for Intelligent Query Understanding

This module provides LLM-based intent understanding to properly classify
user queries and extract structured information needed for action execution.
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
from loguru import logger

class IntentType(Enum):
    """Types of user intents the system can handle"""
    # Product-related
    PRODUCT_SEARCH = "product_search"
    PRODUCT_DETAILS = "product_details"
    PRODUCT_COMPARISON = "product_comparison"
    
    # Order-related
    ORDER_CREATE = "order_create"
    ORDER_UPDATE = "order_update"
    ORDER_CANCEL = "order_cancel"
    ORDER_STATUS = "order_status"
    ORDER_HISTORY = "order_history"
    
    # Customer-related
    CUSTOMER_INFO = "customer_info"
    CUSTOMER_UPDATE = "customer_update"
    CUSTOMER_SUPPORT = "customer_support"
    
    # Knowledge-related
    FAQ = "faq"
    POLICY = "policy"
    HELP = "help"
    
    # General
    GREETING = "greeting"
    UNKNOWN = "unknown"

class EntityType(Enum):
    """Types of entities that can be referenced in queries"""
    PRODUCT = "product"
    ORDER = "order"
    CUSTOMER = "customer"
    ADDRESS = "address"
    PAYMENT = "payment"
    DELIVERY = "delivery"

class TemporalReference(Enum):
    """Types of temporal references in queries"""
    LAST = "last"
    RECENT = "recent"
    CURRENT = "current"
    SPECIFIC_DATE = "specific_date"
    DATE_RANGE = "date_range"
    NONE = "none"

class IntentClassifier:
    """
    LLM-based intent classifier for understanding user queries
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.intent_patterns = self._initialize_patterns()
        
    def _initialize_patterns(self) -> Dict[IntentType, List[str]]:
        """Initialize keyword patterns for initial intent detection"""
        return {
            IntentType.PRODUCT_SEARCH: ["find", "search", "looking for", "show me", "need", "want to buy"],
            IntentType.PRODUCT_DETAILS: ["tell me about", "what is", "details", "specifications", "features"],
            IntentType.ORDER_UPDATE: ["change", "update", "modify", "edit", "correct"],
            IntentType.ORDER_CANCEL: ["cancel", "stop", "don't want", "return"],
            IntentType.ORDER_STATUS: ["where is", "track", "status", "when will", "delivery date"],
            IntentType.ORDER_CREATE: ["order", "buy", "purchase", "checkout", "add to cart"],
            IntentType.ORDER_HISTORY: ["my orders", "past orders", "order history", "previous purchases"],
            IntentType.CUSTOMER_UPDATE: ["update my", "change my", "edit profile"],
            IntentType.FAQ: ["how do", "how to", "can I", "is it possible"],
            IntentType.POLICY: ["policy", "terms", "conditions", "warranty", "guarantee"],
        }
    
    async def classify_intent(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify user intent using LLM for sophisticated understanding
        
        Args:
            query: User's natural language query
            context: Session context (customer_id, previous_queries, etc.)
            
        Returns:
            Structured intent information including type, entities, and actions
        """
        try:
            # First, try quick pattern matching for obvious cases
            quick_intent = self._quick_classify(query.lower())
            
            # Then use LLM for detailed analysis
            detailed_intent = await self._llm_classify(query, context, quick_intent)
            
            # Combine and validate
            final_intent = self._validate_and_combine(quick_intent, detailed_intent, context)
            
            logger.info(f"Classified intent for query '{query[:50]}...': {final_intent['intent_type']}")
            return final_intent
            
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return self._fallback_intent(query)
    
    def _quick_classify(self, query_lower: str) -> Optional[IntentType]:
        """Quick pattern-based classification for obvious intents"""
        for intent_type, patterns in self.intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent_type
        return None
    
    async def _llm_classify(self, query: str, context: Dict[str, Any], quick_intent: Optional[IntentType]) -> Dict[str, Any]:
        """Use LLM for sophisticated intent understanding"""
        
        prompt = f"""Analyze this user query and extract structured intent information.

User Query: "{query}"

Quick Classification Hint: {quick_intent.value if quick_intent else "None"}

Session Context:
- Customer ID: {context.get('customer_id', 'Not logged in')}
- Previous Query: {context.get('previous_query', 'None')}
- Current Page: {context.get('current_page', 'Unknown')}

Extract the following information:

1. PRIMARY INTENT - Choose from:
   - product_search: Looking for products
   - product_details: Asking about specific product details
   - order_create: Wanting to place an order
   - order_update: Wanting to modify an existing order
   - order_cancel: Wanting to cancel an order
   - order_status: Checking order status/delivery
   - order_history: Viewing past orders
   - customer_update: Updating customer information
   - faq: General help questions
   - policy: Questions about policies/terms

2. ACTION VERB - The main action (e.g., "change", "find", "track", "cancel")

3. TARGET ENTITY - What the action applies to:
   - product: Product-related
   - order: Order-related
   - customer: Customer account-related
   - address: Address-specific
   - payment: Payment-related

4. ENTITY REFERENCES - Specific items mentioned:
   - Product names/categories (e.g., "iPhone", "laptop")
   - Order references (e.g., "last order", "order #123")
   - Attributes (e.g., "address", "payment method")

5. TEMPORAL REFERENCES:
   - last: Most recent item
   - recent: Recent items (multiple)
   - specific_date: Specific date mentioned
   - none: No temporal reference

6. CONSTRAINTS - Any conditions or filters:
   - Price ranges: Extract numbers from "under $X", "below $X", "less than $X" → {"max_price": X}
   - Time constraints (e.g., "delivered by Friday")
   - Quantity (e.g., "2 items")
   - Categories (e.g., "laptops", "phones")

7. REQUIRED CONTEXT - What information is needed to fulfill this request:
   - customer_id: Need customer identification
   - order_id: Need specific order ID
   - product_id: Need specific product ID
   - none: No additional context needed

Return as JSON with this structure:
{{
  "intent_type": "primary intent from list above",
  "action": "main action verb",
  "target_entity": "entity type",
  "entity_references": ["specific items mentioned"],
  "temporal_reference": "temporal type",
  "constraints": {{"type": "value"}},
  "required_context": ["list of required context"],
  "confidence": 0.0-1.0
}}
"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            else:
                logger.warning(f"No JSON found in LLM response: {content[:200]}")
                return {}
                
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return {}
    
    def _validate_and_combine(self, quick_intent: Optional[IntentType], llm_intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and combine quick and LLM classification results"""
        
        # Start with LLM intent if available
        result = llm_intent.copy() if llm_intent else {}
        
        # Use quick intent as fallback
        if not result.get('intent_type') and quick_intent:
            result['intent_type'] = quick_intent.value
        
        # Ensure all required fields are present
        result.setdefault('intent_type', IntentType.UNKNOWN.value)
        result.setdefault('action', 'unknown')
        result.setdefault('target_entity', EntityType.PRODUCT.value)
        result.setdefault('entity_references', [])
        result.setdefault('temporal_reference', TemporalReference.NONE.value)
        result.setdefault('constraints', {})
        result.setdefault('required_context', [])
        result.setdefault('confidence', 0.5)
        
        # Add session context requirements
        if result['intent_type'] in ['order_update', 'order_cancel', 'order_status', 'order_history']:
            if 'customer_id' not in result['required_context']:
                result['required_context'].append('customer_id')
        
        # Validate temporal references for order-related intents
        if result['temporal_reference'] == 'last' and result['target_entity'] == 'order':
            result['requires_order_lookup'] = True
        
        return result
    
    def _fallback_intent(self, query: str) -> Dict[str, Any]:
        """Fallback intent when classification fails"""
        return {
            'intent_type': IntentType.UNKNOWN.value,
            'action': 'search',
            'target_entity': EntityType.PRODUCT.value,
            'entity_references': self._extract_potential_products(query),
            'temporal_reference': TemporalReference.NONE.value,
            'constraints': {},
            'required_context': [],
            'confidence': 0.1,
            'fallback': True
        }
    
    def _extract_potential_products(self, query: str) -> List[str]:
        """Extract potential product names from query"""
        # Simple extraction of capitalized words and known product keywords
        words = query.split()
        products = []
        
        known_products = ['iphone', 'macbook', 'laptop', 'phone', 'tablet', 'watch']
        for word in words:
            if word.lower() in known_products or word[0].isupper():
                products.append(word)
        
        return products
    
    def get_required_tools(self, intent: Dict[str, Any]) -> List[str]:
        """
        Determine which MCP tools are needed for this intent
        
        Args:
            intent: Classified intent dictionary
            
        Returns:
            List of required tool names
        """
        intent_type = intent.get('intent_type', '')
        tools = []
        
        # Map intent types to required tools
        tool_mapping = {
            'product_search': ['search_products'],
            'product_details': ['search_products', 'get_product_details'],
            'order_create': ['create_order', 'get_customer_info'],
            'order_update': ['get_order', 'update_order', 'get_customer_info'],
            'order_cancel': ['get_order', 'cancel_order', 'get_customer_info'],
            'order_status': ['get_order', 'track_order', 'get_customer_info'],
            'order_history': ['get_customer_orders', 'get_customer_info'],
            'customer_update': ['get_customer_info', 'update_customer'],
        }
        
        tools = tool_mapping.get(intent_type, ['search_products'])
        
        # Add additional tools based on constraints
        if intent.get('constraints', {}).get('delivery'):
            tools.append('calculate_delivery')
        
        if intent.get('constraints', {}).get('notification'):
            tools.append('send_notification')
        
        return list(set(tools))  # Remove duplicates
    
    def requires_authentication(self, intent: Dict[str, Any]) -> bool:
        """Check if this intent requires customer authentication"""
        auth_required_intents = [
            'order_create', 'order_update', 'order_cancel', 
            'order_status', 'order_history', 'customer_update'
        ]
        return intent.get('intent_type', '') in auth_required_intents