"""Build expert agent for detecting build configuration issues."""

from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, DelusionResult


class BuildExpert(BaseExpert):
    """Expert agent for detecting build configuration issues."""

    def __init__(self):
        """Initialize the build expert."""
        super().__init__("BuildExpert")

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect build configuration issues in the project."""
        delusions = []
        recommendations = []

        # Check for essential build files
        required_files = [
            "pyproject.toml",
            "requirements.txt",
            "setup.py",
            "Makefile",
        ]

        for required_file in required_files:
            if not (project_path / required_file).exists():
                delusions.append(
                    self._create_delusion(
                        "missing_build_file",
                        str(project_path / required_file),
                        1,
                        f"Missing build configuration file: {required_file}",
                        0.8,
                        "medium",
                    ),
                )

        # Check pyproject.toml if it exists
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            pyproject_delusions = await self._scan_pyproject(pyproject_path)
            delusions.extend(pyproject_delusions)

        # Generate recommendations
        if delusions:
            recommendations.append(
                self._create_recommendation(
                    "Add missing build configuration files",
                    "high",
                ),
            )
            recommendations.append(
                self._create_recommendation(
                    "Configure proper dependency management",
                    "medium",
                ),
            )
        else:
            recommendations.append(
                self._create_recommendation("Build configuration looks good", "low"),
            )

        confidence = self._calculate_confidence(delusions)

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )

    async def _scan_pyproject(self, file_path: Path) -> list[dict[str, Any]]:
        """Scan pyproject.toml for issues."""
        delusions = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Check for basic project configuration
            has_project_section = False
            has_dependencies = False

            for line in lines:
                if line.strip() == "[project]":
                    has_project_section = True
                elif "dependencies" in line and "=" in line:
                    has_dependencies = True

            if not has_project_section:
                delusions.append(
                    self._create_delusion(
                        "missing_project_section",
                        str(file_path),
                        1,
                        "Missing [project] section in pyproject.toml",
                        0.85,
                        "medium",
                    ),
                )

            if not has_dependencies:
                delusions.append(
                    self._create_delusion(
                        "missing_dependencies",
                        str(file_path),
                        1,
                        "No dependencies specified in pyproject.toml",
                        0.75,
                        "low",
                    ),
                )

        except Exception:
            # Skip files that can't be read
            pass

        return delusions
