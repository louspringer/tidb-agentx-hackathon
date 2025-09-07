"""
Bus Client for Beast Mode Agent Network.

This module provides a high-level API for agents to connect to the network,
send messages, handle responses, and participate in collaborative workflows.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Callable, Awaitable, Any, Union
from dataclasses import dataclass
from datetime import datetime

from .message_models import (
    BeastModeMessage, MessageType, AgentCapabilities, MessageSerializer,
    create_simple_message, create_agent_discovery_message, create_help_request
)
from .redis_foundation import RedisConnectionManager, ConnectionConfig
from .agent_discovery import AgentDiscoveryManager, DiscoveredAgent
from .help_system import HelpSystemManager, HelpRequest, HelpResponse, HelpRequestStatus


@dataclass
class MessageHandler:
    """Represents a registered message handler."""
    message_type: MessageType
    handler: Callable[[BeastModeMessage], Awaitable[None]]
    agent_filter: Optional[str] = None  # Filter by source agent ID


class BeastModeBusClient:
    """
    High-level client for connecting to the Beast Mode Agent Network.
    
    This class provides a simplified API for agents to join the network,
    send messages, discover other agents, request help, and handle responses.
    """
    
    def __init__(self, agent_id: str, capabilities: List[str],
                 specializations: Optional[List[str]] = None,
                 description: str = "",
                 redis_url: str = "redis://localhost:6379",
                 channel_name: str = "beast_mode_network",
                 version: str = "1.0.0",
                 max_concurrent_tasks: int = 5):
        """
        Initialize the bus client.
        
        Args:
            agent_id: Unique identifier for this agent
            capabilities: List of agent capabilities
            specializations: Optional list of specializations
            description: Description of the agent
            redis_url: Redis connection URL
            channel_name: Redis channel for network communication
            version: Agent version
            max_concurrent_tasks: Maximum concurrent tasks this agent can handle
        """
        self.logger = logging.getLogger(__name__)
        self.agent_id = agent_id
        self.channel_name = channel_name
        
        # Create agent capabilities
        self.capabilities = AgentCapabilities(
            agent_id=agent_id,
            capabilities=capabilities,
            specializations=specializations or [],
            description=description,
            version=version,
            max_concurrent_tasks=max_concurrent_tasks,
            supported_message_types=[
                MessageType.SIMPLE_MESSAGE,
                MessageType.AGENT_DISCOVERY,
                MessageType.AGENT_RESPONSE,
                MessageType.HELP_WANTED,
                MessageType.HELP_RESPONSE,
                MessageType.TECHNICAL_EXCHANGE,
                MessageType.SYSTEM_HEALTH
            ]
        )
        
        # Initialize components
        redis_config = ConnectionConfig(redis_url=redis_url)
        self.redis_manager = RedisConnectionManager(redis_config)
        self.agent_discovery_manager: Optional[AgentDiscoveryManager] = None
        self.help_system_manager: Optional[HelpSystemManager] = None
        
        # Message handling
        self._message_handlers: Dict[str, MessageHandler] = {}
        self._is_listening = False
        self._listen_task: Optional[asyncio.Task] = None
        
        # Connection state
        self._is_connected = False
        self._connection_lock = asyncio.Lock()
        
        # Configuration
        self.auto_respond_to_discovery = True
        self.auto_respond_to_health_checks = True
        
        self.logger.info(f"BeastModeBusClient initialized for agent {agent_id}")
    
    async def connect(self) -> bool:
        """
        Connect to the Beast Mode Agent Network.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        async with self._connection_lock:
            if self._is_connected:
                self.logger.warning("Bus client is already connected")
                return True
            
            try:
                # Connect to Redis
                if not await self.redis_manager.connect():
                    self.logger.error("Failed to connect to Redis")
                    return False
                
                # Initialize agent discovery manager
                self.agent_discovery_manager = AgentDiscoveryManager(
                    self.redis_manager,
                    self.agent_id,
                    self.capabilities,
                    self.channel_name
                )
                
                if not await self.agent_discovery_manager.start():
                    self.logger.error("Failed to start agent discovery manager")
                    await self.redis_manager.disconnect()
                    return False
                
                # Initialize help system manager
                self.help_system_manager = HelpSystemManager(
                    self.redis_manager,
                    self.agent_id,
                    self.agent_discovery_manager,
                    self.channel_name
                )
                
                if not await self.help_system_manager.start():
                    self.logger.error("Failed to start help system manager")
                    await self.agent_discovery_manager.stop()
                    await self.redis_manager.disconnect()
                    return False
                
                # Subscribe to the main channel
                success = await self.redis_manager.subscribe_to_channel(
                    self.channel_name,
                    self._handle_message
                )
                
                if not success:
                    self.logger.error("Failed to subscribe to network channel")
                    await self._cleanup()
                    return False
                
                # Start message listening
                await self._start_listening()
                
                # Announce presence
                await self.announce_presence()
                
                self._is_connected = True
                self.logger.info(f"Successfully connected to Beast Mode Agent Network")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to connect to network: {e}")
                await self._cleanup()
                return False
    
    async def disconnect(self) -> None:
        """Disconnect from the Beast Mode Agent Network."""
        async with self._connection_lock:
            if not self._is_connected:
                return
            
            self._is_connected = False
            
            # Stop listening
            await self._stop_listening()
            
            # Cleanup components
            await self._cleanup()
            
            self.logger.info("Disconnected from Beast Mode Agent Network")
    
    async def announce_presence(self) -> bool:
        """
        Announce this agent's presence to the network.
        
        Returns:
            bool: True if announcement was successful, False otherwise
        """
        if not self._is_connected or not self.agent_discovery_manager:
            self.logger.warning("Cannot announce presence: not connected")
            return False
        
        return await self.agent_discovery_manager.announce_presence()
    
    async def send_message(self, message: BeastModeMessage) -> bool:
        """
        Send a message to the network.
        
        Args:
            message: BeastModeMessage to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if not self._is_connected:
            self.logger.warning("Cannot send message: not connected")
            return False
        
        try:
            # Ensure message has correct source
            message.source = self.agent_id
            
            # Serialize and publish
            message_json = MessageSerializer.serialize(message)
            success = await self.redis_manager.publish(self.channel_name, message_json)
            
            if success:
                self.logger.debug(f"Sent message: {message.type.value} to {message.target or 'broadcast'}")
            else:
                self.logger.warning(f"Failed to send message: {message.type.value}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    async def send_simple_message(self, message_text: str, 
                                target_agent: Optional[str] = None) -> bool:
        """
        Send a simple text message to another agent or broadcast.
        
        Args:
            message_text: Text message to send
            target_agent: Optional target agent ID (None for broadcast)
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            message = create_simple_message(self.agent_id, message_text, target_agent)
            return await self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending simple message: {e}")
            return False
    
    async def discover_agents(self, required_capabilities: Optional[List[str]] = None,
                            include_offline: bool = False) -> List[DiscoveredAgent]:
        """
        Discover agents in the network.
        
        Args:
            required_capabilities: Optional list of required capabilities
            include_offline: Whether to include offline agents
            
        Returns:
            List of discovered agents
        """
        if not self._is_connected or not self.agent_discovery_manager:
            self.logger.warning("Cannot discover agents: not connected")
            return []
        
        return await self.agent_discovery_manager.discover_agents(
            required_capabilities, include_offline
        )
    
    async def find_best_agents(self, required_capabilities: List[str],
                             max_agents: int = 5) -> List[tuple]:
        """
        Find the best agents for specific capabilities.
        
        Args:
            required_capabilities: List of required capabilities
            max_agents: Maximum number of agents to return
            
        Returns:
            List of tuples (agent, score) sorted by score
        """
        if not self._is_connected or not self.agent_discovery_manager:
            self.logger.warning("Cannot find agents: not connected")
            return []
        
        return await self.agent_discovery_manager.find_best_agents(
            required_capabilities, max_agents
        )
    
    async def request_help(self, required_capabilities: List[str], description: str,
                         timeout_minutes: int = 30, priority: int = 5,
                         tags: Optional[List[str]] = None,
                         context: Optional[Dict[str, Any]] = None) -> str:
        """
        Request help from other agents in the network.
        
        Args:
            required_capabilities: List of required capabilities
            description: Description of what help is needed
            timeout_minutes: Minutes before request expires
            priority: Request priority (1-10, lower is higher priority)
            tags: Optional tags for categorization
            context: Optional additional context information
            
        Returns:
            str: Request ID if successful, empty string if failed
        """
        if not self._is_connected or not self.help_system_manager:
            self.logger.warning("Cannot request help: not connected")
            return ""
        
        return await self.help_system_manager.request_help(
            required_capabilities, description, timeout_minutes, 
            priority, tags, context
        )
    
    async def respond_to_help(self, request_id: str, message: str,
                            capabilities_offered: List[str],
                            estimated_time_minutes: int = 30,
                            confidence_level: float = 0.8,
                            additional_info: Optional[Dict[str, Any]] = None) -> bool:
        """
        Respond to a help request from another agent.
        
        Args:
            request_id: ID of the help request to respond to
            message: Response message
            capabilities_offered: List of capabilities being offered
            estimated_time_minutes: Estimated time to complete the help
            confidence_level: Confidence in ability to help (0.0-1.0)
            additional_info: Optional additional information
            
        Returns:
            bool: True if response was sent successfully, False otherwise
        """
        if not self._is_connected or not self.help_system_manager:
            self.logger.warning("Cannot respond to help: not connected")
            return False
        
        return await self.help_system_manager.respond_to_help(
            request_id, message, capabilities_offered, 
            estimated_time_minutes, confidence_level, additional_info
        )
    
    async def select_helper(self, request_id: str, responder_id: str) -> bool:
        """
        Select a helper for one of our help requests.
        
        Args:
            request_id: ID of our help request
            responder_id: ID of the agent to select as helper
            
        Returns:
            bool: True if helper was selected successfully, False otherwise
        """
        if not self._is_connected or not self.help_system_manager:
            self.logger.warning("Cannot select helper: not connected")
            return False
        
        return await self.help_system_manager.select_helper(request_id, responder_id)
    
    async def complete_help_request(self, request_id: str, success: bool = True,
                                  completion_message: str = "") -> bool:
        """
        Mark a help request as completed or failed.
        
        Args:
            request_id: ID of the help request to complete
            success: Whether the help was successful
            completion_message: Optional completion message
            
        Returns:
            bool: True if request was completed successfully, False otherwise
        """
        if not self._is_connected or not self.help_system_manager:
            self.logger.warning("Cannot complete help request: not connected")
            return False
        
        return await self.help_system_manager.complete_help_request(
            request_id, success, completion_message
        )
    
    async def get_help_requests(self, include_expired: bool = False,
                              status_filter: Optional[List[HelpRequestStatus]] = None) -> List[HelpRequest]:
        """
        Get help requests that we've received from other agents.
        
        Args:
            include_expired: Whether to include expired requests
            status_filter: Optional list of statuses to filter by
            
        Returns:
            List of help requests matching the criteria
        """
        if not self._is_connected or not self.help_system_manager:
            self.logger.warning("Cannot get help requests: not connected")
            return []
        
        return await self.help_system_manager.get_help_requests(
            include_expired, status_filter
        )
    
    async def get_my_requests(self, include_expired: bool = False,
                            status_filter: Optional[List[HelpRequestStatus]] = None) -> List[HelpRequest]:
        """
        Get help requests that we've made.
        
        Args:
            include_expired: Whether to include expired requests
            status_filter: Optional list of statuses to filter by
            
        Returns:
            List of our help requests matching the criteria
        """
        if not self._is_connected or not self.help_system_manager:
            self.logger.warning("Cannot get my requests: not connected")
            return []
        
        return await self.help_system_manager.get_my_requests(
            include_expired, status_filter
        )
    
    def register_message_handler(self, message_type: MessageType,
                               handler: Callable[[BeastModeMessage], Awaitable[None]],
                               agent_filter: Optional[str] = None) -> str:
        """
        Register a message handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async function to handle the message
            agent_filter: Optional filter by source agent ID
            
        Returns:
            str: Handler ID for later removal
        """
        handler_id = str(uuid.uuid4())
        
        message_handler = MessageHandler(
            message_type=message_type,
            handler=handler,
            agent_filter=agent_filter
        )
        
        self._message_handlers[handler_id] = message_handler
        
        self.logger.debug(f"Registered message handler for {message_type.value}")
        return handler_id
    
    def unregister_message_handler(self, handler_id: str) -> bool:
        """
        Unregister a message handler.
        
        Args:
            handler_id: ID of the handler to remove
            
        Returns:
            bool: True if handler was removed, False if not found
        """
        if handler_id in self._message_handlers:
            del self._message_handlers[handler_id]
            self.logger.debug(f"Unregistered message handler: {handler_id}")
            return True
        
        return False
    
    async def get_network_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive network statistics.
        
        Returns:
            Dictionary containing network statistics
        """
        stats = {
            "agent_id": self.agent_id,
            "is_connected": self._is_connected,
            "is_listening": self._is_listening,
            "registered_handlers": len(self._message_handlers),
            "capabilities": self.capabilities.to_dict()
        }
        
        if self._is_connected and self.agent_discovery_manager:
            discovery_stats = await self.agent_discovery_manager.get_network_stats()
            stats["discovery"] = discovery_stats
        
        if self._is_connected and self.help_system_manager:
            help_stats = await self.help_system_manager.get_help_system_stats()
            stats["help_system"] = help_stats
        
        return stats
    
    async def _handle_message(self, channel: str, message: str) -> None:
        """
        Handle incoming messages from the network.
        
        Args:
            channel: Redis channel the message came from
            message: JSON message content
        """
        try:
            # Deserialize message
            beast_message = MessageSerializer.deserialize(message)
            
            # Skip our own messages
            if beast_message.source == self.agent_id:
                return
            
            # Handle system messages first
            if beast_message.type in [MessageType.HELP_WANTED, MessageType.HELP_RESPONSE, MessageType.TECHNICAL_EXCHANGE]:
                if self.help_system_manager:
                    await self.help_system_manager.handle_help_message(beast_message)
            
            # Handle discovery messages
            elif beast_message.type in [MessageType.AGENT_DISCOVERY, MessageType.AGENT_RESPONSE]:
                # These are handled by the agent discovery manager automatically
                pass
            
            # Handle system health checks
            elif beast_message.type == MessageType.SYSTEM_HEALTH:
                if self.auto_respond_to_health_checks:
                    await self._handle_health_check(beast_message)
            
            # Route to registered handlers
            await self._route_to_handlers(beast_message)
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    async def _route_to_handlers(self, message: BeastModeMessage) -> None:
        """Route message to registered handlers."""
        for handler_id, message_handler in self._message_handlers.items():
            try:
                # Check message type match
                if message_handler.message_type != message.type:
                    continue
                
                # Check agent filter
                if message_handler.agent_filter and message_handler.agent_filter != message.source:
                    continue
                
                # Call handler
                await message_handler.handler(message)
                
            except Exception as e:
                self.logger.error(f"Error in message handler {handler_id}: {e}")
    
    async def _handle_health_check(self, message: BeastModeMessage) -> None:
        """Handle system health check messages."""
        try:
            payload = message.payload
            request_type = payload.get("request_type")
            
            if request_type == "availability_check":
                # Respond with our current status
                response_message = BeastModeMessage(
                    type=MessageType.AGENT_RESPONSE,
                    source=self.agent_id,
                    target=message.source,
                    payload={
                        "response_type": "availability_response",
                        "status": "online",
                        "capabilities": self.capabilities.capabilities,
                        "specializations": self.capabilities.specializations,
                        "timestamp": datetime.now().isoformat()
                    },
                    priority=3
                )
                
                await self.send_message(response_message)
                
        except Exception as e:
            self.logger.error(f"Error handling health check: {e}")
    
    async def _start_listening(self) -> None:
        """Start the message listening loop."""
        if self._is_listening:
            return
        
        self._is_listening = True
        self._listen_task = asyncio.create_task(self._listen_loop())
        self.logger.debug("Started message listening")
    
    async def _stop_listening(self) -> None:
        """Stop the message listening loop."""
        if not self._is_listening:
            return
        
        self._is_listening = False
        
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            self._listen_task = None
        
        self.logger.debug("Stopped message listening")
    
    async def _listen_loop(self) -> None:
        """Background loop for processing messages."""
        while self._is_listening:
            try:
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
                # The actual message handling is done through Redis pub/sub callbacks
                # This loop just keeps the listening active
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in listen loop: {e}")
                await asyncio.sleep(1)  # Brief pause before continuing
    
    async def _cleanup(self) -> None:
        """Clean up all resources."""
        try:
            if self.help_system_manager:
                await self.help_system_manager.stop()
                self.help_system_manager = None
            
            if self.agent_discovery_manager:
                await self.agent_discovery_manager.stop()
                self.agent_discovery_manager = None
            
            await self.redis_manager.disconnect()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Convenience functions
async def create_bus_client(agent_id: str, capabilities: List[str],
                          specializations: Optional[List[str]] = None,
                          description: str = "",
                          redis_url: str = "redis://localhost:6379",
                          channel_name: str = "beast_mode_network") -> BeastModeBusClient:
    """
    Create and connect a bus client.
    
    Args:
        agent_id: Unique identifier for this agent
        capabilities: List of agent capabilities
        specializations: Optional list of specializations
        description: Description of the agent
        redis_url: Redis connection URL
        channel_name: Redis channel for network communication
        
    Returns:
        Connected BeastModeBusClient instance
    """
    client = BeastModeBusClient(
        agent_id=agent_id,
        capabilities=capabilities,
        specializations=specializations,
        description=description,
        redis_url=redis_url,
        channel_name=channel_name
    )
    
    await client.connect()
    return client