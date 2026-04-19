"""CLI integration for --watch mode."""

import sys
from typing import List, Optional

from csvdiff.pipeline import PipelineOptions, run_pipeline
from csvdiff.watcher import WatchOptions, watch


def _run_diff(path_a: str, path_b: str, opts: PipelineOptions) -> None:
    """Run a single diff and print output."""
    result = run_pipeline(path_a, path_b, opts)
    from csvdiff.reporter import render_report
    print(render_report(result, fmt=opts.output_format if hasattr(opts, 'output_format') else 'text'))


def watch_command(
    path_a: str,
    path_b: str,
    pipeline_opts: PipelineOptions,
    interval: float = 1.0,
    max_polls: Optional[int] = None,
) -> None:
    """Start watch mode: re-run diff whenever either file changes."""
    print(f"Watching {path_a} and {path_b} for changes (interval={interval}s) ...",
          file=sys.stderr)

    # Run once immediately
    _run_diff(path_a, path_b, pipeline_opts)

    def on_change(a: str, b: str) -> None:
        print("--- change detected ---", file=sys.stderr)
        _run_diff(a, b, pipeline_opts)

    watch_opts = WatchOptions(interval=interval, max_polls=max_polls)
    try:
        watch(path_a, path_b, on_change, watch_opts)
    except KeyboardInterrupt:
        print("\nWatch stopped.", file=sys.stderr)


def add_watch_args(parser) -> None:
    """Attach --watch related arguments to an argparse parser."""
    parser.add_argument(
        "--watch",
        action="store_true",
        default=False,
        help="Re-run diff whenever either input file changes.",
    )
    parser.add_argument(
        "--watch-interval",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="Polling interval in seconds for --watch mode (default: 1.0).",
    )
