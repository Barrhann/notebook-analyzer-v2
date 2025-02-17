"""
Code Reusability Analyzer Module.

This module analyzes code reusability and modularity in Jupyter notebook cells.
It evaluates function abstraction, code duplication, and potential for reuse.

Created by: Barrhann
Date: 2025-02-17
Last Updated: 2025-02-17 00:43:51
"""

import ast
from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict
import re
from dataclasses import dataclass
from ..base_analyzer import BaseAnalyzer, AnalysisError

@dataclass
class CodeBlock:
    """Represents a block of code for similarity comparison."""
    content: str
    start_line: int
    end_line: int
    complexity: int

class CodeReusabilityAnalyzer(BaseAnalyzer):
    """
    Analyzer for code reusability and modularity metrics.
    
    This analyzer evaluates:
    - Function abstraction levels
    - Code duplication patterns
    - Potential for modularization
    - Variable and function reuse
    - Code block similarity
    
    Attributes:
        MIN_BLOCK_SIZE (int): Minimum size for considering code blocks
        MAX_FUNCTION_SIZE (int): Maximum recommended function size
        SIMILARITY_THRESHOLD (float): Threshold for code similarity detection
    """

    MIN_BLOCK_SIZE = 4
    MAX_FUNCTION_SIZE = 30
    SIMILARITY_THRESHOLD = 0.8

    def __init__(self):
        """Initialize the code reusability analyzer."""
        super().__init__(name="Code Reusability")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'abstraction_levels': [],
            'duplicated_code': [],
            'modularization': [],
            'reuse_patterns': [],
            'complexity': []
        }
        self.code_blocks = []
        self.function_calls = defaultdict(int)

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'builder_mindset'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze code reusability and modularity.

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

            # Perform various reusability checks
            abstraction_score = self._analyze_abstraction_levels(tree)
            duplication_score = self._analyze_code_duplication(code)
            modular_score = self._analyze_modularization(tree)
            reuse_score = self._analyze_reuse_patterns(tree)
            complexity_score = self._analyze_complexity(tree)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (abstraction_score, 0.25),   # 25% weight
                (duplication_score, 0.25),   # 25% weight
                (modular_score, 0.20),       # 20% weight
                (reuse_score, 0.15),         # 15% weight
                (complexity_score, 0.15)      # 15% weight
            ])

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(),
                'details': {
                    'abstraction_score': abstraction_score,
                    'duplication_score': duplication_score,
                    'modularization_score': modular_score,
                    'reuse_score': reuse_score,
                    'complexity_score': complexity_score,
                    'metrics': self.metrics
                },
                'suggestions': self._generate_suggestions()
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing code reusability: {str(e)}")

    def _analyze_abstraction_levels(self, tree: ast.AST) -> float:
        """
        Analyze function abstraction levels.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Abstraction level score (0-100)
        """
        issues = []
        function_depths = []

        class AbstractionVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_depth = 0

            def visit_FunctionDef(self, node):
                self.current_depth += 1
                function_depths.append(self.current_depth)
                
                # Check function complexity
                if len(node.body) > self.MAX_FUNCTION_SIZE:
                    issues.append(
                        f"Function '{node.name}' is too large ({len(node.body)} lines)"
                    )
                
                # Check abstraction level
                if self.current_depth > 3:
                    issues.append(
                        f"Function '{node.name}' has deep nesting (level {self.current_depth})"
                    )
                
                self.generic_visit(node)
                self.current_depth -= 1

        visitor = AbstractionVisitor()
        visitor.visit(tree)

        # Calculate score based on issues and depth distribution
        if not function_depths:
            return 100.0  # No functions to analyze
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['abstraction_levels'].extend(issues)
        return score

    def _analyze_code_duplication(self, code: str) -> float:
        """
        Analyze code for duplication patterns.

        Args:
            code (str): Code to analyze

        Returns:
            float: Duplication score (0-100)
        """
        issues = []
        
        # Split code into blocks
        lines = code.splitlines()
        blocks: List[CodeBlock] = []
        
        current_block = []
        for i, line in enumerate(lines):
            if line.strip():
                current_block.append(line)
            elif len(current_block) >= self.MIN_BLOCK_SIZE:
                blocks.append(CodeBlock(
                    content='\n'.join(current_block),
                    start_line=i - len(current_block),
                    end_line=i,
                    complexity=self._calculate_block_complexity('\n'.join(current_block))
                ))
                current_block = []

        # Check for similar blocks
        for i, block1 in enumerate(blocks):
            for block2 in blocks[i+1:]:
                similarity = self._calculate_similarity(block1.content, block2.content)
                if similarity > self.SIMILARITY_THRESHOLD:
                    issues.append(
                        f"Similar code blocks found at lines {block1.start_line}-{block1.end_line} "
                        f"and {block2.start_line}-{block2.end_line}"
                    )

        # Calculate score
        if not blocks:
            return 100.0  # No blocks to analyze
            
        score = max(0, 100 - (len(issues) * 15))
        self.metrics['duplicated_code'].extend(issues)
        return score

    def _analyze_modularization(self, tree: ast.AST) -> float:
        """
        Analyze code modularization opportunities.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Modularization score (0-100)
        """
        issues = []

        class ModularizationVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # Check for complex loop bodies
                if len(node.body) > 5:
                    issues.append(
                        f"Complex loop body at line {node.lineno} - consider extracting to function"
                    )
                self.generic_visit(node)

            def visit_If(self, node):
                # Check for complex conditional blocks
                if len(node.body) > 5 or (hasattr(node, 'orelse') and len(node.orelse) > 5):
                    issues.append(
                        f"Complex conditional block at line {node.lineno} - consider extracting to function"
                    )
                self.generic_visit(node)

        visitor = ModularizationVisitor()
        visitor.visit(tree)

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['modularization'].extend(issues)
        return score

    def _analyze_reuse_patterns(self, tree: ast.AST) -> float:
        """
        Analyze code reuse patterns.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Reuse pattern score (0-100)
        """
        issues = []

        class ReuseVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    self.function_calls[node.func.id] += 1
                self.generic_visit(node)

        visitor = ReuseVisitor()
        visitor.visit(tree)

        # Analyze function call patterns
        for func_name, call_count in self.function_calls.items():
            if call_count == 1:
                issues.append(f"Function '{func_name}' is only used once")
            elif call_count > 5:
                issues.append(f"Function '{func_name}' is used {call_count} times - consider utility module")

        # Calculate score
        if not self.function_calls:
            return 100.0  # No functions to analyze
            
        score = max(0, 100 - (len(issues) * 5))
        self.metrics['reuse_patterns'].extend(issues)
        return score

    def _analyze_complexity(self, tree: ast.AST) -> float:
        """
        Analyze code complexity.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Complexity score (0-100)
        """
        issues = []
        complexity_scores = []

        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0

            def visit_FunctionDef(self, node):
                local_complexity = self._calculate_function_complexity(node)
                complexity_scores.append(local_complexity)
                
                if local_complexity > 10:
                    issues.append(
                        f"Function '{node.name}' has high complexity ({local_complexity})"
                    )
                
                self.generic_visit(node)

            def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
                """Calculate cyclomatic complexity of a function."""
                complexity = 1  # Base complexity
                
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                        
                return complexity

        visitor = ComplexityVisitor()
        visitor.visit(tree)

        # Calculate score
        if not complexity_scores:
            return 100.0  # No functions to analyze
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['complexity'].extend(issues)
        return score

    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity ratio between two text blocks."""
        import difflib
        return difflib.SequenceMatcher(None, text1, text2).ratio()

    @staticmethod
    def _calculate_block_complexity(code: str) -> int:
        """Calculate complexity of a code block."""
        try:
            tree = ast.parse(code)
            complexity = 1
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For)):
                    complexity += 1
                    
            return complexity
        except:
            return 1

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
        
        # Add abstraction level issues
        if self.metrics['abstraction_levels']:
            findings.extend(self.metrics['abstraction_levels'][:2])
            
        # Add code duplication issues
        if self.metrics['duplicated_code']:
            findings.extend(self.metrics['duplicated_code'][:2])
            
        # Add modularization opportunities
        if self.metrics['modularization']:
            findings.extend(self.metrics['modularization'][:2])
            
        return findings

    def _generate_suggestions(self) -> List[str]:
        """Generate improvement suggestions based on findings."""
        suggestions = []
        
        # Abstraction suggestions
        if self.metrics['abstraction_levels']:
            suggestions.append(
                f"Keep functions under {self.MAX_FUNCTION_SIZE} lines"
            )
            
        # Duplication suggestions
        if self.metrics['duplicated_code']:
            suggestions.append(
                "Extract duplicated code into reusable functions"
            )
            
        # Modularization suggestions
        if self.metrics['modularization']:
            suggestions.append(
                "Break down complex code blocks into smaller functions"
            )
            
        # Complexity suggestions
        if self.metrics['complexity']:
            suggestions.append(
                "Reduce function complexity by extracting logic into helper functions"
            )
            
        return suggestions
