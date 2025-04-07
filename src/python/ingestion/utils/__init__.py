"""COVID-19 Data Ingestion Utilities Module.

This module provides utility functions for the COVID-19 data ingestion pipeline,
including logging setup, data validation, cleaning, and transformation operations.

Main Components:
    setup_logging: Configures logging with appropriate handlers and formatters
    validate_data: Performs validation checks on input data
    clean_data: Cleanses and standardizes data
    transform_time_series: Converts time series data from wide to long format

Usage Examples:
    # 1. Setting up logging
    from ingestion.utils import setup_logging
    
    logger = setup_logging(__name__)
    logger.info("Starting data processing")

    # 2. Data validation and cleaning
    from ingestion.utils import validate_data, clean_data
    
    validate_data(df, data_type='confirmed', logger=logger)
    cleaned_df = clean_data(df, logger)

    # 3. Time series transformation
    from ingestion.utils import transform_time_series
    
    transformed_df = transform_time_series(
        df,
        metric_name='cases',
        logger=logger
    )

Module Structure:
    logging_setup.py - Logging configuration utilities
    data_validation.py - Data validation and cleaning functions
    data_transformation.py - Data reshaping and transformation utilities
"""

# Local imports
from .data_transformation import transform_time_series
from .data_validation import validate_data, clean_data
from .logging_setup import setup_logging

__all__ = ['setup_logging', 'validate_data', 'clean_data', 'transform_time_series']
