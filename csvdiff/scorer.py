"""Similarity scoring for CSV diff results.

Provides a numeric similarity score (0.0–1.0) between two CSV snapshots
based on the proportion of unchanged rows.
"""

from dataclasses import dataclass
from typing import Optional
from csvdiff.differ import DiffResult


@dataclass
class SimilarityScore:
    """Holds the computed similarity metrics between two CSV files."""
    total_rows: int
    unchanged_rows: int
    added: int
    removed: int
    modified: int

    @property
    def score(self) -> float:
        """Return similarity as a float between 0.0 and 1.0."""
        if self.total_rows == 0:
            return 1.0
        return self.unchanged_rows / self.total_rows

    @property
    def percent(self) -> float:
        """Return similarity as a percentage (0–100)."""
        return round(self.score * 100, 2)

    def __str__(self) -> str:
        return (
            f"Similarity: {self.percent}% "
            f"({self.unchanged_rows}/{self.total_rows} rows unchanged, "
            f"+{self.added} added, -{self.removed} removed, ~{self.modified} modified)"
        )


def compute_score(result: DiffResult, total_rows_in_old: int) -> SimilarityScore:
    """Compute a similarity score from a DiffResult.

    Args:
        result: The diff result produced by the differ.
        total_rows_in_old: Total number of rows in the *original* CSV file.

    Returns:
        A SimilarityScore instance.
    """
    added = sum(1 for c in result.changes if c.change_type == "added")
    removed = sum(1 for c in result.changes if c.change_type == "removed")
    modified = sum(1 for c in result.changes if c.change_type == "modified")

    # Total rows seen across both files (union size approximation)
    total = total_rows_in_old + added
    unchanged = total_rows_in_old - removed - modified
    unchanged = max(unchanged, 0)

    return SimilarityScore(
        total_rows=total,
        unchanged_rows=unchanged,
        added=added,
        removed=removed,
        modified=modified,
    )


def score_as_dict(score: SimilarityScore) -> dict:
    """Serialize a SimilarityScore to a plain dictionary."""
    return {
        "score": score.score,
        "percent": score.percent,
        "total_rows": score.total_rows,
        "unchanged_rows": score.unchanged_rows,
        "added": score.added,
        "removed": score.removed,
        "modified": score.modified,
    }
