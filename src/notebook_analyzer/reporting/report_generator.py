"""
Report Generator.

This module provides the main functionality for generating analysis reports
by combining analysis results with appropriate templates and formatters.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 23:16:33
"""

from typing import Dict, Any, List, Optional
import os
from datetime import datetime
from .templates import HTMLTemplate, MarkdownTemplate
from .formatters.builder_mindset import (
    CodeFormattingFormatter,
    CodeStructureFormatter,
    CodeCommentsFormatter,
    CodeConcisenessFormatter,
    CodeReusabilityFormatter,
    AdvancedTechniquesFormatter,
    DatasetJoinFormatter
)
from .formatters.business_intelligence import (
    VisualizationTypesFormatter,
    VisualizationFormattingFormatter
)


def get_template_by_format(format_type: str) -> type:
    """Get the appropriate template class for the given format."""
    templates = {
        'html': HTMLTemplate,
        'markdown': MarkdownTemplate
    }
    if format_type.lower() not in templates:
        raise ValueError(f"Unsupported format type: {format_type}")
    return templates[format_type.lower()]


def get_file_extension(format_type: str) -> str:
    """Get the file extension for the given format."""
    extensions = {
        'html': '.html',
        'markdown': '.md'
    }
    return extensions.get(format_type.lower(), '')


class ReportGenerator:
    """
    Main report generator class for notebook analysis results.

    This class orchestrates the report generation process by combining
    analysis results with appropriate formatters and templates.
    """

    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the report generator.

        Args:
            output_dir (str): Directory for storing generated reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._initialize_formatters()

    def _initialize_formatters(self):
        """Initialize all available formatters."""
        self.formatters = {
            'builder_mindset': {
                'code_formatting': CodeFormattingFormatter(),
                'code_structure': CodeStructureFormatter(),
                'code_comments': CodeCommentsFormatter(),
                'code_conciseness': CodeConcisenessFormatter(),
                'code_reusability': CodeReusabilityFormatter(),
                'advanced_techniques': AdvancedTechniquesFormatter(),
                'dataset_join': DatasetJoinFormatter()
            },
            'business_intelligence': {
                'visualization_types': VisualizationTypesFormatter(),
                'visualization_formatting': VisualizationFormattingFormatter()
            }
        }

    def generate_report(self,
                       analysis_results: Dict[str, Any],
                       format_type: str = 'html',
                       filename: Optional[str] = None) -> str:
        """
        Generate a report from analysis results.

        Args:
            analysis_results (Dict[str, Any]): Results from notebook analysis
            format_type (str): Output format ('html' or 'markdown')
            filename (Optional[str]): Custom filename for the report

        Returns:
            str: Path to the generated report file

        Raises:
            ValueError: If format type is not supported
        """
        # Prepare report data
        report_data = self._prepare_report_data(analysis_results)
        
        # Get appropriate template
        template_class = get_template_by_format(format_type)
        template = template_class()
        
        # Generate report content
        content = template.render(report_data)
        
        # Save report
        file_path = self._save_report(content, format_type, filename)
        
        return file_path

