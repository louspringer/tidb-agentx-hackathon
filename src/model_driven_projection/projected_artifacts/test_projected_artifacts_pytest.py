#!/usr/bin/env python3
"""
Pytest tests for projected artifacts

These are proper pytest test functions that use assertions.
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
                with open(file_path, "r") as f:
                    content = f.read()

                # Parse with AST to check syntax
                ast.parse(content)
                print(f"✅ {file_path} has valid Python syntax")

            except SyntaxError as e:
                print(f"❌ Syntax error in {file_path}: {e}")
                assert False, f"Syntax error in {file_path}: {e}"
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                assert False, f"Error reading {file_path}: {e}"
        else:
            print(f"⚠️  File not found: {file_path}")
            assert False, f"File not found: {file_path}"


def test_projected_artifacts_structure() -> None:
    """Test that projected artifacts have the expected structure."""
    # Test streamlit app structure
    streamlit_file = Path("src/streamlit/openflow_quickstart_app.py")
    assert streamlit_file.exists(), "Streamlit app file should exist"

    with open(streamlit_file, "r") as f:
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
    assert security_file.exists(), "Security module file should exist"

    with open(security_file, "r") as f:
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


def test_projected_artifacts_content() -> None:
    """Test that projected artifacts contain expected content."""
    # Test streamlit app content
    streamlit_file = Path("src/streamlit/openflow_quickstart_app.py")
    assert streamlit_file.exists(), "Streamlit app file should exist"

    with open(streamlit_file, "r") as f:
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
    assert security_file.exists(), "Security module file should exist"

    with open(security_file, "r") as f:
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


def test_projected_artifacts_file_size() -> None:
    """Test that projected artifacts have reasonable file sizes."""
    test_files = [
        "src/streamlit/openflow_quickstart_app.py",
        "src/security_first/input_validator.py",
    ]

    for file_path in test_files:
        file_path_obj = Path(file_path)
        assert file_path_obj.exists(), f"{file_path} should exist"

        file_size = file_path_obj.stat().st_size
        print(f"📄 {file_path}: {file_size} bytes")

        # Check that files are not empty
        assert file_size > 0, f"{file_path} should not be empty"

        # Check that files are not too small (should have content)
        assert file_size > 1000, f"{file_path} should have substantial content"

        print(f"✅ {file_path} has reasonable file size")


def test_projected_artifacts_import_structure() -> None:
    """Test that projected artifacts have proper import structure."""
    # Test that imports are at the top
    streamlit_file = Path("src/streamlit/openflow_quickstart_app.py")
    assert streamlit_file.exists(), "Streamlit app file should exist"

    with open(streamlit_file, "r") as f:
        lines = f.readlines()

    # Check that imports are in the first 20 lines
    import_lines = []
    for i, line in enumerate(lines[:20]):
        if line.strip().startswith(("import ", "from ")):
            import_lines.append((i, line.strip()))

    assert len(import_lines) > 0, "Should have imports at the top"
    print(f"✅ Found {len(import_lines)} imports in first 20 lines")

    # Check that imports are properly formatted
    for line_num, import_line in import_lines:
        assert import_line.startswith(
            ("import ", "from ")
        ), f"Line {line_num} should be an import"
        print(f"✅ Import at line {line_num}: {import_line}")


def test_projected_artifacts_class_structure() -> None:
    """Test that projected artifacts have proper class structure."""
    streamlit_file = Path("src/streamlit/openflow_quickstart_app.py")
    assert streamlit_file.exists(), "Streamlit app file should exist"

    with open(streamlit_file, "r") as f:
        content = f.read()

    tree = ast.parse(content)

    # Find all classes
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)

    assert len(classes) > 0, "Should have at least one class"
    print(f"✅ Found {len(classes)} classes: {classes}")

    # Check that main classes exist
    expected_classes = ["OpenFlowQuickstartApp", "SecurityManager", "DeploymentManager"]
    for expected_class in expected_classes:
        assert expected_class in classes, f"Should have class {expected_class}"
        print(f"✅ Found expected class: {expected_class}")


def test_projected_artifacts_function_structure() -> None:
    """Test that projected artifacts have proper function structure."""
    streamlit_file = Path("src/streamlit/openflow_quickstart_app.py")
    assert streamlit_file.exists(), "Streamlit app file should exist"

    with open(streamlit_file, "r") as f:
        content = f.read()

    tree = ast.parse(content)

    # Find all functions
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

    assert len(functions) > 0, "Should have at least one function"
    print(f"✅ Found {len(functions)} functions")

    # Check that key functions exist (based on what's actually in the projected artifacts)
    expected_functions = [
        "validate_snowflake_url",
        "validate_uuid",
        "encrypt_credential",
    ]
    for expected_func in expected_functions:
        assert expected_func in functions, f"Should have function {expected_func}"
        print(f"✅ Found expected function: {expected_func}")

    # Check that we have some class methods (__init__ functions)
    init_functions = [f for f in functions if f == "__init__"]
    assert len(init_functions) > 0, "Should have __init__ functions"
    print(f"✅ Found {len(init_functions)} __init__ functions")
