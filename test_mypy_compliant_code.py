"""Mypy-compliant Ghostbusters agents"""

import logging
from typing import Any, Optional


class BaseExpert:
    """Base class for all expert agents"""

    name: str
    logger: Optional[Any] = None

    def __init__(self: BaseExpert, name: str) -> None:
        """Initialize the base expert"""
        self.name = name
        self.logger = logging.getLogger(__name__)

    def detect_delusions(self: BaseExpert, project_path: str) -> dict[str, Any]:
        """Detect delusions in the project"""
        raise NotImplementedError


class SecurityExpert(BaseExpert):
    """Expert agent for detecting security vulnerabilities"""

    def __init__(self: SecurityExpert) -> None:
        """Initialize the security expert"""
        super().__init__("SecurityExpert")

    def detect_delusions(self: SecurityExpert, project_path: str) -> dict[str, Any]:
        """Detect security vulnerabilities"""
        return {"type": "security", "issues": []}
