"""Persist and retrieve audited diff results from a JSON-lines log file."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, List, Optional

from csvdiff.differ_audit import AuditMeta, AuditedResult
from csvdiff.differ_patch import Patch, build_patch
from csvdiff.differ import DiffResult


def _entry_to_dict(audited: AuditedResult) -> dict:
    patch = build_patch(audited.result)
    return {"audit": audited.meta.to_dict(), "patch": patch.to_dict()}


def _entry_from_dict(d: dict) -> dict:
    """Return raw dict; callers may reconstruct as needed."""
    return d


def append_entry(path: Path, audited: AuditedResult) -> None:
    """Append one audited result as a JSON line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(_entry_to_dict(audited)) + "\n")


def iter_entries(path: Path) -> Iterator[dict]:
    """Yield raw entry dicts from a JSON-lines audit log."""
    if not path.exists():
        return
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_entries(path: Path) -> List[dict]:
    return list(iter_entries(path))


def entry_count(path: Path) -> int:
    return sum(1 for _ in iter_entries(path))


def last_entry(path: Path) -> Optional[dict]:
    last = None
    for entry in iter_entries(path):
        last = entry
    return last
