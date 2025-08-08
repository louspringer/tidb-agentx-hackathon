"""Type annotation fixer recovery engine."""

import ast
from pathlib import Path
from typing import Any

from .base_recovery_engine import BaseRecoveryEngine, RecoveryResult


class TypeAnnotationFixer(BaseRecoveryEngine):
    """Recovery engine for fixing type annotation issues."""

    def __init__(self) -> None:
        """Initialize the type annotation fixer."""
        super().__init__("TypeAnnotationFixer")

    async def execute_recovery(self, action: dict[str, Any]) -> RecoveryResult:
        """Execute type annotation recovery action."""
        try:
            file_path = action.get("target_file")
            if not file_path:
                return RecoveryResult(
                    success=False,
                    message=self._create_failure_message(
                        "type_annotation",
                        "No target file specified",
                    ),
                    confidence=0.0,
                    changes_made=[],
                    engine_name=self.name,
                )

            changes_made = await self._fix_type_annotations(Path(file_path))

            if changes_made:
                return RecoveryResult(
                    success=True,
                    message=self._create_success_message("type_annotation"),
                    confidence=self._calculate_confidence(changes_made),
                    changes_made=changes_made,
                    engine_name=self.name,
                )
            return RecoveryResult(
                success=True,
                message="No type annotation issues found to fix",
                confidence=0.8,
                changes_made=[],
                engine_name=self.name,
            )

        except Exception as e:
            return RecoveryResult(
                success=False,
                message=self._create_failure_message("type_annotation", str(e)),
                confidence=0.0,
                changes_made=[],
                engine_name=self.name,
            )

    async def _fix_type_annotations(self, file_path: Path) -> list[str]:
        """Fix type annotation issues in a file."""
        changes_made = []

        try:
            content = file_path.read_text(encoding="utf-8")

            # Parse the file to analyze functions
            try:
                tree = ast.parse(content)
                lines = content.split("\n")

                # Find functions without return type annotations
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not node.returns and not node.name.startswith("_"):
                            # Add return type annotation
                            line_num = node.lineno - 1
                            if line_num < len(lines):
                                line = lines[line_num]
                                if "def " in line and ":" in line:
                                    # Add -> Any return type
                                    if "->" not in line:
                                        fixed_line = line.replace("):", ") -> Any:")
                                        lines[line_num] = fixed_line
                                        changes_made.append(
                                            self._create_change_message(
                                                f"Added return type annotation to function '{node.name}' on line {node.lineno}",
                                            ),
                                        )

                # Write back the fixed content
                if changes_made:
                    fixed_content = "\n".join(lines)
                    file_path.write_text(fixed_content, encoding="utf-8")

            except SyntaxError:
                # Skip files with syntax errors
                pass

        except Exception:
            # Skip files that can't be read or written
            pass

        return changes_made
