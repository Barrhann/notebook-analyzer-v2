"""
Code Reusability Report Formatter.

This module handles the formatting of code reusability analysis results
for the builder mindset category.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:25:53
"""

from typing import Dict, List, Any, Optional
from ....models import ReportSection, MetricBlock


class CodeReusabilityFormatter:
    """
    Formatter for code reusability analysis results.

    This formatter creates report sections for code reusability analysis,
    including abstraction levels, function modularity, and component isolation.
    """

    def __init__(self):
        """Initialize the code reusability formatter."""
        self.template = {
            'title': 'Code Reusability Analysis',
            'category': 'builder_mindset',
            'section_order': [
                'overview',
                'abstraction_metrics',
                'modularity_analysis',
                'component_isolation',
                'suggestions'
            ]
        }

    def format_metrics(self, metrics: MetricBlock) -> ReportSection:
        """
        Format code reusability metrics into a report section.

        Args:
            metrics (MetricBlock): Code reusability metrics to format

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
            metrics (MetricBlock): Code reusability metrics

        Returns:
            str: Formatted content text
        """
        content_parts = []
        
        # Overview
        content_parts.append("# Code Reusability Analysis\n")
        content_parts.append(
            f"Overall reusability score: {metrics.score}/100\n"
        )
        
        # Abstraction Metrics
        content_parts.append("\n## Abstraction Level\n")
        abstraction_score = metrics.get_metric('abstraction_score')
        if abstraction_score is not None:
            content_parts.append(
                f"Abstraction level score: {abstraction_score}/100\n"
            )
            
        # Modularity Analysis
        content_parts.append("\n## Function Modularity\n")
        modularity_score = metrics.get_metric('function_modularity_score')
        if modularity_score is not None:
            content_parts.append(
                f"Function modularity score: {modularity_score}/100\n"
            )
        
        # Component Isolation
        content_parts.append("\n## Component Isolation\n")
        isolation_score = metrics.get_metric('component_isolation_score')
        if isolation_score is not None:
            content_parts.append(
                f"Component isolation score: {isolation_score}/100\n"
            )

        return '\n'.join(content_parts)

    def _extract_findings(self, metrics: MetricBlock) -> List[str]:
        """
        Extract findings from the metrics.

        Args:
            metrics (MetricBlock): Code reusability metrics

        Returns:
            List[str]: List of findings
        """
        findings = []
        
        # Abstraction findings
        abstraction_score = metrics.get_metric('abstraction_score')
        if abstraction_score and abstraction_score < 70:
            findings.append(
                "Low abstraction level may hinder code reuse"
            )
        
        # Modularity findings
        function_deps = metrics.get_metric('function_dependencies')
        if function_deps and len(function_deps) > 5:
            findings.append(
                f"High function dependencies: {len(function_deps)} dependencies found"
            )
        
        # Isolation findings
        global_usage = metrics.get_metric('global_variable_usage')
        if global_usage and global_usage > 0:
            findings.append(
                f"Found {global_usage} instances of global variable usage"
            )

        return findings

    def _generate_suggestions(self, metrics: MetricBlock) -> List[str]:
        """
        Generate improvement suggestions based on metrics.

        Args:
            metrics (MetricBlock): Code reusability metrics

        Returns:
            List[str]: List of suggestions
        """
        suggestions = []
        
        # Abstraction suggestions
        abstraction_score = metrics.get_metric('abstraction_score')
        if abstraction_score and abstraction_score < 70:
            suggestions.append(
                "Consider creating abstract base classes for common functionality"
            )
            suggestions.append(
                "Use interfaces to define clear contracts between components"
            )
        
        # Modularity suggestions
        modularity_score = metrics.get_metric('function_modularity_score')
        if modularity_score and modularity_score < 70:
            suggestions.append(
                "Break down large functions into smaller, reusable components"
            )
            suggestions.append(
                "Use dependency injection to improve function modularity"
            )
        
        # Isolation suggestions
        isolation_score = metrics.get_metric('component_isolation_score')
        if isolation_score and isolation_score < 70:
            suggestions.append(
                "Avoid using global variables, use parameter passing instead"
            )
            suggestions.append(
                "Create utility classes for commonly used functionality"
            )

        return suggestions

    def _create_charts_data(self, metrics: MetricBlock) -> Dict[str, Any]:
        """
        Create visualization data for the metrics.

        Args:
            metrics (MetricBlock): Code reusability metrics

        Returns:
            Dict[str, Any]: Chart data
        """
        return {
            'reusability_scores': {
                'type': 'radar',
                'data': {
                    'Abstraction': metrics.get_metric('abstraction_score'),
                    'Modularity': metrics.get_metric('function_modularity_score'),
                    'Isolation': metrics.get_metric('component_isolation_score')
                }
            },
            'dependency_analysis': {
                'type': 'network',
                'data': metrics.get_metric('function_dependencies'),
                'title': 'Function Dependency Network'
            },
            'component_metrics': {
                'type': 'bar',
                'data': {
                    'Reusable Components': metrics.get_metric('reusable_component_count'),
                    'Total Components': metrics.get_metric('total_component_count')
                }
            }
        }

    def __str__(self) -> str:
        """Return string representation of the formatter."""
        return f"CodeReusabilityFormatter(category='{self.template['category']}')"

    def __repr__(self) -> str:
        """Return detailed string representation of the formatter."""
        return (f"CodeReusabilityFormatter("
                f"title='{self.template['title']}', "
                f"category='{self.template['category']}')")
