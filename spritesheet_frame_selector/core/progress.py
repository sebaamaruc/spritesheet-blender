"""Small wrappers around Blender window manager progress reporting."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator


class ProgressReporter:
    def __init__(self, window_manager: Any, total: int):
        self._window_manager = window_manager
        self._total = max(1, int(total))
        self._current = 0

    def step(self, amount: int = 1) -> None:
        self._current = min(self._total, self._current + max(0, amount))
        update = getattr(self._window_manager, "progress_update", None)
        if update is not None:
            update(self._current)


@contextmanager
def progress_scope(context: Any, total: int) -> Iterator[ProgressReporter]:
    window_manager = getattr(context, "window_manager", None)
    begin = getattr(window_manager, "progress_begin", None)
    end = getattr(window_manager, "progress_end", None)
    reporter = ProgressReporter(window_manager, total)
    if begin is not None:
        begin(0, reporter._total)
    try:
        yield reporter
    finally:
        if end is not None:
            end()
