"""Model expert agent for detecting model-related issues."""

from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, DelusionResult


class ModelExpert(BaseExpert):
    """Expert agent for detecting model-related issues."""

    def __init__(self) -> None:
        """Initialize the model expert."""
        super().__init__("ModelExpert")

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect model-related issues in the project."""
        delusions = []
        recommendations = []

        # Check for model registry
        registry_delusions = await self._check_model_registry(project_path)
        delusions.extend(registry_delusions)

        # Check for domain models
        domain_delusions = await self._check_domain_models(project_path)
        delusions.extend(domain_delusions)

        # Check for data validation
        validation_delusions = await self._check_data_validation(project_path)
        delusions.extend(validation_delusions)

        # Generate recommendations
        if delusions:
            recommendations.append(
                self._create_recommendation("Implement proper domain modeling", "high"),
            )
            recommendations.append(
                self._create_recommendation(
                    "Add data validation and schemas",
                    "medium",
                ),
            )
        else:
            recommendations.append(
                self._create_recommendation("Model architecture looks good", "low"),
            )

        confidence = self._calculate_confidence(delusions)

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )

    async def _check_model_registry(self, project_path: Path) -> list[dict[str, Any]]:
        """Check for model registry configuration."""
        delusions = []

        # Check for project_model_registry.json
        registry_file = project_path / "project_model_registry.json"
        if not registry_file.exists():
            delusions.append(
                self._create_delusion(
                    "missing_model_registry",
                    str(registry_file),
                    1,
                    "Missing project_model_registry.json for model-driven development",
                    0.85,
                    "medium",
                ),
            )

        return delusions

    async def _check_domain_models(self, project_path: Path) -> list[dict[str, Any]]:
        """Check for domain model implementation."""
        delusions = []

        # Look for domain model files
        domain_files = list(project_path.rglob("*domain*.py"))
        domain_files.extend(list(project_path.rglob("*model*.py")))

        if not domain_files:
            delusions.append(
                self._create_delusion(
                    "no_domain_models",
                    str(project_path),
                    1,
                    "No domain model files found",
                    0.75,
                    "medium",
                ),
            )

        return delusions

    async def _check_data_validation(self, project_path: Path) -> list[dict[str, Any]]:
        """Check for data validation implementation."""
        delusions = []

        # Look for validation files
        validation_files = list(project_path.rglob("*validation*.py"))
        validation_files.extend(list(project_path.rglob("*schema*.py")))

        if not validation_files:
            delusions.append(
                self._create_delusion(
                    "no_data_validation",
                    str(project_path),
                    1,
                    "No data validation or schema files found",
                    0.7,
                    "low",
                ),
            )

        return delusions
