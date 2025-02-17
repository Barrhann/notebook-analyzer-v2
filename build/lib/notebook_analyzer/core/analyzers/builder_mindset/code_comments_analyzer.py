"""Analyzer for code comments and documentation."""
import ast
import re
from typing import Dict, Any, List
from ...base_analyzer import BaseAnalyzer

class CodeCommentsAnalyzer(BaseAnalyzer):
    """Analyzes code comments and documentation quality."""
    
    def __init__(self):
        super().__init__()
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by'
        }

    def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze code comments and documentation."""
        try:
            tree = ast.parse(code)
            return {
                'metrics': {
                    'docstrings': self._analyze_docstrings(tree),
                    'inline_comments': self._analyze_inline_comments(code),
                    'comment_quality': self._analyze_comment_quality(code),
                    'documentation_coverage': self._analyze_documentation_coverage(tree)
                }
            }
        except SyntaxError:
            return self._get_default_metrics()

    def _analyze_docstrings(self, tree: ast.AST) -> Dict[str, Any]:
        docstrings = []
        missing_docstrings = []
        
        class DocstringVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                doc = ast.get_docstring(node)
                if doc:
                    docstrings.append({
                        'name': node.name,
                        'type': 'function',
                        'lineno': node.lineno,
                        'content': doc
                    })
                else:
                    missing_docstrings.append({
                        'name': node.name,
                        'type': 'function',
                        'lineno': node.lineno
                    })
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                doc = ast.get_docstring(node)
                if doc:
                    docstrings.append({
                        'name': node.name,
                        'type': 'class',
                        'lineno': node.lineno,
                        'content': doc
                    })
                else:
                    missing_docstrings.append({
                        'name': node.name,
                        'type': 'class',
                        'lineno': node.lineno
                    })
                self.generic_visit(node)
                
        DocstringVisitor().visit(tree)
        
        total_items = len(docstrings) + len(missing_docstrings)
        if total_items == 0:
            coverage_score = 100
        else:
            coverage_score = (len(docstrings) / total_items) * 100
            
        quality_score = self._evaluate_docstring_quality(docstrings)
        
        return {
            'docstrings': docstrings,
            'missing': missing_docstrings,
            'coverage_score': round(coverage_score, 2),
            'quality_score': round(quality_score, 2),
            'score': round((coverage_score + quality_score) / 2, 2)
        }

    def _analyze_inline_comments(self, code: str) -> Dict[str, Any]:
        lines = code.splitlines()
        inline_comments = []
        code_to_comment_ratio = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                inline_comments.append({
                    'line': i,
                    'content': stripped[1:].strip(),
                    'type': 'standalone'
                })
            elif '#' in line:
                code_part = line[:line.index('#')].strip()
                comment_part = line[line.index('#')+1:].strip()
                inline_comments.append({
                    'line': i,
                    'content': comment_part,
                    'type': 'inline',
                    'code': code_part
                })
        
        total_lines = len(lines)
        if total_lines > 0:
            code_to_comment_ratio = len(inline_comments) / total_lines
            
        return {
            'comments': inline_comments,
            'count': len(inline_comments),
            'ratio': round(code_to_comment_ratio, 2),
            'score': round(self._evaluate_comment_distribution(code_to_comment_ratio) * 100, 2)
        }

    def _analyze_comment_quality(self, code: str) -> Dict[str, Any]:
        issues = []
        comments = []
        
        for i, line in enumerate(code.splitlines(), 1):
            if '#' in line:
                comment_start = line.index('#')
                comment_text = line[comment_start + 1:].strip()
                
                if comment_text:
                    comments.append({
                        'line': i,
                        'content': comment_text
                    })
                    
                    # Check comment quality
                    if len(comment_text.split()) < 3:
                        issues.append({
                            'line': i,
                            'type': 'too_short',
                            'message': 'Comment is too brief'
                        })
                    
                    if self._is_redundant_comment(line[:comment_start].strip(), comment_text):
                        issues.append({
                            'line': i,
                            'type': 'redundant',
                            'message': 'Comment repeats code'
                        })
                        
                    if not comment_text[0].isupper():
                        issues.append({
                            'line': i,
                            'type': 'style',
                            'message': 'Comment should start with capital letter'
                        })
        
        total_comments = len(comments)
        quality_score = 100
        if total_comments > 0:
            quality_score = max(0, 100 - (len(issues) / total_comments * 50))
        
        return {
            'issues': issues,
            'total_comments': total_comments,
            'score': round(quality_score, 2)
        }

    def _analyze_documentation_coverage(self, tree: ast.AST) -> Dict[str, Any]:
        class CoverageVisitor(ast.NodeVisitor):
            def __init__(self):
                self.documented = 0
                self.total = 0
                self.public_items = []
                
            def visit_FunctionDef(self, node):
                self.total += 1
                if ast.get_docstring(node):
                    self.documented += 1
                if not node.name.startswith('_'):
                    self.public_items.append({
                        'name': node.name,
                        'type': 'function',
                        'documented': bool(ast.get_docstring(node))
                    })
                self.generic_visit(node)
                
            def visit_ClassDef(self, node):
                self.total += 1
                if ast.get_docstring(node):
                    self.documented += 1
                if not node.name.startswith('_'):
                    self.public_items.append({
                        'name': node.name,
                        'type': 'class',
                        'documented': bool(ast.get_docstring(node))
                    })
                self.generic_visit(node)
                
        visitor = CoverageVisitor()
        visitor.visit(tree)
        
        coverage_ratio = 1.0
        if visitor.total > 0:
            coverage_ratio = visitor.documented / visitor.total
            
        return {
            'public_items': visitor.public_items,
            'coverage_ratio': round(coverage_ratio, 2),
            'score': round(coverage_ratio * 100, 2)
        }

    def _evaluate_docstring_quality(self, docstrings: List[Dict]) -> float:
        if not docstrings:
            return 100.0
            
        quality_scores = []
        for doc in docstrings:
            content = doc['content']
            score = 100.0
            
            # Check length
            if len(content.split()) < 3:
                score -= 30
            
            # Check for parameters description
            if doc['type'] == 'function' and 'Args:' not in content:
                score -= 20
            
            # Check for return value description
            if doc['type'] == 'function' and 'Returns:' not in content:
                score -= 20
            
            # Check for class description
            if doc['type'] == 'class' and len(content.split('\n')) < 2:
                score -= 20
                
            quality_scores.append(max(0, score))
            
        return sum(quality_scores) / len(quality_scores)

    def _evaluate_comment_distribution(self, ratio: float) -> float:
        """Evaluate comment distribution score."""
        # Ideal comment ratio is between 0.1 and 0.3
        if ratio < 0.05:
            return ratio * 10  # Too few comments
        elif 0.05 <= ratio <= 0.3:
            return 1.0  # Ideal range
        else:
            return max(0, 1.0 - ((ratio - 0.3) * 2))  # Too many comments

    def _is_redundant_comment(self, code: str, comment: str) -> bool:
        """Check if a comment is redundant with its code."""
        code_tokens = set(
            word.lower() for word in re.findall(r'\w+', code)
            if word.lower() not in self.stop_words
        )
        comment_tokens = set(
            word.lower() for word in re.findall(r'\w+', comment)
            if word.lower() not in self.stop_words
        )
        
        if not code_tokens or not comment_tokens:
            return False
            
        overlap = len(code_tokens.intersection(comment_tokens))
        return overlap / len(comment_tokens) > 0.8

    def _get_default_metrics(self) -> Dict[str, Any]:
        return {
            'metrics': {
                'docstrings': {
                    'docstrings': [],
                    'missing': [],
                    'coverage_score': 100,
                    'quality_score': 100,
                    'score': 100
                },
                'inline_comments': {
                    'comments': [],
                    'count': 0,
                    'ratio': 0,
                    'score': 100
                },
                'comment_quality': {
                    'issues': [],
                    'total_comments': 0,
                    'score': 100
                },
                'documentation_coverage': {
                    'public_items': [],
                    'coverage_ratio': 1.0,
                    'score': 100
                }
            }
        }
