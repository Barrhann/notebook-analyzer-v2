from typing import Dict, Any
from ...base_formatter import BaseFormatter

class VisualizationFormattingFormatter(BaseFormatter):
    def format_section(self, formatting: Dict[str, Any]) -> str:
        """Format visualization formatting section with detailed metrics."""
        sections = []
        metrics = formatting.get('metrics', {})
        
        # Calculate individual scores
        clarity_score = self._get_metric_score(metrics, 'visual_clarity')
        labeling_score = self._get_metric_score(metrics, 'labeling_quality')
        consistency_score = self._get_metric_score(metrics, 'style_consistency')
        
        # Component summary
        avg_score = (clarity_score + labeling_score + consistency_score) / 3
        scores = {
            'Visual Clarity': clarity_score,
            'Labeling Quality': labeling_score,
            'Style Consistency': consistency_score
        }
        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])
        
        sections.append(self._format_component_summary(
            name="VISUALIZATION FORMATTING",
            score=avg_score,
            strongest_metric=f"{strongest[0]} ({strongest[1]:.1f}/100)",
            weakest_metric=f"{weakest[0]} ({weakest[1]:.1f}/100)",
            key_findings={
                'highlight': formatting.get('key_highlight', 'Clear and consistent axis labeling'),
                'concern': formatting.get('main_concern', 'Some plots lack proper titles or legends')
            }
        ))
        
        # Visual Clarity Details
        clarity_details = {
            'Figure Size': metrics.get('visual_clarity', {}).get('figure_sizes', []),
            'Color Schemes': metrics.get('visual_clarity', {}).get('color_schemes', []),
            'Data-Ink Ratio': f"{metrics.get('visual_clarity', {}).get('data_ink_ratio', 0):.2f}",
            'Readability Issues': metrics.get('visual_clarity', {}).get('readability_issues', [])
        }
        
        sections.append(self._format_metric(
            name="Visual Clarity",
            score=clarity_score,
            benchmark="good ≥ 90, moderate ≥ 75, poor < 75",
            definition="Assesses the clarity and readability of visualizations",
            details=clarity_details,
            findings={
                'positive': metrics.get('visual_clarity', {}).get('good_practices', []),
                'negative': metrics.get('visual_clarity', {}).get('clarity_issues', [])
            }
        ))
        
        # Labeling Quality Details
        labeling_details = {
            'Title Coverage': f"{metrics.get('labeling_quality', {}).get('title_coverage', 0)}%",
            'Axis Labels': f"{metrics.get('labeling_quality', {}).get('axis_label_coverage', 0)}%",
            'Legend Usage': f"{metrics.get('labeling_quality', {}).get('legend_usage', 0)}%",
            'Label Clarity': metrics.get('labeling_quality', {}).get('unclear_labels', [])
        }
        
        sections.append(self._format_metric(
            name="Labeling Quality",
            score=labeling_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Evaluates completeness and clarity of visualization labels",
            details=labeling_details,
            findings={
                'positive': metrics.get('labeling_quality', {}).get('good_practices', []),
                'negative': metrics.get('labeling_quality', {}).get('missing_labels', [])
            }
        ))
        
        # Style Consistency Details
        consistency_details = {
            'Style Elements': metrics.get('style_consistency', {}).get('style_elements', []),
            'Theme Usage': metrics.get('style_consistency', {}).get('theme_usage', {}),
            'Format Consistency': f"{metrics.get('style_consistency', {}).get('consistency_score', 0)}%",
            'Style Variations': metrics.get('style_consistency', {}).get('variations', [])
        }
        
        sections.append(self._format_metric(
            name="Style Consistency",
            score=consistency_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Measures consistency in visualization styling",
            details=consistency_details,
            findings={
                'positive': metrics.get('style_consistency', {}).get('consistent_elements', []),
                'negative': metrics.get('style_consistency', {}).get('inconsistencies', [])
            }
        ))
        
        return '\n'.join(sections)
