"""
Visualization Formatting Analyzer Module.

This module analyzes visualization formatting practices in Jupyter notebooks.
It evaluates plot aesthetics, readability, and formatting best practices.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 23:59:44
"""

import ast
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict
from ..base_analyzer import BaseAnalyzer, AnalysisError


class FormattingFeatures:
    """Constants for visualization formatting analysis."""
    
    # Style parameters to check
    STYLE_PARAMETERS = {
        'figure': {'figsize', 'dpi', 'facecolor', 'edgecolor', 'layout'},
        'axes': {'title', 'xlabel', 'ylabel', 'xlim', 'ylim', 'grid'},
        'text': {'fontsize', 'fontweight', 'fontstyle', 'color'},
        'legend': {'loc', 'bbox_to_anchor', 'frameon', 'title'},
        'color': {'cmap', 'color', 'palette'}
    }
    
    # Recommended parameter values
    RECOMMENDED_VALUES = {
        'figsize': (8, 6),  # Default size
        'dpi': 100,         # Minimum DPI
        'fontsize': 12,     # Minimum font size
        'title_fontsize': 14
    }
    
    # Aesthetic elements to check
    AESTHETIC_ELEMENTS = {
        'title': {'set_title', 'suptitle'},
        'labels': {'set_xlabel', 'set_ylabel'},
        'legend': {'legend'},
        'grid': {'grid'},
        'theme': {'style', 'set_style', 'set_theme'}
    }
    
    # Pattern weights for scoring
    PATTERN_WEIGHTS = {
        'basic_formatting': 0.3,
        'readability': 0.3,
        'aesthetics': 0.2,
        'consistency': 0.2
    }


