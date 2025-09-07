"""
Unit tests for Redis Foundation module.

Tests the RedisConnectionManager class and related functionality including
connection management, retry logic, health monitoring, and pub/sub operations.
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch, call
from typing import Any, Dict

from src.beast_mode_network.redis_foundation import (
    ConnectionStatus,
    ConnectionConfig,
    RedisConnectionError,
    RedisConnectionManager,
    create_redis_manager,
    verify_redis_connectivity,
)


class TestConnectionConfig:
    """Test ConnectionConfig dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = ConnectionConfig()
        
        assert config.redis_url == "redis://localhost:6379"
        assert config.max_retries == 5
        assert config.retry_delay == 1.0
        assert config.max_retry_delay == 60.0
        assert config.backoff_multiplier == 2.0
        assert config.health_check_interval == 30.0
        assert config.connection_timeout == 10.0
        assert config.socket_timeout == 5.0
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = ConnectionConfig(
            redis_url="redis://custom:6380",
            max_retries=3,
            retry_delay=2.0
        )
        
        assert config.redis_url == "redis://custom:6380"
        assert config.max_retries == 3
        assert config.retry_delay == 2.0


class TestRedisConnectionManager:
    """Test RedisConnectionManager class."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ConnectionConfig(
            redis_url="redis://test:6379",
            max_retries=3,
            retry_delay=0.1,
            health_check_interval=1.0
        )
    
    @pytest.fixture
    def manager(self, config):
        """Create RedisConnectionManager instance."""
        return RedisConnectionManager(config)
    
    def test_initialization(self, manager, config):
        """Test manager initialization."""
        assert manager.config == config
        assert manager.status == ConnectionStatus.DISCONNECTED
        assert not manager.is_connected
        assert manager.redis_client is None
    
    def test_initialization_with_defaults(self):
        """Test manager initialization with default config."""
        manager = RedisConnectionManager()
        
        assert manager.config.redis_url == "redis://localhost:6379"
        assert manager.status == ConnectionStatus.DISCONNECTED
    
    @pytest.mark.asyncio
    async def test_successful_connection(self, manager):
        """Test successful Redis connection."""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('src.beast_mode_network.redis_foundation.redis.from_url', return_value=mock_redis):
            with patch.object(manager, '_start_health_monitoring', new_callable=AsyncMock):
                result = await manager.connect()
        
        assert result is True
        assert manager.status == ConnectionStatus.CONNECTED
        assert manager.is_connected
        assert manager.redis_client == mock_redis
        mock_redis.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connection_already_connected(self, manager):
        """Test connection when already connected."""
        manager._status = ConnectionStatus.CONNECTED
        
        result = await manager.connect()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_connection_failure_with_retries(self, manager):
        """Test connection failure with retry logic."""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(side_effect=Exception("Connection failed"))
        
        with patch('src.beast_mode_network.redis_foundation.redis.from_url', return_value=mock_redis):
            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                result = await manager.connect()
        
        assert result is False
        assert manager.status == ConnectionStatus.FAILED
        assert mock_redis.ping.call_count == 3  # max_retries
        assert mock_sleep.call_count == 2  # retries - 1
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self, manager):
        """Test exponential backoff in retry logic."""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(side_effect=Exception("Connection failed"))
        
        with patch('src.beast_mode_network.redis_foundation.redis.from_url', return_value=mock_redis):
            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                await manager.connect()
        
        # Check exponential backoff delays
        expected_delays = [0.1, 0.2]  # retry_delay * backoff_multiplier^(attempt-1)
        actual_delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert actual_delays == expected_delays
    
    @pytest.mark.asyncio
    async def test_disconnect(self, manager):
        """Test graceful disconnection."""
        # Setup connected state
        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        
        # Create a proper task mock that can be awaited and cancelled
        async def mock_task_coro():
            raise asyncio.CancelledError()
        
        mock_task = asyncio.create_task(mock_task_coro())
        # Let the task start
        await asyncio.sleep(0.01)
        
        manager._redis_client = mock_redis
        manager._pubsub = mock_pubsub
        manager._health_check_task = mock_task
        manager._status = ConnectionStatus.CONNECTED
        
        await manager.disconnect()
        
        assert manager.status == ConnectionStatus.DISCONNECTED
        assert manager._redis_client is None
        assert manager._pubsub is None
        assert mock_task.cancelled()
        mock_pubsub.close.assert_called_once()
        mock_redis.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, manager):
        """Test successful health check."""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        manager._redis_client = mock_redis
        manager._status = ConnectionStatus.CONNECTED
        
        result = await manager.is_healthy()
        
        assert result is True
        mock_redis.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, manager):
        """Test health check failure."""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(side_effect=Exception("Ping failed"))
        
        manager._redis_client = mock_redis
        manager._status = ConnectionStatus.CONNECTED
        
        result = await manager.is_healthy()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_not_connected(self, manager):
        """Test health check when not connected."""
        result = await manager.is_healthy()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_publish_success(self, manager):
        """Test successful message publishing."""
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock(return_value=2)  # 2 subscribers
        
        manager._redis_client = mock_redis
        manager._status = ConnectionStatus.CONNECTED
        
        result = await manager.publish("test_channel", "test_message")
        
        assert result is True
        mock_redis.publish.assert_called_once_with("test_channel", "test_message")
    
    @pytest.mark.asyncio
    async def test_publish_not_connected(self, manager):
        """Test publishing when not connected."""
        result = await manager.publish("test_channel", "test_message")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_publish_failure(self, manager):
        """Test publishing failure with connection loss handling."""
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock(side_effect=Exception("Publish failed"))
        
        manager._redis_client = mock_redis
        manager._status = ConnectionStatus.CONNECTED
        
        with patch('asyncio.create_task') as mock_create_task:
            result = await manager.publish("test_channel", "test_message")
        
        assert result is False
        mock_create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_pubsub_success(self, manager):
        """Test getting pub/sub connection."""
        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)
        
        manager._redis_client = mock_redis
        manager._status = ConnectionStatus.CONNECTED
        
        result = await manager.get_pubsub()
        
        assert result == mock_pubsub
        assert manager._pubsub == mock_pubsub
    
    @pytest.mark.asyncio
    async def test_get_pubsub_not_connected(self, manager):
        """Test getting pub/sub when not connected."""
        result = await manager.get_pubsub()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_subscribe_to_channel_success(self, manager):
        """Test successful channel subscription."""
        mock_pubsub = AsyncMock()
        mock_handler = AsyncMock()
        
        with patch.object(manager, 'get_pubsub', return_value=mock_pubsub):
            with patch('asyncio.create_task') as mock_create_task:
                result = await manager.subscribe_to_channel("test_channel", mock_handler)
        
        assert result is True
        mock_pubsub.subscribe.assert_called_once_with("test_channel")
        mock_create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_subscribe_to_channel_no_pubsub(self, manager):
        """Test channel subscription when pub/sub unavailable."""
        with patch.object(manager, 'get_pubsub', return_value=None):
            result = await manager.subscribe_to_channel("test_channel", AsyncMock())
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_listen_for_messages(self, manager):
        """Test message listening loop."""
        mock_pubsub = AsyncMock()
        mock_handler = AsyncMock()
        
        # Mock message stream
        messages = [
            {'type': 'subscribe', 'channel': 'test_channel'},
            {'type': 'message', 'channel': 'test_channel', 'data': 'test_message'},
            {'type': 'message', 'channel': 'test_channel', 'data': 'another_message'},
        ]
        
        async def mock_listen():
            for msg in messages:
                yield msg
        
        mock_pubsub.listen = mock_listen
        
        # Run listener for a short time
        task = asyncio.create_task(manager._listen_for_messages(mock_pubsub, mock_handler))
        await asyncio.sleep(0.1)
        manager._is_shutting_down = True
        
        try:
            await asyncio.wait_for(task, timeout=1.0)
        except asyncio.TimeoutError:
            task.cancel()
        
        # Verify handler was called for message types only
        assert mock_handler.call_count == 2
        mock_handler.assert_any_call('test_channel', 'test_message')
        mock_handler.assert_any_call('test_channel', 'another_message')
    
    @pytest.mark.asyncio
    async def test_connection_loss_handling(self, manager):
        """Test connection loss handling and reconnection."""
        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        
        manager._redis_client = mock_redis
        manager._pubsub = mock_pubsub
        manager._status = ConnectionStatus.CONNECTED
        
        with patch.object(manager, 'connect', return_value=True) as mock_connect:
            await manager._handle_connection_loss()
        
        # After successful reconnect, status should be CONNECTED
        # But the connect method will set it, so we check that connect was called
        mock_pubsub.close.assert_called_once()
        mock_redis.close.assert_called_once()
        mock_connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_context_manager(self, manager):
        """Test async context manager functionality."""
        with patch.object(manager, 'connect', return_value=True) as mock_connect:
            with patch.object(manager, 'disconnect') as mock_disconnect:
                async with manager as ctx_manager:
                    assert ctx_manager == manager
        
        mock_connect.assert_called_once()
        mock_disconnect.assert_called_once()


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_create_redis_manager_success(self):
        """Test successful Redis manager creation."""
        with patch('src.beast_mode_network.redis_foundation.RedisConnectionManager') as MockManager:
            mock_instance = AsyncMock()
            mock_instance.connect = AsyncMock(return_value=True)
            MockManager.return_value = mock_instance
            
            result = await create_redis_manager("redis://test:6379", max_retries=3)
            
            assert result == mock_instance
            mock_instance.connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_redis_manager_failure(self):
        """Test Redis manager creation failure."""
        with patch('src.beast_mode_network.redis_foundation.RedisConnectionManager') as MockManager:
            mock_instance = AsyncMock()
            mock_instance.connect = AsyncMock(return_value=False)
            MockManager.return_value = mock_instance
            
            with pytest.raises(RedisConnectionError):
                await create_redis_manager("redis://test:6379")
    
    @pytest.mark.asyncio
    async def test_verify_redis_connectivity_success(self):
        """Test successful Redis connectivity verification."""
        mock_manager = AsyncMock()
        mock_manager.is_healthy = AsyncMock(return_value=True)
        mock_manager.disconnect = AsyncMock()
        
        with patch('src.beast_mode_network.redis_foundation.create_redis_manager', return_value=mock_manager):
            result = await verify_redis_connectivity("redis://test:6379")
            
            assert result is True
            mock_manager.is_healthy.assert_called_once()
            mock_manager.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verify_redis_connectivity_failure(self):
        """Test Redis connectivity verification failure."""
        with patch('src.beast_mode_network.redis_foundation.create_redis_manager', side_effect=Exception("Connection failed")):
            result = await verify_redis_connectivity("redis://test:6379")
            assert result is False


class TestConnectionStatus:
    """Test ConnectionStatus enum."""
    
    def test_enum_values(self):
        """Test enum values are correct."""
        assert ConnectionStatus.DISCONNECTED == "disconnected"
        assert ConnectionStatus.CONNECTING == "connecting"
        assert ConnectionStatus.CONNECTED == "connected"
        assert ConnectionStatus.RECONNECTING == "reconnecting"
        assert ConnectionStatus.FAILED == "failed"


if __name__ == "__main__":
    pytest.main([__file__])