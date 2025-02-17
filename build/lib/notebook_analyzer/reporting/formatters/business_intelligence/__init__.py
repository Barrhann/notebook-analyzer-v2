"""
Business Intelligence Formatters Package.

This package contains formatters for analyzing and reporting on business intelligence
aspects of notebook code, including visualization types, formatting, and data presentation.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:33:54
"""

from .visualization_types_formatter import VisualizationTypesFormatter
from .visualization_formatting_formatter import VisualizationFormattingFormatter

__all__ = [
    'VisualizationTypesFormatter',
    'VisualizationFormattingFormatter'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Barrhann'
__email__ = 'barrhann@github.com'

# Package metadata
PACKAGE_INFO = {
    'name': 'notebook_analyzer.reporting.formatters.business_intelligence',
    'description': 'Formatters for business intelligence analysis aspects',
    'formatters': len(__all__),
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 01:33:54'
}

# Formatter categories
FORMATTER_CATEGORIES = {
    'visualization': [
        'VisualizationTypesFormatter',
        'VisualizationFormattingFormatter'
    ]
}

def get_formatter_info() -> dict:
    """
    Get information about available formatters.

    Returns:
        dict: Information about formatter categories and their descriptions
    """
    return {
        'visualization': {
            'description': 'Formatters for analyzing visualization practices',
            'formatters': FORMATTER_CATEGORIES['visualization']
        }
    }

def get_available_formatters() -> list:
    """
    Get list of all available formatters.

    Returns:
        list: Names of all available formatters
    """
    return __all__

def get_formatter_by_name(formatter_name: str) -> type:
    """
    Get formatter class by name.

    Args:
        formatter_name (str): Name of the formatter

    Returns:
        type: Formatter class

    Raises:
        ValueError: If formatter name is not found
    """
    formatters = globals()
    if formatter_name not in formatters:
        raise ValueError(f"Formatter '{formatter_name}' not found")
    return formatters[formatter_name]

def get_formatters_by_category(category: str) -> list:
    """
    Get formatters for a specific category.

    Args:
        category (str): Category name

    Returns:
        list: List of formatter names in the category

    Raises:
        ValueError: If category is not found
    """
    if category not in FORMATTER_CATEGORIES:
        raise ValueError(f"Category '{category}' not found")
    return FORMATTER_CATEGORIES[category]
