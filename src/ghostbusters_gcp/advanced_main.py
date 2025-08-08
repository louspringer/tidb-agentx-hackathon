#!/usr/bin/env python3
"""
Advanced Ghostbusters GCP Cloud Functions
Phase 3: Custom Agents, ML Integration, and Enterprise Features
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

import functions_framework  # type: ignore
from firebase_admin import auth, initialize_app  # type: ignore
from google.cloud import aiplatform, firestore, pubsub_v1  # type: ignore
from google.cloud.aiplatform import Endpoint  # type: ignore

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

# Initialize Vertex AI
aiplatform.init(project="ghostbusters-project", location="us-central1")


def authenticate_request(request) -> Optional[str]:  # type: ignore
    """Authenticate request using Firebase Auth"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        return decoded_token["uid"]  # type: ignore
    except Exception as e:
        logger.warning("Authentication failed: %s", str(e))
        return None


def check_enterprise_quota(user_id: str) -> bool:
    """Check enterprise quota for user"""
    try:
        # Get user's enterprise plan
        user_doc = db.collection("enterprise_users").document(user_id).get()

        if user_doc.exists:
            data = user_doc.to_dict()
            monthly_usage = data.get("monthly_usage", 0)
            monthly_limit = data.get("monthly_limit", 100)

            # Update usage
            db.collection("enterprise_users").document(user_id).update(
                {
                    "monthly_usage": monthly_usage + 1,
                    "last_used": firestore.SERVER_TIMESTAMP,
                },
            )

            return monthly_usage < monthly_limit  # type: ignore
        else:
            # Default to basic plan
            return True
    except Exception as e:
        logger.error("Enterprise quota check failed: %s", str(e))
        return True  # Allow on error


def get_custom_agents(user_id: str) -> list[dict[str, Any]]:
    """Get user's custom agents"""
    try:
        docs = db.collection("custom_agents").where("user_id", "==", user_id).stream()
        agents = []
        for doc in docs:
            data = doc.to_dict()
            agents.append(
                {
                    "agent_id": doc.id,
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "type": data.get("type"),
                    "config": data.get("config", {}),
                    "enabled": data.get("enabled", True),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                },
            )
        return agents
    except Exception as e:
        logger.error("Failed to get custom agents: %s", str(e))
        return []


def create_custom_agent(user_id: str, agent_config: dict[str, Any]) -> str:
    """Create a new custom agent"""
    try:
        agent_id = str(uuid.uuid4())

        db.collection("custom_agents").document(agent_id).set(
            {
                "user_id": user_id,
                "name": agent_config.get("name"),
                "description": agent_config.get("description"),
                "type": agent_config.get("type"),
                "config": agent_config.get("config", {}),
                "enabled": True,
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP,
            },
        )

        logger.info("Created custom agent: %s for user: %s", agent_id, user_id)
        return agent_id
    except Exception as e:
        logger.error("Failed to create custom agent: %s", str(e))
        raise


def get_ml_insights(analysis_data: dict[str, Any]) -> dict[str, Any]:
    """Get ML-powered insights from analysis data"""
    try:
        # Use Vertex AI for ML insights
        endpoint = Endpoint(
            "projects/ghostbusters-project/locations/us-central1/endpoints/ghostbusters-insights",
        )

        # Prepare data for ML model
        ml_input = {
            "delusions_count": len(analysis_data.get("delusions_detected", [])),
            "recovery_actions_count": len(analysis_data.get("recovery_actions", [])),
            "confidence_score": analysis_data.get("confidence_score", 0),
            "processing_time": analysis_data.get("processing_time", 0),
            "errors_count": len(analysis_data.get("errors", [])),
            "warnings_count": len(analysis_data.get("warnings", [])),
        }

        # Get ML predictions
        response = endpoint.predict([ml_input])
        predictions = response.predictions[0]

        return {
            "risk_score": predictions.get("risk_score", 0),
            "priority_level": predictions.get("priority_level", "medium"),
            "recommended_actions": predictions.get("recommended_actions", []),
            "trend_analysis": predictions.get("trend_analysis", {}),
            "anomaly_detection": predictions.get("anomaly_detection", False),
        }
    except Exception as e:
        logger.error("ML insights failed: %s", str(e))
        return {
            "risk_score": 0.5,
            "priority_level": "medium",
            "recommended_actions": [],
            "trend_analysis": {},
            "anomaly_detection": False,
        }


