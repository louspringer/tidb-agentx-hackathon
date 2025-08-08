#!/usr/bin/env python3
"""
Test Ghostbusters GCP Cloud Functions

Tests are designed to be ahead of implementation as per model requirements.
"""

from unittest.mock import Mock, patch

import pytest

from src.ghostbusters_gcp.main import (
    ghostbusters_analyze,
    ghostbusters_history,
    ghostbusters_status,
)


class MockRequest:
    """Mock request object for testing Cloud Functions"""

    def __init__(self, data: dict):
        self.data = data

    def get_json(self):
        return self.data if self.data else None


@pytest.fixture
def mock_firestore():
    """Mock Firestore client"""
    with patch("src.ghostbusters_gcp.main.db") as mock_db:
        yield mock_db


def test_ghostbusters_status_not_found(mock_firestore):
    """Test status check for non-existent analysis"""
    # Mock the entire Firestore chain
    mock_doc = Mock()
    mock_doc.exists = False  # Direct attribute, not method
    mock_doc.to_dict.return_value = {}

    mock_firestore.collection.return_value.document.return_value.get.return_value = (
        mock_doc
    )

    request = MockRequest({"analysis_id": "non-existent-id"})
    result, status_code = ghostbusters_status(request)

    assert status_code == 404
    assert result["status"] == "error"
    assert "Analysis not found" in result["error_message"]


def test_ghostbusters_status_missing_id():
    """Test status check with missing analysis_id"""
    request = MockRequest({"other_field": "value"})  # Dict with no analysis_id key
    result, status_code = ghostbusters_status(request)

    assert status_code == 400
    assert result["status"] == "error"
    assert "Missing analysis_id" in result["error_message"]


def test_ghostbusters_status_success(mock_firestore):
    """Test status check"""
    # Mock the entire Firestore chain
    mock_doc = Mock()
    mock_doc.exists = True  # Direct attribute, not method
    mock_doc.to_dict.return_value = {
        "analysis_id": "test-id",
        "status": "completed",
        "confidence_score": 0.95,
        "delusions_detected": [{"type": "security"}],
        "recovery_actions": [{"action": "fix"}],
        "timestamp": "2024-01-01T00:00:00Z",
    }

    mock_firestore.collection.return_value.document.return_value.get.return_value = (
        mock_doc
    )

    request = MockRequest({"analysis_id": "test-id"})
    result, status_code = ghostbusters_status(request)

    assert status_code == 200
    assert result["analysis_id"] == "test-id"
    assert result["status"] == "completed"
    assert result["confidence_score"] == 0.95
    assert result["delusions_detected"] == 1
    assert result["recovery_actions"] == 1


def test_ghostbusters_analyze_success(mock_firestore):
    """Test successful analysis"""
    with patch("src.ghostbusters_gcp.main.mock_ghostbusters_analysis") as mock_run:
        mock_run.return_value = {
            "confidence_score": 0.95,
            "delusions_detected": [{"type": "security"}],
            "recovery_actions": [{"action": "fix"}],
            "errors": [],
        }

        request = MockRequest({"project_path": "test_project"})
        result = ghostbusters_analyze(request)

        assert result["status"] == "completed"
        assert "analysis_id" in result
        assert result["confidence_score"] == 0.95


def test_ghostbusters_history_success(mock_firestore):
    """Test history retrieval"""
    # Mock: return empty list for simplicity
    mock_firestore.collection.return_value.order_by.return_value.limit.return_value.stream.return_value = (
        []
    )

    request = MockRequest({"limit": 5})
    result = ghostbusters_history(request)

    assert result["status"] == "success"
    assert "analyses" in result
    assert result["count"] == 0