def _prepare_report_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare report data by formatting analysis results.

    Args:
        analysis_results (Dict[str, Any]): Raw analysis results

    Returns:
        Dict[str, Any]: Formatted report data
    """
    # Extract the actual results from the nested structure
    results = analysis_results.get('results', {})
    metadata = analysis_results.get('metadata', {})
    summary = analysis_results.get('summary', {})

    report_data = {
        'title': f"Notebook Analysis Report - {metadata.get('filename', 'Untitled')}",
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '1.0.0',
        'overall_score': summary.get('overall_score', 0),
        'sections': []
    }

    # Process builder mindset metrics
    if 'builder_mindset' in results:
        builder_sections = []
        for metric_name, metric_data in results['builder_mindset'].items():
            if metric_name in self.formatters['builder_mindset']:
                formatter = self.formatters['builder_mindset'][metric_name]
                section = {
                    'title': metric_name.replace('_', ' ').title(),
                    'content': formatter.format_metrics(metric_data),
                    'findings': metric_data.get('findings', []),
                    'suggestions': metric_data.get('suggestions', []),
                    'score': metric_data.get('score', 0),
                    'charts': []
                }
                
                # Add charts if available
                if 'charts' in metric_data:
                    section['charts'] = metric_data['charts']
                
                builder_sections.append(section)
        
        if builder_sections:
            report_data['sections'].extend(builder_sections)

    # Process business intelligence metrics
    if 'business_intelligence' in results:
        bi_sections = []
        for metric_name, metric_data in results['business_intelligence'].items():
            if metric_name in self.formatters['business_intelligence']:
                formatter = self.formatters['business_intelligence'][metric_name]
                section = {
                    'title': metric_name.replace('_', ' ').title(),
                    'content': formatter.format_metrics(metric_data),
                    'findings': metric_data.get('findings', []),
                    'suggestions': metric_data.get('suggestions', []),
                    'score': metric_data.get('score', 0),
                    'charts': []
                }
                
                # Add charts if available
                if 'charts' in metric_data:
                    section['charts'] = metric_data['charts']
                
                bi_sections.append(section)
        
        if bi_sections:
            report_data['sections'].extend(bi_sections)

    # Add error section if there are any errors
    if summary.get('errors'):
        report_data['sections'].append({
            'title': 'Analysis Errors',
            'content': '\n'.join(summary['errors']),
            'findings': [],
            'suggestions': ['Please check the error messages and try again.'],
            'score': 0,
            'charts': []
        })

    return report_data

    def _format_builder_mindset_sections(
        self, builder_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Format builder mindset metrics into report sections.

        Args:
            builder_metrics (Dict[str, Any]): Builder mindset analysis results

        Returns:
            List[Dict[str, Any]]: Formatted sections
        """
        sections = []
        for metric_type, formatter in self.formatters['builder_mindset'].items():
            if metric_type in builder_metrics:
                sections.append(
                    formatter.format_metrics(builder_metrics[metric_type]).to_dict()
                )
        return sections

    def _format_business_intelligence_sections(
        self, bi_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Format business intelligence metrics into report sections.

        Args:
            bi_metrics (Dict[str, Any]): Business intelligence analysis results

        Returns:
            List[Dict[str, Any]]: Formatted sections
        """
        sections = []
        for metric_type, formatter in self.formatters['business_intelligence'].items():
            if metric_type in bi_metrics:
                sections.append(
                    formatter.format_metrics(bi_metrics[metric_type]).to_dict()
                )
        return sections

    def _calculate_overall_score(self, analysis_results: Dict[str, Any]) -> int:
        """
        Calculate overall score from analysis results.

        Args:
            analysis_results (Dict[str, Any]): Analysis results

        Returns:
            int: Overall score (0-100)
        """
        scores = []
        
        # Collect builder mindset scores
        if 'builder_mindset' in analysis_results:
            for metric in analysis_results['builder_mindset'].values():
                if hasattr(metric, 'score'):
                    scores.append(metric.score)
        
        # Collect business intelligence scores
        if 'business_intelligence' in analysis_results:
            for metric in analysis_results['business_intelligence'].values():
                if hasattr(metric, 'score'):
                    scores.append(metric.score)
        
        return round(sum(scores) / len(scores)) if scores else 0

    def _save_report(self,
                    content: str,
                    format_type: str,
                    filename: Optional[str] = None) -> str:
        """
        Save report content to file.

        Args:
            content (str): Report content
            format_type (str): Output format
            filename (Optional[str]): Custom filename

        Returns:
            str: Path to the saved report file
        """
        if filename is None:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"notebook_analysis_{timestamp}"
        
        extension = get_file_extension(format_type)
        file_path = os.path.join(self.output_dir, f"{filename}{extension}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
