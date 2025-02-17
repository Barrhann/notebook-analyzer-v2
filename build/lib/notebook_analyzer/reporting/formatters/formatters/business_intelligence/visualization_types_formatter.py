from typing import Dict, Any
from ...base_formatter import BaseFormatter

class VisualizationTypesFormatter(BaseFormatter):
    def format_section(self, viz_types: Dict[str, Any]) -> str:
        """Format visualization types section with detailed metrics."""
        sections = []
        metrics = viz_types.get('metrics', {})
        
        # Calculate individual scores
        appropriateness_score = self._get_metric_score(metrics, 'type_appropriateness')
        diversity_score = self._get_metric_score(metrics, 'type_diversity')
        interactivity_score = self._get_metric_score(metrics, 'interactivity')
        
        # Component summary
        avg_score = (appropriateness_score + diversity_score + interactivity_score) / 3
        scores = {
            'Type Appropriateness': appropriateness_score,
            'Type Diversity': diversity_score,
            'Interactivity': interactivity_score
        }
        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])
        
        sections.append(self._format_component_summary(
            name="VISUALIZATION TYPES",
            score=avg_score,
            strongest_metric=f"{strongest[0]} ({strongest[1]:.1f}/100)",
            weakest_metric=f"{weakest[0]} ({weakest[1]:.1f}/100)",
            key_findings={
                'highlight': viz_types.get('key_highlight', 'Good variety of chart types for different data aspects'),
                'concern': viz_types.get('main_concern', 'Some complex data could benefit from interactive visualizations')
            }
        ))
        
        # Type Appropriateness Details
        appropriateness_details = {
            'Chart Types Used': metrics.get('type_appropriateness', {}).get('types_used', []),
            'Data-Type Matches': metrics.get('type_appropriateness', {}).get('matches', {}),
            'Mismatched Charts': metrics.get('type_appropriateness', {}).get('mismatches', []),
            'Suggested Alternatives': metrics.get('type_appropriateness', {}).get('suggestions', [])
        }
        
        sections.append(self._format_metric(
            name="Type Appropriateness",
            score=appropriateness_score,
            benchmark="good ≥ 90, moderate ≥ 75, poor < 75",
            definition="Evaluates if visualization types match the data and purpose",
            details=appropriateness_details,
            findings={
                'positive': metrics.get('type_appropriateness', {}).get('good_choices', []),
                'negative': metrics.get('type_appropriateness', {}).get('poor_choices', [])
            }
        ))
        
        # Type Diversity Details
        diversity_details = {
            'Unique Chart Types': metrics.get('type_diversity', {}).get('unique_types', 0),
            'Type Distribution': metrics.get('type_diversity', {}).get('distribution', {}),
            'Missing Types': metrics.get('type_diversity', {}).get('missing_types', []),
            'Advanced Types': metrics.get('type_diversity', {}).get('advanced_types', [])
        }
        
        sections.append(self._format_metric(
            name="Type Diversity",
            score=diversity_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Assesses the variety of visualization types used",
            details=diversity_details,
            findings={
                'positive': metrics.get('type_diversity', {}).get('good_practices', []),
                'negative': metrics.get('type_diversity', {}).get('improvement_areas', [])
            }
        ))
        
        # Interactivity Details
        interactivity_details = {
            'Interactive Features': metrics.get('interactivity', {}).get('features_used', []),
            'User Controls': metrics.get('interactivity', {}).get('controls', []),
            'Response Time': f"{metrics.get('interactivity', {}).get('response_time', 0)}ms",
            'Browser Compatibility': metrics.get('interactivity', {}).get('compatibility', {})
        }
        
        sections.append(self._format_metric(
            name="Interactivity",
            score=interactivity_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Measures the implementation of interactive visualization features",
            details=interactivity_details,
            findings={
                'positive': metrics.get('interactivity', {}).get('good_features', []),
                'negative': metrics.get('interactivity', {}).get('missing_features', [])
            }
        ))
        
        return '\n'.join(sections)
