"""COVID-19 Data Ingestion Package.

This package provides tools for downloading, processing, and storing COVID-19 data
from the Johns Hopkins University (JHU) repository.

Main Components:
    CovidDataIngestion: Main class for handling the ingestion pipeline
    IngestionConfig: Configuration class for customizing the ingestion process

Usage Examples:
    # 1. Basic usage with default configuration
    from src.python.ingestion import CovidDataIngestion
    
    ingestion = CovidDataIngestion()
    ingestion.download_data()
    ingestion.load_to_duckdb()

    # 2. Custom configuration
    from src.python.ingestion import CovidDataIngestion, IngestionConfig
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

Package Structure:
    core/
        covid_ingestion.py - Main ingestion implementation
    config/
        ingestion_config.py - Configuration classes
    utils/
        data_validation.py - Data validation utilities
        data_transformation.py - Data transformation utilities
        logging_setup.py - Logging configuration

For command-line usage:
    $ python -m src.python.ingestion
"""

# Local imports
from .core.covid_ingestion import CovidDataIngestion
from .config.ingestion_config import IngestionConfig

__all__ = ['CovidDataIngestion', 'IngestionConfig']
