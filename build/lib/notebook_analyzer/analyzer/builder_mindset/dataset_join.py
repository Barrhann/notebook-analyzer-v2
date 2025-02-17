"""
Dataset Join Analyzer Module.

This module analyzes the data joining operations in Jupyter notebook cells.
It evaluates pandas and SQL join operations, merge patterns, and data combination efficiency.

Created by: Barrhann
Date: 2025-02-17
Last Updated: 2025-02-17 00:41:07
"""

import ast
from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict
import re
from ..base_analyzer import BaseAnalyzer, AnalysisError

class DatasetJoinAnalyzer(BaseAnalyzer):
    """
    Analyzer for dataset joining operations and patterns.
    
    This analyzer evaluates:
    - Pandas merge and join operations
    - SQL join patterns
    - Data concatenation methods
    - Memory efficiency in joins
    - Join key selection
    
    Attributes:
        PANDAS_JOIN_METHODS (Set[str]): Valid pandas join/merge methods
        SQL_JOIN_TYPES (Set[str]): Valid SQL join types
        MAX_JOIN_CHAIN (int): Maximum recommended chain of joins
    """

    PANDAS_JOIN_METHODS = {
        'merge', 'join', 'concat', 'append',
        'combine_first', 'combine', 'update'
    }
    
    SQL_JOIN_TYPES = {
        'inner join', 'left join', 'right join', 'outer join',
        'full join', 'cross join', 'left outer join', 'right outer join'
    }
    
    MAX_JOIN_CHAIN = 3

    def __init__(self):
        """Initialize the dataset join analyzer."""
        super().__init__(name="Dataset Join")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'join_operations': [],
            'join_efficiency': [],
            'memory_usage': [],
            'key_selection': [],
            'join_chains': []
        }
        self.join_count = 0
        self.join_chains = []

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'builder_mindset'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze dataset joining operations.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing:
                - score: Overall join operations score (0-100)
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

            # Perform various join analysis checks
            pandas_score = self._analyze_pandas_joins(tree)
            sql_score = self._analyze_sql_joins(code)
            efficiency_score = self._analyze_join_efficiency(tree)
            memory_score = self._analyze_memory_usage(tree)
            key_score = self._analyze_key_selection(tree)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (pandas_score, 0.30),    # 30% weight
                (sql_score, 0.25),       # 25% weight
                (efficiency_score, 0.20), # 20% weight
                (memory_score, 0.15),    # 15% weight
                (key_score, 0.10)        # 10% weight
            ])

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(),
                'details': {
                    'pandas_joins_score': pandas_score,
                    'sql_joins_score': sql_score,
                    'join_efficiency_score': efficiency_score,
                    'memory_usage_score': memory_score,
                    'key_selection_score': key_score,
                    'metrics': self.metrics,
                    'stats': {
                        'join_count': self.join_count,
                        'join_chains': len(self.join_chains)
                    }
                },
                'suggestions': self._generate_suggestions()
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing dataset joins: {str(e)}")

    def _analyze_pandas_joins(self, tree: ast.AST) -> float:
        """
        Analyze Pandas join operations.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Pandas joins score (0-100)
        """
        issues = []
        current_chain = []

        class PandasJoinVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    method_name = node.func.attr
                    if method_name in self.PANDAS_JOIN_METHODS:
                        self.join_count += 1
                        current_chain.append(method_name)
                        
                        # Check join method arguments
                        if method_name == 'merge':
                            self._check_merge_args(node, issues)
                        elif method_name == 'join':
                            self._check_join_args(node, issues)
                            
                self.generic_visit(node)

        visitor = PandasJoinVisitor()
        visitor.visit(tree)

        # Check join chain length
        if len(current_chain) > self.MAX_JOIN_CHAIN:
            issues.append(
                f"Chain of {len(current_chain)} joins might be inefficient"
            )
            self.join_chains.append(current_chain)

        # Calculate score
        if self.join_count == 0:
            return 100.0  # No joins to analyze
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['join_operations'].extend(issues)
        return score

    def _analyze_sql_joins(self, code: str) -> float:
        """
        Analyze SQL join patterns.

        Args:
            code (str): Code to analyze

        Returns:
            float: SQL joins score (0-100)
        """
        issues = []
        sql_joins = []

        # Look for SQL queries in strings
        for match in re.finditer(r"['\"]{1,3}(.*?)['\"]{1,3}", code):
            query = match.group(1).lower()
            if any(join_type in query for join_type in self.SQL_JOIN_TYPES):
                sql_joins.append(query)
                
                # Check join conditions
                if 'join' in query and 'on' not in query:
                    issues.append("SQL join without ON clause detected")
                    
                # Check cross joins
                if 'cross join' in query:
                    issues.append("Consider alternatives to CROSS JOIN")

        # Calculate score
        if not sql_joins:
            return 100.0  # No SQL joins to analyze
            
        score = max(0, 100 - (len(issues) * 15))
        self.metrics['join_operations'].extend(issues)
        return score

    def _analyze_join_efficiency(self, tree: ast.AST) -> float:
        """
        Analyze join operation efficiency.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Join efficiency score (0-100)
        """
        issues = []

        class EfficiencyVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    method_name = node.func.attr
                    if method_name in self.PANDAS_JOIN_METHODS:
                        # Check for inefficient patterns
                        if not self._has_index_specification(node):
                            issues.append(
                                f"Join operation without specified index/keys"
                            )
                            
                        if self._has_copy_before_join(node):
                            issues.append(
                                "Unnecessary copy before join operation"
                            )
                            
                self.generic_visit(node)

        visitor = EfficiencyVisitor()
        visitor.visit(tree)

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['join_efficiency'].extend(issues)
        return score

    def _analyze_memory_usage(self, tree: ast.AST) -> float:
        """
        Analyze memory usage in join operations.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Memory usage score (0-100)
        """
        issues = []

        class MemoryVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    method_name = node.func.attr
                    if method_name in self.PANDAS_JOIN_METHODS:
                        # Check for memory optimization keywords
                        if not self._has_memory_optimization(node):
                            issues.append(
                                "Join operation without memory optimization"
                            )
                            
                self.generic_visit(node)

        visitor = MemoryVisitor()
        visitor.visit(tree)

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 5))
        self.metrics['memory_usage'].extend(issues)
        return score

    def _analyze_key_selection(self, tree: ast.AST) -> float:
        """
        Analyze join key selection.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Key selection score (0-100)
        """
        issues = []

        class KeySelectionVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    method_name = node.func.attr
                    if method_name == 'merge':
                        # Check key selection
                        if self._has_multiple_keys(node):
                            if not self._has_sorted_data_hint(node):
                                issues.append(
                                    "Multiple join keys without sorted data hint"
                                )
                                
                self.generic_visit(node)

        visitor = KeySelectionVisitor()
        visitor.visit(tree)

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['key_selection'].extend(issues)
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
        
        # Add join operation issues
        if self.metrics['join_operations']:
            findings.extend(self.metrics['join_operations'][:3])
            
        # Add efficiency issues
        if self.metrics['join_efficiency']:
            findings.extend(self.metrics['join_efficiency'][:2])
            
        # Add memory issues
        if self.metrics['memory_usage']:
            findings.extend(self.metrics['memory_usage'][:2])
            
        return findings

    def _generate_suggestions(self) -> List[str]:
        """Generate improvement suggestions based on findings."""
        suggestions = []
        
        # Join operation suggestions
        if self.metrics['join_operations']:
            suggestions.append(
                f"Keep join chains under {self.MAX_JOIN_CHAIN} operations"
            )
            
        # Efficiency suggestions
        if self.metrics['join_efficiency']:
            suggestions.append(
                "Always specify join keys/indexes explicitly"
            )
            
        # Memory usage suggestions
        if self.metrics['memory_usage']:
            suggestions.append(
                "Consider using memory optimization techniques for large joins"
            )
            
        # Key selection suggestions
        if self.metrics['key_selection']:
            suggestions.append(
                "Sort data before joining on multiple keys"
            )
            
        return suggestions

    @staticmethod
    def _has_index_specification(node: ast.Call) -> bool:
        """Check if join operation specifies index or keys."""
        return any(
            kw.arg in {'on', 'left_on', 'right_on', 'left_index', 'right_index'}
            for kw in node.keywords
        )

    @staticmethod
    def _has_memory_optimization(node: ast.Call) -> bool:
        """Check if join operation includes memory optimization."""
        return any(
            kw.arg in {'copy', 'inplace'} and isinstance(kw.value, ast.Constant)
            for kw in node.keywords
        )

    @staticmethod
    def _has_multiple_keys(node: ast.Call) -> bool:
        """Check if join operation uses multiple keys."""
        for kw in node.keywords:
            if kw.arg == 'on' and isinstance(kw.value, (ast.List, ast.Tuple)):
                return len(kw.value.elts) > 1
        return False

    @staticmethod
    def _has_sorted_data_hint(node: ast.Call) -> bool:
        """Check if join operation includes sorted data hint."""
        return any(
            kw.arg == 'sort' and isinstance(kw.value, ast.Constant)
            for kw in node.keywords
        )
