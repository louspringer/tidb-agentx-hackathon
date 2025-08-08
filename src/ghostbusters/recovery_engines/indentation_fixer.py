"""Indentation fixer recovery engine."""

from pathlib import Path
from typing import Any

from .base_recovery_engine import BaseRecoveryEngine, RecoveryResult


class IndentationFixer(BaseRecoveryEngine):
    """Recovery engine for fixing indentation issues."""

    def __init__(self) -> None:
        """Initialize the indentation fixer."""
        super().__init__("IndentationFixer")

    async def execute_recovery(self, action: dict[str, Any]) -> RecoveryResult:
        """Execute indentation recovery action."""
        try:
            file_path = action.get("target_file")
            if not file_path:
                return RecoveryResult(
                    success=False,
                    message=self._create_failure_message(
                        "indentation",
                        "No target file specified",
                    ),
                    confidence=0.0,
                    changes_made=[],
                    engine_name=self.name,
                )

            changes_made = await self._fix_indentation(Path(file_path))

            if changes_made:
                return RecoveryResult(
                    success=True,
                    message=self._create_success_message("indentation"),
                    confidence=self._calculate_confidence(changes_made),
                    changes_made=changes_made,
                    engine_name=self.name,
                )
            return RecoveryResult(
                success=True,
                message="No indentation issues found to fix",
                confidence=0.8,
                changes_made=[],
                engine_name=self.name,
            )

        except Exception as e:
            return RecoveryResult(
                success=False,
                message=self._create_failure_message("indentation", str(e)),
                confidence=0.0,
                changes_made=[],
                engine_name=self.name,
            )

    async def _fix_indentation(self, file_path: Path) -> list[str]:
        """Fix indentation issues in a file."""
        changes_made = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            fixed_lines = []

            for line_num, line in enumerate(lines):
                fixed_line = line

                # Fix mixed tabs and spaces
                if "\t" in line and " " in line:
                    # Convert tabs to spaces
                    fixed_line = line.expandtabs(4)
                    changes_made.append(
                        self._create_change_message(
                            f"Converted tabs to spaces on line {line_num + 1}",
                        ),
                    )

                # Fix inconsistent indentation
                if line.strip() and not line.startswith((" ", "\t", "#")):
                    # Check if this line should be indented
                    if line_num > 0:
                        prev_line = lines[line_num - 1]
                        if prev_line.strip().endswith(":"):
                            # Add proper indentation
                            fixed_line = "    " + line
                            changes_made.append(
                                self._create_change_message(
                                    f"Fixed indentation on line {line_num + 1}",
                                ),
                            )

                fixed_lines.append(fixed_line)

            # Write back the fixed content
            if changes_made:
                fixed_content = "\n".join(fixed_lines)
                file_path.write_text(fixed_content, encoding="utf-8")

        except Exception:
            # Skip files that can't be read or written
            pass

        return changes_made
