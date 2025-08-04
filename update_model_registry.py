#!/usr/bin/env python3
"""
Update Model Registry with Ghostbusters Findings
"""

import json
import sys
from typing import Dict, Any


def load_model_registry() -> Dict[str, Any]:
    """Load the project model registry"""
    try:
        with open('project_model_registry.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ ERROR: project_model_registry.json not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in project_model_registry.json: {e}")
        sys.exit(1)


def update_security_domain(model: Dict[str, Any]) -> None:
    """Update security domain with missing requirements"""
    security_domain = model['domains']['security_first']
    
    # Add missing global Python pattern
    if "**/*.py" not in security_domain['patterns']:
        security_domain['patterns'].append("**/*.py")
        print("✅ Added **/*.py pattern to security domain")
    
    # Add missing CSRF protection requirement
    csrf_requirement = "Implement CSRF protection for all forms"
    if csrf_requirement not in security_domain['requirements']:
        security_domain['requirements'].append(csrf_requirement)
        print("✅ Added CSRF protection requirement")


def update_type_safety_domain(model: Dict[str, Any]) -> None:
    """Update type safety domain with improved requirements"""
    type_safety_domain = model['domains']['type_safety']
    
    # Update type safety requirements
    updated_requirements = [
        "All Python functions must have type annotations",
        "All function parameters must have type annotations", 
        "All return values must have type annotations",
        "External library stubs must be installed",
        "Mypy configuration must be properly set up",
        "Achieve minimum 50% type annotation coverage",
        "Enforce type annotations in CI/CD pipeline"
    ]
    
    type_safety_domain['requirements'] = updated_requirements
    print("✅ Updated type safety requirements")


def add_testing_domain(model: Dict[str, Any]) -> None:
    """Add comprehensive testing domain"""
    if 'testing' not in model['domains']:
        model['domains']['testing'] = {
            "patterns": [
                "tests/*.py",
                "test_*.py",
                "*_test.py"
            ],
            "content_indicators": [
                "pytest",
                "test_",
                "assert",
                "unittest"
            ],
            "linter": "flake8",
            "formatter": "black",
            "validator": "pytest",
            "type_checker": "mypy",
            "exclusions": [
                "__pycache__/*",
                "*.pyc"
            ],
            "requirements": [
                "Use flake8 for test file linting",
                "Format test code with black",
                "Validate tests with pytest",
                "Type check tests with mypy",
                "Maintain minimum 80% test coverage",
                "Fix all indentation errors in test files",
                "Resolve all import errors in test files"
            ]
        }
        print("✅ Added comprehensive testing domain")


def add_code_quality_model_domain(model: Dict[str, Any]) -> None:
    """Add code quality model domain"""
    if 'code_quality_model' not in model['domains']:
        model['domains']['code_quality_model'] = {
            "patterns": [
                "src/code_quality_system/*.py",
                "*quality*.py"
            ],
            "content_indicators": [
                "CodeQualityModel",
                "quality_model",
                "code_quality"
            ],
            "linter": "flake8",
            "formatter": "black",
            "validator": "pytest",
            "exclusions": [
                "__pycache__/*",
                "*.pyc"
            ],
            "requirements": [
                "Implement CodeQualityModel class",
                "Use flake8 for code quality model linting",
                "Format code quality model with black",
                "Validate code quality model with pytest",
                "Ensure code quality model follows best practices"
            ]
        }
        print("✅ Added code quality model domain")


def update_requirements_traceability(model: Dict[str, Any]) -> None:
    """Update requirements traceability with missing requirements"""
    
    # Add missing requirements
    new_requirements = [
        {
            "requirement": "Fix indentation errors in test files",
            "domain": "testing",
            "implementation": "Use black formatter and flake8 linter to fix indentation",
            "test": "test_indentation_fixes"
        },
        {
            "requirement": "Implement CodeQualityModel",
            "domain": "code_quality_model",
            "implementation": "Create CodeQualityModel class with proper structure",
            "test": "test_code_quality_model_implementation"
        },
        {
            "requirement": "Achieve 50% type annotation coverage",
            "domain": "type_safety",
            "implementation": "Add type annotations to all functions and enforce with mypy",
            "test": "test_type_annotation_coverage"
        },
        {
            "requirement": "Fix UV/hatchling compatibility",
            "domain": "package_management",
            "implementation": "Update pyproject.toml and UV configuration",
            "test": "test_uv_compatibility"
        },
        {
            "requirement": "Add global Python pattern to security",
            "domain": "security_first",
            "implementation": "Add **/*.py pattern to security domain patterns",
            "test": "test_security_pattern_coverage"
        }
    ]
    
    # Add new requirements to traceability
    for req in new_requirements:
        if req not in model['requirements_traceability']:
            model['requirements_traceability'].append(req)
    
    print(f"✅ Added {len(new_requirements)} new requirements to traceability")


def save_model_registry(model: Dict[str, Any]) -> None:
    """Save the updated model registry"""
    try:
        with open('project_model_registry.json', 'w') as f:
            json.dump(model, f, indent=2)
        print("✅ Model registry updated successfully")
    except Exception as e:
        print(f"❌ ERROR: Failed to save model registry: {e}")
        sys.exit(1)


def main():
    """Update model registry with ghostbusters findings"""
    
    print("🎯 UPDATING MODEL REGISTRY WITH GHOSTBUSTERS FINDINGS")
    print("=" * 60)
    
    # Load current model
    model = load_model_registry()
    
    # Update domains
    update_security_domain(model)
    update_type_safety_domain(model)
    add_testing_domain(model)
    add_code_quality_model_domain(model)
    
    # Update requirements traceability
    update_requirements_traceability(model)
    
    # Update version
    model['version'] = '1.8'
    model['last_updated'] = '2024-12-19'
    
    # Save updated model
    save_model_registry(model)
    
    print("\n✅ MODEL REGISTRY UPDATED SUCCESSFULLY!")
    print(f"📊 New version: {model['version']}")
    print(f"🏢 Total domains: {len(model['domains'])}")
    print(f"📋 Total requirements: {len(model['requirements_traceability'])}")


if __name__ == "__main__":
    main() 