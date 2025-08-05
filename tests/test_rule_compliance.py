#!/usr/bin/env python3
"""
🧪 Rule Compliance Test Suite

Tests for rule compliance enforcement system including MDC linter,
Cursor IDE plugin, and pre-commit hooks.
"""


import subprocess
import tempfile
import os
import sys

        """Test that linter accepts valid .mdc file"""
        # Create a valid test .mdc file
        valid_content = """---
description: Test rule
globs: ["**/*.py"]
alwaysApply: true
---

# Test Rule

This is a valid .mdc file.
"""

        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True,

        """Test that linter rejects .mdc file without frontmatter"""
        # Create an invalid test .mdc file (missing frontmatter)
        invalid_content = """# Invalid Rule

This is an invalid .mdc file without frontmatter.
"""

        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True,

            )
            assert result.returncode != 0, "Invalid .mdc file should fail"
        finally:
            # Clean up
            test_file.unlink(missing_ok=True)

        """Test that linter rejects .mdc file with missing required fields"""
        # Create an invalid test .mdc file (missing required fields)
        invalid_content = """---
description: Test rule
---

# Test Rule

This is an invalid .mdc file missing required fields.
"""

        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True,

            )
            assert result.returncode != 0, "Invalid .mdc file should fail"
        finally:
            # Clean up
            test_file.unlink(missing_ok=True)


        for mdc_file in mdc_files:
            # Skip test files
            if "test" in str(mdc_file).lower():
                continue

