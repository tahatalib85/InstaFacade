"""
InstaFacade - AI-powered image authenticity analyzer with Instagram integration
"""

__version__ = "1.0.0"
__author__ = "InstaFacade Team"

from .core.agent import InstaFacadeAgent
from .core.analyzer import InstaFacadeAnalyzer

__all__ = ["InstaFacadeAgent", "InstaFacadeAnalyzer"] 