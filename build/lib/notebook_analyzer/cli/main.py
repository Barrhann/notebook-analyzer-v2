"""Command-line interface for notebook analyzer."""
import sys
import argparse
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from ..analyzer import NotebookAnalyzer
from ..config import AnalyzerConfig

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze Jupyter notebooks for best practices and patterns."
    )
    parser.add_argument(
        'notebook_path',
        type=str,
        help="Path to the Jupyter notebook file or directory containing notebooks"
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help="Output directory for analysis results",
        default=None
    )
    parser.add_argument(
        '-f', '--format',
        type=str,
        choices=['html', 'json', 'markdown'],
        default='html',
        help="Output format for the report (default: html)"
    )
    parser.add_argument(
        '--config',
        type=str,
        help="Path to configuration file",
        default=None
    )
    return parser.parse_args()

def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()
    
    try:
        config = AnalyzerConfig()
        if args.config:
            with open(args.config, 'r') as f:
                config_dict = json.load(f)
                config = AnalyzerConfig.from_dict(config_dict)
        
        notebook_path = Path(args.notebook_path)
        if not notebook_path.exists():
            print(f"Error: File or directory not found: {args.notebook_path}", file=sys.stderr)
            sys.exit(1)
        
        analyzer = NotebookAnalyzer(config)
        
        if notebook_path.is_file():
            results = analyzer.analyze_notebook(str(notebook_path))
            _save_results(results, notebook_path, args.output, args.format)
        else:
            for file in notebook_path.glob('**/*.ipynb'):
                if '.ipynb_checkpoints' not in str(file):
                    try:
                        results = analyzer.analyze_notebook(str(file))
                        _save_results(results, file, args.output, args.format)
                    except Exception as e:
                        print(f"Error analyzing notebook {file}:", file=sys.stderr)
                        print(str(e), file=sys.stderr)
                        continue
                        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def _save_results(results: dict, notebook_path: Path, output_dir: Optional[str], format_type: str) -> None:
    """Save analysis results to file."""
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        output_file = output_path / f"{notebook_path.stem}_analysis.{format_type}"
        with open(output_file, 'w') as f:
            if format_type == 'json':
                json.dump(results, f, indent=2)
            else:
                f.write(results)
                
        print(f"Analysis saved to: {output_file}")
    else:
        if format_type == 'json':
            print(json.dumps(results, indent=2))
        else:
            print(results)

if __name__ == '__main__':
    main()
