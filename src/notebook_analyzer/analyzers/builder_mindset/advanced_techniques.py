"""
Advanced Techniques Analyzer Module.

This module analyzes the usage of advanced programming techniques in Jupyter notebook cells.
It evaluates comprehensions, generators, decorators, and other advanced Python features.

Created by: Barrhann
Date: 2025-02-17
Last Updated: 2025-02-17 00:46:09
"""

import ast
from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict
from ..base_analyzer import BaseAnalyzer, AnalysisError

class AdvancedTechniquesAnalyzer(BaseAnalyzer):
    """
    Analyzer for advanced Python programming techniques.
    
    This analyzer evaluates:
    - List/Dict/Set comprehensions
    - Generator expressions and functions
    - Decorator usage
    - Context managers
    - Lambda functions
    - Advanced built-ins (map, filter, reduce)
    - Type hints usage
    
    Attributes:
        ADVANCED_BUILTINS (Set[str]): Set of advanced Python built-in functions
        CONTEXT_MANAGERS (Set[str]): Common context manager patterns
        MIN_COMPREHENSION_LENGTH (int): Minimum length for comprehension benefit
    """

    ADVANCED_BUILTINS = {
        'map', 'filter', 'reduce', 'zip', 'enumerate',
        'any', 'all', 'iter', 'next', 'functools'
    }
    
    CONTEXT_MANAGERS = {
        'open', 'threading.Lock', 'asyncio.Lock',
        'tempfile.NamedTemporaryFile', 'contextlib.contextmanager'
    }
    
    MIN_COMPREHENSION_LENGTH = 3

    def __init__(self):
        """Initialize the advanced techniques analyzer."""
        super().__init__(name="Advanced Techniques")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'comprehensions': [],
            'generators': [],
            'decorators': [],
            'context_managers': [],
            'functional_features': [],
            'type_hints': []
        }
        self.advanced_feature_count = defaultdict(int)

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'builder_mindset'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze usage of advanced Python techniques.

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

            # Perform various technique analysis
            comprehension_score = self._analyze_comprehensions(tree)
            generator_score = self._analyze_generators(tree)
            decorator_score = self._analyze_decorators(tree)
            context_score = self._analyze_context_managers(tree)
            functional_score = self._analyze_functional_features(tree)
            type_score = self._analyze_type_hints(tree)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (comprehension_score, 0.25),  # 25% weight
                (generator_score, 0.20),      # 20% weight
                (decorator_score, 0.15),      # 15% weight
                (context_score, 0.15),        # 15% weight
                (functional_score, 0.15),     # 15% weight
                (type_score, 0.10)           # 10% weight
            ])

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(),
                'details': {
                    'comprehension_score': comprehension_score,
                    'generator_score': generator_score,
                    'decorator_score': decorator_score,
                    'context_manager_score': context_score,
                    'functional_score': functional_score,
                    'type_hints_score': type_score,
                    'metrics': self.metrics,
                    'feature_usage': dict(self.advanced_feature_count)
                },
                'suggestions': self._generate_suggestions()
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing advanced techniques: {str(e)}")

    def _analyze_comprehensions(self, tree: ast.AST) -> float:
        """
        Analyze usage of list/dict/set comprehensions.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Comprehension usage score (0-100)
        """
        opportunities = []
        used_comprehensions = []

        class ComprehensionVisitor(ast.NodeVisitor):
            def visit_ListComp(self, node):
                self.advanced_feature_count['list_comprehension'] += 1
                used_comprehensions.append(('list', node))
                self.generic_visit(node)

            def visit_DictComp(self, node):
                self.advanced_feature_count['dict_comprehension'] += 1
                used_comprehensions.append(('dict', node))
                self.generic_visit(node)

            def visit_SetComp(self, node):
                self.advanced_feature_count['set_comprehension'] += 1
                used_comprehensions.append(('set', node))
                self.generic_visit(node)

            def visit_For(self, node):
                # Check for potential comprehension opportunities
                if (len(node.body) == 1 and
                    isinstance(node.body[0], (ast.Append, ast.Assign))):
                    opportunities.append(
                        f"Loop at line {node.lineno} could be a comprehension"
                    )
                self.generic_visit(node)

        visitor = ComprehensionVisitor()
        visitor.visit(tree)

        # Calculate score based on opportunities taken vs. missed
        total = len(used_comprehensions) + len(opportunities)
        if total == 0:
            return 100.0
            
        score = (len(used_comprehensions) / total * 100) if total > 0 else 100
        self.metrics['comprehensions'].extend(opportunities)
        return score

    def _analyze_generators(self, tree: ast.AST) -> float:
        """
        Analyze generator usage.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Generator usage score (0-100)
        """
        issues = []

        class GeneratorVisitor(ast.NodeVisitor):
            def visit_GeneratorExp(self, node):
                self.advanced_feature_count['generator_expression'] += 1
                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                # Check for yield statements
                yields = [n for n in ast.walk(node) if isinstance(n, ast.Yield)]
                if yields:
                    self.advanced_feature_count['generator_function'] += 1
                self.generic_visit(node)

            def visit_For(self, node):
                # Check for list materialization that could use generators
                if isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name):
                        if node.iter.func.id == 'range':
                            issues.append(
                                f"Consider using generator instead of range at line {node.lineno}"
                            )
                self.generic_visit(node)

        visitor = GeneratorVisitor()
        visitor.visit(tree)

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['generators'].extend(issues)
        return score

    def _analyze_decorators(self, tree: ast.AST) -> float:
        """
        Analyze decorator usage.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Decorator usage score (0-100)
        """
        custom_decorators = set()
        used_decorators = []

        class DecoratorVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                if node.decorator_list:
                    self.advanced_feature_count['decorated_function'] += 1
                    used_decorators.extend(node.decorator_list)
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                if node.decorator_list:
                    self.advanced_feature_count['decorated_class'] += 1
                    used_decorators.extend(node.decorator_list)
                self.generic_visit(node)

        visitor = DecoratorVisitor()
        visitor.visit(tree)

        # Analyze decorator complexity and usage
        score = 100.0
        if used_decorators:
            # Check for custom decorator definitions
            for node in ast.walk(tree):
                if (isinstance(node, ast.FunctionDef) and
                    any('decorator' in node.name.lower() for name in node.name.split('_'))):
                    custom_decorators.add(node.name)
            
            # Adjust score based on decorator variety
            score = min(100.0, 60.0 + (len(custom_decorators) * 10))
            
        self.metrics['decorators'].append(
            f"Found {len(custom_decorators)} custom decorators"
        )
        return score

    def _analyze_context_managers(self, tree: ast.AST) -> float:
        """
        Analyze context manager usage.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Context manager usage score (0-100)
        """
        issues = []
        context_managers_used = set()

        class ContextManagerVisitor(ast.NodeVisitor):
            def visit_With(self, node):
                self.advanced_feature_count['with_statement'] += 1
                
                # Track context manager types
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call):
                        if isinstance(item.context_expr.func, ast.Name):
                            context_managers_used.add(item.context_expr.func.id)
                
                self.generic_visit(node)

            def visit_Call(self, node):
                # Check for resource management without context managers
                if isinstance(node.func, ast.Name):
                    if node.func.id == 'open':
                        if not isinstance(node.parent, ast.withitem):
                            issues.append(
                                f"File operation without context manager at line {node.lineno}"
                            )
                self.generic_visit(node)

        visitor = ContextManagerVisitor()
        visitor.visit(tree)

        # Calculate score
        if not issues and not context_managers_used:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 15))
        self.metrics['context_managers'].extend(issues)
        return score

    def _analyze_functional_features(self, tree: ast.AST) -> float:
        """
        Analyze functional programming feature usage.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Functional features score (0-100)
        """
        issues = []
        used_features = set()

        class FunctionalVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.ADVANCED_BUILTINS:
                        self.advanced_feature_count[f'builtin_{node.func.id}'] += 1
                        used_features.add(node.func.id)
                self.generic_visit(node)

            def visit_Lambda(self, node):
                self.advanced_feature_count['lambda'] += 1
                used_features.add('lambda')
                self.generic_visit(node)

        visitor = FunctionalVisitor()
        visitor.visit(tree)

        # Calculate score based on feature variety
        score = min(100.0, len(used_features) * 20)
        self.metrics['functional_features'].extend(
            [f"Used functional feature: {feature}" for feature in used_features]
        )
        return score

    def _analyze_type_hints(self, tree: ast.AST) -> float:
        """
        Analyze type hint usage.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Type hint usage score (0-100)
        """
        type_hints = 0
        total_annotations = 0

        class TypeHintVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                nonlocal type_hints, total_annotations
                
                # Check return type annotation
                if node.returns:
                    type_hints += 1
                total_annotations += 1
                
                # Check argument annotations
                for arg in node.args.args:
                    if arg.annotation:
                        type_hints += 1
                    total_annotations += 1
                
                self.generic_visit(node)

            def visit_AnnAssign(self, node):
                nonlocal type_hints, total_annotations
                if node.annotation:
                    type_hints += 1
                total_annotations += 1
                self.generic_visit(node)

        visitor = TypeHintVisitor()
        visitor.visit(tree)

        # Calculate score
        if total_annotations == 0:
            return 100.0
            
        score = (type_hints / total_annotations * 100) if total_annotations > 0 else 100
        self.metrics['type_hints'].append(
            f"Type hints usage: {type_hints}/{total_annotations}"
        )
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
        
        # Add comprehension opportunities
        if self.metrics['comprehensions']:
            findings.extend(self.metrics['comprehensions'][:2])
            
        # Add generator suggestions
        if self.metrics['generators']:
            findings.extend(self.metrics['generators'][:2])
            
        # Add context manager issues
        if self.metrics['context_managers']:
            findings.extend(self.metrics['context_managers'][:2])
            
        return findings
        
    def _generate_suggestions(self) -> List[str]:
        """Generate improvement suggestions based on findings."""
        suggestions = []
        
        # Comprehension suggestions
        if self.metrics['comprehensions']:
            suggestions.append(
                "Consider using list comprehensions for simple loops"
            )
            
        # Generator suggestions
        if self.metrics['generators']:
            suggestions.append(
                "Use generators for memory-efficient iteration"
            )
            
        # Decorator suggestions
        if self.metrics['decorators']:
            suggestions.append(
                "Consider using decorators for cross-cutting concerns"
            )
            
        # Context manager suggestions
        if self.metrics['context_managers']:
            suggestions.append(
                "Use context managers for resource management"
            )
            
        # Functional feature suggestions
        if len(self.advanced_feature_count) < len(self.ADVANCED_BUILTINS) / 2:
            suggestions.append(
                "Explore functional programming features like map, filter, and reduce"
            )
            
        # Type hint suggestions
        if 'type_hints' in self.metrics and self.metrics['type_hints']:
            suggestions.append(
                "Add type hints to improve code maintainability and IDE support"
            )
            
        return suggestions

    def __str__(self) -> str:
        """Return string representation of the analyzer."""
        return f"Advanced Techniques Analyzer (Features detected: {len(self.advanced_feature_count)})"

    def __repr__(self) -> str:
        """Return detailed string representation of the analyzer."""
        return (f"{self.__class__.__name__}("
                f"features={len(self.advanced_feature_count)}, "
                f"active={self.is_active})")

    @staticmethod
    def get_feature_description(feature_name: str) -> str:
        """
        Get description of an advanced feature.

        Args:
            feature_name (str): Name of the feature

        Returns:
            str: Description of the feature
        """
        descriptions = {
            'list_comprehension': 'Concise way to create lists',
            'dict_comprehension': 'Concise way to create dictionaries',
            'set_comprehension': 'Concise way to create sets',
            'generator_expression': 'Memory-efficient iteration',
            'generator_function': 'Function that yields values',
            'decorated_function': 'Function with added functionality via decorators',
            'decorated_class': 'Class with added functionality via decorators',
            'with_statement': 'Context manager for resource handling',
            'lambda': 'Anonymous function',
            'builtin_map': 'Apply function to iterable',
            'builtin_filter': 'Filter iterable based on function',
            'builtin_reduce': 'Reduce iterable to single value',
            'builtin_zip': 'Combine multiple iterables',
            'builtin_enumerate': 'Iterate with index',
            'builtin_any': 'Check if any item is True',
            'builtin_all': 'Check if all items are True',
            'builtin_iter': 'Create iterator from iterable',
            'builtin_next': 'Get next item from iterator',
            'builtin_functools': 'Functional programming tools'
        }
        return descriptions.get(feature_name, 'Advanced Python feature')

    def get_feature_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed statistics about feature usage.

        Returns:
            Dict[str, Dict[str, Any]]: Statistics about each feature including:
                - count: Number of times used
                - description: Feature description
                - category: Feature category
        """
        stats = {}
        for feature, count in self.advanced_feature_count.items():
            category = feature.split('_')[0] if '_' in feature else 'other'
            stats[feature] = {
                'count': count,
                'description': self.get_feature_description(feature),
                'category': category
            }
        return stats
