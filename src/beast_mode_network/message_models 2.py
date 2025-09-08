"""
Core message models and serialization system for Beast Mode Agent Network.

This module provides structured data models for inter-agent communication,
including message types, agent capabilities, and JSON serialization utilities.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class MessageType(str, Enum):
    """Enumeration of all supported message types in the Beast Mode network."""
    
    SIMPLE_MESSAGE = "simple_message"
    PROMPT_REQUEST = "prompt_request"
    PROMPT_RESPONSE = "prompt_response"
    AGENT_DISCOVERY = "agent_discovery"
    AGENT_RESPONSE = "agent_response"
    HELP_WANTED = "help_wanted"
    HELP_RESPONSE = "help_response"
    SPORE_DELIVERY = "spore_delivery"
    SPORE_REQUEST = "spore_request"
    TECHNICAL_EXCHANGE = "technical_exchange"
    SYSTEM_HEALTH = "system_health"
    PROCESSOR_RESPONSE = "processor_response"


@dataclass
class AgentCapabilities:
    """Metadata describing an agent's capabilities and specializations."""
    
    agent_id: str
    capabilities: List[str] = field(default_factory=list)
    specializations: List[str] = field(default_factory=list)
    description: str = ""
    version: str = "1.0.0"
    max_concurrent_tasks: int = 5
    supported_message_types: List[MessageType] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and normalize agent capabilities after initialization."""
        if not self.agent_id:
            raise ValueError("agent_id cannot be empty")
        
        # Normalize capabilities and specializations to lowercase
        self.capabilities = [cap.lower().strip() for cap in self.capabilities if cap.strip()]
        self.specializations = [spec.lower().strip() for spec in self.specializations if spec.strip()]
        
        # Ensure supported_message_types contains valid MessageType instances
        validated_types = []
        for msg_type in self.supported_message_types:
            if isinstance(msg_type, str):
                try:
                    validated_types.append(MessageType(msg_type))
                except ValueError:
                    continue  # Skip invalid message types
            elif isinstance(msg_type, MessageType):
                validated_types.append(msg_type)
        self.supported_message_types = validated_types
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert AgentCapabilities to dictionary representation."""
        return {
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "specializations": self.specializations,
            "description": self.description,
            "version": self.version,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "supported_message_types": [msg_type.value for msg_type in self.supported_message_types]
        }


