# `tests/one-off/` — Archived Legacy Test Scripts

**Status:** archival. NOT part of the active test suite.

## What's in here

89 Python scripts moved here from the repo root during **Cleanup Phase 2** (2026-04-20). They have the `test_` prefix but are **not real pytest tests**. They're ad-hoc scripts that were run manually during specific build sessions (many have session numbers in their names — `test_session_143_*.py`, `test_session_128_*.py`, etc.) and got committed.

## Why they're preserved

Per `docs/docs-pattern/06_dos_and_donts.md` **DO 11**: archive, never delete. These scripts are part of the build history and may have retrospective / white-paper value.

## Why they're NOT collected by pytest

- Most call `django.setup()` at module level — would fail pytest collection.
- They aren't structured as pytest tests (no fixtures, no `def test_*` functions in most cases, no `assert` patterns — often just `print()` + `if __name__ == '__main__'` blocks).
- `pytest.ini` has `testpaths = tests` which already excluded the root versions from collection before the move.

The `conftest.py` in this directory sets `collect_ignore_glob = ["test_*.py"]` so `python -m pytest` still finds exactly the real test suite (766 tests as of 2026-04-20) without getting polluted by these archives.

## How to run one of these scripts manually

They are meant to be run directly with Python, not pytest:

```bash
python tests/one-off/test_agent_learning.py
python tests/one-off/test_pa_readonly_tools.py
```

Most require a running local Django + Celery stack. Many will fail without specific environment setup. If a script fails, check its docstring / opening comments for the prerequisites.

## Security note ⚠

Two files in this directory contain hardcoded auth tokens for the Railway production API:

- `test_pa_readonly_tools.py` (line 11)
- `test_pa_mutation_tools.py` (line 14)

Both embed `TOKEN = '43d4612...'`. This token has been in git history since the files were committed. **Rotate it** rather than trust that moving the files reduces exposure — the git history is the authoritative record.

## Related

- `docs/cleanup/ROOT_CLEANUP_PLAN.md` — the phased cleanup plan
- `docs/cleanup/PHASE_2_EXECUTION_LOG.md` — the execution log for this phase
