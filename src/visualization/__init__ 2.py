#!/usr/bin/env python3
"""
Visualization module for OpenFlow Playground
SVG-centric visualization system for project analysis
"""

from .svg_engine import SVGVisualizationConfig, SVGVisualizationEngine

__version__ = "1.0.0"
__all__ = ["SVGVisualizationEngine", "SVGVisualizationConfig"]
