"""
Dynamic Workflow Orchestrator
Replaces hard-coded workflows with dynamic strategy-driven orchestration
"""
import asyncio
from typing import Dict, List, Any, Optional
from loguru import logger

from .agents.agent_orchestrator import AgentOrchestrator
from .agents.base_agent import WorkflowContext, AgentMessage
from .strategy_engine import StrategyEngine, StrategyContext


class DynamicOrchestrator(AgentOrchestrator):
    """
    Enhanced orchestrator that can execute dynamic strategies instead of 
    pre-defined workflows
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize strategy engine
        self.strategy_engine = StrategyEngine()
        
        # Override rigid workflows with dynamic strategy evaluation
        self.enable_dynamic_strategies = True
        
        # Override workflow definitions with simplified agent structure
        self._override_workflows_for_simplified_agents()
        
        logger.info("Dynamic Orchestrator initialized with strategy engine and simplified workflows")
    
    def _override_workflows_for_simplified_agents(self):
        """Override workflow definitions to use simplified agent structure"""
        from .agents.agent_orchestrator import WorkflowStep
        
        # Place Order Workflow - using unified business agent
        self.workflow_definitions["place_order"] = [
            WorkflowStep("unified_business_agent", "search_product", parallel=False),
            WorkflowStep("unified_business_agent", "authenticate_customer", parallel=True),
            WorkflowStep("unified_business_agent", "check_inventory", depends_on=["search_product"]),
            WorkflowStep("unified_business_agent", "get_address", depends_on=["authenticate_customer"]),
            WorkflowStep("unified_business_agent", "calculate_delivery", 
                        depends_on=["check_inventory", "get_address"]),
            WorkflowStep("rules_agent", "validate_order", 
                        depends_on=["check_inventory", "get_address"]),
            WorkflowStep("unified_business_agent", "create_order", 
                        depends_on=["validate_order", "calculate_delivery"]),
            WorkflowStep("unified_business_agent", "send_confirmation", 
                        depends_on=["create_order"])
        ]
        
        # Product Inquiry Workflow - simplified
        self.workflow_definitions["product_inquiry"] = [
            WorkflowStep("unified_business_agent", "search_product"),
            WorkflowStep("unified_business_agent", "check_availability", 
                        depends_on=["search_product"]),
            WorkflowStep("unified_business_agent", "calculate_delivery", parallel=True)
        ]
    
    async def classify_user_intent(self, user_query: str) -> tuple[str, Dict[str, Any]]:
        """
        Enhanced intent classification that detects when dynamic strategies should be used
        """
        query_lower = user_query.lower()
        
        # Check for address change requests that need dynamic strategy evaluation
        if any(word in query_lower for word in ["change address", "update address", "delivery address", "different address"]):
            return "dynamic_address_change", {
                "user_query": user_query,
                "strategy_required": True
            }
        
        # Fall back to parent classification for other intents
        return await super().classify_user_intent(user_query)
    
    async def execute_dynamic_workflow(self, workflow_name: str, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute dynamic workflow based on business strategies instead of hard-coded steps
        """
        try:
            if workflow_name == "dynamic_address_change":
                return await self._execute_dynamic_address_change(context)
            else:
                # Fall back to standard workflow execution
                return await self._execute_workflow(workflow_name, context)
                
        except Exception as e:
            logger.error(f"Dynamic workflow execution failed: {e}")
            raise
    
    async def _execute_dynamic_address_change(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute dynamic address change using strategy engine with simplified agent structure
        """
        try:
            logger.info("Executing dynamic address change workflow with unified business agent")
            
            # Step 1: Authenticate customer using unified business agent
            await self._execute_step_by_name("unified_business_agent", "authenticate_customer", {}, context)
            
            # Step 2: Get current order information (if applicable)
            order_context = await self._extract_order_context(context)
            
            # Step 3: Get and complete address using unified business agent
            await self._execute_step_by_name("unified_business_agent", "get_address", {}, context)
            
            # Step 4: Let Rules Agent evaluate strategies dynamically
            strategy_data = {
                "order_data": order_context,
                "requested_changes": self._extract_requested_changes(context),
                "current_situation": self._analyze_current_situation(order_context, context)
            }
            
            strategy_result = await self._execute_step_by_name(
                "rules_agent", 
                "evaluate_address_change_strategy", 
                strategy_data, 
                context
            )
            
            if not strategy_result.get("success"):
                return {"error": "Could not determine appropriate strategy", "strategy_result": strategy_result}
            
            # Step 5: Execute the strategy's action plan using simplified agents
            execution_plan = strategy_result.get("execution_plan", {})
            agent_instructions = execution_plan.get("agent_instructions", [])
            
            # Map old agent names to new unified structure
            for instruction in agent_instructions:
                await self._execute_simplified_strategy_instruction(instruction, context)
            
            # Step 6: Provide final response based on strategy outcome
            final_result = {
                "strategy_executed": strategy_result.get("strategy_selected"),
                "strategy_description": strategy_result.get("strategy_description"),
                "business_rationale": strategy_result.get("business_rationale"),
                "completed_actions": len(agent_instructions),
                "workflow_complete": True
            }
            
            return final_result
            
        except Exception as e:
            logger.error(f"Dynamic address change execution failed: {e}")
            return {"error": str(e), "workflow_complete": False}
    
    async def _execute_step_by_name(self, agent_name: str, action: str, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Execute a single agent step by name"""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not registered")
        
        agent = self.agents[agent_name]
        
        message = AgentMessage(
            from_agent="dynamic_orchestrator",
            to_agent=agent_name,
            workflow_id=context.workflow_id,
            action=action,
            data=data,
            context={"user_query": context.user_query}
        )
        
        result = await agent.handle_message(message, context)
        return result
    
    async def _execute_strategy_instruction(self, instruction: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Execute a single strategy instruction (legacy method)"""
        return await self._execute_simplified_strategy_instruction(instruction, context)
    
    async def _execute_simplified_strategy_instruction(self, instruction: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Execute strategy instruction with simplified agent mapping"""
        try:
            original_agent = instruction.get("agent")
            action = instruction.get("action")
            parameters = instruction.get("parameters", {})
            description = instruction.get("description", "")
            
            # Map old agent names to simplified structure
            agent_mapping = {
                "customer_agent": "unified_business_agent",
                "product_agent": "unified_business_agent", 
                "order_agent": "unified_business_agent",
                "shipping_agent": "unified_business_agent",
                "payment_agent": "unified_business_agent",  # For gift card operations
                "rules_agent": "rules_agent"  # Keep separate
            }
            
            mapped_agent = agent_mapping.get(original_agent, original_agent)
            
            # Handle special cases for payment operations that unified agent doesn't have
            if original_agent == "payment_agent":
                if action == "issue_gift_card":
                    # Simulate gift card issuance as business operation
                    action = "create_gift_card"
                    mapped_agent = "unified_business_agent"
            
            logger.info(f"Executing strategy step: {description} (mapped {original_agent} -> {mapped_agent})")
            
            result = await self._execute_step_by_name(mapped_agent, action, parameters, context)
            
            # Store result in context using original agent name for compatibility
            if original_agent not in context.agent_data:
                context.agent_data[original_agent] = {}
            
            context.agent_data[original_agent][f"step_{instruction.get('step', 0)}"] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Simplified strategy instruction execution failed: {e}")
            return {"error": str(e), "instruction": instruction}
    
    def _extract_order_context(self, context: WorkflowContext) -> Dict[str, Any]:
        """Extract order information from context"""
        # This would typically query for existing orders
        # For demo, we'll simulate based on user query
        user_query = context.user_query.lower()
        
        if "order" in user_query:
            # Simulate finding an order
            return {
                "order_id": "ORD-12345",
                "status": "CONFIRMED",
                "total_amount": 999.99,
                "items": [{"product": "iPhone 15 Pro", "quantity": 1, "price": 999.99}],
                "created_hours_ago": 2  # Recent order
            }
        
        return {}
    
    def _extract_requested_changes(self, context: WorkflowContext) -> Dict[str, Any]:
        """Extract what changes the user is requesting"""
        # Extract from user query or context
        delivery_address = context.metadata.get("delivery_address")
        
        changes = {}
        if delivery_address:
            changes["new_address"] = delivery_address
        
        return changes
    
    def _analyze_current_situation(self, order_context: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Analyze current situation to help strategy selection"""
        situation = {}
        
        if order_context:
            situation["has_existing_order"] = True
            situation["order_status"] = order_context.get("status", "UNKNOWN")
            situation["order_age_hours"] = order_context.get("created_hours_ago", 0)
        else:
            situation["has_existing_order"] = False
        
        # Add other contextual information
        situation["user_query"] = context.user_query
        
        return situation
    
    async def start_workflow(self, workflow_name: str, user_query: str, context_data: Dict[str, Any] = None) -> str:
        """
        Override parent method to handle dynamic workflows
        """
        if workflow_name.startswith("dynamic_") and self.enable_dynamic_strategies:
            # Use dynamic execution
            workflow_id = self._generate_workflow_id()
            context = WorkflowContext(
                workflow_id=workflow_id,
                user_query=user_query,
                metadata=context_data or {}
            )
            
            self.workflows[workflow_id] = context
            self.total_workflows += 1
            
            try:
                result = await self.execute_dynamic_workflow(workflow_name, context)
                self.completed_workflows += 1
                logger.info(f"Completed dynamic workflow {workflow_id}")
                return workflow_id
                
            except Exception as e:
                self.failed_workflows += 1
                logger.error(f"Dynamic workflow {workflow_id} failed: {e}")
                raise
        else:
            # Use parent's standard workflow execution
            return await super().start_workflow(workflow_name, user_query, context_data)
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        import uuid
        return str(uuid.uuid4())