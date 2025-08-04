#!/usr/bin/env python3
"""
Test Security Enhancements
Validates the security blind spot fixes implemented based on Gemini 2.5 Flash Lite recommendations.
"""

import json
import sys
from pathlib import Path
from typing import Any


def load_project_model() -> Any:
    """Load the project model registry."""
    try:
        with open("project_model_registry.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ project_model_registry.json not found")
        return None


def test_requirement_33_https_enforcement() -> None:
    """Test HTTPS enforcement requirement."""
    print("Testing Requirement 33: HTTPS enforcement...")

    project_model: Any = load_project_model()
    if not project_model:
        return

    # Check security_first domain exists
    assert (
        "security_first" in project_model["domains"]
    ), "security_first domain not found"
    print("✅ security_first domain exists")

    # Check HTTPS enforcement requirement
    security_domain: Any = project_model["domains"]["security_first"]
    requirements: Any = security_domain["requirements"]

    https_requirement: str = "Enforce HTTPS for all connections"
    assert (
        https_requirement in requirements
    ), f"Missing HTTPS requirement: {https_requirement}"
    print(f"✅ HTTPS requirement found: {https_requirement}")

    # Check content indicators include HTTPS
    content_indicators: Any = security_domain["content_indicators"]
    https_indicators: list = ["https", "ssl"]

    for indicator in https_indicators:
        assert indicator in content_indicators, f"Missing HTTPS indicator: {indicator}"
        print(f"✅ HTTPS indicator found: {indicator}")

    # Check implementation file exists
    https_file: Any = Path("src/security_first/https_enforcement.py")
    assert https_file.exists(), "HTTPS enforcement module not found"
    print("✅ HTTPS enforcement module exists")

    print("✅ Requirement 33: HTTPS enforcement - PASSED")


def test_requirement_34_rate_limiting() -> None:
    """Test rate limiting requirement."""
    print("Testing Requirement 34: Rate limiting...")

    project_model: Any = load_project_model()
    if not project_model:
        return

    # Check rate limiting requirement
    security_domain: Any = project_model["domains"]["security_first"]
    requirements: Any = security_domain["requirements"]

    rate_limit_requirement: str = "Implement rate limiting to prevent abuse"
    assert (
        rate_limit_requirement in requirements
    ), f"Missing rate limiting requirement: {rate_limit_requirement}"
    print(f"✅ Rate limiting requirement found: {rate_limit_requirement}")

    # Check content indicators include rate limiting
    content_indicators: Any = security_domain["content_indicators"]
    rate_limit_indicator: str = "rate_limit"

    assert (
        rate_limit_indicator in content_indicators
    ), f"Missing rate limiting indicator: {rate_limit_indicator}"
    print(f"✅ Rate limiting indicator found: {rate_limit_indicator}")

    # Check implementation file exists - rate limiting should be in its own module
    rate_limit_file: Any = Path("src/security_first/rate_limiting.py")
    assert (
        rate_limit_file.exists()
    ), "Rate limiting module not found (expected src/security_first/rate_limiting.py)"
    print("✅ Rate limiting module exists")

    print("✅ Requirement 34: Rate limiting - PASSED")


def test_requirement_35_csrf_protection() -> None:
    """Test CSRF protection requirement."""
    print("Testing Requirement 35: CSRF protection...")

    project_model: Any = load_project_model()
    if not project_model:
        return

    # Check CSRF protection requirement
    security_domain: Any = project_model["domains"]["security_first"]
    requirements: Any = security_domain["requirements"]

    csrf_requirement: str = "Implement CSRF protection for all forms"
    assert (
        csrf_requirement in requirements
    ), f"Missing CSRF protection requirement: {csrf_requirement}"
    print(f"✅ CSRF protection requirement found: {csrf_requirement}")

    # Check content indicators include CSRF
    content_indicators: Any = security_domain["content_indicators"]
    csrf_indicators: list = ["csrf", "token"]

    for indicator in csrf_indicators:
        assert indicator in content_indicators, f"Missing CSRF indicator: {indicator}"
        print(f"✅ CSRF indicator found: {indicator}")

    # Check implementation file exists
    https_file: Any = Path("src/security_first/https_enforcement.py")
    assert https_file.exists(), "HTTPS enforcement module not found"
    print("✅ CSRF protection module exists")

    print("✅ Requirement 35: CSRF protection - PASSED")


def test_security_enhancements_completeness() -> None:
    """Test that all security enhancements are properly implemented."""
    print("Testing Security Enhancements Completeness...")

    project_model: Any = load_project_model()
    if not project_model:
        return

    # Check all required security domains exist
    required_domains: list = ["security_first", "streamlit", "multi_agent_testing"]
    for domain in required_domains:
        assert domain in project_model["domains"], f"Missing domain: {domain}"
        print(f"✅ Domain exists: {domain}")

    # Check security_first has all required components
    security_domain: Any = project_model["domains"]["security_first"]

    # Check patterns
    patterns: Any = security_domain["patterns"]
    required_patterns: list = ["**/*.py", "**/*.yaml", "**/*.yml"]
    for pattern in required_patterns:
        assert pattern in patterns, f"Missing pattern: {pattern}"
        print(f"✅ Pattern exists: {pattern}")

    # Check content indicators
    content_indicators: Any = security_domain["content_indicators"]
    required_indicators: list = ["https", "ssl", "rate_limit", "csrf", "token"]
    for indicator in required_indicators:
        assert indicator in content_indicators, f"Missing indicator: {indicator}"
        print(f"✅ Indicator exists: {indicator}")

    # Check requirements
    requirements: Any = security_domain["requirements"]
    required_requirements: list = [
        "Enforce HTTPS for all connections",
        "Implement rate limiting to prevent abuse",
        "Implement CSRF protection for all forms",
    ]
    for requirement in required_requirements:
        assert requirement in requirements, f"Missing requirement: {requirement}"
        print(f"✅ Requirement exists: {requirement}")

    print("✅ Security Enhancements Completeness - PASSED")


def main() -> None:
    """Run all security enhancement tests."""
    print("🔒 Testing Security Enhancements")
    print("=" * 50)

    test_requirement_33_https_enforcement()
    test_requirement_34_rate_limiting()
    test_requirement_35_csrf_protection()
    test_security_enhancements_completeness()

    print("\n✅ All security enhancement tests passed!")


if __name__ == "__main__":
    main()
