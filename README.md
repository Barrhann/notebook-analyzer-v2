# Jupyter Notebook Analyzer

A tool for analyzing Jupyter notebooks to assess code quality and documentation standards. The analyzer provides detailed business insights about code formatting and documentation quality.

## Features

- PEP8 code formatting analysis
- Documentation quality assessment (markdown cells and code comments)
- Detailed business-friendly reports
- Identification of both positive and negative aspects
- Command-line interface for easy integration

## Installation

```bash
# Install from the current directory
pip install .
```

## Usage

### Command Line Interface

```bash
# Analyze a single notebook
notebook-analyzer path/to/notebook.ipynb

# Analyze a notebook and save the report to a file
notebook-analyzer path/to/notebook.ipynb -o report.json

# Analyze all notebooks in a directory
notebook-analyzer path/to/notebooks/

# Choose output format (json or text)
notebook-analyzer path/to/notebook.ipynb --format json

# Get help
notebook-analyzer --help
```

### Python API

```python
from notebook_analyzer import NotebookAnalyzer

analyzer = NotebookAnalyzer()
report = analyzer.analyze("path/to/your/notebook.ipynb")
print(report)
```

## Output Format

The analyzer generates a structured report containing:

1. Overall Quality Score
2. Code Formatting Analysis
   - PEP8 compliance
   - Code style consistency
3. Documentation Analysis
   - Markdown cell quality
   - Code comments coverage and quality
4. Detailed Findings
   - Positive aspects
   - Areas for improvement

## Requirements

- Python 3.8+
- Jupyter Notebook
