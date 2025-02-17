# Notebook Analyzer

A Python tool for analyzing Jupyter notebooks, focusing on code quality assessment through builder mindset patterns and business intelligence aspects.

## Features

### Builder Mindset Analysis
- **Code Formatting**: Style consistency and PEP 8 compliance
- **Code Structure**: Organization and modular design
- **Code Comments**: Documentation quality assessment
- **Code Conciseness**: Efficiency and clarity metrics
- **Code Reusability**: Function and module reuse patterns
- **Advanced Techniques**: Python feature utilization
- **Dataset Join Analysis**: Data manipulation patterns

### Business Intelligence Analysis
- **Visualization Types**: Chart selection and variety
- **Visualization Formatting**: Plot readability and style

## Installation

```bash
# Install from source
git clone https://github.com/Barrhann/notebook-analyzer-v2.git
cd notebook-analyzer-v2
pip install -e .
```

## Requirements

- Python >= 3.8
- nbformat >= 5.7.0
- pycodestyle >= 2.10.0
- jinja2 >= 3.0.0

## Usage

### Command Line Interface

```bash
# Basic analysis
notebook-analyzer analyze path/to/notebook.ipynb

# Generate HTML report
notebook-analyzer analyze path/to/notebook.ipynb --format html

# Generate Markdown report
notebook-analyzer analyze path/to/notebook.ipynb --format markdown
```

### Python API

```python
from notebook_analyzer import create_analyzer, create_report_generator

# Create analyzer instance
analyzer = create_analyzer()

# Analyze notebook
results = analyzer.analyze("path/to/notebook.ipynb")

# Generate report
report_gen = create_report_generator(output_dir="reports")
report_path = report_gen.generate_report(results, format_type="html")
```

## Project Structure

```
notebook-analyzer-v2/
└── src/
    └── notebook_analyzer/
        ├── analyzer/           # Core analysis functionality
        ├── reporting/         # Report generation
        │   ├── templates/     # HTML and Markdown templates
        │   └── formatters/    # Metric formatters
        │       ├── builder_mindset/
        │       └── business_intelligence/
        └── cli/              # Command-line interface
```

## Available Metrics

### Builder Mindset Metrics
- Code Formatting Analysis
- Code Structure Analysis
- Code Comments Analysis
- Code Conciseness Analysis
- Code Reusability Analysis
- Advanced Techniques Analysis
- Dataset Join Analysis

### Business Intelligence Metrics
- Visualization Types Analysis
- Visualization Formatting Analysis

## Report Types

### HTML Reports
- Interactive visualizations
- Collapsible sections
- Score summaries
- Detailed metrics

### Markdown Reports
- GitHub-compatible format
- Plain text results
- Easy to version control

## Package Information

- Version: 1.0.0
- Author: Barrhann
- Email: barrhann@github.com
- Last Updated: 2025-02-17 02:13:15

## License

This project is licensed under the MIT License.

---

**Note**: This project is actively maintained. For bug reports or feature requests, please open an issue on GitHub.
