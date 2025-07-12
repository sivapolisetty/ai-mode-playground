"""
Simplified Multi-Agent System Package
Contains streamlined agents with consolidated business operations
"""
from .base_agent import BaseAgent, AgentCapability, AgentMessage, WorkflowContext
from .agent_orchestrator import AgentOrchestrator
from .unified_business_agent import UnifiedBusinessAgent
from .rules_agent import RulesAgent

# Legacy imports available in deprecated/ folder if needed
# from .deprecated.customer_agent import CustomerAgent
# from .deprecated.product_agent import ProductAgent  
# from .deprecated.order_agent import OrderAgent
# from .deprecated.shipping_agent import ShippingAgent

__all__ = [
    'BaseAgent', 'AgentCapability', 'AgentMessage', 'WorkflowContext',
    'AgentOrchestrator', 'UnifiedBusinessAgent', 'RulesAgent'
]