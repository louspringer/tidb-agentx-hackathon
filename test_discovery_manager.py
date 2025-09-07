#!/usr/bin/env python3
"""
Simple test to verify AgentDiscoveryManager implementation.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from beast_mode_network.agent_discovery import AgentDiscoveryManager
from beast_mode_network.message_models import AgentCapabilities, MessageType
from beast_mode_network.redis_foundation import RedisConnectionManager, ConnectionConfig


async def test_discovery_manager():
    """Test basic AgentDiscoveryManager functionality."""
    print("Testing AgentDiscoveryManager...")
    
    # Create mock Redis manager (we'll test without actual Redis)
    config = ConnectionConfig(redis_url="redis://localhost:6379")
    redis_manager = RedisConnectionManager(config)
    
    # Create agent capabilities
    capabilities = AgentCapabilities(
        agent_id="test_agent_1",
        capabilities=["python", "data_analysis"],
        specializations=["machine_learning"],
        description="Test agent for discovery manager",
        version="1.0.0",
        supported_message_types=[MessageType.SIMPLE_MESSAGE, MessageType.HELP_WANTED]
    )
    
    # Create discovery manager
    discovery_manager = AgentDiscoveryManager(
        redis_manager=redis_manager,
        agent_id="test_agent_1",
        capabilities=capabilities,
        channel_name="test_channel"
    )
    
    print("✓ AgentDiscoveryManager created successfully")
    
    # Test basic properties
    assert discovery_manager.agent_id == "test_agent_1"
    assert discovery_manager.channel_name == "test_channel"
    assert discovery_manager.capabilities.agent_id == "test_agent_1"
    
    print("✓ Basic properties verified")
    
    # Test registry access
    assert discovery_manager.registry is not None
    
    print("✓ Registry initialized")
    
    # Test network stats (should work even without Redis connection)
    stats = await discovery_manager.get_network_stats()
    assert isinstance(stats, dict)
    assert "discovery_manager" in stats
    assert stats["discovery_manager"]["agent_id"] == "test_agent_1"
    
    print("✓ Network stats working")
    
    # Test discover agents (should return empty list without Redis)
    agents = await discovery_manager.discover_agents()
    assert isinstance(agents, list)
    
    print("✓ Agent discovery working")
    
    # Test find best agents
    best_agents = await discovery_manager.find_best_agents(["python"])
    assert isinstance(best_agents, list)
    
    print("✓ Best agent finding working")
    
    # Test track interaction
    result = await discovery_manager.track_agent_interaction("other_agent", True, 2.5)
    # Should return False since agent doesn't exist, but shouldn't crash
    assert isinstance(result, bool)
    
    print("✓ Interaction tracking working")
    
    print("All tests passed! ✓")


if __name__ == "__main__":
    asyncio.run(test_discovery_manager())