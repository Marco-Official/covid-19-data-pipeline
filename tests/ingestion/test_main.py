# Global import
import pytest

# Built-in import
from unittest.mock import patch, MagicMock

# Local import
from src.python.ingestion.__main__ import main


@patch('src.python.ingestion.__main__.CovidDataIngestion')
def test_main_success(mock_ingestion_class):
    """Test successful execution of main function."""
    # Mock the ingestion instance
    mock_ingestion = MagicMock()
    mock_ingestion_class.return_value = mock_ingestion

    # Run main
    main()

    # Verify methods were called in correct order
    mock_ingestion.download_data.assert_called_once()
    mock_ingestion.load_to_duckdb.assert_called_once()
    mock_ingestion.cleanup_old_files.assert_called_once()


@patch('src.python.ingestion.__main__.CovidDataIngestion')
def test_main_failure(mock_ingestion_class):
    """Test main function with failure."""
    # Mock the ingestion instance to raise an exception
    mock_ingestion = MagicMock()
    mock_ingestion.download_data.side_effect = Exception("Test error")
    mock_ingestion_class.return_value = mock_ingestion

    # Run main and expect exception
    with pytest.raises(Exception):
        main()

    # Verify cleanup was not called after error
    mock_ingestion.cleanup_old_files.assert_not_called()
