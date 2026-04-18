"""Export diff results to various output formats (JSON, CSV, Markdown)."""

import csv
import io
import json
from typing import List

from csvdiff.differ import DiffResult, RowChange


def _changes_to_records(result: DiffResult) -> List[dict]:
    records = []
    for change in result.changes:
        base = {
            "change_type": change.change_type,
            "key": change.key,
        }
        if change.change_type == "modified":
            for field, (old_val, new_val) in change.fields.items():
                base[f"{field}_old"] = old_val
                base[f"{field}_new"] = new_val
        elif change.change_type == "added":
            base.update(change.row)
        elif change.change_type == "removed":
            base.update(change.row)
        records.append(base)
    return records


def export_json(result: DiffResult, indent: int = 2) -> str:
    """Serialize diff result to a JSON string."""
    records = _changes_to_records(result)
    return json.dumps({"changes": records, "total": len(records)}, indent=indent)


def export_csv(result: DiffResult) -> str:
    """Serialize diff result to a CSV string."""
    records = _changes_to_records(result)
    if not records:
        return ""
    fieldnames = sorted({k for r in records for k in r})
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in records:
        writer.writerow(row)
    return buf.getvalue()


def export_markdown(result: DiffResult) -> str:
    """Serialize diff result to a Markdown table string."""
    records = _changes_to_records(result)
    if not records:
        return "_No changes detected._\n"
    fieldnames = sorted({k for r in records for k in r})
    lines = []
    lines.append("| " + " | ".join(fieldnames) + " |")
    lines.append("| " + " | ".join("---" for _ in fieldnames) + " |")
    for row in records:
        lines.append("| " + " | ".join(str(row.get(f, "")) for f in fieldnames) + " |")
    return "\n".join(lines) + "\n"
