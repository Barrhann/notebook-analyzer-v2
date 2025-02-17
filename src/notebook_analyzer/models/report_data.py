"""
Report Data Model.

This module defines the data model for representing analysis report data,
including findings, suggestions, and visualizations.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:13:56
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


@dataclass
class ReportSection:
    """
    Represents a section of the analysis report.

    Attributes:
        title (str): Section title
        category (str): Analysis category (builder_mindset, business_intelligence)
        content (str): Main content text
        findings (List[str]): List of findings
        suggestions (List[str]): List of improvement suggestions
        metrics (Dict[str, Any]): Section-specific metrics
        charts (Dict[str, Any]): Visualization data
    """
    title: str
    category: str
    content: str
    findings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    charts: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate the report section after initialization."""
        if not self.title:
            raise ValueError("Title cannot be empty")
            
        if self.category not in ['builder_mindset', 'business_intelligence']:
            raise ValueError(
                "Category must be either 'builder_mindset' or 'business_intelligence'"
            )

    def add_finding(self, finding: str) -> None:
        """
        Add a new finding to the section.

        Args:
            finding (str): Finding to add
        """
        if finding not in self.findings:
            self.findings.append(finding)

    def add_suggestion(self, suggestion: str) -> None:
        """
        Add a new suggestion to the section.

        Args:
            suggestion (str): Suggestion to add
        """
        if suggestion not in self.suggestions:
            self.suggestions.append(suggestion)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the section to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the section
        """
        return {
            'title': self.title,
            'category': self.category,
            'content': self.content,
            'findings': self.findings,
            'suggestions': self.suggestions,
            'metrics': self.metrics,
            'charts': self.charts
        }


@dataclass
class ReportData:
    """
    Represents the complete analysis report data.

    Attributes:
        notebook_path (str): Path to the analyzed notebook
        sections (List[ReportSection]): Report sections
        metadata (Dict[str, Any]): Report metadata
        overall_score (float): Combined analysis score
        timestamp (datetime): When the report was generated
    """
    notebook_path: str
    sections: List[ReportSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    overall_score: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())

    def __post_init__(self):
        """Validate and initialize report data."""
        if not 0 <= self.overall_score <= 100:
            raise ValueError("Overall score must be between 0 and 100")
            
        if not self.notebook_path:
            raise ValueError("Notebook path cannot be empty")
            
        self.metadata.update({
            'generated_at': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'notebook_name': Path(self.notebook_path).name
        })

    def add_section(self, section: ReportSection) -> None:
        """
        Add a new section to the report.

        Args:
            section (ReportSection): Section to add
        """
        self.sections.append(section)

    def get_section(self, title: str) -> Optional[ReportSection]:
        """
        Get a section by title.

        Args:
            title (str): Section title

        Returns:
            Optional[ReportSection]: The section if found, None otherwise
        """
        for section in self.sections:
            if section.title == title:
                return section
        return None

    def get_category_sections(self, category: str) -> List[ReportSection]:
        """
        Get all sections for a specific category.

        Args:
            category (str): Category to filter by

        Returns:
            List[ReportSection]: List of sections in the category
        """
        return [
            section for section in self.sections
            if section.category == category
        ]

    def get_all_findings(self) -> Dict[str, List[str]]:
        """
        Get all findings grouped by category.

        Returns:
            Dict[str, List[str]]: Findings by category
        """
        findings = {}
        for section in self.sections:
            if section.category not in findings:
                findings[section.category] = []
            findings[section.category].extend(section.findings)
        return findings

    def get_all_suggestions(self) -> Dict[str, List[str]]:
        """
        Get all suggestions grouped by category.

        Returns:
            Dict[str, List[str]]: Suggestions by category
        """
        suggestions = {}
        for section in self.sections:
            if section.category not in suggestions:
                suggestions[section.category] = []
            suggestions[section.category].extend(section.suggestions)
        return suggestions

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the report data.

        Returns:
            Dict[str, Any]: Report summary
        """
        return {
            'notebook': Path(self.notebook_path).name,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_score': self.overall_score,
            'sections': len(self.sections),
            'categories': list({
                section.category for section in self.sections
            }),
            'total_findings': sum(
                len(section.findings) for section in self.sections
            ),
            'total_suggestions': sum(
                len(section.suggestions) for section in self.sections
            )
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the report data to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the report data
        """
        return {
            'notebook_path': self.notebook_path,
            'metadata': self.metadata,
            'overall_score': self.overall_score,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sections': [section.to_dict() for section in self.sections],
            'summary': self.get_summary()
        }

    def __str__(self) -> str:
        """Return string representation of the report data."""
        return (f"ReportData(notebook='{Path(self.notebook_path).name}', "
                f"sections={len(self.sections)}, "
                f"score={self.overall_score})")

    def __repr__(self) -> str:
        """Return detailed string representation of the report data."""
        categories = {section.category for section in self.sections}
        return (f"ReportData("
                f"notebook='{Path(self.notebook_path).name}', "
                f"sections={len(self.sections)}, "
                f"categories={list(categories)}, "
                f"score={self.overall_score})")
