"""
Notebook Reader module
Created by: Barrhann
"""

import json
import nbformat
from typing import Dict, Any

class NotebookReader:
    def read(self, notebook_path: str) -> Dict[str, Any]:
        """
        Read and parse a Jupyter notebook file.

        Args:
            notebook_path (str): Path to the Jupyter notebook file

        Returns:
            Dict[str, Any]: Parsed notebook content with separated code and markdown cells
        """
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)

        return {
            'code_cells': [cell for cell in notebook.cells if cell.cell_type == 'code'],
            'markdown_cells': [cell for cell in notebook.cells if cell.cell_type == 'markdown'],
            'metadata': notebook.metadata
        }
