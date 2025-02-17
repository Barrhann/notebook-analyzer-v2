"""
Core Package for Notebook Analyzer.

This package contains the core components for analyzing Jupyter notebooks:
- NotebookReader: Handles reading and parsing Jupyter notebooks
- AnalysisOrchestrator: Coordinates the analysis process

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:09:04
"""

from .notebook_reader import NotebookReader
from .analysis_orchestrator import AnalysisOrchestrator

__all__ = [
    'NotebookReader',
    'AnalysisOrchestrator'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Barrhann'
__email__ = 'barrhann@github.com'

# Package metadata
PACKAGE_INFO = {
    'name': 'notebook_analyzer.core',
    'description': 'Core components for Jupyter notebook analysis',
    'components': len(__all__),
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 01:09:04'
}

def get_package_info():
    """
    Get information about this package and its components.

    Returns:
        dict: Package metadata and component information
    """
    return {
        **PACKAGE_INFO,
        'components': {
            'NotebookReader': 'Handles reading and parsing of Jupyter notebooks',
            'AnalysisOrchestrator': 'Coordinates the analysis process'
        }
    }
