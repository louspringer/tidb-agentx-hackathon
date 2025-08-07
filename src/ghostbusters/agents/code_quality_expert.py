"""Code quality expert agent for detecting code quality issues."""

import ast
from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, DelusionResult


class CodeQualityExpert(BaseExpert):
    """Expert agent for detecting code quality issues."""

    def __init__(self):
        """Initialize the code quality expert."""
        super().__init__("CodeQualityExpert")

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect code quality issues in the project."""
        delusions = []
        recommendations = []

        # Scan Python files for code quality issues
        for py_file in project_path.rglob("*.py"):
            if py_file.is_file():
                try:
                    file_delusions = await self._scan_file(py_file)
                    delusions.extend(file_delusions)
                except Exception:
                    # Skip files that can't be parsed
                    continue

        # Generate recommendations
        if delusions:
            recommendations.append(
                self._create_recommendation(
                    "Fix syntax errors and improve code quality",
                    "high",
                ),
            )
            recommendations.append(
                self._create_recommendation("Add type hints and docstrings", "medium"),
            )
        else:
            recommendations.append(
                self._create_recommendation("No code quality issues detected", "low"),
            )

        confidence = self._calculate_confidence(delusions)

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )

    async def _scan_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Scan a single file for code quality issues."""
        delusions = []

        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for syntax errors
            try:
                ast.parse(content)
            except SyntaxError as e:
                delusions.append(
                    self._create_delusion(
                        "syntax_error",
                        str(file_path),
                        e.lineno or 1,
                        f"Syntax error: {e.msg}",
                        0.95,
                        "high",
                    ),
                )

            # Check for indentation issues
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                if line.strip() and not line.startswith((" ", "\t")) and line_num > 1:
                    # Check if this line should be indented
                    prev_line = lines[line_num - 2] if line_num > 1 else ""
                    if prev_line.strip().endswith(":"):
                        delusions.append(
                            self._create_delusion(
                                "indentation_error",
                                str(file_path),
                                line_num,
                                f"Missing indentation after colon: {line.strip()}",
                                0.85,
                                "medium",
                            ),
                        )

            # Check for missing type hints
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.returns and not node.name.startswith("_"):
                        delusions.append(
                            self._create_delusion(
                                "missing_type_hint",
                                str(file_path),
                                node.lineno,
                                f"Function '{node.name}' missing return type hint",
                                0.75,
                                "low",
                            ),
                        )

        except Exception:
            # Skip files that can't be read
            pass

        return delusions
