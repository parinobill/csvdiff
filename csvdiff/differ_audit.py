"""Audit trail: attach timestamps and run IDs to diff results."""
from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class AuditMeta:
    run_id: str
    timestamp: str  # ISO-8601
    label: Optional[str] = None

    def to_dict(self) -> dict:
        return {"run_id": self.run_id, "timestamp": self.timestamp, "label": self.label}

    @classmethod
    def from_dict(cls, d: dict) -> "AuditMeta":
        return cls(run_id=d["run_id"], timestamp=d["timestamp"], label=d.get("label"))

    def __str__(self) -> str:
        parts = [f"run={self.run_id[:8]}", f"at={self.timestamp}"]
        if self.label:
            parts.append(f"label={self.label}")
        return " ".join(parts)


@dataclass
class AuditedResult:
    meta: AuditMeta
    result: DiffResult

    @property
    def changes(self) -> List[RowChange]:
        return self.result.changes

    def summary(self) -> str:
        return f"[{self.meta}] {self.result.summary()}"


def new_meta(label: Optional[str] = None) -> AuditMeta:
    """Create a fresh AuditMeta with a new UUID and current UTC timestamp."""
    return AuditMeta(
        run_id=str(uuid.uuid4()),
        timestamp=datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        label=label,
    )


def audit_result(result: DiffResult, label: Optional[str] = None) -> AuditedResult:
    """Wrap a DiffResult with a fresh audit stamp."""
    return AuditedResult(meta=new_meta(label), result=result)
