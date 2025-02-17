"""Analyzer for code structure and organization."""
import ast
from typing import Dict, Any, List, Set
from collections import defaultdict
from ...base_analyzer import BaseAnalyzer

class CodeStructureAnalyzer(BaseAnalyzer):
    """Analyzes code structure including modularity, organization, and dependencies."""
    
    def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze code structure."""
        try:
            tree = ast.parse(code)
            return {
                'metrics': {
                    'modularity': self._analyze_modularity(tree),
                    'dependencies': self._analyze_dependencies(tree),
                    'organization': self._analyze_organization(tree),
                    'cohesion': self._analyze_cohesion(tree)
                }
            }
        except SyntaxError:
            return self._get_default_metrics()

    def _analyze_modularity(self, tree: ast.AST) -> Dict[str, Any]:
        modules = {
            'classes': [],
            'functions': [],
            'nested_functions': []
        }
        
        class ModularityVisitor(ast.NodeVisitor):
            def visit_ClassDef(self, node):
                methods = []
                attributes = set()
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            'name': item.name,
                            'args': len(item.args.args),
                            'lineno': item.lineno
                        })
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attributes.add(target.id)
                
                modules['classes'].append({
                    'name': node.name,
                    'methods': methods,
                    'attributes': list(attributes),
                    'lineno': node.lineno,
                    'complexity': len(methods) + len(attributes)
                })
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                if isinstance(node.parent, ast.ClassDef):
                    return  # Skip methods as they're handled in visit_ClassDef
                
                nested_functions = []
                for item in ast.walk(node):
                    if isinstance(item, ast.FunctionDef) and item != node:
                        nested_functions.append({
                            'name': item.name,
                            'lineno': item.lineno
                        })
                
                if nested_functions:
                    modules['nested_functions'].extend(nested_functions)
                else:
                    modules['functions'].append({
                        'name': node.name,
                        'args': len(node.args.args),
                        'lineno': node.lineno,
                        'complexity': self._calculate_function_complexity(node)
                    })
                
            def _calculate_function_complexity(self, node):
                complexity = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While)):
                        complexity += 1
                return complexity
        
        ModularityVisitor().visit(tree)
        
        # Calculate modularity score
        total_components = (
            len(modules['classes']) +
            len(modules['functions']) +
            len(modules['nested_functions'])
        )
        
        if total_components == 0:
            modularity_score = 100
        else:
            # Penalize for excessive nesting and complexity
            nested_ratio = len(modules['nested_functions']) / total_components
            avg_complexity = sum(
                c['complexity'] for c in modules['classes'] + modules['functions']
            ) / total_components if total_components > 0 else 0
            
            modularity_score = 100 - (nested_ratio * 30) - min(30, avg_complexity * 5)
        
        return {
            'components': modules,
            'total_components': total_components,
            'score': round(max(0, modularity_score), 2)
        }

    def _analyze_dependencies(self, tree: ast.AST) -> Dict[str, Any]:
        dependencies = {
            'imports': [],
            'internal_deps': [],
            'cyclic_deps': []
        }
        
        class DependencyVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_scope = None
                self.dependency_graph = defaultdict(set)
                
            def visit_Import(self, node):
                for name in node.names:
                    dependencies['imports'].append({
                        'name': name.name,
                        'asname': name.asname,
                        'lineno': node.lineno
                    })
                
            def visit_ImportFrom(self, node):
                if node.module:
                    for name in node.names:
                        dependencies['imports'].append({
                            'name': f"{node.module}.{name.name}",
                            'asname': name.asname,
                            'lineno': node.lineno
                        })
            
            def visit_FunctionDef(self, node):
                prev_scope = self.current_scope
                self.current_scope = node.name
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                        if child.id in [f.name for f in modules['functions']]:
                            self.dependency_graph[self.current_scope].add(child.id)
                            dependencies['internal_deps'].append({
                                'from': self.current_scope,
                                'to': child.id,
                                'lineno': child.lineno
                            })
                
                self.generic_visit(node)
                self.current_scope = prev_scope
        
        visitor = DependencyVisitor()
        visitor.visit(tree)
        
        # Detect cyclic dependencies
        def find_cycles(graph):
            visited = set()
            path = []
            
            def dfs(node):
                if node in path:
                    cycle = path[path.index(node):]
                    dependencies['cyclic_deps'].append({
                        'components': cycle,
                        'length': len(cycle)
                    })
                    return
                
                if node in visited:
                    return
                    
                visited.add(node)
                path.append(node)
                
                for neighbor in graph[node]:
                    dfs(neighbor)
                    
                path.pop()
            
            for node in graph:
                if node not in visited:
                    dfs(node)
        
        find_cycles(visitor.dependency_graph)
        
        # Calculate dependency score
        import_count = len(dependencies['imports'])
        internal_dep_count = len(dependencies['internal_deps'])
        cyclic_dep_count = len(dependencies['cyclic_deps'])
        
        dependency_score = 100
        if import_count + internal_dep_count > 0:
            # Penalize for excessive dependencies and cyclic dependencies
            dependency_score -= min(30, (import_count + internal_dep_count) * 2)
            dependency_score -= cyclic_dep_count * 20
        
        return {
            'dependencies': dependencies,
            'score': round(max(0, dependency_score), 2)
        }

    def _analyze_organization(self, tree: ast.AST) -> Dict[str, Any]:
        organization = {
            'top_level_structure': [],
            'scope_depth': defaultdict(int),
            'code_blocks': []
        }
        
        class OrganizationVisitor(ast.NodeVisitor):
            def __init__(self):
                self.depth = 0
                self.current_block = None
                
            def visit(self, node):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    organization['top_level_structure'].append({
                        'type': node.__class__.__name__,
                        'name': node.name,
                        'lineno': node.lineno
                    })
                
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.If, ast.For, ast.While)):
                    self.depth += 1
                    organization['scope_depth'][self.depth] += 1
                    
                    if hasattr(node, 'name'):
                        block_name = node.name
                    else:
                        block_name = f"{node.__class__.__name__}_{node.lineno}"
                    
                    organization['code_blocks'].append({
                        'type': node.__class__.__name__,
                        'name': block_name,
                        'depth': self.depth,
                        'lineno': node.lineno
                    })
                    
                    prev_block = self.current_block
                    self.current_block = block_name
                    self.generic_visit(node)
                    self.current_block = prev_block
                    self.depth -= 1
                else:
                    self.generic_visit(node)
        
        OrganizationVisitor().visit(tree)
        
        # Calculate organization score
        max_depth = max(organization['scope_depth'].keys()) if organization['scope_depth'] else 0
        deep_blocks = sum(
            count for depth, count in organization['scope_depth'].items()
            if depth > 3
        )
        
        organization_score = 100
        if max_depth > 0:
            # Penalize for deep nesting
            organization_score -= min(40, max_depth * 10)
            # Penalize for too many deeply nested blocks
            organization_score -= min(30, deep_blocks * 5)
        
        return {
            'structure': organization,
            'max_depth': max_depth,
            'score': round(max(0, organization_score), 2)
        }

    def _analyze_cohesion(self, tree: ast.AST) -> Dict[str, Any]:
        cohesion = {
            'method_relationships': defaultdict(list),
            'shared_attributes': defaultdict(set),
            'coupling_score': 0
        }
        
        class CohesionVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_class = None
                self.current_method = None
                self.used_attributes = defaultdict(set)
                
            def visit_ClassDef(self, node):
                prev_class = self.current_class
                self.current_class = node.name
                self.generic_visit(node)
                self.current_class = prev_class
                
            def visit_FunctionDef(self, node):
                if self.current_class:
                    prev_method = self.current_method
                    self.current_method = node.name
                    
                    # Analyze method body for attribute usage
                    for child in ast.walk(node):
                        if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name):
                            if child.value.id == 'self':
                                self.used_attributes[self.current_method].add(child.attr)
                    
                    self.generic_visit(node)
                    self.current_method = prev_method
                else:
                    self.generic_visit(node)
        
        visitor = CohesionVisitor()
        visitor.visit(tree)
        
        # Calculate method relationships based on shared attributes
        for method1, attrs1 in visitor.used_attributes.items():
            for method2, attrs2 in visitor.used_attributes.items():
                if method1 < method2:  # Avoid duplicates
                    shared = attrs1.intersection(attrs2)
                    if shared:
                        cohesion['method_relationships'][method1].append({
                            'method': method2,
                            'shared_attributes': list(shared)
                        })
                        cohesion['shared_attributes'][method1].update(shared)
        
        # Calculate cohesion score
        total_methods = len(visitor.used_attributes)
        if total_methods <= 1:
            cohesion_score = 100
        else:
            related_methods = sum(len(rels) for rels in cohesion['method_relationships'].values())
            max_possible_relations = (total_methods * (total_methods - 1)) / 2
            cohesion_score = (related_methods / max_possible_relations * 100) if max_possible_relations > 0 else 100
        
        return {
            'relationships': dict(cohesion['method_relationships']),
            'shared_attributes': {k: list(v) for k, v in cohesion['shared_attributes'].items()},
            'score': round(cohesion_score, 2)
        }

    def _get_default_metrics(self) -> Dict[str, Any]:
        return {
            'metrics': {
                'modularity': {
                    'components': {
                        'classes': [],
                        'functions': [],
                        'nested_functions': []
                    },
                    'total_components': 0,
                    'score': 100
                },
                'dependencies': {
                    'dependencies': {
                        'imports': [],
                        'internal_deps': [],
                        'cyclic_deps': []
                    },
                    'score': 100
                },
                'organization': {
                    'structure': {
                        'top_level_structure': [],
                        'scope_depth': {},
                        'code_blocks': []
                    },
                    'max_depth': 0,
                    'score': 100
                },
                'cohesion': {
                    'relationships': {},
                    'shared_attributes': {},
                    'score': 100
                }
            }
        }
