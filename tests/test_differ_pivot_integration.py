"""Integration tests: pivot interacts correctly with real DiffResult data."""
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_pivot import pivot_diff, top_changed_fields


def _rc(key, ctype, old, new, fields):
    return RowChange(
        key=key,
        change_type=ctype,
        old_row=old,
        new_row=new,
        changed_fields=fields,
    )


def _result(added=(), removed=(), modified=(), unchanged=()):
    return DiffResult(
        added=list(added),
        removed=list(removed),
        modified=list(modified),
        unchanged=list(unchanged),
    )


def test_pivot_accumulates_multiple_modified_rows():
    mods = [
        _rc(str(i), "modified", {"score": str(i)}, {"score": str(i + 1)}, ["score"])
        for i in range(5)
    ]
    result = _result(modified=mods)
    pivots = pivot_diff(result)
    assert pivots["score"].total_touches == 5
    assert len(pivots["score"].old_values) == 5


def test_top_changed_fields_returns_all_when_no_cap():
    result = _result(
        added=[_rc("1", "added", {}, {"a": "1", "b": "2", "c": "3"}, [])]
    )
    ranked = top_changed_fields(result)
    assert len(ranked) == 3


def test_mixed_changes_field_touches_summed_correctly():
    result = _result(
        added=[_rc("1", "added", {}, {"col": "v1"}, [])],
        removed=[_rc("2", "removed", {"col": "v2"}, {}, [])],
        modified=[_rc("3", "modified", {"col": "v3"}, {"col": "v4"}, ["col"])],
    )
    pivots = pivot_diff(result)
    assert pivots["col"].total_touches == 3


def test_unchanged_rows_do_not_appear_in_pivot():
    result = _result(
        unchanged=[_rc("9", "unchanged", {"z": "same"}, {"z": "same"}, [])]
    )
    pivots = pivot_diff(result)
    assert pivots == {}