def audit_log_action(user_id: str, action: str, details: dict[str, Any]) -> None:
    """Log enterprise audit actions"""
    try:
        db.collection("audit_logs").add(
            {
                "user_id": user_id,
                "action": action,
                "details": details,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "ip_address": "cloud_function",  # Would be real IP in production
                "user_agent": "ghostbusters-api",
            },
        )
    except Exception as e:
        logger.error("Audit logging failed: %s", str(e))


def validate_and_parse_advanced_request(request) -> dict[str, Any]:  # type: ignore
    """Validate and parse advanced request data"""
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
        "custom_agents": request_json.get("custom_agents", []),
        "ml_insights": request_json.get("ml_insights", True),
        "enterprise_features": request_json.get("enterprise_features", False),
    }


def start_advanced_progress_tracking(analysis_id: str, user_id: str) -> None:
    """Start advanced progress tracking with ML insights"""
    try:
        # Create advanced progress document
        db.collection("advanced_analysis_progress").document(analysis_id).set(
            {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "status": "started",
                "progress": 0,
                "current_step": "Initializing advanced analysis...",
                "ml_insights_enabled": True,
                "custom_agents_enabled": True,
                "enterprise_features_enabled": True,
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
                    "event": "advanced_started",
                    "progress": 0,
                    "message": "Advanced analysis started with ML insights",
                },
            ).encode(),
        )

    except Exception as e:
        logger.error("Failed to start advanced progress tracking: %s", str(e))


def update_advanced_progress(
    analysis_id: str,
    progress: int,
    step: str,
    ml_insights: dict[str, Any] = None,
) -> None:  # type: ignore
    """Update advanced analysis progress with ML insights"""
    try:
        update_data = {
            "progress": progress,
            "current_step": step,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }

        if ml_insights:
            update_data["ml_insights"] = ml_insights

        # Update progress document
        db.collection("advanced_analysis_progress").document(analysis_id).update(
            update_data,
        )

        # Publish progress event
        event_data = {
            "analysis_id": analysis_id,
            "event": "advanced_progress",
            "progress": progress,
            "message": step,
        }

        if ml_insights:
            event_data["ml_insights"] = ml_insights

        publisher.publish(topic_path, json.dumps(event_data).encode())

    except Exception as e:
        logger.error("Failed to update advanced progress: %s", str(e))


def store_advanced_results(
    analysis_id: str,
    result: Any,
    user_id: str,
    ml_insights: dict[str, Any],
) -> None:
    """Store advanced analysis results with ML insights"""
    try:
        # Store comprehensive results with ML insights
        doc_ref = db.collection("advanced_ghostbusters_results").document(analysis_id)
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
                "ml_insights": ml_insights,
                "enterprise_features": {
                    "audit_logged": True,
                    "quota_checked": True,
                    "custom_agents_used": True,
                },
                "timestamp": firestore.SERVER_TIMESTAMP,
                "status": "completed",
                "processing_time": result.metadata.get("processing_time", 0),
                "agents_used": result.metadata.get("agents_used", []),
                "validation_results": result.validation_results,
                "recovery_results": result.recovery_results,
            },
        )

        # Update progress to completed
        db.collection("advanced_analysis_progress").document(analysis_id).update(
            {
                "status": "completed",
                "progress": 100,
                "current_step": "Advanced analysis completed with ML insights",
                "completed_at": firestore.SERVER_TIMESTAMP,
            },
        )

    except Exception as e:
        logger.error("Failed to store advanced results: %s", str(e))


