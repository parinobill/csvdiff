"""Pipeline: orchestrate filter → diff → annotate → sort → paginate."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, compute_diff
from csvdiff.filter import filter_columns, filter_rows
from csvdiff.sorter import sort_changes
from csvdiff.pager import Page
from csvdiff.annotator import AnnotatedChange, annotate_changes


@dataclass
class PipelineOptions:
    key_column: str
    include_columns: Optional[List[str]] = None
    exclude_columns: Optional[List[str]] = None
    row_filter: Optional[str] = None
    sort_field: str = "key"
    sort_asc: bool = True
    page: int = 1
    page_size: int = 50
    annotate: bool = False
    index_map: Optional[Dict[str, int]] = field(default=None)


def run_pipeline(
    old_rows: List[dict],
    new_rows: List[dict],
    options: PipelineOptions,
) -> dict:
    """Run the full diff pipeline and return a result dict."""
    if options.include_columns or options.exclude_columns:
        old_rows = filter_columns(
            old_rows, options.include_columns, options.exclude_columns
        )
        new_rows = filter_columns(
            new_rows, options.include_columns, options.exclude_columns
        )

    if options.row_filter:
        old_rows = filter_rows(old_rows, options.row_filter)
        new_rows = filter_rows(new_rows, options.row_filter)

    result: DiffResult = compute_diff(old_rows, new_rows, options.key_column)

    result = sort_changes(result, options.sort_field, options.sort_asc)

    paged: Page = Page(result.changes, options.page_size, options.page)

    annotations: Optional[List[AnnotatedChange]] = None
    if options.annotate:
        sub = DiffResult(changes=paged.items)
        annotations = annotate_changes(sub, options.key_column, options.index_map)

    return {
        "result": result,
        "page": paged,
        "annotations": annotations,
    }
