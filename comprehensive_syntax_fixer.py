#!/usr/bin/env python3
"""
Comprehensive Python syntax fixer using multiple strategies
Handles broken Python files that can't be parsed normally
"""

import ast
import tokenize
import io
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Any
import difflib


class ComprehensiveSyntaxFixer:
    """Multi-strategy Python syntax fixer"""

    def __init__(self):
        self.fixes_applied = 0
        self.files_fixed = 0
        self.strategies_used = []

    def fix_file(self, file_path: Path) -> List[str]:
        """Fix syntax errors using multiple strategies"""
        fixes = []

        try:
            with open(file_path, "r") as f:
                content = f.read()
        except Exception as e:
            return [f"Error reading {file_path}: {e}"]

        original_content = content

        # Strategy 1: Try AST parsing first
        if self._can_parse_with_ast(content):
            return []

        # Strategy 2: Fix common patterns that break parsing
        content, pattern_fixes = self._fix_common_patterns(content)
        fixes.extend(pattern_fixes)

        # Strategy 3: Fix indentation issues
        content, indent_fixes = self._fix_indentation_issues(content)
        fixes.extend(indent_fixes)

        # Strategy 4: Fix structural issues
        content, struct_fixes = self._fix_structural_issues(content)
        fixes.extend(struct_fixes)

        # Strategy 5: Try AST parsing again
        if self._can_parse_with_ast(content):
            self.strategies_used.append("comprehensive_fix")
        else:
            # Strategy 6: Aggressive line-by-line fix
            content, aggressive_fixes = self._aggressive_line_fix(content)
            fixes.extend(aggressive_fixes)
            self.strategies_used.append("aggressive_fix")

        # Write fixed content if changes were made
        if content != original_content:
            try:
                with open(file_path, "w") as f:
                    f.write(content)
                self.files_fixed += 1
            except Exception as e:
                return [f"Error writing {file_path}: {e}"]

        return fixes

    def _can_parse_with_ast(self, content: str) -> bool:
        """Check if content can be parsed with AST"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False

    def _fix_common_patterns(self, content: str) -> tuple[str, List[str]]:
        """Fix common patterns that break parsing"""
        fixes = []
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            fixed_line = line

            # Fix 1: Remove type annotations from subprocess.run calls
            if "subprocess.run(" in line and ": Any =" in line:
                fixed_line = re.sub(r"(\w+): Any = (\w+)", r"\1=\2", line)
                if fixed_line != line:
                    fixes.append(f"Fixed subprocess.run parameters at line {i+1}")

            # Fix 2: Fix malformed variable assignments
            if ": Any =" in line and not line.startswith("    "):
                if self._should_be_indented(lines, i):
                    fixed_line = "    " + line.strip()
                    fixes.append(f"Fixed variable assignment indentation at line {i+1}")

            # Fix 3: Fix unindented statements after colons
            if (
                i > 0
                and lines[i - 1].strip().endswith(":")
                and not line.startswith("    ")
            ):
                if line.strip() and not line.strip().startswith("#"):
                    fixed_line = "    " + line.strip()
                    fixes.append(
                        f"Fixed unindented statement after colon at line {i+1}"
                    )

            fixed_lines.append(fixed_line)

        return "\n".join(fixed_lines), fixes

    def _fix_indentation_issues(self, content: str) -> tuple[str, List[str]]:
        """Fix indentation issues systematically"""
        fixes = []
        lines = content.split("\n")
        fixed_lines = []

        # Track indentation context
        indent_stack = [0]  # Current indentation levels
        in_block = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                fixed_lines.append(line)
                continue

            # Skip comments and imports
            if (
                stripped.startswith("#")
                or stripped.startswith("import ")
                or stripped.startswith("from ")
            ):
                fixed_lines.append(line)
                continue

            # Check if we're in a block that requires indentation
            if self._in_block_context(lines, i):
                expected_indent = indent_stack[-1] + 4
                current_indent = len(line) - len(line.lstrip())

                if current_indent < expected_indent and stripped:
                    # Fix indentation
                    new_line = " " * expected_indent + stripped
                    fixed_lines.append(new_line)
                    fixes.append(f"Fixed indentation at line {i+1}")
                    indent_stack.append(expected_indent)
                else:
                    fixed_lines.append(line)
                    if current_indent > indent_stack[-1]:
                        indent_stack.append(current_indent)
            else:
                fixed_lines.append(line)
                # Reset indentation if we're at top level
                if not line.startswith("    "):
                    indent_stack = [0]

        return "\n".join(fixed_lines), fixes

    def _fix_structural_issues(self, content: str) -> tuple[str, List[str]]:
        """Fix structural issues in the code"""
        fixes = []
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            fixed_line = line

            # Fix 1: Add missing colons after function/class definitions
            if re.match(r"^\s*(def|class)\s+\w+\s*\([^)]*\)\s*$", line):
                if not line.strip().endswith(":"):
                    fixed_line = line.rstrip() + ":"
                    fixes.append(f"Added missing colon at line {i+1}")

            # Fix 2: Fix malformed try/except blocks
            if line.strip().startswith("try") and not line.strip().endswith(":"):
                fixed_line = line.rstrip() + ":"
                fixes.append(f"Added missing colon in try block at line {i+1}")

            # Fix 3: Fix malformed if/for/while blocks
            if re.match(
                r"^\s*(if|for|while|with)\s+.*$", line
            ) and not line.strip().endswith(":"):
                fixed_line = line.rstrip() + ":"
                fixes.append(f"Added missing colon in control block at line {i+1}")

            fixed_lines.append(fixed_line)

        return "\n".join(fixed_lines), fixes

    def _aggressive_line_fix(self, content: str) -> tuple[str, List[str]]:
        """Aggressive line-by-line fix for severely broken files"""
        fixes = []
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            fixed_line = line

            # Aggressive fix: If line looks like it should be indented, indent it
            if self._looks_like_indented_statement(line, lines, i):
                if not line.startswith("    "):
                    fixed_line = "    " + line.strip()
                    fixes.append(f"Aggressively fixed indentation at line {i+1}")

            fixed_lines.append(fixed_line)

        return "\n".join(fixed_lines), fixes

    def _should_be_indented(self, lines: List[str], line_index: int) -> bool:
        """Check if a line should be indented based on context"""
        # Look backwards for context
        for i in range(line_index - 1, max(0, line_index - 5), -1):
            line = lines[i].strip()
            if line.startswith("def ") or line.startswith("class "):
                return True
            if (
                line.startswith("if ")
                or line.startswith("for ")
                or line.startswith("while ")
            ):
                return True
            if (
                line.startswith("try:")
                or line.startswith("except:")
                or line.startswith("finally:")
            ):
                return True
            if line.startswith("with "):
                return True
            if line.endswith(":"):
                return True
            # If we hit a top-level statement, we're not in a block
            if line and not line.startswith("    "):
                if not line.startswith("import ") and not line.startswith("from "):
                    return False
        return False

    def _in_block_context(self, lines: List[str], line_index: int) -> bool:
        """Check if we're in a block context that requires indentation"""
        # Look backwards for block starters
        for i in range(line_index - 1, max(0, line_index - 3), -1):
            line = lines[i].strip()
            if line.endswith(":"):
                return True
            if line.startswith("def ") or line.startswith("class "):
                return True
            if (
                line.startswith("if ")
                or line.startswith("for ")
                or line.startswith("while ")
            ):
                return True
            if (
                line.startswith("try:")
                or line.startswith("except:")
                or line.startswith("finally:")
            ):
                return True
            if line.startswith("with "):
                return True
        return False

    def _looks_like_indented_statement(
        self, line: str, lines: List[str], line_index: int
    ) -> bool:
        """Check if a line looks like it should be indented"""
        stripped = line.strip()
        if not stripped or line.startswith("    "):
            return False

        # Skip function/class definitions, imports, comments
        if (
            stripped.startswith("def ")
            or stripped.startswith("class ")
            or stripped.startswith("import ")
            or stripped.startswith("from ")
            or stripped.startswith("#")
            or stripped.startswith("#!")
        ):
            return False

        # Check if it looks like a statement that should be indented
        if (
            (":" in stripped and "=" in stripped)
            or stripped.endswith(":")
            or "assert" in stripped
            or "print(" in stripped
            or "return" in stripped
            or "break" in stripped
            or "continue" in stripped
        ):
            return self._should_be_indented(lines, line_index)

        return False


