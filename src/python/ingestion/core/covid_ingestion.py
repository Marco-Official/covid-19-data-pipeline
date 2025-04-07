# Global imports
import pandas as pd
import requests
import duckdb

# Built-in imports
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

# Local imports
from ..config.ingestion_config import IngestionConfig
from ..utils.data_validation import validate_data, clean_data
from ..utils.data_transformation import transform_time_series
from ..utils.logging_setup import setup_logging


class CovidDataIngestion:
    """Main class for handling COVID-19 data ingestion process.

    This class orchestrates the entire data ingestion pipeline including:
    - Downloading raw data from JHU repository
    - Data validation and cleaning
    - Data transformation
    - Loading data into DuckDB
    - Managing file retention

    Attributes:
        logger (logging.Logger): Logging instance, automatically configured during initialization
        config (IngestionConfig): Configuration settings for the ingestion process. If not provided
            in __init__, a default configuration is created

    Example:
        >>> ingestion = CovidDataIngestion()  # Uses default config
        >>> ingestion.download_data()
        >>> ingestion.load_to_duckdb()
    """

    def __init__(self, config: Optional[IngestionConfig] = None):
        """Initialize the COVID data ingestion pipeline.

        Args:
            config: Optional configuration object. If None, uses default config
                   with predefined paths and settings.
        """
        # Set up logging for this instance
        self.logger = setup_logging(__name__)
        # Use provided config or create default one
        self.config = config or IngestionConfig.default_config()

    def download_data(self) -> None:
        """Download the latest COVID-19 data from JHU repository.

        Downloads three types of data:
        - Confirmed cases
        - Deaths
        - Recoveries

        Each file is saved with a timestamp in the configured raw data directory.

        Raises:
            RequestException: If download fails for any data type
        """
        # Create raw data directory if it doesn't exist
        self.config.raw_data_path.mkdir(parents=True, exist_ok=True)

        # Download each type of data (confirmed, deaths, recovered)
        for data_type, filename in self.config.data_types.items():
            url = f"{self.config.base_url}/{filename}"
            self.logger.info(f"Downloading {data_type} data from {url}")

            try:
                # Fetch data from JHU repository
                response = requests.get(url)
                response.raise_for_status()

                # Save file with timestamp in name (e.g., confirmed_20240315.csv)
                output_path = (
                    self.config.raw_data_path
                    / f"{data_type}_{datetime.now().strftime('%Y%m%d')}.csv"
                )
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                self.logger.info(
                    f"Successfully downloaded {data_type} data to {output_path}"
                )

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to download {data_type} data: {str(e)}")
                raise

    def cleanup_old_files(self) -> None:
        """Remove data files older than the configured retention period.

        Files are identified by their timestamp in the filename.
        Files older than retention_days are deleted from the raw data directory.

        Note:
            Files with invalid naming patterns are logged but not deleted.
        """
        self.logger.info(
            f"Cleaning up files older than {self.config.retention_days} days"
        )

        # Calculate the cutoff date based on retention period
        retention_delta = timedelta(days=self.config.retention_days)

        # Check all CSV files in the raw data directory
        for file in self.config.raw_data_path.glob("*.csv"):
            try:
                # Extract date from filename (expects format: type_YYYYMMDD.csv)
                file_date = datetime.strptime(file.stem.split('_')[1], '%Y%m%d')

                # Delete file if it's older than retention period
                if datetime.now() - file_date > retention_delta:
                    file.unlink()
                    self.logger.info(f"Removed old file: {file}")
            except (IndexError, ValueError) as e:
                self.logger.warning(
                    f"Could not parse date from filename {file}: {str(e)}"
                )

    def load_to_duckdb(self) -> None:
        """Load the downloaded data into DuckDB database.

        Process:
        1. Reads the latest file for each data type
        2. Validates data structure and content
        3. Cleans and transforms the data
        4. Creates or replaces tables in DuckDB

        Tables created:
        - raw_confirmed: Daily confirmed cases
        - raw_deaths: Daily death counts
        - raw_recovered: Daily recovery counts

        Raises:
            Exception: If any step in the process fails
        """
        self.logger.info("Starting data load to DuckDB")

        # Create directory for DuckDB file if it doesn't exist
        Path(self.config.db_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            # Initialize DuckDB connection
            conn = duckdb.connect(self.config.db_path)

            # Process each type of data (confirmed, deaths, recovered)
            for data_type in self.config.data_types.keys():
                # Find the most recent file for this data type
                latest_file = max(self.config.raw_data_path.glob(f"{data_type}_*.csv"))
                self.logger.info(f"Processing {latest_file}")

                # Load and validate the data
                df = pd.read_csv(latest_file)
                validate_data(df, data_type, self.logger)

                # Apply cleaning and transformation steps
                df = clean_data(df, self.logger)
                transformed_df = transform_time_series(df, data_type, self.logger)

                # Update or create the table in DuckDB
                table_name = f"raw_{data_type}"
                # Register DataFrame explicitly with DuckDB
                conn.register('transformed_data_view', transformed_df)
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                conn.execute(
                    f"CREATE TABLE {table_name} AS SELECT * FROM transformed_data_view"
                )
                self.logger.info(
                    f"Successfully loaded {data_type} data into {table_name}"
                )

            # Clean up resources
            conn.close()
            self.logger.info("Data load completed successfully")

        except Exception as e:
            self.logger.error(f"Error loading data to DuckDB: {str(e)}")
            raise
