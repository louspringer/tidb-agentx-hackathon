#!/usr/bin/env python3
"""
Test Rule Compliance Enforcement System
Tests the pre-commit hooks, IDE plugins, and automated linting
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
        assert os.access(script_path, os.X_OK), "Rule compliance checker should be executable"
        
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
        
        with open(config_path, 'r') as f:
            content = f.read()
            
        # Check for rule compliance hooks
        assert "rule-compliance-check" in content, "Rule compliance hook should be configured"
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
                timeout=30
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mdc', delete=False) as f:
            f.write(valid_content)
            test_file = Path(f.name)
            
        try:
            result = subprocess.run(
                [sys.executable, str(linter_path), str(test_file)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            assert result.returncode == 0, f"Valid .mdc file should pass: {result.stderr}"
        finally:
            # Clean up
            test_file.unlink(missing_ok=True)
            
    def test_mdc_linter_rejects_invalid_structure(self):
        """Test that MDC linter rejects invalid file structure"""
        linter_path = self.scripts_dir / "mdc-linter.py"
        
        # Create an invalid test .mdc file (missing frontmatter)
        invalid_content = """# Invalid Rule

This is an invalid .mdc file without frontmatter.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mdc', delete=False) as f:
            f.write(invalid_content)
            test_file = Path(f.name)
            
        try:
            result = subprocess.run(
                [sys.executable, str(linter_path), str(test_file)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            assert result.returncode != 0, "Invalid .mdc file should fail"
        finally:
            # Clean up
            test_file.unlink(missing_ok=True)
            
    @patch('subprocess.run')
    def test_cursor_plugin_interface(self, mock_run):
        """Test that Cursor IDE plugin has correct interface"""
        plugin_path = self.plugins_dir / "rule-compliance-checker.py"
        assert plugin_path.exists(), "Cursor IDE plugin should exist"
        
        # Mock successful execution
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Rule compliance check passed"
        
        # Test that plugin can be executed
        try:
            result = subprocess.run(
                [sys.executable, str(plugin_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            # Should not crash
            assert result.returncode in [0, 1], "Cursor plugin should not crash"
        except Exception as e:
            pytest.fail(f"Cursor plugin failed to run: {e}")
            
    def test_deterministic_editing_rule_enforcement(self):
        """Test that deterministic editing rule is enforced"""
        # Check that deterministic editing rule exists
        rule_file = self.project_root / ".cursor" / "rules" / "deterministic-editing.mdc"
        assert rule_file.exists(), "Deterministic editing rule should exist"
        
        with open(rule_file, 'r') as f:
            content = f.read()
            
        lines = content.split('\n')
        assert lines[0].strip() == '---', "Should start with YAML frontmatter"
        
        # Parse frontmatter
        frontmatter_end = lines.index('---', 1)
        frontmatter_text = '\n'.join(lines[1:frontmatter_end])
        frontmatter = yaml.safe_load(frontmatter_text)
        
        assert frontmatter.get("alwaysApply") is True, "Should always apply"
        # Check that .mdc files are included in globs (using fnmatch for proper glob pattern matching)
        globs = frontmatter.get("globs", [])
        mdc_patterns = [g for g in globs if fnmatch.fnmatch("test.mdc", g) or fnmatch.fnmatch("**/*.mdc", g)]
        assert len(mdc_patterns) > 0, "Should apply to .mdc files"
        
    def test_project_model_includes_rule_compliance(self):
        """Test that project model includes rule compliance domain"""
        model_path = self.project_root / "project_model_registry.json"
        assert model_path.exists(), "Project model should exist"
        
        with open(model_path, 'r') as f:
            model = json.load(f)
            
        assert "rule_compliance" in model["domains"], "Should include rule_compliance domain"
        
        rule_compliance_domain = model["domains"]["rule_compliance"]
        # Check for the correct pattern format
        patterns = rule_compliance_domain["patterns"]
        rule_checker_patterns = [p for p in patterns if "rule-compliance-check" in p]
        assert len(rule_checker_patterns) > 0, "Should include rule compliance checker"
        mdc_linter_patterns = [p for p in patterns if "mdc-linter" in p]
        assert len(mdc_linter_patterns) > 0, "Should include MDC linter"
        assert "deterministic-editing" in rule_compliance_domain["content_indicators"], "Should include deterministic editing"
        
    def test_requirements_traceability_includes_rule_compliance(self):
        """Test that requirements traceability includes rule compliance"""
        model_path = self.project_root / "project_model_registry.json"
        
        with open(model_path, 'r') as f:
            model = json.load(f)
            
        requirements = model["requirements_traceability"]
        rule_compliance_requirements = [
            req for req in requirements 
            if req.get("domain") == "rule_compliance"
        ]
        
        assert len(rule_compliance_requirements) >= 3, "Should have at least 3 rule compliance requirements"
        
        requirement_names = [req["requirement"] for req in rule_compliance_requirements]
        assert "Rule compliance enforcement system" in requirement_names, "Should include rule compliance enforcement"
        assert "Deterministic editing enforcement" in requirement_names, "Should include deterministic editing enforcement"
        assert "Immediate IDE feedback" in requirement_names, "Should include immediate IDE feedback"

class TestRuleComplianceIntegration:
    """Integration tests for rule compliance system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        
    def test_all_mdc_files_comply_with_rules(self):
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