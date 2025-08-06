#!/usr/bin/env python3
"""
Ghostbusters Orchestrator - Multi-Agent Delusion Detection & Recovery System
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# LangGraph imports
from langgraph.graph import END, StateGraph

# Local imports
from .agents import (
    ArchitectureExpert,
    BuildExpert,
    CodeQualityExpert,
    ModelExpert,
    SecurityExpert,
    TestExpert,
)
from .recovery import (
    ImportResolver,
    IndentationFixer,
    SyntaxRecoveryEngine,
    TypeAnnotationFixer,
)
from .validators import (
    ArchitectureValidator,
    BuildValidator,
    CodeQualityValidator,
    ModelValidator,
    SecurityValidator,
    TestValidator,
)


@dataclass
class GhostbustersState:
    """State for Ghostbusters workflow"""

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


class GhostbustersOrchestrator:
    """Multi-agent orchestrator for delusion detection and recovery"""

    def __init__(self, project_path: str = ".") -> None:
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
        self,
        state: GhostbustersState,
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
                        {"agent": name, "delusions": result.delusions},
                    )
                self.logger.info(f"✅ {name} detection completed")
            except Exception as e:
                self.logger.error(f"❌ {name} detection failed: {e}")
                state.errors.append(f"{name} detection error: {e}")

        state.delusions_detected = delusions_detected
        state.current_phase = "detection_complete"

        return state

    async def _validate_findings_node(
        self,
        state: GhostbustersState,
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
        for agent_result in state.delusions_detected:
            agent_name = agent_result["agent"]
            delusions = agent_result.get("delusions", [])
            for delusion_item in delusions:
                action = await self._plan_recovery_action(agent_name, delusion_item)
                if action:
                    recovery_actions.append(action)

        state.recovery_actions = recovery_actions
        state.current_phase = "planning_complete"

        return state

    async def _execute_recovery_node(
        self,
        state: GhostbustersState,
    ) -> GhostbustersState:
        """Execute recovery actions"""
        self.logger.info("🔧 Executing recovery actions...")

        recovery_results = {}

        # Limit recovery actions to prevent infinite loops
        max_recovery_actions = 10
        actions_to_execute = state.recovery_actions[:max_recovery_actions]

        for action in actions_to_execute:
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

        if len(state.recovery_actions) > max_recovery_actions:
            self.logger.warning(
                f"⚠️ Limited recovery actions to {max_recovery_actions} to prevent infinite loops",
            )

        state.recovery_results = recovery_results
        state.current_phase = "recovery_complete"

        return state

    async def _validate_recovery_node(
        self,
        state: GhostbustersState,
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
        self,
        state: GhostbustersState,
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

        # Calculate confidence score based on results
        if state.delusions_detected:
            # Higher confidence if we found issues and have recovery actions
            base_confidence = 0.8
            if state.recovery_actions:
                base_confidence += 0.1
            if not state.errors:
                base_confidence += 0.1
            state.confidence_score = min(base_confidence, 1.0)
        else:
            # No issues found - high confidence
            state.confidence_score = 0.9

        state.metadata["report"] = report
        state.current_phase = "complete"

        return state

    def _calculate_confidence(self, validation_results: dict[str, Any]) -> float:
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
        """Run the complete Ghostbusters workflow"""

        # Initialize state
        state = GhostbustersState(
            project_path=str(self.project_path),
            delusions_detected=[],
            recovery_actions=[],
            confidence_score=0.0,
            validation_results={},
            recovery_results={},
            current_phase="detection",
            errors=[],
            warnings=[],
            metadata={},
        )

        try:
            # Phase 1: Detect delusions
            self.logger.info("Phase 1: Detecting delusions...")
            state = await self._detect_delusions(state)

            # Phase 2: Validate findings
            self.logger.info("Phase 2: Validating findings...")
            state = await self._validate_findings(state)

            # Phase 3: Plan recovery
            self.logger.info("Phase 3: Planning recovery...")
            state = await self._plan_recovery(state)

            # Phase 4: Execute recovery
            self.logger.info("Phase 4: Executing recovery...")
            state = await self._execute_recovery(state)

            # Phase 5: Validate recovery
            self.logger.info("Phase 5: Validating recovery...")
            state = await self._validate_recovery(state)

            # Phase 6: Generate report
            self.logger.info("Phase 6: Generating report...")
            state = await self._generate_report(state)

        except Exception as e:
            self.logger.error(f"Ghostbusters workflow failed: {e}")
            state.errors.append(str(e))
            state.confidence_score = 0.0

        return state

    async def _detect_delusions(self, state: GhostbustersState) -> GhostbustersState:
        """Detect delusions using all agents"""
        all_delusions = []

        # Limit number of files to prevent hanging
        max_files = 50
        file_count = 0

        for agent_name, agent in self.agents.items():
            try:
                if file_count >= max_files:
                    self.logger.warning(
                        f"Reached file limit of {max_files}, stopping detection"
                    )
                    break

                result = await agent.detect_delusions(self.project_path)
                all_delusions.extend(result.delusions)
                state.metadata[f"{agent_name}_confidence"] = result.confidence
                state.metadata[f"{agent_name}_recommendations"] = result.recommendations
                file_count += 1
            except Exception as e:
                self.logger.error(f"Agent {agent_name} failed: {e}")
                state.errors.append(f"Agent {agent_name} failed: {e}")

        state.delusions_detected = all_delusions
        state.current_phase = "validation"
        return state

    async def _validate_findings(self, state: GhostbustersState) -> GhostbustersState:
        """Validate findings using validators"""
        validation_results = {}

        for validator_name, validator in self.validators.items():
            try:
                result = await validator.validate_findings(state.delusions_detected)
                validation_results[validator_name] = result
            except Exception as e:
                self.logger.error(f"Validator {validator_name} failed: {e}")
                state.errors.append(f"Validator {validator_name} failed: {e}")

        state.validation_results = validation_results
        state.current_phase = "planning"
        return state

    async def _plan_recovery(self, state: GhostbustersState) -> GhostbustersState:
        """Plan recovery actions for detected delusions"""
        recovery_actions = []

        for delusion in state.delusions_detected:
            action = await self._plan_recovery_action(delusion)
            if action:
                recovery_actions.append(action)

        state.recovery_actions = recovery_actions
        state.current_phase = "execution"
        return state

    async def _execute_recovery(self, state: GhostbustersState) -> GhostbustersState:
        """Execute recovery actions"""
        recovery_results = {}

        # Limit recovery actions to prevent infinite loops
        max_recovery_actions = 10
        actions_to_execute = state.recovery_actions[:max_recovery_actions]

        for action in actions_to_execute:
            engine_name = action.get("engine")
            if engine_name in self.recovery_engines:
                try:
                    engine = self.recovery_engines[engine_name]
                    result = await engine.execute_recovery(action)
                    recovery_results[action.get("id", "unknown")] = result
                except Exception as e:
                    self.logger.error(f"Recovery engine {engine_name} failed: {e}")
                    state.errors.append(f"Recovery engine {engine_name} failed: {e}")

        if len(state.recovery_actions) > max_recovery_actions:
            self.logger.warning(
                f"Limited recovery actions to {max_recovery_actions} to prevent infinite loops"
            )

        state.recovery_results = recovery_results
        state.current_phase = "validation"
        return state

    async def _validate_recovery(self, state: GhostbustersState) -> GhostbustersState:
        """Validate recovery results"""
        # Re-run detection to see if issues were fixed
        post_recovery_state = await self._detect_delusions(state)
        remaining_delusions = len(post_recovery_state.delusions_detected)
        original_delusions = len(state.delusions_detected)

        if original_delusions > 0:
            success_rate = (
                original_delusions - remaining_delusions
            ) / original_delusions
        else:
            success_rate = 1.0

        state.metadata["recovery_success_rate"] = success_rate
        state.metadata["remaining_delusions"] = remaining_delusions
        state.current_phase = "reporting"
        return state

    async def _generate_report(self, state: GhostbustersState) -> GhostbustersState:
        """Generate final report and calculate confidence"""
        # Calculate confidence based on validation and recovery results
        confidence = self._calculate_confidence(state.validation_results)

        # Adjust confidence based on recovery success
        recovery_success_rate = state.metadata.get("recovery_success_rate", 0.0)
        confidence = (confidence + recovery_success_rate) / 2

        state.confidence_score = confidence
        state.current_phase = "complete"

        self.logger.info(f"Ghostbusters completed with confidence: {confidence}")
        return state

    async def _plan_recovery_action(
        self,
        delusion: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        """Plan a recovery action for a delusion"""
        delusion_type = delusion.get("type", "")

        # Map delusion types to recovery engines
        engine_mapping = {
            "syntax_error": "syntax",
            "indentation_error": "indentation",
            "import_error": "imports",
            "type_error": "types",
            "subprocess_vulnerability": "security",
        }

        engine_name = engine_mapping.get(delusion_type)
        if engine_name and engine_name in self.recovery_engines:
            return {
                "id": f"recovery_{len(self.recovery_actions) if hasattr(self, 'recovery_actions') else 0}",
                "engine": engine_name,
                "delusion": delusion,
                "priority": delusion.get("priority", "medium"),
            }

        return None


async def run_ghostbusters(project_path: str = ".") -> GhostbustersState:
    """Convenience function to run Ghostbusters"""
    orchestrator = GhostbustersOrchestrator(project_path)
    return await orchestrator.run_ghostbusters()


if __name__ == "__main__":

    async def main() -> None:
        state = await run_ghostbusters()
        print(f"Ghostbusters completed with confidence: {state.confidence_score}")

    asyncio.run(main())
