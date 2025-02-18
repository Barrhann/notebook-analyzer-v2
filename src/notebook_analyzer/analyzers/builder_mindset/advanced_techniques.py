"""
Advanced Techniques Analyzer Module.

This module analyzes the usage of advanced programming techniques in Jupyter notebooks.
It evaluates the use of advanced Python features, design patterns, and optimization techniques.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 23:54:15
"""

import ast
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict
from ..base_analyzer import BaseAnalyzer, AnalysisError


class AdvancedFeatures:
    """Constants for advanced technique analysis."""
    
    # Advanced Python features to detect
    ADVANCED_DECORATORS = {
        'property', 'classmethod', 'staticmethod', 'abstractmethod',
        'contextmanager', 'cached_property'
    }
    
    ADVANCED_METHODS = {
        '__enter__', '__exit__', '__iter__', '__next__',
        '__getitem__', '__setitem__', '__call__'
    }
    
    DESIGN_PATTERNS = {
        'Factory': {'create', 'factory', 'build'},
        'Singleton': {'instance', 'getInstance'},
        'Observer': {'notify', 'subscribe', 'observer'},
        'Strategy': {'strategy', 'algorithm'},
        'Decorator': {'wrap', 'decorate'}
    }
    
    # Performance optimization features
    OPTIMIZATION_FEATURES = {
        'generator': {'yield', 'yield from'},
        'comprehension': {'list comp', 'dict comp', 'set comp'},
        'async': {'async', 'await', 'asyncio'}
    }
    
    # Pattern weights for scoring
    PATTERN_WEIGHTS = {
        'decorators': 0.25,
        'magic_methods': 0.25,
        'design_patterns': 0.25,
        'optimizations': 0.25
    }


