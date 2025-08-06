#!/usr/bin/env python3
"""
Ghostbusters API Service - FastAPI Container Version
Proper domain-specific API for Ghostbusters analysis and recovery
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from google.cloud import firestore, pubsub_v1, secretmanager
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Ghostbusters API", version="2.0.0")

# Initialize GCP clients (persistent for container)
db = firestore.Client()
publisher = pubsub_v1.PublisherClient()
secret_client = secretmanager.SecretManagerServiceClient()

# API key caching
_api_keys_cache = None
_cache_timestamp = None


def get_api_keys() -> dict[str, Optional[str]]:
    """Get API keys from Secret Manager with caching"""
    global _api_keys_cache, _cache_timestamp

    # Cache for 5 minutes
    if (
        _api_keys_cache
        and _cache_timestamp
        and (datetime.now(timezone.utc) - _cache_timestamp).seconds < 300
    ):
        return _api_keys_cache

    try:
        # Get OpenAI API key
        openai_name = (
            "projects/aardvark-linkedin-grepper/secrets/openai-api-key/versions/latest"
        )
        openai_response = secret_client.access_secret_version(
            request={"name": openai_name},
        )
        openai_key = openai_response.payload.data.decode("UTF-8")

        # Get Anthropic API key
        anthropic_name = "projects/aardvark-linkedin-grepper/secrets/anthropic-api-key/versions/latest"
        anthropic_response = secret_client.access_secret_version(
            request={"name": anthropic_name},
        )
        anthropic_key = anthropic_response.payload.data.decode("UTF-8")

        _api_keys_cache = {"openai": openai_key, "anthropic": anthropic_key}
        _cache_timestamp = datetime.now(timezone.utc)

        return _api_keys_cache
    except Exception as e:
        logger.warning(f"Failed to get API keys: {e}")
        _api_keys_cache = {"openai": None, "anthropic": None}
        _cache_timestamp = datetime.now(timezone.utc)
        return _api_keys_cache


# Pydantic models
class AnalysisRequest(BaseModel):
    """Request model for analysis"""

    repo_url: str  # GitHub repository URL
    branch: str = "main"  # Branch to analyze (default: main)
    agents: list[str] = [
        "security",
        "code_quality",
        "architecture",
        "build",
    ]  # Agents to run


class AnalysisResponse(BaseModel):
    """Response model for analysis"""

    job_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    """Response model for status"""

    job_id: str
    status: str
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str


# Agent mapping
AGENT_MAP = {
    "security": "SecurityExpert",
    "code_quality": "CodeQualityExpert",
    "test": "TestExpert",
    "build": "BuildExpert",
    "architecture": "ArchitectureExpert",
    "model": "ModelExpert",
}


async def run_analysis(
    job_id: str,
    repo_url: str,
    branch: str,
    agents: list[str],
) -> dict[str, Any]:
    """Run Ghostbusters analysis on the specified repository and branch"""
    try:
        # Import agents
        from agents import (
            ArchitectureExpert,
            BuildExpert,
            CodeQualityExpert,
            ModelExpert,
            SecurityExpert,
            TestExpert,
        )

        # Agent class mapping
        agent_classes = {
            "security": SecurityExpert,
            "code_quality": CodeQualityExpert,
            "test": TestExpert,
            "build": BuildExpert,
            "architecture": ArchitectureExpert,
            "model": ModelExpert,
        }

        # Clone the repository to analyze
        import subprocess
        import tempfile
        from pathlib import Path

        # Create temporary directory for analysis
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Cloning {repo_url} branch {branch} to {temp_dir}")

            # Clone the repository
            clone_cmd = [
                "git",
                "clone",
                "--branch",
                branch,
                "--depth",
                "1",
                repo_url,
                temp_dir,
            ]
            result = subprocess.run(clone_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(f"Failed to clone repository: {result.stderr}")

            logger.info(f"Successfully cloned repository to {temp_dir}")

            # Convert to Path object for agents
            project_path = Path(temp_dir)

            # Run analysis with each agent
            results = []
            for agent_name in agents:
                if agent_name not in agent_classes:
                    logger.warning(f"Unknown agent: {agent_name}")
                    continue

                try:
                    # Create agent instance
                    agent_class = agent_classes[agent_name]
                    agent = agent_class()

                    # Run the agent analysis
                    result = await agent.detect_delusions(project_path)
                    results.append(
                        {
                            "agent": agent_name,
                            "delusions": result.delusions,
                            "confidence": result.confidence,
                            "recommendations": result.recommendations,
                        },
                    )

                    logger.info(
                        f"Agent {agent_name} completed with confidence {result.confidence}",
                    )

                except Exception as e:
                    logger.error(f"Agent {agent_name} failed: {e}")
                    results.append(
                        {
                            "agent": agent_name,
                            "delusions": [],
                            "confidence": 0.0,
                            "recommendations": [f"Analysis failed: {str(e)}"],
                        },
                    )

            return {
                "status": "completed",
                "results": results,
                "job_id": job_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "repo_url": repo_url,
                "branch": branch,
            }

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise


async def process_analysis_background(
    job_id: str,
    repo_url: str,
    branch: str,
    agents: list[str],
):
    """Background task to process analysis"""
    try:
        # Update job status to processing
        job_ref = db.collection("ghostbusters_jobs").document(job_id)
        job_ref.update(
            {"status": "processing", "updated_at": datetime.now(timezone.utc)},
        )

        # Run the analysis
        result = await run_analysis(job_id, repo_url, branch, agents)

        # Update job with results
        job_ref.update(
            {
                "status": "completed",
                "result": result,
                "error": None,
                "updated_at": datetime.now(timezone.utc),
            },
        )

        # Publish result to Pub/Sub
        topic_path = publisher.topic_path(
            "aardvark-linkedin-grepper",
            "ghostbusters-analysis-results",
        )
        message = {"job_id": job_id, "status": "completed", "result": result}
        publisher.publish(topic_path, json.dumps(message).encode("utf-8"))

        logger.info(f"Analysis completed for job {job_id}")

    except Exception as e:
        logger.error(f"Analysis failed for job {job_id}: {e}")

        # Update job with error
        job_ref = db.collection("ghostbusters_jobs").document(job_id)
        job_ref.update(
            {
                "status": "failed",
                "error": str(e),
                "updated_at": datetime.now(timezone.utc),
            },
        )

        # Publish error to Pub/Sub
        topic_path = publisher.topic_path(
            "aardvark-linkedin-grepper",
            "ghostbusters-analysis-results",
        )
        message = {"job_id": job_id, "status": "failed", "error": str(e)}
        publisher.publish(topic_path, json.dumps(message).encode("utf-8"))


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_project(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze a project using Ghostbusters agents"""
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())

        # Create job record
        job_data = {
            "job_id": job_id,
            "status": "queued",
            "repo_url": request.repo_url,
            "branch": request.branch,
            "agents": request.agents,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        db.collection("ghostbusters_jobs").document(job_id).set(job_data)

        # Add background task
        background_tasks.add_task(
            process_analysis_background,
            job_id,
            request.repo_url,
            request.branch,
            request.agents,
        )

        return AnalysisResponse(
            job_id=job_id,
            status="queued",
            message="Analysis job queued successfully",
        )

    except Exception as e:
        logger.error(f"Failed to queue analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{job_id}", response_model=StatusResponse)
async def get_job_status(job_id: str):
    """Get the status of an analysis job"""
    try:
        doc = db.collection("ghostbusters_jobs").document(job_id).get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Job not found")

        data = doc.to_dict()
        return StatusResponse(**data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs")
async def list_jobs(limit: int = 10):
    """List recent analysis jobs"""
    try:
        docs = (
            db.collection("ghostbusters_jobs")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )

        jobs = []
        for doc in docs:
            data = doc.to_dict()
            jobs.append(data)

        return {"jobs": jobs}

    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "api_keys_available": bool(
            get_api_keys()["openai"] or get_api_keys()["anthropic"],
        ),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
