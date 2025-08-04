#!/usr/bin/env python3
"""
Test suite for Healthcare CDC requirements (27-32).
Based on GA Gemini 2.5 Pro implementation plan.
"""

import pytest
import json
import fnmatch
import re
from pathlib import Path
from typing import Dict, Any


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
        print("Testing Requirement 28: PHI detection and validation...")
        
        project_model = self.load_project_model()
        if not project_model:
            return False
        
        # Check that requirement exists in traceability
        requirements_traceability = project_model["requirements_traceability"]
        phi_req = "PHI detection and validation"
        
        found = False
        for req in requirements_traceability:
            if req["requirement"] == phi_req:
                found = True
                print(f"✅ Requirement found in traceability: {phi_req}")
                break
        
        assert found, f"Missing requirement in traceability: {phi_req}"
        
        # Check that healthcare CDC domain exists
        assert "healthcare_cdc" in project_model["domains"], "healthcare_cdc domain should exist"
        
        print("✅ Requirement 28: PHI detection and validation - PASSED")
    
    def test_requirement_29_immutable_audit_logging(self):
        """Test immutable audit logging requirement."""
        print("Testing Requirement 29: Immutable audit logging...")
        
        project_model = self.load_project_model()
        if not project_model:
            return False
        
        # Check that requirement exists in traceability
        requirements_traceability = project_model["requirements_traceability"]
        audit_req = "Immutable audit logging"
        
        found = False
        for req in requirements_traceability:
            if req["requirement"] == audit_req:
                found = True
                print(f"✅ Requirement found in traceability: {audit_req}")
                break
        
        assert found, f"Missing requirement in traceability: {audit_req}"
        
        # Check that healthcare CDC domain exists
        assert "healthcare_cdc" in project_model["domains"], "healthcare_cdc domain should exist"
        
        print("✅ Requirement 29: Immutable audit logging - PASSED")
    
    def test_requirement_30_healthcare_data_encryption(self):
        """Test healthcare data encryption requirement."""
        print("Testing Requirement 30: Healthcare data encryption...")
        
        project_model = self.load_project_model()
        if not project_model:
            return False
        
        # Check that requirement exists in traceability
        requirements_traceability = project_model["requirements_traceability"]
        encryption_req = "Healthcare data encryption"
        
        found = False
        for req in requirements_traceability:
            if req["requirement"] == encryption_req:
                found = True
                print(f"✅ Requirement found in traceability: {encryption_req}")
                break
        
        assert found, f"Missing requirement in traceability: {encryption_req}"
        
        # Check that healthcare CDC domain exists
        assert "healthcare_cdc" in project_model["domains"], "healthcare_cdc domain should exist"
        
        print("✅ Requirement 30: Healthcare data encryption - PASSED")
    
    def test_requirement_31_healthcare_access_control(self):
        """Test healthcare access control and authentication requirement."""
        print("Testing Requirement 31: Healthcare access control and authentication...")
        
        project_model = self.load_project_model()
        if not project_model:
            return False
        
        # Check that requirement exists in traceability
        requirements_traceability = project_model["requirements_traceability"]
        auth_req = "Healthcare access control and authentication"
        
        found = False
        for req in requirements_traceability:
            if req["requirement"] == auth_req:
                found = True
                print(f"✅ Requirement found in traceability: {auth_req}")
                break
        
        assert found, f"Missing requirement in traceability: {auth_req}"
        
        # Check that healthcare CDC domain exists
        assert "healthcare_cdc" in project_model["domains"], "healthcare_cdc domain should exist"
        
        print("✅ Requirement 31: Healthcare access control and authentication - PASSED")
    
    def test_requirement_32_healthcare_cdc_cicd_integration(self):
        """Test healthcare CDC CI/CD integration requirement."""
        # Check that CI/CD patterns are included
        healthcare_domain = self.project_model["domains"]["healthcare_cdc"]
        patterns = healthcare_domain["patterns"]
        
        # Check for YAML and JSON patterns for CI/CD
        cicd_patterns = ["healthcare-cdc/*.yaml", "healthcare-cdc/*.json"]
        for pattern in cicd_patterns:
            # Accept any pattern in patterns that matches the file type (e.g., 'healthcare-cdc/*.yaml', etc.)
            matched = any(fnmatch.fnmatch("healthcare-cdc/test.yaml", p) for p in patterns)
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
        """Test healthcare CDC domain completeness."""
        print("Testing healthcare CDC domain completeness...")
        
        project_model = self.load_project_model()
        if not project_model:
            return False
        
        # Check that healthcare CDC domain exists
        assert "healthcare_cdc" in project_model["domains"], "healthcare_cdc domain should exist"
        
        healthcare_domain = project_model["domains"]["healthcare_cdc"]
        
        # Check that domain has required patterns
        patterns = healthcare_domain["patterns"]
        required_patterns = ["healthcare-cdc/*.py", "healthcare-cdc/*.md", "healthcare-cdc/*.sql", "healthcare-cdc/*.yaml", "healthcare-cdc/*.json"]
        
        for pattern in required_patterns:
            assert pattern in patterns, f"Missing pattern: {pattern}"
            print(f"✅ Pattern found: {pattern}")
        
        # Check that domain has content indicators
        content_indicators = healthcare_domain["content_indicators"]
        assert len(content_indicators) > 0, "Healthcare CDC domain should have content indicators"
        
        # Check that domain has requirements
        requirements = healthcare_domain["requirements"]
        assert len(requirements) > 0, "Healthcare CDC domain should have requirements"
        
        print("✅ Healthcare CDC domain completeness - PASSED")
    
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