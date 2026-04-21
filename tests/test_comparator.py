"""Tests for csvdiff.comparator."""

import pytest
from csvdiff.comparator import (
    CompareOptions,
    compare_rows,
    default_options,
    fields_equal,
)


# ---------------------------------------------------------------------------
# fields_equal
# ---------------------------------------------------------------------------

def test_equal_strings_returns_true():
    opts = default_options()
    assert fields_equal("name", "Alice", "Alice", opts) is True


def test_different_strings_returns_false():
    opts = default_options()
    assert fields_equal("name", "Alice", "Bob", opts) is False


def test_case_insensitive_match():
    opts = CompareOptions(case_sensitive=False)
    assert fields_equal("city", "London", "london", opts) is True


def test_case_sensitive_mismatch():
    opts = CompareOptions(case_sensitive=True)
    assert fields_equal("city", "London", "london", opts) is False


def test_strip_whitespace_matches():
    opts = CompareOptions(strip_whitespace=True)
    assert fields_equal("val", "  42  ", "42", opts) is True


def test_no_strip_whitespace_mismatch():
    opts = CompareOptions(strip_whitespace=False)
    assert fields_equal("val", "  42  ", "42", opts) is False


def test_numeric_tolerance_within_range():
    opts = CompareOptions(numeric_tolerance=0.01)
    assert fields_equal("price", "1.001", "1.009", opts) is True


def test_numeric_tolerance_outside_range():
    opts = CompareOptions(numeric_tolerance=0.01)
    assert fields_equal("price", "1.00", "1.02", opts) is False


def test_ignored_field_always_equal():
    opts = CompareOptions(ignore_fields=["checksum"])
    assert fields_equal("checksum", "abc", "xyz", opts) is True


def test_non_numeric_strings_not_compared_numerically():
    opts = CompareOptions(numeric_tolerance=1.0)
    assert fields_equal("tag", "alpha", "beta", opts) is False


# ---------------------------------------------------------------------------
# compare_rows
# ---------------------------------------------------------------------------

def test_compare_rows_no_diff():
    old = {"id": "1", "name": "Alice", "age": "30"}
    new = {"id": "1", "name": "Alice", "age": "30"}
    result = compare_rows("id", old, new, default_options())
    assert result == {}


def test_compare_rows_detects_change():
    old = {"id": "1", "name": "Alice", "age": "30"}
    new = {"id": "1", "name": "Alice", "age": "31"}
    result = compare_rows("id", old, new, default_options())
    assert result == {"age": ("30", "31")}


def test_compare_rows_skips_key_field():
    old = {"id": "1", "val": "x"}
    new = {"id": "2", "val": "x"}
    result = compare_rows("id", old, new, default_options())
    assert "id" not in result


def test_compare_rows_missing_field_treated_as_empty():
    old = {"id": "1", "score": "10"}
    new = {"id": "1"}
    result = compare_rows("id", old, new, default_options())
    assert result == {"score": ("10", "")}


def test_compare_rows_respects_ignore_fields():
    opts = CompareOptions(ignore_fields=["ts"])
    old = {"id": "1", "ts": "2024-01-01", "val": "a"}
    new = {"id": "1", "ts": "2024-06-01", "val": "a"}
    result = compare_rows("id", old, new, opts)
    assert "ts" not in result
    assert result == {}
