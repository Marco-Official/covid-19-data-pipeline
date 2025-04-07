# Global import
import dagster as dg

# Local import
from . import assets

# Load all assets from the assets module
all_assets = dg.load_assets_from_modules([assets])

# Define a job that will materialize all assets
covid_pipeline = dg.define_asset_job(
    name="covid_pipeline",
    selection="*",  # Select all assets
)

defs = dg.Definitions(
    assets=all_assets,
    jobs=[covid_pipeline],
)
