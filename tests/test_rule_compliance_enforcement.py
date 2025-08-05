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

    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.plugins_dir = self.project_root / ".cursor" / "plugins"

    def test_rule_compliance_checker_exists(self):
        """Test that rule compliance checker exists and is executable"""
        script_path = self.scripts_dir / "rule-compliance-check.sh"
        assert script_path.exists(), "Rule compliance checker should exist"

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

        try:
            result = subprocess.run(
                [str(script_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root,

            )
            # Should run without crashing (may have violations but shouldn't crash)
            assert result.returncode in [0, 1], "Rule compliance script should run"
        except subprocess.TimeoutExpired:
            pytest.fail("Rule compliance script timed out")
        except Exception as e:
            pytest.fail(f"Rule compliance script failed to run: {e}")

        # Create a valid test .mdc file
        valid_content = """---
description: Test rule
globs: ["**/*.py"]
alwaysApply: true
---

# Test Rule

This is a valid .mdc file.
"""

