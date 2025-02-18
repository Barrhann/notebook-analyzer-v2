"""
Report Generator.

This module provides the main functionality for generating analysis reports
by combining analysis results with appropriate templates and formatters.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-18 00:20:29
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
            ValueError: If format type is not supported or if results are invalid
        """
        if not analysis_results:
            raise ValueError("Analysis results cannot be empty")

        # Prepare report data
        try:
            report_data = self._prepare_report_data(analysis_results)
        except Exception as e:
            raise ValueError(f"Failed to prepare report data: {str(e)}")

        # Get appropriate template
        template_class = get_template_by_format(format_type)
        template = template_class()

        # Generate report content
        try:
            content = template.render(report_data)
        except Exception as e:
            raise ValueError(f"Failed to render report template: {str(e)}")

        # Save report
        try:
            file_path = self._save_report(content, format_type, filename)
        except Exception as e:
            raise ValueError(f"Failed to save report: {str(e)}")

        return file_path

    def _prepare_report_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare report data by formatting analysis results.

        Args:
            analysis_results (Dict[str, Any]): Raw analysis results

        Returns:
            Dict[str, Any]: Formatted report data
        """
        # Handle both nested and flat result structures
        results = (analysis_results.get('results', {})
                  if isinstance(analysis_results.get('results'), dict)
                  else analysis_results)
        
        metadata = analysis_results.get('metadata', {})
        summary = analysis_results.get('summary', {})

        # Get filename from metadata or use a default
        filename = metadata.get('filename', 'Untitled')
        if not filename.endswith('.ipynb'):
            filename += '.ipynb'

        # Initialize report data
        report_data = {
            'title': f"Notebook Analysis Report - {filename}",
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0.0',
            'overall_score': summary.get('overall_score', 0),
            'sections': []
        }

        # Add summary section first
        summary_section = {
            'title': 'Analysis Summary',
            'content': [],
            'findings': summary.get('findings', []),
            'suggestions': summary.get('suggestions', []),
            'score': summary.get('overall_score', 0),
            'charts': summary.get('charts', [])
        }

        # Add overall metrics summary
        if 'metrics_summary' in summary:
            summary_section['content'].append('### Overall Metrics Performance\n')
            for metric, score in summary['metrics_summary'].items():
                summary_section['content'].append(f"- {metric}: {score:.2f}/100")

        # Add key statistics if available
        if 'statistics' in summary:
            summary_section['content'].append('\n### Key Statistics\n')
            for stat, value in summary['statistics'].items():
                summary_section['content'].append(f"- {stat}: {value}")

        report_data['sections'].append(summary_section)

        # Process builder mindset metrics
        if 'builder_mindset' in results:
            category_section = {
                'title': 'Builder Mindset Analysis',
                'content': ['Analysis of code quality and best practices:'],
                'findings': [],
                'suggestions': [],
                'score': 0,
                'charts': []
            }

            scores = []
            for metric_name, metric_data in results['builder_mindset'].items():
                if isinstance(metric_data, dict):
                    scores.append(metric_data.get('score', 0))
                    subsection = [f"\n### {metric_name.replace('_', ' ').title()}"]
                    
                    if 'description' in metric_data:
                        subsection.append(f"\n{metric_data['description']}")
                    
                    if 'score' in metric_data:
                        subsection.append(f"\nScore: {metric_data['score']:.2f}/100")
                    
                    if 'findings' in metric_data:
                        category_section['findings'].extend(metric_data['findings'])
                    
                    if 'suggestions' in metric_data:
                        category_section['suggestions'].extend(metric_data['suggestions'])
                    
                    if 'charts' in metric_data:
                        category_section['charts'].extend(metric_data['charts'])
                    
                    category_section['content'].extend(subsection)

            if scores:
                category_section['score'] = sum(scores) / len(scores)
            
            report_data['sections'].append(category_section)

        # Process business intelligence metrics
        if 'business_intelligence' in results:
            category_section = {
                'title': 'Business Intelligence Analysis',
                'content': ['Analysis of data visualization and analytics:'],
                'findings': [],
                'suggestions': [],
                'score': 0,
                'charts': []
            }

            scores = []
            for metric_name, metric_data in results['business_intelligence'].items():
                if isinstance(metric_data, dict):
                    scores.append(metric_data.get('score', 0))
                    subsection = [f"\n### {metric_name.replace('_', ' ').title()}"]
                    
                    if 'description' in metric_data:
                        subsection.append(f"\n{metric_data['description']}")
                    
                    if 'score' in metric_data:
                        subsection.append(f"\nScore: {metric_data['score']:.2f}/100")
                    
                    if 'findings' in metric_data:
                        category_section['findings'].extend(metric_data['findings'])
                    
                    if 'suggestions' in metric_data:
                        category_section['suggestions'].extend(metric_data['suggestions'])
                    
                    if 'charts' in metric_data:
                        category_section['charts'].extend(metric_data['charts'])
                    
                    category_section['content'].extend(subsection)

            if scores:
                category_section['score'] = sum(scores) / len(scores)
            
            report_data['sections'].append(category_section)

        # Add error section if there are any errors
        if summary.get('errors'):
            report_data['sections'].append({
                'title': 'Analysis Errors',
                'content': ['The following errors occurred during analysis:'],
                'findings': summary['errors'],
                'suggestions': ['Please check the error messages and try again.'],
                'score': 0,
                'charts': []
            })

        # Ensure there's at least one section
        if not report_data['sections']:
            report_data['sections'].append({
                'title': 'Analysis Results',
                'content': ['No detailed analysis results available.'],
                'findings': ['Analysis completed with no detailed metrics.'],
                'suggestions': ['Try running the analysis with specific metrics enabled.'],
                'score': report_data['overall_score'],
                'charts': []
            })

        return report_data

    def _process_metric_category(self,
                               metrics: Dict[str, Any],
                               category: str) -> List[Dict[str, Any]]:
        """
        Process metrics for a specific category.

        Args:
            metrics (Dict[str, Any]): Metrics data
            category (str): Category name ('builder_mindset' or 'business_intelligence')

        Returns:
            List[Dict[str, Any]]: List of formatted sections
        """
        sections = []
        for metric_name, metric_data in metrics.items():
            if metric_name in self.formatters[category]:
                formatter = self.formatters[category][metric_name]
                try:
                    section = self._create_metric_section(metric_name, metric_data, formatter)
                    sections.append(section)
                except Exception as e:
                    # Log the error but continue processing other metrics
                    print(f"Error processing metric {metric_name}: {str(e)}")
        return sections

    def _create_metric_section(self,
                             metric_name: str,
                             metric_data: Dict[str, Any],
                             formatter: Any) -> Dict[str, Any]:
        """
        Create a section for a specific metric.

        Args:
            metric_name (str): Name of the metric
            metric_data (Dict[str, Any]): Metric data
            formatter: Formatter for the metric

        Returns:
            Dict[str, Any]: Formatted section
        """
        # Handle both object and dict metric data
        if hasattr(metric_data, 'to_dict'):
            metric_dict = metric_data.to_dict()
        else:
            metric_dict = metric_data

        section = {
            'title': metric_name.replace('_', ' ').title(),
            'content': formatter.format_metrics(metric_dict),
            'findings': metric_dict.get('findings', []),
            'suggestions': metric_dict.get('suggestions', []),
            'score': metric_dict.get('score', 0),
            'charts': metric_dict.get('charts', [])
        }

        return section

    def _create_summary_section(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create the summary section.

        Args:
            summary (Dict[str, Any]): Summary data

        Returns:
            Dict[str, Any]: Formatted summary section
        """
        content_parts = []
        
        if 'description' in summary:
            content_parts.append(summary['description'])
        
        if 'metrics_summary' in summary:
            content_parts.append("\n### Metrics Summary\n")
            for metric, score in summary['metrics_summary'].items():
                content_parts.append(f"- {metric}: {score}/100")

        return {
            'title': 'Analysis Summary',
            'content': '\n'.join(content_parts),
            'findings': summary.get('findings', []),
            'suggestions': summary.get('suggestions', []),
            'score': summary.get('overall_score', 0),
            'charts': summary.get('charts', [])
        }

    def _create_error_section(self, errors: List[str]) -> Dict[str, Any]:
        """
        Create the error section.

        Args:
            errors (List[str]): List of error messages

        Returns:
            Dict[str, Any]: Formatted error section
        """
        return {
            'title': 'Analysis Errors',
            'content': '\n'.join(errors),
            'findings': [],
            'suggestions': ['Please check the error messages and try again.'],
            'score': 0,
            'charts': []
        }

    def _create_default_section(self) -> Dict[str, Any]:
        """
        Create a default section when no other sections are available.

        Returns:
            Dict[str, Any]: Default section
        """
        return {
            'title': 'Analysis Results',
            'content': 'No detailed analysis results available.',
            'findings': ['Analysis completed with no detailed metrics.'],
            'suggestions': ['Try running the analysis with specific metrics enabled.'],
            'score': 0,
            'charts': []
        }

    def _calculate_overall_score(self, analysis_results: Dict[str, Any]) -> int:
        """
        Calculate overall score from analysis results.

        Args:
            analysis_results (Dict[str, Any]): Analysis results

        Returns:
            int: Overall score (0-100)
        """
        # First try to get the score from summary
        if 'summary' in analysis_results:
            score = analysis_results['summary'].get('overall_score')
            if score is not None:
                return score

        # If no summary score, calculate from individual metrics
        scores = []
        results = analysis_results.get('results', analysis_results)
        
        # Collect builder mindset scores
        if 'builder_mindset' in results:
            for metric in results['builder_mindset'].values():
                if hasattr(metric, 'score'):
                    scores.append(metric.score)
                elif isinstance(metric, dict) and 'score' in metric:
                    scores.append(metric['score'])

        # Collect business intelligence scores
        if 'business_intelligence' in results:
            for metric in results['business_intelligence'].values():
                if hasattr(metric, 'score'):
                    scores.append(metric.score)
                elif isinstance(metric, dict) and 'score' in metric:
                    scores.append(metric['score'])

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
        if not content:
            raise ValueError("Report content cannot be empty")

        if filename is None:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"notebook_analysis_{timestamp}"

        extension = get_file_extension(format_type)
        file_path = os.path.join(self.output_dir, f"{filename}{extension}")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise ValueError(f"Failed to write report to file: {str(e)}")

        return file_path
