"""
Agent Discovery and Registry System for Beast Mode Agent Network.

This module provides agent discovery, registration, capability indexing,
trust scoring, and availability monitoring for the distributed agent network.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict
import math

from .message_models import AgentCapabilities, MessageType


class AgentStatus(str, Enum):
    """Agent availability status enumeration."""
    ONLINE = "online"
    BUSY = "busy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass
class DiscoveredAgent:
    """
    Represents a discovered agent in the network with trust scoring and availability tracking.
    
    This dataclass stores comprehensive information about agents including their capabilities,
    trust metrics, collaboration history, and availability status.
    """
    
    agent_id: str
    capabilities: List[str] = field(default_factory=list)
    specializations: List[str] = field(default_factory=list)
    availability: AgentStatus = AgentStatus.UNKNOWN
    last_seen: datetime = field(default_factory=datetime.now)
    collaboration_history: List[str] = field(default_factory=list)
    trust_score: float = 0.5
    response_count: int = 0
    success_count: int = 0
    description: str = ""
    version: str = "1.0.0"
    max_concurrent_tasks: int = 5
    supported_message_types: List[MessageType] = field(default_factory=list)
    
    # Trust scoring fields
    total_interactions: int = 0
    successful_interactions: int = 0
    failed_interactions: int = 0
    average_response_time: float = 0.0
    last_interaction: Optional[datetime] = None
    trust_decay_factor: float = 0.95  # Daily decay factor for trust score
    
    def __post_init__(self):
        """Validate and normalize agent data after initialization."""
        if not self.agent_id:
            raise ValueError("agent_id cannot be empty")
        
        # Normalize capabilities and specializations
        self.capabilities = [cap.lower().strip() for cap in self.capabilities if cap.strip()]
        self.specializations = [spec.lower().strip() for spec in self.specializations if spec.strip()]
        
        # Ensure trust score is within bounds
        self.trust_score = max(0.0, min(1.0, self.trust_score))
        
        # Validate counts
        self.response_count = max(0, self.response_count)
        self.success_count = max(0, min(self.response_count, self.success_count))
        self.total_interactions = max(0, self.total_interactions)
        self.successful_interactions = max(0, min(self.total_interactions, self.successful_interactions))
        self.failed_interactions = max(0, self.failed_interactions)
        
        # Ensure average response time is non-negative
        self.average_response_time = max(0.0, self.average_response_time)
    
    def is_available(self, timeout_minutes: int = 5) -> bool:
        """
        Check if agent is considered available based on last seen time.
        
        Args:
            timeout_minutes: Minutes after which agent is considered offline
            
        Returns:
            bool: True if agent is available, False otherwise
        """
        if self.availability == AgentStatus.OFFLINE:
            return False
        
        time_since_last_seen = datetime.now() - self.last_seen
        return time_since_last_seen.total_seconds() < (timeout_minutes * 60)
    
    def has_capability(self, capability: str) -> bool:
        """
        Check if agent has a specific capability.
        
        Args:
            capability: Capability to check for
            
        Returns:
            bool: True if agent has the capability
        """
        return capability.lower().strip() in self.capabilities
    
    def has_capabilities(self, required_capabilities: List[str]) -> bool:
        """
        Check if agent has all required capabilities.
        
        Args:
            required_capabilities: List of required capabilities
            
        Returns:
            bool: True if agent has all required capabilities
        """
        if not required_capabilities:
            return True
        
        agent_caps = set(self.capabilities)
        required_caps = set(cap.lower().strip() for cap in required_capabilities)
        return required_caps.issubset(agent_caps)
    
    def calculate_capability_match_score(self, required_capabilities: List[str]) -> float:
        """
        Calculate how well this agent matches the required capabilities.
        
        Args:
            required_capabilities: List of required capabilities
            
        Returns:
            float: Match score between 0.0 and 1.2 (with bonus)
        """
        if not required_capabilities:
            return 1.0
        
        agent_caps = set(self.capabilities)
        required_caps = set(cap.lower().strip() for cap in required_capabilities)
        
        if not required_caps:
            return 1.0
        
        # Calculate intersection and match percentage
        matching_caps = agent_caps.intersection(required_caps)
        match_score = len(matching_caps) / len(required_caps)
        
        # Bonus for having additional relevant capabilities
        bonus_caps = agent_caps - required_caps
        bonus_score = min(0.2, len(bonus_caps) * 0.05)  # Max 20% bonus
        
        return min(1.2, match_score + bonus_score)
    
    def update_trust_score(self, success: bool, response_time: Optional[float] = None) -> None:
        """
        Update trust score based on interaction outcome.
        
        Args:
            success: Whether the interaction was successful
            response_time: Response time in seconds (optional)
        """
        self.total_interactions += 1
        self.last_interaction = datetime.now()
        
        if success:
            self.successful_interactions += 1
            self.success_count += 1
        else:
            self.failed_interactions += 1
        
        self.response_count += 1
        
        # Update average response time
        if response_time is not None and response_time > 0:
            if self.average_response_time == 0.0:
                self.average_response_time = response_time
            else:
                # Weighted average with more weight on recent interactions
                weight = 0.3
                self.average_response_time = (
                    (1 - weight) * self.average_response_time + 
                    weight * response_time
                )
        
        # Calculate new trust score using weighted success rate
        if self.total_interactions > 0:
            base_success_rate = self.successful_interactions / self.total_interactions
            
            # Apply time decay for older interactions
            time_factor = self._calculate_time_decay_factor()
            
            # Response time factor (faster responses get slight bonus)
            response_factor = self._calculate_response_time_factor()
            
            # Calculate weighted trust score
            self.trust_score = min(1.0, max(0.0, 
                base_success_rate * time_factor * response_factor
            ))
    
    def apply_time_decay(self) -> None:
        """Apply time-based decay to trust score to account for agent inactivity."""
        if self.last_interaction is None:
            return
        
        days_since_interaction = (datetime.now() - self.last_interaction).days
        if days_since_interaction > 0:
            decay_factor = self.trust_decay_factor ** days_since_interaction
            self.trust_score *= decay_factor
            self.trust_score = max(0.0, min(1.0, self.trust_score))
    
    def _calculate_time_decay_factor(self) -> float:
        """Calculate time decay factor based on last interaction."""
        if self.last_interaction is None:
            return 1.0
        
        days_since = (datetime.now() - self.last_interaction).days
        if days_since <= 1:
            return 1.0
        
        # Gradual decay over time
        return max(0.5, self.trust_decay_factor ** days_since)
    
    def _calculate_response_time_factor(self) -> float:
        """Calculate response time factor for trust scoring."""
        if self.average_response_time <= 0:
            return 1.0
        
        # Optimal response time is around 5 seconds
        optimal_time = 5.0
        if self.average_response_time <= optimal_time:
            return 1.0 + (optimal_time - self.average_response_time) * 0.01  # Small bonus
        else:
            # Penalty for slow responses, but not too harsh
            penalty = min(0.2, (self.average_response_time - optimal_time) * 0.005)
            return max(0.8, 1.0 - penalty)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "specializations": self.specializations,
            "availability": self.availability.value,
            "last_seen": self.last_seen.isoformat(),
            "trust_score": self.trust_score,
            "response_count": self.response_count,
            "success_count": self.success_count,
            "description": self.description,
            "version": self.version,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "total_interactions": self.total_interactions,
            "successful_interactions": self.successful_interactions,
            "average_response_time": self.average_response_time
        }


class AgentRegistry:
    """
    Registry for managing discovered agents with capability indexing and trust scoring.
    
    This class provides thread-safe operations for agent registration, discovery,
    capability-based search, and trust score management.
    """
    
    def __init__(self, availability_timeout_minutes: int = 5):
        """
        Initialize the agent registry.
        
        Args:
            availability_timeout_minutes: Minutes after which agents are considered offline
        """
        self.logger = logging.getLogger(__name__)
        self.availability_timeout_minutes = availability_timeout_minutes
        
        # Thread-safe storage
        self._agents: Dict[str, DiscoveredAgent] = {}
        self._capability_index: Dict[str, Set[str]] = defaultdict(set)
        self._specialization_index: Dict[str, Set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()
        
        # Monitoring
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_shutting_down = False
        
        self.logger.info(f"AgentRegistry initialized with {availability_timeout_minutes}min timeout")
    
    async def start_monitoring(self) -> None:
        """Start background monitoring tasks."""
        if self._cleanup_task and not self._cleanup_task.done():
            return
        
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.logger.info("Started agent registry monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop background monitoring tasks."""
        self._is_shutting_down = True
        
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
        
        self.logger.info("Stopped agent registry monitoring")
    
    async def register_agent(self, capabilities: AgentCapabilities) -> bool:
        """
        Register an agent with the registry.
        
        Args:
            capabilities: Agent capabilities to register
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        async with self._lock:
            try:
                agent_id = capabilities.agent_id
                
                # Check if agent already exists
                if agent_id in self._agents:
                    # Update existing agent
                    existing_agent = self._agents[agent_id]
                    existing_agent.capabilities = capabilities.capabilities
                    existing_agent.specializations = capabilities.specializations
                    existing_agent.description = capabilities.description
                    existing_agent.version = capabilities.version
                    existing_agent.max_concurrent_tasks = capabilities.max_concurrent_tasks
                    existing_agent.supported_message_types = capabilities.supported_message_types
                    existing_agent.last_seen = datetime.now()
                    existing_agent.availability = AgentStatus.ONLINE
                    
                    self.logger.info(f"Updated existing agent: {agent_id}")
                else:
                    # Create new agent
                    agent = DiscoveredAgent(
                        agent_id=agent_id,
                        capabilities=capabilities.capabilities,
                        specializations=capabilities.specializations,
                        description=capabilities.description,
                        version=capabilities.version,
                        max_concurrent_tasks=capabilities.max_concurrent_tasks,
                        supported_message_types=capabilities.supported_message_types,
                        availability=AgentStatus.ONLINE,
                        last_seen=datetime.now()
                    )
                    
                    self._agents[agent_id] = agent
                    self.logger.info(f"Registered new agent: {agent_id}")
                
                # Update indexes
                await self._update_indexes(agent_id)
                
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to register agent {capabilities.agent_id}: {e}")
                return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_id: ID of agent to unregister
            
        Returns:
            bool: True if unregistration successful, False otherwise
        """
        async with self._lock:
            try:
                if agent_id not in self._agents:
                    self.logger.warning(f"Attempted to unregister unknown agent: {agent_id}")
                    return False
                
                agent = self._agents[agent_id]
                
                # Remove from indexes
                for capability in agent.capabilities:
                    self._capability_index[capability].discard(agent_id)
                    if not self._capability_index[capability]:
                        del self._capability_index[capability]
                
                for specialization in agent.specializations:
                    self._specialization_index[specialization].discard(agent_id)
                    if not self._specialization_index[specialization]:
                        del self._specialization_index[specialization]
                
                # Remove agent
                del self._agents[agent_id]
                
                self.logger.info(f"Unregistered agent: {agent_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to unregister agent {agent_id}: {e}")
                return False
    
    async def update_agent_availability(self, agent_id: str, status: AgentStatus) -> bool:
        """
        Update an agent's availability status.
        
        Args:
            agent_id: ID of agent to update
            status: New availability status
            
        Returns:
            bool: True if update successful, False otherwise
        """
        async with self._lock:
            try:
                if agent_id not in self._agents:
                    self.logger.warning(f"Attempted to update unknown agent: {agent_id}")
                    return False
                
                agent = self._agents[agent_id]
                agent.availability = status
                agent.last_seen = datetime.now()
                
                self.logger.debug(f"Updated agent {agent_id} availability to {status.value}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update agent {agent_id} availability: {e}")
                return False
    
    async def find_agents_by_capabilities(self, required_capabilities: List[str], 
                                        include_offline: bool = False) -> List[DiscoveredAgent]:
        """
        Find agents that have the required capabilities.
        
        Args:
            required_capabilities: List of required capabilities
            include_offline: Whether to include offline agents
            
        Returns:
            List of matching agents sorted by capability match score and trust score
        """
        async with self._lock:
            try:
                if not required_capabilities:
                    return await self.get_available_agents(include_offline)
                
                # Find agents with matching capabilities
                candidate_agents = set()
                for capability in required_capabilities:
                    capability = capability.lower().strip()
                    if capability in self._capability_index:
                        candidate_agents.update(self._capability_index[capability])
                
                # Filter and score agents
                matching_agents = []
                for agent_id in candidate_agents:
                    if agent_id not in self._agents:
                        continue
                    
                    agent = self._agents[agent_id]
                    
                    # Check availability
                    if not include_offline and not agent.is_available(self.availability_timeout_minutes):
                        continue
                    
                    # Check if agent has all required capabilities
                    if agent.has_capabilities(required_capabilities):
                        matching_agents.append(agent)
                
                # Sort by capability match score and trust score
                matching_agents.sort(
                    key=lambda a: (
                        a.calculate_capability_match_score(required_capabilities),
                        a.trust_score,
                        -a.average_response_time if a.average_response_time > 0 else 0
                    ),
                    reverse=True
                )
                
                self.logger.debug(f"Found {len(matching_agents)} agents matching capabilities: {required_capabilities}")
                return matching_agents
                
            except Exception as e:
                self.logger.error(f"Failed to find agents by capabilities: {e}")
                return []
    
    async def get_available_agents(self, include_offline: bool = False) -> List[DiscoveredAgent]:
        """
        Get all available agents.
        
        Args:
            include_offline: Whether to include offline agents
            
        Returns:
            List of available agents sorted by trust score
        """
        async with self._lock:
            try:
                available_agents = []
                
                for agent in self._agents.values():
                    if include_offline or agent.is_available(self.availability_timeout_minutes):
                        available_agents.append(agent)
                
                # Sort by trust score
                available_agents.sort(key=lambda a: a.trust_score, reverse=True)
                
                self.logger.debug(f"Found {len(available_agents)} available agents")
                return available_agents
                
            except Exception as e:
                self.logger.error(f"Failed to get available agents: {e}")
                return []
    
    async def get_agent(self, agent_id: str) -> Optional[DiscoveredAgent]:
        """
        Get a specific agent by ID.
        
        Args:
            agent_id: ID of agent to retrieve
            
        Returns:
            DiscoveredAgent if found, None otherwise
        """
        async with self._lock:
            return self._agents.get(agent_id)
    
    async def update_agent_trust(self, agent_id: str, success: bool, 
                               response_time: Optional[float] = None) -> bool:
        """
        Update an agent's trust score based on interaction outcome.
        
        Args:
            agent_id: ID of agent to update
            success: Whether the interaction was successful
            response_time: Response time in seconds (optional)
            
        Returns:
            bool: True if update successful, False otherwise
        """
        async with self._lock:
            try:
                if agent_id not in self._agents:
                    self.logger.warning(f"Attempted to update trust for unknown agent: {agent_id}")
                    return False
                
                agent = self._agents[agent_id]
                old_trust_score = agent.trust_score
                
                agent.update_trust_score(success, response_time)
                
                self.logger.debug(
                    f"Updated trust score for {agent_id}: {old_trust_score:.3f} -> {agent.trust_score:.3f} "
                    f"(success: {success})"
                )
                
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update trust for agent {agent_id}: {e}")
                return False
    
    async def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary containing registry statistics
        """
        async with self._lock:
            try:
                total_agents = len(self._agents)
                online_agents = sum(1 for agent in self._agents.values() 
                                  if agent.is_available(self.availability_timeout_minutes))
                
                # Calculate average trust score
                if total_agents > 0:
                    avg_trust = sum(agent.trust_score for agent in self._agents.values()) / total_agents
                else:
                    avg_trust = 0.0
                
                # Get capability distribution
                capability_counts = {cap: len(agents) for cap, agents in self._capability_index.items()}
                
                return {
                    "total_agents": total_agents,
                    "online_agents": online_agents,
                    "offline_agents": total_agents - online_agents,
                    "average_trust_score": avg_trust,
                    "total_capabilities": len(self._capability_index),
                    "capability_distribution": capability_counts,
                    "availability_timeout_minutes": self.availability_timeout_minutes
                }
                
            except Exception as e:
                self.logger.error(f"Failed to get registry stats: {e}")
                return {}
    
    async def _update_indexes(self, agent_id: str) -> None:
        """Update capability and specialization indexes for an agent."""
        if agent_id not in self._agents:
            return
        
        agent = self._agents[agent_id]
        
        # Update capability index
        for capability in agent.capabilities:
            self._capability_index[capability].add(agent_id)
        
        # Update specialization index
        for specialization in agent.specializations:
            self._specialization_index[specialization].add(agent_id)
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop for offline agents and trust decay."""
        while not self._is_shutting_down:
            try:
                await asyncio.sleep(60)  # Run cleanup every minute
                
                async with self._lock:
                    current_time = datetime.now()
                    agents_to_remove = []
                    
                    for agent_id, agent in self._agents.items():
                        # Apply time decay to trust scores
                        agent.apply_time_decay()
                        
                        # Check if agent should be marked as offline
                        time_since_last_seen = current_time - agent.last_seen
                        if time_since_last_seen.total_seconds() > (self.availability_timeout_minutes * 60):
                            if agent.availability != AgentStatus.OFFLINE:
                                agent.availability = AgentStatus.OFFLINE
                                self.logger.debug(f"Marked agent {agent_id} as offline")
                        
                        # Remove agents that have been offline for too long (24 hours)
                        if (agent.availability == AgentStatus.OFFLINE and 
                            time_since_last_seen.total_seconds() > (24 * 60 * 60)):
                            agents_to_remove.append(agent_id)
                    
                    # Remove old offline agents
                    for agent_id in agents_to_remove:
                        await self.unregister_agent(agent_id)
                        self.logger.info(f"Removed old offline agent: {agent_id}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(5)  # Brief pause before continuing
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_monitoring()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_monitoring()


class AgentDiscoveryManager:
    """
    Manager for coordinating agent discovery and network communication.
    
    This class provides high-level coordination for agent discovery, announcement,
    capability matching, and integration with Redis messaging infrastructure.
    """
    
    def __init__(self, redis_manager, agent_id: str, capabilities: AgentCapabilities,
                 channel_name: str = "beast_mode_network", availability_timeout_minutes: int = 5):
        """
        Initialize the agent discovery manager.
        
        Args:
            redis_manager: RedisConnectionManager instance
            agent_id: Unique identifier for this agent
            capabilities: Agent capabilities to announce
            channel_name: Redis channel for agent communication
            availability_timeout_minutes: Minutes after which agents are considered offline
        """
        self.logger = logging.getLogger(__name__)
        self.redis_manager = redis_manager
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.channel_name = channel_name
        
        # Initialize registry
        self.registry = AgentRegistry(availability_timeout_minutes)
        
        # Discovery state
        self._is_running = False
        self._announcement_task: Optional[asyncio.Task] = None
        self._discovery_task: Optional[asyncio.Task] = None
        self._message_handlers: Dict[str, Callable] = {}
        
        # Thread safety
        self._discovery_lock = asyncio.Lock()
        
        # Configuration
        self.announcement_interval = 30.0  # seconds
        self.discovery_scan_interval = 60.0  # seconds
        
        self.logger.info(f"AgentDiscoveryManager initialized for agent {agent_id}")
    
    async def start(self) -> bool:
        """
        Start the agent discovery manager.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        async with self._discovery_lock:
            if self._is_running:
                self.logger.warning("Agent discovery manager is already running")
                return True
            
            try:
                # Start the registry monitoring
                await self.registry.start_monitoring()
                
                # Register ourselves in the registry
                await self.registry.register_agent(self.capabilities)
                
                # Subscribe to the discovery channel
                success = await self.redis_manager.subscribe_to_channel(
                    self.channel_name, 
                    self._handle_discovery_message
                )
                
                if not success:
                    self.logger.error("Failed to subscribe to discovery channel")
                    return False
                
                # Start announcement and discovery tasks
                self._announcement_task = asyncio.create_task(self._announcement_loop())
                self._discovery_task = asyncio.create_task(self._discovery_scan_loop())
                
                self._is_running = True
                
                # Send initial announcement
                await self.announce_presence()
                
                self.logger.info("Agent discovery manager started successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to start agent discovery manager: {e}")
                await self._cleanup()
                return False
    
    async def stop(self) -> None:
        """Stop the agent discovery manager."""
        async with self._discovery_lock:
            if not self._is_running:
                return
            
            self._is_running = False
            
            # Cancel tasks
            if self._announcement_task and not self._announcement_task.done():
                self._announcement_task.cancel()
                try:
                    await self._announcement_task
                except asyncio.CancelledError:
                    pass
                self._announcement_task = None
            
            if self._discovery_task and not self._discovery_task.done():
                self._discovery_task.cancel()
                try:
                    await self._discovery_task
                except asyncio.CancelledError:
                    pass
                self._discovery_task = None
            
            # Stop registry monitoring
            await self.registry.stop_monitoring()
            
            self.logger.info("Agent discovery manager stopped")
    
    async def announce_presence(self) -> bool:
        """
        Announce this agent's presence to the network.
        
        Returns:
            bool: True if announcement was successful, False otherwise
        """
        try:
            from .message_models import create_agent_discovery_message, MessageSerializer
            
            # Create discovery message
            discovery_message = create_agent_discovery_message(self.capabilities)
            
            # Serialize and publish
            message_json = MessageSerializer.serialize(discovery_message)
            success = await self.redis_manager.publish(self.channel_name, message_json)
            
            if success:
                self.logger.debug(f"Announced presence for agent {self.agent_id}")
            else:
                self.logger.warning(f"Failed to announce presence for agent {self.agent_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error announcing presence: {e}")
            return False
    
    async def discover_agents(self, required_capabilities: Optional[List[str]] = None,
                            include_offline: bool = False) -> List[DiscoveredAgent]:
        """
        Discover agents in the network, optionally filtered by capabilities.
        
        Args:
            required_capabilities: Optional list of required capabilities
            include_offline: Whether to include offline agents
            
        Returns:
            List of discovered agents matching the criteria
        """
        try:
            if required_capabilities:
                agents = await self.registry.find_agents_by_capabilities(
                    required_capabilities, include_offline
                )
            else:
                agents = await self.registry.get_available_agents(include_offline)
            
            # Filter out ourselves
            agents = [agent for agent in agents if agent.agent_id != self.agent_id]
            
            self.logger.debug(f"Discovered {len(agents)} agents")
            return agents
            
        except Exception as e:
            self.logger.error(f"Error discovering agents: {e}")
            return []
    
    async def find_best_agents(self, required_capabilities: List[str], 
                             max_agents: int = 5) -> List[Tuple[DiscoveredAgent, float]]:
        """
        Find the best agents for specific capabilities with scoring.
        
        Args:
            required_capabilities: List of required capabilities
            max_agents: Maximum number of agents to return
            
        Returns:
            List of tuples (agent, combined_score) sorted by score descending
        """
        try:
            agents = await self.discover_agents(required_capabilities)
            
            # Calculate combined scores
            scored_agents = []
            for agent in agents:
                capability_score = agent.calculate_capability_match_score(required_capabilities)
                trust_score = agent.trust_score
                availability_bonus = 1.0 if agent.is_available() else 0.5
                
                # Combined score: capability match (60%) + trust (30%) + availability (10%)
                combined_score = (
                    capability_score * 0.6 + 
                    trust_score * 0.3 + 
                    availability_bonus * 0.1
                )
                
                scored_agents.append((agent, combined_score))
            
            # Sort by combined score and limit results
            scored_agents.sort(key=lambda x: x[1], reverse=True)
            result = scored_agents[:max_agents]
            
            self.logger.debug(f"Found {len(result)} best agents for capabilities: {required_capabilities}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error finding best agents: {e}")
            return []
    
    async def track_agent_interaction(self, agent_id: str, success: bool, 
                                    response_time: Optional[float] = None) -> bool:
        """
        Track an interaction with another agent for trust scoring.
        
        Args:
            agent_id: ID of the agent that was interacted with
            success: Whether the interaction was successful
            response_time: Response time in seconds (optional)
            
        Returns:
            bool: True if tracking was successful, False otherwise
        """
        try:
            return await self.registry.update_agent_trust(agent_id, success, response_time)
        except Exception as e:
            self.logger.error(f"Error tracking agent interaction: {e}")
            return False
    
    async def get_network_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the agent network.
        
        Returns:
            Dictionary containing network statistics
        """
        try:
            registry_stats = await self.registry.get_registry_stats()
            
            # Add discovery manager specific stats
            stats = {
                **registry_stats,
                "discovery_manager": {
                    "agent_id": self.agent_id,
                    "is_running": self._is_running,
                    "channel_name": self.channel_name,
                    "announcement_interval": self.announcement_interval,
                    "discovery_scan_interval": self.discovery_scan_interval
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting network stats: {e}")
            return {}
    
    async def _handle_discovery_message(self, channel: str, message: str) -> None:
        """
        Handle incoming discovery messages from other agents.
        
        Args:
            channel: Redis channel the message came from
            message: JSON message content
        """
        try:
            from .message_models import MessageSerializer, MessageType, AgentCapabilities
            
            # Deserialize message
            beast_message = MessageSerializer.deserialize(message)
            
            # Skip our own messages
            if beast_message.source == self.agent_id:
                return
            
            # Handle different message types
            if beast_message.type == MessageType.AGENT_DISCOVERY:
                await self._handle_agent_discovery(beast_message)
            elif beast_message.type == MessageType.AGENT_RESPONSE:
                await self._handle_agent_response(beast_message)
            else:
                # Forward to registered message handlers
                handler_key = f"{beast_message.type.value}_{beast_message.source}"
                if handler_key in self._message_handlers:
                    await self._message_handlers[handler_key](beast_message)
                
        except Exception as e:
            self.logger.error(f"Error handling discovery message: {e}")
    
    async def _handle_agent_discovery(self, message) -> None:
        """Handle agent discovery messages."""
        try:
            payload = message.payload
            
            # Create AgentCapabilities from message payload
            capabilities = AgentCapabilities(
                agent_id=message.source,
                capabilities=payload.get("capabilities", []),
                specializations=payload.get("specializations", []),
                description=payload.get("description", ""),
                version=payload.get("version", "1.0.0"),
                max_concurrent_tasks=payload.get("max_concurrent_tasks", 5),
                supported_message_types=payload.get("supported_message_types", [])
            )
            
            # Register the agent
            await self.registry.register_agent(capabilities)
            
            self.logger.debug(f"Processed discovery message from agent {message.source}")
            
        except Exception as e:
            self.logger.error(f"Error handling agent discovery: {e}")
    
    async def _handle_agent_response(self, message) -> None:
        """Handle agent response messages."""
        try:
            # Update agent availability
            await self.registry.update_agent_availability(
                message.source, 
                AgentStatus.ONLINE
            )
            
            self.logger.debug(f"Processed response from agent {message.source}")
            
        except Exception as e:
            self.logger.error(f"Error handling agent response: {e}")
    
    async def _announcement_loop(self) -> None:
        """Background loop for periodic presence announcements."""
        while self._is_running:
            try:
                await asyncio.sleep(self.announcement_interval)
                
                if self._is_running:
                    await self.announce_presence()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in announcement loop: {e}")
                await asyncio.sleep(5)  # Brief pause before continuing
    
    async def _discovery_scan_loop(self) -> None:
        """Background loop for periodic discovery scans and cleanup."""
        while self._is_running:
            try:
                await asyncio.sleep(self.discovery_scan_interval)
                
                if self._is_running:
                    # Trigger a discovery scan by requesting agent responses
                    await self._request_agent_responses()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in discovery scan loop: {e}")
                await asyncio.sleep(5)  # Brief pause before continuing
    
    async def _request_agent_responses(self) -> None:
        """Request responses from all agents to update availability."""
        try:
            from .message_models import BeastModeMessage, MessageType, MessageSerializer
            
            # Create a system health check message
            health_message = BeastModeMessage(
                type=MessageType.SYSTEM_HEALTH,
                source=self.agent_id,
                target=None,  # Broadcast
                payload={"request_type": "availability_check"},
                priority=3  # Low priority
            )
            
            # Serialize and publish
            message_json = MessageSerializer.serialize(health_message)
            await self.redis_manager.publish(self.channel_name, message_json)
            
            self.logger.debug("Requested agent responses for availability check")
            
        except Exception as e:
            self.logger.error(f"Error requesting agent responses: {e}")
    
    async def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            await self.registry.stop_monitoring()
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
async def create_agent_registry(availability_timeout_minutes: int = 5) -> AgentRegistry:
    """
    Create and start an agent registry.
    
    Args:
        availability_timeout_minutes: Minutes after which agents are considered offline
        
    Returns:
        Started AgentRegistry instance
    """
    registry = AgentRegistry(availability_timeout_minutes)
    await registry.start_monitoring()
    return registry


async def create_agent_discovery_manager(redis_manager, agent_id: str, 
                                       capabilities: AgentCapabilities,
                                       channel_name: str = "beast_mode_network") -> AgentDiscoveryManager:
    """
    Create and start an agent discovery manager.
    
    Args:
        redis_manager: RedisConnectionManager instance
        agent_id: Unique identifier for this agent
        capabilities: Agent capabilities to announce
        channel_name: Redis channel for agent communication
        
    Returns:
        Started AgentDiscoveryManager instance
    """
    manager = AgentDiscoveryManager(redis_manager, agent_id, capabilities, channel_name)
    await manager.start()
    return manager