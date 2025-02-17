from typing import Dict, Any
from ...base_formatter import BaseFormatter

class CodeStructureFormatter(BaseFormatter):
    def format_section(self, structure: Dict[str, Any]) -> str:
        """Format code structure section with detailed metrics."""
        sections = []
        metrics = structure.get('metrics', {})
        
        # Calculate individual scores
        modularity_score = self._get_metric_score(metrics, 'code_modularity')
        dependencies_score = self._get_metric_score(metrics, 'code_dependencies')
        complexity_score = self._get_metric_score(metrics, 'cyclomatic_complexity')
        
        # Component summary
        avg_score = (modularity_score + dependencies_score + complexity_score) / 3
        scores = {
            'Modularity': modularity_score,
            'Dependencies': dependencies_score,
            'Cyclomatic Complexity': complexity_score
        }
        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])
        
        sections.append(self._format_component_summary(
            name="CODE STRUCTURE",
            score=avg_score,
            strongest_metric=f"{strongest[0]} ({strongest[1]:.1f}/100)",
            weakest_metric=f"{weakest[0]} ({weakest[1]:.1f}/100)",
            key_findings={
                'highlight': structure.get('key_highlight', 'Good separation of concerns in functions'),
                'concern': structure.get('main_concern', 'Some functions have high cyclomatic complexity')
            }
        ))
        
        # Modularity Details
        modularity_details = {
            'Function Count': metrics.get('code_modularity', {}).get('function_count', 0),
            'Class Count': metrics.get('code_modularity', {}).get('class_count', 0),
            'Average Function Size': metrics.get('code_modularity', {}).get('avg_function_size', 0),
            'Code Organization': metrics.get('code_modularity', {}).get('organization_patterns', [])
        }
        
        sections.append(self._format_metric(
            name="Code Modularity",
            score=modularity_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Measures code organization into logical components",
            details=modularity_details,
            findings={
                'positive': metrics.get('code_modularity', {}).get('good_practices', []),
                'negative': metrics.get('code_modularity', {}).get('issues', [])
            }
        ))
        
        # Dependencies Details
        dependencies_details = {
            'Import Count': metrics.get('code_dependencies', {}).get('import_count', 0),
            'Circular Dependencies': metrics.get('code_dependencies', {}).get('circular_deps', []),
            'Unused Imports': metrics.get('code_dependencies', {}).get('unused_imports', []),
            'External Dependencies': metrics.get('code_dependencies', {}).get('external_deps', [])
        }
        
        sections.append(self._format_metric(
            name="Code Dependencies",
            score=dependencies_score,
            benchmark="good ≥ 90, moderate ≥ 75, poor < 75",
            definition="Evaluates management of code dependencies",
            details=dependencies_details,
            findings={
                'positive': metrics.get('code_dependencies', {}).get('good_practices', []),
                'negative': metrics.get('code_dependencies', {}).get('issues', [])
            }
        ))
        
        # Complexity Details
        complexity_details = {
            'Average Complexity': metrics.get('cyclomatic_complexity', {}).get('avg_complexity', 0),
            'Max Complexity': metrics.get('cyclomatic_complexity', {}).get('max_complexity', 0),
            'Complex Functions': metrics.get('cyclomatic_complexity', {}).get('complex_functions', []),
            'Complexity Distribution': metrics.get('cyclomatic_complexity', {}).get('complexity_dist', {})
        }
        
        sections.append(self._format_metric(
            name="Cyclomatic Complexity",
            score=complexity_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Measures code path complexity",
            details=complexity_details,
            findings={
                'positive': metrics.get('cyclomatic_complexity', {}).get('good_practices', []),
                'negative': metrics.get('cyclomatic_complexity', {}).get('issues', [])
            }
        ))
        
        return '\n'.join(sections)
