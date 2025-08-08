"""Import resolver recovery engine."""

from pathlib import Path
from typing import Any

from .base_recovery_engine import BaseRecoveryEngine, RecoveryResult


class ImportResolver(BaseRecoveryEngine):
    """Recovery engine for fixing import issues."""

    def __init__(self) -> None:
        """Initialize the import resolver."""
        super().__init__("ImportResolver")

    async def execute_recovery(self, action: dict[str, Any]) -> RecoveryResult:
        """Execute import recovery action."""
        try:
            file_path = action.get("target_file")
            if not file_path:
                return RecoveryResult(
                    success=False,
                    message=self._create_failure_message(
                        "import",
                        "No target file specified",
                    ),
                    confidence=0.0,
                    changes_made=[],
                    engine_name=self.name,
                )

            changes_made = await self._fix_imports(Path(file_path))

            if changes_made:
                return RecoveryResult(
                    success=True,
                    message=self._create_success_message("import"),
                    confidence=self._calculate_confidence(changes_made),
                    changes_made=changes_made,
                    engine_name=self.name,
                )
            else:
                return RecoveryResult(
                    success=True,
                    message="No import issues found to fix",
                    confidence=0.8,
                    changes_made=[],
                    engine_name=self.name,
                )

        except Exception as e:
            return RecoveryResult(
                success=False,
                message=self._create_failure_message("import", str(e)),
                confidence=0.0,
                changes_made=[],
                engine_name=self.name,
            )

    async def _fix_imports(self, file_path: Path) -> list[str]:
        """Fix import issues in a file."""
        changes_made = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            fixed_lines = []

            for line_num, line in enumerate(lines):
                fixed_line = line

                # Fix common import issues
                if line.strip().startswith("import ") and " as " not in line:
                    # Check for unused imports (simplified check)
                    import_name = line.strip().split()[1]
                    if not self._is_import_used(content, import_name):
                        # Comment out unused import
                        fixed_line = f"# {line}  # noqa: F401"
                        changes_made.append(
                            self._create_change_message(
                                f"Commented unused import on line {line_num + 1}",
                            ),
                        )

                # Fix relative imports
                if line.strip().startswith("from .") and not line.strip().startswith(
                    "from . import",
                ):
                    # Convert relative import to absolute if needed
                    if ".." in line:
                        fixed_line = line.replace("..", "src")
                        changes_made.append(
                            self._create_change_message(
                                f"Fixed relative import on line {line_num + 1}",
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

    def _is_import_used(self, content: str, import_name: str) -> bool:
        """Check if an import is used in the content."""
        # Simple check - in a real implementation, you'd use AST analysis
        return import_name in content
