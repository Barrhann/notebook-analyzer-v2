"""
Models Package for Notebook Analyzer.

This package contains the data models used throughout the notebook analyzer:
- AnalysisResult: Represents analysis results
- MetricBlock: Represents metric collections
- ReportData: Represents analysis report data

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:15:01
"""

from .analysis_result import AnalyzerResult, NotebookAnalysisResult
from .metric_block import MetricBlock, MetricBlockCollection
from .report_data import ReportSection, ReportData

__all__ = [
    'AnalyzerResult',
    'NotebookAnalysisResult',
    'MetricBlock',
    'MetricBlockCollection',
    'ReportSection',
    'ReportData'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Barrhann'
__email__ = 'barrhann@github.com'

# Package metadata
PACKAGE_INFO = {
    'name': 'notebook_analyzer.models',
    'description': 'Data models for notebook analysis',
    'models': len(__all__),
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 01:15:01'
}

def get_package_info():
    """
    Get information about this package and its models.

    Returns:
        dict: Package metadata and model information
    """
    return {
        **PACKAGE_INFO,
        'models': {
            'AnalyzerResult': 'Individual analyzer results',
            'NotebookAnalysisResult': 'Complete notebook analysis results',
            'MetricBlock': 'Collection of related metrics',
            'MetricBlockCollection': 'Collection of metric blocks',
            'ReportSection': 'Section of analysis report',
            'ReportData': 'Complete analysis report data'
        }
    }
