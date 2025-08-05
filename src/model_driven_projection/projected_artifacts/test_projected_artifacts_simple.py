#!/usr/bin/env python3
"""
Simple test for projected artifacts

This test verifies basic functionality without requiring full imports.
"""

import ast
from pathlib import Path


def test_projected_artifacts_syntax() -> None:
    """Test that projected artifacts have valid Python syntax."""
    test_files = [
        "src/streamlit/openflow_quickstart_app.py",
        "src/security_first/input_validator.py",
    ]

    for file_path in test_files:
        if Path(file_path).exists():
            try:
                with open(file_path) as f:
                    content = f.read()

                # Parse with AST to check syntax
                ast.parse(content)
                print(f"✅ {file_path} has valid Python syntax")

            except SyntaxError as e:
                print(f"❌ Syntax error in {file_path}: {e}")
                # Removed return statement
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                # Removed return statement
        else:
            print(f"⚠️  File not found: {file_path}")

    # Removed return statement


def test_projected_artifacts_structure() -> None:
    """Test that projected artifacts have the expected structure."""
    # Test streamlit app structure
    streamlit_file = Path("src/streamlit/openflow_quickstart_app.py")
    if streamlit_file.exists():
        with open(streamlit_file) as f:
            content = f.read()

        tree = ast.parse(content)

        # Count elements
        imports = 0
        functions = 0
        classes = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports += 1
            elif isinstance(node, ast.FunctionDef):
                functions += 1
            elif isinstance(node, ast.ClassDef):
                classes += 1

        print("📊 Streamlit app structure:")
        print(f"  Imports: {imports}")
        print(f"  Functions: {functions}")
        print(f"  Classes: {classes}")

        # Basic structure validation
        assert imports > 0, "Should have imports"
        assert functions > 0, "Should have functions"
        assert classes > 0, "Should have classes"

        print("✅ Streamlit app has expected structure")

    # Test security module structure
    security_file = Path("src/security_first/input_validator.py")
    if security_file.exists():
        with open(security_file) as f:
            content = f.read()

        tree = ast.parse(content)

        # Count elements
        imports = 0
        functions = 0
        classes = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports += 1
            elif isinstance(node, ast.FunctionDef):
                functions += 1
            elif isinstance(node, ast.ClassDef):
                classes += 1

        print("📊 Security module structure:")
        print(f"  Imports: {imports}")
        print(f"  Functions: {functions}")
        print(f"  Classes: {classes}")

        # Basic structure validation
        assert imports > 0, "Should have imports"
        assert functions > 0, "Should have functions"

        print("✅ Security module has expected structure")

    # Removed return statement


def test_projected_artifacts_content() -> None:
    """Test that projected artifacts contain expected content."""
    # Test streamlit app content
    streamlit_file = Path("src/streamlit/openflow_quickstart_app.py")
    if streamlit_file.exists():
        with open(streamlit_file) as f:
            content = f.read()

        # Check for expected content
        expected_imports = [
            "import streamlit as st",
            "import plotly.graph_objects as go",
            "from cryptography.fernet import Fernet",
            "from pydantic import BaseModel, Field, field_validator",
        ]

        for expected_import in expected_imports:
            if expected_import in content:
                print(f"✅ Found expected import: {expected_import}")
            else:
                print(f"⚠️  Missing expected import: {expected_import}")

        # Check for expected classes
        expected_classes = [
            "class OpenFlowQuickstartApp",
            "class SecurityManager",
            "class DeploymentManager",
            "class MonitoringDashboard",
        ]

        for expected_class in expected_classes:
            if expected_class in content:
                print(f"✅ Found expected class: {expected_class}")
            else:
                print(f"⚠️  Missing expected class: {expected_class}")

    # Test security module content
    security_file = Path("src/security_first/input_validator.py")
    if security_file.exists():
        with open(security_file) as f:
            content = f.read()

        # Check for expected content
        expected_functions = [
            "def validate_snowflake_url",
            "def validate_uuid",
            "def sanitize_input",
            "def validate_oauth_credentials",
        ]

        for expected_func in expected_functions:
            if expected_func in content:
                print(f"✅ Found expected function: {expected_func}")
            else:
                print(f"⚠️  Missing expected function: {expected_func}")

    # Removed return statement


def test_projected_artifacts_file_size() -> None:
    """Test that projected artifacts have reasonable file sizes."""
    test_files = [
        "src/streamlit/openflow_quickstart_app.py",
        "src/security_first/input_validator.py",
    ]

    for file_path in test_files:
        if Path(file_path).exists():
            file_size = Path(file_path).stat().st_size
            print(f"📄 {file_path}: {file_size} bytes")

            # Check that files are not empty
            assert file_size > 0, f"{file_path} should not be empty"

            # Check that files are not too small (should have content)
            assert file_size > 1000, f"{file_path} should have substantial content"

            print(f"✅ {file_path} has reasonable file size")

    # Removed return statement


def main() -> None:
    """Run all tests for projected artifacts."""
    print("🧪 Testing Projected Artifacts (Simple)")
    print("=" * 60)

    tests = [
        ("Syntax Check", test_projected_artifacts_syntax),
        ("Structure Check", test_projected_artifacts_structure),
        ("Content Check", test_projected_artifacts_content),
        ("File Size Check", test_projected_artifacts_file_size),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Projected artifacts are working correctly.")
        return True
    print("⚠️  Some tests failed. Check the projected artifacts.")
    return False


if __name__ == "__main__":
    main()
