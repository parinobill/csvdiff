"""Tests for csvdiff.patch_io."""
import json
import pytest
from pathlib import Path
from csvdiff.differ_patch import Patch
from csvdiff.patch_io import save_patch, load_patch, patch_summary


@pytest.fixture
def tmp(tmp_path):
    return tmp_path


def _sample_patch():
    return Patch(
        key_column="id",
        additions=[{"id": "5", "name": "Eve"}],
        removals=["3"],
        modifications=[{"key": "1", "fields": {"age": {"old": "30", "new": "31"}}}],
    )


def test_save_creates_file(tmp):
    p = tmp / "patch.json"
    save_patch(_sample_patch(), p)
    assert p.exists()


def test_save_valid_json(tmp):
    p = tmp / "patch.json"
    save_patch(_sample_patch(), p)
    data = json.loads(p.read_text())
    assert data["key_column"] == "id"


def test_load_roundtrip(tmp):
    p = tmp / "patch.json"
    original = _sample_patch()
    save_patch(original, p)
    loaded = load_patch(p)
    assert loaded.key_column == original.key_column
    assert loaded.removals == original.removals
    assert loaded.additions == original.additions


def test_load_missing_file_raises(tmp):
    with pytest.raises(FileNotFoundError):
        load_patch(tmp / "nonexistent.json")


def test_patch_summary_format():
    patch = _sample_patch()
    summary = patch_summary(patch)
    assert "id" in summary
    assert "1" in summary  # additions count
    assert "1" in summary  # removals count
