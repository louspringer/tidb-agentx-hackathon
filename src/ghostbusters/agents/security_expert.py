"""Security expert agent for detecting security vulnerabilities."""

import re
from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, DelusionResult


class SecurityExpert(BaseExpert):
    """Expert agent for detecting security vulnerabilities."""

    def __init__(self) -> None:
        """Initialize the security expert."""
        super().__init__("SecurityExpert")

        # Patterns for detecting security issues
        self.credential_patterns = [
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]",
            r"key\s*=\s*['\"][^'\"]+['\"]",
        ]

        self.subprocess_patterns = [
            r"subprocess\.call\(",
            r"subprocess\.run\(",
            r"os\.system\(",
            r"eval\(",
            r"exec\(",
        ]

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect security vulnerabilities in the project."""
        delusions = []
        recommendations = []

        # Scan Python files for security issues
        for py_file in project_path.rglob("*.py"):
            if py_file.is_file():
                try:
                    file_delusions = await self._scan_file(py_file)
                    delusions.extend(file_delusions)
                except Exception:
                    # Log error but continue scanning
                    continue

        # Generate recommendations
        if delusions:
            recommendations.append(
                self._create_recommendation(
                    "Remove hardcoded credentials and use environment variables",
                    "high",
                ),
            )
            recommendations.append(
                self._create_recommendation(
                    "Replace subprocess calls with secure alternatives",
                    "medium",
                ),
            )
        else:
            recommendations.append(
                self._create_recommendation(
                    "No security vulnerabilities detected",
                    "low",
                ),
            )

        confidence = self._calculate_confidence(delusions)

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )

    async def _scan_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Scan a single file for security issues."""
        delusions = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                # Check for hardcoded credentials
                for pattern in self.credential_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        delusions.append(
                            self._create_delusion(
                                "hardcoded_credential",
                                str(file_path),
                                line_num,
                                f"Hardcoded credential detected: {line.strip()}",
                                0.95,
                                "high",
                            ),
                        )

                # Check for dangerous subprocess calls
                for pattern in self.subprocess_patterns:
                    if re.search(pattern, line):
                        delusions.append(
                            self._create_delusion(
                                "subprocess_vulnerability",
                                str(file_path),
                                line_num,
                                f"Potentially dangerous subprocess call: {line.strip()}",
                                0.85,
                                "medium",
                            ),
                        )

        except Exception:
            # Skip files that can't be read
            pass

        return delusions
