"""
Code Conciseness Analyzer Module.

This module analyzes code conciseness in Jupyter notebook cells.
It evaluates code length, complexity, and identifies opportunities for more concise expressions.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 23:49:18
"""

import ast
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict
from ..base_analyzer import BaseAnalyzer, AnalysisError


class ConcisenessMeasures:
    """Constants for code conciseness analysis."""
    
    # Length thresholds
    MAX_LINE_LENGTH = 79  # PEP 8 recommendation
    MAX_FUNCTION_LENGTH = 50  # lines
    MAX_CLASS_LENGTH = 100  # lines
    
    # Complexity thresholds
    MAX_LOOP_NESTING = 3
    MAX_IF_NESTING = 3
    MAX_LIST_COMPREHENSION_LENGTH = 50  # characters
    
    # Pattern weights for scoring
    PATTERN_WEIGHTS = {
        'long_lines': 0.3,
        'nested_structures': 0.25,
        'repeated_code': 0.25,
        'comprehension_usage': 0.2
    }


class ConcisenessVisitor(ast.NodeVisitor):
    """Visitor for analyzing code conciseness."""

    def __init__(self):
        """Initialize the conciseness visitor."""
        self.metrics = defaultdict(list)
        self.issues = []
        self.suggestions = []
        self.current_nesting = 0
        self.line_lengths = []
        self.comprehensions = []
        self.repeated_patterns = defaultdict(int)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Visit function definition nodes.

        Args:
            node (ast.FunctionDef): The function definition node
        """
        lines = len(node.body)
        if lines > ConcisenessMeasures.MAX_FUNCTION_LENGTH:
            self.issues.append(
                f"Function '{node.name}' is too long ({lines} lines)"
            )
            self.suggestions.append(
                f"Consider breaking '{node.name}' into smaller functions"
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """
        Visit class definition nodes.

        Args:
            node (ast.ClassDef): The class definition node
        """
        lines = sum(len(n.body) if hasattr(n, 'body') else 1 for n in node.body)
        if lines > ConcisenessMeasures.MAX_CLASS_LENGTH:
            self.issues.append(
                f"Class '{node.name}' is too long ({lines} lines)"
            )
            self.suggestions.append(
                f"Consider splitting '{node.name}' into smaller classes"
            )
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        """
        Visit for loop nodes.

        Args:
            node (ast.For): The for loop node
        """
        self.current_nesting += 1
        if self.current_nesting > ConcisenessMeasures.MAX_LOOP_NESTING:
            self.issues.append(
                f"Deeply nested loop detected (depth: {self.current_nesting})"
            )
            self.suggestions.append(
                "Consider restructuring deeply nested loops using functions or comprehensions"
            )
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_If(self, node: ast.If):
        """
        Visit if statement nodes.

        Args:
            node (ast.If): The if statement node
        """
        self.current_nesting += 1
        if self.current_nesting > ConcisenessMeasures.MAX_IF_NESTING:
            self.issues.append(
                f"Deeply nested conditional detected (depth: {self.current_nesting})"
            )
            self.suggestions.append(
                "Consider simplifying nested conditionals using early returns or guard clauses"
            )
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_ListComp(self, node: ast.ListComp):
        """
        Visit list comprehension nodes.

        Args:
            node (ast.ListComp): The list comprehension node
        """
        self._analyze_comprehension(node, 'list')
        self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp):
        """
        Visit set comprehension nodes.

        Args:
            node (ast.SetComp): The set comprehension node
        """
        self._analyze_comprehension(node, 'set')
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp):
        """
        Visit dictionary comprehension nodes.

        Args:
            node (ast.DictComp): The dictionary comprehension node
        """
        self._analyze_comprehension(node, 'dict')
        self.generic_visit(node)

    def _analyze_comprehension(self, node: ast.AST, comp_type: str):
        """
        Analyze a comprehension node.

        Args:
            node (ast.AST): The comprehension node
            comp_type (str): Type of comprehension ('list', 'set', or 'dict')
        """
        source_length = len(ast.dump(node))
        if source_length > ConcisenessMeasures.MAX_LIST_COMPREHENSION_LENGTH:
            self.issues.append(
                f"Complex {comp_type} comprehension detected"
            )
            self.suggestions.append(
                f"Consider breaking down the {comp_type} comprehension into multiple steps"
            )
        self.comprehensions.append({
            'type': comp_type,
            'length': source_length,
            'line': getattr(node, 'lineno', 0)
        })

    def analyze_line_lengths(self, code: str):
        """
        Analyze line lengths in the code.

        Args:
            code (str): The code to analyze
        """
        for i, line in enumerate(code.splitlines(), 1):
            length = len(line)
            if length > ConcisenessMeasures.MAX_LINE_LENGTH:
                self.issues.append(
                    f"Line {i} is too long ({length} characters)"
                )
                self.suggestions.append(
                    f"Consider breaking line {i} into multiple lines"
                )
            self.line_lengths.append(length)


class CodeConcisenessAnalyzer(BaseAnalyzer):
    """
    Analyzer for code conciseness.
    
    This analyzer evaluates:
    - Code length and complexity
    - Line lengths
    - Nesting depth
    - Use of comprehensions
    - Code repetition
    - Opportunities for more concise expressions
    """

    def __init__(self):
        """Initialize the code conciseness analyzer."""
        super().__init__(name="Code Conciseness")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'line_lengths': [],
            'nesting_depths': [],
            'comprehensions': [],
            'issues': [],
            'suggestions': []
        }

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'builder_mindset'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze code conciseness.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing:
                - score: Overall conciseness score (0-100)
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
            visitor = ConcisenessVisitor()
            visitor.visit(tree)
            visitor.analyze_line_lengths(code)

            # Calculate component scores
            line_score = self._calculate_line_score(visitor.line_lengths)
            nesting_score = self._calculate_nesting_score(visitor.current_nesting)
            comprehension_score = self._calculate_comprehension_score(visitor.comprehensions)
            repetition_score = self._calculate_repetition_score(visitor.repeated_patterns)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (line_score, ConcisenessMeasures.PATTERN_WEIGHTS['long_lines']),
                (nesting_score, ConcisenessMeasures.PATTERN_WEIGHTS['nested_structures']),
                (repetition_score, ConcisenessMeasures.PATTERN_WEIGHTS['repeated_code']),
                (comprehension_score, ConcisenessMeasures.PATTERN_WEIGHTS['comprehension_usage'])
            ])

            # Prepare results
            results = {
                'score': overall_score,
                'findings': visitor.issues,
                'details': {
                    'line_score': line_score,
                    'nesting_score': nesting_score,
                    'comprehension_score': comprehension_score,
                    'repetition_score': repetition_score,
                    'metrics': {
                        'line_lengths': visitor.line_lengths,
                        'comprehensions': visitor.comprehensions,
                        'repeated_patterns': dict(visitor.repeated_patterns)
                    }
                },
                'suggestions': self._generate_suggestions(visitor)
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing code conciseness: {str(e)}")

    def _calculate_line_score(self, line_lengths: List[int]) -> float:
        """
        Calculate score based on line lengths.

        Args:
            line_lengths (List[int]): List of line lengths

        Returns:
            float: Line length score (0-100)
        """
        if not line_lengths:
            return 100.0
            
        long_lines = sum(1 for length in line_lengths
                        if length > ConcisenessMeasures.MAX_LINE_LENGTH)
        return max(0, 100 - (long_lines * 5))

    def _calculate_nesting_score(self, max_nesting: int) -> float:
        """
        Calculate score based on nesting depth.

        Args:
            max_nesting (int): Maximum nesting depth found

        Returns:
            float: Nesting score (0-100)
        """
        if max_nesting <= ConcisenessMeasures.MAX_IF_NESTING:
            return 100.0
        return max(0, 100 - ((max_nesting - ConcisenessMeasures.MAX_IF_NESTING) * 15))

    def _calculate_comprehension_score(self, comprehensions: List[Dict[str, Any]]) -> float:
        """
        Calculate score based on comprehension usage.

        Args:
            comprehensions (List[Dict[str, Any]]): List of comprehension metrics

        Returns:
            float: Comprehension score (0-100)
        """
        if not comprehensions:
            return 100.0
            
        complex_comprehensions = sum(
            1 for comp in comprehensions
            if comp['length'] > ConcisenessMeasures.MAX_LIST_COMPREHENSION_LENGTH
        )
        return max(0, 100 - (complex_comprehensions * 10))

    def _calculate_repetition_score(self, patterns: Dict[str, int]) -> float:
        """
        Calculate score based on code repetition.

        Args:
            patterns (Dict[str, int]): Dictionary of repeated patterns

        Returns:
            float: Repetition score (0-100)
        """
        if not patterns:
            return 100.0
            
        repetition_penalty = sum(count - 1 for count in patterns.values() if count > 1)
        return max(0, 100 - (repetition_penalty * 5))

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

    def _generate_suggestions(self, visitor: ConcisenessVisitor) -> List[str]:
        """
        Generate improvement suggestions.

        Args:
            visitor (ConcisenessVisitor): The visitor containing analysis data

        Returns:
            List[str]: List of improvement suggestions
        """
        suggestions = visitor.suggestions.copy()

        # Add general suggestions
        if visitor.line_lengths:
            avg_length = sum(visitor.line_lengths) / len(visitor.line_lengths)
            if avg_length > ConcisenessMeasures.MAX_LINE_LENGTH * 0.8:
                suggestions.append(
                    "Consider using shorter, more focused lines of code"
                )

        if visitor.current_nesting > ConcisenessMeasures.MAX_IF_NESTING - 1:
            suggestions.append(
                "Consider extracting nested logic into separate functions"
            )

        if not visitor.comprehensions:
            suggestions.append(
                "Consider using list/dict comprehensions for simple iterations"
            )

        return suggestions

    def __str__(self) -> str:
        """Return string representation of the analyzer."""
        return f"Code Conciseness Analyzer"

    def __repr__(self) -> str:
        """Return detailed string representation of the analyzer."""
        return f"CodeConcisenessAnalyzer(metrics={self.metrics})"
