"""Generate and apply patches to transform one CSV into another."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any
import json

from csvdiff.differ import DiffResult, RowChange


@dataclass
class Patch:
    key_column: str
    additions: List[Dict[str, Any]] = field(default_factory=list)
    removals: List[str] = field(default_factory=list)
    modifications: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "key_column": self.key_column,
            "additions": self.additions,
            "removals": self.removals,
            "modifications": self.modifications,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @staticmethod
    def from_dict(data: dict) -> "Patch":
        return Patch(
            key_column=data["key_column"],
            additions=data.get("additions", []),
            removals=data.get("removals", []),
            modifications=data.get("modifications", []),
        )

    @staticmethod
    def from_json(text: str) -> "Patch":
        return Patch.from_dict(json.loads(text))


def build_patch(result: DiffResult, key_column: str) -> Patch:
    patch = Patch(key_column=key_column)
    for change in result.changes:
        if change.change_type == "added":
            patch.additions.append(change.new_row)
        elif change.change_type == "removed":
            patch.removals.append(change.old_row[key_column])
        elif change.change_type == "modified":
            patch.modifications.append({
                "key": change.old_row[key_column],
                "fields": change.field_changes,
            })
    return patch


def apply_patch(rows: List[Dict[str, Any]], patch: Patch) -> List[Dict[str, Any]]:
    key = patch.key_column
    index = {row[key]: row.copy() for row in rows}

    for key_val in patch.removals:
        index.pop(str(key_val), None)

    for mod in patch.modifications:
        k = str(mod["key"])
        if k in index:
            for field_name, change in mod["fields"].items():
                index[k][field_name] = change.get("new", index[k].get(field_name))

    for addition in patch.additions:
        k = str(addition[key])
        index[k] = addition

    return list(index.values())