class FormattingVisitor(ast.NodeVisitor):
    """Visitor for analyzing visualization formatting."""

    def __init__(self):
        """Initialize the formatting visitor."""
        self.format_calls = defaultdict(list)
        self.style_settings = defaultdict(list)
        self.aesthetic_elements = defaultdict(list)
        self.issues = []
        self.suggestions = []
        self.current_figure = None

    def visit_Call(self, node: ast.Call):
        """
        Visit call nodes.

        Args:
            node (ast.Call): The call node
        """
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
            base_obj = self._get_base_object(node.func.value)
            
            # Track formatting calls
            self._analyze_formatting_call(method_name, base_obj, node)
            
            # Track style settings
            self._analyze_style_settings(method_name, node)
            
            # Track aesthetic elements
            self._analyze_aesthetic_elements(method_name, node)
            
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

    def _analyze_formatting_call(self, method_name: str, base_obj: str, node: ast.Call):
        """
        Analyze formatting method calls.

        Args:
            method_name (str): The method name
            base_obj (str): The base object name
            node (ast.Call): The call node
        """
        # Track figure creation and formatting
        if method_name == 'figure':
            self.current_figure = node.lineno
            
        for category, params in FormattingFeatures.STYLE_PARAMETERS.items():
            if method_name in params:
                self.format_calls[category].append({
                    'method': method_name,
                    'base': base_obj,
                    'line': node.lineno,
                    'args': len(node.args),
                    'kwargs': {k.arg: self._extract_value(k.value) for k in node.keywords}
                })
                
                # Check parameter values
                self._check_parameter_values(category, method_name, node)

    def _analyze_style_settings(self, method_name: str, node: ast.Call):
        """
        Analyze style-related settings.

        Args:
            method_name (str): The method name
            node (ast.Call): The call node
        """
        style_methods = {'set_style', 'style', 'set_context', 'set_palette'}
        if method_name in style_methods:
            self.style_settings[method_name].append({
                'line': node.lineno,
                'args': [self._extract_value(arg) for arg in node.args],
                'kwargs': {k.arg: self._extract_value(k.value) for k in node.keywords}
            })

    def _analyze_aesthetic_elements(self, method_name: str, node: ast.Call):
        """
        Analyze aesthetic element usage.

        Args:
            method_name (str): The method name
            node (ast.Call): The call node
        """
        for element, methods in FormattingFeatures.AESTHETIC_ELEMENTS.items():
            if method_name in methods:
                self.aesthetic_elements[element].append({
                    'line': node.lineno,
                    'args': len(node.args),
                    'kwargs': {k.arg: self._extract_value(k.value) for k in node.keywords}
                })

    def _check_parameter_values(self, category: str, method_name: str, node: ast.Call):
        """
        Check parameter values against recommendations.

        Args:
            category (str): The parameter category
            method_name (str): The method name
            node (ast.Call): The call node
        """
        for kw in node.keywords:
            if kw.arg in FormattingFeatures.RECOMMENDED_VALUES:
                value = self._extract_value(kw.value)
                recommended = FormattingFeatures.RECOMMENDED_VALUES[kw.arg]
                
                if isinstance(recommended, tuple):
                    if not isinstance(value, (list, tuple)) or len(value) != len(recommended):
                        self.issues.append(
                            f"Line {node.lineno}: Invalid {kw.arg} format"
                        )
                elif isinstance(value, (int, float)) and value < recommended:
                    self.suggestions.append(
                        f"Line {node.lineno}: Consider increasing {kw.arg} to at least {recommended}"
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
        elif isinstance(node, ast.Tuple):
            return tuple(self._extract_value(elt) for elt in node.elts)
        elif isinstance(node, ast.Name):
            return node.id
        return None


class VisualizationFormattingAnalyzer(BaseAnalyzer):
    """
    Analyzer for visualization formatting practices.
    
    This analyzer evaluates:
    - Basic plot formatting
    - Text readability
    - Visual aesthetics
    - Style consistency
    """

    def __init__(self):
        """Initialize the visualization formatting analyzer."""
        super().__init__(name="Visualization Formatting")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'format_calls': defaultdict(list),
            'style_settings': defaultdict(list),
            'aesthetic_elements': defaultdict(list),
            'issues': [],
            'suggestions': []
        }

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'business_intelligence'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze visualization formatting practices.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing:
                - score: Overall formatting score (0-100)
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

            # Analyze formatting
            visitor = FormattingVisitor()
            visitor.visit(tree)

            # Calculate component scores
            basic_score = self._calculate_basic_score(visitor.format_calls)
            readability_score = self._calculate_readability_score(visitor)
            aesthetics_score = self._calculate_aesthetics_score(visitor.aesthetic_elements)
            consistency_score = self._calculate_consistency_score(visitor)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (basic_score, FormattingFeatures.PATTERN_WEIGHTS['basic_formatting']),
                (readability_score, FormattingFeatures.PATTERN_WEIGHTS['readability']),
                (aesthetics_score, FormattingFeatures.PATTERN_WEIGHTS['aesthetics']),
                (consistency_score, FormattingFeatures.PATTERN_WEIGHTS['consistency'])
            ])

            # Store metrics
            self.metrics['format_calls'] = dict(visitor.format_calls)
            self.metrics['style_settings'] = dict(visitor.style_settings)
            self.metrics['aesthetic_elements'] = dict(visitor.aesthetic_elements)
            self.metrics['issues'] = visitor.issues
            self.metrics['suggestions'] = visitor.suggestions

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(visitor),
                'details': {
                    'basic_score': basic_score,
                    'readability_score': readability_score,
                    'aesthetics_score': aesthetics_score,
                    'consistency_score': consistency_score,
                    'metrics': self.metrics
                },
                'suggestions': self._generate_suggestions(visitor)
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing visualization formatting: {str(e)}")

    def _calculate_basic_score(self, format_calls: Dict[str, List[Dict[str, Any]]]) -> float:
        """
        Calculate score based on basic formatting.

        Args:
            format_calls (Dict[str, List[Dict[str, Any]]]): Dictionary of formatting calls

        Returns:
            float: Basic formatting score (0-100)
        """
        if not format_calls:
            return 50.0  # Basic score for no formatting
            
        # Score based on formatting variety
        categories_used = len(format_calls)
        return min(100, 50 + (categories_used * 10))

    def _calculate_readability_score(self, visitor: FormattingVisitor) -> float:
        """
        Calculate score based on text readability.

        Args:
            visitor (FormattingVisitor): The visitor containing analysis data

        Returns:
            float: Readability score (0-100)
        """
        if not visitor.format_calls.get('text', []):
            return 50.0  # Basic score for no text formatting
            
        # Score based on text formatting practices
        text_issues = sum(1 for issue in visitor.issues if 'font' in issue.lower())
        return max(0, 100 - (text_issues * 15))

    def _calculate_aesthetics_score(self, aesthetic_elements: Dict[str, List[Dict[str, Any]]]) -> float:
        """
        Calculate score based on aesthetic elements.

        Args:
            aesthetic_elements (Dict[str, List[Dict[str, Any]]]): Dictionary of aesthetic elements

        Returns:
            float: Aesthetics score (0-100)
        """
        if not aesthetic_elements:
            return 50.0  # Basic score for no aesthetic elements
            
        # Score based on aesthetic element variety
        elements_used = len(aesthetic_elements)
        return min(100, 50 + (elements_used * 10))

    def _calculate_consistency_score(self, visitor: FormattingVisitor) -> float:
        """
        Calculate score based on style consistency.

        Args:
            visitor (FormattingVisitor): The visitor containing analysis data

        Returns:
            float: Consistency score (0-100)
        """
        if not visitor.style_settings:
            return 50.0  # Basic score for no style settings
            
        # Deduct points for inconsistent styles
        inconsistencies = len(visitor.style_settings) - 1  # More than one style change
        return max(0, 100 - (inconsistencies * 20))

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

    def _generate_findings(self, visitor: FormattingVisitor) -> List[str]:
        """
        Generate list of findings from the analysis.

        Args:
            visitor (FormattingVisitor): The visitor containing analysis data

        Returns:
            List[str]: List of findings
        """
        findings = []
        
        if visitor.format_calls:
            findings.append(
                f"Found {sum(len(calls) for calls in visitor.format_calls.values())} formatting calls"
            )
            
        if visitor.style_settings:
            findings.append(
                f"Found {len(visitor.style_settings)} style settings"
            )
            
        if visitor.aesthetic_elements:
            findings.append(
                f"Found {len(visitor.aesthetic_elements)} aesthetic elements"
            )
            
        return findings
        
    def _generate_suggestions(self, visitor: FormattingVisitor) -> List[str]:
        """
        Generate improvement suggestions.

        Args:
            visitor (FormattingVisitor): The visitor containing analysis data

        Returns:
            List[str]: List of improvement suggestions
        """
        suggestions = visitor.suggestions.copy()

        if not visitor.format_calls:
            suggestions.append(
                "Consider adding basic plot formatting (figure size, labels, etc.)"
            )

        if not visitor.aesthetic_elements.get('title', []):
            suggestions.append(
                "Add descriptive titles to plots"
            )

        if not visitor.aesthetic_elements.get('labels', []):
            suggestions.append(
                "Add axis labels to improve plot readability"
            )

        if not visitor.aesthetic_elements.get('legend', []):
            suggestions.append(
                "Consider adding legends where appropriate"
            )

        if not visitor.style_settings:
            suggestions.append(
                "Consider setting a consistent visualization style"
            )

        return suggestions

    def __str__(self) -> str:
        """Return string representation of the analyzer."""
        return (f"Visualization Formatting Analyzer "
                f"(Elements: {list(self.metrics['aesthetic_elements'].keys())})")

    def __repr__(self) -> str:
        """Return detailed string representation of the analyzer."""
        return (f"VisualizationFormattingAnalyzer("
                f"format_calls={dict(self.metrics['format_calls'])}, "
                f"style_settings={dict(self.metrics['style_settings'])}, "
                f"aesthetic_elements={dict(self.metrics['aesthetic_elements'])})")
