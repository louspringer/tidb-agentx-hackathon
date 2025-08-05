#!/usr/bin/env python3
"""
Tests for UV Package Management Requirements
Tests that UV is properly configured and all dependencies are managed correctly
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any


    tests = [
        tester.test_requirement_36_uv_package_management,
        tester.test_requirement_37_streamlit_dependencies_uv,
        tester.test_requirement_38_security_dependencies_uv,
        tester.test_requirement_39_dev_dependencies_uv,
        tester.test_uv_rule_exists,

