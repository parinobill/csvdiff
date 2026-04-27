"""Tests for csvdiff.differ_audit."""
import datetime

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_audit import (
    AuditMeta,
    AuditedResult,
    audit_result,
    new_meta,
)


def _result(changes=None) -> DiffResult:
    return DiffResult(changes=changes or [])


def _added(key="k1") -> RowChange:
    return RowChange(change_type="added", key=key, old_row={}, new_row={"id": key})


def _modified(key="k2") -> RowChange:
    return RowChange(
        change_type="modified",
        key=key,
        old_row={"id": key, "v": "a"},
        new_row={"id": key, "v": "b"},
    )


def test_new_meta_has_run_id():
    m = new_meta()
    assert len(m.run_id) == 36  # UUID4 string


def test_new_meta_timestamp_is_utc_iso():
    m = new_meta()
    assert m.timestamp.endswith("Z")
    # should parse without error
    datetime.datetime.fromisoformat(m.timestamp.rstrip("Z"))


def test_new_meta_label_none_by_default():
    assert new_meta().label is None


def test_new_meta_label_stored():
    m = new_meta(label="release-1.2")
    assert m.label == "release-1.2"


def test_audit_meta_round_trip():
    m = new_meta(label="test")
    assert AuditMeta.from_dict(m.to_dict()) == m


def test_audit_meta_str_contains_run_prefix():
    m = new_meta()
    assert m.run_id[:8] in str(m)


def test_audit_meta_str_contains_label_when_set():
    m = new_meta(label="foo")
    assert "foo" in str(m)


def test_audited_result_changes_proxied():
    r = _result([_added()])
    ar = audit_result(r)
    assert ar.changes == r.changes


def test_audited_result_summary_includes_meta():
    r = _result([_added()])
    ar = audit_result(r, label="ci")
    s = ar.summary()
    assert "ci" in s


def test_audit_result_no_label():
    r = _result()
    ar = audit_result(r)
    assert ar.meta.label is None
    assert "run=" in ar.summary()
