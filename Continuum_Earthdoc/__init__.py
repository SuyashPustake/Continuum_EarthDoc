"""
Verra PDD Generator
A professional tool for generating Verra VCS Project Description Documents
"""

__version__ = "1.0.0"
__author__ = "Continuum"

from .agents import PDDAgent, METHODOLOGY_DATABASE, METHODOLOGY_CATEGORIES

__all__ = [
    "PDDAgent",
    "METHODOLOGY_DATABASE", 
    "METHODOLOGY_CATEGORIES",
    "__version__"
]
