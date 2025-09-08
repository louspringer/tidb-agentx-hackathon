"""
Integration tests for multi-agent scenarios in Beast Mode Agent Network.

These tests cover agent discovery and communication workflows, complete help request
lifecycles with multiple agents, message routing and handler execution, network
resilience with Redis connection failures, and agent trust score updates through
collaboration.
"""

import asyncio
import pytest
import pytest_asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import AsyncMock, patch, MagicMock
import json

from src.beast_mode_network.bus_client import BeastModeBusClient, create_bus_client
from src.beast_mode_network.message_models import (
    BeastModeMessage, MessageType, AgentCapabilities, MessageSerializer,
    create_simple_message, create_help_request
)
from src.beast_mode_network.redis_foundation import RedisConnectionManager, ConnectionConfig
from src.beast_mode_network.agent_discovery import AgentDiscoveryManager, DiscoveredAgent, AgentStatus
from src.beast_mode_network.help_system import HelpSystemManager, HelpRequest, HelpRequestStatus, HelpResponse


# Test configuration
TEST_REDIS_URL = "redis://localhost:6379"
TEST_CHANNEL = "test_beast_mode_network"
TEST_TIMEOUT = 10.0  # seconds


class MockRedisManager:
    """Mock Redis manager for testing without actual Redis."""
    
    def __init__(self):
        self.is_connected = False
        self.published_messages = []
        self.subscribers = {}
        self.message_handlers = {}
        
    async def connect(self):
        self.is_connected = True
        return True
        
    async def disconnect(self):
        self.is_connected = False
        
    async def publish(self, channel: str, message: str):
        if not self.is_connected:
            return False
        
        self.published_messages.append((channel, message))
        
        # Simulate message delivery to subscribers
        if channel in self.subscribers:
            for handler in self.subscribers[channel]:
                try:
                    await handler(channel, message)
                except Exception as e:
                    logging.error(f"Error in message handler: {e}")
        
        return True
        
    async def subscribe_to_channel(self, channel: str, handler):
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(handler)
        return True
        
    async def is_healthy(self):
        return self.is_connected


