"""
Code Structure Analyzer Module.

This module analyzes the structural quality of code in Jupyter notebook cells.
It evaluates class/function organization, code modularity, and structural patterns.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 23:39:04
"""

import ast
from typing import Dict, Any, List, Tuple, Set, Optional
from collections import defaultdict
from ..base_analyzer import BaseAnalyzer, AnalysisError


class ParentNodeVisitor(ast.NodeVisitor):
    """Base visitor that tracks parent nodes."""
    
    def visit(self, node):
        """Visit a node and set its parent."""
        if hasattr(node, 'parent'):
            return super().visit(node)
        for child in ast.iter_child_nodes(node):
            child.parent = node
        return super().visit(node)


class ClassVisitor(ParentNodeVisitor):
    """Visitor for analyzing class structure."""
    
    def __init__(self, max_methods: int, min_methods: int):
        """
        Initialize class visitor.

        Args:
            max_methods (int): Maximum allowed methods per class
            min_methods (int): Minimum recommended methods per class
        """
        self.class_count = 0
        self.class_methods = defaultdict(list)
        self.issues = []
        self.max_methods = max_methods
        self.min_methods = min_methods

    def visit_ClassDef(self, node: ast.ClassDef):
        """
        Visit a class definition node.

        Args:
            node (ast.ClassDef): The class definition node to visit
        """
        self.class_count += 1
        
        # Check inheritance structure
        if len(node.bases) > 3:
            self.issues.append(f"Class '{node.name}' has too many base classes")
        
        # Analyze methods
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        self.class_methods[node.name].extend(methods)
        
        if len(methods) > self.max_methods:
            self.issues.append(
                f"Class '{node.name}' has too many methods ({len(methods)})"
            )
        elif len(methods) < self.min_methods:
            self.issues.append(
                f"Class '{node.name}' might be too small ({len(methods)} methods)"
            )
        
        self.generic_visit(node)


class FunctionVisitor(ParentNodeVisitor):
    """Visitor for analyzing function structure."""
    
    def __init__(self, max_params: int):
        """
        Initialize function visitor.

        Args:
            max_params (int): Maximum allowed parameters per function
        """
        self.function_count = 0
        self.issues = []
        self.max_params = max_params

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Visit a function definition node.

        Args:
            node (ast.FunctionDef): The function definition node to visit
        """
        self.function_count += 1
        
        # Check parameter count
        if len(node.args.args) > self.max_params:
            self.issues.append(
                f"Function '{node.name}' has too many parameters "
                f"({len(node.args.args)})"
            )
        
        # Check return statement presence
        returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
        if not returns and not node.name.startswith('__'):
            self.issues.append(
                f"Function '{node.name}' lacks explicit return statement"
            )
        
        self.generic_visit(node)


class ImportVisitor(ParentNodeVisitor):
    """Visitor for analyzing import structure."""
    
    def __init__(self):
        """Initialize import visitor."""
        self.import_lines = []

    def visit_Import(self, node: ast.Import):
        """
        Visit an import node.

        Args:
            node (ast.Import): The import node to visit
        """
        self.import_lines.append(node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """
        Visit an import from node.

        Args:
            node (ast.ImportFrom): The import from node to visit
        """
        self.import_lines.append(node.lineno)
        self.generic_visit(node)


class ScopeVisitor(ParentNodeVisitor):
    """Visitor for analyzing scope usage."""
    
    def __init__(self):
        """Initialize scope visitor."""
        self.global_vars = set()
        self.local_vars = set()

    def visit_Global(self, node: ast.Global):
        """
        Visit a global statement node.

        Args:
            node (ast.Global): The global statement node to visit
        """
        self.global_vars.update(node.names)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        """
        Visit a name node.

        Args:
            node (ast.Name): The name node to visit
        """
        if isinstance(node.ctx, ast.Store):
            if not isinstance(getattr(node, 'parent', None), (ast.ClassDef, ast.FunctionDef)):
                self.local_vars.add(node.id)
        self.generic_visit(node)


class DependencyVisitor(ParentNodeVisitor):
    """Visitor for analyzing code dependencies."""
    
    def __init__(self):
        """Initialize dependency visitor."""
        self.dependency_graph = defaultdict(set)

    def visit_ClassDef(self, node: ast.ClassDef):
        """
        Visit a class definition node.

        Args:
            node (ast.ClassDef): The class definition node to visit
        """
        # Track class dependencies
        for base in node.bases:
            if isinstance(base, ast.Name):
                self.dependency_graph[node.name].add(base.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Visit a function definition node.

        Args:
            node (ast.FunctionDef): The function definition node to visit
        """
        # Track function dependencies
        calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)]
        for call in calls:
            if isinstance(call.func, ast.Name):
                self.dependency_graph[node.name].add(call.func.id)
        self.generic_visit(node)


