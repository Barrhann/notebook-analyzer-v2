"""
Code Reusability Analyzer Module.

This module analyzes code reusability in Jupyter notebook cells.
It evaluates function and class design, modularity, and identifies opportunities for better code reuse.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 23:51:34
"""

import ast
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict
from ..base_analyzer import BaseAnalyzer, AnalysisError


class ReusabilityMetrics:
    """Constants for code reusability analysis."""
    
    # Function metrics
    MAX_FUNCTION_PARAMS = 5
    MIN_FUNCTION_LENGTH = 3
    MAX_FUNCTION_LENGTH = 50
    
    # Class metrics
    MAX_CLASS_METHODS = 10
    MIN_CLASS_METHODS = 2
    MAX_CLASS_ATTRIBUTES = 10
    
    # Documentation metrics
    MIN_DOCSTRING_LENGTH = 10
    REQUIRED_DOCSTRING_SECTIONS = {'Args', 'Returns', 'Raises'}
    
    # Pattern weights for scoring
    PATTERN_WEIGHTS = {
        'function_design': 0.3,
        'class_design': 0.25,
        'documentation': 0.25,
        'modularity': 0.2
    }


class ReusabilityVisitor(ast.NodeVisitor):
    """Visitor for analyzing code reusability."""

    def __init__(self):
        """Initialize the reusability visitor."""
        self.functions = []
        self.classes = []
        self.issues = []
        self.suggestions = []
        self.metrics = defaultdict(list)
        self.dependencies = defaultdict(set)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Visit function definition nodes.

        Args:
            node (ast.FunctionDef): The function definition node
        """
        function_info = {
            'name': node.name,
            'params': len(node.args.args),
            'lines': len(node.body),
            'docstring': ast.get_docstring(node),
            'line_no': node.lineno,
            'dependencies': set()
        }
        
        # Check parameter count
        if function_info['params'] > ReusabilityMetrics.MAX_FUNCTION_PARAMS:
            self.issues.append(
                f"Function '{node.name}' has too many parameters ({function_info['params']})"
            )
            self.suggestions.append(
                f"Consider grouping parameters in '{node.name}' using a class or data structure"
            )
            
        # Check function length
        if function_info['lines'] < ReusabilityMetrics.MIN_FUNCTION_LENGTH:
            self.issues.append(
                f"Function '{node.name}' might be too short ({function_info['lines']} lines)"
            )
        elif function_info['lines'] > ReusabilityMetrics.MAX_FUNCTION_LENGTH:
            self.issues.append(
                f"Function '{node.name}' might be too long ({function_info['lines']} lines)"
            )
            self.suggestions.append(
                f"Consider breaking '{node.name}' into smaller, more focused functions"
            )
            
        # Check docstring
        self._analyze_docstring(node, function_info['docstring'], 'function')
        
        # Analyze function body for dependencies
        self._analyze_dependencies(node, function_info['dependencies'])
        
        self.functions.append(function_info)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """
        Visit class definition nodes.

        Args:
            node (ast.ClassDef): The class definition node
        """
        class_info = {
            'name': node.name,
            'methods': [],
            'attributes': set(),
            'docstring': ast.get_docstring(node),
            'line_no': node.lineno,
            'dependencies': set()
        }
        
        # Collect methods and attributes
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info['methods'].append(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_info['attributes'].add(target.id)
                        
        # Check method count
        method_count = len(class_info['methods'])
        if method_count < ReusabilityMetrics.MIN_CLASS_METHODS:
            self.issues.append(
                f"Class '{node.name}' has too few methods ({method_count})"
            )
        elif method_count > ReusabilityMetrics.MAX_CLASS_METHODS:
            self.issues.append(
                f"Class '{node.name}' has too many methods ({method_count})"
            )
            self.suggestions.append(
                f"Consider splitting '{node.name}' into multiple classes"
            )
            
        # Check attribute count
        attr_count = len(class_info['attributes'])
        if attr_count > ReusabilityMetrics.MAX_CLASS_ATTRIBUTES:
            self.issues.append(
                f"Class '{node.name}' has too many attributes ({attr_count})"
            )
            self.suggestions.append(
                f"Consider grouping attributes in '{node.name}' into logical subclasses"
            )
            
        # Check docstring
        self._analyze_docstring(node, class_info['docstring'], 'class')
        
        # Analyze class dependencies
        self._analyze_dependencies(node, class_info['dependencies'])
        
        self.classes.append(class_info)
        self.generic_visit(node)

    def _analyze_docstring(self, node: ast.AST, docstring: Optional[str], node_type: str):
        """
        Analyze docstring quality.

        Args:
            node (ast.AST): The AST node
            docstring (Optional[str]): The docstring to analyze
            node_type (str): Type of node ('function' or 'class')
        """
        if not docstring:
            self.issues.append(
                f"{node_type.capitalize()} '{node.name}' lacks a docstring"
            )
            self.suggestions.append(
                f"Add a descriptive docstring to {node_type} '{node.name}'"
            )
            return
            
        if len(docstring) < ReusabilityMetrics.MIN_DOCSTRING_LENGTH:
            self.issues.append(
                f"{node_type.capitalize()} '{node.name}' has a short docstring"
            )
            
        # Check for required sections
        sections_found = {
            section for section in ReusabilityMetrics.REQUIRED_DOCSTRING_SECTIONS
            if section.lower() in docstring.lower()
        }
        
        missing_sections = ReusabilityMetrics.REQUIRED_DOCSTRING_SECTIONS - sections_found
        if missing_sections:
            self.suggestions.append(
                f"Add {', '.join(missing_sections)} sections to {node_type} '{node.name}' docstring"
            )

    def _analyze_dependencies(self, node: ast.AST, dependencies: Set[str]):
        """
        Analyze node dependencies.

        Args:
            node (ast.AST): The AST node
            dependencies (Set[str]): Set to store dependencies
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                dependencies.add(child.id)


