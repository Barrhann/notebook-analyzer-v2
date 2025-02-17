"""Analyzer for visualization types and their appropriateness."""
import ast
from typing import Dict, Any, List, Set
from collections import defaultdict
from ...base_analyzer import BaseAnalyzer

class VisualizationTypesAnalyzer(BaseAnalyzer):
    """Analyzes visualization types and their suitability for different data types."""
    
    def __init__(self):
        super().__init__()
        self.viz_types = {
            'categorical': {
                'bar': {'barplot', 'bar'},
                'count': {'countplot', 'hist'},
                'box': {'boxplot', 'box'},
                'violin': {'violinplot', 'violin'},
                'pie': {'pie', 'piecharts'}
            },
            'numerical': {
                'histogram': {'hist', 'histogram'},
                'kde': {'kdeplot', 'kde'},
                'scatter': {'scatter', 'scatterplot'},
                'line': {'line', 'lineplot', 'plot'},
                'area': {'area', 'areaplot', 'fill_between'}
            },
            'temporal': {
                'timeseries': {'plot_date', 'tsplot'},
                'seasonal': {'seasonal_plot'},
                'decomposition': {'decompose'}
            },
            'relational': {
                'correlation': {'heatmap', 'corrplot'},
                'pair': {'pairplot', 'pairs'},
                'joint': {'jointplot'},
                'facet': {'facetgrid', 'facet'}
            },
            'geographical': {
                'map': {'geoplot', 'choropleth'},
                'points': {'scatter_geo'},
                'density': {'kdeplot_geo'}
            }
        }

    def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze visualization types."""
        try:
            tree = ast.parse(code)
            return {
                'metrics': {
                    'type_usage': self._analyze_type_usage(tree),
                    'data_appropriateness': self._analyze_data_appropriateness(tree),
                    'visualization_complexity': self._analyze_visualization_complexity(tree),
                    'combination_effectiveness': self._analyze_combination_effectiveness(tree)
                }
            }
        except SyntaxError:
            return self._get_default_metrics()

    def _analyze_type_usage(self, tree: ast.AST) -> Dict[str, Any]:
        usage = defaultdict(list)
        
        class TypeVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    viz_type = self._identify_viz_type(node.func.attr)
                    if viz_type:
                        usage[viz_type['category']].append({
                            'type': viz_type['type'],
                            'function': node.func.attr,
                            'lineno': node.lineno,
                            'params': self._extract_params(node)
                        })
                self.generic_visit(node)
            
            def _identify_viz_type(self, func_name: str) -> Dict[str, str]:
                for category, types in self.viz_types.items():
                    for type_name, functions in types.items():
                        if func_name in functions:
                            return {'category': category, 'type': type_name}
                return None
            
            def _extract_params(self, node):
                params = []
                for kw in node.keywords:
                    if isinstance(kw.value, ast.Name):
                        params.append((kw.arg, kw.value.id))
                    elif isinstance(kw.value, ast.Constant):
                        params.append((kw.arg, str(kw.value.value)))
                return params
        
        TypeVisitor().visit(tree)
        
        # Calculate type usage score
        if not usage:
            type_score = 60  # Base score for no visualizations
        else:
            base_score = 70
            # Bonus for using multiple categories
            category_bonus = min(15, len(usage) * 5)
            # Bonus for visualization diversity within categories
            diversity_bonus = min(15, sum(len(set(v['type'] for v in viz_list)) - 1
                                        for viz_list in usage.values()))
            
            type_score = base_score + category_bonus + diversity_bonus
        
        return {
            'usage_by_category': dict(usage),
            'total_visualizations': sum(len(v) for v in usage.values()),
            'category_coverage': len(usage),
            'score': round(min(100, type_score), 2)
        }

    def _analyze_data_appropriateness(self, tree: ast.AST) -> Dict[str, Any]:
        appropriateness = {
            'matches': [],
            'mismatches': [],
            'data_types': defaultdict(set)
        }
        
        class AppropriatenessVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    viz_info = self._analyze_visualization(node)
                    if viz_info:
                        data_type = self._infer_data_type(node)
                        if data_type:
                            appropriateness['data_types'][viz_info['category']].add(data_type)
                            
                            if self._is_appropriate_match(viz_info['category'], data_type):
                                appropriateness['matches'].append({
                                    'viz_type': viz_info['type'],
                                    'data_type': data_type,
                                    'lineno': node.lineno
                                })
                            else:
                                appropriateness['mismatches'].append({
                                    'viz_type': viz_info['type'],
                                    'data_type': data_type,
                                    'lineno': node.lineno,
                                    'suggestion': self._suggest_alternative(data_type)
                                })
                
                self.generic_visit(node)
            
            def _analyze_visualization(self, node):
                if isinstance(node.func, ast.Attribute):
                    for category, types in self.viz_types.items():
                        for type_name, functions in types.items():
                            if node.func.attr in functions:
                                return {'category': category, 'type': type_name}
                return None
            
            def _infer_data_type(self, node):
                # Try to infer data type from parameter names and values
                for kw in node.keywords:
                    if kw.arg in {'x', 'y', 'data'}:
                        if isinstance(kw.value, ast.Name):
                            if 'time' in kw.value.id.lower() or 'date' in kw.value.id.lower():
                                return 'temporal'
                            elif 'cat' in kw.value.id.lower():
                                return 'categorical'
                            elif 'num' in kw.value.id.lower():
                                return 'numerical'
                return None
            
            def _is_appropriate_match(self, category: str, data_type: str) -> bool:
                appropriate_matches = {
                    'categorical': {'categorical'},
                    'numerical': {'numerical'},
                    'temporal': {'temporal'},
                    'relational': {'numerical', 'categorical'},
                    'geographical': {'categorical', 'numerical'}
                }
                return data_type in appropriate_matches.get(category, set())
            
            def _suggest_alternative(self, data_type: str) -> str:
                suggestions = {
                    'categorical': 'bar, box, or violin plot',
                    'numerical': 'histogram, scatter, or line plot',
                    'temporal': 'line plot or time series visualization'
                }
                return suggestions.get(data_type, 'appropriate visualization type')
        
        AppropriatenessVisitor().visit(tree)
        
        # Calculate appropriateness score
        total_viz = len(appropriateness['matches']) + len(appropriateness['mismatches'])
        if total_viz == 0:
            appropriateness_score = 60  # Base score for no visualizations
        else:
            match_ratio = len(appropriateness['matches']) / total_viz
            appropriateness_score = 60 + (match_ratio * 40)  # Scale from 60-100
        
        return {
            'matches': appropriateness['matches'],
            'mismatches': appropriateness['mismatches'],
            'data_types': dict(appropriateness['data_types']),
            'score': round(appropriateness_score, 2)
        }

    def _analyze_visualization_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        complexity = {
            'simple': [],
            'intermediate': [],
            'advanced': []
        }
        
        class ComplexityVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    viz_complexity = self._assess_complexity(node)
                    if viz_complexity:
                        complexity[viz_complexity['level']].append({
                            'type': viz_complexity['type'],
                            'lineno': node.lineno,
                            'features': viz_complexity['features']
                        })
                self.generic_visit(node)
            
            def _assess_complexity(self, node):
                if not isinstance(node.func, ast.Attribute):
                    return None
                
                features = []
                # Check for layered visualizations
                if any(layer in node.func.attr for layer in ['layer', 'add']):
                    features.append('layered')
                
                # Check for multiple variables
                param_count = len([k for k in node.keywords if k.arg in {'x', 'y', 'hue', 'size'}])
                if param_count > 2:
                    features.append('multivariate')
                
                # Check for advanced customizations
                if any(kw.arg in {'facet', 'row', 'col'} for kw in node.keywords):
                    features.append('faceted')
                
                # Determine complexity level
                if len(features) <= 1:
                    level = 'simple'
                elif len(features) == 2:
                    level = 'intermediate'
                else:
                    level = 'advanced'
                
                return {
                    'level': level,
                    'type': node.func.attr,
                    'features': features
                }
        
        ComplexityVisitor().visit(tree)
        
        # Calculate complexity score
        total_viz = sum(len(v) for v in complexity.values())
        if total_viz == 0:
            complexity_score = 60  # Base score for no visualizations
        else:
            base_score = 70
            # Bonus for advanced visualizations
            advanced_ratio = len(complexity['advanced']) / total_viz
            advanced_bonus = min(20, advanced_ratio * 40)
            # Bonus for intermediate visualizations
            intermediate_ratio = len(complexity['intermediate']) / total_viz
            intermediate_bonus = min(10, intermediate_ratio * 20)
            
            complexity_score = base_score + advanced_bonus + intermediate_bonus
        
        return {
            'by_level': complexity,
            'total_visualizations': total_viz,
            'score': round(min(100, complexity_score), 2)
        }

    def _analyze_combination_effectiveness(self, tree: ast.AST) -> Dict[str, Any]:
        combinations = {
            'sequences': [],
            'effectiveness': []
        }
        
        class CombinationVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_sequence = []
            
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    viz_type = self._get_viz_type(node.func.attr)
                    if viz_type:
                        self.current_sequence.append({
                            'type': viz_type,
                            'lineno': node.lineno
                        })
                        
                        # Analyze effectiveness when sequence is complete
                        if len(self.current_sequence) >= 2:
                            effectiveness = self._analyze_sequence_effectiveness(
                                self.current_sequence[-2:])
                            if effectiveness:
                                combinations['effectiveness'].append(effectiveness)
                
                self.generic_visit(node)
            
            def _get_viz_type(self, func_name: str) -> str:
                for category, types in self.viz_types.items():
                    for type_name, functions in types.items():
                        if func_name in functions:
                            return f"{category}.{type_name}"
                return None
            
            def _analyze_sequence_effectiveness(self, sequence):
                prev_viz, curr_viz = sequence
                
                # Define effective combinations
                effective_pairs = {
                    ('numerical.histogram', 'numerical.boxplot'),
                    ('numerical.scatter', 'numerical.line'),
                    ('categorical.bar', 'numerical.line'),
                    ('relational.correlation', 'numerical.scatter')
                }
                
                pair = (prev_viz['type'], curr_viz['type'])
                is_effective = pair in effective_pairs
                
                return {
                    'sequence': [v['type'] for v in sequence],
                    'is_effective': is_effective,
                    'lines': [v['lineno'] for v in sequence],
                    'suggestion': self._get_combination_suggestion(pair) if not is_effective else None
                }
            
            def _get_combination_suggestion(self, pair):
                suggestions = {
                    ('numerical.histogram', 'numerical.scatter'):
                        'Consider adding a box plot to show distribution',
                    ('categorical.bar', 'categorical.bar'):
                        'Consider using a grouped or stacked bar chart instead',
                    ('numerical.line', 'numerical.line'):
                        'Consider using subplots or dual axis for better comparison'
                }
                return suggestions.get(pair, 'Consider reorganizing visualizations for better flow')
        
        visitor = CombinationVisitor()
        visitor.visit(tree)
        combinations['sequences'] = visitor.current_sequence
        
        # Calculate combination effectiveness score
        total_combinations = len(combinations['effectiveness'])
        if total_combinations == 0:
            combination_score = 60  # Base score for no combinations
        else:
            effective_count = sum(
                1 for e in combinations['effectiveness'] if e['is_effective']
            )
            effectiveness_ratio = effective_count / total_combinations
            combination_score = 60 + (effectiveness_ratio * 40)  # Scale from 60-100
        
        return {
            'sequences': combinations['sequences'],
            'effectiveness': combinations['effectiveness'],
            'total_combinations': total_combinations,
            'score': round(combination_score, 2)
        }

    def _get_default_metrics(self) -> Dict[str, Any]:
        return {
            'metrics': {
                'type_usage': {
                    'usage_by_category': {},
                    'total_visualizations': 0,
                    'category_coverage': 0,
                    'score': 60
                },
                'data_appropriateness': {
                    'matches': [],
                    'mismatches': [],
                    'data_types': {},
                    'score': 60
                },
                'visualization_complexity': {
                    'by_level': {
                        'simple': [],
                        'intermediate': [],
                        'advanced': []
                    },
                    'total_visualizations': 0,
                    'score': 60
                },
                'combination_effectiveness': {
                    'sequences': [],
                    'effectiveness': [],
                    'total_combinations': 0,
                    'score': 60
                }
            }
        }
