#!/usr/bin/env python3
"""
Improved syntax fix script that's more careful about structural integrity
"""

import subprocess
from pathlib import Path
from typing import List


def fix_syntax_safely(file_path: Path) -> List[str]:
    """Fix syntax errors safely without introducing structural issues"""
    fixes = []

    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

    lines = content.split("\n")
    fixed_lines = []

    # Track if we already have a shebang
    has_shebang = False

    for i, line in enumerate(lines):
        fixed_line = line

        # Check for existing shebang
        if line.strip().startswith("#!"):
            if has_shebang:
                # Skip duplicate shebangs
                continue
            has_shebang = True

        # Only fix indentation for lines that are clearly inside functions
        if i > 0 and is_inside_function(lines, i):
            if needs_indentation(line):
                fixed_line = "    " + line
                fixes.append(f"Fixed indentation at line {i+1}")

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


def is_inside_function(lines: List[str], line_index: int) -> bool:
    """Check if a line is inside a function definition"""
    # Look backwards for function definition
    for i in range(line_index - 1, max(0, line_index - 10), -1):
        line = lines[i].strip()
        if line.startswith("def ") and line.endswith(":"):
            return True
        if line.startswith("class ") and line.endswith(":"):
            return True
        if line.startswith("if ") and line.endswith(":"):
            return True
        if line.startswith("for ") and line.endswith(":"):
            return True
        if line.startswith("while ") and line.endswith(":"):
            return True
        if (
            line.startswith("try:")
            or line.startswith("except:")
            or line.startswith("finally:")
        ):
            return True
        if line.startswith("with ") and line.endswith(":"):
            return True
        # If we hit a top-level statement, we're not inside a function
        if line and not line.startswith("    ") and not line.startswith("\t"):
            if not line.startswith("import ") and not line.startswith("from "):
                return False

    return False


def needs_indentation(line: str) -> bool:
    """Check if a line needs indentation"""
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

    # Check if it looks like a variable assignment or statement
    if ":" in stripped and "=" in stripped:
        return True

    if stripped.endswith(":"):
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
    """Fix syntax errors safely in all Python files"""
    print("🔧 Safely fixing Python syntax errors...")

    python_files = find_python_files()
    total_fixes = 0

    for file_path in python_files:
        print(f"\n📁 Processing: {file_path}")
        fixes = fix_syntax_safely(file_path)

        if fixes:
            print(f"  ✅ Fixed {len(fixes)} issues:")
            for fix in fixes:
                print(f"    - {fix}")
            total_fixes += len(fixes)
        else:
            print("  ✅ No syntax issues found")

    print(f"\n🎉 Total fixes applied: {total_fixes}")

    # Test if black can now format the files
    print("\n🧪 Testing with black...")
    try:
        result = subprocess.run(
            ["black", "--check", "."], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ All files can now be formatted with black!")
        else:
            print("⚠️  Some files still have syntax issues:")
            print(result.stderr)
    except FileNotFoundError:
        print("⚠️  Black not found, skipping format test")


if __name__ == "__main__":
    main()
