"""Main analyzer class for processing notebooks."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from .core.notebook_reader import NotebookReader
from .core.analyzers.builder_mindset import (
    CodeStructureAnalyzer,
    DatasetJoinAnalyzer,
    AdvancedTechniquesAnalyzer,
    CodeReusabilityAnalyzer
)
from .core.analyzers.business_intelligence import (
    VisualizationFormattingAnalyzer,
    VisualizationTypesAnalyzer
)
from .config import AnalyzerConfig

class NotebookAnalyzer:
    """Main class for analyzing Jupyter notebooks."""
    
    def __init__(self, config: Optional[AnalyzerConfig] = None):
        """
        Initialize the notebook analyzer.
        
        Args:
            config: Optional configuration object for customizing analysis
        """
        self.config = config or AnalyzerConfig()
        self.notebook_reader = NotebookReader()
        
        # Initialize analyzers
        self.analyzers = {
            'builder_mindset': {
                'code_structure': CodeStructureAnalyzer(),
                'dataset_join': DatasetJoinAnalyzer(),
                'advanced_techniques': AdvancedTechniquesAnalyzer(),
                'code_reusability': CodeReusabilityAnalyzer()
            },
            'business_intelligence': {
                'visualization_formatting': VisualizationFormattingAnalyzer(),
                'visualization_types': VisualizationTypesAnalyzer()
            }
        }

    def analyze_notebook(self, path: str) -> Dict[str, Any]:
        """
        Analyze a Jupyter notebook.
        
        Args:
            path: Path to the notebook file
            
        Returns:
            Dict containing analysis results
            
        Raises:
            FileNotFoundError: If notebook file doesn't exist
            ValueError: If notebook format is invalid
        """
        # Read notebook
        notebook = self.notebook_reader.read(path)
        code_cells = self.notebook_reader.get_code_cells(notebook)
        
        # Analyze each cell
        cell_results = []
        for cell in code_cells:
            result = self._analyze_cell(cell)
            if result:  # Skip empty results
                cell_results.append(result)
        
        # Aggregate results
        return self._aggregate_results(cell_results, Path(path).name)

    def _analyze_cell(self, cell: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a single code cell."""
        code = self.notebook_reader.preprocess_code(cell['source'])
        if not code.strip():  # Skip empty cells
            return None
            
        cell_analysis = {
            'cell_number': cell['cell_number'],
            'metrics': {
                'builder_mindset': self._analyze_builder_mindset(code),
                'business_intelligence': self._analyze_business_intelligence(code)
            }
        }
        
        # Calculate cell scores
        builder_score = self._calculate_builder_score(cell_analysis['metrics']['builder_mindset'])
        bi_score = self._calculate_bi_score(cell_analysis['metrics']['business_intelligence'])
        
        cell_analysis['summary'] = {
            'builder_mindset_score': builder_score,
            'bi_score': bi_score,
            'overall_score': (builder_score + bi_score) / 2
        }
        
        return cell_analysis

    def _analyze_builder_mindset(self, code: str) -> Dict[str, Any]:
        """Analyze code for builder mindset metrics."""
        return {
            name: analyzer.analyze(code)
            for name, analyzer in self.analyzers['builder_mindset'].items()
        }

    def _analyze_business_intelligence(self, code: str) -> Dict[str, Any]:
        """Analyze code for business intelligence metrics."""
        return {
            name: analyzer.analyze(code)
            for name, analyzer in self.analyzers['business_intelligence'].items()
        }

    def _calculate_builder_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate builder mindset score from metrics."""
        weights = self.config.builder_weights
        scores = []
        
        for name, weight in weights.items():
            if name in metrics and 'metrics' in metrics[name]:
                metric_scores = [
                    m.get('score', 0)
                    for m in metrics[name]['metrics'].values()
                ]
                if metric_scores:
                    scores.append(sum(metric_scores) / len(metric_scores) * weight)
        
        return round(sum(scores), 2) if scores else 0

    def _calculate_bi_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate business intelligence score from metrics."""
        weights = self.config.bi_weights
        scores = []
        
        for name, weight in weights.items():
            if name in metrics and 'metrics' in metrics[name]:
                metric_scores = [
                    m.get('score', 0)
                    for m in metrics[name]['metrics'].values()
                ]
                if metric_scores:
                    scores.append(sum(metric_scores) / len(metric_scores) * weight)
        
        return round(sum(scores), 2) if scores else 0

    def _aggregate_results(
        self,
        cell_results: List[Dict[str, Any]],
        notebook_name: str
    ) -> Dict[str, Any]:
        """Aggregate results from individual cell analyses."""
        if not cell_results:
            return {
                'metadata': {
                    'notebook_name': notebook_name,
                    'analysis_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_cells': 0
                },
                'cell_results': [],
                'summary': {
                    'builder_mindset_score': 0,
                    'bi_score': 0,
                    'overall_score': 0
                }
            }
        
        # Calculate average scores
        builder_scores = [r['summary']['builder_mindset_score'] for r in cell_results]
        bi_scores = [r['summary']['bi_score'] for r in cell_results]
        
        avg_builder = sum(builder_scores) / len(builder_scores)
        avg_bi = sum(bi_scores) / len(bi_scores)
        
        return {
            'metadata': {
                'notebook_name': notebook_name,
                'analysis_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                'total_cells': len(cell_results)
            },
            'cell_results': cell_results,
            'summary': {
                'builder_mindset_score': round(avg_builder, 2),
                'bi_score': round(avg_bi, 2),
                'overall_score': round((avg_builder + avg_bi) / 2, 2)
            }
        }
