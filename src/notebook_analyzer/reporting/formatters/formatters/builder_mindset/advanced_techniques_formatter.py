from typing import Dict, Any
from ...base_formatter import BaseFormatter

class AdvancedTechniquesFormatter(BaseFormatter):
    def format_section(self, advanced: Dict[str, Any]) -> str:
        """Format advanced techniques section with detailed metrics."""
        sections = []
        metrics = advanced.get('metrics', {})
        
        # Calculate individual scores
        library_usage_score = self._get_metric_score(metrics, 'library_usage')
        optimization_score = self._get_metric_score(metrics, 'code_optimization')
        patterns_score = self._get_metric_score(metrics, 'design_patterns')
        
        # Component summary
        avg_score = (library_usage_score + optimization_score + patterns_score) / 3
        scores = {
            'Library Usage': library_usage_score,
            'Code Optimization': optimization_score,
            'Design Patterns': patterns_score
        }
        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])
        
        sections.append(self._format_component_summary(
            name="ADVANCED TECHNIQUES",
            score=avg_score,
            strongest_metric=f"{strongest[0]} ({strongest[1]:.1f}/100)",
            weakest_metric=f"{weakest[0]} ({weakest[1]:.1f}/100)",
            key_findings={
                'highlight': advanced.get('key_highlight', 'Effective use of pandas optimizations'),
                'concern': advanced.get('main_concern', 'Some operations could be vectorized')
            }
        ))
        
        # Library Usage Details
        library_details = {
            'Libraries Used': metrics.get('library_usage', {}).get('libraries', []),
            'Advanced Features': metrics.get('library_usage', {}).get('advanced_features', []),
            'Optimization Methods': metrics.get('library_usage', {}).get('optimizations', []),
            'Version Compatibility': metrics.get('library_usage', {}).get('compatibility', {})
        }
        
        sections.append(self._format_metric(
            name="Library Usage",
            score=library_usage_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Evaluates effective use of library features",
            details=library_details,
            findings={
                'positive': metrics.get('library_usage', {}).get('good_practices', []),
                'negative': metrics.get('library_usage', {}).get('improvement_areas', [])
            }
        ))
        
        # Code Optimization Details
        optimization_details = {
            'Vectorized Operations': metrics.get('code_optimization', {}).get('vectorized_ops', 0),
            'Performance Bottlenecks': metrics.get('code_optimization', {}).get('bottlenecks', []),
            'Memory Optimizations': metrics.get('code_optimization', {}).get('memory_opts', []),
            'Execution Time': metrics.get('code_optimization', {}).get('execution_time', {})
        }
        
        sections.append(self._format_metric(
            name="Code Optimization",
            score=optimization_score,
            benchmark="good ≥ 90, moderate ≥ 75, poor < 75",
            definition="Measures implementation of performance optimizations",
            details=optimization_details,
            findings={
                'positive': metrics.get('code_optimization', {}).get('optimized_sections', []),
                'negative': metrics.get('code_optimization', {}).get('optimization_opportunities', [])
            }
        ))
        
        # Design Patterns Details
        patterns_details = {
            'Patterns Used': metrics.get('design_patterns', {}).get('patterns_used', []),
            'Pattern Quality': metrics.get('design_patterns', {}).get('pattern_quality', {}),
            'Anti-patterns': metrics.get('design_patterns', {}).get('anti_patterns', []),
            'Pattern Opportunities': metrics.get('design_patterns', {}).get('opportunities', [])
        }
        
        sections.append(self._format_metric(
            name="Design Patterns",
            score=patterns_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Assesses use of software design patterns",
            details=patterns_details,
            findings={
                'positive': metrics.get('design_patterns', {}).get('good_implementations', []),
                'negative': metrics.get('design_patterns', {}).get('improvement_needed', [])
            }
        ))
        
        return '\n'.join(sections)
