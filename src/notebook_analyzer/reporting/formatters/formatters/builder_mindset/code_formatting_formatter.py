from typing import Dict, Any
from ...base_formatter import BaseFormatter

class CodeFormattingFormatter(BaseFormatter):
    def format_section(self, formatting: Dict[str, Any]) -> str:
        """Format code formatting section with detailed metrics."""
        sections = []
        metrics = formatting.get('metrics', {})
        
        # Calculate individual scores
        style_score = self._get_metric_score(metrics, 'style_consistency')
        indent_score = self._get_metric_score(metrics, 'indentation')
        line_length_score = self._get_metric_score(metrics, 'line_length')
        
        # Component summary
        avg_score = (style_score + indent_score + line_length_score) / 3
        scores = {
            'Style Consistency': style_score,
            'Indentation': indent_score,
            'Line Length': line_length_score
        }
        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])
        
        sections.append(self._format_component_summary(
            name="CODE FORMATTING",
            score=avg_score,
            strongest_metric=f"{strongest[0]} ({strongest[1]:.1f}/100)",
            weakest_metric=f"{weakest[0]} ({weakest[1]:.1f}/100)",
            key_findings={
                'highlight': formatting.get('key_highlight', 'Good adherence to PEP 8 guidelines'),
                'concern': formatting.get('main_concern', 'Some line length violations detected')
            }
        ))
        
        # Style Consistency Details
        style_details = {
            'Files Analyzed': metrics.get('style_consistency', {}).get('files_analyzed', 0),
            'PEP 8 Violations': [
                f"{v['count']} {v['type']} violations"
                for v in metrics.get('style_consistency', {}).get('violation_types', [])
            ],
            'Most Common Issues': metrics.get('style_consistency', {}).get('common_issues', [])
        }
        
        sections.append(self._format_metric(
            name="Style Consistency",
            score=style_score,
            benchmark="good ≥ 90, moderate ≥ 70, poor < 70",
            definition="Measures adherence to PEP 8 style guidelines",
            details=style_details,
            findings={
                'positive': metrics.get('style_consistency', {}).get('good_practices', []),
                'negative': metrics.get('style_consistency', {}).get('violations', [])
            }
        ))
        
        # Indentation Details
        indent_details = {
            'Consistent Blocks': metrics.get('indentation', {}).get('consistent_blocks', 0),
            'Inconsistent Blocks': metrics.get('indentation', {}).get('inconsistent_blocks', 0),
            'Common Patterns': metrics.get('indentation', {}).get('common_patterns', [])
        }
        
        sections.append(self._format_metric(
            name="Indentation",
            score=indent_score,
            benchmark="good ≥ 95, moderate ≥ 80, poor < 80",
            definition="Evaluates consistent use of indentation",
            details=indent_details,
            findings={
                'positive': metrics.get('indentation', {}).get('good_practices', []),
                'negative': metrics.get('indentation', {}).get('issues', [])
            }
        ))
        
        # Line Length Details
        line_length_details = {
            'Lines Analyzed': metrics.get('line_length', {}).get('total_lines', 0),
            'Lines > 79 chars': metrics.get('line_length', {}).get('long_lines', 0),
            'Max Line Length': metrics.get('line_length', {}).get('max_length', 0),
            'Common Causes': metrics.get('line_length', {}).get('common_causes', [])
        }
        
        sections.append(self._format_metric(
            name="Line Length",
            score=line_length_score,
            benchmark="good ≥ 90, moderate ≥ 70, poor < 70",
            definition="Checks if lines stay within recommended length",
            details=line_length_details,
            findings={
                'positive': metrics.get('line_length', {}).get('good_practices', []),
                'negative': metrics.get('line_length', {}).get('violations', [])
            }
        ))
        
        return '\n'.join(sections)
