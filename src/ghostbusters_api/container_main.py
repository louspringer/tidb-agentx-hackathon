#!/usr/bin/env python3
"""
Ghostbusters API - Container Version
FastAPI-based service with persistent state and better performance
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

import uvicorn
from agents import (
    ArchitectureExpert,
    BuildExpert,
    CodeQualityExpert,
    ModelExpert,
    SecurityExpert,
    TestExpert,
)
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from google.cloud import firestore, pubsub_v1, secretmanager
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Ghostbusters API", version="2.0.0")

# Initialize GCP clients (persistent)
db = firestore.Client()
publisher = pubsub_v1.PublisherClient()
secret_client = secretmanager.SecretManagerServiceClient()

# Project configuration
PROJECT_ID = "aardvark-linkedin-grepper"
ANALYSIS_TOPIC_PATH = publisher.topic_path(PROJECT_ID, "ghostbusters-analysis-updates")

# Agent mapping (loaded once)
AGENT_MAP = {
    "security": SecurityExpert,
    "code_quality": CodeQualityExpert,
    "test": TestExpert,
    "build": BuildExpert,
    "architecture": ArchitectureExpert,
    "model": ModelExpert,
}

# Cache for API keys (persistent)
_api_keys_cache = {}
_cache_timestamp = None


# Pydantic models
class AnalysisRequest(BaseModel):
    project_path: str = "."
    agents: list[str] = ["security", "code_quality"]
    user_id: Optional[str] = None


class RecoveryRequest(BaseModel):
    recovery_type: str
    target_files: list[str]
    user_id: Optional[str] = None


class JobStatus(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}


# Get API keys from cache or Secret Manager
def get_api_keys() -> dict[str, Optional[str]]:
    """Get API keys with caching"""
    global _api_keys_cache, _cache_timestamp

    # Cache for 1 hour
    if (
        _cache_timestamp
        and (datetime.now(timezone.utc) - _cache_timestamp).seconds < 3600
    ):
        return _api_keys_cache

    try:
        # Get OpenAI API key
        openai_name = f"projects/{PROJECT_ID}/secrets/openai-api-key/versions/latest"
        openai_response = secret_client.access_secret_version(
            request={"name": openai_name},
        )
        openai_key = openai_response.payload.data.decode("UTF-8")

        # Get Anthropic API key
        anthropic_name = (
            f"projects/{PROJECT_ID}/secrets/anthropic-api-key/versions/latest"
        )
        anthropic_response = secret_client.access_secret_version(
            request={"name": anthropic_name},
        )
        anthropic_key = anthropic_response.payload.data.decode("UTF-8")

        _api_keys_cache = {
            "openai": openai_key,
            "anthropic": anthropic_key,
        }
        _cache_timestamp = datetime.now(timezone.utc)

        logger.info("API keys loaded and cached")
        return _api_keys_cache

    except Exception as e:
        logger.warning(f"Failed to load API keys: {e}")
        return {"openai": None, "anthropic": None}


# Publish result to Pub/Sub
def publish_result(job_id: str, status: str, data: dict[str, Any]):
    """Publish result to Pub/Sub"""
    try:
        message = {
            "job_id": job_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }

        future = publisher.publish(
            ANALYSIS_TOPIC_PATH,
            json.dumps(message).encode("utf-8"),
            job_id=job_id,
            status=status,
        )
        future.result()
        logger.info(f"Published result for job {job_id}: {status}")

    except Exception as e:
        logger.error(f"Failed to publish result: {e}")


# Run Ghostbusters analysis
async def run_analysis(
    job_id: str,
    project_path: str,
    agents: list[str],
) -> dict[str, Any]:
    """Run Ghostbusters analysis with persistent state"""
    try:
        logger.info(f"Running analysis for job {job_id} with agents: {agents}")

        # Check API keys availability
        api_keys = get_api_keys()
        has_llm = api_keys["openai"] or api_keys["anthropic"]

        all_delusions = []
        all_recommendations = []
        agents_run = []
        total_confidence = 0.0

        # Run each requested agent
        for agent_name in agents:
            if agent_name not in AGENT_MAP:
                logger.warning(f"Unknown agent: {agent_name}")
                continue

            try:
                agent_class = AGENT_MAP[agent_name]
                agent = agent_class()

                logger.info(f"Running {agent_name} agent...")
                result = await agent.detect_delusions(project_path)

                # Add agent name to each delusion
                for delusion in result.delusions:
                    delusion["agent"] = agent_name
                    all_delusions.append(delusion)

                all_recommendations.extend(result.recommendations)
                agents_run.append(agent_name)
                total_confidence += result.confidence

                logger.info(
                    f"{agent_name} agent found {len(result.delusions)} delusions",
                )

            except Exception as e:
                logger.error(f"Error running {agent_name} agent: {e}")
                continue

        # Calculate average confidence
        avg_confidence = total_confidence / len(agents_run) if agents_run else 0.0

        result = {
            "success": True,
            "delusions_found": len(all_delusions),
            "agents_run": agents_run,
            "project_path": project_path,
            "confidence": avg_confidence,
            "delusions": all_delusions,
            "recommendations": list(set(all_recommendations)),
            "analysis_time": "container",
            "llm_available": has_llm,
        }

        logger.info(
            f"Analysis completed for job {job_id}: {len(all_delusions)} delusions found",
        )
        return result

    except Exception as e:
        logger.error(f"Analysis failed for job {job_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "delusions_found": 0,
            "agents_run": agents,
            "project_path": project_path,
            "confidence": 0.0,
            "delusions": [],
            "recommendations": [],
        }


# Background task for analysis
async def process_analysis_background(
    job_id: str,
    project_path: str,
    agents: list[str],
):
    """Background task to process analysis"""
    try:
        # Update job status to processing
        doc_ref = db.collection("ghostbusters_jobs").document(job_id)
        doc_ref.update(
            {
                "status": "processing",
                "updated_at": datetime.now(timezone.utc),
            },
        )

        publish_result(job_id, "processing", {"message": "Analysis started"})

        # Run analysis
        result = await run_analysis(job_id, project_path, agents)

        # Update job status
        doc_ref.update(
            {
                "status": "completed" if result["success"] else "failed",
                "result": result,
                "completed_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        )

        publish_result(job_id, "completed" if result["success"] else "failed", result)

    except Exception as e:
        logger.error(f"Background processing failed for job {job_id}: {e}")

        # Update job status to failed
        doc_ref = db.collection("ghostbusters_jobs").document(job_id)
        doc_ref.update(
            {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        )

        publish_result(job_id, "failed", {"error": str(e)})


# API endpoints
@app.post("/analyze")
async def analyze_project(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Queue a Ghostbusters analysis job"""
    try:
        job_id = str(uuid4())

        # Create job record
        job_data = {
            "job_id": job_id,
            "type": "analysis",
            "project_path": request.project_path,
            "agents": request.agents,
            "user_id": request.user_id,
            "status": "submitted",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        doc_ref = db.collection("ghostbusters_jobs").document(job_id)
        doc_ref.set(job_data)

        # Start background processing
        background_tasks.add_task(
            process_analysis_background,
            job_id,
            request.project_path,
            request.agents,
        )

        logger.info(f"Analysis job {job_id} queued")

        return {
            "job_id": job_id,
            "status": "submitted",
            "message": "Ghostbusters analysis queued",
            "project_path": request.project_path,
            "agents": request.agents,
        }

    except Exception as e:
        logger.error(f"Failed to queue analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    try:
        doc_ref = db.collection("ghostbusters_jobs").document(job_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Job not found")

        data = doc.to_dict()
        return JSONResponse(content=data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs")
async def list_jobs(limit: int = 50, status: Optional[str] = None):
    """List recent jobs"""
    try:
        query = (
            db.collection("ghostbusters_jobs")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )

        if status:
            query = query.where("status", "==", status)

        docs = query.stream()
        jobs = [doc.to_dict() for doc in docs]

        return {"jobs": jobs, "count": len(jobs)}

    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
