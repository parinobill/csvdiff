"""Ledger: track cumulative change counts across multiple diff runs."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List

from csvdiff.differ import DiffResult


@dataclass
class LedgerEntry:
    label: str
    added: int
    removed: int
    modified: int

    @property
    def total(self) -> int:
        return self.added + self.removed + self.modified

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "LedgerEntry":
        return cls(**d)

    def __str__(self) -> str:
        return (
            f"{self.label}: +{self.added} -{self.removed} ~{self.modified}"
        )


@dataclass
class Ledger:
    entries: List[LedgerEntry] = field(default_factory=list)

    def record(self, label: str, result: DiffResult) -> LedgerEntry:
        counts = {"added": 0, "removed": 0, "modified": 0}
        for ch in result.changes:
            counts[ch.change_type] = counts.get(ch.change_type, 0) + 1
        entry = LedgerEntry(label=label, **counts)
        self.entries.append(entry)
        return entry

    def totals(self) -> LedgerEntry:
        a = sum(e.added for e in self.entries)
        r = sum(e.removed for e in self.entries)
        m = sum(e.modified for e in self.entries)
        return LedgerEntry(label="TOTAL", added=a, removed=r, modified=m)

    def summary(self) -> str:
        lines = [str(e) for e in self.entries]
        lines.append(str(self.totals()))
        return "\n".join(lines)


def save_ledger(ledger: Ledger, path: Path) -> None:
    data = [e.to_dict() for e in ledger.entries]
    path.write_text(json.dumps(data, indent=2))


def load_ledger(path: Path) -> Ledger:
    data = json.loads(path.read_text())
    return Ledger(entries=[LedgerEntry.from_dict(d) for d in data])
