"""
Dataset Join Analyzer Module.

This module analyzes data joining operations in Jupyter notebooks.
It evaluates join patterns, efficiency, and best practices in data merging.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 23:45:59
"""

import ast
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict
from ..base_analyzer import BaseAnalyzer, AnalysisError


class JoinVisitor(ast.NodeVisitor):
    """Visitor for analyzing join operations."""

    PANDAS_JOIN_METHODS = {
        'merge', 'join', 'concat', 'append'
    }

    PANDAS_ALIASES = {
        'pandas', 'pd'
    }

    JOIN_TYPE_WEIGHTS = {
        'inner': 1.0,
        'outer': 0.8,
        'left': 0.9,
        'right': 0.9,
        'cross': 0.6
    }

    def __init__(self):
        """Initialize the join visitor."""
        self.join_operations = []
        self.import_aliases = {}
        self.issues = []
        self.suggestions = []
        self.join_count = 0

    def visit_Import(self, node: ast.Import):
        """
        Visit import nodes to track pandas aliases.

        Args:
            node (ast.Import): The import node to visit
        """
        for name in node.names:
            if name.name == 'pandas':
                self.import_aliases[name.asname or name.name] = 'pandas'
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """
        Visit import from nodes to track pandas aliases.

        Args:
            node (ast.ImportFrom): The import from node to visit
        """
        if node.module == 'pandas':
            for name in node.names:
                self.import_aliases[name.asname or name.name] = 'pandas'
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """
        Visit call nodes to analyze join operations.

        Args:
            node (ast.Call): The call node to visit
        """
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
            if method_name in self.PANDAS_JOIN_METHODS:
                self.join_count += 1
                base_obj = self._get_base_object(node.func.value)
                
                join_info = {
                    'method': method_name,
                    'line_no': getattr(node, 'lineno', 0),
                    'args': len(node.args),
                    'kwargs': {k.arg: self._extract_value(k.value) for k in node.keywords},
                    'base_obj': base_obj
                }
                
                self._analyze_join_operation(join_info, node)
                self.join_operations.append(join_info)
                
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

    def _analyze_join_operation(self, join_info: Dict[str, Any], node: ast.Call):
        """
        Analyze a join operation for potential issues.

        Args:
            join_info (Dict[str, Any]): Information about the join
            node (ast.Call): The join operation node
        """
        method = join_info['method']
        kwargs = join_info['kwargs']
        line_no = join_info['line_no']

        if method == 'merge':
            # Check join type
            join_type = kwargs.get('how', 'inner')
            if join_type == 'cross':
                self.issues.append(
                    f"Line {line_no}: Cross join detected - consider using a more specific join type"
                )

            # Check join keys
            if not any(key in kwargs for key in ['on', 'left_on', 'right_on']):
                self.issues.append(
                    f"Line {line_no}: Join columns not explicitly specified"
                )

            # Check for sorted data with multiple keys
            if self._has_multiple_keys(kwargs) and not kwargs.get('sort', False):
                self.suggestions.append(
                    f"Line {line_no}: Consider sorting data before joining on multiple keys"
                )

        elif method == 'concat':
            if 'axis' not in kwargs:
                self.suggestions.append(
                    f"Line {line_no}: Consider specifying 'axis' parameter in concat operation"
                )

        elif method == 'append':
            self.suggestions.append(
                f"Line {line_no}: 'append' is deprecated, consider using 'concat' instead"
            )

    def _has_multiple_keys(self, kwargs: Dict[str, Any]) -> bool:
        """
        Check if join uses multiple keys.

        Args:
            kwargs (Dict[str, Any]): Join operation keyword arguments

        Returns:
            bool: True if multiple keys are used
        """
        on_keys = kwargs.get('on', [])
        if isinstance(on_keys, list):
            return len(on_keys) > 1
        return False


