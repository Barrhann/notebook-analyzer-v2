"""
Code Conciseness Analyzer Module.

This module analyzes the conciseness and clarity of code in Jupyter notebook cells.
It evaluates code complexity, redundancy, and efficiency of expression.

Created by: Barrhann
Date: 2025-02-17
Last Updated: 2025-02-17 00:35:11
"""

import ast
from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict
import re
from ..base_analyzer import BaseAnalyzer, AnalysisError

class CodeConcisenessAnalyzer(BaseAnalyzer):
    """
    Analyzer for code conciseness and clarity metrics.
    
    This analyzer evaluates:
    - Code complexity and length
    - Variable reuse and scope
    - Redundant operations
    - Expression efficiency
    - List/dict comprehension usage
    - Loop efficiency
    
    Attributes:
        MAX_LINE_LENGTH (int): Maximum recommended line length
        MAX_FUNCTION_LENGTH (int): Maximum recommended function length
        MAX_NESTED_DEPTH (int): Maximum recommended nesting depth
    """

    MAX_LINE_LENGTH = 79
    MAX_FUNCTION_LENGTH = 50
    MAX_NESTED_DEPTH = 3

    def __init__(self):
        """Initialize the code conciseness analyzer."""
        super().__init__(name="Code Conciseness")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'complexity_issues': [],
            'redundancy_issues': [],
            'comprehension_opportunities': [],
            'loop_efficiency': [],
            'variable_reuse': []
        }

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'builder_mindset'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze code conciseness and clarity.

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

            # Perform various conciseness checks
            complexity_score = self._analyze_complexity(tree)
            redundancy_score = self._analyze_redundancy(tree)
            comprehension_score = self._analyze_comprehension_usage(tree)
            loop_score = self._analyze_loop_efficiency(tree)
            variable_score = self._analyze_variable_usage(tree)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (complexity_score, 0.30),    # 30% weight
                (redundancy_score, 0.25),    # 25% weight
                (comprehension_score, 0.20), # 20% weight
                (loop_score, 0.15),         # 15% weight
                (variable_score, 0.10)      # 10% weight
            ])

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(),
                'details': {
                    'complexity_score': complexity_score,
                    'redundancy_score': redundancy_score,
                    'comprehension_score': comprehension_score,
                    'loop_efficiency_score': loop_score,
                    'variable_usage_score': variable_score,
                    'metrics': self.metrics
                },
                'suggestions': self._generate_suggestions()
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing code conciseness: {str(e)}")

    def _analyze_complexity(self, tree: ast.AST) -> float:
        """
        Analyze code complexity and nesting.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Complexity score (0-100)
        """
        issues = []
        max_depth = 0
        current_depth = 0

        class DepthVisitor(ast.NodeVisitor):
            def visit_ClassDef(self, node):
                nonlocal current_depth, max_depth
                current_depth += 1
                max_depth = max(max_depth, current_depth)
                self.generic_visit(node)
                current_depth -= 1

            def visit_FunctionDef(self, node):
                nonlocal current_depth, max_depth
                current_depth += 1
                max_depth = max(max_depth, current_depth)
                
                # Check function length
                if len(node.body) > self.MAX_FUNCTION_LENGTH:
                    issues.append(f"Function '{node.name}' is too long ({len(node.body)} lines)")
                
                self.generic_visit(node)
                current_depth -= 1

            visit_If = visit_For = visit_While = visit_With = visit_Try = visit_ClassDef

        visitor = DepthVisitor()
        visitor.visit(tree)

        if max_depth > self.MAX_NESTED_DEPTH:
            issues.append(f"Maximum nesting depth of {max_depth} exceeds limit of {self.MAX_NESTED_DEPTH}")

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['complexity_issues'].extend(issues)
        return score

    def _analyze_redundancy(self, tree: ast.AST) -> float:
        """
        Analyze code for redundant operations.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Redundancy score (0-100)
        """
        issues = []
        operations = defaultdict(int)

        class RedundancyVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # Track function calls
                if isinstance(node.func, ast.Name):
                    operations[f"call_{node.func.id}"] += 1
                self.generic_visit(node)

            def visit_BinOp(self, node):
                # Track binary operations
                op_type = type(node.op).__name__
                operations[f"binop_{op_type}"] += 1
                self.generic_visit(node)

        visitor = RedundancyVisitor()
        visitor.visit(tree)

        # Check for redundant operations
        for op, count in operations.items():
            if count > 3:
                issues.append(f"Operation {op} used {count} times - consider refactoring")

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 5))
        self.metrics['redundancy_issues'].extend(issues)
        return score

    def _analyze_comprehension_usage(self, tree: ast.AST) -> float:
        """
        Analyze usage of list/dict comprehensions.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Comprehension usage score (0-100)
        """
        opportunities = []
        comprehension_count = 0

        class ComprehensionVisitor(ast.NodeVisitor):
            def visit_ListComp(self, node):
                nonlocal comprehension_count
                comprehension_count += 1
                self.generic_visit(node)

            def visit_For(self, node):
                # Check if for loop could be a comprehension
                if isinstance(node.body, list) and len(node.body) == 1:
                    if isinstance(node.body[0], (ast.Append, ast.Assign)):
                        opportunities.append(
                            f"Loop at line {node.lineno} could be a list comprehension"
                        )
                self.generic_visit(node)

        visitor = ComprehensionVisitor()
        visitor.visit(tree)

        # Calculate score based on opportunities taken vs. missed
        total = comprehension_count + len(opportunities)
        if total == 0:
            return 100.0
            
        score = (comprehension_count / total) * 100 if total > 0 else 100
        self.metrics['comprehension_opportunities'].extend(opportunities)
        return score

    def _analyze_loop_efficiency(self, tree: ast.AST) -> float:
        """
        Analyze loop efficiency.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Loop efficiency score (0-100)
        """
        issues = []

        class LoopVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # Check for inefficient list operations in loops
                if isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name):
                        if node.iter.func.id == 'range' and len(node.iter.args) == 1:
                            if isinstance(node.iter.args[0], ast.Call):
                                if isinstance(node.iter.args[0].func, ast.Name):
                                    if node.iter.args[0].func.id == 'len':
                                        issues.append(
                                            f"Use enumerate() instead of range(len()) at line {node.lineno}"
                                        )
                self.generic_visit(node)

        visitor = LoopVisitor()
        visitor.visit(tree)

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['loop_efficiency'].extend(issues)
        return score

    def _analyze_variable_usage(self, tree: ast.AST) -> float:
        """
        Analyze variable usage efficiency.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Variable usage score (0-100)
        """
        issues = []
        variables = defaultdict(int)

        class VariableVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    variables[node.id] += 1
                self.generic_visit(node)

        visitor = VariableVisitor()
        visitor.visit(tree)

        # Check for single-use variables
        for var, count in variables.items():
            if count == 1 and not var.startswith('_'):
                issues.append(f"Variable '{var}' is only used once")

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 5))
        self.metrics['variable_reuse'].extend(issues)
        return score

    def _calculate_overall_score(self, scores_and_weights: List[Tuple[float, float]]) -> float:
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

    def _generate_findings(self) -> List[str]:
        """Generate list of significant findings."""
        findings = []
        
        # Add significant complexity issues
        if self.metrics['complexity_issues']:
            findings.extend(self.metrics['complexity_issues'][:3])
            
        # Add significant redundancy issues
        if self.metrics['redundancy_issues']:
            findings.extend(self.metrics['redundancy_issues'][:3])
            
        # Add comprehension opportunities
        if self.metrics['comprehension_opportunities']:
            findings.extend(self.metrics['comprehension_opportunities'][:2])
            
        return findings

    def _generate_suggestions(self) -> List[str]:
        """Generate improvement suggestions based on findings."""
        suggestions = []
        
        # Complexity suggestions
        if self.metrics['complexity_issues']:
            suggestions.append(
                f"Reduce nesting depth to maximum of {self.MAX_NESTED_DEPTH} levels"
            )
            suggestions.append(
                f"Keep functions under {self.MAX_FUNCTION_LENGTH} lines"
            )
            
        # Redundancy suggestions
        if self.metrics['redundancy_issues']:
            suggestions.append(
                "Extract repeated operations into helper functions"
            )
            
        # Comprehension suggestions
        if self.metrics['comprehension_opportunities']:
            suggestions.append(
                "Consider using list comprehensions for simple loops"
            )
            
        # Loop suggestions
        if self.metrics['loop_efficiency']:
            suggestions.append(
                "Use enumerate() instead of range(len()) for index-based iteration"
            )
            
        return suggestions
