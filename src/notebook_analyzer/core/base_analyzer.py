"""Base analyzer class that provides common functionality."""
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime

class BaseAnalyzer(ABC):
    """Base class for all analyzers."""
    
    def __init__(self):
        self.complexity_indicators = {
            'loops': ['for', 'while'],
            'conditionals': ['if', 'elif', 'else'],
            'comprehensions': ['for', 'if'],
            'try_except': ['try', 'except', 'finally']
        }
        self.creation_time = datetime.utcnow()

    @abstractmethod
    def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """
        Abstract method that all analyzers must implement.
        
        Args:
            code: The source code to analyze
            **kwargs: Additional parameters for specific analyzers
            
        Returns:
            Dict containing analysis results
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Get analyzer metadata."""
        return {
            'analyzer_type': self.__class__.__name__,
            'creation_time': self.creation_time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0.0'
        }
