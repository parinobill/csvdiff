"""Tests for csvdiff.filter module."""
import pytest
from csvdiff.filter import filter_columns, filter_rows, select_columns

SAMPLE = [
    {"id": "1", "name": "Alice", "age": "30"},
    {"id": "2", "name": "Bob", "age": "25"},
    {"id": "3", "name": "Carol", "age": "35"},
]


def test_filter_columns_include():
    result = filter_columns(SAMPLE, include=["id", "name"])
    assert result == [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Carol"},
    ]


def test_filter_columns_exclude():
    result = filter_columns(SAMPLE, exclude=["age"])
    assert all("age" not in row for row in result)
    assert all("id" in row and "name" in row for row in result)


def test_filter_columns_both_raises():
    with pytest.raises(ValueError):
        filter_columns(SAMPLE, include=["id"], exclude=["age"])


def test_filter_columns_none_returns_original():
    result = filter_columns(SAMPLE)
    assert result == SAMPLE


def test_filter_rows_match():
    result = filter_rows(SAMPLE, "name", "Bob")
    assert len(result) == 1
    assert result[0]["id"] == "2"


def test_filter_rows_no_match():
    result = filter_rows(SAMPLE, "name", "Zara")
    assert result == []


def test_filter_rows_bad_column():
    with pytest.raises(KeyError):
        filter_rows(SAMPLE, "nonexistent", "value")


def test_filter_rows_empty():
    assert filter_rows([], "id", "1") == []


def test_select_columns_reorders():
    result = select_columns(SAMPLE, ["name", "id"])
    assert list(result[0].keys()) == ["name", "id"]


def test_select_columns_missing_filled():
    result = select_columns(SAMPLE, ["id", "email"])
    assert result[0]["email"] == ""
