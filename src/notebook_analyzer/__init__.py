"""
Notebook Analyzer - A tool for analyzing Jupyter notebooks
Created by: Barrhann
"""

from .core.notebook_reader import NotebookReader
from .analyzers.code_format import CodeFormatAnalyzer
from .analyzers.documentation import DocumentationAnalyzer
from .reporting.report_generator import ReportGenerator

class NotebookAnalyzer:
    def __init__(self):
        self.notebook_reader = NotebookReader()
        self.code_analyzer = CodeFormatAnalyzer()
        self.doc_analyzer = DocumentationAnalyzer()
        self.report_generator = ReportGenerator()

    def analyze(self, notebook_path: str) -> dict:
        """
        Analyze a Jupyter notebook and generate a comprehensive report.

        Args:
            notebook_path (str): Path to the Jupyter notebook file

        Returns:
            dict: A structured report containing analysis results
        """
        # Read the notebook
        notebook_content = self.notebook_reader.read(notebook_path)
        
        # Analyze code formatting
        code_analysis = self.code_analyzer.analyze(notebook_content)
        
        # Analyze documentation
        doc_analysis = self.doc_analyzer.analyze(notebook_content)
        
        # Generate and return the report
        return self.report_generator.generate(code_analysis, doc_analysis)
