"""
Unit tests for Beast Mode Agent Network message models and serialization.
"""

import json
import pytest
from datetime import datetime
from unittest.mock import patch

from src.beast_mode_network.message_models import (
    MessageType,
    BeastModeMessage,
    AgentCapabilities,
    MessageSerializer,
    MessageSerializationError,
    create_simple_message,
    create_help_request,
    create_agent_discovery_message,
)


class TestMessageType:
    """Test MessageType enum functionality."""
    
    def test_message_type_values(self):
        """Test that all expected message types are defined."""
        expected_types = [
            "simple_message",
            "prompt_request", 
            "prompt_response",
            "agent_discovery",
            "agent_response",
            "help_wanted",
            "help_response",
            "spore_delivery",
            "spore_request",
            "technical_exchange",
            "system_health",
            "processor_response"
        ]
        
        for expected_type in expected_types:
            assert hasattr(MessageType, expected_type.upper())
            assert MessageType(expected_type).value == expected_type
    
    def test_message_type_string_conversion(self):
        """Test MessageType can be converted to/from strings."""
        msg_type = MessageType.SIMPLE_MESSAGE
        assert msg_type.value == "simple_message"
        assert MessageType("simple_message") == msg_type


class TestAgentCapabilities:
    """Test AgentCapabilities dataclass functionality."""
    
    def test_agent_capabilities_creation(self):
        """Test basic AgentCapabilities creation."""
        capabilities = AgentCapabilities(
            agent_id="test_agent",
            capabilities=["python", "data_analysis"],
            specializations=["machine_learning", "nlp"],
            description="Test agent for unit testing"
        )
        
        assert capabilities.agent_id == "test_agent"
        assert capabilities.capabilities == ["python", "data_analysis"]
        assert capabilities.specializations == ["machine_learning", "nlp"]
        assert capabilities.description == "Test agent for unit testing"
        assert capabilities.version == "1.0.0"
        assert capabilities.max_concurrent_tasks == 5
    
    def test_agent_capabilities_validation(self):
        """Test AgentCapabilities validation."""
        # Test empty agent_id raises error
        with pytest.raises(ValueError, match="agent_id cannot be empty"):
            AgentCapabilities(agent_id="")
        
        # Test None agent_id raises error
        with pytest.raises(ValueError, match="agent_id cannot be empty"):
            AgentCapabilities(agent_id=None)
    
    def test_agent_capabilities_normalization(self):
        """Test that capabilities and specializations are normalized."""
        capabilities = AgentCapabilities(
            agent_id="test_agent",
            capabilities=["  Python  ", "DATA_ANALYSIS", ""],
            specializations=["Machine_Learning  ", "  NLP", "   "]
        )
        
        assert capabilities.capabilities == ["python", "data_analysis"]
        assert capabilities.specializations == ["machine_learning", "nlp"]
    
    def test_supported_message_types_validation(self):
        """Test supported_message_types validation and conversion."""
        capabilities = AgentCapabilities(
            agent_id="test_agent",
            supported_message_types=["simple_message", MessageType.HELP_WANTED, "invalid_type"]
        )
        
        expected_types = [MessageType.SIMPLE_MESSAGE, MessageType.HELP_WANTED]
        assert capabilities.supported_message_types == expected_types


class TestBeastModeMessage:
    """Test BeastModeMessage dataclass functionality."""
    
    def test_message_creation(self):
        """Test basic message creation."""
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="agent1",
            target="agent2",
            payload={"text": "Hello"}
        )
        
        assert message.type == MessageType.SIMPLE_MESSAGE
        assert message.source == "agent1"
        assert message.target == "agent2"
        assert message.payload == {"text": "Hello"}
        assert message.priority == 5
        assert message.id is not None
        assert isinstance(message.timestamp, datetime)
    
    def test_message_validation(self):
        """Test message validation."""
        # Test empty source raises error
        with pytest.raises(ValueError, match="source cannot be empty"):
            BeastModeMessage(type=MessageType.SIMPLE_MESSAGE, source="")
        
        # Test invalid message type
        with pytest.raises(ValueError, match="Invalid message type"):
            BeastModeMessage(type="invalid_type", source="agent1")
        
        # Test invalid payload type
        with pytest.raises(ValueError, match="payload must be a dictionary"):
            BeastModeMessage(type=MessageType.SIMPLE_MESSAGE, source="agent1", payload="not_dict")
        
        # Test invalid priority
        with pytest.raises(ValueError, match="priority must be between 1 and 10"):
            BeastModeMessage(type=MessageType.SIMPLE_MESSAGE, source="agent1", priority=11)
    
    def test_message_type_string_conversion(self):
        """Test that string message types are converted to MessageType enum."""
        message = BeastModeMessage(
            type="simple_message",
            source="agent1"
        )
        
        assert message.type == MessageType.SIMPLE_MESSAGE
    
    def test_broadcast_and_targeted_methods(self):
        """Test is_broadcast and is_targeted methods."""
        broadcast_msg = BeastModeMessage(type=MessageType.SIMPLE_MESSAGE, source="agent1")
        targeted_msg = BeastModeMessage(type=MessageType.SIMPLE_MESSAGE, source="agent1", target="agent2")
        
        assert broadcast_msg.is_broadcast() is True
        assert broadcast_msg.is_targeted() is False
        
        assert targeted_msg.is_broadcast() is False
        assert targeted_msg.is_targeted() is True


