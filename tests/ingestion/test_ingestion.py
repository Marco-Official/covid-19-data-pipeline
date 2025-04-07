# Global import
import pytest

# Built-in import
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from pathlib import Path

# Local import
from src.python.ingestion.core.covid_ingestion import CovidDataIngestion
from src.python.ingestion.config.ingestion_config import IngestionConfig


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return IngestionConfig(
        base_url="https://test.url",
        data_types={"test": "test.csv"},
        raw_data_path=Path("test/raw"),
        db_path="test/db.duckdb",
        retention_days=1,
    )


@pytest.fixture
def mock_ingestion(mock_config):
    """Create a mock ingestion instance."""
    return CovidDataIngestion(config=mock_config)


def test_ingestion_initialization(mock_config):
    """Test that ingestion class initializes correctly."""
    ingestion = CovidDataIngestion(config=mock_config)
    assert ingestion.config == mock_config
    assert hasattr(ingestion, 'logger')


@patch('requests.get')
def test_download_data_success(mock_get, mock_ingestion, tmp_path):
    """Test successful data download."""
    # Mock the response
    mock_response = Mock()
    mock_response.content = b"test,data\n1,2"
    mock_get.return_value = mock_response

    # Set up test directory
    mock_ingestion.config.raw_data_path = tmp_path / "raw"

    # Run download
    mock_ingestion.download_data()

    # Verify file was created
    assert len(list((tmp_path / "raw").glob("*.csv"))) == 1


@patch('requests.get')
def test_download_data_failure(mock_get, mock_ingestion):
    """Test data download failure."""
    mock_get.side_effect = Exception("Download failed")

    with pytest.raises(Exception):
        mock_ingestion.download_data()


@patch('duckdb.connect')
@patch('src.python.ingestion.utils.data_validation.validate_data')
def test_load_to_duckdb_success(mock_validate, mock_connect, mock_ingestion, tmp_path):
    """Test successful data loading to DuckDB."""
    # Mock DuckDB connection
    mock_conn = Mock()
    mock_connect.return_value = mock_conn

    # Mock validation to pass
    mock_validate.return_value = None

    # Set up test directory with a CSV file containing required columns
    test_file = tmp_path / "raw" / "test_20230101.csv"
    test_file.parent.mkdir(parents=True)

    # Create test data with required columns
    test_data = """Province/State,Country/Region,Lat,Long,1/1/20
"",Afghanistan,33.0,65.0,0
"",Albania,41.0,20.0,0"""
    test_file.write_text(test_data)

    # Update config to use the test directory
    mock_ingestion.config.raw_data_path = tmp_path / "raw"
    mock_ingestion.config.db_path = str(tmp_path / "test.duckdb")

    # Run load
    mock_ingestion.load_to_duckdb()

    # Verify DuckDB operations
    assert mock_conn.execute.called
    assert mock_conn.close.called


@patch('src.python.ingestion.core.covid_ingestion.datetime')
def test_cleanup_old_files(mock_datetime, mock_ingestion, tmp_path):
    """Test cleanup of old files."""
    # Set up test directory
    mock_ingestion.config.raw_data_path = tmp_path / "raw"
    mock_ingestion.config.raw_data_path.mkdir(parents=True)

    # Create old and new files with proper timestamps
    old_file = mock_ingestion.config.raw_data_path / "test_20220101.csv"
    new_file = mock_ingestion.config.raw_data_path / "test_20230101.csv"

    old_file.write_text("old")
    new_file.write_text("new")

    # Mock datetime.now() to return a fixed date
    current_date = datetime(2023, 1, 2)
    mock_datetime.now.return_value = current_date

    # Mock datetime.strptime to parse our test filenames
    def mock_strptime(date_string, format_string):
        if date_string == "20220101":
            return datetime(2022, 1, 1)
        elif date_string == "20230101":
            return datetime(2023, 1, 1)
        return datetime.strptime(date_string, format_string)

    mock_datetime.strptime.side_effect = mock_strptime

    # Mock timedelta
    mock_datetime.timedelta = timedelta

    # Run cleanup
    mock_ingestion.cleanup_old_files()

    # Verify old file was deleted but new file remains
    assert not old_file.exists()
    assert new_file.exists()
