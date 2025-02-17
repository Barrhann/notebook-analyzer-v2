"""
Builder Mindset Formatters Package.

This package contains formatters for analyzing and reporting on builder mindset
aspects of notebook code, including code structure, formatting, reusability,
and advanced techniques.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:29:03
"""

from .code_formatting_formatter import CodeFormattingFormatter
from .code_structure_formatter import CodeStructureFormatter
from .code_comments_formatter import CodeCommentsFormatter
from .code_conciseness_formatter import CodeConcisenessFormatter
from .code_reusability_formatter import CodeReusabilityFormatter
from .advanced_techniques_formatter import AdvancedTechniquesFormatter
from .dataset_join_formatter import DatasetJoinFormatter

__all__ = [
    'CodeFormattingFormatter',
    'CodeStructureFormatter',
    'CodeCommentsFormatter',
    'CodeConcisenessFormatter',
    'CodeReusabilityFormatter',
    'AdvancedTechniquesFormatter',
    'DatasetJoinFormatter'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Barrhann'
__email__ = 'barrhann@github.com'

# Package metadata
PACKAGE_INFO = {
    'name': 'notebook_analyzer.reporting.formatters.builder_mindset',
    'description': 'Formatters for builder mindset analysis aspects',
    'formatters': len(__all__),
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 01:29:03'
}

# Formatter categories
FORMATTER_CATEGORIES = {
    'code_quality': [
        'CodeFormattingFormatter',
        'CodeStructureFormatter',
        'CodeCommentsFormatter',
        'CodeConcisenessFormatter'
    ],
    'code_design': [
        'CodeReusabilityFormatter',
        'AdvancedTechniquesFormatter'
    ],
    'data_handling': [
        'DatasetJoinFormatter'
    ]
}

def get_formatter_info() -> dict:
    """
    Get information about available formatters.

    Returns:
        dict: Information about formatter categories and their descriptions
    """
    return {
        'code_quality': {
            'description': 'Formatters for code quality metrics',
            'formatters': FORMATTER_CATEGORIES['code_quality']
        },
        'code_design': {
            'description': 'Formatters for code design and architecture',
            'formatters': FORMATTER_CATEGORIES['code_design']
        },
        'data_handling': {
            'description': 'Formatters for data manipulation patterns',
            'formatters': FORMATTER_CATEGORIES['data_handling']
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
