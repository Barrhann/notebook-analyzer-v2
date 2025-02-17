"""
Setup configuration for the notebook-analyzer package.

This module contains the package configuration for installation and distribution.
It defines dependencies, entry points, and package metadata.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 02:26:49
"""

from setuptools import setup, find_packages

setup(
    name="notebook-analyzer",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Required dependencies
    install_requires=[
        "nbformat>=5.7.0",        # For Jupyter notebook parsing
        "pycodestyle>=2.10.0",    # For code style checking
        "jinja2>=3.0.0",         # For template rendering
    ],
    
    # CLI entry point
    entry_points={
        'console_scripts': [
            'notebook-analyzer=notebook_analyzer.cli:main',  
        ],
    },
    
    # Package metadata
    author="Barrhann",
    author_email="barrhann@github.com",
    description="A tool for analyzing Jupyter notebooks",
    url="https://github.com/Barrhann/notebook-analyzer-v2",
    
    # Python version support
    python_requires=">=3.8",
    
    # Classifiers
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
