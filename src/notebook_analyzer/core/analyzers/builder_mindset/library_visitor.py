"""AST visitor for analyzing library imports and usage."""
import ast
from typing import List, Set, Dict
from datetime import datetime

class LibraryVisitor(ast.NodeVisitor):
    """AST visitor for analyzing library imports and their usage."""

    def __init__(self, creation_date: datetime = datetime(2025, 2, 16, 2, 41, 45),
                 created_by: str = "Barrhann"):
        super().__init__()
        # Metadata
        self.creation_date = creation_date
        self.created_by = created_by
        
        # Initialize collections
        self.imports: Set[str] = set()
        self.import_froms: Set[str] = set()
        self.used_names: Set[str] = set()
        
        # Define library categories
        self.advanced_libs: Set[str] = {
            'numpy',
            'pandas',
            'sklearn',
            'tensorflow',
            'torch',
            'keras',
            'scipy',
            'statsmodels',
            'xgboost',
            'lightgbm',
            'catboost',
            'plotly',
            'seaborn',
            'matplotlib',
            'numba',
            'pyspark',
            'dask',
            'h5py',
            'networkx',
            'gensim',
            'nltk',
            'spacy'
        }
        
        self.basic_libs: Set[str] = {
            'math',
            'random',
            'datetime',
            'collections',
            'itertools',
            'os',
            'sys',
            'json',
            'csv',
            'time',
            're'
        }
        
        self.library_calls: Dict[str, List[ast.Call]] = {}

    def visit_Import(self, node: ast.Import) -> None:
        """Visit Import nodes."""
        for alias in node.names:
            name = alias.name.split('.')[0]
            self.imports.add(name)
            if name not in self.library_calls:
                self.library_calls[name] = []
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit ImportFrom nodes."""
        if node.module:
            name = node.module.split('.')[0]
            self.import_froms.add(name)
            if name not in self.library_calls:
                self.library_calls[name] = []
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Visit Name nodes."""
        self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Visit Call nodes."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                lib_name = node.func.value.id
                if lib_name in self.library_calls:
                    self.library_calls[lib_name].append(node)
        self.generic_visit(node)

    def get_advanced_imports(self) -> Set[str]:
        """Get set of advanced library imports."""
        all_imports = self.imports.union(self.import_froms)
        return {lib for lib in all_imports if lib in self.advanced_libs}

    def get_basic_imports(self) -> Set[str]:
        """Get set of basic library imports."""
        all_imports = self.imports.union(self.import_froms)
        return {lib for lib in all_imports if lib in self.basic_libs}

    def get_library_usage(self) -> Dict[str, int]:
        """Get dictionary of library usage counts."""
        return {lib: len(calls) for lib, calls in self.library_calls.items()}

    def get_library_complexity(self) -> float:
        """Calculate library usage complexity score."""
        advanced_count = len(self.get_advanced_imports())
        basic_count = len(self.get_basic_imports())
        total_count = len(self.imports.union(self.import_froms))
        
        if total_count == 0:
            return 0.0
            
        # Weight advanced libraries more heavily
        complexity_score = (advanced_count * 2 + basic_count) / (total_count * 2)
        return min(1.0, complexity_score) * 100  # Convert to percentage

    def analyze(self, code: str) -> Dict[str, any]:
        """
        Analyze code for library usage patterns.
        
        Args:
            code: Python code string to analyze
            
        Returns:
            Dict containing analysis results
        """
        try:
            tree = ast.parse(code)
            self.visit(tree)
            
            return {
                'metadata': {
                    'creation_date': self.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'created_by': self.created_by
                },
                'metrics': {
                    'advanced_libraries': {
                        'count': len(self.get_advanced_imports()),
                        'list': list(self.get_advanced_imports()),
                        'score': self.get_library_complexity()
                    },
                    'basic_libraries': {
                        'count': len(self.get_basic_imports()),
                        'list': list(self.get_basic_imports())
                    },
                    'library_usage': self.get_library_usage()
                }
            }
        except SyntaxError:
            return {
                'metadata': {
                    'creation_date': self.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'created_by': self.created_by
                },
                'metrics': {
                    'advanced_libraries': {
                        'count': 0,
                        'list': [],
                        'score': 0.0
                    },
                    'basic_libraries': {
                        'count': 0,
                        'list': []
                    },
                    'library_usage': {}
                }
            }
