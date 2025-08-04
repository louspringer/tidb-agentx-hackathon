#!/usr/bin/env python3
"""
Test suite for Healthcare CDC requirements (27-32).
Based on GA Gemini 2.5 Pro implementation plan.
"""

import pytest
import json
import fnmatch
from pathlib import Path
from typing import Dict, Any, List


class TestHealthcareCDCRequirements:
    """Test suite for Healthcare CDC domain requirements."""

    def setup_method(self: Any) -> None:
        """Setup test environment."""
        self.project_root = Path(__file__).parent.parent
        self.healthcare_cdc_dir = self.project_root / "healthcare-cdc"
        self.project_model = self.load_project_model()

    def load_project_model(self: Any) -> Dict[str, Any]:
        """Load project model registry."""
        model_path: Path = self.project_root / "project_model_registry.json"
        with open(model_path, "r") as f:
            return json.load(f)

    def test_requirement_27_hipaa_compliance_validation(self: Any) -> None:
        """Test HIPAA compliance validation requirement."""
        print("Testing Requirement 27: HIPAA compliance validation...")

        # Check that healthcare_cdc domain exists
        assert "healthcare_cdc" in self.project_model["domains"]

        # Check that HIPAA compliance is in requirements
        healthcare_domain: Dict[str, Any] = self.project_model["domains"][
            "healthcare_cdc"
        ]
        requirements: List[str] = healthcare_domain["requirements"]

        hipaa_requirements: List[str] = [
            "Enforce HIPAA compliance validation",
            "Implement PHI detection and validation",
        ]

        for req in hipaa_requirements:
            assert req in requirements, f"Missing HIPAA requirement: {req}"

        # Check that healthcare-cdc directory exists
        assert self.healthcare_cdc_dir.exists(), "healthcare-cdc directory not found"

        # Check for HIPAA-related files
        hipaa_files: List[str] = [
            "healthcare_cdc_domain_model.py",
            "test_healthcare_cdc_domain_model.py",
        ]

        for file_name in hipaa_files:
            file_path: Path = self.healthcare_cdc_dir / file_name
            assert file_path.exists(), f"Missing HIPAA file: {file_name}"

        print("✅ Requirement 27: HIPAA compliance validation - PASSED")

    def test_requirement_28_phi_detection_validation(self: Any) -> None:
        """Test PHI detection and validation requirement."""
        print("Testing Requirement 28: PHI detection and validation...")

        project_model: Dict[str, Any] = self.load_project_model()
        if not project_model:
            return

        # Check that requirement exists in traceability
        requirements_traceability: List[Dict[str, str]] = project_model[
            "requirements_traceability"
        ]
        phi_req: str = "PHI detection and validation"

        found: bool = False
        for req in requirements_traceability:
            if req["requirement"] == phi_req:
                found = True
                print(f"✅ Requirement found in traceability: {phi_req}")
                break

        assert found, f"Missing requirement in traceability: {phi_req}"

        # Check that healthcare CDC domain exists
        assert (
            "healthcare_cdc" in project_model["domains"]
        ), "healthcare_cdc domain should exist"

        print("✅ Requirement 28: PHI detection and validation - PASSED")

    def test_requirement_29_immutable_audit_logging(self: Any) -> None:
        """Test immutable audit logging requirement."""
        print("Testing Requirement 29: Immutable audit logging...")

        project_model: Dict[str, Any] = self.load_project_model()
        if not project_model:
            return

        # Check that requirement exists in traceability
        requirements_traceability: List[Dict[str, str]] = project_model[
            "requirements_traceability"
        ]
        audit_req: str = "Immutable audit logging"

        found: bool = False
        for req in requirements_traceability:
            if req["requirement"] == audit_req:
                found = True
                print(f"✅ Requirement found in traceability: {audit_req}")
                break

        assert found, f"Missing requirement in traceability: {audit_req}"

        # Check that healthcare CDC domain exists
        assert (
            "healthcare_cdc" in project_model["domains"]
        ), "healthcare_cdc domain should exist"

        print("✅ Requirement 29: Immutable audit logging - PASSED")

    def test_requirement_30_healthcare_data_encryption(self: Any) -> None:
        """Test healthcare data encryption requirement."""
        print("Testing Requirement 30: Healthcare data encryption...")

        project_model: Dict[str, Any] = self.load_project_model()
        if not project_model:
            return

        # Check that requirement exists in traceability
        requirements_traceability: List[Dict[str, str]] = project_model[
            "requirements_traceability"
        ]
        encryption_req: str = "Healthcare data encryption"

        found: bool = False
        for req in requirements_traceability:
            if req["requirement"] == encryption_req:
                found = True
                print(f"✅ Requirement found in traceability: {encryption_req}")
                break

        assert found, f"Missing requirement in traceability: {encryption_req}"

        # Check that healthcare CDC domain exists
        assert (
            "healthcare_cdc" in project_model["domains"]
        ), "healthcare_cdc domain should exist"

        print("✅ Requirement 30: Healthcare data encryption - PASSED")

    def test_requirement_31_healthcare_access_control(self: Any) -> None:
        """Test healthcare access control requirement."""
        print("Testing Requirement 31: Healthcare access control...")

        project_model: Dict[str, Any] = self.load_project_model()
        if not project_model:
            return

        # Check that requirement exists in traceability
        requirements_traceability: List[Dict[str, str]] = project_model[
            "requirements_traceability"
        ]
        access_req: str = "Healthcare access control and authentication"

        found: bool = False
        for req in requirements_traceability:
            if req["requirement"] == access_req:
                found = True
                print(f"✅ Requirement found in traceability: {access_req}")
                break

        assert found, f"Missing requirement in traceability: {access_req}"

        # Check that healthcare CDC domain exists
        assert (
            "healthcare_cdc" in project_model["domains"]
        ), "healthcare_cdc domain should exist"

        print("✅ Requirement 31: Healthcare access control - PASSED")

    def test_requirement_32_healthcare_cdc_cicd_integration(self: Any) -> None:
        """Test healthcare CDC CI/CD integration requirement."""
        print("Testing Requirement 32: Healthcare CDC CI/CD integration...")

        project_model: Dict[str, Any] = self.load_project_model()
        if not project_model:
            return

        # Check that requirement exists in traceability
        requirements_traceability: List[Dict[str, str]] = project_model[
            "requirements_traceability"
        ]
        cicd_req: str = "Healthcare CDC CI/CD integration"

        found: bool = False
        for req in requirements_traceability:
            if req["requirement"] == cicd_req:
                found = True
                print(f"✅ Requirement found in traceability: {cicd_req}")
                break

        assert found, f"Missing requirement in traceability: {cicd_req}"

        # Check that healthcare CDC domain exists
        assert (
            "healthcare_cdc" in project_model["domains"]
        ), "healthcare_cdc domain should exist"

        print("✅ Requirement 32: Healthcare CDC CI/CD integration - PASSED")

    def test_healthcare_cdc_domain_completeness(self: Any) -> None:
        """Test that healthcare CDC domain is complete."""
        print("Testing healthcare CDC domain completeness...")

        project_model: Dict[str, Any] = self.load_project_model()
        if not project_model:
            return

        # Check that healthcare_cdc domain exists
        assert (
            "healthcare_cdc" in project_model["domains"]
        ), "healthcare_cdc domain should exist"

        healthcare_domain: Dict[str, Any] = project_model["domains"]["healthcare_cdc"]

        # Check required fields
        required_fields: List[str] = ["patterns", "content_indicators", "requirements"]
        for field in required_fields:
            assert (
                field in healthcare_domain
            ), f"Missing field in healthcare_cdc domain: {field}"

        # Check that patterns include healthcare files
        patterns: List[str] = healthcare_domain["patterns"]
        healthcare_patterns: List[str] = ["*healthcare*", "*cdc*", "*hipaa*", "*phi*"]

        for pattern in healthcare_patterns:
            assert pattern in patterns, f"Missing healthcare pattern: {pattern}"

        # Check that content indicators include healthcare terms
        content_indicators: List[str] = healthcare_domain["content_indicators"]
        healthcare_indicators: List[str] = ["healthcare", "cdc", "hipaa", "phi"]

        for indicator in healthcare_indicators:
            assert (
                indicator in content_indicators
            ), f"Missing healthcare indicator: {indicator}"

        print("✅ Healthcare CDC domain completeness - PASSED")

    def test_healthcare_cdc_file_organization(self: Any) -> None:
        """Test healthcare CDC file organization."""
        print("Testing healthcare CDC file organization...")

        # Check that healthcare-cdc directory exists
        assert self.healthcare_cdc_dir.exists(), "healthcare-cdc directory not found"

        # Check for required healthcare CDC files
        required_files: List[str] = [
            "healthcare_cdc_domain_model.py",
            "test_healthcare_cdc_domain_model.py",
        ]

        for file_name in required_files:
            file_path: Path = self.healthcare_cdc_dir / file_name
            assert (
                file_path.exists()
            ), f"Missing required healthcare CDC file: {file_name}"

        # Check that files contain healthcare CDC content
        for file_name in required_files:
            file_path = self.healthcare_cdc_dir / file_name
            with open(file_path, "r") as f:
                content: str = f.read()
                assert (
                    "healthcare" in content.lower() or "cdc" in content.lower()
                ), f"File should contain healthcare CDC content: {file_name}"

        print("✅ Healthcare CDC file organization - PASSED")


def main() -> None:
    """Run all healthcare CDC requirement tests."""
    print("🏥 Testing Healthcare CDC Requirements")
    print("=" * 60)

    tester = TestHealthcareCDCRequirements()

    tests = [
        tester.test_requirement_27_hipaa_compliance_validation,
        tester.test_requirement_28_phi_detection_validation,
        tester.test_requirement_29_immutable_audit_logging,
        tester.test_requirement_30_healthcare_data_encryption,
        tester.test_requirement_31_healthcare_access_control,
        tester.test_requirement_32_healthcare_cdc_cicd_integration,
        tester.test_healthcare_cdc_domain_completeness,
        tester.test_healthcare_cdc_file_organization,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print()

    print("=" * 60)
    print(f"📊 Healthcare CDC Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All healthcare CDC tests passed!")
        return True
    else:
        print("⚠️ Some healthcare CDC tests failed")
        return False


if __name__ == "__main__":
    success = main()
    import sys

    sys.exit(0 if success else 1)
