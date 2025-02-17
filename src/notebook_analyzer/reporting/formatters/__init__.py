"""
Formatters Package.

This package provides formatters for converting analysis results into
structured report sections. It includes both builder mindset and
business intelligence formatters.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 02:02:52
"""

from .base_formatter import BaseFormatter, FormattedSection
from .builder_mindset import (
    CodeFormattingFormatter,
    CodeStructureFormatter,
    CodeCommentsFormatter,
    CodeConcisenessFormatter,
    CodeReusabilityFormatter,
    AdvancedTechniquesFormatter,
    DatasetJoinFormatter
)
from .business_intelligence import (
    VisualizationTypesFormatter,
    VisualizationFormattingFormatter
)

__all__ = [
    # Base classes
    'BaseFormatter',
    'FormattedSection',
    
    # Builder mindset formatters
    'CodeFormattingFormatter',
    'CodeStructureFormatter',
    'CodeCommentsFormatter',
    'CodeConcisenessFormatter',
    'CodeReusabilityFormatter',
    'AdvancedTechniquesFormatter',
    'DatasetJoinFormatter',
    
    # Business intelligence formatters
    'VisualizationTypesFormatter',
    'VisualizationFormattingFormatter'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Barrhann'
__email__ = 'barrhann@github.com'

# Package metadata
PACKAGE_INFO = {
    'name': 'notebook_analyzer.reporting.formatters',
    'description': 'Formatters for notebook analysis results',
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 02:02:52',
    'components': {
        'base': {
            'description': 'Base formatter functionality',
            'classes': ['BaseFormatter', 'FormattedSection']
        },
        'builder_mindset': {
            'description': 'Builder mindset metric formatters',
            'formatters': [
                'CodeFormattingFormatter',
                'CodeStructureFormatter',
                'CodeCommentsFormatter',
                'CodeConcisenessFormatter',
                'CodeReusabilityFormatter',
                'AdvancedTechniquesFormatter',
                'DatasetJoinFormatter'
            ]
        },
        'business_intelligence': {
            'description': 'Business intelligence metric formatters',
            'formatters': [
                'VisualizationTypesFormatter',
                'VisualizationFormattingFormatter'
            ]
        }
    }
}

def get_all_formatters() -> list:
    """
    Get a list of all available formatters.

    Returns:
        list: Names of all available formatters
    """
    return [
        name for name in __all__
        if name.endswith('Formatter') and name != 'BaseFormatter'
    ]

def get_formatter_by_category(category: str) -> list:
    """
    Get formatters for a specific category.

    Args:
        category (str): Category name ('builder_mindset' or 'business_intelligence')

    Returns:
        list: List of formatter names in the category

    Raises:
        ValueError: If category is not recognized
    """
    if category not in PACKAGE_INFO['components']:
        raise ValueError(f"Unknown category: {category}")
    
    return PACKAGE_INFO['components'][category]['formatters']

def get_package_info() -> dict:
    """
    Get information about the formatters package.

    Returns:
        dict: Package information and capabilities
    """
    return PACKAGE_INFO

def get_formatter_categories() -> list:
    """
    Get available formatter categories.

    Returns:
        list: List of available formatter categories
    """
    return [
        category for category in PACKAGE_INFO['components']
        if category != 'base'
    ]

def create_formatter(formatter_name: str) -> 'BaseFormatter':
    """
    Create a formatter instance by name.

    Args:
        formatter_name (str): Name of the formatter to create

    Returns:
        BaseFormatter: Instance of the requested formatter

    Raises:
        ValueError: If formatter name is not recognized
    """
    if formatter_name not in __all__:
        raise ValueError(f"Unknown formatter: {formatter_name}")
    
    formatter_class = globals()[formatter_name]
    return formatter_class()

def get_formatter_info(formatter_name: str) -> dict:
    """
    Get information about a specific formatter.

    Args:
        formatter_name (str): Name of the formatter

    Returns:
        dict: Formatter information

    Raises:
        ValueError: If formatter name is not recognized
    """
    if formatter_name not in __all__:
        raise ValueError(f"Unknown formatter: {formatter_name}")
    
    formatter = create_formatter(formatter_name)
    return formatter.get_metadata()
