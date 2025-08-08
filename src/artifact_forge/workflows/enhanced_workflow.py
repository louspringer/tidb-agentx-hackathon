#!/usr/bin/env python3
"""
Enhanced ArtifactForge Workflow with LangGraph Orchestration
Integrates enhanced parser with intelligent fixes and full codebase scaling
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from langgraph.graph import END, StateGraph

from src.artifact_forge.agents.artifact_correlator import ArtifactCorrelator
from src.artifact_forge.agents.artifact_detector import ArtifactDetector
from src.artifact_forge.agents.artifact_optimizer import ArtifactOptimizer
from src.artifact_forge.agents.artifact_parser import ArtifactParser
from src.artifact_forge.agents.artifact_synthesizer import ArtifactSynthesizer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EnhancedArtifactForgeState:
    """Enhanced state for ArtifactForge workflow with intelligent fixes"""

    root_path: str
    artifacts: list[dict[str, Any]] = None  # type: ignore
    parsed_artifacts: list[dict[str, Any]] = None  # type: ignore
    relationships: list[dict[str, Any]] = None  # type: ignore
    optimization_opportunities: list[dict[str, Any]] = None  # type: ignore
    insights: list[dict[str, Any]] = None  # type: ignore
    fixes_applied: list[dict[str, Any]] = None  # type: ignore
    confidence_score: float = 0.0
    processing_time: float = 0.0
    errors: list[str] = None  # type: ignore
    block_analysis: dict[str, Any] = None  # type: ignore


class EnhancedArtifactForgeWorkflow:
    """Enhanced ArtifactForge workflow with LangGraph orchestration"""

    def __init__(self) -> None:
        self.detector = ArtifactDetector()
        self.parser = ArtifactParser()
        self.correlator = ArtifactCorrelator()
        self.optimizer = ArtifactOptimizer()
        self.synthesizer = ArtifactSynthesizer()

        # Create LangGraph workflow
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        """Create LangGraph workflow with enhanced orchestration"""
        workflow = StateGraph(EnhancedArtifactForgeState)

        # Add nodes
        workflow.add_node("detect_artifacts", self._detect_artifacts_node)
        workflow.add_node("parse_artifacts", self._parse_artifacts_node)
        workflow.add_node("correlate_artifacts", self._correlate_artifacts_node)
        workflow.add_node("optimize_artifacts", self._optimize_artifacts_node)
        workflow.add_node("apply_intelligent_fixes", self._apply_intelligent_fixes_node)
        workflow.add_node("synthesize_insights", self._synthesize_insights_node)
        workflow.add_node("validate_fixes", self._validate_fixes_node)

        # Define workflow edges
        workflow.set_entry_point("detect_artifacts")
        workflow.add_edge("detect_artifacts", "parse_artifacts")
        workflow.add_edge("parse_artifacts", "correlate_artifacts")
        workflow.add_edge("correlate_artifacts", "optimize_artifacts")
        workflow.add_edge("optimize_artifacts", "apply_intelligent_fixes")
        workflow.add_edge("apply_intelligent_fixes", "synthesize_insights")
        workflow.add_edge("synthesize_insights", "validate_fixes")
        workflow.add_edge("validate_fixes", END)

        return workflow.compile()  # type: ignore

    def _detect_artifacts_node(
        self,
        state: EnhancedArtifactForgeState,
    ) -> EnhancedArtifactForgeState:
        """Detect artifacts in the codebase"""
        logger.info("🔍 **STEP 1: DETECTING ARTIFACTS**")

        try:
            artifacts = self.detector.detect_artifacts(state.root_path)
            state.artifacts = artifacts  # type: ignore
            logger.info(f"  Found {len(artifacts)} artifacts")
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            state.errors = state.errors or []
            state.errors.append(f"Detection failed: {e}")

        return state

    def _parse_artifacts_node(
        self,
        state: EnhancedArtifactForgeState,
    ) -> EnhancedArtifactForgeState:
        """Parse artifacts with enhanced error recovery"""
        logger.info("📝 **STEP 2: PARSING ARTIFACTS**")

        if not state.artifacts:
            logger.warning("No artifacts to parse")
            return state

        parsed_artifacts = []
        errors = []

        for artifact in state.artifacts[:50]:  # Limit for performance
            try:
                # Convert ArtifactInfo to dict format for parser

                parsed = self.parser.parse_artifact(
                    artifact.path,  # type: ignore
                    artifact.artifact_type,  # type: ignore
                )
                parsed_artifacts.append(
                    {
                        "path": parsed.path,
                        "type": parsed.artifact_type,
                        "data": parsed.parsed_data,
                        "errors": parsed.parsing_errors,
                        "block_analysis": parsed.block_analysis,
                    },
                )

                # Log enhanced parser results
                if parsed.block_analysis:
                    blocks = parsed.block_analysis.get("total_blocks", 0)
                    issues = len(parsed.block_analysis.get("indentation_issues", []))
                    if blocks > 0 or issues > 0:
                        logger.info(
                            f"  {parsed.path}: {blocks} blocks, {issues} indentation issues",
                        )

            except Exception as e:
                errors.append(f"Parsing failed for {artifact.path}: {e}")  # type: ignore

        state.parsed_artifacts = parsed_artifacts
        if errors:
            state.errors = state.errors or []
            state.errors.extend(errors)

        logger.info(f"  Parsed {len(parsed_artifacts)} artifacts")
        return state

    def _correlate_artifacts_node(
        self,
        state: EnhancedArtifactForgeState,
    ) -> EnhancedArtifactForgeState:
        """Correlate artifacts with performance limits"""
        logger.info("🔗 **STEP 3: CORRELATING ARTIFACTS**")

        if not state.parsed_artifacts:
            logger.warning("No parsed artifacts to correlate")
            return state

        try:
            relationships = self.correlator.correlate_artifacts(state.parsed_artifacts)
            state.relationships = relationships  # type: ignore
            logger.info(f"  Found {len(relationships)} relationships")
        except Exception as e:
            logger.error(f"Correlation failed: {e}")
            state.errors = state.errors or []
            state.errors.append(f"Correlation failed: {e}")

        return state

    def _optimize_artifacts_node(
        self,
        state: EnhancedArtifactForgeState,
    ) -> EnhancedArtifactForgeState:
        """Find optimization opportunities including syntax errors"""
        logger.info("🎯 **STEP 4: OPTIMIZING ARTIFACTS**")

        if not state.parsed_artifacts:
            logger.warning("No parsed artifacts to optimize")
            return state

        try:
            opportunities = self.optimizer.optimize_artifacts(state.parsed_artifacts)
            state.optimization_opportunities = opportunities  # type: ignore
            logger.info(f"  Found {len(opportunities)} optimization opportunities")
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            state.errors = state.errors or []
            state.errors.append(f"Optimization failed: {e}")

        return state

    def _apply_intelligent_fixes_node(
        self,
        state: EnhancedArtifactForgeState,
    ) -> EnhancedArtifactForgeState:
        """Apply intelligent fixes based on block analysis"""
        logger.info("🔧 **STEP 5: APPLYING INTELLIGENT FIXES**")

        fixes_applied = []

        if state.optimization_opportunities:
            for opportunity in state.optimization_opportunities:
                if opportunity["type"] == "syntax_error":
                    fix_result = self._apply_syntax_fix(opportunity, state)
                    if fix_result:
                        fixes_applied.append(fix_result)

        state.fixes_applied = fixes_applied
        logger.info(f"  Applied {len(fixes_applied)} intelligent fixes")
        return state

    def _apply_syntax_fix(
        self,
        opportunity: dict[str, Any],
        state: EnhancedArtifactForgeState,
    ) -> Optional[dict[str, Any]]:
        """Apply intelligent syntax fix based on block analysis"""
        file_path = opportunity["file_path"]
        line_number = opportunity.get("line_number")

        # Find the parsed artifact for this file
        parsed_artifact = None
        for artifact in state.parsed_artifacts:
            if artifact["path"] == file_path:
                parsed_artifact = artifact
                break

        if not parsed_artifact or not parsed_artifact.get("block_analysis"):
            return None

        # Use block analysis to understand the scope
        block_analysis = parsed_artifact["block_analysis"]
        blocks = block_analysis.get("blocks", [])

        # Find the block containing the problematic line
        target_block = None
        for block in blocks:
            if block["start_line"] <= line_number <= block["end_line"]:
                target_block = block
                break

        if target_block:
            # Apply fix within the block scope
            fix_result = self._fix_block_indentation(file_path, target_block)
            return {
                "file_path": file_path,
                "block_type": target_block["block_type"],
                "block_lines": f"{target_block['start_line']}-{target_block['end_line']}",
                "fix_type": "indentation",
                "success": fix_result,
            }

        return None

    def _fix_block_indentation(self, file_path: str, block: dict[str, Any]) -> bool:
        """Fix indentation within a specific block scope"""
        try:
            with open(file_path) as f:
                lines = f.readlines()

            # Fix indentation within the block
            start_line = block["start_line"] - 1  # Convert to 0-based
            end_line = block["end_line"]

            # Apply consistent indentation
            block["indent_level"]
            for i in range(start_line, end_line):
                if i < len(lines):
                    line = lines[i]
                    if line.strip() and not line.startswith("#"):
                        # Ensure consistent indentation
                        stripped = line.strip()
                        current_indent = len(line) - len(line.lstrip())

                        if current_indent % 4 != 0:
                            # Fix indentation to be multiple of 4
                            new_indent = (current_indent // 4) * 4
                            lines[i] = " " * new_indent + stripped + "\n"

            # Write back the fixed content
            with open(file_path, "w") as f:
                f.writelines(lines)

            return True

        except Exception as e:
            logger.error(f"Failed to fix indentation for {file_path}: {e}")
            return False

    def _synthesize_insights_node(
        self,
        state: EnhancedArtifactForgeState,
    ) -> EnhancedArtifactForgeState:
        """Synthesize insights from all analysis"""
        logger.info("🧠 **STEP 6: SYNTHESIZING INSIGHTS**")

        try:
            insights = self.synthesizer.synthesize_insights(
                state.parsed_artifacts or [],
                state.relationships or [],
                state.optimization_opportunities or [],
            )
            state.insights = insights  # type: ignore
            logger.info(f"  Generated {len(insights)} insights")
        except Exception as e:
            logger.error(f"Insight synthesis failed: {e}")
            state.errors = state.errors or []
            state.errors.append(f"Insight synthesis failed: {e}")

        return state

    def _validate_fixes_node(
        self,
        state: EnhancedArtifactForgeState,
    ) -> EnhancedArtifactForgeState:
        """Validate that fixes were successful"""
        logger.info("✅ **STEP 7: VALIDATING FIXES**")

        validation_results = []

        if state.fixes_applied:
            for fix in state.fixes_applied:
                if fix["success"]:
                    # Test if the file now parses correctly
                    try:
                        import ast

                        with open(fix["file_path"]) as f:
                            content = f.read()
                        ast.parse(content)
                        validation_results.append(
                            {
                                "file": fix["file_path"],
                                "status": "SUCCESS",
                                "message": "File now parses correctly",
                            },
                        )
                    except SyntaxError as e:
                        validation_results.append(
                            {
                                "file": fix["file_path"],
                                "status": "PARTIAL",
                                "message": f"Still has syntax errors: {e}",
                            },
                        )

        state.block_analysis = {
            "validation_results": validation_results,
            "fixes_applied": len(state.fixes_applied or []),
            "successful_fixes": len(
                [f for f in state.fixes_applied or [] if f["success"]],
            ),
        }

        logger.info(f"  Validated {len(validation_results)} fixes")
        return state

    def run_workflow(self, root_path: str) -> EnhancedArtifactForgeState:
        """Run the enhanced ArtifactForge workflow"""
        start_time = datetime.now()

        # Initialize state
        initial_state = EnhancedArtifactForgeState(
            root_path=root_path,
            artifacts=[],
            parsed_artifacts=[],
            relationships=[],
            optimization_opportunities=[],
            insights=[],
            fixes_applied=[],
            errors=[],
        )

        # Run the workflow
        try:
            final_state = self.workflow.invoke(initial_state)  # type: ignore

            # Calculate confidence and processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            final_state.processing_time = processing_time

            # Calculate confidence based on success rates
            total_artifacts = len(final_state.artifacts or [])
            successful_parses = len(
                [a for a in final_state.parsed_artifacts or [] if not a.get("errors")],
            )
            successful_fixes = len(
                [f for f in final_state.fixes_applied or [] if f["success"]],
            )

            if total_artifacts > 0:
                parse_rate = successful_parses / total_artifacts
                fix_rate = successful_fixes / max(
                    len(final_state.fixes_applied or []),
                    1,
                )
                final_state.confidence_score = (parse_rate + fix_rate) / 2
            else:
                final_state.confidence_score = 0.0

            return final_state  # type: ignore

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            final_state = initial_state
            final_state.errors = [f"Workflow failed: {e}"]
            final_state.processing_time = (datetime.now() - start_time).total_seconds()
            return final_state


def main() -> None:
    """Test the enhanced ArtifactForge workflow"""
    print("🚀 **ENHANCED ARTIFACTFORGE WORKFLOW TEST**")
    print("=" * 50)

    workflow = EnhancedArtifactForgeWorkflow()
    state = workflow.run_workflow(".")

    print("\n✅ **WORKFLOW COMPLETED**")
    print(f"  Processing time: {state.processing_time:.2f} seconds")
    print(f"  Confidence score: {state.confidence_score:.2f}")

    print("\n📊 **WORKFLOW SUMMARY:**")
    print(f"Artifacts discovered: {len(state.artifacts or [])}")
    print(f"Artifacts parsed: {len(state.parsed_artifacts or [])}")
    print(f"Relationships found: {len(state.relationships or [])}")
    print(f"Optimization opportunities: {len(state.optimization_opportunities or [])}")
    print(f"Fixes applied: {len(state.fixes_applied or [])}")
    print(f"Insights generated: {len(state.insights or [])}")
    print(f"Processing time: {state.processing_time:.2f} seconds")
    print(f"Confidence score: {state.confidence_score:.2f}")

    if state.errors:
        print("\n❌ **ERRORS:**")
        for error in state.errors:
            print(f"  - {error}")

    if state.block_analysis:
        print("\n🔧 **FIX VALIDATION:**")
        validation_results = state.block_analysis.get("validation_results", [])
        for result in validation_results:
            status_emoji = "✅" if result["status"] == "SUCCESS" else "⚠️"
            print(f"  {status_emoji} {result['file']}: {result['message']}")


if __name__ == "__main__":
    main()
