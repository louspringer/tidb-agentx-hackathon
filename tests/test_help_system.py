"""
Unit tests for Help System functionality.

Tests the HelpRequest, HelpSystemManager, and related functionality including
request lifecycle management, timeout handling, helper selection, and response tracking.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from src.beast_mode_network.help_system import (
    HelpRequestStatus,
    HelpRequest,
    HelpResponse,
    HelpSystemManager,
    create_help_request,
    create_help_response,
)
from src.beast_mode_network.message_models import MessageType, BeastModeMessage


class TestHelpRequestStatus:
    """Test HelpRequestStatus enum."""
    
    def test_status_values(self):
        """Test that all expected status values are defined."""
        expected_statuses = [
            "pending",
            "responded", 
            "in_progress",
            "completed",
            "failed",
            "timeout",
            "cancelled"
        ]
        
        for status in expected_statuses:
            assert hasattr(HelpRequestStatus, status.upper())
            assert HelpRequestStatus(status).value == status


class TestHelpRequest:
    """Test HelpRequest dataclass functionality."""
    
    def test_help_request_creation(self):
        """Test basic HelpRequest creation."""
        request = HelpRequest(
            request_id="test-123",
            requester_id="agent1",
            required_capabilities=["python", "data_analysis"],
            description="Need help with data processing",
            timeout_minutes=30
        )
        
        assert request.request_id == "test-123"
        assert request.requester_id == "agent1"
        assert request.required_capabilities == ["python", "data_analysis"]
        assert request.description == "Need help with data processing"
        assert request.status == HelpRequestStatus.PENDING
        assert request.timeout_minutes == 30
        assert request.priority == 5
        assert isinstance(request.created_at, datetime)
        assert request.responses == []
        assert request.selected_responder is None
    
    def test_help_request_validation(self):
        """Test HelpRequest validation."""
        # Test empty request_id
        with pytest.raises(ValueError, match="request_id cannot be empty"):
            HelpRequest(request_id="", requester_id="agent1")
        
        # Test empty requester_id
        with pytest.raises(ValueError, match="requester_id cannot be empty"):
            HelpRequest(request_id="test", requester_id="")
        
        # Test empty required_capabilities
        with pytest.raises(ValueError, match="required_capabilities cannot be empty"):
            HelpRequest(request_id="test", requester_id="agent1", required_capabilities=[])
        
        # Test invalid priority
        with pytest.raises(ValueError, match="priority must be between 1 and 10"):
            HelpRequest(request_id="test", requester_id="agent1", priority=11)
        
        # Test invalid timeout
        with pytest.raises(ValueError, match="timeout_minutes must be positive"):
            HelpRequest(request_id="test", requester_id="agent1", timeout_minutes=0)
    
    def test_help_request_methods(self):
        """Test HelpRequest utility methods."""
        request = HelpRequest(
            request_id="test",
            requester_id="agent1",
            timeout_minutes=30
        )
        
        # Test is_expired
        assert not request.is_expired()
        
        # Test with expired request
        old_request = HelpRequest(
            request_id="old",
            requester_id="agent1",
            timeout_minutes=30
        )
        old_request.created_at = datetime.now() - timedelta(minutes=31)
        assert old_request.is_expired()
        
        # Test can_be_responded_to
        assert request.can_be_responded_to()
        
        request.status = HelpRequestStatus.COMPLETED
        assert not request.can_be_responded_to()
        
        # Test add_response
        request.status = HelpRequestStatus.PENDING
        response = HelpResponse(
            response_id="resp-1",
            responder_id="agent2",
            request_id="test",
            message="I can help!",
            capabilities_offered=["python"]
        )
        
        request.add_response(response)
        assert len(request.responses) == 1
        assert request.responses[0] == response
        assert request.status == HelpRequestStatus.RESPONDED
    
    def test_help_request_select_responder(self):
        """Test responder selection."""
        request = HelpRequest(
            request_id="test",
            requester_id="agent1"
        )
        
        # Add responses
        response1 = HelpResponse(
            response_id="resp-1",
            responder_id="agent2",
            request_id="test",
            message="I can help!",
            capabilities_offered=["python"],
            confidence_level=0.8
        )
        
        response2 = HelpResponse(
            response_id="resp-2", 
            responder_id="agent3",
            request_id="test",
            message="I'm an expert!",
            capabilities_offered=["python", "data_analysis"],
            confidence_level=0.9
        )
        
        request.add_response(response1)
        request.add_response(response2)
        
        # Select responder
        request.select_responder("agent3")
        
        assert request.selected_responder == "agent3"
        assert request.status == HelpRequestStatus.IN_PROGRESS
    
    def test_help_request_complete(self):
        """Test request completion."""
        request = HelpRequest(
            request_id="test",
            requester_id="agent1"
        )
        
        request.status = HelpRequestStatus.IN_PROGRESS
        request.complete(success=True, result="Task completed successfully")
        
        assert request.status == HelpRequestStatus.COMPLETED
        assert request.completion_result == "Task completed successfully"
        assert isinstance(request.completed_at, datetime)
        
        # Test failure
        failed_request = HelpRequest(
            request_id="test2",
            requester_id="agent1"
        )
        
        failed_request.status = HelpRequestStatus.IN_PROGRESS
        failed_request.complete(success=False, result="Task failed")
        
        assert failed_request.status == HelpRequestStatus.FAILED
        assert failed_request.completion_result == "Task failed"


class TestHelpResponse:
    """Test HelpResponse dataclass functionality."""
    
    def test_help_response_creation(self):
        """Test basic HelpResponse creation."""
        response = HelpResponse(
            response_id="resp-123",
            responder_id="agent2",
            request_id="req-456",
            message="I can help with this task!",
            capabilities_offered=["python", "data_analysis"],
            estimated_time_minutes=45,
            confidence_level=0.85
        )
        
        assert response.response_id == "resp-123"
        assert response.responder_id == "agent2"
        assert response.request_id == "req-456"
        assert response.message == "I can help with this task!"
        assert response.capabilities_offered == ["python", "data_analysis"]
        assert response.estimated_time_minutes == 45
        assert response.confidence_level == 0.85
        assert isinstance(response.created_at, datetime)
    
    def test_help_response_validation(self):
        """Test HelpResponse validation."""
        # Test empty response_id
        with pytest.raises(ValueError, match="response_id cannot be empty"):
            HelpResponse(response_id="", responder_id="agent2", request_id="req")
        
        # Test empty responder_id
        with pytest.raises(ValueError, match="responder_id cannot be empty"):
            HelpResponse(response_id="resp", responder_id="", request_id="req")
        
        # Test empty request_id
        with pytest.raises(ValueError, match="request_id cannot be empty"):
            HelpResponse(response_id="resp", responder_id="agent2", request_id="")
        
        # Test invalid confidence level
        with pytest.raises(ValueError, match="confidence_level must be between 0.0 and 1.0"):
            HelpResponse(
                response_id="resp", 
                responder_id="agent2", 
                request_id="req",
                confidence_level=1.5
            )
        
        # Test negative estimated time
        with pytest.raises(ValueError, match="estimated_time_minutes must be positive"):
            HelpResponse(
                response_id="resp",
                responder_id="agent2", 
                request_id="req",
                estimated_time_minutes=-5
            )


class TestHelpSystemManager:
    """Test HelpSystemManager class."""
    
    @pytest.fixture
    def mock_bus_client(self):
        """Create mock bus client."""
        mock_client = AsyncMock()
        mock_client.agent_id = "test_agent"
        return mock_client
    
    @pytest.fixture
    def manager(self, mock_bus_client):
        """Create HelpSystemManager instance."""
        return HelpSystemManager(mock_bus_client)
    
    def test_initialization(self, manager, mock_bus_client):
        """Test manager initialization."""
        assert manager.bus_client == mock_bus_client
        assert manager.agent_id == "test_agent"
        assert len(manager.active_requests) == 0
        assert len(manager.my_requests) == 0
        assert len(manager.my_responses) == 0
    
    @pytest.mark.asyncio
    async def test_request_help_success(self, manager):
        """Test successful help request creation."""
        manager.bus_client.send_message = AsyncMock(return_value=True)
        
        request_id = await manager.request_help(
            required_capabilities=["python", "data_analysis"],
            description="Need help with data processing",
            timeout_minutes=45,
            priority=7
        )
        
        assert request_id is not None
        assert len(manager.my_requests) == 1
        
        request = manager.my_requests[request_id]
        assert request.requester_id == "test_agent"
        assert request.required_capabilities == ["python", "data_analysis"]
        assert request.description == "Need help with data processing"
        assert request.timeout_minutes == 45
        assert request.priority == 7
        assert request.status == HelpRequestStatus.PENDING
        
        # Verify message was sent
        manager.bus_client.send_message.assert_called_once()
        sent_message = manager.bus_client.send_message.call_args[0][0]
        assert sent_message.type == MessageType.HELP_WANTED
        assert sent_message.source == "test_agent"
        assert sent_message.target is None  # Broadcast
    
    @pytest.mark.asyncio
    async def test_request_help_send_failure(self, manager):
        """Test help request when message sending fails."""
        manager.bus_client.send_message = AsyncMock(return_value=False)
        
        request_id = await manager.request_help(
            required_capabilities=["python"],
            description="Test request"
        )
        
        assert request_id is None
        assert len(manager.my_requests) == 0
    
    @pytest.mark.asyncio
    async def test_respond_to_help_success(self, manager):
        """Test successful help response."""
        manager.bus_client.send_message = AsyncMock(return_value=True)
        
        # First, add a request to respond to
        request = HelpRequest(
            request_id="req-123",
            requester_id="other_agent",
            required_capabilities=["python"],
            description="Need Python help"
        )
        manager.active_requests["req-123"] = request
        
        response_id = await manager.respond_to_help(
            request_id="req-123",
            message="I can help with Python!",
            capabilities_offered=["python", "debugging"],
            estimated_time_minutes=30,
            confidence_level=0.9
        )
        
        assert response_id is not None
        assert len(manager.my_responses) == 1
        
        response = manager.my_responses[response_id]
        assert response.responder_id == "test_agent"
        assert response.request_id == "req-123"
        assert response.message == "I can help with Python!"
        assert response.capabilities_offered == ["python", "debugging"]
        assert response.estimated_time_minutes == 30
        assert response.confidence_level == 0.9
        
        # Verify message was sent
        manager.bus_client.send_message.assert_called_once()
        sent_message = manager.bus_client.send_message.call_args[0][0]
        assert sent_message.type == MessageType.HELP_RESPONSE
        assert sent_message.target == "other_agent"
    
    @pytest.mark.asyncio
    async def test_respond_to_nonexistent_request(self, manager):
        """Test responding to non-existent request."""
        response_id = await manager.respond_to_help(
            request_id="nonexistent",
            message="I can help!"
        )
        
        assert response_id is None
        assert len(manager.my_responses) == 0
    
    @pytest.mark.asyncio
    async def test_respond_to_expired_request(self, manager):
        """Test responding to expired request."""
        # Create expired request
        request = HelpRequest(
            request_id="expired",
            requester_id="other_agent",
            timeout_minutes=30
        )
        request.created_at = datetime.now() - timedelta(minutes=31)
        manager.active_requests["expired"] = request
        
        response_id = await manager.respond_to_help(
            request_id="expired",
            message="I can help!"
        )
        
        assert response_id is None
        assert len(manager.my_responses) == 0
    
    @pytest.mark.asyncio
    async def test_select_helper_success(self, manager):
        """Test successful helper selection."""
        manager.bus_client.send_message = AsyncMock(return_value=True)
        
        # Create request with responses
        request = HelpRequest(
            request_id="req-123",
            requester_id="test_agent"
        )
        
        response = HelpResponse(
            response_id="resp-456",
            responder_id="helper_agent",
            request_id="req-123",
            message="I can help!"
        )
        
        request.add_response(response)
        manager.my_requests["req-123"] = request
        
        success = await manager.select_helper("req-123", "helper_agent")
        
        assert success is True
        assert request.selected_responder == "helper_agent"
        assert request.status == HelpRequestStatus.IN_PROGRESS
        
        # Verify selection message was sent
        manager.bus_client.send_message.assert_called_once()
        sent_message = manager.bus_client.send_message.call_args[0][0]
        assert sent_message.type == MessageType.TECHNICAL_EXCHANGE
        assert sent_message.target == "helper_agent"
        assert sent_message.payload["exchange_type"] == "helper_selected"
    
    @pytest.mark.asyncio
    async def test_select_helper_invalid_request(self, manager):
        """Test helper selection for invalid request."""
        success = await manager.select_helper("nonexistent", "helper_agent")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_complete_help_request_success(self, manager):
        """Test successful help request completion."""
        manager.bus_client.send_message = AsyncMock(return_value=True)
        
        # Create in-progress request
        request = HelpRequest(
            request_id="req-123",
            requester_id="test_agent"
        )
        request.status = HelpRequestStatus.IN_PROGRESS
        request.selected_responder = "helper_agent"
        manager.my_requests["req-123"] = request
        
        success = await manager.complete_help_request(
            "req-123", 
            success=True, 
            result="Task completed successfully"
        )
        
        assert success is True
        assert request.status == HelpRequestStatus.COMPLETED
        assert request.completion_result == "Task completed successfully"
        
        # Verify completion message was sent
        manager.bus_client.send_message.assert_called_once()
        sent_message = manager.bus_client.send_message.call_args[0][0]
        assert sent_message.type == MessageType.TECHNICAL_EXCHANGE
        assert sent_message.target == "helper_agent"
        assert sent_message.payload["exchange_type"] == "work_completed"
    
    def test_get_help_requests_filtering(self, manager):
        """Test help request filtering."""
        # Add requests with different statuses
        req1 = HelpRequest(request_id="req1", requester_id="agent1")
        req1.status = HelpRequestStatus.PENDING
        
        req2 = HelpRequest(request_id="req2", requester_id="agent2") 
        req2.status = HelpRequestStatus.RESPONDED
        
        req3 = HelpRequest(request_id="req3", requester_id="agent3")
        req3.status = HelpRequestStatus.COMPLETED
        
        manager.active_requests = {"req1": req1, "req2": req2, "req3": req3}
        
        # Test no filter
        all_requests = manager.get_help_requests()
        assert len(all_requests) == 3
        
        # Test status filter
        pending_requests = manager.get_help_requests(status_filter=[HelpRequestStatus.PENDING])
        assert len(pending_requests) == 1
        assert pending_requests[0].request_id == "req1"
        
        # Test capability filter
        req1.required_capabilities = ["python"]
        req2.required_capabilities = ["java"]
        req3.required_capabilities = ["python", "data_analysis"]
        
        python_requests = manager.get_help_requests(capability_filter=["python"])
        assert len(python_requests) == 2
        assert all(req.request_id in ["req1", "req3"] for req in python_requests)
    
    def test_get_my_requests(self, manager):
        """Test getting user's own requests."""
        req1 = HelpRequest(request_id="req1", requester_id="test_agent")
        req2 = HelpRequest(request_id="req2", requester_id="test_agent")
        
        manager.my_requests = {"req1": req1, "req2": req2}
        
        my_requests = manager.get_my_requests()
        assert len(my_requests) == 2
        
        # Test status filter
        req1.status = HelpRequestStatus.PENDING
        req2.status = HelpRequestStatus.COMPLETED
        
        pending_requests = manager.get_my_requests(status_filter=[HelpRequestStatus.PENDING])
        assert len(pending_requests) == 1
        assert pending_requests[0].request_id == "req1"
    
    def test_get_my_responses(self, manager):
        """Test getting user's own responses."""
        resp1 = HelpResponse(
            response_id="resp1",
            responder_id="test_agent", 
            request_id="req1"
        )
        resp2 = HelpResponse(
            response_id="resp2",
            responder_id="test_agent",
            request_id="req2"
        )
        
        manager.my_responses = {"resp1": resp1, "resp2": resp2}
        
        my_responses = manager.get_my_responses()
        assert len(my_responses) == 2
        
        # Test request filter
        req1_responses = manager.get_my_responses(request_id="req1")
        assert len(req1_responses) == 1
        assert req1_responses[0].response_id == "resp1"
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_requests(self, manager):
        """Test cleanup of expired requests."""
        # Create expired and active requests
        expired_req = HelpRequest(
            request_id="expired",
            requester_id="agent1",
            timeout_minutes=30
        )
        expired_req.created_at = datetime.now() - timedelta(minutes=31)
        
        active_req = HelpRequest(
            request_id="active",
            requester_id="agent2",
            timeout_minutes=30
        )
        
        manager.active_requests = {"expired": expired_req, "active": active_req}
        
        cleaned_count = await manager.cleanup_expired_requests()
        
        assert cleaned_count == 1
        assert "expired" not in manager.active_requests
        assert "active" in manager.active_requests
        assert expired_req.status == HelpRequestStatus.TIMEOUT
    
    def test_get_statistics(self, manager):
        """Test statistics generation."""
        # Add some test data
        req1 = HelpRequest(request_id="req1", requester_id="test_agent")
        req1.status = HelpRequestStatus.COMPLETED
        
        req2 = HelpRequest(request_id="req2", requester_id="test_agent")
        req2.status = HelpRequestStatus.PENDING
        
        resp1 = HelpResponse(
            response_id="resp1",
            responder_id="test_agent",
            request_id="other_req"
        )
        
        manager.my_requests = {"req1": req1, "req2": req2}
        manager.my_responses = {"resp1": resp1}
        manager.active_requests = {"req2": req2}
        
        stats = manager.get_statistics()
        
        assert stats["agent_id"] == "test_agent"
        assert stats["total_requests_made"] == 2
        assert stats["total_responses_given"] == 1
        assert stats["active_requests"] == 1
        assert stats["completed_requests"] == 1
        assert stats["success_rate"] == 1.0  # 1 completed out of 1 non-pending


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_create_help_request(self):
        """Test create_help_request function."""
        message = create_help_request(
            requester_id="agent1",
            required_capabilities=["python", "data_analysis"],
            description="Need help with data processing",
            timeout_minutes=45,
            priority=8
        )
        
        assert message.type == MessageType.HELP_WANTED
        assert message.source == "agent1"
        assert message.target is None  # Always broadcast
        assert message.priority == 8
        
        payload = message.payload
        assert payload["required_capabilities"] == ["python", "data_analysis"]
        assert payload["description"] == "Need help with data processing"
        assert payload["timeout_minutes"] == 45
        assert "request_id" in payload
    
    def test_create_help_response(self):
        """Test create_help_response function."""
        message = create_help_response(
            responder_id="agent2",
            target_agent="agent1",
            request_id="req-123",
            message="I can help with this!",
            capabilities_offered=["python", "debugging"],
            estimated_time_minutes=30,
            confidence_level=0.85
        )
        
        assert message.type == MessageType.HELP_RESPONSE
        assert message.source == "agent2"
        assert message.target == "agent1"
        assert message.priority == 6
        
        payload = message.payload
        assert payload["request_id"] == "req-123"
        assert payload["message"] == "I can help with this!"
        assert payload["capabilities_offered"] == ["python", "debugging"]
        assert payload["estimated_time_minutes"] == 30
        assert payload["confidence_level"] == 0.85
        assert "response_id" in payload


if __name__ == "__main__":
    pytest.main([__file__])