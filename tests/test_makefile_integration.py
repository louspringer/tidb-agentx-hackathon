#!/usr/bin/env python3
"""
Tests for Makefile Integration with Model-Driven Approach
Tests that the Makefile properly leverages the project_model_registry.json
"""

import json
import subprocess
import sys

        """Initialize test environment"""
        self.project_root = Path(__file__).parent.parent
        self.model_file = self.project_root / "project_model_registry.json"
        self.makefile = self.project_root / "Makefile"

        # Check for domain-specific targets
        assert "install-python" in content, "Makefile should have install-python target"
        assert "test-security" in content, "Makefile should have test-security target"
        assert "lint-all" in content, "Makefile should have lint-all target"
        print("✅ Makefile has domain-specific targets")

        try:
            result = subprocess.run(
                ["make", "show-domains"],
                capture_output=True,
                text=True,

        try:
            result = subprocess.run(
                ["make", "show-rules"],
                capture_output=True,
                text=True,

        try:
            result = subprocess.run(
                ["make", "validate-model"],
                capture_output=True,
                text=True,

    tests = [
        tester.test_makefile_exists,
        tester.test_makefile_domains_match_model,
        tester.test_makefile_help_works,
        tester.test_makefile_show_domains_works,
        tester.test_makefile_show_rules_works,
        tester.test_makefile_validate_model_works,
        tester.test_makefile_targets_are_sensible,

