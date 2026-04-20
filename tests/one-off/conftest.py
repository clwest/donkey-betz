"""
Pytest collection guard for tests/one-off/.

The files in this directory are legacy ad-hoc scripts (not real pytest tests)
that were moved here from the repo root during Cleanup Phase 2 (2026-04-20).
They are preserved for historical reference per DO 11 (archive, never delete)
but are NOT part of the active test suite.

This conftest.py tells pytest to skip collection of .py files in this
directory, so `python -m pytest` still cleanly collects only the real test
suite under tests/ (excluding this one-off archive).

See docs/cleanup/PHASE_2_EXECUTION_LOG.md for full context.
"""

collect_ignore_glob = ["test_*.py"]
