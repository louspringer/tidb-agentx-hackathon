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


class TestHelpSystemIntegration:
    """Test help system integration scenarios."""
    
    @pytest.fixture
    def mock_bus_client(self):
        """Create mock bus client with more realistic behavior."""
        mock_client = AsyncMock()
        mock_client.agent_id = "integration_agent"
        mock_client.send_message = AsyncMock(return_value=True)
        return mock_client
    
    @pytest.fixture
    def manager(self, mock_bus_client):
        """Create HelpSystemManager instance."""
        return HelpSystemManager(mock_bus_client)
    
    @pytest.mark.asyncio
    async def test_full_help_request_lifecycle(self, manager):
        """Test complete help request lifecycle from creation to completion."""
        # Step 1: Request help
        request_id = await manager.request_help(
            required_capabilities=["python", "data_analysis"],
            description="Need help with complex data processing task",
            timeout_minutes=60,
            priority=7
        )
        
        assert request_id is not None
        request = manager.my_requests[request_id]
        assert request.status == HelpRequestStatus.PENDING
        
        # Step 2: Simulate receiving responses
        response1 = HelpResponse(
            response_id="resp1",
            responder_id="helper1",
            request_id=request_id,
            message="I can help with Python!",
            capabilities_offered=["python"],
            confidence_level=0.7,
            estimated_time_minutes=45
        )
        
        response2 = HelpResponse(
            response_id="resp2", 
            responder_id="helper2",
            request_id=request_id,
            message="I'm an expert in both Python and data analysis!",
            capabilities_offered=["python", "data_analysis", "machine_learning"],
            confidence_level=0.9,
            estimated_time_minutes=30
        )
        
        request.add_response(response1)
        request.add_response(response2)
        
        assert request.status == HelpRequestStatus.RESPONDED
        assert len(request.responses) == 2
        
        # Step 3: Select best helper
        success = await manager.select_helper(request_id, "helper2")
        assert success is True
        assert request.selected_responder == "helper2"
        assert request.status == HelpRequestStatus.IN_PROGRESS
        
        # Step 4: Complete the request
        success = await manager.complete_help_request(
            request_id,
            success=True,
            result="Data processing completed successfully with 95% accuracy"
        )
        
        assert success is True
        assert request.status == HelpRequestStatus.COMPLETED
        assert "95% accuracy" in request.completion_result
        
        # Verify all messages were sent
        assert manager.bus_client.send_message.call_count == 3  # request, selection, completion
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self, manager):
        """Test handling multiple concurrent help requests."""
        # Create multiple requests concurrently
        request_tasks = []
        for i in range(5):
            task = manager.request_help(
                required_capabilities=[f"skill_{i}"],
                description=f"Need help with task {i}",
                priority=i + 1
            )
            request_tasks.append(task)
        
        request_ids = await asyncio.gather(*request_tasks)
        
        # All requests should succeed
        assert all(req_id is not None for req_id in request_ids)
        assert len(manager.my_requests) == 5
        
        # Verify requests have different priorities
        priorities = [manager.my_requests[req_id].priority for req_id in request_ids]
        assert sorted(priorities) == [1, 2, 3, 4, 5]
    
    @pytest.mark.asyncio
    async def test_request_timeout_handling(self, manager):
        """Test automatic timeout handling for requests."""
        # Create request with very short timeout
        request_id = await manager.request_help(
            required_capabilities=["test"],
            description="Test timeout",
            timeout_minutes=0.01  # 0.6 seconds
        )
        
        request = manager.my_requests[request_id]
        assert not request.is_expired()
        
        # Wait for timeout
        await asyncio.sleep(0.1)
        
        # Request should now be expired
        assert request.is_expired()
        
        # Cleanup should mark it as timed out
        cleaned = await manager.cleanup_expired_requests()
        assert cleaned == 1
        assert request.status == HelpRequestStatus.TIMEOUT
    
    @pytest.mark.asyncio
    async def test_response_ranking_algorithm(self, manager):
        """Test response ranking and selection algorithms."""
        # Create request
        request_id = await manager.request_help(
            required_capabilities=["python", "data_analysis"],
            description="Complex data task"
        )
        
        request = manager.my_requests[request_id]
        
        # Add responses with different qualities
        responses = [
            HelpResponse(
                response_id="resp1",
                responder_id="novice",
                request_id=request_id,
                message="I'll try to help",
                capabilities_offered=["python"],
                confidence_level=0.5,
                estimated_time_minutes=120
            ),
            HelpResponse(
                response_id="resp2",
                responder_id="expert",
                request_id=request_id,
                message="I'm highly experienced in this area",
                capabilities_offered=["python", "data_analysis", "machine_learning"],
                confidence_level=0.95,
                estimated_time_minutes=30
            ),
            HelpResponse(
                response_id="resp3",
                responder_id="specialist",
                request_id=request_id,
                message="This is exactly my specialty",
                capabilities_offered=["python", "data_analysis"],
                confidence_level=0.9,
                estimated_time_minutes=45
            )
        ]
        
        for response in responses:
            request.add_response(response)
        
        # Get best responses (should be ranked by quality)
        best_responses = request.get_best_responses(max_responses=3)
        
        assert len(best_responses) == 3
        # Expert should be first (highest confidence + most capabilities)
        assert best_responses[0].responder_id == "expert"
        # Specialist should be second
        assert best_responses[1].responder_id == "specialist"
        # Novice should be last
        assert best_responses[2].responder_id == "novice"
    
    @pytest.mark.asyncio
    async def test_duplicate_response_prevention(self, manager):
        """Test prevention of duplicate responses from same agent."""
        # Add a request to respond to
        request = HelpRequest(
            request_id="test_req",
            requester_id="other_agent",
            required_capabilities=["python"]
        )
        manager.active_requests["test_req"] = request
        
        # First response should succeed
        response_id1 = await manager.respond_to_help(
            request_id="test_req",
            message="First response"
        )
        assert response_id1 is not None
        
        # Second response from same agent should fail
        response_id2 = await manager.respond_to_help(
            request_id="test_req", 
            message="Second response"
        )
        assert response_id2 is None
        
        # Only one response should be recorded
        assert len(manager.my_responses) == 1
    
    @pytest.mark.asyncio
    async def test_message_handling_integration(self, manager):
        """Test integration with message handling system."""
        # Test handling help wanted message
        help_wanted_msg = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="remote_agent",
            payload={
                "request_id": "remote_req_123",
                "required_capabilities": ["python", "web"],
                "description": "Need help with web scraping",
                "timeout_minutes": 45,
                "priority": 6,
                "created_at": datetime.now().isoformat()
            }
        )
        
        await manager.handle_help_message(help_wanted_msg)
        
        # Request should be added to active requests
        assert "remote_req_123" in manager.active_requests
        request = manager.active_requests["remote_req_123"]
        assert request.requester_id == "remote_agent"
        assert request.required_capabilities == ["python", "web"]
        assert request.description == "Need help with web scraping"
        
        # Test handling help response message
        help_response_msg = BeastModeMessage(
            type=MessageType.HELP_RESPONSE,
            source="helper_agent",
            target="integration_agent",
            payload={
                "response_id": "helper_resp_456",
                "request_id": "my_request_789",
                "message": "I can help with that!",
                "capabilities_offered": ["python", "web", "scraping"],
                "confidence_level": 0.8,
                "estimated_time_minutes": 60,
                "created_at": datetime.now().isoformat()
            }
        )
        
        # First add the request this is responding to
        my_request = HelpRequest(
            request_id="my_request_789",
            requester_id="integration_agent",
            required_capabilities=["python"]
        )
        manager.my_requests["my_request_789"] = my_request
        
        await manager.handle_help_message(help_response_msg)
        
        # Response should be added to the request
        assert len(my_request.responses) == 1
        response = my_request.responses[0]
        assert response.responder_id == "helper_agent"
        assert response.message == "I can help with that!"
        assert my_request.status == HelpRequestStatus.RESPONDED


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases in help system."""
    
    @pytest.fixture
    def manager(self):
        """Create manager with mock bus client."""
        mock_client = AsyncMock()
        mock_client.agent_id = "error_test_agent"
        return HelpSystemManager(mock_client)
    
    @pytest.mark.asyncio
    async def test_network_failure_handling(self, manager):
        """Test handling of network failures during operations."""
        # Simulate network failure
        manager.bus_client.send_message = AsyncMock(return_value=False)
        
        # Request help should fail gracefully
        request_id = await manager.request_help(
            required_capabilities=["test"],
            description="Test request"
        )
        
        assert request_id is None
        assert len(manager.my_requests) == 0
        
        # Response should also fail gracefully
        request = HelpRequest(
            request_id="test_req",
            requester_id="other_agent",
            required_capabilities=["test"]
        )
        manager.active_requests["test_req"] = request
        
        response_id = await manager.respond_to_help(
            request_id="test_req",
            message="Test response"
        )
        
        assert response_id is None
        assert len(manager.my_responses) == 0
    
    @pytest.mark.asyncio
    async def test_malformed_message_handling(self, manager):
        """Test handling of malformed messages."""
        # Test message with missing required fields
        bad_message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="bad_agent",
            payload={"description": "Missing required fields"}
        )
        
        # Should not crash
        await manager.handle_help_message(bad_message)
        
        # No request should be created
        assert len(manager.active_requests) == 0
    
    def test_invalid_request_operations(self, manager):
        """Test operations on invalid or non-existent requests."""
        # Test operations on non-existent request
        request = manager.get_help_request("nonexistent")
        assert request is None
        
        # Test selecting helper for non-existent request
        async def test_select():
            success = await manager.select_helper("nonexistent", "helper")
            assert success is False
        
        asyncio.run(test_select())
    
    def test_request_state_validation(self, manager):
        """Test request state validation and transitions."""
        request = HelpRequest(
            request_id="state_test",
            requester_id="test_agent",
            required_capabilities=["test"]
        )
        
        # Test invalid state transitions
        request.status = HelpRequestStatus.COMPLETED
        
        # Should not be able to add responses to completed request
        response = HelpResponse(
            response_id="resp1",
            responder_id="helper",
            request_id="state_test",
            message="Late response"
        )
        
        result = request.add_response(response)
        assert result is False
        assert len(request.responses) == 0
        
        # Should not be able to select responder for completed request
        result = request.select_responder("helper")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_concurrent_request_modifications(self, manager):
        """Test concurrent modifications to requests."""
        request = HelpRequest(
            request_id="concurrent_test",
            requester_id="test_agent",
            required_capabilities=["test"]
        )
        manager.my_requests["concurrent_test"] = request
        
        async def add_response(responder_id):
            response = HelpResponse(
                response_id=f"resp_{responder_id}",
                responder_id=responder_id,
                request_id="concurrent_test",
                message=f"Response from {responder_id}"
            )
            return request.add_response(response)
        
        # Try to add multiple responses concurrently
        tasks = [add_response(f"helper_{i}") for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed since they're from different responders
        assert all(results)
        assert len(request.responses) == 5
    
    def test_memory_cleanup_on_completion(self, manager):
        """Test that completed requests are properly cleaned up."""
        # Add many completed requests
        for i in range(100):
            request = HelpRequest(
                request_id=f"completed_{i}",
                requester_id="test_agent",
                required_capabilities=["test"]
            )
            request.status = HelpRequestStatus.COMPLETED
            request.completed_at = datetime.now() - timedelta(hours=1)
            manager.my_requests[f"completed_{i}"] = request
        
        # Add some active requests
        for i in range(10):
            request = HelpRequest(
                request_id=f"active_{i}",
                requester_id="test_agent",
                required_capabilities=["test"]
            )
            manager.my_requests[f"active_{i}"] = request
        
        initial_count = len(manager.my_requests)
        assert initial_count == 110
        
        # Cleanup old completed requests (this would be called by a background task)
        manager.cleanup_old_requests(max_age_hours=0.5)
        
        # Only active requests should remain
        remaining_count = len(manager.my_requests)
        assert remaining_count == 10
        
        # Verify only active requests remain
        for request_id in manager.my_requests:
            assert request_id.startswith("active_")


class TestPerformanceAndScaling:
    """Test performance characteristics and scaling behavior."""
    
    @pytest.fixture
    def manager(self):
        """Create manager for performance testing."""
        mock_client = AsyncMock()
        mock_client.agent_id = "perf_test_agent"
        mock_client.send_message = AsyncMock(return_value=True)
        return HelpSystemManager(mock_client)
    
    @pytest.mark.asyncio
    async def test_large_number_of_requests(self, manager):
        """Test handling large numbers of help requests."""
        import time
        
        # Create many requests
        start_time = time.time()
        request_ids = []
        
        for i in range(1000):
            request_id = await manager.request_help(
                required_capabilities=[f"skill_{i % 10}"],
                description=f"Request {i}",
                priority=(i % 10) + 1
            )
            request_ids.append(request_id)
        
        creation_time = time.time() - start_time
        
        # Should complete in reasonable time (less than 1 second)
        assert creation_time < 1.0
        assert len(manager.my_requests) == 1000
        assert all(req_id is not None for req_id in request_ids)
    
    @pytest.mark.asyncio
    async def test_large_number_of_responses(self, manager):
        """Test handling large numbers of responses to a single request."""
        # Create a request
        request_id = await manager.request_help(
            required_capabilities=["popular_skill"],
            description="Very popular request"
        )
        
        request = manager.my_requests[request_id]
        
        # Add many responses
        import time
        start_time = time.time()
        
        for i in range(500):
            response = HelpResponse(
                response_id=f"mass_resp_{i}",
                responder_id=f"helper_{i}",
                request_id=request_id,
                message=f"Response {i}",
                confidence_level=0.5 + (i % 50) / 100.0  # Vary confidence
            )
            request.add_response(response)
        
        response_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert response_time < 1.0
        assert len(request.responses) == 500
        
        # Test ranking performance
        start_time = time.time()
        best_responses = request.get_best_responses(max_responses=10)
        ranking_time = time.time() - start_time
        
        # Ranking should be fast even with many responses
        assert ranking_time < 0.1
        assert len(best_responses) == 10
        
        # Verify ranking quality (higher confidence should be ranked higher)
        confidences = [resp.confidence_level for resp in best_responses]
        assert confidences == sorted(confidences, reverse=True)
    
    def test_memory_usage_with_large_datasets(self, manager):
        """Test memory usage doesn't grow excessively."""
        import gc
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Create and process many requests
        for batch in range(10):
            # Create batch of requests
            for i in range(100):
                request = HelpRequest(
                    request_id=f"batch_{batch}_req_{i}",
                    requester_id="test_agent",
                    required_capabilities=["test"]
                )
                
                # Add responses
                for j in range(10):
                    response = HelpResponse(
                        response_id=f"batch_{batch}_req_{i}_resp_{j}",
                        responder_id=f"helper_{j}",
                        request_id=request.request_id,
                        message=f"Response {j}"
                    )
                    request.add_response(response)
                
                # Complete request
                request.complete(success=True, result="Completed")
            
            # Simulate cleanup of old requests
            if batch > 2:  # Keep some history
                # In real implementation, this would be automatic cleanup
                pass
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Object growth should be reasonable
        object_growth = final_objects - initial_objects
        assert object_growth < 5000  # Reasonable threshold for test overhead


if __name__ == "__main__":
    pytest.main([__file__])