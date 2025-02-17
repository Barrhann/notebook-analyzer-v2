"""
Base Formatter Module.

This module provides the base formatter class that all specific formatters
must inherit from. It defines the interface and common functionality for
formatting analysis results into report sections.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 02:00:43
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class FormattedSection:
    """
    Data class representing a formatted section in the report.

    Attributes:
        title (str): Section title
        description (str): Section description
        score (int): Section score (0-100)
        metrics (Dict[str, Any]): Detailed metrics
        recommendations (list[str]): List of improvement recommendations
        category (str): Metric category (e.g., 'builder_mindset', 'business_intelligence')
        subsections (Optional[list[Dict[str, Any]]]): Optional nested subsections
    """
    title: str
    description: str
    score: int
    metrics: Dict[str, Any]
    recommendations: list[str]
    category: str
    subsections: Optional[list[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the formatted section to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the section
        """
        result = {
            'title': self.title,
            'description': self.description,
            'score': self.score,
            'metrics': self.metrics,
            'recommendations': self.recommendations,
            'category': self.category
        }
        
        if self.subsections:
            result['subsections'] = self.subsections
            
        return result


class BaseFormatter(ABC):
    """
    Base class for all metric formatters.

    This class defines the interface that all formatters must implement
    and provides common functionality for formatting analysis results
    into report sections.
    """

    def __init__(self):
        """Initialize the formatter."""
        self._score_weights = self._get_score_weights()
        self._metric_descriptions = self._get_metric_descriptions()

    @property
    @abstractmethod
    def formatter_name(self) -> str:
        """
        Get the name of the formatter.

        Returns:
            str: Formatter name
        """
        pass

    @property
    @abstractmethod
    def formatter_description(self) -> str:
        """
        Get the description of what this formatter analyzes.

        Returns:
            str: Formatter description
        """
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """
        Get the category this formatter belongs to.

        Returns:
            str: Category name ('builder_mindset' or 'business_intelligence')
        """
        pass

    @abstractmethod
    def _get_score_weights(self) -> Dict[str, float]:
        """
        Define the weights for different aspects of the score calculation.

        Returns:
            Dict[str, float]: Dictionary mapping metric names to their weights
        """
        pass

    @abstractmethod
    def _get_metric_descriptions(self) -> Dict[str, str]:
        """
        Define descriptions for each metric this formatter handles.

        Returns:
            Dict[str, str]: Dictionary mapping metric names to their descriptions
        """
        pass

    @abstractmethod
    def _calculate_score(self, metrics: Dict[str, Any]) -> int:
        """
        Calculate the overall score for this section.

        Args:
            metrics (Dict[str, Any]): Metrics to calculate score from

        Returns:
            int: Calculated score (0-100)
        """
        pass

    @abstractmethod
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> list[str]:
        """
        Generate improvement recommendations based on metrics.

        Args:
            metrics (Dict[str, Any]): Metrics to generate recommendations from

        Returns:
            list[str]: List of recommendations
        """
        pass

    def format_metrics(self, metrics: Dict[str, Any]) -> FormattedSection:
        """
        Format metrics into a report section.

        This method implements the common formatting logic and delegates
        specific calculations to abstract methods that must be implemented
        by subclasses.

        Args:
            metrics (Dict[str, Any]): Raw metrics to format

        Returns:
            FormattedSection: Formatted section for the report
        """
        score = self._calculate_score(metrics)
        recommendations = self._generate_recommendations(metrics)

        return FormattedSection(
            title=self.formatter_name,
            description=self.formatter_description,
            score=score,
            metrics=self._format_detailed_metrics(metrics),
            recommendations=recommendations,
            category=self.category
        )

    def _format_detailed_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format detailed metrics with descriptions.

        Args:
            metrics (Dict[str, Any]): Raw metrics to format

        Returns:
            Dict[str, Any]: Formatted metrics with descriptions
        """
        formatted_metrics = {}
        
        for metric_name, value in metrics.items():
            formatted_metrics[metric_name] = {
                'value': value,
                'description': self._metric_descriptions.get(
                    metric_name,
                    f"Metric: {metric_name}"
                ),
                'weight': self._score_weights.get(metric_name, 0)
            }
            
        return formatted_metrics

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get formatter metadata.

        Returns:
            Dict[str, Any]: Formatter metadata including name, description,
                           category, and supported metrics
        """
        return {
            'name': self.formatter_name,
            'description': self.formatter_description,
            'category': self.category,
            'metrics': {
                name: {
                    'description': desc,
                    'weight': self._score_weights.get(name, 0)
                }
                for name, desc in self._metric_descriptions.items()
            }
        }

    def validate_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Validate that all required metrics are present.

        Args:
            metrics (Dict[str, Any]): Metrics to validate

        Returns:
            bool: True if all required metrics are present, False otherwise
        """
        required_metrics = set(self._score_weights.keys())
        provided_metrics = set(metrics.keys())
        return required_metrics.issubset(provided_metrics)

    @classmethod
    def get_version(cls) -> str:
        """
        Get the version of the formatter.

        Returns:
            str: Formatter version
        """
        return '1.0.0'

    @classmethod
    def get_author(cls) -> str:
        """
        Get the author of the formatter.

        Returns:
            str: Formatter author
        """
        return 'Barrhann'
