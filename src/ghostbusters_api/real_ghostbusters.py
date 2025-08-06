#!/usr/bin/env python3
"""
Real Ghostbusters Integration
Actually uses the real Ghostbusters agents for analysis
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

# Import base agents directly
from agents import (
    ArchitectureExpert,
    BuildExpert,
    CodeQualityExpert,
    ModelExpert,
    SecurityExpert,
    TestExpert,
)

# Map agent names to actual agent classes
AGENT_MAP = {
    "security": SecurityExpert,
    "code_quality": CodeQualityExpert,
    "test": TestExpert,
    "build": BuildExpert,
    "architecture": ArchitectureExpert,
    "model": ModelExpert,
}

logger = logging.getLogger(__name__)


async def run_real_ghostbusters_analysis(
    project_path: str,
    agents: list[str],
) -> dict[str, Any]:
    """Run real Ghostbusters analysis using actual agents"""
    try:
        logger.info(
            f"Running real Ghostbusters analysis on {project_path} with agents: {agents}",
        )

        project_path_obj = Path(project_path)
        if not project_path_obj.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

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
                result = await agent.detect_delusions(project_path_obj)

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

        return {
            "success": True,
            "delusions_found": len(all_delusions),
            "agents_run": agents_run,
            "project_path": project_path,
            "confidence": avg_confidence,
            "delusions": all_delusions,
            "recommendations": list(set(all_recommendations)),  # Remove duplicates
            "analysis_time": "real",  # We'll calculate this properly
        }

    except Exception as e:
        logger.error(f"Real Ghostbusters analysis failed: {e}")
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


def run_real_ghostbusters_sync(project_path: str, agents: list[str]) -> dict[str, Any]:
    """Synchronous wrapper for real Ghostbusters analysis"""
    return asyncio.run(run_real_ghostbusters_analysis(project_path, agents))


if __name__ == "__main__":
    # Test the real integration
    import json

    result = run_real_ghostbusters_sync(".", ["security", "code_quality"])
    print(json.dumps(result, indent=2))
