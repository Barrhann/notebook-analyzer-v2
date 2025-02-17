from typing import Dict, Any
from ..base_formatter import BaseFormatter

class OverallScoresFormatter(BaseFormatter):
    def format_section(self, builder_score: float, bi_score: float) -> str:
        """Format overall quality scores section."""
        sections = [
            self._format_block_header("OVERALL QUALITY SCORES"),
            "\nBuilder Mindset Score:",
            f"• Score: {builder_score:.1f}/100 ({self._get_assessment_level(builder_score)})",
            "• Components (weighted equally):",
            "  - Code Formatting: Style consistency, indentation, and line length",
            "  - Code Comments: Documentation coverage and quality",
            "  - Code Conciseness: Duplication, function length, and variable usage",
            "  - Code Structure: Modularity and complexity",
            "  - Dataset Operations: Join efficiency and key handling",
            "  - Code Reusability: Parameter usage and function reuse",
            "  - Advanced Techniques: Library usage and optimization",
            
            "\nBusiness Intelligence Score:",
            f"• Score: {bi_score:.1f}/100 ({self._get_assessment_level(bi_score)})",
            "• Components:",
            "  - Visualization Types (50%): Diversity and appropriateness",
            "  - Visualization Formatting (50%): Clarity and readability",
            
            "\nOverall Assessment:",
            f"• Overall Score: {((builder_score + bi_score) / 2):.1f}/100",
            f"• Builder Mindset: {self._get_assessment_level(builder_score)}",
            f"• Business Intelligence: {self._get_assessment_level(bi_score)}"
        ]
        return '\n'.join(sections)
