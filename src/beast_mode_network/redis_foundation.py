"""
Redis Foundation - Core Redis connection management and messaging infrastructure.

This module provides the foundational Redis connectivity, connection management,
health monitoring, and pub/sub messaging capabilities for the Beast Mode Agent Network.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum

try:
    import redis.asyncio as redis
    from redis.asyncio import Redis
    from redis.asyncio.client import PubSub
except ImportError:
    raise ImportError(
        "redis package is required. Install with: pip install redis"
    )


class ConnectionStatus(str, Enum):
    """Redis connection status enumeration."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class ConnectionConfig:
    """Configuration for Redis connection management."""
    redis_url: str = "redis://localhost:6379"
    max_retries: int = 5
    retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    backoff_multiplier: float = 2.0
    health_check_interval: float = 30.0
    connection_timeout: float = 10.0
    socket_timeout: float = 5.0


class RedisConnectionError(Exception):
    """Custom exception for Redis connection issues."""
    pass


class RedisConnectionManager:
    """
    Manages Redis connections with automatic retry logic, health monitoring,
    and pub/sub abstraction for the Beast Mode Agent Network.
    
    Features:
    - Automatic reconnection with exponential backoff
    - Health monitoring and connection state management
    - Pub/sub abstraction for message broadcasting
    - Comprehensive error handling and logging
    """
    
    def __init__(self, config: Optional[ConnectionConfig] = None):
        """
        Initialize the Redis connection manager.
        
        Args:
            config: Connection configuration. Uses defaults if None.
        """
        self.config = config or ConnectionConfig()
        self.logger = logging.getLogger(__name__)
        
        # Connection state
        self._redis_client: Optional[Redis] = None
        self._pubsub: Optional[PubSub] = None
        self._status = ConnectionStatus.DISCONNECTED
        self._retry_count = 0
        self._last_health_check = 0.0
        self._connection_lock = asyncio.Lock()
        
        # Health monitoring
        self._health_check_task: Optional[asyncio.Task] = None
        self._is_shutting_down = False
        
        self.logger.info(f"RedisConnectionManager initialized with URL: {self.config.redis_url}")
    
    @property
    def status(self) -> ConnectionStatus:
        """Get current connection status."""
        return self._status
    
    @property
    def is_connected(self) -> bool:
        """Check if currently connected to Redis."""
        return self._status == ConnectionStatus.CONNECTED
    
    @property
    def redis_client(self) -> Optional[Redis]:
        """Get the Redis client instance."""
        return self._redis_client
    
    async def connect(self) -> bool:
        """
        Establish connection to Redis with retry logic.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        async with self._connection_lock:
            if self.is_connected:
                self.logger.debug("Already connected to Redis")
                return True
            
            self._status = ConnectionStatus.CONNECTING
            self._retry_count = 0
            
            while self._retry_count < self.config.max_retries:
                try:
                    self.logger.info(f"Attempting to connect to Redis (attempt {self._retry_count + 1}/{self.config.max_retries})")
                    
                    # Create Redis client
                    self._redis_client = redis.from_url(
                        self.config.redis_url,
                        socket_timeout=self.config.socket_timeout,
                        socket_connect_timeout=self.config.connection_timeout,
                        retry_on_timeout=True,
                        decode_responses=True
                    )
                    
                    # Test connection
                    await asyncio.wait_for(
                        self._redis_client.ping(),
                        timeout=self.config.connection_timeout
                    )
                    
                    self._status = ConnectionStatus.CONNECTED
                    self._retry_count = 0
                    self._last_health_check = time.time()
                    
                    self.logger.info("Successfully connected to Redis")
                    
                    # Start health monitoring
                    await self._start_health_monitoring()
                    
                    return True
                    
                except (redis.ConnectionError, redis.TimeoutError, asyncio.TimeoutError) as e:
                    self._retry_count += 1
                    self.logger.warning(f"Redis connection attempt {self._retry_count} failed: {e}")
                    
                    if self._retry_count < self.config.max_retries:
                        # Calculate exponential backoff delay
                        delay = min(
                            self.config.retry_delay * (self.config.backoff_multiplier ** (self._retry_count - 1)),
                            self.config.max_retry_delay
                        )
                        self.logger.info(f"Retrying in {delay:.2f} seconds...")
                        await asyncio.sleep(delay)
                    
                except Exception as e:
                    self._retry_count += 1
                    self.logger.error(f"Unexpected error during Redis connection: {e}")
                    
                    if self._retry_count < self.config.max_retries:
                        # Calculate exponential backoff delay for unexpected errors too
                        delay = min(
                            self.config.retry_delay * (self.config.backoff_multiplier ** (self._retry_count - 1)),
                            self.config.max_retry_delay
                        )
                        self.logger.info(f"Retrying in {delay:.2f} seconds...")
                        await asyncio.sleep(delay)
            
            self._status = ConnectionStatus.FAILED
            self.logger.error(f"Failed to connect to Redis after {self.config.max_retries} attempts")
            return False
    
    async def disconnect(self) -> None:
        """Gracefully disconnect from Redis."""
        async with self._connection_lock:
            self._is_shutting_down = True
            
            # Stop health monitoring
            if self._health_check_task and not self._health_check_task.done():
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
                self._health_check_task = None
            
            # Close pub/sub connection
            if self._pubsub:
                try:
                    await self._pubsub.close()
                except Exception as e:
                    self.logger.warning(f"Error closing pub/sub connection: {e}")
                finally:
                    self._pubsub = None
            
            # Close Redis client
            if self._redis_client:
                try:
                    await self._redis_client.close()
                except Exception as e:
                    self.logger.warning(f"Error closing Redis client: {e}")
                finally:
                    self._redis_client = None
            
            self._status = ConnectionStatus.DISCONNECTED
            self.logger.info("Disconnected from Redis")
    
    async def is_healthy(self) -> bool:
        """
        Check Redis connection health.
        
        Returns:
            bool: True if connection is healthy, False otherwise.
        """
        if not self._redis_client or self._status != ConnectionStatus.CONNECTED:
            return False
        
        try:
            # Perform ping with timeout
            await asyncio.wait_for(
                self._redis_client.ping(),
                timeout=self.config.socket_timeout
            )
            self._last_health_check = time.time()
            return True
            
        except (redis.ConnectionError, redis.TimeoutError, asyncio.TimeoutError) as e:
            self.logger.warning(f"Redis health check failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during health check: {e}")
            return False
    
    async def publish(self, channel: str, message: str) -> bool:
        """
        Publish a message to a Redis channel.
        
        Args:
            channel: Redis channel name
            message: Message to publish
            
        Returns:
            bool: True if message was published successfully, False otherwise.
        """
        if not self.is_connected or not self._redis_client:
            self.logger.error("Cannot publish message: not connected to Redis")
            return False
        
        try:
            result = await self._redis_client.publish(channel, message)
            self.logger.debug(f"Published message to channel '{channel}', {result} subscribers received it")
            return True
            
        except (redis.ConnectionError, redis.TimeoutError) as e:
            self.logger.error(f"Failed to publish message to channel '{channel}': {e}")
            # Trigger reconnection attempt
            asyncio.create_task(self._handle_connection_loss())
            return False
            
        except Exception as e:
            self.logger.error(f"Unexpected error publishing message to channel '{channel}': {e}")
            # Also trigger reconnection for unexpected errors that might be connection-related
            asyncio.create_task(self._handle_connection_loss())
            return False
    
    async def get_pubsub(self) -> Optional[PubSub]:
        """
        Get a pub/sub connection for subscribing to channels.
        
        Returns:
            PubSub instance if connected, None otherwise.
        """
        if not self.is_connected or not self._redis_client:
            self.logger.error("Cannot create pub/sub: not connected to Redis")
            return None
        
        try:
            if not self._pubsub:
                self._pubsub = self._redis_client.pubsub()
            return self._pubsub
            
        except Exception as e:
            self.logger.error(f"Failed to create pub/sub connection: {e}")
            return None
    
    async def subscribe_to_channel(self, channel: str, 
                                 message_handler: Callable[[str, str], Awaitable[None]]) -> bool:
        """
        Subscribe to a Redis channel and handle incoming messages.
        
        Args:
            channel: Channel name to subscribe to
            message_handler: Async function to handle messages (channel, message)
            
        Returns:
            bool: True if subscription was successful, False otherwise.
        """
        pubsub = await self.get_pubsub()
        if not pubsub:
            return False
        
        try:
            await pubsub.subscribe(channel)
            self.logger.info(f"Subscribed to channel: {channel}")
            
            # Start message listening task
            asyncio.create_task(self._listen_for_messages(pubsub, message_handler))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to subscribe to channel '{channel}': {e}")
            return False
    
    async def _listen_for_messages(self, pubsub: PubSub, 
                                 message_handler: Callable[[str, str], Awaitable[None]]) -> None:
        """
        Listen for messages on subscribed channels.
        
        Args:
            pubsub: PubSub instance
            message_handler: Function to handle incoming messages
        """
        try:
            async for message in pubsub.listen():
                if self._is_shutting_down:
                    break
                
                if message['type'] == 'message':
                    channel = message['channel']
                    data = message['data']
                    
                    try:
                        await message_handler(channel, data)
                    except Exception as e:
                        self.logger.error(f"Error in message handler for channel '{channel}': {e}")
                        
        except Exception as e:
            self.logger.error(f"Error listening for messages: {e}")
            if not self._is_shutting_down:
                # Attempt to reconnect
                asyncio.create_task(self._handle_connection_loss())
    
    async def _start_health_monitoring(self) -> None:
        """Start the health monitoring task."""
        if self._health_check_task and not self._health_check_task.done():
            return
        
        self._health_check_task = asyncio.create_task(self._health_monitor_loop())
    
    async def _health_monitor_loop(self) -> None:
        """Continuous health monitoring loop."""
        while not self._is_shutting_down and self.is_connected:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                if not await self.is_healthy():
                    self.logger.warning("Health check failed, attempting reconnection")
                    await self._handle_connection_loss()
                    break
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health monitor loop: {e}")
                await asyncio.sleep(5)  # Brief pause before continuing
    
    async def _handle_connection_loss(self) -> None:
        """Handle connection loss and attempt reconnection."""
        if self._status == ConnectionStatus.RECONNECTING:
            return  # Already reconnecting
        
        self._status = ConnectionStatus.RECONNECTING
        self.logger.warning("Connection lost, attempting to reconnect...")
        
        # Close existing connections
        if self._pubsub:
            try:
                await self._pubsub.close()
            except Exception:
                pass
            self._pubsub = None
        
        if self._redis_client:
            try:
                await self._redis_client.close()
            except Exception:
                pass
            self._redis_client = None
        
        # Attempt reconnection
        success = await self.connect()
        if not success:
            self.logger.error("Failed to reconnect to Redis")
            self._status = ConnectionStatus.FAILED
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Convenience functions for common operations
async def create_redis_manager(redis_url: str = "redis://localhost:6379",
                             max_retries: int = 5) -> RedisConnectionManager:
    """
    Create and connect a Redis connection manager.
    
    Args:
        redis_url: Redis connection URL
        max_retries: Maximum connection retry attempts
        
    Returns:
        Connected RedisConnectionManager instance
        
    Raises:
        RedisConnectionError: If connection fails after all retries
    """
    config = ConnectionConfig(redis_url=redis_url, max_retries=max_retries)
    manager = RedisConnectionManager(config)
    
    if not await manager.connect():
        raise RedisConnectionError(f"Failed to connect to Redis at {redis_url}")
    
    return manager


async def verify_redis_connectivity(redis_url: str = "redis://localhost:6379") -> bool:
    """
    Verify Redis connectivity without maintaining a connection.
    
    Args:
        redis_url: Redis connection URL
        
    Returns:
        bool: True if Redis is accessible, False otherwise.
    """
    try:
        manager = await create_redis_manager(redis_url, max_retries=1)
        try:
            result = await manager.is_healthy()
            return result
        finally:
            await manager.disconnect()
    except Exception:
        return False