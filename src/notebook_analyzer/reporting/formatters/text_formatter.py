from typing import Dict, Any, List
from .base_formatter import BaseFormatter
from .utils.metric_utils import calculate_block_score
from .formatters.header_formatter import HeaderFormatter
from .formatters.overall_scores_formatter import OverallScoresFormatter
from .formatters.builder_mindset import (
    CodeFormattingFormatter,
    CodeCommentsFormatter,
    CodeConcisenessFormatter,
    CodeStructureFormatter,
    DatasetJoinFormatter,
    CodeReusabilityFormatter,
    AdvancedTechniquesFormatter
)
from .formatters.business_intelligence import (
    VisualizationTypesFormatter,
    VisualizationFormattingFormatter
)

class TextReportFormatter(BaseFormatter):
    """Main formatter class that orchestrates all formatting components."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize all formatters
        self.header_formatter = HeaderFormatter()
        self.overall_scores_formatter = OverallScoresFormatter()
        
        # Builder Mindset formatters
        self.builder_mindset_formatters = {
            'code_formatting': CodeFormattingFormatter(),
            'code_comments': CodeCommentsFormatter(),
            'code_conciseness': CodeConcisenessFormatter(),
            'code_structure': CodeStructureFormatter(),
            'dataset_join': DatasetJoinFormatter(),
            'code_reusability': CodeReusabilityFormatter(),
            'advanced_techniques': AdvancedTechniquesFormatter()
        }
        
        # Business Intelligence formatters
        self.bi_formatters = {
            'visualization_formatting': VisualizationFormattingFormatter(),
            'visualization_types': VisualizationTypesFormatter()
        }

    def format_report(self, report_data: Dict[str, Any]) -> str:
        """Format the complete report."""
        sections = []
        analysis = report_data.get('analysis', {})
        summary = report_data.get('summary', {})
        
        # Report Header (only once)
        sections.append(
            f"NOTEBOOK ANALYSIS REPORT\n"
            f"Generated: {self.timestamp}\n"
            f"User: {self.username}\n"
            f"{'=' * 80}"
        )
        
        # Overall Quality Scores (at the beginning)
        builder_mindset_score = summary.get('builder_mindset_score', 0.0)
        bi_score = summary.get('bi_score', 0.0)
        sections.append(self.overall_scores_formatter.format_section(
            builder_mindset_score,
            bi_score
        ))
        
        # Executive Summary
        sections.append(self.header_formatter.format_summary(summary))
        
        # Builder Mindset sections with detailed metrics
        sections.append(self._format_block_header("BUILDER MINDSET ANALYSIS"))
        builder_sections = []
        builder_scores = []
        
        for key, formatter in self.builder_mindset_formatters.items():
            if key in analysis:
                try:
                    section_data = analysis[key]
                    score = calculate_block_score(section_data)
                    builder_scores.append(score)
                    builder_sections.append(formatter.format_section(section_data))
                except Exception as e:
                    print(f"Warning: Error processing {key}: {str(e)}")
                    builder_scores.append(0.0)
        
        # Business Intelligence sections with detailed metrics
        sections.append(self._format_block_header("BUSINESS INTELLIGENCE ANALYSIS"))
        bi_sections = []
        bi_scores = []
        
        for key, formatter in self.bi_formatters.items():
            if key in analysis:
                try:
                    section_data = analysis[key]
                    score = calculate_block_score(section_data)
                    bi_scores.append(score)
                    bi_sections.append(formatter.format_section(section_data))
                except Exception as e:
                    print(f"Warning: Error processing {key}: {str(e)}")
                    bi_scores.append(0.0)
        
        # Add all sections
        sections.extend(builder_sections)
        sections.extend(bi_sections)
        
        return '\n\n'.join(sections)
