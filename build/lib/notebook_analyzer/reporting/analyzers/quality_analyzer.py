"""
Quality Analyzer - Handles quality score calculations
"""

from typing import Dict, Any, Tuple
from ..constants import QUALITY_BENCHMARKS

class QualityAnalyzer:
    def calculate_score(self, code_analysis: Dict[str, Any],
                       doc_analysis: Dict[str, Any]) -> Tuple[float, list]:
        """Calculate quality score and deductions."""
        score = 100
        deductions = []
        
        # PEP8 violations deduction
        pep8_deduction = self._calculate_pep8_deduction(code_analysis)
        if pep8_deduction:
            score -= pep8_deduction['points']
            deductions.append(pep8_deduction)
        
        # Documentation deduction
        doc_deduction = self._calculate_doc_deduction(doc_analysis)
        if doc_deduction:
            score -= doc_deduction['points']
            deductions.append(doc_deduction)
            
        return max(0, round(score, 1)), deductions

    def _calculate_pep8_deduction(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate deduction for PEP8 violations."""
        violations = len(analysis.get('pep8_violations', []))
        if violations == 0:
            return None
            
        points = min(
            violations * QUALITY_BENCHMARKS['pep8_per_violation'],
            QUALITY_BENCHMARKS['pep8_max_deduction']
        )
        
        return {
            'category': 'Code Style Issues',
            'points': points,
            'reason': f'Found {violations} style issues in the code'
        }

    def _calculate_doc_deduction(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate deduction for documentation coverage."""
        coverage = analysis.get('coverage', 0)
        if coverage >= QUALITY_BENCHMARKS['doc_min_coverage']:
            return None
            
        points = QUALITY_BENCHMARKS['doc_max_deduction'] * (
            1 - coverage/QUALITY_BENCHMARKS['doc_min_coverage']
        )
        
        return {
            'category': 'Documentation Coverage',
            'points': points,
            'reason': f'Documentation covers only {coverage:.1%} of the code'
        }
