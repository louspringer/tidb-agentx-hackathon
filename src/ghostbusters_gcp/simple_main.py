#!/usr/bin/env python3
"""
Simplified Ghostbusters GCP Cloud Function
A working version that doesn't depend on external source code
"""

import logging
import uuid
from datetime import datetime
from typing import Any

import functions_framework  # type: ignore
from google.cloud import firestore  # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firestore client
db = firestore.Client()


def mock_ghostbusters_analysis(project_path: str) -> dict[str, Any]:
    """
    Mock Ghostbusters analysis for demonstration
    In a real implementation, this would call the actual Ghostbusters orchestrator
    """
    return {
        "confidence_score": 0.85,
        "delusions_detected": [
            {
                "type": "security",
                "description": "Potential subprocess usage detected",
                "severity": "medium",
            },
            {
                "type": "performance",
                "description": "IDE sluggishness detected",
                "severity": "low",
            },
        ],
        "recovery_actions": [
            {
                "action": "replace_subprocess",
                "description": "Replace subprocess calls with secure alternatives",
            },
            {
                "action": "optimize_ide",
                "description": "Apply IDE performance optimizations",
            },
        ],
        "errors": [],
        "timestamp": datetime.utcnow().isoformat(),
    }


@functions_framework.http
def ghostbusters_analyze(request):  # type: ignore
    """
    HTTP Cloud Function for Ghostbusters analysis

    Args:
        request: HTTP request object

    Returns:
        JSON response with analysis results
    """
    try:
        # Parse request
        request_json = request.get_json()
        if not request_json:
            return {
                "status": "error",
                "error_message": "Invalid JSON in request body",
            }, 400

        project_path = request_json.get("project_path", ".")
        analysis_id = str(uuid.uuid4())

        logger.info("Starting Ghostbusters analysis for project: %s", project_path)
        logger.info("Analysis ID: %s", analysis_id)

        # Run mock Ghostbusters analysis
        result = mock_ghostbusters_analysis(project_path)

        # Store results in Firestore
        doc_ref = db.collection("ghostbusters_results").document(analysis_id)
        doc_ref.set(
            {
                "analysis_id": analysis_id,
                "project_path": project_path,
                "confidence_score": result["confidence_score"],
                "delusions_detected": result["delusions_detected"],
                "recovery_actions": result["recovery_actions"],
                "errors": result["errors"],
                "timestamp": firestore.SERVER_TIMESTAMP,
                "status": "completed",
            },
        )

        logger.info(
            "Analysis completed successfully. Confidence: %s",
            result["confidence_score"],
        )

        return {
            "analysis_id": analysis_id,
            "confidence_score": result["confidence_score"],
            "delusions_detected": len(result["delusions_detected"]),
            "recovery_actions": len(result["recovery_actions"]),
            "errors": len(result["errors"]),
            "status": "completed",
            "dashboard_url": f"/dashboard/{analysis_id}",
        }

    except Exception as e:
        logger.error("Error during Ghostbusters analysis: %s", str(e))

        # Store error in Firestore
        error_id = str(uuid.uuid4())
        db.collection("ghostbusters_errors").document(error_id).set(
            {
                "error_id": error_id,
                "error_message": str(e),
                "timestamp": firestore.SERVER_TIMESTAMP,
                "status": "error",
            },
        )

        return {"status": "error", "error_message": str(e), "error_id": error_id}, 500


@functions_framework.http
def ghostbusters_status(request):  # type: ignore
    """
    HTTP Cloud Function to check analysis status

    Args:
        request: HTTP request object

    Returns:
        JSON response with status information
    """
    try:
        request_json = request.get_json()
        if not request_json:
            return {
                "status": "error",
                "error_message": "Invalid JSON in request body",
            }, 400

        analysis_id = request_json.get("analysis_id")
        if not analysis_id:
            return {"status": "error", "error_message": "Missing analysis_id"}, 400

        # Get status from Firestore
        doc_ref = db.collection("ghostbusters_results").document(analysis_id)
        doc = doc_ref.get()

        if not doc.exists:
            return {"status": "error", "error_message": "Analysis not found"}, 404

        data = doc.to_dict()
        return {
            "analysis_id": analysis_id,
            "status": data.get("status", "unknown"),
            "confidence_score": data.get("confidence_score", 0),
            "delusions_detected": len(data.get("delusions_detected", [])),
            "recovery_actions": len(data.get("recovery_actions", [])),
            "timestamp": data.get("timestamp"),
        }

    except Exception as e:
        logger.error("Error checking status: %s", str(e))
        return {"status": "error", "error_message": str(e)}, 500


@functions_framework.http
def ghostbusters_history(request):  # type: ignore
    """
    HTTP Cloud Function to get analysis history

    Args:
        request: HTTP request object

    Returns:
        JSON response with analysis history
    """
    try:
        # Get recent analyses from Firestore
        docs = (
            db.collection("ghostbusters_results")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(10)
            .stream()
        )

        history = []
        for doc in docs:
            data = doc.to_dict()
            history.append(
                {
                    "analysis_id": data.get("analysis_id"),
                    "project_path": data.get("project_path"),
                    "confidence_score": data.get("confidence_score"),
                    "delusions_detected": len(data.get("delusions_detected", [])),
                    "recovery_actions": len(data.get("recovery_actions", [])),
                    "timestamp": data.get("timestamp"),
                    "status": data.get("status"),
                },
            )

        return {
            "history": history,
            "total_analyses": len(history),
        }

    except Exception as e:
        logger.error("Error getting history: %s", str(e))
        return {"status": "error", "error_message": str(e)}, 500
