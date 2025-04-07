"""COVID-19 Data Ingestion Core Module.

This module provides the core functionality for downloading, processing, and storing
COVID-19 data from the Johns Hopkins University (JHU) repository into DuckDB.

Main Components:
    CovidDataIngestion: Core ingestion class that handles:
        - Data downloading from JHU repository
        - File management and retention
        - Data validation and cleaning
        - DuckDB loading and table creation

Usage Examples:
    # 1. Basic usage with default configuration
    from ingestion.core import CovidDataIngestion
    
    ingestion = CovidDataIngestion()
    ingestion.download_data()
    ingestion.cleanup_old_files()
    ingestion.load_to_duckdb()

    # 2. Usage with custom configuration
    from ingestion.config import IngestionConfig
    from pathlib import Path
    
    config = IngestionConfig(
        base_url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/...",
        data_types={'confirmed': 'time_series_covid19_confirmed_global.csv'},
        raw_data_path=Path('custom/raw/path'),
        db_path='custom/db/covid.duckdb',
        retention_days=14
    )
    
    ingestion = CovidDataIngestion(config)
    ingestion.download_data()

Module Structure:
    covid_ingestion.py - Main ingestion class implementation
        - CovidDataIngestion: Core class for data pipeline
        - download_data: Method for fetching latest data
        - cleanup_old_files: Method for managing file retention
        - load_to_duckdb: Method for database loading
"""

# Local import
from .covid_ingestion import CovidDataIngestion

__all__ = ['CovidDataIngestion']