class AdvancedTechniquesVisitor(ast.NodeVisitor):
    """Visitor for analyzing advanced programming techniques."""

    def __init__(self):
        """Initialize the advanced techniques visitor."""
        self.features = defaultdict(list)
        self.issues = []
        self.suggestions = []
        self.metrics = defaultdict(int)
        self.decorators = []
        self.magic_methods = []
        self.patterns = defaultdict(list)
        self.optimizations = []

    def visit_ClassDef(self, node: ast.ClassDef):
        """
        Visit class definition nodes.

        Args:
            node (ast.ClassDef): The class definition node
        """
        # Analyze decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in AdvancedFeatures.ADVANCED_DECORATORS:
                    self.decorators.append({
                        'type': decorator.id,
                        'target': node.name,
                        'line': node.lineno
                    })
        
        # Check for design patterns
        self._analyze_design_pattern(node)
        
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Visit function definition nodes.

        Args:
            node (ast.FunctionDef): The function definition node
        """
        # Analyze decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in AdvancedFeatures.ADVANCED_DECORATORS:
                    self.decorators.append({
                        'type': decorator.id,
                        'target': node.name,
                        'line': node.lineno
                    })
        
        # Check for magic methods
        if node.name in AdvancedFeatures.ADVANCED_METHODS:
            self.magic_methods.append({
                'name': node.name,
                'line': node.lineno
            })
        
        self.generic_visit(node)

    def visit_Yield(self, node: ast.Yield):
        """
        Visit yield nodes.

        Args:
            node (ast.Yield): The yield node
        """
        self.optimizations.append({
            'type': 'generator',
            'line': node.lineno
        })
        self.generic_visit(node)

    def visit_YieldFrom(self, node: ast.YieldFrom):
        """
        Visit yield from nodes.

        Args:
            node (ast.YieldFrom): The yield from node
        """
        self.optimizations.append({
            'type': 'generator',
            'line': node.lineno
        })
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp):
        """
        Visit list comprehension nodes.

        Args:
            node (ast.ListComp): The list comprehension node
        """
        self.optimizations.append({
            'type': 'comprehension',
            'subtype': 'list',
            'line': node.lineno
        })
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp):
        """
        Visit dictionary comprehension nodes.

        Args:
            node (ast.DictComp): The dictionary comprehension node
        """
        self.optimizations.append({
            'type': 'comprehension',
            'subtype': 'dict',
            'line': node.lineno
        })
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """
        Visit async function definition nodes.

        Args:
            node (ast.AsyncFunctionDef): The async function definition node
        """
        self.optimizations.append({
            'type': 'async',
            'name': node.name,
            'line': node.lineno
        })
        self.generic_visit(node)

    def _analyze_design_pattern(self, node: ast.ClassDef):
        """
        Analyze class for design pattern usage.

        Args:
            node (ast.ClassDef): The class definition node
        """
        class_src = ast.dump(node)
        
        for pattern, keywords in AdvancedFeatures.DESIGN_PATTERNS.items():
            if any(keyword.lower() in node.name.lower() for keyword in keywords):
                self.patterns[pattern].append({
                    'class': node.name,
                    'line': node.lineno
                })
            elif any(keyword.lower() in class_src.lower() for keyword in keywords):
                self.patterns[pattern].append({
                    'class': node.name,
                    'line': node.lineno
                })


class AdvancedTechniquesAnalyzer(BaseAnalyzer):
    """
    Analyzer for advanced programming techniques.
    
    This analyzer evaluates:
    - Use of decorators and magic methods
    - Implementation of design patterns
    - Performance optimization techniques
    - Advanced Python features
    """

    def __init__(self):
        """Initialize the advanced techniques analyzer."""
        super().__init__(name="Advanced Techniques")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'decorators': [],
            'magic_methods': [],
            'design_patterns': defaultdict(list),
            'optimizations': []
        }

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'builder_mindset'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze advanced programming techniques.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing:
                - score: Overall advanced techniques score (0-100)
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

            # Analyze code structure
            visitor = AdvancedTechniquesVisitor()
            visitor.visit(tree)

            # Calculate component scores
            decorator_score = self._calculate_decorator_score(visitor.decorators)
            method_score = self._calculate_method_score(visitor.magic_methods)
            pattern_score = self._calculate_pattern_score(visitor.patterns)
            optimization_score = self._calculate_optimization_score(visitor.optimizations)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (decorator_score, AdvancedFeatures.PATTERN_WEIGHTS['decorators']),
                (method_score, AdvancedFeatures.PATTERN_WEIGHTS['magic_methods']),
                (pattern_score, AdvancedFeatures.PATTERN_WEIGHTS['design_patterns']),
                (optimization_score, AdvancedFeatures.PATTERN_WEIGHTS['optimizations'])
            ])

            # Store metrics
            self.metrics['decorators'] = visitor.decorators
            self.metrics['magic_methods'] = visitor.magic_methods
            self.metrics['design_patterns'] = dict(visitor.patterns)
            self.metrics['optimizations'] = visitor.optimizations

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(visitor),
                'details': {
                    'decorator_score': decorator_score,
                    'method_score': method_score,
                    'pattern_score': pattern_score,
                    'optimization_score': optimization_score,
                    'metrics': self.metrics
                },
                'suggestions': self._generate_suggestions(visitor)
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing advanced techniques: {str(e)}")

    def _calculate_decorator_score(self, decorators: List[Dict[str, Any]]) -> float:
        """
        Calculate score based on decorator usage.

        Args:
            decorators (List[Dict[str, Any]]): List of decorator usages

        Returns:
            float: Decorator usage score (0-100)
        """
        if not decorators:
            return 50.0  # Baseline score for no decorator usage
            
        unique_decorators = len({d['type'] for d in decorators})
        return min(100, 50 + (unique_decorators * 10))

    def _calculate_method_score(self, methods: List[Dict[str, Any]]) -> float:
        """
        Calculate score based on magic method usage.

        Args:
            methods (List[Dict[str, Any]]): List of magic method usages

        Returns:
            float: Magic method usage score (0-100)
        """
        if not methods:
            return 50.0  # Baseline score for no magic method usage
            
        unique_methods = len({m['name'] for m in methods})
        return min(100, 50 + (unique_methods * 10))

    def _calculate_pattern_score(self, patterns: Dict[str, List[Dict[str, Any]]]) -> float:
        """
        Calculate score based on design pattern usage.

        Args:
            patterns (Dict[str, List[Dict[str, Any]]]): Dictionary of pattern usages

        Returns:
            float: Design pattern usage score (0-100)
        """
        if not patterns:
            return 50.0  # Baseline score for no pattern usage
            
        unique_patterns = len(patterns)
        return min(100, 50 + (unique_patterns * 15))

    def _calculate_optimization_score(self, optimizations: List[Dict[str, Any]]) -> float:
        """
        Calculate score based on optimization technique usage.

        Args:
            optimizations (List[Dict[str, Any]]): List of optimization usages

        Returns:
            float: Optimization usage score (0-100)
        """
        if not optimizations:
            return 50.0  # Baseline score for no optimization usage
            
        unique_optimizations = len({o['type'] for o in optimizations})
        return min(100, 50 + (unique_optimizations * 15))

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

    def _generate_findings(self, visitor: AdvancedTechniquesVisitor) -> List[str]:
        """
        Generate list of findings from the analysis.

        Args:
            visitor (AdvancedTechniquesVisitor): The visitor containing analysis data

        Returns:
            List[str]: List of findings
        """
        findings = []
        
        if visitor.decorators:
            findings.append(
                f"Found {len(visitor.decorators)} decorator uses"
            )
            
        if visitor.magic_methods:
            findings.append(
                f"Found {len(visitor.magic_methods)} magic method implementations"
            )
            
        if visitor.patterns:
            findings.append(
                f"Detected {len(visitor.patterns)} design pattern implementations"
            )
            
        if visitor.optimizations:
            findings.append(
                f"Found {len(visitor.optimizations)} optimization techniques"
            )
            
        return findings

    def _generate_suggestions(self, visitor: AdvancedTechniquesVisitor) -> List[str]:
        """
        Generate improvement suggestions.

        Args:
            visitor (AdvancedTechniquesVisitor): The visitor containing analysis data

        Returns:
            List[str]: List of improvement suggestions
        """
        suggestions = []

        if not visitor.decorators:
            suggestions.append(
                "Consider using decorators for code reuse and clean implementation"
            )

        if not visitor.magic_methods:
            suggestions.append(
                "Consider implementing magic methods for more Pythonic code"
            )

        if not visitor.patterns:
            suggestions.append(
                "Consider using design patterns for better code organization"
            )

        if not visitor.optimizations:
            suggestions.append(
                "Consider using generators and comprehensions for better performance"
            )

        return suggestions

    def __str__(self) -> str:
        """Return string representation of the analyzer."""
        return f"Advanced Techniques Analyzer"

    def __repr__(self) -> str:
        """Return detailed string representation of the analyzer."""
        return f"AdvancedTechniquesAnalyzer(metrics={self.metrics})"
