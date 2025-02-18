"""
Visualization Types Analyzer Module.

This module analyzes visualization practices in Jupyter notebooks.
It evaluates plot types, chart appropriateness, and visualization best practices.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 23:56:57
"""

import ast
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict
from ..base_analyzer import BaseAnalyzer, AnalysisError


class VisualizationFeatures:
    """Constants for visualization analysis."""
    
    # Common plotting libraries
    PLOTTING_LIBRARIES = {
        'matplotlib': {'pyplot', 'plt'},
        'seaborn': {'sns'},
        'plotly': {'express', 'graph_objects', 'px', 'go'},
        'bokeh': {'figure', 'show'},
        'altair': {'alt'}
    }
    
    # Plot types and their appropriate use cases
    PLOT_TYPES = {
        'scatter': {'scatter', 'scatterplot', 'scatter_plot'},
        'line': {'plot', 'lineplot', 'line_plot'},
        'bar': {'bar', 'barplot', 'bar_plot'},
        'histogram': {'hist', 'histogram'},
        'box': {'box', 'boxplot', 'box_plot'},
        'heatmap': {'heatmap', 'imshow'},
        'pie': {'pie', 'pieplot', 'pie_plot'},
        'violin': {'violin', 'violinplot', 'violin_plot'},
        'kde': {'kdeplot', 'kde_plot'},
        'area': {'area', 'areaplot', 'area_plot'}
    }
    
    # Data type appropriateness for plot types
    APPROPRIATE_PLOTS = {
        'categorical': {'bar', 'box', 'violin', 'pie'},
        'numerical': {'histogram', 'kde', 'box', 'violin'},
        'temporal': {'line', 'area'},
        'correlation': {'scatter', 'heatmap'}
    }
    
    # Pattern weights for scoring
    PATTERN_WEIGHTS = {
        'library_usage': 0.2,
        'plot_variety': 0.3,
        'plot_appropriateness': 0.3,
        'customization': 0.2
    }


