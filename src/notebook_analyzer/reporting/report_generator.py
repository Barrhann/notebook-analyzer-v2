"""
Report Generator module - Main orchestrator for report generation
"""

from typing import Dict, Any, List
from datetime import datetime
import os
import getpass
from .formatters.text_formatter import TextReportFormatter
from .analyzers.metrics_analyzer import MetricsAnalyzer

class ReportGenerator:
    def __init__(self):
        self.metrics_analyzer = MetricsAnalyzer()
        self.text_formatter = TextReportFormatter()

    def generate(self, code_analysis: Dict[str, Any], doc_analysis: Dict[str, Any],
                current_time: str = None, current_user: str = None) -> Dict[str, Any]:
        """Generate a comprehensive report from code and documentation analysis."""
        metrics_analysis = self.metrics_analyzer.analyze_all(code_analysis, doc_analysis)
        
        quality_score = self._calculate_quality_score(metrics_analysis)
        deductions = self._calculate_deductions(metrics_analysis)
        
        # Get notebook metadata
        notebook_path = code_analysis.get('notebook_path', '')
        notebook_name = os.path.basename(notebook_path) if notebook_path else 'Unknown Notebook'
        
        # Get notebook author from metadata
        notebook_metadata = code_analysis.get('notebook_metadata', {})
        # Look for author in different possible metadata locations
        author = (notebook_metadata.get('author') or
                 notebook_metadata.get('kernelspec', {}).get('author') or
                 notebook_metadata.get('metadata', {}).get('author') or
                 '')
        
        # Use system time and user if not provided
        if current_time is None:
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        if current_user is None:
            current_user = getpass.getuser()
        
        return {
            'summary': {
                'notebook_name': notebook_name,
                'notebook_author': author if author else None,  # Only include if author exists
                'generation_date': current_time,
                'generated_by': current_user,
                'overall_quality_score': quality_score,
                'score_deductions': deductions
            },
            'analysis': metrics_analysis
        }

    def generate_text_report(self, code_analysis: Dict[str, Any], doc_analysis: Dict[str, Any],
                           current_time: str = "2025-02-15 02:05:28",
                           current_user: str = "Barrhann") -> str:
        """
        Generate human-readable text report.
        
        Args:
            code_analysis: Results from code format analysis
            doc_analysis: Results from documentation analysis
            current_time: Current UTC time in YYYY-MM-DD HH:MM:SS format
            current_user: Current user's login name
            
        Returns:
            str: Formatted text report
        """
        report_data = self.generate(code_analysis, doc_analysis, current_time, current_user)
        return self.text_formatter.format_report(report_data)

    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        score = 100.0
        
        # Code formatting deductions
        formatting = analysis['code_formatting']
        style_violations = formatting['metrics']['style_violations']['total_violations']
        if style_violations > 0:
            score -= min(style_violations * 0.5, 30)  # Max 30 points deduction for style
            
        complexity = formatting['metrics']['complexity_metrics']['complexity_percentage']
        if complexity > 20:
            score -= min((complexity - 20) * 0.5, 20)  # Max 20 points deduction for complexity
            
        # Comments deductions
        comments = analysis['code_comments']
        comment_coverage = comments['metrics']['inline_comments']['comment_percentage']
        redundant_count = len(comments['metrics'].get('redundant_comments', []))
        
        if comment_coverage < 20:
            score -= min((20 - comment_coverage) * 0.5, 25)  # Max 25 points deduction for low coverage
            
        # Small deduction for redundant comments
        if redundant_count > 0:
            score -= min(redundant_count * 0.5, 10)  # Max 10 points deduction for redundant comments
            
        # Only apply docstring deductions if there are functions to document
        docstrings = comments['metrics']['docstrings']
        if docstrings['function_count'] > 0:  # Only if there are functions
            docstring_coverage = docstrings['coverage_percentage']
            if docstring_coverage < 80:
                score -= min((80 - docstring_coverage) * 0.25, 25)  # Max 25 points deduction for docstrings
            
        # Conciseness deductions
        conciseness = analysis['code_conciseness']['metrics']
        
        # Duplicate code deduction
        if conciseness['duplicates']['count'] > 0:
            score -= min(conciseness['duplicates']['count'] * 2, 15)  # Max 15 points
            
        # Dead code deduction
        dead_code = conciseness['dead_code']
        dead_code_count = (
            len(dead_code['unused_vars']) +
            len(dead_code['unused_functions']) +
            len(dead_code['unreachable'])
        )
        if dead_code_count > 0:
            score -= min(dead_code_count, 10)  # Max 10 points
            
        # Function length deduction
        if conciseness['function_lengths']['average_length'] > 30:
            score -= min((conciseness['function_lengths']['average_length'] - 30) * 0.5, 10)
            
        # Variable usage deduction
        if conciseness['variable_usage']['efficiency'] < 75:
            score -= min((75 - conciseness['variable_usage']['efficiency']) * 0.2, 10)
            
        # Structure deductions
        structure = analysis.get('code_structure', {}).get('metrics', {})
        
        # Complexity deduction
        complexity = structure.get('cyclomatic_complexity', {})
        if complexity.get('average', 0) > 10:
            score -= min((complexity['average'] - 10) * 2, 15)  # Max 15 points
            
        # Modularity deduction
        deps = structure.get('function_dependencies', {})
        if deps.get('modularity_score', 100) < 80:
            score -= min((80 - deps['modularity_score']) * 0.2, 10)  # Max 10 points
            
        # Global variables deduction
        globals_analysis = structure.get('global_variables', {})
        if globals_analysis.get('count', 0) > 3:
            score -= min((globals_analysis['count'] - 3) * 2, 10)  # Max 10 points
            
        # Execution order deduction
        execution = structure.get('execution_order', {})
        if execution.get('score', 100) < 100:
            score -= min((100 - execution['score']) * 0.15, 10)  # Max 10 points
            
        # Dataset Join deductions
        joins = analysis.get('dataset_join', {}).get('metrics', {})
        
        # Join method consistency deduction
        methods = joins.get('join_methods', {})
        if methods.get('consistency_score', 100) < 90:
            score -= min((90 - methods['consistency_score']) * 0.2, 10)  # Max 10 points
            
        # Key handling deduction
        key_handling = joins.get('key_handling', {})
        if key_handling.get('score', 100) < 100:
            score -= min((100 - key_handling['score']) * 0.15, 10)  # Max 10 points
            
        # Efficiency deduction
        efficiency = joins.get('efficiency', {})
        if efficiency.get('score', 100) < 100:
            score -= min((100 - efficiency['score']) * 0.25, 15)  # Max 15 points
            
        # Modularity deduction
        modularity = joins.get('modularity', {})
        if modularity.get('score', 100) < 80:
            score -= min((80 - modularity['score']) * 0.2, 10)  # Max 10 points
            
        # Code Reusability deductions
        reusability = analysis.get('code_reusability', {}).get('metrics', {})
        
        # Hardcoded values deduction
        hardcoded = reusability.get('hardcoded_values', {})
        if hardcoded.get('score', 100) < 90:
            score -= min((90 - hardcoded['score']) * 0.3, 15)  # Max 15 points
            
        # Function reuse deduction
        reuse = reusability.get('function_reuse', {})
        if reuse.get('score', 100) < 80:
            score -= min((80 - reuse['score']) * 0.3, 15)  # Max 15 points
            
        # OOP usage deduction
        oop = reusability.get('oop_usage', {})
        if oop.get('score', 100) < 80:
            score -= min((80 - oop['score']) * 0.2, 10)  # Max 10 points
            
        # Parameterization deduction
        params = reusability.get('parameterization', {})
        if params.get('parameter_score', 100) < 90:
            score -= min((90 - params['parameter_score']) * 0.2, 10)  # Max 10 points
            
        # Advanced Techniques deductions
        tech = analysis.get('advanced_techniques', {}).get('metrics', {})
        if tech.get('library_usage', {}).get('score', 100) < 60:
            score -= min((60 - tech['library_usage']['score']) * 0.2, 10)
        if tech.get('ml_complexity', {}).get('complexity_score', 100) < 50:
            score -= min((50 - tech['ml_complexity']['complexity_score']) * 0.2, 10)
        if tech.get('optimization', {}).get('score', 100) < 50:
            score -= min((50 - tech['optimization']['score']) * 0.2, 10)
        
        # Visualization Type deductions
        viz = analysis.get('visualization_types', {}).get('metrics', {})
        if viz.get('diversity', {}).get('score', 100) < 70:
            score -= min((70 - viz['diversity']['score']) * 0.2, 10)
        if viz.get('appropriateness', {}).get('score', 100) < 80:
            score -= min((80 - viz['appropriateness']['score']) * 0.2, 10)
        
        # Visualization Formatting deductions
        fmt = analysis.get('visualization_formatting', {}).get('metrics', {})
        if fmt.get('axis_labels', {}).get('score', 100) < 90:
            score -= min((90 - fmt['axis_labels']['score']) * 0.15, 7.5)
        if fmt.get('titles', {}).get('score', 100) < 90:
            score -= min((90 - fmt['titles']['score']) * 0.15, 7.5)
        if fmt.get('legends', {}).get('score', 100) < 90:
            score -= min((90 - fmt['legends']['score']) * 0.15, 7.5)
        if fmt.get('readability', {}).get('score', 100) < 90:
            score -= min((90 - fmt['readability']['score']) * 0.15, 7.5)
            
        return max(0, round(score, 1))

    def _calculate_deductions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate and explain score deductions."""
        deductions = []
        
        # Style violations deduction
        formatting = analysis['code_formatting']
        violations = formatting['metrics']['style_violations']['total_violations']
        if violations > 0:
            points = min(violations * 0.5, 30)
            deductions.append({
                'category': 'Code Style Issues',
                'points': points,
                'reason': f'Found {violations} style issues affecting code readability'
            })
            
        # Complexity deduction
        complexity = formatting['metrics']['complexity_metrics']['complexity_percentage']
        if complexity > 20:
            points = min((complexity - 20) * 0.5, 20)
            deductions.append({
                'category': 'Code Complexity',
                'points': points,
                'reason': f'Code complexity ({complexity:.1f}%) exceeds recommended 20%'
            })
            
        # Comments deduction
        comments = analysis['code_comments']
        comment_coverage = comments['metrics']['inline_comments']['comment_percentage']
        redundant_count = len(comments['metrics'].get('redundant_comments', []))
        
        if comment_coverage < 20:
            points = min((20 - comment_coverage) * 0.5, 25)
            deductions.append({
                'category': 'Code Comments',
                'points': points,
                'reason': f'Insufficient code comments (only {comment_coverage:.1f}% coverage)'
            })
            
        if redundant_count > 0:
            points = min(redundant_count * 0.5, 10)
            deductions.append({
                'category': 'Comment Quality',
                'points': points,
                'reason': f'Found {redundant_count} redundant comments that could be improved'
            })
            
        # Docstrings deduction - only if there are functions to document
        docstrings = comments['metrics']['docstrings']
        if docstrings['function_count'] > 0:  # Only calculate deduction if there are functions
            coverage = docstrings['coverage_percentage']
            if coverage < 80:
                points = min((80 - coverage) * 0.25, 25)
                deductions.append({
                    'category': 'Function Documentation',
                    'points': points,
                    'reason': (
                        f'Only {docstrings["docstring_count"]} out of {docstrings["function_count"]} '
                        f'functions have docstrings ({coverage:.1f}% coverage)'
                    )
                })
        
        # Conciseness deductions
        conciseness = analysis['code_conciseness']['metrics']
        
        if conciseness['duplicates']['count'] > 0:
            points = min(conciseness['duplicates']['count'] * 2, 15)
            deductions.append({
                'category': 'Code Duplication',
                'points': points,
                'reason': f"Found {conciseness['duplicates']['count']} instances of duplicated code"
            })
            
        dead_code = conciseness['dead_code']
        dead_code_count = (
            len(dead_code['unused_vars']) +
            len(dead_code['unused_functions']) +
            len(dead_code['unreachable'])
        )
        if dead_code_count > 0:
            points = min(dead_code_count, 10)
            deductions.append({
                'category': 'Dead Code',
                'points': points,
                'reason': f"Found {dead_code_count} instances of unused or unreachable code"
            })
            
        if conciseness['function_lengths']['average_length'] > 30:
            points = min((conciseness['function_lengths']['average_length'] - 30) * 0.5, 10)
            deductions.append({
                'category': 'Function Length',
                'points': points,
                'reason': f"Average function length ({conciseness['function_lengths']['average_length']:.1f} lines) exceeds recommended 30 lines"
            })
            
        if conciseness['variable_usage']['efficiency'] < 75:
            points = min((75 - conciseness['variable_usage']['efficiency']) * 0.2, 10)
            deductions.append({
                'category': 'Variable Usage',
                'points': points,
                'reason': f"Low variable usage efficiency ({conciseness['variable_usage']['efficiency']:.1f}%)"
            })
            
       # Structure deductions
        structure = analysis.get('code_structure', {}).get('metrics', {})
        
        complexity = structure.get('cyclomatic_complexity', {})
        if complexity.get('average', 0) > 10:
            points = min((complexity['average'] - 10) * 2, 15)
            deductions.append({
                'category': 'Code Complexity',
                'points': points,
                'reason': f"Average cyclomatic complexity ({complexity['average']:.1f}) exceeds recommended 10"
            })
            
        deps = structure.get('function_dependencies', {})
        if deps.get('modularity_score', 100) < 80:
            points = min((80 - deps['modularity_score']) * 0.2, 10)
            deductions.append({
                'category': 'Code Modularity',
                'points': points,
                'reason': f"Low modularity score ({deps['modularity_score']:.1f}/100)"
            })
            
        globals_analysis = structure.get('global_variables', {})
        if globals_analysis.get('count', 0) > 3:
            points = min((globals_analysis['count'] - 3) * 2, 10)
            deductions.append({
                'category': 'Global Variables',
                'points': points,
                'reason': f"Too many global variables ({globals_analysis['count']})"
            })
            
        execution = structure.get('execution_order', {})
        if execution.get('score', 100) < 100:
            points = min((100 - execution['score']) * 0.15, 10)
            deductions.append({
                'category': 'Execution Order',
                'points': points,
                'reason': f"Issues with cell execution order (score: {execution['score']}/100)"
            })
            
        # Dataset Join deductions
        joins = analysis.get('dataset_join', {}).get('metrics', {})
        
        methods = joins.get('join_methods', {})
        if methods.get('consistency_score', 100) < 90:
            points = min((90 - methods['consistency_score']) * 0.2, 10)
            deductions.append({
                'category': 'Join Methods',
                'points': points,
                'reason': f"Inconsistent join methods (score: {methods['consistency_score']:.1f}/100)"
            })
            
        key_handling = joins.get('key_handling', {})
        if key_handling.get('score', 100) < 100:
            points = min((100 - key_handling['score']) * 0.15, 10)
            deductions.append({
                'category': 'Join Keys',
                'points': points,
                'reason': f"Issues with join key handling ({len(key_handling.get('issues', []))} issues found)"
            })
            
        efficiency = joins.get('efficiency', {})
        if efficiency.get('score', 100) < 100:
            points = min((100 - efficiency['score']) * 0.25, 15)
            deductions.append({
                'category': 'Join Efficiency',
                'points': points,
                'reason': f"Inefficient join operations ({len(efficiency.get('issues', []))} issues found)"
            })
            
        modularity = joins.get('modularity', {})
        if modularity.get('score', 100) < 80:
            points = min((80 - modularity['score']) * 0.2, 10)
            deductions.append({
                'category': 'Join Modularity',
                'points': points,
                'reason': f"Poor join modularity (score: {modularity['score']:.1f}/100)"
            })
            
        # Code Reusability deductions
        reusability = analysis.get('code_reusability', {}).get('metrics', {})
        
        hardcoded = reusability.get('hardcoded_values', {})
        if hardcoded.get('score', 100) < 90:
            points = min((90 - hardcoded['score']) * 0.3, 15)
            deductions.append({
                'category': 'Hardcoded Values',
                'points': points,
                'reason': f"Found {hardcoded.get('count', 0)} hardcoded values that should be parameterized"
            })
            
        reuse = reusability.get('function_reuse', {})
        if reuse.get('score', 100) < 80:
            points = min((80 - reuse['score']) * 0.3, 15)
            deductions.append({
                'category': 'Function Reuse',
                'points': points,
                'reason': f"Low function reuse (average: {reuse.get('average_reuse', 0):.1f} times)"
            })
            
        oop = reusability.get('oop_usage', {})
        if oop.get('score', 100) < 80:
            points = min((80 - oop['score']) * 0.2, 10)
            deductions.append({
                'category': 'OOP Usage',
                'points': points,
                'reason': "Inappropriate or missing object-oriented design"
            })
            
        params = reusability.get('parameterization', {})
        if params.get('parameter_score', 100) < 90:
            points = min((90 - params['parameter_score']) * 0.2, 10)
            deductions.append({
                'category': 'Function Parameterization',
                'points': points,
                'reason': f"Found {len(params.get('global_usage', []))} functions using global variables"
            })
            
        # Advanced Techniques deductions
        tech = analysis.get('advanced_techniques', {}).get('metrics', {})
        
        if tech.get('library_usage', {}).get('score', 100) < 60:
            points = min((60 - tech['library_usage']['score']) * 0.2, 10)
            deductions.append({
                'category': 'Advanced Libraries',
                'points': points,
                'reason': "Limited use of advanced libraries"
            })
            
        if tech.get('ml_complexity', {}).get('complexity_score', 100) < 50:
            points = min((50 - tech['ml_complexity']['complexity_score']) * 0.2, 10)
            deductions.append({
                'category': 'ML Complexity',
                'points': points,
                'reason': "Basic ML implementation"
            })
            
        # Visualization Type deductions
        viz = analysis.get('visualization_types', {}).get('metrics', {})
        
        if viz.get('diversity', {}).get('score', 100) < 70:
            points = min((70 - viz['diversity']['score']) * 0.2, 10)
            deductions.append({
                'category': 'Visualization Diversity',
                'points': points,
                'reason': "Limited variety in visualization types"
            })
            
        if viz.get('appropriateness', {}).get('score', 100) < 80:
            points = min((80 - viz['appropriateness']['score']) * 0.2, 10)
            deductions.append({
                'category': 'Visualization Appropriateness',
                'points': points,
                'reason': f"Found {len(viz['appropriateness'].get('issues', []))} inappropriate visualization choices"
            })
            
        # Visualization Formatting deductions
        fmt = analysis.get('visualization_formatting', {}).get('metrics', {})
        
        if fmt.get('axis_labels', {}).get('score', 100) < 90:
            points = min((90 - fmt['axis_labels']['score']) * 0.15, 7.5)
            deductions.append({
                'category': 'Axis Labels',
                'points': points,
                'reason': f"Missing axis labels in {len(fmt['axis_labels'].get('missing', []))} plots"
            })
            
        if fmt.get('titles', {}).get('score', 100) < 90:
            points = min((90 - fmt['titles']['score']) * 0.15, 7.5)
            deductions.append({
                'category': 'Plot Titles',
                'points': points,
                'reason': f"Missing or poor titles in {len(fmt['titles'].get('missing', []))} plots"
            })
            
        return deductions
