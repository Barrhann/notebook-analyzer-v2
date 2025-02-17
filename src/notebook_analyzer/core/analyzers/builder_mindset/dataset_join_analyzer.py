"""Analyzer for dataset joining operations and patterns."""
import ast
from typing import Dict, Any, List
from collections import defaultdict
from ...base_analyzer import BaseAnalyzer

class DatasetJoinAnalyzer(BaseAnalyzer):
    """Analyzes dataset joining operations and their efficiency."""
    
    def __init__(self):
        super().__init__()
        self.join_functions = {
            'merge', 'join', 'concat', 'append',  # pandas
            'combine', 'union', 'intersection',  # set operations
            'join_asof', 'merge_ordered', 'merge_asof'  # advanced pandas joins
        }
        self.data_prep_functions = {
            'sort_values', 'reset_index', 'set_index',
            'dropna', 'fillna', 'drop_duplicates'
        }

    def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze dataset joining operations."""
        try:
            tree = ast.parse(code)
            return {
                'metrics': {
                    'join_operations': self._analyze_join_operations(tree),
                    'data_preparation': self._analyze_data_preparation(tree),
                    'join_efficiency': self._analyze_join_efficiency(tree),
                    'memory_usage': self._analyze_memory_usage(tree)
                }
            }
        except SyntaxError:
            return self._get_default_metrics()

    def _analyze_join_operations(self, tree: ast.AST) -> Dict[str, Any]:
        join_ops = []
        
        class JoinVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.join_functions:
                        join_ops.append({
                            'type': node.func.attr,
                            'lineno': node.lineno,
                            'args': self._extract_join_args(node)
                        })
                self.generic_visit(node)
            
            def _extract_join_args(self, node):
                args = []
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        args.append(arg.id)
                for kw in node.keywords:
                    args.append(f"{kw.arg}={kw.value.id if isinstance(kw.value, ast.Name) else '...'}")
                return args
        
        JoinVisitor().visit(tree)
        
        # Calculate join operations score
        score = 100
        if join_ops:
            # Penalize for multiple joins without proper preparation
            for op in join_ops:
                if op['type'] not in {'merge_asof', 'merge_ordered'}:
                    score -= 10  # Prefer more specialized join operations
            
            # Bonus for using appropriate join types
            score += min(20, len([op for op in join_ops if op['type'] in {'merge_asof', 'merge_ordered'}]) * 10)
        
        return {
            'operations': join_ops,
            'count': len(join_ops),
            'score': max(0, score)
        }

    def _analyze_data_preparation(self, tree: ast.AST) -> Dict[str, Any]:
        prep_operations = defaultdict(list)
        
        class PrepVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.data_prep_functions:
                        prep_operations[node.func.attr].append({
                            'lineno': node.lineno,
                            'target': node.func.value.id if isinstance(node.func.value, ast.Name) else None
                        })
                self.generic_visit(node)
        
        PrepVisitor().visit(tree)
        
        # Calculate preparation score
        total_preps = sum(len(ops) for ops in prep_operations.values())
        essential_preps = len(prep_operations.get('sort_values', [])) + \
                         len(prep_operations.get('set_index', [])) + \
                         len(prep_operations.get('dropna', []))
        
        if total_preps == 0:
            prep_score = 100 if not self._has_joins(tree) else 50
        else:
            prep_score = min(100, (essential_preps / total_preps) * 100 + 50)
        
        return {
            'operations': dict(prep_operations),
            'total_operations': total_preps,
            'essential_operations': essential_preps,
            'score': round(prep_score, 2)
        }

    def _analyze_join_efficiency(self, tree: ast.AST) -> Dict[str, Any]:
        efficiency_issues = []
        join_sequence = []
        
        class EfficiencyVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.join_functions:
                        join_info = {
                            'type': node.func.attr,
                            'lineno': node.lineno,
                            'preparation': self._check_preparation(node)
                        }
                        
                        # Check for potential issues
                        if not join_info['preparation']['sorted']:
                            efficiency_issues.append({
                                'type': 'missing_sort',
                                'lineno': node.lineno,
                                'message': 'Join operation without prior sorting'
                            })
                        
                        if not join_info['preparation']['indexed']:
                            efficiency_issues.append({
                                'type': 'missing_index',
                                'lineno': node.lineno,
                                'message': 'Join operation without proper indexing'
                            })
                        
                        join_sequence.append(join_info)
                        
                self.generic_visit(node)
            
            def _check_preparation(self, node):
                """Check if proper preparation was done before join."""
                parent = getattr(node, 'parent', None)
                if not parent:
                    return {'sorted': False, 'indexed': False}
                
                # Look for preparation steps in previous siblings
                sorted_data = False
                indexed_data = False
                
                for sibling in ast.iter_child_nodes(parent):
                    if isinstance(sibling, ast.Call) and isinstance(sibling.func, ast.Attribute):
                        if sibling.func.attr == 'sort_values':
                            sorted_data = True
                        elif sibling.func.attr in {'set_index', 'reset_index'}:
                            indexed_data = True
                
                return {'sorted': sorted_data, 'indexed': indexed_data}
        
        EfficiencyVisitor().visit(tree)
        
        # Calculate efficiency score
        if not join_sequence:
            efficiency_score = 100
        else:
            base_score = 100
            for issue in efficiency_issues:
                if issue['type'] == 'missing_sort':
                    base_score -= 20
                elif issue['type'] == 'missing_index':
                    base_score -= 15
            
            # Bonus for proper join sequence
            if len(join_sequence) > 1:
                base_score += min(20, len([j for j in join_sequence if all(j['preparation'].values())]) * 10)
            
            efficiency_score = max(0, base_score)
        
        return {
            'issues': efficiency_issues,
            'join_sequence': join_sequence,
            'score': round(efficiency_score, 2)
        }

    def _analyze_memory_usage(self, tree: ast.AST) -> Dict[str, Any]:
        memory_patterns = []
        
        class MemoryVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for memory-efficient operations
                    if node.func.attr in {'copy', 'deepcopy'}:
                        memory_patterns.append({
                            'type': 'unnecessary_copy',
                            'lineno': node.lineno,
                            'message': 'Unnecessary data copy operation'
                        })
                    elif node.func.attr in self.join_functions:
                        # Check for memory-efficient join parameters
                        self._check_join_memory_efficiency(node)
                self.generic_visit(node)
            
            def _check_join_memory_efficiency(self, node):
                inplace_found = False
                copy_found = False
                
                for kw in node.keywords:
                    if kw.arg == 'inplace' and isinstance(kw.value, ast.Constant):
                        inplace_found = kw.value.value
                    elif kw.arg == 'copy' and isinstance(kw.value, ast.Constant):
                        copy_found = kw.value.value
                
                if not inplace_found and copy_found:
                    memory_patterns.append({
                        'type': 'inefficient_join',
                        'lineno': node.lineno,
                        'message': 'Join operation creates unnecessary copy'
                    })
        
        MemoryVisitor().visit(tree)
        
        # Calculate memory usage score
        if not memory_patterns:
            memory_score = 100
        else:
            base_score = 100
            for pattern in memory_patterns:
                if pattern['type'] == 'unnecessary_copy':
                    base_score -= 15
                elif pattern['type'] == 'inefficient_join':
                    base_score -= 20
            
            memory_score = max(0, base_score)
        
        return {
            'patterns': memory_patterns,
            'score': round(memory_score, 2)
        }

    def _has_joins(self, tree: ast.AST) -> bool:
        """Helper method to check if code contains any join operations."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in self.join_functions:
                    return True
        return False

    def _get_default_metrics(self) -> Dict[str, Any]:
        return {
            'metrics': {
                'join_operations': {
                    'operations': [],
                    'count': 0,
                    'score': 100
                },
                'data_preparation': {
                    'operations': {},
                    'total_operations': 0,
                    'essential_operations': 0,
                    'score': 100
                },
                'join_efficiency': {
                    'issues': [],
                    'join_sequence': [],
                    'score': 100
                },
                'memory_usage': {
                    'patterns': [],
                    'score': 100
                }
            }
        }
