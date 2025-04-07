# Global imports
import pytest
import dagster as dg

# Built-in import
from unittest.mock import patch, MagicMock

# Local imports
from covid_dagster.assets.ingestion_assets import ingest_covid_data
from covid_dagster.assets.dbt_assets import run_dbt_models


class MockCovidDataIngestion:
    def download_data(self):
        pass

    def load_to_duckdb(self):
        pass

    def cleanup_old_files(self):
        pass


@pytest.fixture
def mock_ingestion():
    return MockCovidDataIngestion()


@pytest.fixture
def dagster_context():
    context = dg.build_op_context()
    yield context
    # Cleanup after test
    if hasattr(context, 'instance'):
        context.instance.dispose()


def test_ingest_covid_data_success(mock_ingestion, dagster_context):
    """Test successful execution of the ingestion asset."""
    with patch(
        'covid_dagster.assets.ingestion_assets.CovidDataIngestion',
        return_value=mock_ingestion,
    ):
        result = ingest_covid_data(dagster_context)
        assert result is True


def test_ingest_covid_data_failure(mock_ingestion, dagster_context):
    """Test failure handling in the ingestion asset."""
    mock_ingestion.download_data = MagicMock(side_effect=Exception("Download failed"))

    with patch(
        'covid_dagster.assets.ingestion_assets.CovidDataIngestion',
        return_value=mock_ingestion,
    ):
        with pytest.raises(Exception):
            ingest_covid_data(dagster_context)


def test_run_dbt_models_success(dagster_context):
    """Test successful execution of the dbt asset."""
    # Mock the ingest_covid_data dependency first
    with patch('covid_dagster.assets.ingestion_assets.ingest_covid_data', return_value=True):
        # Then mock subprocess.run
        with patch('subprocess.run') as mock_run:
            # Create mock return values for all four commands
            deps_result = MagicMock()
            deps_result.returncode = 0
            deps_result.stdout = "dbt deps success"
            deps_result.stderr = ""

            compile_result = MagicMock()
            compile_result.returncode = 0
            compile_result.stdout = "dbt compile success"
            compile_result.stderr = ""

            run_result = MagicMock()
            run_result.returncode = 0
            run_result.stdout = "dbt run success"
            run_result.stderr = ""

            test_result = MagicMock()
            test_result.returncode = 0
            test_result.stdout = "dbt test success"
            test_result.stderr = ""

            # Set up the side effect to return our mocks in the correct order
            mock_run.side_effect = [deps_result, compile_result, run_result, test_result]

            # Execute the test
            result = run_dbt_models(dagster_context, True)
            
            # Verify results
            assert result is True
            assert mock_run.call_count == 4  # Called for deps, compile, run, and test
            
            # Verify the correct commands were called in the correct order
            deps_call = mock_run.call_args_list[0]
            compile_call = mock_run.call_args_list[1]
            run_call = mock_run.call_args_list[2]
            test_call = mock_run.call_args_list[3]
            
            assert deps_call[0][0] == ["dbt", "deps"]
            assert compile_call[0][0] == ["dbt", "compile"]
            assert run_call[0][0] == ["dbt", "run"]
            assert test_call[0][0] == ["dbt", "test"]


def test_run_dbt_models_test_failure(dagster_context):
    """Test handling of dbt test failures."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "Test failed"

        with pytest.raises(Exception):
            run_dbt_models(dagster_context, True)


def test_run_dbt_models_run_failure(dagster_context):
    """Test handling of dbt run failures."""
    with patch('subprocess.run') as mock_run:
        # First call (test) succeeds
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="Success", stderr=""),
            MagicMock(returncode=1, stdout="", stderr="Run failed"),
        ]

        with pytest.raises(Exception):
            run_dbt_models(dagster_context, True)
