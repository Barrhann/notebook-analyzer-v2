"""
Notebook Reader Module.

This module provides functionality for reading and parsing Jupyter notebooks,
extracting cells and their content for analysis.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:05:37
"""

import json
import nbformat
from typing import Dict, List, Any, Optional, Generator
from pathlib import Path


class NotebookReader:
    """
    Class for reading and parsing Jupyter notebooks.

    This class handles:
    - Reading notebook files
    - Parsing notebook structure
    - Extracting code and markdown cells
    - Basic notebook validation
    """

    def __init__(self):
        """Initialize the notebook reader."""
        self.notebook = None
        self.filepath = None

    def read_notebook(self, filepath: str) -> bool:
        """
        Read a Jupyter notebook from file.

        Args:
            filepath (str): Path to the notebook file

        Returns:
            bool: True if notebook was read successfully, False otherwise

        Raises:
            FileNotFoundError: If notebook file doesn't exist
            ValueError: If file is not a valid notebook
        """
        try:
            self.filepath = Path(filepath)
            if not self.filepath.exists():
                raise FileNotFoundError(f"Notebook file not found: {filepath}")
                
            if self.filepath.suffix != '.ipynb':
                raise ValueError(f"File is not a Jupyter notebook: {filepath}")
                
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.notebook = nbformat.read(f, as_version=4)
                
            return True
            
        except (json.JSONDecodeError, nbformat.reader.NotJSONError):
            raise ValueError(f"Invalid notebook format: {filepath}")
        except Exception as e:
            raise ValueError(f"Error reading notebook: {str(e)}")

    def get_code_cells(self) -> Generator[Dict[str, Any], None, None]:
        """
        Get all code cells from the notebook.

        Yields:
            Dict[str, Any]: Dictionary containing cell information:
                - source: Cell source code
                - execution_count: Cell execution count
                - outputs: Cell outputs
                - metadata: Cell metadata
        """
        if not self.notebook:
            raise ValueError("No notebook loaded")
            
        for cell in self.notebook.cells:
            if cell.cell_type == 'code':
                yield {
                    'source': cell.source,
                    'execution_count': cell.execution_count,
                    'outputs': cell.outputs,
                    'metadata': cell.metadata
                }

    def get_markdown_cells(self) -> Generator[Dict[str, Any], None, None]:
        """
        Get all markdown cells from the notebook.

        Yields:
            Dict[str, Any]: Dictionary containing cell information:
                - source: Cell markdown content
                - metadata: Cell metadata
        """
        if not self.notebook:
            raise ValueError("No notebook loaded")
            
        for cell in self.notebook.cells:
            if cell.cell_type == 'markdown':
                yield {
                    'source': cell.source,
                    'metadata': cell.metadata
                }

    def get_notebook_metadata(self) -> Dict[str, Any]:
        """
        Get notebook metadata.

        Returns:
            Dict[str, Any]: Notebook metadata
        """
        if not self.notebook:
            raise ValueError("No notebook loaded")
            
        return {
            'filename': self.filepath.name,
            'kernelspec': self.notebook.metadata.get('kernelspec', {}),
            'language_info': self.notebook.metadata.get('language_info', {}),
            'total_cells': len(self.notebook.cells),
            'code_cells': sum(1 for cell in self.notebook.cells if cell.cell_type == 'code'),
            'markdown_cells': sum(1 for cell in self.notebook.cells if cell.cell_type == 'markdown')
        }

    def get_cell_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get cell by its index in the notebook.

        Args:
            index (int): Cell index

        Returns:
            Optional[Dict[str, Any]]: Cell information if index exists, None otherwise
        """
        if not self.notebook:
            raise ValueError("No notebook loaded")
            
        if 0 <= index < len(self.notebook.cells):
            cell = self.notebook.cells[index]
            return {
                'type': cell.cell_type,
                'source': cell.source,
                'metadata': cell.metadata,
                'outputs': cell.outputs if cell.cell_type == 'code' else None,
                'execution_count': cell.execution_count if cell.cell_type == 'code' else None
            }
        return None

    def validate_notebook(self) -> List[str]:
        """
        Validate notebook structure and content.

        Returns:
            List[str]: List of validation issues found
        """
        if not self.notebook:
            raise ValueError("No notebook loaded")
            
        issues = []
        
        # Check notebook version
        if self.notebook.nbformat < 4:
            issues.append("Notebook format version is less than 4.0")
            
        # Check for empty cells
        for idx, cell in enumerate(self.notebook.cells):
            if not cell.source.strip():
                issues.append(f"Empty cell found at index {idx}")
                
        # Check for valid metadata
        if not self.notebook.metadata.get('kernelspec'):
            issues.append("Missing kernel specification")
            
        return issues

    def get_notebook_summary(self) -> Dict[str, Any]:
        """
        Get a summary of notebook content and structure.

        Returns:
            Dict[str, Any]: Notebook summary information
        """
        if not self.notebook:
            raise ValueError("No notebook loaded")
            
        code_lines = sum(
            len(cell.source.splitlines())
            for cell in self.notebook.cells
            if cell.cell_type == 'code'
        )
        
        markdown_lines = sum(
            len(cell.source.splitlines())
            for cell in self.notebook.cells
            if cell.cell_type == 'markdown'
        )
        
        return {
            'filename': self.filepath.name,
            'total_cells': len(self.notebook.cells),
            'code_cells': sum(1 for cell in self.notebook.cells if cell.cell_type == 'code'),
            'markdown_cells': sum(1 for cell in self.notebook.cells if cell.cell_type == 'markdown'),
            'total_lines': code_lines + markdown_lines,
            'code_lines': code_lines,
            'markdown_lines': markdown_lines,
            'has_outputs': any(
                cell.outputs
                for cell in self.notebook.cells
                if cell.cell_type == 'code'
            )
        }

    def __str__(self) -> str:
        """Return string representation of the notebook reader."""
        if not self.notebook:
            return "NotebookReader(No notebook loaded)"
        return f"NotebookReader(file='{self.filepath.name}')"

    def __repr__(self) -> str:
        """Return detailed string representation of the notebook reader."""
        if not self.notebook:
            return "NotebookReader()"
        return (
            f"NotebookReader(file='{self.filepath.name}', "
            f"cells={len(self.notebook.cells)}, "
            f"format={self.notebook.nbformat}.{self.notebook.nbformat_minor})"
        )
