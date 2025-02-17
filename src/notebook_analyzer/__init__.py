"""
Notebook Analyzer Package.

This package provides functionality for analyzing Jupyter notebooks,
focusing on code quality, builder mindset patterns, and business intelligence aspects.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:47:50
"""

from .analyzer import NotebookAnalyzer
from .reporting import (
    ReportGenerator,
    HTMLTemplate,
    MarkdownTemplate,
    # Builder Mindset Formatters
    CodeFormattingFormatter,
    CodeStructureFormatter,
    CodeCommentsFormatter,
    CodeConcisenessFormatter,
    CodeReusabilityFormatter,
    AdvancedTechniquesFormatter,
    DatasetJoinFormatter,
    # Business Intelligence Formatters
    VisualizationTypesFormatter,
    VisualizationFormattingFormatter
)
from .cli import main as cli_main

__all__ = [
    # Core components
    'NotebookAnalyzer',
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
    'VisualizationFormattingFormatter',
    
    # CLI
    'cli_main'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Barrhann'
__email__ = 'barrhann@github.com'

# Package metadata
PACKAGE_INFO = {
    'name': 'notebook_analyzer',
    'description': 'A tool for analyzing Jupyter notebooks',
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 01:47:50',
    'components': {
        'analyzer': {
            'description': 'Core analysis functionality',
            'metrics': {
                'builder_mindset': [
                    'code_formatting',
                    'code_structure',
                    'code_comments',
                    'code_conciseness',
                    'code_reusability',
                    'advanced_techniques',
                    'dataset_join'
                ],
                'business_intelligence': [
                    'visualization_types',
                    'visualization_formatting'
                ]
            }
        },
        'reporting': {
            'description': 'Report generation functionality',
            'templates': ['html', 'markdown'],
            'formatters': len([f for f in __all__ if 'Formatter' in f])
        },
        'cli': {
            'description': 'Command-line interface',
            'entry_point': 'cli_main'
        }
    }
}

def get_version() -> str:
    """
    Get the package version.

    Returns:
        str: Package version
    """
    return __version__

def get_package_info() -> dict:
    """
    Get information about the package.

    Returns:
        dict: Package information and capabilities
    """
    return PACKAGE_INFO

def create_analyzer() -> NotebookAnalyzer:
    """
    Create a new notebook analyzer instance.

    Returns:
        NotebookAnalyzer: Configured analyzer instance
    """
    return NotebookAnalyzer()

def create_report_generator(output_dir: str = "reports") -> ReportGenerator:
    """
    Create a new report generator instance.

    Args:
        output_dir (str): Directory for storing generated reports

    Returns:
        ReportGenerator: Configured report generator instance
    """
    return ReportGenerator(output_dir)

def run_cli():
    """
    Run the command-line interface.

    This function serves as a convenient entry point for running the CLI.
    """
    cli_main()

def get_available_metrics() -> dict:
    """
    Get information about available metrics.

    Returns:
        dict: Dictionary containing available metrics by category
    """
    return PACKAGE_INFO['components']['analyzer']['metrics']

def get_supported_templates() -> list:
    """
    Get list of supported report templates.

    Returns:
        list: List of supported template formats
    """
    return PACKAGE_INFO['components']['reporting']['templates']
