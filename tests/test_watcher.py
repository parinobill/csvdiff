"""Tests for csvdiff.watcher."""

import os
import tempfile
import time
import pytest

from csvdiff.watcher import FileSnapshot, WatchOptions, watch


def _write(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


def test_snapshot_take():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("a,b\n1,2\n")
        path = f.name
    try:
        snap = FileSnapshot.take(path)
        assert snap.path == path
        assert snap.size > 0
    finally:
        os.unlink(path)


def test_snapshot_unchanged():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("a,b\n")
        path = f.name
    try:
        s1 = FileSnapshot.take(path)
        s2 = FileSnapshot.take(path)
        assert not s1.has_changed(s2)
    finally:
        os.unlink(path)


def test_snapshot_detects_size_change():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("a\n")
        path = f.name
    try:
        s1 = FileSnapshot.take(path)
        _write(path, "a,b,c\n1,2,3\n")
        s2 = FileSnapshot.take(path)
        assert s2.has_changed(s1)
    finally:
        os.unlink(path)


def test_watch_fires_on_change():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as fa:
        fa.write("id,val\n1,a\n")
        path_a = fa.name
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as fb:
        fb.write("id,val\n1,a\n")
        path_b = fb.name
    try:
        calls = []

        def on_change(a, b):
            calls.append((a, b))

        # Schedule a write after first poll
        import threading

        def delayed_write():
            time.sleep(0.05)
            _write(path_b, "id,val\n1,b\n")

        t = threading.Thread(target=delayed_write)
        t.start()
        opts = WatchOptions(interval=0.02, max_polls=10)
        events = watch(path_a, path_b, on_change, opts)
        t.join()
        assert events >= 1
        assert calls[0] == (path_a, path_b)
    finally:
        os.unlink(path_a)
        os.unlink(path_b)


def test_watch_no_change_no_event():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as fa:
        fa.write("id\n1\n")
        path_a = fa.name
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as fb:
        fb.write("id\n1\n")
        path_b = fb.name
    try:
        calls = []
        opts = WatchOptions(interval=0.01, max_polls=3)
        events = watch(path_a, path_b, lambda a, b: calls.append(1), opts)
        assert events == 0
        assert calls == []
    finally:
        os.unlink(path_a)
        os.unlink(path_b)
