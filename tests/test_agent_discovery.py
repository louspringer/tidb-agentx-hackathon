"""
Unit tests for the agent discovery and registry system.

Tests cover agent registration, capability matching, trust scoring,
availability monitoring, and registry operations.
"""

import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
import threading
import time
import concurrent.futures

from src.beast_mode_network.agent_discovery import (
    DiscoveredAgent, AgentRegistry, AgentStatus, AgentDiscoveryManager
)
from src.beast_mode_network.message_models import AgentCapabilities, MessageType


class TestDiscoveredAgent:
    """Test cases for DiscoveredAgent dataclass."""
    
    def test_agent_creation_with_defaults(self):
        """Test creating an agent with minimal required fields."""
        agent = DiscoveredAgent(agent_id="test_agent")
        
        assert agent.agent_id == "test_agent"
        assert agent.capabilities == []
        assert agent.specializations == []
        assert agent.availability == AgentStatus.UNKNOWN
        assert agent.trust_score == 0.5
        assert agent.response_count == 0
        assert agent.success_count == 0
        assert agent.total_interactions == 0
        assert agent.successful_interactions == 0
        assert agent.failed_interactions == 0
        assert agent.average_response_time == 0.0
    
    def test_agent_creation_with_full_data(self):
        """Test creating an agent with all fields populated."""
        capabilities = ["python", "data_analysis"]
        specializations = ["machine_learning", "nlp"]
        
        agent = DiscoveredAgent(
            agent_id="full_agent",
            capabilities=capabilities,
            specializations=specializations,
            availability=AgentStatus.ONLINE,
            trust_score=0.8,
            response_count=10,
            success_count=8,
            description="Test agent",
            version="2.0.0"
        )
        
        assert agent.agent_id == "full_agent"
        assert agent.capabilities == capabilities
        assert agent.specializations == specializations
        assert agent.availability == AgentStatus.ONLINE
        assert agent.trust_score == 0.8
        assert agent.response_count == 10
        assert agent.success_count == 8
        assert agent.description == "Test agent"
        assert agent.version == "2.0.0"
    
    def test_agent_validation_empty_id(self):
        """Test that empty agent_id raises ValueError."""
        with pytest.raises(ValueError, match="agent_id cannot be empty"):
            DiscoveredAgent(agent_id="")
    
    def test_capability_normalization(self):
        """Test that capabilities are normalized to lowercase."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=["Python", "  DATA_ANALYSIS  ", ""],
            specializations=["Machine_Learning", "  NLP  ", ""]
        )
        
        assert agent.capabilities == ["python", "data_analysis"]
        assert agent.specializations == ["machine_learning", "nlp"]
    
    def test_trust_score_bounds(self):
        """Test that trust score is bounded between 0.0 and 1.0."""
        agent1 = DiscoveredAgent(agent_id="agent1", trust_score=-0.5)
        assert agent1.trust_score == 0.0
        
        agent2 = DiscoveredAgent(agent_id="agent2", trust_score=1.5)
        assert agent2.trust_score == 1.0
    
    def test_count_validation(self):
        """Test that counts are validated and corrected."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            response_count=-5,
            success_count=15,  # More than response_count
            total_interactions=-3,
            successful_interactions=20,  # More than total_interactions
            failed_interactions=-2
        )
        
        assert agent.response_count == 0
        assert agent.success_count == 0  # Capped by response_count
        assert agent.total_interactions == 0
        assert agent.successful_interactions == 0  # Capped by total_interactions
        assert agent.failed_interactions == 0
    
    def test_is_available_online(self):
        """Test availability check for online agent."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            availability=AgentStatus.ONLINE,
            last_seen=datetime.now()
        )
        
        assert agent.is_available(timeout_minutes=5) is True
    
    def test_is_available_offline(self):
        """Test availability check for offline agent."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            availability=AgentStatus.OFFLINE,
            last_seen=datetime.now()
        )
        
        assert agent.is_available(timeout_minutes=5) is False
    
    def test_is_available_timeout(self):
        """Test availability check with timeout."""
        old_time = datetime.now() - timedelta(minutes=10)
        agent = DiscoveredAgent(
            agent_id="test_agent",
            availability=AgentStatus.ONLINE,
            last_seen=old_time
        )
        
        assert agent.is_available(timeout_minutes=5) is False
        assert agent.is_available(timeout_minutes=15) is True
    
    def test_has_capability(self):
        """Test capability checking."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=["python", "data_analysis"]
        )
        
        assert agent.has_capability("python") is True
        assert agent.has_capability("Python") is True  # Case insensitive
        assert agent.has_capability("  PYTHON  ") is True  # Whitespace handling
        assert agent.has_capability("javascript") is False
    
    def test_has_capabilities_all_match(self):
        """Test checking multiple capabilities - all match."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=["python", "data_analysis", "machine_learning"]
        )
        
        assert agent.has_capabilities(["python", "data_analysis"]) is True
        assert agent.has_capabilities(["Python", "DATA_ANALYSIS"]) is True  # Case insensitive
    
    def test_has_capabilities_partial_match(self):
        """Test checking multiple capabilities - partial match."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=["python", "data_analysis"]
        )
        
        assert agent.has_capabilities(["python", "javascript"]) is False
    
    def test_has_capabilities_empty_list(self):
        """Test checking empty capabilities list."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=["python"]
        )
        
        assert agent.has_capabilities([]) is True
    
    def test_calculate_capability_match_score_perfect(self):
        """Test capability match score calculation - perfect match."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=["python", "data_analysis", "machine_learning"]
        )
        
        score = agent.calculate_capability_match_score(["python", "data_analysis"])
        assert score > 1.0  # Should have bonus for extra capability (machine_learning)
        assert score <= 1.2  # But capped at 20% bonus
    
    def test_calculate_capability_match_score_partial(self):
        """Test capability match score calculation - partial match."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=["python", "data_analysis"]
        )
        
        score = agent.calculate_capability_match_score(["python", "javascript", "data_analysis"])
        assert score == pytest.approx(2/3, rel=1e-2)  # 2 out of 3 capabilities match
    
    def test_calculate_capability_match_score_with_bonus(self):
        """Test capability match score with bonus for extra capabilities."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=["python", "data_analysis", "machine_learning", "nlp", "web_scraping"]
        )
        
        score = agent.calculate_capability_match_score(["python", "data_analysis"])
        assert score > 1.0  # Should have bonus for extra capabilities
        assert score <= 1.2  # But capped at 20% bonus
    
    def test_calculate_capability_match_score_empty_required(self):
        """Test capability match score with empty required capabilities."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=["python"]
        )
        
        score = agent.calculate_capability_match_score([])
        assert score == 1.0
    
    def test_update_trust_score_success(self):
        """Test trust score update on successful interaction."""
        agent = DiscoveredAgent(agent_id="test_agent", trust_score=0.5)
        
        agent.update_trust_score(success=True, response_time=3.0)
        
        assert agent.total_interactions == 1
        assert agent.successful_interactions == 1
        assert agent.failed_interactions == 0
        assert agent.success_count == 1
        assert agent.response_count == 1
        assert agent.average_response_time == 3.0
        assert agent.trust_score > 0.5  # Should increase
        assert agent.last_interaction is not None
    
    def test_update_trust_score_failure(self):
        """Test trust score update on failed interaction."""
        agent = DiscoveredAgent(agent_id="test_agent", trust_score=0.8)
        
        agent.update_trust_score(success=False, response_time=10.0)
        
        assert agent.total_interactions == 1
        assert agent.successful_interactions == 0
        assert agent.failed_interactions == 1
        assert agent.success_count == 0
        assert agent.response_count == 1
        assert agent.average_response_time == 10.0
        assert agent.trust_score < 0.8  # Should decrease
    
    def test_update_trust_score_multiple_interactions(self):
        """Test trust score updates over multiple interactions."""
        agent = DiscoveredAgent(agent_id="test_agent")
        
        # Multiple successful interactions
        for _ in range(8):
            agent.update_trust_score(success=True, response_time=2.0)
        
        # Two failed interactions
        for _ in range(2):
            agent.update_trust_score(success=False, response_time=15.0)
        
        assert agent.total_interactions == 10
        assert agent.successful_interactions == 8
        assert agent.failed_interactions == 2
        assert agent.trust_score > 0.5  # Should be high due to 80% success rate
    
    def test_apply_time_decay(self):
        """Test time decay application to trust score."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            trust_score=0.9,
            last_interaction=datetime.now() - timedelta(days=5)
        )
        
        original_score = agent.trust_score
        agent.apply_time_decay()
        
        assert agent.trust_score < original_score
        assert agent.trust_score >= 0.0
    
    def test_apply_time_decay_no_interaction(self):
        """Test time decay with no previous interactions."""
        agent = DiscoveredAgent(agent_id="test_agent", trust_score=0.8)
        
        original_score = agent.trust_score
        agent.apply_time_decay()
        
        assert agent.trust_score == original_score  # No change without interactions
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=["python"],
            trust_score=0.7,
            response_count=5
        )
        
        agent_dict = agent.to_dict()
        
        assert isinstance(agent_dict, dict)
        assert agent_dict["agent_id"] == "test_agent"
        assert agent_dict["capabilities"] == ["python"]
        assert agent_dict["trust_score"] == 0.7
        assert agent_dict["response_count"] == 5
        assert "last_seen" in agent_dict
        assert "availability" in agent_dict

    def test_trust_score_calculation_edge_cases(self):
        """Test trust score calculations with edge cases."""
        agent = DiscoveredAgent(agent_id="test_agent")
        
        # Test with zero interactions
        assert agent.trust_score == 0.5  # Default
        
        # Test with single success
        agent.update_trust_score(success=True, response_time=1.0)
        assert agent.trust_score > 0.5
        
        # Test with single failure
        agent2 = DiscoveredAgent(agent_id="test_agent2")
        agent2.update_trust_score(success=False, response_time=10.0)
        assert agent2.trust_score < 0.5
        
        # Test bounds enforcement
        agent3 = DiscoveredAgent(agent_id="test_agent3", trust_score=2.0)
        assert agent3.trust_score == 1.0  # Capped at 1.0
        
        agent4 = DiscoveredAgent(agent_id="test_agent4", trust_score=-1.0)
        assert agent4.trust_score == 0.0  # Floored at 0.0

    def test_trust_score_time_decay_calculation(self):
        """Test detailed trust score time decay calculations."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            trust_score=0.9,
            trust_decay_factor=0.9
        )
        
        # Set last interaction to 1 day ago
        agent.last_interaction = datetime.now() - timedelta(days=1)
        
        original_score = agent.trust_score
        agent.apply_time_decay()
        
        # Should decay by factor^1 = 0.9
        expected_score = original_score * 0.9
        assert abs(agent.trust_score - expected_score) < 0.001
        
        # Test multiple days decay
        agent.last_interaction = datetime.now() - timedelta(days=3)
        agent.trust_score = 0.9  # Reset
        agent.apply_time_decay()
        
        # Should decay by factor^3 = 0.9^3 = 0.729
        expected_score = 0.9 * (0.9 ** 3)
        assert abs(agent.trust_score - expected_score) < 0.001

    def test_response_time_factor_calculation(self):
        """Test response time factor in trust score calculation."""
        agent = DiscoveredAgent(agent_id="test_agent")
        
        # Test optimal response time (around 5 seconds)
        agent.update_trust_score(success=True, response_time=5.0)
        optimal_score = agent.trust_score
        
        # Test faster response time (should get bonus)
        agent2 = DiscoveredAgent(agent_id="test_agent2")
        agent2.update_trust_score(success=True, response_time=2.0)
        fast_score = agent2.trust_score
        
        # Test slower response time (should get penalty)
        agent3 = DiscoveredAgent(agent_id="test_agent3")
        agent3.update_trust_score(success=True, response_time=15.0)
        slow_score = agent3.trust_score
        
        # Fast should be >= optimal >= slow
        assert fast_score >= optimal_score >= slow_score

    def test_capability_match_scoring_algorithms(self):
        """Test detailed capability matching algorithms."""
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=["python", "data_analysis", "machine_learning", "nlp"]
        )
        
        # Test exact match
        score = agent.calculate_capability_match_score(["python", "data_analysis"])
        assert score > 1.0  # Should have bonus for extra capabilities
        
        # Test partial match
        score = agent.calculate_capability_match_score(["python", "javascript", "data_analysis"])
        assert 0.6 < score < 0.8  # 2/3 match
        
        # Test no match
        score = agent.calculate_capability_match_score(["javascript", "php"])
        assert score == 0.0
        
        # Test superset (agent has more than required)
        score = agent.calculate_capability_match_score(["python"])
        assert score > 1.0  # Should get bonus
        
        # Test bonus cap (max 20% bonus)
        agent_many_caps = DiscoveredAgent(
            agent_id="many_caps_agent",
            capabilities=["python"] + [f"skill_{i}" for i in range(20)]
        )
        score = agent_many_caps.calculate_capability_match_score(["python"])
        assert score <= 1.2  # Capped at 20% bonus

    def test_availability_timeout_edge_cases(self):
        """Test availability checking with various timeout scenarios."""
        # Test exactly at timeout boundary
        agent = DiscoveredAgent(
            agent_id="test_agent",
            availability=AgentStatus.ONLINE,
            last_seen=datetime.now() - timedelta(minutes=5, seconds=0)
        )
        assert agent.is_available(timeout_minutes=5) is False
        
        # Test just before timeout
        agent.last_seen = datetime.now() - timedelta(minutes=4, seconds=59)
        assert agent.is_available(timeout_minutes=5) is True
        
        # Test with zero timeout
        agent.last_seen = datetime.now() - timedelta(seconds=1)
        assert agent.is_available(timeout_minutes=0) is False
        
        # Test with very large timeout
        agent.last_seen = datetime.now() - timedelta(days=1)
        assert agent.is_available(timeout_minutes=2000) is True


