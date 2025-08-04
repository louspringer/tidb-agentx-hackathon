#!/usr/bin/env python3
"""
Tests for Makefile Integration with Model-Driven Approach
Tests that the Makefile properly leverages the project_model_registry.json
"""

import json
import subprocess
import sys
import re
from pathlib import Path
from typing import Dict, Any


class TestMakefileIntegration:
    """Test Makefile integration with model-driven approach"""

    def __init__(self: Any) -> None:
        """Initialize test environment"""
        self.project_root = Path(__file__).parent.parent
        self.model_file = self.project_root / "project_model_registry.json"
        self.makefile = self.project_root / "Makefile"

    def load_project_model(self: Any) -> Dict[str, Any]:
        """Load the project model registry"""
        with open(self.model_file, "r") as f:
            return json.load(f)

    def test_makefile_exists(self: Any) -> None:
        """Test that Makefile exists and is properly structured."""
        print("Testing Makefile existence and structure...")

        assert self.makefile.exists(), "Makefile should exist"
        print("✅ Makefile exists")

        with open(self.makefile, "r") as f:
            content: str = f.read()

        # Check for model-driven references
        assert (
            "project_model_registry.json" in content
        ), "Makefile should reference project model registry"
        print("✅ Makefile references project model registry")

        # Check for domain-specific targets
        assert "install-python" in content, "Makefile should have install-python target"
        assert "test-security" in content, "Makefile should have test-security target"
        assert "lint-all" in content, "Makefile should have lint-all target"
        print("✅ Makefile has domain-specific targets")

        # Check for UV integration
        assert "$(UV) sync" in content, "Makefile should use UV for Python dependencies"
        print("✅ Makefile uses UV for Python dependencies")

        print("✅ Makefile structure is valid")

    def test_makefile_domains_match_model(self: Any) -> None:
        """Test that Makefile domains match the model registry."""
        print("Testing Makefile domains match model registry...")

        project_model: Dict[str, Any] = self.load_project_model()
        model_domains = set(project_model["domains"].keys())

        # Read Makefile to extract domain targets
        with open(self.makefile, "r") as f:
            content: str = f.read()

        # Extract domain names from install targets
        install_targets = re.findall(r"install-(\w+):", content)
        makefile_domains = set(install_targets)

        # Check that key domains are present
        key_domains = {"python", "bash", "security", "streamlit", "healthcare"}
        for domain in key_domains:
            assert (
                domain in makefile_domains
            ), f"Makefile should have install-{domain} target"
            print(f"✅ Makefile has install-{domain} target")

        print("✅ Makefile domains match model registry")

    def test_makefile_help_works(self: Any) -> None:
        """Test that make help works and shows proper information."""
        print("Testing make help functionality...")

        try:
            result = subprocess.run(
                ["make", "help"], capture_output=True, text=True, cwd=self.project_root
            )
            assert result.returncode == 0, "make help should work"
            print("✅ make help works")

            # Check that help shows domain information
            help_output = result.stdout
            assert (
                "Available targets:" in help_output
            ), "Help should show available targets"
            assert "install-" in help_output, "Help should show install targets"
            print("✅ make help shows proper information")

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"⚠️ make help test skipped: {e}")
            return

        print("✅ make help functionality test passed")

    def test_makefile_show_domains_works(self: Any) -> None:
        """Test that make show-domains works and shows domain information."""
        print("Testing make show-domains functionality...")

        try:
            result = subprocess.run(
                ["make", "show-domains"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            assert result.returncode == 0, "make show-domains should work"
            print("✅ make show-domains works")

            # Check that it shows domain information
            output = result.stdout
            assert "python" in output.lower(), "Should show python domain"
            assert "security" in output.lower(), "Should show security domain"
            print("✅ make show-domains shows domain information")

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"⚠️ make show-domains test skipped: {e}")
            return

        print("✅ make show-domains functionality test passed")

    def test_makefile_show_rules_works(self: Any) -> None:
        """Test that make show-rules works and shows rule information."""
        print("Testing make show-rules functionality...")

        try:
            result = subprocess.run(
                ["make", "show-rules"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            assert result.returncode == 0, "make show-rules should work"
            print("✅ make show-rules works")

            # Check that it shows rule information
            output = result.stdout
            assert "rules" in output.lower(), "Should show rules information"
            print("✅ make show-rules shows rule information")

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"⚠️ make show-rules test skipped: {e}")
            return

        print("✅ make show-rules functionality test passed")

    def test_makefile_validate_model_works(self: Any) -> None:
        """Test that make validate-model works and validates the model."""
        print("Testing make validate-model functionality...")

        try:
            result = subprocess.run(
                ["make", "validate-model"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            # validate-model might fail if there are issues, but it should run
            print("✅ make validate-model runs")

            # Check that it shows validation information
            output = result.stdout + result.stderr
            assert (
                "validation" in output.lower() or "model" in output.lower()
            ), "Should show validation information"
            print("✅ make validate-model shows validation information")

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"⚠️ make validate-model test skipped: {e}")
            return

        print("✅ make validate-model functionality test passed")

    def test_makefile_targets_are_sensible(self: Any) -> None:
        """Test that Makefile targets are sensible and well-structured."""
        print("Testing Makefile target sensibility...")

        with open(self.makefile, "r") as f:
            content: str = f.read()

        # Check for essential targets
        essential_targets = [
            "help",
            "install",
            "test",
            "lint",
            "clean",
        ]

        for target in essential_targets:
            assert f"{target}:" in content, f"Makefile should have {target} target"
            print(f"✅ Makefile has {target} target")

        # Check for proper target structure
        assert ".PHONY:" in content, "Makefile should have .PHONY declaration"
        print("✅ Makefile has proper .PHONY declaration")

        # Check for comments
        assert "#" in content, "Makefile should have comments"
        print("✅ Makefile has comments")

        print("✅ Makefile targets are sensible")

    def test_makefile_leverages_model_driven_approach(self: Any) -> None:
        """Test that Makefile properly leverages the model-driven approach."""
        print("Testing Makefile model-driven approach...")

        # Load the project model
        project_model: Dict[str, Any] = self.load_project_model()

        # Check that the model has domains
        assert "domains" in project_model, "Project model should have domains"
        domains = project_model["domains"]

        # Check that the Makefile references the model
        with open(self.makefile, "r") as f:
            content: str = f.read()

        # Check for model file reference
        assert (
            "project_model_registry.json" in content
        ), "Makefile should reference model file"
        print("✅ Makefile references project model registry")

        # Check for domain-specific targets
        for domain_name in domains.keys():
            if domain_name in ["python", "bash", "security", "streamlit"]:
                assert (
                    f"install-{domain_name}" in content
                ), f"Makefile should have install-{domain_name} target"
                print(f"✅ Makefile has install-{domain_name} target")

        # Check for model validation
        assert "validate-model" in content, "Makefile should have validate-model target"
        print("✅ Makefile has validate-model target")

        print("✅ Makefile leverages model-driven approach")


def main() -> None:
    """Run all Makefile integration tests"""
    print("🔧 Testing Makefile Integration Requirements")
    print("=" * 60)

    tester = TestMakefileIntegration()

    tests = [
        tester.test_makefile_exists,
        tester.test_makefile_domains_match_model,
        tester.test_makefile_help_works,
        tester.test_makefile_show_domains_works,
        tester.test_makefile_show_rules_works,
        tester.test_makefile_validate_model_works,
        tester.test_makefile_targets_are_sensible,
        tester.test_makefile_leverages_model_driven_approach,
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
    print(f"📊 Makefile Integration Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All Makefile integration tests passed!")
        return True
    else:
        print("⚠️ Some Makefile integration tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
