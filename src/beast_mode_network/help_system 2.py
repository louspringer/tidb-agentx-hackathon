"""
Help Request System for Beast Mode Agent Network.

This module provides help request lifecycle management, helper selection,
response tracking, and timeout handling for collaborative problem-solving.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Callable, Awaitable
from collections import defaultdict

from .message_models import BeastModeMessage, MessageType, MessageSerializer


class HelpRequestStatus(str, Enum):
    """Help request status enumeration."""
    PENDING = "pending"
    RESPONDED = "responded"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class HelpResponse:
    """Represents a response to a help request."""
    
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    responder_id: str = ""
    request_id: str = ""
    message: str = ""
    capabilities_offered: List[str] = field(default_factory=list)
    estimated_time_minutes: int = 30
    confidence_level: float = 0.8  # 0.0 to 1.0
    response_time: datetime = field(default_factory=datetime.now)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate response data after initialization."""
        if not self.responder_id:
            raise ValueError("responder_id cannot be empty")
        if not self.request_id:
            raise ValueError("request_id cannot be empty")
        
        # Ensure confidence level is within bounds
        self.confidence_level = max(0.0, min(1.0, self.confidence_level))
        
        # Ensure estimated time is positive
        self.estimated_time_minutes = max(1, self.estimated_time_minutes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary representation."""
        return {
            "response_id": self.response_id,
            "responder_id": self.responder_id,
            "request_id": self.request_id,
            "message": self.message,
            "capabilities_offered": self.capabilities_offered,
            "estimated_time_minutes": self.estimated_time_minutes,
            "confidence_level": self.confidence_level,
            "response_time": self.response_time.isoformat(),
            "additional_info": self.additional_info
        }


@dataclass
class HelpRequest:
    """
    Represents a help request with status tracking and lifecycle management.
    
    This dataclass stores comprehensive information about help requests including
    required capabilities, responses, status transitions, and timeout handling.
    """
    
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requester_id: str = ""
    required_capabilities: List[str] = field(default_factory=list)
    description: str = ""
    status: HelpRequestStatus = HelpRequestStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    responses: List[HelpResponse] = field(default_factory=list)
    selected_responder: Optional[str] = None
    timeout_minutes: int = 30
    priority: int = 5  # 1-10, lower is higher priority
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Status tracking
    responded_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate and normalize request data after initialization."""
        if not self.requester_id:
            raise ValueError("requester_id cannot be empty")
        if not self.description.strip():
            raise ValueError("description cannot be empty")
        
        # Normalize capabilities and tags
        self.required_capabilities = [cap.lower().strip() for cap in self.required_capabilities if cap.strip()]
        self.tags = [tag.lower().strip() for tag in self.tags if tag.strip()]
        
        # Ensure timeout is reasonable
        self.timeout_minutes = max(1, min(1440, self.timeout_minutes))  # 1 minute to 24 hours
        
        # Ensure priority is within bounds
        self.priority = max(1, min(10, self.priority))
    
    def is_expired(self) -> bool:
        """
        Check if the help request has expired based on timeout.
        
        Returns:
            bool: True if request has expired, False otherwise
        """
        if self.status in [HelpRequestStatus.COMPLETED, HelpRequestStatus.FAILED, HelpRequestStatus.TIMEOUT]:
            return True
        
        time_since_creation = datetime.now() - self.created_at
        return time_since_creation.total_seconds() > (self.timeout_minutes * 60)
    
    def get_time_remaining(self) -> timedelta:
        """
        Get the time remaining before the request expires.
        
        Returns:
            timedelta: Time remaining, or zero if expired
        """
        if self.is_expired():
            return timedelta(0)
        
        expiry_time = self.created_at + timedelta(minutes=self.timeout_minutes)
        return expiry_time - datetime.now()
    
    def add_response(self, response: HelpResponse) -> bool:
        """
        Add a response to this help request.
        
        Args:
            response: HelpResponse to add
            
        Returns:
            bool: True if response was added, False if request is not accepting responses
        """
        if self.status not in [HelpRequestStatus.PENDING, HelpRequestStatus.RESPONDED]:
            return False
        
        if self.is_expired():
            return False
        
        # Check for duplicate responses from same agent
        for existing_response in self.responses:
            if existing_response.responder_id == response.responder_id:
                return False  # Agent already responded
        
        self.responses.append(response)
        
        # Update status if this is the first response
        if self.status == HelpRequestStatus.PENDING:
            self.status = HelpRequestStatus.RESPONDED
            self.responded_at = datetime.now()
        
        return True
    
    def select_helper(self, responder_id: str) -> bool:
        """
        Select a helper from the available responses.
        
        Args:
            responder_id: ID of the agent to select as helper
            
        Returns:
            bool: True if helper was selected, False otherwise
        """
        if self.status != HelpRequestStatus.RESPONDED:
            return False
        
        # Check if responder actually responded
        responder_found = False
        for response in self.responses:
            if response.responder_id == responder_id:
                responder_found = True
                break
        
        if not responder_found:
            return False
        
        self.selected_responder = responder_id
        self.status = HelpRequestStatus.IN_PROGRESS
        self.started_at = datetime.now()
        
        return True
    
    def mark_completed(self, success: bool = True) -> bool:
        """
        Mark the help request as completed or failed.
        
        Args:
            success: Whether the help was successful
            
        Returns:
            bool: True if status was updated, False otherwise
        """
        if self.status != HelpRequestStatus.IN_PROGRESS:
            return False
        
        if success:
            self.status = HelpRequestStatus.COMPLETED
            self.completed_at = datetime.now()
        else:
            self.status = HelpRequestStatus.FAILED
            self.failed_at = datetime.now()
        
        return True
    
    def mark_timeout(self) -> bool:
        """
        Mark the help request as timed out.
        
        Returns:
            bool: True if status was updated, False otherwise
        """
        if self.status in [HelpRequestStatus.COMPLETED, HelpRequestStatus.FAILED, HelpRequestStatus.TIMEOUT]:
            return False
        
        self.status = HelpRequestStatus.TIMEOUT
        self.timeout_at = datetime.now()
        
        return True
    
    def get_best_responses(self, max_responses: int = 5) -> List[HelpResponse]:
        """
        Get the best responses sorted by confidence and capability match.
        
        Args:
            max_responses: Maximum number of responses to return
            
        Returns:
            List of best responses sorted by score
        """
        if not self.responses:
            return []
        
        # Score responses based on confidence, capability match, and response time
        scored_responses = []
        
        for response in self.responses:
            # Calculate capability match score
            if self.required_capabilities:
                offered_caps = set(cap.lower().strip() for cap in response.capabilities_offered)
                required_caps = set(self.required_capabilities)
                match_score = len(offered_caps.intersection(required_caps)) / len(required_caps)
            else:
                match_score = 1.0
            
            # Calculate response time score (faster is better, but not too much weight)
            response_delay = (response.response_time - self.created_at).total_seconds()
            time_score = max(0.5, 1.0 - (response_delay / 3600))  # Decay over 1 hour
            
            # Combined score: confidence (50%) + capability match (40%) + response time (10%)
            combined_score = (
                response.confidence_level * 0.5 +
                match_score * 0.4 +
                time_score * 0.1
            )
            
            scored_responses.append((response, combined_score))
        
        # Sort by score and return top responses
        scored_responses.sort(key=lambda x: x[1], reverse=True)
        return [response for response, _ in scored_responses[:max_responses]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary representation."""
        return {
            "request_id": self.request_id,
            "requester_id": self.requester_id,
            "required_capabilities": self.required_capabilities,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "responses": [response.to_dict() for response in self.responses],
            "selected_responder": self.selected_responder,
            "timeout_minutes": self.timeout_minutes,
            "priority": self.priority,
            "tags": self.tags,
            "context": self.context,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "failed_at": self.failed_at.isoformat() if self.failed_at else None,
            "timeout_at": self.timeout_at.isoformat() if self.timeout_at else None,
            "is_expired": self.is_expired(),
            "time_remaining_seconds": self.get_time_remaining().total_seconds()
        }


class HelpSystemManager:
    """
    Manager for coordinating help requests and responses in the agent network.
    
    This class provides high-level coordination for help request lifecycle,
    helper selection, response tracking, and integration with agent discovery.
    """
    
    def __init__(self, redis_manager, agent_id: str, agent_discovery_manager,
                 channel_name: str = "beast_mode_network"):
        """
        Initialize the help system manager.
        
        Args:
            redis_manager: RedisConnectionManager instance
            agent_id: Unique identifier for this agent
            agent_discovery_manager: AgentDiscoveryManager instance
            channel_name: Redis channel for help system communication
        """
        self.logger = logging.getLogger(__name__)
        self.redis_manager = redis_manager
        self.agent_id = agent_id
        self.agent_discovery_manager = agent_discovery_manager
        self.channel_name = channel_name
        
        # Help request storage
        self._help_requests: Dict[str, HelpRequest] = {}
        self._my_requests: Dict[str, HelpRequest] = {}  # Requests I made
        self._my_responses: Dict[str, HelpResponse] = {}  # Responses I gave
        
        # Thread safety
        self._help_lock = asyncio.Lock()
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        # Configuration
        self.cleanup_interval = 300.0  # 5 minutes
        self.max_stored_requests = 1000
        
        self.logger.info(f"HelpSystemManager initialized for agent {agent_id}") 
   
    async def start(self) -> bool:
        """
        Start the help system manager.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        async with self._help_lock:
            if self._is_running:
                self.logger.warning("Help system manager is already running")
                return True
            
            try:
                # Start cleanup task
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
                self._is_running = True
                
                self.logger.info("Help system manager started successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to start help system manager: {e}")
                return False
    
    async def stop(self) -> None:
        """Stop the help system manager."""
        async with self._help_lock:
            if not self._is_running:
                return
            
            self._is_running = False
            
            # Cancel cleanup task
            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
                self._cleanup_task = None
            
            self.logger.info("Help system manager stopped")
    
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
        async with self._help_lock:
            try:
                # Create help request
                help_request = HelpRequest(
                    requester_id=self.agent_id,
                    required_capabilities=required_capabilities,
                    description=description,
                    timeout_minutes=timeout_minutes,
                    priority=priority,
                    tags=tags or [],
                    context=context or {}
                )
                
                # Store the request
                self._my_requests[help_request.request_id] = help_request
                
                # Create help wanted message
                help_message = BeastModeMessage(
                    type=MessageType.HELP_WANTED,
                    source=self.agent_id,
                    target=None,  # Broadcast
                    payload={
                        "request_id": help_request.request_id,
                        "required_capabilities": required_capabilities,
                        "description": description,
                        "timeout_minutes": timeout_minutes,
                        "priority": priority,
                        "tags": tags or [],
                        "context": context or {},
                        "created_at": help_request.created_at.isoformat()
                    },
                    priority=priority
                )
                
                # Serialize and publish
                message_json = MessageSerializer.serialize(help_message)
                success = await self.redis_manager.publish(self.channel_name, message_json)
                
                if success:
                    self.logger.info(f"Requested help: {help_request.request_id} - {description[:50]}...")
                    return help_request.request_id
                else:
                    # Remove from storage if publish failed
                    del self._my_requests[help_request.request_id]
                    self.logger.error(f"Failed to publish help request: {help_request.request_id}")
                    return ""
                
            except Exception as e:
                self.logger.error(f"Error requesting help: {e}")
                return ""
    
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
        async with self._help_lock:
            try:
                # Check if we have this request
                if request_id not in self._help_requests:
                    self.logger.warning(f"Attempted to respond to unknown help request: {request_id}")
                    return False
                
                help_request = self._help_requests[request_id]
                
                # Check if request is still accepting responses
                if help_request.status not in [HelpRequestStatus.PENDING, HelpRequestStatus.RESPONDED]:
                    self.logger.warning(f"Help request {request_id} is not accepting responses (status: {help_request.status})")
                    return False
                
                if help_request.is_expired():
                    self.logger.warning(f"Help request {request_id} has expired")
                    return False
                
                # Create response
                response = HelpResponse(
                    responder_id=self.agent_id,
                    request_id=request_id,
                    message=message,
                    capabilities_offered=capabilities_offered,
                    estimated_time_minutes=estimated_time_minutes,
                    confidence_level=confidence_level,
                    additional_info=additional_info or {}
                )
                
                # Store our response
                self._my_responses[response.response_id] = response
                
                # Create help response message
                response_message = BeastModeMessage(
                    type=MessageType.HELP_RESPONSE,
                    source=self.agent_id,
                    target=help_request.requester_id,
                    payload={
                        "response_id": response.response_id,
                        "request_id": request_id,
                        "message": message,
                        "capabilities_offered": capabilities_offered,
                        "estimated_time_minutes": estimated_time_minutes,
                        "confidence_level": confidence_level,
                        "additional_info": additional_info or {},
                        "response_time": response.response_time.isoformat()
                    },
                    priority=help_request.priority
                )
                
                # Serialize and publish
                message_json = MessageSerializer.serialize(response_message)
                success = await self.redis_manager.publish(self.channel_name, message_json)
                
                if success:
                    self.logger.info(f"Responded to help request: {request_id}")
                    return True
                else:
                    # Remove from storage if publish failed
                    del self._my_responses[response.response_id]
                    self.logger.error(f"Failed to publish help response: {response.response_id}")
                    return False
                
            except Exception as e:
                self.logger.error(f"Error responding to help: {e}")
                return False
    
    async def select_helper(self, request_id: str, responder_id: str) -> bool:
        """
        Select a helper for one of our help requests.
        
        Args:
            request_id: ID of our help request
            responder_id: ID of the agent to select as helper
            
        Returns:
            bool: True if helper was selected successfully, False otherwise
        """
        async with self._help_lock:
            try:
                # Check if this is our request
                if request_id not in self._my_requests:
                    self.logger.warning(f"Attempted to select helper for unknown request: {request_id}")
                    return False
                
                help_request = self._my_requests[request_id]
                
                # Select the helper
                if not help_request.select_helper(responder_id):
                    self.logger.warning(f"Failed to select helper {responder_id} for request {request_id}")
                    return False
                
                # Notify the selected helper
                selection_message = BeastModeMessage(
                    type=MessageType.TECHNICAL_EXCHANGE,
                    source=self.agent_id,
                    target=responder_id,
                    payload={
                        "exchange_type": "helper_selected",
                        "request_id": request_id,
                        "message": f"You have been selected to help with request: {help_request.description}",
                        "selected_at": datetime.now().isoformat()
                    },
                    priority=help_request.priority
                )
                
                # Serialize and publish
                message_json = MessageSerializer.serialize(selection_message)
                success = await self.redis_manager.publish(self.channel_name, message_json)
                
                if success:
                    self.logger.info(f"Selected helper {responder_id} for request {request_id}")
                    
                    # Track the interaction start
                    await self.agent_discovery_manager.track_agent_interaction(
                        responder_id, True, 0.0  # Successful selection
                    )
                    
                    return True
                else:
                    # Revert the selection if publish failed
                    help_request.status = HelpRequestStatus.RESPONDED
                    help_request.selected_responder = None
                    help_request.started_at = None
                    self.logger.error(f"Failed to notify selected helper: {responder_id}")
                    return False
                
            except Exception as e:
                self.logger.error(f"Error selecting helper: {e}")
                return False
    
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
        async with self._help_lock:
            try:
                # Check if this is our request
                if request_id not in self._my_requests:
                    self.logger.warning(f"Attempted to complete unknown request: {request_id}")
                    return False
                
                help_request = self._my_requests[request_id]
                
                # Mark as completed
                if not help_request.mark_completed(success):
                    self.logger.warning(f"Failed to mark request {request_id} as completed")
                    return False
                
                # Update trust score for the helper
                if help_request.selected_responder:
                    response_time = None
                    if help_request.started_at and help_request.completed_at:
                        response_time = (help_request.completed_at - help_request.started_at).total_seconds()
                    
                    await self.agent_discovery_manager.track_agent_interaction(
                        help_request.selected_responder, success, response_time
                    )
                
                # Notify the helper about completion
                if help_request.selected_responder:
                    completion_msg = BeastModeMessage(
                        type=MessageType.TECHNICAL_EXCHANGE,
                        source=self.agent_id,
                        target=help_request.selected_responder,
                        payload={
                            "exchange_type": "help_completed",
                            "request_id": request_id,
                            "success": success,
                            "message": completion_message or ("Help completed successfully" if success else "Help request failed"),
                            "completed_at": help_request.completed_at.isoformat() if help_request.completed_at else None
                        },
                        priority=help_request.priority
                    )
                    
                    # Serialize and publish
                    message_json = MessageSerializer.serialize(completion_msg)
                    await self.redis_manager.publish(self.channel_name, message_json)
                
                status_str = "completed" if success else "failed"
                self.logger.info(f"Help request {request_id} marked as {status_str}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error completing help request: {e}")
                return False
    
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
        async with self._help_lock:
            try:
                requests = []
                
                for help_request in self._help_requests.values():
                    # Filter by expiration
                    if not include_expired and help_request.is_expired():
                        continue
                    
                    # Filter by status
                    if status_filter and help_request.status not in status_filter:
                        continue
                    
                    requests.append(help_request)
                
                # Sort by priority and creation time
                requests.sort(key=lambda r: (r.priority, r.created_at))
                
                return requests
                
            except Exception as e:
                self.logger.error(f"Error getting help requests: {e}")
                return []
    
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
        async with self._help_lock:
            try:
                requests = []
                
                for help_request in self._my_requests.values():
                    # Filter by expiration
                    if not include_expired and help_request.is_expired():
                        continue
                    
                    # Filter by status
                    if status_filter and help_request.status not in status_filter:
                        continue
                    
                    requests.append(help_request)
                
                # Sort by priority and creation time
                requests.sort(key=lambda r: (r.priority, r.created_at))
                
                return requests
                
            except Exception as e:
                self.logger.error(f"Error getting my requests: {e}")
                return []
    
    async def get_available_helpers(self, required_capabilities: List[str],
                                  max_helpers: int = 10) -> List[tuple]:
        """
        Get available agents that can help with specific capabilities.
        
        Args:
            required_capabilities: List of required capabilities
            max_helpers: Maximum number of helpers to return
            
        Returns:
            List of tuples (agent, score) sorted by capability match and trust
        """
        try:
            # Use agent discovery to find suitable helpers
            best_agents = await self.agent_discovery_manager.find_best_agents(
                required_capabilities, max_helpers
            )
            
            self.logger.debug(f"Found {len(best_agents)} available helpers for capabilities: {required_capabilities}")
            return best_agents
            
        except Exception as e:
            self.logger.error(f"Error getting available helpers: {e}")
            return []
    
    async def handle_help_message(self, message: BeastModeMessage) -> None:
        """
        Handle incoming help-related messages.
        
        Args:
            message: BeastModeMessage to handle
        """
        try:
            if message.type == MessageType.HELP_WANTED:
                await self._handle_help_wanted(message)
            elif message.type == MessageType.HELP_RESPONSE:
                await self._handle_help_response(message)
            elif message.type == MessageType.TECHNICAL_EXCHANGE:
                await self._handle_technical_exchange(message)
            else:
                self.logger.warning(f"Unhandled help message type: {message.type}")
                
        except Exception as e:
            self.logger.error(f"Error handling help message: {e}")
    
    async def _handle_help_wanted(self, message: BeastModeMessage) -> None:
        """Handle help wanted messages from other agents."""
        async with self._help_lock:
            try:
                payload = message.payload
                
                # Create help request from message
                help_request = HelpRequest(
                    request_id=payload.get("request_id", str(uuid.uuid4())),
                    requester_id=message.source,
                    required_capabilities=payload.get("required_capabilities", []),
                    description=payload.get("description", ""),
                    timeout_minutes=payload.get("timeout_minutes", 30),
                    priority=payload.get("priority", 5),
                    tags=payload.get("tags", []),
                    context=payload.get("context", {}),
                    created_at=datetime.fromisoformat(payload.get("created_at", datetime.now().isoformat()))
                )
                
                # Store the request
                self._help_requests[help_request.request_id] = help_request
                
                self.logger.info(f"Received help request: {help_request.request_id} from {message.source}")
                
            except Exception as e:
                self.logger.error(f"Error handling help wanted message: {e}")
    
    async def _handle_help_response(self, message: BeastModeMessage) -> None:
        """Handle help response messages for our requests."""
        async with self._help_lock:
            try:
                payload = message.payload
                request_id = payload.get("request_id")
                
                # Check if this is a response to our request
                if request_id not in self._my_requests:
                    return
                
                help_request = self._my_requests[request_id]
                
                # Create response object
                response = HelpResponse(
                    response_id=payload.get("response_id", str(uuid.uuid4())),
                    responder_id=message.source,
                    request_id=request_id,
                    message=payload.get("message", ""),
                    capabilities_offered=payload.get("capabilities_offered", []),
                    estimated_time_minutes=payload.get("estimated_time_minutes", 30),
                    confidence_level=payload.get("confidence_level", 0.8),
                    response_time=datetime.fromisoformat(payload.get("response_time", datetime.now().isoformat())),
                    additional_info=payload.get("additional_info", {})
                )
                
                # Add response to request
                if help_request.add_response(response):
                    self.logger.info(f"Received help response from {message.source} for request {request_id}")
                else:
                    self.logger.warning(f"Failed to add response from {message.source} for request {request_id}")
                
            except Exception as e:
                self.logger.error(f"Error handling help response message: {e}")
    
    async def _handle_technical_exchange(self, message: BeastModeMessage) -> None:
        """Handle technical exchange messages related to help system."""
        try:
            payload = message.payload
            exchange_type = payload.get("exchange_type")
            
            if exchange_type == "helper_selected":
                self.logger.info(f"Selected as helper for request {payload.get('request_id')}")
            elif exchange_type == "help_completed":
                request_id = payload.get("request_id")
                success = payload.get("success", True)
                completion_message = payload.get("message", "")
                self.logger.info(f"Help request {request_id} completed: {completion_message}")
            else:
                self.logger.debug(f"Received technical exchange: {exchange_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling technical exchange: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop for expired requests and responses."""
        while self._is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                if not self._is_running:
                    break
                
                async with self._help_lock:
                    current_time = datetime.now()
                    
                    # Clean up expired help requests
                    expired_requests = []
                    for request_id, help_request in self._help_requests.items():
                        if help_request.is_expired() and help_request.status not in [
                            HelpRequestStatus.COMPLETED, HelpRequestStatus.FAILED, HelpRequestStatus.TIMEOUT
                        ]:
                            help_request.mark_timeout()
                            self.logger.debug(f"Marked help request {request_id} as timed out")
                        
                        # Remove very old requests (older than 24 hours)
                        age = current_time - help_request.created_at
                        if age.total_seconds() > (24 * 60 * 60):
                            expired_requests.append(request_id)
                    
                    for request_id in expired_requests:
                        del self._help_requests[request_id]
                        self.logger.debug(f"Removed old help request: {request_id}")
                    
                    # Clean up our old requests
                    expired_my_requests = []
                    for request_id, help_request in self._my_requests.items():
                        if help_request.is_expired() and help_request.status not in [
                            HelpRequestStatus.COMPLETED, HelpRequestStatus.FAILED, HelpRequestStatus.TIMEOUT
                        ]:
                            help_request.mark_timeout()
                            self.logger.debug(f"Marked my help request {request_id} as timed out")
                        
                        # Remove very old requests (older than 24 hours)
                        age = current_time - help_request.created_at
                        if age.total_seconds() > (24 * 60 * 60):
                            expired_my_requests.append(request_id)
                    
                    for request_id in expired_my_requests:
                        del self._my_requests[request_id]
                        self.logger.debug(f"Removed old my request: {request_id}")
                    
                    # Clean up old responses
                    expired_responses = []
                    for response_id, response in self._my_responses.items():
                        age = current_time - response.response_time
                        if age.total_seconds() > (24 * 60 * 60):
                            expired_responses.append(response_id)
                    
                    for response_id in expired_responses:
                        del self._my_responses[response_id]
                        self.logger.debug(f"Removed old response: {response_id}")
                    
                    # Limit storage size
                    if len(self._help_requests) > self.max_stored_requests:
                        # Remove oldest requests
                        sorted_requests = sorted(
                            self._help_requests.items(),
                            key=lambda x: x[1].created_at
                        )
                        to_remove = len(self._help_requests) - self.max_stored_requests
                        for i in range(to_remove):
                            request_id = sorted_requests[i][0]
                            del self._help_requests[request_id]
                            self.logger.debug(f"Removed old request due to storage limit: {request_id}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in help system cleanup loop: {e}")
                await asyncio.sleep(5)  # Brief pause before continuing
    
    async def get_help_system_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the help system.
        
        Returns:
            Dictionary containing help system statistics
        """
        async with self._help_lock:
            try:
                # Count requests by status
                request_status_counts = defaultdict(int)
                for request in self._help_requests.values():
                    request_status_counts[request.status.value] += 1
                
                my_request_status_counts = defaultdict(int)
                for request in self._my_requests.values():
                    my_request_status_counts[request.status.value] += 1
                
                # Calculate average response times
                total_response_time = 0
                response_count = 0
                for request in self._my_requests.values():
                    if request.started_at and request.responded_at:
                        response_time = (request.started_at - request.responded_at).total_seconds()
                        total_response_time += response_time
                        response_count += 1
                
                avg_response_time = total_response_time / response_count if response_count > 0 else 0
                
                return {
                    "total_help_requests": len(self._help_requests),
                    "my_requests": len(self._my_requests),
                    "my_responses": len(self._my_responses),
                    "request_status_distribution": dict(request_status_counts),
                    "my_request_status_distribution": dict(my_request_status_counts),
                    "average_response_time_seconds": avg_response_time,
                    "is_running": self._is_running,
                    "cleanup_interval": self.cleanup_interval,
                    "max_stored_requests": self.max_stored_requests
                }
                
            except Exception as e:
                self.logger.error(f"Error getting help system stats: {e}")
                return {}
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()


# Convenience functions
async def create_help_system_manager(redis_manager, agent_id: str, 
                                   agent_discovery_manager,
                                   channel_name: str = "beast_mode_network") -> HelpSystemManager:
    """
    Create and start a help system manager.
    
    Args:
        redis_manager: RedisConnectionManager instance
        agent_id: Unique identifier for this agent
        agent_discovery_manager: AgentDiscoveryManager instance
        channel_name: Redis channel for help system communication
        
    Returns:
        Started HelpSystemManager instance
    """
    manager = HelpSystemManager(redis_manager, agent_id, agent_discovery_manager, channel_name)
    await manager.start()
    return manager