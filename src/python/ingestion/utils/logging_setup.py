# Built-in imports
from pathlib import Path
import logging


def setup_logging(name: str) -> logging.Logger:
    """Configure and return a logger instance.

    Sets up logging with both file and console output. The file output
    is saved in 'data/logs/ingestion.log'.

    Args:
        name: The name for the logger, typically __name__ of the calling module

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = setup_logging(__name__)
        >>> logger.info("Starting process")

    """
    # Create logs directory if it doesn't exist
    # Path: data/logs/ingestion.log
    log_path = Path('data/logs')
    log_path.mkdir(parents=True, exist_ok=True)

    # Configure the basic settings for logging
    logging.basicConfig(
        # Set the minimum logging level to capture
        level=logging.INFO,
        # Define log message format:
        # timestamp - module_name - log_level - message
        # Example: "2024-03-15 10:30:45 - ingestion.core - INFO - Starting download"
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        # Set up two handlers for output:
        handlers=[
            # 1. FileHandler: Writes logs to ingestion.log file
            logging.FileHandler(log_path / 'ingestion.log'),
            # 2. StreamHandler: Prints logs to console/terminal
            logging.StreamHandler(),
        ],
    )

    # Get and return a logger instance with the specified name
    return logging.getLogger(name)
