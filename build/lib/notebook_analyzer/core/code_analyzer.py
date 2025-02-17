"""Main code analyzer that orchestrates all individual analyzers."""
from typing import Dict, Any
from datetime import datetime
from .analyzers.builder_mindset import (
    CodeFormattingAnalyzer,
    CodeCommentsAnalyzer,
    CodeConcisenessAnalyzer,
    CodeStructureAnalyzer,
    DatasetJoinAnalyzer,
    CodeReusabilityAnalyzer,
    AdvancedTechniquesAnalyzer
)
from .analyzers.business_intelligence import (
    VisualizationFormattingAnalyzer,
    VisualizationTypesAnalyzer
)

class CodeAnalyzer:
    """Main analyzer class that orchestrates all analysis components."""
    
    def __init__(self):
        self.analyzers = {
            # Builder Mindset analyzers
            'formatting': CodeFormattingAnalyzer(),
            'comments': CodeCommentsAnalyzer(),
            'conciseness': CodeConcisenessAnalyzer(),
            'structure': CodeStructureAnalyzer(),
            'dataset_join': DatasetJoinAnalyzer(),
            'reusability': CodeReusabilityAnalyzer(),
            'advanced_techniques': AdvancedTechniquesAnalyzer(),
            
            # Business Intelligence analyzers
            'visualization_formatting': VisualizationFormattingAnalyzer(),
            'visualization_types': VisualizationTypesAnalyzer()
        }
        self.analysis_time = datetime.utcnow()

    def analyze_code(self, code: str, cell_number: int = 0) -> Dict[str, Any]:
        """
        Analyze Python code from notebook cells.
        
        Args:
            code: String containing Python code from notebook cell
            cell_number: Current cell number for execution order analysis
            
        Returns:
            Dict containing analysis results from all analyzers
        """
        try:
            results = {
                'metadata': {
                    'analysis_time': self.analysis_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'cell_number': cell_number
                },
                'analysis': {}
            }
            
            # Run all analyzers
            for key, analyzer in self.analyzers.items():
                results['analysis'][key] = analyzer.analyze(
                    code,
                    cell_number=cell_number
                )
                
            # Calculate overall scores
            results['summary'] = self._calculate_overall_scores(results['analysis'])
            
            return results
            
        except SyntaxError:
            return self._get_default_results()

    def _calculate_overall_scores(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall scores from individual analyzer results."""
        builder_mindset_scores = []
        bi_scores = []
        
        # Builder Mindset scores
        if 'formatting' in analysis_results:
            builder_mindset_scores.extend([
                analysis_results['formatting'].get('style', {}).get('score', 0),
                analysis_results['formatting'].get('complexity', {}).get('score', 0)
            ])
            
        for key in ['comments', 'conciseness', 'structure', 'dataset_join',
                   'reusability', 'advanced_techniques']:
            if key in analysis_results:
                metrics = analysis_results[key].get('metrics', {})
                for metric in metrics.values():
                    if isinstance(metric, dict) and 'score' in metric:
                        builder_mindset_scores.append(metric['score'])
        
        # Business Intelligence scores
        for key in ['visualization_formatting', 'visualization_types']:
            if key in analysis_results:
                metrics = analysis_results[key].get('metrics', {})
                for metric in metrics.values():
                    if isinstance(metric, dict) and 'score' in metric:
                        bi_scores.append(metric['score'])
        
        # Calculate averages
        builder_mindset_score = (
            sum(builder_mindset_scores) / len(builder_mindset_scores)
            if builder_mindset_scores else 0
        )
        
        bi_score = (
            sum(bi_scores) / len(bi_scores)
            if bi_scores else 0
        )
        
        return {
            'builder_mindset_score': round(builder_mindset_score, 2),
            'bi_score': round(bi_score, 2),
            'overall_score': round((builder_mindset_score + bi_score) / 2, 2)
        }

    def _get_default_results(self) -> Dict[str, Any]:
        """Return default results when analysis fails."""
        return {
            'metadata': {
                'analysis_time': self.analysis_time.strftime('%Y-%m-%d %H:%M:%S'),
                'cell_number': 0,
                'status': 'error',
                'error_type': 'SyntaxError'
            },
            'analysis': {
                analyzer_name: analyzer.analyze("", cell_number=0)
                for analyzer_name, analyzer in self.analyzers.items()
            },
            'summary': {
                'builder_mindset_score': 0,
                'bi_score': 0,
                'overall_score': 0
            }
        }
