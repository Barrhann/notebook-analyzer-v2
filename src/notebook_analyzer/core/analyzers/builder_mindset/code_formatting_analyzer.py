"""Analyzer for code formatting aspects."""
import ast
from typing import Dict, Any, List
from ...base_analyzer import BaseAnalyzer

class CodeFormattingAnalyzer(BaseAnalyzer):
    """Analyzes code formatting including style and complexity."""
    
    def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze code formatting."""
        try:
            tree = ast.parse(code)
            return {
                'style': self._analyze_style(code),
                'complexity': self._analyze_complexity(tree)
            }
        except SyntaxError:
            return self._get_default_metrics()

    def _analyze_style(self, code: str) -> Dict[str, Any]:
        violations = []
        lines = code.splitlines()
        max_line_length = 79  # PEP 8 recommendation
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line.rstrip()) > max_line_length:
                violations.append({
                    'type': 'E501',
                    'line': i,
                    'message': f'Line too long ({len(line)} > {max_line_length} characters)'
                })
            
            # Check indentation
            leading_spaces = len(line) - len(line.lstrip())
            if line.strip() and leading_spaces % 4 != 0:
                violations.append({
                    'type': 'E111',
                    'line': i,
                    'message': 'Indentation is not a multiple of 4'
                })
            
            # Check trailing whitespace
            if line.rstrip() != line:
                violations.append({
                    'type': 'W291',
                    'line': i,
                    'message': 'Trailing whitespace'
                })
            
            # Check mixed tabs and spaces
            if '\t' in line:
                violations.append({
                    'type': 'E101',
                    'line': i,
                    'message': 'Mixed tabs and spaces'
                })

        # Calculate style score
        total_lines = len(lines) or 1  # Avoid division by zero
        violation_ratio = len(violations) / total_lines
        style_score = max(0, 100 - (violation_ratio * 100))
        
        return {
            'violations': violations,
            'total_lines': total_lines,
            'violation_count': len(violations),
            'score': round(style_score, 2)
        }

    def _analyze_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        complexity_metrics = {
            'nested_structures': 0,
            'complex_expressions': 0,
            'long_functions': 0,
            'cognitive_complexity': 0
        }
        
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.nesting_level = 0
                self.current_function_lines = 0
                
            def visit_FunctionDef(self, node):
                self.current_function_lines = node.end_lineno - node.lineno + 1
                if self.current_function_lines > 50:  # Long function threshold
                    complexity_metrics['long_functions'] += 1
                self.generic_visit(node)
            
            def visit_If(self, node):
                self._handle_nesting()
                if isinstance(node.test, ast.BoolOp):
                    complexity_metrics['complex_expressions'] += 1
                self.generic_visit(node)
            
            def visit_For(self, node):
                self._handle_nesting()
                self.generic_visit(node)
            
            def visit_While(self, node):
                self._handle_nesting()
                self.generic_visit(node)
            
            def visit_Try(self, node):
                self._handle_nesting()
                if len(node.handlers) > 2:  # Multiple except clauses
                    complexity_metrics['complex_expressions'] += 1
                self.generic_visit(node)
            
            def _handle_nesting(self):
                self.nesting_level += 1
                if self.nesting_level > 2:  # Deep nesting threshold
                    complexity_metrics['nested_structures'] += 1
                complexity_metrics['cognitive_complexity'] += self.nesting_level
                self.generic_visit(node)
                self.nesting_level -= 1

        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        # Calculate complexity score
        complexity_weights = {
            'nested_structures': 2.0,
            'complex_expressions': 1.5,
            'long_functions': 1.0,
            'cognitive_complexity': 0.5
        }
        
        total_penalty = sum(
            complexity_metrics[metric] * weight
            for metric, weight in complexity_weights.items()
        )
        
        complexity_score = max(0, 100 - total_penalty)
        
        return {
            'metrics': complexity_metrics,
            'score': round(complexity_score, 2)
        }

    def _get_default_metrics(self) -> Dict[str, Any]:
        return {
            'style': {
                'violations': [],
                'total_lines': 0,
                'violation_count': 0,
                'score': 100
            },
            'complexity': {
                'metrics': {
                    'nested_structures': 0,
                    'complex_expressions': 0,
                    'long_functions': 0,
                    'cognitive_complexity': 0
                },
                'score': 100
            }
        }