def find_python_files() -> List[Path]:
    """Find all Python files in the project"""
    python_files = []
    for file_path in Path(".").rglob("*.py"):
        if "__pycache__" not in str(file_path) and ".git" not in str(file_path):
            python_files.append(file_path)
    return python_files


def main() -> None:
    """Run the comprehensive syntax fixer"""
    print("🔧 Running comprehensive Python syntax fixer...")

    fixer = ComprehensiveSyntaxFixer()
    python_files = find_python_files()
    total_fixes = 0

    for file_path in python_files:
        print(f"\n📁 Processing: {file_path}")
        fixes = fixer.fix_file(file_path)

        if fixes:
            print(f"  ✅ Fixed {len(fixes)} issues:")
            for fix in fixes:
                print(f"    - {fix}")
            total_fixes += len(fixes)
        else:
            print("  ✅ No syntax issues found")

    print(f"\n🎉 Total fixes applied: {total_fixes}")
    print(f"📊 Files fixed: {fixer.files_fixed}")
    print(f"🔧 Strategies used: {fixer.strategies_used}")

    # Test if flake8 passes now
    print("\n🧪 Testing with flake8...")
    try:
        result = subprocess.run(
            ["python", "-m", "flake8", ".", "--count", "--select=E9,F63,F7,F82"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ All files pass flake8 syntax checks!")
        else:
            print("⚠️  Some files still have syntax issues:")
            print(result.stdout)
    except FileNotFoundError:
        print("⚠️  Flake8 not found, skipping syntax test")


if __name__ == "__main__":
    main()