class TestAgentDiscoveryIntegration:
    """Test agent discovery and communication workflows."""
    
    @pytest_asyncio.fixture
    async def mock_redis_managers(self):
        """Create mock Redis managers for multiple agents."""
        managers = {}
        for i in range(3):
            managers[f"agent_{i}"] = MockRedisManager()
        return managers
    
    @pytest_asyncio.fixture
    async def test_agents(self, mock_redis_managers):
        """Create test agents with different capabilities."""
        agents = {}
        
        # Agent 0: Python specialist
        agents["agent_0"] = {
            "id": "agent_0",
            "capabilities": ["python", "data_analysis", "machine_learning"],
            "specializations": ["pandas", "scikit-learn"],
            "description": "Python data science specialist"
        }
        
        # Agent 1: Web development specialist
        agents["agent_1"] = {
            "id": "agent_1", 
            "capabilities": ["javascript", "web_development", "react"],
            "specializations": ["frontend", "ui_ux"],
            "description": "Frontend web developer"
        }
        
        # Agent 2: DevOps specialist
        agents["agent_2"] = {
            "id": "agent_2",
            "capabilities": ["docker", "kubernetes", "aws", "python"],
            "specializations": ["infrastructure", "deployment"],
            "description": "DevOps and infrastructure specialist"
        }
        
        return agents
    
    @pytest.mark.asyncio
    async def test_multi_agent_discovery_workflow(self, mock_redis_managers, test_agents):
        """Test complete agent discovery workflow with multiple agents."""
        bus_clients = {}
        
        try:
            # Create and connect bus clients
            for agent_id, agent_data in test_agents.items():
                with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
                    MockRedis.return_value = mock_redis_managers[agent_id]
                    
                    client = BeastModeBusClient(
                        agent_id=agent_data["id"],
                        capabilities=agent_data["capabilities"],
                        specializations=agent_data["specializations"],
                        description=agent_data["description"],
                        redis_url=TEST_REDIS_URL,
                        channel_name=TEST_CHANNEL
                    )
                    
                    # Mock the internal managers
                    client.redis_manager = mock_redis_managers[agent_id]
                    
                    # Create mock discovery manager
                    mock_discovery = AsyncMock()
                    mock_discovery.start = AsyncMock(return_value=True)
                    mock_discovery.stop = AsyncMock()
                    mock_discovery.announce_presence = AsyncMock(return_value=True)
                    client.agent_discovery_manager = mock_discovery
                    
                    # Create mock help system manager
                    mock_help = AsyncMock()
                    mock_help.start = AsyncMock(return_value=True)
                    mock_help.stop = AsyncMock()
                    client.help_system_manager = mock_help
                    
                    # Manually set connection state
                    client._is_connected = True
                    
                    bus_clients[agent_id] = client
            
            # Test agent discovery announcements
            for agent_id, client in bus_clients.items():
                success = await client.announce_presence()
                assert success, f"Failed to announce presence for {agent_id}"
                
                # Verify discovery manager was called
                client.agent_discovery_manager.announce_presence.assert_called_once()
            
            # Test message broadcasting
            test_message = "Hello from agent_0"
            success = await bus_clients["agent_0"].send_simple_message(test_message)
            assert success, "Failed to send broadcast message"
            
            # Verify message was published
            redis_manager = mock_redis_managers["agent_0"]
            assert len(redis_manager.published_messages) > 0
            
            # Check message content
            channel, message_json = redis_manager.published_messages[-1]
            assert channel == TEST_CHANNEL
            
            message = MessageSerializer.deserialize(message_json)
            assert message.type == MessageType.SIMPLE_MESSAGE
            assert message.source == "agent_0"
            assert message.payload["message"] == test_message
            
        finally:
            # Cleanup
            for client in bus_clients.values():
                await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_capability_based_agent_discovery(self, mock_redis_managers, test_agents):
        """Test discovering agents based on specific capabilities."""
        # Create mock discovered agents
        discovered_agents = [
            DiscoveredAgent(
                agent_id="agent_0",
                capabilities=["python", "data_analysis", "machine_learning"],
                specializations=["pandas", "scikit-learn"],
                availability=AgentStatus.ONLINE,
                trust_score=0.8
            ),
            DiscoveredAgent(
                agent_id="agent_1",
                capabilities=["javascript", "web_development", "react"],
                specializations=["frontend", "ui_ux"],
                availability=AgentStatus.ONLINE,
                trust_score=0.7
            ),
            DiscoveredAgent(
                agent_id="agent_2",
                capabilities=["docker", "kubernetes", "aws", "python"],
                specializations=["infrastructure", "deployment"],
                availability=AgentStatus.ONLINE,
                trust_score=0.9
            )
        ]
        
        # Create bus client for agent_0
        with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
            MockRedis.return_value = mock_redis_managers["agent_0"]
            
            client = BeastModeBusClient(
                agent_id="agent_0",
                capabilities=["python", "data_analysis"],
                redis_url=TEST_REDIS_URL,
                channel_name=TEST_CHANNEL
            )
            
            client.redis_manager = mock_redis_managers["agent_0"]
            
            # Mock discovery manager with test data
            mock_discovery = AsyncMock()
            mock_discovery.start = AsyncMock(return_value=True)
            mock_discovery.stop = AsyncMock()
            mock_discovery.discover_agents = AsyncMock(return_value=discovered_agents)
            mock_discovery.find_best_agents = AsyncMock(return_value=[
                (discovered_agents[2], 0.95),  # agent_2 has python + devops
                (discovered_agents[0], 0.85)   # agent_0 has python + ML
            ])
            client.agent_discovery_manager = mock_discovery
            
            # Mock help system manager
            mock_help = AsyncMock()
            mock_help.start = AsyncMock(return_value=True)
            mock_help.stop = AsyncMock()
            client.help_system_manager = mock_help
            
            # Manually set connection state
            client._is_connected = True
            
            try:
                # Test discovering all agents
                all_agents = await client.discover_agents()
                assert len(all_agents) == 3
                assert all([agent.agent_id in ["agent_0", "agent_1", "agent_2"] for agent in all_agents])
                
                # Test discovering agents with specific capabilities
                python_agents = await client.discover_agents(required_capabilities=["python"])
                mock_discovery.discover_agents.assert_called_with(["python"], False)
                
                # Test finding best agents for specific task
                best_agents = await client.find_best_agents(["python", "deployment"])
                assert len(best_agents) == 2
                assert best_agents[0][0].agent_id == "agent_2"  # Best match
                assert best_agents[0][1] == 0.95  # High score
                
            finally:
                await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_message_routing_and_handlers(self, mock_redis_managers):
        """Test message routing and handler execution."""
        received_messages = []
        
        async def simple_message_handler(message: BeastModeMessage):
            received_messages.append(("simple", message))
        
        async def discovery_message_handler(message: BeastModeMessage):
            received_messages.append(("discovery", message))
        
        # Create bus client
        with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
            MockRedis.return_value = mock_redis_managers["agent_0"]
            
            client = BeastModeBusClient(
                agent_id="agent_0",
                capabilities=["python"],
                redis_url=TEST_REDIS_URL,
                channel_name=TEST_CHANNEL
            )
            
            client.redis_manager = mock_redis_managers["agent_0"]
            
            # Mock managers
            mock_discovery = AsyncMock()
            mock_discovery.start = AsyncMock(return_value=True)
            mock_discovery.stop = AsyncMock()
            client.agent_discovery_manager = mock_discovery
            
            mock_help = AsyncMock()
            mock_help.start = AsyncMock(return_value=True)
            mock_help.stop = AsyncMock()
            mock_help.handle_help_message = AsyncMock()
            client.help_system_manager = mock_help
            
            # Manually set connection state
            client._is_connected = True
            
            try:
                # Register message handlers
                handler_id_1 = client.register_message_handler(
                    MessageType.SIMPLE_MESSAGE, simple_message_handler
                )
                handler_id_2 = client.register_message_handler(
                    MessageType.AGENT_DISCOVERY, discovery_message_handler
                )
                
                assert handler_id_1 != handler_id_2
                assert len(client._message_handlers) == 2
                
                # Simulate incoming messages
                simple_msg = create_simple_message("agent_1", "Hello agent_0", "agent_0")
                await client._handle_message(TEST_CHANNEL, MessageSerializer.serialize(simple_msg))
                
                discovery_msg = BeastModeMessage(
                    type=MessageType.AGENT_DISCOVERY,
                    source="agent_1",
                    payload={"capabilities": ["javascript"]}
                )
                await client._handle_message(TEST_CHANNEL, MessageSerializer.serialize(discovery_msg))
                
                # Verify handlers were called
                assert len(received_messages) == 2
                assert received_messages[0][0] == "simple"
                assert received_messages[0][1].source == "agent_1"
                assert received_messages[1][0] == "discovery"
                assert received_messages[1][1].source == "agent_1"
                
                # Test handler removal
                success = client.unregister_message_handler(handler_id_1)
                assert success
                assert len(client._message_handlers) == 1
                
                # Test removing non-existent handler
                success = client.unregister_message_handler("non_existent")
                assert not success
                
            finally:
                await client.disconnect()


