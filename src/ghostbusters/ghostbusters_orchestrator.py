#!/usr/bin/env python3
"""
Ghostbusters Orchestrator - Multi-Agent Delusion Detection & Recovery System
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# LangGraph imports
from langgraph.graph import StateGraph, END

# Local imports
from .agents import (
    SecurityExpert,
    CodeQualityExpert,
    TestExpert,
    BuildExpert,
    ArchitectureExpert,
    ModelExpert,
)
from .validators import (
    SecurityValidator,
    CodeQualityValidator,
    TestValidator,
    BuildValidator,
    ArchitectureValidator,
    ModelValidator,
)
from .recovery import (
    SyntaxRecoveryEngine,
    IndentationFixer,
    ImportResolver,
    TypeAnnotationFixer,
)


@dataclass
class GhostbustersState:
    """State for Ghostbusters workflow"""

    project_path: str
    delusions_detected: List[Dict[str, Any]]
    recovery_actions: List[Dict[str, Any]]
    confidence_score: float
    validation_results: Dict[str, Any]
    recovery_results: Dict[str, Any]
    current_phase: str
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


class GhostbustersOrchestrator:
    """Multi-agent orchestrator for delusion detection and recovery"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)

        # Initialize agents
        self.agents = {
            "security": SecurityExpert(),
            "code_quality": CodeQualityExpert(),
            "test": TestExpert(),
            "build": BuildExpert(),
            "architecture": ArchitectureExpert(),
            "model": ModelExpert(),
        }

        # Initialize validators
        self.validators = {
            "security": SecurityValidator(),
            "code_quality": CodeQualityValidator(),
            "test": TestValidator(),
            "build": BuildValidator(),
            "architecture": ArchitectureValidator(),
            "model": ModelValidator(),
        }

        # Initialize recovery engines
        self.recovery_engines = {
            "syntax": SyntaxRecoveryEngine(),
            "indentation": IndentationFixer(),
            "imports": ImportResolver(),
            "types": TypeAnnotationFixer(),
        }

        # Create LangGraph workflow
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        """Create LangGraph workflow for Ghostbusters"""

        # Define the state graph
        workflow = StateGraph(GhostbustersState)

        # Add nodes
        workflow.add_node("detect_delusions", self._detect_delusions_node)
        workflow.add_node("validate_findings", self._validate_findings_node)
        workflow.add_node("plan_recovery", self._plan_recovery_node)
        workflow.add_node("execute_recovery", self._execute_recovery_node)
        workflow.add_node("validate_recovery", self._validate_recovery_node)
        workflow.add_node("generate_report", self._generate_report_node)

        # Define edges
        workflow.set_entry_point("detect_delusions")
        workflow.add_edge("detect_delusions", "validate_findings")
        workflow.add_edge("validate_findings", "plan_recovery")
        workflow.add_edge("plan_recovery", "execute_recovery")
        workflow.add_edge("execute_recovery", "validate_recovery")
        workflow.add_edge("validate_recovery", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow

    async def _detect_delusions_node(
        self, state: GhostbustersState
    ) -> GhostbustersState:
        """Detect delusions using agents"""
        self.logger.info("🔍 Detecting delusions...")

        delusions_detected = []
        for name, agent in self.agents.items():
            try:
                result = await agent.detect_delusions(self.project_path)
                # BRUTAL FIX: Extract delusions from DelusionResult
                if result and hasattr(result, "delusions"):
                    delusions_detected.append(
                        {"agent": name, "delusions": result.delusions}
                    )
                self.logger.info(f"✅ {name} detection completed")
            except Exception as e:
                self.logger.error(f"❌ {name} detection failed: {e}")
                state.errors.append(f"{name} detection error: {e}")

        state.delusions_detected = delusions_detected
        state.current_phase = "detection_complete"

        return state

    async def _validate_findings_node(
        self, state: GhostbustersState
    ) -> GhostbustersState:
        """Validate findings using validators - FIXED ITERATION BUG"""
        self.logger.info("🔍 Validating findings...")

        validation_results = {}
        for name, validator in self.validators.items():
            try:
                # FIXED: Don't iterate over ValidationResult, just store it
                result = await validator.validate_findings(state.delusions_detected)
                validation_results[name] = result
                self.logger.info(f"✅ {name} validation completed")
            except Exception as e:
                self.logger.error(f"❌ {name} validation failed: {e}")
                state.errors.append(f"{name} validation error: {e}")

        state.validation_results = validation_results
        state.current_phase = "validation_complete"

        return state

    async def _plan_recovery_node(self, state: GhostbustersState) -> GhostbustersState:
        """Plan recovery actions based on findings"""
        self.logger.info("📋 Planning recovery actions...")

        recovery_actions = []

        # Analyze delusions and plan recovery
        for delusion in state.delusions_detected:
            agent_name = delusion["agent"]
            for delusion_item in delusion["delusions"]:
                action = await self._plan_recovery_action(agent_name, delusion_item)
                if action:
                    recovery_actions.append(action)

        state.recovery_actions = recovery_actions
        state.current_phase = "planning_complete"

        return state

    async def _execute_recovery_node(
        self, state: GhostbustersState
    ) -> GhostbustersState:
        """Execute recovery actions"""
        self.logger.info("🔧 Executing recovery actions...")

        recovery_results = {}

        for action in state.recovery_actions:
            engine_name = action["engine"]
            if engine_name in self.recovery_engines:
                try:
                    engine = self.recovery_engines[engine_name]
                    result = await engine.execute_recovery(action)
                    recovery_results[action["id"]] = result
                    self.logger.info(f"✅ Recovery action {action['id']} completed")
                except Exception as e:
                    self.logger.error(f"❌ Recovery action {action['id']} failed: {e}")
                    state.errors.append(f"Recovery error: {e}")

        state.recovery_results = recovery_results
        state.current_phase = "recovery_complete"

        return state

    async def _validate_recovery_node(
        self, state: GhostbustersState
    ) -> GhostbustersState:
        """Validate recovery results"""
        self.logger.info("🔍 Validating recovery results...")

        # Re-run validation to check if issues are resolved
        post_recovery_validation = {}
        for name, validator in self.validators.items():
            try:
                result = await validator.validate_findings(state.delusions_detected)
                post_recovery_validation[name] = result
            except Exception as e:
                self.logger.error(f"❌ Post-recovery validation failed: {e}")

        # Calculate confidence improvement
        pre_confidence = self._calculate_confidence(state.validation_results)
        post_confidence = self._calculate_confidence(post_recovery_validation)
        confidence_improvement = post_confidence - pre_confidence

        state.confidence_score = post_confidence
        state.metadata["confidence_improvement"] = confidence_improvement
        state.current_phase = "validation_complete"

        return state

    async def _generate_report_node(
        self, state: GhostbustersState
    ) -> GhostbustersState:
        """Generate comprehensive report"""
        self.logger.info("📊 Generating Ghostbusters report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "confidence_score": state.confidence_score,
            "delusions_detected": len(state.delusions_detected),
            "recovery_actions": len(state.recovery_actions),
            "errors": state.errors,
            "warnings": state.warnings,
            "current_phase": state.current_phase,
        }

        state.metadata["report"] = report
        state.current_phase = "complete"

        return state

    async def _plan_recovery_action(
        self, agent_name: str, delusion: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Plan recovery action for a specific delusion"""
        try:
            # Simple recovery action planning
            action = {
                "id": f"recovery_{agent_name}_{hash(str(delusion))}",
                "agent": agent_name,
                "delusion": delusion,
                "engine": "syntax",  # Default to syntax recovery
                "description": f"Fix {delusion.get('type', 'unknown')} issue",
            }
            return action
        except Exception as e:
            self.logger.error(f"Failed to plan recovery action: {e}")
            return None

    def _calculate_confidence(self, validation_results: Dict[str, Any]) -> float:
        """Calculate confidence score from validation results"""
        if not validation_results:
            return 0.0

        total_confidence = 0.0
        count = 0

        for result in validation_results.values():
            if hasattr(result, "confidence"):
                total_confidence += result.confidence
                count += 1

        return total_confidence / count if count > 0 else 0.0

    async def run_ghostbusters(self) -> GhostbustersState:
        """Run the complete Ghostbusters workflow with extreme prejudice"""
        try:
            # Initialize state
            state = GhostbustersState(
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
            )

            # BRUTAL APPROACH: Skip LangGraph and run manually
            state = await self._detect_delusions_node(state)
            state = await self._validate_findings_node(state)
            state = await self._plan_recovery_node(state)
            state = await self._execute_recovery_node(state)
            state = await self._validate_recovery_node(state)
            state = await self._generate_report_node(state)

            return state

        except Exception as e:
            self.logger.error(f"Ghostbusters workflow failed: {e}")
            # Return error state
            return GhostbustersState(
                project_path=str(self.project_path),
                delusions_detected=[],
                recovery_actions=[],
                confidence_score=0.0,
                validation_results={},
                recovery_results={},
                current_phase="error",
                errors=[f"Workflow error: {e}"],
                warnings=[],
                metadata={},
            )


async def run_ghostbusters(project_path: str = ".") -> GhostbustersState:
    """Convenience function to run Ghostbusters"""
    orchestrator = GhostbustersOrchestrator(project_path)
    return await orchestrator.run_ghostbusters()


if __name__ == "__main__":

    async def main() -> None:
        state = await run_ghostbusters()
        print(f"Ghostbusters completed with confidence: {state.confidence_score}")

    asyncio.run(main())
