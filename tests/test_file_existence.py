#!/usr/bin/env python3
"""
File Existence and Structure Validation Tests
Tests that all expected files exist and are properly structured
"""

from pathlib import Path
from typing import Any


class FileExistenceValidator:
    """Validates that expected files exist and are properly structured"""

    def __init__(self: Any) -> None:
        self.project_root = Path(__file__).parent.parent

    def test_rate_limiting_module_exists(self: Any) -> None:
        """Test that rate_limiting.py exists and is properly structured"""
        rate_limit_file: Any = (
            self.project_root / "src" / "security_first" / "rate_limiting.py"
        )

        # Check file exists
        assert (
            rate_limit_file.exists()
        ), f"Rate limiting module not found: {rate_limit_file}"

        # Check file is readable
        with open(rate_limit_file, "r") as f:
            content: Any = f.read()

        # Check it contains the RateLimiting class
        assert (
            "class RateLimiting" in content
        ), "RateLimiting class not found in rate_limiting.py"

        # Check it has the required methods
        required_methods: Any = [
            "check_rate_limit",
            "get_remaining_requests",
            "reset_rate_limit",
            "get_rate_limit_info",
        ]

        for method in required_methods:
            assert (
                f"def {method}" in content
            ), f"Method {method} not found in rate_limiting.py"

        print("✅ Rate limiting module exists and is properly structured")
        return True

    def test_https_enforcement_module_exists(self: Any) -> None:
        """Test that https_enforcement.py exists and is properly structured"""
        https_file: Any = (
            self.project_root / "src" / "security_first" / "https_enforcement.py"
        )

        # Check file exists
        assert https_file.exists(), f"HTTPS enforcement module not found: {https_file}"

        # Check file is readable
        with open(https_file, "r") as f:
            content: Any = f.read()

        # Check it contains the HTTPSEnforcement class
        assert (
            "class HTTPSEnforcement" in content
        ), "HTTPSEnforcement class not found in https_enforcement.py"

        # Check it has the required methods
        required_methods: Any = [
            "_create_ssl_context",
            "validate_https_url",
            "enforce_https_redirect",
            "validate_ssl_certificate",
        ]

        for method in required_methods:
            assert (
                f"def {method}" in content
            ), f"Method {method} not found in https_enforcement.py"

        print("✅ HTTPS enforcement module exists and is properly structured")
        return True

    def test_csrf_protection_exists(self: Any) -> None:
        """Test that CSRF protection is implemented"""
        https_file: Any = (
            self.project_root / "src" / "security_first" / "https_enforcement.py"
        )

        # Check file exists
        assert https_file.exists(), f"HTTPS enforcement module not found: {https_file}"

        # Check file is readable
        with open(https_file, "r") as f:
            content: Any = f.read()

        # Check it contains the CSRFProtection class
        assert (
            "class CSRFProtection" in content
        ), "CSRFProtection class not found in https_enforcement.py"

        # Check it has the required methods
        required_methods: Any = [
            "generate_csrf_token",
            "validate_csrf_token",
            "enforce_csrf_protection",
        ]

        for method in required_methods:
            assert (
                f"def {method}" in content
            ), f"Method {method} not found in https_enforcement.py"

        print("✅ CSRF protection module exists and is properly structured")
        return True

    def test_security_manager_exists(self: Any) -> None:
        """Test that security_manager.py exists and is properly structured"""
        security_file: Any = (
            self.project_root / "src" / "security_first" / "security_manager.py"
        )

        # Check file exists
        assert security_file.exists(), f"Security manager not found: {security_file}"

        # Check file is readable
        with open(security_file, "r") as f:
            content: Any = f.read()

        # Check it contains the SecurityManager class
        assert (
            "class SecurityManager" in content
        ), "SecurityManager class not found in security_manager.py"

        # Check it has the required methods
        required_methods: Any = [
            "validate_security_config",
            "enforce_security_policies",
            "audit_security_events",
        ]

        for method in required_methods:
            assert (
                f"def {method}" in content
            ), f"Method {method} not found in security_manager.py"

        print("✅ Security manager exists and is properly structured")
        return True

    def test_input_validator_exists(self: Any) -> None:
        """Test that input_validator.py exists and is properly structured"""
        validator_file: Any = (
            self.project_root / "src" / "security_first" / "input_validator.py"
        )

        # Check file exists
        assert validator_file.exists(), f"Input validator not found: {validator_file}"

        # Check file is readable
        with open(validator_file, "r") as f:
            content: Any = f.read()

        # Check it contains the InputValidator class
        assert (
            "class InputValidator" in content
        ), "InputValidator class not found in input_validator.py"

        # Check it has the required methods
        required_methods: Any = [
            "validate_input",
            "sanitize_input",
            "validate_file_upload",
        ]

        for method in required_methods:
            assert (
                f"def {method}" in content
            ), f"Method {method} not found in input_validator.py"

        print("✅ Input validator exists and is properly structured")
        return True


def test_all_required_files_exist() -> None:
    """Test that all required security files exist and are properly structured"""
    validator = FileExistenceValidator()

    # Test all security modules
    validator.test_rate_limiting_module_exists()
    validator.test_https_enforcement_module_exists()
    validator.test_csrf_protection_exists()
    validator.test_security_manager_exists()
    validator.test_input_validator_exists()

    print("✅ All required security files exist and are properly structured")


def test_project_structure() -> None:
    """Test that the project has the expected directory structure"""
    project_root = Path(__file__).parent.parent

    # Check for required directories
    required_dirs = [
        "src",
        "tests",
        "docs",
        ".cursor",
        ".cursor/rules",
    ]

    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        assert dir_path.exists(), f"Required directory not found: {dir_path}"
        assert dir_path.is_dir(), f"Path is not a directory: {dir_path}"

    # Check for required files
    required_files = [
        "README.md",
        "pyproject.toml",
        # requirements.txt removed - this is a UV project
    ]

    for file_name in required_files:
        file_path = project_root / file_name
        assert file_path.exists(), f"Required file not found: {file_path}"
        assert file_path.is_file(), f"Path is not a file: {file_path}"

    print("✅ Project structure is correct")


def test_security_first_directory() -> None:
    """Test that the security_first directory exists and contains expected modules"""
    project_root = Path(__file__).parent.parent
    security_dir = project_root / "src" / "security_first"

    assert security_dir.exists(), f"Security directory not found: {security_dir}"
    assert security_dir.is_dir(), f"Path is not a directory: {security_dir}"

    # Check for expected security modules
    expected_modules = [
        "rate_limiting.py",
        "https_enforcement.py",
        "security_manager.py",
        "input_validator.py",
    ]

    for module in expected_modules:
        module_path = security_dir / module
        assert module_path.exists(), f"Security module not found: {module_path}"
        assert module_path.is_file(), f"Path is not a file: {module_path}"

    print("✅ Security first directory structure is correct")
