"""
Notebook Analyzer Reporting Package.

This package provides reporting capabilities for notebook analysis results,
including formatters, templates, and report generation functionality.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:44:23
"""

from .report_generator import ReportGenerator
from .templates import HTMLTemplate, MarkdownTemplate
from .formatters.builder_mindset import (
    CodeFormattingFormatter,
    CodeStructureFormatter,
    CodeCommentsFormatter,
    CodeConcisenessFormatter,
    CodeReusabilityFormatter,
    AdvancedTechniquesFormatter,
    DatasetJoinFormatter
)
from .formatters.business_intelligence import (
    VisualizationTypesFormatter,
    VisualizationFormattingFormatter
)

__all__ = [
    # Main report generator
    'ReportGenerator',
    
    # Templates
    'HTMLTemplate',
    'MarkdownTemplate',
    
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
    'name': 'notebook_analyzer.reporting',
    'description': 'Reporting package for notebook analysis',
    'components': {
        'formatters': {
            'builder_mindset': len([f for f in __all__ if 'Formatter' in f and f not in
                                  ['VisualizationTypesFormatter', 'VisualizationFormattingFormatter']]),
            'business_intelligence': len([f for f in __all__ if f in
                                       ['VisualizationTypesFormatter', 'VisualizationFormattingFormatter']])
        },
        'templates': len([t for t in __all__ if 'Template' in t])
    },
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 01:44:23'
}

def get_available_formatters() -> dict:
    """
    Get information about available formatters.

    Returns:
        dict: Dictionary containing available formatters by category
    """
    return {
        'builder_mindset': [
            'CodeFormattingFormatter',
            'CodeStructureFormatter',
            'CodeCommentsFormatter',
            'CodeConcisenessFormatter',
            'CodeReusabilityFormatter',
            'AdvancedTechniquesFormatter',
            'DatasetJoinFormatter'
        ],
        'business_intelligence': [
            'VisualizationTypesFormatter',
            'VisualizationFormattingFormatter'
        ]
    }

def get_available_templates() -> list:
    """
    Get list of available report templates.

    Returns:
        list: List of available template names
    """
    return ['HTMLTemplate', 'MarkdownTemplate']

def get_formatter_by_name(formatter_name: str) -> type:
    """
    Get formatter class by name.

    Args:
        formatter_name (str): Name of the formatter class

    Returns:
        type: Formatter class

    Raises:
        ValueError: If formatter name is not found
    """
    if formatter_name not in __all__:
        raise ValueError(f"Formatter '{formatter_name}' not found")
    return globals()[formatter_name]

def get_template_by_name(template_name: str) -> type:
    """
    Get template class by name.

    Args:
        template_name (str): Name of the template class

    Returns:
        type: Template class

    Raises:
        ValueError: If template name is not found
    """
    if template_name not in get_available_templates():
        raise ValueError(f"Template '{template_name}' not found")
    return globals()[template_name]

def create_report_generator(output_dir: str = "reports") -> ReportGenerator:
    """
    Create a new report generator instance.

    Args:
        output_dir (str): Directory for storing generated reports

    Returns:
        ReportGenerator: Configured report generator instance
    """
    return ReportGenerator(output_dir)
