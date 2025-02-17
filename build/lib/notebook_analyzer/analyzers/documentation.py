"""
Documentation Analyzer module
Created by: Barrhann
"""

from typing import Dict, Any
import re

class DocumentationAnalyzer:
    def analyze(self, notebook_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze documentation quality in notebook cells.

        Args:
            notebook_content (Dict[str, Any]): Parsed notebook content

        Returns:
            Dict[str, Any]: Analysis results including documentation metrics
        """
        markdown_cells = notebook_content['markdown_cells']
        code_cells = notebook_content['code_cells']
        
        results = {
            'markdown_metrics': self._analyze_markdown(markdown_cells),
            'code_comments_metrics': self._analyze_code_comments(code_cells),
            'positive_findings': [],
            'negative_findings': []
        }
        
        self._generate_findings(results)
        
        return results

    def _analyze_markdown(self, markdown_cells: list) -> Dict[str, Any]:
        """Analyze markdown cells for quality and completeness."""
        total_cells = len(markdown_cells)
        total_length = sum(len(cell['source']) for cell in markdown_cells)
        has_headers = sum(1 for cell in markdown_cells
                         if any(line.startswith('#') for line in cell['source'].split('\n')))
        
        return {
            'total_cells': total_cells,
            'avg_length': total_length / max(total_cells, 1),
            'cells_with_headers': has_headers,
            'documentation_ratio': total_length / max(total_cells, 1)
        }

    def _analyze_code_comments(self, code_cells: list) -> Dict[str, Any]:
        """Analyze code comments for coverage and quality."""
        total_lines = 0
        commented_lines = 0
        docstring_count = 0
        
        for cell in code_cells:
            code = cell['source']
            lines = code.split('\n')
            total_lines += len(lines)
            
            # Count comments
            commented_lines += sum(1 for line in lines if line.strip().startswith('#'))
            
            # Count docstrings
            docstring_count += len(re.findall(r'"""[\s\S]*?"""', code))
        
        return {
            'total_lines': total_lines,
            'commented_lines': commented_lines,
            'comment_ratio': commented_lines / max(total_lines, 1),
            'docstring_count': docstring_count
        }

    def _generate_findings(self, results: Dict[str, Any]):
        """Generate positive and negative findings based on the analysis."""
        markdown_metrics = results['markdown_metrics']
        code_comments_metrics = results['code_comments_metrics']

        # Markdown findings
        if markdown_metrics['total_cells'] > 0:
            if markdown_metrics['avg_length'] > 100:
                results['positive_findings'].append(
                    "Detailed markdown documentation present"
                )
            else:
                results['negative_findings'].append(
                    "Markdown documentation could be more detailed"
                )

        # Code comments findings
        if code_comments_metrics['comment_ratio'] >= 0.2:
            results['positive_findings'].append(
                "Good code comment coverage"
            )
        else:
            results['negative_findings'].append(
                "Insufficient code comments"
            )

        if code_comments_metrics['docstring_count'] > 0:
            results['positive_findings'].append(
                f"Found {code_comments_metrics['docstring_count']} docstrings"
            )
