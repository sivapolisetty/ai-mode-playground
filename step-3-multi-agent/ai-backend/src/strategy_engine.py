"""
Dynamic Strategy Engine
Interprets text-based business strategies from knowledge base and executes them
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class StrategyContext:
    """Context for strategy evaluation and execution"""
    user_query: str
    order_data: Dict[str, Any]
    customer_data: Dict[str, Any]
    current_situation: Dict[str, Any]
    requested_changes: Dict[str, Any]


@dataclass 
class StrategyAction:
    """Represents a single action within a strategy"""
    description: str
    agent: str
    action_type: str
    parameters: Dict[str, Any]
    

class StrategyEngine:
    """
    Dynamic strategy engine that evaluates business conditions and executes 
    appropriate strategies based on text-based business rules
    """
    
    def __init__(self, knowledge_path: str = None):
        self.strategies = {}
        self.fallback_strategy = None
        
        # Load strategies from knowledge base
        if knowledge_path:
            self.load_strategies(knowledge_path)
    
    def load_strategies(self, knowledge_path: str):
        """Load business strategies from JSON knowledge base"""
        try:
            with open(knowledge_path, 'r') as f:
                data = json.load(f)
                
            self.strategies = {s['id']: s for s in data.get('strategies', [])}
            self.fallback_strategy = data.get('fallback_strategy')
            
            logger.info(f"Loaded {len(self.strategies)} business strategies")
            
        except Exception as e:
            logger.error(f"Failed to load strategies: {e}")
    
    async def evaluate_strategies(self, context: StrategyContext) -> Optional[Dict[str, Any]]:
        """
        Evaluate all strategies against current context and return the best match
        
        Args:
            context: Current situation and requirements
            
        Returns:
            Selected strategy or None if no match
        """
        try:
            applicable_strategies = []
            
            for strategy_id, strategy in self.strategies.items():
                conditions_met = await self._evaluate_conditions(
                    strategy.get('conditions', []), 
                    context
                )
                
                if conditions_met:
                    applicable_strategies.append({
                        'strategy': strategy,
                        'priority': strategy.get('priority', 999)
                    })
            
            # Sort by priority (lower number = higher priority)
            applicable_strategies.sort(key=lambda x: x['priority'])
            
            if applicable_strategies:
                selected = applicable_strategies[0]['strategy']
                logger.info(f"Selected strategy: {selected['name']}")
                return selected
            
            # Return fallback if no strategies match
            logger.warning("No strategies matched, using fallback")
            return self.fallback_strategy
            
        except Exception as e:
            logger.error(f"Strategy evaluation failed: {e}")
            return self.fallback_strategy
    
    async def _evaluate_conditions(self, conditions: List[str], context: StrategyContext) -> bool:
        """
        Evaluate if all strategy conditions are met
        
        Args:
            conditions: List of condition descriptions in natural language
            context: Current context to evaluate against
            
        Returns:
            True if all conditions are met
        """
        try:
            order_status = context.order_data.get('status', '').upper()
            order_age_hours = context.current_situation.get('order_age_hours', 0)
            
            for condition in conditions:
                condition_lower = condition.lower()
                
                # Order status conditions
                if 'pending' in condition_lower and 'pending' not in order_status.lower():
                    return False
                if 'confirmed' in condition_lower and 'confirmed' not in order_status.lower():
                    return False
                if 'shipped' in condition_lower and 'shipped' not in order_status.lower():
                    return False
                
                # Time-based conditions
                if 'within 24 hours' in condition_lower and order_age_hours > 24:
                    return False
                if 'outside change window' in condition_lower and order_age_hours <= 24:
                    return False
                
                # Address validation conditions
                if 'new address is valid' in condition_lower:
                    new_address = context.requested_changes.get('new_address')
                    if not new_address or not self._is_valid_address(new_address):
                        return False
                
                # Change possibility conditions
                if 'direct address change not possible' in condition_lower:
                    if order_status in ['PENDING', 'CONFIRMED'] and order_age_hours <= 24:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    def _is_valid_address(self, address: Dict[str, Any]) -> bool:
        """Simple address validation"""
        required_fields = ['street', 'city', 'state', 'zip']
        return all(address.get(field) for field in required_fields)
    
    async def execute_strategy(self, strategy: Dict[str, Any], context: StrategyContext) -> Dict[str, Any]:
        """
        Execute the selected strategy by converting actions to agent instructions
        
        Args:
            strategy: Selected business strategy
            context: Current context
            
        Returns:
            Execution plan for agents
        """
        try:
            actions = strategy.get('actions', [])
            execution_plan = {
                'strategy_name': strategy.get('name'),
                'strategy_description': strategy.get('description'),
                'agent_instructions': [],
                'workflow_steps': []
            }
            
            for i, action_desc in enumerate(actions):
                agent_instruction = await self._convert_action_to_instruction(
                    action_desc, context, step_number=i+1
                )
                execution_plan['agent_instructions'].append(agent_instruction)
            
            return execution_plan
            
        except Exception as e:
            logger.error(f"Strategy execution failed: {e}")
            return {'error': str(e)}
    
    async def _convert_action_to_instruction(self, action_desc: str, context: StrategyContext, step_number: int) -> Dict[str, Any]:
        """
        Convert natural language action description to specific agent instruction
        
        Args:
            action_desc: Natural language action description
            context: Current context
            step_number: Step number in workflow
            
        Returns:
            Agent instruction with specific parameters
        """
        action_lower = action_desc.lower()
        
        # Cancel order actions
        if 'cancel' in action_lower and 'order' in action_lower:
            return {
                'step': step_number,
                'agent': 'order_agent',
                'action': 'cancel_order',
                'description': action_desc,
                'parameters': {
                    'order_id': context.order_data.get('order_id'),
                    'reason': 'Address change requested'
                }
            }
        
        # Gift card actions
        elif 'gift card' in action_lower and 'issue' in action_lower:
            return {
                'step': step_number,
                'agent': 'payment_agent',
                'action': 'issue_gift_card',
                'description': action_desc,
                'parameters': {
                    'amount': context.order_data.get('total_amount'),
                    'customer_id': context.customer_data.get('customer_id'),
                    'reason': 'Order cancellation for address change'
                }
            }
        
        # Create new order actions
        elif 'create new order' in action_lower:
            return {
                'step': step_number,
                'agent': 'order_agent', 
                'action': 'create_order',
                'description': action_desc,
                'parameters': {
                    'customer_id': context.customer_data.get('customer_id'),
                    'items': context.order_data.get('items', []),
                    'shipping_address': context.requested_changes.get('new_address'),
                    'payment_method': {'type': 'gift_card'}
                }
            }
        
        # Address validation actions
        elif 'validate' in action_lower and 'address' in action_lower:
            return {
                'step': step_number,
                'agent': 'shipping_agent',
                'action': 'validate_address',
                'description': action_desc,
                'parameters': {
                    'address': context.requested_changes.get('new_address')
                }
            }
        
        # Update order actions
        elif 'update order' in action_lower:
            return {
                'step': step_number,
                'agent': 'order_agent',
                'action': 'update_order',
                'description': action_desc,
                'parameters': {
                    'order_id': context.order_data.get('order_id'),
                    'updates': context.requested_changes
                }
            }
        
        # Customer notification actions
        elif 'send confirmation' in action_lower or 'notify customer' in action_lower:
            return {
                'step': step_number,
                'agent': 'customer_agent',
                'action': 'send_notification',
                'description': action_desc,
                'parameters': {
                    'customer_id': context.customer_data.get('customer_id'),
                    'message_type': 'address_change_confirmation',
                    'details': context.requested_changes
                }
            }
        
        # Default fallback
        else:
            return {
                'step': step_number,
                'agent': 'rules_agent',
                'action': 'execute_custom_action',
                'description': action_desc,
                'parameters': {
                    'action_description': action_desc,
                    'context': context.__dict__
                }
            }