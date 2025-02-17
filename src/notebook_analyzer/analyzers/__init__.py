"""
Notebook Analyzers Package.

This package contains analyzer modules for evaluating different aspects of Jupyter notebooks.
It includes analyzers for builder mindset and business intelligence aspects.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 22:51:46
"""

from .base_analyzer import BaseAnalyzer, AnalysisError
from .notebook_analyzer import NotebookAnalyzer  # Added import
from .builder_mindset import (  # Explicit imports for better code completion
    CodeFormattingAnalyzer,
    CodeStructureAnalyzer,
    CodeCommentsAnalyzer,
    CodeConcisenessAnalyzer,
    CodeReusabilityAnalyzer,
    AdvancedTechniquesAnalyzer,
    DatasetJoinAnalyzer
)
from .business_intelligence import (  # Explicit imports for better code completion
    VisualizationTypesAnalyzer,
    VisualizationFormattingAnalyzer
)
from . import builder_mindset
from . import business_intelligence

__all__ = [
    # Base classes
    'BaseAnalyzer',
    'AnalysisError',
    'NotebookAnalyzer',  # Added to exports
    
    # Categories
    'builder_mindset',
    'business_intelligence',
    
    # Builder mindset analyzers
    'CodeFormattingAnalyzer',
    'CodeStructureAnalyzer',
    'CodeCommentsAnalyzer',
    'CodeConcisenessAnalyzer',
    'CodeReusabilityAnalyzer',
    'AdvancedTechniquesAnalyzer',
    'DatasetJoinAnalyzer',
    
    # Business intelligence analyzers
    'VisualizationTypesAnalyzer',
    'VisualizationFormattingAnalyzer'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Barrhann'
__email__ = 'barrhann@github.com'

# Package metadata
PACKAGE_INFO = {
    'name': 'notebook_analyzer',
    'description': 'Jupyter notebook analysis toolkit for builder mindset and business intelligence',
    'categories': [
        'builder_mindset',
        'business_intelligence'
    ],
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 22:51:46'
}

def get_all_analyzers():
    """
    Get a list of all available analyzer classes across all categories.

    Returns:
        Dict[str, List[type]]: Dictionary mapping categories to their analyzer classes
    """
    return {
        'builder_mindset': builder_mindset.get_all_analyzers(),
        'business_intelligence': business_intelligence.get_all_analyzers()
    }

def create_analyzer(category: str, analyzer_name: str):
    """
    Create an instance of a specific analyzer by category and name.

    Args:
        category (str): Category of the analyzer ('builder_mindset' or 'business_intelligence')
        analyzer_name (str): Name of the analyzer to create

    Returns:
        BaseAnalyzer: Instance of the requested analyzer

    Raises:
        ValueError: If category or analyzer_name is not recognized
    """
    categories = {
        'builder_mindset': builder_mindset.create_analyzer,
        'business_intelligence': business_intelligence.create_analyzer
    }
    
    if category not in categories:
        raise ValueError(
            f"Unknown category: {category}. "
            f"Available categories: {', '.join(categories.keys())}"
        )
        
    return categories[category](analyzer_name)

def get_package_info():
    """
    Get comprehensive information about this package and all its analyzers.

    Returns:
        dict: Package metadata and analyzer information by category
    """
    category_info = {}
    for category in PACKAGE_INFO['categories']:
        module = globals()[category]
        category_info[category] = module.get_package_info()
    
    return {
        **PACKAGE_INFO,
        'categories': category_info
    }
