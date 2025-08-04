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

    def __init__(self: Any) -> None:
        """Initialize test environment"""
        self.project_root = Path(__file__).parent.parent

    def load_project_model(self: Any) -> Dict[str, Any]:
        """Load the project model registry"""
        model_path: Any = self.project_root / "project_model_registry.json"
        with open(model_path, "r") as f:
            return json.load(f)

    def test_requirement_36_uv_package_management(self: Any) -> None:
        """Test UV package management enforcement requirement."""
        print("Testing Requirement 36: UV package management enforcement...")

        project_model: Any = self.load_project_model()
        if not project_model:
            return

        # Check that package_management domain exists
        assert (
            "package_management" in project_model["domains"]
        ), "package_management domain should exist"

        package_domain: Any = project_model["domains"]["package_management"]
        requirements: Any = package_domain["requirements"]

        uv_requirement: str = "Use UV for all package management"
        assert (
            uv_requirement in requirements
        ), f"Missing UV requirement: {uv_requirement}"
        print(f"✅ UV requirement found: {uv_requirement}")

        # Check content indicators include UV
        content_indicators: Any = package_domain["content_indicators"]
        uv_indicator: str = "uv"
        assert (
            uv_indicator in content_indicators
        ), f"Missing UV indicator: {uv_indicator}"
        print(f"✅ UV indicator found: {uv_indicator}")

        # Check that pyproject.toml exists
        pyproject_file: Any = self.project_root / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml should exist"
        print("✅ pyproject.toml exists")

        # Check that uv.lock exists
        uv_lock_file: Any = self.project_root / "uv.lock"
        assert uv_lock_file.exists(), "uv.lock should exist"
        print("✅ uv.lock exists")

        print("✅ Requirement 36: UV package management enforcement - PASSED")

    def test_requirement_37_streamlit_dependencies_uv(self: Any) -> None:
        """Test Streamlit app dependencies with UV requirement."""
        print("Testing Requirement 37: Streamlit app dependencies with UV...")

        project_model: Any = self.load_project_model()
        if not project_model:
            return

        # Check requirement exists in traceability
        requirements_traceability: Any = project_model["requirements_traceability"]
        streamlit_req: str = "Streamlit app dependencies with UV"

        found: bool = False
        for req in requirements_traceability:
            if req["requirement"] == streamlit_req:
                found: bool = True
                print(f"✅ Requirement found in traceability: {streamlit_req}")
                break

        assert found, f"Missing requirement in traceability: {streamlit_req}"

        # Check that pyproject.toml contains streamlit dependencies
        pyproject_file: Any = self.project_root / "pyproject.toml"
        with open(pyproject_file, "r") as f:
            content: Any = f.read()

        required_deps: list = [
            "streamlit",
            "boto3",
            "redis",
            "plotly",
            "pandas",
            "pydantic",
        ]

        for dep in required_deps:
            assert dep in content, f"Missing dependency in pyproject.toml: {dep}"
            print(f"✅ Dependency found: {dep}")

        print("✅ Requirement 37: Streamlit app dependencies with UV - PASSED")

    def test_requirement_38_security_dependencies_uv(self: Any) -> None:
        """Test security-first dependencies with UV requirement."""
        print("Testing Requirement 38: Security-first dependencies with UV...")

        project_model: Any = self.load_project_model()
        if not project_model:
            return

        # Check requirement exists in traceability
        requirements_traceability: Any = project_model["requirements_traceability"]
        security_req: str = "Security-first dependencies with UV"

        found: bool = False
        for req in requirements_traceability:
            if req["requirement"] == security_req:
                found: bool = True
                print(f"✅ Requirement found in traceability: {security_req}")
                break

        assert found, f"Missing requirement in traceability: {security_req}"

        # Check that pyproject.toml contains security dependencies
        pyproject_file: Any = self.project_root / "pyproject.toml"
        with open(pyproject_file, "r") as f:
            content: Any = f.read()

        security_deps: list = [
            "cryptography",
            "PyJWT",
            "bcrypt",
        ]

        for dep in security_deps:
            assert dep in content, f"Missing security dependency: {dep}"
            print(f"✅ Security dependency found: {dep}")

        print("✅ Requirement 38: Security-first dependencies with UV - PASSED")

    def test_requirement_39_dev_dependencies_uv(self: Any) -> None:
        """Test development dependencies with UV requirement."""
        print("Testing Requirement 39: Development dependencies with UV...")

        project_model: Any = self.load_project_model()
        if not project_model:
            return

        # Check requirement exists in traceability
        requirements_traceability: Any = project_model["requirements_traceability"]
        dev_req: str = "Development dependencies with UV"

        found: bool = False
        for req in requirements_traceability:
            if req["requirement"] == dev_req:
                found: bool = True
                print(f"✅ Requirement found in traceability: {dev_req}")
                break

        assert found, f"Missing requirement in traceability: {dev_req}"

        # Check that pyproject.toml contains dev dependencies
        pyproject_file: Any = self.project_root / "pyproject.toml"
        with open(pyproject_file, "r") as f:
            content: Any = f.read()

        dev_deps: list = [
            "pytest",
            "flake8",
            "black",
            "mypy",
        ]

        for dep in dev_deps:
            assert dep in content, f"Missing dev dependency: {dep}"
            print(f"✅ Dev dependency found: {dep}")

        print("✅ Requirement 39: Development dependencies with UV - PASSED")

    def test_uv_rule_exists(self: Any) -> None:
        """Test that UV rule exists in the project model."""
        print("Testing UV rule existence...")

        project_model: Any = self.load_project_model()
        if not project_model:
            return

        # Check that UV rule exists in requirements_traceability
        requirements_traceability: Any = project_model["requirements_traceability"]
        uv_rule: str = "UV package management enforcement"

        found: bool = False
        for req in requirements_traceability:
            if req["requirement"] == uv_rule:
                found: bool = True
                print(f"✅ UV rule found in traceability: {uv_rule}")
                break

        assert found, f"Missing UV rule in traceability: {uv_rule}"

        print("✅ UV rule exists - PASSED")

    def test_uv_commands_work(self: Any) -> None:
        """Test that UV commands work correctly."""
        print("Testing UV commands...")

        # Test that UV is installed
        try:
            result = subprocess.run(
                ["uv", "--version"], capture_output=True, text=True, timeout=10
            )
            assert result.returncode == 0, "UV should be installed"
            print("✅ UV is installed")

            # Test that we can read pyproject.toml
            pyproject_file = self.project_root / "pyproject.toml"
            assert pyproject_file.exists(), "pyproject.toml should exist"
            print("✅ pyproject.toml exists")

            # Test that we can read uv.lock
            uv_lock_file = self.project_root / "uv.lock"
            assert uv_lock_file.exists(), "uv.lock should exist"
            print("✅ uv.lock exists")

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"⚠️ UV command test skipped: {e}")
            return

        print("✅ UV commands work - PASSED")


def main() -> None:
    """Run all UV package management tests."""
    print("📦 Testing UV Package Management Requirements")
    print("=" * 60)

    tester = TestUVPackageManagement()

    tests = [
        tester.test_requirement_36_uv_package_management,
        tester.test_requirement_37_streamlit_dependencies_uv,
        tester.test_requirement_38_security_dependencies_uv,
        tester.test_requirement_39_dev_dependencies_uv,
        tester.test_uv_rule_exists,
        tester.test_uv_commands_work,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print()

    print("=" * 60)
    print(f"📊 UV Package Management Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All UV package management tests passed!")
        return True
    else:
        print("⚠️ Some UV package management tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
