from typing import Dict, Any, List

def calculate_block_score(block_data: Dict[str, Any]) -> float:
    """Calculate normalized score for a block."""
    metrics = block_data.get('metrics', {})
    scores = []
    
    for metric in metrics.values():
        if isinstance(metric, dict):
            if 'score' in metric:
                scores.append(metric['score'])
            elif 'consistency_score' in metric:
                scores.append(metric['consistency_score'])
            elif 'complexity_score' in metric:
                scores.append(metric['complexity_score'])
            elif 'parameter_score' in metric:
                scores.append(metric['parameter_score'])
    
    return sum(scores) / len(scores) if scores else 0

def get_assessment_level(score: float) -> str:
    """Get assessment level based on score."""
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
