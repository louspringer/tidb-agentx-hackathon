#!/usr/bin/env python3
"""
🧪 File Organization Test

Test suite to validate the new domain-based file organization structure.
"""


import pytest
import os
import json
from pathlib import Path

        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"

            "src/streamlit/openflow_quickstart_app.py",
            "src/security_first/test_streamlit_security_first.py",
            "src/multi_agent_testing/test_multi_agent_blind_spot_detection.py",
            "tests/test_basic_validation.py",

