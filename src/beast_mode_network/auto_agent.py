"""
Auto Agent for Beast Mode Agent Network.

This module provides an automated agent class that demonstrates the full
functionality of the Beast Mode Agent Network including discovery, messaging,
help requests, and collaborative workflows.
"""

import asyncio
import logging
import random
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .bus_client import BeastModeBusClient
from .message_models import BeastModeMessage, MessageType
from .help_system import HelpRequestStatus
from .agent_discovery import DiscoveredAgent


class AgentPersonality(str, Enum):
    """Agent personality types for demonstration."""
    HELPFUL = "helpful"
    CURIOUS = "curious"
    EXPERT = "expert"
    COLLABORATIVE = "collaborative"
    ANALYTICAL = "analytical"


@dataclass
class AutoAgentConfig:
    """Configuration for auto agent behavior."""
    
    # Basic settings
    agent_id: str = ""
    capabilities: List[str] = None
    specializations: List[str] = None
    description: str = ""
    personality: AgentPersonality = AgentPersonality.HELPFUL
    
    # Network settings
    redis_url: str = "redis://localhost:6379"
    channel_name: str = "beast_mode_network"
    
    # Behavior settings
    auto_respond_to_help: bool = True
    auto_request_help: bool = True
    help_response_probability: float = 0.7  # Probability of responding to help requests
    help_request_interval: int = 300  # Seconds between help requests
    discovery_interval: int = 120  # Seconds between discovery scans
    
    # Message settings
    send_periodic_messages: bool = True
    message_interval: int = 180  # Seconds between periodic messages
    max_concurrent_help_requests: int = 3
    
    def __post_init__(self):
        """Set defaults after initialization."""
        if not self.agent_id:
            self.agent_id = f"auto_agent_{uuid.uuid4().hex[:8]}"
        
        if self.capabilities is None:
            self.capabilities = ["general", "automation", "demonstration"]
        
        if self.specializations is None:
            self.specializations = ["network_testing", "collaboration"]


