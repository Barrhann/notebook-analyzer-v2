"""
Code Comments Analyzer Module.

This module analyzes the quality, quantity, and relevance of code comments in
Jupyter notebook cells. It evaluates docstrings, inline comments, and overall
documentation coverage.

Created by: Barrhann
Date: 2025-02-17
"""

import ast
from typing import Dict, Any, List, Tuple, Set
import re
from ..base_analyzer import BaseAnalyzer, AnalysisError

class CodeCommentsAnalyzer(BaseAnalyzer):
    """
    Analyzer for code comments and documentation metrics.
    
    This analyzer evaluates:
    - Docstring presence and quality
    - Inline comment coverage and relevance
    - Documentation completeness
    - Comment-to-code ratio
    - Documentation style consistency
    
    Attributes:
        MIN_DOCSTRING_LENGTH (int): Minimum recommended docstring length
        MAX_COMMENT_LENGTH (int): Maximum recommended comment length
        IDEAL_COMMENT_RATIO (float): Ideal ratio of comments to code
    """

    MIN_DOCSTRING_LENGTH = 10
    MAX_COMMENT_LENGTH = 100
    IDEAL_COMMENT_RATIO = 0.2  # 20% comments to code ratio

    def __init__(self):
        """Initialize the code comments analyzer."""
        super().__init__(name="Code Comments")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'docstring_coverage': [],
            'inline_comments': [],
            'comment_quality': [],
            'documentation_style': [],
            'comment_ratios': []
        }
        self.docstring_count = 0
        self.comment_count = 0
        self.code_lines = 0

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'builder_mindset'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze code comments and documentation.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing:
                - score: Overall documentation score (0-100)
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

            # Perform various documentation checks
            docstring_score = self._analyze_docstrings(tree)
            inline_score = self._analyze_inline_comments(code)
            quality_score = self._analyze_comment_quality(code)
            style_score = self._analyze_documentation_style(code)
            ratio_score = self._analyze_comment_ratio(code)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (docstring_score, 0.35),  # 35% weight
                (inline_score, 0.25),     # 25% weight
                (quality_score, 0.20),    # 20% weight
                (style_score, 0.10),      # 10% weight
                (ratio_score, 0.10)       # 10% weight
            ])

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(),
                'details': {
                    'docstring_score': docstring_score,
                    'inline_comments_score': inline_score,
                    'comment_quality_score': quality_score,
                    'documentation_style_score': style_score,
                    'comment_ratio_score': ratio_score,
                    'metrics': self.metrics
                },
                'suggestions': self._generate_suggestions()
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing code comments: {str(e)}")

    def _analyze_docstrings(self, tree: ast.AST) -> float:
        """
        Analyze presence and quality of docstrings.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Docstring quality score (0-100)
        """
        issues = []
        docstring_nodes = []

        # Collect all nodes that should have docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    self.docstring_count += 1
                    if len(docstring.strip()) < self.MIN_DOCSTRING_LENGTH:
                        issues.append(f"Short docstring in {node.__class__.__name__}")
                    docstring_nodes.append((node, docstring))
                else:
                    issues.append(f"Missing docstring in {node.__class__.__name__}")

        # Calculate coverage score
        if not docstring_nodes and not issues:
            return 100.0  # No documentable nodes found
        
        coverage = self.docstring_count / (len(docstring_nodes) + len(issues))
        score = coverage * 100

        self.metrics['docstring_coverage'].extend(issues)
        return score

    def _analyze_inline_comments(self, code: str) -> float:
        """
        Analyze inline comments for quality and relevance.

        Args:
            code (str): Code to analyze

        Returns:
            float: Inline comments score (0-100)
        """
        lines = code.splitlines()
        issues = []
        
        for i, line in enumerate(lines, 1):
            # Skip empty lines and docstrings
            if not line.strip() or line.strip().startswith('"""'):
                continue

            # Check for inline comments
            comment_idx = line.find('#')
            if comment_idx > -1:
                self.comment_count += 1
                comment = line[comment_idx:].strip()
                
                # Check comment quality
                if len(comment) <= 2:  # Just # or #_
                    issues.append(f"Line {i}: Too short comment")
                elif len(comment) > self.MAX_COMMENT_LENGTH:
                    issues.append(f"Line {i}: Comment too long")
                elif comment.strip('#').strip().lower() in {'todo', 'fixme'}:
                    issues.append(f"Line {i}: TODO/FIXME comment found")

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 5))
        self.metrics['inline_comments'].extend(issues)
        return score

    def _analyze_comment_quality(self, code: str) -> float:
        """
        Analyze the quality of comments.

        Args:
            code (str): Code to analyze

        Returns:
            float: Comment quality score (0-100)
        """
        lines = code.splitlines()
        issues = []
        
        for i, line in enumerate(lines, 1):
            if '#' in line:
                comment = line[line.find('#'):].strip()
                
                # Check for obvious issues
                if re.search(r'#\s*[a-z]', comment):  # Comment doesn't start with capital
                    issues.append(f"Line {i}: Comment should start with capital letter")
                    
                if re.search(r'#\s*[^a-zA-Z0-9\s]', comment):  # Special characters
                    issues.append(f"Line {i}: Avoid special characters at start of comment")
                    
                # Check for redundant comments
                code_part = line[:line.find('#')].strip()
                if code_part and comment[1:].strip() == code_part:
                    issues.append(f"Line {i}: Redundant comment")

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 5))
        self.metrics['comment_quality'].extend(issues)
        return score

    def _analyze_documentation_style(self, code: str) -> float:
        """
        Analyze documentation style consistency.

        Args:
            code (str): Code to analyze

        Returns:
            float: Documentation style score (0-100)
        """
        issues = []
        doc_styles = set()
        
        # Check docstring style consistency
        for match in re.finditer(r'""".*?"""|\'\'\'.*?\'\'\'', code, re.DOTALL):
            docstring = match.group()
            if docstring.startswith('"""'):
                doc_styles.add('double')
            else:
                doc_styles.add('single')

        if len(doc_styles) > 1:
            issues.append("Inconsistent docstring quote style")

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['documentation_style'].extend(issues)
        return score

    def _analyze_comment_ratio(self, code: str) -> float:
        """
        Analyze the ratio of comments to code.

        Args:
            code (str): Code to analyze

        Returns:
            float: Comment ratio score (0-100)
        """
        lines = code.splitlines()
        code_lines = 0
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped:
                if stripped.startswith('#'):
                    comment_lines += 1
                elif '#' in line:
                    code_lines += 1
                    comment_lines += 1
                else:
                    code_lines += 1

        if code_lines == 0:
            return 100.0

        actual_ratio = comment_lines / code_lines
        ratio_difference = abs(actual_ratio - self.IDEAL_COMMENT_RATIO)
        
        # Calculate score based on how close to ideal ratio
        score = max(0, 100 - (ratio_difference * 100))
        
        self.metrics['comment_ratios'].append(
            f"Comment ratio: {actual_ratio:.2f} (ideal: {self.IDEAL_COMMENT_RATIO})"
        )
        
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
        
        # Add significant docstring issues
        if self.metrics['docstring_coverage']:
            findings.extend(self.metrics['docstring_coverage'][:3])
            
        # Add significant inline comment issues
        if self.metrics['inline_comments']:
            findings.extend(self.metrics['inline_comments'][:3])
            
        # Add comment quality issues
        if self.metrics['comment_quality']:
            findings.extend(self.metrics['comment_quality'][:3])
            
        return findings

    def _generate_suggestions(self) -> List[str]:
        """Generate improvement suggestions based on findings."""
        suggestions = []
        
        # Docstring suggestions
        if self.metrics['docstring_coverage']:
            suggestions.append(
                "Add docstrings to all functions and classes"
            )
            
        # Inline comment suggestions
        if self.metrics['inline_comments']:
            suggestions.append(
                "Improve inline comments quality and relevance"
            )
            
        # Style suggestions
        if self.metrics['documentation_style']:
            suggestions.append(
                "Maintain consistent documentation style throughout the code"
            )
            
        # Ratio suggestions
        if self.metrics['comment_ratios']:
            suggestions.append(
                f"Aim for {self.IDEAL_COMMENT_RATIO:.0%} comment-to-code ratio"
            )
            
        return suggestions