class TestHelpRequestIntegration:
    """Test complete help request lifecycle with multiple agents."""
    
    @pytest_asyncio.fixture
    async def help_scenario_agents(self):
        """Create agents for help request scenarios."""
        return {
            "requester": {
                "id": "help_requester",
                "capabilities": ["project_management", "documentation"],
                "description": "Project manager needing technical help"
            },
            "helper_1": {
                "id": "python_expert",
                "capabilities": ["python", "data_analysis", "machine_learning"],
                "description": "Python and ML expert"
            },
            "helper_2": {
                "id": "web_expert", 
                "capabilities": ["javascript", "python", "web_development"],
                "description": "Full-stack web developer"
            }
        }
    
    @pytest.mark.asyncio
    async def test_complete_help_request_lifecycle(self, help_scenario_agents):
        """Test complete help request lifecycle from request to completion."""
        mock_redis = MockRedisManager()
        help_messages = []
        
        # Track help-related messages
        original_publish = mock_redis.publish
        async def track_help_messages(channel, message):
            result = await original_publish(channel, message)
            try:
                parsed_msg = MessageSerializer.deserialize(message)
                if parsed_msg.type in [MessageType.HELP_WANTED, MessageType.HELP_RESPONSE, MessageType.TECHNICAL_EXCHANGE]:
                    help_messages.append(parsed_msg)
            except:
                pass
            return result
        
        mock_redis.publish = track_help_messages
        
        # Create requester client
        with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
            MockRedis.return_value = mock_redis
            
            requester = BeastModeBusClient(
                agent_id="help_requester",
                capabilities=["project_management"],
                redis_url=TEST_REDIS_URL,
                channel_name=TEST_CHANNEL
            )
            
            requester.redis_manager = mock_redis
            
            # Mock managers for requester
            mock_discovery = AsyncMock()
            mock_discovery.start = AsyncMock(return_value=True)
            mock_discovery.stop = AsyncMock()
            mock_discovery.track_agent_interaction = AsyncMock()
            requester.agent_discovery_manager = mock_discovery
            
            # Create real help system manager for testing
            help_manager = HelpSystemManager(
                mock_redis, "help_requester", mock_discovery, TEST_CHANNEL
            )
            requester.help_system_manager = help_manager
            
            # Manually set connection state
            requester._is_connected = True
            await help_manager.start()
            
            try:
                # Step 1: Request help
                request_id = await requester.request_help(
                    required_capabilities=["python", "data_analysis"],
                    description="Need help analyzing customer data with Python pandas",
                    timeout_minutes=60,
                    priority=3
                )
                
                assert request_id != "", "Help request should return valid ID"
                
                # Verify help request was published
                help_wanted_msgs = [msg for msg in help_messages if msg.type == MessageType.HELP_WANTED]
                assert len(help_wanted_msgs) == 1
                assert help_wanted_msgs[0].payload["request_id"] == request_id
                assert help_wanted_msgs[0].payload["description"] == "Need help analyzing customer data with Python pandas"
                
                # Step 2: Simulate helper responses
                # Helper 1 responds
                helper1_response = HelpResponse(
                    responder_id="python_expert",
                    request_id=request_id,
                    message="I can help with pandas data analysis. I have 5+ years experience.",
                    capabilities_offered=["python", "pandas", "data_analysis"],
                    estimated_time_minutes=45,
                    confidence_level=0.9
                )
                
                # Add response to help manager
                help_request = help_manager._my_requests[request_id]
                success = help_request.add_response(helper1_response)
                assert success, "Should be able to add helper response"
                
                # Helper 2 responds
                helper2_response = HelpResponse(
                    responder_id="web_expert",
                    request_id=request_id,
                    message="I can help with Python data analysis, though it's not my main specialty.",
                    capabilities_offered=["python", "data_analysis"],
                    estimated_time_minutes=90,
                    confidence_level=0.6
                )
                
                success = help_request.add_response(helper2_response)
                assert success, "Should be able to add second helper response"
                
                # Verify request status updated
                assert help_request.status == HelpRequestStatus.RESPONDED
                assert len(help_request.responses) == 2
                
                # Step 3: Select best helper
                best_responses = help_request.get_best_responses(max_responses=2)
                assert len(best_responses) == 2
                assert best_responses[0].responder_id == "python_expert"  # Should be ranked higher
                
                # Select the best helper
                success = await requester.select_helper(request_id, "python_expert")
                assert success, "Should be able to select helper"
                
                # Verify selection was published
                selection_msgs = [msg for msg in help_messages if msg.type == MessageType.TECHNICAL_EXCHANGE 
                                and msg.payload.get("exchange_type") == "helper_selected"]
                assert len(selection_msgs) == 1
                assert selection_msgs[0].target == "python_expert"
                
                # Verify request status
                assert help_request.status == HelpRequestStatus.IN_PROGRESS
                assert help_request.selected_responder == "python_expert"
                
                # Step 4: Complete the help request
                success = await requester.complete_help_request(
                    request_id, success=True, completion_message="Great help with the pandas analysis!"
                )
                assert success, "Should be able to complete help request"
                
                # Verify completion was published
                completion_msgs = [msg for msg in help_messages if msg.type == MessageType.TECHNICAL_EXCHANGE 
                                 and msg.payload.get("exchange_type") == "help_completed"]
                assert len(completion_msgs) == 1
                assert completion_msgs[0].payload["success"] is True
                
                # Verify final status
                assert help_request.status == HelpRequestStatus.COMPLETED
                assert help_request.completed_at is not None
                
                # Verify trust score update was called
                mock_discovery.track_agent_interaction.assert_called_with(
                    "python_expert", True, pytest.approx(0, abs=60)  # Response time should be small
                )
                
            finally:
                await help_manager.stop()
                await requester.disconnect()
    
    @pytest.mark.asyncio
    async def test_help_request_timeout_handling(self):
        """Test help request timeout and expiration handling."""
        mock_redis = MockRedisManager()
        
        with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
            MockRedis.return_value = mock_redis
            
            requester = BeastModeBusClient(
                agent_id="timeout_requester",
                capabilities=["testing"],
                redis_url=TEST_REDIS_URL,
                channel_name=TEST_CHANNEL
            )
            
            requester.redis_manager = mock_redis
            
            # Mock managers
            mock_discovery = AsyncMock()
            mock_discovery.start = AsyncMock(return_value=True)
            mock_discovery.stop = AsyncMock()
            requester.agent_discovery_manager = mock_discovery
            
            help_manager = HelpSystemManager(
                mock_redis, "timeout_requester", mock_discovery, TEST_CHANNEL
            )
            requester.help_system_manager = help_manager
            
            await requester.connect()
            await help_manager.start()
            
            try:
                # Create help request with very short timeout
                request_id = await requester.request_help(
                    required_capabilities=["urgent_help"],
                    description="Urgent help needed",
                    timeout_minutes=1  # 1 minute timeout
                )
                
                assert request_id != ""
                
                # Get the request and manually set creation time to past
                help_request = help_manager._my_requests[request_id]
                help_request.created_at = datetime.now() - timedelta(minutes=2)  # 2 minutes ago
                
                # Check if request is expired
                assert help_request.is_expired(), "Request should be expired"
                
                # Try to add response to expired request
                response = HelpResponse(
                    responder_id="late_helper",
                    request_id=request_id,
                    message="Sorry I'm late",
                    capabilities_offered=["urgent_help"]
                )
                
                success = help_request.add_response(response)
                assert not success, "Should not be able to add response to expired request"
                
                # Try to select helper for expired request
                success = await requester.select_helper(request_id, "late_helper")
                assert not success, "Should not be able to select helper for expired request"
                
                # Mark as timeout
                success = help_request.mark_timeout()
                assert success, "Should be able to mark as timeout"
                assert help_request.status == HelpRequestStatus.TIMEOUT
                
            finally:
                await help_manager.stop()
                await requester.disconnect()
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_help_requests(self):
        """Test handling multiple concurrent help requests."""
        mock_redis = MockRedisManager()
        
        with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
            MockRedis.return_value = mock_redis
            
            requester = BeastModeBusClient(
                agent_id="multi_requester",
                capabilities=["coordination"],
                redis_url=TEST_REDIS_URL,
                channel_name=TEST_CHANNEL
            )
            
            requester.redis_manager = mock_redis
            
            # Mock managers
            mock_discovery = AsyncMock()
            mock_discovery.start = AsyncMock(return_value=True)
            mock_discovery.stop = AsyncMock()
            mock_discovery.track_agent_interaction = AsyncMock()
            requester.agent_discovery_manager = mock_discovery
            
            help_manager = HelpSystemManager(
                mock_redis, "multi_requester", mock_discovery, TEST_CHANNEL
            )
            requester.help_system_manager = help_manager
            
            await requester.connect()
            await help_manager.start()
            
            try:
                # Create multiple help requests
                request_ids = []
                
                for i in range(3):
                    request_id = await requester.request_help(
                        required_capabilities=[f"skill_{i}"],
                        description=f"Help request {i}",
                        timeout_minutes=30,
                        priority=i + 1
                    )
                    request_ids.append(request_id)
                
                assert len(request_ids) == 3
                assert all(rid != "" for rid in request_ids)
                
                # Verify all requests are stored
                my_requests = await requester.get_my_requests()
                assert len(my_requests) == 3
                
                # Add responses to each request
                for i, request_id in enumerate(request_ids):
                    help_request = help_manager._my_requests[request_id]
                    
                    response = HelpResponse(
                        responder_id=f"helper_{i}",
                        request_id=request_id,
                        message=f"I can help with request {i}",
                        capabilities_offered=[f"skill_{i}"]
                    )
                    
                    success = help_request.add_response(response)
                    assert success, f"Should be able to add response to request {i}"
                
                # Select helpers for all requests
                for i, request_id in enumerate(request_ids):
                    success = await requester.select_helper(request_id, f"helper_{i}")
                    assert success, f"Should be able to select helper for request {i}"
                
                # Complete all requests
                for i, request_id in enumerate(request_ids):
                    success = await requester.complete_help_request(request_id, success=True)
                    assert success, f"Should be able to complete request {i}"
                
                # Verify all requests are completed
                completed_requests = await requester.get_my_requests(
                    status_filter=[HelpRequestStatus.COMPLETED]
                )
                assert len(completed_requests) == 3
                
                # Verify trust score updates were called for all helpers
                assert mock_discovery.track_agent_interaction.call_count == 3
                
            finally:
                await help_manager.stop()
                await requester.disconnect()