class TestMessageSerializer:
    """Test MessageSerializer functionality."""
    
    def test_message_serialization(self):
        """Test message serialization to JSON."""
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="agent1",
            target="agent2",
            payload={"text": "Hello"},
            priority=7
        )
        
        json_str = MessageSerializer.serialize(message)
        data = json.loads(json_str)
        
        assert data["type"] == "simple_message"
        assert data["source"] == "agent1"
        assert data["target"] == "agent2"
        assert data["payload"] == {"text": "Hello"}
        assert data["priority"] == 7
        assert "timestamp" in data
        assert "id" in data
    
    def test_message_deserialization(self):
        """Test message deserialization from JSON."""
        json_data = {
            "type": "simple_message",
            "source": "agent1",
            "target": "agent2",
            "payload": {"text": "Hello"},
            "priority": 7,
            "timestamp": "2023-01-01T12:00:00",
            "id": "test-id"
        }
        json_str = json.dumps(json_data)
        
        message = MessageSerializer.deserialize(json_str)
        
        assert message.type == MessageType.SIMPLE_MESSAGE
        assert message.source == "agent1"
        assert message.target == "agent2"
        assert message.payload == {"text": "Hello"}
        assert message.priority == 7
        assert message.id == "test-id"
    
    def test_serialization_round_trip(self):
        """Test that serialization and deserialization are reversible."""
        original_message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="agent1",
            payload={"capabilities": ["python"], "description": "Need help"}
        )
        
        json_str = MessageSerializer.serialize(original_message)
        deserialized_message = MessageSerializer.deserialize(json_str)
        
        assert deserialized_message.type == original_message.type
        assert deserialized_message.source == original_message.source
        assert deserialized_message.target == original_message.target
        assert deserialized_message.payload == original_message.payload
        assert deserialized_message.priority == original_message.priority
        assert deserialized_message.id == original_message.id
    
    def test_deserialization_missing_fields(self):
        """Test deserialization with missing required fields."""
        # Missing type field
        with pytest.raises(MessageSerializationError, match="Missing required fields"):
            MessageSerializer.deserialize('{"source": "agent1"}')
        
        # Missing source field
        with pytest.raises(MessageSerializationError, match="Missing required fields"):
            MessageSerializer.deserialize('{"type": "simple_message"}')
    
    def test_deserialization_invalid_json(self):
        """Test deserialization with invalid JSON."""
        with pytest.raises(MessageSerializationError, match="Invalid JSON format"):
            MessageSerializer.deserialize('{"invalid": json}')
    
    def test_deserialization_invalid_message_type(self):
        """Test deserialization with invalid message type."""
        json_str = '{"type": "invalid_type", "source": "agent1"}'
        with pytest.raises(MessageSerializationError, match="Invalid message data"):
            MessageSerializer.deserialize(json_str)
    
    def test_deserialization_with_defaults(self):
        """Test deserialization uses proper defaults for missing optional fields."""
        json_str = '{"type": "simple_message", "source": "agent1"}'
        message = MessageSerializer.deserialize(json_str)
        
        assert message.target is None
        assert message.payload == {}
        assert message.priority == 5
        assert message.id is not None
    
    def test_agent_capabilities_serialization(self):
        """Test AgentCapabilities serialization."""
        capabilities = AgentCapabilities(
            agent_id="test_agent",
            capabilities=["python", "data_analysis"],
            specializations=["ml"],
            supported_message_types=[MessageType.SIMPLE_MESSAGE, MessageType.HELP_WANTED]
        )
        
        json_str = MessageSerializer.serialize_agent_capabilities(capabilities)
        data = json.loads(json_str)
        
        assert data["agent_id"] == "test_agent"
        assert data["capabilities"] == ["python", "data_analysis"]
        assert data["specializations"] == ["ml"]
        assert data["supported_message_types"] == ["simple_message", "help_wanted"]
    
    def test_agent_capabilities_deserialization(self):
        """Test AgentCapabilities deserialization."""
        json_data = {
            "agent_id": "test_agent",
            "capabilities": ["python"],
            "specializations": ["ml"],
            "description": "Test agent",
            "supported_message_types": ["simple_message", "help_wanted"]
        }
        json_str = json.dumps(json_data)
        
        capabilities = MessageSerializer.deserialize_agent_capabilities(json_str)
        
        assert capabilities.agent_id == "test_agent"
        assert capabilities.capabilities == ["python"]
        assert capabilities.specializations == ["ml"]
        assert capabilities.description == "Test agent"
        assert MessageType.SIMPLE_MESSAGE in capabilities.supported_message_types
        assert MessageType.HELP_WANTED in capabilities.supported_message_types
    
    def test_agent_capabilities_deserialization_missing_agent_id(self):
        """Test AgentCapabilities deserialization with missing agent_id."""
        json_str = '{"capabilities": ["python"]}'
        with pytest.raises(MessageSerializationError, match="Missing required field: agent_id"):
            MessageSerializer.deserialize_agent_capabilities(json_str)


