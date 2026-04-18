"""Column and row filtering utilities for csvdiff."""
from typing import List, Optional, Dict


def filter_columns(
    rows: List[Dict[str, str]],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """Return rows with only the specified columns included/excluded."""
    if include and exclude:
        raise ValueError("Cannot specify both include and exclude column lists.")

    if not include and not exclude:
        return rows

    result = []
    for row in rows:
        if include:
            filtered = {k: v for k, v in row.items() if k in include}
        else:
            filtered = {k: v for k, v in row.items() if k not in exclude}
        result.append(filtered)
    return result


def filter_rows(
    rows: List[Dict[str, str]],
    column: str,
    value: str,
) -> List[Dict[str, str]]:
    """Return only rows where column matches value."""
    if not rows:
        return rows
    if column not in rows[0]:
        raise KeyError(f"Column '{column}' not found in data.")
    return [row for row in rows if row.get(column) == value]


def select_columns(
    rows: List[Dict[str, str]],
    columns: List[str],
) -> List[Dict[str, str]]:
    """Reorder/select columns, filling missing keys with empty string."""
    return [{col: row.get(col, "") for col in columns} for row in rows]