class TestAgentRegistry:
    """Test cases for AgentRegistry class."""
    
    @pytest_asyncio.fixture
    async def registry(self):
        """Create a test registry."""
        registry = AgentRegistry(availability_timeout_minutes=5)
        await registry.start_monitoring()
        yield registry
        await registry.stop_monitoring()
    
    @pytest.fixture
    def sample_capabilities(self):
        """Create sample agent capabilities."""
        return AgentCapabilities(
            agent_id="test_agent",
            capabilities=["python", "data_analysis"],
            specializations=["machine_learning"],
            description="Test agent for unit tests",
            version="1.0.0"
        )
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_registry_initialization(self):
        """Test registry initialization."""
        registry = AgentRegistry(availability_timeout_minutes=10)
        
        assert registry.availability_timeout_minutes == 10
        assert len(registry._agents) == 0
        assert len(registry._capability_index) == 0
        assert len(registry._specialization_index) == 0
        assert registry._cleanup_task is None
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring."""
        registry = AgentRegistry()
        
        await registry.start_monitoring()
        assert registry._cleanup_task is not None
        assert not registry._cleanup_task.done()
        
        await registry.stop_monitoring()
        assert registry._is_shutting_down is True
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_register_new_agent(self, registry, sample_capabilities):
        """Test registering a new agent."""
        result = await registry.register_agent(sample_capabilities)
        
        assert result is True
        
        agent = await registry.get_agent("test_agent")
        assert agent is not None
        assert agent.agent_id == "test_agent"
        assert agent.capabilities == ["python", "data_analysis"]
        assert agent.specializations == ["machine_learning"]
        assert agent.availability == AgentStatus.ONLINE
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_register_existing_agent_update(self, registry, sample_capabilities):
        """Test updating an existing agent registration."""
        # Register initial agent
        await registry.register_agent(sample_capabilities)
        
        # Update with new capabilities
        updated_capabilities = AgentCapabilities(
            agent_id="test_agent",
            capabilities=["python", "web_development"],
            specializations=["backend"],
            description="Updated test agent",
            version="2.0.0"
        )
        
        result = await registry.register_agent(updated_capabilities)
        assert result is True
        
        agent = await registry.get_agent("test_agent")
        assert agent.capabilities == ["python", "web_development"]
        assert agent.specializations == ["backend"]
        assert agent.description == "Updated test agent"
        assert agent.version == "2.0.0"
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_unregister_agent(self, registry, sample_capabilities):
        """Test unregistering an agent."""
        # Register agent first
        await registry.register_agent(sample_capabilities)
        
        # Verify agent exists
        agent = await registry.get_agent("test_agent")
        assert agent is not None
        
        # Unregister agent
        result = await registry.unregister_agent("test_agent")
        assert result is True
        
        # Verify agent is gone
        agent = await registry.get_agent("test_agent")
        assert agent is None
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_unregister_nonexistent_agent(self, registry):
        """Test unregistering a non-existent agent."""
        result = await registry.unregister_agent("nonexistent_agent")
        assert result is False
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_update_agent_availability(self, registry, sample_capabilities):
        """Test updating agent availability status."""
        await registry.register_agent(sample_capabilities)
        
        result = await registry.update_agent_availability("test_agent", AgentStatus.BUSY)
        assert result is True
        
        agent = await registry.get_agent("test_agent")
        assert agent.availability == AgentStatus.BUSY
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_update_availability_nonexistent_agent(self, registry):
        """Test updating availability for non-existent agent."""
        result = await registry.update_agent_availability("nonexistent", AgentStatus.BUSY)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_find_agents_by_capabilities_exact_match(self, registry):
        """Test finding agents by exact capability match."""
        # Register multiple agents with different capabilities
        agent1_caps = AgentCapabilities(
            agent_id="agent1",
            capabilities=["python", "data_analysis"]
        )
        agent2_caps = AgentCapabilities(
            agent_id="agent2",
            capabilities=["javascript", "web_development"]
        )
        agent3_caps = AgentCapabilities(
            agent_id="agent3",
            capabilities=["python", "machine_learning", "data_analysis"]
        )
        
        await registry.register_agent(agent1_caps)
        await registry.register_agent(agent2_caps)
        await registry.register_agent(agent3_caps)
        
        # Find agents with python capability
        agents = await registry.find_agents_by_capabilities(["python"])
        
        assert len(agents) == 2
        agent_ids = [agent.agent_id for agent in agents]
        assert "agent1" in agent_ids
        assert "agent3" in agent_ids
        assert "agent2" not in agent_ids
    
    @pytest.mark.asyncio
    async def test_find_agents_by_capabilities_multiple_requirements(self, registry):
        """Test finding agents with multiple required capabilities."""
        # Register agents
        agent1_caps = AgentCapabilities(
            agent_id="agent1",
            capabilities=["python", "data_analysis", "machine_learning"]
        )
        agent2_caps = AgentCapabilities(
            agent_id="agent2",
            capabilities=["python", "web_development"]
        )
        
        await registry.register_agent(agent1_caps)
        await registry.register_agent(agent2_caps)
        
        # Find agents with both python and data_analysis
        agents = await registry.find_agents_by_capabilities(["python", "data_analysis"])
        
        assert len(agents) == 1
        assert agents[0].agent_id == "agent1"
    
    @pytest.mark.asyncio
    async def test_find_agents_by_capabilities_empty_requirements(self, registry):
        """Test finding agents with empty requirements (should return all)."""
        agent_caps = AgentCapabilities(agent_id="test_agent", capabilities=["python"])
        await registry.register_agent(agent_caps)
        
        agents = await registry.find_agents_by_capabilities([])
        
        assert len(agents) == 1
        assert agents[0].agent_id == "test_agent"
    
    @pytest.mark.asyncio
    async def test_find_agents_by_capabilities_sorting(self, registry):
        """Test that agents are sorted by capability match and trust score."""
        # Register agents with different trust scores
        agent1_caps = AgentCapabilities(
            agent_id="agent1",
            capabilities=["python", "data_analysis"]
        )
        agent2_caps = AgentCapabilities(
            agent_id="agent2",
            capabilities=["python", "data_analysis", "machine_learning"]
        )
        
        await registry.register_agent(agent1_caps)
        await registry.register_agent(agent2_caps)
        
        # Update trust scores
        await registry.update_agent_trust("agent1", success=True)
        await registry.update_agent_trust("agent1", success=True)
        await registry.update_agent_trust("agent2", success=True)
        
        agents = await registry.find_agents_by_capabilities(["python"])
        
        # agent2 should be first due to better capability match (has extra ML capability)
        assert len(agents) == 2
        assert agents[0].agent_id == "agent2"
    
    @pytest.mark.asyncio
    async def test_get_available_agents(self, registry):
        """Test getting all available agents."""
        # Register agents with different availability
        agent1_caps = AgentCapabilities(agent_id="agent1", capabilities=["python"])
        agent2_caps = AgentCapabilities(agent_id="agent2", capabilities=["javascript"])
        
        await registry.register_agent(agent1_caps)
        await registry.register_agent(agent2_caps)
        
        # Set one agent offline
        await registry.update_agent_availability("agent2", AgentStatus.OFFLINE)
        
        # Get available agents (should exclude offline)
        agents = await registry.get_available_agents(include_offline=False)
        assert len(agents) == 1
        assert agents[0].agent_id == "agent1"
        
        # Get all agents (should include offline)
        all_agents = await registry.get_available_agents(include_offline=True)
        assert len(all_agents) == 2
    
    @pytest.mark.asyncio
    async def test_get_agent_existing(self, registry, sample_capabilities):
        """Test getting an existing agent."""
        await registry.register_agent(sample_capabilities)
        
        agent = await registry.get_agent("test_agent")
        
        assert agent is not None
        assert agent.agent_id == "test_agent"
    
    @pytest.mark.asyncio
    async def test_get_agent_nonexistent(self, registry):
        """Test getting a non-existent agent."""
        agent = await registry.get_agent("nonexistent_agent")
        assert agent is None
    
    @pytest.mark.asyncio
    async def test_update_agent_trust_success(self, registry, sample_capabilities):
        """Test updating agent trust score on success."""
        await registry.register_agent(sample_capabilities)
        
        result = await registry.update_agent_trust("test_agent", success=True, response_time=2.5)
        assert result is True
        
        agent = await registry.get_agent("test_agent")
        assert agent.total_interactions == 1
        assert agent.successful_interactions == 1
        assert agent.average_response_time == 2.5
    
    @pytest.mark.asyncio
    async def test_update_agent_trust_failure(self, registry, sample_capabilities):
        """Test updating agent trust score on failure."""
        await registry.register_agent(sample_capabilities)
        
        result = await registry.update_agent_trust("test_agent", success=False)
        assert result is True
        
        agent = await registry.get_agent("test_agent")
        assert agent.total_interactions == 1
        assert agent.successful_interactions == 0
        assert agent.failed_interactions == 1
    
    @pytest.mark.asyncio
    async def test_update_trust_nonexistent_agent(self, registry):
        """Test updating trust for non-existent agent."""
        result = await registry.update_agent_trust("nonexistent", success=True)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_registry_stats(self, registry):
        """Test getting registry statistics."""
        # Register some agents
        agent1_caps = AgentCapabilities(
            agent_id="agent1",
            capabilities=["python", "data_analysis"]
        )
        agent2_caps = AgentCapabilities(
            agent_id="agent2",
            capabilities=["javascript", "web_development"]
        )
        
        await registry.register_agent(agent1_caps)
        await registry.register_agent(agent2_caps)
        
        # Set one agent offline
        await registry.update_agent_availability("agent2", AgentStatus.OFFLINE)
        
        stats = await registry.get_registry_stats()
        
        assert stats["total_agents"] == 2
        assert stats["online_agents"] == 1
        assert stats["offline_agents"] == 1
        assert "average_trust_score" in stats
        assert "total_capabilities" in stats
        assert "capability_distribution" in stats
        assert stats["availability_timeout_minutes"] == 5
    
    @pytest.mark.asyncio
    async def test_get_registry_stats_empty(self, registry):
        """Test getting statistics from empty registry."""
        stats = await registry.get_registry_stats()
        
        assert stats["total_agents"] == 0
        assert stats["online_agents"] == 0
        assert stats["offline_agents"] == 0
        assert stats["average_trust_score"] == 0.0
        assert stats["total_capabilities"] == 0
        assert stats["capability_distribution"] == {}
    
    @pytest.mark.asyncio
    async def test_capability_indexing(self, registry):
        """Test that capability indexing works correctly."""
        # Register agents with overlapping capabilities
        agent1_caps = AgentCapabilities(
            agent_id="agent1",
            capabilities=["python", "data_analysis"]
        )
        agent2_caps = AgentCapabilities(
            agent_id="agent2", 
            capabilities=["python", "web_development"]
        )
        agent3_caps = AgentCapabilities(
            agent_id="agent3",
            capabilities=["javascript", "web_development"]
        )
        
        await registry.register_agent(agent1_caps)
        await registry.register_agent(agent2_caps)
        await registry.register_agent(agent3_caps)
        
        # Test python capability index
        python_agents = await registry.find_agents_by_capabilities(["python"])
        assert len(python_agents) == 2
        
        # Test web_development capability index
        web_agents = await registry.find_agents_by_capabilities(["web_development"])
        assert len(web_agents) == 2
        
        # Test unique capability
        data_agents = await registry.find_agents_by_capabilities(["data_analysis"])
        assert len(data_agents) == 1
        assert data_agents[0].agent_id == "agent1"
    
    @pytest.mark.asyncio
    async def test_cleanup_loop_offline_detection(self, registry):
        """Test that cleanup loop marks agents as offline."""
        # Use very short timeout for testing
        registry.availability_timeout_minutes = 0.01  # 0.6 seconds
        
        agent_caps = AgentCapabilities(agent_id="test_agent", capabilities=["python"])
        await registry.register_agent(agent_caps)
        
        # Agent should be online initially
        agent = await registry.get_agent("test_agent")
        assert agent.availability == AgentStatus.ONLINE
        
        # Wait for timeout + cleanup cycle
        await asyncio.sleep(0.1)
        
        # Manually trigger cleanup cycle
        await registry._cleanup_loop()
        
        # Agent should now be offline
        agent = await registry.get_agent("test_agent")
        assert agent.availability == AgentStatus.OFFLINE
    
    @pytest.mark.asyncio
    async def test_cleanup_loop_old_agent_removal(self, registry):
        """Test that cleanup loop removes very old offline agents."""
        agent_caps = AgentCapabilities(agent_id="old_agent", capabilities=["python"])
        await registry.register_agent(agent_caps)
        
        # Manually set agent as old and offline
        agent = await registry.get_agent("old_agent")
        agent.availability = AgentStatus.OFFLINE
        agent.last_seen = datetime.now() - timedelta(hours=25)  # Older than 24 hours
        
        # Trigger cleanup
        await registry._cleanup_loop()
        
        # Agent should be removed
        agent = await registry.get_agent("old_agent")
        assert agent is None
    
    @pytest.mark.asyncio
    async def test_time_decay_application(self, registry):
        """Test that time decay is applied to trust scores."""
        agent_caps = AgentCapabilities(agent_id="decay_agent", capabilities=["python"])
        await registry.register_agent(agent_caps)
        
        # Set high trust score and old interaction
        agent = await registry.get_agent("decay_agent")
        agent.trust_score = 0.9
        agent.last_interaction = datetime.now() - timedelta(days=2)
        
        original_score = agent.trust_score
        
        # Trigger cleanup (which applies time decay)
        await registry._cleanup_loop()
        
        # Trust score should have decayed
        agent = await registry.get_agent("decay_agent")
        assert agent.trust_score < original_score
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, registry):
        """Test concurrent agent registration and operations."""
        async def register_agent(agent_num):
            caps = AgentCapabilities(
                agent_id=f"concurrent_agent_{agent_num}",
                capabilities=[f"skill_{agent_num}", "common_skill"]
            )
            return await registry.register_agent(caps)
        
        # Register multiple agents concurrently
        tasks = [register_agent(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All registrations should succeed
        assert all(results)
        
        # All agents should be findable
        agents = await registry.find_agents_by_capabilities(["common_skill"])
        assert len(agents) == 10
    
    @pytest.mark.asyncio
    async def test_registry_context_manager(self, registry):
        """Test registry as async context manager."""
        # Registry fixture already handles this, but test explicit usage
        async with AgentRegistry() as test_registry:
            agent_caps = AgentCapabilities(agent_id="context_agent", capabilities=["test"])
            result = await test_registry.register_agent(agent_caps)
            assert result is True
        
        # Registry should be properly shut down after context exit
        assert test_registry._is_shutting_down is True


class TestAgentDiscoveryManager:
    """Test cases for AgentDiscoveryManager class."""
    
    @pytest.fixture
    def mock_redis_manager(self):
        """Create mock Redis manager."""
        mock_manager = AsyncMock()
        mock_manager.subscribe_to_channel = AsyncMock(return_value=True)
        mock_manager.publish = AsyncMock(return_value=True)
        return mock_manager
    
    @pytest.fixture
    def sample_capabilities(self):
        """Create sample agent capabilities."""
        return AgentCapabilities(
            agent_id="discovery_agent",
            capabilities=["python", "discovery"],
            specializations=["testing"],
            description="Test discovery agent"
        )
    
    @pytest.fixture
    def discovery_manager(self, mock_redis_manager, sample_capabilities):
        """Create AgentDiscoveryManager instance."""
        return AgentDiscoveryManager(
            redis_manager=mock_redis_manager,
            agent_id="discovery_agent",
            capabilities=sample_capabilities,
            channel_name="test_channel"
        )
    
    def test_discovery_manager_initialization(self, discovery_manager, sample_capabilities):
        """Test discovery manager initialization."""
        assert discovery_manager.agent_id == "discovery_agent"
        assert discovery_manager.capabilities == sample_capabilities
        assert discovery_manager.channel_name == "test_channel"
        assert discovery_manager._is_running is False
        assert discovery_manager.announcement_interval == 30.0
        assert discovery_manager.discovery_scan_interval == 60.0
    
    @pytest.mark.asyncio
    async def test_start_discovery_manager(self, discovery_manager, mock_redis_manager):
        """Test starting the discovery manager."""
        with patch.object(discovery_manager.registry, 'start_monitoring') as mock_start_monitoring:
            with patch.object(discovery_manager.registry, 'register_agent', return_value=True) as mock_register:
                with patch.object(discovery_manager, 'announce_presence', return_value=True) as mock_announce:
                    result = await discovery_manager.start()
        
        assert result is True
        assert discovery_manager._is_running is True
        mock_start_monitoring.assert_called_once()
        mock_register.assert_called_once_with(discovery_manager.capabilities)
        mock_redis_manager.subscribe_to_channel.assert_called_once()
        mock_announce.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_discovery_manager_already_running(self, discovery_manager):
        """Test starting discovery manager when already running."""
        discovery_manager._is_running = True
        
        result = await discovery_manager.start()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_start_discovery_manager_redis_failure(self, discovery_manager, mock_redis_manager):
        """Test starting discovery manager with Redis subscription failure."""
        mock_redis_manager.subscribe_to_channel.return_value = False
        
        with patch.object(discovery_manager.registry, 'start_monitoring'):
            with patch.object(discovery_manager.registry, 'register_agent', return_value=True):
                result = await discovery_manager.start()
        
        assert result is False
        assert discovery_manager._is_running is False
    
    @pytest.mark.asyncio
    async def test_stop_discovery_manager(self, discovery_manager):
        """Test stopping the discovery manager."""
        # Set up running state
        discovery_manager._is_running = True
        discovery_manager._announcement_task = AsyncMock()
        discovery_manager._discovery_task = AsyncMock()
        
        with patch.object(discovery_manager.registry, 'stop_monitoring') as mock_stop:
            await discovery_manager.stop()
        
        assert discovery_manager._is_running is False
        mock_stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_announce_presence(self, discovery_manager, mock_redis_manager):
        """Test announcing agent presence."""
        with patch('src.beast_mode_network.agent_discovery.create_agent_discovery_message') as mock_create:
            with patch('src.beast_mode_network.agent_discovery.MessageSerializer') as mock_serializer:
                mock_message = MagicMock()
                mock_create.return_value = mock_message
                mock_serializer.serialize.return_value = '{"test": "message"}'
                
                result = await discovery_manager.announce_presence()
        
        assert result is True
        mock_create.assert_called_once_with(discovery_manager.capabilities)
        mock_serializer.serialize.assert_called_once_with(mock_message)
        mock_redis_manager.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_discover_agents(self, discovery_manager):
        """Test discovering agents in the network."""
        # Mock registry with some agents
        mock_agents = [
            DiscoveredAgent(agent_id="agent1", capabilities=["python"]),
            DiscoveredAgent(agent_id="agent2", capabilities=["javascript"]),
            DiscoveredAgent(agent_id="discovery_agent", capabilities=["python"])  # Self
        ]
        
        with patch.object(discovery_manager.registry, 'find_agents_by_capabilities', return_value=mock_agents):
            agents = await discovery_manager.discover_agents(["python"])
        
        # Should exclude self from results
        assert len(agents) == 1
        assert agents[0].agent_id == "agent1"
    
    @pytest.mark.asyncio
    async def test_discover_agents_no_capabilities(self, discovery_manager):
        """Test discovering agents without capability filter."""
        mock_agents = [
            DiscoveredAgent(agent_id="agent1", capabilities=["python"]),
            DiscoveredAgent(agent_id="discovery_agent", capabilities=["python"])  # Self
        ]
        
        with patch.object(discovery_manager.registry, 'get_available_agents', return_value=mock_agents):
            agents = await discovery_manager.discover_agents()
        
        # Should exclude self from results
        assert len(agents) == 1
        assert agents[0].agent_id == "agent1"
    
    @pytest.mark.asyncio
    async def test_find_best_agents(self, discovery_manager):
        """Test finding best agents with scoring."""
        mock_agents = [
            DiscoveredAgent(agent_id="agent1", capabilities=["python"], trust_score=0.8),
            DiscoveredAgent(agent_id="agent2", capabilities=["python", "data_analysis"], trust_score=0.6)
        ]
        
        with patch.object(discovery_manager, 'discover_agents', return_value=mock_agents):
            best_agents = await discovery_manager.find_best_agents(["python"], max_agents=2)
        
        assert len(best_agents) == 2
        # Results should be tuples of (agent, score)
        assert all(isinstance(result, tuple) and len(result) == 2 for result in best_agents)
        # Should be sorted by score (descending)
        assert best_agents[0][1] >= best_agents[1][1]
    
    @pytest.mark.asyncio
    async def test_track_agent_interaction(self, discovery_manager):
        """Test tracking agent interactions."""
        with patch.object(discovery_manager.registry, 'update_agent_trust', return_value=True) as mock_update:
            result = await discovery_manager.track_agent_interaction("agent1", success=True, response_time=2.5)
        
        assert result is True
        mock_update.assert_called_once_with("agent1", True, 2.5)
    
    @pytest.mark.asyncio
    async def test_get_network_stats(self, discovery_manager):
        """Test getting network statistics."""
        mock_registry_stats = {
            "total_agents": 5,
            "online_agents": 3,
            "average_trust_score": 0.7
        }
        
        with patch.object(discovery_manager.registry, 'get_registry_stats', return_value=mock_registry_stats):
            stats = await discovery_manager.get_network_stats()
        
        assert "total_agents" in stats
        assert "discovery_manager" in stats
        assert stats["discovery_manager"]["agent_id"] == "discovery_agent"
        assert stats["discovery_manager"]["is_running"] is False
    
    @pytest.mark.asyncio
    async def test_handle_agent_discovery_message(self, discovery_manager):
        """Test handling agent discovery messages."""
        from src.beast_mode_network.message_models import BeastModeMessage, MessageType
        
        message = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="remote_agent",
            payload={
                "capabilities": ["python", "web"],
                "specializations": ["backend"],
                "description": "Remote test agent",
                "version": "1.0.0",
                "max_concurrent_tasks": 3,
                "supported_message_types": ["simple_message"]
            }
        )
        
        with patch.object(discovery_manager.registry, 'register_agent', return_value=True) as mock_register:
            await discovery_manager._handle_agent_discovery(message)
        
        mock_register.assert_called_once()
        # Verify the AgentCapabilities object was created correctly
        call_args = mock_register.call_args[0][0]
        assert call_args.agent_id == "remote_agent"
        assert call_args.capabilities == ["python", "web"]
        assert call_args.specializations == ["backend"]
    
    @pytest.mark.asyncio
    async def test_handle_agent_response_message(self, discovery_manager):
        """Test handling agent response messages."""
        from src.beast_mode_network.message_models import BeastModeMessage, MessageType
        
        message = BeastModeMessage(
            type=MessageType.AGENT_RESPONSE,
            source="responding_agent",
            payload={"status": "online"}
        )
        
        with patch.object(discovery_manager.registry, 'update_agent_availability', return_value=True) as mock_update:
            await discovery_manager._handle_agent_response(message)
        
        mock_update.assert_called_once_with("responding_agent", AgentStatus.ONLINE)
    
    @pytest.mark.asyncio
    async def test_request_agent_responses(self, discovery_manager, mock_redis_manager):
        """Test requesting responses from all agents."""
        with patch('src.beast_mode_network.agent_discovery.BeastModeMessage') as mock_message_class:
            with patch('src.beast_mode_network.agent_discovery.MessageSerializer') as mock_serializer:
                mock_message = MagicMock()
                mock_message_class.return_value = mock_message
                mock_serializer.serialize.return_value = '{"test": "health_check"}'
                
                await discovery_manager._request_agent_responses()
        
        mock_redis_manager.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_discovery_manager_context_manager(self, discovery_manager):
        """Test discovery manager as async context manager."""
        with patch.object(discovery_manager, 'start', return_value=True) as mock_start:
            with patch.object(discovery_manager, 'stop') as mock_stop:
                async with discovery_manager as ctx_manager:
                    assert ctx_manager == discovery_manager
        
        mock_start.assert_called_once()
        mock_stop.assert_called_once()


class TestConvenienceFunctions:
    """Test convenience functions for agent discovery."""
    
    @pytest.mark.asyncio
    async def test_create_agent_registry(self):
        """Test create_agent_registry convenience function."""
        from src.beast_mode_network.agent_discovery import create_agent_registry
        
        registry = await create_agent_registry(availability_timeout_minutes=10)
        
        assert isinstance(registry, AgentRegistry)
        assert registry.availability_timeout_minutes == 10
        assert registry._cleanup_task is not None
        
        # Clean up
        await registry.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_create_agent_discovery_manager(self):
        """Test create_agent_discovery_manager convenience function."""
        from src.beast_mode_network.agent_discovery import create_agent_discovery_manager
        
        mock_redis_manager = AsyncMock()
        mock_redis_manager.subscribe_to_channel = AsyncMock(return_value=True)
        
        capabilities = AgentCapabilities(
            agent_id="test_agent",
            capabilities=["python"]
        )
        
        with patch.object(AgentDiscoveryManager, 'start', return_value=True):
            manager = await create_agent_discovery_manager(
                mock_redis_manager,
                "test_agent",
                capabilities,
                "test_channel"
            )
        
        assert isinstance(manager, AgentDiscoveryManager)
        assert manager.agent_id == "test_agent"
        assert manager.channel_name == "test_channel"


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases in agent discovery."""
    
    @pytest.mark.asyncio
    async def test_registry_error_handling(self):
        """Test registry error handling with invalid data."""
        registry = AgentRegistry()
        
        # Test with invalid capabilities (should handle gracefully)
        try:
            invalid_caps = AgentCapabilities(agent_id="")  # Empty ID should raise ValueError
            await registry.register_agent(invalid_caps)
        except ValueError:
            pass  # Expected
        
        # Registry should still be functional
        valid_caps = AgentCapabilities(agent_id="valid_agent", capabilities=["test"])
        result = await registry.register_agent(valid_caps)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_discovery_manager_message_handling_errors(self, discovery_manager):
        """Test discovery manager handles message processing errors gracefully."""
        from src.beast_mode_network.message_models import BeastModeMessage, MessageType
        
        # Test with malformed message payload
        bad_message = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="bad_agent",
            payload={"invalid": "structure"}  # Missing required fields
        )
        
        # Should not raise exception
        await discovery_manager._handle_agent_discovery(bad_message)
    
    @pytest.mark.asyncio
    async def test_concurrent_registry_operations(self):
        """Test concurrent registry operations don't cause race conditions."""
        registry = AgentRegistry()
        await registry.start_monitoring()
        
        async def register_and_update_agent(agent_num):
            caps = AgentCapabilities(
                agent_id=f"race_agent_{agent_num}",
                capabilities=["test"]
            )
            await registry.register_agent(caps)
            await registry.update_agent_trust(f"race_agent_{agent_num}", success=True)
            return await registry.get_agent(f"race_agent_{agent_num}")
        
        # Run many concurrent operations
        tasks = [register_and_update_agent(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All operations should complete successfully
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 20
        
        await registry.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_memory_cleanup_on_agent_removal(self):
        """Test that memory is properly cleaned up when agents are removed."""
        registry = AgentRegistry()
        
        # Register many agents
        for i in range(100):
            caps = AgentCapabilities(
                agent_id=f"temp_agent_{i}",
                capabilities=[f"skill_{i % 10}"]  # Some overlap in capabilities
            )
            await registry.register_agent(caps)
        
        # Verify all agents are registered
        stats = await registry.get_registry_stats()
        assert stats["total_agents"] == 100
        
        # Remove all agents
        for i in range(100):
            await registry.unregister_agent(f"temp_agent_{i}")
        
        # Verify cleanup
        stats = await registry.get_registry_stats()
        assert stats["total_agents"] == 0
        assert stats["total_capabilities"] == 0
        assert len(registry._capability_index) == 0
        assert len(registry._specialization_index) == 0


if __name__ == "__main__":
    pytest.main([__file__])
        stats = await registry.get_registry_stats()
        
        assert stats["total_agents"] == 0
        assert stats["online_agents"] == 0
        assert stats["offline_agents"] == 0
        assert stats["average_trust_score"] == 0.0
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using registry as async context manager."""
        async with AgentRegistry() as registry:
            assert registry._cleanup_task is not None
            
            # Register an agent
            caps = AgentCapabilities(agent_id="test_agent", capabilities=["python"])
            await registry.register_agent(caps)
            
            agent = await registry.get_agent("test_agent")
            assert agent is not None
        
        # Should be shut down after context exit
        assert registry._is_shutting_down is True
    
    @patch('asyncio.sleep')
    @pytest.mark.asyncio
    async def test_cleanup_loop_offline_detection(self, mock_sleep, registry):
        """Test that cleanup loop marks agents as offline."""
        import asyncio
        import logging
        
        # Enable debug logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        
        logger.debug("=== STARTING CLEANUP LOOP TEST ===")
        
        # Register agent
        caps = AgentCapabilities(agent_id="test_agent", capabilities=["python"])
        await registry.register_agent(caps)
        logger.debug("Agent registered")
        
        # Manually set last_seen to old time
        agent = await registry.get_agent("test_agent")
        agent.last_seen = datetime.now() - timedelta(minutes=10)
        logger.debug(f"Agent last_seen set to: {agent.last_seen}")
        
        # Mock sleep to return immediately and count calls
        call_count = 0
        def mock_sleep_func(duration):
            nonlocal call_count
            call_count += 1
            logger.debug(f"Mock sleep call #{call_count}, duration: {duration}")
            
            # After first iteration, trigger shutdown to prevent infinite loop
            if call_count >= 1:
                logger.debug("Setting shutdown flag to break loop")
                registry._is_shutting_down = True
            
            # Return a completed future instead of calling real asyncio.sleep
            future = asyncio.Future()
            future.set_result(None)
            return future
        
        mock_sleep.side_effect = mock_sleep_func
        
        # Ensure shutdown flag is initially False
        registry._is_shutting_down = False
        logger.debug(f"Initial shutdown flag: {registry._is_shutting_down}")
        
        # Run cleanup loop with timeout protection
        logger.debug("Starting cleanup loop with timeout")
        try:
            await asyncio.wait_for(registry._cleanup_loop(), timeout=2.0)
        except asyncio.TimeoutError:
            logger.warning("Cleanup loop timed out - forcing shutdown")
            registry._is_shutting_down = True
        
        logger.debug(f"Cleanup completed, sleep was called {call_count} times")
        
        # Agent should be marked offline
        updated_agent = await registry.get_agent("test_agent")
        logger.debug(f"Agent availability after cleanup: {updated_agent.availability}")
        assert updated_agent.availability == AgentStatus.OFFLINE
        
        logger.debug("=== CLEANUP LOOP TEST COMPLETED ===")
        
        # Reset shutdown flag for other tests
        registry._is_shutting_down = False

    @pytest.mark.asyncio
    async def test_capability_indexing_comprehensive(self, registry):
        """Test comprehensive capability indexing and search functionality."""
        # Register agents with overlapping capabilities
        agents_data = [
            ("agent1", ["python", "data_analysis", "machine_learning"]),
            ("agent2", ["python", "web_development", "javascript"]),
            ("agent3", ["data_analysis", "sql", "statistics"]),
            ("agent4", ["machine_learning", "tensorflow", "pytorch"]),
            ("agent5", ["python", "data_analysis", "web_development"])
        ]
        
        for agent_id, capabilities in agents_data:
            caps = AgentCapabilities(agent_id=agent_id, capabilities=capabilities)
            await registry.register_agent(caps)
        
        # Test single capability search
        python_agents = await registry.find_agents_by_capabilities(["python"])
        python_ids = [agent.agent_id for agent in python_agents]
        assert set(python_ids) == {"agent1", "agent2", "agent5"}
        
        # Test multiple capability search (intersection)
        data_python_agents = await registry.find_agents_by_capabilities(["python", "data_analysis"])
        data_python_ids = [agent.agent_id for agent in data_python_agents]
        assert set(data_python_ids) == {"agent1", "agent5"}
        
        # Test capability that no agent has
        no_match_agents = await registry.find_agents_by_capabilities(["nonexistent_skill"])
        assert len(no_match_agents) == 0
        
        # Test case insensitive search
        case_agents = await registry.find_agents_by_capabilities(["PYTHON", "Data_Analysis"])
        case_ids = [agent.agent_id for agent in case_agents]
        assert set(case_ids) == {"agent1", "agent5"}

    @pytest.mark.asyncio
    async def test_capability_search_with_availability_filtering(self, registry):
        """Test capability search with availability filtering."""
        # Register agents
        agent1_caps = AgentCapabilities(agent_id="agent1", capabilities=["python"])
        agent2_caps = AgentCapabilities(agent_id="agent2", capabilities=["python"])
        agent3_caps = AgentCapabilities(agent_id="agent3", capabilities=["python"])
        
        await registry.register_agent(agent1_caps)
        await registry.register_agent(agent2_caps)
        await registry.register_agent(agent3_caps)
        
        # Set different availability statuses
        await registry.update_agent_availability("agent1", AgentStatus.ONLINE)
        await registry.update_agent_availability("agent2", AgentStatus.OFFLINE)
        await registry.update_agent_availability("agent3", AgentStatus.BUSY)
        
        # Search excluding offline agents
        online_agents = await registry.find_agents_by_capabilities(["python"], include_offline=False)
        online_ids = [agent.agent_id for agent in online_agents]
        assert "agent2" not in online_ids  # Offline agent excluded
        assert "agent1" in online_ids
        assert "agent3" in online_ids  # BUSY is considered available
        
        # Search including offline agents
        all_agents = await registry.find_agents_by_capabilities(["python"], include_offline=True)
        all_ids = [agent.agent_id for agent in all_agents]
        assert len(all_ids) == 3
        assert set(all_ids) == {"agent1", "agent2", "agent3"}

    @pytest.mark.asyncio
    async def test_agent_ranking_by_trust_and_capability_match(self, registry):
        """Test agent ranking by trust score and capability match."""
        # Register agents with different capabilities and trust scores
        agent1_caps = AgentCapabilities(agent_id="agent1", capabilities=["python", "data_analysis"])
        agent2_caps = AgentCapabilities(agent_id="agent2", capabilities=["python", "data_analysis", "machine_learning"])
        agent3_caps = AgentCapabilities(agent_id="agent3", capabilities=["python"])
        
        await registry.register_agent(agent1_caps)
        await registry.register_agent(agent2_caps)
        await registry.register_agent(agent3_caps)
        
        # Set different trust scores
        # agent1: high trust, exact match
        for _ in range(10):
            await registry.update_agent_trust("agent1", success=True, response_time=2.0)
        
        # agent2: medium trust, better capability match (has ML)
        for _ in range(5):
            await registry.update_agent_trust("agent2", success=True, response_time=3.0)
        for _ in range(2):
            await registry.update_agent_trust("agent2", success=False, response_time=8.0)
        
        # agent3: low trust, partial match
        for _ in range(2):
            await registry.update_agent_trust("agent3", success=True, response_time=5.0)
        for _ in range(5):
            await registry.update_agent_trust("agent3", success=False, response_time=10.0)
        
        # Search for agents with python and data_analysis
        agents = await registry.find_agents_by_capabilities(["python", "data_analysis"])
        
        # Should be ranked by capability match first, then trust score
        assert len(agents) == 2  # agent3 doesn't have data_analysis
        # agent2 should be first due to better capability match (has ML bonus)
        assert agents[0].agent_id == "agent2"
        assert agents[1].agent_id == "agent1"

    @pytest.mark.asyncio
    async def test_availability_monitoring_and_timeouts(self, registry):
        """Test comprehensive availability monitoring and timeout handling."""
        # Register agent
        caps = AgentCapabilities(agent_id="test_agent", capabilities=["python"])
        await registry.register_agent(caps)
        
        # Test initial availability
        agent = await registry.get_agent("test_agent")
        assert agent.availability == AgentStatus.ONLINE
        assert agent.is_available(timeout_minutes=5) is True
        
        # Test timeout detection
        agent.last_seen = datetime.now() - timedelta(minutes=6)
        assert agent.is_available(timeout_minutes=5) is False
        
        # Test availability update
        await registry.update_agent_availability("test_agent", AgentStatus.BUSY)
        updated_agent = await registry.get_agent("test_agent")
        assert updated_agent.availability == AgentStatus.BUSY
        assert updated_agent.last_seen > agent.last_seen  # Should update timestamp
        
        # Test offline status overrides timeout
        await registry.update_agent_availability("test_agent", AgentStatus.OFFLINE)
        offline_agent = await registry.get_agent("test_agent")
        offline_agent.last_seen = datetime.now()  # Recent timestamp
        assert offline_agent.is_available(timeout_minutes=5) is False  # Still offline

    @pytest.mark.asyncio
    async def test_registry_index_consistency(self, registry):
        """Test that capability indexes remain consistent during operations."""
        # Register agent with capabilities
        caps = AgentCapabilities(
            agent_id="test_agent",
            capabilities=["python", "data_analysis"],
            specializations=["machine_learning"]
        )
        await registry.register_agent(caps)
        
        # Verify indexes are populated
        assert "python" in registry._capability_index
        assert "data_analysis" in registry._capability_index
        assert "machine_learning" in registry._specialization_index
        assert "test_agent" in registry._capability_index["python"]
        assert "test_agent" in registry._capability_index["data_analysis"]
        
        # Update agent capabilities
        updated_caps = AgentCapabilities(
            agent_id="test_agent",
            capabilities=["python", "web_development"],  # Changed data_analysis to web_development
            specializations=["backend"]  # Changed ML to backend
        )
        await registry.register_agent(updated_caps)
        
        # Verify indexes are updated correctly
        assert "test_agent" in registry._capability_index["python"]  # Still has python
        assert "test_agent" in registry._capability_index["web_development"]  # New capability
        assert "test_agent" not in registry._capability_index.get("data_analysis", set())  # Removed
        assert "test_agent" in registry._specialization_index["backend"]  # New specialization
        assert "test_agent" not in registry._specialization_index.get("machine_learning", set())  # Removed
        
        # Unregister agent
        await registry.unregister_agent("test_agent")
        
        # Verify indexes are cleaned up
        assert "test_agent" not in registry._capability_index.get("python", set())
        assert "test_agent" not in registry._capability_index.get("web_development", set())
        assert "test_agent" not in registry._specialization_index.get("backend", set())


class TestThreadSafetyAndConcurrency:
    """Test thread-safe registry operations."""
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_registration(self):
        """Test concurrent agent registration operations."""
        registry = AgentRegistry()
        await registry.start_monitoring()
        
        try:
            # Create multiple agents to register concurrently
            agent_capabilities = [
                AgentCapabilities(agent_id=f"agent_{i}", capabilities=[f"skill_{i}"])
                for i in range(10)
            ]
            
            # Register agents concurrently
            tasks = [
                registry.register_agent(caps) for caps in agent_capabilities
            ]
            results = await asyncio.gather(*tasks)
            
            # All registrations should succeed
            assert all(results)
            
            # Verify all agents are registered
            for i in range(10):
                agent = await registry.get_agent(f"agent_{i}")
                assert agent is not None
                assert agent.agent_id == f"agent_{i}"
            
            # Verify registry stats
            stats = await registry.get_registry_stats()
            assert stats["total_agents"] == 10
            
        finally:
            await registry.stop_monitoring()

    @pytest.mark.asyncio
    async def test_concurrent_trust_updates(self):
        """Test concurrent trust score updates."""
        registry = AgentRegistry()
        await registry.start_monitoring()
        
        try:
            # Register an agent
            caps = AgentCapabilities(agent_id="test_agent", capabilities=["python"])
            await registry.register_agent(caps)
            
            # Perform concurrent trust updates
            update_tasks = []
            for i in range(20):
                success = i % 3 != 0  # 2/3 success rate
                response_time = 1.0 + (i % 5)  # Varying response times
                task = registry.update_agent_trust("test_agent", success, response_time)
                update_tasks.append(task)
            
            results = await asyncio.gather(*update_tasks)
            
            # All updates should succeed
            assert all(results)
            
            # Verify final state
            agent = await registry.get_agent("test_agent")
            assert agent.total_interactions == 20
            assert agent.successful_interactions > 0
            assert agent.failed_interactions > 0
            assert 0.0 <= agent.trust_score <= 1.0
            
        finally:
            await registry.stop_monitoring()

    @pytest.mark.asyncio
    async def test_concurrent_capability_searches(self):
        """Test concurrent capability search operations."""
        registry = AgentRegistry()
        await registry.start_monitoring()
        
        try:
            # Register multiple agents
            for i in range(5):
                caps = AgentCapabilities(
                    agent_id=f"agent_{i}",
                    capabilities=["python", f"skill_{i}"]
                )
                await registry.register_agent(caps)
            
            # Perform concurrent searches
            search_tasks = [
                registry.find_agents_by_capabilities(["python"]),
                registry.find_agents_by_capabilities(["skill_0"]),
                registry.find_agents_by_capabilities(["skill_1", "python"]),
                registry.get_available_agents(),
                registry.get_registry_stats()
            ]
            
            results = await asyncio.gather(*search_tasks)
            
            # Verify search results
            python_agents, skill0_agents, skill1_python_agents, available_agents, stats = results
            
            assert len(python_agents) == 5  # All agents have python
            assert len(skill0_agents) == 1  # Only agent_0 has skill_0
            assert len(skill1_python_agents) == 1  # Only agent_1 has both
            assert len(available_agents) == 5  # All agents are available
            assert stats["total_agents"] == 5
            
        finally:
            await registry.stop_monitoring()

    @pytest.mark.asyncio
    async def test_concurrent_registration_and_search(self):
        """Test concurrent registration and search operations."""
        registry = AgentRegistry()
        await registry.start_monitoring()
        
        try:
            async def register_agents():
                """Register agents continuously."""
                for i in range(10):
                    caps = AgentCapabilities(
                        agent_id=f"reg_agent_{i}",
                        capabilities=["python", "concurrent_test"]
                    )
                    await registry.register_agent(caps)
                    await asyncio.sleep(0.01)  # Small delay
            
            async def search_agents():
                """Search for agents continuously."""
                results = []
                for _ in range(20):
                    agents = await registry.find_agents_by_capabilities(["python"])
                    results.append(len(agents))
                    await asyncio.sleep(0.005)  # Small delay
                return results
            
            # Run registration and search concurrently
            reg_task = asyncio.create_task(register_agents())
            search_task = asyncio.create_task(search_agents())
            
            await asyncio.gather(reg_task, search_task)
            
            # Verify final state
            final_agents = await registry.find_agents_by_capabilities(["python"])
            assert len(final_agents) == 10
            
        finally:
            await registry.stop_monitoring()


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_create_agent_registry(self):
        """Test creating agent registry with convenience function."""
        from src.beast_mode_network.agent_discovery import create_agent_registry
        
        registry = await create_agent_registry(availability_timeout_minutes=10)
        
        assert isinstance(registry, AgentRegistry)
        assert registry.availability_timeout_minutes == 10
        assert registry._cleanup_task is not None
        
        await registry.stop_monitoring()


class TestAgentDiscoveryManager:
    """Test cases for AgentDiscoveryManager class."""
    
    @pytest.fixture
    def mock_redis_manager(self):
        """Create a mock Redis manager."""
        mock_redis = AsyncMock()
        mock_redis.subscribe_to_channel = AsyncMock(return_value=True)
        mock_redis.publish = AsyncMock(return_value=True)
        mock_redis.is_connected = AsyncMock(return_value=True)
        return mock_redis
    
    @pytest.fixture
    def sample_capabilities(self):
        """Create sample agent capabilities for discovery manager."""
        return AgentCapabilities(
            agent_id="discovery_test_agent",
            capabilities=["python", "discovery_testing"],
            specializations=["network_coordination"],
            description="Agent for discovery manager testing"
        )
    
    @pytest.mark.asyncio
    async def test_discovery_manager_initialization(self, mock_redis_manager, sample_capabilities):
        """Test AgentDiscoveryManager initialization."""
        manager = AgentDiscoveryManager(
            redis_manager=mock_redis_manager,
            agent_id="test_agent",
            capabilities=sample_capabilities,
            channel_name="test_channel"
        )
        
        assert manager.agent_id == "test_agent"
        assert manager.capabilities == sample_capabilities
        assert manager.channel_name == "test_channel"
        assert isinstance(manager.registry, AgentRegistry)
        assert manager._is_running is False

    @pytest.mark.asyncio
    async def test_discovery_manager_start_stop(self, mock_redis_manager, sample_capabilities):
        """Test starting and stopping the discovery manager."""
        manager = AgentDiscoveryManager(
            redis_manager=mock_redis_manager,
            agent_id="test_agent",
            capabilities=sample_capabilities
        )
        
        # Test start
        result = await manager.start()
        assert result is True
        assert manager._is_running is True
        
        # Verify Redis subscription was called
        mock_redis_manager.subscribe_to_channel.assert_called_once()
        
        # Test stop
        await manager.stop()
        assert manager._is_running is False

    @pytest.mark.asyncio
    async def test_discovery_manager_with_redis_failure(self, sample_capabilities):
        """Test discovery manager behavior when Redis fails."""
        mock_redis = AsyncMock()
        mock_redis.subscribe_to_channel = AsyncMock(return_value=False)  # Simulate failure
        
        manager = AgentDiscoveryManager(
            redis_manager=mock_redis,
            agent_id="test_agent",
            capabilities=sample_capabilities
        )
        
        result = await manager.start()
        assert result is False
        assert manager._is_running is False


# Integration tests
class TestAgentDiscoveryIntegration:
    """Integration tests for agent discovery system."""
    
    @pytest.mark.asyncio
    async def test_full_agent_lifecycle(self):
        """Test complete agent lifecycle from registration to removal."""
        async with AgentRegistry(availability_timeout_minutes=1) as registry:
            # Register agent
            caps = AgentCapabilities(
                agent_id="lifecycle_agent",
                capabilities=["python", "testing"],
                specializations=["integration_testing"],
                description="Agent for lifecycle testing"
            )
            
            result = await registry.register_agent(caps)
            assert result is True
            
            # Verify registration
            agent = await registry.get_agent("lifecycle_agent")
            assert agent is not None
            assert agent.availability == AgentStatus.ONLINE
            
            # Update trust score
            await registry.update_agent_trust("lifecycle_agent", success=True, response_time=1.5)
            await registry.update_agent_trust("lifecycle_agent", success=True, response_time=2.0)
            await registry.update_agent_trust("lifecycle_agent", success=False, response_time=5.0)
            
            # Check updated metrics
            updated_agent = await registry.get_agent("lifecycle_agent")
            assert updated_agent.total_interactions == 3
            assert updated_agent.successful_interactions == 2
            assert updated_agent.failed_interactions == 1
            assert updated_agent.average_response_time > 0
            
            # Find agent by capabilities
            found_agents = await registry.find_agents_by_capabilities(["python"])
            assert len(found_agents) == 1
            assert found_agents[0].agent_id == "lifecycle_agent"
            
            # Update availability
            await registry.update_agent_availability("lifecycle_agent", AgentStatus.BUSY)
            busy_agent = await registry.get_agent("lifecycle_agent")
            assert busy_agent.availability == AgentStatus.BUSY
            
            # Get registry stats
            stats = await registry.get_registry_stats()
            assert stats["total_agents"] == 1
            assert stats["online_agents"] == 1  # BUSY is considered online
            
            # Unregister agent
            result = await registry.unregister_agent("lifecycle_agent")
            assert result is True
            
            # Verify removal
            removed_agent = await registry.get_agent("lifecycle_agent")
            assert removed_agent is None
            
            final_stats = await registry.get_registry_stats()
            assert final_stats["total_agents"] == 0

    @pytest.mark.asyncio
    async def test_multi_agent_collaboration_scenario(self):
        """Test realistic multi-agent collaboration scenario."""
        async with AgentRegistry(availability_timeout_minutes=2) as registry:
            # Register multiple agents with different capabilities
            agents_data = [
                ("python_expert", ["python", "backend", "api_development"], ["django", "fastapi"]),
                ("data_scientist", ["python", "data_analysis", "machine_learning"], ["pandas", "scikit_learn"]),
                ("frontend_dev", ["javascript", "react", "css"], ["ui_design", "responsive_design"]),
                ("devops_engineer", ["docker", "kubernetes", "ci_cd"], ["aws", "monitoring"]),
                ("fullstack_dev", ["python", "javascript", "database"], ["postgresql", "mongodb"])
            ]
            
            # Register all agents
            for agent_id, capabilities, specializations in agents_data:
                caps = AgentCapabilities(
                    agent_id=agent_id,
                    capabilities=capabilities,
                    specializations=specializations,
                    description=f"Agent specialized in {', '.join(specializations)}"
                )
                result = await registry.register_agent(caps)
                assert result is True
            
            # Simulate collaboration history and trust building
            collaboration_scenarios = [
                ("python_expert", True, 2.0),  # Fast, successful
                ("data_scientist", True, 3.5),  # Successful
                ("frontend_dev", False, 8.0),  # Failed, slow
                ("devops_engineer", True, 1.5),  # Very fast, successful
                ("fullstack_dev", True, 4.0),  # Successful
                ("python_expert", True, 1.8),  # Another success
                ("data_scientist", False, 6.0),  # One failure
                ("frontend_dev", True, 5.0),  # Redemption success
            ]
            
            for agent_id, success, response_time in collaboration_scenarios:
                await registry.update_agent_trust(agent_id, success, response_time)
            
            # Test various search scenarios
            
            # 1. Find Python developers
            python_devs = await registry.find_agents_by_capabilities(["python"])
            python_ids = [agent.agent_id for agent in python_devs]
            assert set(python_ids) == {"python_expert", "data_scientist", "fullstack_dev"}
            
            # 2. Find agents for full-stack web project
            web_project_agents = await registry.find_agents_by_capabilities(["python", "javascript"])
            assert len(web_project_agents) == 1
            assert web_project_agents[0].agent_id == "fullstack_dev"
            
            # 3. Find data analysis experts
            data_experts = await registry.find_agents_by_capabilities(["data_analysis"])
            assert len(data_experts) == 1
            assert data_experts[0].agent_id == "data_scientist"
            
            # 4. Test trust-based ranking
            all_agents = await registry.get_available_agents()
            trust_scores = [(agent.agent_id, agent.trust_score) for agent in all_agents]
            
            # Verify agents are sorted by trust score
            sorted_by_trust = sorted(trust_scores, key=lambda x: x[1], reverse=True)
            actual_order = [agent.agent_id for agent in all_agents]
            expected_order = [item[0] for item in sorted_by_trust]
            assert actual_order == expected_order
            
            # 5. Test availability scenarios
            # Set some agents as busy
            await registry.update_agent_availability("python_expert", AgentStatus.BUSY)
            await registry.update_agent_availability("frontend_dev", AgentStatus.OFFLINE)
            
            # Search should still include BUSY but exclude OFFLINE
            available_python_devs = await registry.find_agents_by_capabilities(["python"], include_offline=False)
            available_ids = [agent.agent_id for agent in available_python_devs]
            assert "python_expert" in available_ids  # BUSY is available
            assert "frontend_dev" not in available_ids  # Not a Python dev anyway
            
            # 6. Test registry statistics
            stats = await registry.get_registry_stats()
            assert stats["total_agents"] == 5
            assert stats["online_agents"] == 4  # 1 offline
            assert stats["offline_agents"] == 1
            assert stats["total_capabilities"] > 0
            assert "capability_distribution" in stats

    @pytest.mark.asyncio
    async def test_trust_score_evolution_over_time(self):
        """Test how trust scores evolve over extended collaboration."""
        async with AgentRegistry() as registry:
            # Register agent
            caps = AgentCapabilities(
                agent_id="evolving_agent",
                capabilities=["python", "testing"],
                description="Agent for trust evolution testing"
            )
            await registry.register_agent(caps)
            
            # Phase 1: Initial poor performance
            for _ in range(5):
                await registry.update_agent_trust("evolving_agent", success=False, response_time=10.0)
            
            agent = await registry.get_agent("evolving_agent")
            phase1_trust = agent.trust_score
            assert phase1_trust < 0.5  # Should be low
            
            # Phase 2: Improvement period
            for _ in range(10):
                await registry.update_agent_trust("evolving_agent", success=True, response_time=3.0)
            
            agent = await registry.get_agent("evolving_agent")
            phase2_trust = agent.trust_score
            assert phase2_trust > phase1_trust  # Should improve
            
            # Phase 3: Consistent high performance
            for _ in range(20):
                await registry.update_agent_trust("evolving_agent", success=True, response_time=2.0)
            
            agent = await registry.get_agent("evolving_agent")
            phase3_trust = agent.trust_score
            assert phase3_trust > phase2_trust  # Should continue improving
            assert phase3_trust > 0.8  # Should be high
            
            # Verify interaction counts
            assert agent.total_interactions == 35
            assert agent.successful_interactions == 30
            assert agent.failed_interactions == 5


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases in agent discovery system."""
    
    @pytest.mark.asyncio
    async def test_registry_operations_with_invalid_data(self):
        """Test registry operations with invalid or malformed data."""
        async with AgentRegistry() as registry:
            # Test with invalid agent capabilities
            invalid_caps = AgentCapabilities(
                agent_id="",  # Empty ID should be caught by AgentCapabilities validation
                capabilities=["python"]
            )
            
            with pytest.raises(ValueError):
                await registry.register_agent(invalid_caps)
            
            # Test operations on non-existent agents
            result = await registry.update_agent_availability("nonexistent", AgentStatus.ONLINE)
            assert result is False
            
            result = await registry.update_agent_trust("nonexistent", success=True)
            assert result is False
            
            result = await registry.unregister_agent("nonexistent")
            assert result is False
            
            agent = await registry.get_agent("nonexistent")
            assert agent is None

    @pytest.mark.asyncio
    async def test_capability_search_edge_cases(self):
        """Test capability search with edge cases."""
        async with AgentRegistry() as registry:
            # Register agent with empty capabilities
            caps = AgentCapabilities(agent_id="empty_caps_agent", capabilities=[])
            await registry.register_agent(caps)
            
            # Search for empty capabilities (should return all agents)
            agents = await registry.find_agents_by_capabilities([])
            assert len(agents) == 1
            
            # Search for capabilities that don't exist
            agents = await registry.find_agents_by_capabilities(["nonexistent_skill"])
            assert len(agents) == 0
            
            # Search with whitespace and case variations
            caps2 = AgentCapabilities(
                agent_id="case_test_agent",
                capabilities=["  Python  ", "DATA_analysis", ""]
            )
            await registry.register_agent(caps2)
            
            # Should find agent despite case and whitespace differences
            agents = await registry.find_agents_by_capabilities(["python", "data_analysis"])
            assert len(agents) == 1
            assert agents[0].agent_id == "case_test_agent"

    @pytest.mark.asyncio
    async def test_trust_score_boundary_conditions(self):
        """Test trust score calculations at boundary conditions."""
        agent = DiscoveredAgent(agent_id="boundary_test_agent")
        
        # Test with extreme response times
        agent.update_trust_score(success=True, response_time=0.0)  # Zero response time
        assert 0.0 <= agent.trust_score <= 1.0
        
        agent.update_trust_score(success=True, response_time=1000.0)  # Very slow response
        assert 0.0 <= agent.trust_score <= 1.0
        
        agent.update_trust_score(success=True, response_time=-5.0)  # Negative response time
        assert 0.0 <= agent.trust_score <= 1.0
        
        # Test with many interactions to check stability
        for i in range(1000):
            success = i % 2 == 0  # 50% success rate
            agent.update_trust_score(success=success, response_time=1.0)
        
        # Trust score should stabilize around 0.5 for 50% success rate
        assert 0.4 <= agent.trust_score <= 0.6
        assert agent.total_interactions == 1003  # 1000 + 3 from above

    @pytest.mark.asyncio
    async def test_availability_timeout_edge_cases(self):
        """Test availability timeout with edge cases."""
        agent = DiscoveredAgent(
            agent_id="timeout_test_agent",
            availability=AgentStatus.ONLINE
        )
        
        # Test with zero timeout
        assert agent.is_available(timeout_minutes=0) is False
        
        # Test with negative timeout (should be treated as 0)
        assert agent.is_available(timeout_minutes=-5) is False
        
        # Test with very large timeout
        agent.last_seen = datetime.now() - timedelta(days=365)  # 1 year ago
        assert agent.is_available(timeout_minutes=1000000) is True

    @pytest.mark.asyncio
    async def test_registry_cleanup_with_many_agents(self):
        """Test registry cleanup behavior with many agents."""
        registry = AgentRegistry(availability_timeout_minutes=1)
        await registry.start_monitoring()
        
        try:
            # Register many agents
            for i in range(100):
                caps = AgentCapabilities(
                    agent_id=f"cleanup_agent_{i}",
                    capabilities=[f"skill_{i % 10}"]  # 10 different skills
                )
                await registry.register_agent(caps)
            
            # Set half of them to old timestamps
            for i in range(0, 100, 2):
                agent = await registry.get_agent(f"cleanup_agent_{i}")
                if agent:
                    agent.last_seen = datetime.now() - timedelta(minutes=2)
            
            # Trigger cleanup manually
            await registry._cleanup_loop()
            
            # Check that old agents are marked offline
            offline_count = 0
            for i in range(100):
                agent = await registry.get_agent(f"cleanup_agent_{i}")
                if agent and agent.availability == AgentStatus.OFFLINE:
                    offline_count += 1
            
            assert offline_count >= 40  # At least most of the old agents should be offline
            
        finally:
            await registry.stop_monitoring()

    def test_discovered_agent_validation_comprehensive(self):
        """Test comprehensive validation in DiscoveredAgent."""
        # Test with extreme values
        agent = DiscoveredAgent(
            agent_id="validation_test",
            trust_score=5.0,  # Above 1.0
            response_count=-10,  # Negative
            success_count=100,  # More than response_count
            total_interactions=-5,  # Negative
            successful_interactions=200,  # More than total_interactions
            failed_interactions=-3,  # Negative
            average_response_time=-10.0  # Negative
        )
        
        # All values should be normalized
        assert agent.trust_score == 1.0
        assert agent.response_count == 0
        assert agent.success_count == 0  # Capped by response_count
        assert agent.total_interactions == 0
        assert agent.successful_interactions == 0  # Capped by total_interactions
        assert agent.failed_interactions == 0
        assert agent.average_response_time == 0.0

    @pytest.mark.asyncio
    async def test_registry_stats_with_empty_registry(self):
        """Test registry statistics with empty registry."""
        async with AgentRegistry() as registry:
            stats = await registry.get_registry_stats()
            
            assert stats["total_agents"] == 0
            assert stats["online_agents"] == 0
            assert stats["offline_agents"] == 0
            assert stats["average_trust_score"] == 0.0
            assert stats["total_capabilities"] == 0
            assert stats["capability_distribution"] == {}
            assert "availability_timeout_minutes" in stats


if __name__ == "__main__":
    pytest.main([__file__])