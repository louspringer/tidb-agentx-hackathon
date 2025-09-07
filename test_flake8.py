#!/usr/bin/env python3
"""
Test file to check Flake8 errors
"""

import logging

from code_generator import (
    CodeGenerator,
)


class PerfectCodeGenerator(CodeGenerator):
    """
    Generator that CANNOT emit non-conforming code
    Integrates with linting tools and validates before emission
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.linters = {
            "black": self._run_black,
            "flake8": self._run_flake8,
            "ast": self._validate_ast,
        }
        self.max_fix_attempts = 5
