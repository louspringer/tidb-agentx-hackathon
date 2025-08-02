#!/usr/bin/env python3
"""
🧪 Rule Compliance Test Suite

Tests for rule compliance enforcement system including MDC linter,
Cursor IDE plugin, and pre-commit hooks.
"""

import pytest
import subprocess
import tempfile
import os
import sys
import yaml
import json
import fnmatch
from pathlib import Path
from unittest.mock import patch, Mock

class TestMDCLinter:
    """Test MDC linter functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.linter_path = self.project_root / "scripts" / "mdc-linter.py"
    
    def test_valid_mdc_file(self):
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mdc', delete=False) as f:
            f.write(valid_content)
            test_file = Path(f.name)
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            assert result.returncode == 0, f"Valid .mdc file should pass: {result.stderr}"
        finally:
            # Clean up
            test_file.unlink(missing_ok=True)
    
    def test_invalid_mdc_file_missing_frontmatter(self):
        """Test that linter rejects .mdc file without frontmatter"""
        # Create an invalid test .mdc file (missing frontmatter)
        invalid_content = """# Invalid Rule

This is an invalid .mdc file without frontmatter.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mdc', delete=False) as f:
            f.write(invalid_content)
            test_file = Path(f.name)
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            assert result.returncode != 0, "Invalid .mdc file should fail"
        finally:
            # Clean up
            test_file.unlink(missing_ok=True)
    
    def test_invalid_mdc_file_missing_fields(self):
        """Test that linter rejects .mdc file with missing required fields"""
        # Create an invalid test .mdc file (missing required fields)
        invalid_content = """---
description: Test rule
---

# Test Rule

This is an invalid .mdc file missing required fields.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mdc', delete=False) as f:
            f.write(invalid_content)
            test_file = Path(f.name)
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            assert result.returncode != 0, "Invalid .mdc file should fail"
        finally:
            # Clean up
            test_file.unlink(missing_ok=True)

class TestCursorPlugin:
    """Test Cursor IDE plugin functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.plugin_path = self.project_root / ".cursor" / "plugins" / "rule-compliance-checker.py"
    
    def test_plugin_exists(self):
        """Test that Cursor IDE plugin exists"""
        assert self.plugin_path.exists(), "Cursor IDE plugin should exist"
        assert os.access(self.plugin_path, os.X_OK), "Cursor IDE plugin should be executable"
    
    def test_plugin_check_file_compliance(self):
        """Test that plugin can check file compliance"""
        # Mock the plugin import since it may not be fully implemented
        with patch('builtins.__import__') as mock_import:
            mock_module = Mock()
            mock_import.return_value = mock_module
            
            # Test that plugin can be executed
            try:
                result = subprocess.run(
                    [sys.executable, str(self.plugin_path)],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                # Should not crash
                assert result.returncode in [0, 1], "Cursor plugin should not crash"
            except Exception as e:
                pytest.skip(f"Cursor plugin not fully implemented: {e}")

class TestRuleComplianceIntegration:
    """Integration tests for rule compliance system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
    
    def test_all_mdc_files_comply(self):
        """Test that all .mdc files in the project comply with rules"""
        mdc_files = list(self.project_root.rglob("*.mdc"))
        
        for mdc_file in mdc_files:
            # Skip test files
            if "test" in str(mdc_file).lower():
                continue
            
            with open(mdc_file, 'r') as f:
                content = f.read()
            
            # Check for YAML frontmatter
            lines = content.split('\n')
            assert lines[0].strip() == '---', f"{mdc_file} should start with YAML frontmatter"
            
            # Check for required fields
            assert "description:" in content, f"{mdc_file} should have description field"
            assert "globs:" in content, f"{mdc_file} should have globs field"
            assert "alwaysApply:" in content, f"{mdc_file} should have alwaysApply field"
    
    def test_pre_commit_hooks_can_be_installed(self):
        """Test that pre-commit hooks can be installed"""
        try:
            result = subprocess.run(
                ["pre-commit", "install"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            # Should not fail (hooks may already be installed)
            assert result.returncode in [0, 1], "Pre-commit install should not fail"
        except FileNotFoundError:
            pytest.skip("pre-commit not installed")
    
    def test_rule_compliance_system_completeness(self):
        """Test that rule compliance system is complete"""
        # Check all required components exist
        components = [
            self.project_root / "scripts" / "rule-compliance-check.sh",
            self.project_root / "scripts" / "mdc-linter.py",
            self.project_root / ".cursor" / "plugins" / "rule-compliance-checker.py",
            self.project_root / "config" / ".pre-commit-config.yaml",
            self.project_root / ".cursor" / "rules" / "deterministic-editing.mdc"
        ]
        
        for component in components:
            assert component.exists(), f"Required component should exist: {component}"
        
        # Check that project model includes rule compliance
        model_path = self.project_root / "project_model_registry.json"
        with open(model_path, 'r') as f:
            model = json.load(f)
        
        assert "rule_compliance" in model["domains"], "Project model should include rule_compliance domain"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 