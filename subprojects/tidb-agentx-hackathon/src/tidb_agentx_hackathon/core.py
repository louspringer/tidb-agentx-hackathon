"""
Core TiDB Agent Orchestrator

Main orchestration service for AI agents in TiDB AgentX hackathon
"""

import asyncio
import logging
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Configuration for individual AI agents"""

    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(..., description="Type of agent (testing, analysis, etc.)")
    capabilities: list[str] = Field(
        default_factory=list, description="Agent capabilities"
    )
    status: str = Field(default="idle", description="Current agent status")


class WorkflowConfig(BaseModel):
    """Configuration for AI agent workflows"""

    workflow_id: str = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Workflow name")
    agents: list[str] = Field(..., description="List of agent IDs in workflow")
    steps: list[dict[str, Any]] = Field(..., description="Workflow execution steps")


class TiDBAgentOrchestrator:
    """Main orchestrator for TiDB AI agents"""

    def __init__(self):
        self.agents: dict[str, AgentConfig] = {}
        self.workflows: dict[str, WorkflowConfig] = {}
        self.active_workflows: dict[str, asyncio.Task] = {}

    async def register_agent(self, agent_config: AgentConfig) -> bool:
        """Register a new AI agent"""
        try:
            self.agents[agent_config.agent_id] = agent_config
            logger.info(f"Registered agent: {agent_config.agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {agent_config.agent_id}: {e}")
            return False

    async def create_workflow(self, workflow_config: WorkflowConfig) -> bool:
        """Create a new AI agent workflow"""
        try:
            # Validate that all agents exist
            for agent_id in workflow_config.agents:
                if agent_id not in self.agents:
                    raise ValueError(f"Agent {agent_id} not found")

            self.workflows[workflow_config.workflow_id] = workflow_config
            logger.info(f"Created workflow: {workflow_config.workflow_id}")
            return True
        except Exception as e:
            logger.error(
                f"Failed to create workflow {workflow_config.workflow_id}: {e}"
            )
            return False

    async def execute_workflow(self, workflow_id: str) -> bool:
        """Execute an AI agent workflow"""
        if workflow_id not in self.workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return False

        if workflow_id in self.active_workflows:
            logger.warning(f"Workflow {workflow_id} already running")
            return False

        try:
            workflow = self.workflows[workflow_id]
            task = asyncio.create_task(self._run_workflow(workflow))
            self.active_workflows[workflow_id] = task
            logger.info(f"Started workflow: {workflow_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start workflow {workflow_id}: {e}")
            return False

    async def _run_workflow(self, workflow: WorkflowConfig):
        """Internal method to run a workflow"""
        try:
            logger.info(f"Running workflow: {workflow.workflow_id}")

            # Execute workflow steps
            for step in workflow.steps:
                await self._execute_step(step)

            logger.info(f"Completed workflow: {workflow.workflow_id}")
        except Exception as e:
            logger.error(f"Workflow {workflow.workflow_id} failed: {e}")
        finally:
            # Clean up active workflow
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]

    async def _execute_step(self, step: dict[str, Any]):
        """Execute a single workflow step"""
        step_type = step.get("type", "unknown")
        logger.info(f"Executing step: {step_type}")

        # Simulate step execution
        await asyncio.sleep(0.1)

        logger.info(f"Completed step: {step_type}")

    def get_agent_status(self, agent_id: str) -> Optional[AgentConfig]:
        """Get status of a specific agent"""
        return self.agents.get(agent_id)

    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowConfig]:
        """Get status of a specific workflow"""
        return self.workflows.get(workflow_id)

    def list_agents(self) -> list[AgentConfig]:
        """List all registered agents"""
        return list(self.agents.values())

    def list_workflows(self) -> list[WorkflowConfig]:
        """List all available workflows"""
        return list(self.workflows.values())

    def is_workflow_active(self, workflow_id: str) -> bool:
        """Check if a workflow is currently running"""
        return workflow_id in self.active_workflows
