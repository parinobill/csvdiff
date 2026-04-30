"""Integration tests: WatchReport behaviour across multiple realistic cycles."""
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_watch_report import build_watch_report


def _rc(key, change_type, old=None, new=None):
    return RowChange(
        key=key,
        change_type=change_type,
        old_row=old or {},
        new_row=new or {},
    )


def _result(*changes):
    return DiffResult(changes=list(changes), unchanged_count=0)


def test_rolling_totals_accumulate_correctly():
    report = build_watch_report()
    report.record(_result(_rc("1", "added", new={"id": "1"})))
    report.record(
        _result(
            _rc("2", "added", new={"id": "2"}),
            _rc("3", "removed", old={"id": "3"}),
        )
    )
    report.record(_result(_rc("4", "modified", old={"v": "a"}, new={"v": "b"})))
    total = sum(e.stats.changed for e in report.entries)
    assert total == 4


def test_trend_sequence_across_three_cycles():
    report = build_watch_report()
    report.record(_result(_rc("1", "added", new={"id": "1"})))
    report.record(
        _result(
            _rc("2", "added", new={"id": "2"}),
            _rc("3", "added", new={"id": "3"}),
        )
    )
    report.record(_result())  # no changes
    trends = [
        report.entries[i].trend_vs(report.entries[i - 1] if i > 0 else None)
        for i in range(3)
    ]
    assert trends[0] == "~"
    assert trends[1].startswith("+")
    assert trends[2].startswith("-")


def test_summary_total_line_present():
    report = build_watch_report()
    for i in range(4):
        report.record(_result(_rc(str(i), "added", new={"id": str(i)})))
    s = report.summary()
    assert "Total changes across all cycles: 4" in s


def test_label_stored_on_entry():
    report = build_watch_report()
    entry = report.record(_result(), label="run-abc")
    assert entry.label == "run-abc"
