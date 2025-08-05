#!/usr/bin/env python3
"""
Comprehensive script to fix all remaining syntax errors
"""

import subprocess
import re
from pathlib import Path
from typing import List


def fix_file_syntax(file_path: Path) -> List[str]:
    """Fix syntax errors in a single file"""
    fixes = []

    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        fixed_line = line

        # Fix specific patterns that are causing syntax errors

        # Pattern 1: Unindented variable assignments after function definitions
        if i > 0 and is_after_function_definition(lines, i):
            if needs_indentation_fix(line):
                fixed_line = "    " + line
                fixes.append(f"Fixed indentation at line {i+1}")

        # Pattern 2: Unindented control flow statements
        if i > 0 and is_after_control_flow(lines, i):
            if needs_indentation_fix(line):
                fixed_line = "    " + line
                fixes.append(f"Fixed indentation at line {i+1}")

        # Pattern 3: Unindented statements after try/if/for blocks
        if i > 0 and is_after_block_start(lines, i):
            if needs_indentation_fix(line):
                fixed_line = "    " + line
                fixes.append(f"Fixed indentation at line {i+1}")

        # Pattern 4: Fix subprocess.run calls with type annotations
        if "subprocess.run(" in line and ": Any =" in line:
            # Remove type annotations from subprocess.run parameters
            fixed_line = re.sub(r"(\w+): Any = (\w+)", r"\1=\2", line)
            if fixed_line != line:
                fixes.append(f"Fixed subprocess.run parameters at line {i+1}")

        # Pattern 5: Fix variable assignments with type annotations
        if ": Any =" in line and not line.startswith("    "):
            # Check if this should be indented
            if i > 0 and should_be_indented(lines, i):
                fixed_line = "    " + line
                fixes.append(f"Fixed variable assignment indentation at line {i+1}")

        fixed_lines.append(fixed_line)

    # Write fixed content back
    if fixes:
        fixed_content = "\n".join(fixed_lines)
        try:
            with open(file_path, "w") as f:
                f.write(fixed_content)
        except Exception as e:
            return [f"Error writing {file_path}: {e}"]

    return fixes


def is_after_function_definition(lines: List[str], line_index: int) -> bool:
    """Check if line is after a function definition"""
    for i in range(line_index - 1, max(0, line_index - 5), -1):
        line = lines[i].strip()
        if line.startswith("def ") and line.endswith(":"):
            return True
        if line.startswith("class ") and line.endswith(":"):
            return True
        if line and not line.startswith("    ") and not line.startswith("\t"):
            if not line.startswith("import ") and not line.startswith("from "):
                return False
    return False


def is_after_control_flow(lines: List[str], line_index: int) -> bool:
    """Check if line is after a control flow statement"""
    for i in range(line_index - 1, max(0, line_index - 3), -1):
        line = lines[i].strip()
        if (
            line.startswith("if ")
            or line.startswith("for ")
            or line.startswith("while ")
            or line.startswith("try:")
            or line.startswith("except:")
            or line.startswith("finally:")
            or line.startswith("with ")
            or line.startswith("elif ")
            or line.startswith("else:")
        ):
            if line.endswith(":"):
                return True
        if line and not line.startswith("    ") and not line.startswith("\t"):
            return False
    return False


def is_after_block_start(lines: List[str], line_index: int) -> bool:
    """Check if line is after a block start"""
    for i in range(line_index - 1, max(0, line_index - 2), -1):
        line = lines[i].strip()
        if line.endswith(":"):
            return True
        if line and not line.startswith("    ") and not line.startswith("\t"):
            return False
    return False


def should_be_indented(lines: List[str], line_index: int) -> bool:
    """Check if a line should be indented based on context"""
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
        if line and not line.startswith("    ") and not line.startswith("\t"):
            if not line.startswith("import ") and not line.startswith("from "):
                return False
    return False


def needs_indentation_fix(line: str) -> bool:
    """Check if a line needs indentation fix"""
    stripped = line.strip()
    if not stripped:
        return False

    # Skip lines that are already indented
    if line.startswith("    ") or line.startswith("\t"):
        return False

    # Skip function/class definitions
    if stripped.startswith("def ") or stripped.startswith("class "):
        return False

    # Skip imports
    if stripped.startswith("import ") or stripped.startswith("from "):
        return False

    # Skip comments
    if stripped.startswith("#"):
        return False

    # Skip shebangs
    if stripped.startswith("#!"):
        return False

    # Skip empty lines
    if not stripped:
        return False

    # Check if it looks like a statement that should be indented
    if (
        (":" in stripped and "=" in stripped)
        or stripped.endswith(":")
        or "assert" in stripped
        or "print(" in stripped
        or "for " in stripped
        or "if " in stripped
        or "try:" in stripped
    ):
        return True

    return False


def find_python_files() -> List[Path]:
    """Find all Python files in the project"""
    python_files = []
    for file_path in Path(".").rglob("*.py"):
        # Skip __pycache__ and .git directories
        if "__pycache__" not in str(file_path) and ".git" not in str(file_path):
            python_files.append(file_path)
    return python_files


def main() -> None:
    """Fix all remaining syntax errors"""
    print("🔧 Fixing all remaining syntax errors...")

    python_files = find_python_files()
    total_fixes = 0

    for file_path in python_files:
        print(f"\n📁 Processing: {file_path}")
        fixes = fix_file_syntax(file_path)

        if fixes:
            print(f"  ✅ Fixed {len(fixes)} issues:")
            for fix in fixes:
                print(f"    - {fix}")
            total_fixes += len(fixes)
        else:
            print("  ✅ No syntax issues found")

    print(f"\n🎉 Total fixes applied: {total_fixes}")

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
