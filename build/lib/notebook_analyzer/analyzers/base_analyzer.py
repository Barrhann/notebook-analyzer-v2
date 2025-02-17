"""
Base Analyzer Module.

This module provides the abstract base class for all notebook analyzers.
It defines the interface and common functionality that all analyzers must implement.

Created by: Barrhann
Date: 2025-02-17
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

class AnalysisError(Exception):
    """Custom exception for analyzer-related errors."""
    pass

class BaseAnalyzer(ABC):
    """
    Abstract base class for all notebook analyzers.
    
    This class defines the interface that all analyzers must implement and provides
    common utility methods for analysis tasks. Each analyzer should focus on a specific
    aspect of the notebook analysis (e.g., code structure, visualization, etc.).

    Attributes:
        name (str): The name of the analyzer
        created_at (datetime): Timestamp when the analyzer was instantiated
        last_analysis (datetime): Timestamp of the last analysis performed
        
    Properties:
        is_active (bool): Indicates if the analyzer is currently active
        analysis_count (int): Number of analyses performed by this analyzer
    """

    def __init__(self, name: str):
        """
        Initialize the base analyzer.

        Args:
            name (str): The name of the analyzer
            
        Raises:
            ValueError: If name is empty or not a string
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Analyzer name must be a non-empty string")
            
        self.name = name.strip()
        self.created_at = datetime.utcnow()
        self.last_analysis = None
        self._analysis_count = 0
        self._is_active = True

    @property
    def is_active(self) -> bool:
        """Check if the analyzer is currently active."""
        return self._is_active

    @property
    def analysis_count(self) -> int:
        """Get the number of analyses performed."""
        return self._analysis_count

    @abstractmethod
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze the provided code and return analysis results.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing metrics and findings

        Raises:
            AnalysisError: If analysis fails
            ValueError: If code is empty or invalid
        """
        raise NotImplementedError("Analyzers must implement analyze method")

    @abstractmethod
    def get_metric_type(self) -> str:
        """
        Get the type of metric this analyzer produces.

        Returns:
            str: Either 'builder_mindset' or 'business_intelligence'
        """
        raise NotImplementedError("Analyzers must implement get_metric_type method")

    def validate_input(self, code: str) -> bool:
        """
        Validate the input code before analysis.

        Args:
            code (str): The code to validate

        Returns:
            bool: True if code is valid, False otherwise

        Raises:
            ValueError: If code is None
        """
        if code is None:
            raise ValueError("Code cannot be None")
        return bool(code.strip())

    def validate_results(self, results: Dict[str, Any]) -> bool:
        """
        Validate analysis results before returning them.

        Args:
            results (Dict[str, Any]): The analysis results to validate

        Returns:
            bool: True if results are valid, False otherwise
        """
        required_keys = {'score', 'findings', 'details'}
        return (
            isinstance(results, dict) and
            all(key in results for key in required_keys) and
            isinstance(results['score'], (int, float)) and
            0 <= results['score'] <= 100
        )

    def prepare_analysis(self, code: str) -> None:
        """
        Prepare for analysis by validating input and updating state.

        Args:
            code (str): The code to be analyzed

        Raises:
            ValueError: If code is invalid
            AnalysisError: If analyzer is not active
        """
        if not self.is_active:
            raise AnalysisError(f"Analyzer '{self.name}' is not active")
        
        if not self.validate_input(code):
            raise ValueError("Invalid or empty code provided")
            
        self.last_analysis = datetime.utcnow()
        self._analysis_count += 1

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the analyzer.

        Returns:
            Dict[str, Any]: Analyzer metadata including name, creation time,
                           last analysis time, and analysis count
        """
        return {
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'last_analysis': self.last_analysis.isoformat() if self.last_analysis else None,
            'analysis_count': self.analysis_count,
            'is_active': self.is_active,
            'metric_type': self.get_metric_type()
        }

    def deactivate(self) -> None:
        """Deactivate the analyzer."""
        self._is_active = False

    def activate(self) -> None:
        """Activate the analyzer."""
        self._is_active = True

    def __str__(self) -> str:
        """Return string representation of the analyzer."""
        return f"{self.name} Analyzer (Active: {self.is_active})"

    def __repr__(self) -> str:
        """Return detailed string representation of the analyzer."""
        return (f"{self.__class__.__name__}(name='{self.name}', "
                f"active={self.is_active}, analyses={self.analysis_count})")
