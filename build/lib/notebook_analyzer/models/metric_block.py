"""
Metric Block Model.

This module defines the data model for representing metric blocks,
which are collections of related metrics from notebook analyzers.

Created by: Barrhann
Created on: 2025-02-17
Last Updated: 2025-02-17 01:12:39
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class MetricBlock:
    """
    Represents a collection of related metrics from an analyzer.

    Attributes:
        name (str): Name of the metric block
        category (str): Category of metrics (builder_mindset, business_intelligence)
        metrics (Dict[str, Any]): Collection of metrics and their values
        score (float): Score for this metric block (0-100)
        weight (float): Weight of this block in overall analysis (0-1)
        timestamp (datetime): When the metrics were collected
    """
    name: str
    category: str
    metrics: Dict[str, Any]
    score: float
    weight: float = 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())

    def __post_init__(self):
        """Validate the metric block after initialization."""
        if not 0 <= self.score <= 100:
            raise ValueError("Score must be between 0 and 100")
            
        if not 0 <= self.weight <= 1:
            raise ValueError("Weight must be between 0 and 1")
            
        if self.category not in ['builder_mindset', 'business_intelligence']:
            raise ValueError(
                "Category must be either 'builder_mindset' or 'business_intelligence'"
            )
            
        if not self.name:
            raise ValueError("Name cannot be empty")

    def add_metric(self, name: str, value: Any) -> None:
        """
        Add a new metric to the block.

        Args:
            name (str): Name of the metric
            value (Any): Value of the metric
        """
        self.metrics[name] = value

    def get_metric(self, name: str) -> Optional[Any]:
        """
        Get a metric value by name.

        Args:
            name (str): Name of the metric

        Returns:
            Optional[Any]: Value of the metric if it exists, None otherwise
        """
        return self.metrics.get(name)

    def update_score(self, new_score: float) -> None:
        """
        Update the block's score.

        Args:
            new_score (float): New score value

        Raises:
            ValueError: If score is not between 0 and 100
        """
        if not 0 <= new_score <= 100:
            raise ValueError("Score must be between 0 and 100")
        self.score = new_score

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the metric block.

        Returns:
            Dict[str, Any]: Summary of the metric block
        """
        return {
            'name': self.name,
            'category': self.category,
            'score': self.score,
            'weight': self.weight,
            'metric_count': len(self.metrics),
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the metric block to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the block
        """
        return {
            'name': self.name,
            'category': self.category,
            'metrics': self.metrics,
            'score': self.score,
            'weight': self.weight,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


@dataclass
class MetricBlockCollection:
    """
    Represents a collection of metric blocks for a notebook analysis.

    Attributes:
        blocks (List[MetricBlock]): List of metric blocks
        timestamp (datetime): When the collection was created
    """
    blocks: List[MetricBlock] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())

    def add_block(self, block: MetricBlock) -> None:
        """
        Add a new metric block to the collection.

        Args:
            block (MetricBlock): Block to add
        """
        self.blocks.append(block)

    def get_block(self, name: str) -> Optional[MetricBlock]:
        """
        Get a metric block by name.

        Args:
            name (str): Name of the block to get

        Returns:
            Optional[MetricBlock]: The metric block if found, None otherwise
        """
        for block in self.blocks:
            if block.name == name:
                return block
        return None

    def get_category_blocks(self, category: str) -> List[MetricBlock]:
        """
        Get all blocks for a specific category.

        Args:
            category (str): Category to filter by

        Returns:
            List[MetricBlock]: List of blocks in the category
        """
        return [
            block for block in self.blocks
            if block.category == category
        ]

    def calculate_overall_score(self) -> float:
        """
        Calculate overall weighted score from all blocks.

        Returns:
            float: Overall weighted score (0-100)
        """
        if not self.blocks:
            return 0.0
            
        total_score = 0.0
        total_weight = 0.0
        
        for block in self.blocks:
            total_score += block.score * block.weight
            total_weight += block.weight
            
        return round(total_score / total_weight, 2) if total_weight > 0 else 0.0

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all metric blocks.

        Returns:
            Dict[str, Any]: Summary of the collection
        """
        category_scores = {}
        for block in self.blocks:
            if block.category not in category_scores:
                category_scores[block.category] = []
            category_scores[block.category].append(block.score)
            
        return {
            'total_blocks': len(self.blocks),
            'categories': list(category_scores.keys()),
            'overall_score': self.calculate_overall_score(),
            'category_averages': {
                category: round(sum(scores) / len(scores), 2)
                for category, scores in category_scores.items()
            },
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the collection to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the collection
        """
        return {
            'blocks': [block.to_dict() for block in self.blocks],
            'overall_score': self.calculate_overall_score(),
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': self.get_summary()
        }

    def __str__(self) -> str:
        """Return string representation of the collection."""
        return (f"MetricBlockCollection(blocks={len(self.blocks)}, "
                f"score={self.calculate_overall_score()})")

    def __repr__(self) -> str:
        """Return detailed string representation of the collection."""
        categories = {block.category for block in self.blocks}
        return (f"MetricBlockCollection("
                f"blocks={len(self.blocks)}, "
                f"categories={list(categories)}, "
                f"score={self.calculate_overall_score()})")