@dataclass
class BeastModeMessage:
    """Core message structure for Beast Mode Agent Network communication."""
    
    type: MessageType
    source: str
    target: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 5
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Validate message fields after initialization."""
        if not self.source:
            raise ValueError("source cannot be empty")
        
        if not isinstance(self.type, MessageType):
            if isinstance(self.type, str):
                try:
                    self.type = MessageType(self.type)
                except ValueError:
                    raise ValueError(f"Invalid message type: {self.type}")
            else:
                raise ValueError(f"Message type must be MessageType or string, got {type(self.type)}")
        
        if not isinstance(self.payload, dict):
            raise ValueError("payload must be a dictionary")
        
        if not (1 <= self.priority <= 10):
            raise ValueError("priority must be between 1 and 10")
        
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def is_broadcast(self) -> bool:
        """Check if this message is a broadcast message (no specific target)."""
        return self.target is None
    
    def is_targeted(self) -> bool:
        """Check if this message is targeted to a specific agent."""
        return self.target is not None


class MessageSerializationError(Exception):
    """Exception raised when message serialization/deserialization fails."""
    pass


class MessageSerializer:
    """Handles JSON serialization and deserialization of Beast Mode messages."""
    
    @staticmethod
    def serialize(message: BeastModeMessage) -> str:
        """
        Serialize a BeastModeMessage to JSON string.
        
        Args:
            message: The message to serialize
            
        Returns:
            JSON string representation of the message
            
        Raises:
            MessageSerializationError: If serialization fails
        """
        try:
            message_dict = {
                "type": message.type.value,
                "source": message.source,
                "target": message.target,
                "payload": message.payload,
                "timestamp": message.timestamp.isoformat(),
                "priority": message.priority,
                "id": message.id
            }
            return json.dumps(message_dict, ensure_ascii=False, separators=(',', ':'))
        except (TypeError, ValueError) as e:
            raise MessageSerializationError(f"Failed to serialize message: {e}") from e
    
    @staticmethod
    def deserialize(json_str: str) -> BeastModeMessage:
        """
        Deserialize a JSON string to BeastModeMessage.
        
        Args:
            json_str: JSON string to deserialize
            
        Returns:
            BeastModeMessage instance
            
        Raises:
            MessageSerializationError: If deserialization fails
        """
        try:
            data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["type", "source"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise MessageSerializationError(f"Missing required fields: {missing_fields}")
            
            # Parse timestamp
            timestamp = datetime.now()
            if "timestamp" in data and data["timestamp"]:
                try:
                    timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
                except ValueError:
                    # If timestamp parsing fails, use current time
                    pass
            
            # Create message with validated data
            return BeastModeMessage(
                type=MessageType(data["type"]),
                source=data["source"],
                target=data.get("target"),
                payload=data.get("payload", {}),
                timestamp=timestamp,
                priority=data.get("priority", 5),
                id=data.get("id", str(uuid.uuid4()))
            )
            
        except json.JSONDecodeError as e:
            raise MessageSerializationError(f"Invalid JSON format: {e}") from e
        except ValueError as e:
            raise MessageSerializationError(f"Invalid message data: {e}") from e
        except Exception as e:
            raise MessageSerializationError(f"Unexpected error during deserialization: {e}") from e
    
    @staticmethod
    def serialize_agent_capabilities(capabilities: AgentCapabilities) -> str:
        """
        Serialize AgentCapabilities to JSON string.
        
        Args:
            capabilities: The agent capabilities to serialize
            
        Returns:
            JSON string representation of the capabilities
            
        Raises:
            MessageSerializationError: If serialization fails
        """
        try:
            capabilities_dict = {
                "agent_id": capabilities.agent_id,
                "capabilities": capabilities.capabilities,
                "specializations": capabilities.specializations,
                "description": capabilities.description,
                "version": capabilities.version,
                "max_concurrent_tasks": capabilities.max_concurrent_tasks,
                "supported_message_types": [msg_type.value for msg_type in capabilities.supported_message_types]
            }
            return json.dumps(capabilities_dict, ensure_ascii=False, separators=(',', ':'))
        except (TypeError, ValueError) as e:
            raise MessageSerializationError(f"Failed to serialize agent capabilities: {e}") from e
    
    @staticmethod
    def deserialize_agent_capabilities(json_str: str) -> AgentCapabilities:
        """
        Deserialize a JSON string to AgentCapabilities.
        
        Args:
            json_str: JSON string to deserialize
            
        Returns:
            AgentCapabilities instance
            
        Raises:
            MessageSerializationError: If deserialization fails
        """
        try:
            data = json.loads(json_str)
            
            # Validate required fields
            if "agent_id" not in data:
                raise MessageSerializationError("Missing required field: agent_id")
            
            # Parse supported message types
            supported_types = []
            if "supported_message_types" in data:
                for msg_type_str in data["supported_message_types"]:
                    try:
                        supported_types.append(MessageType(msg_type_str))
                    except ValueError:
                        continue  # Skip invalid message types
            
            return AgentCapabilities(
                agent_id=data["agent_id"],
                capabilities=data.get("capabilities", []),
                specializations=data.get("specializations", []),
                description=data.get("description", ""),
                version=data.get("version", "1.0.0"),
                max_concurrent_tasks=data.get("max_concurrent_tasks", 5),
                supported_message_types=supported_types
            )
            
        except json.JSONDecodeError as e:
            raise MessageSerializationError(f"Invalid JSON format: {e}") from e
        except ValueError as e:
            raise MessageSerializationError(f"Invalid capabilities data: {e}") from e
        except Exception as e:
            raise MessageSerializationError(f"Unexpected error during deserialization: {e}") from e


def create_simple_message(source: str, message_text: str, target: Optional[str] = None, 
                         priority: int = 5) -> BeastModeMessage:
    """
    Convenience function to create a simple text message.
    
    Args:
        source: ID of the sending agent
        message_text: The text content of the message
        target: Optional target agent ID (None for broadcast)
        priority: Message priority (1-10, default 5)
        
    Returns:
        BeastModeMessage configured as a simple message
    """
    return BeastModeMessage(
        type=MessageType.SIMPLE_MESSAGE,
        source=source,
        target=target,
        payload={"message": message_text},
        priority=priority
    )


def create_help_request(source: str, required_capabilities: List[str], 
                       description: str, timeout_minutes: int = 30) -> BeastModeMessage:
    """
    Convenience function to create a help request message.
    
    Args:
        source: ID of the requesting agent
        required_capabilities: List of required capabilities
        description: Description of the help needed
        timeout_minutes: Request timeout in minutes
        
    Returns:
        BeastModeMessage configured as a help request
    """
    return BeastModeMessage(
        type=MessageType.HELP_WANTED,
        source=source,
        target=None,  # Help requests are always broadcast
        payload={
            "required_capabilities": required_capabilities,
            "description": description,
            "timeout_minutes": timeout_minutes
        },
        priority=7  # Help requests have higher priority
    )


def create_agent_discovery_message(capabilities: AgentCapabilities) -> BeastModeMessage:
    """
    Convenience function to create an agent discovery message.
    
    Args:
        capabilities: Agent capabilities to announce
        
    Returns:
        BeastModeMessage configured as an agent discovery message
    """
    return BeastModeMessage(
        type=MessageType.AGENT_DISCOVERY,
        source=capabilities.agent_id,
        target=None,  # Discovery messages are always broadcast
        payload={
            "capabilities": capabilities.capabilities,
            "specializations": capabilities.specializations,
            "description": capabilities.description,
            "version": capabilities.version,
            "max_concurrent_tasks": capabilities.max_concurrent_tasks,
            "supported_message_types": [msg_type.value for msg_type in capabilities.supported_message_types]
        },
        priority=6  # Discovery messages have medium-high priority
    )