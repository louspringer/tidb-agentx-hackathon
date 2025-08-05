#!/usr/bin/env python3
"""
Sophisticated Python AST-based syntax fixer
Uses Python's built-in ast module for proper parsing and fixing
"""

import ast
import tokenize
import io
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import re


class PythonASTFixer:
    """AST-based Python syntax fixer"""

    def __init__(self):
        self.fixes_applied = 0
        self.errors_found = 0

    def fix_file(self, file_path: Path) -> List[str]:
        """Fix syntax errors in a Python file using AST analysis"""
        fixes = []

        try:
            with open(file_path, "r") as f:
                content = f.read()
        except Exception as e:
            return [f"Error reading {file_path}: {e}"]

        # First, try to parse with AST to identify issues
        try:
            ast.parse(content)
            # If AST parsing succeeds, the file is syntactically correct
            return []
        except SyntaxError as e:
            # AST parsing failed, we need to fix the syntax
            self.errors_found += 1
            fixes.extend(self._fix_syntax_error(file_path, content, e))

        return fixes

    def _fix_syntax_error(
        self, file_path: Path, content: str, error: SyntaxError
    ) -> List[str]:
        """Fix specific syntax errors identified by AST"""
        fixes = []

        # Parse tokens to understand the structure
        try:
            tokens = list(
                tokenize.tokenize(io.BytesIO(content.encode("utf-8")).readline)
            )
        except tokenize.TokenError:
            # Token parsing failed, use line-by-line analysis
            return self._fix_line_by_line(file_path, content)

        # Analyze indentation structure
        indentation_issues = self._analyze_indentation(tokens, content)
        if indentation_issues:
            fixes.extend(
                self._fix_indentation_issues(file_path, content, indentation_issues)
            )

        # Fix specific syntax patterns
        fixes.extend(self._fix_common_patterns(file_path, content))

        return fixes

    def _analyze_indentation(
        self, tokens: List[tokenize.TokenInfo], content: str
    ) -> List[Dict[str, Any]]:
        """Analyze indentation structure using tokens"""
        issues = []
        lines = content.split("\n")

        # Track indentation levels
        current_indent = 0
        expected_indent = 0
        in_block = False

        for i, token in enumerate(tokens):
            if token.type == tokenize.INDENT:
                current_indent = len(token.string)
                if current_indent != expected_indent and expected_indent > 0:
                    issues.append(
                        {
                            "line": token.start[0],
                            "expected": expected_indent,
                            "actual": current_indent,
                            "type": "indentation_mismatch",
                        }
                    )
            elif token.type == tokenize.DEDENT:
                current_indent = 0
                expected_indent = max(0, expected_indent - 4)
            elif token.type == tokenize.NL:
                # Check if next line should be indented
                if i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    if next_token.type == tokenize.NAME:
                        # Check if we're in a block that requires indentation
                        if self._should_be_indented(tokens, i):
                            expected_indent = current_indent + 4

        return issues

    def _should_be_indented(
        self, tokens: List[tokenize.TokenInfo], position: int
    ) -> bool:
        """Check if the next statement should be indented"""
        # Look backwards for block starters
        for i in range(position - 1, max(0, position - 10), -1):
            if i >= 0 and i < len(tokens):
                token = tokens[i]
                if token.type == tokenize.NAME:
                    if token.string in [
                        "def",
                        "class",
                        "if",
                        "for",
                        "while",
                        "try",
                        "with",
                    ]:
                        return True
                elif token.type == tokenize.OP and token.string == ":":
                    return True
        return False

    def _fix_indentation_issues(
        self, file_path: Path, content: str, issues: List[Dict[str, Any]]
    ) -> List[str]:
        """Fix indentation issues"""
        fixes = []
        lines = content.split("\n")

        for issue in issues:
            line_num = issue["line"] - 1  # Convert to 0-based index
            if line_num < len(lines):
                line = lines[line_num]
                expected_indent = issue["expected"]

                # Fix indentation
                stripped = line.strip()
                if stripped:
                    new_line = " " * expected_indent + stripped
                    lines[line_num] = new_line
                    fixes.append(f"Fixed indentation at line {line_num + 1}")

        if fixes:
            # Write fixed content
            fixed_content = "\n".join(lines)
            try:
                with open(file_path, "w") as f:
                    f.write(fixed_content)
            except Exception as e:
                return [f"Error writing {file_path}: {e}"]

        return fixes

    def _fix_common_patterns(self, file_path: Path, content: str) -> List[str]:
        """Fix common syntax patterns that cause issues"""
        fixes = []
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            fixed_line = line

            # Pattern 1: Fix unindented variable assignments
            if self._is_unindented_assignment(line, lines, i):
                fixed_line = "    " + line.strip()
                fixes.append(f"Fixed unindented assignment at line {i + 1}")

            # Pattern 2: Fix subprocess.run calls with type annotations
            if "subprocess.run(" in line and ": Any =" in line:
                fixed_line = re.sub(r"(\w+): Any = (\w+)", r"\1=\2", line)
                if fixed_line != line:
                    fixes.append(f"Fixed subprocess.run parameters at line {i + 1}")

            # Pattern 3: Fix variable assignments with type annotations
            if ": Any =" in line and not line.startswith("    "):
                if self._should_be_indented_by_context(lines, i):
                    fixed_line = "    " + line.strip()
                    fixes.append(
                        f"Fixed variable assignment indentation at line {i + 1}"
                    )

            fixed_lines.append(fixed_line)

        if fixes:
            # Write fixed content
            fixed_content = "\n".join(fixed_lines)
            try:
                with open(file_path, "w") as f:
                    f.write(fixed_content)
            except Exception as e:
                return [f"Error writing {file_path}: {e}"]

        return fixes

    def _is_unindented_assignment(
        self, line: str, lines: List[str], line_index: int
    ) -> bool:
        """Check if a line is an unindented assignment that should be indented"""
        stripped = line.strip()
        if not stripped or line.startswith("    "):
            return False

        # Check if it looks like an assignment
        if "=" in stripped and ":" in stripped:
            # Check if we're in a context that requires indentation
            return self._should_be_indented_by_context(lines, line_index)

        return False

    def _should_be_indented_by_context(self, lines: List[str], line_index: int) -> bool:
        """Check if a line should be indented based on surrounding context"""
        # Look backwards for context
        for i in range(line_index - 1, max(0, line_index - 10), -1):
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
            if line and not line.startswith("    ") and not line.startswith("\t"):
                if not line.startswith("import ") and not line.startswith("from "):
                    return False
        return False

    def _fix_line_by_line(self, file_path: Path, content: str) -> List[str]:
        """Fallback line-by-line fix for files that can't be tokenized"""
        fixes = []
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            fixed_line = line

            # Basic indentation fixes
            if self._needs_indentation_fix(line, lines, i):
                fixed_line = "    " + line.strip()
                fixes.append(f"Fixed indentation at line {i + 1}")

            fixed_lines.append(fixed_line)

        if fixes:
            fixed_content = "\n".join(fixed_lines)
            try:
                with open(file_path, "w") as f:
                    f.write(fixed_content)
            except Exception as e:
                return [f"Error writing {file_path}: {e}"]

        return fixes

    def _needs_indentation_fix(
        self, line: str, lines: List[str], line_index: int
    ) -> bool:
        """Check if a line needs indentation fix"""
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
        ):
            return self._should_be_indented_by_context(lines, line_index)

        return False


def find_python_files() -> List[Path]:
    """Find all Python files in the project"""
    python_files = []
    for file_path in Path(".").rglob("*.py"):
        if "__pycache__" not in str(file_path) and ".git" not in str(file_path):
            python_files.append(file_path)
    return python_files


def main() -> None:
    """Run the AST-based Python syntax fixer"""
    print("🔧 Running AST-based Python syntax fixer...")

    fixer = PythonASTFixer()
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
    print(f"📊 Files with errors: {fixer.errors_found}")

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