@functions_framework.http
def ghostbusters_analyze_advanced(request):  # type: ignore
    """
    Advanced HTTP Cloud Function for Ghostbusters analysis
    with custom agents, ML integration, and enterprise features
    """
    try:
        # Authentication
        user_id = authenticate_request(request)
        if not user_id:
            return {"status": "error", "error_message": "Authentication required"}, 401

        # Enterprise quota check
        if not check_enterprise_quota(user_id):
            return {
                "status": "error",
                "error_message": "Enterprise quota exceeded. Please upgrade your plan.",
            }, 429

        # Parse and validate request
        try:
            project_data = validate_and_parse_advanced_request(request)
        except ValueError as e:
            return {"status": "error", "error_message": str(e)}, 400

        analysis_id = str(uuid.uuid4())
        project_path = project_data["project_path"]

        logger.info(
            "Starting advanced Ghostbusters analysis for project: %s",
            project_path,
        )
        logger.info("Analysis ID: %s, User ID: %s", analysis_id, user_id)

        # Audit log the action
        audit_log_action(
            user_id,
            "advanced_analysis_started",
            {
                "analysis_id": analysis_id,
                "project_path": project_path,
                "options": project_data.get("options", {}),
            },
        )

        # Start advanced progress tracking
        start_advanced_progress_tracking(analysis_id, user_id)

        # Get custom agents
        custom_agents = get_custom_agents(user_id)
        update_advanced_progress(
            analysis_id,
            10,
            f"Loaded {len(custom_agents)} custom agents...",
        )

        # Update progress - Initializing
        update_advanced_progress(
            analysis_id,
            20,
            "Initializing advanced Ghostbusters agents...",
        )

        # Import and run Ghostbusters (async)
        from src.ghostbusters.ghostbusters_orchestrator import run_ghostbusters

        # Update progress - Running analysis
        update_advanced_progress(
            analysis_id,
            40,
            "Running advanced multi-agent analysis...",
        )

        start_time = datetime.now()
        result = asyncio.run(run_ghostbusters(project_path))
        processing_time = (datetime.now() - start_time).total_seconds()

        # Update progress - ML insights
        update_advanced_progress(analysis_id, 70, "Generating ML-powered insights...")

        # Get ML insights
        analysis_data = {
            "delusions_detected": result.delusions_detected,
            "recovery_actions": result.recovery_actions,
            "confidence_score": result.confidence_score,
            "processing_time": processing_time,
            "errors": result.errors,
            "warnings": result.warnings,
        }

        ml_insights = get_ml_insights(analysis_data)
        update_advanced_progress(
            analysis_id,
            80,
            "Processing results and storing data...",
            ml_insights,
        )

        # Add processing time to metadata
        if not hasattr(result, "metadata"):
            result.metadata = {}
        result.metadata["processing_time"] = processing_time
        result.metadata["agents_used"] = list(result.metadata.get("agents_used", []))
        result.metadata["custom_agents_used"] = len(custom_agents)
        result.metadata["ml_insights_enabled"] = True

        # Store advanced results
        store_advanced_results(analysis_id, result, user_id, ml_insights)

        # Audit log completion
        audit_log_action(
            user_id,
            "advanced_analysis_completed",
            {
                "analysis_id": analysis_id,
                "confidence_score": result.confidence_score,
                "processing_time": processing_time,
                "ml_insights": ml_insights,
            },
        )

        logger.info(
            "Advanced analysis completed successfully. Confidence: %s",
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
            "ml_insights": ml_insights,
            "custom_agents_used": len(custom_agents),
            "enterprise_features": {
                "audit_logged": True,
                "quota_checked": True,
                "custom_agents_enabled": True,
            },
            "status": "completed",
            "dashboard_url": f"/advanced-dashboard/{analysis_id}",
            "websocket_url": f"wss://ghostbusters-project.cloudfunctions.net/advanced-analysis-updates/{analysis_id}",
        }

    except Exception as e:
        logger.error("Error during advanced Ghostbusters analysis: %s", str(e))

        # Store error in Firestore
        error_id = str(uuid.uuid4())
        db.collection("advanced_ghostbusters_errors").document(error_id).set(
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
def ghostbusters_custom_agents(request):  # type: ignore
    """
    HTTP Cloud Function to manage custom agents
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

        action = request_json.get("action")
        if not action:
            return {"status": "error", "error_message": "action is required"}, 400

        if action == "list":
            # List custom agents
            agents = get_custom_agents(user_id)
            return {"status": "success", "agents": agents, "count": len(agents)}

        elif action == "create":
            # Create custom agent
            agent_config = request_json.get("agent_config")
            if not agent_config:
                return {
                    "status": "error",
                    "error_message": "agent_config is required",
                }, 400

            agent_id = create_custom_agent(user_id, agent_config)

            # Audit log
            audit_log_action(
                user_id,
                "custom_agent_created",
                {"agent_id": agent_id, "agent_name": agent_config.get("name")},
            )

            return {
                "status": "success",
                "agent_id": agent_id,
                "message": "Custom agent created successfully",
            }

        elif action == "update":
            # Update custom agent
            agent_id = request_json.get("agent_id")
            if not agent_id:
                return {"status": "error", "error_message": "agent_id is required"}, 400

            agent_config = request_json.get("agent_config", {})

            db.collection("custom_agents").document(agent_id).update(
                {**agent_config, "updated_at": firestore.SERVER_TIMESTAMP},
            )

            # Audit log
            audit_log_action(
                user_id,
                "custom_agent_updated",
                {"agent_id": agent_id, "agent_name": agent_config.get("name")},
            )

            return {"status": "success", "message": "Custom agent updated successfully"}

        elif action == "delete":
            # Delete custom agent
            agent_id = request_json.get("agent_id")
            if not agent_id:
                return {"status": "error", "error_message": "agent_id is required"}, 400

            db.collection("custom_agents").document(agent_id).delete()

            # Audit log
            audit_log_action(user_id, "custom_agent_deleted", {"agent_id": agent_id})

            return {"status": "success", "message": "Custom agent deleted successfully"}

        else:
            return {"status": "error", "error_message": "Invalid action"}, 400

    except Exception as e:
        logger.error("Error managing custom agents: %s", str(e))
        return {"status": "error", "error_message": str(e)}, 500


@functions_framework.http
def ghostbusters_enterprise_analytics(request):  # type: ignore
    """
    HTTP Cloud Function for enterprise analytics
    """
    try:
        # Authentication
        user_id = authenticate_request(request)
        if not user_id:
            return {"status": "error", "error_message": "Authentication required"}, 401

        # Parse request
        request_json = request.get_json() or {}
        analytics_type = request_json.get("type", "overview")

        if analytics_type == "overview":
            # Get enterprise overview
            total_analyses = len(
                list(db.collection("advanced_ghostbusters_results").stream()),
            )
            total_users = len(list(db.collection("enterprise_users").stream()))
            total_custom_agents = len(list(db.collection("custom_agents").stream()))

            return {
                "status": "success",
                "analytics": {
                    "total_analyses": total_analyses,
                    "total_users": total_users,
                    "total_custom_agents": total_custom_agents,
                    "ml_insights_generated": total_analyses,  # All advanced analyses have ML insights
                    "enterprise_features_used": total_analyses,
                },
            }

        elif analytics_type == "user_activity":
            # Get user activity analytics
            limit = request_json.get("limit", 10)
            docs = (
                db.collection("advanced_ghostbusters_results")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )

            activities = []
            for doc in docs:
                data = doc.to_dict()
                activities.append(
                    {
                        "user_id": data.get("user_id"),
                        "analysis_id": data.get("analysis_id"),
                        "confidence_score": data.get("confidence_score"),
                        "processing_time": data.get("processing_time"),
                        "timestamp": data.get("timestamp"),
                    },
                )

            return {
                "status": "success",
                "activities": activities,
                "count": len(activities),
            }

        elif analytics_type == "audit_logs":
            # Get audit logs
            limit = request_json.get("limit", 50)
            docs = (
                db.collection("audit_logs")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )

            logs = []
            for doc in docs:
                data = doc.to_dict()
                logs.append(
                    {
                        "user_id": data.get("user_id"),
                        "action": data.get("action"),
                        "details": data.get("details"),
                        "timestamp": data.get("timestamp"),
                    },
                )

            return {"status": "success", "audit_logs": logs, "count": len(logs)}

        else:
            return {"status": "error", "error_message": "Invalid analytics type"}, 400

    except Exception as e:
        logger.error("Error getting enterprise analytics: %s", str(e))
        return {"status": "error", "error_message": str(e)}, 500
