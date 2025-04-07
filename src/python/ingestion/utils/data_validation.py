# Global import
import pandas as pd

# Built-in import
import logging


def validate_data(df: pd.DataFrame, data_type: str, logger: logging.Logger) -> None:
    """Validate the structure and content of COVID-19 data.

    Performs two main validations:
    1. Checks for required columns (Province/State, Country/Region, etc.)
    2. Ensures all date columns contain numeric values

    Args:
        df: DataFrame containing COVID-19 data
        data_type: Type of data being validated (confirmed, deaths, recovered)
        logger: Logger instance for recording validation results

    Raises:
        ValueError: If required columns are missing or data types are incorrect

    Example:
        >>> validate_data(df, 'confirmed', logger)
    """
    logger.info(f"Validating {data_type} data")

    # Define the columns that must be present in the data
    # These are the geographic identifiers used in JHU COVID data
    required_cols = ['Province/State', 'Country/Region', 'Lat', 'Long']

    # Check if any required columns are missing from the DataFrame
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        error_msg = f"Missing required columns in {data_type} data: {missing_cols}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Identify all date columns (any column not in required_cols is assumed to be a date)
    # Date columns should contain the daily counts for each location
    date_cols = [col for col in df.columns if col not in required_cols]

    # Check for non-numeric values in date columns
    # All date columns should contain only numbers (case counts)
    non_numeric = df[date_cols].select_dtypes(exclude=['number']).columns
    if len(non_numeric) > 0:
        error_msg = f"Non-numeric values found in date columns: {non_numeric}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info(f"Validation successful for {data_type} data")


def clean_data(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """Clean and standardize COVID-19 data.

    Cleaning operations:
    1. Replace missing values with 0
    2. Remove negative values (replace with 0)
    3. Standardize country/region names

    Args:
        df: DataFrame to clean
        logger: Logger instance for recording cleaning operations

    Returns:
        pd.DataFrame: Cleaned DataFrame

    Example:
        >>> cleaned_df = clean_data(df, logger)
    """
    logger.info("Starting data cleaning process")

    # Handle missing values
    # Replace NaN/None with 0 as we assume no data means no cases
    df = df.fillna(0)
    logger.info("Replaced missing values with 0")

    # Handle negative values
    # Negative case counts don't make sense, so we replace them with 0
    for col in df.select_dtypes(include=['number']).columns:
        negative_count = (df[col] < 0).sum()
        if negative_count > 0:
            logger.warning(
                f"Found {negative_count} negative values in {col}, replacing with 0"
            )
            df.loc[df[col] < 0, col] = 0

    # Standardize country/region names
    # Remove leading/trailing whitespace to prevent duplicates
    # e.g., "USA " and "USA" would be treated as different countries
    df['Country/Region'] = df['Country/Region'].str.strip()
    logger.info("Standardized country/region names")

    logger.info("Data cleaning completed successfully")
    return df
