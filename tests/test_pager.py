"""Tests for csvdiff.pager module."""

import pytest
from csvdiff.pager import paginate, all_pages, Page, DEFAULT_PAGE_SIZE


ITEMS = list(range(1, 26))  # 25 items


def test_first_page_items():
    page = paginate(ITEMS, page=1, page_size=10)
    assert page.items == list(range(1, 11))


def test_last_partial_page():
    page = paginate(ITEMS, page=3, page_size=10)
    assert page.items == list(range(21, 26))


def test_total_pages():
    page = paginate(ITEMS, page=1, page_size=10)
    assert page.total_pages == 3


def test_has_next_true():
    page = paginate(ITEMS, page=1, page_size=10)
    assert page.has_next is True


def test_has_next_false_on_last():
    page = paginate(ITEMS, page=3, page_size=10)
    assert page.has_next is False


def test_has_prev_false_on_first():
    page = paginate(ITEMS, page=1, page_size=10)
    assert page.has_prev is False


def test_has_prev_true():
    page = paginate(ITEMS, page=2, page_size=10)
    assert page.has_prev is True


def test_summary_line():
    page = paginate(ITEMS, page=2, page_size=10)
    assert "11-20" in page.summary_line()
    assert "25" in page.summary_line()
    assert "page 2/3" in page.summary_line()


def test_empty_items_summary():
    page = paginate([], page=1, page_size=10)
    assert page.summary_line() == "No changes to display."


def test_invalid_page_size_raises():
    with pytest.raises(ValueError, match="page_size"):
        paginate(ITEMS, page=1, page_size=0)


def test_invalid_page_raises():
    with pytest.raises(ValueError, match="page"):
        paginate(ITEMS, page=0, page_size=10)


def test_all_pages_count():
    pages = all_pages(ITEMS, page_size=10)
    assert len(pages) == 3


def test_all_pages_empty():
    pages = all_pages([], page_size=10)
    assert len(pages) == 1
    assert pages[0].items == []


def test_page_beyond_range_returns_empty():
    page = paginate(ITEMS, page=99, page_size=10)
    assert page.items == []
