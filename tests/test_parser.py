"""Tests for csvdiff.parser module."""

import os
import tempfile
import textwrap

import pytest

from csvdiff.parser import get_all_columns, read_csv


def write_temp_csv(content: str) -> str:
    """Write content to a temporary CSV file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
    f.write(textwrap.dedent(content))
    f.close()
    return f.name


class TestReadCsv:
    def test_basic_read(self):
        path = write_temp_csv("""
            id,name,age
            1,Alice,30
            2,Bob,25
        """)
        try:
            rows, fieldnames = read_csv(path, "id")
            assert fieldnames == ["id", "name", "age"]
            assert "1" in rows
            assert rows["1"]["name"] == "Alice"
            assert rows["2"]["age"] == "25"
        finally:
            os.unlink(path)

    def test_missing_key_column_raises(self):
        path = write_temp_csv("""
            id,name
            1,Alice
        """)
        try:
            with pytest.raises(KeyError, match="email"):
                read_csv(path, "email")
        finally:
            os.unlink(path)

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            read_csv("/nonexistent/path/file.csv", "id")

    def test_empty_csv_returns_empty(self):
        path = write_temp_csv("id,name\n")
        try:
            rows, fieldnames = read_csv(path, "id")
            assert rows == {}
            assert fieldnames == ["id", "name"]
        finally:
            os.unlink(path)


class TestGetAllColumns:
    def test_combines_unique_columns(self):
        result = get_all_columns(["id", "name"], ["id", "age"])
        assert result == ["id", "name", "age"]

    def test_preserves_order(self):
        result = get_all_columns(["a", "b", "c"], ["c", "d"])
        assert result == ["a", "b", "c", "d"]

    def test_identical_lists(self):
        result = get_all_columns(["x", "y"], ["x", "y"])
        assert result == ["x", "y"]
