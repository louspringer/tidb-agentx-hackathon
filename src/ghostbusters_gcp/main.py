#!/usr/bin/env python3
"""
Ghostbusters GCP Cloud Function
Main entry point for Ghostbusters analysis on Google Cloud Functions
"""

# Import Ghostbusters core
import asyncio
import logging
import uuid

import functions_framework
from google.cloud import firestore

from src.ghostbusters.ghostbusters_orchestrator import run_ghostbusters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firestore client
db = firestore.Client()


@functions_framework.http
def ghostbusters_analyze(request):
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

        # Run Ghostbusters analysis (async)
        result = asyncio.run(run_ghostbusters(project_path))

        # Store results in Firestore
        doc_ref = db.collection("ghostbusters_results").document(analysis_id)
        doc_ref.set(
            {
                "analysis_id": analysis_id,
                "project_path": project_path,
                "confidence_score": result.confidence_score,
                "delusions_detected": result.delusions_detected,
                "recovery_actions": result.recovery_actions,
                "errors": result.errors,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "status": "completed",
            },
        )

        logger.info(
            "Analysis completed successfully. Confidence: %s",
            result.confidence_score,
        )

        return {
            "analysis_id": analysis_id,
            "confidence_score": result.confidence_score,
            "delusions_detected": len(result.delusions_detected),
            "recovery_actions": len(result.recovery_actions),
            "errors": len(result.errors),
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
def ghostbusters_status(request):
    """
    HTTP Cloud Function to check analysis status

    Args:
        request: HTTP request object

    Returns:
        JSON response with analysis status
    """
    try:
        # Parse request
        request_json = request.get_json()
        if not request_json:
            return {
                "status": "error",
                "error_message": "Invalid JSON in request body",
            }, 400

        analysis_id = request_json.get("analysis_id")
        if not analysis_id:
            return {"status": "error", "error_message": "analysis_id is required"}, 400

        # Get analysis status from Firestore
        doc_ref = db.collection("ghostbusters_results").document(analysis_id)
        doc = doc_ref.get()

        if not doc.exists:
            return {
                "status": "error",
                "error_message": f"Analysis {analysis_id} not found",
            }, 404

        data = doc.to_dict()

        return {
            "analysis_id": analysis_id,
            "status": data.get("status", "unknown"),
            "confidence_score": data.get("confidence_score"),
            "delusions_detected": len(data.get("delusions_detected", [])),
            "recovery_actions": len(data.get("recovery_actions", [])),
            "errors": len(data.get("errors", [])),
            "timestamp": data.get("timestamp"),
            "dashboard_url": f"/dashboard/{analysis_id}",
        }

    except Exception as e:
        logger.error("Error checking analysis status: %s", str(e))
        return {"status": "error", "error_message": str(e)}, 500


@functions_framework.http
def ghostbusters_history(request):
    """
    HTTP Cloud Function to get analysis history

    Args:
        request: HTTP request object

    Returns:
        JSON response with analysis history
    """
    try:
        # Parse request
        request_json = request.get_json() or {}
        limit = request_json.get("limit", 10)

        # Get recent analyses from Firestore
        docs = (
            db.collection("ghostbusters_results")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )

        analyses = []
        for doc in docs:
            data = doc.to_dict()
            analyses.append(
                {
                    "analysis_id": data.get("analysis_id"),
                    "project_path": data.get("project_path"),
                    "confidence_score": data.get("confidence_score"),
                    "delusions_detected": len(data.get("delusions_detected", [])),
                    "recovery_actions": len(data.get("recovery_actions", [])),
                    "errors": len(data.get("errors", [])),
                    "timestamp": data.get("timestamp"),
                    "status": data.get("status"),
                    "dashboard_url": f"/dashboard/{data.get('analysis_id')}",
                },
            )

        return {"status": "success", "analyses": analyses, "count": len(analyses)}

    except Exception as e:
        logger.error("Error getting analysis history: %s", str(e))
        return {"status": "error", "error_message": str(e)}, 500