class TestNetworkResilience:
    """Test network resilience with Redis connection failures."""
    
    @pytest.mark.asyncio
    async def test_redis_connection_failure_recovery(self):
        """Test agent behavior during Redis connection failures."""
        # Create a mock Redis manager that can simulate failures
        class FailingRedisManager:
            def __init__(self):
                self.is_connected = True
                self.fail_next_operation = False
                self.published_messages = []
                
            async def connect(self):
                if self.fail_next_operation:
                    self.fail_next_operation = False
                    return False
                self.is_connected = True
                return True
                
            async def disconnect(self):
                self.is_connected = False
                
            async def publish(self, channel: str, message: str):
                if self.fail_next_operation or not self.is_connected:
                    self.fail_next_operation = False
                    return False
                self.published_messages.append((channel, message))
                return True
                
            async def subscribe_to_channel(self, channel: str, handler):
                if self.fail_next_operation:
                    self.fail_next_operation = False
                    return False
                return True
                
            async def is_healthy(self):
                return self.is_connected and not self.fail_next_operation
        
        failing_redis = FailingRedisManager()
        
        with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
            MockRedis.return_value = failing_redis
            
            client = BeastModeBusClient(
                agent_id="resilient_agent",
                capabilities=["resilience_testing"],
                redis_url=TEST_REDIS_URL,
                channel_name=TEST_CHANNEL
            )
            
            client.redis_manager = failing_redis
            
            # Mock managers
            mock_discovery = AsyncMock()
            mock_discovery.start = AsyncMock(return_value=True)
            mock_discovery.stop = AsyncMock()
            client.agent_discovery_manager = mock_discovery
            
            mock_help = AsyncMock()
            mock_help.start = AsyncMock(return_value=True)
            mock_help.stop = AsyncMock()
            client.help_system_manager = mock_help
            
            # Test initial connection
            success = await client.connect()
            assert success, "Initial connection should succeed"
            
            try:
                # Test normal operation
                success = await client.send_simple_message("Test message")
                assert success, "Message sending should work normally"
                
                # Simulate Redis failure
                failing_redis.fail_next_operation = True
                success = await client.send_simple_message("Failed message")
                assert not success, "Message sending should fail when Redis fails"
                
                # Test recovery - Redis is back online
                success = await client.send_simple_message("Recovery message")
                assert success, "Message sending should work after recovery"
                
                # Verify messages were published (except the failed one)
                assert len(failing_redis.published_messages) == 2
                
            finally:
                await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_connection_failure_during_help_request(self):
        """Test help request handling during connection failures."""
        class InterruptibleRedisManager:
            def __init__(self):
                self.is_connected = True
                self.published_messages = []
                self.interrupt_after = None
                self.operation_count = 0
                
            async def connect(self):
                self.is_connected = True
                return True
                
            async def disconnect(self):
                self.is_connected = False
                
            async def publish(self, channel: str, message: str):
                self.operation_count += 1
                
                if self.interrupt_after and self.operation_count >= self.interrupt_after:
                    self.is_connected = False
                    return False
                    
                if not self.is_connected:
                    return False
                    
                self.published_messages.append((channel, message))
                return True
                
            async def subscribe_to_channel(self, channel: str, handler):
                return self.is_connected
                
            async def is_healthy(self):
                return self.is_connected
        
        interruptible_redis = InterruptibleRedisManager()
        
        with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
            MockRedis.return_value = interruptible_redis
            
            client = BeastModeBusClient(
                agent_id="interrupted_agent",
                capabilities=["interruption_testing"],
                redis_url=TEST_REDIS_URL,
                channel_name=TEST_CHANNEL
            )
            
            client.redis_manager = interruptible_redis
            
            # Mock managers
            mock_discovery = AsyncMock()
            mock_discovery.start = AsyncMock(return_value=True)
            mock_discovery.stop = AsyncMock()
            client.agent_discovery_manager = mock_discovery
            
            help_manager = HelpSystemManager(
                interruptible_redis, "interrupted_agent", mock_discovery, TEST_CHANNEL
            )
            client.help_system_manager = help_manager
            
            await client.connect()
            await help_manager.start()
            
            try:
                # Set interruption to happen after first publish (help request)
                interruptible_redis.interrupt_after = 1
                
                # Try to request help - should fail when trying to publish
                request_id = await client.request_help(
                    required_capabilities=["emergency_help"],
                    description="Help needed during connection failure"
                )
                
                # Request should fail due to connection interruption
                assert request_id == "", "Help request should fail when connection is interrupted"
                
                # Verify no request was stored since publish failed
                my_requests = await client.get_my_requests()
                assert len(my_requests) == 0, "No requests should be stored when publish fails"
                
            finally:
                await help_manager.stop()
                await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_message_handler_resilience(self):
        """Test message handler resilience to exceptions."""
        mock_redis = MockRedisManager()
        received_messages = []
        handler_exceptions = []
        
        async def failing_handler(message: BeastModeMessage):
            handler_exceptions.append("Handler failed")
            raise Exception("Simulated handler failure")
        
        async def working_handler(message: BeastModeMessage):
            received_messages.append(message)
        
        with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
            MockRedis.return_value = mock_redis
            
            client = BeastModeBusClient(
                agent_id="resilient_handler_agent",
                capabilities=["handler_testing"],
                redis_url=TEST_REDIS_URL,
                channel_name=TEST_CHANNEL
            )
            
            client.redis_manager = mock_redis
            
            # Mock managers
            mock_discovery = AsyncMock()
            mock_discovery.start = AsyncMock(return_value=True)
            mock_discovery.stop = AsyncMock()
            client.agent_discovery_manager = mock_discovery
            
            mock_help = AsyncMock()
            mock_help.start = AsyncMock(return_value=True)
            mock_help.stop = AsyncMock()
            mock_help.handle_help_message = AsyncMock()
            client.help_system_manager = mock_help
            
            await client.connect()
            
            try:
                # Register both failing and working handlers for same message type
                client.register_message_handler(MessageType.SIMPLE_MESSAGE, failing_handler)
                client.register_message_handler(MessageType.SIMPLE_MESSAGE, working_handler)
                
                # Send a message that will trigger both handlers
                test_message = create_simple_message("sender", "Test message", "resilient_handler_agent")
                await client._handle_message(TEST_CHANNEL, MessageSerializer.serialize(test_message))
                
                # Working handler should still receive the message despite failing handler
                assert len(received_messages) == 1, "Working handler should receive message"
                assert len(handler_exceptions) == 1, "Failing handler should have thrown exception"
                assert received_messages[0].payload["message"] == "Test message"
                
            finally:
                await client.disconnect()