class DatasetJoinAnalyzer(BaseAnalyzer):
    """
    Analyzer for dataset join operations.
    
    This analyzer evaluates:
    - Join methods and patterns
    - Join efficiency
    - Join column specifications
    - Join type selections
    - Data concatenation patterns
    
    Attributes:
        MAX_JOINS_PER_CELL (int): Maximum recommended joins per cell
        MIN_JOIN_SCORE (float): Minimum acceptable join score
    """

    MAX_JOINS_PER_CELL = 3
    MIN_JOIN_SCORE = 70.0

    def __init__(self):
        """Initialize the dataset join analyzer."""
        super().__init__(name="Dataset Join")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'join_operations': [],
            'issues': [],
            'suggestions': [],
            'join_types': defaultdict(int),
            'join_methods': defaultdict(int)
        }

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'builder_mindset'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze dataset join operations.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing:
                - score: Overall join pattern score (0-100)
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

            # Analyze join patterns
            visitor = JoinVisitor()
            visitor.visit(tree)

            # Process results
            join_count = visitor.join_count
            self.metrics['issues'] = visitor.issues
            self.metrics['suggestions'] = visitor.suggestions

            # Analyze join operations
            for join_op in visitor.join_operations:
                method = join_op['method']
                self.metrics['join_methods'][method] += 1

                if method == 'merge':
                    join_type = join_op['kwargs'].get('how', 'inner')
                    self.metrics['join_types'][join_type] += 1

            # Calculate score
            score = self._calculate_score(visitor)

            # Prepare results
            results = {
                'score': score,
                'findings': visitor.issues,
                'details': {
                    'join_count': join_count,
                    'join_types': dict(self.metrics['join_types']),
                    'join_methods': dict(self.metrics['join_methods']),
                    'operations': visitor.join_operations
                },
                'suggestions': self._generate_suggestions(visitor)
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing dataset joins: {str(e)}")

    def _calculate_score(self, visitor: JoinVisitor) -> float:
        """
        Calculate the overall score for join operations.

        Args:
            visitor (JoinVisitor): The visitor containing analysis data

        Returns:
            float: Overall score (0-100)
        """
        if visitor.join_count == 0:
            return 100.0

        base_score = 100.0
        
        # Deduct points for issues
        base_score -= len(visitor.issues) * 10
        
        # Deduct points for too many joins
        if visitor.join_count > self.MAX_JOINS_PER_CELL:
            base_score -= (visitor.join_count - self.MAX_JOINS_PER_CELL) * 5
            
        # Adjust score based on join types
        for op in visitor.join_operations:
            if op['method'] == 'merge':
                join_type = op['kwargs'].get('how', 'inner')
                base_score *= visitor.JOIN_TYPE_WEIGHTS.get(join_type, 0.7)

        return max(0, min(100, round(base_score, 2)))

    def _generate_suggestions(self, visitor: JoinVisitor) -> List[str]:
        """
        Generate improvement suggestions.

        Args:
            visitor (JoinVisitor): The visitor containing analysis data

        Returns:
            List[str]: List of improvement suggestions
        """
        suggestions = visitor.suggestions.copy()

        # Add general suggestions
        if visitor.join_count > self.MAX_JOINS_PER_CELL:
            suggestions.append(
                f"Consider splitting joins across multiple cells (recommended max: {self.MAX_JOINS_PER_CELL})"
            )

        if 'append' in self.metrics['join_methods']:
            suggestions.append(
                "Replace 'append' operations with 'concat' for better performance"
            )

        if len(self.metrics['join_types']) == 1 and 'inner' in self.metrics['join_types']:
            suggestions.append(
                "Consider if other join types (left, right, outer) might be more appropriate"
            )

        return suggestions

    def __str__(self) -> str:
        """Return string representation of the analyzer."""
        return f"Dataset Join Analyzer (Methods: {dict(self.metrics['join_methods'])})"

    def __repr__(self) -> str:
        """Return detailed string representation of the analyzer."""
        return (f"DatasetJoinAnalyzer(join_types={dict(self.metrics['join_types'])}, "
                f"methods={dict(self.metrics['join_methods'])})")
