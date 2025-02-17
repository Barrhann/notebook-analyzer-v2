"""Analyzer for code conciseness and efficiency."""
import ast
from typing import Dict, Any, List, Set
from collections import defaultdict
from ...base_analyzer import BaseAnalyzer

class CodeConcisenessAnalyzer(BaseAnalyzer):
    """Analyzes code conciseness and efficiency."""
    
    def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze code conciseness."""
        try:
            tree = ast.parse(code)
            return {
                'metrics': {
                    'redundancy': self._analyze_code_redundancy(tree),
                    'variable_usage': self._analyze_variable_usage(tree),
                    'code_density': self._analyze_code_density(tree),
                    'simplification': self._analyze_simplification_opportunities(tree)
                }
            }
        except SyntaxError:
            return self._get_default_metrics()

    def _analyze_code_redundancy(self, tree: ast.AST) -> Dict[str, Any]:
        redundant_patterns = []
        similar_blocks = defaultdict(list)
        
        class RedundancyVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Hash the function body to identify similar functions
                body_hash = hash(ast.dump(node))
                similar_blocks[body_hash].append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'type': 'function'
                })
                self.generic_visit(node)
            
            def visit_For(self, node):
                # Check for repeated loop patterns
                loop_hash = hash(ast.dump(node.body))
                similar_blocks[loop_hash].append({
                    'type': 'loop',
                    'lineno': node.lineno
                })
                self.generic_visit(node)
            
            def visit_If(self, node):
                # Check for repeated conditional blocks
                if_hash = hash(ast.dump(node.body))
                similar_blocks[if_hash].append({
                    'type': 'conditional',
                    'lineno': node.lineno
                })
                self.generic_visit(node)
        
        RedundancyVisitor().visit(tree)
        
        # Identify redundant patterns
        for block_hash, occurrences in similar_blocks.items():
            if len(occurrences) > 1:
                redundant_patterns.append({
                    'type': occurrences[0]['type'],
                    'occurrences': occurrences,
                    'count': len(occurrences)
                })
        
        # Calculate redundancy score
        total_blocks = sum(len(blocks) for blocks in similar_blocks.values())
        redundant_blocks = sum(pattern['count'] for pattern in redundant_patterns)
        
        if total_blocks == 0:
            redundancy_score = 100
        else:
            redundancy_ratio = redundant_blocks / total_blocks
            redundancy_score = max(0, 100 - (redundancy_ratio * 100))
        
        return {
            'patterns': redundant_patterns,
            'total_blocks': total_blocks,
            'redundant_blocks': redundant_blocks,
            'score': round(redundancy_score, 2)
        }

    def _analyze_variable_usage(self, tree: ast.AST) -> Dict[str, Any]:
        class VariableUsageVisitor(ast.NodeVisitor):
            def __init__(self):
                self.declarations = {}
                self.usages = defaultdict(list)
                self.scope_stack = ['global']
                
            def visit_Name(self, node):
                scope = self.scope_stack[-1]
                if isinstance(node.ctx, ast.Store):
                    self.declarations[(scope, node.id)] = node.lineno
                elif isinstance(node.ctx, ast.Load):
                    self.usages[(scope, node.id)].append(node.lineno)
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                self.scope_stack.append(node.name)
                self.generic_visit(node)
                self.scope_stack.pop()
        
        visitor = VariableUsageVisitor()
        visitor.visit(tree)
        
        unused_vars = []
        inefficient_vars = []
        
        for (scope, var), decl_line in visitor.declarations.items():
            usages = visitor.usages.get((scope, var), [])
            if not usages:
                unused_vars.append({
                    'name': var,
                    'scope': scope,
                    'line': decl_line
                })
            elif len(usages) == 1:
                inefficient_vars.append({
                    'name': var,
                    'scope': scope,
                    'declaration': decl_line,
                    'usage': usages[0]
                })
        
        total_vars = len(visitor.declarations)
        if total_vars == 0:
            usage_score = 100
        else:
            usage_score = max(0, 100 - (
                (len(unused_vars) * 20 + len(inefficient_vars) * 10) / total_vars
            ))
        
        return {
            'unused_variables': unused_vars,
            'inefficient_variables': inefficient_vars,
            'total_variables': total_vars,
            'score': round(usage_score, 2)
        }

    def _analyze_code_density(self, tree: ast.AST) -> Dict[str, Any]:
        class DensityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.operations = 0
                self.lines = set()
                self.complex_expressions = []
                
            def visit_BinOp(self, node):
                self.operations += 1
                if hasattr(node, 'lineno'):
                    self.lines.add(node.lineno)
                self.generic_visit(node)
            
            def visit_Compare(self, node):
                if len(node.ops) > 1:
                    self.complex_expressions.append({
                        'type': 'comparison',
                        'lineno': node.lineno
                    })
                self.operations += len(node.ops)
                self.lines.add(node.lineno)
                self.generic_visit(node)
            
            def visit_ListComp(self, node):
                self.complex_expressions.append({
                    'type': 'comprehension',
                    'lineno': node.lineno
                })
                self.operations += 1
                self.lines.add(node.lineno)
                self.generic_visit(node)
        
        visitor = DensityVisitor()
        visitor.visit(tree)
        
        total_lines = len(visitor.lines)
        if total_lines == 0:
            density_score = 100
        else:
            operations_per_line = visitor.operations / total_lines
            # Ideal density is between 1-3 operations per line
            if operations_per_line <= 3:
                density_score = 100
            else:
                density_score = max(0, 100 - ((operations_per_line - 3) * 20))
        
        return {
            'operations': visitor.operations,
            'lines': total_lines,
            'density': round(visitor.operations / total_lines if total_lines > 0 else 0, 2),
            'complex_expressions': visitor.complex_expressions,
            'score': round(density_score, 2)
        }

    def _analyze_simplification_opportunities(self, tree: ast.AST) -> Dict[str, Any]:
        opportunities = []
        
        class SimplificationVisitor(ast.NodeVisitor):
            def visit_If(self, node):
                # Check for simplifiable if-else structures
                if isinstance(node.test, ast.Compare) and len(node.body) == 1 and node.orelse:
                    if isinstance(node.body[0], ast.Return) and len(node.orelse) == 1:
                        if isinstance(node.orelse[0], ast.Return):
                            opportunities.append({
                                'type': 'conditional',
                                'lineno': node.lineno,
                                'message': 'Could be simplified to a single return with conditional expression'
                            })
                self.generic_visit(node)
            
            def visit_For(self, node):
                # Check for loops that could use list comprehension
                if len(node.body) == 1:
                    if isinstance(node.body[0], (ast.Append, ast.Assign)):
                        opportunities.append({
                            'type': 'loop',
                            'lineno': node.lineno,
                            'message': 'Could be replaced with list comprehension'
                        })
                self.generic_visit(node)
            
            def visit_Compare(self, node):
                # Check for chained comparisons
                if len(node.ops) > 1:
                    opportunities.append({
                        'type': 'comparison',
                        'lineno': node.lineno,
                        'message': 'Could use chained comparison'
                    })
                self.generic_visit(node)
        
        SimplificationVisitor().visit(tree)
        
        # Calculate simplification score
        total_nodes = sum(1 for _ in ast.walk(tree))
        if total_nodes == 0:
            simplification_score = 100
        else:
            simplification_score = max(0, 100 - (len(opportunities) * 10))
        
        return {
            'opportunities': opportunities,
            'count': len(opportunities),
            'score': round(simplification_score, 2)
        }

    def _get_default_metrics(self) -> Dict[str, Any]:
        return {
            'metrics': {
                'redundancy': {
                    'patterns': [],
                    'total_blocks': 0,
                    'redundant_blocks': 0,
                    'score': 100
                },
                'variable_usage': {
                    'unused_variables': [],
                    'inefficient_variables': [],
                    'total_variables': 0,
                    'score': 100
                },
                'code_density': {
                    'operations': 0,
                    'lines': 0,
                    'density': 0,
                    'complex_expressions': [],
                    'score': 100
                },
                'simplification': {
                    'opportunities': [],
                    'count': 0,
                    'score': 100
                }
            }
        }
