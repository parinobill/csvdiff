"""Tests for csvdiff.config."""
import json
import tempfile
from pathlib import Path

import pytest

from csvdiff.config import CsvDiffConfig, default_config, from_dict, load_config


def _write_config(data: dict) -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(data, tmp)
    tmp.close()
    return Path(tmp.name)


def test_default_config_values():
    cfg = default_config()
    assert cfg.key_column == "id"
    assert cfg.output_format == "text"
    assert cfg.color is True
    assert cfg.ignore.columns == []


def test_from_dict_sets_key_column():
    cfg = from_dict({"key_column": "uuid"})
    assert cfg.key_column == "uuid"


def test_from_dict_ignore_columns():
    cfg = from_dict({"ignore": {"columns": ["updated_at", "checksum"]}})
    assert "updated_at" in cfg.ignore.columns
    assert "checksum" in cfg.ignore.columns


def test_from_dict_ignore_change_types():
    cfg = from_dict({"ignore": {"change_types": ["added"]}})
    assert cfg.ignore.change_types == ["added"]


def test_from_dict_ignore_row_filter():
    cfg = from_dict({"ignore": {"row_filter": "^temp-"}})
    assert cfg.ignore.row_filter == "^temp-"


def test_from_dict_output_format():
    cfg = from_dict({"output_format": "json"})
    assert cfg.output_format == "json"


def test_load_config_from_file():
    path = _write_config({"key_column": "sku", "color": False})
    cfg = load_config(path)
    assert cfg.key_column == "sku"
    assert cfg.color is False


def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.json")


def test_load_config_invalid_json():
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    tmp.write("not valid json{{{")
    tmp.close()
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_config(tmp.name)
