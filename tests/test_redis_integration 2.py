"""
Integration tests for Redis Foundation with Message Models.

Tests the integration between RedisConnectionManager and BeastModeMessage
to ensure they work together correctly.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from src.beast_mode_network.redis_foundation import (
    RedisConnectionManager,
    ConnectionConfig,
    verify_redis_connectivity,
)
from src.beast_mode_network.message_models import (
    BeastModeMessage,
    MessageType,
    MessageSerializer,
    create_simple_message,
)


class TestRedisMessageIntegration:
    """Test integration between Redis foundation and message models."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ConnectionConfig(
            redis_url="redis://test:6379",
            max_retries=1,
            retry_delay=0.1
        )
    
    @pytest.fixture
    def manager(self, config):
        """Create RedisConnectionManager instance."""
        return RedisConnectionManager(config)
    
    @pytest.mark.asyncio
    async def test_publish_beast_mode_message(self, manager):
        """Test publishing a BeastModeMessage through Redis."""
        # Create a test message
        message = create_simple_message(
            source="test_agent",
            target="target_agent",
            message_text="Hello, Beast Mode!"
        )
        
        # Serialize the message
        serialized = MessageSerializer.serialize(message)
        
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.publish = AsyncMock(return_value=1)
        
        with patch('src.beast_mode_network.redis_foundation.redis.from_url', return_value=mock_redis):
            with patch.object(manager, '_start_health_monitoring', new_callable=AsyncMock):
                # Connect and publish
                await manager.connect()
                result = await manager.publish("beast_mode_network", serialized)
        
        assert result is True
        mock_redis.publish.assert_called_once_with("beast_mode_network", serialized)
        
        # Verify the serialized message can be deserialized
        deserialized = MessageSerializer.deserialize(serialized)
        assert deserialized.type == MessageType.SIMPLE_MESSAGE
        assert deserialized.source == "test_agent"
        assert deserialized.target == "target_agent"
        assert deserialized.payload["message"] == "Hello, Beast Mode!"
    
    @pytest.mark.asyncio
    async def test_message_handler_integration(self, manager):
        """Test message handling with BeastModeMessage deserialization."""
        received_messages = []
        
        async def message_handler(channel: str, message_data: str):
            """Handler that deserializes BeastModeMessage."""
            try:
                message = MessageSerializer.deserialize(message_data)
                received_messages.append((channel, message))
            except Exception as e:
                pytest.fail(f"Failed to deserialize message: {e}")
        
        # Create test messages
        message1 = create_simple_message("agent1", "First message", target="agent2")
        message2 = create_simple_message("agent2", "Second message", target="agent1")
        
        # Mock pub/sub behavior
        mock_pubsub = AsyncMock()
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.pubsub.return_value = mock_pubsub
        
        # Mock message stream
        messages = [
            {'type': 'subscribe', 'channel': 'test_channel'},
            {'type': 'message', 'channel': 'test_channel', 'data': MessageSerializer.serialize(message1)},
            {'type': 'message', 'channel': 'test_channel', 'data': MessageSerializer.serialize(message2)},
        ]
        
        async def mock_listen():
            for msg in messages:
                yield msg
        
        mock_pubsub.listen = mock_listen
        mock_pubsub.subscribe = AsyncMock()
        
        with patch('src.beast_mode_network.redis_foundation.redis.from_url', return_value=mock_redis):
            with patch.object(manager, '_start_health_monitoring', new_callable=AsyncMock):
                await manager.connect()
                
                # Start listening for messages
                listen_task = asyncio.create_task(
                    manager._listen_for_messages(mock_pubsub, message_handler)
                )
                
                # Let it process messages
                await asyncio.sleep(0.1)
                manager._is_shutting_down = True
                
                try:
                    await asyncio.wait_for(listen_task, timeout=1.0)
                except asyncio.TimeoutError:
                    listen_task.cancel()
        
        # Verify messages were received and deserialized correctly
        assert len(received_messages) == 2
        
        channel1, msg1 = received_messages[0]
        assert channel1 == 'test_channel'
        assert msg1.source == "agent1"
        assert msg1.target == "agent2"
        assert msg1.payload["message"] == "First message"
        
        channel2, msg2 = received_messages[1]
        assert channel2 == 'test_channel'
        assert msg2.source == "agent2"
        assert msg2.target == "agent1"
        assert msg2.payload["message"] == "Second message"
    
    @pytest.mark.asyncio
    async def test_connectivity_verification_integration(self):
        """Test Redis connectivity verification with mocked Redis."""
        with patch('src.beast_mode_network.redis_foundation.RedisConnectionManager') as MockManager:
            mock_instance = AsyncMock()
            mock_instance.connect = AsyncMock(return_value=True)
            mock_instance.is_healthy = AsyncMock(return_value=True)
            mock_instance.disconnect = AsyncMock()
            MockManager.return_value = mock_instance
            
            result = await verify_redis_connectivity("redis://test:6379")
            
            assert result is True
            mock_instance.connect.assert_called_once()
            mock_instance.is_healthy.assert_called_once()
            mock_instance.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_with_invalid_message(self, manager):
        """Test error handling when receiving invalid message data."""
        error_logged = False
        
        async def message_handler(channel: str, message_data: str):
            """Handler that tries to deserialize invalid data."""
            try:
                MessageSerializer.deserialize(message_data)
            except Exception:
                nonlocal error_logged
                error_logged = True
                # This is expected behavior - handler should handle errors gracefully
        
        # Mock pub/sub with invalid message data
        mock_pubsub = AsyncMock()
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.pubsub.return_value = mock_pubsub
        
        messages = [
            {'type': 'message', 'channel': 'test_channel', 'data': 'invalid json data'},
        ]
        
        async def mock_listen():
            for msg in messages:
                yield msg
        
        mock_pubsub.listen = mock_listen
        
        with patch('src.beast_mode_network.redis_foundation.redis.from_url', return_value=mock_redis):
            with patch.object(manager, '_start_health_monitoring', new_callable=AsyncMock):
                await manager.connect()
                
                listen_task = asyncio.create_task(
                    manager._listen_for_messages(mock_pubsub, message_handler)
                )
                
                await asyncio.sleep(0.1)
                manager._is_shutting_down = True
                
                try:
                    await asyncio.wait_for(listen_task, timeout=1.0)
                except asyncio.TimeoutError:
                    listen_task.cancel()
        
        # Verify that the error was handled gracefully
        assert error_logged is True


if __name__ == "__main__":
    pytest.main([__file__])