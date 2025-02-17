"""
Dataset Join Report Formatter.

This module handles the formatting of dataset join analysis results
for the builder mindset category.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:24:24
"""

from typing import Dict, List, Any, Optional
from ....models import ReportSection, MetricBlock


class DatasetJoinFormatter:
    """
    Formatter for dataset join analysis results.

    This formatter creates report sections for dataset join analysis,
    including join efficiency, key usage, and data integrity metrics.
    """

    def __init__(self):
        """Initialize the dataset join formatter."""
        self.template = {
            'title': 'Dataset Join Analysis',
            'category': 'builder_mindset',
            'section_order': [
                'overview',
                'join_efficiency',
                'key_analysis',
                'data_integrity',
                'suggestions'
            ]
        }

    def format_metrics(self, metrics: MetricBlock) -> ReportSection:
        """
        Format dataset join metrics into a report section.

        Args:
            metrics (MetricBlock): Dataset join metrics to format

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
            metrics (MetricBlock): Dataset join metrics

        Returns:
            str: Formatted content text
        """
        content_parts = []
        
        # Overview
        content_parts.append("# Dataset Join Analysis\n")
        content_parts.append(
            f"Overall join efficiency score: {metrics.score}/100\n"
        )
        
        # Join Efficiency
        content_parts.append("\n## Join Efficiency\n")
        memory_usage = metrics.get_metric('join_memory_usage')
        if memory_usage is not None:
            content_parts.append(
                f"Memory usage: {memory_usage:.2f} MB\n"
            )
            
        execution_time = metrics.get_metric('join_execution_time')
        if execution_time is not None:
            content_parts.append(
                f"Execution time: {execution_time:.2f} seconds\n"
            )
        
        # Key Analysis
        content_parts.append("\n## Join Key Analysis\n")
        key_cardinality = metrics.get_metric('key_cardinality')
        if key_cardinality is not None:
            content_parts.append(
                f"Key cardinality: {key_cardinality:,}\n"
            )
            
        # Data Integrity
        content_parts.append("\n## Data Integrity\n")
        null_percentage = metrics.get_metric('join_key_null_percentage')
        if null_percentage is not None:
            content_parts.append(
                f"Join key null percentage: {null_percentage:.2f}%\n"
            )

        return '\n'.join(content_parts)

    def _extract_findings(self, metrics: MetricBlock) -> List[str]:
        """
        Extract findings from the metrics.

        Args:
            metrics (MetricBlock): Dataset join metrics

        Returns:
            List[str]: List of findings
        """
        findings = []
        
        # Memory usage findings
        memory_usage = metrics.get_metric('join_memory_usage')
        if memory_usage and memory_usage > 1000:  # 1GB threshold
            findings.append(
                f"High memory usage in join operation: {memory_usage:.2f} MB"
            )
        
        # Performance findings
        execution_time = metrics.get_metric('join_execution_time')
        if execution_time and execution_time > 60:  # 1 minute threshold
            findings.append(
                f"Slow join execution: {execution_time:.2f} seconds"
            )
        
        # Data quality findings
        null_percentage = metrics.get_metric('join_key_null_percentage')
        if null_percentage and null_percentage > 5:
            findings.append(
                f"High percentage of null join keys: {null_percentage:.2f}%"
            )
            
        # Cardinality findings
        duplicate_keys = metrics.get_metric('duplicate_join_keys')
        if duplicate_keys:
            findings.append(
                f"Found {len(duplicate_keys)} duplicate join keys"
            )

        return findings

    def _generate_suggestions(self, metrics: MetricBlock) -> List[str]:
        """
        Generate improvement suggestions based on metrics.

        Args:
            metrics (MetricBlock): Dataset join metrics

        Returns:
            List[str]: List of suggestions
        """
        suggestions = []
        
        # Memory optimization suggestions
        memory_usage = metrics.get_metric('join_memory_usage')
        if memory_usage and memory_usage > 1000:
            suggestions.append(
                "Consider using chunked processing for large joins"
            )
            suggestions.append(
                "Optimize data types to reduce memory usage"
            )
        
        # Performance suggestions
        execution_time = metrics.get_metric('join_execution_time')
        if execution_time and execution_time > 60:
            suggestions.append(
                "Add appropriate indexes on join keys"
            )
            suggestions.append(
                "Consider using merge sort join for large datasets"
            )
        
        # Data quality suggestions
        null_percentage = metrics.get_metric('join_key_null_percentage')
        if null_percentage and null_percentage > 5:
            suggestions.append(
                "Clean and handle null values before joining"
            )
            suggestions.append(
                "Consider using outer joins if nulls are expected"
            )

        return suggestions

    def _create_charts_data(self, metrics: MetricBlock) -> Dict[str, Any]:
        """
        Create visualization data for the metrics.

        Args:
            metrics (MetricBlock): Dataset join metrics

        Returns:
            Dict[str, Any]: Chart data
        """
        return {
            'performance_metrics': {
                'type': 'bar',
                'data': {
                    'Memory Usage (MB)': metrics.get_metric('join_memory_usage'),
                    'Execution Time (s)': metrics.get_metric('join_execution_time')
                }
            },
            'key_distribution': {
                'type': 'histogram',
                'data': metrics.get_metric('key_distribution'),
                'title': 'Join Key Distribution'
            },
            'data_quality': {
                'type': 'pie',
                'data': {
                    'Valid Keys': 100 - (metrics.get_metric('join_key_null_percentage') or 0),
                    'Null Keys': metrics.get_metric('join_key_null_percentage') or 0
                }
            }
        }

    def __str__(self) -> str:
        """Return string representation of the formatter."""
        return f"DatasetJoinFormatter(category='{self.template['category']}')"

    def __repr__(self) -> str:
        """Return detailed string representation of the formatter."""
        return (f"DatasetJoinFormatter("
                f"title='{self.template['title']}', "
                f"category='{self.template['category']}')")
