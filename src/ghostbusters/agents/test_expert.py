"""Test expert agent for detecting test-related issues."""

from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, DelusionResult


class TestExpert(BaseExpert):
    """Expert agent for detecting test-related issues."""

    def __init__(self) -> None:
        """Initialize the test expert."""
        super().__init__("TestExpert")

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect test-related issues in the project."""
        delusions = []
        recommendations = []

        # Check for test files
        test_files = list(project_path.rglob("test_*.py"))
        test_dirs = [
            d for d in project_path.iterdir() if d.is_dir() and "test" in d.name.lower()
        ]

        # Check if tests exist
        if not test_files and not test_dirs:
            delusions.append(
                self._create_delusion(
                    "no_tests_found",
                    str(project_path),
                    1,
                    "No test files found in project",
                    0.9,
                    "high",
                ),
            )

        # Check test coverage
        for test_file in test_files:
            try:
                file_delusions = await self._scan_test_file(test_file)
                delusions.extend(file_delusions)
            except Exception:
                continue

        # Generate recommendations
        if delusions:
            recommendations.append(
                self._create_recommendation("Add comprehensive test coverage", "high"),
            )
            recommendations.append(
                self._create_recommendation(
                    "Implement unit tests for all modules",
                    "medium",
                ),
            )
        else:
            recommendations.append(
                self._create_recommendation("Test coverage looks good", "low"),
            )

        confidence = self._calculate_confidence(delusions)

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )

    async def _scan_test_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Scan a single test file for issues."""
        delusions = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Check for empty test files
            if not content.strip():
                delusions.append(
                    self._create_delusion(
                        "empty_test_file",
                        str(file_path),
                        1,
                        "Test file is empty",
                        0.8,
                        "medium",
                    ),
                )

            # Check for test functions
            has_test_functions = False
            for line in lines:
                if line.strip().startswith("def test_"):
                    has_test_functions = True
                    break

            if not has_test_functions:
                delusions.append(
                    self._create_delusion(
                        "no_test_functions",
                        str(file_path),
                        1,
                        "No test functions found in test file",
                        0.85,
                        "medium",
                    ),
                )

        except Exception:
            # Skip files that can't be read
            pass

        return delusions
