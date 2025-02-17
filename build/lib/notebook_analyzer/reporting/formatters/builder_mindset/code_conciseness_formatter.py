"""
Code Conciseness Report Formatter.

This module handles the formatting of code conciseness analysis results
for the builder mindset category.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:20:27
"""

from typing import Dict, List, Any, Optional
from ....models import ReportSection, MetricBlock


class CodeConcisenessFormatter:
    """
    Formatter for code conciseness analysis results.

    This formatter creates report sections for code conciseness analysis,
    including code complexity, redundancy, and efficiency metrics.
    """

    def __init__(self):
        """Initialize the code conciseness formatter."""
        self.template = {
            'title': 'Code Conciseness Analysis',
            'category': 'builder_mindset',
            'section_order': [
                'overview',
                'complexity_metrics',
                'redundancy_analysis',
                'suggestions'
            ]
        }

    def format_metrics(self, metrics: MetricBlock) -> ReportSection:
        """
        Format code conciseness metrics into a report section.

        Args:
            metrics (MetricBlock): Code conciseness metrics to format

        Returns:
            ReportSection: Formatted report section
        """
        # Create section content
        content = self._create_section_content(metrics)
        
        # Extract findings
        findings = self._extract_findings(metrics)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(metrics)
        
        # Create charts data
        charts = self._create_charts_data(metrics)

        return ReportSection(
            title=self.template['title'],
            category=self.template['category'],
            content=content,
            findings=findings,
            suggestions=suggestions,
            metrics=metrics.metrics,
            charts=charts
        )

    def _create_section_content(self, metrics: MetricBlock) -> str:
        """
        Create the main content text for the section.

        Args:
            metrics (MetricBlock): Code conciseness metrics

        Returns:
            str: Formatted content text
        """
        content_parts = []
        
        # Overview
        content_parts.append("# Code Conciseness Analysis\n")
        content_parts.append(
            f"Overall conciseness score: {metrics.score}/100\n"
        )
        
        # Complexity Metrics
        content_parts.append("\n## Code Complexity\n")
        cyclomatic = metrics.get_metric('cyclomatic_complexity')
        if cyclomatic is not None:
            content_parts.append(
                f"Average cyclomatic complexity: {cyclomatic:.2f}\n"
            )
        
        # Redundancy Analysis
        content_parts.append("\n## Code Redundancy\n")
        duplication = metrics.get_metric('code_duplication_percentage')
        if duplication is not None:
            content_parts.append(
                f"Code duplication: {duplication:.1f}%\n"
            )
            
        # Lines of Code
        content_parts.append("\n## Code Size Metrics\n")
        avg_function_length = metrics.get_metric('average_function_length')
        if avg_function_length is not None:
            content_parts.append(
                f"Average function length: {avg_function_length:.1f} lines\n"
            )

        return '\n'.join(content_parts)

    def _extract_findings(self, metrics: MetricBlock) -> List[str]:
        """
        Extract findings from the metrics.

        Args:
            metrics (MetricBlock): Code conciseness metrics

        Returns:
            List[str]: List of findings
        """
        findings = []
        
        # Complexity findings
        cyclomatic = metrics.get_metric('cyclomatic_complexity')
        if cyclomatic and cyclomatic > 10:
            findings.append(
                f"High average cyclomatic complexity: {cyclomatic:.2f}"
            )
        
        # Redundancy findings
        duplication = metrics.get_metric('code_duplication_percentage')
        if duplication and duplication > 15:
            findings.append(
                f"Significant code duplication detected: {duplication:.1f}%"
            )
        
        # Function length findings
        long_functions = metrics.get_metric('long_functions')
        if long_functions:
            findings.append(
                f"Found {len(long_functions)} functions exceeding recommended length"
            )

        return findings

    def _generate_suggestions(self, metrics: MetricBlock) -> List[str]:
        """
        Generate improvement suggestions based on metrics.

        Args:
            metrics (MetricBlock): Code conciseness metrics

        Returns:
            List[str]: List of suggestions
        """
        suggestions = []
        
        # Complexity suggestions
        cyclomatic = metrics.get_metric('cyclomatic_complexity')
        if cyclomatic and cyclomatic > 10:
            suggestions.append(
                "Consider breaking down complex functions into smaller ones"
            )
            suggestions.append(
                "Use early returns to reduce nesting levels"
            )
        
        # Redundancy suggestions
        duplication = metrics.get_metric('code_duplication_percentage')
        if duplication and duplication > 15:
            suggestions.append(
                "Extract duplicated code into reusable functions"
            )
            suggestions.append(
                "Consider using helper functions for common operations"
            )
        
        # Function length suggestions
        avg_function_length = metrics.get_metric('average_function_length')
        if avg_function_length and avg_function_length > 20:
            suggestions.append(
                "Split long functions into smaller, focused functions"
            )

        return suggestions

    def _create_charts_data(self, metrics: MetricBlock) -> Dict[str, Any]:
        """
        Create visualization data for the metrics.

        Args:
            metrics (MetricBlock): Code conciseness metrics

        Returns:
            Dict[str, Any]: Chart data
        """
        return {
            'complexity_distribution': {
                'type': 'histogram',
                'data': metrics.get_metric('complexity_distribution'),
                'title': 'Function Complexity Distribution'
            },
            'size_metrics': {
                'type': 'bar',
                'data': {
                    'Average Function Length': metrics.get_metric('average_function_length'),
                    'Maximum Function Length': metrics.get_metric('max_function_length'),
                    'Recommended Length': 20
                }
            },
            'duplication_analysis': {
                'type': 'pie',
                'data': {
                    'Unique Code': 100 - (metrics.get_metric('code_duplication_percentage') or 0),
                    'Duplicated Code': metrics.get_metric('code_duplication_percentage') or 0
                }
            }
        }

    def __str__(self) -> str:
        """Return string representation of the formatter."""
        return f"CodeConcisenessFormatter(category='{self.template['category']}')"

    def __repr__(self) -> str:
        """Return detailed string representation of the formatter."""
        return (f"CodeConcisenessFormatter("
                f"title='{self.template['title']}', "
                f"category='{self.template['category']}')")