class TestConvenienceFunctions:
    """Test convenience functions for creating common message types."""
    
    def test_create_simple_message(self):
        """Test create_simple_message function."""
        message = create_simple_message("agent1", "Hello world", "agent2", priority=8)
        
        assert message.type == MessageType.SIMPLE_MESSAGE
        assert message.source == "agent1"
        assert message.target == "agent2"
        assert message.payload == {"message": "Hello world"}
        assert message.priority == 8
    
    def test_create_simple_message_broadcast(self):
        """Test create_simple_message for broadcast."""
        message = create_simple_message("agent1", "Hello everyone")
        
        assert message.type == MessageType.SIMPLE_MESSAGE
        assert message.source == "agent1"
        assert message.target is None
        assert message.payload == {"message": "Hello everyone"}
        assert message.priority == 5
    
    def test_create_help_request(self):
        """Test create_help_request function."""
        message = create_help_request(
            "agent1", 
            ["python", "data_analysis"], 
            "Need help with data processing",
            timeout_minutes=45
        )
        
        assert message.type == MessageType.HELP_WANTED
        assert message.source == "agent1"
        assert message.target is None  # Help requests are always broadcast
        assert message.payload["required_capabilities"] == ["python", "data_analysis"]
        assert message.payload["description"] == "Need help with data processing"
        assert message.payload["timeout_minutes"] == 45
        assert message.priority == 7
    
    def test_create_agent_discovery_message(self):
        """Test create_agent_discovery_message function."""
        capabilities = AgentCapabilities(
            agent_id="test_agent",
            capabilities=["python"],
            specializations=["ml"],
            description="Test agent",
            supported_message_types=[MessageType.SIMPLE_MESSAGE]
        )
        
        message = create_agent_discovery_message(capabilities)
        
        assert message.type == MessageType.AGENT_DISCOVERY
        assert message.source == "test_agent"
        assert message.target is None  # Discovery messages are always broadcast
        assert message.payload["capabilities"] == ["python"]
        assert message.payload["specializations"] == ["ml"]
        assert message.payload["description"] == "Test agent"
        assert message.payload["supported_message_types"] == ["simple_message"]
        assert message.priority == 6


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_serialization_error_handling(self):
        """Test serialization error handling."""
        # Create a message with non-serializable payload
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="agent1",
            payload={"func": lambda x: x}  # Functions are not JSON serializable
        )
        
        with pytest.raises(MessageSerializationError, match="Failed to serialize message"):
            MessageSerializer.serialize(message)
    
    def test_timestamp_parsing_fallback(self):
        """Test that invalid timestamps fall back to current time."""
        json_str = '{"type": "simple_message", "source": "agent1", "timestamp": "invalid-timestamp"}'
        
        with patch('src.beast_mode_network.message_models.datetime') as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromisoformat.side_effect = ValueError("Invalid timestamp")
            
            message = MessageSerializer.deserialize(json_str)
            assert message.timestamp == mock_now
    
    def test_invalid_message_types_in_capabilities(self):
        """Test that invalid message types in capabilities are filtered out."""
        json_data = {
            "agent_id": "test_agent",
            "supported_message_types": ["simple_message", "invalid_type", "help_wanted"]
        }
        json_str = json.dumps(json_data)
        
        capabilities = MessageSerializer.deserialize_agent_capabilities(json_str)
        
        # Only valid message types should be included
        assert len(capabilities.supported_message_types) == 2
        assert MessageType.SIMPLE_MESSAGE in capabilities.supported_message_types
        assert MessageType.HELP_WANTED in capabilities.supported_message_types