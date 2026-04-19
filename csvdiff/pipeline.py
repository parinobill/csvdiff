"""Compose filter, sort, truncate, and paginate steps into a single pipeline."""

from dataclasses import dataclass, field
from typing import Optional, List

from csvdiff.differ import DiffResult
from csvdiff.filter import filter_columns, filter_rows
from csvdiff.sorter import sort_changes
from csvdiff.truncator import truncate_diff
from csvdiff.pager import Page


@dataclass
class PipelineOptions:
    include_columns: Optional[List[str]] = None
    exclude_columns: Optional[List[str]] = None
    row_filter: Optional[str] = None
    sort_by: Optional[str] = None
    sort_ascending: bool = True
    max_value_len: Optional[int] = None
    page: Optional[int] = None
    page_size: int = 50


def run_pipeline(result: DiffResult, opts: PipelineOptions) -> DiffResult:
    """Apply transformation steps to a DiffResult in order."""
    if opts.include_columns or opts.exclude_columns:
        result = filter_columns(
            result,
            include=opts.include_columns,
            exclude=opts.exclude_columns,
        )

    if opts.row_filter:
        result = filter_rows(result, opts.row_filter)

    if opts.sort_by:
        result = sort_changes(result, opts.sort_by, ascending=opts.sort_ascending)

    if opts.max_value_len is not None:
        result = truncate_diff(result, max_len=opts.max_value_len)

    if opts.page is not None:
        page = Page(result.changes, page_size=opts.page_size)
        paged_changes = page.get_page(opts.page)
        result = DiffResult(changes=paged_changes)

    return result
