"""
Visualization Formatting Analyzer Module.

This module analyzes the formatting and styling of data visualizations in Jupyter notebook cells.
It evaluates aesthetic choices, color palettes, text formatting, and layout configurations.

Created by: Barrhann
Date: 2025-02-17
Last Updated: 2025-02-17 00:55:42
"""

import ast
from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict
import re
from ..base_analyzer import BaseAnalyzer, AnalysisError

class VisualizationFormattingAnalyzer(BaseAnalyzer):
    """
    Analyzer for visualization formatting and styling.
    
    This analyzer evaluates:
    - Color palette selection
    - Text formatting and labeling
    - Figure size and layout
    - Theme consistency
    - Grid and axis styling
    
    Attributes:
        RECOMMENDED_FIGURE_SIZES (Dict[str, Tuple[int, int]]): Standard figure sizes
        COLOR_PALETTES (Dict[str, List[str]]): Recommended color palettes
        TEXT_SIZES (Dict[str, int]): Standard text sizes for different elements
    """

    RECOMMENDED_FIGURE_SIZES = {
        'small': (6, 4),
        'medium': (8, 6),
        'large': (12, 8),
        'wide': (16, 6),
        'square': (8, 8)
    }

    COLOR_PALETTES = {
        'sequential': ['Blues', 'Greens', 'Oranges', 'Purples', 'Reds'],
        'diverging': ['RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm'],
        'qualitative': ['Set1', 'Set2', 'Set3', 'Paired', 'Dark2'],
        'colorblind_friendly': ['viridis', 'plasma', 'inferno', 'cividis']
    }

    TEXT_SIZES = {
        'title': 16,
        'axis_label': 12,
        'tick_label': 10,
        'legend': 10,
        'annotation': 11
    }

    def __init__(self):
        """Initialize the visualization formatting analyzer."""
        super().__init__(name="Visualization Formatting")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'color_usage': [],
            'text_formatting': [],
            'layout_config': [],
            'theme_consistency': [],
            'style_issues': []
        }
        self.style_counts = defaultdict(int)
        self.theme_usage = defaultdict(int)

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'business_intelligence'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze visualization formatting and styling.

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
            color_score = self._analyze_color_usage(tree)
            text_score = self._analyze_text_formatting(tree)
            layout_score = self._analyze_layout_configuration(tree)
            theme_score = self._analyze_theme_consistency(tree)
            style_score = self._analyze_style_elements(tree)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (color_score, 0.25),    # 25% weight
                (text_score, 0.25),     # 25% weight
                (layout_score, 0.20),   # 20% weight
                (theme_score, 0.15),    # 15% weight
                (style_score, 0.15)     # 15% weight
            ])

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(),
                'details': {
                    'color_usage_score': color_score,
                    'text_formatting_score': text_score,
                    'layout_config_score': layout_score,
                    'theme_consistency_score': theme_score,
                    'style_elements_score': style_score,
                    'metrics': {
                        'color_usage': self.metrics['color_usage'],
                        'text_formatting': self.metrics['text_formatting'],
                        'layout_config': self.metrics['layout_config'],
                        'theme_consistency': self.metrics['theme_consistency'],
                        'style_issues': self.metrics['style_issues']
                    },
                    'stats': {
                        'style_counts': dict(self.style_counts),
                        'theme_usage': dict(self.theme_usage)
                    }
                },
                'suggestions': self._generate_suggestions()
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing visualization formatting: {str(e)}")

    def _analyze_color_usage(self, tree: ast.AST) -> float:
        """
        Analyze color palette usage and selection.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Color usage score (0-100)
        """
        issues = []

        class ColorVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check color-related parameters
                    self._check_color_parameters(node, issues)
                self.generic_visit(node)

        visitor = ColorVisitor()
        visitor.visit(tree)

        # Calculate score based on color usage issues
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['color_usage'].extend(issues)
        return score

    def _analyze_text_formatting(self, tree: ast.AST) -> float:
        """
        Analyze text formatting and labeling.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Text formatting score (0-100)
        """
        issues = []

        class TextVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check text-related parameters
                    self._check_text_parameters(node, issues)
                self.generic_visit(node)

        visitor = TextVisitor()
        visitor.visit(tree)

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['text_formatting'].extend(issues)
        return score

    def _analyze_layout_configuration(self, tree: ast.AST) -> float:
        """
        Analyze layout and figure configuration.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Layout configuration score (0-100)
        """
        issues = []

        class LayoutVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check layout parameters
                    self._check_layout_parameters(node, issues)
                self.generic_visit(node)

        visitor = LayoutVisitor()
        visitor.visit(tree)

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 15))
        self.metrics['layout_config'].extend(issues)
        return score

    def _analyze_theme_consistency(self, tree: ast.AST) -> float:
        """
        Analyze theme consistency across visualizations.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Theme consistency score (0-100)
        """
        issues = []

        class ThemeVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Track theme usage
                    self._check_theme_usage(node)
                self.generic_visit(node)

        visitor = ThemeVisitor()
        visitor.visit(tree)

        # Check theme consistency
        if len(self.theme_usage) > 1:
            issues.append(f"Multiple themes detected: {', '.join(self.theme_usage.keys())}")

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 20))
        self.metrics['theme_consistency'].extend(issues)
        return score

    def _analyze_style_elements(self, tree: ast.AST) -> float:
        """
        Analyze style elements and aesthetics.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Style elements score (0-100)
        """
        issues = []

        class StyleVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check style elements
                    self._check_style_elements(node, issues)
                self.generic_visit(node)

        visitor = StyleVisitor()
        visitor.visit(tree)

        # Calculate score
        if not issues:
            return 100.0
            
        score = max(0, 100 - (len(issues) * 10))
        self.metrics['style_issues'].extend(issues)
        return score

    def _check_color_parameters(self, node: ast.Call, issues: List[str]) -> None:
        """Check color-related parameters in visualization calls."""
        for kw in node.keywords:
            if kw.arg in {'color', 'palette', 'cmap'}:
                if isinstance(kw.value, ast.Constant):
                    palette_name = kw.value.value
                    if isinstance(palette_name, str):
                        if not self._is_valid_palette(palette_name):
                            issues.append(f"Non-standard color palette: {palette_name}")

    def _check_text_parameters(self, node: ast.Call, issues: List[str]) -> None:
        """Check text-related parameters in visualization calls."""
        has_title = False
        has_labels = False
        
        for kw in node.keywords:
            if kw.arg == 'title':
                has_title = True
            elif kw.arg in {'xlabel', 'ylabel'}:
                has_labels = True
            elif kw.arg == 'fontsize':
                if isinstance(kw.value, ast.Constant):
                    if kw.value.value < 8 or kw.value.value > 16:
                        issues.append(f"Non-standard font size: {kw.value.value}")

        if not has_title:
            issues.append("Missing plot title")
        if not has_labels:
            issues.append("Missing axis labels")

    def _check_layout_parameters(self, node: ast.Call, issues: List[str]) -> None:
        """Check layout-related parameters in visualization calls."""
        has_figsize = False
        
        for kw in node.keywords:
            if kw.arg == 'figsize':
                has_figsize = True
                if isinstance(kw.value, ast.Tuple):
                    size = tuple(elt.value for elt in kw.value.elts)
                    if not self._is_recommended_size(size):
                        issues.append(f"Non-standard figure size: {size}")

        if not has_figsize:
            issues.append("Figure size not specified")

    def _check_theme_usage(self, node: ast.Call) -> None:
        """Track theme usage in visualizations."""
        for kw in node.keywords:
            if kw.arg in {'style', 'theme'}:
                if isinstance(kw.value, ast.Constant):
                    self.theme_usage[str(kw.value.value)] += 1

    def _check_style_elements(self, node: ast.Call, issues: List[str]) -> None:
        """Check style elements in visualizations."""
        has_grid = False
        has_legend = False
        
        for kw in node.keywords:
            if kw.arg == 'grid':
                has_grid = True
            elif kw.arg == 'legend':
                has_legend = True
                
        if not has_grid:
            issues.append("Consider adding grid for better readability")
        if not has_legend and self._might_need_legend(node):
            issues.append("Consider adding legend for clarity")

    def _is_valid_palette(self, palette: str) -> bool:
        """Check if color palette is in recommended set."""
        return any(
            palette in palettes
            for palettes in self.COLOR_PALETTES.values()
        )

    def _is_recommended_size(self, size: Tuple[int, int]) -> bool:
        """Check if figure size matches recommended sizes."""
        return size in self.RECOMMENDED_FIGURE_SIZES.values()

    def _might_need_legend(self, node: ast.Call) -> bool:
        """Determine if visualization might need a legend."""
        return any(
            kw.arg in {'hue', 'color', 'groups', 'categories'}
            for kw in node.keywords
        )

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
        
        # Add color usage findings
        if self.metrics['color_usage']:
            findings.extend(self.metrics['color_usage'][:2])
            
        # Add text formatting findings
        if self.metrics['text_formatting']:
            findings.extend(self.metrics['text_formatting'][:2])
            
        # Add layout findings
        if self.metrics['layout_config']:
            findings.extend(self.metrics['layout_config'][:2])
            
        return findings
        
    def _generate_suggestions(self) -> List[str]:
        """Generate improvement suggestions based on findings."""
        suggestions = []
        
        # Color usage suggestions
        if self.metrics['color_usage']:
            suggestions.append(
                "Use consistent and colorblind-friendly palettes"
            )
            
        # Text formatting suggestions
        if self.metrics['text_formatting']:
            suggestions.append(
                "Add clear titles and labels with appropriate font sizes"
            )
            
        # Layout suggestions
        if self.metrics['layout_config']:
            suggestions.append(
                "Use standard figure sizes and proper layout configurations"
            )
            
        # Theme consistency suggestions
        if len(self.theme_usage) > 1:
            suggestions.append(
                "Maintain consistent theme across all visualizations"
            )
            
        # Style element suggestions
        if self.metrics['style_issues']:
            suggestions.append(
                "Add grids and legends where appropriate for better readability"
            )
            
        return suggestions

    def get_recommended_formatting(self, chart_type: str) -> Dict[str, Any]:
        """
        Get recommended formatting settings for a specific chart type.

        Args:
            chart_type (str): Type of chart ('scatter', 'line', 'bar', etc.)

        Returns:
            Dict[str, Any]: Recommended formatting settings
        """
        base_settings = {
            'figsize': self.RECOMMENDED_FIGURE_SIZES['medium'],
            'fontsize': self.TEXT_SIZES['title'],
            'grid': True,
            'legend_loc': 'best'
        }

        type_specific = {
            'scatter': {
                'alpha': 0.6,
                'palette': 'viridis',
                'marker_size': 60
            },
            'line': {
                'linewidth': 2,
                'palette': 'Set2',
                'marker': 'o'
            },
            'bar': {
                'palette': 'Dark2',
                'alpha': 0.8,
                'edgecolor': 'black'
            },
            'heatmap': {
                'cmap': 'RdYlBu_r',
                'annot': True,
                'fmt': '.2f'
            }
        }

        return {**base_settings, **type_specific.get(chart_type, {})}

    def validate_formatting(self, node: ast.Call) -> List[str]:
        """
        Validate formatting settings against best practices.

        Args:
            node (ast.Call): AST node of visualization call

        Returns:
            List[str]: List of formatting violations
        """
        violations = []
        
        # Check text formatting
        self._check_text_parameters(node, violations)
        
        # Check color usage
        self._check_color_parameters(node, violations)
        
        # Check layout
        self._check_layout_parameters(node, violations)
        
        # Check style elements
        self._check_style_elements(node, violations)
        
        return violations

    def suggest_improvements(self, node: ast.Call) -> Dict[str, Any]:
        """
        Suggest specific formatting improvements for a visualization.

        Args:
            node (ast.Call): AST node of visualization call

        Returns:
            Dict[str, Any]: Suggested improvements
        """
        improvements = {}
        
        # Check for missing essential parameters
        for kw in node.keywords:
            if kw.arg == 'figsize' and not self._is_recommended_size(
                tuple(elt.value for elt in kw.value.elts)
            ):
                improvements['figsize'] = self.RECOMMENDED_FIGURE_SIZES['medium']
                
            if kw.arg == 'fontsize' and kw.value.value not in self.TEXT_SIZES.values():
                improvements['fontsize'] = self.TEXT_SIZES['title']
                
        # Suggest color palette if needed
        if not any(kw.arg in {'color', 'palette', 'cmap'} for kw in node.keywords):
            improvements['palette'] = self.COLOR_PALETTES['colorblind_friendly'][0]
            
        return improvements

    def __str__(self) -> str:
        """Return string representation of the analyzer."""
        return (f"Visualization Formatting Analyzer "
                f"(Style Issues: {len(self.metrics['style_issues'])})")

    def __repr__(self) -> str:
        """Return detailed string representation of the analyzer."""
        return (f"{self.__class__.__name__}("
                f"themes={len(self.theme_usage)}, "
                f"style_counts={dict(self.style_counts)})")

    def get_style_guide(self) -> Dict[str, Any]:
        """
        Get comprehensive style guide for visualizations.

        Returns:
            Dict[str, Any]: Style guide including recommended settings
        """
        return {
            'figure_sizes': self.RECOMMENDED_FIGURE_SIZES,
            'color_palettes': self.COLOR_PALETTES,
            'text_sizes': self.TEXT_SIZES,
            'best_practices': {
                'titles': 'Use clear, descriptive titles',
                'labels': 'Label all axes with units',
                'colors': 'Use colorblind-friendly palettes',
                'text': 'Maintain consistent font sizes',
                'layout': 'Use appropriate figure sizes',
                'grid': 'Add grid lines for readability',
                'legend': 'Include legends for multiple series'
            }
        }

    def get_theme_recommendations(self) -> Dict[str, List[str]]:
        """
        Get theme recommendations for different visualization contexts.

        Returns:
            Dict[str, List[str]]: Theme recommendations by context
        """
        return {
            'presentation': ['default', 'seaborn-talk', 'seaborn-poster'],
            'publication': ['seaborn-paper', 'grayscale', 'seaborn-deep'],
            'web': ['seaborn-whitegrid', 'seaborn-darkgrid'],
            'dashboard': ['plotly', 'seaborn-white'],
            'dark_mode': ['dark_background', 'seaborn-dark']
        }
