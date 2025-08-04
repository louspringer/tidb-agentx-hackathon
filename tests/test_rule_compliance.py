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
import json
from pathlib import Path


class TestMDCLinter:
    """Test MDC linter functionality"""

    def setup_method(self) -> None:
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.linter_path = self.project_root / "scripts" / "mdc-linter.py"

    def test_valid_mdc_file(self) -> None:
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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mdc", delete=False) as f:
            f.write(valid_content)
            test_file = Path(f.name)

        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            assert (
                result.returncode == 0
            ), f"Valid .mdc file should pass: {result.stderr}"
        finally:
            # Clean up
            test_file.unlink(missing_ok=True)

    def test_invalid_mdc_file_missing_frontmatter(self) -> None:
        """Test that linter rejects .mdc file without frontmatter"""
        # Create an invalid test .mdc file (missing frontmatter)
        invalid_content = """# Invalid Rule

This is an invalid .mdc file without frontmatter.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mdc", delete=False) as f:
            f.write(invalid_content)
            test_file = Path(f.name)

        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            assert result.returncode != 0, "Invalid .mdc file should fail"
        finally:
            # Clean up
            test_file.unlink(missing_ok=True)

    def test_invalid_mdc_file_missing_fields(self) -> None:
        """Test that linter rejects .mdc file with missing required fields"""
        # Create an invalid test .mdc file (missing required fields)
        invalid_content = """---
description: Test rule
---

# Test Rule

This is an invalid .mdc file missing required fields.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mdc", delete=False) as f:
            f.write(invalid_content)
            test_file = Path(f.name)

        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            assert result.returncode != 0, "Invalid .mdc file should fail"
        finally:
            # Clean up
            test_file.unlink(missing_ok=True)


class TestCursorPlugin:
    """Test Cursor IDE plugin functionality"""

    def setup_method(self) -> None:
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.plugin_path = (
            self.project_root / ".cursor" / "plugins" / "rule-compliance-checker.py"
        )

    def test_plugin_exists(self) -> None:
        """Test that Cursor IDE plugin exists and is executable"""
        assert self.plugin_path.exists(), "Cursor IDE plugin should exist"
        assert os.access(
            self.plugin_path, os.X_OK
        ), "Cursor IDE plugin should be executable"

    def test_plugin_check_file_compliance(self) -> None:
        """Test that plugin can check file compliance"""
        # Create a test file to check
        test_file = self.project_root / "test_file.py"
        test_content = "print('Hello, World!')"

        with open(test_file, "w") as f:
            f.write(test_content)

        try:
            result = subprocess.run(
                [sys.executable, str(self.plugin_path), str(test_file)],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            # Should run without crashing (may have violations but shouldn't crash)
            assert result.returncode in [0, 1], "Plugin should run without crashing"
        finally:
            test_file.unlink(missing_ok=True)


class TestRuleComplianceSystem:
    """Test the complete rule compliance system"""

    def setup_method(self) -> None:
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent

    def test_all_mdc_files_comply(self) -> None:
        """Test that all .mdc files in the project comply with rules"""
        mdc_files = list(self.project_root.rglob("*.mdc"))

        for mdc_file in mdc_files:
            # Skip test files
            if "test" in str(mdc_file).lower():
                continue

            with open(mdc_file, "r") as f:
                content = f.read()

            # Check for YAML frontmatter
            lines = content.split("\n")
            assert (
                lines[0].strip() == "---"
            ), f"{mdc_file} should start with YAML frontmatter"

            # Check for required fields
            assert (
                "description:" in content
            ), f"{mdc_file} should have description field"
            assert "globs:" in content, f"{mdc_file} should have globs field"
            assert (
                "alwaysApply:" in content
            ), f"{mdc_file} should have alwaysApply field"

    def test_rule_compliance_system_completeness(self) -> None:
        """Test that rule compliance system is complete"""
        # Check all required components exist
        components = [
            self.project_root / "scripts" / "mdc-linter.py",
            self.project_root / ".cursor" / "plugins" / "rule-compliance-checker.py",
            self.project_root / "config" / ".pre-commit-config.yaml",
        ]

        for component in components:
            assert component.exists(), f"Required component should exist: {component}"

        # Check that project model includes rule compliance
        model_path = self.project_root / "project_model_registry.json"
        with open(model_path, "r") as f:
            model = json.load(f)

        assert (
            "rule_compliance" in model["domains"]
        ), "Project model should include rule_compliance domain"
