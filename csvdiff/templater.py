"""Template-based report rendering for csvdiff output."""

from __future__ import annotations

from string import Template
from typing import Dict, Optional

from csvdiff.differ import DiffResult
from csvdiff.stats import compute_stats

_DEFAULT_TEXT_TEMPLATE = """\
Diff Summary: $file_a vs $file_b
==========================================
Added rows   : $added
Removed rows : $removed
Modified rows: $modified
Unchanged    : $unchanged
Total rows   : $total
==========================================
$change_lines"""

_DEFAULT_HTML_TEMPLATE = """\
<html><body>
<h2>Diff: $file_a vs $file_b</h2>
<table border="1">
  <tr><th>Type</th><th>Count</th></tr>
  <tr><td>Added</td><td>$added</td></tr>
  <tr><td>Removed</td><td>$removed</td></tr>
  <tr><td>Modified</td><td>$modified</td></tr>
  <tr><td>Unchanged</td><td>$unchanged</td></tr>
  <tr><td>Total</td><td>$total</td></tr>
</table>
<pre>$change_lines</pre>
</body></html>"""


def _build_change_lines(result: DiffResult) -> str:
    lines = []
    for change in result.changes:
        lines.append(str(change))
    return "\n".join(lines) if lines else "(no changes)"


def render_template(
    result: DiffResult,
    file_a: str = "file_a",
    file_b: str = "file_b",
    template_str: Optional[str] = None,
    fmt: str = "text",
) -> str:
    """Render a DiffResult using a string template.

    Args:
        result: the diff result to render.
        file_a: label for the first file.
        file_b: label for the second file.
        template_str: custom Template string; if None, a built-in is used.
        fmt: 'text' or 'html' selects the built-in template when template_str is None.

    Returns:
        Rendered string.
    """
    stats = compute_stats(result)
    d = stats.as_dict()

    mapping: Dict[str, str] = {
        "file_a": file_a,
        "file_b": file_b,
        "added": str(d["added"]),
        "removed": str(d["removed"]),
        "modified": str(d["modified"]),
        "unchanged": str(d["unchanged"]),
        "total": str(d["total"]),
        "change_lines": _build_change_lines(result),
    }

    if template_str is None:
        template_str = _DEFAULT_HTML_TEMPLATE if fmt == "html" else _DEFAULT_TEXT_TEMPLATE

    return Template(template_str).safe_substitute(mapping)


def list_builtin_formats() -> list[str]:
    """Return names of built-in template formats."""
    return ["text", "html"]
