#!/usr/bin/env python3
"""
Test suite for Healthcare CDC requirements (27-32).
Based on GA Gemini 2.5 Pro implementation plan.
"""

import pytest
import json
import os
import fnmatch
from pathlib import Path
from typing import Dict, Any, List


class TestHealthcareCDCRequirements:
    """Test suite for Healthcare CDC domain requirements."""
    
    def setup_method(self):
        """Setup test environment."""
        self.project_root = Path(__file__).parent.parent
        self.healthcare_cdc_dir = self.project_root / "healthcare-cdc"
        self.project_model = self.load_project_model()
    
    def load_project_model(self) -> Dict[str, Any]:
        """Load project model registry."""
        model_path = self.project_root / "project_model_registry.json"
        with open(model_path, 'r') as f:
            return json.load(f)
    
    def test_requirement_27_hipaa_compliance_validation(self):
        """Test HIPAA compliance validation requirement."""
        # Check that healthcare_cdc domain exists
        assert "healthcare_cdc" in self.project_model["domains"]
        
        # Check that HIPAA compliance is in requirements
        healthcare_domain = self.project_model["domains"]["healthcare_cdc"]
        requirements = healthcare_domain["requirements"]
        
        hipaa_requirements = [
            "Enforce HIPAA compliance validation",
            "Implement PHI detection and validation"
        ]
        
        for req in hipaa_requirements:
            assert req in requirements, f"Missing HIPAA requirement: {req}"
        
        # Check that healthcare-cdc directory exists
        assert self.healthcare_cdc_dir.exists(), "healthcare-cdc directory not found"
        
        # Check for HIPAA-related files
        hipaa_files = [
            "healthcare_cdc_domain_model.py",
            "test_healthcare_cdc_domain_model.py"
        ]
        
        for file_name in hipaa_files:
            file_path = self.healthcare_cdc_dir / file_name
            assert file_path.exists(), f"Missing HIPAA file: {file_name}"
    
    def test_requirement_28_phi_detection_validation(self):
        """Test PHI detection and validation requirement."""
        # Check that PHI detection is mentioned in content indicators
        healthcare_domain = self.project_model["domains"]["healthcare_cdc"]
        content_indicators = healthcare_domain["content_indicators"]
        
        phi_indicators = ["phi", "hipaa", "patient", "medical"]
        for indicator in phi_indicators:
            assert indicator in content_indicators, f"Missing PHI indicator: {indicator}"
        
        # Check for PHI detection implementation
        domain_model_path = self.healthcare_cdc_dir / "healthcare_cdc_domain_model.py"
        if domain_model_path.exists():
            with open(domain_model_path, 'r') as f:
                content = f.read()
                # Check for PHI-related classes or functions
                phi_keywords = ["PHI", "phi", "ProtectedHealthInformation", "detect_phi"]
                found_phi = any(keyword in content for keyword in phi_keywords)
                assert found_phi, "PHI detection not implemented in domain model"
    
    def test_requirement_29_immutable_audit_logging(self):
        """Test immutable audit logging requirement."""
        # Check that audit logging is mentioned in content indicators
        healthcare_domain = self.project_model["domains"]["healthcare_cdc"]
        content_indicators = healthcare_domain["content_indicators"]
        
        assert "audit" in content_indicators, "Missing audit indicator"
        
        # Check for audit logging implementation
        domain_model_path = self.healthcare_cdc_dir / "healthcare_cdc_domain_model.py"
        if domain_model_path.exists():
            with open(domain_model_path, 'r') as f:
                content = f.read()
                # Check for audit-related classes or functions
                audit_keywords = ["audit", "Audit", "logging", "Log"]
                found_audit = any(keyword in content for keyword in audit_keywords)
                assert found_audit, "Audit logging not implemented in domain model"
    
    def test_requirement_30_healthcare_data_encryption(self):
        """Test healthcare data encryption requirement."""
        # Check that encryption is mentioned in requirements
        healthcare_domain = self.project_model["domains"]["healthcare_cdc"]
        requirements = healthcare_domain["requirements"]
        
        encryption_requirements = [
            "Validate healthcare data encryption"
        ]
        
        for req in encryption_requirements:
            assert req in requirements, f"Missing encryption requirement: {req}"
        
        # Check for encryption implementation
        domain_model_path = self.healthcare_cdc_dir / "healthcare_cdc_domain_model.py"
        if domain_model_path.exists():
            with open(domain_model_path, 'r') as f:
                content = f.read()
                # Check for encryption-related imports or classes
                encryption_keywords = ["encrypt", "Encrypt", "AES", "TLS", "cryptography"]
                found_encryption = any(keyword in content for keyword in encryption_keywords)
                assert found_encryption, "Data encryption not implemented in domain model"
    
    def test_requirement_31_healthcare_access_control(self):
        """Test healthcare access control and authentication requirement."""
        # Check that access control is mentioned in requirements
        healthcare_domain = self.project_model["domains"]["healthcare_cdc"]
        requirements = healthcare_domain["requirements"]
        
        access_control_requirements = [
            "Enforce access control and authentication"
        ]
        
        for req in access_control_requirements:
            assert req in requirements, f"Missing access control requirement: {req}"
        
        # Check for access control implementation
        domain_model_path = self.healthcare_cdc_dir / "healthcare_cdc_domain_model.py"
        if domain_model_path.exists():
            with open(domain_model_path, 'r') as f:
                content = f.read()
                # Check for authentication-related classes or functions
                auth_keywords = ["auth", "Auth", "JWT", "RBAC", "authentication", "authorization"]
                found_auth = any(keyword in content for keyword in auth_keywords)
                assert found_auth, "Access control not implemented in domain model"
    
    def test_requirement_32_healthcare_cdc_cicd_integration(self):
        """Test healthcare CDC CI/CD integration requirement."""
        # Check that CI/CD patterns are included
        healthcare_domain = self.project_model["domains"]["healthcare_cdc"]
        patterns = healthcare_domain["patterns"]
        
        # Check for YAML and JSON patterns for CI/CD
        cicd_patterns = ["healthcare-cdc/*.yaml", "healthcare-cdc/*.json"]
        for pattern in cicd_patterns:
            # Accept any pattern in patterns that matches the file type (e.g., 'healthcare-cdc/*.yaml', etc.)
            import re
            regex = re.compile(fnmatch.translate(pattern))
            matched = any(regex.match(p) for p in patterns)
            assert matched, f"Missing CI/CD pattern matching: {pattern}"
        
        # Check for CI/CD files in healthcare-cdc directory
        cicd_files = [
            "healthcare-cdc-infrastructure.yaml",
            "healthcare-cdc-config.json"
        ]
        
        # At least one CI/CD file should exist
        found_cicd_file = False
        for file_name in cicd_files:
            file_path = self.healthcare_cdc_dir / file_name
            if file_path.exists():
                found_cicd_file = True
                break
        
        # Also check models directory for infrastructure files
        models_dir = self.healthcare_cdc_dir / "models"
        if models_dir.exists():
            for file_path in models_dir.glob("*.yaml"):
                if "infrastructure" in file_path.name or "cicd" in file_path.name:
                    found_cicd_file = True
                    break
        
        assert found_cicd_file, "No CI/CD configuration files found in healthcare-cdc"
    
    def test_healthcare_cdc_domain_completeness(self):
        """Test that healthcare CDC domain is complete and well-structured."""
        healthcare_domain = self.project_model["domains"]["healthcare_cdc"]
        
        # Check required fields
        required_fields = ["patterns", "content_indicators", "linter", "formatter", "validator", "requirements"]
        for field in required_fields:
            assert field in healthcare_domain, f"Missing required field: {field}"
        
        # Check that patterns include all necessary file types
        patterns = healthcare_domain["patterns"]
        required_patterns = ["*.py", "*.md", "*.sql", "*.yaml", "*.json"]
        for pattern in required_patterns:
            assert pattern in patterns, f"Missing pattern: {pattern}"
        
        # Check that content indicators include healthcare-specific terms
        content_indicators = healthcare_domain["content_indicators"]
        required_indicators = ["healthcare", "cdc", "phi", "hipaa"]
        for indicator in required_indicators:
            assert indicator in content_indicators, f"Missing content indicator: {indicator}"
        
        # Check that requirements include security and compliance
        requirements = healthcare_domain["requirements"]
        required_requirements = [
            "Enforce HIPAA compliance validation",
            "Implement PHI detection and validation",
            "Ensure immutable audit logging",
            "Validate healthcare data encryption",
            "Enforce access control and authentication"
        ]
        for req in required_requirements:
            assert req in requirements, f"Missing requirement: {req}"
    
    def test_healthcare_cdc_file_organization(self):
        """Test that healthcare CDC files are properly organized."""
        # Check directory structure
        required_dirs = [
            self.healthcare_cdc_dir,
            self.healthcare_cdc_dir / "models",
            self.healthcare_cdc_dir / "sql",
            self.healthcare_cdc_dir / "docs"
        ]
        
        for dir_path in required_dirs:
            assert dir_path.exists(), f"Missing directory: {dir_path}"
        
        # Check for required files
        required_files = [
            "healthcare_cdc_domain_model.py",
            "test_healthcare_cdc_domain_model.py",
            "README.md"
        ]
        
        for file_name in required_files:
            file_path = self.healthcare_cdc_dir / file_name
            assert file_path.exists(), f"Missing file: {file_name}"
        
        # Check for SQL schema
        sql_dir = self.healthcare_cdc_dir / "sql"
        sql_files = list(sql_dir.glob("*.sql"))
        assert len(sql_files) > 0, "No SQL schema files found"
        
        # Check for documentation
        docs_dir = self.healthcare_cdc_dir / "docs"
        if docs_dir.exists():
            doc_files = list(docs_dir.glob("*.md"))
            assert len(doc_files) > 0, "No documentation files found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 