class AutoAgent:
    """
    Automated agent for demonstrating Beast Mode Agent Network functionality.
    
    This agent automatically participates in network activities including:
    - Discovering other agents
    - Sending periodic messages
    - Responding to help requests
    - Making help requests
    - Demonstrating collaborative workflows
    """
    
    def __init__(self, config: Optional[AutoAgentConfig] = None):
        """
        Initialize the auto agent.
        
        Args:
            config: Optional configuration for the agent
        """
        self.config = config or AutoAgentConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.config.agent_id}")
        
        # Initialize bus client
        description = self.config.description
        if not description:
            description = self._generate_description()
        
        self.bus_client = BeastModeBusClient(
            agent_id=self.config.agent_id,
            capabilities=self.config.capabilities,
            specializations=self.config.specializations,
            description=description,
            redis_url=self.config.redis_url,
            channel_name=self.config.channel_name
        )
        
        # Agent state
        self._is_running = False
        self._tasks: List[asyncio.Task] = []
        self._active_help_requests: Dict[str, datetime] = {}
        self._message_count = 0
        self._help_responses_sent = 0
        self._help_requests_made = 0
        
        # Statistics
        self._start_time: Optional[datetime] = None
        self._last_discovery: Optional[datetime] = None
        self._discovered_agents: List[str] = []
        
        self.logger.info(f"AutoAgent initialized: {self.config.agent_id}")
    
    async def start(self) -> bool:
        """
        Start the auto agent.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self._is_running:
            self.logger.warning("Auto agent is already running")
            return True
        
        try:
            # Connect to the network
            if not await self.bus_client.connect():
                self.logger.error("Failed to connect to network")
                return False
            
            # Register message handlers
            self._register_message_handlers()
            
            # Start background tasks
            self._start_background_tasks()
            
            self._is_running = True
            self._start_time = datetime.now()
            
            self.logger.info(f"Auto agent started successfully")
            
            # Send initial greeting
            await self._send_greeting()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start auto agent: {e}")
            await self._cleanup()
            return False
    
    async def stop(self) -> None:
        """Stop the auto agent."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # Cancel background tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self._tasks.clear()
        
        # Send goodbye message
        await self._send_goodbye()
        
        # Disconnect from network
        await self.bus_client.disconnect()
        
        self.logger.info("Auto agent stopped")
    
    async def demonstrate_functionality(self) -> Dict[str, Any]:
        """
        Demonstrate key functionality of the agent network.
        
        Returns:
            Dictionary containing demonstration results
        """
        if not self._is_running:
            await self.start()
        
        results = {
            "agent_id": self.config.agent_id,
            "start_time": datetime.now().isoformat(),
            "demonstrations": []
        }
        
        try:
            # 1. Agent Discovery
            self.logger.info("Demonstrating agent discovery...")
            agents = await self.bus_client.discover_agents()
            results["demonstrations"].append({
                "name": "agent_discovery",
                "success": True,
                "agents_found": len(agents),
                "agent_ids": [agent.agent_id for agent in agents]
            })
            
            # 2. Simple Message
            self.logger.info("Demonstrating simple messaging...")
            message_sent = await self.bus_client.send_simple_message(
                "Hello from auto agent demonstration!",
                None  # Broadcast
            )
            results["demonstrations"].append({
                "name": "simple_message",
                "success": message_sent,
                "message": "Broadcast greeting message"
            })
            
            # 3. Help Request (if other agents available)
            if agents:
                self.logger.info("Demonstrating help request...")
                request_id = await self.bus_client.request_help(
                    required_capabilities=["general"],
                    description="Demonstration help request from auto agent",
                    timeout_minutes=5
                )
                
                if request_id:
                    # Wait a bit for responses
                    await asyncio.sleep(10)
                    
                    # Check for responses
                    my_requests = await self.bus_client.get_my_requests()
                    demo_request = None
                    for req in my_requests:
                        if req.request_id == request_id:
                            demo_request = req
                            break
                    
                    results["demonstrations"].append({
                        "name": "help_request",
                        "success": True,
                        "request_id": request_id,
                        "responses_received": len(demo_request.responses) if demo_request else 0,
                        "status": demo_request.status.value if demo_request else "unknown"
                    })
                else:
                    results["demonstrations"].append({
                        "name": "help_request",
                        "success": False,
                        "error": "Failed to create help request"
                    })
            
            # 4. Capability Search
            self.logger.info("Demonstrating capability search...")
            best_agents = await self.bus_client.find_best_agents(
                required_capabilities=["general", "automation"],
                max_agents=3
            )
            results["demonstrations"].append({
                "name": "capability_search",
                "success": True,
                "matching_agents": len(best_agents),
                "agents": [{"agent_id": agent.agent_id, "score": score} 
                          for agent, score in best_agents]
            })
            
            # 5. Network Statistics
            self.logger.info("Demonstrating network statistics...")
            stats = await self.bus_client.get_network_stats()
            results["demonstrations"].append({
                "name": "network_statistics",
                "success": True,
                "stats": stats
            })
            
            results["end_time"] = datetime.now().isoformat()
            results["success"] = True
            
            self.logger.info("Demonstration completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during demonstration: {e}")
            results["error"] = str(e)
            results["success"] = False
        
        return results
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """
        Get current agent status and statistics.
        
        Returns:
            Dictionary containing agent status
        """
        uptime = None
        if self._start_time:
            uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            "agent_id": self.config.agent_id,
            "is_running": self._is_running,
            "uptime_seconds": uptime,
            "personality": self.config.personality.value,
            "capabilities": self.config.capabilities,
            "specializations": self.config.specializations,
            "statistics": {
                "messages_sent": self._message_count,
                "help_responses_sent": self._help_responses_sent,
                "help_requests_made": self._help_requests_made,
                "active_help_requests": len(self._active_help_requests),
                "discovered_agents": len(self._discovered_agents),
                "last_discovery": self._last_discovery.isoformat() if self._last_discovery else None
            },
            "network_stats": await self.bus_client.get_network_stats() if self._is_running else {}
        }
    
    async def send_message(self, message_text: str, target_agent: Optional[str] = None, 
                          message_type: MessageType = MessageType.SIMPLE_MESSAGE) -> bool:
        """
        Send a message to another agent or broadcast.
        
        Args:
            message_text: Text message to send
            target_agent: Optional target agent ID (None for broadcast)
            message_type: Type of message to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if not self._is_running:
            self.logger.warning("Cannot send message: agent is not running")
            return False
        
        try:
            if message_type == MessageType.SIMPLE_MESSAGE:
                success = await self.bus_client.send_simple_message(message_text, target_agent)
            else:
                # Create a custom message
                message = BeastModeMessage(
                    type=message_type,
                    source=self.config.agent_id,
                    target=target_agent,
                    payload={"message": message_text}
                )
                success = await self.bus_client.send_message(message)
            
            if success:
                self._message_count += 1
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    async def request_help(self, required_capabilities: List[str], description: str,
                          timeout_minutes: int = 30, priority: int = 5) -> str:
        """
        Request help from other agents in the network.
        
        Args:
            required_capabilities: List of required capabilities
            description: Description of what help is needed
            timeout_minutes: Minutes before request expires
            priority: Request priority (1-10, lower is higher priority)
            
        Returns:
            str: Request ID if successful, empty string if failed
        """
        if not self._is_running:
            self.logger.warning("Cannot request help: agent is not running")
            return ""
        
        try:
            request_id = await self.bus_client.request_help(
                required_capabilities=required_capabilities,
                description=description,
                timeout_minutes=timeout_minutes,
                priority=priority
            )
            
            if request_id:
                self._active_help_requests[request_id] = datetime.now()
                self._help_requests_made += 1
                self.logger.info(f"Requested help: {request_id}")
            
            return request_id
            
        except Exception as e:
            self.logger.error(f"Error requesting help: {e}")
            return ""
    
    async def discover_agents(self, required_capabilities: Optional[List[str]] = None) -> List[DiscoveredAgent]:
        """
        Discover agents in the network.
        
        Args:
            required_capabilities: Optional list of required capabilities
            
        Returns:
            List of discovered agents
        """
        if not self._is_running:
            self.logger.warning("Cannot discover agents: agent is not running")
            return []
        
        try:
            agents = await self.bus_client.discover_agents(required_capabilities)
            self._discovered_agents = [agent.agent_id for agent in agents]
            self._last_discovery = datetime.now()
            
            self.logger.info(f"Discovered {len(agents)} agents")
            return agents
            
        except Exception as e:
            self.logger.error(f"Error discovering agents: {e}")
            return []
    
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
        if not self._is_running:
            self.logger.warning("Cannot find agents: agent is not running")
            return []
        
        try:
            return await self.bus_client.find_best_agents(required_capabilities, max_agents)
            
        except Exception as e:
            self.logger.error(f"Error finding best agents: {e}")
            return []
    
    async def respond_to_help_request(self, request_id: str, message: str,
                                    capabilities_offered: List[str],
                                    estimated_time_minutes: int = 30,
                                    confidence_level: float = 0.8) -> bool:
        """
        Respond to a help request from another agent.
        
        Args:
            request_id: ID of the help request to respond to
            message: Response message
            capabilities_offered: List of capabilities being offered
            estimated_time_minutes: Estimated time to complete the help
            confidence_level: Confidence in ability to help (0.0-1.0)
            
        Returns:
            bool: True if response was sent successfully, False otherwise
        """
        if not self._is_running:
            self.logger.warning("Cannot respond to help: agent is not running")
            return False
        
        try:
            success = await self.bus_client.respond_to_help(
                request_id=request_id,
                message=message,
                capabilities_offered=capabilities_offered,
                estimated_time_minutes=estimated_time_minutes,
                confidence_level=confidence_level
            )
            
            if success:
                self._help_responses_sent += 1
                self.logger.info(f"Responded to help request: {request_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error responding to help request: {e}")
            return False
    
    def _generate_description(self) -> str:
        """Generate a description based on personality and capabilities."""
        personality_descriptions = {
            AgentPersonality.HELPFUL: "A helpful agent that loves to assist others",
            AgentPersonality.CURIOUS: "A curious agent that asks questions and explores",
            AgentPersonality.EXPERT: "An expert agent with specialized knowledge",
            AgentPersonality.COLLABORATIVE: "A collaborative agent that works well with others",
            AgentPersonality.ANALYTICAL: "An analytical agent that processes information systematically"
        }
        
        base_desc = personality_descriptions.get(
            self.config.personality, 
            "An automated agent for network demonstration"
        )
        
        if self.config.capabilities:
            cap_desc = f" with capabilities in {', '.join(self.config.capabilities[:3])}"
            return base_desc + cap_desc
        
        return base_desc
    
    def _register_message_handlers(self) -> None:
        """Register message handlers for different message types."""
        
        # Handle simple messages
        self.bus_client.register_message_handler(
            MessageType.SIMPLE_MESSAGE,
            self._handle_simple_message
        )
        
        # Handle technical exchanges
        self.bus_client.register_message_handler(
            MessageType.TECHNICAL_EXCHANGE,
            self._handle_technical_exchange
        )
        
        # Handle prompt requests
        self.bus_client.register_message_handler(
            MessageType.PROMPT_REQUEST,
            self._handle_prompt_request
        )
        
        # Handle prompt responses
        self.bus_client.register_message_handler(
            MessageType.PROMPT_RESPONSE,
            self._handle_prompt_response
        )
        
        # Handle agent discovery messages
        self.bus_client.register_message_handler(
            MessageType.AGENT_DISCOVERY,
            self._handle_agent_discovery
        )
        
        # Handle agent responses
        self.bus_client.register_message_handler(
            MessageType.AGENT_RESPONSE,
            self._handle_agent_response
        )
        
        # Handle help wanted messages
        self.bus_client.register_message_handler(
            MessageType.HELP_WANTED,
            self._handle_help_wanted
        )
        
        # Handle help responses
        self.bus_client.register_message_handler(
            MessageType.HELP_RESPONSE,
            self._handle_help_response
        )
        
        # Handle spore delivery
        self.bus_client.register_message_handler(
            MessageType.SPORE_DELIVERY,
            self._handle_spore_delivery
        )
        
        # Handle spore requests
        self.bus_client.register_message_handler(
            MessageType.SPORE_REQUEST,
            self._handle_spore_request
        )
        
        # Handle system health messages
        self.bus_client.register_message_handler(
            MessageType.SYSTEM_HEALTH,
            self._handle_system_health
        )
        
        # Handle processor responses
        self.bus_client.register_message_handler(
            MessageType.PROCESSOR_RESPONSE,
            self._handle_processor_response
        )
    
    def _start_background_tasks(self) -> None:
        """Start background tasks for automated behavior."""
        
        if self.config.send_periodic_messages:
            self._tasks.append(asyncio.create_task(self._periodic_message_task()))
        
        if self.config.auto_request_help:
            self._tasks.append(asyncio.create_task(self._periodic_help_request_task()))
        
        self._tasks.append(asyncio.create_task(self._periodic_discovery_task()))
        self._tasks.append(asyncio.create_task(self._help_request_monitor_task()))
    
    async def _periodic_message_task(self) -> None:
        """Send periodic messages to the network."""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.message_interval)
                
                if self._is_running:
                    message = self._generate_periodic_message()
                    await self.bus_client.send_simple_message(message)
                    self._message_count += 1
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic message task: {e}")
                await asyncio.sleep(10)
    
    async def _periodic_help_request_task(self) -> None:
        """Periodically make help requests to demonstrate the system."""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.help_request_interval)
                
                if (self._is_running and 
                    len(self._active_help_requests) < self.config.max_concurrent_help_requests):
                    
                    await self._make_demonstration_help_request()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in help request task: {e}")
                await asyncio.sleep(30)
    
    async def _periodic_discovery_task(self) -> None:
        """Periodically discover agents in the network."""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.discovery_interval)
                
                if self._is_running:
                    agents = await self.bus_client.discover_agents()
                    self._discovered_agents = [agent.agent_id for agent in agents]
                    self._last_discovery = datetime.now()
                    
                    self.logger.debug(f"Discovered {len(agents)} agents")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in discovery task: {e}")
                await asyncio.sleep(30)
    
    async def _help_request_monitor_task(self) -> None:
        """Monitor and respond to help requests."""
        while self._is_running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                if self._is_running and self.config.auto_respond_to_help:
                    await self._check_and_respond_to_help_requests()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in help monitor task: {e}")
                await asyncio.sleep(10)
    
    async def _handle_simple_message(self, message: BeastModeMessage) -> None:
        """Handle simple messages from other agents."""
        try:
            self.logger.info(f"Received message from {message.source}: {message.payload.get('message', '')}")
            
            # Respond based on personality
            if self.config.personality == AgentPersonality.HELPFUL:
                if random.random() < 0.3:  # 30% chance to respond
                    response = f"Thanks for the message, {message.source}! How can I help?"
                    await self.bus_client.send_simple_message(response, message.source)
                    self._message_count += 1
            
        except Exception as e:
            self.logger.error(f"Error handling simple message: {e}")
    
    async def _handle_technical_exchange(self, message: BeastModeMessage) -> None:
        """Handle technical exchange messages."""
        try:
            payload = message.payload
            exchange_type = payload.get("exchange_type", "")
            
            self.logger.info(f"Received technical exchange '{exchange_type}' from {message.source}")
            
            if exchange_type == "helper_selected":
                request_id = payload.get("request_id")
                self.logger.info(f"Selected as helper for request {request_id}")
                
                # Simulate some work and then complete
                await asyncio.sleep(random.uniform(5, 15))
                
                # Send completion notification
                completion_message = BeastModeMessage(
                    type=MessageType.TECHNICAL_EXCHANGE,
                    source=self.config.agent_id,
                    target=message.source,
                    payload={
                        "exchange_type": "work_completed",
                        "request_id": request_id,
                        "result": "Task completed successfully by auto agent",
                        "completion_time": datetime.now().isoformat()
                    }
                )
                await self.bus_client.send_message(completion_message)
            
        except Exception as e:
            self.logger.error(f"Error handling technical exchange: {e}")
    
    async def _handle_prompt_request(self, message: BeastModeMessage) -> None:
        """Handle prompt requests from other agents."""
        try:
            payload = message.payload
            prompt = payload.get("prompt", "")
            
            self.logger.info(f"Received prompt request from {message.source}: {prompt[:50]}...")
            
            # Generate a simple response based on personality
            response = self._generate_prompt_response(prompt)
            
            # Send response
            response_message = BeastModeMessage(
                type=MessageType.PROMPT_RESPONSE,
                source=self.config.agent_id,
                target=message.source,
                payload={
                    "original_prompt": prompt,
                    "response": response,
                    "confidence": random.uniform(0.6, 0.9),
                    "response_time": datetime.now().isoformat()
                }
            )
            
            await self.bus_client.send_message(response_message)
            self._message_count += 1
            
        except Exception as e:
            self.logger.error(f"Error handling prompt request: {e}")
    
    async def _handle_prompt_response(self, message: BeastModeMessage) -> None:
        """Handle prompt responses from other agents."""
        try:
            payload = message.payload
            original_prompt = payload.get("original_prompt", "")
            response = payload.get("response", "")
            confidence = payload.get("confidence", 0.0)
            
            self.logger.info(f"Received prompt response from {message.source} (confidence: {confidence:.2f})")
            self.logger.debug(f"Response: {response[:100]}...")
            
        except Exception as e:
            self.logger.error(f"Error handling prompt response: {e}")
    
    async def _handle_agent_discovery(self, message: BeastModeMessage) -> None:
        """Handle agent discovery messages."""
        try:
            payload = message.payload
            agent_id = payload.get("agent_id", message.source)
            capabilities = payload.get("capabilities", [])
            
            self.logger.info(f"Discovered agent {agent_id} with capabilities: {capabilities}")
            
            # Optionally respond with our own capabilities if this is a discovery request
            if payload.get("request_response", False):
                discovery_response = BeastModeMessage(
                    type=MessageType.AGENT_RESPONSE,
                    source=self.config.agent_id,
                    target=message.source,
                    payload={
                        "agent_id": self.config.agent_id,
                        "capabilities": self.config.capabilities,
                        "specializations": self.config.specializations,
                        "description": self.config.description or self._generate_description(),
                        "response_time": datetime.now().isoformat()
                    }
                )
                await self.bus_client.send_message(discovery_response)
            
        except Exception as e:
            self.logger.error(f"Error handling agent discovery: {e}")
    
    async def _handle_agent_response(self, message: BeastModeMessage) -> None:
        """Handle agent response messages."""
        try:
            payload = message.payload
            agent_id = payload.get("agent_id", message.source)
            capabilities = payload.get("capabilities", [])
            specializations = payload.get("specializations", [])
            
            self.logger.info(f"Received agent response from {agent_id}")
            self.logger.debug(f"Capabilities: {capabilities}, Specializations: {specializations}")
            
        except Exception as e:
            self.logger.error(f"Error handling agent response: {e}")
    
    async def _handle_help_wanted(self, message: BeastModeMessage) -> None:
        """Handle help wanted messages."""
        try:
            payload = message.payload
            request_id = payload.get("request_id", "")
            required_capabilities = payload.get("required_capabilities", [])
            description = payload.get("description", "")
            
            self.logger.info(f"Received help request {request_id} from {message.source}")
            self.logger.debug(f"Required capabilities: {required_capabilities}")
            
            # Check if we can help and respond if configured to do so
            if self.config.auto_respond_to_help and self._can_help_with_capabilities(required_capabilities):
                if random.random() < self.config.help_response_probability:
                    # Generate a help response
                    response_message = f"I can help with {description[:50]}... based on my {self.config.personality.value} nature."
                    
                    # Determine capabilities we can offer
                    our_caps = set(self.config.capabilities + self.config.specializations)
                    required_caps = set(required_capabilities)
                    offered_caps = list(our_caps.intersection(required_caps))
                    
                    if not offered_caps:
                        offered_caps = self.config.capabilities[:2]
                    
                    await self.bus_client.respond_to_help(
                        request_id=request_id,
                        message=response_message,
                        capabilities_offered=offered_caps,
                        estimated_time_minutes=random.randint(10, 60),
                        confidence_level=random.uniform(0.6, 0.9)
                    )
                    
                    self._help_responses_sent += 1
            
        except Exception as e:
            self.logger.error(f"Error handling help wanted: {e}")
    
    async def _handle_help_response(self, message: BeastModeMessage) -> None:
        """Handle help response messages."""
        try:
            payload = message.payload
            request_id = payload.get("request_id", "")
            responder_message = payload.get("message", "")
            capabilities_offered = payload.get("capabilities_offered", [])
            confidence_level = payload.get("confidence_level", 0.0)
            
            self.logger.info(f"Received help response from {message.source} for request {request_id}")
            self.logger.debug(f"Confidence: {confidence_level:.2f}, Capabilities: {capabilities_offered}")
            
        except Exception as e:
            self.logger.error(f"Error handling help response: {e}")
    
    async def _handle_spore_delivery(self, message: BeastModeMessage) -> None:
        """Handle spore delivery messages."""
        try:
            payload = message.payload
            spore_type = payload.get("spore_type", "")
            spore_data = payload.get("spore_data", {})
            
            self.logger.info(f"Received spore delivery of type '{spore_type}' from {message.source}")
            
            # Acknowledge receipt
            ack_message = BeastModeMessage(
                type=MessageType.TECHNICAL_EXCHANGE,
                source=self.config.agent_id,
                target=message.source,
                payload={
                    "exchange_type": "spore_received",
                    "spore_type": spore_type,
                    "status": "acknowledged",
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.bus_client.send_message(ack_message)
            
        except Exception as e:
            self.logger.error(f"Error handling spore delivery: {e}")
    
    async def _handle_spore_request(self, message: BeastModeMessage) -> None:
        """Handle spore request messages."""
        try:
            payload = message.payload
            requested_spore_type = payload.get("spore_type", "")
            
            self.logger.info(f"Received spore request for '{requested_spore_type}' from {message.source}")
            
            # For demonstration, we can offer a simple spore
            if requested_spore_type in ["demo", "example", "basic"]:
                spore_data = {
                    "agent_id": self.config.agent_id,
                    "capabilities": self.config.capabilities,
                    "personality": self.config.personality.value,
                    "created_at": datetime.now().isoformat(),
                    "demo_data": "This is a demonstration spore from an auto agent"
                }
                
                delivery_message = BeastModeMessage(
                    type=MessageType.SPORE_DELIVERY,
                    source=self.config.agent_id,
                    target=message.source,
                    payload={
                        "spore_type": requested_spore_type,
                        "spore_data": spore_data,
                        "delivery_time": datetime.now().isoformat()
                    }
                )
                await self.bus_client.send_message(delivery_message)
                self._message_count += 1
            
        except Exception as e:
            self.logger.error(f"Error handling spore request: {e}")
    
    async def _handle_system_health(self, message: BeastModeMessage) -> None:
        """Handle system health messages."""
        try:
            payload = message.payload
            health_check_type = payload.get("check_type", "")
            
            self.logger.info(f"Received system health check '{health_check_type}' from {message.source}")
            
            # Respond with our health status
            health_response = BeastModeMessage(
                type=MessageType.SYSTEM_HEALTH,
                source=self.config.agent_id,
                target=message.source,
                payload={
                    "check_type": "health_response",
                    "status": "healthy" if self._is_running else "stopped",
                    "uptime_seconds": (datetime.now() - self._start_time).total_seconds() if self._start_time else 0,
                    "message_count": self._message_count,
                    "help_responses_sent": self._help_responses_sent,
                    "help_requests_made": self._help_requests_made,
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.bus_client.send_message(health_response)
            
        except Exception as e:
            self.logger.error(f"Error handling system health: {e}")
    
    async def _handle_processor_response(self, message: BeastModeMessage) -> None:
        """Handle processor response messages."""
        try:
            payload = message.payload
            processor_type = payload.get("processor_type", "")
            result = payload.get("result", "")
            success = payload.get("success", True)
            
            self.logger.info(f"Received processor response from {message.source}")
            self.logger.debug(f"Processor: {processor_type}, Success: {success}")
            
        except Exception as e:
            self.logger.error(f"Error handling processor response: {e}")
    
    def _can_help_with_capabilities(self, required_capabilities: List[str]) -> bool:
        """Check if we can help with the required capabilities."""
        our_caps = set(self.config.capabilities + self.config.specializations)
        required_caps = set(required_capabilities)
        return bool(our_caps.intersection(required_caps))
    
    async def _check_and_respond_to_help_requests(self) -> None:
        """Check for help requests and respond if appropriate."""
        try:
            help_requests = await self.bus_client.get_help_requests(
                status_filter=[HelpRequestStatus.PENDING, HelpRequestStatus.RESPONDED]
            )
            
            for request in help_requests:
                # Check if we can help
                if self._can_help_with_request(request):
                    if random.random() < self.config.help_response_probability:
                        await self._respond_to_help_request(request)
                        
        except Exception as e:
            self.logger.error(f"Error checking help requests: {e}")
    
    def _can_help_with_request(self, request) -> bool:
        """Check if we can help with a specific request."""
        # Check if we have any of the required capabilities
        our_caps = set(self.config.capabilities + self.config.specializations)
        required_caps = set(request.required_capabilities)
        
        return bool(our_caps.intersection(required_caps))
    
    async def _respond_to_help_request(self, request) -> None:
        """Respond to a help request."""
        try:
            # Generate response based on personality
            message = self._generate_help_response_message(request)
            
            # Determine capabilities we can offer
            our_caps = set(self.config.capabilities + self.config.specializations)
            required_caps = set(request.required_capabilities)
            offered_caps = list(our_caps.intersection(required_caps))
            
            if not offered_caps:
                offered_caps = self.config.capabilities[:2]  # Offer some general capabilities
            
            success = await self.bus_client.respond_to_help(
                request_id=request.request_id,
                message=message,
                capabilities_offered=offered_caps,
                estimated_time_minutes=random.randint(10, 60),
                confidence_level=random.uniform(0.6, 0.9)
            )
            
            if success:
                self._help_responses_sent += 1
                self.logger.info(f"Responded to help request: {request.request_id}")
            
        except Exception as e:
            self.logger.error(f"Error responding to help request: {e}")
    
    async def _make_demonstration_help_request(self) -> None:
        """Make a demonstration help request."""
        try:
            # Generate a random help request
            capabilities = random.sample(
                ["general", "automation", "analysis", "communication", "problem_solving"],
                random.randint(1, 2)
            )
            
            descriptions = [
                "Need help with data analysis task",
                "Looking for assistance with automation script",
                "Seeking collaboration on problem solving",
                "Need support with communication strategy",
                "Looking for help with system optimization"
            ]
            
            description = random.choice(descriptions)
            
            request_id = await self.bus_client.request_help(
                required_capabilities=capabilities,
                description=f"{description} (demonstration request)",
                timeout_minutes=random.randint(15, 45),
                priority=random.randint(3, 7)
            )
            
            if request_id:
                self._active_help_requests[request_id] = datetime.now()
                self._help_requests_made += 1
                self.logger.info(f"Made demonstration help request: {request_id}")
            
        except Exception as e:
            self.logger.error(f"Error making help request: {e}")
    
    def _generate_periodic_message(self) -> str:
        """Generate a periodic message based on personality."""
        messages = {
            AgentPersonality.HELPFUL: [
                "Hello everyone! I'm here if anyone needs assistance.",
                "Just checking in - how is everyone doing?",
                "Available to help with any tasks you might have!",
                "Hope everyone is having a productive day!"
            ],
            AgentPersonality.CURIOUS: [
                "What interesting projects is everyone working on?",
                "I'm curious about what capabilities others have.",
                "Anyone discovered anything interesting lately?",
                "What challenges are you all facing today?"
            ],
            AgentPersonality.EXPERT: [
                "Sharing my expertise - feel free to ask questions.",
                "Available for technical consultations.",
                "Happy to share knowledge in my areas of specialization.",
                "Here to provide expert guidance when needed."
            ],
            AgentPersonality.COLLABORATIVE: [
                "Looking for collaboration opportunities!",
                "Anyone interested in working together on projects?",
                "Collaboration makes everything better - who's in?",
                "Let's combine our capabilities for better results!"
            ],
            AgentPersonality.ANALYTICAL: [
                "Analyzing network patterns and agent behaviors.",
                "Interesting data emerging from our interactions.",
                "Processing information and looking for insights.",
                "Statistical analysis shows positive network growth."
            ]
        }
        
        personality_messages = messages.get(self.config.personality, messages[AgentPersonality.HELPFUL])
        return random.choice(personality_messages)
    
    def _generate_help_response_message(self, request) -> str:
        """Generate a help response message based on personality."""
        base_messages = {
            AgentPersonality.HELPFUL: "I'd be happy to help you with this task!",
            AgentPersonality.CURIOUS: "This looks interesting! I'd like to learn while helping.",
            AgentPersonality.EXPERT: "I have expertise in this area and can assist.",
            AgentPersonality.COLLABORATIVE: "Let's work together on this challenge!",
            AgentPersonality.ANALYTICAL: "I can provide analytical support for this request."
        }
        
        base = base_messages.get(self.config.personality, "I can help with this request.")
        return f"{base} Request: {request.description[:50]}..."
    
    def _generate_prompt_response(self, prompt: str) -> str:
        """Generate a response to a prompt based on personality."""
        responses = {
            AgentPersonality.HELPFUL: f"I'd be glad to help with that. Regarding '{prompt[:30]}...', here's my assistance.",
            AgentPersonality.CURIOUS: f"That's an interesting question about '{prompt[:30]}...'. Let me explore this with you.",
            AgentPersonality.EXPERT: f"Based on my expertise, regarding '{prompt[:30]}...', I can provide this guidance.",
            AgentPersonality.COLLABORATIVE: f"Great question! Let's work through '{prompt[:30]}...' together.",
            AgentPersonality.ANALYTICAL: f"Analyzing your request '{prompt[:30]}...', here's my systematic response."
        }
        
        return responses.get(self.config.personality, f"Regarding '{prompt[:30]}...', here's my response.")
    
    async def _send_greeting(self) -> None:
        """Send initial greeting message."""
        greeting = f"Hello! I'm {self.config.agent_id}, a {self.config.personality.value} auto agent. Ready to collaborate!"
        await self.bus_client.send_simple_message(greeting)
        self._message_count += 1
    
    async def _send_goodbye(self) -> None:
        """Send goodbye message."""
        goodbye = f"Goodbye from {self.config.agent_id}! It was great collaborating with everyone."
        await self.bus_client.send_simple_message(goodbye)
    
    async def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            await self.bus_client.disconnect()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()


# Convenience functions
async def create_auto_agent(agent_id: Optional[str] = None,
                          capabilities: Optional[List[str]] = None,
                          personality: AgentPersonality = AgentPersonality.HELPFUL,
                          redis_url: str = "redis://localhost:6379") -> AutoAgent:
    """
    Create and start an auto agent.
    
    Args:
        agent_id: Optional agent ID (generated if not provided)
        capabilities: Optional list of capabilities
        personality: Agent personality type
        redis_url: Redis connection URL
        
    Returns:
        Started AutoAgent instance
    """
    config = AutoAgentConfig(
        agent_id=agent_id or f"auto_agent_{uuid.uuid4().hex[:8]}",
        capabilities=capabilities or ["general", "automation", "demonstration"],
        personality=personality,
        redis_url=redis_url
    )
    
    agent = AutoAgent(config)
    await agent.start()
    return agent


async def run_agent_demonstration(num_agents: int = 3, 
                                duration_minutes: int = 5,
                                redis_url: str = "redis://localhost:6379") -> Dict[str, Any]:
    """
    Run a demonstration with multiple auto agents.
    
    Args:
        num_agents: Number of agents to create
        duration_minutes: How long to run the demonstration
        redis_url: Redis connection URL
        
    Returns:
        Dictionary containing demonstration results
    """
    agents = []
    results = {
        "start_time": datetime.now().isoformat(),
        "num_agents": num_agents,
        "duration_minutes": duration_minutes,
        "agents": [],
        "success": False
    }
    
    try:
        # Create agents with different personalities
        personalities = list(AgentPersonality)
        
        for i in range(num_agents):
            personality = personalities[i % len(personalities)]
            agent_id = f"demo_agent_{i+1}"
            
            config = AutoAgentConfig(
                agent_id=agent_id,
                capabilities=["general", "demonstration", f"specialty_{i+1}"],
                personality=personality,
                redis_url=redis_url,
                help_request_interval=60,  # More frequent for demo
                message_interval=90
            )
            
            agent = AutoAgent(config)
            await agent.start()
            agents.append(agent)
            
            results["agents"].append({
                "agent_id": agent_id,
                "personality": personality.value,
                "capabilities": config.capabilities
            })
        
        # Let agents run for the specified duration
        await asyncio.sleep(duration_minutes * 60)
        
        # Collect final statistics
        for agent in agents:
            status = await agent.get_agent_status()
            for agent_result in results["agents"]:
                if agent_result["agent_id"] == agent.config.agent_id:
                    agent_result["final_stats"] = status["statistics"]
                    break
        
        results["success"] = True
        results["end_time"] = datetime.now().isoformat()
        
    except Exception as e:
        results["error"] = str(e)
        
    finally:
        # Stop all agents
        for agent in agents:
            try:
                await agent.stop()
            except Exception as e:
                logging.error(f"Error stopping agent: {e}")
    
    return results