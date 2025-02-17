"""Analyzer for code reusability and maintainability."""
import ast
from typing import Dict, Any, List, Set
from collections import defaultdict
from ...base_analyzer import BaseAnalyzer

class CodeReusabilityAnalyzer(BaseAnalyzer):
    """Analyzes code reusability and maintainability patterns."""

    def __init__(self):
        super().__init__()
        self.standard_libs = {
            'os', 'sys', 'datetime', 'collections', 'itertools',
            'functools', 'math', 'random', 'json', 're'
        }
        self.data_science_libs = {
            'pandas', 'numpy', 'scipy', 'sklearn',
            'matplotlib', 'seaborn', 'plotly'
        }

    def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze code reusability."""
        try:
            tree = ast.parse(code)
            return {
                'metrics': {
                    'function_reusability': self._analyze_function_reusability(tree),
                    'code_modularity': self._analyze_code_modularity(tree),
                    'dependency_management': self._analyze_dependency_management(tree),
                    'interface_design': self._analyze_interface_design(tree)
                }
            }
        except SyntaxError:
            return self._get_default_metrics()

    def _analyze_function_reusability(self, tree: ast.AST) -> Dict[str, Any]:
        functions = []
        reusability_issues = []
        
        class FunctionVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                function_info = {
                    'name': node.name,
                    'args': len(node.args.args),
                    'returns': self._has_return_annotation(node),
                    'docstring': ast.get_docstring(node) is not None,
                    'lineno': node.lineno,
                    'complexity': self._analyze_function_complexity(node)
                }
                
                # Check for reusability issues
                if function_info['args'] > 5:
                    reusability_issues.append({
                        'type': 'too_many_args',
                        'function': node.name,
                        'lineno': node.lineno,
                        'message': f"Function has too many arguments ({function_info['args']})"
                    })
                
                if not function_info['docstring']:
                    reusability_issues.append({
                        'type': 'missing_docstring',
                        'function': node.name,
                        'lineno': node.lineno,
                        'message': "Function lacks docstring"
                    })
                
                if not function_info['returns']:
                    reusability_issues.append({
                        'type': 'missing_return_type',
                        'function': node.name,
                        'lineno': node.lineno,
                        'message': "Function lacks return type annotation"
                    })
                
                functions.append(function_info)
                self.generic_visit(node)
            
            def _has_return_annotation(self, node):
                return node.returns is not None
            
            def _analyze_function_complexity(self, node):
                complexity = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While)):
                        complexity += 1
                return complexity
        
        FunctionVisitor().visit(tree)
        
        # Calculate reusability score
        if not functions:
            reusability_score = 100
        else:
            base_score = 100
            for issue in reusability_issues:
                if issue['type'] == 'too_many_args':
                    base_score -= 15
                elif issue['type'] == 'missing_docstring':
                    base_score -= 10
                elif issue['type'] == 'missing_return_type':
                    base_score -= 5
            
            reusability_score = max(0, base_score)
        
        return {
            'functions': functions,
            'issues': reusability_issues,
            'score': round(reusability_score, 2)
        }

    def _analyze_code_modularity(self, tree: ast.AST) -> Dict[str, Any]:
        modules = {
            'classes': [],
            'functions': [],
            'dependencies': defaultdict(set)
        }
        
        class ModularityVisitor(ast.NodeVisitor):
            def visit_ClassDef(self, node):
                class_info = {
                    'name': node.name,
                    'methods': [],
                    'attributes': set(),
                    'dependencies': set(),
                    'lineno': node.lineno
                }
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        class_info['methods'].append(item.name)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_info['attributes'].add(target.id)
                
                modules['classes'].append(class_info)
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                if not isinstance(node.parent, ast.ClassDef):
                    function_deps = set()
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                            function_deps.add(child.id)
                    
                    modules['functions'].append({
                        'name': node.name,
                        'dependencies': list(function_deps),
                        'lineno': node.lineno
                    })
                    
                    if function_deps:
                        modules['dependencies'][node.name].update(function_deps)
                
                self.generic_visit(node)
        
        ModularityVisitor().visit(tree)
        
        # Calculate modularity score
        total_components = len(modules['classes']) + len(modules['functions'])
        if total_components == 0:
            modularity_score = 100
        else:
            base_score = 80
            # Bonus for good class/function ratio
            if modules['classes']:
                class_method_ratio = sum(len(c['methods']) for c in modules['classes']) / len(modules['classes'])
                if 2 <= class_method_ratio <= 7:
                    base_score += 10
            
            # Penalty for high coupling
            avg_dependencies = sum(len(deps) for deps in modules['dependencies'].values())
            if total_components > 0:
                avg_dependencies /= total_components
                if avg_dependencies > 3:
                    base_score -= min(30, (avg_dependencies - 3) * 10)
            
            modularity_score = max(0, base_score)
        
        return {
            'components': modules,
            'score': round(modularity_score, 2)
        }

    def _analyze_dependency_management(self, tree: ast.AST) -> Dict[str, Any]:
        dependencies = {
            'imports': [],
            'external_deps': set(),
            'internal_deps': set()
        }
        
        class DependencyVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    import_info = {
                        'module': alias.name,
                        'alias': alias.asname,
                        'type': self._categorize_import(alias.name),
                        'lineno': node.lineno
                    }
                    dependencies['imports'].append(import_info)
                    self._update_dep_sets(alias.name)
                
            def visit_ImportFrom(self, node):
                if node.module:
                    for alias in node.names:
                        import_info = {
                            'module': f"{node.module}.{alias.name}",
                            'alias': alias.asname,
                            'type': self._categorize_import(node.module),
                            'lineno': node.lineno
                        }
                        dependencies['imports'].append(import_info)
                        self._update_dep_sets(node.module)
            
            def _categorize_import(self, module_name):
                base_module = module_name.split('.')[0]
                if base_module in self.standard_libs:
                    return 'standard'
                elif base_module in self.data_science_libs:
                    return 'data_science'
                else:
                    return 'external'
            
            def _update_dep_sets(self, module_name):
                base_module = module_name.split('.')[0]
                if base_module not in self.standard_libs:
                    if base_module in self.data_science_libs:
                        dependencies['external_deps'].add(base_module)
                    else:
                        dependencies['internal_deps'].add(base_module)
        
        DependencyVisitor().visit(tree)
        
        # Calculate dependency management score
        if not dependencies['imports']:
            dep_score = 100
        else:
            base_score = 100
            # Penalty for too many external dependencies
            external_dep_count = len(dependencies['external_deps'])
            if external_dep_count > 5:
                base_score -= min(30, (external_dep_count - 5) * 5)
            
            # Penalty for not using aliases for long import paths
            long_imports_no_alias = sum(
                1 for imp in dependencies['imports']
                if len(imp['module'].split('.')) > 2 and not imp['alias']
            )
            base_score -= min(20, long_imports_no_alias * 5)
            
            dep_score = max(0, base_score)
        
        return {
            'imports': dependencies['imports'],
            'external_dependencies': list(dependencies['external_deps']),
            'internal_dependencies': list(dependencies['internal_deps']),
            'score': round(dep_score, 2)
        }

    def _analyze_interface_design(self, tree: ast.AST) -> Dict[str, Any]:
        interfaces = {
            'public_methods': [],
            'private_methods': [],
            'properties': [],
            'interface_issues': []
        }
        
        class InterfaceVisitor(ast.NodeVisitor):
            def visit_ClassDef(self, node):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            'name': item.name,
                            'class': node.name,
                            'lineno': item.lineno,
                            'docstring': ast.get_docstring(item) is not None,
                            'args': len(item.args.args) - 1  # Subtract 'self'
                        }
                        
                        if item.name.startswith('_'):
                            interfaces['private_methods'].append(method_info)
                        else:
                            interfaces['public_methods'].append(method_info)
                            
                            # Check interface design issues
                            if not method_info['docstring']:
                                interfaces['interface_issues'].append({
                                    'type': 'missing_docstring',
                                    'method': item.name,
                                    'class': node.name,
                                    'lineno': item.lineno
                                })
                            
                            if method_info['args'] > 4:
                                interfaces['interface_issues'].append({
                                    'type': 'complex_interface',
                                    'method': item.name,
                                    'class': node.name,
                                    'lineno': item.lineno
                                })
                    
                    elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        interfaces['properties'].append({
                            'name': item.target.id,
                            'class': node.name,
                            'lineno': item.lineno,
                            'type': item.annotation.id if isinstance(item.annotation, ast.Name) else None
                        })
                
                self.generic_visit(node)
        
        InterfaceVisitor().visit(tree)
        
        # Calculate interface design score
        if not interfaces['public_methods'] and not interfaces['properties']:
            interface_score = 100
        else:
            base_score = 100
            # Penalty for interface issues
            for issue in interfaces['interface_issues']:
                if issue['type'] == 'missing_docstring':
                    base_score -= 10
                elif issue['type'] == 'complex_interface':
                    base_score -= 15
            
            # Bonus for good public/private method ratio
            total_methods = len(interfaces['public_methods']) + len(interfaces['private_methods'])
            if total_methods > 0:
                public_ratio = len(interfaces['public_methods']) / total_methods
                if 0.25 <= public_ratio <= 0.75:
                    base_score += 10
            
            interface_score = max(0, base_score)
        
        return {
            'methods': {
                'public': interfaces['public_methods'],
                'private': interfaces['private_methods']
            },
            'properties': interfaces['properties'],
            'issues': interfaces['interface_issues'],
            'score': round(interface_score, 2)
        }

    def _get_default_metrics(self) -> Dict[str, Any]:
        return {
            'metrics': {
                'function_reusability': {
                    'functions': [],
                    'issues': [],
                    'score': 100
                },
                'code_modularity': {
                    'components': {
                        'classes': [],
                        'functions': [],
                        'dependencies': {}
                    },
                    'score': 100
                },
                'dependency_management': {
                    'imports': [],
                    'external_dependencies': [],
                    'internal_dependencies': [],
                    'score': 100
                },
                'interface_design': {
                    'methods': {
                        'public': [],
                        'private': []
                    },
                    'properties': [],
                    'issues': [],
                    'score': 100
                }
            }
        }
