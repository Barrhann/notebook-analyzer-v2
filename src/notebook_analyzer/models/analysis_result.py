"""
Analysis Result Model.

This module defines the data model for representing analysis results
from notebook analyzers.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:11:10
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class AnalyzerResult:
    """
    Represents the result from a single analyzer.

    Attributes:
        analyzer_name (str): Name of the analyzer
        category (str): Category of the analyzer (builder_mindset, business_intelligence)
        score (float): Analysis score (0-100)
        findings (List[str]): List of findings from the analysis
        suggestions (List[str]): List of improvement suggestions
        details (Dict[str, Any]): Detailed analysis results
        timestamp (datetime): When the analysis was performed
    """
    analyzer_name: str
    category: str
    score: float
    findings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())

    def __post_init__(self):
        """Validate the analysis result after initialization."""
        if not 0 <= self.score <= 100:
            raise ValueError("Score must be between 0 and 100")
        
        if not self.analyzer_name:
            raise ValueError("Analyzer name cannot be empty")
            
        if self.category not in ['builder_mindset', 'business_intelligence']:
            raise ValueError(
                "Category must be either 'builder_mindset' or 'business_intelligence'"
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the analysis result to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the result
        """
        return {
            'analyzer_name': self.analyzer_name,
            'category': self.category,
            'score': self.score,
            'findings': self.findings,
            'suggestions': self.suggestions,
            'details': self.details,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


@dataclass
class NotebookAnalysisResult:
    """
    Represents the complete analysis result for a notebook.

    Attributes:
        notebook_path (str): Path to the analyzed notebook
        metadata (Dict[str, Any]): Notebook metadata
        analyzer_results (List[AnalyzerResult]): Results from individual analyzers
        overall_score (float): Combined analysis score
        timestamp (datetime): When the analysis was performed
        errors (List[str]): Any errors that occurred during analysis
    """
    notebook_path: str
    metadata: Dict[str, Any]
    analyzer_results: List[AnalyzerResult] = field(default_factory=list)
    overall_score: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())
    errors: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Calculate the overall score if not provided."""
        if not self.overall_score and self.analyzer_results:
            weights = {
                'builder_mindset': 0.6,
                'business_intelligence': 0.4
            }
            
            category_scores = {}
            for result in self.analyzer_results:
                if result.category not in category_scores:
                    category_scores[result.category] = []
                category_scores[result.category].append(result.score)
            
            weighted_scores = []
            for category, scores in category_scores.items():
                if scores:
                    avg_score = sum(scores) / len(scores)
                    weighted_scores.append(avg_score * weights.get(category, 1.0))
            
            if weighted_scores:
                self.overall_score = round(
                    sum(weighted_scores) / sum(weights.values()),
                    2
                )

    def add_analyzer_result(self, result: AnalyzerResult) -> None:
        """
        Add a new analyzer result and update the overall score.

        Args:
            result (AnalyzerResult): Analyzer result to add
        """
        self.analyzer_results.append(result)
        self.__post_init__()  # Recalculate overall score

    def get_category_summary(self, category: str) -> Dict[str, Any]:
        """
        Get summary of results for a specific category.

        Args:
            category (str): Category to summarize

        Returns:
            Dict[str, Any]: Category summary
        """
        category_results = [
            r for r in self.analyzer_results
            if r.category == category
        ]
        
        if not category_results:
            return {'status': 'No results for category'}
            
        return {
            'analyzers': len(category_results),
            'average_score': round(
                sum(r.score for r in category_results) / len(category_results),
                2
            ),
            'findings': [
                finding
                for result in category_results
                for finding in result.findings
            ],
            'suggestions': [
                suggestion
                for result in category_results
                for suggestion in result.suggestions
            ]
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the notebook analysis result to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the result
        """
        return {
            'notebook_path': self.notebook_path,
            'metadata': self.metadata,
            'analyzer_results': [
                result.to_dict() for result in self.analyzer_results
            ],
            'overall_score': self.overall_score,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'errors': self.errors,
            'summary': {
                'total_analyzers': len(self.analyzer_results),
                'categories': list({
                    result.category for result in self.analyzer_results
                }),
                'status': 'success' if not self.errors else 'completed with errors'
            }
        }

    def __str__(self) -> str:
        """Return string representation of the analysis result."""
        return (f"NotebookAnalysisResult(notebook='{self.notebook_path}', "
                f"score={self.overall_score}, "
                f"analyzers={len(self.analyzer_results)})")

    def __repr__(self) -> str:
        """Return detailed string representation of the analysis result."""
        return (f"NotebookAnalysisResult("
                f"path='{self.notebook_path}', "
                f"score={self.overall_score}, "
                f"analyzers={len(self.analyzer_results)}, "
                f"errors={len(self.errors)})")
