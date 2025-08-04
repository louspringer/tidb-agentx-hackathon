#!/usr/bin/env python3
"""
ArtifactForge Basic Workflow
LangGraph workflow for artifact processing
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Import our agents
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.artifact_forge.agents.artifact_detector import ArtifactDetector
from src.artifact_forge.agents.artifact_parser import ArtifactParser
from src.artifact_forge.agents.artifact_correlator import ArtifactCorrelator


@dataclass
class ArtifactForgeState:
    """State for ArtifactForge workflow"""

    artifacts_discovered: List[Dict[str, Any]]
    artifacts_parsed: List[Dict[str, Any]]
    relationships_found: List[Dict[str, Any]]
    errors: List[str]
    processing_time: float
    confidence_score: float


class ArtifactForgeWorkflow:
    """Basic ArtifactForge workflow"""

    def __init__(self):
        self.detector = ArtifactDetector()
        self.parser = ArtifactParser()
        self.correlator = ArtifactCorrelator()

    def run_workflow(self, root_path: str) -> ArtifactForgeState:
        """Run the complete ArtifactForge workflow"""
        start_time = datetime.now()
        state = ArtifactForgeState([], [], [], [], 0.0, 0.0)

        try:
            # Step 1: Detect artifacts
            print("🔍 **STEP 1: DETECTING ARTIFACTS**")
            artifacts = self.detector.detect_artifacts(root_path)
            state.artifacts_discovered = [self._artifact_to_dict(a) for a in artifacts]
            print(f"  Found {len(artifacts)} artifacts")

            # Step 2: Parse artifacts
            print("📝 **STEP 2: PARSING ARTIFACTS**")
            parsed_artifacts = []
            for artifact in artifacts:
                parsed = self.parser.parse_artifact(
                    artifact.path, artifact.artifact_type
                )
                parsed_dict = self._parsed_artifact_to_dict(parsed)
                parsed_artifacts.append(parsed_dict)

                if parsed.parsing_errors:
                    state.errors.extend(parsed.parsing_errors)

            state.artifacts_parsed = parsed_artifacts
            print(f"  Parsed {len(parsed_artifacts)} artifacts")

            # Step 3: Correlate artifacts
            print("🔗 **STEP 3: CORRELATING ARTIFACTS**")
            relationships = self.correlator.correlate_artifacts(parsed_artifacts)
            state.relationships_found = [
                self._relationship_to_dict(r) for r in relationships
            ]
            print(f"  Found {len(relationships)} relationships")

            # Calculate processing time and confidence
            end_time = datetime.now()
            state.processing_time = (end_time - start_time).total_seconds()
            state.confidence_score = self._calculate_confidence(state)

            print(f"✅ **WORKFLOW COMPLETED**")
            print(f"  Processing time: {state.processing_time:.2f} seconds")
            print(f"  Confidence score: {state.confidence_score:.2f}")

        except Exception as e:
            state.errors.append(f"Workflow failed: {str(e)}")
            print(f"❌ **WORKFLOW FAILED**: {str(e)}")

        return state

    def _artifact_to_dict(self, artifact) -> Dict[str, Any]:
        """Convert ArtifactInfo to dictionary"""
        return {
            "path": artifact.path,
            "artifact_type": artifact.artifact_type,
            "size": artifact.size,
            "complexity_score": artifact.complexity_score,
            "last_modified": (
                artifact.last_modified.isoformat() if artifact.last_modified else None
            ),
            "metadata": artifact.metadata,
        }

    def _parsed_artifact_to_dict(self, parsed_artifact) -> Dict[str, Any]:
        """Convert ParsedArtifact to dictionary"""
        return {
            "path": parsed_artifact.path,
            "artifact_type": parsed_artifact.artifact_type,
            "parsed_data": parsed_artifact.parsed_data,
            "parsing_errors": parsed_artifact.parsing_errors,
            "parsing_timestamp": parsed_artifact.parsing_timestamp.isoformat(),
        }

    def _relationship_to_dict(self, relationship) -> Dict[str, Any]:
        """Convert ArtifactRelationship to dictionary"""
        return {
            "source_artifact": relationship.source_artifact,
            "target_artifact": relationship.target_artifact,
            "relationship_type": relationship.relationship_type,
            "confidence": relationship.confidence,
            "evidence": relationship.evidence,
            "created_at": relationship.created_at.isoformat(),
        }

    def _calculate_confidence(self, state: ArtifactForgeState) -> float:
        """Calculate overall confidence score"""
        if not state.artifacts_discovered:
            return 0.0

        # Base confidence on successful processing
        total_artifacts = len(state.artifacts_discovered)
        parsed_artifacts = len(state.artifacts_parsed)
        error_count = len(state.errors)

        # Calculate confidence based on success rate
        success_rate = (
            parsed_artifacts / total_artifacts if total_artifacts > 0 else 0.0
        )
        error_penalty = (
            min(error_count / total_artifacts, 1.0) if total_artifacts > 0 else 1.0
        )

        confidence = success_rate * (1.0 - error_penalty)
        return max(0.0, min(1.0, confidence))


def main():
    """Test ArtifactForge workflow"""
    workflow = ArtifactForgeWorkflow()

    print("🚀 **ARTIFACTFORGE WORKFLOW TEST**")
    print("=" * 50)

    # Run workflow on current directory
    state = workflow.run_workflow(".")

    # Print summary
    print(f"\n📊 **WORKFLOW SUMMARY:**")
    print(f"Artifacts discovered: {len(state.artifacts_discovered)}")
    print(f"Artifacts parsed: {len(state.artifacts_parsed)}")
    print(f"Relationships found: {len(state.relationships_found)}")
    print(f"Errors: {len(state.errors)}")
    print(f"Processing time: {state.processing_time:.2f} seconds")
    print(f"Confidence score: {state.confidence_score:.2f}")

    if state.errors:
        print(f"\n❌ **ERRORS:**")
        for error in state.errors:
            print(f"  - {error}")


if __name__ == "__main__":
    main()
