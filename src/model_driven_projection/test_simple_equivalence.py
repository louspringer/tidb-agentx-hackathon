#!/usr/bin/env python3
"""
Simple functional equivalence test without external dependencies
"""

import ast
from src.secure_shell_service.secure_executor import secure_execute


def test_syntax_equivalence() -> None:
    """Test if projected artifacts have the same syntax structure."""
    print("🔍 Testing syntax equivalence...")

    try:
        # Parse both files with AST
        # Parse original
        with open("../../src/streamlit/openflow_quickstart_app.py") as f:
            original_content = f.read()
        original_tree = ast.parse(original_content)

        # Parse projected
        with open("final_projection.py") as f:
            projected_content = f.read()
        projected_tree = ast.parse(projected_content)

        # Count elements
        original_functions = len(
            [n for n in ast.walk(original_tree) if isinstance(n, ast.FunctionDef)],
        )
        projected_functions = len(
            [n for n in ast.walk(projected_tree) if isinstance(n, ast.FunctionDef)],
        )

        original_classes = len(
            [n for n in ast.walk(original_tree) if isinstance(n, ast.ClassDef)],
        )
        projected_classes = len(
            [n for n in ast.walk(projected_tree) if isinstance(n, ast.ClassDef)],
        )

        original_imports = len(
            [
                n
                for n in ast.walk(original_tree)
                if isinstance(n, (ast.Import, ast.ImportFrom))
            ],
        )
        projected_imports = len(
            [
                n
                for n in ast.walk(projected_tree)
                if isinstance(n, (ast.Import, ast.ImportFrom))
            ],
        )

        print(
            f"📊 Function count: Original {original_functions} vs Projected {projected_functions}",
        )
        print(
            f"📊 Class count: Original {original_classes} vs Projected {projected_classes}",
        )
        print(
            f"📊 Import count: Original {original_imports} vs Projected {projected_imports}",
        )

        if (
            original_functions == projected_functions
            and original_classes == projected_classes
            and projected_imports >= original_imports
        ):
            print("✅ Projected artifacts: Syntax structure matches original")
            # Removed return statement
        else:
            print("❌ Projected artifacts: Syntax structure differs from original")
            # Removed return statement

    except Exception as e:
        print(f"❌ Error testing syntax equivalence: {e}")
        # Removed return statement


def test_content_equivalence() -> None:
    """Test if projected artifacts contain the same key content."""
    print("\n🔍 Testing content equivalence...")

    try:
        # Read both files
        with open("../../src/streamlit/openflow_quickstart_app.py") as f:
            f.read()

        with open("final_projection.py") as f:
            projected_content = f.read()

        # Check for key classes
        key_classes = [
            "OpenFlowQuickstartApp",
            "SecurityManager",
            "DeploymentManager",
            "MonitoringDashboard",
        ]
        missing_classes = []

        for class_name in key_classes:
            if class_name not in projected_content:
                missing_classes.append(class_name)

        if missing_classes:
            print(f"❌ Projected artifacts: Missing classes - {missing_classes}")
            # Removed return statement
        else:
            print("✅ Projected artifacts: All key classes present")

        # Check for key functions
        key_functions = [
            "main",
            "encrypt_credential",
            "decrypt_credential",
            "create_session_token",
        ]
        missing_functions = []

        for func_name in key_functions:
            if f"def {func_name}" not in projected_content:
                missing_functions.append(func_name)

        if missing_functions:
            print(f"❌ Projected artifacts: Missing functions - {missing_functions}")
            # Removed return statement
        else:
            print("✅ Projected artifacts: All key functions present")

        # Check for key imports
        key_imports = ["streamlit", "plotly", "pydantic", "cryptography"]
        missing_imports = []

        for import_name in key_imports:
            if import_name not in projected_content:
                missing_imports.append(import_name)

        if missing_imports:
            print(f"❌ Projected artifacts: Missing imports - {missing_imports}")
            # Removed return statement
        else:
            print("✅ Projected artifacts: All key imports present")

        # Removed return statement

    except Exception as e:
        print(f"❌ Error testing content equivalence: {e}")
        # Removed return statement


def test_structure_equivalence() -> None:
    """Test if projected artifacts have the same structural elements."""
    print("\n🔍 Testing structure equivalence...")

    try:
        # Parse both files
        with open("../../src/streamlit/openflow_quickstart_app.py") as f:
            original_content = f.read()
        original_tree = ast.parse(original_content)

        with open("final_projection.py") as f:
            projected_content = f.read()
        projected_tree = ast.parse(projected_content)

        # Check for specific structural elements
        original_class_names = [
            node.name
            for node in ast.walk(original_tree)
            if isinstance(node, ast.ClassDef)
        ]
        projected_class_names = [
            node.name
            for node in ast.walk(projected_tree)
            if isinstance(node, ast.ClassDef)
        ]

        print(f"📊 Original classes: {original_class_names}")
        print(f"📊 Projected classes: {projected_class_names}")

        # Check if all original classes are in projected
        missing_classes = set(original_class_names) - set(projected_class_names)
        if missing_classes:
            print(f"❌ Projected artifacts: Missing classes - {missing_classes}")
            # Removed return statement
        else:
            print("✅ Projected artifacts: All original classes present")

        # Check for constants
        if "SECURITY_CONFIG" in projected_content:
            print("✅ Projected artifacts: SECURITY_CONFIG present")
        else:
            print("❌ Projected artifacts: SECURITY_CONFIG missing")
            # Removed return statement

        if "AWS_CONFIG" in projected_content:
            print("✅ Projected artifacts: AWS_CONFIG present")
        else:
            print("❌ Projected artifacts: AWS_CONFIG missing")
            # Removed return statement

        # Removed return statement

    except Exception as e:
        print(f"❌ Error testing structure equivalence: {e}")
        # Removed return statement


def test_original_tests() -> None:
    """Test if original tests still pass."""
    print("\n🔍 Testing original tests...")

    try:
# import subprocess  # REMOVED - replaced with secure_execute

        # Run a simple test that doesn't require external dependencies
        result = secure_execute(
            [
                "python",
                "-m",
                "pytest",
                "../../tests/test_basic_validation.py::TestSecurityManager::test_credential_encryption_decryption",
                "-v",
                "--tb=short",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ Original tests: Security manager test passed")
            # Removed return statement
        else:
            print("❌ Original tests: Security manager test failed")
            print(result.stdout)
            print(result.stderr)
            # Removed return statement

    except Exception as e:
        print(f"❌ Error testing original tests: {e}")
        # Removed return statement


def main() -> None:
    """Run all equivalence tests."""
    print("🧪 SIMPLE FUNCTIONAL EQUIVALENCE TESTING")
    print("=" * 60)

    tests = [
        ("Syntax Equivalence", test_syntax_equivalence),
        ("Content Equivalence", test_content_equivalence),
        ("Structure Equivalence", test_structure_equivalence),
        ("Original Tests", test_original_tests),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False

    # Summary
    print("\n📊 TEST RESULTS SUMMARY:")
    print("=" * 40)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Functional equivalence achieved!")
    else:
        print("⚠️ Some tests failed. Check the projected artifacts.")


if __name__ == "__main__":
    main()