class TestTrustScoreUpdates:
    """Test agent trust score updates through collaboration."""
    
    @pytest.mark.asyncio
    async def test_trust_score_updates_through_help_collaboration(self):
        """Test trust score updates through successful help collaborations."""
        mock_redis = MockRedisManager()
        trust_updates = []
        
        # Mock discovery manager to track trust updates
        class TrustTrackingDiscoveryManager:
            def __init__(self):
                self.trust_updates = []
                
            async def start(self):
                return True
                
            async def stop(self):
                pass
                
            async def track_agent_interaction(self, agent_id: str, success: bool, response_time: Optional[float]):
                self.trust_updates.append({
                    "agent_id": agent_id,
                    "success": success,
                    "response_time": response_time,
                    "timestamp": datetime.now()
                })
        
        trust_tracker = TrustTrackingDiscoveryManager()
        
        with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
            MockRedis.return_value = mock_redis
            
            requester = BeastModeBusClient(
                agent_id="trust_requester",
                capabilities=["trust_testing"],
                redis_url=TEST_REDIS_URL,
                channel_name=TEST_CHANNEL
            )
            
            requester.redis_manager = mock_redis
            requester.agent_discovery_manager = trust_tracker
            
            help_manager = HelpSystemManager(
                mock_redis, "trust_requester", trust_tracker, TEST_CHANNEL
            )
            requester.help_system_manager = help_manager
            
            await requester.connect()
            await help_manager.start()
            
            try:
                # Test successful collaboration
                request_id = await requester.request_help(
                    required_capabilities=["trust_skill"],
                    description="Help for trust testing"
                )
                
                # Add helper response
                help_request = help_manager._my_requests[request_id]
                response = HelpResponse(
                    responder_id="trusted_helper",
                    request_id=request_id,
                    message="I can help with trust testing",
                    capabilities_offered=["trust_skill"]
                )
                help_request.add_response(response)
                
                # Select helper
                await requester.select_helper(request_id, "trusted_helper")
                
                # Complete successfully
                await requester.complete_help_request(request_id, success=True)
                
                # Verify trust update for successful collaboration
                assert len(trust_tracker.trust_updates) == 1
                update = trust_tracker.trust_updates[0]
                assert update["agent_id"] == "trusted_helper"
                assert update["success"] is True
                assert update["response_time"] is not None
                
                # Test failed collaboration
                request_id_2 = await requester.request_help(
                    required_capabilities=["another_skill"],
                    description="Another help request"
                )
                
                help_request_2 = help_manager._my_requests[request_id_2]
                response_2 = HelpResponse(
                    responder_id="unreliable_helper",
                    request_id=request_id_2,
                    message="I'll try to help",
                    capabilities_offered=["another_skill"]
                )
                help_request_2.add_response(response_2)
                
                await requester.select_helper(request_id_2, "unreliable_helper")
                
                # Complete with failure
                await requester.complete_help_request(request_id_2, success=False)
                
                # Verify trust update for failed collaboration
                assert len(trust_tracker.trust_updates) == 2
                update_2 = trust_tracker.trust_updates[1]
                assert update_2["agent_id"] == "unreliable_helper"
                assert update_2["success"] is False
                
            finally:
                await help_manager.stop()
                await requester.disconnect()
    
    @pytest.mark.asyncio
    async def test_trust_score_calculation_with_response_times(self):
        """Test trust score calculations considering response times."""
        mock_redis = MockRedisManager()
        
        class DetailedTrustTracker:
            def __init__(self):
                self.interactions = []
                
            async def start(self):
                return True
                
            async def stop(self):
                pass
                
            async def track_agent_interaction(self, agent_id: str, success: bool, response_time: Optional[float]):
                self.interactions.append({
                    "agent_id": agent_id,
                    "success": success,
                    "response_time": response_time,
                    "timestamp": datetime.now()
                })
        
        trust_tracker = DetailedTrustTracker()
        
        with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
            MockRedis.return_value = mock_redis
            
            requester = BeastModeBusClient(
                agent_id="response_time_requester",
                capabilities=["timing_testing"],
                redis_url=TEST_REDIS_URL,
                channel_name=TEST_CHANNEL
            )
            
            requester.redis_manager = mock_redis
            requester.agent_discovery_manager = trust_tracker
            
            help_manager = HelpSystemManager(
                mock_redis, "response_time_requester", trust_tracker, TEST_CHANNEL
            )
            requester.help_system_manager = help_manager
            
            await requester.connect()
            await help_manager.start()
            
            try:
                # Test fast response time
                request_id = await requester.request_help(
                    required_capabilities=["speed_test"],
                    description="Fast response test"
                )
                
                help_request = help_manager._my_requests[request_id]
                
                # Simulate fast helper
                help_request.started_at = datetime.now()
                await asyncio.sleep(0.1)  # Very fast response
                
                await requester.complete_help_request(request_id, success=True)
                
                # Verify fast response time was recorded
                assert len(trust_tracker.interactions) == 1
                interaction = trust_tracker.interactions[0]
                assert interaction["response_time"] is not None
                assert interaction["response_time"] < 1.0  # Should be very fast
                
                # Test slow response time
                request_id_2 = await requester.request_help(
                    required_capabilities=["slow_test"],
                    description="Slow response test"
                )
                
                help_request_2 = help_manager._my_requests[request_id_2]
                
                # Simulate slow helper
                help_request_2.started_at = datetime.now() - timedelta(seconds=30)
                
                await requester.complete_help_request(request_id_2, success=True)
                
                # Verify slow response time was recorded
                assert len(trust_tracker.interactions) == 2
                interaction_2 = trust_tracker.interactions[1]
                assert interaction_2["response_time"] is not None
                assert interaction_2["response_time"] > 25.0  # Should be slow
                
            finally:
                await help_manager.stop()
                await requester.disconnect()


