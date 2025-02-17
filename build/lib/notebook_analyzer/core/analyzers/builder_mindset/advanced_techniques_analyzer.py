"""Analyzer for advanced programming techniques and patterns."""
import ast
from typing import Dict, Any, List, Set
from collections import defaultdict
from datetime import datetime
from ...base_analyzer import BaseAnalyzer

class AdvancedTechniquesAnalyzer(BaseAnalyzer):
    """Analyzes usage of advanced programming techniques and patterns."""
    
    def __init__(self):
        super().__init__()
        self.ml_libraries = {
            'sklearn', 'tensorflow', 'torch', 'keras', 'xgboost',
            'lightgbm', 'catboost', 'fastai'
        }
        self.optimization_libraries = {
            'numba', 'cython', 'dask', 'ray', 'multiprocessing',
            'concurrent.futures', 'joblib'
        }
        self.advanced_libs = {
            'ml': self.ml_libraries,
            'stats': {'scipy', 'statsmodels', 'pingouin'},
            'geo': {'geopandas', 'shapely', 'rasterio', 'folium'},
            'optimization': self.optimization_libraries
        }

    def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze advanced programming techniques."""
        try:
            tree = ast.parse(code)
            return {
                'metrics': {
                    'library_usage': self._analyze_library_usage(tree),
                    'ml_complexity': self._analyze_ml_complexity(tree),
                    'optimization': self._analyze_optimization_techniques(tree),
                    'custom_algorithms': self._analyze_custom_algorithms(tree)
                }
            }
        except SyntaxError:
            return self._get_default_metrics()

    def _analyze_library_usage(self, tree: ast.AST) -> Dict[str, Any]:
        found_libraries = set()
        categories = defaultdict(set)
        
        class LibraryVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    lib_name = alias.name.split('.')[0]
                    if self._is_advanced_library(lib_name):
                        found_libraries.add(lib_name)
                        self._categorize_library(lib_name)
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module:
                    lib_name = node.module.split('.')[0]
                    if self._is_advanced_library(lib_name):
                        found_libraries.add(lib_name)
                        self._categorize_library(lib_name)
                self.generic_visit(node)
            
            def _is_advanced_library(self, lib_name: str) -> bool:
                return any(lib_name in libs for libs in self.advanced_libs.values())
            
            def _categorize_library(self, lib_name: str):
                for category, libs in self.advanced_libs.items():
                    if lib_name in libs:
                        categories[category].add(lib_name)
        
        LibraryVisitor().visit(tree)
        
        # Calculate library usage score
        if not found_libraries:
            library_score = 60  # Base score for no advanced libraries
        else:
            base_score = 70
            # Bonus for using libraries from different categories
            category_bonus = min(30, len(categories) * 10)
            # Bonus for using multiple libraries within categories
            diversity_bonus = min(20, sum(len(libs) - 1 for libs in categories.values()) * 5)
            library_score = base_score + category_bonus + diversity_bonus
        
        return {
            'found_libraries': list(found_libraries),
            'categories': {k: list(v) for k, v in categories.items()},
            'score': round(min(100, library_score), 2)
        }

    def _analyze_ml_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        models = []
        
        class MLVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    # Direct model instantiation
                    if self._is_ml_model(node.func.id):
                        models.append(self._extract_model_info(node))
                elif isinstance(node.func, ast.Attribute):
                    # Model from library
                    if isinstance(node.func.value, ast.Name) and node.func.value.id in self.ml_libraries:
                        models.append(self._extract_model_info(node))
                self.generic_visit(node)
            
            def _is_ml_model(self, name: str) -> bool:
                return any(
                    term in name.lower()
                    for term in ['model', 'classifier', 'regressor', 'network']
                )
            
            def _extract_model_info(self, node) -> Dict:
                params = {}
                for kw in node.keywords:
                    if isinstance(kw.value, (ast.Constant, ast.Name)):
                        params[kw.arg] = ast.literal_eval(kw.value) if isinstance(kw.value, ast.Constant) else kw.value.id
                
                return {
                    'type': node.func.id if isinstance(node.func, ast.Name) else node.func.attr,
                    'params': params,
                    'lineno': node.lineno
                }
        
        MLVisitor().visit(tree)
        
        # Calculate ML complexity score
        if not models:
            ml_score = 60  # Base score for no ML usage
        else:
            base_score = 70
            # Bonus for using multiple models
            model_bonus = min(20, len(models) * 5)
            # Bonus for model sophistication
            sophistication_bonus = sum(
                10 if 'Neural' in model['type'] or 'Deep' in model['type']
                else 5 if any(term in model['type'] for term in ['Forest', 'Boost', 'Ensemble'])
                else 2
                for model in models
            )
            ml_score = base_score + model_bonus + min(20, sophistication_bonus)
        
        return {
            'models': models,
            'score': round(min(100, ml_score), 2)
        }

    def _analyze_optimization_techniques(self, tree: ast.AST) -> Dict[str, Any]:
        techniques = defaultdict(list)
        
        class OptimizationVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for vectorization
                    if node.func.attr in {'apply', 'vectorize', 'map'}:
                        techniques['vectorization'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno
                        })
                    # Check for parallel processing
                    elif node.func.attr in {'parallel', 'map_async', 'starmap'}:
                        techniques['multiprocessing'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno
                        })
                    # Check for caching
                    elif node.func.attr in {'cache', 'memoize', 'lru_cache'}:
                        techniques['caching'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno
                        })
                
                # Check for optimization decorators
                if isinstance(node.func, ast.Name):
                    if node.func.id in {'njit', 'jit', 'vectorize'}:
                        techniques['compilation'].append({
                            'type': node.func.id,
                            'lineno': node.lineno
                        })
                
                self.generic_visit(node)
            
            def visit_With(self, node):
                # Check for context managers related to optimization
                if isinstance(node.items[0].context_expr, ast.Call):
                    call = node.items[0].context_expr
                    if isinstance(call.func, ast.Name):
                        if call.func.id in {'Pool', 'ThreadPool', 'ProcessPool'}:
                            techniques['multiprocessing'].append({
                                'type': call.func.id,
                                'lineno': node.lineno
                            })
                self.generic_visit(node)
        
        OptimizationVisitor().visit(tree)
        
        # Calculate optimization score
        if not any(techniques.values()):
            opt_score = 60  # Base score for no optimization
        else:
            base_score = 70
            # Bonus for using multiple optimization techniques
            technique_bonus = min(20, len(techniques) * 10)
            # Bonus for technique sophistication
            sophistication_bonus = sum(
                len(techs) * (
                    8 if category == 'multiprocessing'
                    else 6 if category == 'vectorization'
                    else 4
                )
                for category, techs in techniques.items()
            )
            opt_score = base_score + technique_bonus + min(20, sophistication_bonus / 2)
        
        return {
            'techniques': dict(techniques),
            'score': round(min(100, opt_score), 2)
        }

    def _analyze_custom_algorithms(self, tree: ast.AST) -> Dict[str, Any]:
        implementations = []
        
        class AlgorithmVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check for algorithm implementation characteristics
                if self._is_algorithm_implementation(node):
                    implementations.append({
                        'name': node.name,
                        'type': self._determine_algorithm_type(node),
                        'complexity': self._analyze_complexity(node),
                        'lineno': node.lineno
                    })
                self.generic_visit(node)
            
            def _is_algorithm_implementation(self, node) -> bool:
                # Heuristics to identify algorithm implementations
                contains_loop = False
                contains_recursion = False
                contains_math = False
                
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While)):
                        contains_loop = True
                    elif isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        if child.func.id == node.name:
                            contains_recursion = True
                    elif isinstance(child, ast.BinOp):
                        contains_math = True
                
                return (contains_loop or contains_recursion) and contains_math
            
            def _determine_algorithm_type(self, node) -> str:
                # Attempt to classify algorithm type
                if self._is_sorting_algorithm(node):
                    return 'sorting'
                elif self._is_search_algorithm(node):
                    return 'search'
                elif self._is_graph_algorithm(node):
                    return 'graph'
                return 'other'
            
            def _is_sorting_algorithm(self, node) -> bool:
                return (
                    'sort' in node.name.lower() or
                    self._has_swap_operations(node)
                )
            
            def _is_search_algorithm(self, node) -> bool:
                return (
                    'search' in node.name.lower() or
                    'find' in node.name.lower()
                )
            
            def _is_graph_algorithm(self, node) -> bool:
                # Check for typical graph algorithm characteristics
                contains_adjacency = False
                contains_visited = False
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        if 'graph' in child.id.lower() or 'adj' in child.id.lower():
                            contains_adjacency = True
                        elif 'visit' in child.id.lower():
                            contains_visited = True
                
                return contains_adjacency or contains_visited
            
            def _has_swap_operations(self, node) -> bool:
                # Check for typical swap operations in sorting algorithms
                for child in ast.walk(node):
                    if isinstance(child, ast.Assign):
                        if len(child.targets) == 1 and isinstance(child.value, ast.Subscript):
                            return True
                return False
            
            def _analyze_complexity(self, node) -> Dict[str, Any]:
                loops = 0
                max_depth = 0
                current_depth = 0
                
                class ComplexityVisitor(ast.NodeVisitor):
                    def visit_For(self, node):
                        nonlocal loops, current_depth, max_depth
                        loops += 1
                        current_depth += 1
                        max_depth = max(max_depth, current_depth)
                        self.generic_visit(node)
                        current_depth -= 1
                    
                    visit_While = visit_For
                
                ComplexityVisitor().visit(node)
                
                return {
                    'nested_loops': max_depth,
                    'total_loops': loops,
                    'estimated_complexity': (
                        'O(1)' if loops == 0
                        else 'O(n)' if max_depth == 1
                        else 'O(n²)' if max_depth == 2
                        else 'O(n³)' if max_depth == 3
                        else f'O(n^{max_depth})'
                    )
                }
        
        AlgorithmVisitor().visit(tree)
        
        # Calculate custom algorithms score
        if not implementations:
            algo_score = 60  # Base score for no custom algorithms
        else:
            base_score = 70
            # Bonus for implementing multiple algorithms
            count_bonus = min(20, len(implementations) * 5)
            # Bonus for algorithm sophistication
            sophistication_bonus = sum(
                10 if impl['type'] in {'graph', 'search'}
                else 5 if impl['type'] == 'sorting'
                else 3
                for impl in implementations
            )
            algo_score = base_score + count_bonus + min(20, sophistication_bonus)
        
        return {
            'implementations': implementations,
            'score': round(min(100, algo_score), 2)
        }

    def _get_default_metrics(self) -> Dict[str, Any]:
        return {
            'metrics': {
                'library_usage': {
                    'found_libraries': [],
                    'categories': {},
                    'score': 60
                },
                'ml_complexity': {
                    'models': [],
                    'score': 60
                },
                'optimization': {
                    'techniques': {},
                    'score': 60
                },
                'custom_algorithms': {
                    'implementations': [],
                    'score': 60
                }
            }
        }
