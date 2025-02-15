"""
CLI Main module for Notebook Analyzer
Created by: Barrhann
"""

import argparse
import json
import sys
import traceback  # Added missing import
from datetime import datetime
from pathlib import Path
from typing import Optional

from notebook_analyzer import NotebookAnalyzer

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze Jupyter notebooks for code quality and documentation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single notebook
  notebook-analyzer notebook.ipynb
  
  # Save analysis to a file
  notebook-analyzer notebook.ipynb -o report.txt
  
  # Analyze all notebooks in a directory
  notebook-analyzer path/to/notebooks/
  
  # Get JSON format output
  notebook-analyzer notebook.ipynb --format json
        """
    )
    
    parser.add_argument(
        "notebook_path",
        type=str,
        help="Path to the Jupyter notebook file or directory containing notebooks"
    )
    
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to save the analysis report. If not provided, prints to stdout"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)"
    )
    
    return parser.parse_args()

def analyze_notebook(path: str, output_path: Optional[str] = None, output_format: str = "text") -> None:
    """
    Analyze a single notebook and output the results.
    
    Args:
        path: Path to the notebook
        output_path: Path to save the report (optional)
        output_format: Format of the output ("json" or "text")
    """
    try:
        # Create analyzer instance
        analyzer = NotebookAnalyzer()
        
        # Read notebook content once
        notebook_content = analyzer.notebook_reader.read(path)
        
        # Perform analyses
        code_analysis = analyzer.code_analyzer.analyze(notebook_content)
        doc_analysis = analyzer.doc_analyzer.analyze(notebook_content)
        
        # Format the report
        if output_format == "json":
            report = analyzer.report_generator.generate(code_analysis, doc_analysis)
            formatted_report = json.dumps(report, indent=2)
        else:
            formatted_report = analyzer.report_generator.generate_text_report(
                code_analysis, doc_analysis
            )
        
        # Output the report
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_report)
            print(f"Report saved to: {output_path}")
        else:
            print(formatted_report)
            
    except Exception as e:
        print(f"Error analyzing notebook {path}:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)

def process_directory(directory_path: str, output_dir: Optional[str], output_format: str) -> None:
    """
    Process all notebooks in a directory.
    
    Args:
        directory_path (str): Path to the directory containing notebooks
        output_dir (Optional[str]): Directory to save reports
        output_format (str): Format of the output ("json" or "text")
    """
    path = Path(directory_path)
    notebooks = list(path.glob('**/*.ipynb'))
    
    if not notebooks:
        print(f"No Jupyter notebooks found in {path}", file=sys.stderr)
        sys.exit(1)
    
    for notebook in notebooks:
        print(f"\nAnalyzing {notebook}...")
        output_path = None
        
        if output_dir:
            # Create output path for each notebook
            output_base = Path(output_dir)
            output_base.mkdir(parents=True, exist_ok=True)
            
            # Create a similar directory structure as the input
            relative_path = notebook.relative_to(path)
            output_file = relative_path.with_suffix(f'.{output_format}')
            output_path = str(output_base / output_file)
            
            # Ensure the parent directory exists
            output_file_path = Path(output_path)
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        analyze_notebook(str(notebook), output_path, output_format)

def main() -> None:
    """Main entry point for the CLI application."""
    try:
        args = parse_args()
        path = Path(args.notebook_path)
        
        if path.is_file():
            if not path.suffix == '.ipynb':
                print(f"Error: {path} is not a Jupyter notebook file", file=sys.stderr)
                sys.exit(1)
            analyze_notebook(str(path), args.output, args.format)
        
        elif path.is_dir():
            process_directory(str(path), args.output, args.format)
        
        else:
            print(f"Error: Path {path} does not exist", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