class CodeStructureAnalyzer(BaseAnalyzer):
    """
    Analyzer for code structure and organization metrics.
    
    This analyzer evaluates:
    - Class structure and inheritance
    - Function organization and dependencies
    - Code modularity
    - Import organization
    - Global vs. local scope usage
    - Code block organization
    
    Attributes:
        MAX_CLASS_METHODS (int): Maximum recommended methods per class
        MAX_METHOD_PARAMS (int): Maximum recommended parameters per method
        MIN_CLASS_METHODS (int): Minimum recommended methods for a class
    """

    MAX_CLASS_METHODS = 10
    MAX_METHOD_PARAMS = 5
    MIN_CLASS_METHODS = 2

    def __init__(self):
        """Initialize the code structure analyzer."""
        super().__init__(name="Code Structure")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'class_structure': [],
            'function_organization': [],
            'import_structure': [],
            'scope_usage': [],
            'dependencies': []
        }
        self.class_count = 0
        self.function_count = 0
        self.dependency_graph = defaultdict(set)

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'builder_mindset'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze code structure and organization.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing:
                - score: Overall structure score (0-100)
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

            # Perform various structural checks
            class_score = self._analyze_class_structure(tree)
            function_score = self._analyze_function_organization(tree)
            import_score = self._analyze_import_structure(tree)
            scope_score = self._analyze_scope_usage(tree)
            dependency_score = self._analyze_dependencies(tree)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (class_score, 0.30),      # 30% weight
                (function_score, 0.25),   # 25% weight
                (import_score, 0.20),     # 20% weight
                (scope_score, 0.15),      # 15% weight
                (dependency_score, 0.10)  # 10% weight
            ])

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(),
                'details': {
                    'class_structure_score': class_score,
                    'function_organization_score': function_score,
                    'import_structure_score': import_score,
                    'scope_usage_score': scope_score,
                    'dependency_score': dependency_score,
                    'metrics': self.metrics,
                    'stats': {
                        'class_count': self.class_count,
                        'function_count': self.function_count,
                        'dependency_count': len(self.dependency_graph)
                    }
                },
                'suggestions': self._generate_suggestions()
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing code structure: {str(e)}")

    def _analyze_class_structure(self, tree: ast.AST) -> float:
        """
        Analyze class structure and organization.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Class structure score (0-100)
        """
        visitor = ClassVisitor(self.MAX_CLASS_METHODS, self.MIN_CLASS_METHODS)
        visitor.visit(tree)
        
        self.class_count = visitor.class_count
        
        if self.class_count == 0:
            return 100.0
            
        score = max(0, 100 - (len(visitor.issues) * 10))
        self.metrics['class_structure'].extend(visitor.issues)
        return score

    def _analyze_function_organization(self, tree: ast.AST) -> float:
        """
        Analyze function organization and complexity.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Function organization score (0-100)
        """
        visitor = FunctionVisitor(self.MAX_METHOD_PARAMS)
        visitor.visit(tree)
        
        self.function_count = visitor.function_count
        
        if self.function_count == 0:
            return 100.0
            
        score = max(0, 100 - (len(visitor.issues) * 5))
        self.metrics['function_organization'].extend(visitor.issues)
        return score

    def _analyze_import_structure(self, tree: ast.AST) -> float:
        """
        Analyze import statement organization.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Import structure score (0-100)
        """
        visitor = ImportVisitor()
        visitor.visit(tree)
        
        issues = []
        if visitor.import_lines:
            if max(visitor.import_lines) - min(visitor.import_lines) > 5:
                issues.append("Imports are not properly grouped together")
            
            if max(visitor.import_lines) > 20:
                issues.append("Imports appear too late in the code")
            
        if not visitor.import_lines:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 15))
        self.metrics['import_structure'].extend(issues)
        return score

    def _analyze_scope_usage(self, tree: ast.AST) -> float:
        """
        Analyze usage of global vs. local scope.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Scope usage score (0-100)
        """
        visitor = ScopeVisitor()
        visitor.visit(tree)
        
        issues = []
        if len(visitor.global_vars) > 0:
            issues.append(f"Found {len(visitor.global_vars)} global variables - consider refactoring")
        
        if len(visitor.local_vars) > 5:
            issues.append(f"Too many module-level variables ({len(visitor.local_vars)})")
        
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['scope_usage'].extend(issues)
        return score

    def _analyze_dependencies(self, tree: ast.AST) -> float:
        """
        Analyze code dependencies and coupling.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Dependency score (0-100)
        """
        visitor = DependencyVisitor()
        visitor.visit(tree)
        
        issues = []
        for name, deps in visitor.dependency_graph.items():
            if len(deps) > 5:
                issues.append(f"'{name}' has too many dependencies ({len(deps)})")
        
        if not visitor.dependency_graph:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.dependency_graph = visitor.dependency_graph
        self.metrics['dependencies'].extend(issues)
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
        """
        Generate list of significant findings.

        Returns:
            List[str]: List of significant findings from the analysis
        """
        findings = []
        
        # Add class structure issues
        if self.metrics['class_structure']:
            findings.extend(self.metrics['class_structure'][:3])
            
        # Add function organization issues
        if self.metrics['function_organization']:
            findings.extend(self.metrics['function_organization'][:3])
            
        # Add import structure issues
        if self.metrics['import_structure']:
            findings.extend(self.metrics['import_structure'][:2])
            
        return findings
        
    def _generate_suggestions(self) -> List[str]:
        """
        Generate improvement suggestions based on findings.

        Returns:
            List[str]: List of improvement suggestions based on analysis findings
        """
        suggestions = []
        
        # Class structure suggestions
        if self.metrics['class_structure']:
            suggestions.append(
                f"Keep classes focused with {self.MIN_CLASS_METHODS}-{self.MAX_CLASS_METHODS} methods"
            )
            suggestions.append(
                "Consider splitting large classes into smaller, more focused ones"
            )
            
        # Function organization suggestions
        if self.metrics['function_organization']:
            suggestions.append(
                f"Limit function parameters to {self.MAX_METHOD_PARAMS} or fewer"
            )
            suggestions.append(
                "Ensure functions have explicit return statements where appropriate"
            )
            
        # Import structure suggestions
        if self.metrics['import_structure']:
            suggestions.append(
                "Group all imports at the beginning of the file"
            )
            suggestions.append(
                "Organize imports by standard library, third-party, and local modules"
            )
            
        # Scope suggestions
        if self.metrics['scope_usage']:
            suggestions.append(
                "Minimize use of global variables and module-level state"
            )
            suggestions.append(
                "Consider using class attributes or function parameters instead of globals"
            )
            
        # Dependency suggestions
        if self.metrics['dependencies']:
            suggestions.append(
                "Reduce coupling between components by minimizing dependencies"
            )
            suggestions.append(
                "Consider using dependency injection or composition patterns"
            )
            
        return suggestions

    def __str__(self) -> str:
        """Return string representation of the analyzer."""
        return (f"Code Structure Analyzer (Classes: {self.class_count}, "
                f"Functions: {self.function_count})")

    def __repr__(self) -> str:
        """Return detailed string representation of the analyzer."""
        return (f"CodeStructureAnalyzer(classes={self.class_count}, "
                f"functions={self.function_count}, "
                f"dependencies={len(self.dependency_graph)})")
