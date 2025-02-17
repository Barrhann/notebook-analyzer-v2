"""Analyzer for visualization formatting and presentation."""
import ast
from typing import Dict, Any, List
from collections import defaultdict
from ...base_analyzer import BaseAnalyzer

class VisualizationFormattingAnalyzer(BaseAnalyzer):
    """Analyzes visualization formatting and presentation quality."""
    
    def __init__(self):
        super().__init__()
        self.viz_libraries = {
            'matplotlib': {'plt', 'matplotlib'},
            'seaborn': {'sns', 'seaborn'},
            'plotly': {'px', 'go', 'plotly'},
            'bokeh': {'bokeh'},
            'altair': {'alt', 'altair'}
        }
        self.formatting_functions = {
            'title', 'xlabel', 'ylabel', 'legend',
            'xticks', 'yticks', 'grid', 'colorbar',
            'set_title', 'set_xlabel', 'set_ylabel'
        }

    def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze visualization formatting."""
        try:
            tree = ast.parse(code)
            return {
                'metrics': {
                    'formatting': self._analyze_formatting(tree),
                    'aesthetics': self._analyze_aesthetics(tree),
                    'interactivity': self._analyze_interactivity(tree),
                    'accessibility': self._analyze_accessibility(tree)
                }
            }
        except SyntaxError:
            return self._get_default_metrics()

    def _analyze_formatting(self, tree: ast.AST) -> Dict[str, Any]:
        formatting = {
            'elements': [],
            'missing_elements': [],
            'customizations': []
        }
        
        class FormattingVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.formatting_functions:
                        formatting['elements'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno,
                            'has_custom_params': bool(node.args or node.keywords)
                        })
                        
                        if node.args or node.keywords:
                            formatting['customizations'].append({
                                'element': node.func.attr,
                                'lineno': node.lineno,
                                'params': self._extract_params(node)
                            })
                
                self.generic_visit(node)
            
            def _extract_params(self, node):
                params = []
                for arg in node.args:
                    if isinstance(arg, ast.Constant):
                        params.append(str(arg.value))
                for kw in node.keywords:
                    params.append(f"{kw.arg}=...")
                return params
        
        FormattingVisitor().visit(tree)
        
        # Check for missing essential elements
        essential_elements = {'title', 'xlabel', 'ylabel', 'legend'}
        found_elements = {elem['type'] for elem in formatting['elements']}
        formatting['missing_elements'] = list(essential_elements - found_elements)
        
        # Calculate formatting score
        if not formatting['elements']:
            formatting_score = 60  # Base score for no formatting
        else:
            base_score = 70
            # Bonus for essential elements
            essential_coverage = len(essential_elements.intersection(found_elements))
            element_bonus = min(20, essential_coverage * 5)
            
            # Bonus for customizations
            custom_bonus = min(10, len(formatting['customizations']) * 2)
            
            formatting_score = base_score + element_bonus + custom_bonus
        
        return {
            'elements': formatting['elements'],
            'missing': formatting['missing_elements'],
            'customizations': formatting['customizations'],
            'score': round(min(100, formatting_score), 2)
        }

    def _analyze_aesthetics(self, tree: ast.AST) -> Dict[str, Any]:
        aesthetics = {
            'style_settings': [],
            'color_usage': [],
            'layout_adjustments': []
        }
        
        class AestheticsVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for style settings
                    if node.func.attr in {'style', 'set_style', 'theme'}:
                        aesthetics['style_settings'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno,
                            'params': self._extract_params(node)
                        })
                    
                    # Check for color-related calls
                    elif 'color' in node.func.attr.lower():
                        aesthetics['color_usage'].append({
                            'function': node.func.attr,
                            'lineno': node.lineno,
                            'params': self._extract_params(node)
                        })
                    
                    # Check for layout adjustments
                    elif node.func.attr in {'tight_layout', 'subplots_adjust', 'set_size_inches'}:
                        aesthetics['layout_adjustments'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno
                        })
                
                self.generic_visit(node)
            
            def _extract_params(self, node):
                return [
                    str(arg.value) if isinstance(arg, ast.Constant) else '...'
                    for arg in node.args
                ]
        
        AestheticsVisitor().visit(tree)
        
        # Calculate aesthetics score
        if not any(aesthetics.values()):
            aesthetics_score = 60  # Base score for no aesthetic customization
        else:
            base_score = 70
            # Bonus for style customization
            style_bonus = min(10, len(aesthetics['style_settings']) * 5)
            # Bonus for color usage
            color_bonus = min(10, len(aesthetics['color_usage']) * 3)
            # Bonus for layout adjustments
            layout_bonus = min(10, len(aesthetics['layout_adjustments']) * 5)
            
            aesthetics_score = base_score + style_bonus + color_bonus + layout_bonus
        
        return {
            'customizations': aesthetics,
            'score': round(min(100, aesthetics_score), 2)
        }

    def _analyze_interactivity(self, tree: ast.AST) -> Dict[str, Any]:
        interactivity = {
            'interactive_elements': [],
            'widgets': [],
            'callbacks': []
        }
        
        class InteractivityVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for interactive plot calls
                    if node.func.attr in {'iplot', 'interactive'}:
                        interactivity['interactive_elements'].append({
                            'type': 'plot',
                            'lineno': node.lineno
                        })
                    
                    # Check for widget creation
                    elif 'widget' in node.func.attr.lower():
                        interactivity['widgets'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno
                        })
                    
                    # Check for callback registration
                    elif node.func.attr in {'on_click', 'on_change', 'observe'}:
                        interactivity['callbacks'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno
                        })
                
                self.generic_visit(node)
        
        InteractivityVisitor().visit(tree)
        
        # Calculate interactivity score
        if not any(interactivity.values()):
            interactivity_score = 60  # Base score for no interactivity
        else:
            base_score = 70
            # Bonus for interactive elements
            element_bonus = min(10, len(interactivity['interactive_elements']) * 5)
            # Bonus for widgets
            widget_bonus = min(10, len(interactivity['widgets']) * 3)
            # Bonus for callbacks
            callback_bonus = min(10, len(interactivity['callbacks']) * 5)
            
            interactivity_score = base_score + element_bonus + widget_bonus + callback_bonus
        
        return {
            'elements': interactivity,
            'score': round(min(100, interactivity_score), 2)
        }

    def _analyze_accessibility(self, tree: ast.AST) -> Dict[str, Any]:
        accessibility = {
            'text_elements': [],
            'color_considerations': [],
            'size_adjustments': []
        }
        
        class AccessibilityVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    # Check for text-related calls
                    if any(text in node.func.attr.lower() for text in ['text', 'label', 'title']):
                        accessibility['text_elements'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno,
                            'params': self._extract_params(node)
                        })
                    
                    # Check for color-blind friendly settings
                    elif 'color' in node.func.attr.lower():
                        accessibility['color_considerations'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno,
                            'params': self._extract_params(node)
                        })
                    
                    # Check for size adjustments
                    elif 'size' in node.func.attr.lower():
                        accessibility['size_adjustments'].append({
                            'type': node.func.attr,
                            'lineno': node.lineno,
                            'params': self._extract_params(node)
                        })
                
                self.generic_visit(node)
            
            def _extract_params(self, node):
                return [
                    str(arg.value) if isinstance(arg, ast.Constant) else '...'
                    for arg in node.args
                ]
        
        AccessibilityVisitor().visit(tree)
        
        # Calculate accessibility score
        if not any(accessibility.values()):
            accessibility_score = 60  # Base score for no accessibility considerations
        else:
            base_score = 70
            # Bonus for text elements
            text_bonus = min(10, len(accessibility['text_elements']) * 3)
            # Bonus for color considerations
            color_bonus = min(10, len(accessibility['color_considerations']) * 5)
            # Bonus for size adjustments
            size_bonus = min(10, len(accessibility['size_adjustments']) * 3)
            
            accessibility_score = base_score + text_bonus + color_bonus + size_bonus
        
        return {
            'elements': accessibility,
            'score': round(min(100, accessibility_score), 2)
        }

    def _get_default_metrics(self) -> Dict[str, Any]:
        return {
            'metrics': {
                'formatting': {
                    'elements': [],
                    'missing': [],
                    'customizations': [],
                    'score': 60
                },
                'aesthetics': {
                    'customizations': {
                        'style_settings': [],
                        'color_usage': [],
                        'layout_adjustments': []
                    },
                    'score': 60
                },
                'interactivity': {
                    'elements': {
                        'interactive_elements': [],
                        'widgets': [],
                        'callbacks': []
                    },
                    'score': 60
                },
                'accessibility': {
                    'elements': {
                        'text_elements': [],
                        'color_considerations': [],
                        'size_adjustments': []
                    },
                    'score': 60
                }
            }
        }
