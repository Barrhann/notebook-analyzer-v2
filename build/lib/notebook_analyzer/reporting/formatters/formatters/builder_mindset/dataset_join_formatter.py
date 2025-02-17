from typing import Dict, Any
from ...base_formatter import BaseFormatter

class DatasetJoinFormatter(BaseFormatter):
    def format_section(self, joins: Dict[str, Any]) -> str:
        """Format dataset join section with detailed metrics."""
        sections = []
        metrics = joins.get('metrics', {})
        
        # Calculate individual scores
        efficiency_score = self._get_metric_score(metrics, 'join_efficiency')
        key_handling_score = self._get_metric_score(metrics, 'key_handling')
        validation_score = self._get_metric_score(metrics, 'data_validation')
        
        # Component summary
        avg_score = (efficiency_score + key_handling_score + validation_score) / 3
        scores = {
            'Join Efficiency': efficiency_score,
            'Key Handling': key_handling_score,
            'Data Validation': validation_score
        }
        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])
        
        sections.append(self._format_component_summary(
            name="DATASET JOINS",
            score=avg_score,
            strongest_metric=f"{strongest[0]} ({strongest[1]:.1f}/100)",
            weakest_metric=f"{weakest[0]} ({weakest[1]:.1f}/100)",
            key_findings={
                'highlight': joins.get('key_highlight', 'Efficient join operations with proper key validation'),
                'concern': joins.get('main_concern', 'Some joins lack proper null handling')
            }
        ))
        
        # Join Efficiency Details
        efficiency_details = {
            'Join Operations': metrics.get('join_efficiency', {}).get('join_count', 0),
            'Average Join Time': metrics.get('join_efficiency', {}).get('avg_join_time', 0),
            'Memory Usage': metrics.get('join_efficiency', {}).get('memory_usage', "N/A"),
            'Join Types Used': metrics.get('join_efficiency', {}).get('join_types', [])
        }
        
        sections.append(self._format_metric(
            name="Join Efficiency",
            score=efficiency_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Evaluates the efficiency of dataset join operations",
            details=efficiency_details,
            findings={
                'positive': metrics.get('join_efficiency', {}).get('optimized_joins', []),
                'negative': metrics.get('join_efficiency', {}).get('inefficient_joins', [])
            }
        ))
        
        # Key Handling Details
        key_handling_details = {
            'Key Validation': metrics.get('key_handling', {}).get('validation_checks', []),
            'Duplicate Keys': metrics.get('key_handling', {}).get('duplicate_keys', 0),
            'Missing Keys': metrics.get('key_handling', {}).get('missing_keys', 0),
            'Key Type Issues': metrics.get('key_handling', {}).get('type_issues', [])
        }
        
        sections.append(self._format_metric(
            name="Key Handling",
            score=key_handling_score,
            benchmark="good ≥ 90, moderate ≥ 75, poor < 75",
            definition="Assesses the handling of join keys and related validations",
            details=key_handling_details,
            findings={
                'positive': metrics.get('key_handling', {}).get('good_practices', []),
                'negative': metrics.get('key_handling', {}).get('issues', [])
            }
        ))
        
        # Data Validation Details
        validation_details = {
            'Pre-join Validations': metrics.get('data_validation', {}).get('pre_join_checks', []),
            'Post-join Validations': metrics.get('data_validation', {}).get('post_join_checks', []),
            'Data Quality Issues': metrics.get('data_validation', {}).get('quality_issues', []),
            'Validation Coverage': f"{metrics.get('data_validation', {}).get('validation_coverage', 0)}%"
        }
        
        sections.append(self._format_metric(
            name="Data Validation",
            score=validation_score,
            benchmark="good ≥ 85, moderate ≥ 70, poor < 70",
            definition="Measures the completeness of data validation in join operations",
            details=validation_details,
            findings={
                'positive': metrics.get('data_validation', {}).get('good_practices', []),
                'negative': metrics.get('data_validation', {}).get('issues', [])
            }
        ))
        
        return '\n'.join(sections)
