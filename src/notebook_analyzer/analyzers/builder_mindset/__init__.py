"""
Builder Mindset Analyzers Package.

This package contains analyzers focused on evaluating code quality aspects that reflect
a builder's mindset - emphasizing code structure, reusability, and advanced techniques.

Analyzers:
    - CodeFormattingAnalyzer: Evaluates code style and formatting
    - CodeCommentsAnalyzer: Analyzes documentation and comments
    - CodeConcisenessAnalyzer: Evaluates code brevity and clarity
    - CodeStructureAnalyzer: Analyzes code organization and patterns
    - CodeReusabilityAnalyzer: Evaluates code modularity and reuse
    - DatasetJoinAnalyzer: Analyzes data joining operations
    - AdvancedTechniquesAnalyzer: Evaluates usage of advanced programming features

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 00:49:26
"""

from .code_formatting import CodeFormattingAnalyzer
from .code_comments import CodeCommentsAnalyzer
from .code_conciseness import CodeConcisenessAnalyzer
from .code_structure import CodeStructureAnalyzer
from .code_reusability import CodeReusabilityAnalyzer
from .dataset_join import DatasetJoinAnalyzer
from .advanced_techniques import AdvancedTechniquesAnalyzer

__all__ = [
    'CodeFormattingAnalyzer',
    'CodeCommentsAnalyzer',
    'CodeConcisenessAnalyzer',
    'CodeStructureAnalyzer',
    'CodeReusabilityAnalyzer',
    'DatasetJoinAnalyzer',
    'AdvancedTechniquesAnalyzer',
]

# Version information
__version__ = '1.0.0'
__author__ = 'Barrhann'
__email__ = 'barrhann@github.com'

# Package metadata
PACKAGE_INFO = {
    'name': 'builder_mindset',
    'description': 'Analyzers for evaluating code quality with a builder mindset',
    'analyzers': len(__all__),
    'version': __version__,
    'author': __author__,
    'last_updated': '2025-02-17 00:49:26'
}

def get_all_analyzers():
    """
    Get a list of all available analyzer classes in this package.

    Returns:
        List[type]: List of analyzer classes
    """
    return [
        CodeFormattingAnalyzer,
        CodeCommentsAnalyzer,
        CodeConcisenessAnalyzer,
        CodeStructureAnalyzer,
        CodeReusabilityAnalyzer,
        DatasetJoinAnalyzer,
        AdvancedTechniquesAnalyzer
    ]

def create_analyzer(analyzer_name: str):
    """
    Create an instance of a specific analyzer by name.

    Args:
        analyzer_name (str): Name of the analyzer to create

    Returns:
        BaseAnalyzer: Instance of the requested analyzer

    Raises:
        ValueError: If analyzer_name is not recognized
    """
    analyzers = {
        'formatting': CodeFormattingAnalyzer,
        'comments': CodeCommentsAnalyzer,
        'conciseness': CodeConcisenessAnalyzer,
        'structure': CodeStructureAnalyzer,
        'reusability': CodeReusabilityAnalyzer,
        'dataset_join': DatasetJoinAnalyzer,
        'advanced_techniques': AdvancedTechniquesAnalyzer
    }
    
    if analyzer_name not in analyzers:
        raise ValueError(
            f"Unknown analyzer: {analyzer_name}. "
            f"Available analyzers: {', '.join(analyzers.keys())}"
        )
        
    return analyzers[analyzer_name]()

def get_package_info():
    """
    Get information about this package and its analyzers.

    Returns:
        dict: Package metadata and analyzer information
    """
    analyzer_info = []
    for analyzer_class in get_all_analyzers():
        instance = analyzer_class()
        analyzer_info.append({
            'name': instance.name,
            'type': 'builder_mindset',
            'description': instance.__doc__.split('\n')[0] if instance.__doc__ else 'No description'
        })
    
    return {
        **PACKAGE_INFO,
        'available_analyzers': analyzer_info
    }
