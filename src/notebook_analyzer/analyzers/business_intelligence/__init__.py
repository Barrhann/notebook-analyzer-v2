"""
Business Intelligence Analyzers Package.

This package contains analyzers focused on data visualization aspects of Jupyter notebooks,
including visualization types and formatting.

Analyzers:
    - VisualizationTypesAnalyzer: Evaluates visualization choices and techniques
    - VisualizationFormattingAnalyzer: Analyzes visualization styling and formatting

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:03:53
"""

from .visualization_types import VisualizationTypesAnalyzer
from .visualization_formatting import VisualizationFormattingAnalyzer

__all__ = [
    'VisualizationTypesAnalyzer',
    'VisualizationFormattingAnalyzer',
]

# Version information
__version__ = '1.0.0'
__author__ = 'Barrhann'
__email__ = 'barrhann@github.com'

# Package metadata
PACKAGE_INFO = {
    'name': 'business_intelligence',
    'description': 'Analyzers for evaluating visualization aspects of notebooks',
    'analyzers': len(__all__),
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 01:03:53'
}

def get_all_analyzers():
    """
    Get a list of all available analyzer classes in this package.

    Returns:
        List[type]: List of analyzer classes
    """
    return [
        VisualizationTypesAnalyzer,
        VisualizationFormattingAnalyzer
    ]

def create_analyzer(analyzer_name: str):
    """
    Create an instance of a specific analyzer by name.

    Args:
        analyzer_name (str): Name of the analyzer to create

    Returns:
        BaseAnalyzer: Instance of the requested analyzer

    Raises:
        ValueError: If analyzer_name is not recognized
    """
    analyzers = {
        'visualization_types': VisualizationTypesAnalyzer,
        'visualization_formatting': VisualizationFormattingAnalyzer
    }
    
    if analyzer_name not in analyzers:
        raise ValueError(
            f"Unknown analyzer: {analyzer_name}. "
            f"Available analyzers: {', '.join(analyzers.keys())}"
        )
        
    return analyzers[analyzer_name]()

def get_package_info():
    """
    Get information about this package and its analyzers.

    Returns:
        dict: Package metadata and analyzer information
    """
    analyzer_info = []
    for analyzer_class in get_all_analyzers():
        instance = analyzer_class()
        analyzer_info.append({
            'name': instance.name,
            'type': 'business_intelligence',
            'description': instance.__doc__.split('\n')[0] if instance.__doc__ else 'No description'
        })
    
    return {
        **PACKAGE_INFO,
        'available_analyzers': analyzer_info
    }
