#!/usr/bin/env python3
"""
Artifact Requirement Mapper - Maps individual AST models to specific requirements
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class ArtifactRequirementMapping:
    """Mapping between individual artifacts and requirements"""

    artifact_path: str
    artifact_type: str
    requirement_id: str
    requirement_domain: str
    requirement_description: str
    implementation_files: list[str]
    test_files: list[str]
    ast_model: dict[str, Any]
    complexity_score: float
    coverage_score: float
    compliance_score: float
    last_updated: str


class ArtifactRequirementMapper:
    """Map individual AST models to specific requirements"""

    def __init__(self) -> None:
        self.project_model = self._load_project_model()
        self.ast_models = self._load_ast_models()
        self.test_requirements = self._load_test_requirements()

    def _load_project_model(self) -> dict[str, Any]:
        """Load project model registry"""
        try:
            with open("project_model_registry.json") as f:
                return json.load(f)  # type: ignore
        except Exception as e:
            print(f"Error loading project model: {e}")
            return {}

    def _load_ast_models(self) -> dict[str, Any]:
        """Load AST models"""
        try:
            with open("ast_models_focused.json") as f:
                return json.load(f)  # type: ignore
        except Exception as e:
            print(f"Error loading AST models: {e}")
            return {}

    def _load_test_requirements(self) -> dict[str, Any]:
        """Load test-driven requirements"""
        try:
            with open("test_driven_ast_models.json") as f:
                return json.load(f)  # type: ignore
        except Exception as e:
            print(f"Error loading test requirements: {e}")
            return {}

    def map_artifact_to_requirements(
        self,
        artifact_path: str,
    ) -> list[ArtifactRequirementMapping]:
        """Map a specific artifact to its requirements"""
        mappings = []  # type: ignore

        # Get artifact AST model
        artifact_model = self.ast_models.get("file_models", {}).get(artifact_path)
        if not artifact_model:
            return mappings

        # Get requirements for this artifact's domain
        domain = self._determine_artifact_domain(artifact_path, artifact_model)
        requirements = self._get_requirements_for_domain(domain)

        for req in requirements:
            mapping = self._create_artifact_requirement_mapping(
                artifact_path,
                artifact_model,
                req,
            )
            if mapping:
                mappings.append(mapping)

        return mappings

    def _determine_artifact_domain(
        self,
        artifact_path: str,
        artifact_model: dict[str, Any],
    ) -> str:
        """Determine which domain an artifact belongs to"""
        path = Path(artifact_path)

        # Check patterns for each domain
        for domain_name, domain_config in self.project_model.get("domains", {}).items():
            patterns = domain_config.get("patterns", [])
            for pattern in patterns:
                if self._path_matches_pattern(path, pattern):
                    return domain_name  # type: ignore

        # Check content indicators
        content = artifact_model.get("model_data", {})
        for domain_name, domain_config in self.project_model.get("domains", {}).items():
            indicators = domain_config.get("content_indicators", [])
            for indicator in indicators:
                if self._content_contains_indicator(content, indicator):
                    return domain_name  # type: ignore

        return "unknown"

    def _path_matches_pattern(self, path: Path, pattern: str) -> bool:
        """Check if path matches pattern"""
        # Simple pattern matching - in practice you'd use fnmatch
        return pattern in str(path) or path.match(pattern)

    def _content_contains_indicator(
        self,
        content: dict[str, Any],
        indicator: str,
    ) -> bool:
        """Check if content contains indicator"""
        # Check in docstrings, imports, function names, etc.
        docstrings = content.get("docstrings", [])
        imports = content.get("imports", [])
        functions = content.get("functions", [])

        for docstring in docstrings:
            if indicator.lower() in docstring.lower():
                return True

        for import_item in imports:
            if indicator.lower() in str(import_item).lower():
                return True

        for func in functions:
            if indicator.lower() in func.get("name", "").lower():
                return True

        return False

    def _get_requirements_for_domain(self, domain: str) -> list[dict[str, Any]]:
        """Get requirements for a specific domain"""
        requirements = self.project_model.get("requirements_traceability", [])
        return [req for req in requirements if req.get("domain") == domain]

    def _create_artifact_requirement_mapping(
        self,
        artifact_path: str,
        artifact_model: dict[str, Any],
        requirement: dict[str, Any],
    ) -> Optional[ArtifactRequirementMapping]:
        """Create mapping between artifact and requirement"""

        # Calculate scores
        complexity_score = artifact_model.get("complexity_score", 0)
        coverage_score = self._calculate_coverage_score(artifact_path, requirement)
        compliance_score = self._calculate_compliance_score(artifact_path, requirement)

        # Get implementation and test files
        implementation_files = self._get_implementation_files(requirement)
        test_files = self._get_test_files(requirement)

        return ArtifactRequirementMapping(
            artifact_path=artifact_path,
            artifact_type=artifact_model.get("file_type", "unknown"),
            requirement_id=requirement.get("requirement", ""),
            requirement_domain=requirement.get("domain", ""),
            requirement_description=requirement.get("implementation", ""),
            implementation_files=implementation_files,
            test_files=test_files,
            ast_model=artifact_model,
            complexity_score=complexity_score,
            coverage_score=coverage_score,
            compliance_score=compliance_score,
            last_updated=datetime.now().isoformat(),
        )

    def _calculate_coverage_score(
        self,
        artifact_path: str,
        requirement: dict[str, Any],
    ) -> float:
        """Calculate how well the artifact covers the requirement"""
        # This would analyze the AST model to see how well it implements the requirement
        # For now, return a simple score based on complexity and line count
        return 0.8  # Placeholder

    def _calculate_compliance_score(
        self,
        artifact_path: str,
        requirement: dict[str, Any],
    ) -> float:
        """Calculate compliance score for the requirement"""
        # This would check if the artifact follows the requirement's guidelines
        # For now, return a simple score
        return 0.9  # Placeholder

    def _get_implementation_files(self, requirement: dict[str, Any]) -> list[str]:
        """Get implementation files for a requirement"""
        implementation = requirement.get("implementation", "")
        # Extract file patterns from implementation description
        # This is a simplified version
        return [implementation]

    def _get_test_files(self, requirement: dict[str, Any]) -> list[str]:
        """Get test files for a requirement"""
        test_file = requirement.get("test", "")
        if test_file:
            return [test_file]
        return []

    def generate_artifact_requirement_report(self) -> dict[str, Any]:
        """Generate comprehensive report of artifact-requirement mappings"""
        print("🔍 Generating Artifact-Requirement Mapping Report...")

        all_mappings = []
        coverage_stats = {}

        # Process all artifacts
        for artifact_path, artifact_model in self.ast_models.get(
            "file_models",
            {},
        ).items():
            mappings = self.map_artifact_to_requirements(artifact_path)
            all_mappings.extend(mappings)

            # Update coverage stats
            for mapping in mappings:
                domain = mapping.requirement_domain
                if domain not in coverage_stats:
                    coverage_stats[domain] = {
                        "total_artifacts": 0,
                        "total_requirements": 0,
                        "avg_complexity": 0,
                        "avg_coverage": 0,
                        "avg_compliance": 0,
                    }

                coverage_stats[domain]["total_artifacts"] += 1
                coverage_stats[domain]["avg_complexity"] += mapping.complexity_score  # type: ignore
                coverage_stats[domain]["avg_coverage"] += mapping.coverage_score  # type: ignore
                coverage_stats[domain]["avg_compliance"] += mapping.compliance_score  # type: ignore

        # Calculate averages
        for domain, stats in coverage_stats.items():
            if stats["total_artifacts"] > 0:
                stats["avg_complexity"] /= stats["total_artifacts"]  # type: ignore
                stats["avg_coverage"] /= stats["total_artifacts"]  # type: ignore
                stats["avg_compliance"] /= stats["total_artifacts"]  # type: ignore

        return {
            "total_mappings": len(all_mappings),
            "total_artifacts": len(self.ast_models.get("file_models", {})),
            "coverage_stats": coverage_stats,
            "mappings": [asdict(mapping) for mapping in all_mappings],
        }

    def find_requirements_for_artifact(
        self,
        artifact_path: str,
    ) -> list[dict[str, Any]]:
        """Find all requirements that apply to a specific artifact"""
        mappings = self.map_artifact_to_requirements(artifact_path)
        return [asdict(mapping) for mapping in mappings]

    def find_artifacts_for_requirement(
        self,
        requirement_id: str,
    ) -> list[dict[str, Any]]:
        """Find all artifacts that implement a specific requirement"""
        artifacts = []

        for artifact_path, artifact_model in self.ast_models.get(
            "file_models",
            {},
        ).items():
            mappings = self.map_artifact_to_requirements(artifact_path)
            for mapping in mappings:
                if requirement_id in mapping.requirement_id:
                    artifacts.append(
                        {
                            "artifact_path": artifact_path,
                            "artifact_model": artifact_model,
                            "mapping": asdict(mapping),
                        },
                    )

        return artifacts


def main() -> None:
    """Main function for testing"""
    mapper = ArtifactRequirementMapper()

    # Generate comprehensive report
    report = mapper.generate_artifact_requirement_report()

    # Save report
    with open("artifact_requirement_mappings.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print("✅ Generated artifact-requirement mapping report:")
    print(f"   - Total mappings: {report['total_mappings']}")
    print(f"   - Total artifacts: {report['total_artifacts']}")
    print(f"   - Domains covered: {len(report['coverage_stats'])}")

    # Example: Find requirements for a specific artifact
    example_artifact = ".cursor/plugins/rule-compliance-checker.py"
    requirements = mapper.find_requirements_for_artifact(example_artifact)
    print(f"\n📋 Requirements for {example_artifact}:")
    for req in requirements:
        print(f"   - {req['requirement_id']} ({req['requirement_domain']})")


if __name__ == "__main__":
    main()
