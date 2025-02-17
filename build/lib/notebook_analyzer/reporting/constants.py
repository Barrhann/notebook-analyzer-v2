"""
Constants used in reporting
"""

QUALITY_BENCHMARKS = {
    'pep8_per_violation': 0.5,
    'pep8_max_deduction': 30,
    'doc_min_coverage': 0.7,
    'doc_max_deduction': 30,
    'code_complexity_threshold': 0.2,
    'code_complexity_deduction': 20,
    'comment_coverage_threshold': 0.2,
    'comment_coverage_deduction': 20
}

STYLE_DESCRIPTIONS = {
    'E1': 'Indentation issues',
    'E2': 'Whitespace issues',
    'E3': 'Blank line issues',
    'E4': 'Import formatting issues',
    'E5': 'Line too long',
    'E7': 'Statement formatting issues',
    'W1': 'Indentation warnings',
    'W2': 'Whitespace warnings',
    'W3': 'Blank line warnings',
    'W4': 'Source code warnings',
    'W5': 'Line break warnings',
    'W6': 'Deprecation warnings'
}
