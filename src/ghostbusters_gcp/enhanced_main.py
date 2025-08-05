#!/usr/bin/env python3
"""
Enhanced Ghostbusters GCP Cloud Functions
Phase 2: Real-time updates, authentication, and advanced features
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

import functions_framework
from firebase_admin import auth, initialize_app
from google.cloud import firestore, pubsub_v1

# Initialize Firebase Admin SDK
try:
    initialize_app()
except ValueError:
    # App already initialized
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firestore client
db = firestore.Client()

# Initialize Pub/Sub client for real-time updates
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("ghostbusters-project", "analysis-updates")


def authenticate_request(request) -> Optional[str]:
    """Authenticate request using Firebase Auth"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        return decoded_token["uid"]
    except Exception as e:
        logger.warning("Authentication failed: %s", str(e))
        return None


def check_rate_limit(user_id: str) -> bool:
    """Check rate limiting for user"""
    try:
        # Get user's recent requests
        recent_requests = db.collection("rate_limits").document(user_id).get()

        if recent_requests.exists:
            data = recent_requests.to_dict()
            request_count = data.get("count", 0)
            last_reset = data.get("last_reset")

            # Reset counter if more than 1 hour ago
            if last_reset and datetime.fromisoformat(
                last_reset,
            ) < datetime.now() - timedelta(hours=1):
                request_count = 0
                last_reset = datetime.now().isoformat()
            else:
                request_count += 1
                last_reset = data.get("last_reset", datetime.now().isoformat())
        else:
            request_count = 1
            last_reset = datetime.now().isoformat()

        # Update rate limit
        db.collection("rate_limits").document(user_id).set(
            {"count": request_count, "last_reset": last_reset, "user_id": user_id},
        )

        # Allow up to 10 requests per hour
        return request_count <= 10
    except Exception as e:
        logger.error("Rate limit check failed: %s", str(e))
        return True  # Allow on error


def validate_and_parse_request(request) -> dict[str, Any]:
    """Validate and parse request data"""
    request_json = request.get_json()
    if not request_json:
        raise ValueError("Invalid JSON in request body")

    project_path = request_json.get("project_path")
    if not project_path:
        raise ValueError("project_path is required")

    return {
        "project_path": project_path,
        "options": request_json.get("options", {}),
        "priority": request_json.get("priority", "normal"),
    }


def start_progress_tracking(analysis_id: str, user_id: str) -> None:
    """Start progress tracking for analysis"""
    try:
        # Create progress document
        db.collection("analysis_progress").document(analysis_id).set(
            {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "status": "started",
                "progress": 0,
                "current_step": "Initializing analysis...",
                "started_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP,
            },
        )

        # Publish start event
        publisher.publish(
            topic_path,
            json.dumps(
                {
                    "analysis_id": analysis_id,
                    "user_id": user_id,
                    "event": "started",
                    "progress": 0,
                    "message": "Analysis started",
                },
            ).encode(),
        )

    except Exception as e:
        logger.error("Failed to start progress tracking: %s", str(e))


def update_progress(analysis_id: str, progress: int, step: str) -> None:
    """Update analysis progress"""
    try:
        # Update progress document
        db.collection("analysis_progress").document(analysis_id).update(
            {
                "progress": progress,
                "current_step": step,
                "updated_at": firestore.SERVER_TIMESTAMP,
            },
        )

        # Publish progress event
        publisher.publish(
            topic_path,
            json.dumps(
                {
                    "analysis_id": analysis_id,
                    "event": "progress",
                    "progress": progress,
                    "message": step,
                },
            ).encode(),
        )

    except Exception as e:
        logger.error("Failed to update progress: %s", str(e))


def store_enhanced_results(analysis_id: str, result: Any, user_id: str) -> None:
    """Store enhanced analysis results"""
    try:
        # Store comprehensive results
        doc_ref = db.collection("ghostbusters_results").document(analysis_id)
        doc_ref.set(
            {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "project_path": result.project_path,
                "confidence_score": result.confidence_score,
                "delusions_detected": result.delusions_detected,
                "recovery_actions": result.recovery_actions,
                "errors": result.errors,
                "warnings": result.warnings,
                "metadata": result.metadata,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "status": "completed",
                "processing_time": result.metadata.get("processing_time", 0),
                "agents_used": result.metadata.get("agents_used", []),
                "validation_results": result.validation_results,
                "recovery_results": result.recovery_results,
            },
        )

        # Update progress to completed
        db.collection("analysis_progress").document(analysis_id).update(
            {
                "status": "completed",
                "progress": 100,
                "current_step": "Analysis completed",
                "completed_at": firestore.SERVER_TIMESTAMP,
            },
        )

    except Exception as e:
        logger.error("Failed to store enhanced results: %s", str(e))


def notify_completion(analysis_id: str, user_id: str) -> None:
    """Send completion notification"""
    try:
        # Publish completion event
        publisher.publish(
            topic_path,
            json.dumps(
                {
                    "analysis_id": analysis_id,
                    "user_id": user_id,
                    "event": "completed",
                    "progress": 100,
                    "message": "Analysis completed successfully",
                },
            ).encode(),
        )

    except Exception as e:
        logger.error("Failed to send completion notification: %s", str(e))


