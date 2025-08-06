"""
Context Resolution System for Temporal References and Entity Resolution

This module resolves contextual references like "last order", "my recent purchases",
"that product" into concrete entity IDs that can be used by MCP tools.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from loguru import logger

class ContextResolver:
    """
    Resolves contextual references in user queries to concrete entities
    """
    
    def __init__(self, mcp_tools):
        self.mcp_tools = mcp_tools
        self.resolution_cache = {}  # Cache resolved references per session
    
    async def resolve_references(self, intent: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve all contextual references in the intent
        
        Args:
            intent: Classified intent with potential references
            session: Session context with customer_id, history, etc.
            
        Returns:
            Resolved context with concrete entity IDs
        """
        resolved = {
            'original_intent': intent,
            'session': session,
            'resolved_entities': {},
            'resolution_status': 'success',
            'resolution_errors': []
        }
        
        try:
            # Resolve customer context first (most important)
            if self._requires_customer_context(intent):
                customer_context = await self._resolve_customer_context(session)
                if customer_context:
                    resolved['resolved_entities']['customer'] = customer_context
                else:
                    resolved['resolution_errors'].append("Customer not authenticated")
                    resolved['resolution_status'] = 'partial'
                    logger.warning(f"Customer context missing for intent: {intent['intent_type']}")
            else:
                # For intents that don't require customer context, add mock context if session has customer_id
                customer_id = session.get('customer_id')
                if customer_id:
                    resolved['resolved_entities']['customer'] = {'id': customer_id, 'customer_id': customer_id}
            
            # Resolve temporal references (last order, recent purchases, etc.)
            if intent.get('temporal_reference') != 'none':
                temporal_entities = await self._resolve_temporal_reference(
                    intent['temporal_reference'],
                    intent['target_entity'],
                    resolved.get('resolved_entities', {}).get('customer', {})
                )
                if temporal_entities:
                    resolved['resolved_entities'].update(temporal_entities)
            
            # Resolve entity references (specific products, orders mentioned)
            if intent.get('entity_references'):
                entity_refs = await self._resolve_entity_references(
                    intent['entity_references'],
                    intent['target_entity']
                )
                if entity_refs:
                    resolved['resolved_entities']['referenced_items'] = entity_refs
            
            # Resolve pronoun references from conversation history
            if self._has_pronoun_references(intent.get('action', '')):
                pronoun_refs = await self._resolve_pronoun_references(session)
                if pronoun_refs:
                    resolved['resolved_entities']['pronoun_references'] = pronoun_refs
            
            logger.info(f"Context resolution completed: {resolved['resolution_status']}")
            return resolved
            
        except Exception as e:
            logger.error(f"Context resolution failed: {e}")
            resolved['resolution_status'] = 'failed'
            resolved['resolution_errors'].append(str(e))
            return resolved
    
    def _requires_customer_context(self, intent: Dict[str, Any]) -> bool:
        """Check if intent requires customer authentication"""
        return 'customer_id' in intent.get('required_context', [])
    
    async def _resolve_customer_context(self, session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Resolve customer information from session"""
        customer_id = session.get('customer_id')
        if not customer_id:
            # Try to get from session token or other auth mechanism
            customer_id = session.get('user_id')
        
        if customer_id:
            try:
                # Get full customer info from MCP tools
                customer_info = await self.mcp_tools.get_customer_info(customer_id)
                if customer_info.get('success'):
                    return customer_info.get('data', {})
            except Exception as e:
                logger.error(f"Failed to get customer info: {e}")
        
        return None
    
    async def _resolve_temporal_reference(
        self, 
        temporal_type: str, 
        target_entity: str,
        customer_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve temporal references like 'last', 'recent', etc.
        
        Args:
            temporal_type: Type of temporal reference (last, recent, etc.)
            target_entity: Entity type being referenced (order, product, etc.)
            customer_context: Resolved customer information
            
        Returns:
            Dictionary with resolved entities
        """
        resolved = {}
        
        if not customer_context:
            logger.warning("Cannot resolve temporal reference without customer context")
            return resolved
        
        customer_id = customer_context.get('id') or customer_context.get('customer_id')
        
        try:
            if target_entity == 'order':
                if temporal_type == 'last':
                    # Get the most recent order
                    orders = await self.mcp_tools.get_customer_orders(customer_id, limit=1)
                    if orders and orders.get('success') and orders.get('data'):
                        resolved['last_order'] = orders['data'][0] if isinstance(orders['data'], list) else orders['data']
                        resolved['order_id'] = resolved['last_order'].get('id')
                        
                elif temporal_type == 'recent':
                    # Get recent orders (last 5)
                    orders = await self.mcp_tools.get_customer_orders(customer_id, limit=5)
                    if orders and orders.get('success'):
                        resolved['recent_orders'] = orders.get('data', [])
                        
                elif temporal_type == 'specific_date':
                    # Would need date extraction from intent
                    pass
                    
            elif target_entity == 'product':
                if temporal_type == 'last':
                    # Get last viewed/purchased product
                    # This might come from session history or order history
                    last_order = resolved.get('last_order')
                    if not last_order:
                        orders = await self.mcp_tools.get_customer_orders(customer_id, limit=1)
                        if orders and orders.get('success') and orders.get('data'):
                            last_order = orders['data'][0] if isinstance(orders['data'], list) else orders['data']
                    
                    if last_order and last_order.get('items'):
                        resolved['last_product'] = last_order['items'][0]
                        
                elif temporal_type == 'recent':
                    # Get recently viewed products from session
                    resolved['recent_products'] = customer_context.get('recently_viewed', [])
            
        except Exception as e:
            logger.error(f"Failed to resolve temporal reference: {e}")
        
        return resolved
    
    async def _resolve_entity_references(self, references: List[str], entity_type: str) -> List[Dict[str, Any]]:
        """
        Resolve specific entity references mentioned in the query
        
        Args:
            references: List of entity references from the query
            entity_type: Type of entity being referenced
            
        Returns:
            List of resolved entities
        """
        resolved = []
        
        for reference in references:
            try:
                if entity_type == 'product':
                    # Search for the product
                    results = await self.mcp_tools.search_products(reference)
                    if results and results.get('success') and results.get('data'):
                        products = results['data']
                        if products:
                            resolved.append({
                                'reference': reference,
                                'type': 'product',
                                'resolved_entity': products[0],
                                'alternatives': products[1:3] if len(products) > 1 else []
                            })
                            
                elif entity_type == 'order':
                    # Check if it's an order ID
                    if reference.startswith('#') or reference.upper().startswith('ORD'):
                        order = await self.mcp_tools.get_order(reference.strip('#'))
                        if order and order.get('success'):
                            resolved.append({
                                'reference': reference,
                                'type': 'order',
                                'resolved_entity': order.get('data')
                            })
                            
            except Exception as e:
                logger.error(f"Failed to resolve entity reference '{reference}': {e}")
        
        return resolved
    
    def _has_pronoun_references(self, action: str) -> bool:
        """Check if the query contains pronoun references that need resolution"""
        pronouns = ['it', 'that', 'this', 'them', 'those', 'these']
        return any(pronoun in action.lower() for pronoun in pronouns)
    
    async def _resolve_pronoun_references(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve pronoun references from conversation history
        
        Args:
            session: Session context with conversation history
            
        Returns:
            Resolved pronoun references
        """
        resolved = {}
        
        # Get the last mentioned entities from session
        conversation_history = session.get('conversation_history', [])
        if conversation_history:
            last_interaction = conversation_history[-1] if conversation_history else {}
            
            # Extract entities from last interaction
            if last_interaction.get('entities'):
                resolved['last_mentioned'] = last_interaction['entities']
            
            # Look for specific entity types in recent history
            for interaction in reversed(conversation_history[-3:]):  # Last 3 interactions
                if interaction.get('product_mentioned'):
                    resolved['last_product_mentioned'] = interaction['product_mentioned']
                    break
                if interaction.get('order_mentioned'):
                    resolved['last_order_mentioned'] = interaction['order_mentioned']
                    break
        
        return resolved
    
    def build_execution_context(self, resolved_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build final execution context for MCP tools
        
        Args:
            resolved_context: Fully resolved context
            
        Returns:
            Execution context ready for tool invocation
        """
        execution_context = {
            'intent': resolved_context['original_intent'],
            'customer': resolved_context.get('resolved_entities', {}).get('customer'),
            'entities': resolved_context.get('resolved_entities', {}),
            'session': resolved_context.get('session', {}),
            'ready_for_execution': resolved_context['resolution_status'] == 'success'
        }
        
        # Add specific entity IDs for easy access
        entities = resolved_context.get('resolved_entities', {})
        
        if entities.get('order_id'):
            execution_context['order_id'] = entities['order_id']
            
        if entities.get('last_order'):
            execution_context['target_order'] = entities['last_order']
            
        if entities.get('referenced_items'):
            execution_context['target_items'] = entities['referenced_items']
        
        # Add constraints from intent
        if resolved_context['original_intent'].get('constraints'):
            execution_context['constraints'] = resolved_context['original_intent']['constraints']
        
        return execution_context
    
    def get_missing_context(self, resolved_context: Dict[str, Any]) -> List[str]:
        """
        Identify what context is still missing for execution
        
        Args:
            resolved_context: Partially resolved context
            
        Returns:
            List of missing context items
        """
        missing = []
        intent = resolved_context.get('original_intent', {})
        resolved_entities = resolved_context.get('resolved_entities', {})
        
        # Check required context from intent
        for required in intent.get('required_context', []):
            if required == 'customer_id' and not resolved_entities.get('customer'):
                missing.append('customer_authentication')
            elif required == 'order_id' and not resolved_entities.get('order_id'):
                missing.append('order_identification')
            elif required == 'product_id' and not resolved_entities.get('referenced_items'):
                missing.append('product_specification')
        
        # Check for temporal resolution failures
        if intent.get('temporal_reference') != 'none':
            temporal_type = intent['temporal_reference']
            if temporal_type == 'last' and not resolved_entities.get('last_order'):
                missing.append('last_order_reference')
        
        return missing