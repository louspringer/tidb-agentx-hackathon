#!/usr/bin/env python3
"""
Test Python Quality Enforcement Rule
Validate that Python files pass quality checks
"""

import ast
from src.secure_shell_service.secure_executor import secure_execute
import logging
# import subprocess  # REMOVED - replaced with secure_execute
import sys
from pathlib import Path
from typing import List, Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("quality_enforcement_test.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def _test_black_formatting(file_path: str) -> bool:
    """Test if a file passes Black formatting"""
    try:
        logger.info(f"Testing Black formatting for {file_path}")
        result = secure_execute(
            ["uv", "run", "black", "--check", "--quiet", file_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        success = result.returncode == 0
        logger.info(
            f"Black formatting for {file_path}: {'PASS' if success else 'FAIL'}"
        )
        return success
    except subprocess.TimeoutExpired:
        logger.error(f"Black formatting timeout for {file_path}")
        return False
    except Exception as e:
        logger.error(f"Error running black on {file_path}: {e}")
        return False


def _test_flake8_linting(file_path: str) -> bool:
    """Test if a file passes Flake8 linting"""
    try:
        logger.info(f"Testing Flake8 linting for {file_path}")
        result = secure_execute(
            ["uv", "run", "flake8", "--select=F401,E302,E305,W291,W292", file_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        success = result.returncode == 0
        logger.info(f"Flake8 linting for {file_path}: {'PASS' if success else 'FAIL'}")
        return success
    except subprocess.TimeoutExpired:
        logger.error(f"Flake8 linting timeout for {file_path}")
        return False
    except Exception as e:
        logger.error(f"Error running flake8 on {file_path}: {e}")
        return False


def _test_ast_parsing(file_path: str) -> bool:
    """Test if a file passes AST parsing"""
    try:
        logger.info(f"Testing AST parsing for {file_path}")
        with open(file_path, "r") as f:
            content = f.read()
        ast.parse(content)
        logger.info(f"AST parsing for {file_path}: PASS")
        return True
    except SyntaxError as e:
        logger.error(f"Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {e}")
        return False


def find_reasonable_python_files() -> List[str]:
    """Find reasonable Python files for testing - focus on core functionality"""
    # Define specific files that should be tested
    core_files = [
        "src/streamlit/openflow_quickstart_app.py",
        "src/artifact_forge/agents/artifact_detector.py",
        "src/artifact_forge/agents/artifact_parser.py",
        "tests/test_basic_validation_simple.py",
        "tests/test_type_safety.py",
        "scripts/mdc-linter.py",
    ]

    # Only test files that actually exist and are reasonable size
    existing_files = []
    for file_path in core_files:
        if Path(file_path).exists():
            # Check file size - exclude massive files
            try:
                with open(file_path, "r") as f:
                    line_count = sum(1 for _ in f)
                if line_count <= 500:  # Only test files with reasonable size
                    existing_files.append(file_path)
                else:
                    logger.warning(
                        f"Skipping {file_path} - too large ({line_count} lines)"
                    )
            except Exception as e:
                logger.warning(f"Could not check {file_path}: {e}")
        else:
            logger.warning(f"Test file not found: {file_path}")

    logger.info(f"Found {len(existing_files)} reasonable core files to test")
    return existing_files


def test_python_quality_enforcement() -> None:
    """Test that core Python files pass quality enforcement"""
    logger.info("🧪 **PYTHON QUALITY ENFORCEMENT TEST**")
    logger.info("=" * 50)

    python_files = find_reasonable_python_files()
    if not python_files:
        logger.error("❌ No core Python files found to test")
        assert False, "No core Python files found to test"

    logger.info(f"Testing {len(python_files)} core Python files")

    results: Dict[str, List[str]] = {
        "black": [],
        "flake8": [],
        "ast_parse": [],
    }

    for file_path in python_files:
        logger.info(f"\n📝 Testing {file_path}...")

        # Test Black formatting
        if _test_black_formatting(file_path):
            results["black"].append(file_path)
        else:
            logger.error("  ❌ Black formatting failed")

        # Test Flake8 linting
        if _test_flake8_linting(file_path):
            results["flake8"].append(file_path)
        else:
            logger.error("  ❌ Flake8 linting failed")

        # Test AST parsing
        if _test_ast_parsing(file_path):
            results["ast_parse"].append(file_path)
        else:
            logger.error("  ❌ AST parsing failed")

    # Print results
    logger.info("\n📊 **QUALITY ENFORCEMENT RESULTS:**")
    logger.info(f"Total files tested: {len(python_files)}")
    logger.info(f"Black formatting: {len(results['black'])}/{len(python_files)}")
    logger.info(f"Flake8 linting: {len(results['flake8'])}/{len(python_files)}")
    logger.info(f"AST parsing: {len(results['ast_parse'])}/{len(python_files)}")

    # Check if all files pass all tests
    all_passed = all(len(result) == len(python_files) for result in results.values())

    if all_passed:
        logger.info("\n🎉 **ALL CORE PYTHON FILES PASS QUALITY ENFORCEMENT!**")
    else:
        logger.warning("\n⚠️ **SOME FILES FAILED QUALITY ENFORCEMENT**")

        # Show which files failed which tests
        for test_name, passed_files in results.items():
            failed_files = set(python_files) - set(passed_files)
            if failed_files:
                logger.error(f"\n❌ {test_name.upper()} failed for:")
                for failed_file in failed_files:
                    logger.error(f"  - {failed_file}")

    assert all_passed, "Some Python files failed quality enforcement"


def test_zero_linter_errors() -> None:
    """Test that core files have zero linter errors"""
    logger.info("🧪 **ZERO LINTER ERRORS TEST**")
    logger.info("=" * 50)

    python_files = find_reasonable_python_files()
    if not python_files:
        logger.error("❌ No core Python files found to test")
        assert False, "No core Python files found to test"

    total_errors = 0
    for file_path in python_files:
        try:
            # Run flake8 with specific error codes using uv
            result = secure_execute(
                ["uv", "run", "flake8", "--select=F401,E302,E305,W291,W292", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                error_count = len(result.stdout.splitlines())
                total_errors += error_count
                logger.error(f"❌ {file_path}: {error_count} linter errors")
                logger.error(f"   Errors: {result.stdout}")
            else:
                logger.info(f"✅ {file_path}: No linter errors")

        except Exception as e:
            logger.error(f"❌ Error testing {file_path}: {e}")
            total_errors += 1

    if total_errors == 0:
        logger.info("🎉 **ALL CORE FILES HAVE ZERO LINTER ERRORS!**")
    else:
        logger.error(f"❌ **TOTAL LINTER ERRORS: {total_errors}**")

    assert total_errors == 0, f"Found {total_errors} linter errors"


def test_ast_parsing_compliance() -> None:
    """Test that core files pass AST parsing"""
    logger.info("🧪 **AST PARSING COMPLIANCE TEST**")
    logger.info("=" * 50)

    python_files = find_reasonable_python_files()
    if not python_files:
        logger.error("❌ No core Python files found to test")
        assert False, "No core Python files found to test"

    failed_files = []
    for file_path in python_files:
        try:
            with open(file_path, "r") as f:
                content = f.read()
            ast.parse(content)
            logger.info(f"✅ {file_path}: AST parsing successful")
        except Exception as e:
            logger.error(f"❌ {file_path}: AST parsing failed - {e}")
            failed_files.append(file_path)

    if not failed_files:
        logger.info("🎉 **ALL CORE FILES PASS AST PARSING!**")
    else:
        logger.error(f"❌ **AST PARSING FAILED FOR {len(failed_files)} FILES**")

    assert not failed_files, f"AST parsing failed for {len(failed_files)} files"


def main() -> bool:
    """Main test function"""
    logger.info("🚀 Starting Python Quality Enforcement Tests")
    logger.info("=" * 60)

    tests = [
        ("Python Quality Enforcement", test_python_quality_enforcement),
        ("Zero Linter Errors", test_zero_linter_errors),
        ("AST Parsing Compliance", test_ast_parsing_compliance),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 40)

        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")

    logger.info("\n" + "=" * 60)
    logger.info(f"📊 **FINAL RESULTS: {passed}/{total} tests passed**")

    if passed == total:
        logger.info("🎉 **ALL PYTHON QUALITY ENFORCEMENT TESTS PASSED!**")
        return True
    else:
        logger.error("❌ **SOME PYTHON QUALITY ENFORCEMENT TESTS FAILED**")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
