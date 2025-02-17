"""
Code Formatting Report Formatter.

This module handles the formatting of code formatting analysis results
for the builder mindset category.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:16:54
"""

from typing import Dict, List, Any, Optional
from ....models import ReportSection, MetricBlock


class CodeFormattingFormatter:
    """
    Formatter for code formatting analysis results.

    This formatter creates report sections for code formatting analysis,
    including PEP 8 compliance, code structure, and readability metrics.
    """

    def __init__(self):
        """Initialize the code formatting formatter."""
        self.template = {
            'title': 'Code Formatting Analysis',
            'category': 'builder_mindset',
            'section_order': [
                'overview',
                'style_compliance',
                'readability',
                'suggestions'
            ]
        }

    def format_metrics(self, metrics: MetricBlock) -> ReportSection:
        """
        Format code formatting metrics into a report section.

        Args:
            metrics (MetricBlock): Code formatting metrics to format

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
            metrics (MetricBlock): Code formatting metrics

        Returns:
            str: Formatted content text
        """
        content_parts = []
        
        # Overview
        content_parts.append("# Code Formatting Analysis\n")
        content_parts.append(
            f"Overall formatting score: {metrics.score}/100\n"
        )
        
        # Style Compliance
        content_parts.append("\n## PEP 8 Compliance\n")
        pep8_score = metrics.get_metric('pep8_compliance_score')
        if pep8_score is not None:
            content_parts.append(
                f"PEP 8 compliance score: {pep8_score}/100\n"
            )
        
        # Readability
        content_parts.append("\n## Code Readability\n")
        readability = metrics.get_metric('readability_score')
        if readability is not None:
            content_parts.append(
                f"Code readability score: {readability}/100\n"
            )

        return '\n'.join(content_parts)

    def _extract_findings(self, metrics: MetricBlock) -> List[str]:
        """
        Extract findings from the metrics.

        Args:
            metrics (MetricBlock): Code formatting metrics

        Returns:
            List[str]: List of findings
        """
        findings = []
        
        # PEP 8 findings
        pep8_issues = metrics.get_metric('pep8_issues')
        if pep8_issues:
            for issue in pep8_issues:
                findings.append(f"PEP 8 violation: {issue}")
        
        # Readability findings
        readability_issues = metrics.get_metric('readability_issues')
        if readability_issues:
            for issue in readability_issues:
                findings.append(f"Readability issue: {issue}")

        return findings

    def _generate_suggestions(self, metrics: MetricBlock) -> List[str]:
        """
        Generate improvement suggestions based on metrics.

        Args:
            metrics (MetricBlock): Code formatting metrics

        Returns:
            List[str]: List of suggestions
        """
        suggestions = []
        
        # PEP 8 suggestions
        pep8_score = metrics.get_metric('pep8_compliance_score')
        if pep8_score and pep8_score < 80:
            suggestions.append(
                "Consider using a code formatter like 'black' or 'autopep8'"
            )
        
        # Readability suggestions
        readability = metrics.get_metric('readability_score')
        if readability and readability < 80:
            suggestions.append(
                "Consider breaking down complex lines into multiple lines"
            )
            suggestions.append(
                "Use meaningful variable names and add docstrings"
            )

        return suggestions

    def _create_charts_data(self, metrics: MetricBlock) -> Dict[str, Any]:
        """
        Create visualization data for the metrics.

        Args:
            metrics (MetricBlock): Code formatting metrics

        Returns:
            Dict[str, Any]: Chart data
        """
        return {
            'score_breakdown': {
                'type': 'pie',
                'data': {
                    'PEP 8 Compliance': metrics.get_metric('pep8_compliance_score'),
                    'Readability': metrics.get_metric('readability_score')
                }
            },
            'issues_distribution': {
                'type': 'bar',
                'data': {
                    'PEP 8 Issues': len(metrics.get_metric('pep8_issues') or []),
                    'Readability Issues': len(metrics.get_metric('readability_issues') or [])
                }
            }
        }

    def __str__(self) -> str:
        """Return string representation of the formatter."""
        return f"CodeFormattingFormatter(category='{self.template['category']}')"

    def __repr__(self) -> str:
        """Return detailed string representation of the formatter."""
        return (f"CodeFormattingFormatter("
                f"title='{self.template['title']}', "
                f"category='{self.template['category']}')")
