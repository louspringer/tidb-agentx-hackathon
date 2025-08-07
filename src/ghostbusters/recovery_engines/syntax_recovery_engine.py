"""Syntax recovery engine for fixing syntax errors."""

import ast
from pathlib import Path
from typing import Any

from .base_recovery_engine import BaseRecoveryEngine, RecoveryResult


class SyntaxRecoveryEngine(BaseRecoveryEngine):
    """Recovery engine for fixing syntax errors."""

    def __init__(self):
        """Initialize the syntax recovery engine."""
        super().__init__("SyntaxRecoveryEngine")

    async def execute_recovery(self, action: dict[str, Any]) -> RecoveryResult:
        """Execute syntax recovery action."""
        try:
            file_path = action.get("target_file")
            if not file_path:
                return RecoveryResult(
                    success=False,
                    message=self._create_failure_message(
                        "syntax",
                        "No target file specified",
                    ),
                    confidence=0.0,
                    changes_made=[],
                    engine_name=self.name,
                )

            changes_made = await self._fix_syntax_errors(Path(file_path))

            if changes_made:
                return RecoveryResult(
                    success=True,
                    message=self._create_success_message("syntax"),
                    confidence=self._calculate_confidence(changes_made),
                    changes_made=changes_made,
                    engine_name=self.name,
                )
            else:
                return RecoveryResult(
                    success=True,
                    message="No syntax errors found to fix",
                    confidence=0.8,
                    changes_made=[],
                    engine_name=self.name,
                )

        except Exception as e:
            return RecoveryResult(
                success=False,
                message=self._create_failure_message("syntax", str(e)),
                confidence=0.0,
                changes_made=[],
                engine_name=self.name,
            )

    async def _fix_syntax_errors(self, file_path: Path) -> list[str]:
        """Fix syntax errors in a file."""
        changes_made = []

        try:
            content = file_path.read_text(encoding="utf-8")

            # Try to parse the file
            try:
                ast.parse(content)
                # No syntax errors found
                return changes_made
            except SyntaxError as e:
                # Fix common syntax errors
                lines = content.split("\n")

                # Fix missing colons
                if "expected ':'" in str(e):
                    line_num = e.lineno - 1
                    if line_num < len(lines):
                        line = lines[line_num]
                        if (
                            line.strip().endswith("if")
                            or line.strip().endswith("for")
                            or line.strip().endswith("while")
                        ):
                            lines[line_num] = line + ":"
                            changes_made.append(
                                self._create_change_message(
                                    f"Added missing colon on line {e.lineno}",
                                ),
                            )

                # Fix indentation issues
                if "expected an indented block" in str(e):
                    line_num = e.lineno - 1
                    if line_num < len(lines):
                        line = lines[line_num]
                        if line.strip() and not line.startswith((" ", "\t")):
                            # Add indentation
                            lines[line_num] = "    " + line
                            changes_made.append(
                                self._create_change_message(
                                    f"Fixed indentation on line {e.lineno}",
                                ),
                            )

                # Write back the fixed content
                if changes_made:
                    fixed_content = "\n".join(lines)
                    file_path.write_text(fixed_content, encoding="utf-8")

        except Exception:
            # Skip files that can't be read or written
            pass

        return changes_made
