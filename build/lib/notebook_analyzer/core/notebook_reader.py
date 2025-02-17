"""Module for reading and preprocessing Jupyter notebooks."""
import nbformat
from typing import Dict, Any, List
import re

class NotebookReader:
    """Class for reading and preprocessing Jupyter notebooks."""

    def __init__(self):
        self.current_notebook = None

    def read(self, path: str) -> Dict[str, Any]:
        """
        Read a Jupyter notebook from a file.
        
        Args:
            path: Path to the notebook file
            
        Returns:
            Dict containing the notebook content
            
        Raises:
            FileNotFoundError: If notebook file doesn't exist
            nbformat.reader.NotJSONError: If notebook is invalid JSON
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.current_notebook = nbformat.read(f, as_version=4)
            return self.current_notebook
        except FileNotFoundError:
            raise FileNotFoundError(f"Notebook file not found: {path}")
        except nbformat.reader.NotJSONError:
            raise ValueError(f"Invalid notebook format: {path}")

    def get_code_cells(self, notebook: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract code cells from notebook.
        
        Args:
            notebook: Notebook content dictionary
            
        Returns:
            List of code cells with metadata
        """
        code_cells = []
        cell_number = 0
        
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                cell_number += 1
                code_cells.append({
                    'source': cell.get('source', ''),
                    'cell_number': cell_number,
                    'execution_count': cell.get('execution_count'),
                    'metadata': cell.get('metadata', {})
                })
        
        return code_cells

    def preprocess_code(self, code: str) -> str:
        """
        Preprocess code cell content.
        
        Args:
            code: Code cell content
            
        Returns:
            Preprocessed code string
        """
        # Remove IPython magic commands
        code = re.sub(r'^%.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'^%%.*$', '', code, flags=re.MULTILINE)
        
        # Remove system commands
        code = re.sub(r'^!.*$', '', code, flags=re.MULTILINE)
        
        # Remove empty lines at start and end
        code = code.strip()
        
        return code
