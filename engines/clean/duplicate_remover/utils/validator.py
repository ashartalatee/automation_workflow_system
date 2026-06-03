"""
validator.py
------------
Input validation utilities for the DuplicateRemover engine.
Centralizes all validation logic so engine.py stays clean.
"""

import logging
from pathlib import Path
from typing import List

import pandas as pd

logger = logging.getLogger(__name__)


def validate_input_file(path: Path) -> None:
    """
    Validate that the input file exists, is readable, and is non-empty.

    Args:
        path: Path object pointing to the CSV file.

    Raises:
        FileNotFoundError : File does not exist.
        ValueError        : File is empty or has zero size.
        TypeError         : Path is not a file (e.g., directory).
    """
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: '{path}'")

    if not path.is_file():
        raise TypeError(f"Path is not a file: '{path}'")

    if path.stat().st_size == 0:
        raise ValueError(f"Input file is empty: '{path}'")

    logger.debug("Input file validated: %s", path)


def validate_columns(df: pd.DataFrame, columns: List[str]) -> None:
    """
    Validate that all requested subset columns exist in the DataFrame.

    Args:
        df      : The loaded DataFrame to check against.
        columns : List of column names to validate.

    Raises:
        ValueError: One or more columns are missing from the DataFrame.
    """
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"Column(s) not found in dataset: {missing}. "
            f"Available columns: {list(df.columns)}"
        )
    logger.debug("All subset columns validated: %s", columns)
