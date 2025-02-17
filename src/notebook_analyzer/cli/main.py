"""
Notebook Analyzer CLI Main Module.

This module provides the command-line interface for the notebook analyzer,
allowing users to analyze Jupyter notebooks and generate reports.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 23:11:34
"""

import argparse
import sys
import os
from typing import List, Optional
from pathlib import Path

from ..core.analysis_orchestrator import AnalysisOrchestrator
from ..reporting import (
    create_report_generator,
    get_available_formatters,
    get_available_templates
)


def parse_args(args: List[str]) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args (List[str]): Command-line arguments

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Analyze Jupyter notebooks for code quality and generate reports."
    )

    parser.add_argument(
        "notebook_path",
        type=str,
        help="Path to the Jupyter notebook file or directory containing notebooks"
    )

    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default="reports",
        help="Directory to store generated reports (default: reports)"
    )

    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["html", "markdown"],
        default="html",
        help="Output format for the report (default: html)"
    )

    parser.add_argument(
        "--categories",
        type=str,
        nargs="+",
        choices=["builder_mindset", "business_intelligence"],
        default=["builder_mindset", "business_intelligence"],
        help="Analysis categories to include (default: all)"
    )

    parser.add_argument(
        "--metrics",
        type=str,
        nargs="+",
        help="Specific metrics to analyze (default: all available metrics)"
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively analyze notebooks in subdirectories"
    )

    parser.add_argument(
        "--list-metrics",
        action="store_true",
        help="List available metrics and exit"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Run analyzers in parallel (default: True)"
    )

    return parser.parse_args(args)


def list_available_metrics():
    """Display available metrics and exit."""
    formatters = get_available_formatters()
    print("\nAvailable Metrics:")
    
    for category, metrics in formatters.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for metric in metrics:
            metric_name = metric.replace('Formatter', '').lower()
            print(f"  - {metric_name}")


def validate_notebook_path(path: str, recursive: bool) -> List[Path]:
    """
    Validate and resolve notebook paths.

    Args:
        path (str): Path to notebook or directory
        recursive (bool): Whether to search recursively

    Returns:
        List[Path]: List of valid notebook paths

    Raises:
        SystemExit: If no valid notebooks are found
    """
    input_path = Path(path)
    notebooks = []

    if input_path.is_file():
        if input_path.suffix == '.ipynb':
            notebooks.append(input_path)
        else:
            print(f"Error: {path} is not a Jupyter notebook file")
            sys.exit(1)
    elif input_path.is_dir():
        pattern = '**/*.ipynb' if recursive else '*.ipynb'
        notebooks.extend(input_path.glob(pattern))
    else:
        print(f"Error: {path} does not exist")
        sys.exit(1)

    if not notebooks:
        print(f"Error: No notebooks found in {path}")
        sys.exit(1)

    return notebooks


def analyze_notebook(
    notebook_path: Path,
    categories: List[str],
    metrics: Optional[List[str]],
    verbose: bool,
    parallel: bool = True
) -> dict:
    """
    Analyze a single notebook.

    Args:
        notebook_path (Path): Path to the notebook
        categories (List[str]): Categories to analyze
        metrics (Optional[List[str]]): Specific metrics to analyze
        verbose (bool): Whether to print verbose output
        parallel (bool): Whether to run analyzers in parallel

    Returns:
        dict: Analysis results
    """
    if verbose:
        print(f"\nAnalyzing {notebook_path}...")

    analyzer = AnalysisOrchestrator()
    
    try:
        results = analyzer.analyze_notebook(  # Changed from analyze() to analyze_notebook()
            str(notebook_path),
            parallel=parallel
        )
        
        if verbose:
            print(f"Analysis completed for {notebook_path}")
        
        return results
    
    except Exception as e:
        print(f"Error analyzing {notebook_path}: {str(e)}")
        return None


def generate_report(
    results: dict,
    output_dir: str,
    format_type: str,
    notebook_path: Path,
    verbose: bool
) -> Optional[str]:
    """
    Generate a report for analysis results.

    Args:
        results (dict): Analysis results
        output_dir (str): Output directory
        format_type (str): Report format
        notebook_path (Path): Path to the analyzed notebook
        verbose (bool): Whether to print verbose output

    Returns:
        Optional[str]: Path to generated report, or None if generation failed
    """
    if not results:
        return None

    try:
        generator = create_report_generator(output_dir)
        report_name = f"{notebook_path.stem}_analysis"
        
        report_path = generator.generate_report(
            results,
            format_type=format_type,
            filename=report_name
        )
        
        if verbose:
            print(f"Report generated: {report_path}")
        
        return report_path
    
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return None


def main():
    """Main entry point for the CLI."""
    args = parse_args(sys.argv[1:])

    if args.list_metrics:
        list_available_metrics()
        sys.exit(0)

    notebooks = validate_notebook_path(args.notebook_path, args.recursive)
    
    if args.verbose:
        print(f"\nFound {len(notebooks)} notebook(s) to analyze")

    for notebook in notebooks:
        results = analyze_notebook(
            notebook,
            args.categories,
            args.metrics,
            args.verbose,
            args.parallel
        )
        
        if results:
            report_path = generate_report(
                results,
                args.output_dir,
                args.format,
                notebook,
                args.verbose
            )
            
            if report_path:
                print(f"\nAnalysis complete for {notebook}")
                print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
