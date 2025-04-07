# Built-in import
from pathlib import Path

# Local import
from src.python.ingestion.config.ingestion_config import IngestionConfig


def test_default_config_creation():
    """Test that default configuration is created correctly."""
    config = IngestionConfig.default_config()

    # Check base URL
    assert (
        config.base_url
        == "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"
    )

    # Check data types
    assert isinstance(config.data_types, dict)
    assert 'confirmed' in config.data_types
    assert 'deaths' in config.data_types
    assert 'recovered' in config.data_types

    # Check paths
    assert isinstance(config.raw_data_path, Path)
    assert config.raw_data_path == Path('data/raw')
    assert config.db_path == 'data/processed/covid_analysis_dev.duckdb'

    # Check default retention days
    assert config.retention_days == 7


def test_custom_config_creation():
    """Test that custom configuration can be created."""
    custom_config = IngestionConfig(
        base_url="https://custom.url",
        data_types={"test": "test.csv"},
        raw_data_path=Path("custom/path"),
        db_path="custom/db.duckdb",
        retention_days=14,
    )

    assert custom_config.base_url == "https://custom.url"
    assert custom_config.data_types == {"test": "test.csv"}
    assert custom_config.raw_data_path == Path("custom/path")
    assert custom_config.db_path == "custom/db.duckdb"
    assert custom_config.retention_days == 14
