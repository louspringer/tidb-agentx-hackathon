#!/usr/bin/env python3
"""
Enhanced Ghostbusters with Real Analysis and Smart Tool Discovery
"""

import asyncio
import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Import our tool discovery
sys.path.append(str(Path(__file__).parent))
from tool_discovery import ToolDiscovery


@dataclass
class EnhancedGhostbustersState:
    """Enhanced state for Ghostbusters workflow"""

    project_path: str
    delusions_detected: list[dict[str, Any]]
    recovery_actions: list[dict[str, Any]]
    confidence_score: float
    validation_results: dict[str, Any]
    recovery_results: dict[str, Any]
    current_phase: str
    errors: list[str]
    warnings: list[str]
    metadata: dict[str, Any]
    analysis_details: dict[str, Any]
    tool_discovery: dict[str, Any]


class EnhancedGhostbustersOrchestrator:
    """Enhanced Ghostbusters with real analysis and smart tool discovery"""

    def __init__(self, project_path: str = ".") -> None:
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)
        self.tool_discovery = ToolDiscovery(project_path)
        self.logger.info(
            "🎯 Initializing Enhanced Ghostbusters for %s",
            self.project_path,
        )

    async def run_real_analysis(self) -> EnhancedGhostbustersState:
        """Run real analysis with detailed logging and smart recommendations"""

        self.logger.info("🚀 Starting Enhanced Ghostbusters Analysis")

        # Initialize state
        state = EnhancedGhostbustersState(
            project_path=str(self.project_path),
            delusions_detected=[],
            recovery_actions=[],
            confidence_score=0.0,
            validation_results={},
            recovery_results={},
            current_phase="initialized",
            errors=[],
            warnings=[],
            metadata={},
            analysis_details={},
            tool_discovery=self.tool_discovery.get_tool_summary(),
        )

        # Phase 1: Real MyPy Analysis
        self.logger.info("🔍 Phase 1: Running MyPy Analysis")
        mypy_results = await self._run_mypy_analysis()
        state.analysis_details["mypy"] = mypy_results
        self.logger.info("📊 MyPy found %d errors", len(mypy_results["errors"]))

        # Phase 2: Real Flake8 Analysis
        self.logger.info("🔍 Phase 2: Running Flake8 Analysis")
        flake8_results = await self._run_flake8_analysis()
        state.analysis_details["flake8"] = flake8_results
        self.logger.info("📊 Flake8 found %d errors", len(flake8_results["errors"]))

        # Phase 3: Real AST Analysis
        self.logger.info("🔍 Phase 3: Running AST Analysis")
        ast_results = await self._run_ast_analysis()
        state.analysis_details["ast"] = ast_results
        self.logger.info("📊 AST found %d syntax errors", len(ast_results["errors"]))

        # Phase 4: Calculate Real Confidence
        self.logger.info("🔍 Phase 4: Calculating Real Confidence")
        confidence = self._calculate_real_confidence(state.analysis_details)
        state.confidence_score = confidence
        self.logger.info("📊 Real confidence score: %.2f%%", confidence * 100)

        # Phase 5: Generate Smart Recommendations with Tool Discovery
        self.logger.info("🔍 Phase 5: Generating Smart Recommendations")
        recommendations = self.tool_discovery.get_smart_recommendations(
            state.analysis_details,
        )
        state.metadata["recommendations"] = recommendations
        self.logger.info("📊 Generated %d smart recommendations", len(recommendations))

        state.current_phase = "analysis_complete"
        self.logger.info("✅ Enhanced Ghostbusters Analysis Complete")

        return state

    async def _run_mypy_analysis(self) -> dict[str, Any]:
        """Run real MyPy analysis"""
        try:
            result = subprocess.run(
                ["uv", "run", "mypy", "src/", "--ignore-missing-imports"],
                capture_output=True,
                text=True,
                cwd=self.project_path,
                check=False,
            )

            errors = []
            if result.stdout:
                for line in result.stdout.split("\n"):
                    if line.strip() and "error:" in line:
                        errors.append(line.strip())

            return {
                "exit_code": result.returncode,
                "errors": errors,
                "total_errors": len(errors),
                "success": result.returncode == 0,
            }
        except Exception as e:
            self.logger.error("❌ MyPy analysis failed: %s", e)
            return {"errors": [], "total_errors": 0, "success": False, "error": str(e)}

    async def _run_flake8_analysis(self) -> dict[str, Any]:
        """Run real Flake8 analysis"""
        try:
            result = subprocess.run(
                ["uv", "run", "flake8", "src/"],
                capture_output=True,
                text=True,
                cwd=self.project_path,
                check=False,
            )

            errors = []
            if result.stdout:
                for line in result.stdout.split("\n"):
                    if line.strip():
                        errors.append(line.strip())

            return {
                "exit_code": result.returncode,
                "errors": errors,
                "total_errors": len(errors),
                "success": result.returncode == 0,
            }
        except Exception as e:
            self.logger.error("❌ Flake8 analysis failed: %s", e)
            return {"errors": [], "total_errors": 0, "success": False, "error": str(e)}

    async def _run_ast_analysis(self) -> dict[str, Any]:
        """Run real AST analysis"""
        errors = []
        try:
            for py_file in self.project_path.rglob("*.py"):
                try:
                    compile(py_file.read_text(), str(py_file), "exec")
                except SyntaxError as e:
                    errors.append(f"Syntax error in {py_file}: {e}")
                except Exception as e:
                    errors.append(f"Error in {py_file}: {e}")
        except Exception as e:
            self.logger.error("❌ AST analysis failed: %s", e)
            errors.append(f"AST analysis error: {e}")

        return {
            "errors": errors,
            "total_errors": len(errors),
            "success": len(errors) == 0,
        }

    def _calculate_real_confidence(self, analysis_details: dict[str, Any]) -> float:
        """Calculate real confidence based on actual analysis"""

        total_issues = 0
        total_files = 0

        # Count Python files
        for py_file in self.project_path.rglob("*.py"):
            total_files += 1

        # Count issues from each analysis
        if "mypy" in analysis_details:
            total_issues += analysis_details["mypy"]["total_errors"]

        if "flake8" in analysis_details:
            total_issues += analysis_details["flake8"]["total_errors"]

        if "ast" in analysis_details:
            total_issues += analysis_details["ast"]["total_errors"]

        # Calculate confidence based on issues per file
        if total_files == 0:
            return 1.0  # Perfect if no files

        issues_per_file = total_issues / total_files

        # Confidence decreases with more issues per file
        # 0 issues per file = 100% confidence
        # 10+ issues per file = 0% confidence
        confidence = max(0.0, 1.0 - (issues_per_file / 10.0))

        self.logger.info(
            "📊 Analysis: %d issues in %d files",
            total_issues,
            total_files,
        )
        self.logger.info("📊 Issues per file: %.2", issues_per_file)
        self.logger.info("📊 Calculated confidence: %.2f%%", confidence * 100)

        return confidence


async def run_enhanced_ghostbusters(
    project_path: str = ".",
) -> EnhancedGhostbustersState:
    """Run enhanced Ghostbusters with real analysis and smart tool discovery"""
    orchestrator = EnhancedGhostbustersOrchestrator(project_path)
    return await orchestrator.run_real_analysis()


if __name__ == "__main__":

    async def main() -> None:
        state = await run_enhanced_ghostbusters()
        print("🎯 Enhanced Ghostbusters Results:")
        print(f"📊 Confidence: {state.confidence_score:.2%}")
        print(f"📊 Phase: {state.current_phase}")
        print(f"📊 Built Tools: {state.tool_discovery['total_built']}")
        print(f"📊 Available Tools: {state.tool_discovery['total_available']}")
        print("📊 Smart Recommendations:")
        for rec in state.metadata.get("recommendations", []):
            print(f"   • {rec}")

    asyncio.run(main())
