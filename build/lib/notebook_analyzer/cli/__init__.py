"""
Notebook Analyzer CLI Package.

This package provides command-line interface functionality for the notebook analyzer,
allowing users to analyze notebooks and generate reports through the command line.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:47:02
"""

from .main import main

__all__ = ['main']

# Version information
__version__ = '1.0.0'
__author__ = 'Barrhann'
__email__ = 'barrhann@github.com'

# Package metadata
PACKAGE_INFO = {
    'name': 'notebook_analyzer.cli',
    'description': 'Command-line interface for notebook analysis',
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 01:47:02',
    'supported_formats': {
        'input': ['.ipynb'],
        'output': ['html', 'markdown']
    },
    'analysis_categories': [
        'builder_mindset',
        'business_intelligence'
    ]
}

def get_cli_info() -> dict:
    """
    Get information about the CLI package.

    Returns:
        dict: CLI package information and capabilities
    """
    return PACKAGE_INFO

def run_cli():
    """
    Entry point for running the CLI application.
    
    This function serves as a convenient wrapper around the main CLI function.
    """
    main()

def get_supported_formats() -> dict:
    """
    Get supported input and output formats.

    Returns:
        dict: Dictionary of supported input and output formats
    """
    return PACKAGE_INFO['supported_formats']

def get_analysis_categories() -> list:
    """
    Get available analysis categories.

    Returns:
        list: List of available analysis categories
    """
    return PACKAGE_INFO['analysis_categories']
