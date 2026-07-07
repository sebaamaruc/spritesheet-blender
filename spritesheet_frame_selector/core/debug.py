"""Shared opt-in debug logging for selector/playback/preview instrumentation."""

from __future__ import annotations

import os

DEBUG_ENV_VAR = "SFS_SELECTOR_PLAYBACK_DEBUG"
DEBUG_LOG_PREFIX = "[spritesheet-selector-playback]"

debug_enabled_override = False


def debug_enabled() -> bool:
    return bool(debug_enabled_override or os.environ.get(DEBUG_ENV_VAR))


def debug_log(message: str, exc: Exception | None = None) -> None:
    if not debug_enabled():
        return
    if exc is None:
        print(f"{DEBUG_LOG_PREFIX} {message}")
    else:
        print(f"{DEBUG_LOG_PREFIX} {message}: {exc!r}")
