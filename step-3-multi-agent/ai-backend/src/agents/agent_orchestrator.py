"""
Agent Orchestrator
Coordinates complex multi-agent workflows and manages inter-agent communication
"""
import time
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import asdict
from loguru import logger

from .base_agent import BaseAgent, AgentMessage, WorkflowContext, AgentCapability


class WorkflowStep:
    """Represents a single step in a workflow"""
    def __init__(self, agent_name: str, action: str, data: Dict[str, Any] = None, 
                 depends_on: List[str] = None, parallel: bool = False):
        self.agent_name = agent_name
        self.action = action
        self.data = data or {}
        self.depends_on = depends_on or []
        self.parallel = parallel
        self.completed = False
        self.result = None


class AgentOrchestrator:
    """Orchestrates multi-agent workflows"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, WorkflowContext] = {}
        self.workflow_definitions: Dict[str, List[WorkflowStep]] = {}
        
        # Performance tracking
        self.total_workflows = 0
        self.completed_workflows = 0
        self.failed_workflows = 0
        self.average_workflow_time = 0.0
        
        logger.info("Agent Orchestrator initialized")
        
        # Define standard workflows
        self._define_standard_workflows()
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_name] = agent
        logger.info(f"Registered agent: {agent.agent_name}")
    
    def _define_standard_workflows(self):
        """Define standard multi-agent workflows"""
        
        # Place Order Workflow
        self.workflow_definitions["place_order"] = [
            WorkflowStep("product_agent", "search_product", parallel=False),
            WorkflowStep("customer_agent", "authenticate_customer", parallel=True),
            WorkflowStep("product_agent", "check_inventory", depends_on=["search_product"]),
            WorkflowStep("customer_agent", "get_address", depends_on=["authenticate_customer"]),
            WorkflowStep("shipping_agent", "calculate_delivery", 
                        depends_on=["check_inventory", "get_address"]),
            WorkflowStep("rules_agent", "validate_order", 
                        depends_on=["check_inventory", "get_address"]),
            WorkflowStep("product_agent", "reserve_inventory", 
                        depends_on=["validate_order", "calculate_delivery"]),
            WorkflowStep("order_agent", "create_order", 
                        depends_on=["reserve_inventory"]),
            WorkflowStep("customer_agent", "send_confirmation", 
                        depends_on=["create_order"])
        ]
        
        # Address Change Workflow
        self.workflow_definitions["change_address"] = [
            WorkflowStep("customer_agent", "authenticate_customer"),
            WorkflowStep("order_agent", "get_order_details", 
                        depends_on=["authenticate_customer"]),
            WorkflowStep("rules_agent", "check_change_policy", 
                        depends_on=["get_order_details"]),
            WorkflowStep("shipping_agent", "validate_new_address", 
                        depends_on=["check_change_policy"]),
            WorkflowStep("shipping_agent", "recalculate_delivery", 
                        depends_on=["validate_new_address"]),
            WorkflowStep("order_agent", "update_order", 
                        depends_on=["recalculate_delivery"]),
            WorkflowStep("customer_agent", "notify_changes", 
                        depends_on=["update_order"])
        ]
        
        # Product Inquiry Workflow
        self.workflow_definitions["product_inquiry"] = [
            WorkflowStep("product_agent", "search_product"),
            WorkflowStep("product_agent", "check_availability", 
                        depends_on=["search_product"]),
            WorkflowStep("customer_agent", "get_location", parallel=True),
            WorkflowStep("shipping_agent", "estimate_delivery", 
                        depends_on=["check_availability", "get_location"])
        ]
    
    async def classify_user_intent(self, user_query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Classify user intent to determine appropriate workflow
        
        Args:
            user_query: User's natural language query
            
        Returns:
            Tuple of (workflow_name, extracted_data)
        """
        query_lower = user_query.lower()
        
        # Enhanced classification with address extraction
        if any(word in query_lower for word in ["place order", "buy", "purchase", "order"]):
            # Extract product and delivery preferences
            data = {
                "product_query": user_query,
                "delivery_preference": "standard"
            }
            
            # Extract delivery speed preference
            if "2 days" in query_lower or "fast" in query_lower or "express" in query_lower:
                data["delivery_preference"] = "express"
            elif "overnight" in query_lower:
                data["delivery_preference"] = "overnight"
            
            # Extract address information from query using MCP tools
            address_info = await self._extract_address_from_query(user_query)
            if address_info:
                data["delivery_address"] = address_info
            
            return "place_order", data
            
        elif any(word in query_lower for word in ["change address", "update address", "delivery address"]):
            # Extract order ID if mentioned
            data = {}
            words = query_lower.split()
            for i, word in enumerate(words):
                if word in ["order", "#"] and i + 1 < len(words):
                    data["order_id"] = words[i + 1].replace("#", "")
                    break
            return "change_address", data
            
        elif any(word in query_lower for word in ["do you have", "in stock", "available", "delivery to"]):
            return "product_inquiry", {"product_query": user_query}
            
        else:
            # Default to product inquiry for product-related queries
            return "product_inquiry", {"product_query": user_query}
    
    async def _extract_address_from_query(self, user_query: str) -> Optional[Dict[str, Any]]:
        """
        Extract address information from user query using MCP tools
        
        Args:
            user_query: User's natural language query
            
        Returns:
            Dictionary with extracted address components or None
        """
        # Use MCP tools for address extraction
        from tools.mcp_tools import MCPTools
        
        mcp_tools = MCPTools()
        try:
            extraction_result = await mcp_tools.extract_address_from_text(user_query)
            
            if extraction_result.get("success"):
                address_data = extraction_result.get("data", {})
                # Only return if we found meaningful address information
                if address_data and (address_data.get('street') or address_data.get('city') or address_data.get('type') != 'shipping'):
                    return address_data
            
            return None
            
        except Exception as e:
            logger.error(f"Address extraction failed: {e}")
            return None
        finally:
            await mcp_tools.close()
    
    async def start_workflow(self, workflow_name: str, user_query: str, 
                           context_data: Dict[str, Any] = None) -> str:
        """
        Start a new multi-agent workflow
        
        Args:
            workflow_name: Name of the workflow to execute
            user_query: Original user query
            context_data: Additional context data
            
        Returns:
            Workflow ID
        """
        if workflow_name not in self.workflow_definitions:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow_id = str(uuid.uuid4())
        context = WorkflowContext(
            workflow_id=workflow_id,
            user_query=user_query,
            metadata=context_data or {}
        )
        
        self.workflows[workflow_id] = context
        self.total_workflows += 1
        
        logger.info(f"Starting workflow {workflow_name} with ID {workflow_id}")
        
        try:
            result = await self._execute_workflow(workflow_name, context)
            self.completed_workflows += 1
            logger.info(f"Completed workflow {workflow_id}")
            return workflow_id
            
        except Exception as e:
            self.failed_workflows += 1
            logger.error(f"Workflow {workflow_id} failed: {e}")
            raise
    
    async def _execute_workflow(self, workflow_name: str, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute a multi-agent workflow
        
        Args:
            workflow_name: Name of the workflow
            context: Workflow context
            
        Returns:
            Final workflow result
        """
        steps = self.workflow_definitions[workflow_name].copy()
        completed_steps = set()
        
        while steps:
            # Find steps that can be executed (dependencies satisfied)
            ready_steps = []
            for step in steps:
                if all(dep in completed_steps for dep in step.depends_on):
                    ready_steps.append(step)
            
            if not ready_steps:
                raise RuntimeError(f"Workflow deadlock in {workflow_name}")
            
            # Group parallel steps
            parallel_steps = [s for s in ready_steps if s.parallel]
            sequential_steps = [s for s in ready_steps if not s.parallel]
            
            # Execute parallel steps concurrently
            if parallel_steps:
                tasks = []
                for step in parallel_steps:
                    task = self._execute_step(step, context)
                    tasks.append(task)
                
                await asyncio.gather(*tasks)
                
                for step in parallel_steps:
                    completed_steps.add(step.action)
                    context.completed_steps.append(step.action)
                    steps.remove(step)
            
            # Execute sequential steps one by one
            for step in sequential_steps:
                await self._execute_step(step, context)
                completed_steps.add(step.action)
                context.completed_steps.append(step.action)
                steps.remove(step)
        
        return context.agent_data
    
    async def _execute_step(self, step: WorkflowStep, context: WorkflowContext) -> Any:
        """
        Execute a single workflow step
        
        Args:
            step: The workflow step to execute
            context: Workflow context
            
        Returns:
            Step result
        """
        if step.agent_name not in self.agents:
            raise ValueError(f"Agent {step.agent_name} not registered")
        
        agent = self.agents[step.agent_name]
        
        # Create message for the agent
        message = AgentMessage(
            from_agent="orchestrator",
            to_agent=step.agent_name,
            workflow_id=context.workflow_id,
            action=step.action,
            data=step.data,
            context={"user_query": context.user_query}
        )
        
        # Execute the step
        context.current_step = step.action
        result = await agent.handle_message(message, context)
        
        step.completed = True
        step.result = result
        
        return result
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow"""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}
        
        context = self.workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "status": "completed" if len(context.completed_steps) > 0 else "running",
            "current_step": context.current_step,
            "completed_steps": context.completed_steps,
            "pending_steps": context.pending_steps,
            "agent_data": context.agent_data,
            "created_at": context.created_at,
            "updated_at": context.updated_at
        }
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            logger.info(f"Cancelled workflow {workflow_id}")
            return True
        return False
    
    def get_agent_status(self, agent_name: str = None) -> Dict[str, Any]:
        """Get status of specific agent or all agents"""
        if agent_name:
            if agent_name in self.agents:
                return self.agents[agent_name].get_status()
            return {"error": "Agent not found"}
        
        return {agent_name: agent.get_status() for agent_name, agent in self.agents.items()}
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get orchestrator performance statistics"""
        return {
            "total_workflows": self.total_workflows,
            "completed_workflows": self.completed_workflows,
            "failed_workflows": self.failed_workflows,
            "success_rate": self.completed_workflows / max(1, self.total_workflows),
            "active_workflows": len(self.workflows),
            "registered_agents": len(self.agents),
            "available_workflows": list(self.workflow_definitions.keys())
        }