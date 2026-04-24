"""Tests for csvdiff.tagger."""

import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.tagger import (
    TagRule,
    TaggedChange,
    apply_tags,
    group_by_tag,
    tag_summary,
)


def _added(key: str) -> RowChange:
    return RowChange(key=key, change_type="added", old_row=None, new_row={"id": key})


def _removed(key: str) -> RowChange:
    return RowChange(key=key, change_type="removed", old_row={"id": key}, new_row=None)


def _modified(key: str, field: str = "name", old: str = "a", new: str = "b") -> RowChange:
    return RowChange(
        key=key,
        change_type="modified",
        old_row={"id": key, field: old},
        new_row={"id": key, field: new},
        field_diffs={field: (old, new)},
    )


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes), unchanged_count=0)


# --- TagRule.matches ---

def test_rule_matches_by_change_type():
    rule = TagRule(tag="new", change_type="added")
    assert rule.matches(_added("1"))
    assert not rule.matches(_removed("1"))


def test_rule_matches_any_type_when_none():
    rule = TagRule(tag="any")
    assert rule.matches(_added("1"))
    assert rule.matches(_removed("1"))
    assert rule.matches(_modified("1"))


def test_rule_matches_field_name_on_modified():
    rule = TagRule(tag="name-change", change_type="modified", field_name="name")
    assert rule.matches(_modified("1", field="name"))
    assert not rule.matches(_modified("1", field="email"))


def test_rule_field_name_on_non_modified_returns_false():
    rule = TagRule(tag="x", field_name="name")
    assert not rule.matches(_added("1"))


def test_rule_matches_field_value_substring():
    rule = TagRule(tag="old-val", change_type="modified", field_name="name", field_value="Alice")
    assert rule.matches(_modified("1", field="name", old="Alice", new="Bob"))
    assert not rule.matches(_modified("1", field="name", old="Charlie", new="Dave"))


# --- apply_tags ---

def test_apply_tags_no_rules():
    result = _result(_added("1"), _removed("2"))
    tagged = apply_tags(result, [])
    assert len(tagged) == 2
    assert all(tc.tags == [] for tc in tagged)


def test_apply_tags_assigns_matching_tag():
    rules = [TagRule(tag="added", change_type="added")]
    result = _result(_added("1"), _removed("2"))
    tagged = apply_tags(result, rules)
    assert tagged[0].tags == ["added"]
    assert tagged[1].tags == []


def test_apply_tags_multiple_tags_per_change():
    rules = [
        TagRule(tag="changed", change_type="modified"),
        TagRule(tag="name-field", change_type="modified", field_name="name"),
    ]
    result = _result(_modified("1", field="name"))
    tagged = apply_tags(result, rules)
    assert set(tagged[0].tags) == {"changed", "name-field"}


# --- group_by_tag ---

def test_group_by_tag_separates_untagged():
    tc1 = TaggedChange(change=_added("1"), tags=["new"])
    tc2 = TaggedChange(change=_removed("2"), tags=[])
    groups = group_by_tag([tc1, tc2])
    assert "new" in groups
    assert "" in groups
    assert groups["new"] == [tc1]
    assert groups[""] == [tc2]


def test_group_by_tag_empty_input():
    assert group_by_tag([]) == {}


# --- tag_summary ---

def test_tag_summary_no_changes():
    assert tag_summary([]) == "No changes to tag."


def test_tag_summary_shows_counts():
    tc1 = TaggedChange(change=_added("1"), tags=["new"])
    tc2 = TaggedChange(change=_added("2"), tags=["new"])
    tc3 = TaggedChange(change=_removed("3"), tags=[])
    summary = tag_summary([tc1, tc2, tc3])
    assert "new: 2" in summary
    assert "(untagged): 1" in summary
    assert "3 change(s)" in summary
