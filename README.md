# COVID-19 Data Pipeline

A robust data pipeline for ingesting, processing, and analyzing COVID-19 data from Johns Hopkins University CSSE. Built with Dagster for orchestration, dbt for transformation, and DuckDB for storage.

## Table of Contents

- [Features](#features)
- [Data Transformation Process](#data-transformation-process)
  - [Raw Data Ingestion](#1-raw-data-ingestion)
  - [Data Cleaning](#2-data-cleaning-dbt-models)
  - [Final Schema Design](#3-final-schema-design-duckdb)
- [Data Analysis Results](#data-analysis-results)
  - [Top 5 Most Common Countries](#1--top-5-most-common-countries-by-record-count)
  - [Global COVID-19 Trends](#2--global-covid-19-trends-over-the-last-14-days)
  - [Case-Mortality Correlation](#3-correlation-between-total-cases-and-mortality-rate)
- [Design Decisions](#design-decisions)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Using Docker](#using-docker-recommended)
  - [Manual Installation](#manual-installation-alternative)
- [Usage](#usage)
  - [Docker Usage](#using-docker-recommended-1)
  - [Manual Usage](#manual-usage)
- [Project Structure](#project-structure)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

- **Data Ingestion**: Automated download and storage of COVID-19 data
- **Data Processing**: Clean and transform data using dbt
- **Data Storage**: Efficient storage using DuckDB
- **Data Analysis**: Pre-built queries for common COVID-19 metrics
- **Testing**: Comprehensive test suite for all components
- **Documentation**: Detailed documentation for all assets and jobs

## Data Transformation Process

### 1. Raw Data Ingestion

- Source: Johns Hopkins University CSSE COVID-19 Data Repository
- Format: CSV files with daily case and death counts
- Initial Schema (from JHU CSSE data):
  - Province/State # Province or state name (can be null)
  - Country/Region # Country or region name
  - Lat # Latitude coordinate
  - Long # Longitude coordinate
  - date # Date of observation
  - count # Cumulative count based on file type: (confirmed cases, death count, recovered count)

### 2. Data Cleaning (dbt Models)

- **Handling Missing Values**:

  - Replace null values with 0 for case and death counts

- **Data Deduplication**:

  - Ensure unique records by joining on (date, country, province) combination
  - Handle NULL provinces using COALESCE for consistent matching

- **Format Transformation**:
  - Clean column names (e.g., "Province/State" → province_state)
  - Standardize metric names (confirmed → confirmed_cases, deaths → death_count)
  - Calculate derived metrics (active_cases, mortality_rate, recovery_rate)

### 3. Final Schema Design (DuckDB)

Our database is organized into multiple schemas, each serving a specific purpose in the data pipeline:

#### Raw Data Schema (`main`)

Contains the original source data:

- `raw_confirmed`: Daily confirmed cases
- `raw_deaths`: Daily death counts
- `raw_recovered`: Daily recovery counts

#### Staging Schema (`main_staging`)

Contains cleaned and standardized data:

- `stg_covid_metrics`: Combined and cleaned metrics with calculated fields

#### Analytics Schema (`main_analytics`)

Contains aggregated metrics for analysis:

- `country_metrics`: Country-level aggregated statistics
- `daily_metrics`: Daily aggregated statistics
- `daily_trends`: Time-series analysis of trends

#### Reporting Schema (`main_reporting`)

Contains analytical views for reporting:

- `country_mortality_analysis`: Country-specific mortality analysis
- `global_daily_trends`: Global trend analysis
- `top_countries_by_records`: Rankings of countries by key metrics

This schema design follows a typical data warehouse pattern:

1. Raw data is stored in the `main` schema
2. Data is cleaned and standardized in the `main_staging` schema
3. Analytics-ready tables are created in `main_analytics`
4. Reporting views are maintained in `main_reporting`

## Data Analysis Results

### 1. 📊 Top 5 Most Common Countries by Record Count

Based on the query:

```sql
SELECT * FROM main_reporting.top_countries_by_records ORDER BY record_count DESC LIMIT 5;
```

I analyzed the top 5 most frequent values in the `country_region` column and their corresponding record counts.

| Rank | Country        | Record Count | Frequency (%) |
| ---- | -------------- | ------------ | ------------- |
| 1    | China          | 38,862       | 11.76%        |
| 2    | Canada         | 18,288       | 5.54%         |
| 3    | United Kingdom | 17,145       | 5.19%         |
| 4    | France         | 13,716       | 4.15%         |
| 5    | Australia      | 9,144        | 2.77%         |

### 🔍 Key Insights

- **China** has the highest number of records, accounting for **11.76%** of all entries.
- A significant drop in record count is seen after China, with other countries having roughly half or less.
- These five countries together make up approximately **29.41%** of the total dataset.
- The dominance of these countries in record count may reflect factors like early pandemic impact, better data infrastructure, or more comprehensive reporting practices.

### 2. 📈 Global COVID-19 Trends Over the Last 14 Days

```sql
SELECT
    date,
    total_cases,
    new_cases,
    total_deaths,
    avg_growth_rate,
    cases_7day_avg
FROM main_reporting.global_daily_trends
ORDER BY date DESC
LIMIT 14;
```

This section highlights global COVID-19 trends, analyzing the progression of cases and deaths from **February 24 to March 9, 2023**. The metrics were aggregated daily and smoothed using a 7-day moving average.

### 🦠 New COVID-19 Cases

- **Highest daily new cases**:  
  📅 March 1, 2023 — **220,614** new cases
- **Lowest daily new cases**:  
  📅 February 25, 2023 — **45,451** new cases

Although there were fluctuations, daily new cases remained relatively stable, ranging between ~45k and ~220k.

### 📉 7-Day Moving Average

- 7-day average of new cases **decreased** from **150,644** on Feb 24 to **119,748** on Mar 9.
- Indicates a **moderate downward trend** in new case counts globally.

### 💀 Cumulative Deaths

- Total global deaths increased from **6,870,806** to **6,881,802**.
- That's an increase of approximately **10,996 deaths** over 14 days.

### 📊 Growth Rate (%)

- Daily growth rate stayed consistently low at **0.00% to 0.03%**.
- Suggests that the global spread has **stabilized** during this timeframe.

---

### ✅ Summary

- The pandemic is currently in a **plateau or slight decline phase**.
- There's no indication of a major spike in new cases or deaths.
- Continued monitoring is essential for detecting potential new waves or variants.

### 3. Correlation Between Total Cases and Mortality Rate

This analysis investigates whether there's a relationship between the total number of confirmed COVID-19 cases and the mortality rate across countries.

We used the dbt model `main_reporting.country_mortality_analysis`, which includes countries with more than 1,000 confirmed cases to ensure statistical significance.

```sql
SELECT
  country_region,
  total_cases,
  mortality_rate
FROM main_reporting.country_mortality_analysis
ORDER BY total_cases DESC;
```

From the dataset, we observed:

- Countries with the **highest number of cases** (e.g., United States, India, France) do not necessarily have high mortality rates.
- Some countries with **fewer cases** (e.g., Mexico, Peru, Yemen) show **very high mortality rates** — suggesting healthcare quality and reporting accuracy play a significant role.
- For example:
  - **United States**: 103.8M cases, 1.08% mortality
  - **Mexico**: 7.5M cases, 4.45% mortality
  - **Yemen**: 11.9K cases, 18.07% mortality

There is no strong linear relationship between total cases and mortality rate. A statistical correlation analysis would likely confirm that the two variables are **weakly correlated or uncorrelated**. Mortality rate appears to depend more on contextual factors than case volume alone.

## Design Decisions

### Technology Choices

1. **Dagster**:

   - Provides robust pipeline orchestration
   - Built-in monitoring and logging
   - Easy integration with dbt and DuckDB

2. **dbt**:

   - Enables version-controlled data transformations
   - Provides testing framework for data quality
   - Supports incremental models for efficiency

3. **DuckDB**:
   - Fast analytical queries
   - Simple file-based storage
   - SQL interface for easy analysis

## Prerequisites

- Docker and Docker Compose
- Python (Optional)
- Git

## Installation

### Using Docker (Recommended)

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Marco-Official/covid-19-data-pipeline.git
   cd covid-19-data-pipeline
   ```

2. **Build and start the containers**:

   ```bash
   docker-compose up --build
   ```

3. **Access the services**:

   - Dagster UI: http://localhost:3000

### Manual Installation (Alternative)

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/covid-19-data-pipeline.git
   cd covid-19-data-pipeline
   ```

2. **Create and activate virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Using Docker (Recommended)

1. **Start the pipeline**:

   ```bash
   docker-compose up
   ```

2. **Run the pipeline through Dagster UI**:

   - Open http://localhost:3000 in your browser
   - Navigate to the "Assets" tab
   - Select both assets:
     - `ingest_covid_data`
     - `run_dbt_models`
   - Click "Materialize selected (2)" button in the upper right
   - View the run progress
   - Wait for completion (typically ~13 seconds, depending on internet connection)

3. **Access the DuckDB database**:

   ```bash
   # Method 1: Using Python
   docker-compose exec app python
   >>> import duckdb
   >>> conn = duckdb.connect('data/processed/covid_analysis_dev.duckdb')
   >>> conn.sql('SELECT * FROM main_reporting.top_countries_by_records LIMIT 5;').show()

   # Method 2: Using DBeaver
   # 1. Open DBeaver
   # 2. Create a new DuckDB connection
   # 3. Set the database path to:
   #    <directory-path>/covid-19-data-pipeline/data/processed/covid_analysis_dev.duckdb
   # 4. Connect and explore the schemas:
   #    - main
   #    - main_staging
   #    - main_analytics
   #    - main_reporting

   ```

4. **Run tests**:

   ```bash
   # From the project root directory
   pytest tests -v
   ```

5. **View logs**:
   ```bash
   docker-compose logs -f
   ```

### Common Docker Commands

- **Stop the pipeline**:

  ```bash
  docker-compose down
  ```

- **Rebuild containers**:

  ```bash
  docker-compose up --build
  ```

- **View container status**:

  ```bash
  docker-compose ps
  ```

- **Access container shell**:
  ```bash
  docker-compose exec -it covid-19-data-pipeline-covid-pipeline bash
  ```

### Manual Usage

1. **Start Dagster UI**:

   ```bash
   dagster dev
   ```

2. **Run the pipeline**:

   - Open http://localhost:3000 in your browser
   - Navigate to the "Assets" tab
   - Select both assets:
     - `ingest_covid_data`
     - `run_dbt_models`
   - Click "Materialize selected (2)" button in the upper right
   - View the run progress
   - Wait for completion (typically ~13 seconds, depending on internet connection)

3. **Run tests**:
   ```bash
   # From the project root directory
   pytest tests -v
   ```

## Project Structure

```
.
├── covid_dagster/           # Dagster pipeline code
│   ├── assets/             # Asset definitions
│   └── definitions.py      # Pipeline configuration
├── src/
│   ├── dbt/               # dbt models and tests
│   └── python/            # Python utilities
├── tests/                 # Test suite
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Docker build file
└── requirements.txt      # Python dependencies
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Developer**: Marco Ramos - Creator and maintainer of this COVID-19 data pipeline
- **Data Source**: Johns Hopkins University CSSE for the COVID-19 data
