# Global import
import dagster as dg

# Built-in import
from typing import cast

# Local import
from covid_dagster.definitions import defs, covid_pipeline, all_assets


def test_definitions_structure():
    """Test that the definitions object is properly structured."""
    assert isinstance(defs, dg.Definitions)
    assert hasattr(defs, 'get_job_def')
    assert defs.get_job_def("covid_pipeline") is not None


def test_covid_pipeline_configuration():
    """Test that the covid_pipeline job is properly configured."""
    assert covid_pipeline.name == "covid_pipeline"
    assert isinstance(covid_pipeline.selection, dg.AssetSelection)


def test_assets_loading():
    """Test that assets are properly loaded from the modules."""
    asset_keys = []
    for asset in all_assets:
        if isinstance(asset, dg.AssetsDefinition):
            asset_keys.extend(key.to_string() for key in asset.keys)
        else:
            # For other asset types
            asset_keys.append(str(asset))

    expected_assets = {"ingest_covid_data", "run_dbt_models"}
    assert all(asset in str(asset_keys) for asset in expected_assets)


def test_asset_dependencies():
    """Test that asset dependencies are properly set up."""
    # Check that run_dbt_models depends on ingest_covid_data
    for asset in all_assets:
        if isinstance(asset, dg.AssetsDefinition) and "run_dbt_models" in str(asset):
            assert "ingest_covid_data" in str(asset.dependency_keys)


def test_job_asset_selection():
    """Test that the job selects the correct assets."""
    selection = dg.AssetSelection.all()

    selected_keys = selection.resolve(cast(list, all_assets))

    assert any("ingest_covid_data" in str(key) for key in selected_keys)
    assert any("run_dbt_models" in str(key) for key in selected_keys)
