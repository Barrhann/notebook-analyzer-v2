from setuptools import setup, find_packages

setup(
    name="notebook-analyzer",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "nbformat>=5.7.0",
        "pycodestyle>=2.10.0",
    ],
    entry_points={
        'console_scripts': [
            'notebook-analyzer=notebook_analyzer.cli.main:main',
        ],
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for analyzing Jupyter notebooks for code quality and documentation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
