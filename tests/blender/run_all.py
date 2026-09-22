"""Entry point for the Blender-in-process integration suite.

Usage:
    blender -b --factory-startup --python tests/blender/run_all.py -- [pattern]

Exits non-zero when a test fails so CI/scripts can gate on it.
"""

from __future__ import annotations

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import it_common  # noqa: F401  (inserts repo root into sys.path)

import spritesheet_frame_selector as addon


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    pattern = argv[0] if argv else "it_*.py"

    addon.register()
    try:
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir=HERE, pattern=pattern, top_level_dir=HERE)
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)
    finally:
        try:
            addon.unregister()
        except Exception as exc:  # pragma: no cover - teardown diagnostics only
            print(f"WARNING: unregister failed: {exc!r}")

    print(f"\nSUITE_RESULT run={result.testsRun} "
          f"failures={len(result.failures)} errors={len(result.errors)} "
          f"skipped={len(result.skipped)}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
