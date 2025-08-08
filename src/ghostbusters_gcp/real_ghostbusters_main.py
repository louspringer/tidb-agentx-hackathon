#!/usr/bin/env python3
"""
Real Ghostbusters GCP Cloud Functions
Phase 2: Integration with actual Ghostbusters multi-agent system
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import functions_framework  # type: ignore
from google.cloud import firestore, pubsub_v1  # type: ignore

# Import real Ghostbusters
from src.ghostbusters.ghostbusters_orchestrator import run_ghostbusters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firestore client
db = firestore.Client()

# Initialize Pub/Sub publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(
    "aardvark-linkedin-grepper",
    "ghostbusters-analysis-updates",
)


def authenticate_request(request) -> str:  # type: ignore
    """Simple authentication for demo purposes"""
    try:
        # Get the Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # In a real app, you'd verify the token
            return "demo-user-123"
        return "demo-user-123"  # Default for demo
    except Exception as e:
        logger.warning("Authentication failed, using demo user: %s", str(e))
        return "demo-user-123"


def publish_update(analysis_id: str, status: str, data: dict) -> None:
    """Publish real-time update to Pub/Sub"""
    try:
        message = {
            "analysis_id": analysis_id,
            "status": status,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "data": data,
        }

        # Publish to Pub/Sub
        future = publisher.publish(
            topic_path,
            json.dumps(message).encode("utf-8"),
            analysis_id=analysis_id,
            status=status,
        )

        logger.info("Published update for analysis %s: %s", analysis_id, status)
        return future.result()  # type: ignore
    except Exception as e:
        logger.error("Failed to publish update: %s", str(e))


def convert_ghostbusters_result(result) -> dict[str, Any]:  # type: ignore
    """Convert Ghostbusters result to Cloud Function response format"""
    return {
        "confidence_score": result.confidence_score,
        "delusions_detected": result.delusions_detected,
        "recovery_actions": result.recovery_actions,
        "errors": result.errors,
        "warnings": result.warnings,
        "metadata": result.metadata,
        "validation_results": result.validation_results,
        "recovery_results": result.recovery_results,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }


@functions_framework.http
def ghostbusters_analyze_real(request):  # type: ignore
    """
    Real Ghostbusters HTTP Cloud Function with actual multi-agent analysis
    """
    try:
        # Authenticate user
        user_id = authenticate_request(request)

        # Parse request
        request_json = request.get_json()
        if not request_json:
            return {
                "status": "error",
                "error_message": "Invalid JSON in request body",
            }, 400

        project_path = request_json.get("project_path", ".")
        analysis_id = str(uuid.uuid4())

        logger.info(
            "Starting REAL Ghostbusters analysis for project: %s",
            project_path,
        )
        logger.info("Analysis ID: %s, User ID: %s", analysis_id, user_id)

        # Publish start update
        publish_update(analysis_id, "started", {"project_path": project_path})

        # Run REAL Ghostbusters analysis
        logger.info("Running Ghostbusters orchestrator...")
        result = asyncio.run(run_ghostbusters(project_path))
        logger.info("Ghostbusters analysis completed!")

        # Convert result to response format
        analysis_result = convert_ghostbusters_result(result)

        # Store results in Firestore
        doc_ref = db.collection("ghostbusters_results").document(analysis_id)
        doc_ref.set(
            {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "project_path": project_path,
                "confidence_score": analysis_result["confidence_score"],
                "delusions_detected": analysis_result["delusions_detected"],
                "recovery_actions": analysis_result["recovery_actions"],
                "errors": analysis_result["errors"],
                "warnings": analysis_result["warnings"],
                "metadata": analysis_result["metadata"],
                "validation_results": analysis_result["validation_results"],
                "recovery_results": analysis_result["recovery_results"],
                "timestamp": firestore.SERVER_TIMESTAMP,
                "status": "completed",
            },
        )

        # Publish completion update
        publish_update(
            analysis_id,
            "completed",
            {
                "confidence_score": analysis_result["confidence_score"],
                "delusions_detected": len(analysis_result["delusions_detected"]),
                "recovery_actions": len(analysis_result["recovery_actions"]),
                "errors": len(analysis_result["errors"]),
                "warnings": len(analysis_result["warnings"]),
            },
        )

        logger.info(
            "Real Ghostbusters analysis completed successfully. Confidence: %s",
            analysis_result["confidence_score"],
        )

        return {
            "analysis_id": analysis_id,
            "confidence_score": analysis_result["confidence_score"],
            "delusions_detected": len(analysis_result["delusions_detected"]),
            "recovery_actions": len(analysis_result["recovery_actions"]),
            "errors": len(analysis_result["errors"]),
            "warnings": len(analysis_result["warnings"]),
            "status": "completed",
            "dashboard_url": f"https://ghostbusters-dashboard-1077539189076.us-central1.run.app/dashboard/{analysis_id}",
            "real_time_updates": True,
            "real_ghostbusters": True,
        }

    except Exception as e:
        logger.error("Error during real Ghostbusters analysis: %s", str(e))

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
def ghostbusters_progress_real(request):  # type: ignore
    """
    HTTP Cloud Function to get real-time progress updates for real Ghostbusters
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

        # Get progress from Firestore
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
            "errors": len(data.get("errors", [])),
            "warnings": len(data.get("warnings", [])),
            "timestamp": data.get("timestamp"),
            "real_time_updates": True,
            "real_ghostbusters": True,
        }

    except Exception as e:
        logger.error("Error checking progress: %s", str(e))
        return {"status": "error", "error_message": str(e)}, 500


@functions_framework.http
def ghostbusters_user_analyses_real(request):  # type: ignore
    """
    HTTP Cloud Function to get user's real Ghostbusters analysis history
    """
    try:
        # Authenticate user
        user_id = authenticate_request(request)

        # Get user's analyses from Firestore
        docs = (
            db.collection("ghostbusters_results")
            .where("user_id", "==", user_id)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(20)
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
                    "warnings": len(data.get("warnings", [])),
                    "timestamp": data.get("timestamp"),
                    "status": data.get("status"),
                    "real_ghostbusters": data.get("real_ghostbusters", False),
                },
            )

        return {
            "user_id": user_id,
            "analyses": analyses,
            "total_analyses": len(analyses),
            "real_time_updates": True,
            "real_ghostbusters": True,
        }

    except Exception as e:
        logger.error("Error getting user analyses: %s", str(e))
        return {"status": "error", "error_message": str(e)}, 500
