"""
Notebook Analyzer Package.

This package provides functionality for analyzing Jupyter notebooks,
focusing on code quality, builder mindset patterns, and business intelligence aspects.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 02:35:08
"""

from .analyzers.base_analyzer import BaseAnalyzer
from .analyzers import (
    builder_mindset,
    business_intelligence
)
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
from .cli.main import main

__all__ = [
    # Core components
    'BaseAnalyzer',
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
    'main'
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
    'last_updated': '2025-02-17 02:35:08',
    'components': {
        'analyzers': { 
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
            'templates': ['html', 'markdown']
        },
        'cli': {
            'description': 'Command-line interface',
            'entry_point': 'main'
        }
    }
}

def get_version() -> str:
    """Get the package version."""
    return __version__

def get_package_info() -> dict:
    """Get package information."""
    return PACKAGE_INFO

def create_analyzer(category: str = None) -> 'BaseAnalyzer':
    """
    Create a new analyzer instance.

    Args:
        category (str, optional): Category of analyzer to create 
                               ('builder_mindset' or 'business_intelligence')

    Returns:
        BaseAnalyzer: Configured analyzer instance
    """
    if category == 'builder_mindset':
        return builder_mindset.create_analyzer()
    elif category == 'business_intelligence':
        return business_intelligence.create_analyzer()
    else:
        return BaseAnalyzer("Generic")
