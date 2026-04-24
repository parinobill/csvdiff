"""Integration tests verifying rebase + patch round-trip correctness."""

import json
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_patch import Patch
from csvdiff.differ_rebase import rebase_patch


def _ch(key, ctype, before, after):
    return RowChange(key=key, change_type=ctype, before=before, after=after)


def _result(*changes):
    return DiffResult(changes=list(changes))


def test_rebase_round_trips_through_patch_serialisation():
    """Rebased result survives JSON serialisation and deserialisation."""
    orig = _result(_ch("1", "added", {}, {"id": "1"}))
    upstream = _result(_ch("2", "modified", {"id": "2", "v": "a"}, {"id": "2", "v": "b"}))
    rebase_result = rebase_patch(orig, upstream)

    patch = Patch.from_diff_result(rebase_result.rebased)
    serialised = patch.to_json()
    loaded = Patch.from_json(serialised)
    restored = loaded.to_diff_result()

    assert len(restored.changes) == 2
    keys = {ch.key for ch in restored.changes}
    assert keys == {"1", "2"}


def test_all_conflicting_leaves_only_upstream_changes():
    orig = _result(
        _ch("A", "modified", {"id": "A", "x": "1"}, {"id": "A", "x": "2"}),
        _ch("B", "removed", {"id": "B"}, {}),
    )
    upstream = _result(
        _ch("A", "modified", {"id": "A", "x": "1"}, {"id": "A", "x": "99"}),
        _ch("B", "modified", {"id": "B", "y": "old"}, {"id": "B", "y": "new"}),
    )
    result = rebase_patch(orig, upstream)
    assert len(result.conflicts) == 2
    # Upstream changes win and appear in rebased
    keys = {ch.key for ch in result.rebased.changes}
    assert keys == set()  # both conflicted, none kept from orig; upstream already in index


def test_partial_overlap_correct_counts():
    orig = _result(
        _ch("keep", "added", {}, {"id": "keep"}),
        _ch("clash", "modified", {"id": "clash", "v": "1"}, {"id": "clash", "v": "2"}),
    )
    upstream = _result(
        _ch("clash", "modified", {"id": "clash", "v": "1"}, {"id": "clash", "v": "X"}),
        _ch("new", "added", {}, {"id": "new"}),
    )
    result = rebase_patch(orig, upstream)
    assert len(result.conflicts) == 1
    rebased_keys = {ch.key for ch in result.rebased.changes}
    assert "keep" in rebased_keys
    assert "new" in rebased_keys
    assert "clash" not in rebased_keys
