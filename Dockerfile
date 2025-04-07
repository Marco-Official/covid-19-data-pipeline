# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Install dbt and DuckDB adapter
RUN pip install --no-cache-dir dbt-duckdb

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed data/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV DAGSTER_HOME=/app/dagster_home

# Create dagster home directory and set ownership
RUN mkdir -p $DAGSTER_HOME && \
    chown -R 1000:1000 $DAGSTER_HOME

# Switch to non-root user
USER 1000

# Expose Dagster UI port
EXPOSE 3000

# Command to run the application
CMD ["dagster", "dev", "-h", "0.0.0.0"]