@functions_framework.http
def ghostbusters_analyze_enhanced(request):
    """
    Enhanced HTTP Cloud Function for Ghostbusters analysis
    with authentication, rate limiting, and real-time updates
    """
    try:
        # Authentication
        user_id = authenticate_request(request)
        if not user_id:
            return {"status": "error", "error_message": "Authentication required"}, 401

        # Rate limiting
        if not check_rate_limit(user_id):
            return {
                "status": "error",
                "error_message": "Rate limit exceeded. Please try again later.",
            }, 429

        # Parse and validate request
        try:
            project_data = validate_and_parse_request(request)
        except ValueError as e:
            return {"status": "error", "error_message": str(e)}, 400

        analysis_id = str(uuid.uuid4())
        project_path = project_data["project_path"]

        logger.info(
            "Starting enhanced Ghostbusters analysis for project: %s",
            project_path,
        )
        logger.info("Analysis ID: %s, User ID: %s", analysis_id, user_id)

        # Start progress tracking
        start_progress_tracking(analysis_id, user_id)

        # Update progress - Initializing
        update_progress(analysis_id, 10, "Initializing Ghostbusters agents...")

        # Import and run Ghostbusters (async)
        from src.ghostbusters.ghostbusters_orchestrator import run_ghostbusters

        # Update progress - Running analysis
        update_progress(analysis_id, 30, "Running multi-agent analysis...")

        start_time = datetime.now()
        result = asyncio.run(run_ghostbusters(project_path))
        processing_time = (datetime.now() - start_time).total_seconds()

        # Update progress - Processing results
        update_progress(analysis_id, 80, "Processing results and storing data...")

        # Add processing time to metadata
        if not hasattr(result, "metadata"):
            result.metadata = {}
        result.metadata["processing_time"] = processing_time
        result.metadata["agents_used"] = list(result.metadata.get("agents_used", []))

        # Store enhanced results
        store_enhanced_results(analysis_id, result, user_id)

        # Send completion notification
        notify_completion(analysis_id, user_id)

        logger.info(
            "Enhanced analysis completed successfully. Confidence: %s",
            result.confidence_score,
        )

        return {
            "analysis_id": analysis_id,
            "confidence_score": result.confidence_score,
            "delusions_detected": len(result.delusions_detected),
            "recovery_actions": len(result.recovery_actions),
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "processing_time": processing_time,
            "status": "completed",
            "dashboard_url": f"/dashboard/{analysis_id}",
            "websocket_url": f"wss://ghostbusters-project.cloudfunctions.net/analysis-updates/{analysis_id}",
        }

    except Exception as e:
        logger.error("Error during enhanced Ghostbusters analysis: %s", str(e))

        # Store error in Firestore
        error_id = str(uuid.uuid4())
        db.collection("ghostbusters_errors").document(error_id).set(
            {
                "error_id": error_id,
                "error_message": str(e),
                "user_id": user_id if "user_id" in locals() else None,
                "analysis_id": analysis_id if "analysis_id" in locals() else None,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "status": "error",
            },
        )

        return {"status": "error", "error_message": str(e), "error_id": error_id}, 500


@functions_framework.http
def ghostbusters_progress(request):
    """
    HTTP Cloud Function to get analysis progress
    """
    try:
        # Authentication
        user_id = authenticate_request(request)
        if not user_id:
            return {"status": "error", "error_message": "Authentication required"}, 401

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

        # Get progress from Firestore
        doc_ref = db.collection("analysis_progress").document(analysis_id)
        doc = doc_ref.get()

        if not doc.exists:
            return {
                "status": "error",
                "error_message": f"Analysis {analysis_id} not found",
            }, 404

        data = doc.to_dict()

        # Check if user has access to this analysis
        if data.get("user_id") != user_id:
            return {"status": "error", "error_message": "Access denied"}, 403

        return {
            "analysis_id": analysis_id,
            "status": data.get("status", "unknown"),
            "progress": data.get("progress", 0),
            "current_step": data.get("current_step", ""),
            "started_at": data.get("started_at"),
            "updated_at": data.get("updated_at"),
            "completed_at": data.get("completed_at"),
        }

    except Exception as e:
        logger.error("Error checking analysis progress: %s", str(e))
        return {"status": "error", "error_message": str(e)}, 500


@functions_framework.http
def ghostbusters_user_analyses(request):
    """
    HTTP Cloud Function to get user's analysis history
    """
    try:
        # Authentication
        user_id = authenticate_request(request)
        if not user_id:
            return {"status": "error", "error_message": "Authentication required"}, 401

        # Parse request
        request_json = request.get_json() or {}
        limit = request_json.get("limit", 10)

        # Get user's analyses from Firestore
        docs = (
            db.collection("ghostbusters_results")
            .where("user_id", "==", user_id)
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
                    "warnings": len(data.get("warnings", [])),
                    "processing_time": data.get("processing_time", 0),
                    "timestamp": data.get("timestamp"),
                    "status": data.get("status"),
                    "dashboard_url": f"/dashboard/{data.get('analysis_id')}",
                },
            )

        return {
            "status": "success",
            "user_id": user_id,
            "analyses": analyses,
            "count": len(analyses),
        }

    except Exception as e:
        logger.error("Error getting user analyses: %s", str(e))
        return {"status": "error", "error_message": str(e)}, 500
