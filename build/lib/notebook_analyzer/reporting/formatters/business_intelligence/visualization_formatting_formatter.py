"""
Visualization Formatting Report Formatter.

This module handles the formatting of visualization formatting analysis results
for the business intelligence category.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:32:09
"""

from typing import Dict, List, Any, Optional
from ....models import ReportSection, MetricBlock


class VisualizationFormattingFormatter:
    """
    Formatter for visualization formatting analysis results.

    This formatter creates report sections for visualization formatting analysis,
    including style consistency, readability, and visual design elements.
    """

    def __init__(self):
        """Initialize the visualization formatting formatter."""
        self.template = {
            'title': 'Visualization Formatting Analysis',
            'category': 'business_intelligence',
            'section_order': [
                'overview',
                'style_consistency',
                'readability',
                'visual_design',
                'suggestions'
            ]
        }

    def format_metrics(self, metrics: MetricBlock) -> ReportSection:
        """
        Format visualization formatting metrics into a report section.

        Args:
            metrics (MetricBlock): Visualization formatting metrics to format

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
            metrics (MetricBlock): Visualization formatting metrics

        Returns:
            str: Formatted content text
        """
        content_parts = []
        
        # Overview
        content_parts.append("# Visualization Formatting Analysis\n")
        content_parts.append(
            f"Overall formatting score: {metrics.score}/100\n"
        )
        
        # Style Consistency
        content_parts.append("\n## Style Consistency\n")
        consistency_score = metrics.get_metric('style_consistency_score')
        if consistency_score is not None:
            content_parts.append(
                f"Style consistency score: {consistency_score}/100\n"
            )
        
        # Readability
        content_parts.append("\n## Readability Analysis\n")
        readability_score = metrics.get_metric('readability_score')
        if readability_score is not None:
            content_parts.append(
                f"Visualization readability score: {readability_score}/100\n"
            )
            
        # Visual Design
        content_parts.append("\n## Visual Design Elements\n")
        design_score = metrics.get_metric('visual_design_score')
        if design_score is not None:
            content_parts.append(
                f"Visual design score: {design_score}/100\n"
            )

        return '\n'.join(content_parts)

    def _extract_findings(self, metrics: MetricBlock) -> List[str]:
        """
        Extract findings from the metrics.

        Args:
            metrics (MetricBlock): Visualization formatting metrics

        Returns:
            List[str]: List of findings
        """
        findings = []
        
        # Style consistency findings
        style_issues = metrics.get_metric('style_inconsistencies')
        if style_issues:
            findings.append(
                f"Found {len(style_issues)} style inconsistencies across visualizations"
            )
        
        # Readability findings
        missing_labels = metrics.get_metric('missing_labels')
        if missing_labels:
            findings.append(
                f"Found {len(missing_labels)} visualizations with missing labels"
            )
        
        # Color usage findings
        color_issues = metrics.get_metric('color_accessibility_issues')
        if color_issues:
            findings.append(
                f"Identified {len(color_issues)} color accessibility concerns"
            )
        
        # Layout findings
        layout_issues = metrics.get_metric('layout_issues')
        if layout_issues:
            findings.append(
                f"Found {len(layout_issues)} layout and alignment issues"
            )

        return findings

    def _generate_suggestions(self, metrics: MetricBlock) -> List[str]:
        """
        Generate improvement suggestions based on metrics.

        Args:
            metrics (MetricBlock): Visualization formatting metrics

        Returns:
            List[str]: List of suggestions
        """
        suggestions = []
        
        # Style consistency suggestions
        consistency_score = metrics.get_metric('style_consistency_score')
        if consistency_score and consistency_score < 70:
            suggestions.append(
                "Create and follow a consistent style guide for visualizations"
            )
            suggestions.append(
                "Use consistent color schemes across related visualizations"
            )
        
        # Readability suggestions
        readability_score = metrics.get_metric('readability_score')
        if readability_score and readability_score < 70:
            suggestions.append(
                "Increase font sizes for better readability"
            )
            suggestions.append(
                "Add clear axes labels and titles to all charts"
            )
        
        # Visual design suggestions
        design_score = metrics.get_metric('visual_design_score')
        if design_score and design_score < 70:
            suggestions.append(
                "Improve visual hierarchy through consistent sizing"
            )
            suggestions.append(
                "Consider using whitespace more effectively"
            )

        return suggestions

    def _create_charts_data(self, metrics: MetricBlock) -> Dict[str, Any]:
        """
        Create visualization data for the metrics.

        Args:
            metrics (MetricBlock): Visualization formatting metrics

        Returns:
            Dict[str, Any]: Chart data
        """
        return {
            'formatting_scores': {
                'type': 'radar',
                'data': {
                    'Style Consistency': metrics.get_metric('style_consistency_score'),
                    'Readability': metrics.get_metric('readability_score'),
                    'Visual Design': metrics.get_metric('visual_design_score')
                }
            },
            'issue_distribution': {
                'type': 'bar',
                'data': {
                    'Style Issues': len(metrics.get_metric('style_inconsistencies') or []),
                    'Label Issues': len(metrics.get_metric('missing_labels') or []),
                    'Color Issues': len(metrics.get_metric('color_accessibility_issues') or []),
                    'Layout Issues': len(metrics.get_metric('layout_issues') or [])
                }
            },
            'improvement_areas': {
                'type': 'heatmap',
                'data': metrics.get_metric('formatting_improvement_areas'),
                'title': 'Areas Needing Improvement'
            }
        }

    def __str__(self) -> str:
        """Return string representation of the formatter."""
        return f"VisualizationFormattingFormatter(category='{self.template['category']}')"

    def __repr__(self) -> str:
        """Return detailed string representation of the formatter."""
        return (f"VisualizationFormattingFormatter("
                f"title='{self.template['title']}', "
                f"category='{self.template['category']}')")
