"""Pagination support for large diff outputs."""

from typing import List, Optional


DEFAULT_PAGE_SIZE = 20


class Page:
    def __init__(self, items: list, page: int, page_size: int, total: int):
        self.items = items
        self.page = page
        self.page_size = page_size
        self.total = total

    @property
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 1
        return max(1, (self.total + self.page_size - 1) // self.page_size)

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    def summary_line(self) -> str:
        start = (self.page - 1) * self.page_size + 1
        end = min(self.page * self.page_size, self.total)
        if self.total == 0:
            return "No changes to display."
        return f"Showing {start}-{end} of {self.total} change(s) (page {self.page}/{self.total_pages})"


def paginate(items: list, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
    """Return a Page slice of items."""
    if page_size <= 0:
        raise ValueError("page_size must be a positive integer")
    if page < 1:
        raise ValueError("page must be >= 1")
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return Page(items[start:end], page=page, page_size=page_size, total=total)


def all_pages(items: list, page_size: int = DEFAULT_PAGE_SIZE) -> List[Page]:
    """Yield all pages for the given items list."""
    if not items:
        return [Page([], 1, page_size, 0)]
    total_pages = max(1, (len(items) + page_size - 1) // page_size)
    return [paginate(items, page=p, page_size=page_size) for p in range(1, total_pages + 1)]
