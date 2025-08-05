"""
Model-Driven Projection Component

This component implements the radical model-driven architecture where all artifacts
are projected from a central model rather than managed individually.

Key Features:
- Granular node extraction and modeling
- Functional equivalence projection
- Zero duplication architecture
- Perfect order preservation
- Complete test compatibility

Components:
- level1_granular_nodes.py: Core granular node system
- final_projection_system.py: Production projection system
- improved_projection_system.py: Enhanced projection with fixes
- test_*.py: Equivalence testing suite
- projected_artifacts/: Generated artifacts directory
- *_REPORT.md: Comprehensive analysis reports
"""

from .final_projection_system import FinalProjectionSystem
from .level1_granular_nodes import (
    CodeNode,
    DependencyResolver,
    ModelRegistry,
    NodeProjector,
)

__version__ = "1.0.0"
__author__ = "OpenFlow Playground Team"

__all__ = [
    "CodeNode",
    "DependencyResolver",
    "NodeProjector",
    "ModelRegistry",
    "FinalProjectionSystem",
]
