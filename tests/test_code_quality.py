#!/usr/bin/env python3
"""
Code Quality Tests
Tests code quality using projected artifact patterns
"""

import ast
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_python_syntax() -> None:
    """Test that Python files have valid syntax"""
    test_files = [
        "src/streamlit/openflow_quickstart_app.py",
        "src/security_first/input_validator.py",
        "src/mdc_generator/mdc_model.py",
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
                error_msg = f"Syntax error in {file_path}: {e}"
                raise AssertionError(error_msg)
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                error_msg = f"Error reading {file_path}: {e}"
                raise AssertionError(error_msg)
        else:
            print(f"⚠️  File not found: {file_path}")


def test_code_structure() -> None:
    """Test that code has expected structure"""
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


def run_code_quality_tests() -> None:
    """Run all code quality tests"""
    print("🚀 Running code quality tests...")

    tests = [
        test_python_syntax,
        test_code_structure,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test {test.__name__} failed: {e}")

    if passed == total:
        print("🎉 All code quality tests passed!")
    else:
        print(f"⚠️  {passed}/{total} tests passed")


if __name__ == "__main__":
    run_code_quality_tests()
