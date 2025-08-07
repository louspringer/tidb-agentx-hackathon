#!/usr/bin/env python3
"""
Gemini-Integrated Ghostbusters Billing Analyzer
Cloud Function that combines Ghostbusters analysis with Gemini LLM for GCP billing insights
"""

import asyncio
import json
import logging
import os
import subprocess
import uuid
from datetime import datetime, timezone
from typing import Any

import functions_framework
from google.cloud import firestore, pubsub_v1
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize GCP clients
db = firestore.Client()
publisher = pubsub_v1.PublisherClient()


# Gemini LLM setup
def setup_gemini_llm():
    """Setup Gemini LLM with proper API key"""
    try:
        # Try to get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

        if not api_key:
            # Try to get from gcloud (this might not work for Gemini API)
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                check=True,
            )
            api_key = result.stdout.strip()
            logger.info("Using Google Cloud access token for Gemini")

        if api_key:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.1,
            )
            logger.info("✅ Gemini LLM initialized successfully")
            return llm
        else:
            logger.warning("❌ No API key found for Gemini")
            return None

    except Exception as e:
        logger.error(f"❌ Error setting up Gemini LLM: {e}")
        return None


def get_billing_data():
    """Get current GCP billing data"""
    try:
        # Get project info
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            check=True,
        )
        project_id = result.stdout.strip()

        # Get billing account
        result = subprocess.run(
            ["gcloud", "billing", "accounts", "list", "--format=value(name)"],
            capture_output=True,
            text=True,
            check=True,
        )
        billing_account = (
            result.stdout.strip().split("\n")[0] if result.stdout.strip() else None
        )

        # Get enabled services
        result = subprocess.run(
            ["gcloud", "services", "list", "--enabled", "--format=value(name)"],
            capture_output=True,
            text=True,
            check=True,
        )
        enabled_services = (
            result.stdout.strip().split("\n") if result.stdout.strip() else []
        )

        # Get resource usage
        resources = {}

        # Cloud Functions
        try:
            result = subprocess.run(
                ["gcloud", "functions", "list", "--format=value(name)"],
                capture_output=True,
                text=True,
                check=True,
            )
            functions = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )
            resources["cloud_functions"] = len(functions)
        except Exception:
            resources["cloud_functions"] = 0

        # Cloud Run
        try:
            result = subprocess.run(
                ["gcloud", "run", "services", "list", "--format=value(name)"],
                capture_output=True,
                text=True,
                check=True,
            )
            run_services = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )
            resources["cloud_run"] = len(run_services)
        except Exception:
            resources["cloud_run"] = 0

        # Firestore
        try:
            result = subprocess.run(
                ["gcloud", "firestore", "databases", "list", "--format=value(name)"],
                capture_output=True,
                text=True,
                check=True,
            )
            databases = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )
            resources["firestore"] = len(databases)
        except Exception:
            resources["firestore"] = 0

        return {
            "project_id": project_id,
            "billing_account": billing_account,
            "enabled_services": enabled_services,
            "resources": resources,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting billing data: {e}")
        return None


def analyze_billing_with_gemini(billing_data: dict[str, Any], llm) -> dict[str, Any]:
    """Analyze billing data using Gemini LLM"""
    if not llm:
        return {"error": "Gemini LLM not available"}

    try:
        # Create analysis prompt
        prompt = f"""
        You are a GCP cost optimization expert. Analyze this billing data and provide insights:

        📊 PROJECT INFO:
        - Project ID: {billing_data.get('project_id', 'Unknown')}
        - Billing Account: {billing_data.get('billing_account', 'Unknown')}
        - Enabled Services: {len(billing_data.get('enabled_services', []))} services
        - Analysis Time: {billing_data.get('timestamp', 'Unknown')}

        🔧 RESOURCE USAGE:
        {json.dumps(billing_data.get('resources', {}), indent=2)}

        📋 ENABLED SERVICES:
        {json.dumps(billing_data.get('enabled_services', [])[:10], indent=2)}
        {'...' if len(billing_data.get('enabled_services', [])) > 10 else ''}

        💰 COST ANALYSIS REQUEST:
        1. **Cost Drivers**: What are the biggest potential cost drivers in this setup?
        2. **Optimization Opportunities**: What specific optimizations would you recommend?
        3. **Risk Assessment**: Any potential billing surprises or unexpected costs?
        4. **Service Analysis**: Which services are most likely to incur costs?
        5. **Actionable Recommendations**: What specific actions should be taken?

        Please provide a comprehensive analysis with specific recommendations for cost optimization.
        Focus on practical, actionable insights that can reduce GCP costs.
        """

        # Send to Gemini
        response = llm.invoke([HumanMessage(content=prompt)])

        return {
            "gemini_analysis": response.content,
            "billing_data": billing_data,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in Gemini analysis: {e}")
        return {"error": f"Gemini analysis failed: {str(e)}"}


def run_ghostbusters_analysis(project_path: str = ".") -> dict[str, Any]:
    """Run Ghostbusters analysis on the project"""
    try:
        # Import Ghostbusters orchestrator
        from src.ghostbusters.ghostbusters_orchestrator import run_ghostbusters

        # Run Ghostbusters analysis
        result = asyncio.run(run_ghostbusters(project_path))

        return {
            "confidence_score": result.confidence_score,
            "delusions_detected": len(result.delusions),
            "recovery_actions": len(result.recovery_actions),
            "errors": len(result.errors),
            "ghostbusters_result": result,
        }

    except Exception as e:
        logger.error(f"Error in Ghostbusters analysis: {e}")
        return {"error": f"Ghostbusters analysis failed: {str(e)}"}


@functions_framework.http
def gemini_billing_analyzer(request):
    """
    Gemini-Integrated Ghostbusters Billing Analyzer
    Combines Ghostbusters analysis with Gemini LLM for comprehensive GCP billing insights
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

        logger.info("Starting Gemini-Integrated Ghostbusters Billing Analysis")
        logger.info("Analysis ID: %s", analysis_id)

        # Step 1: Get billing data
        logger.info("📊 Collecting GCP billing data...")
        billing_data = get_billing_data()

        if not billing_data:
            return {
                "status": "error",
                "error_message": "Failed to collect billing data",
            }, 500

        # Step 2: Setup Gemini LLM
        logger.info("🤖 Setting up Gemini LLM...")
        llm = setup_gemini_llm()

        # Step 3: Analyze billing with Gemini
        logger.info("🔍 Analyzing billing data with Gemini...")
        gemini_analysis = analyze_billing_with_gemini(billing_data, llm)

        # Step 4: Run Ghostbusters analysis
        logger.info("👻 Running Ghostbusters analysis...")
        ghostbusters_result = run_ghostbusters_analysis(project_path)

        # Step 5: Combine results
        combined_result = {
            "analysis_id": analysis_id,
            "project_path": project_path,
            "billing_analysis": gemini_analysis,
            "ghostbusters_analysis": ghostbusters_result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }

        # Store results in Firestore
        doc_ref = db.collection("gemini_billing_analyses").document(analysis_id)
        doc_ref.set(combined_result)

        logger.info("✅ Gemini-Integrated Ghostbusters Billing Analysis completed!")

        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "billing_analysis_available": "gemini_analysis" in gemini_analysis,
            "ghostbusters_analysis_available": "error" not in ghostbusters_result,
            "summary": {
                "project_id": billing_data.get("project_id"),
                "enabled_services": len(billing_data.get("enabled_services", [])),
                "resources": billing_data.get("resources", {}),
                "ghostbusters_delusions": ghostbusters_result.get(
                    "delusions_detected",
                    0,
                ),
                "ghostbusters_confidence": ghostbusters_result.get(
                    "confidence_score",
                    0,
                ),
            },
        }

    except Exception as e:
        logger.error(f"Error in Gemini-Integrated Billing Analysis: {e}")
        return {
            "status": "error",
            "error_message": str(e),
        }, 500
