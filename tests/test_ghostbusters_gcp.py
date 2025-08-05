#!/usr/bin/env python3
"""
Tests for Ghostbusters GCP Cloud Functions
"""

from unittest.mock import Mock, patch

import pytest

from src.ghostbusters_gcp.main import (
    ghostbusters_analyze,
    ghostbusters_history,
    ghostbusters_status,
)


class MockRequest:
    """Mock HTTP request for testing"""

    def __init__(self, data: dict):
        self.data = data

    def get_json(self):
        return self.data


class MockFirestoreDoc:
    """Mock Firestore document"""

    def __init__(self, data: dict):
        self.data = data

    def exists(self):
        return True

    def to_dict(self):
        return self.data


class MockFirestoreCollection:
    """Mock Firestore collection"""

    def __init__(self, docs: list):
        self.docs = docs

    def document(self, doc_id: str):
        return Mock()

    def order_by(self, field: str, direction=None):
        return self

    def limit(self, limit: int):
        return self

    def stream(self):
        return [MockFirestoreDoc(doc) for doc in self.docs]


@pytest.fixture
def mock_firestore():
    """Mock Firestore client"""
    with patch("src.ghostbusters_gcp.main.db") as mock_db:
        mock_db.collection.return_value = MockFirestoreCollection([])
        yield mock_db


@pytest.fixture
def mock_ghostbusters_result():
    """Mock Ghostbusters result"""
    return Mock(
        confidence_score=0.95,
        delusions_detected=[{"type": "security", "file": "test.py"}],
        recovery_actions=[{"action": "fix", "file": "test.py"}],
        errors=[],
    )


def test_ghostbusters_analyze_success(mock_firestore, mock_ghostbusters_result):
    """Test successful analysis"""
    with patch("src.ghostbusters_gcp.main.asyncio.run") as mock_run:
        mock_run.return_value = mock_ghostbusters_result

        request = MockRequest({"project_path": "test_project"})

        result = ghostbusters_analyze(request)

        assert result["status"] == "completed"
        assert "analysis_id" in result
        assert result["confidence_score"] == 0.95
        assert result["delusions_detected"] == 1
        assert result["recovery_actions"] == 1
        assert result["errors"] == 0


def test_ghostbusters_analyze_invalid_json():
    """Test analysis with invalid JSON"""
    request = Mock()
    request.get_json.return_value = None

    result, status_code = ghostbusters_analyze(request)

    assert status_code == 400
    assert result["status"] == "error"
    assert "Invalid JSON" in result["error_message"]


def test_ghostbusters_analyze_error(mock_firestore):
    """Test analysis with error"""
    with patch("src.ghostbusters_gcp.main.asyncio.run") as mock_run:
        mock_run.side_effect = Exception("Test error")

        request = MockRequest({"project_path": "test_project"})

        result, status_code = ghostbusters_analyze(request)

        assert status_code == 500
        assert result["status"] == "error"
        assert "Test error" in result["error_message"]
        assert "error_id" in result


def test_ghostbusters_status_success(mock_firestore):
    """Test status check"""
    analysis_data = {
        "analysis_id": "test-id",
        "status": "completed",
        "confidence_score": 0.95,
        "delusions_detected": [{"type": "security"}],
        "recovery_actions": [{"action": "fix"}],
        "errors": [],
        "timestamp": "2024-01-01T00:00:00Z",
    }

    mock_doc = MockFirestoreDoc(analysis_data)
    mock_firestore.collection.return_value.document.return_value.get.return_value = (
        mock_doc
    )

    request = MockRequest({"analysis_id": "test-id"})

    result = ghostbusters_status(request)

    assert result["analysis_id"] == "test-id"
    assert result["status"] == "completed"
    assert result["confidence_score"] == 0.95
    assert result["delusions_detected"] == 1
    assert result["recovery_actions"] == 1
    assert result["errors"] == 0


def test_ghostbusters_status_not_found(mock_firestore):
    """Test status check for non-existent analysis"""
    mock_doc = Mock()
    mock_doc.exists.return_value = False
    mock_firestore.collection.return_value.document.return_value.get.return_value = (
        mock_doc
    )

    request = MockRequest({"analysis_id": "non-existent-id"})

    result, status_code = ghostbusters_status(request)

    assert status_code == 404
    assert result["status"] == "error"
    assert "not found" in result["error_message"]


def test_ghostbusters_status_missing_id():
    """Test status check with missing analysis_id"""
    request = MockRequest({})

    result, status_code = ghostbusters_status(request)

    assert status_code == 400
    assert result["status"] == "error"
    assert "analysis_id is required" in result["error_message"]


def test_ghostbusters_history_success(mock_firestore):
    """Test history retrieval"""
    history_data = [
        {
            "analysis_id": "test-1",
            "project_path": "project-1",
            "confidence_score": 0.95,
            "delusions_detected": [{"type": "security"}],
            "recovery_actions": [{"action": "fix"}],
            "errors": [],
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "completed",
        },
        {
            "analysis_id": "test-2",
            "project_path": "project-2",
            "confidence_score": 0.85,
            "delusions_detected": [],
            "recovery_actions": [],
            "errors": [],
            "timestamp": "2024-01-02T00:00:00Z",
            "status": "completed",
        },
    ]

    mock_firestore.collection.return_value = MockFirestoreCollection(history_data)

    request = MockRequest({"limit": 5})

    result = ghostbusters_history(request)

    assert result["status"] == "success"
    assert len(result["analyses"]) == 2
    assert result["count"] == 2
    assert result["analyses"][0]["analysis_id"] == "test-1"
    assert result["analyses"][1]["analysis_id"] == "test-2"


def test_ghostbusters_history_default_limit(mock_firestore):
    """Test history with default limit"""
    mock_firestore.collection.return_value = MockFirestoreCollection([])

    request = MockRequest({})

    result = ghostbusters_history(request)

    assert result["status"] == "success"
    assert result["count"] == 0
    assert result["analyses"] == []


if __name__ == "__main__":
    pytest.main([__file__])
