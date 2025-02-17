"""
Code Structure Report Formatter.

This module handles the formatting of code structure analysis results
for the builder mindset category.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:22:22
"""

from typing import Dict, List, Any, Optional
from ....models import ReportSection, MetricBlock


class CodeStructureFormatter:
    """
    Formatter for code structure analysis results.

    This formatter creates report sections for code structure analysis,
    including modularity, dependency management, and architectural patterns.
    """

    def __init__(self):
        """Initialize the code structure formatter."""
        self.template = {
            'title': 'Code Structure Analysis',
            'category': 'builder_mindset',
            'section_order': [
                'overview',
                'modularity',
                'dependencies',
                'architecture',
                'suggestions'
            ]
        }

    def format_metrics(self, metrics: MetricBlock) -> ReportSection:
        """
        Format code structure metrics into a report section.

        Args:
            metrics (MetricBlock): Code structure metrics to format

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
            metrics (MetricBlock): Code structure metrics

        Returns:
            str: Formatted content text
        """
        content_parts = []
        
        # Overview
        content_parts.append("# Code Structure Analysis\n")
        content_parts.append(
            f"Overall structure score: {metrics.score}/100\n"
        )
        
        # Modularity
        content_parts.append("\n## Code Modularity\n")
        cohesion = metrics.get_metric('cohesion_score')
        if cohesion is not None:
            content_parts.append(
                f"Code cohesion score: {cohesion}/100\n"
            )
            
        coupling = metrics.get_metric('coupling_score')
        if coupling is not None:
            content_parts.append(
                f"Code coupling score: {coupling}/100\n"
            )
        
        # Dependencies
        content_parts.append("\n## Dependencies Analysis\n")
        dep_complexity = metrics.get_metric('dependency_complexity')
        if dep_complexity is not None:
            content_parts.append(
                f"Dependency complexity: {dep_complexity:.2f}\n"
            )
            
        # Architecture
        content_parts.append("\n## Architectural Patterns\n")
        pattern_adherence = metrics.get_metric('pattern_adherence_score')
        if pattern_adherence is not None:
            content_parts.append(
                f"Pattern adherence score: {pattern_adherence}/100\n"
            )

        return '\n'.join(content_parts)

    def _extract_findings(self, metrics: MetricBlock) -> List[str]:
        """
        Extract findings from the metrics.

        Args:
            metrics (MetricBlock): Code structure metrics

        Returns:
            List[str]: List of findings
        """
        findings = []
        
        # Modularity findings
        cohesion = metrics.get_metric('cohesion_score')
        if cohesion and cohesion < 70:
            findings.append(
                "Low code cohesion detected - functions may have too many responsibilities"
            )
        
        coupling = metrics.get_metric('coupling_score')
        if coupling and coupling < 70:
            findings.append(
                "High code coupling detected - modules are too interdependent"
            )
        
        # Dependency findings
        circular_deps = metrics.get_metric('circular_dependencies')
        if circular_deps:
            findings.append(
                f"Found {len(circular_deps)} circular dependencies"
            )
        
        # Architecture findings
        pattern_violations = metrics.get_metric('pattern_violations')
        if pattern_violations:
            findings.append(
                f"Found {len(pattern_violations)} architectural pattern violations"
            )

        return findings

    def _generate_suggestions(self, metrics: MetricBlock) -> List[str]:
        """
        Generate improvement suggestions based on metrics.

        Args:
            metrics (MetricBlock): Code structure metrics

        Returns:
            List[str]: List of suggestions
        """
        suggestions = []
        
        # Modularity suggestions
        cohesion = metrics.get_metric('cohesion_score')
        if cohesion and cohesion < 70:
            suggestions.append(
                "Consider grouping related functions into classes"
            )
            suggestions.append(
                "Split functions with multiple responsibilities"
            )
        
        # Coupling suggestions
        coupling = metrics.get_metric('coupling_score')
        if coupling and coupling < 70:
            suggestions.append(
                "Use dependency injection to reduce module coupling"
            )
            suggestions.append(
                "Consider implementing interface abstractions"
            )
        
        # Architecture suggestions
        pattern_adherence = metrics.get_metric('pattern_adherence_score')
        if pattern_adherence and pattern_adherence < 70:
            suggestions.append(
                "Review and align code with chosen architectural patterns"
            )

        return suggestions

    def _create_charts_data(self, metrics: MetricBlock) -> Dict[str, Any]:
        """
        Create visualization data for the metrics.

        Args:
            metrics (MetricBlock): Code structure metrics

        Returns:
            Dict[str, Any]: Chart data
        """
        return {
            'modularity_scores': {
                'type': 'radar',
                'data': {
                    'Cohesion': metrics.get_metric('cohesion_score'),
                    'Coupling': metrics.get_metric('coupling_score'),
                    'Pattern Adherence': metrics.get_metric('pattern_adherence_score')
                }
            },
            'dependency_graph': {
                'type': 'network',
                'data': metrics.get_metric('dependency_graph'),
                'title': 'Module Dependencies'
            },
            'complexity_trends': {
                'type': 'line',
                'data': metrics.get_metric('complexity_trend'),
                'title': 'Structure Complexity Trend'
            }
        }

    def __str__(self) -> str:
        """Return string representation of the formatter."""
        return f"CodeStructureFormatter(category='{self.template['category']}')"

    def __repr__(self) -> str:
        """Return detailed string representation of the formatter."""
        return (f"CodeStructureFormatter("
                f"title='{self.template['title']}', "
                f"category='{self.template['category']}')")
