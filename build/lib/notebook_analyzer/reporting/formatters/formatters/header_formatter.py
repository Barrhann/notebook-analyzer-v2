from typing import Dict, Any
from ..base_formatter import BaseFormatter

class HeaderFormatter(BaseFormatter):
    def format_summary(self, summary: Dict[str, Any]) -> str:
        """Format executive summary section."""
        sections = [
            self._format_block_header("EXECUTIVE SUMMARY"),
            "\nAnalysis Overview:",
            f"• Total Files Analyzed: {summary.get('total_files', 0)}",
            f"• Total Lines of Code: {summary.get('total_lines', 0)}",
            f"• Analysis Duration: {summary.get('analysis_duration', '0')} seconds",
            "\nKey Metrics:",
            f"• Code Quality Score: {summary.get('code_quality_score', 0):.1f}/100",
            f"• Documentation Score: {summary.get('documentation_score', 0):.1f}/100",
            f"• Visualization Score: {summary.get('visualization_score', 0):.1f}/100",
        ]
        
        # Add high-priority findings
        high_priority = summary.get('high_priority_findings', [])
        if high_priority:
            sections.append("\nHigh-Priority Findings:")
            for finding in high_priority:
                sections.append(f"! {finding}")
        
        return '\n'.join(sections)
