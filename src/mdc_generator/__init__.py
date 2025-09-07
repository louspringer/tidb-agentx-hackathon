"""
MDC Generator Package
Python-based model and generator for .mdc files
"""

from .mdc_model import MDCFile, MDCFrontmatter, MDCGenerator

__version__ = "1.0.0"
__all__ = ["MDCFile", "MDCFrontmatter", "MDCGenerator"]
