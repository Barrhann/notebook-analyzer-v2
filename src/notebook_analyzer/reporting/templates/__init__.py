"""
Report Templates Package.

This package provides templates for generating analysis reports in different formats.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:40:22
"""

from .html_template import HTMLTemplate
from .markdown_template import MarkdownTemplate

__all__ = [
    'HTMLTemplate',
    'MarkdownTemplate'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Barrhann'
__email__ = 'barrhann@github.com'

# Package metadata
PACKAGE_INFO = {
    'name': 'notebook_analyzer.reporting.templates',
    'description': 'Templates for notebook analysis report generation',
    'templates': len(__all__),
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 01:40:22'
}

# Template formats
TEMPLATE_FORMATS = {
    'html': {
        'class': 'HTMLTemplate',
        'description': 'Interactive HTML report with dynamic charts',
        'file_extension': '.html'
    },
    'markdown': {
        'class': 'MarkdownTemplate',
        'description': 'Markdown report with embedded images',
        'file_extension': '.md'
    }
}

def get_template_info() -> dict:
    """
    Get information about available templates.

    Returns:
        dict: Information about template formats and their descriptions
    """
    return TEMPLATE_FORMATS

def get_available_templates() -> list:
    """
    Get list of all available template classes.

    Returns:
        list: Names of all available template classes
    """
    return __all__

def get_template_by_format(format_name: str) -> type:
    """
    Get template class by format name.

    Args:
        format_name (str): Name of the format (e.g., 'html', 'markdown')

    Returns:
        type: Template class

    Raises:
        ValueError: If format name is not found
    """
    if format_name not in TEMPLATE_FORMATS:
        raise ValueError(f"Format '{format_name}' not found")
    template_class = TEMPLATE_FORMATS[format_name]['class']
    return globals()[template_class]

def get_file_extension(format_name: str) -> str:
    """
    Get file extension for a template format.

    Args:
        format_name (str): Name of the format (e.g., 'html', 'markdown')

    Returns:
        str: File extension including the dot

    Raises:
        ValueError: If format name is not found
    """
    if format_name not in TEMPLATE_FORMATS:
        raise ValueError(f"Format '{format_name}' not found")
    return TEMPLATE_FORMATS[format_name]['file_extension']
