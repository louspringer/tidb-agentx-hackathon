#!/usr/bin/env python3
"""
Represents an AST node with metadata
"""

from dataclasses import *
from dataclasses import dataclass
from typing import *


@dataclass
class ASTNode:
    """
    Represents an AST node with metadata
    """

    def __init__(self):
        # TODO: Initialize based on requirements: ['dataclass', 'metadata support', 'parent-child relationships']
        pass

    def __post_init__(self) -> None:
        """
        Initialize default values
        """
        # TODO: Implement based on requirements: []
