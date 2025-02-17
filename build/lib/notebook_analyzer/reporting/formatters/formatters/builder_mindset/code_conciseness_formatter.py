from typing import Dict, Any
from ...base_formatter import BaseFormatter

class CodeConcisenessFormatter(BaseFormatter):
    def format_section(self, conciseness: Dict[str, Any]) -> str:
        """Format code conciseness section with detailed metrics."""
        sections = []
        metrics = conciseness.get('metrics', {})
        
        # Calculate individual scores
        duplication_score = self._get_metric_score(metrics, 'code_duplication')
        function_length_score = self._get_metric_score(metrics, 'function_length')
        variable_score = self._get_metric_score(metrics, 'variable_usage')
        
        # Component summary
        avg_score = (duplication_score + function_length_score + variable_score) / 3
        scores = {
            'Code Duplication': duplication_score,
            'Function Length': function_length_score,
            'Variable Usage': variable_score
        }
        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])
        
        sections.append(self._format_component_summary(
            name="CODE CONCISENESS",
            score=avg_score,
            strongest_metric=f"{strongest[0]} ({strongest[1]:.1f}/100)",
            weakest_metric=f"{weakest[0]} ({weakest[1]:.1f}/100)",
            key_findings={
                'highlight': conciseness.get('key_highlight', 'Good variable naming and reuse'),
                'concern': conciseness.get('main_concern', 'Some code duplication detected')
            }
        ))
        
        # Code Duplication Details
        duplication_details = {
            'Duplicate Blocks Found': metrics.get('code_duplication', {}).get('duplicate_blocks', 0),
            'Lines of Duplicated Code': metrics.get('code_duplication', {}).get('duplicate_lines', 0),
            'Duplication Percentage': f"{metrics.get('code_duplication', {}).get('duplication_ratio', 0):.1%}",
            'Largest Duplicate Block': metrics.get('code_duplication', {}).get('largest_duplicate', 0)
        }
        
        sections.append(self._format_metric(
            name="Code Duplication",
            score=duplication_score,
            benchmark="good ≥ 90, moderate ≥ 75, poor < 75",
            definition="Measures presence of repeated code blocks",
            details=duplication_details,
            findings={
                'positive': metrics.get('code_duplication', {}).get('good_practices', []),
                'negative': metrics.get('code_duplication', {}).get('duplication_instances', [])
            }
        ))
        
        # Function Length Details
        function_length_details = {
            'Average Function Length': metrics.get('function_length', {}).get('avg_length', 0),
            'Longest Function': metrics.get('function_length', {}).get('max_length', 0),
            'Functions > 50 lines': metrics.get('function_length', {}).get('long_functions', 0),
            'Complex Functions': metrics.get('function_length', {}).get('complex_functions', [])
        }
        
        sections.append(self._format_metric(
            name="Function Length",
            score=function_length_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Evaluates function size and complexity",
            details=function_length_details,
            findings={
                'positive': metrics.get('function_length', {}).get('well_sized_functions', []),
                'negative': metrics.get('function_length', {}).get('oversized_functions', [])
            }
        ))
        
        # Variable Usage Details
        variable_details = {
            'Unused Variables': metrics.get('variable_usage', {}).get('unused_vars', 0),
            'Single-Use Variables': metrics.get('variable_usage', {}).get('single_use_vars', 0),
            'Well-Named Variables': metrics.get('variable_usage', {}).get('well_named_vars', 0),
            'Naming Issues': metrics.get('variable_usage', {}).get('naming_issues', [])
        }
        
        sections.append(self._format_metric(
            name="Variable Usage",
            score=variable_score,
            benchmark="good ≥ 90, moderate ≥ 80, poor < 80",
            definition="Analyzes efficient use of variables",
            details=variable_details,
            findings={
                'positive': metrics.get('variable_usage', {}).get('good_practices', []),
                'negative': metrics.get('variable_usage', {}).get('improvement_needed', [])
            }
        ))
        
        return '\n'.join(sections)
