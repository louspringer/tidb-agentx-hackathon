"""Tests for TiDB AgentX Hackathon core functionality"""

import asyncio

import pytest
from tidb_agentx_hackathon.core import (
    AgentConfig,
    TiDBAgentOrchestrator,
    WorkflowConfig,
)


class TestTiDBAgentOrchestrator:
    """Test the main TiDB agent orchestrator"""

    @pytest.fixture
    async def orchestrator(self):
        """Create a fresh orchestrator for each test"""
        return TiDBAgentOrchestrator()

    @pytest.fixture
    def sample_agent(self):
        """Sample agent configuration"""
        return AgentConfig(
            agent_id="test-agent-1",
            agent_type="testing",
            capabilities=["unit_testing", "integration_testing"],
            status="idle",
        )

    @pytest.fixture
    def sample_workflow(self):
        """Sample workflow configuration"""
        return WorkflowConfig(
            workflow_id="test-workflow-1",
            name="Test Workflow",
            agents=["test-agent-1"],
            steps=[
                {"type": "capability_test", "agent": "test-agent-1"},
                {"type": "performance_test", "agent": "test-agent-1"},
            ],
        )

    @pytest.mark.asyncio
    async def test_register_agent(self, orchestrator, sample_agent):
        """Test agent registration"""
        result = await orchestrator.register_agent(sample_agent)
        assert result is True
        assert sample_agent.agent_id in orchestrator.agents

    @pytest.mark.asyncio
    async def test_create_workflow(self, orchestrator, sample_agent, sample_workflow):
        """Test workflow creation"""
        # First register an agent
        await orchestrator.register_agent(sample_agent)

        # Then create workflow
        result = await orchestrator.create_workflow(sample_workflow)
        assert result is True
        assert sample_workflow.workflow_id in orchestrator.workflows

    @pytest.mark.asyncio
    async def test_execute_workflow(self, orchestrator, sample_agent, sample_workflow):
        """Test workflow execution"""
        # Setup
        await orchestrator.register_agent(sample_agent)
        await orchestrator.create_workflow(sample_workflow)

        # Execute workflow
        result = await orchestrator.execute_workflow(sample_workflow.workflow_id)
        assert result is True

        # Check if workflow is active
        assert orchestrator.is_workflow_active(sample_workflow.workflow_id)

        # Wait for completion
        await asyncio.sleep(0.2)

        # Check if workflow completed
        assert not orchestrator.is_workflow_active(sample_workflow.workflow_id)

    def test_list_agents(self, orchestrator, sample_agent):
        """Test listing agents"""
        # Initially no agents
        assert len(orchestrator.list_agents()) == 0

        # Add agent (sync operation)
        orchestrator.agents[sample_agent.agent_id] = sample_agent

        # Check listing
        agents = orchestrator.list_agents()
        assert len(agents) == 1
        assert agents[0].agent_id == sample_agent.agent_id

    def test_list_workflows(self, orchestrator, sample_workflow):
        """Test listing workflows"""
        # Initially no workflows
        assert len(orchestrator.list_workflows()) == 0

        # Add workflow (sync operation)
        orchestrator.workflows[sample_workflow.workflow_id] = sample_workflow

        # Check listing
        workflows = orchestrator.list_workflows()
        assert len(workflows) == 1
        assert workflows[0].workflow_id == sample_workflow.workflow_id


class TestAgentConfig:
    """Test agent configuration model"""

    def test_agent_config_creation(self):
        """Test creating agent configuration"""
        agent = AgentConfig(
            agent_id="test-agent",
            agent_type="testing",
            capabilities=["unit_testing"],
            status="idle",
        )

        assert agent.agent_id == "test-agent"
        assert agent.agent_type == "testing"
        assert "unit_testing" in agent.capabilities
        assert agent.status == "idle"

    def test_agent_config_defaults(self):
        """Test agent configuration defaults"""
        agent = AgentConfig(agent_id="test-agent", agent_type="testing")

        assert agent.capabilities == []
        assert agent.status == "idle"


class TestWorkflowConfig:
    """Test workflow configuration model"""

    def test_workflow_config_creation(self):
        """Test creating workflow configuration"""
        workflow = WorkflowConfig(
            workflow_id="test-workflow",
            name="Test Workflow",
            agents=["agent-1", "agent-2"],
            steps=[
                {"type": "step1", "agent": "agent-1"},
                {"type": "step2", "agent": "agent-2"},
            ],
        )

        assert workflow.workflow_id == "test-workflow"
        assert workflow.name == "Test Workflow"
        assert len(workflow.agents) == 2
        assert len(workflow.steps) == 2
        assert workflow.status == "pending"
