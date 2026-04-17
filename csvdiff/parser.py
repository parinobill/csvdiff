"""CSV parsing utilities for csvdiff."""

import csv
from typing import Dict, List, Optional, Tuple


def read_csv(filepath: str, key_column: str) -> Tuple[Dict[str, Dict], List[str]]:
    """
    Read a CSV file and return a dict keyed by the key_column value.

    Args:
        filepath: Path to the CSV file.
        key_column: Column name to use as the unique row identifier.

    Returns:
        A tuple of (rows_dict, fieldnames) where rows_dict maps key -> row dict.

    Raises:
        FileNotFoundError: If the file does not exist.
        KeyError: If the key_column is not present in the CSV headers.
    """
    rows: Dict[str, Dict] = {}
    fieldnames: List[str] = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return {}, []
        fieldnames = list(reader.fieldnames)
        if key_column not in fieldnames:
            raise KeyError(
                f"Key column '{key_column}' not found in {filepath}. "
                f"Available columns: {fieldnames}"
            )
        for row in reader:
            key = row[key_column]
            rows[key] = dict(row)

    return rows, fieldnames


def get_all_columns(fieldnames_a: List[str], fieldnames_b: List[str]) -> List[str]:
    """Return a deduplicated ordered list of columns from both files."""
    seen = set()
    combined: List[str] = []
    for col in fieldnames_a + fieldnames_b:
        if col not in seen:
            combined.append(col)
            seen.add(col)
    return combined
