"""
Code Format Analyzer module
Created by: Barrhann
"""

import pycodestyle
from typing import Dict, Any, List
import ast
import tempfile
import os
from collections import Counter

class CodeFormatAnalyzer:
    def __init__(self):
        self.style_guide = pycodestyle.StyleGuide(quiet=True)

    def analyze(self, notebook_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code formatting in notebook cells.

        Args:
            notebook_content (Dict[str, Any]): Parsed notebook content

        Returns:
            Dict[str, Any]: Analysis results including PEP8 compliance and code style metrics
        """
        code_cells = notebook_content.get('code_cells', [])
        notebook_path = notebook_content.get('path', '')
        
        results = {
            'notebook_path': notebook_path,
            'pep8_violations': [],
            'code_style_metrics': {
                'total_lines': 0,
                'complex_lines': 0,
                'avg_line_length': 0,
                'max_line_length': 0,
                'lines_over_limit': 0
            }
        }

        total_length = 0
        line_lengths = []

        for cell in code_cells:
            code = cell['source']
            if not code.strip():  # Skip empty cells
                continue

            # Write code to temporary file for PEP8 checking
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
                tmp_file.write(code)
                tmp_file_path = tmp_file.name

            try:
                # Create a custom report to collect violations
                class ViolationReport:
                    def __init__(self):
                        self.violations = []
                        self.total_errors = 0
                        self.counters = dict.fromkeys([
                            'logical lines', 'physical lines', 'tokens'
                        ], 0)

                    def error(self, line_number, offset, text, check):
                        """Report an error, according to options."""
                        self.violations.append(f"{text} at line {line_number}")
                        self.total_errors += 1

                    def get_file_results(self):
                        """Return the count of errors."""
                        return self.total_errors

                    def init_file(self, filename, lines, expected=None, line_offset=0):
                        """Initialize the report for a file."""
                        self.filename = filename
                        self.lines = lines
                        self.expected = expected or ()
                        self.line_offset = line_offset
                        self.indent_char = None
                        self.indent_level = 0
                        self.previous_indent_level = 0
                        self.previous_logical = ''
                        self.tokens = []
                        self.counters['tokens'] = 0
                        self.counters['physical lines'] = 0
                        self.counters['logical lines'] = 0

                    def increment_logical_line(self):
                        """Increment the logical line counter."""
                        self.counters['logical lines'] += 1

                    def increment_token(self):
                        """Increment the token counter."""
                        self.counters['tokens'] += 1

                    def new_line(self, line_number):
                        """Process a new physical line."""
                        self.counters['physical lines'] += 1

                    def finish(self):
                        """Clean up the report after all lines are checked."""
                        pass

                # Use a FileReport as the base and extend it with our custom functionality
                report = ViolationReport()
                checker = pycodestyle.Checker(
                    tmp_file_path,
                    quiet=True,
                    report=report
                )
                # Run the checker - this will populate our custom report
                checker.check_all()
                results['pep8_violations'].extend(report.violations)

                # Calculate metrics
                lines = code.split('\n')
                results['code_style_metrics']['total_lines'] += len(lines)
                
                # Line length analysis
                for line in lines:
                    length = len(line)
                    total_length += length
                    line_lengths.append(length)
                    if length > 79:
                        results['code_style_metrics']['lines_over_limit'] += 1
                
                # Analyze code complexity
                try:
                    tree = ast.parse(code)
                    results['code_style_metrics']['complex_lines'] += self._count_complexity(tree)
                except SyntaxError:
                    pass  # Skip complexity analysis for cells with syntax errors

            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass

        # Calculate final metrics
        if results['code_style_metrics']['total_lines'] > 0:
            results['code_style_metrics']['avg_line_length'] = (
                total_length / results['code_style_metrics']['total_lines']
            )
            results['code_style_metrics']['max_line_length'] = max(line_lengths) if line_lengths else 0
        
        return results

    def _count_complexity(self, tree: ast.AST) -> int:
        """Count complex constructs in the AST."""
        complex_nodes = (
            ast.If, ast.For, ast.While, ast.Try,
            ast.FunctionDef, ast.ClassDef,
            ast.ListComp, ast.DictComp, ast.SetComp
        )
        return sum(1 for node in ast.walk(tree) if isinstance(node, complex_nodes))
