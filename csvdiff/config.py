"""Load and validate csvdiff configuration from a TOML or dict source."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from csvdiff.ignorer import IgnoreRules


@dataclass
class CsvDiffConfig:
    key_column: str = "id"
    ignore: IgnoreRules = field(default_factory=IgnoreRules)
    include_columns: List[str] = field(default_factory=list)
    exclude_columns: List[str] = field(default_factory=list)
    output_format: str = "text"  # text | json | markdown
    color: bool = True


def _parse_ignore(raw: Dict[str, Any]) -> IgnoreRules:
    return IgnoreRules(
        columns=raw.get("columns", []),
        row_filter=raw.get("row_filter"),
        change_types=raw.get("change_types", []),
    )


def from_dict(data: Dict[str, Any]) -> CsvDiffConfig:
    ignore_raw = data.get("ignore", {})
    return CsvDiffConfig(
        key_column=data.get("key_column", "id"),
        ignore=_parse_ignore(ignore_raw),
        include_columns=data.get("include_columns", []),
        exclude_columns=data.get("exclude_columns", []),
        output_format=data.get("output_format", "text"),
        color=data.get("color", True),
    )


def load_config(path: str | Path) -> CsvDiffConfig:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open() as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON config: {exc}") from exc
    return from_dict(data)


def default_config() -> CsvDiffConfig:
    return CsvDiffConfig()
