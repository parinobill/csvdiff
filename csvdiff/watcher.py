"""Watch CSV files for changes and trigger diffs automatically."""

import os
import time
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class WatchOptions:
    interval: float = 1.0
    max_polls: Optional[int] = None


@dataclass
class FileSnapshot:
    path: str
    mtime: float
    size: int

    @staticmethod
    def take(path: str) -> "FileSnapshot":
        stat = os.stat(path)
        return FileSnapshot(path=path, mtime=stat.st_mtime, size=stat.st_size)

    def has_changed(self, other: "FileSnapshot") -> bool:
        return self.mtime != other.mtime or self.size != other.size


def watch(
    path_a: str,
    path_b: str,
    on_change: Callable[[str, str], None],
    options: Optional[WatchOptions] = None,
) -> int:
    """Poll path_a and path_b; call on_change when either file changes.

    Returns the number of change events fired.
    """
    opts = options or WatchOptions()
    snapshots = {
        path_a: FileSnapshot.take(path_a),
        path_b: FileSnapshot.take(path_b),
    }
    polls = 0
    events = 0

    while True:
        time.sleep(opts.interval)
        polls += 1
        changed = False
        for path in (path_a, path_b):
            current = FileSnapshot.take(path)
            if current.has_changed(snapshots[path]):
                snapshots[path] = current
                changed = True
        if changed:
            on_change(path_a, path_b)
            events += 1
        if opts.max_polls is not None and polls >= opts.max_polls:
            break

    return events
