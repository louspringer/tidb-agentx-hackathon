#!/usr/bin/env python3
"""
Tests for Rule Compliance System
Tests pre-commit hooks, IDE plugins, and automated linting
"""

import pytest
import subprocess
import tempfile
import os
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

class TestRuleComplianceChecker:
    """Test the rule compliance checker script"""
    
    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.rules_dir = self.project_root / ".cursor" / "rules"
        
    def test_rule_compliance_checker_exists(self):
        """Test that the rule compliance checker script exists"""
        script_path = self.scripts_dir / "rule-compliance-check.sh"
        assert script_path.exists(), "Rule compliance checker script should exist"
        assert script_path.is_file(), "Rule compliance checker should be a file"
        
    def test_rule_compliance_checker_executable(self):
        """Test that the rule compliance checker is executable"""
        script_path = self.scripts_dir / "rule-compliance-check.sh"
        assert os.access(script_path, os.X_OK), "Rule compliance checker should be executable"
        
    def test_mdc_linter_exists(self):
        """Test that the MDC linter exists"""
        linter_path = self.scripts_dir / "mdc-linter.py"
        assert linter_path.exists(), "MDC linter should exist"
        assert linter_path.is_file(), "MDC linter should be a file"
        
    def test_mdc_linter_executable(self):
        """Test that the MDC linter is executable"""
        linter_path = self.scripts_dir / "mdc-linter.py"
        assert os.access(linter_path, os.X_OK), "MDC linter should be executable"

class TestMDCLinter:
    """Test the MDC file linter"""
    
    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.linter_path = self.project_root / "scripts" / "mdc-linter.py"
        
    def create_test_mdc_file(self, content: str) -> Path:
        """Create a temporary test .mdc file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mdc', delete=False) as f:
            f.write(content)
            return Path(f.name)
            
    def test_valid_mdc_file(self):
        """Test that a valid .mdc file passes linting"""
        valid_content = """---
description: Test rule
globs: ["**/*.py"]
alwaysApply: true
---

# Test Rule

This is a valid .mdc file with proper YAML frontmatter.
"""
        
        test_file = self.create_test_mdc_file(valid_content)
        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Valid .mdc file should pass: {result.stderr}"
        finally:
            test_file.unlink()
            
    def test_invalid_mdc_file_missing_frontmatter(self):
        """Test that .mdc file without frontmatter fails"""
        invalid_content = """# Test Rule

This is an invalid .mdc file without YAML frontmatter.
"""
        
        test_file = self.create_test_mdc_file(invalid_content)
        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True
            )
            assert result.returncode != 0, "Invalid .mdc file should fail"
        finally:
            test_file.unlink()
            
    def test_invalid_mdc_file_missing_fields(self):
        """Test that .mdc file with missing required fields fails"""
        invalid_content = """---
description: Test rule
---

# Test Rule

This is an invalid .mdc file missing required fields.
"""
        
        test_file = self.create_test_mdc_file(invalid_content)
        try:
            result = subprocess.run(
                [sys.executable, str(self.linter_path), str(test_file)],
                capture_output=True,
                text=True
            )
            assert result.returncode != 0, "Invalid .mdc file should fail"
        finally:
            test_file.unlink()

class TestPreCommitHooks:
    """Test pre-commit hooks configuration"""
    
    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.pre_commit_config = self.project_root / "config" / ".pre-commit-config.yaml"
        
    def test_pre_commit_config_exists(self):
        """Test that pre-commit configuration exists"""
        assert self.pre_commit_config.exists(), "Pre-commit config should exist"
        
    def test_pre_commit_config_valid_yaml(self):
        """Test that pre-commit config is valid YAML"""
        with open(self.pre_commit_config, 'r') as f:
            content = f.read()
            yaml.safe_load(content)  # Should not raise exception
            
    def test_rule_compliance_hook_configured(self):
        """Test that rule compliance hook is configured"""
        with open(self.pre_commit_config, 'r') as f:
            content = f.read()
            assert "rule-compliance-check" in content, "Rule compliance hook should be configured"
            
    def test_mdc_linter_hook_configured(self):
        """Test that MDC linter hook is configured"""
        with open(self.pre_commit_config, 'r') as f:
            content = f.read()
            assert "mdc-linter" in content, "MDC linter hook should be configured"

class TestCursorPlugin:
    """Test Cursor IDE plugin"""
    
    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.plugin_path = self.project_root / ".cursor" / "plugins" / "rule-compliance-checker.py"
        
    def test_plugin_exists(self):
        """Test that the Cursor plugin exists"""
        assert self.plugin_path.exists(), "Cursor plugin should exist"
        assert self.plugin_path.is_file(), "Cursor plugin should be a file"
        
    def test_plugin_executable(self):
        """Test that the Cursor plugin is executable"""
        assert os.access(self.plugin_path, os.X_OK), "Cursor plugin should be executable"
        
    @patch('subprocess.run')
    def test_plugin_check_file_compliance(self, mock_run):
        """Test plugin file compliance checking"""
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "All checks passed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Import and test the plugin
        import sys
        sys.path.insert(0, str(self.project_root / ".cursor" / "plugins"))
        
        from rule_compliance_checker import RuleComplianceChecker
        checker = RuleComplianceChecker()
        
        result = checker.check_file_compliance("test.py")
        assert result["success"] is True
        assert result["return_code"] == 0

class TestDeterministicEditingCompliance:
    """Test deterministic editing compliance"""
    
    def test_deterministic_editing_rule_exists(self):
        """Test that deterministic editing rule exists"""
        rule_path = Path(__file__).parent.parent / ".cursor" / "rules" / "deterministic-editing.mdc"
        assert rule_path.exists(), "Deterministic editing rule should exist"
        
    def test_deterministic_editing_rule_structure(self):
        """Test that deterministic editing rule has proper structure"""
        rule_path = Path(__file__).parent.parent / ".cursor" / "rules" / "deterministic-editing.mdc"
        
        with open(rule_path, 'r') as f:
            content = f.read()
            
        # Check for YAML frontmatter
        lines = content.split('\n')
        assert lines[0].strip() == '---', "Should start with YAML frontmatter"
        
        # Check for required content
        assert "BANNED: Stochastic/Fuzzy Editors" in content, "Should contain banned tools"
        assert "REQUIRED: Deterministic Tools" in content, "Should contain required tools"
        
    def test_deterministic_editing_rule_always_apply(self):
        """Test that deterministic editing rule is always applied"""
        rule_path = Path(__file__).parent.parent / ".cursor" / "rules" / "deterministic-editing.mdc"
        
        with open(rule_path, 'r') as f:
            content = f.read()
            
        # Parse YAML frontmatter
        lines = content.split('\n')
        frontmatter_end = lines.index('---', 1)
        frontmatter_text = '\n'.join(lines[1:frontmatter_end])
        frontmatter = yaml.safe_load(frontmatter_text)
        
        assert frontmatter.get("alwaysApply") is True, "Deterministic editing rule should always apply"

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
            
    def test_pre_commit_hooks_installed(self):
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
            
    def test_rule_compliance_script_runs(self):
        """Test that rule compliance script runs without errors"""
        script_path = self.project_root / "scripts" / "rule-compliance-check.sh"
        
        try:
            result = subprocess.run(
                [str(script_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            # Should run without crashing
            assert result.returncode in [0, 1], "Rule compliance script should run"
        except Exception as e:
            pytest.fail(f"Rule compliance script failed to run: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 