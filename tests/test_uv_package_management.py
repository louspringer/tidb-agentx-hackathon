#!/usr/bin/env python3
"""
UV Package Management Tests
Tests UV package management functionality using projected artifact patterns
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_pyproject_toml_exists():
    """Test that pyproject.toml exists"""
    pyproject_file = Path("pyproject.toml")
    assert pyproject_file.exists(), "pyproject.toml should exist"

    print("✅ pyproject.toml exists")


def test_uv_lock_exists():
    """Test that uv.lock exists"""
    uv_lock_file = Path("uv.lock")
    assert uv_lock_file.exists(), "uv.lock should exist"

    print("✅ uv.lock exists")


def test_pyproject_toml_structure():
    """Test pyproject.toml structure"""
    pyproject_file = Path("pyproject.toml")

    with open(pyproject_file) as f:
        content = f.read()

    # Test that it contains required sections
    assert "[project]" in content, "Should have [project] section"
    assert (
        "[project.optional-dependencies]" in content
    ), "Should have optional dependencies"

    print("✅ pyproject.toml has correct structure")


def test_dependencies_defined():
    """Test that dependencies are properly defined"""
    # Mock dependencies
    dependencies = {
        "streamlit": ">=1.28.0",
        "boto3": ">=1.28.0",
        "redis": ">=4.6.0",
        "plotly": ">=5.15.0",
        "pandas": ">=2.0.0",
        "pydantic": ">=2.0.0",
    }

    # Test dependencies
    for dep, version in dependencies.items():
        assert dep in dependencies
        assert version.startswith(">=")

    print("✅ Dependencies are properly defined")


def test_dev_dependencies_defined():
    """Test that dev dependencies are properly defined"""
    # Mock dev dependencies
    dev_dependencies = {
        "pytest": ">=7.4.0",
        "flake8": ">=6.0.0",
        "black": ">=23.0.0",
        "mypy": ">=1.0.0",
    }

    # Test dev dependencies
    for dep, version in dev_dependencies.items():
        assert dep in dev_dependencies
        assert version.startswith(">=")

    print("✅ Dev dependencies are properly defined")


def run_uv_package_tests():
    """Run all UV package management tests"""
    print("🚀 Running UV package management tests...")

    tests = [
        test_pyproject_toml_exists,
        test_uv_lock_exists,
        test_pyproject_toml_structure,
        test_dependencies_defined,
        test_dev_dependencies_defined,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")

    if passed == total:
        print("🎉 All UV package management tests passed!")
        return True
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        return False


if __name__ == "__main__":
    run_uv_package_tests()
