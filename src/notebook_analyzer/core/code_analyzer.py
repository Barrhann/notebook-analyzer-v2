"""
Code Analyzer module - Analyzes Python code in notebook cells
"""

import ast
from typing import Dict, Any, List
import re
from collections import defaultdict

class CodeAnalyzer:
    def __init__(self):
        self.complexity_indicators = {
            'loops': ['for', 'while'],
            'conditionals': ['if', 'elif', 'else'],
            'comprehensions': ['for', 'if'],
            'try_except': ['try', 'except', 'finally']
        }

    def analyze_code(self, code: str, cell_number: int = 0) -> Dict[str, Any]:
        """
        Analyze Python code from notebook cells.
        
        Args:
            code: String containing Python code from notebook cell
            cell_number: Current cell number for execution order analysis
            
        Returns:
            Dict containing analysis results including:
            - function definitions
            - complexity metrics
            - style metrics
            - comment analysis
            - conciseness metrics
            - structure metrics
        """
        try:
            tree = ast.parse(code)
            
            return {
                'functions': self.analyze_functions(code),
                'complexity': self.analyze_complexity(code),
                'style': self.analyze_style(code),
                'comments': self.analyze_comments(code),
                'conciseness': self.analyze_conciseness(code),
                'structure': self.analyze_structure(code, cell_number)  # Added this line
            }
        except SyntaxError:
            # Handle invalid Python code
            return {
                'functions': {'function_count': 0, 'docstring_count': 0, 'functions': []},
                'complexity': {'complex_lines': 0, 'total_lines': 0},
                'style': {'violations': []},
                'comments': {'inline_comments': 0, 'total_lines': 0},
                'conciseness': {
                    'duplicates': {'count': 0, 'instances': []},
                    'dead_code': {'unused_vars': [], 'unused_functions': [], 'unreachable': []},
                    'function_lengths': {'average_length': 0, 'functions': []},
                    'variable_usage': {'declared': 0, 'used': 0, 'efficiency': 100}
                },
                'structure': {  
                    'metrics': {
                        'cyclomatic_complexity': {'total': 0, 'per_function': {}, 'average': 0},
                        'function_dependencies': {'dependencies': {}, 'modularity_score': 100, 'circular_dependencies': []},
                        'global_variables': {'count': 0, 'names': [], 'usage_count': {}},
                        'execution_order': {'issues': [], 'score': 100, 'undefined_references': []}
                    }
                }
            }

    def analyze_functions(self, code: str) -> Dict[str, Any]:
        """
        Analyze user-defined functions in the code.
        Looks for 'def' statements that define new functions.
        
        Args:
            code: String containing Python code
            
        Returns:
            Dict containing:
            - function_count: Number of functions defined
            - docstring_count: Number of functions with docstrings
            - functions: List of function details
        """
        function_defs = []
        try:
            tree = ast.parse(code)
            
            class FunctionVisitor(ast.NodeVisitor):
                def visit_FunctionDef(self, node):
                    """Visit function definitions."""
                    # Get the docstring if it exists
                    docstring = ast.get_docstring(node)
                    function_defs.append({
                        'name': node.name,
                        'has_docstring': bool(docstring),
                        'lineno': node.lineno,
                        'end_lineno': getattr(node, 'end_lineno', node.lineno),
                        'args': len(node.args.args)
                    })
                    # Continue visiting child nodes
                    self.generic_visit(node)
            
            # Visit all nodes in the AST
            visitor = FunctionVisitor()
            visitor.visit(tree)
            
        except SyntaxError:
            # Handle invalid Python code
            return {
                'function_count': 0,
                'docstring_count': 0,
                'functions': []
            }
            
        return {
            'function_count': len(function_defs),
            'docstring_count': sum(1 for f in function_defs if f['has_docstring']),
            'functions': function_defs
        }

    def analyze_complexity(self, code: str) -> Dict[str, Any]:
        """
        Analyze code complexity by looking for:
        - Nested loops
        - Multiple conditionals
        - List/dict comprehensions
        - Try-except blocks
        
        Args:
            code: String containing Python code
            
        Returns:
            Dict containing complexity metrics
        """
        complex_lines = 0
        total_lines = len(code.splitlines())
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Check for nested structures
                if isinstance(node, (ast.For, ast.While)):
                    # Count nested loops
                    if any(isinstance(child, (ast.For, ast.While)) for child in ast.walk(node)):
                        complex_lines += 1
                        
                elif isinstance(node, ast.If):
                    # Count multiple conditions
                    if isinstance(node.test, ast.BoolOp):
                        complex_lines += 1
                        
                elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                    # Count complex comprehensions
                    if len([g for g in node.generators if g.ifs]) > 1:
                        complex_lines += 1
                        
                elif isinstance(node, ast.Try):
                    # Count try blocks with multiple except clauses
                    if len(node.handlers) > 1:
                        complex_lines += 1
        
        except SyntaxError:
            return {'complex_lines': 0, 'total_lines': total_lines}
            
        return {
            'complex_lines': complex_lines,
            'total_lines': total_lines,
            'complexity_percentage': (complex_lines / total_lines * 100) if total_lines > 0 else 0
        }

    def analyze_style(self, code: str) -> Dict[str, Any]:
        """
        Analyze code style issues including:
        - Line length
        - Indentation
        - Whitespace
        - Blank lines
        
        Args:
            code: String containing Python code
            
        Returns:
            Dict containing style violation metrics
        """
        violations = []
        lines = code.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check line length (PEP 8: 79 characters)
            if len(line.rstrip()) > 79:
                violations.append({
                    'type': 'E5',
                    'line': i,
                    'message': 'Line too long'
                })
                
            # Check indentation (must be multiple of 4)
            leading_spaces = len(line) - len(line.lstrip())
            if line.strip() and leading_spaces % 4 != 0:
                violations.append({
                    'type': 'E1',
                    'line': i,
                    'message': 'Indentation not a multiple of 4'
                })
                
        return {
            'violations': violations,
            'violation_count': len(violations)
        }

    def analyze_comments(self, code: str) -> Dict[str, Any]:
        """
        Analyze code comments including:
        - Inline comments
        - Docstrings
        - Comment to code ratio
        - Redundant comments detection
        
        Args:
            code: String containing Python code
            
        Returns:
            Dict containing comment metrics
        """
        lines = code.splitlines()
        inline_comments = 0
        redundant_comments = []
        total_lines = len(lines)
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            code_part = stripped
            comment_part = ""
            
            # Extract comment if exists
            if '#' in stripped:
                if stripped.startswith('#'):
                    inline_comments += 1
                    code_part = ""
                    comment_part = stripped[1:].strip()
                else:
                    # Handle inline comment
                    inline_comments += 1
                    parts = stripped.split('#')
                    code_part = parts[0].strip()
                    comment_part = parts[1].strip()
                    
                    # Check for redundant comments
                    if comment_part and code_part:
                        is_redundant = self._is_redundant_comment(code_part, comment_part)
                        if is_redundant:
                            redundant_comments.append({
                                'line': i,
                                'code': code_part,
                                'comment': comment_part
                            })
                
        return {
            'inline_comments': inline_comments,
            'total_lines': total_lines,
            'comment_ratio': (inline_comments / total_lines) if total_lines > 0 else 0,
            'redundant_comments': redundant_comments,
            'redundant_count': len(redundant_comments)
        }
        
    def analyze_conciseness(self, code: str) -> Dict[str, Any]:
        """
        Analyze code conciseness including duplicates, dead code, function length,
        and variable usage efficiency.
        """
        try:
            tree = ast.parse(code)
            
            class VariableVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.declared_vars = set()
                    self.used_vars = set()
                    self.assigned_vars = set()
                    self.function_calls = set()
                    self.defined_functions = set()
                    self.current_scope = []
                    
                def visit_Name(self, node):
                    """Track variable usage."""
                    if isinstance(node.ctx, ast.Store):
                        self.declared_vars.add(node.id)
                        if self.current_scope:
                            self.assigned_vars.add(node.id)
                    elif isinstance(node.ctx, ast.Load):
                        self.used_vars.add(node.id)
                    self.generic_visit(node)
                    
                def visit_FunctionDef(self, node):
                    """Track function definitions and create new scope."""
                    self.defined_functions.add(node.name)
                    self.current_scope.append(node.name)
                    # Add function parameters as declared variables
                    for arg in node.args.args:
                        self.declared_vars.add(arg.arg)
                        self.assigned_vars.add(arg.arg)
                    self.generic_visit(node)
                    self.current_scope.pop()
                    
                def visit_Call(self, node):
                    """Track function calls."""
                    if isinstance(node.func, ast.Name):
                        self.function_calls.add(node.func.id)
                    self.generic_visit(node)
            
            visitor = VariableVisitor()
            visitor.visit(tree)
            
            # Calculate metrics
            declared_count = len(visitor.declared_vars)
            used_count = len(visitor.used_vars)
            unused_vars = visitor.declared_vars - visitor.used_vars
            unused_functions = visitor.defined_functions - visitor.function_calls
            
            # Get function lengths
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    length = getattr(node, 'end_lineno', node.lineno) - node.lineno + 1
                    functions.append({
                        'name': node.name,
                        'length': length,
                        'start_line': node.lineno,
                        'end_line': getattr(node, 'end_lineno', node.lineno)
                    })
            
            return {
                'metrics': {
                    'duplicates': self._find_duplicate_code(tree),
                    'dead_code': {
                        'unused_vars': list(unused_vars),
                        'unused_functions': list(unused_functions),
                        'unreachable': self._find_unreachable_code(tree)
                    },
                    'function_lengths': {
                        'average_length': sum(f['length'] for f in functions) / len(functions) if functions else 0,
                        'functions': functions
                    },
                    'variable_usage': {
                        'declared': declared_count,
                        'used': used_count,
                        'efficiency': (used_count / declared_count * 100) if declared_count > 0 else 100
                    }
                }
            }
            
        except SyntaxError:
            return {
                'metrics': {
                    'duplicates': {'count': 0, 'instances': []},
                    'dead_code': {'unused_vars': [], 'unused_functions': [], 'unreachable': []},
                    'function_lengths': {'average_length': 0, 'functions': []},
                    'variable_usage': {'declared': 0, 'used': 0, 'efficiency': 100}
                }
            }
            
    def analyze_structure(self, code: str, cell_number: int = 0) -> Dict[str, Any]:
        """
        Analyze code structure including cyclomatic complexity, dependencies,
        execution order, and global variable usage.
        
        Args:
            code: String containing Python code
            cell_number: Current cell number for execution order analysis
            
        Returns:
            Dict containing structure metrics
        """
        try:
            tree = ast.parse(code)
            
            # Analyze cyclomatic complexity
            complexity = self._analyze_cyclomatic_complexity(tree)
            
            # Analyze function dependencies
            dependencies = self._analyze_function_dependencies(tree)
            
            # Analyze global variables
            globals_analysis = self._analyze_global_variables(tree)
            
            # Analyze execution order
            execution = self._analyze_execution_order(tree, cell_number)
            
            return {
                'metrics': {
                    'cyclomatic_complexity': complexity,
                    'function_dependencies': dependencies,
                    'global_variables': globals_analysis,
                    'execution_order': execution
                }
            }
        except SyntaxError:
            return {
                'metrics': {
                    'cyclomatic_complexity': {'total': 0, 'per_function': {}},
                    'function_dependencies': {'dependencies': {}, 'modularity_score': 100},
                    'global_variables': {'count': 0, 'names': [], 'usage_count': {}},
                    'execution_order': {'issues': [], 'score': 100}
                }
            }
            
    def analyze_dataset_joins(self, code: str) -> Dict[str, Any]:
        """
        Analyze dataset join operations in the code.
        
        Args:
            code: String containing Python code
            
        Returns:
            Dict containing join analysis metrics
        """
        try:
            tree = ast.parse(code)
            
            # Analyze joins
            join_analysis = self._analyze_join_methods(tree)
            key_analysis = self._analyze_join_keys(tree)
            efficiency_analysis = self._analyze_join_efficiency(tree)
            modularity_analysis = self._analyze_join_modularity(tree)
            
            return {
                'metrics': {
                    'join_methods': join_analysis,
                    'key_handling': key_analysis,
                    'efficiency': efficiency_analysis,
                    'modularity': modularity_analysis
                }
            }
        except SyntaxError:
            return {
                'metrics': {
                    'join_methods': {'methods': [], 'consistency_score': 100},
                    'key_handling': {'issues': [], 'score': 100},
                    'efficiency': {'issues': [], 'score': 100},
                    'modularity': {'reusable_count': 0, 'repeated_count': 0, 'score': 100}
                }
            }
            
    def analyze_reusability(self, code: str) -> Dict[str, Any]:
        """
        Analyze code reusability including hardcoded values, function reuse,
        OOP usage, and function parameterization.
        
        Args:
            code: String containing Python code
            
        Returns:
            Dict containing reusability metrics
        """
        try:
            tree = ast.parse(code)
            
            # Analyze hardcoded values
            hardcoded = self._analyze_hardcoded_values(tree)
            
            # Analyze function reuse
            reuse = self._analyze_function_reuse(tree)
            
            # Analyze OOP usage
            oop = self._analyze_oop_usage(tree)
            
            # Analyze function parameterization
            params = self._analyze_function_parameterization(tree)
            
            return {
                'metrics': {
                    'hardcoded_values': hardcoded,
                    'function_reuse': reuse,
                    'oop_usage': oop,
                    'parameterization': params
                }
            }
        except SyntaxError:
            return {
                'metrics': {
                    'hardcoded_values': {'count': 0, 'instances': [], 'score': 100},
                    'function_reuse': {'reuse_count': {}, 'average_reuse': 0, 'score': 100},
                    'oop_usage': {'classes': [], 'appropriate_usage': True, 'score': 100},
                    'parameterization': {'global_usage': [], 'parameter_score': 100}
                }
            }

    def analyze_advanced_techniques(self, code: str) -> Dict[str, Any]:
        """Analyze usage of advanced coding techniques."""
        
        # Advanced library imports to check for
        ADVANCED_LIBRARIES = {
            'ml': ['sklearn', 'tensorflow', 'torch', 'keras', 'xgboost', 'lightgbm'],
            'stats': ['statsmodels', 'scipy.stats', 'pingouin'],
            'geo': ['geopandas', 'folium', 'shapely', 'pyproj'],
            'optimization': ['numba', 'multiprocessing', 'joblib', 'dask']
        }
        
        # Visualization libraries to check for
        VIZ_LIBRARIES = {
            'basic': ['matplotlib', 'seaborn'],
            'interactive': ['plotly', 'bokeh', 'altair'],
            'specialized': ['networkx', 'graphviz', 'folium']
        }
        
        try:
            tree = ast.parse(code)
            
            # Analyze library usage
            libraries = self._analyze_library_usage(tree)
            
            # Analyze ML model complexity
            ml_complexity = self._analyze_ml_complexity(tree)
            
            # Analyze optimization techniques
            optimization = self._analyze_optimization_techniques(tree)
            
            # Analyze custom algorithms
            custom_algos = self._analyze_custom_algorithms(tree)
            
            return {
                'metrics': {
                    'library_usage': libraries,
                    'ml_complexity': ml_complexity,
                    'optimization': optimization,
                    'custom_algorithms': custom_algos
                }
            }
        except SyntaxError:
            return self._get_default_advanced_metrics()

    def analyze_visualization_types(self, code: str) -> Dict[str, Any]:
        """Analyze visualization types and their appropriateness."""
        try:
            tree = ast.parse(code)
            
            # Analyze visualization diversity
            diversity = self._analyze_viz_diversity(tree)
            
            # Analyze advanced visualizations
            advanced = self._analyze_advanced_viz(tree)
            
            # Analyze visualization appropriateness
            appropriateness = self._analyze_viz_appropriateness(tree)
            
            return {
                'metrics': {
                    'diversity': diversity,
                    'advanced_viz': advanced,
                    'appropriateness': appropriateness
                }
            }
        except SyntaxError:
            return self._get_default_viz_type_metrics()

    def analyze_visualization_formatting(self, code: str) -> Dict[str, Any]:
        """Analyze visualization formatting and readability."""
        try:
            tree = ast.parse(code)
            
            # Analyze axis labels
            axis_labels = self._analyze_axis_labels(tree)
            
            # Analyze titles
            titles = self._analyze_viz_titles(tree)
            
            # Analyze legends
            legends = self._analyze_legends(tree)
            
            # Analyze readability
            readability = self._analyze_viz_readability(tree)
            
            return {
                'metrics': {
                    'axis_labels': axis_labels,
                    'titles': titles,
                    'legends': legends,
                    'readability': readability
                }
            }
        except SyntaxError:
            return self._get_default_viz_format_metrics()
            
    def _is_redundant_comment(self, code: str, comment: str) -> bool:
        """
        Check if a comment is redundant (just restates the code).
        
        Args:
            code: The code portion of the line
            comment: The comment portion of the line
            
        Returns:
            bool: True if comment is deemed redundant
        """
        # Convert both to lowercase for comparison
        code_lower = code.lower()
        comment_lower = comment.lower()
        
        # Remove common words that don't add meaning
        stop_words = {'the', 'a', 'an', 'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were'}
        
        # Clean and tokenize the code and comment
        code_tokens = set(
            word.strip('()[]{},.=:<>+-*/"\' ')
            for word in code_lower.split()
            if word.strip('()[]{},.=:<>+-*/"\' ') not in stop_words
        )
        comment_tokens = set(
            word.strip('()[]{},.=:<>+-*/"\' ')
            for word in comment_lower.split()
            if word.strip('()[]{},.=:<>+-*/"\' ') not in stop_words
        )
        
        # Common patterns that indicate redundant comments
        redundant_patterns = [
            # Variable assignment comments
            code_lower.endswith('= true') and 'set' in comment_lower and 'true' in comment_lower,
            code_lower.endswith('= false') and 'set' in comment_lower and 'false' in comment_lower,
            # Simple operation comments
            code_lower.startswith('return') and 'return' in comment_lower,
            'increment' in comment_lower and '+=' in code_lower,
            'decrement' in comment_lower and '-=' in code_lower,
            # Loop comments
            code_lower.startswith('for') and 'loop' in comment_lower,
            code_lower.startswith('while') and 'loop' in comment_lower,
        ]
        
        # Check if significant words from the code appear in the comment
        word_overlap = len(code_tokens.intersection(comment_tokens))
        total_comment_words = len(comment_tokens)
        
        # Comment is considered redundant if:
        # 1. It matches any redundant patterns, or
        # 2. More than 70% of code words appear in the comment
        return (
            any(redundant_patterns) or
            (total_comment_words > 0 and word_overlap / total_comment_words > 0.7)
        )

    def _find_duplicate_code(self, tree: ast.AST) -> Dict[str, Any]:
        """Find duplicate code blocks."""
        code_blocks = {}
        duplicates = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.For, ast.While, ast.If)):
                block_hash = hash(ast.dump(node))
                if block_hash in code_blocks:
                    duplicates.append({
                        'lines': (node.lineno, node.end_lineno),
                        'original_lines': code_blocks[block_hash],
                        'type': node.__class__.__name__
                    })
                else:
                    code_blocks[block_hash] = (node.lineno, node.end_lineno)
        
        return {
            'count': len(duplicates),
            'instances': duplicates
        }

    def _find_dead_code(self, tree: ast.AST) -> Dict[str, Any]:
        """Find unused variables, functions, and unreachable code."""
        class DeadCodeFinder(ast.NodeVisitor):
            def __init__(self):
                self.defined_vars = set()
                self.used_vars = set()
                self.defined_funcs = set()
                self.called_funcs = set()
                self.unreachable = []
                
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    self.defined_vars.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    self.used_vars.add(node.id)
                    
            def visit_FunctionDef(self, node):
                self.defined_funcs.add(node.name)
                self.generic_visit(node)
                
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    self.called_funcs.add(node.func.id)
                self.generic_visit(node)
                
            def visit_Return(self, node):
                # Check for code after return statements
                parent = self.get_parent(node)
                if parent and isinstance(parent, ast.FunctionDef):
                    for stmt in parent.body:
                        if hasattr(stmt, 'lineno') and stmt.lineno > node.lineno:
                            self.unreachable.append(stmt.lineno)
                
        finder = DeadCodeFinder()
        finder.visit(tree)
        
        return {
            'unused_vars': list(finder.defined_vars - finder.used_vars),
            'unused_functions': list(finder.defined_funcs - finder.called_funcs),
            'unreachable': finder.unreachable
        }

    def _analyze_function_lengths(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze function lengths."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                length = node.end_lineno - node.lineno + 1
                functions.append({
                    'name': node.name,
                    'length': length,
                    'start_line': node.lineno
                })
        
        avg_length = (
            sum(f['length'] for f in functions) / len(functions)
            if functions else 0
        )
        
        return {
            'average_length': avg_length,
            'functions': functions
        }

    def _analyze_variable_usage(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze variable usage efficiency."""
        class VariableTracker(ast.NodeVisitor):
            def __init__(self):
                self.declared = set()
                self.used = set()
                
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    self.declared.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    self.used.add(node.id)
                    
        tracker = VariableTracker()
        tracker.visit(tree)
        
        declared_count = len(tracker.declared)
        used_count = len(tracker.used)
        efficiency = (used_count / declared_count * 100) if declared_count > 0 else 100
        
        return {
            'declared': declared_count,
            'used': used_count,
            'efficiency': efficiency
        }
        
    def _find_unreachable_code(self, tree: ast.AST) -> List[int]:
        """Find unreachable code after return statements."""
        unreachable_lines = []
        
        class UnreachableCodeFinder(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                has_return = False
                for stmt in node.body:
                    if isinstance(stmt, ast.Return):
                        has_return = True
                    elif has_return and hasattr(stmt, 'lineno'):
                        unreachable_lines.append(stmt.lineno)
                self.generic_visit(node)
        
        UnreachableCodeFinder().visit(tree)
        return unreachable_lines
        
    def _analyze_cyclomatic_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate cyclomatic complexity for each function and overall."""
        complexities = {}
        
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_function = None
                self.complexity = 1  # Base complexity is 1
                
            def visit_FunctionDef(self, node):
                prev_function = self.current_function
                prev_complexity = self.complexity
                
                self.current_function = node.name
                self.complexity = 1
                
                # Visit function body
                self.generic_visit(node)
                
                # Store complexity for this function
                complexities[node.name] = self.complexity
                
                # Restore previous state
                self.current_function = prev_function
                self.complexity = prev_complexity
                
            def visit_If(self, node):
                self.complexity += len(node.orelse) + 1
                self.generic_visit(node)
                
            def visit_While(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_For(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_And(self, node):
                self.complexity += len(node.values) - 1
                self.generic_visit(node)
                
            def visit_Or(self, node):
                self.complexity += len(node.values) - 1
                self.generic_visit(node)
                
            def visit_Try(self, node):
                self.complexity += len(node.handlers)
                self.generic_visit(node)
        
        ComplexityVisitor().visit(tree)
        
        return {
            'total': sum(complexities.values()),
            'per_function': complexities,
            'average': sum(complexities.values()) / len(complexities) if complexities else 0
        }

    def _analyze_function_dependencies(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze function dependencies and calculate modularity score."""
        dependencies = {}
        defined_functions = set()
        
        class DependencyVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_function = None
                self.called_functions = set()
                
            def visit_FunctionDef(self, node):
                prev_function = self.current_function
                prev_called = self.called_functions
                
                defined_functions.add(node.name)
                self.current_function = node.name
                self.called_functions = set()
                
                # Visit function body
                self.generic_visit(node)
                
                # Store dependencies
                if self.called_functions:
                    dependencies[node.name] = list(self.called_functions)
                
                # Restore previous state
                self.current_function = prev_function
                self.called_functions = prev_called
                
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    self.called_functions.add(node.func.id)
                self.generic_visit(node)
        
        DependencyVisitor().visit(tree)
        
        # Build dependency graph
        G = nx.DiGraph()
        for func in defined_functions:
            G.add_node(func)
        for func, deps in dependencies.items():
            for dep in deps:
                if dep in defined_functions:  # Only add edges for defined functions
                    G.add_edge(func, dep)
        
        # Calculate modularity score
        if G.number_of_nodes() > 0:
            # Score based on average dependency ratio
            avg_deps = sum(len(G.edges(node)) for node in G.nodes()) / G.number_of_nodes()
            modularity_score = max(0, 100 - (avg_deps * 10))  # Deduct 10 points per average dependency
        else:
            modularity_score = 100
        
        return {
            'dependencies': {func: deps for func, deps in dependencies.items()},
            'modularity_score': modularity_score,
            'circular_dependencies': list(nx.simple_cycles(G))
        }

    def _analyze_global_variables(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze global variable usage."""
        global_vars = set()
        usage_count = {}
        
        class GlobalVarVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_function = None
                self.globals_declared = set()
                
            def visit_Global(self, node):
                for name in node.names:
                    global_vars.add(name)
                    self.globals_declared.add(name)
                
            def visit_Name(self, node):
                if (isinstance(node.ctx, (ast.Load, ast.Store)) and
                    not self.current_function and
                    node.id not in self.globals_declared):
                    global_vars.add(node.id)
                    usage_count[node.id] = usage_count.get(node.id, 0) + 1
                
            def visit_FunctionDef(self, node):
                prev_function = self.current_function
                self.current_function = node.name
                self.generic_visit(node)
                self.current_function = prev_function
        
        GlobalVarVisitor().visit(tree)
        
        return {
            'count': len(global_vars),
            'names': list(global_vars),
            'usage_count': usage_count
        }

    def _analyze_execution_order(self, tree: ast.AST, cell_number: int) -> Dict[str, Any]:
        """Analyze logical execution order of cells."""
        issues = []
        referenced_vars = set()
        defined_vars = set()
        
        class ExecutionOrderVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    referenced_vars.add(node.id)
                elif isinstance(node.ctx, ast.Store):
                    defined_vars.add(node.id)
                
            def visit_FunctionDef(self, node):
                defined_vars.add(node.name)
                self.generic_visit(node)
                
            def visit_ClassDef(self, node):
                defined_vars.add(node.name)
                self.generic_visit(node)
        
        ExecutionOrderVisitor().visit(tree)
        
        # Calculate execution order score
        undefined_refs = referenced_vars - defined_vars
        if undefined_refs:
            issues.append({
                'type': 'undefined_reference',
                'cell': cell_number,
                'variables': list(undefined_refs)
            })
        
        score = 100 - (len(undefined_refs) * 10)  # Deduct 10 points per undefined reference
        
        return {
            'issues': issues,
            'score': max(0, score),
            'undefined_references': list(undefined_refs)
        }
        
    def _analyze_join_methods(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze consistency of join methods used."""
        join_methods = []
        
        class JoinMethodVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # Check for DataFrame join methods
                if isinstance(node.func, ast.Attribute):
                    method_name = node.func.attr
                    if method_name in ['merge', 'join', 'concat']:
                        join_methods.append({
                            'method': method_name,
                            'lineno': node.lineno,
                            'args': self._get_join_args(node)
                        })
                self.generic_visit(node)
                
            def _get_join_args(self, node):
                args = {}
                for kw in node.keywords:
                    if kw.arg in ['how', 'on', 'left_on', 'right_on']:
                        args[kw.arg] = ast.literal_eval(kw.value) if isinstance(kw.value, ast.Constant) else None
                return args
        
        JoinMethodVisitor().visit(tree)
        
        # Calculate consistency score
        method_counts = {}
        for join in join_methods:
            method_counts[join['method']] = method_counts.get(join['method'], 0) + 1
            
        total_joins = len(join_methods)
        if total_joins > 0:
            most_common = max(method_counts.values())
            consistency_score = (most_common / total_joins) * 100
        else:
            consistency_score = 100
            
        return {
            'methods': join_methods,
            'method_counts': method_counts,
            'consistency_score': consistency_score
        }

    def _analyze_join_keys(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze join key handling."""
        key_issues = []
        
        class JoinKeyVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    method_name = node.func.attr
                    if method_name in ['merge', 'join']:
                        # Check for null check before join
                        if not self._has_null_check(node):
                            key_issues.append({
                                'type': 'missing_null_check',
                                'lineno': node.lineno,
                                'message': 'No null check before join'
                            })
                        
                        # Check for duplicate check before join
                        if not self._has_duplicate_check(node):
                            key_issues.append({
                                'type': 'missing_duplicate_check',
                                'lineno': node.lineno,
                                'message': 'No duplicate check before join'
                            })
                self.generic_visit(node)
                
            def _has_null_check(self, node):
                # Look for dropna() or isna() calls before join
                parent = self._get_parent_stmt(node)
                if parent and isinstance(parent, ast.Expr):
                    prev_stmt = self._get_previous_stmt(parent)
                    return self._contains_null_check(prev_stmt)
                return False
                
            def _has_duplicate_check(self, node):
                # Look for drop_duplicates() calls before join
                parent = self._get_parent_stmt(node)
                if parent and isinstance(parent, ast.Expr):
                    prev_stmt = self._get_previous_stmt(parent)
                    return self._contains_duplicate_check(prev_stmt)
                return False
        
        JoinKeyVisitor().visit(tree)
        
        score = 100 - (len(key_issues) * 10)  # Deduct 10 points per issue
        
        return {
            'issues': key_issues,
            'score': max(0, score)
        }

    def _analyze_join_efficiency(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze efficiency of join operations."""
        efficiency_issues = []
        
        class JoinEfficiencyVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # Check for manual joins using loops
                if self._is_manual_join(node):
                    efficiency_issues.append({
                        'type': 'manual_loop_join',
                        'lineno': node.lineno,
                        'message': 'Manual join using loop instead of vectorized operation'
                    })
                self.generic_visit(node)
                
            def _is_manual_join(self, node):
                # Look for patterns that suggest manual joining
                loop_vars = set()
                assignments = []
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        if isinstance(child.ctx, ast.Store):
                            loop_vars.add(child.id)
                    elif isinstance(child, ast.Assign):
                        assignments.append(child)
                
                # Check if loop variables are used in assignments
                return any(
                    any(v in loop_vars for v in self._get_vars_in_node(assign))
                    for assign in assignments
                )
                
            def _get_vars_in_node(self, node):
                vars_used = set()
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        vars_used.add(child.id)
                return vars_used
        
        JoinEfficiencyVisitor().visit(tree)
        
        score = 100 - (len(efficiency_issues) * 20)  # Deduct 20 points per efficiency issue
        
        return {
            'issues': efficiency_issues,
            'score': max(0, score)
        }

    def _analyze_join_modularity(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze modularity of join operations."""
        join_patterns = {}
        
        class JoinModularityVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute) and node.func.attr in ['merge', 'join', 'concat']:
                    # Create a pattern key based on join attributes
                    pattern = self._get_join_pattern(node)
                    if pattern in join_patterns:
                        join_patterns[pattern]['count'] += 1
                        join_patterns[pattern]['locations'].append(node.lineno)
                    else:
                        join_patterns[pattern] = {
                            'count': 1,
                            'locations': [node.lineno],
                            'in_function': self._is_in_function(node)
                        }
                self.generic_visit(node)
                
            def _get_join_pattern(self, node):
                # Create a unique pattern based on join attributes
                attrs = []
                for kw in node.keywords:
                    attrs.append(f"{kw.arg}={ast.dump(kw.value)}")
                return f"{node.func.attr}({','.join(sorted(attrs))})"
                
            def _is_in_function(self, node):
                parent = node
                while hasattr(parent, 'parent'):
                    parent = parent.parent
                    if isinstance(parent, ast.FunctionDef):
                        return True
                return False
        
        JoinModularityVisitor().visit(tree)
        
        # Count reusable vs repeated joins
        reusable_count = sum(1 for p in join_patterns.values() if p['in_function'])
        repeated_count = sum(1 for p in join_patterns.values() if p['count'] > 1 and not p['in_function'])
        
        # Calculate modularity score
        total_patterns = len(join_patterns)
        if total_patterns > 0:
            score = (reusable_count / total_patterns) * 100 - (repeated_count * 10)
        else:
            score = 100
            
        return {
            'patterns': join_patterns,
            'reusable_count': reusable_count,
            'repeated_count': repeated_count,
            'score': max(0, score)
        }
        
    def _analyze_hardcoded_values(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze hardcoded values in the code."""
        hardcoded_instances = []
        
        class HardcodedValueVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_function = False
                self.function_params = set()
                
            def visit_FunctionDef(self, node):
                prev_in_function = self.in_function
                prev_params = self.function_params
                
                self.in_function = True
                self.function_params = {arg.arg for arg in node.args.args}
                
                self.generic_visit(node)
                
                self.in_function = prev_in_function
                self.function_params = prev_params
                
            def visit_Constant(self, node):
                # Skip None, True, False, and docstrings
                if not isinstance(node.value, (bool, type(None))) and not (
                    isinstance(node.value, str) and ast.get_docstring(node)
                ):
                    hardcoded_instances.append({
                        'value': node.value,
                        'lineno': node.lineno,
                        'in_function': self.in_function
                    })
                
            def visit_Num(self, node):
                # For older Python versions
                hardcoded_instances.append({
                    'value': node.n,
                    'lineno': node.lineno,
                    'in_function': self.in_function
                })
                
            def visit_Str(self, node):
                # For older Python versions, skip docstrings
                if not ast.get_docstring(node):
                    hardcoded_instances.append({
                        'value': node.s,
                        'lineno': node.lineno,
                        'in_function': self.in_function
                    })
        
        HardcodedValueVisitor().visit(tree)
        
        # Calculate score based on number of hardcoded values
        score = max(0, 100 - (len(hardcoded_instances) * 5))  # -5 points per hardcoded value
        
        return {
            'count': len(hardcoded_instances),
            'instances': hardcoded_instances,
            'score': score
        }

    def _analyze_function_reuse(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze function reuse patterns."""
        function_calls = defaultdict(int)
        function_defs = set()
        
        class FunctionReuseVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                function_defs.add(node.name)
                self.generic_visit(node)
                
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    function_calls[node.func.id] += 1
                self.generic_visit(node)
        
        FunctionReuseVisitor().visit(tree)
        
        # Filter to only user-defined functions
        reuse_count = {
            name: count
            for name, count in function_calls.items()
            if name in function_defs
        }
        
        # Calculate average reuse
        if reuse_count:
            average_reuse = sum(reuse_count.values()) / len(reuse_count)
            # Score based on average reuse (2+ reuses is good)
            score = min(100, average_reuse * 50)
        else:
            average_reuse = 0
            score = 0 if function_defs else 100  # Only penalize if functions exist but aren't reused
        
        return {
            'reuse_count': reuse_count,
            'average_reuse': average_reuse,
            'score': score
        }

    def _analyze_oop_usage(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze object-oriented programming usage."""
        classes = []
        
        class OOPVisitor(ast.NodeVisitor):
            def visit_ClassDef(self, node):
                methods = []
                attributes = set()
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            'name': item.name,
                            'args': len(item.args.args)
                        })
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attributes.add(target.id)
                
                classes.append({
                    'name': node.name,
                    'methods': methods,
                    'attributes': list(attributes),
                    'base_classes': [
                        base.id if isinstance(base, ast.Name) else None
                        for base in node.bases
                    ],
                    'lineno': node.lineno
                })
                
                self.generic_visit(node)
        
        OOPVisitor().visit(tree)
        
        # Evaluate OOP appropriateness
        appropriate_usage = True
        reasons = []
        
        for cls in classes:
            # Check if class has both attributes and methods
            if not cls['methods'] or not cls['attributes']:
                appropriate_usage = False
                reasons.append(f"Class {cls['name']} might be better as a function")
            
            # Check if class has too few methods
            if len(cls['methods']) < 2:
                appropriate_usage = False
                reasons.append(f"Class {cls['name']} has too few methods")
        
        # Calculate score based on appropriate usage
        score = 100 if appropriate_usage else max(0, 100 - (len(reasons) * 20))
        
        return {
            'classes': classes,
            'appropriate_usage': appropriate_usage,
            'reasons': reasons,
            'score': score
        }

    def _analyze_function_parameterization(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze function parameterization and global variable usage."""
        global_usage = []
        
        class ParameterizationVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_function = None
                self.function_params = set()
                self.global_vars = set()
                self.used_vars = set()
                
            def visit_FunctionDef(self, node):
                prev_function = self.current_function
                prev_params = self.function_params
                prev_used = self.used_vars
                
                self.current_function = node.name
                self.function_params = {arg.arg for arg in node.args.args}
                self.used_vars = set()
                
                self.generic_visit(node)
                
                # Check for global variable usage
                globals_used = self.used_vars - self.function_params
                if globals_used & self.global_vars:
                    global_usage.append({
                        'function': node.name,
                        'globals_used': list(globals_used & self.global_vars),
                        'lineno': node.lineno
                    })
                
                self.current_function = prev_function
                self.function_params = prev_params
                self.used_vars = prev_used
                
            def visit_Global(self, node):
                self.global_vars.update(node.names)
                
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    self.used_vars.add(node.id)
        
        ParameterizationVisitor().visit(tree)
        
        # Calculate parameterization score
        if global_usage:
            # -20 points per function using globals
            parameter_score = max(0, 100 - (len(global_usage) * 20))
        else:
            parameter_score = 100
        
        return {
            'global_usage': global_usage,
            'parameter_score': parameter_score
        }
        
    def _analyze_library_usage(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze usage of advanced libraries."""
        imports = set()
        
        class LibraryVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
                    
            def visit_ImportFrom(self, node):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        LibraryVisitor().visit(tree)
        
        # Categorize libraries
        categories = {
            category: [lib for lib in libs if any(imp.startswith(lib) for imp in imports)]
            for category, libs in self.ADVANCED_LIBRARIES.items()
        }
        
        # Calculate score based on library diversity
        total_libs = sum(len(libs) for libs in categories.values())
        score = min(100, total_libs * 20)  # 20 points per advanced library type
        
        return {
            'found_libraries': list(imports),
            'categories': categories,
            'score': score
        }

    def _analyze_ml_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze machine learning model complexity."""
        models = []
        
        class MLVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for model instantiation
                    if any(
                        hasattr(node.func, 'value') and
                        isinstance(node.func.value, ast.Name) and
                        node.func.value.id in ['sklearn', 'tf', 'torch']
                    ):
                        models.append({
                            'type': node.func.attr,
                            'lineno': node.lineno,
                            'args': len(node.args) + len(node.keywords)
                        })
                self.generic_visit(node)
        
        MLVisitor().visit(tree)
        
        # Categorize model complexity
        complexity_score = 0
        for model in models:
            if model['type'] in ['LinearRegression', 'LogisticRegression']:
                complexity_score += 10
            elif model['type'] in ['RandomForestClassifier', 'XGBClassifier']:
                complexity_score += 20
            elif 'Neural' in model['type'] or 'Deep' in model['type']:
                complexity_score += 30
        
        return {
            'models': models,
            'complexity_score': min(100, complexity_score)
        }

    def _analyze_optimization_techniques(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze usage of optimization techniques."""
        techniques = defaultdict(list)
        
        class OptimizationVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for vectorization
                    if hasattr(node.func, 'value') and isinstance(node.func.value, ast.Name):
                        if node.func.value.id in ['np', 'pd']:
                            techniques['vectorization'].append({
                                'function': node.func.attr,
                                'lineno': node.lineno
                            })
                
                # Check for multiprocessing
                if isinstance(node.func, ast.Name) and node.func.id in ['Pool', 'Process']:
                    techniques['multiprocessing'].append({
                        'lineno': node.lineno
                    })
                
                # Check for caching
                if isinstance(node.func, ast.Name) and node.func.id in ['cache', 'lru_cache']:
                    techniques['caching'].append({
                        'lineno': node.lineno
                    })
                    
                self.generic_visit(node)
        
        OptimizationVisitor().visit(tree)
        
        # Calculate optimization score
        score = min(100, sum(len(instances) * 20 for instances in techniques.values()))
        
        return {
            'techniques': dict(techniques),
            'score': score
        }

    def _analyze_custom_algorithms(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze implementation of custom algorithms."""
        custom_implementations = []
        
        class CustomAlgoVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check for algorithm-like characteristics
                if (len(node.body) > 10 and  # Non-trivial implementation
                    any(isinstance(child, (ast.For, ast.While)) for child in node.body)):
                    custom_implementations.append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'complexity': len(node.body)
                    })
                self.generic_visit(node)
        
        CustomAlgoVisitor().visit(tree)
        
        return {
            'implementations': custom_implementations,
            'score': min(100, len(custom_implementations) * 25)  # 25 points per custom algorithm
        }

    def _analyze_viz_diversity(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze diversity of visualization types."""
        viz_types = defaultdict(int)
        
        class VizDiversityVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for plotting functions
                    if node.func.attr in ['plot', 'scatter', 'bar', 'hist', 'box', 'violin', 'heatmap']:
                        viz_types[node.func.attr] += 1
                self.generic_visit(node)
        
        VizDiversityVisitor().visit(tree)
        
        # Calculate diversity score
        unique_types = len(viz_types)
        score = min(100, unique_types * 20)  # 20 points per unique visualization type
        
        return {
            'types': dict(viz_types),
            'unique_count': unique_types,
            'score': score
        }

    def _analyze_advanced_viz(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze presence of advanced visualizations."""
        advanced_viz = defaultdict(list)
        
        class AdvancedVizVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for interactive plots
                    if any(
                        hasattr(node.func, 'value') and
                        isinstance(node.func.value, ast.Name) and
                        node.func.value.id in ['px', 'go', 'alt']
                    ):
                        advanced_viz['interactive'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno
                        })
                    
                    # Check for 3D plots
                    if node.func.attr in ['scatter3d', 'plot3d']:
                        advanced_viz['3d'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno
                        })
                    
                    # Check for GIS
                    if node.func.attr in ['choropleth', 'geodata']:
                        advanced_viz['gis'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno
                        })
                self.generic_visit(node)
        
        AdvancedVizVisitor().visit(tree)
        
        # Calculate advanced visualization score
        score = min(100, sum(len(instances) * 25 for instances in advanced_viz.values()))
        
        return {
            'visualizations': dict(advanced_viz),
            'score': score
        }

    def _analyze_viz_appropriateness(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze appropriateness of visualization types."""
        issues = []
        
        class AppropriatenessVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for common misuses
                    if node.func.attr == 'bar' and self._is_continuous_data(node):
                        issues.append({
                            'type': 'inappropriate_bar',
                            'lineno': node.lineno,
                            'message': 'Bar chart used for continuous data'
                        })
                    elif node.func.attr == 'scatter' and self._is_categorical_data(node):
                        issues.append({
                            'type': 'inappropriate_scatter',
                            'lineno': node.lineno,
                            'message': 'Scatter plot used for categorical data'
                        })
                self.generic_visit(node)
            
            def _is_continuous_data(self, node):
                # Heuristic implementation
                return False
            
            def _is_categorical_data(self, node):
                # Heuristic implementation
                return False
        
        AppropriatenessVisitor().visit(tree)
        
        return {
            'issues': issues,
            'score': max(0, 100 - len(issues) * 20)  # -20 points per issue
        }

    def _analyze_axis_labels(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze completeness of axis labels."""
        labels = []
        missing_labels = []
        
        class AxisLabelsVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['set_xlabel', 'set_ylabel']:
                        labels.append({
                            'type': node.func.attr,
                            'lineno': node.lineno
                        })
                    elif node.func.attr in ['plot', 'scatter', 'bar']:
                        # Check if labels are set in the same context
                        if not self._has_axis_labels(node):
                            missing_labels.append({
                                'type': node.func.attr,
                                'lineno': node.lineno
                            })
                self.generic_visit(node)
            
            def _has_axis_labels(self, node):
                # Check parent context for label setting
                return True  # Simplified implementation
        
        AxisLabelsVisitor().visit(tree)
        
        return {
            'labels': labels,
            'missing': missing_labels,
            'score': max(0, 100 - len(missing_labels) * 20)  # -20 points per missing label
        }

    def _analyze_viz_titles(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze visualization titles."""
        titles = []
        missing_titles = []
        
        class TitleVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'set_title':
                        titles.append({
                            'lineno': node.lineno,
                            'text': self._get_title_text(node)
                        })
                    elif node.func.attr in ['plot', 'scatter', 'bar']:
                        if not self._has_title(node):
                            missing_titles.append({
                                'type': node.func.attr,
                                'lineno': node.lineno
                            })
                self.generic_visit(node)
            
            def _get_title_text(self, node):
                if node.args:
                    return ast.literal_eval(node.args[0]) if isinstance(node.args[0], ast.Constant) else None
                return None
            
            def _has_title(self, node):
                # Check parent context for title setting
                return True  # Simplified implementation
        
        TitleVisitor().visit(tree)
        
        # Calculate title quality score
        quality_score = sum(1 for t in titles if t['text'] and len(t['text'].split()) >= 3)
        score = max(0, 100 - len(missing_titles) * 20 - (len(titles) - quality_score) * 10)
        
        return {
            'titles': titles,
            'missing': missing_titles,
            'quality_score': quality_score,
            'score': score
        }