class TestSystemIntegration:
    """Test complete system integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_multi_agent_collaboration(self):
        """Test complete end-to-end multi-agent collaboration scenario."""
        # This test simulates a realistic scenario where multiple agents
        # discover each other, exchange messages, collaborate on help requests,
        # and update trust scores through successful interactions.
        
        mock_redis = MockRedisManager()
        
        # Track all system interactions
        system_events = []
        
        def log_event(event_type: str, details: Dict[str, Any]):
            system_events.append({
                "type": event_type,
                "details": details,
                "timestamp": datetime.now()
            })
        
        # Create multiple agents with different specialties
        agents_config = {
            "coordinator": {
                "capabilities": ["project_management", "coordination"],
                "description": "Project coordinator"
            },
            "data_scientist": {
                "capabilities": ["python", "data_analysis", "machine_learning"],
                "description": "Data science expert"
            },
            "web_developer": {
                "capabilities": ["javascript", "react", "web_development"],
                "description": "Frontend specialist"
            },
            "devops_engineer": {
                "capabilities": ["docker", "kubernetes", "aws", "python"],
                "description": "DevOps and infrastructure"
            }
        }
        
        agents = {}
        
        try:
            # Initialize all agents
            for agent_id, config in agents_config.items():
                with patch('src.beast_mode_network.bus_client.RedisConnectionManager') as MockRedis:
                    MockRedis.return_value = mock_redis
                    
                    agent = BeastModeBusClient(
                        agent_id=agent_id,
                        capabilities=config["capabilities"],
                        description=config["description"],
                        redis_url=TEST_REDIS_URL,
                        channel_name=TEST_CHANNEL
                    )
                    
                    agent.redis_manager = mock_redis
                    
                    # Mock discovery manager with event logging
                    mock_discovery = AsyncMock()
                    mock_discovery.start = AsyncMock(return_value=True)
                    mock_discovery.stop = AsyncMock()
                    
                    async def track_interaction(agent_id_param, success, response_time):
                        log_event("trust_update", {
                            "agent_id": agent_id_param,
                            "success": success,
                            "response_time": response_time
                        })
                    
                    mock_discovery.track_agent_interaction = track_interaction
                    agent.agent_discovery_manager = mock_discovery
                    
                    # Create help system manager
                    help_manager = HelpSystemManager(
                        mock_redis, agent_id, mock_discovery, TEST_CHANNEL
                    )
                    agent.help_system_manager = help_manager
                    
                    await agent.connect()
                    await help_manager.start()
                    
                    agents[agent_id] = agent
                    log_event("agent_connected", {"agent_id": agent_id})
            
            # Scenario: Coordinator needs help with data analysis
            log_event("help_request_start", {"requester": "coordinator"})
            
            request_id = await agents["coordinator"].request_help(
                required_capabilities=["python", "data_analysis"],
                description="Need help analyzing user engagement data",
                timeout_minutes=60
            )
            
            assert request_id != ""
            log_event("help_request_created", {"request_id": request_id})
            
            # Data scientist responds
            coordinator_help_manager = agents["coordinator"].help_system_manager
            help_request = coordinator_help_manager._my_requests[request_id]
            
            ds_response = HelpResponse(
                responder_id="data_scientist",
                request_id=request_id,
                message="I can help with data analysis using pandas and matplotlib",
                capabilities_offered=["python", "data_analysis", "visualization"],
                confidence_level=0.9
            )
            
            help_request.add_response(ds_response)
            log_event("help_response_added", {"responder": "data_scientist"})
            
            # DevOps engineer also responds (has Python skills)
            devops_response = HelpResponse(
                responder_id="devops_engineer",
                request_id=request_id,
                message="I can help with Python scripting for data processing",
                capabilities_offered=["python"],
                confidence_level=0.6
            )
            
            help_request.add_response(devops_response)
            log_event("help_response_added", {"responder": "devops_engineer"})
            
            # Coordinator selects data scientist (better match)
            await agents["coordinator"].select_helper(request_id, "data_scientist")
            log_event("helper_selected", {"helper": "data_scientist"})
            
            # Complete the collaboration successfully
            await agents["coordinator"].complete_help_request(request_id, success=True)
            log_event("help_completed", {"success": True})
            
            # Scenario: Web developer needs DevOps help
            web_request_id = await agents["web_developer"].request_help(
                required_capabilities=["docker", "deployment"],
                description="Need help containerizing React application",
                timeout_minutes=45
            )
            
            log_event("second_help_request", {"requester": "web_developer"})
            
            # DevOps engineer responds
            web_help_manager = agents["web_developer"].help_system_manager
            web_help_request = web_help_manager._my_requests[web_request_id]
            
            devops_web_response = HelpResponse(
                responder_id="devops_engineer",
                request_id=web_request_id,
                message="I can help with Docker containerization and deployment",
                capabilities_offered=["docker", "kubernetes", "deployment"],
                confidence_level=0.95
            )
            
            web_help_request.add_response(devops_web_response)
            
            await agents["web_developer"].select_helper(web_request_id, "devops_engineer")
            await agents["web_developer"].complete_help_request(web_request_id, success=True)
            
            log_event("second_help_completed", {"success": True})
            
            # Verify system state
            # Check that trust updates were recorded
            trust_events = [e for e in system_events if e["type"] == "trust_update"]
            assert len(trust_events) == 2, "Should have 2 trust updates"
            
            # Verify both collaborations were successful
            assert trust_events[0]["details"]["success"] is True
            assert trust_events[1]["details"]["success"] is True
            
            # Check that all expected events occurred
            event_types = [e["type"] for e in system_events]
            expected_events = [
                "agent_connected", "help_request_start", "help_request_created",
                "help_response_added", "helper_selected", "help_completed",
                "second_help_request", "second_help_completed", "trust_update"
            ]
            
            for expected_event in expected_events:
                assert expected_event in event_types, f"Missing expected event: {expected_event}"
            
            # Verify message flow
            assert len(mock_redis.published_messages) > 0, "Messages should have been published"
            
            # Check for help-related messages
            help_messages = []
            for channel, message_json in mock_redis.published_messages:
                try:
                    msg = MessageSerializer.deserialize(message_json)
                    if msg.type in [MessageType.HELP_WANTED, MessageType.TECHNICAL_EXCHANGE]:
                        help_messages.append(msg)
                except:
                    pass
            
            assert len(help_messages) >= 4, "Should have multiple help-related messages"
            
        finally:
            # Cleanup all agents
            for agent in agents.values():
                if hasattr(agent, 'help_system_manager') and agent.help_system_manager:
                    await agent.help_system_manager.stop()
                await agent.disconnect()


if __name__ == "__main__":
    # Configure logging for tests
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    pytest.main([__file__, "-v"])