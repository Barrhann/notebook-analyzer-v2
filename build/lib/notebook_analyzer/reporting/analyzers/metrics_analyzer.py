"""
Metrics Analyzer - Analyzes code and documentation metrics
"""

from typing import Dict, Any, List
from datetime import datetime

class MetricsAnalyzer:
    def __init__(self):
        self.thresholds = {
            'line_length': {
                'ideal': 60,
                'acceptable': 79,
                'critical': 100
            },
            'complexity': {
                'low': 0.1,
                'moderate': 0.2,
                'high': 0.3
            },
            'comments': {
                'ratio': {'good': 0.2, 'minimum': 0.1},
                'docstring': {'good': 0.8, 'minimum': 0.5},
                'markdown': {'good': 5, 'minimum': 3}
            }
        }

    def analyze_all(self, code_analysis: Dict[str, Any], doc_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze all metrics from code and documentation analysis."""
        return {
            'code_formatting': self._analyze_code_formatting(code_analysis),
            'code_comments': self._analyze_code_comments(code_analysis, doc_analysis),
            'code_conciseness': self._analyze_code_conciseness(code_analysis),
            'code_structure': self._analyze_code_structure(code_analysis),
            'dataset_join': self._analyze_dataset_joins(code_analysis),
            'code_reusability': self._analyze_code_reusability(code_analysis),
            'advanced_techniques': self._analyze_advanced_techniques(code_analysis),
            'visualization_types': self._analyze_visualization_types(code_analysis),
            'visualization_formatting': self._analyze_visualization_formatting(code_analysis)
        }

    def _analyze_code_formatting(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code formatting metrics."""
        metrics = analysis.get('code_style_metrics', {})
        violations = analysis.get('pep8_violations', [])
        
        # Calculate metrics
        style_analysis = self._analyze_style_violations(violations)
        line_analysis = self._analyze_line_metrics(metrics)
        complexity_analysis = self._analyze_complexity_metrics(metrics)
        formatting_analysis = self._analyze_formatting_metrics(metrics)
        
        # Combine findings
        findings = {
            'positive': [],
            'negative': []
        }
        
        # Add findings from each analysis
        findings['positive'].extend(style_analysis.get('positive', []))
        findings['negative'].extend(style_analysis.get('negative', []))
        findings['positive'].extend(line_analysis.get('positive', []))
        findings['negative'].extend(line_analysis.get('negative', []))
        findings['positive'].extend(complexity_analysis.get('positive', []))
        findings['negative'].extend(complexity_analysis.get('negative', []))
        findings['positive'].extend(formatting_analysis.get('positive', []))
        findings['negative'].extend(formatting_analysis.get('negative', []))
        
        return {
            'metrics': {
                'style_violations': style_analysis['metrics'],
                'line_metrics': line_analysis['metrics'],
                'complexity_metrics': complexity_analysis['metrics'],
                'formatting_metrics': formatting_analysis['metrics']
            },
            'findings': findings
        }

    def _analyze_code_comments(self, code_analysis: Dict[str, Any],
                             doc_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code comments and documentation."""
        code_metrics = code_analysis.get('code_style_metrics', {})
        markdown_metrics = doc_analysis.get('markdown_metrics', {})
        comments_metrics = doc_analysis.get('code_comments_metrics', {})
        
        # Calculate various documentation metrics
        inline_analysis = self._analyze_inline_comments(comments_metrics)
        docstring_analysis = self._analyze_docstrings(comments_metrics)
        markdown_analysis = self._analyze_markdown(markdown_metrics)
        
        # Combine findings
        findings = {
            'positive': [],
            'negative': []
        }
        
        findings['positive'].extend(inline_analysis.get('positive', []))
        findings['negative'].extend(inline_analysis.get('negative', []))
        findings['positive'].extend(docstring_analysis.get('positive', []))
        findings['negative'].extend(docstring_analysis.get('negative', []))
        findings['positive'].extend(markdown_analysis.get('positive', []))
        findings['negative'].extend(markdown_analysis.get('negative', []))
        
        return {
            'metrics': {
                'inline_comments': inline_analysis['metrics'],
                'docstrings': docstring_analysis['metrics'],
                'markdown': markdown_analysis['metrics']
            },
            'findings': findings
        }

    def _analyze_style_violations(self, violations: list) -> Dict[str, Any]:
        """Analyze code style violations."""
        if not violations:
            return {
                'metrics': {
                    'total_violations': 0,
                    'violation_types': {}
                },
                'positive': ["Code follows PEP8 style guidelines perfectly"],
                'negative': []
            }
            
        categories = {}
        for violation in violations:
            category = violation.split()[0][:2]
            categories[category] = categories.get(category, 0) + 1
            
        total = len(violations)
        return {
            'metrics': {
                'total_violations': total,
                'violation_types': categories
            },
            'positive': [],
            'negative': [f"Found {total} style violations affecting code readability"]
        }

    def _analyze_line_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze line length and related metrics."""
        avg_length = metrics.get('avg_line_length', 0)
        max_length = metrics.get('max_line_length', 0)
        lines_over = metrics.get('lines_over_limit', 0)
        total_lines = metrics.get('total_lines', 1)
        
        findings = {'positive': [], 'negative': []}
        
        if avg_length <= self.thresholds['line_length']['ideal']:
            findings['positive'].append(
                f"Excellent line length practices (average {avg_length:.1f} characters)"
            )
        elif avg_length > self.thresholds['line_length']['acceptable']:
            findings['negative'].append(
                f"Lines are too long (average {avg_length:.1f} characters)"
            )
            
        return {
            'metrics': {
                'average_length': avg_length,
                'maximum_length': max_length,
                'lines_over_limit': lines_over,
                'lines_over_limit_percentage': (lines_over / total_lines) * 100
            },
            'positive': findings['positive'],
            'negative': findings['negative']
        }

    def _analyze_complexity_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        complex_lines = metrics.get('complex_lines', 0)
        total_lines = metrics.get('total_lines', 1)
        complexity_ratio = complex_lines / total_lines
        
        findings = {'positive': [], 'negative': []}
        
        if complexity_ratio <= self.thresholds['complexity']['low']:
            findings['positive'].append(
                f"Code maintains low complexity ({(complexity_ratio*100):.1f}% complex constructs)"
            )
        elif complexity_ratio > self.thresholds['complexity']['high']:
            findings['negative'].append(
                f"High code complexity ({(complexity_ratio*100):.1f}% complex constructs)"
            )
            
        return {
            'metrics': {
                'complex_lines': complex_lines,
                'complexity_ratio': complexity_ratio,
                'complexity_percentage': complexity_ratio * 100
            },
            'positive': findings['positive'],
            'negative': findings['negative']
        }

    def _analyze_formatting_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code formatting metrics."""
        blank_lines = metrics.get('blank_lines', 0)
        total_lines = metrics.get('total_lines', 1)
        blank_ratio = blank_lines / total_lines
        
        findings = {'positive': [], 'negative': []}
        
        if 0.1 <= blank_ratio <= 0.2:
            findings['positive'].append(
                f"Good use of whitespace ({(blank_ratio*100):.1f}% blank lines)"
            )
        elif blank_ratio > 0.3:
            findings['negative'].append(
                f"Excessive blank lines ({(blank_ratio*100):.1f}% of code)"
            )
            
        return {
            'metrics': {
                'blank_lines': blank_lines,
                'blank_ratio': blank_ratio,
                'blank_percentage': blank_ratio * 100
            },
            'positive': findings['positive'],
            'negative': findings['negative']
        }

    def _analyze_inline_comments(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze inline comments usage."""
        comment_ratio = metrics.get('comment_ratio', 0)
        commented_lines = metrics.get('commented_lines', 0)
        total_lines = metrics.get('total_lines', 1)
        
        findings = {'positive': [], 'negative': []}
        
        if comment_ratio >= self.thresholds['comments']['ratio']['good']:
            findings['positive'].append(
                f"Good inline documentation ({(comment_ratio*100):.1f}% of code commented)"
            )
        elif comment_ratio < self.thresholds['comments']['ratio']['minimum']:
            findings['negative'].append(
                f"Insufficient inline comments ({(comment_ratio*100):.1f}% of code commented)"
            )
            
        return {
            'metrics': {
                'commented_lines': commented_lines,
                'comment_ratio': comment_ratio,
                'comment_percentage': comment_ratio * 100
            },
            'positive': findings['positive'],
            'negative': findings['negative']
        }

    def _analyze_docstrings(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze docstring usage in user-defined functions."""
        function_count = metrics.get('function_count', 0)    # total number of UDFs
        docstring_count = metrics.get('docstring_count', 0)  # number of UDFs with docstrings
        
        findings = {
            'positive': [],
            'negative': []
        }
        
        if function_count > 0:
            coverage_ratio = docstring_count / function_count
            coverage_percentage = coverage_ratio * 100
            
            if coverage_ratio == 1.0:
                findings['positive'].append(
                    f"All {function_count} user-defined functions have docstrings"
                )
            elif coverage_ratio >= 0.8:
                findings['positive'].append(
                    f"Good documentation coverage: {docstring_count} out of {function_count} "
                    f"functions have docstrings ({coverage_percentage:.1f}%)"
                )
            else:
                findings['negative'].append(
                    f"Low documentation coverage: only {docstring_count} out of {function_count} "
                    f"functions have docstrings ({coverage_percentage:.1f}%)"
                )
        else:
            coverage_ratio = 0
            coverage_percentage = 0
            findings['positive'].append("No user-defined functions to document")
            
        return {
            'metrics': {
                'docstring_count': docstring_count,
                'function_count': function_count,
                'coverage_ratio': coverage_ratio,
                'coverage_percentage': coverage_percentage
            },
            'findings': findings
        }

    def _analyze_markdown(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze markdown documentation."""
        total_cells = metrics.get('total_cells', 0)
        total_content = metrics.get('total_content_length', 0)
        avg_content = total_content / max(total_cells, 1)
        
        findings = {'positive': [], 'negative': []}
        
        if total_cells >= self.thresholds['comments']['markdown']['good']:
            findings['positive'].append(
                f"Well-documented notebook with {total_cells} markdown cells"
            )
        elif total_cells < self.thresholds['comments']['markdown']['minimum']:
            findings['negative'].append(
                f"Insufficient notebook documentation (only {total_cells} markdown cells)"
            )
            
        return {
            'metrics': {
                'markdown_cells': total_cells,
                'total_content': total_content,
                'average_content': avg_content
            },
            'positive': findings['positive'],
            'negative': findings['negative']
        }
        
    def _analyze_code_conciseness(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code conciseness metrics."""
        conciseness = analysis.get('conciseness', {})
        
        metrics = {
            'duplicates': conciseness.get('duplicates', {'count': 0, 'instances': []}),
            'dead_code': conciseness.get('dead_code', {
                'unused_vars': [],
                'unused_functions': [],
                'unreachable': []
            }),
            'function_lengths': conciseness.get('function_lengths', {
                'average_length': 0,
                'functions': []
            }),
            'variable_usage': conciseness.get('variable_usage', {
                'declared': 0,
                'used': 0,
                'efficiency': 100
            })
        }
        
        findings = {
            'positive': [],
            'negative': []
        }
        
        # Add findings based on metrics
        if metrics['duplicates']['count'] == 0:
            findings['positive'].append("No code duplication found")
        else:
            findings['negative'].append(
                f"Found {metrics['duplicates']['count']} instances of duplicated code"
            )
            
        if not any([
            metrics['dead_code']['unused_vars'],
            metrics['dead_code']['unused_functions'],
            metrics['dead_code']['unreachable']
        ]):
            findings['positive'].append("No dead code detected")
        else:
            if metrics['dead_code']['unused_vars']:
                findings['negative'].append(
                    f"Found {len(metrics['dead_code']['unused_vars'])} unused variables"
                )
            if metrics['dead_code']['unused_functions']:
                findings['negative'].append(
                    f"Found {len(metrics['dead_code']['unused_functions'])} unused functions"
                )
            if metrics['dead_code']['unreachable']:
                findings['negative'].append(
                    f"Found {len(metrics['dead_code']['unreachable'])} instances of unreachable code"
                )
        
        if metrics['function_lengths']['average_length'] <= 15:
            findings['positive'].append("Functions are concise")
        elif metrics['function_lengths']['average_length'] > 30:
            findings['negative'].append("Some functions are too long")
        
        if metrics['variable_usage']['efficiency'] >= 90:
            findings['positive'].append("Efficient variable usage")
        elif metrics['variable_usage']['efficiency'] < 75:
            findings['negative'].append("Poor variable usage efficiency")
        
        return {
            'metrics': metrics,
            'findings': findings
        }
        
    def _analyze_code_structure(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code structure metrics."""
        structure = analysis.get('structure', {})
        metrics = structure.get('metrics', {
            'cyclomatic_complexity': {'total': 0, 'per_function': {}, 'average': 0},
            'function_dependencies': {'dependencies': {}, 'modularity_score': 100, 'circular_dependencies': []},
            'global_variables': {'count': 0, 'names': [], 'usage_count': {}},
            'execution_order': {'issues': [], 'score': 100, 'undefined_references': []}
        })
        
        findings = {
            'positive': [],
            'negative': []
        }
        
        # Analyze cyclomatic complexity
        complexity = metrics['cyclomatic_complexity']
        if complexity['average'] <= 10:
            findings['positive'].append("Functions have good cyclomatic complexity")
        elif complexity['average'] > 20:
            findings['negative'].append("Several functions have high cyclomatic complexity")
        
        # Analyze dependencies
        deps = metrics['function_dependencies']
        if deps['modularity_score'] >= 80:
            findings['positive'].append("Code has good modularity")
        elif deps['modularity_score'] < 60:
            findings['negative'].append("Poor modularity - high function interdependence")
        if deps['circular_dependencies']:
            findings['negative'].append(f"Found {len(deps['circular_dependencies'])} circular dependencies")
        
        # Analyze global variables
        globals_analysis = metrics['global_variables']
        if globals_analysis['count'] <= 3:
            findings['positive'].append("Minimal use of global variables")
        elif globals_analysis['count'] > 7:
            findings['negative'].append("Excessive use of global variables")
        
        # Analyze execution order
        execution = metrics['execution_order']
        if not execution['issues']:
            findings['positive'].append("Cells follow logical execution order")
        else:
            findings['negative'].append(f"Found {len(execution['issues'])} execution order issues")
        
        return {
            'metrics': metrics,
            'findings': findings
        }
        
    def _analyze_dataset_joins(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dataset join operations."""
        joins = analysis.get('dataset_joins', {
            'metrics': {
                'join_methods': {'methods': [], 'method_counts': {}, 'consistency_score': 100},
                'key_handling': {'issues': [], 'score': 100},
                'efficiency': {'issues': [], 'score': 100},
                'modularity': {'reusable_count': 0, 'repeated_count': 0, 'score': 100}
            }
        })
        
        metrics = joins.get('metrics', {})
        
        findings = {
            'positive': [],
            'negative': []
        }
        
        # Analyze join method consistency
        methods = metrics.get('join_methods', {})
        if methods.get('consistency_score', 100) >= 90:
            findings['positive'].append("Consistent use of join methods")
        elif methods.get('consistency_score', 100) < 70:
            findings['negative'].append(
                f"Inconsistent join methods (score: {methods.get('consistency_score', 0):.1f}/100)"
            )
        
        # Analyze key handling
        key_handling = metrics.get('key_handling', {})
        if not key_handling.get('issues', []):
            findings['positive'].append("Proper handling of join keys")
        else:
            issues = key_handling.get('issues', [])
            findings['negative'].append(
                f"Found {len(issues)} key handling issues"
            )
        
        # Analyze efficiency
        efficiency = metrics.get('efficiency', {})
        if not efficiency.get('issues', []):
            findings['positive'].append("Efficient join operations")
        else:
            issues = efficiency.get('issues', [])
            findings['negative'].append(
                f"Found {len(issues)} efficiency issues in joins"
            )
        
        # Analyze modularity
        modularity = metrics.get('modularity', {})
        if modularity.get('score', 100) >= 80:
            findings['positive'].append("Good join operation modularity")
        elif modularity.get('repeated_count', 0) > 0:
            findings['negative'].append(
                f"Found {modularity.get('repeated_count', 0)} repeated join patterns"
            )
        
        # Calculate overall quality
        scores = [
            methods.get('consistency_score', 100),
            key_handling.get('score', 100),
            efficiency.get('score', 100),
            modularity.get('score', 100)
        ]
        overall_quality = sum(scores) / len(scores)
        
        if overall_quality >= 90:
            findings['positive'].append("Excellent overall join quality")
        elif overall_quality < 60:
            findings['negative'].append("Poor overall join quality - needs improvement")
        
        return {
            'metrics': metrics,
            'findings': findings,
            'overall_quality': overall_quality
        }
        
    def _analyze_code_reusability(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code reusability metrics."""
        reusability = analysis.get('reusability', {
            'metrics': {
                'hardcoded_values': {'count': 0, 'instances': [], 'score': 100},
                'function_reuse': {'reuse_count': {}, 'average_reuse': 0, 'score': 100},
                'oop_usage': {'classes': [], 'appropriate_usage': True, 'reasons': [], 'score': 100},
                'parameterization': {'global_usage': [], 'parameter_score': 100}
            }
        })
        
        metrics = reusability.get('metrics', {})
        
        findings = {
            'positive': [],
            'negative': []
        }
        
        # Analyze hardcoded values
        hardcoded = metrics.get('hardcoded_values', {})
        if hardcoded.get('score', 100) >= 90:
            findings['positive'].append("Minimal use of hardcoded values")
        elif hardcoded.get('count', 0) > 0:
            findings['negative'].append(
                f"Found {hardcoded.get('count', 0)} hardcoded values that could be parameterized"
            )
        
        # Analyze function reuse
        reuse = metrics.get('function_reuse', {})
        if reuse.get('average_reuse', 0) >= 2:
            findings['positive'].append("Good function reuse patterns")
        elif reuse.get('reuse_count'):
            findings['negative'].append(
                f"Functions are not reused enough (average: {reuse.get('average_reuse', 0):.1f} times)"
            )
        
        # Analyze OOP usage
        oop = metrics.get('oop_usage', {})
        if oop.get('classes') and oop.get('appropriate_usage', True):
            findings['positive'].append("Appropriate use of object-oriented programming")
        elif oop.get('reasons', []):
            findings['negative'].append(
                f"Found {len(oop.get('reasons', []))} issues with class design"
            )
        
        # Analyze parameterization
        params = metrics.get('parameterization', {})
        if not params.get('global_usage', []):
            findings['positive'].append("Good function parameterization")
        else:
            findings['negative'].append(
                f"Found {len(params.get('global_usage', []))} functions using global variables"
            )
        
        # Calculate overall quality
        scores = [
            hardcoded.get('score', 100) * 0.3,  # 30% weight
            reuse.get('score', 100) * 0.3,      # 30% weight
            oop.get('score', 100) * 0.2,        # 20% weight
            params.get('parameter_score', 100) * 0.2  # 20% weight
        ]
        overall_quality = sum(scores)
        
        if overall_quality >= 90:
            findings['positive'].append("Excellent overall code reusability")
        elif overall_quality < 60:
            findings['negative'].append("Poor code reusability - needs improvement")
        
        return {
            'metrics': metrics,
            'findings': findings,
            'overall_quality': overall_quality
        }
        
    def _analyze_advanced_techniques(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze advanced coding techniques."""
        techniques = analysis.get('advanced_techniques', {})
        metrics = techniques.get('metrics', {
            'library_usage': {'found_libraries': [], 'categories': {}, 'score': 0},
            'ml_complexity': {'models': [], 'complexity_score': 0},
            'optimization': {'techniques': {}, 'score': 0},
            'custom_algorithms': {'implementations': [], 'score': 0}
        })

        findings = {
            'positive': [],
            'negative': []
        }

        # Analyze library usage
        lib_usage = metrics['library_usage']
        if lib_usage['score'] >= 80:
            findings['positive'].append("Good use of advanced libraries")
        elif lib_usage['score'] < 40:
            findings['negative'].append("Limited use of advanced libraries")

        # Analyze ML complexity
        ml = metrics['ml_complexity']
        if ml['complexity_score'] >= 70:
            findings['positive'].append("Advanced ML techniques utilized")
        elif ml['models']:
            findings['negative'].append("Basic ML implementation - consider advanced techniques")

        # Analyze optimization
        opt = metrics['optimization']
        if opt['score'] >= 60:
            findings['positive'].append("Good use of optimization techniques")
        elif opt['score'] < 30:
            findings['negative'].append("Limited optimization - consider performance improvements")

        # Analyze custom algorithms
        custom = metrics['custom_algorithms']
        if custom['score'] >= 50:
            findings['positive'].append("Good implementation of custom algorithms")
        elif not custom['implementations']:
            findings['negative'].append("No custom algorithm implementations found")

        return {
            'metrics': metrics,
            'findings': findings
        }

    def _analyze_visualization_types(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze visualization types."""
        viz = analysis.get('visualization_types', {})
        metrics = viz.get('metrics', {
            'diversity': {'types': {}, 'unique_count': 0, 'score': 0},
            'advanced_viz': {'visualizations': {}, 'score': 0},
            'appropriateness': {'issues': [], 'score': 100}
        })

        findings = {
            'positive': [],
            'negative': []
        }

        # Analyze diversity
        diversity = metrics['diversity']
        if diversity['score'] >= 80:
            findings['positive'].append("Good diversity of visualization types")
        elif diversity['score'] < 40:
            findings['negative'].append("Limited visualization variety")

        # Analyze advanced visualizations
        advanced = metrics['advanced_viz']
        if advanced['score'] >= 60:
            findings['positive'].append("Good use of advanced visualizations")
        elif advanced['score'] < 30:
            findings['negative'].append("Consider using more advanced visualization techniques")

        # Analyze appropriateness
        appropriate = metrics['appropriateness']
        if appropriate['score'] >= 90:
            findings['positive'].append("Appropriate visualization choices")
        elif appropriate['issues']:
            findings['negative'].append(f"Found {len(appropriate['issues'])} inappropriate visualization choices")

        return {
            'metrics': metrics,
            'findings': findings
        }

    def _analyze_visualization_formatting(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze visualization formatting."""
        formatting = analysis.get('visualization_formatting', {})
        metrics = formatting.get('metrics', {
            'axis_labels': {'labels': [], 'missing': [], 'score': 100},
            'titles': {'titles': [], 'missing': [], 'quality_score': 0, 'score': 100},
            'legends': {'count': 0, 'issues': [], 'score': 100},
            'readability': {'issues': [], 'score': 100}
        })

        findings = {
            'positive': [],
            'negative': []
        }

        # Analyze axis labels
        labels = metrics['axis_labels']
        if labels['score'] >= 90:
            findings['positive'].append("Well-labeled axes")
        elif labels['missing']:
            findings['negative'].append(f"Missing axis labels in {len(labels['missing'])} plots")

        # Analyze titles
        titles = metrics['titles']
        if titles['score'] >= 90:
            findings['positive'].append("Good plot titles")
        elif titles['missing']:
            findings['negative'].append(f"Missing or poor titles in {len(titles['missing'])} plots")

        # Analyze legends
        legends = metrics['legends']
        if legends['score'] >= 90:
            findings['positive'].append("Clear and appropriate legends")
        elif legends['issues']:
            findings['negative'].append(f"Legend issues in {len(legends['issues'])} plots")

        # Analyze readability
        readability = metrics['readability']
        if readability['score'] >= 90:
            findings['positive'].append("Good visualization readability")
        elif readability['score'] < 70:
            findings['negative'].append("Poor visualization readability")

        return {
            'metrics': metrics,
            'findings': findings
        }
