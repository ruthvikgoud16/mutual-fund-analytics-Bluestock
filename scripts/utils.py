"""Utility functions and logging configurations for Mutual Fund Analytics.

This module provides logging setup and generic directory/file manipulation helpers.
"""

import logging
import sys
from pathlib import Path


def setup_logging(name: str = "mutual_fund_analytics") -> logging.Logger:
    """Configure and return a structured logger printing to standard output.

    Args:
        name: Name of the logger instance.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def ensure_directory(path: Path) -> None:
    """Ensure that the given directory path exists, creating it if necessary.

    Args:
        path: Path object representing the target directory.
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        # Log via simple print since logger is set up in each module
        print(f"Created directory: {path}")
