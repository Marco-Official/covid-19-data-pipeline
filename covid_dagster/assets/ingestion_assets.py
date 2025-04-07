# Global import
import dagster as dg

# Built-in import
from datetime import datetime

# Local import
from src.python.ingestion.core.covid_ingestion import CovidDataIngestion


@dg.asset(
    group_name="ingestion",
    description="""Ingest COVID-19 data from Johns Hopkins University CSSE.
    
    This asset performs the following operations:
    1. Downloads the latest COVID-19 data
    2. Loads the data into DuckDB
    3. Cleans up old data files
    
    Dependencies:
    - Internet connection for data download
    - Sufficient disk space for data storage
    - DuckDB installed and configured
    
    Expected runtime: 5-10 minutes depending on data size and network speed.
    """,
    metadata={
        "owner": "Marco Ramos",
        "expected_runtime_minutes": 10,
        "data_source": "Johns Hopkins University CSSE",
        "data_freshness": "Daily",
        "required_resources": {"memory": "2GB", "disk_space": "1GB"},
    },
)
def ingest_covid_data(context):
    """Ingest COVID-19 data using the existing CovidDataIngestion class.

    Args:
        context: Dagster context object for logging and metadata

    Returns:
        bool: True if ingestion was successful

    Raises:
        Exception: If data download or loading fails
    """
    start_time = datetime.now()

    try:
        # Initialize the ingestion class
        ingestion = CovidDataIngestion()

        # Download data
        context.log.info("Starting data download...")
        ingestion.download_data()

        # Load data into DuckDB
        context.log.info("Loading data to DuckDB...")
        ingestion.load_to_duckdb()

        # Clean up old files
        context.log.info("Cleaning up old files...")
        ingestion.cleanup_old_files()

        end_time = datetime.now()
        runtime = (end_time - start_time).total_seconds() / 60

        # Add detailed metadata
        context.add_output_metadata(
            {
                "execution_time_minutes": runtime,
                "completion_time": end_time.isoformat(),
                "status": "success",
                "data_source_url": "https://github.com/CSSEGISandData/COVID-19",
            }
        )

        context.log.info(f"COVID-19 data ingestion completed in {runtime:.2f} minutes.")
        return True

    except Exception as e:
        context.log.error(f"Data ingestion failed: {str(e)}")
        raise
