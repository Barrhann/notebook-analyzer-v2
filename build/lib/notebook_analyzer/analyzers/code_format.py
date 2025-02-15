"""
Code Format Analyzer module
Created by: Barrhann
"""

import pycodestyle
from typing import Dict, Any, List
import ast
import tempfile
import os

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
        code_cells = notebook_content['code_cells']
        
        results = {
            'pep8_violations': [],
            'code_style_metrics': {
                'total_lines': 0,
                'complex_lines': 0,
                'avg_line_length': 0,
            },
            'positive_findings': [],
            'negative_findings': []
        }

        total_length = 0
        total_violations = 0

        for cell in code_cells:
            code = cell['source']
            if not code.strip():  # Skip empty cells
                continue

            # Write code to temporary file for PEP8 checking
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
                tmp_file.write(code)
                tmp_file_path = tmp_file.name

            try:
                # Run PEP8 checker on temporary file
                checker = pycodestyle.Checker(tmp_file_path, quiet=True)
                violations = checker.check_all()
                total_violations += violations

                # Calculate metrics
                lines = code.split('\n')
                results['code_style_metrics']['total_lines'] += len(lines)
                total_length += sum(len(line) for line in lines)
                
                # Analyze code complexity
                try:
                    tree = ast.parse(code)
                    results['code_style_metrics']['complex_lines'] += sum(
                        1 for node in ast.walk(tree)
                        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try))
                    )
                except SyntaxError:
                    pass  # Skip complexity analysis for cells with syntax errors

            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass

        # Update violations count
        results['pep8_violations'] = total_violations

        # Calculate average line length
        if results['code_style_metrics']['total_lines'] > 0:
            results['code_style_metrics']['avg_line_length'] = (
                total_length / results['code_style_metrics']['total_lines']
            )

        # Generate findings
        self._generate_findings(results)
        
        return results

    def _generate_findings(self, results: Dict[str, Any]):
        """Generate positive and negative findings based on the analysis."""
        if results['pep8_violations'] == 0:
            results['positive_findings'].append(
                "Code follows PEP8 standards perfectly"
            )
        else:
            results['negative_findings'].append(
                f"Found {results['pep8_violations']} PEP8 violations"
            )

        if results['code_style_metrics']['avg_line_length'] <= 79:
            results['positive_findings'].append(
                "Line lengths are within recommended PEP8 limits"
            )
        else:
            results['negative_findings'].append(
                "Average line length exceeds PEP8 recommendation of 79 characters"
            )
