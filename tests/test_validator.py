"""Tests for csvdiff.validator."""

import pytest
from csvdiff.validator import (
    ValidationError,
    ValidationResult,
    validate_key_column,
    validate_columns_exist,
    validate_diff_inputs,
)


def test_valid_key_column():
    result = validate_key_column("id", ["id", "name", "age"])
    assert result.is_valid


def test_missing_key_column():
    result = validate_key_column("missing", ["id", "name"])
    assert not result.is_valid
    assert any("missing" in str(e) for e in result.errors)


def test_empty_key_column():
    result = validate_key_column("", ["id", "name"])
    assert not result.is_valid
    assert result.errors[0].field == "key"


def test_validate_columns_exist_all_present():
    result = validate_columns_exist(["id", "name"], ["id", "name", "age"])
    assert result.is_valid


def test_validate_columns_exist_some_missing():
    result = validate_columns_exist(["id", "ghost"], ["id", "name"])
    assert not result.is_valid
    assert "ghost" in str(result.errors[0])


def test_validate_diff_inputs_valid():
    cols = ["id", "name", "age"]
    result = validate_diff_inputs("id", cols, cols)
    assert result.is_valid


def test_validate_diff_inputs_column_mismatch():
    result = validate_diff_inputs("id", ["id", "name"], ["id", "age"])
    assert not result.is_valid
    assert any(e.field == "columns" for e in result.errors)


def test_validate_diff_inputs_with_include_columns():
    cols = ["id", "name", "age"]
    result = validate_diff_inputs("id", cols, cols, include_columns=["name"])
    assert result.is_valid


def test_validate_diff_inputs_bad_include_columns():
    cols = ["id", "name"]
    result = validate_diff_inputs("id", cols, cols, include_columns=["nonexistent"])
    assert not result.is_valid


def test_validation_result_str_ok():
    result = ValidationResult()
    assert str(result) == "OK"


def test_validation_result_str_errors():
    result = ValidationResult()
    result.add_error("key", "bad key")
    assert "key" in str(result)
    assert "bad key" in str(result)


def test_validation_error_str():
    err = ValidationError(field="col", message="not found")
    assert "col" in str(err)
    assert "not found" in str(err)
