"""
Code Comments Report Formatter.

This module handles the formatting of code comments analysis results
for the builder mindset category.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:18:48
"""

from typing import Dict, List, Any, Optional
from ....models import ReportSection, MetricBlock


class CodeCommentsFormatter:
    """
    Formatter for code comments analysis results.

    This formatter creates report sections for code comments analysis,
    including docstring coverage, comment quality, and documentation metrics.
    """

    def __init__(self):
        """Initialize the code comments formatter."""
        self.template = {
            'title': 'Code Comments Analysis',
            'category': 'builder_mindset',
            'section_order': [
                'overview',
                'docstring_coverage',
                'comment_quality',
                'suggestions'
            ]
        }

    def format_metrics(self, metrics: MetricBlock) -> ReportSection:
        """
        Format code comments metrics into a report section.

        Args:
            metrics (MetricBlock): Code comments metrics to format

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
            metrics (MetricBlock): Code comments metrics

        Returns:
            str: Formatted content text
        """
        content_parts = []
        
        # Overview
        content_parts.append("# Code Comments Analysis\n")
        content_parts.append(
            f"Overall documentation score: {metrics.score}/100\n"
        )
        
        # Docstring Coverage
        content_parts.append("\n## Docstring Coverage\n")
        docstring_coverage = metrics.get_metric('docstring_coverage')
        if docstring_coverage is not None:
            content_parts.append(
                f"Function docstring coverage: {docstring_coverage}%\n"
            )
        
        # Comment Quality
        content_parts.append("\n## Comment Quality\n")
        comment_quality = metrics.get_metric('comment_quality_score')
        if comment_quality is not None:
            content_parts.append(
                f"Comment quality score: {comment_quality}/100\n"
            )
            
        # Documentation Metrics
        content_parts.append("\n## Documentation Metrics\n")
        comments_ratio = metrics.get_metric('comments_to_code_ratio')
        if comments_ratio is not None:
            content_parts.append(
                f"Comments to code ratio: {comments_ratio:.2f}\n"
            )

        return '\n'.join(content_parts)

    def _extract_findings(self, metrics: MetricBlock) -> List[str]:
        """
        Extract findings from the metrics.

        Args:
            metrics (MetricBlock): Code comments metrics

        Returns:
            List[str]: List of findings
        """
        findings = []
        
        # Docstring findings
        missing_docstrings = metrics.get_metric('functions_missing_docstrings')
        if missing_docstrings:
            findings.append(
                f"Found {len(missing_docstrings)} functions without docstrings"
            )
        
        # Comment quality findings
        low_quality_comments = metrics.get_metric('low_quality_comments')
        if low_quality_comments:
            findings.append(
                f"Found {len(low_quality_comments)} low-quality comments"
            )
        
        # Comments ratio findings
        comments_ratio = metrics.get_metric('comments_to_code_ratio')
        if comments_ratio and comments_ratio < 0.1:
            findings.append("Code is under-documented (low comments ratio)")

        return findings

    def _generate_suggestions(self, metrics: MetricBlock) -> List[str]:
        """
        Generate improvement suggestions based on metrics.

        Args:
            metrics (MetricBlock): Code comments metrics

        Returns:
            List[str]: List of suggestions
        """
        suggestions = []
        
        # Docstring suggestions
        docstring_coverage = metrics.get_metric('docstring_coverage')
        if docstring_coverage and docstring_coverage < 80:
            suggestions.append(
                "Add docstrings to functions following Google or NumPy style"
            )
        
        # Comment quality suggestions
        comment_quality = metrics.get_metric('comment_quality_score')
        if comment_quality and comment_quality < 80:
            suggestions.append(
                "Improve comment quality by explaining 'why' rather than 'what'"
            )
            suggestions.append(
                "Keep comments up-to-date with code changes"
            )
        
        # Comments ratio suggestions
        comments_ratio = metrics.get_metric('comments_to_code_ratio')
        if comments_ratio and comments_ratio < 0.1:
            suggestions.append(
                "Consider adding more inline comments for complex logic"
            )

        return suggestions

    def _create_charts_data(self, metrics: MetricBlock) -> Dict[str, Any]:
        """
        Create visualization data for the metrics.

        Args:
            metrics (MetricBlock): Code comments metrics

        Returns:
            Dict[str, Any]: Chart data
        """
        return {
            'documentation_scores': {
                'type': 'radar',
                'data': {
                    'Docstring Coverage': metrics.get_metric('docstring_coverage'),
                    'Comment Quality': metrics.get_metric('comment_quality_score'),
                    'Documentation Completeness': metrics.get_metric('documentation_completeness')
                }
            },
            'comments_distribution': {
                'type': 'pie',
                'data': {
                    'Inline Comments': metrics.get_metric('inline_comments_count'),
                    'Docstrings': metrics.get_metric('docstrings_count'),
                    'Module Comments': metrics.get_metric('module_comments_count')
                }
            }
        }

    def __str__(self) -> str:
        """Return string representation of the formatter."""
        return f"CodeCommentsFormatter(category='{self.template['category']}')"

    def __repr__(self) -> str:
        """Return detailed string representation of the formatter."""
        return (f"CodeCommentsFormatter("
                f"title='{self.template['title']}', "
                f"category='{self.template['category']}')")