class CodeReusabilityAnalyzer(BaseAnalyzer):
    """
    Analyzer for code reusability.
    
    This analyzer evaluates:
    - Function design and organization
    - Class structure and cohesion
    - Documentation quality
    - Code modularity
    - Dependencies and coupling
    """

    def __init__(self):
        """Initialize the code reusability analyzer."""
        super().__init__(name="Code Reusability")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'function_metrics': [],
            'class_metrics': [],
            'documentation_metrics': [],
            'modularity_metrics': []
        }

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'builder_mindset'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze code reusability.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing:
                - score: Overall reusability score (0-100)
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
            visitor = ReusabilityVisitor()
            visitor.visit(tree)

            # Calculate component scores
            function_score = self._calculate_function_score(visitor.functions)
            class_score = self._calculate_class_score(visitor.classes)
            doc_score = self._calculate_documentation_score(visitor)
            modularity_score = self._calculate_modularity_score(visitor)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (function_score, ReusabilityMetrics.PATTERN_WEIGHTS['function_design']),
                (class_score, ReusabilityMetrics.PATTERN_WEIGHTS['class_design']),
                (doc_score, ReusabilityMetrics.PATTERN_WEIGHTS['documentation']),
                (modularity_score, ReusabilityMetrics.PATTERN_WEIGHTS['modularity'])
            ])

            # Prepare results
            results = {
                'score': overall_score,
                'findings': visitor.issues,
                'details': {
                    'function_score': function_score,
                    'class_score': class_score,
                    'documentation_score': doc_score,
                    'modularity_score': modularity_score,
                    'metrics': {
                        'functions': visitor.functions,
                        'classes': visitor.classes,
                        'dependencies': dict(visitor.dependencies)
                    }
                },
                'suggestions': self._generate_suggestions(visitor)
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing code reusability: {str(e)}")

    def _calculate_function_score(self, functions: List[Dict[str, Any]]) -> float:
        """
        Calculate score based on function design.

        Args:
            functions (List[Dict[str, Any]]): List of function metrics

        Returns:
            float: Function design score (0-100)
        """
        if not functions:
            return 100.0
            
        issues = 0
        for func in functions:
            if func['params'] > ReusabilityMetrics.MAX_FUNCTION_PARAMS:
                issues += 1
            if func['lines'] > ReusabilityMetrics.MAX_FUNCTION_LENGTH:
                issues += 1
            if func['lines'] < ReusabilityMetrics.MIN_FUNCTION_LENGTH:
                issues += 0.5
                
        return max(0, 100 - (issues * 10))

    def _calculate_class_score(self, classes: List[Dict[str, Any]]) -> float:
        """
        Calculate score based on class design.

        Args:
            classes (List[Dict[str, Any]]): List of class metrics

        Returns:
            float: Class design score (0-100)
        """
        if not classes:
            return 100.0
            
        issues = 0
        for cls in classes:
            if len(cls['methods']) > ReusabilityMetrics.MAX_CLASS_METHODS:
                issues += 1
            if len(cls['methods']) < ReusabilityMetrics.MIN_CLASS_METHODS:
                issues += 0.5
            if len(cls['attributes']) > ReusabilityMetrics.MAX_CLASS_ATTRIBUTES:
                issues += 1
                
        return max(0, 100 - (issues * 10))

    def _calculate_documentation_score(self, visitor: ReusabilityVisitor) -> float:
        """
        Calculate score based on documentation quality.

        Args:
            visitor (ReusabilityVisitor): The visitor containing analysis data

        Returns:
            float: Documentation score (0-100)
        """
        doc_issues = sum(
            1 for issue in visitor.issues
            if 'docstring' in issue.lower()
        )
        return max(0, 100 - (doc_issues * 15))

    def _calculate_modularity_score(self, visitor: ReusabilityVisitor) -> float:
        """
        Calculate score based on code modularity.

        Args:
            visitor (ReusabilityVisitor): The visitor containing analysis data

        Returns:
            float: Modularity score (0-100)
        """
        dependency_issues = 0
        for deps in visitor.dependencies.values():
            if len(deps) > ReusabilityMetrics.MAX_FUNCTION_PARAMS:
                dependency_issues += 1
                
        return max(0, 100 - (dependency_issues * 10))

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

    def _generate_suggestions(self, visitor: ReusabilityVisitor) -> List[str]:
        """
        Generate improvement suggestions.

        Args:
            visitor (ReusabilityVisitor): The visitor containing analysis data

        Returns:
            List[str]: List of improvement suggestions
        """
        suggestions = visitor.suggestions.copy()

        # Add general suggestions
        if not visitor.functions and not visitor.classes:
            suggestions.append(
                "Consider organizing code into reusable functions and classes"
            )

        if visitor.functions and not visitor.classes:
            suggestions.append(
                "Consider grouping related functions into classes"
            )

        if any(len(deps) > ReusabilityMetrics.MAX_FUNCTION_PARAMS
               for deps in visitor.dependencies.values()):
            suggestions.append(
                "Consider reducing dependencies through better encapsulation"
            )

        return suggestions

    def __str__(self) -> str:
        """Return string representation of the analyzer."""
        return f"Code Reusability Analyzer"

    def __repr__(self) -> str:
        """Return detailed string representation of the analyzer."""
        return f"CodeReusabilityAnalyzer(metrics={self.metrics})"
