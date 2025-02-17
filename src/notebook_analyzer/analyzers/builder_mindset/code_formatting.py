"""
Code Formatting Analyzer Module.

This module provides the analyzer for code formatting metrics in Jupyter notebooks.
It evaluates code style, indentation, line length, and other PEP 8 compliance aspects.

Created by: Barrhann
Date: 2025-02-17
"""

import ast
from typing import Dict, Any, List, Tuple
import re
from ..base_analyzer import BaseAnalyzer, AnalysisError
import autopep8
import black

class CodeFormattingAnalyzer(BaseAnalyzer):
    """
    Analyzer for code formatting and style metrics.
    
    This analyzer evaluates:
    - PEP 8 compliance
    - Code indentation consistency
    - Line length
    - Whitespace usage
    - Variable naming conventions
    - Import statement organization
    
    Attributes:
        MAX_LINE_LENGTH (int): Maximum recommended line length
        INDENT_SIZE (int): Standard indentation size in spaces
        NAME_PATTERNS (Dict[str, str]): Regex patterns for naming conventions
    """

    MAX_LINE_LENGTH = 79  # PEP 8 recommended
    INDENT_SIZE = 4
    NAME_PATTERNS = {
        'variable': r'^[a-z_][a-z0-9_]*$',
        'constant': r'^[A-Z_][A-Z0-9_]*$',
        'class': r'^[A-Z][a-zA-Z0-9]*$',
        'function': r'^[a-z_][a-z0-9_]*$'
    }

    def __init__(self):
        """Initialize the code formatting analyzer."""
        super().__init__(name="Code Formatting")
        self.black_mode = black.Mode()
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'style_violations': [],
            'line_lengths': [],
            'indentation_issues': [],
            'naming_violations': [],
            'import_organization': [],
            'whitespace_issues': []
        }

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'builder_mindset'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze code formatting and style.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing:
                - score: Overall formatting score (0-100)
                - findings: List of specific findings
                - details: Detailed metrics and issues found
                - suggestions: Improvement suggestions

        Raises:
            AnalysisError: If analysis fails
            ValueError: If code is invalid
        """
        try:
            self.prepare_analysis(code)
            self._reset_metrics()

            # Parse the code
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                raise AnalysisError(f"Syntax error in code: {str(e)}")

            # Perform various formatting checks
            style_score = self._check_pep8_compliance(code)
            indent_score = self._check_indentation(code)
            naming_score = self._check_naming_conventions(tree)
            import_score = self._check_import_organization(tree)
            whitespace_score = self._check_whitespace(code)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (style_score, 0.3),    # 30% weight
                (indent_score, 0.25),   # 25% weight
                (naming_score, 0.2),    # 20% weight
                (import_score, 0.15),   # 15% weight
                (whitespace_score, 0.1) # 10% weight
            ])

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(),
                'details': {
                    'style_score': style_score,
                    'indentation_score': indent_score,
                    'naming_score': naming_score,
                    'import_organization_score': import_score,
                    'whitespace_score': whitespace_score,
                    'metrics': self.metrics
                },
                'suggestions': self._generate_suggestions()
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing code formatting: {str(e)}")

    def _check_pep8_compliance(self, code: str) -> float:
        """
        Check code compliance with PEP 8 style guide.

        Args:
            code (str): Code to check

        Returns:
            float: Style compliance score (0-100)
        """
        try:
            # Use autopep8 to identify style issues
            fixed_code = autopep8.fix_code(code, options={'aggressive': 1})
            diff_lines = len(fixed_code.splitlines()) - len(code.splitlines())
            
            # Calculate style score based on number of fixes needed
            if diff_lines == 0:
                return 100.0
            
            # Deduct points based on number of style issues
            score = max(0, 100 - (diff_lines * 5))
            
            # Record style violations
            if diff_lines > 0:
                self.metrics['style_violations'].append(
                    f"Found {diff_lines} style issues that need fixing"
                )
            
            return score

        except Exception as e:
            self.metrics['style_violations'].append(f"Style check error: {str(e)}")
            return 50.0  # Default to middle score on error

    def _check_indentation(self, code: str) -> float:
        """
        Check code indentation consistency.

        Args:
            code (str): Code to check

        Returns:
            float: Indentation consistency score (0-100)
        """
        lines = code.splitlines()
        issues = []
        
        for i, line in enumerate(lines, 1):
            if line.strip():  # Skip empty lines
                # Check if indentation is multiple of INDENT_SIZE
                indent_level = len(line) - len(line.lstrip())
                if indent_level % self.INDENT_SIZE != 0:
                    issues.append(f"Line {i}: Invalid indentation level")

        # Calculate score based on number of issues
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['indentation_issues'].extend(issues)
        return score

    def _check_naming_conventions(self, tree: ast.AST) -> float:
        """
        Check adherence to Python naming conventions.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Naming convention compliance score (0-100)
        """
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not re.match(self.NAME_PATTERNS['class'], node.name):
                    issues.append(f"Class name '{node.name}' doesn't follow conventions")
                    
            elif isinstance(node, ast.FunctionDef):
                if not re.match(self.NAME_PATTERNS['function'], node.name):
                    issues.append(f"Function name '{node.name}' doesn't follow conventions")
                    
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                # Check variables and constants
                if node.id.isupper() and not re.match(self.NAME_PATTERNS['constant'], node.id):
                    issues.append(f"Constant name '{node.id}' doesn't follow conventions")
                elif not node.id.isupper() and not re.match(self.NAME_PATTERNS['variable'], node.id):
                    issues.append(f"Variable name '{node.id}' doesn't follow conventions")

        # Calculate score based on number of issues
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 5))
        self.metrics['naming_violations'].extend(issues)
        return score

    def _check_import_organization(self, tree: ast.AST) -> float:
        """
        Check if imports are properly organized.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Import organization score (0-100)
        """
        issues = []
        import_nodes = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_nodes.append(node)

        if not import_nodes:
            return 100.0

        # Check import ordering and grouping
        last_import_line = -1
        for node in import_nodes:
            if hasattr(node, 'lineno'):
                if last_import_line > -1 and node.lineno > last_import_line + 1:
                    issues.append("Imports are not grouped together")
                last_import_line = node.lineno

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['import_organization'].extend(issues)
        return score

    def _check_whitespace(self, code: str) -> float:
        """
        Check whitespace usage in code.

        Args:
            code (str): Code to check

        Returns:
            float: Whitespace usage score (0-100)
        """
        issues = []
        lines = code.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check trailing whitespace
            if line.rstrip() != line:
                issues.append(f"Line {i}: Trailing whitespace")
                
            # Check multiple spaces between tokens
            if '  ' in line.strip():
                issues.append(f"Line {i}: Multiple spaces used")
                
            # Check line length
            if len(line) > self.MAX_LINE_LENGTH:
                self.metrics['line_lengths'].append(
                    f"Line {i}: Length {len(line)} exceeds {self.MAX_LINE_LENGTH}"
                )

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 5))
        self.metrics['whitespace_issues'].extend(issues)
        return score

    def _calculate_overall_score(self, scores_and_weights: List[Tuple[float, float]]) -> float:
        """
        Calculate weighted average score.

        Args:
            scores_and_weights: List of (score, weight) tuples

        Returns:
            float: Weighted average score (0-100)
        """
        total_score = 0.0
        total_weight = 0.0
        
        for score, weight in scores_and_weights:
            total_score += score * weight
            total_weight += weight
            
        return round(total_score / total_weight if total_weight > 0 else 0, 2)

    def _generate_findings(self) -> List[str]:
        """Generate list of significant findings."""
        findings = []
        
        # Add significant style violations
        if self.metrics['style_violations']:
            findings.extend(self.metrics['style_violations'][:3])
            
        # Add significant indentation issues
        if self.metrics['indentation_issues']:
            findings.extend(self.metrics['indentation_issues'][:3])
            
        # Add significant naming violations
        if self.metrics['naming_violations']:
            findings.extend(self.metrics['naming_violations'][:3])
            
        return findings

    def _generate_suggestions(self) -> List[str]:
        """Generate improvement suggestions based on findings."""
        suggestions = []
        
        # Style suggestions
        if self.metrics['style_violations']:
            suggestions.append("Consider using an auto-formatter like black or autopep8")
            
        # Indentation suggestions
        if self.metrics['indentation_issues']:
            suggestions.append(f"Use consistent indentation ({self.INDENT_SIZE} spaces)")
            
        # Naming suggestions
        if self.metrics['naming_violations']:
            suggestions.append("Follow PEP 8 naming conventions for classes, functions, and variables")
            
        # Import suggestions
        if self.metrics['import_organization']:
            suggestions.append("Group imports together at the top of the file")
            
        return suggestions
