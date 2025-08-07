"""Architecture expert agent for detecting architectural issues."""

from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, DelusionResult


class ArchitectureExpert(BaseExpert):
    """Expert agent for detecting architectural issues."""

    def __init__(self):
        """Initialize the architecture expert."""
        super().__init__("ArchitectureExpert")

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect architectural issues in the project."""
        delusions = []
        recommendations = []

        # Check project structure
        structure_delusions = await self._check_project_structure(project_path)
        delusions.extend(structure_delusions)

        # Check for proper __init__.py files
        init_delusions = await self._check_init_files(project_path)
        delusions.extend(init_delusions)

        # Check for circular imports
        import_delusions = await self._check_imports(project_path)
        delusions.extend(import_delusions)

        # Generate recommendations
        if delusions:
            recommendations.append(
                self._create_recommendation(
                    "Improve project structure and organization",
                    "high",
                ),
            )
            recommendations.append(
                self._create_recommendation("Add missing __init__.py files", "medium"),
            )
        else:
            recommendations.append(
                self._create_recommendation("Architecture looks well-organized", "low"),
            )

        confidence = self._calculate_confidence(delusions)

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )

    async def _check_project_structure(
        self,
        project_path: Path,
    ) -> list[dict[str, Any]]:
        """Check project structure for issues."""
        delusions = []

        # Check for src directory
        src_dir = project_path / "src"
        if not src_dir.exists():
            delusions.append(
                self._create_delusion(
                    "missing_src_directory",
                    str(project_path),
                    1,
                    "Missing src/ directory for source code organization",
                    0.8,
                    "medium",
                ),
            )

        # Check for tests directory
        tests_dir = project_path / "tests"
        if not tests_dir.exists():
            delusions.append(
                self._create_delusion(
                    "missing_tests_directory",
                    str(project_path),
                    1,
                    "Missing tests/ directory for test organization",
                    0.75,
                    "medium",
                ),
            )

        return delusions

    async def _check_init_files(self, project_path: Path) -> list[dict[str, Any]]:
        """Check for missing __init__.py files."""
        delusions = []

        # Check src directory
        src_dir = project_path / "src"
        if src_dir.exists():
            for subdir in src_dir.iterdir():
                if subdir.is_dir() and not (subdir / "__init__.py").exists():
                    delusions.append(
                        self._create_delusion(
                            "missing_init_file",
                            str(subdir / "__init__.py"),
                            1,
                            f"Missing __init__.py in {subdir.name}/",
                            0.7,
                            "low",
                        ),
                    )

        return delusions

    async def _check_imports(self, project_path: Path) -> list[dict[str, Any]]:
        """Check for potential import issues."""
        delusions = []

        # This is a simplified check - in a real implementation,
        # you would analyze import statements for circular dependencies
        python_files = list(project_path.rglob("*.py"))

        if len(python_files) > 10:
            # Large projects might have import issues
            delusions.append(
                self._create_delusion(
                    "potential_import_issues",
                    str(project_path),
                    1,
                    "Large project detected - consider checking for circular imports",
                    0.6,
                    "low",
                ),
            )

        return delusions
