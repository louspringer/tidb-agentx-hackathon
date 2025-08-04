#!/usr/bin/env python3
"""
Fix f-string issues by converting them to regular strings
"""

import re
import sys
from pathlib import Path


def fix_f_strings_in_file(file_path: Path) -> None:
    """Fix f-string issues in a single file"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match f-strings without placeholders
    pattern = r'f"([^"]*)"'

    def replace_f_string(match):
        inner_content = match.group(1)
        # Only replace if there are no curly braces (no placeholders)
        if "{" not in inner_content and "}" not in inner_content:
            return f'"{inner_content}"'
        return match.group(0)

    new_content = re.sub(pattern, replace_f_string, content)

    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Fixed f-strings in {file_path}")


def main():
    """Fix f-strings in all Python files"""
    directories = ["src", "tests", "scripts", ".cursor"]

    for directory in directories:
        if Path(directory).exists():
            for py_file in Path(directory).rglob("*.py"):
                fix_f_strings_in_file(py_file)


if __name__ == "__main__":
    main()
