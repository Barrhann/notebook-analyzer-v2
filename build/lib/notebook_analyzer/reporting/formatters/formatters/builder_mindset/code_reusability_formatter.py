from typing import Dict, Any
from ...base_formatter import BaseFormatter

class CodeReusabilityFormatter(BaseFormatter):
    def format_section(self, reusability: Dict[str, Any]) -> str:
        """Format code reusability section with detailed metrics."""
        sections = []
        metrics = reusability.get('metrics', {})
        
        # Calculate individual scores
        function_reuse_score = self._get_metric_score(metrics, 'function_reuse')
        parameter_score = self._get_metric_score(metrics, 'parameter_usage')
        modularity_score = self._get_metric_score(metrics, 'code_modularity')
        
        # Component summary
        avg_score = (function_reuse_score + parameter_score + modularity_score) / 3
        scores = {
            'Function Reuse': function_reuse_score,
            'Parameter Usage': parameter_score,
            'Code Modularity': modularity_score
        }
        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])
        
        sections.append(self._format_component_summary(
            name="CODE REUSABILITY",
            score=avg_score,
            strongest_metric=f"{strongest[0]} ({strongest[1]:.1f}/100)",
            weakest_metric=f"{weakest[0]} ({weakest[1]:.1f}/100)",
            key_findings={
                'highlight': reusability.get('key_highlight', 'Good function parameterization'),
                'concern': reusability.get('main_concern', 'Some functions could be more generic')
            }
        ))
        
        # Function Reuse Details
        reuse_details = {
            'Reusable Functions': metrics.get('function_reuse', {}).get('reusable_count', 0),
            'Function Call Count': metrics.get('function_reuse', {}).get('call_count', {}),
            'Repeated Code Blocks': metrics.get('function_reuse', {}).get('repeated_blocks', []),
            'Reuse Opportunities': metrics.get('function_reuse', {}).get('opportunities', [])
        }
        
        sections.append(self._format_metric(
            name="Function Reuse",
            score=function_reuse_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Measures how effectively functions are reused across the codebase",
            details=reuse_details,
            findings={
                'positive': metrics.get('function_reuse', {}).get('good_practices', []),
                'negative': metrics.get('function_reuse', {}).get('improvement_areas', [])
            }
        ))
        
        # Parameter Usage Details
        parameter_details = {
            'Well-Parameterized Functions': metrics.get('parameter_usage', {}).get('well_parameterized', 0),
            'Hard-Coded Values': metrics.get('parameter_usage', {}).get('hard_coded_values', []),
            'Default Parameters': metrics.get('parameter_usage', {}).get('default_params', 0),
            'Parameter Type Hints': f"{metrics.get('parameter_usage', {}).get('type_hint_coverage', 0)}%"
        }
        
        sections.append(self._format_metric(
            name="Parameter Usage",
            score=parameter_score,
            benchmark="good ≥ 90, moderate ≥ 75, poor < 75",
            definition="Evaluates effective use of function parameters",
            details=parameter_details,
            findings={
                'positive': metrics.get('parameter_usage', {}).get('good_practices', []),
                'negative': metrics.get('parameter_usage', {}).get('issues', [])
            }
        ))
        
        # Code Modularity for Reuse Details
        modularity_details = {
            'Modular Functions': metrics.get('code_modularity', {}).get('modular_functions', 0),
            'Function Dependencies': metrics.get('code_modularity', {}).get('dependencies', {}),
            'Shared Code Usage': metrics.get('code_modularity', {}).get('shared_code', []),
            'Refactoring Opportunities': metrics.get('code_modularity', {}).get('refactoring_ops', [])
        }
        
        sections.append(self._format_metric(
            name="Code Modularity for Reuse",
            score=modularity_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Assesses code organization for reusability",
            details=modularity_details,
            findings={
                'positive': metrics.get('code_modularity', {}).get('good_practices', []),
                'negative': metrics.get('code_modularity', {}).get('issues', [])
            }
        ))
        
        return '\n'.join(sections)
