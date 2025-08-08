"""Gemini-Integrated Billing Analyzer for Elmo Fuzzy Giggle
Clean implementation combining Ghostbusters with Gemini LLM for GCP billing insights"""

import asyncio
import json
import logging
import os
import subprocess
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI


class GeminiBillingAnalyzer:
    """Gemini-integrated billing analyzer for GCP cost optimization"""

    def __init__(self) -> None:
        """Initialize the Gemini billing analyzer"""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.llm = self._setup_gemini_llm()

    def _setup_gemini_llm(self) -> Optional[ChatGoogleGenerativeAI]:
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
                self.logger.info("Using Google Cloud access token for Gemini")

            if api_key:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=api_key,
                    temperature=0.1,
                )
                self.logger.info("✅ Gemini LLM initialized successfully")
                return llm
            else:
                self.logger.warning("❌ No API key found for Gemini")
                return None

        except Exception as e:
            self.logger.error(f"❌ Error setting up Gemini LLM: {e}")
            return None

    def get_billing_data(self) -> dict[str, Any]:
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
                    [
                        "gcloud",
                        "firestore",
                        "databases",
                        "list",
                        "--format=value(name)",
                    ],
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
            self.logger.error(f"Error getting billing data: {e}")
            return None

    def analyze_billing_with_gemini(self, billing_data) -> dict[str, Any]:
        """Analyze billing data using Gemini LLM"""
        if not self.llm:
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
            response = self.llm.invoke([HumanMessage(content=prompt)])

            return {
                "gemini_analysis": response.content,
                "billing_data": billing_data,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error in Gemini analysis: {e}")
            return {"error": f"Gemini analysis failed: {str(e)}"}

    async def run_ghostbusters_analysis(self, project_path) -> dict[str, Any]:
        """Run Ghostbusters analysis on the project"""
        try:
            # Import Ghostbusters orchestrator
            from src.ghostbusters.ghostbusters_orchestrator import (
                GhostbustersOrchestrator,
            )

            # Run Ghostbusters analysis
            orchestrator = GhostbustersOrchestrator(project_path)
            result = await orchestrator.run_ghostbusters()

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

    async def analyze_project(self, project_path) -> dict[str, Any]:
        """Complete analysis combining Ghostbusters with Gemini billing insights"""
        analysis_id = str(uuid.uuid4())

        self.logger.info("Starting Gemini-Integrated Ghostbusters Billing Analysis")
        self.logger.info(f"Analysis ID: {analysis_id}")

        # Step 1: Get billing data
        self.logger.info("📊 Collecting GCP billing data...")
        billing_data = self.get_billing_data()

        if not billing_data:
            return {
                "status": "error",
                "error_message": "Failed to collect billing data",
            }

        # Step 2: Analyze billing with Gemini
        self.logger.info("🔍 Analyzing billing data with Gemini...")
        gemini_analysis = self.analyze_billing_with_gemini(billing_data)

        # Step 3: Run Ghostbusters analysis
        self.logger.info("👻 Running Ghostbusters analysis...")
        ghostbusters_result = await self.run_ghostbusters_analysis(project_path)

        # Step 4: Combine results
        combined_result = {
            "analysis_id": analysis_id,
            "project_path": project_path,
            "billing_analysis": gemini_analysis,
            "ghostbusters_analysis": ghostbusters_result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }

        self.logger.info(
            "✅ Gemini-Integrated Ghostbusters Billing Analysis completed!"
        )

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
            "full_analysis": combined_result,
        }


async def main() -> None:
    """Main function for testing the Gemini billing analyzer"""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    analyzer = GeminiBillingAnalyzer()

    print("🚀 Starting Gemini-Integrated Ghostbusters Billing Analysis...")
    print("📊 Project: elmo-fuzzy-giggle")
    print(f'🤖 Gemini LLM: {"✅ Available" if analyzer.llm else "❌ Not available"}')

    result = await analyzer.analyze_project(".")

    print("\n" + "=" * 60)
    print("📋 ANALYSIS RESULTS")
    print("=" * 60)
    print(f'Status: {result["status"]}')
    print(f'Analysis ID: {result["analysis_id"]}')
    print(
        f'Billing Analysis: {"✅ Available" if result["billing_analysis_available"] else "❌ Not available"}',
    )
    print(
        f'Ghostbusters Analysis: {"✅ Available" if result["ghostbusters_analysis_available"] else "❌ Not available"}',
    )

    if result["summary"]:
        print("\n📊 Summary:")
        print(f'  Project ID: {result["summary"]["project_id"]}')
        print(f'  Enabled Services: {result["summary"]["enabled_services"]}')
        print(f'  Resources: {result["summary"]["resources"]}')
        print(
            f'  Ghostbusters Delusions: {result["summary"]["ghostbusters_delusions"]}',
        )
        print(
            f'  Ghostbusters Confidence: {result["summary"]["ghostbusters_confidence"]}',
        )

    if (
        result.get("full_analysis", {})
        .get("billing_analysis", {})
        .get("gemini_analysis")
    ):
        print("\n🤖 Gemini Analysis:")
        print("-" * 40)
        print(result["full_analysis"]["billing_analysis"]["gemini_analysis"])

    return result


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
