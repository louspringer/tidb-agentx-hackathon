"""
Beast Mode Agent Network - A distributed AI agent collaboration system.

This package provides the core infrastructure for AI agents to discover each other,
communicate, and collaborate in real-time using Redis-based messaging.
"""

from .message_models import (
    MessageType,
    BeastModeMessage,
    AgentCapabilities,
    MessageSerializer,
    MessageSerializationError,
    create_simple_message,
    create_help_request,
    create_agent_discovery_message,
)

from .redis_foundation import (
    ConnectionStatus,
    ConnectionConfig,
    RedisConnectionError,
    RedisConnectionManager,
    create_redis_manager,
    verify_redis_connectivity,
)

from .agent_discovery import (
    DiscoveredAgent,
    AgentRegistry,
    AgentStatus,
    create_agent_registry,
)

__version__ = "1.0.0"
__author__ = "Beast Mode Network Team"

__all__ = [
    # Message models
    "MessageType",
    "BeastModeMessage", 
    "AgentCapabilities",
    "MessageSerializer",
    "MessageSerializationError",
    "create_simple_message",
    "create_help_request",
    "create_agent_discovery_message",
    # Redis foundation
    "ConnectionStatus",
    "ConnectionConfig", 
    "RedisConnectionError",
    "RedisConnectionManager",
    "create_redis_manager",
    "verify_redis_connectivity",
    # Agent discovery
    "DiscoveredAgent",
    "AgentRegistry",
    "AgentStatus",
    "create_agent_registry",
]