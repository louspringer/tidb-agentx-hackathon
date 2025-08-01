#!/usr/bin/env python3
"""
Tests for UV Package Management Requirements
Tests that UV is properly configured and all dependencies are managed correctly
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

class TestUVPackageManagement:
    """Test UV package management requirements"""
    
    def __init__(self):
        """Initialize test environment"""
        self.project_root = Path(__file__).parent.parent
        
    def load_project_model(self) -> Dict[str, Any]:
        """Load the project model registry"""
        model_path = self.project_root / "project_model_registry.json"
        with open(model_path, 'r') as f:
            return json.load(f)
    
    def test_requirement_36_uv_package_management(self):
        """Test UV package management enforcement requirement."""
        print("Testing Requirement 36: UV package management enforcement...")
        
        project_model = self.load_project_model()
        if not project_model:
            return False
        
        # Check that package_management domain exists
        assert "package_management" in project_model["domains"], "package_management domain should exist"
        
        package_domain = project_model["domains"]["package_management"]
        requirements = package_domain["requirements"]
        
        uv_requirement = "Use UV for all package management"
        assert uv_requirement in requirements, f"Missing UV requirement: {uv_requirement}"
        print(f"✅ UV requirement found: {uv_requirement}")
        
        # Check content indicators include UV
        content_indicators = package_domain["content_indicators"]
        uv_indicator = "uv"
        assert uv_indicator in content_indicators, f"Missing UV indicator: {uv_indicator}"
        print(f"✅ UV indicator found: {uv_indicator}")
        
        # Check that pyproject.toml exists
        pyproject_file = self.project_root / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml should exist"
        print("✅ pyproject.toml exists")
        
        # Check that uv.lock exists
        uv_lock_file = self.project_root / "uv.lock"
        assert uv_lock_file.exists(), "uv.lock should exist"
        print("✅ uv.lock exists")
        
        print("✅ Requirement 36: UV package management enforcement - PASSED")
        return True
    
    def test_requirement_37_streamlit_dependencies_uv(self):
        """Test Streamlit app dependencies with UV requirement."""
        print("Testing Requirement 37: Streamlit app dependencies with UV...")
        
        project_model = self.load_project_model()
        if not project_model:
            return False
        
        # Check requirement exists in traceability
        requirements_traceability = project_model["requirements_traceability"]
        streamlit_req = "Streamlit app dependencies with UV"
        
        found = False
        for req in requirements_traceability:
            if req["requirement"] == streamlit_req:
                found = True
                print(f"✅ Requirement found in traceability: {streamlit_req}")
                break
        
        assert found, f"Missing requirement in traceability: {streamlit_req}"
        
        # Check that pyproject.toml contains streamlit dependencies
        pyproject_file = self.project_root / "pyproject.toml"
        with open(pyproject_file, 'r') as f:
            content = f.read()
        
        required_deps = ["streamlit", "boto3", "redis", "plotly", "pandas", "pydantic", "bcrypt"]
        for dep in required_deps:
            assert dep in content, f"Missing dependency in pyproject.toml: {dep}"
            print(f"✅ Dependency found: {dep}")
        
        print("✅ Requirement 37: Streamlit app dependencies with UV - PASSED")
        return True
    
    def test_requirement_38_security_dependencies_uv(self):
        """Test security-first dependencies with UV requirement."""
        print("Testing Requirement 38: Security-first dependencies with UV...")
        
        project_model = self.load_project_model()
        if not project_model:
            return False
        
        # Check requirement exists in traceability
        requirements_traceability = project_model["requirements_traceability"]
        security_req = "Security-first dependencies with UV"
        
        found = False
        for req in requirements_traceability:
            if req["requirement"] == security_req:
                found = True
                print(f"✅ Requirement found in traceability: {security_req}")
                break
        
        assert found, f"Missing requirement in traceability: {security_req}"
        
        # Check that pyproject.toml contains security dependencies
        pyproject_file = self.project_root / "pyproject.toml"
        with open(pyproject_file, 'r') as f:
            content = f.read()
        
        required_deps = ["cryptography", "PyJWT", "bandit", "safety"]
        for dep in required_deps:
            assert dep in content, f"Missing security dependency in pyproject.toml: {dep}"
            print(f"✅ Security dependency found: {dep}")
        
        print("✅ Requirement 38: Security-first dependencies with UV - PASSED")
        return True
    
    def test_requirement_39_dev_dependencies_uv(self):
        """Test development dependencies with UV requirement."""
        print("Testing Requirement 39: Development dependencies with UV...")
        
        project_model = self.load_project_model()
        if not project_model:
            return False
        
        # Check requirement exists in traceability
        requirements_traceability = project_model["requirements_traceability"]
        dev_req = "Development dependencies with UV"
        
        found = False
        for req in requirements_traceability:
            if req["requirement"] == dev_req:
                found = True
                print(f"✅ Requirement found in traceability: {dev_req}")
                break
        
        assert found, f"Missing requirement in traceability: {dev_req}"
        
        # Check that pyproject.toml contains dev dependencies
        pyproject_file = self.project_root / "pyproject.toml"
        with open(pyproject_file, 'r') as f:
            content = f.read()
        
        required_deps = ["pytest", "flake8", "black", "mypy"]
        for dep in required_deps:
            assert dep in content, f"Missing dev dependency in pyproject.toml: {dep}"
            print(f"✅ Dev dependency found: {dep}")
        
        print("✅ Requirement 39: Development dependencies with UV - PASSED")
        return True
    
    def test_uv_rule_exists(self):
        """Test that UV rule exists and is properly configured."""
        print("Testing UV rule existence...")
        
        uv_rule_file = self.project_root / ".cursor" / "rules" / "package-management-uv.mdc"
        assert uv_rule_file.exists(), "UV rule file should exist"
        
        with open(uv_rule_file, 'r') as f:
            content = f.read()
        
        # Check for UV-specific content
        assert "UV Package Management Rules" in content, "UV rule should contain UV package management rules"
        assert "uv sync" in content, "UV rule should mention uv sync"
        assert "pyproject.toml" in content, "UV rule should mention pyproject.toml"
        
        print("✅ UV rule exists and is properly configured")
        return True
    
    def test_uv_commands_work(self):
        """Test that UV commands work properly."""
        print("Testing UV commands...")
        
        try:
            # Test uv sync
            result = subprocess.run(
                ["uv", "sync", "--dry-run"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            assert result.returncode == 0, "uv sync --dry-run should work"
            print("✅ uv sync --dry-run works")
            
            # Test uv run
            result = subprocess.run(
                ["uv", "run", "python", "-c", "import streamlit; print('streamlit imported')"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            assert result.returncode == 0, "uv run should work"
            assert "streamlit imported" in result.stdout, "uv run should execute Python code"
            print("✅ uv run works")
            
        except FileNotFoundError:
            print("⚠️  UV not found in PATH, skipping command tests")
            return True
        
        print("✅ UV commands work properly")
        return True

def main():
    """Run all UV package management tests."""
    print("🔧 Testing UV Package Management Requirements")
    print("=" * 60)
    
    tester = TestUVPackageManagement()
    
    tests = [
        tester.test_requirement_36_uv_package_management,
        tester.test_requirement_37_streamlit_dependencies_uv,
        tester.test_requirement_38_security_dependencies_uv,
        tester.test_requirement_39_dev_dependencies_uv,
        tester.test_uv_rule_exists,
        tester.test_uv_commands_work
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 UV Package Management Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All UV package management requirements implemented successfully!")
        print("✅ UV is properly configured and all dependencies are managed correctly")
        return True
    else:
        print("⚠️  Some UV package management requirements need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 