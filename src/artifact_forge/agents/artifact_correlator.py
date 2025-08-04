#!/usr/bin/env python3
"""
ArtifactCorrelator Agent
Finds relationships between artifacts
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ArtifactRelationship:
    """Relationship between artifacts"""

    source_artifact: str
    target_artifact: str
    relationship_type: str  # 'imports', 'references', 'depends_on', 'similar', etc.
    confidence: float  # 0.0 to 1.0
    evidence: List[str]
    created_at: datetime


class ArtifactCorrelator:
    """Finds relationships between artifacts"""

    def __init__(self):
        self.relationship_types = {
            "imports": self._find_import_relationships,
            "references": self._find_reference_relationships,
            "depends_on": self._find_dependency_relationships,
            "similar": self._find_similarity_relationships,
            "configures": self._find_configuration_relationships,
        }
        self.max_artifacts = 50  # Limit for performance
        self.max_relationships = 100  # Limit total relationships

    def correlate_artifacts(
        self, artifacts: List[Dict[str, Any]]
    ) -> List[ArtifactRelationship]:
        """Find relationships between artifacts"""
        logger.info(f"Starting correlation of {len(artifacts)} artifacts")

        # Limit artifacts for performance
        if len(artifacts) > self.max_artifacts:
            logger.warning(
                f"Limiting artifacts from {len(artifacts)} to {self.max_artifacts} for performance"
            )
            artifacts = artifacts[: self.max_artifacts]

        relationships = []
        total_comparisons = len(artifacts) * (len(artifacts) - 1) // 2
        comparison_count = 0

        logger.info(f"Will perform {total_comparisons} comparisons")

        for i, artifact1 in enumerate(artifacts):
            for j, artifact2 in enumerate(artifacts):
                if i != j:
                    comparison_count += 1

                    # Log progress every 100 comparisons
                    if comparison_count % 100 == 0:
                        logger.info(
                            f"Progress: {comparison_count}/{total_comparisons} comparisons"
                        )

                    # Find all types of relationships
                    for rel_type, finder_func in self.relationship_types.items():
                        try:
                            rels = finder_func(artifact1, artifact2)
                            relationships.extend(rels)

                            # Limit total relationships
                            if len(relationships) >= self.max_relationships:
                                logger.warning(
                                    f"Reached maximum relationships limit ({self.max_relationships})"
                                )
                                return relationships

                        except Exception as e:
                            logger.error(f"Error in {rel_type} relationship: {e}")
                            continue

        logger.info(f"Completed correlation: {len(relationships)} relationships found")
        return relationships

    def _find_import_relationships(
        self, artifact1: Dict[str, Any], artifact2: Dict[str, Any]
    ) -> List[ArtifactRelationship]:
        """Find import relationships between artifacts"""
        relationships = []

        # Check if artifact1 imports artifact2
        if (
            artifact1.get("artifact_type") == "python"
            and artifact2.get("artifact_type") == "python"
        ):
            imports = artifact1.get("parsed_data", {}).get("imports", [])
            target_name = Path(artifact2["path"]).stem

            for import_stmt in imports:
                if target_name in import_stmt:
                    relationships.append(
                        ArtifactRelationship(
                            source_artifact=artifact1["path"],
                            target_artifact=artifact2["path"],
                            relationship_type="imports",
                            confidence=0.9,
                            evidence=[f"Import statement: {import_stmt}"],
                            created_at=datetime.now(),
                        )
                    )

        return relationships

    def _find_reference_relationships(
        self, artifact1: Dict[str, Any], artifact2: Dict[str, Any]
    ) -> List[ArtifactRelationship]:
        """Find reference relationships between artifacts"""
        relationships = []

        # Check if artifact1 references artifact2 in content
        try:
            content1 = self._get_artifact_content(artifact1)
            target_name = Path(artifact2["path"]).name

            if target_name in content1:
                relationships.append(
                    ArtifactRelationship(
                        source_artifact=artifact1["path"],
                        target_artifact=artifact2["path"],
                        relationship_type="references",
                        confidence=0.7,
                        evidence=[f"References file: {target_name}"],
                        created_at=datetime.now(),
                    )
                )
        except Exception as e:
            logger.debug(f"Error reading content for {artifact1['path']}: {e}")

        return relationships

    def _find_dependency_relationships(
        self, artifact1: Dict[str, Any], artifact2: Dict[str, Any]
    ) -> List[ArtifactRelationship]:
        """Find dependency relationships between artifacts"""
        relationships = []

        # Check for configuration dependencies
        if (
            artifact1.get("artifact_type") in ["yaml", "json"]
            and artifact2.get("artifact_type") == "python"
        ):
            # Configuration files often configure Python modules
            relationships.append(
                ArtifactRelationship(
                    source_artifact=artifact1["path"],
                    target_artifact=artifact2["path"],
                    relationship_type="configures",
                    confidence=0.6,
                    evidence=["Configuration file likely configures Python module"],
                    created_at=datetime.now(),
                )
            )

        return relationships

    def _find_similarity_relationships(
        self, artifact1: Dict[str, Any], artifact2: Dict[str, Any]
    ) -> List[ArtifactRelationship]:
        """Find similarity relationships between artifacts"""
        relationships = []

        # Check for similar structure or patterns
        if artifact1.get("artifact_type") == artifact2.get("artifact_type"):
            similarity_score = self._calculate_similarity(artifact1, artifact2)

            if similarity_score > 0.8:
                relationships.append(
                    ArtifactRelationship(
                        source_artifact=artifact1["path"],
                        target_artifact=artifact2["path"],
                        relationship_type="similar",
                        confidence=similarity_score,
                        evidence=[f"Similar structure (score: {similarity_score:.2f})"],
                        created_at=datetime.now(),
                    )
                )

        return relationships

    def _find_configuration_relationships(
        self, artifact1: Dict[str, Any], artifact2: Dict[str, Any]
    ) -> List[ArtifactRelationship]:
        """Find configuration relationships between artifacts"""
        relationships = []

        # Check if one artifact configures another
        if artifact1.get("artifact_type") in ["yaml", "json"] and artifact2.get(
            "artifact_type"
        ) in ["python", "mdc"]:
            try:
                config_content = self._get_artifact_content(artifact1)
                target_name = Path(artifact2["path"]).stem

                if target_name.lower() in config_content.lower():
                    relationships.append(
                        ArtifactRelationship(
                            source_artifact=artifact1["path"],
                            target_artifact=artifact2["path"],
                            relationship_type="configures",
                            confidence=0.8,
                            evidence=[
                                f"Configuration file contains target name: {target_name}"
                            ],
                            created_at=datetime.now(),
                        )
                    )
            except Exception as e:
                logger.debug(
                    f"Error reading config content for {artifact1['path']}: {e}"
                )

        return relationships

    def _get_artifact_content(self, artifact: Dict[str, Any]) -> str:
        """Get content of an artifact"""
        try:
            with open(artifact["path"], "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.debug(f"Error reading {artifact['path']}: {e}")
            return ""

    def _calculate_similarity(
        self, artifact1: Dict[str, Any], artifact2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between artifacts"""
        # Simple similarity based on structure
        data1 = artifact1.get("parsed_data", {})
        data2 = artifact2.get("parsed_data", {})

        # Compare basic metrics
        lines1 = data1.get("line_count", 0)
        lines2 = data2.get("line_count", 0)

        if lines1 == 0 or lines2 == 0:
            return 0.0

        # Calculate similarity based on line count ratio
        ratio = min(lines1, lines2) / max(lines1, lines2)

        # Additional similarity factors
        if (
            artifact1.get("artifact_type") == "python"
            and artifact2.get("artifact_type") == "python"
        ):
            funcs1 = len(data1.get("functions", []))
            funcs2 = len(data2.get("functions", []))
            if funcs1 > 0 and funcs2 > 0:
                func_ratio = min(funcs1, funcs2) / max(funcs1, funcs2)
                ratio = (ratio + func_ratio) / 2

        return ratio


def main():
    """Test ArtifactCorrelator"""
    logger.info("Starting ArtifactCorrelator test")

    correlator = ArtifactCorrelator()

    # Create sample artifacts for testing
    sample_artifacts = [
        {
            "path": "comprehensive_ast_modeler.py",
            "artifact_type": "python",
            "parsed_data": {
                "imports": ["import ast", "import json"],
                "functions": [{"name": "test_func", "line_number": 10}],
                "line_count": 100,
            },
        },
        {
            "path": "ast_data_validator.py",
            "artifact_type": "python",
            "parsed_data": {
                "imports": ["import json", "import ast"],
                "functions": [{"name": "validate", "line_number": 5}],
                "line_count": 80,
            },
        },
    ]

    logger.info("Running correlation on sample artifacts")
    relationships = correlator.correlate_artifacts(sample_artifacts)

    print(f"🔍 **ARTIFACT CORRELATION RESULTS:**")
    print(f"Total relationships found: {len(relationships)}")

    for rel in relationships:
        print(
            f"  {rel.source_artifact} -> {rel.target_artifact} ({rel.relationship_type}, confidence: {rel.confidence:.2f})"
        )


if __name__ == "__main__":
    main()
