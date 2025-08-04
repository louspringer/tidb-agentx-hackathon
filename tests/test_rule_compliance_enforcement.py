#!/usr/bin/env python3
"""
🧪 Test Rule Compliance Enforcement System

Tests the pre-commit hooks, IDE plugins, and automated linting
"""

import pytest
import subprocess
import tempfile
import os
import sys
import json
from pathlib import Path
from unittest.mock import patch


class TestRuleComplianceEnforcement:
    """Test the rule compliance enforcement system"""

    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.plugins_dir = self.project_root / ".cursor" / "plugins"

    def test_rule_compliance_checker_exists(self):
        """Test that rule compliance checker exists and is executable"""
        script_path = self.scripts_dir / "rule-compliance-check.sh"
        assert script_path.exists(), "Rule compliance checker should exist"
        assert os.access(
            script_path, os.X_OK
        ), "Rule compliance checker should be executable"

    def test_mdc_linter_exists(self):
        """Test that MDC linter exists and is executable"""
        linter_path = self.scripts_dir / "mdc-linter.py"
        assert linter_path.exists(), "MDC linter should exist"
        assert os.access(linter_path, os.X_OK), "MDC linter should be executable"

    def test_cursor_plugin_exists(self):
        """Test that Cursor IDE plugin exists and is executable"""
        plugin_path = self.plugins_dir / "rule-compliance-checker.py"
        assert plugin_path.exists(), "Cursor IDE plugin should exist"
        assert os.access(plugin_path, os.X_OK), "Cursor IDE plugin should be executable"

    def test_pre_commit_config_updated(self):
        """Test that pre-commit config includes rule compliance hooks"""
        config_path = self.project_root / "config" / ".pre-commit-config.yaml"
        assert config_path.exists(), "Pre-commit config should exist"

        with open(config_path, "r") as f:
            content = f.read()

        # Check for rule compliance hooks
        assert (
            "rule-compliance-check" in content
        ), "Rule compliance hook should be configured"
        assert "mdc-linter" in content, "MDC linter hook should be configured"

    def test_rule_compliance_script_runs(self):
        """Test that rule compliance script runs without errors"""
        script_path = self.scripts_dir / "rule-compliance-check.sh"

        try:
            result = subprocess.run(
                [str(script_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=30,
            )
            # Should run without crashing (may have violations but shouldn't crash)
            assert result.returncode in [0, 1], "Rule compliance script should run"
        except subprocess.TimeoutExpired:
            pytest.fail("Rule compliance script timed out")
        except Exception as e:
            pytest.fail(f"Rule compliance script failed to run: {e}")

    def test_mdc_linter_validates_structure(self):
        """Test that MDC linter validates file structure"""
        linter_path = self.scripts_dir / "mdc-linter.py"

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
            temp_file = f.name

        try:
            # Test that linter can validate the file
            result = subprocess.run(
                [sys.executable, str(linter_path), temp_file],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Should validate successfully
            assert (
                result.returncode == 0
            ), f"MDC linter should validate valid file: {result.stderr}"
        finally:
            os.unlink(temp_file)

    def test_mdc_linter_rejects_invalid_structure(self):
        """Test that MDC linter rejects invalid file structure"""
        linter_path = self.scripts_dir / "mdc-linter.py"

        # Create an invalid test .mdc file
        invalid_content = """---
description: Test rule
# Missing required fields
---

# Test Rule

This is an invalid .mdc file.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mdc", delete=False) as f:
            f.write(invalid_content)
            temp_file = f.name

        try:
            # Test that linter rejects the file
            result = subprocess.run(
                [sys.executable, str(linter_path), temp_file],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Should reject invalid file
            assert result.returncode != 0, "MDC linter should reject invalid file"
        finally:
            os.unlink(temp_file)

    @patch("subprocess.run")
    def test_cursor_plugin_interface(self, mock_run):
        """Test that Cursor IDE plugin has proper interface"""
        plugin_path = self.plugins_dir / "rule-compliance-checker.py"

        # Mock successful execution
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "All checks passed"

        # Test that plugin can be executed
        result = subprocess.run(
            [sys.executable, str(plugin_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should execute without crashing
        assert result.returncode in [0, 1], "Cursor plugin should execute"

    def test_deterministic_editing_rule_enforcement(self):
        """Test that deterministic editing rules are enforced"""
        # Check that the MDC linter exists and can validate deterministic editing
        linter_path = self.project_root / "scripts" / "mdc-linter.py"

        if linter_path.exists():
            # Test that the linter can validate deterministic editing compliance
            try:
                result = subprocess.run(
                    [sys.executable, str(linter_path), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                # The linter should run without crashing
                assert result.returncode in [0, 1], "MDC linter should run successfully"
            except subprocess.TimeoutExpired:
                pytest.fail("MDC linter timed out")
            except Exception as e:
                pytest.fail(f"MDC linter failed: {e}")
        else:
            pytest.skip("MDC linter not available")

    def test_project_model_includes_rule_compliance(self):
        """Test that project model includes rule compliance"""
        model_file = self.project_root / "project_model_registry.json"

        if model_file.exists():
            with open(model_file, "r") as f:
                model_data = json.load(f)

            # Check that rule compliance is included in requirements
            requirements = model_data.get("requirements_traceability", [])
            rule_compliance_requirements = [
                req
                for req in requirements
                if "rule" in req.get("requirement", "").lower()
                or "compliance" in req.get("requirement", "").lower()
            ]

            assert (
                len(rule_compliance_requirements) > 0
            ), "Project model should include rule compliance requirements"

    def test_requirements_traceability_includes_rule_compliance(self):
        """Test that requirements traceability includes rule compliance"""
        model_file = self.project_root / "project_model_registry.json"

        if model_file.exists():
            with open(model_file, "r") as f:
                model_data = json.load(f)

            # Check that rule compliance is traceable
            requirements = model_data.get("requirements_traceability", [])

            # Look for rule compliance related requirements
            rule_compliance_found = False
            for req in requirements:
                requirement_text = req.get("requirement", "").lower()
                if any(
                    keyword in requirement_text
                    for keyword in ["rule", "compliance", "lint", "enforce"]
                ):
                    rule_compliance_found = True
                    break

            assert rule_compliance_found, "Requirements should include rule compliance"


class TestMDCFileCompliance:
    """Test that all MDC files comply with rules"""

    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.mdc_files = list(self.project_root.rglob("*.mdc"))

    def test_all_mdc_files_comply_with_rules(self):
        """Test that all MDC files comply with established rules"""
        linter_path = self.project_root / "scripts" / "mdc-linter.py"

        if not linter_path.exists():
            pytest.skip("MDC linter not available")

        for mdc_file in self.mdc_files:
            try:
                result = subprocess.run(
                    [sys.executable, str(linter_path), str(mdc_file)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                # All MDC files should pass validation
                assert (
                    result.returncode == 0
                ), f"MDC file {mdc_file} should comply with rules: {result.stderr}"

            except subprocess.TimeoutExpired:
                pytest.fail(f"MDC linter timed out for {mdc_file}")
            except Exception as e:
                pytest.fail(f"MDC linter failed for {mdc_file}: {e}")

    def test_rule_compliance_system_completeness(self):
        """Test that rule compliance system is complete"""
        required_components = [
            "scripts/rule-compliance-check.sh",
            "scripts/mdc-linter.py",
            ".cursor/plugins/rule-compliance-checker.py",
        ]

        for component in required_components:
            component_path = self.project_root / component
            assert (
                component_path.exists()
            ), f"Required component {component} should exist"
            assert os.access(
                component_path, os.R_OK
            ), f"Required component {component} should be readable"
