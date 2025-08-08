#!/usr/bin/env python3
"""
Test Ghostbusters integration with project model
"""

import json
from pathlib import Path


def test_ghostbusters_domain_in_model() -> None:
    """Test that Ghostbusters domain is properly configured in project model"""
    # Load project model
    with open("project_model_registry.json") as f:
        model_data = json.load(f)

    # Check that ghostbusters domain exists
    assert (
        "ghostbusters" in model_data["domains"]
    ), "Ghostbusters domain should exist in project model"

    ghostbusters_domain = model_data["domains"]["ghostbusters"]

    # Check required fields
    assert "patterns" in ghostbusters_domain, "Ghostbusters domain should have patterns"
    assert (
        "content_indicators" in ghostbusters_domain
    ), "Ghostbusters domain should have content_indicators"
    assert "linter" in ghostbusters_domain, "Ghostbusters domain should have linter"
    assert (
        "validator" in ghostbusters_domain
    ), "Ghostbusters domain should have validator"
    assert (
        "formatter" in ghostbusters_domain
    ), "Ghostbusters domain should have formatter"
    assert (
        "requirements" in ghostbusters_domain
    ), "Ghostbusters domain should have requirements"

    # Check patterns
    patterns = ghostbusters_domain["patterns"]
    assert (
        "src/ghostbusters/**/*.py" in patterns
    ), "Should include Ghostbusters source files"
    assert (
        "tests/test_ghostbusters*.py" in patterns
    ), "Should include Ghostbusters test files"
    assert "**/*ghostbusters*.py" in patterns, "Should include all Ghostbusters Python files"

    # Check content indicators
    content_indicators = ghostbusters_domain["content_indicators"]
    expected_indicators = [
        "delusion",
        "recovery",
        "agent",
        "validator",
        "orchestrator",
        "ghostbusters",
        "syntax_error",
        "indentation_error",
        "import_error",
        "type_error",
    ]
    for indicator in expected_indicators:
        assert (
            indicator in content_indicators
        ), f"Should include '{indicator}' in content indicators"

    # Check tools
    assert (
        ghostbusters_domain["linter"] == "flake8"
    ), "Should use flake8 as linter"
    assert (
        ghostbusters_domain["validator"] == "ast-parse"
    ), "Should use ast-parse as validator"
    assert (
        ghostbusters_domain["formatter"] == "black"
    ), "Should use black as formatter"

    # Check requirements
    requirements = ghostbusters_domain["requirements"]
    assert len(requirements) >= 7, "Should have at least 7 Ghostbusters requirements"

    expected_requirements = [
        "Use Ghostbusters for delusion detection and recovery",
        "Run Ghostbusters before linting to fix syntax issues",
        "Use Ghostbusters agents for domain-specific analysis",
        "Apply Ghostbusters recovery engines for automated fixes",
        "Integrate Ghostbusters with LangGraph/LangChain",
        "Use Ghostbusters for multi-agent orchestration",
        "Apply Ghostbusters for confidence scoring and validation",
    ]

    for requirement in expected_requirements:
        assert any(
            req.startswith(requirement.split()[0]) for req in requirements
        ), f"Should include requirement: {requirement}"


def test_ghostbusters_requirements_traceability() -> None:
    """Test that Ghostbusters requirements are properly traced"""
    # Load project model
    with open("project_model_registry.json") as f:
        model_data = json.load(f)

    # Check requirements traceability
    requirements_traceability = model_data["requirements_traceability"]

    # Find Ghostbusters requirements
    ghostbusters_requirements = [
        req for req in requirements_traceability if req.get("domain") == "ghostbusters"
    ]

    assert (
        len(ghostbusters_requirements) >= 7
    ), "Should have at least 7 Ghostbusters requirements in traceability"

    # Check for key requirements
    requirement_texts = [req["requirement"] for req in ghostbusters_requirements]

    expected_requirements = [
        "Use Ghostbusters for delusion detection and recovery",
        "Run Ghostbusters before linting to fix syntax issues",
        "Use Ghostbusters agents for domain-specific analysis",
        "Apply Ghostbusters recovery engines for automated fixes",
        "Integrate Ghostbusters with LangGraph/LangChain",
        "Use Ghostbusters for multi-agent orchestration",
        "Apply Ghostbusters for confidence scoring and validation",
    ]

    for expected_req in expected_requirements:
        assert any(
            expected_req in req_text for req_text in requirement_texts
        ), f"Should include requirement: {expected_req}"


def test_ghostbusters_rule_exists() -> None:
    """Test that Ghostbusters rule file exists and is properly configured"""
    rule_file = Path(".cursor/rules/ghostbusters.mdc")
    assert rule_file.exists(), "Ghostbusters rule file should exist"

    # Check that the file has content
    content = rule_file.read_text()
    assert len(content) > 0, "Ghostbusters rule file should have content"

    # Check for key sections
    assert "---" in content, "Should have YAML frontmatter"
    assert "description:" in content, "Should have description in frontmatter"
    assert "globs:" in content, "Should have globs in frontmatter"
    assert "alwaysApply:" in content, "Should have alwaysApply in frontmatter"

    # Check for component documentation
    assert "Ghostbusters Component" in content, "Should contain component description"
    assert "Tool Integration" in content, "Should contain tool integration section"
    assert "When to Use Ghostbusters" in content, "Should contain usage guidelines"


def test_ghostbusters_component_structure() -> None:
    """Test that Ghostbusters component has proper structure"""
    # Check main component files
    component_files = [
        "src/ghostbusters/__init__.py",
        "src/ghostbusters/ghostbusters_orchestrator.py",
        "src/ghostbusters/agents.py",
        "src/ghostbusters/validators.py",
        "src/ghostbusters/recovery.py",
    ]

    for file_path in component_files:
        assert Path(
            file_path,
        ).exists(), f"Ghostbusters component file should exist: {file_path}"

    # Check test files
    test_files = [
        "tests/test_ghostbusters.py.disabled",
        "tests/test_ghostbusters_integration.py",
    ]

    for file_path in test_files:
        assert Path(
            file_path,
        ).exists(), f"Ghostbusters test file should exist: {file_path}"


def test_ghostbusters_file_organization() -> None:
    """Test that Ghostbusters is properly included in file organization"""
    # Load project model
    with open("project_model_registry.json") as f:
        model_data = json.load(f)

    # Check file organization
    file_organization = model_data["file_organization"]
    domain_rules = file_organization["domain_rules"]

    # Check that Ghostbusters rule is included
    ghostbusters_rule = ".cursor/rules/ghostbusters.mdc"
    assert (
        ghostbusters_rule in domain_rules
    ), "Ghostbusters rule should be in domain rules"
    assert (
        domain_rules[ghostbusters_rule]
        == "Ghostbusters multi-agent delusion detection and recovery guidelines"
    ), "Should have proper description"


if __name__ == "__main__":
    # Run all tests
    test_ghostbusters_domain_in_model()
    test_ghostbusters_requirements_traceability()
    test_ghostbusters_rule_exists()
    test_ghostbusters_component_structure()
    test_ghostbusters_file_organization()

    print("✅ All Ghostbusters integration tests passed!")
