"""
Visualization Types Report Formatter.

This module handles the formatting of visualization types analysis results
for the business intelligence category.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:30:41
"""

from typing import Dict, List, Any, Optional
from ....models import ReportSection, MetricBlock


class VisualizationTypesFormatter:
    """
    Formatter for visualization types analysis results.

    This formatter creates report sections for visualization types analysis,
    including diversity, appropriateness, and effectiveness of visualizations.
    """

    def __init__(self):
        """Initialize the visualization types formatter."""
        self.template = {
            'title': 'Visualization Types Analysis',
            'category': 'business_intelligence',
            'section_order': [
                'overview',
                'visualization_diversity',
                'chart_appropriateness',
                'visualization_effectiveness',
                'suggestions'
            ]
        }

    def format_metrics(self, metrics: MetricBlock) -> ReportSection:
        """
        Format visualization types metrics into a report section.

        Args:
            metrics (MetricBlock): Visualization types metrics to format

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
            metrics (MetricBlock): Visualization types metrics

        Returns:
            str: Formatted content text
        """
        content_parts = []
        
        # Overview
        content_parts.append("# Visualization Types Analysis\n")
        content_parts.append(
            f"Overall visualization score: {metrics.score}/100\n"
        )
        
        # Visualization Diversity
        content_parts.append("\n## Visualization Diversity\n")
        unique_types = metrics.get_metric('unique_visualization_types')
        if unique_types:
            content_parts.append(
                f"Number of unique visualization types: {len(unique_types)}\n"
            )
            content_parts.append("Types used:\n")
            for viz_type in unique_types:
                content_parts.append(f"- {viz_type}\n")
        
        # Chart Appropriateness
        content_parts.append("\n## Chart Appropriateness\n")
        appropriateness_score = metrics.get_metric('chart_appropriateness_score')
        if appropriateness_score is not None:
            content_parts.append(
                f"Chart type appropriateness score: {appropriateness_score}/100\n"
            )
        
        # Effectiveness
        content_parts.append("\n## Visualization Effectiveness\n")
        effectiveness_score = metrics.get_metric('visualization_effectiveness_score')
        if effectiveness_score is not None:
            content_parts.append(
                f"Overall effectiveness score: {effectiveness_score}/100\n"
            )

        return '\n'.join(content_parts)

    def _extract_findings(self, metrics: MetricBlock) -> List[str]:
        """
        Extract findings from the metrics.

        Args:
            metrics (MetricBlock): Visualization types metrics

        Returns:
            List[str]: List of findings
        """
        findings = []
        
        # Diversity findings
        unique_types = metrics.get_metric('unique_visualization_types')
        if unique_types and len(unique_types) < 3:
            findings.append(
                "Limited variety of visualization types used"
            )
        
        # Appropriateness findings
        inappropriate_charts = metrics.get_metric('inappropriate_chart_types')
        if inappropriate_charts:
            findings.append(
                f"Found {len(inappropriate_charts)} potentially inappropriate chart types"
            )
        
        # Effectiveness findings
        missing_elements = metrics.get_metric('missing_visualization_elements')
        if missing_elements:
            findings.append(
                f"Found {len(missing_elements)} visualizations missing key elements"
            )
        
        # Complexity findings
        complex_viz = metrics.get_metric('overly_complex_visualizations')
        if complex_viz:
            findings.append(
                f"Identified {len(complex_viz)} overly complex visualizations"
            )

        return findings

    def _generate_suggestions(self, metrics: MetricBlock) -> List[str]:
        """
        Generate improvement suggestions based on metrics.

        Args:
            metrics (MetricBlock): Visualization types metrics

        Returns:
            List[str]: List of suggestions
        """
        suggestions = []
        
        # Diversity suggestions
        unique_types = metrics.get_metric('unique_visualization_types')
        if unique_types and len(unique_types) < 3:
            suggestions.append(
                "Consider using a wider variety of visualization types"
            )
            suggestions.append(
                "Explore different chart types for different aspects of the data"
            )
        
        # Appropriateness suggestions
        inappropriate_charts = metrics.get_metric('inappropriate_chart_types')
        if inappropriate_charts:
            for chart in inappropriate_charts[:3]:  # Top 3 suggestions
                suggestions.append(
                    f"Consider replacing {chart['current']} with {chart['recommended']} "
                    f"for {chart['data_type']}"
                )
        
        # Effectiveness suggestions
        effectiveness_score = metrics.get_metric('visualization_effectiveness_score')
        if effectiveness_score and effectiveness_score < 70:
            suggestions.append(
                "Add clear titles and labels to all visualizations"
            )
            suggestions.append(
                "Include legends where multiple categories are present"
            )

        return suggestions

    def _create_charts_data(self, metrics: MetricBlock) -> Dict[str, Any]:
        """
        Create visualization data for the metrics.

        Args:
            metrics (MetricBlock): Visualization types metrics

        Returns:
            Dict[str, Any]: Chart data
        """
        return {
            'visualization_usage': {
                'type': 'pie',
                'data': metrics.get_metric('visualization_type_distribution'),
                'title': 'Distribution of Visualization Types'
            },
            'effectiveness_scores': {
                'type': 'radar',
                'data': {
                    'Type Appropriateness': metrics.get_metric('chart_appropriateness_score'),
                    'Visual Clarity': metrics.get_metric('visual_clarity_score'),
                    'Information Density': metrics.get_metric('information_density_score')
                }
            },
            'complexity_analysis': {
                'type': 'bar',
                'data': metrics.get_metric('visualization_complexity_scores'),
                'title': 'Visualization Complexity Analysis'
            }
        }

    def __str__(self) -> str:
        """Return string representation of the formatter."""
        return f"VisualizationTypesFormatter(category='{self.template['category']}')"

    def __repr__(self) -> str:
        """Return detailed string representation of the formatter."""
        return (f"VisualizationTypesFormatter("
                f"title='{self.template['title']}', "
                f"category='{self.template['category']}')")
