# Global import
import pandas as pd

# Built-in import
import logging


def transform_time_series(
    df: pd.DataFrame, metric_name: str, logger: logging.Logger
) -> pd.DataFrame:
    """Transform COVID-19 data from wide to long format.

    Converts the JHU time series data from wide format (dates as columns)
    to long format (single date column with corresponding values).

    Args:
        df: DataFrame in wide format (dates as columns)
        metric_name: Name of the metric (confirmed, deaths, recovered)
        logger: Logger instance for recording transformation steps

    Returns:
        pd.DataFrame: Transformed DataFrame with columns:
            - Province/State
            - Country/Region
            - Lat
            - Long
            - date (datetime)
            - metric_name (value for the given date)

    Raises:
        Exception: If transformation fails (e.g., invalid date format)

    Example:
        >>> df_wide = pd.DataFrame({
        ...     'Province/State': ['', 'California'],
        ...     'Country/Region': ['US', 'US'],
        ...     '1/22/20': [0, 1],
        ...     '1/23/20': [1, 2]
        ... })
        >>> df_long = transform_time_series(df_wide, 'confirmed', logger)
    """
    logger.info(f"Transforming {metric_name} data from wide to long format")

    # Melt the dataframe to convert from wide to long format
    id_vars = ['Province/State', 'Country/Region', 'Lat', 'Long']
    date_cols = [col for col in df.columns if col not in id_vars]

    try:
        melted_df = df.melt(
            id_vars=id_vars, value_vars=date_cols, var_name='date', value_name=metric_name
        )

        # Convert date strings to datetime with explicit format
        melted_df['date'] = pd.to_datetime(melted_df['date'], format='%m/%d/%y')

        logger.info(f"Successfully transformed {metric_name} data")
        return melted_df

    except Exception as e:
        logger.error(f"Error transforming {metric_name} data: {str(e)}")
        raise
