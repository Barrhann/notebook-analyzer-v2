"""Configuration settings for notebook analyzer."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class AnalyzerConfig:
    """Configuration class for notebook analyzer."""

    # General settings
    min_code_length: int = 1  # Minimum lines of code to analyze
    ignore_magic_commands: bool = True  # Whether to ignore Jupyter magic commands
    ignore_system_commands: bool = True  # Whether to ignore system commands (!)
    creation_date: datetime = field(default_factory=lambda: datetime(2025, 2, 16, 2, 34, 12))
    created_by: str = "Barrhann"

    # Analysis weights
    score_weights: Dict[str, float] = field(default_factory=lambda: {
        'builder_mindset': 0.5,
        'business_intelligence': 0.5
    })

    # Builder mindset metrics weights
    builder_weights: Dict[str, float] = field(default_factory=lambda: {
        'formatting': 0.15,
        'comments': 0.15,
        'conciseness': 0.15,
        'structure': 0.15,
        'dataset_join': 0.15,
        'reusability': 0.15,
        'advanced_techniques': 0.10
    })

    # Business intelligence metrics weights
    bi_weights: Dict[str, float] = field(default_factory=lambda: {
        'visualization_formatting': 0.5,
        'visualization_types': 0.5
    })

    # Threshold settings
    thresholds: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        'code_quality': {
            'excellent': 90.0,
            'good': 75.0,
            'fair': 60.0,
            'poor': 40.0
        },
        'complexity': {
            'high': 80.0,
            'medium': 50.0,
            'low': 20.0
        }
    })

    # File patterns to ignore
    ignore_patterns: List[str] = field(default_factory=lambda: [
        r'\.ipynb_checkpoints',
        r'__pycache__',
        r'\.git'
    ])

    # Output settings
    output_formats: List[str] = field(default_factory=lambda: [
        'html',
        'json',
        'markdown'
    ])

    def update(self, **kwargs) -> None:
        """
        Update configuration with new values.
        
        Args:
            **kwargs: Key-value pairs of configuration options to update
            
        Raises:
            ValueError: If an invalid configuration key is provided
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid configuration key: {key}")

    def validate(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate weight sums
        if abs(sum(self.score_weights.values()) - 1.0) > 1e-6:
            raise ValueError("Score weights must sum to 1.0")

        if abs(sum(self.builder_weights.values()) - 1.0) > 1e-6:
            raise ValueError("Builder mindset weights must sum to 1.0")

        if abs(sum(self.bi_weights.values()) - 1.0) > 1e-6:
            raise ValueError("Business intelligence weights must sum to 1.0")

        # Validate threshold values
        for category, levels in self.thresholds.items():
            prev_value = float('inf')
            for level, value in sorted(levels.items(), key=lambda x: x[1], reverse=True):
                if value > prev_value:
                    raise ValueError(
                        f"Invalid threshold values for {category}: {level} threshold"
                        f" ({value}) is greater than previous threshold ({prev_value})"
                    )
                prev_value = value

        # Validate output formats
        valid_formats = {'html', 'json', 'markdown'}
        invalid_formats = set(self.output_formats) - valid_formats
        if invalid_formats:
            raise ValueError(f"Invalid output formats: {invalid_formats}")

        return True

    def get_threshold_level(self, category: str, value: float) -> str:
        """
        Get the threshold level for a given value.
        
        Args:
            category: The threshold category ('code_quality' or 'complexity')
            value: The value to check
            
        Returns:
            str: The threshold level
            
        Raises:
            ValueError: If category is invalid
        """
        if category not in self.thresholds:
            raise ValueError(f"Invalid threshold category: {category}")

        levels = self.thresholds[category]
        for level, threshold in sorted(levels.items(), key=lambda x: x[1], reverse=True):
            if value >= threshold:
                return level

        return min(levels.keys(), key=lambda k: levels[k])

    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'AnalyzerConfig':
        """
        Create a configuration instance from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            AnalyzerConfig: New configuration instance
        """
        return cls(**{
            k: v for k, v in config_dict.items()
            if hasattr(cls, k)
        })

    def to_dict(self) -> Dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict: Configuration as dictionary
        """
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