class VisualizationVisitor(ast.NodeVisitor):
    """Visitor for analyzing visualization code."""

    def __init__(self):
        """Initialize the visualization visitor."""
        self.libraries = defaultdict(list)
        self.plots = defaultdict(list)
        self.customizations = []
        self.issues = []
        self.suggestions = []
        self.imports = set()

    def visit_Import(self, node: ast.Import):
        """
        Visit import nodes.

        Args:
            node (ast.Import): The import node
        """
        for name in node.names:
            for lib, aliases in VisualizationFeatures.PLOTTING_LIBRARIES.items():
                if name.name in aliases or name.name == lib:
                    self.imports.add(lib)
                    self.libraries[lib].append({
                        'alias': name.asname or name.name,
                        'line': node.lineno
                    })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """
        Visit import from nodes.

        Args:
            node (ast.ImportFrom): The import from node
        """
        if node.module in VisualizationFeatures.PLOTTING_LIBRARIES:
            self.imports.add(node.module)
            for name in node.names:
                self.libraries[node.module].append({
                    'alias': name.asname or name.name,
                    'line': node.lineno
                })
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """
        Visit call nodes.

        Args:
            node (ast.Call): The call node
        """
        if isinstance(node.func, ast.Attribute):
            # Check for plotting method calls
            method_name = node.func.attr
            base_obj = self._get_base_object(node.func.value)
            
            # Analyze plot type
            self._analyze_plot_type(method_name, base_obj, node)
            
            # Analyze customizations
            self._analyze_customizations(node)
            
        self.generic_visit(node)

    def _get_base_object(self, node: ast.AST) -> str:
        """
        Get the base object name from an AST node.

        Args:
            node (ast.AST): The AST node

        Returns:
            str: Base object name
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_base_object(node.value)
        return ""

    def _analyze_plot_type(self, method_name: str, base_obj: str, node: ast.Call):
        """
        Analyze plot type and its appropriateness.

        Args:
            method_name (str): The plotting method name
            base_obj (str): The base object name
            node (ast.Call): The call node
        """
        for plot_type, names in VisualizationFeatures.PLOT_TYPES.items():
            if method_name in names or any(name in method_name for name in names):
                self.plots[plot_type].append({
                    'method': method_name,
                    'base': base_obj,
                    'line': node.lineno,
                    'args': len(node.args),
                    'kwargs': {k.arg: self._extract_value(k.value) for k in node.keywords}
                })
                
                # Check plot appropriateness
                self._check_plot_appropriateness(plot_type, node)

    def _analyze_customizations(self, node: ast.Call):
        """
        Analyze plot customizations.

        Args:
            node (ast.Call): The call node
        """
        customization_methods = {
            'set_title', 'set_xlabel', 'set_ylabel',
            'set_figsize', 'grid', 'legend'
        }
        
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in customization_methods:
                self.customizations.append({
                    'type': node.func.attr,
                    'line': node.lineno
                })

    def _check_plot_appropriateness(self, plot_type: str, node: ast.Call):
        """
        Check if plot type is appropriate for the data.

        Args:
            plot_type (str): The type of plot
            node (ast.Call): The call node
        """
        # Check for common misuses
        if plot_type == 'pie' and len(node.args) > 0:
            self.suggestions.append(
                f"Line {node.lineno}: Pie charts are best used for parts of a whole"
            )
            
        if plot_type == 'scatter' and not any(
            k.arg in {'x', 'y'} for k in node.keywords
        ):
            self.suggestions.append(
                f"Line {node.lineno}: Scatter plots should specify x and y variables"
            )

    def _extract_value(self, node: ast.AST) -> Any:
        """
        Extract value from an AST node.

        Args:
            node (ast.AST): The AST node

        Returns:
            Any: Extracted value
        """
        if isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.List):
            return [self._extract_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Name):
            return node.id
        return None


class VisualizationTypesAnalyzer(BaseAnalyzer):
    """
    Analyzer for visualization types and practices.
    
    This analyzer evaluates:
    - Plotting library usage
    - Plot type variety
    - Plot appropriateness
    - Visualization customization
    """

    def __init__(self):
        """Initialize the visualization types analyzer."""
        super().__init__(name="Visualization Types")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'libraries': defaultdict(list),
            'plots': defaultdict(list),
            'customizations': [],
            'issues': [],
            'suggestions': []
        }

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'business_intelligence'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze visualization types and practices.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing:
                - score: Overall visualization score (0-100)
                - findings: List of specific findings
                - details: Detailed metrics and issues found
                - suggestions: Improvement suggestions

        Raises:
            AnalysisError: If analysis fails
            ValueError: If code is invalid
        """
        try:
            self.prepare_analysis(code)
            self._reset_metrics()

            # Parse the code
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                raise AnalysisError(f"Syntax error in code: {str(e)}")

            # Analyze visualization code
            visitor = VisualizationVisitor()
            visitor.visit(tree)

            # Calculate component scores
            library_score = self._calculate_library_score(visitor.libraries)
            variety_score = self._calculate_variety_score(visitor.plots)
            appropriateness_score = self._calculate_appropriateness_score(visitor)
            customization_score = self._calculate_customization_score(visitor.customizations)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (library_score, VisualizationFeatures.PATTERN_WEIGHTS['library_usage']),
                (variety_score, VisualizationFeatures.PATTERN_WEIGHTS['plot_variety']),
                (appropriateness_score, VisualizationFeatures.PATTERN_WEIGHTS['plot_appropriateness']),
                (customization_score, VisualizationFeatures.PATTERN_WEIGHTS['customization'])
            ])

            # Store metrics
            self.metrics['libraries'] = dict(visitor.libraries)
            self.metrics['plots'] = dict(visitor.plots)
            self.metrics['customizations'] = visitor.customizations
            self.metrics['issues'] = visitor.issues
            self.metrics['suggestions'] = visitor.suggestions

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(visitor),
                'details': {
                    'library_score': library_score,
                    'variety_score': variety_score,
                    'appropriateness_score': appropriateness_score,
                    'customization_score': customization_score,
                    'metrics': self.metrics
                },
                'suggestions': self._generate_suggestions(visitor)
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing visualization types: {str(e)}")

    def _calculate_library_score(self, libraries: Dict[str, List[Dict[str, Any]]]) -> float:
        """
        Calculate score based on library usage.

        Args:
            libraries (Dict[str, List[Dict[str, Any]]]): Dictionary of library usages

        Returns:
            float: Library usage score (0-100)
        """
        if not libraries:
            return 0.0  # No visualization libraries used
            
        # Score based on library variety and consistent usage
        score = min(100, len(libraries) * 25)
        return score

    def _calculate_variety_score(self, plots: Dict[str, List[Dict[str, Any]]]) -> float:
        """
        Calculate score based on plot variety.

        Args:
            plots (Dict[str, List[Dict[str, Any]]]): Dictionary of plot usages

        Returns:
            float: Plot variety score (0-100)
        """
        if not plots:
            return 0.0  # No plots used
            
        # Score based on plot type variety
        score = min(100, len(plots) * 20)
        return score

    def _calculate_appropriateness_score(self, visitor: VisualizationVisitor) -> float:
        """
        Calculate score based on plot appropriateness.

        Args:
            visitor (VisualizationVisitor): The visitor containing analysis data

        Returns:
            float: Plot appropriateness score (0-100)
        """
        if not visitor.plots:
            return 0.0  # No plots to analyze
            
        # Start with perfect score and deduct for issues
        score = 100.0 - (len(visitor.suggestions) * 10)
        return max(0, score)

    def _calculate_customization_score(self, customizations: List[Dict[str, Any]]) -> float:
        """
        Calculate score based on visualization customizations.

        Args:
            customizations (List[Dict[str, Any]]): List of customization usages

        Returns:
            float: Customization score (0-100)
        """
        if not customizations:
            return 50.0  # Basic score for no customizations
            
        # Score based on customization variety
        unique_customs = len({c['type'] for c in customizations})
        return min(100, 50 + (unique_customs * 10))

    def _calculate_overall_score(self, scores_and_weights: List[tuple[float, float]]) -> float:
        """
        Calculate weighted average score.

        Args:
            scores_and_weights: List of (score, weight) tuples

        Returns:
            float: Weighted average score (0-100)
        """
        total_score = 0.0
        total_weight = 0.0
        
        for score, weight in scores_and_weights:
            total_score += score * weight
            total_weight += weight
            
        return round(total_score / total_weight if total_weight > 0 else 0, 2)

    def _generate_findings(self, visitor: VisualizationVisitor) -> List[str]:
        """
        Generate list of findings from the analysis.

        Args:
            visitor (VisualizationVisitor): The visitor containing analysis data

        Returns:
            List[str]: List of findings
        """
        findings = []
        
        if visitor.libraries:
            findings.append(
                f"Found {len(visitor.libraries)} visualization libraries in use"
            )
            
        if visitor.plots:
            findings.append(
                f"Detected {len(visitor.plots)} different plot types"
            )
            
        if visitor.customizations:
            findings.append(
                f"Found {len(visitor.customizations)} plot customizations"
            )
            
        return findings

    def _generate_suggestions(self, visitor: VisualizationVisitor) -> List[str]:
        """
        Generate improvement suggestions.

        Args:
            visitor (VisualizationVisitor): The visitor containing analysis data

        Returns:
            List[str]: List of improvement suggestions
        """
        suggestions = visitor.suggestions.copy()

        if not visitor.libraries:
            suggestions.append(
                "Consider using visualization libraries for data presentation"
            )

        if len(visitor.plots) < 2:
            suggestions.append(
                "Consider using a variety of plot types for different aspects of the data"
            )

        if not visitor.customizations:
            suggestions.append(
                "Add plot customizations like titles, labels, and legends"
            )

        return suggestions
        
    def __str__(self) -> str:
        """Return string representation of the analyzer."""
        return f"Visualization Types Analyzer (Libraries: {list(self.metrics['libraries'].keys())})"

    def __repr__(self) -> str:
        """Return detailed string representation of the analyzer."""
        return (f"VisualizationTypesAnalyzer(libraries={dict(self.metrics['libraries'])}, "
                f"plots={dict(self.metrics['plots'])})")
