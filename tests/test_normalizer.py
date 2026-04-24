import pytest
from csvdiff.normalizer import (
    NormalizeOptions,
    normalize_row,
    normalize_rows,
    default_options,
    options_from_dict,
)


def _row(**kwargs):
    return {k: str(v) for k, v in kwargs.items()}


# ---------------------------------------------------------------------------
# normalize_row
# ---------------------------------------------------------------------------

def test_strip_whitespace_default():
    opts = default_options()
    row = _row(name="  Alice ", age=" 30")
    result = normalize_row(row, opts)
    assert result["name"] == "Alice"
    assert result["age"] == "30"


def test_no_strip_when_disabled():
    opts = NormalizeOptions(strip_whitespace=False)
    row = _row(name="  Alice ")
    result = normalize_row(row, opts)
    assert result["name"] == "  Alice "


def test_lowercase_option():
    opts = NormalizeOptions(lowercase=True)
    row = _row(name="Alice", city="New York")
    result = normalize_row(row, opts)
    assert result["name"] == "alice"
    assert result["city"] == "new york"


def test_collapse_whitespace():
    opts = NormalizeOptions(collapse_whitespace=True, strip_whitespace=False)
    row = _row(desc="hello   world\ttab")
    result = normalize_row(row, opts)
    assert result["desc"] == "hello world tab"


def test_value_map_replaces_value():
    opts = NormalizeOptions(value_map={"N/A": "", "null": ""})
    row = _row(score="N/A", label="null", name="Alice")
    result = normalize_row(row, opts)
    assert result["score"] == ""
    assert result["label"] == ""
    assert result["name"] == "Alice"


def test_columns_restriction_only_normalizes_listed():
    opts = NormalizeOptions(lowercase=True, columns=["name"])
    row = _row(name="Alice", city="London")
    result = normalize_row(row, opts)
    assert result["name"] == "alice"
    assert result["city"] == "London"  # untouched


def test_columns_none_normalizes_all():
    opts = NormalizeOptions(lowercase=True, columns=None)
    row = _row(name="Alice", city="London")
    result = normalize_row(row, opts)
    assert result["name"] == "alice"
    assert result["city"] == "london"


# ---------------------------------------------------------------------------
# normalize_rows
# ---------------------------------------------------------------------------

def test_normalize_rows_applies_to_all():
    opts = NormalizeOptions(strip_whitespace=True)
    rows = [_row(name=" Bob "), _row(name=" Carol ")]
    result = normalize_rows(rows, opts)
    assert result[0]["name"] == "Bob"
    assert result[1]["name"] == "Carol"


def test_normalize_rows_empty_list():
    opts = default_options()
    assert normalize_rows([], opts) == []


# ---------------------------------------------------------------------------
# options_from_dict
# ---------------------------------------------------------------------------

def test_options_from_dict_defaults():
    opts = options_from_dict({})
    assert opts.strip_whitespace is True
    assert opts.lowercase is False
    assert opts.collapse_whitespace is False
    assert opts.value_map == {}
    assert opts.columns is None


def test_options_from_dict_overrides():
    d = {
        "strip_whitespace": False,
        "lowercase": True,
        "value_map": {"N/A": ""},
        "columns": ["name", "status"],
    }
    opts = options_from_dict(d)
    assert opts.strip_whitespace is False
    assert opts.lowercase is True
    assert opts.value_map == {"N/A": ""}
    assert opts.columns == ["name", "status"]
