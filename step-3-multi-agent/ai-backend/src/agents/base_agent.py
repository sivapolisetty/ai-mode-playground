"""
Base Agent Class
Defines the common interface and capabilities for all specialized agents
"""
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Set
from loguru import logger


class AgentCapability(Enum):
    """Defines what capabilities each agent has"""
    PRODUCT_SEARCH = "product_search"
    INVENTORY_CHECK = "inventory_check"
    CUSTOMER_AUTH = "customer_auth"
    ORDER_CREATE = "order_create"
    ORDER_UPDATE = "order_update"
    SHIPPING_CALC = "shipping_calc"
    ADDRESS_VALIDATE = "address_validate"
    RULES_VALIDATE = "rules_validate"
    PAYMENT_PROCESS = "payment_process"
    NOTIFICATION_SEND = "notification_send"


@dataclass
class AgentMessage:
    """Message format for inter-agent communication"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str = ""
    to_agent: str = ""
    workflow_id: str = ""
    action: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    priority: int = 1  # 1=high, 2=medium, 3=low
    requires_response: bool = True


@dataclass
class WorkflowContext:
    """Context shared across agents in a workflow"""
    workflow_id: str
    user_query: str
    customer_id: Optional[str] = None
    session_id: Optional[str] = None
    current_step: str = ""
    completed_steps: List[str] = field(default_factory=list)
    pending_steps: List[str] = field(default_factory=list)
    agent_data: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, agent_name: str, capabilities: Set[AgentCapability]):
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.status = "idle"  # idle, busy, error
        self.message_queue: List[AgentMessage] = []
        self.active_workflows: Dict[str, WorkflowContext] = {}
        
        # Performance metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.average_response_time = 0.0
        self.last_activity = time.time()
        
        logger.info(f"Initialized {agent_name} with capabilities: {[c.value for c in capabilities]}")
    
    @abstractmethod
    async def process_request(self, message: AgentMessage, context: WorkflowContext) -> Dict[str, Any]:
        """
        Process an incoming request with the given context
        
        Args:
            message: The request message
            context: Workflow context
            
        Returns:
            Dict containing the response data
        """
        pass
    
    @abstractmethod
    def get_capabilities_description(self) -> Dict[str, str]:
        """
        Get human-readable description of agent capabilities
        
        Returns:
            Dict mapping capability to description
        """
        pass
    
    def can_handle(self, capability: AgentCapability) -> bool:
        """Check if agent can handle a specific capability"""
        return capability in self.capabilities
    
    def add_message(self, message: AgentMessage):
        """Add message to agent's queue"""
        self.message_queue.append(message)
        logger.debug(f"{self.agent_name} received message: {message.action}")
    
    async def handle_message(self, message: AgentMessage, context: WorkflowContext) -> Dict[str, Any]:
        """
        Handle incoming message with error handling and metrics
        
        Args:
            message: The message to process
            context: Workflow context
            
        Returns:
            Response data
        """
        start_time = time.time()
        self.status = "busy"
        self.total_requests += 1
        
        try:
            logger.info(f"{self.agent_name} processing {message.action} for workflow {context.workflow_id}")
            
            # Update context
            context.current_step = message.action
            context.updated_at = time.time()
            
            # Process the request
            response = await self.process_request(message, context)
            
            # Update metrics
            duration = time.time() - start_time
            self.successful_requests += 1
            self.average_response_time = (
                (self.average_response_time * (self.successful_requests - 1) + duration) 
                / self.successful_requests
            )
            
            logger.info(f"{self.agent_name} completed {message.action} in {duration:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"{self.agent_name} failed to process {message.action}: {e}")
            raise
        finally:
            self.status = "idle"
            self.last_activity = time.time()
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and metrics"""
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "capabilities": [c.value for c in self.capabilities],
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate": self.successful_requests / max(1, self.total_requests),
            "average_response_time": self.average_response_time,
            "queue_length": len(self.message_queue),
            "active_workflows": len(self.active_workflows),
            "last_activity": self.last_activity
        }
    
    def update_workflow_context(self, context: WorkflowContext, updates: Dict[str, Any]):
        """Update workflow context with agent-specific data"""
        if self.agent_name not in context.agent_data:
            context.agent_data[self.agent_name] = {}
        
        context.agent_data[self.agent_name].update(updates)
        context.updated_at = time.time()
        
        logger.debug(f"{self.agent_name} updated workflow context: {updates}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            "agent": self.agent_name,
            "status": "healthy" if self.status != "error" else "unhealthy",
            "last_activity": self.last_activity,
            "response_time": self.average_response_time
        }