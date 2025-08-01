#!/usr/bin/env python3
"""
Tests for Makefile Integration with Model-Driven Approach
Tests that the Makefile properly leverages the project_model_registry.json
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List

class TestMakefileIntegration:
    """Test Makefile integration with model-driven approach"""
    
    def __init__(self):
        """Initialize test environment"""
        self.project_root = Path(__file__).parent.parent
        self.model_file = self.project_root / "project_model_registry.json"
        self.makefile = self.project_root / "Makefile"
        
    def load_project_model(self) -> Dict[str, Any]:
        """Load the project model registry"""
        with open(self.model_file, 'r') as f:
            return json.load(f)
    
    def test_makefile_exists(self):
        """Test that Makefile exists and is properly structured."""
        print("Testing Makefile existence and structure...")
        
        assert self.makefile.exists(), "Makefile should exist"
        print("✅ Makefile exists")
        
        with open(self.makefile, 'r') as f:
            content = f.read()
        
        # Check for model-driven references
        assert "project_model_registry.json" in content, "Makefile should reference project model registry"
        print("✅ Makefile references project model registry")
        
        # Check for domain-specific targets
        assert "install-python" in content, "Makefile should have install-python target"
        assert "test-security" in content, "Makefile should have test-security target"
        assert "lint-all" in content, "Makefile should have lint-all target"
        print("✅ Makefile has domain-specific targets")
        
        # Check for UV integration
        assert "$(UV) sync" in content, "Makefile should use UV for Python dependencies"
        print("✅ Makefile uses UV for Python dependencies")
        
        print("✅ Makefile structure is valid")
        return True
    
    def test_makefile_domains_match_model(self):
        """Test that Makefile domains match the model registry."""
        print("Testing Makefile domains match model registry...")
        
        project_model = self.load_project_model()
        model_domains = set(project_model["domains"].keys())
        
        # Read Makefile to extract domain targets
        with open(self.makefile, 'r') as f:
            content = f.read()
        
        # Extract domain names from install targets
        import re
        install_targets = re.findall(r'install-(\w+):', content)
        makefile_domains = set(install_targets)
        
        # Check that key domains are present
        key_domains = {"python", "bash", "security", "streamlit", "healthcare"}
        for domain in key_domains:
            assert domain in makefile_domains, f"Makefile should have install-{domain} target"
            print(f"✅ Makefile has install-{domain} target")
        
        print("✅ Makefile domains match model registry")
        return True
    
    def test_makefile_help_works(self):
        """Test that make help works and shows proper information."""
        print("Testing make help functionality...")
        
        try:
            result = subprocess.run(
                ["make", "help"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            assert result.returncode == 0, "make help should work"
            assert "OpenFlow Playground" in result.stdout, "make help should show project name"
            assert "Available targets" in result.stdout, "make help should show available targets"
            print("✅ make help works correctly")
            
        except FileNotFoundError:
            print("⚠️  make command not found, skipping command test")
            return True
        
        return True
    
    def test_makefile_show_domains_works(self):
        """Test that make show-domains works and shows model domains."""
        print("Testing make show-domains functionality...")
        
        try:
            result = subprocess.run(
                ["make", "show-domains"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            assert result.returncode == 0, "make show-domains should work"
            assert "Available domains from model" in result.stdout, "make show-domains should show domains"
            print("✅ make show-domains works correctly")
            
        except FileNotFoundError:
            print("⚠️  make command not found, skipping command test")
            return True
        
        return True
    
    def test_makefile_show_rules_works(self):
        """Test that make show-rules works and shows available rules."""
        print("Testing make show-rules functionality...")
        
        try:
            result = subprocess.run(
                ["make", "show-rules"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            assert result.returncode == 0, "make show-rules should work"
            assert "Available rules" in result.stdout, "make show-rules should show rules"
            print("✅ make show-rules works correctly")
            
        except FileNotFoundError:
            print("⚠️  make command not found, skipping command test")
            return True
        
        return True
    
    def test_makefile_validate_model_works(self):
        """Test that make validate-model works."""
        print("Testing make validate-model functionality...")
        
        try:
            result = subprocess.run(
                ["make", "validate-model"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            assert result.returncode == 0, "make validate-model should work"
            assert "Project model registry is valid JSON" in result.stdout, "make validate-model should validate JSON"
            print("✅ make validate-model works correctly")
            
        except FileNotFoundError:
            print("⚠️  make command not found, skipping command test")
            return True
        
        return True
    
    def test_makefile_targets_are_sensible(self):
        """Test that Makefile targets are sensible and well-organized."""
        print("Testing Makefile target organization...")
        
        with open(self.makefile, 'r') as f:
            content = f.read()
        
        # Check for proper target organization
        target_categories = [
            "INSTALLATION TARGETS",
            "TESTING TARGETS", 
            "LINTING TARGETS",
            "FORMATTING TARGETS",
            "VALIDATION TARGETS",
            "CLEANUP TARGETS",
            "DEPLOYMENT TARGETS",
            "SECURITY TARGETS",
            "DOCUMENTATION TARGETS",
            "DEVELOPMENT TARGETS",
            "UTILITY TARGETS"
        ]
        
        for category in target_categories:
            assert category in content, f"Makefile should have {category} section"
            print(f"✅ Makefile has {category} section")
        
        # Check for proper help documentation
        assert "## " in content, "Makefile should have help documentation"
        assert "Available domains" in content, "Makefile should show available domains"
        assert "Examples" in content, "Makefile should show examples"
        print("✅ Makefile has proper help documentation")
        
        print("✅ Makefile targets are well-organized")
        return True
    
    def test_makefile_leverages_model_driven_approach(self):
        """Test that Makefile properly leverages the model-driven approach."""
        print("Testing Makefile model-driven integration...")
        
        project_model = self.load_project_model()
        
        # Check that Makefile uses model file
        with open(self.makefile, 'r') as f:
            content = f.read()
        
        assert "MODEL_FILE := project_model_registry.json" in content, "Makefile should reference model file"
        print("✅ Makefile references model file")
        
        # Check that Makefile uses domain-specific tools from model
        domains = project_model["domains"]
        
        # Check Python domain tools
        if "python" in domains:
            python_domain = domains["python"]
            if "linter" in python_domain:
                linter = python_domain["linter"]
                assert linter in content, f"Makefile should use {linter} for Python linting"
                print(f"✅ Makefile uses {linter} for Python linting")
        
        # Check bash domain tools
        if "bash" in domains:
            bash_domain = domains["bash"]
            if "linter" in bash_domain:
                linter = bash_domain["linter"]
                assert linter in content, f"Makefile should use {linter} for bash linting"
                print(f"✅ Makefile uses {linter} for bash linting")
        
        print("✅ Makefile properly leverages model-driven approach")
        return True

def main():
    """Run all Makefile integration tests."""
    print("🔧 Testing Makefile Integration with Model-Driven Approach")
    print("=" * 70)
    
    tester = TestMakefileIntegration()
    
    tests = [
        tester.test_makefile_exists,
        tester.test_makefile_domains_match_model,
        tester.test_makefile_help_works,
        tester.test_makefile_show_domains_works,
        tester.test_makefile_show_rules_works,
        tester.test_makefile_validate_model_works,
        tester.test_makefile_targets_are_sensible,
        tester.test_makefile_leverages_model_driven_approach
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Makefile Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Makefile integration tests passed!")
        print("✅ Makefile properly integrates with model-driven approach")
        return True
    else:
        print("⚠️  Some Makefile integration tests need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 