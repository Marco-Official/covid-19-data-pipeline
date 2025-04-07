"""COVID-19 Data Ingestion Configuration Module.

This module provides configuration management for the COVID-19 data ingestion pipeline,
allowing customization of data sources, file paths, and retention policies.

Main Components:
    IngestionConfig: Core configuration class with settings for:
        - JHU data repository URL
        - Data type mappings
        - File paths for raw and processed data
        - Data retention policies

Usage Examples:
    # 1. Default configuration
    from ingestion.config import IngestionConfig
    
    config = IngestionConfig.default_config()
    print(config.raw_data_path)  # Path('data/raw')
    print(config.retention_days)  # 7

    # 2. Custom configuration
    from pathlib import Path
    
    custom_config = IngestionConfig(
        base_url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/...",
        data_types={'confirmed': 'time_series_covid19_confirmed_global.csv'},
        raw_data_path=Path('custom/raw/path'),
        db_path='custom/db/covid.duckdb',
        retention_days=14
    )

Module Structure:
    ingestion_config.py - Core configuration class implementation
        - IngestionConfig: Main configuration dataclass
        - default_config: Factory method for default settings
"""

# Local import
from .ingestion_config import IngestionConfig

__all__ = ['IngestionConfig']
