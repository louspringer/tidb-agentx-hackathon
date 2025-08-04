from typing import List, Dict, Tuple, Optional, Union, Any

"""
MDC Generator Package
Python-based model and generator for .mdc files
"""

from .mdc_model import MDCFile, MDCFrontmatter, MDCGenerator

__version__: str = "1.0.0"
__all__: List[Any] = ["MDCFile", "MDCFrontmatter", "MDCGenerator"]
