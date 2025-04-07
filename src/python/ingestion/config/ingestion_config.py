# Built-in imports
from pathlib import Path
from dataclasses import dataclass
from typing import Dict


@dataclass
class IngestionConfig:
    """Configuration settings for COVID-19 data ingestion.

    This class holds all configuration parameters needed for the ingestion process.
    It uses Python's dataclass for automatic initialization and representation.

    Attributes:
        base_url: Base URL for JHU COVID-19 data repository
        data_types: Mapping of data types to their respective filenames
        raw_data_path: Directory path for storing raw downloaded files
        db_path: Path to the DuckDB database file
        retention_days: Number of days to keep raw files (default: 7)
    """

    base_url: str
    data_types: Dict[str, str]
    raw_data_path: Path
    db_path: str
    retention_days: int = 7

    @classmethod
    def default_config(cls) -> 'IngestionConfig':
        """Create a default configuration instance.

        Returns:
            IngestionConfig: Instance with default settings for JHU COVID data ingestion

        Example:
            >>> config = IngestionConfig.default_config()
            >>> print(config.raw_data_path)
            Path('data/raw')
        """
        return cls(
            base_url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series",
            data_types={
                'confirmed': 'time_series_covid19_confirmed_global.csv',
                'deaths': 'time_series_covid19_deaths_global.csv',
                'recovered': 'time_series_covid19_recovered_global.csv',
            },
            raw_data_path=Path('data/raw'),
            db_path='data/processed/covid_analysis_dev.duckdb',
        )
