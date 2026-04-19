"""Read and write patch files to disk."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Union

from csvdiff.differ_patch import Patch


def save_patch(patch: Patch, path: Union[str, Path]) -> None:
    """Serialize patch to a JSON file."""
    Path(path).write_text(patch.to_json(indent=2), encoding="utf-8")


def load_patch(path: Union[str, Path]) -> Patch:
    """Deserialize patch from a JSON file."""
    text = Path(path).read_text(encoding="utf-8")
    return Patch.from_json(text)


def patch_summary(patch: Patch) -> str:
    lines = [
        f"Key column : {patch.key_column}",
        f"Additions  : {len(patch.additions)}",
        f"Removals   : {len(patch.removals)}",
        f"Modifications: {len(patch.modifications)}",
    ]
    return "\n".join(lines)
