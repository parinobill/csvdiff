"""Tests for csvdiff.differ_forecast."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from csvdiff.differ_forecast import (
    ForecastPoint,
    ForecastResult,
    _linear_trend,
    forecast_from_ledger,
)


def _entry(added: int, removed: int, modified: int) -> MagicMock:
    e = MagicMock()
    e.added = added
    e.removed = removed
    e.modified = modified
    return e


# ---------------------------------------------------------------------------
# _linear_trend
# ---------------------------------------------------------------------------

def test_linear_trend_empty_returns_zero():
    assert _linear_trend([]) == 0.0


def test_linear_trend_single_returns_zero():
    assert _linear_trend([5.0]) == 0.0


def test_linear_trend_constant_series():
    assert _linear_trend([3.0, 3.0, 3.0]) == 0.0


def test_linear_trend_increasing():
    assert _linear_trend([1.0, 3.0, 5.0]) == pytest.approx(2.0)


def test_linear_trend_decreasing():
    assert _linear_trend([10.0, 7.0, 4.0]) == pytest.approx(-3.0)


# ---------------------------------------------------------------------------
# forecast_from_ledger
# ---------------------------------------------------------------------------

def test_forecast_empty_entries_returns_empty():
    result = forecast_from_ledger([])
    assert result.points == []
    assert result.trend_added == 0.0


def test_forecast_produces_correct_step_count():
    entries = [_entry(2, 1, 3), _entry(4, 2, 5)]
    result = forecast_from_ledger(entries, steps=4)
    assert len(result.points) == 4


def test_forecast_run_indices_are_sequential():
    entries = [_entry(1, 0, 0), _entry(2, 0, 0), _entry(3, 0, 0)]
    result = forecast_from_ledger(entries, steps=2)
    assert [p.run_index for p in result.points] == [4, 5]


def test_forecast_predictions_non_negative():
    # Strongly decreasing series should clamp at zero
    entries = [_entry(100, 0, 0), _entry(50, 0, 0), _entry(1, 0, 0)]
    result = forecast_from_ledger(entries, steps=5)
    for p in result.points:
        assert p.predicted_added >= 0.0
        assert p.predicted_removed >= 0.0
        assert p.predicted_modified >= 0.0


def test_forecast_trend_stored_on_result():
    entries = [_entry(2, 4, 6), _entry(4, 6, 9)]
    result = forecast_from_ledger(entries, steps=1)
    assert result.trend_added == pytest.approx(2.0)
    assert result.trend_removed == pytest.approx(2.0)
    assert result.trend_modified == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# ForecastPoint helpers
# ---------------------------------------------------------------------------

def test_forecast_point_total():
    p = ForecastPoint(run_index=1, predicted_added=2.0, predicted_removed=3.0, predicted_modified=5.0)
    assert p.predicted_total == pytest.approx(10.0)


def test_forecast_point_str_contains_run_index():
    p = ForecastPoint(run_index=7, predicted_added=1.0, predicted_removed=0.0, predicted_modified=2.0)
    assert "7" in str(p)


# ---------------------------------------------------------------------------
# ForecastResult.summary
# ---------------------------------------------------------------------------

def test_forecast_result_summary_contains_steps():
    entries = [_entry(1, 1, 1), _entry(2, 2, 2)]
    result = forecast_from_ledger(entries, steps=2)
    summary = result.summary()
    assert "2 step" in summary
    assert "Trend" in summary
