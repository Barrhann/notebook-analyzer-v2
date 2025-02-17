"""
Analysis Orchestrator Module.

This module coordinates the analysis of Jupyter notebooks using various analyzers,
aggregating results and managing the analysis workflow.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:07:26
"""

from typing import Dict, List, Any, Optional, Type
from pathlib import Path
import concurrent.futures
from datetime import datetime

from ..analyzers import (
    BaseAnalyzer,
    builder_mindset,
    business_intelligence
)
from .notebook_reader import NotebookReader


class AnalysisOrchestrator:
    """
    Coordinates the analysis of Jupyter notebooks.

    This class:
    - Manages the analysis workflow
    - Coordinates multiple analyzers
    - Aggregates analysis results
    - Handles parallel execution
    """

    def __init__(self):
        """Initialize the analysis orchestrator."""
        self.reader = NotebookReader()
        self.analyzers = self._initialize_analyzers()
        self.results = {}
        self.errors = []

    def _initialize_analyzers(self) -> Dict[str, List[BaseAnalyzer]]:
        """
        Initialize all available analyzers.

        Returns:
            Dict[str, List[BaseAnalyzer]]: Dictionary of analyzer categories and instances
        """
        return {
            'builder_mindset': [
                analyzer()
                for analyzer in builder_mindset.get_all_analyzers()
            ],
            'business_intelligence': [
                analyzer()
                for analyzer in business_intelligence.get_all_analyzers()
            ]
        }

    def analyze_notebook(self, filepath: str, parallel: bool = True) -> Dict[str, Any]:
        """
        Analyze a Jupyter notebook using all available analyzers.

        Args:
            filepath (str): Path to the notebook file
            parallel (bool): Whether to run analyzers in parallel

        Returns:
            Dict[str, Any]: Analysis results from all analyzers

        Raises:
            ValueError: If notebook cannot be read or analyzed
        """
        try:
            # Read the notebook
            if not self.reader.read_notebook(filepath):
                raise ValueError(f"Failed to read notebook: {filepath}")

            # Get notebook content
            code_cells = list(self.reader.get_code_cells())
            markdown_cells = list(self.reader.get_markdown_cells())
            metadata = self.reader.get_notebook_metadata()

            # Run analysis
            if parallel:
                results = self._run_parallel_analysis(code_cells, markdown_cells)
            else:
                results = self._run_sequential_analysis(code_cells, markdown_cells)

            # Aggregate results
            return self._aggregate_results(results, metadata)

        except Exception as e:
            self.errors.append(str(e))
            raise ValueError(f"Analysis failed: {str(e)}")

    def _run_parallel_analysis(
        self, code_cells: List[Dict], markdown_cells: List[Dict]
    ) -> Dict[str, Any]:
        """
        Run analyzers in parallel.

        Args:
            code_cells (List[Dict]): List of code cells
            markdown_cells (List[Dict]): List of markdown cells

        Returns:
            Dict[str, Any]: Analysis results from all analyzers
        """
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {}
            
            # Submit analysis tasks
            for category, analyzers in self.analyzers.items():
                for analyzer in analyzers:
                    future = executor.submit(
                        self._run_single_analyzer,
                        analyzer,
                        code_cells,
                        markdown_cells
                    )
                    futures[future] = (category, analyzer.name)

            # Collect results
            for future in concurrent.futures.as_completed(futures):
                category, name = futures[future]
                try:
                    result = future.result()
                    if category not in results:
                        results[category] = {}
                    results[category][name] = result
                except Exception as e:
                    self.errors.append(f"Error in {category}/{name}: {str(e)}")

        return results

    def _run_sequential_analysis(
        self, code_cells: List[Dict], markdown_cells: List[Dict]
    ) -> Dict[str, Any]:
        """
        Run analyzers sequentially.

        Args:
            code_cells (List[Dict]): List of code cells
            markdown_cells (List[Dict]): List of markdown cells

        Returns:
            Dict[str, Any]: Analysis results from all analyzers
        """
        results = {}
        
        for category, analyzers in self.analyzers.items():
            results[category] = {}
            for analyzer in analyzers:
                try:
                    results[category][analyzer.name] = self._run_single_analyzer(
                        analyzer,
                        code_cells,
                        markdown_cells
                    )
                except Exception as e:
                    self.errors.append(f"Error in {category}/{analyzer.name}: {str(e)}")

        return results

    def _run_single_analyzer(
        self,
        analyzer: BaseAnalyzer,
        code_cells: List[Dict],
        markdown_cells: List[Dict]
    ) -> Dict[str, Any]:
        """
        Run a single analyzer on notebook content.

        Args:
            analyzer (BaseAnalyzer): Analyzer instance
            code_cells (List[Dict]): List of code cells
            markdown_cells (List[Dict]): List of markdown cells

        Returns:
            Dict[str, Any]: Analysis results from the analyzer
        """
        # Extract code from cells
        code = '\n\n'.join(cell['source'] for cell in code_cells)
        
        # Run analysis
        return analyzer.analyze(code)

    def _aggregate_results(
        self,
        results: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aggregate results from all analyzers.

        Args:
            results (Dict[str, Any]): Raw analysis results
            metadata (Dict[str, Any]): Notebook metadata

        Returns:
            Dict[str, Any]: Aggregated analysis results
        """
        return {
            'metadata': metadata,
            'analysis_timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'results': results,
            'summary': {
                'total_analyzers': sum(
                    len(analyzers) for analyzers in self.analyzers.values()
                ),
                'categories': list(results.keys()),
                'errors': self.errors,
                'overall_score': self._calculate_overall_score(results)
            }
        }

    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate overall analysis score.

        Args:
            results (Dict[str, Any]): Analysis results

        Returns:
            float: Overall score (0-100)
        """
        scores = []
        weights = {
            'builder_mindset': 0.6,
            'business_intelligence': 0.4
        }

        for category, category_results in results.items():
            category_scores = [
                result.get('score', 0)
                for result in category_results.values()
            ]
            if category_scores:
                avg_score = sum(category_scores) / len(category_scores)
                scores.append(avg_score * weights.get(category, 1.0))

        return round(sum(scores) / sum(weights.values()), 2) if scores else 0.0

    def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the last analysis run.

        Returns:
            Dict[str, Any]: Analysis summary
        """
        if not self.results:
            return {
                'status': 'No analysis performed',
                'errors': self.errors
            }

        return {
            'status': 'completed',
            'timestamp': self.results.get('analysis_timestamp'),
            'notebook': self.results.get('metadata', {}).get('filename'),
            'categories_analyzed': list(self.results.get('results', {}).keys()),
            'overall_score': self.results.get('summary', {}).get('overall_score'),
            'errors': self.errors
        }

    def __str__(self) -> str:
        """Return string representation of the orchestrator."""
        return (f"AnalysisOrchestrator("
                f"analyzers={sum(len(a) for a in self.analyzers.values())})")

    def __repr__(self) -> str:
        """Return detailed string representation of the orchestrator."""
        return (f"AnalysisOrchestrator("
                f"categories={list(self.analyzers.keys())}, "
                f"total_analyzers={sum(len(a) for a in self.analyzers.values())}, "
                f"errors={len(self.errors)})")
