#!/usr/bin/env python3
"""
Security Model Tests - Prevention over Detection
"""

import re
from pathlib import Path


def test_no_hardcoded_credentials() -> None:
    """Test that no real credentials exist in code"""
    # Check for common credential patterns
    patterns = [
        r"sk-[0-9a-zA-Z]{48}",  # OpenAI keys
        r"AKIA[0-9A-Z]{16}",  # AWS keys
        r"ghp_[0-9a-zA-Z]{36}",  # GitHub tokens
    ]

    # UUIDs are context-dependent - only flag if they look like real credentials
    # and aren't in example/placeholder contexts

    # Exclude legitimate files
    excludes = [
        "test_security_model.py",
        "scripts/security-check.sh",
        ".pre-commit-config.yaml",
    ]

    violations = []
    for file_path in Path(".").rglob("*"):
        if file_path.is_file() and file_path.name not in excludes:
            try:
                content = file_path.read_text()
                for pattern in patterns:
                    if re.search(pattern, content):
                        violations.append(f"{file_path}: {pattern}")
            except:
                continue

    assert not violations, f"Found potential credentials: {violations}"


def test_config_uses_placeholders() -> None:
    """Test that config files use placeholders"""
    config_files = ["config.env.example", "models/Openflow-Playground.yaml"]

    for config_file in config_files:
        if Path(config_file).exists():
            content = Path(config_file).read_text()
            # Check that it uses placeholder patterns
            assert (
                "YOUR_" in content or "${" in content
            ), f"{config_file} should use placeholders"


def test_environment_validation() -> None:
    """Test that required environment variables are documented"""
    required_vars = [
        "SNOWFLAKE_ACCOUNT_URL",
        "SNOWFLAKE_ORGANIZATION",
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_OAUTH_CLIENT_ID",
        "SNOWFLAKE_OAUTH_CLIENT_SECRET",
    ]

    # Check that these are documented in example config
    if Path("config.env.example").exists():
        content = Path("config.env.example").read_text()
        for var in required_vars:
            assert var in content, f"Missing {var} in config example"


def test_deployment_parameterized() -> None:
    """Test that deployment uses parameters"""
    if Path("deploy.sh").exists():
        content = Path("deploy.sh").read_text()
        assert "ParameterKey=" in content, "Deployment should use parameters"
        assert "ParameterValue=" in content, "Deployment should use parameters"


if __name__ == "__main__":
    print("Running Security Model Tests...")
    test_no_hardcoded_credentials()
    test_config_uses_placeholders()
    test_environment_validation()
    test_deployment_parameterized()
    print("✅ All security model tests passed!")
