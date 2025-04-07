# Local imports
from .core.covid_ingestion import CovidDataIngestion
from .utils.logging_setup import setup_logging


def main():
    """Main entry point for COVID-19 data ingestion pipeline.

    Executes the complete data ingestion process:
    1. Downloads latest COVID-19 data from JHU
    2. Validates and cleans the data
    3. Loads data into DuckDB
    4. Cleans up old files

    Raises:
        Exception: If any step in the pipeline fails

    Example:
        To run the ingestion pipeline:

        # From project root directory
        $ python -m src.python.ingestion

        This will:
        1. Create necessary directories (data/raw, data/processed, data/logs)
        2. Download latest COVID-19 data files
        3. Create/update DuckDB tables:
           - raw_confirmed
           - raw_deaths
           - raw_recovered
        4. Remove files older than 7 days

        The process logs will be available in data/logs/ingestion.log
    """
    logger = setup_logging(__name__)

    try:
        ingestion = CovidDataIngestion()
        ingestion.download_data()
        ingestion.load_to_duckdb()
        ingestion.cleanup_old_files()
        logger.info("Data ingestion pipeline completed successfully!")

    except Exception as e:
        logger.error(f"Data ingestion pipeline failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
