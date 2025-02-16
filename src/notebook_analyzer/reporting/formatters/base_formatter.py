from typing import Dict, Any, List
from datetime import datetime

class BaseFormatter:
    """Base formatter class providing common formatting utilities."""

    def __init__(self):
        self.timestamp = "2025-02-16 01:02:01"
        self.username = "Barrhann"

    def _format_metric(self, name: str, score: float, benchmark: str, definition: str,
                      details: Dict[str, Any] = None, findings: Dict[str, List[str]] = None) -> str:
        """Format metric with detailed information."""
        sections = [f"\n{name}"]
        sections.append("─" * 40)
        assessment = self._get_assessment_level(score)
        sections.append(f"Score: {score:.1f}/100 ({assessment})")
        sections.append(f"Definition: {definition}")
        sections.append(f"Benchmark: {benchmark}")
        
        if details:
            sections.append("\nDetails:")
            for key, value in details.items():
                if isinstance(value, list):
                    sections.append(f"• {key}:")
                    for item in value:
                        sections.append(f"  - {item}")
                else:
                    sections.append(f"• {key}: {value}")
        
        if findings:
            if findings.get('positive'):
                sections.append("\nStrengths in this metric:")
                for finding in findings['positive'][:3]:  # Top 3 strengths
                    sections.append(f"✓ {finding}")
            
            if findings.get('negative'):
                sections.append("\nAreas for Improvement in this metric:")
                for finding in findings['negative'][:3]:  # Top 3 issues
                    sections.append(f"! {finding}")
        
        return '\n'.join(sections)

    def _get_assessment_level(self, score: float) -> str:
        """Get detailed assessment level based on score."""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Fair"
        else:
            return "Needs Improvement"

    def _format_component_summary(self, name: str, score: float,
                                strongest_metric: str, weakest_metric: str,
                                key_findings: Dict[str, str] = None) -> str:
        """Format component summary with highlights."""
        sections = [
            f"\n{name} Component",
            "─" * 40,
            f"Overall Score: {score:.1f}/100 ({self._get_assessment_level(score)})",
            f"Strongest Area: {strongest_metric}",
            f"Needs Most Attention: {weakest_metric}"
        ]
        
        if key_findings:
            if key_findings.get('highlight'):
                sections.append(f"\nKey Highlight: {key_findings['highlight']}")
            if key_findings.get('concern'):
                sections.append(f"Main Concern: {key_findings['concern']}")
        
        return '\n'.join(sections)

    def _get_metric_score(self, metrics: Dict[str, Any], key: str, subkey: str = 'score') -> float:
        """Safely get metric score with default value."""
        try:
            metric = metrics.get(key, {})
            if isinstance(metric, dict):
                value = metric.get(subkey, 0.0)
            else:
                value = float(metric)
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _format_block_header(self, title: str) -> str:
        """Format block header."""
        return f"\n{title}\n{'=' * 80}"

    def _format_findings(self, findings: Dict[str, List[str]]) -> str:
        """Format findings section."""
        if not isinstance(findings, dict):
            findings = {'positive': [], 'negative': []}
            
        sections = []
        
        if findings.get('positive'):
            sections.append("\nKey Strengths:")
            for finding in findings['positive'][:5]:  # Show top 5 strengths
                sections.append(f"✓ {finding}")
                
        if findings.get('negative'):
            sections.append("\nPriority Improvements:")
            for finding in findings['negative'][:5]:  # Show top 5 issues
                sections.append(f"! {finding}")
                
        return '\n'.join(sections)
