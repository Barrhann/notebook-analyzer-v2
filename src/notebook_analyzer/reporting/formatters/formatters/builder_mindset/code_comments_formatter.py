from typing import Dict, Any
from ...base_formatter import BaseFormatter

class CodeCommentsFormatter(BaseFormatter):
    def format_section(self, comments: Dict[str, Any]) -> str:
        """Format code comments section with detailed metrics."""
        sections = []
        metrics = comments.get('metrics', {})
        
        # Calculate individual scores
        coverage_score = self._get_metric_score(metrics, 'comment_coverage')
        quality_score = self._get_metric_score(metrics, 'comment_quality')
        docstring_score = self._get_metric_score(metrics, 'docstring_coverage')
        
        # Component summary
        avg_score = (coverage_score + quality_score + docstring_score) / 3
        scores = {
            'Comment Coverage': coverage_score,
            'Comment Quality': quality_score,
            'Docstring Coverage': docstring_score
        }
        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])
        
        sections.append(self._format_component_summary(
            name="CODE COMMENTS",
            score=avg_score,
            strongest_metric=f"{strongest[0]} ({strongest[1]:.1f}/100)",
            weakest_metric=f"{weakest[0]} ({weakest[1]:.1f}/100)",
            key_findings={
                'highlight': comments.get('key_highlight', 'Good docstring coverage in main functions'),
                'concern': comments.get('main_concern', 'Some complex sections lack explanatory comments')
            }
        ))
        
        # Comment Coverage Details
        coverage_details = {
            'Total Lines': metrics.get('comment_coverage', {}).get('total_lines', 0),
            'Commented Lines': metrics.get('comment_coverage', {}).get('commented_lines', 0),
            'Coverage Ratio': f"{metrics.get('comment_coverage', {}).get('coverage_ratio', 0):.1%}",
            'Uncommented Complex Blocks': metrics.get('comment_coverage', {}).get('complex_uncommented', [])
        }
        
        sections.append(self._format_metric(
            name="Comment Coverage",
            score=coverage_score,
            benchmark="good ≥ 80, moderate ≥ 60, poor < 60",
            definition="Percentage of code with explanatory comments",
            details=coverage_details,
            findings={
                'positive': metrics.get('comment_coverage', {}).get('well_commented_sections', []),
                'negative': metrics.get('comment_coverage', {}).get('poorly_commented_sections', [])
            }
        ))
        
        # Comment Quality Details
        quality_details = {
            'Informative Comments': metrics.get('comment_quality', {}).get('informative_count', 0),
            'Generic Comments': metrics.get('comment_quality', {}).get('generic_count', 0),
            'Outdated Comments': metrics.get('comment_quality', {}).get('outdated_count', 0),
            'Common Issues': metrics.get('comment_quality', {}).get('common_issues', [])
        }
        
        sections.append(self._format_metric(
            name="Comment Quality",
            score=quality_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Evaluates clarity and meaningfulness of comments",
            details=quality_details,
            findings={
                'positive': metrics.get('comment_quality', {}).get('good_examples', []),
                'negative': metrics.get('comment_quality', {}).get('improvement_needed', [])
            }
        ))
        
        # Docstring Details
        docstring_details = {
            'Functions with Docstrings': metrics.get('docstring_coverage', {}).get('documented_functions', 0),
            'Total Functions': metrics.get('docstring_coverage', {}).get('total_functions', 0),
            'Classes with Docstrings': metrics.get('docstring_coverage', {}).get('documented_classes', 0),
            'Total Classes': metrics.get('docstring_coverage', {}).get('total_classes', 0),
            'Missing Critical Docstrings': metrics.get('docstring_coverage', {}).get('critical_missing', [])
        }
        
        sections.append(self._format_metric(
            name="Docstring Coverage",
            score=docstring_score,
            benchmark="good ≥ 90, moderate ≥ 75, poor < 75",
            definition="Percentage of functions/classes with docstrings",
            details=docstring_details,
            findings={
                'positive': metrics.get('docstring_coverage', {}).get('well_documented', []),
                'negative': metrics.get('docstring_coverage', {}).get('missing_docstrings', [])
            }
        ))
        
        return '\n'.join(sections)
