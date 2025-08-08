#!/usr/bin/env python3
"""Generated from final model-driven projection"""

import os
from dataclasses import dataclass
from typing import Optional

from cryptography.fernet import Fernet

SECURITY_CONFIG = {
    "fernet_key": os.getenv("FERNET_KEY", Fernet.generate_key()),
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "jwt_secret": os.getenv("JWT_SECRET", "your-secret-key"),
    "session_timeout_minutes": int(os.getenv("SESSION_TIMEOUT_MINUTES", "15")),
    "max_login_attempts": int(os.getenv("MAX_LOGIN_ATTEMPTS", "3")),
    "password_min_length": int(os.getenv("PASSWORD_MIN_LENGTH", "12")),
}
AWS_CONFIG = {
    "region": os.getenv("AWS_REGION", "us-east-1"),
    "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
    "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
}


@dataclass
class ViolationPattern:
    """Represents a violation pattern for rule learning"""

    rule_code: str
    file_path: str
    line_number: int
    context: str
    frequency: int = 1
    prevention_strategy: Optional[str] = None
    ignore_directive: Optional[str] = None


class DynamicRuleUpdater:
    """Updates Cursor rules dynamically based on violations"""

    def __init__(self, rules_dir: str = ".cursor/rules") -> None:
        self.rules_dir = Path(rules_dir)
        self.violation_patterns: dict[str, ViolationPattern] = {}
        self.rule_templates = self._load_rule_templates()

    def _load_rule_templates(self) -> dict[str, dict[str, str]]:
        """Load rule templates for different violation types"""
        return {
            "F401": {
                "title": "Unused Import Prevention",
                "description": "Prevent unused imports before they happen",
                "pattern": "import.*unused",
                "suggestion": "Only import modules that are actually used",
                "prevention_code": "",
            },
        }


if __name__ == "__main__":
    main()
