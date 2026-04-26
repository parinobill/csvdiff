"""Cluster diff changes by row similarity using a simple key-distance heuristic."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class ChangeCluster:
    """A group of related RowChanges sharing a common cluster label."""

    label: str
    changes: List[RowChange] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.changes)

    def change_types(self) -> List[str]:
        return list({c.change_type for c in self.changes})

    def summary(self) -> str:
        types = ", ".join(sorted(self.change_types()))
        return f"Cluster '{self.label}': {len(self.changes)} change(s) [{types}]"


@dataclass
class ClusterResult:
    clusters: Dict[str, ChangeCluster] = field(default_factory=dict)
    unclustered: List[RowChange] = field(default_factory=list)

    def all_clusters(self) -> List[ChangeCluster]:
        return list(self.clusters.values())

    def total_clustered(self) -> int:
        return sum(len(c) for c in self.clusters.values())


def _cluster_label(change: RowChange, key_column: str, prefix_len: int) -> Optional[str]:
    """Derive a cluster label from the key value prefix."""
    key_val = change.key_value or ""
    if not key_val:
        return None
    return str(key_val)[:prefix_len]


def cluster_diff(
    result: DiffResult,
    key_column: str,
    prefix_len: int = 3,
) -> ClusterResult:
    """Group changes into clusters based on the leading characters of the key value."""
    cr = ClusterResult()
    for change in result.changes:
        label = _cluster_label(change, key_column, prefix_len)
        if label is None:
            cr.unclustered.append(change)
            continue
        if label not in cr.clusters:
            cr.clusters[label] = ChangeCluster(label=label)
        cr.clusters[label].changes.append(change)
    return cr


def cluster_summary(cr: ClusterResult) -> str:
    lines = [f"Total clusters: {len(cr.clusters)}",
             f"Unclustered changes: {len(cr.unclustered)}"]
    for cluster in sorted(cr.clusters.values(), key=lambda c: c.label):
        lines.append("  " + cluster.summary())
    return "\n".join(lines)
