# Global import
import dagster as dg

# Built-in imports
from datetime import datetime
from pathlib import Path
import subprocess


@dg.asset(
    group_name="dbt",
    description="""Run dbt models and tests for COVID-19 data transformation.
    
    This asset performs the following operations:
    1. Installs dbt dependencies
    2. Compiles dbt models to validate SQL
    3. Runs dbt models to transform the data
    4. Runs dbt tests to validate data quality
    
    Dependencies:
    - dbt installed and configured
    - Valid profiles.yml with database connection
    - Successful data ingestion (ingest_covid_data)
    
    Expected runtime: 2-5 minutes depending on data size and model complexity.
    """,
    metadata={
        "owner": "Marco Ramos",
        "expected_runtime_minutes": 5,
        "dbt_version": ">=1.0.0",
        "required_resources": {"memory": "1GB", "disk_space": "500MB"},
    },
)
def run_dbt_models(context, ingest_covid_data):
    """Run dbt models and tests for COVID-19 data transformation.

    Args:
        context: Dagster context object for logging and metadata
        ingest_covid_data: Dependency on the data ingestion asset

    Returns:
        bool: True if dbt operations were successful

    Raises:
        subprocess.CalledProcessError: If dbt commands fail
        Exception: For other unexpected errors
    """
    start_time = datetime.now()
    dbt_dir = Path("src/dbt")

    try:
        # Install dbt dependencies
        context.log.info("Installing dbt dependencies...")
        deps_result = subprocess.run(
            ["dbt", "deps"], cwd=dbt_dir, capture_output=True, text=True
        )

        if deps_result.returncode != 0:
            context.log.error(f"dbt deps failed: {deps_result.stderr}")
            raise subprocess.CalledProcessError(
                deps_result.returncode,
                deps_result.args,
                deps_result.stdout,
                deps_result.stderr,
            )

        # Compile dbt models
        context.log.info("Compiling dbt models...")
        compile_result = subprocess.run(
            ["dbt", "compile"], cwd=dbt_dir, capture_output=True, text=True
        )

        if compile_result.returncode != 0:
            context.log.error(f"dbt compile failed: {compile_result.stderr}")
            raise subprocess.CalledProcessError(
                compile_result.returncode,
                compile_result.args,
                compile_result.stdout,
                compile_result.stderr,
            )
        
        # Run dbt models
        context.log.info("Running dbt models...")
        run_result = subprocess.run(
            ["dbt", "run"], cwd=dbt_dir, capture_output=True, text=True
        )

        if run_result.returncode != 0:
            context.log.error(f"dbt run failed: {run_result.stderr}")
            raise subprocess.CalledProcessError(
                run_result.returncode,
                run_result.args,
                run_result.stdout,
                run_result.stderr,
            )
        
        # Run dbt tests
        context.log.info("Running dbt tests...")
        test_result = subprocess.run(
            ["dbt", "test"], cwd=dbt_dir, capture_output=True, text=True
        )

        if test_result.returncode != 0:
            context.log.error(f"dbt tests failed: {test_result.stderr}")
            raise subprocess.CalledProcessError(
                test_result.returncode,
                test_result.args,
                test_result.stdout,
                test_result.stderr,
            )

        end_time = datetime.now()
        runtime = (end_time - start_time).total_seconds() / 60

        # Add detailed metadata
        context.add_output_metadata(
            {
                "execution_time_minutes": runtime,
                "completion_time": end_time.isoformat(),
                "status": "success",
                "tests_passed": True,
                "models_run": True,
                "dbt_directory": str(dbt_dir),
                "test_output": test_result.stdout,
                "run_output": run_result.stdout,
                "compile_output": compile_result.stdout,
            }
        )

        context.log.info(f"dbt operations completed in {runtime:.2f} minutes.")
        return True

    except subprocess.CalledProcessError as e:
        context.log.error(f"dbt command failed: {str(e)}")
        raise
    except Exception as e:
        context.log.error(f"Unexpected error in dbt operations: {str(e)}")
        raise
