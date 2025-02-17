"""
Visualization Types Analyzer Module.

This module analyzes the types and quality of data visualizations in Jupyter notebook cells.
It evaluates plotting libraries usage, chart types, and visualization best practices.

Created by: Barrhann
Date: 2025-02-17
Last Updated: 2025-02-17 00:51:45
"""

import ast
from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict
from ..base_analyzer import BaseAnalyzer, AnalysisError

class VisualizationTypesAnalyzer(BaseAnalyzer):
    """
    Analyzer for data visualization types and practices.
    
    This analyzer evaluates:
    - Plotting library usage
    - Chart type selection
    - Visualization configurations
    - Chart clarity and readability
    - Interactive visualization features
    
    Attributes:
        PLOTTING_LIBRARIES (Dict[str, Set[str]]): Mapping of libraries to their plotting functions
        CHART_TYPES (Dict[str, Set[str]]): Categories of chart types
        INTERACTIVE_LIBRARIES (Set[str]): Interactive visualization libraries
    """

    PLOTTING_LIBRARIES = {
        'matplotlib.pyplot': {
            'plot', 'scatter', 'bar', 'barh', 'hist', 'box', 'pie',
            'violinplot', 'heatmap', 'imshow', 'contour'
        },
        'seaborn': {
            'scatterplot', 'lineplot', 'barplot', 'boxplot', 'violinplot',
            'heatmap', 'kdeplot', 'distplot', 'regplot', 'lmplot'
        },
        'plotly.express': {
            'scatter', 'line', 'bar', 'histogram', 'box', 'violin',
            'heatmap', 'imshow', 'density_heatmap', 'treemap'
        },
        'altair': {
            'Chart', 'mark_point', 'mark_line', 'mark_bar', 'mark_circle',
            'mark_square', 'mark_boxplot', 'mark_area'
        }
    }

    CHART_TYPES = {
        'distribution': {'hist', 'boxplot', 'violinplot', 'kdeplot', 'distplot'},
        'relationship': {'scatter', 'regplot', 'lmplot', 'heatmap'},
        'comparison': {'bar', 'barh', 'boxplot'},
        'composition': {'pie', 'area', 'stackedbar'},
        'trend': {'line', 'lineplot'},
        'geographic': {'choropleth', 'scatter_geo', 'map'},
        'interactive': {'widget', 'interactive', 'animation'}
    }

    INTERACTIVE_LIBRARIES = {
        'plotly', 'bokeh', 'holoviews', 'ipywidgets'
    }

    def __init__(self):
        """Initialize the visualization types analyzer."""
        super().__init__(name="Visualization Types")
        self._reset_metrics()

    def _reset_metrics(self) -> None:
        """Reset all metrics for a new analysis."""
        self.metrics = {
            'library_usage': defaultdict(int),
            'chart_types': defaultdict(int),
            'visualization_quality': [],
            'interactive_features': [],
            'configuration_issues': []
        }
        self.total_visualizations = 0
        self.interactive_count = 0

    def get_metric_type(self) -> str:
        """Get the type of metric this analyzer produces."""
        return 'business_intelligence'

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze visualization types and practices.

        Args:
            code (str): The code to analyze

        Returns:
            Dict[str, Any]: Analysis results containing:
                - score: Overall visualization score (0-100)
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

            # Perform various visualization analysis
            library_score = self._analyze_library_usage(tree)
            chart_score = self._analyze_chart_types(tree)
            quality_score = self._analyze_visualization_quality(tree)
            interactive_score = self._analyze_interactive_features(tree)
            config_score = self._analyze_configurations(tree)

            # Calculate overall score
            overall_score = self._calculate_overall_score([
                (library_score, 0.25),     # 25% weight
                (chart_score, 0.25),       # 25% weight
                (quality_score, 0.20),     # 20% weight
                (interactive_score, 0.15), # 15% weight
                (config_score, 0.15)      # 15% weight
            ])

            # Prepare results
            results = {
                'score': overall_score,
                'findings': self._generate_findings(),
                'details': {
                    'library_usage_score': library_score,
                    'chart_types_score': chart_score,
                    'visualization_quality_score': quality_score,
                    'interactive_features_score': interactive_score,
                    'configuration_score': config_score,
                    'metrics': {
                        'library_usage': dict(self.metrics['library_usage']),
                        'chart_types': dict(self.metrics['chart_types']),
                        'visualization_quality': self.metrics['visualization_quality'],
                        'interactive_features': self.metrics['interactive_features'],
                        'configuration_issues': self.metrics['configuration_issues']
                    },
                    'stats': {
                        'total_visualizations': self.total_visualizations,
                        'interactive_ratio': self._calculate_interactive_ratio()
                    }
                },
                'suggestions': self._generate_suggestions()
            }

            if not self.validate_results(results):
                raise AnalysisError("Invalid analysis results generated")

            return results

        except Exception as e:
            raise AnalysisError(f"Error analyzing visualizations: {str(e)}")

    def _analyze_library_usage(self, tree: ast.AST) -> float:
        """
        Analyze visualization library usage.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Library usage score (0-100)
        """
        issues = []

        class LibraryVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    if any(lib in alias.name for lib in self.PLOTTING_LIBRARIES):
                        self.metrics['library_usage'][alias.name] += 1
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                if any(lib in node.module for lib in self.PLOTTING_LIBRARIES):
                    self.metrics['library_usage'][node.module] += 1
                self.generic_visit(node)

            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    for lib, funcs in self.PLOTTING_LIBRARIES.items():
                        if node.func.attr in funcs:
                            self.total_visualizations += 1
                            self.metrics['library_usage'][lib] += 1
                self.generic_visit(node)

        visitor = LibraryVisitor()
        visitor.visit(tree)

        # Calculate score based on library diversity
        if self.total_visualizations == 0:
            return 100.0
            
        unique_libraries = len(self.metrics['library_usage'])
        score = min(100.0, unique_libraries * 25)  # 25 points per unique library
        return score

    def _analyze_chart_types(self, tree: ast.AST) -> float:
        """
        Analyze chart type selection.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Chart type selection score (0-100)
        """
        class ChartVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Identify chart type from function name
                    func_name = node.func.attr
                    for category, charts in self.CHART_TYPES.items():
                        if any(chart in func_name.lower() for chart in charts):
                            self.metrics['chart_types'][category] += 1
                self.generic_visit(node)

        visitor = ChartVisitor()
        visitor.visit(tree)

        # Calculate score based on chart type diversity
        if not self.metrics['chart_types']:
            return 100.0
            
        unique_types = len(self.metrics['chart_types'])
        score = min(100.0, unique_types * 20)  # 20 points per chart type category
        return score

    def _analyze_visualization_quality(self, tree: ast.AST) -> float:
        """
        Analyze visualization quality settings.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Visualization quality score (0-100)
        """
        quality_issues = []

        class QualityVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for essential visualization components
                    self._check_visualization_components(node, quality_issues)
                self.generic_visit(node)

        visitor = QualityVisitor()
        visitor.visit(tree)

        # Calculate score based on issues found
        if not quality_issues:
            return 100.0
            
        score = max(0, 100 - (len(quality_issues) * 10))
        self.metrics['visualization_quality'].extend(quality_issues)
        return score

    def _analyze_interactive_features(self, tree: ast.AST) -> float:
        """
        Analyze interactive visualization features.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Interactive features score (0-100)
        """
        class InteractiveVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.INTERACTIVE_LIBRARIES:
                        self.interactive_count += 1
                elif isinstance(node.func, ast.Attribute):
                    if any(lib in node.func.attr for lib in self.INTERACTIVE_LIBRARIES):
                        self.interactive_count += 1
                self.generic_visit(node)

        visitor = InteractiveVisitor()
        visitor.visit(tree)

        # Calculate score based on interactive visualization ratio
        if self.total_visualizations == 0:
            return 100.0
            
        ratio = self.interactive_count / self.total_visualizations
        score = min(100.0, ratio * 100)
        return score

    def _analyze_configurations(self, tree: ast.AST) -> float:
        """
        Analyze visualization configurations.

        Args:
            tree (ast.AST): AST of the code

        Returns:
            float: Configuration score (0-100)
        """
        config_issues = []

        class ConfigVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for proper configuration settings
                    self._check_configuration_settings(node, config_issues)
                self.generic_visit(node)

        visitor = ConfigVisitor()
        visitor.visit(tree)

        # Calculate score based on configuration issues
        if not config_issues:
            return 100.0
            
        score = max(0, 100 - (len(config_issues) * 10))
        self.metrics['configuration_issues'].extend(config_issues)
        return score

    def _check_visualization_components(self, node: ast.Call, issues: List[str]) -> None:
        """Check for essential visualization components."""
        has_title = False
        has_labels = False
        has_legend = False

        for kw in node.keywords:
            if kw.arg in {'title', 'xlabel', 'ylabel', 'legend'}:
                if kw.arg == 'title':
                    has_title = True
                elif kw.arg in {'xlabel', 'ylabel'}:
                    has_labels = True
                elif kw.arg == 'legend':
                    has_legend = True

        if not has_title:
            issues.append("Missing chart title")
        if not has_labels:
            issues.append("Missing axis labels")
        if not has_legend and self._might_need_legend(node):
            issues.append("Consider adding a legend")

    def _check_configuration_settings(self, node: ast.Call, issues: List[str]) -> None:
        """Check for proper visualization configuration settings."""
        has_size = False
        has_style = False
        has_color = False

        for kw in node.keywords:
            if kw.arg in {'figsize', 'size'}:
                has_size = True
            elif kw.arg in {'style', 'theme'}:
                has_style = True
            elif kw.arg in {'color', 'palette'}:
                has_color = True

        if not has_size:
            issues.append("Consider specifying figure size")
        if not has_style:
            issues.append("Consider setting a style/theme")
        if not has_color:
            issues.append("Consider specifying colors/palette")

    @staticmethod
    def _might_need_legend(node: ast.Call) -> bool:
        """Determine if visualization might need a legend."""
        return any(
            kw.arg in {'hue', 'color', 'groups', 'categories'}
            for kw in node.keywords
        )

    def _calculate_interactive_ratio(self) -> float:
        """Calculate ratio of interactive to total visualizations."""
        if self.total_visualizations == 0:
            return 0.0
        return self.interactive_count / self.total_visualizations

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
        
        # Add library usage findings
        if self.metrics['library_usage']:
            findings.append(
                f"Using {len(self.metrics['library_usage'])} visualization libraries"
            )
            
        # Add chart type findings
        if self.metrics['chart_types']:
            findings.append(
                f"Implemented {len(self.metrics['chart_types'])} different chart types"
            )
            
        # Add quality issues
        if self.metrics['visualization_quality']:
            findings.extend(self.metrics['visualization_quality'][:3])
            
        # Add configuration issues
        if self.metrics['configuration_issues']:
            findings.extend(self.metrics['configuration_issues'][:2])
            
        return findings
        
    def _generate_suggestions(self) -> List[str]:
        """Generate improvement suggestions based on findings."""
        suggestions = []
        
        # Library diversity suggestions
        if len(self.metrics['library_usage']) < 2:
            suggestions.append(
                "Consider using multiple visualization libraries for different chart types"
            )
            
        # Chart type diversity suggestions
        if len(self.metrics['chart_types']) < 3:
            suggestions.append(
                "Explore different chart types to better communicate insights"
            )
            
        # Interactive visualization suggestions
        if self._calculate_interactive_ratio() < 0.2:
            suggestions.append(
                "Consider adding interactive visualizations for better user engagement"
            )
            
        # Quality suggestions
        if self.metrics['visualization_quality']:
            suggestions.append(
                "Enhance visualizations with titles, labels, and legends"
            )
            
        # Configuration suggestions
        if self.metrics['configuration_issues']:
            suggestions.append(
                "Improve visualization configurations with proper sizing and styling"
            )
            
        return suggestions

    def get_visualization_summary(self) -> Dict[str, Any]:
        """
        Get a summary of visualization usage and patterns.

        Returns:
            Dict[str, Any]: Summary of visualization analysis including:
                - library_distribution: Usage count by library
                - chart_type_distribution: Usage count by chart type
                - interactive_ratio: Ratio of interactive visualizations
                - quality_metrics: Quality-related metrics
        """
        return {
            'library_distribution': dict(self.metrics['library_usage']),
            'chart_type_distribution': dict(self.metrics['chart_types']),
            'interactive_ratio': self._calculate_interactive_ratio(),
            'quality_metrics': {
                'total_visualizations': self.total_visualizations,
                'quality_issues': len(self.metrics['visualization_quality']),
                'config_issues': len(self.metrics['configuration_issues'])
            }
        }

    def get_recommended_chart_types(self, data_type: str) -> List[str]:
        """
        Get recommended chart types for a specific type of data.

        Args:
            data_type (str): Type of data ('numerical', 'categorical', 'temporal', etc.)

        Returns:
            List[str]: Recommended chart types for the data type
        """
        recommendations = {
            'numerical': ['histogram', 'boxplot', 'scatter', 'line'],
            'categorical': ['bar', 'pie', 'heatmap', 'treemap'],
            'temporal': ['line', 'area', 'bar'],
            'geographic': ['choropleth', 'scatter_geo', 'map'],
            'relationship': ['scatter', 'bubble', 'heatmap'],
            'distribution': ['histogram', 'kde', 'violin'],
            'composition': ['pie', 'stacked_bar', 'treemap'],
            'comparison': ['bar', 'radar', 'parallel']
        }
        
        return recommendations.get(data_type.lower(), ['bar', 'line', 'scatter'])

    def __str__(self) -> str:
        """Return string representation of the analyzer."""
        return (f"Visualization Types Analyzer "
                f"(Total Visualizations: {self.total_visualizations})")

    def __repr__(self) -> str:
        """Return detailed string representation of the analyzer."""
        return (f"{self.__class__.__name__}("
                f"visualizations={self.total_visualizations}, "
                f"libraries={len(self.metrics['library_usage'])}, "
                f"chart_types={len(self.metrics['chart_types'])})")

    @staticmethod
    def get_library_capabilities() -> Dict[str, List[str]]:
        """
        Get capabilities of different visualization libraries.

        Returns:
            Dict[str, List[str]]: Mapping of libraries to their capabilities
        """
        return {
            'matplotlib': [
                'static plots',
                'full customization',
                'publication quality',
                'complex layouts'
            ],
            'seaborn': [
                'statistical visualization',
                'attractive defaults',
                'built-in themes',
                'dataframe integration'
            ],
            'plotly': [
                'interactive plots',
                'web-ready',
                'rich hover info',
                'animation support'
            ],
            'altair': [
                'declarative visualization',
                'grammar of graphics',
                'responsive design',
                'web integration'
            ]
        }

    def validate_visualization_best_practices(self, node: ast.Call) -> List[str]:
        """
        Validate visualization against best practices.

        Args:
            node (ast.Call): AST node of visualization call

        Returns:
            List[str]: List of best practice violations
        """
        violations = []
        
        # Check for basic requirements
        self._check_visualization_components(node, violations)
        
        # Check for configuration settings
        self._check_configuration_settings(node, violations)
        
        # Check for accessibility
        if not self._has_accessibility_features(node):
            violations.append("Consider adding accessibility features")
            
        # Check for responsive design
        if not self._has_responsive_settings(node):
            violations.append("Consider adding responsive design settings")
            
        return violations

    def _has_accessibility_features(self, node: ast.Call) -> bool:
        """Check if visualization includes accessibility features."""
        return any(
            kw.arg in {'alt_text', 'description', 'colorblind_friendly'}
            for kw in node.keywords
        )

    def _has_responsive_settings(self, node: ast.Call) -> bool:
        """Check if visualization includes responsive design settings."""
        return any(
            kw.arg in {'responsive', 'layout', 'autosize'}
            for kw in node.keywords
        )
