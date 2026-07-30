# `repo_tool` — Validation Report

**Tool:** `repo_tool` — read-only codebase introspection (4 actions: `tree`, `read_file`, `search`, `git_info`).
**Schema:** `core/services/pa_tool_schemas.py:3621-3649`.
**Register site:** `core/services/tool_dispatcher.py:524`.
**Main handler:** `core/services/td_handlers_gateway.py:82-260` (`_handle_repo`).
**Downstream:** stdlib `os`, `os.walk`, `subprocess.run` (grep + git), file I/O.
**Session validated:** S2728 → S2729 (Batch B tool 2 of 5).
**HEAD at validation:** `5ce56b5f` + Batch B tool 1 uncommitted patches.
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred (regression tests suffice).
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch B tool 2 of 5). Trace + 3 patches (F-RT-2, F-RT-5, F-RT-11) + 15 regression tests complete (repo_tool's first regression test file at HEAD). 85 tests total pass across all validation-2728 files.

---

## 1. Intended purpose (per schema description)

*"Read-only codebase introspection: browse file tree, read file contents, search/grep across code, and check git status/log. Use this when you need to answer questions about what code exists, how features are implemented, file structure, or recent commits. Cannot modify files — read-only access only."*

## Covered actions

All 5 schema actions covered. Read-only — no mutation surface.

- `tree` — read — recursive file-tree walk under `path` (default project root). Optional `depth` (default 2, max 4). Applies `BLOCKED_DIRS` filter. Capped entry count.
- `read_file` — read — file content read. Required: `path`. Optional: `start_line`, `max_lines` (default 200, max 500). Applies `BLOCKED_FILES` filter (env / credentials / git objects).
- `search` — read — ripgrep-style grep across code via `subprocess.run`. Required: `query`. Optional: `file_type` (extension filter). Results capped at hard-max (per-file + total).
- `git_info` — read — `git log` / `git status` / `git diff` snapshot via `subprocess.run`.
- `list_repos` — read — enumerates repos under workspace root (added post-S2728).

## 2. Rigby's belief (per schema)

Rigby uses `repo_tool` to answer factual "what does this codebase contain / where is X implemented / what's in the git log" questions. Absent MEMORY rule specifically citing repo_tool — no crystallized failures on record. Adjacent MEMORY rule `feedback_verify_before_deleting_dead_code` implicitly relies on `search` action to grep for callers before proposing deletions.

## 3. Schema claim (verbatim capture)

- **Required:** `action` (enum: `tree`, `read_file`, `search`, `git_info`).
- **Optional:** `path`, `depth` (default 2, max 4), `query`, `start_line`, `max_lines` (default 200, max 500), `file_type`.

## 4. Handler behavior (traced)

### 4.1 Entry (line 82-108)

- Line 87: `action = payload.get('action', 'tree')` — **default `'tree'`** despite schema `required` (**F-RT-1**, batch-close class).
- Line 88: `project_root` computed relative to file location (3 levels up from `core/services/td_handlers_gateway.py`).
- Line 91-92: `BLOCKED_FILES` + `BLOCKED_DIRS` hardcoded (env files + credentials + git objects + node_modules + .venv + __pycache__).
- Line 94-107: `_safe_path` guard — normalizes + validates within project_root; raises `ValueError` for out-of-root or blocked-file/dir requests. **Security invariant enforced.**

### 4.2 Action: `tree` (line 110-137)

- Line 112: `depth = min(payload.get('depth', 2), 4)` — schema default 2, cap 4. Cap applied silently — no signal in response when caller requested > 4.
- Line 118-135: `os.walk` walk. Skips `.git`, `node_modules`, `.venv`, `__pycache__`, `dist`, `.next` in addition to BLOCKED_DIRS check. Entries limited to `[:50]` per directory (line 130). **Silent truncation** — no `files_capped_per_dir: true` signal.
- Line 133-135: total entries hard-capped at 500 with a literal `"... (truncated at 500 entries)"` string appended to the entries list. **Human-readable truncation signal only — no machine-parseable `truncated: bool` field.** **F-RT-2** MEDIUM.
- Line 137: response has `action`, `path`, `depth`, `entries`, `count`. No `truncated` field.

### 4.3 Action: `read_file` (line 139-173)

- Line 141-142: fail-loud on missing `path` (typed error dict without `ok: false`).
- Line 143: `max_lines = min(payload.get('max_lines', 200), 500)` — schema-declared cap. Applied silently on cap; but explicit `truncated: bool` field in response (line 171). **VERIFIED-CORRECT.**
- Line 144: `start_line = max(int(payload.get('start_line', 0)), 0)` — negative → 0.
- Line 149-151: file-size guard — reject files > 500,000 bytes with typed error naming the size. Good.
- Line 153-160: streamed read, 1-based line numbering.
- Line 162: `total_lines` computed via re-open + iter (double-read for line count). Correct but wasteful for large files.
- Line 164-173: response includes `path`, `start_line`, `end_line`, `lines`, `total_lines`, `truncated: bool`, `content`. **Best-in-class truncation surface.**

### 4.4 Action: `search` (line 175-209)

- Line 176-178: fail-loud on missing `query`.
- Line 183-185: `subprocess.run(['grep', '-rn', '--include=*', '-l', query, full_path])` (or `--include=*.{ext}` when `file_type` set). 10s timeout.
- Line 188: `capture_output=True, text=True, timeout=10`. Note: uses `cwd=project_root` (line 188) but full_path is absolute — the cwd is essentially ignored by grep.
- Line 189-190: post-filter blocks BLOCKED_DIRS + BLOCKED_FILES.
- Line 192-199: for first 10 files, run `grep -n query <file>` per-file, take first 5 lines each → `matches` list. Silent truncation. **F-RT-5.**
- Line 201-207: response has `action`, `query`, `files_matched: len(files)`, `files[:30]`, `sample_matches[:30]`. **`files_matched` is len of post-BLOCKED filter list but pre-slice** — so caller sees correct total count; `files` is capped at 30. Truncation of `files[:30]` is implicit (`files_matched > 30` signal via math). **No `files_truncated: bool` or `sample_matches_truncated: bool` fields.** **F-RT-5** MEDIUM.
- Line 208-209: `TimeoutExpired` → typed error naming "10s limit". Good.

### 4.5 Action: `git_info` (line 211-253)

- Line 213-217: comment cites Session 1103c fix that replaced bare `except Exception: pass` with narrow logging per subprocess call.
- Line 220-228: `git branch --show-current` with per-subprocess try/except + WARN log + default `'unknown'`.
- Line 230-238: `git log --oneline -10` with same discipline.
- Line 240-251: `git status --short` with same discipline.
- **Well-hardened.** WARN logs on subprocess failures give operator visibility while returning graceful defaults. Contrast: the outer `except Exception` at line 259 is MORE broad and less well-instrumented.

### 4.6 Unknown action + outer except (line 255-260)

- Line 255: unknown action → `{'error': ...}` typed. **F-RT-BC** batch-close (no `ok: false`).
- Line 257-258: `ValueError` (typically from `_safe_path`) → typed error dict. Good.
- Line 259-260: **outer broad `except Exception as e:` returns `{'error': f'repo_tool error: {str(e)}'}` swallowing ANY other error** with no traceback log. **F-RT-11** — narrower than the F-RG-1 case (this one at least emits a message string with the error text) but still lacks traceback + doesn't distinguish error class. LOW-MEDIUM.

## 5. Defaults inventory

| Param | Schema-declared | Handler-effective | Divergence? |
|---|---|---|---|
| `action` | required | `'tree'` | schema violation — F-RT-1 (batch-close) |
| `path` | none | `''` → project_root | matches |
| `depth` | default 2, max 4 | 2, hard cap 4 | matches; no cap signal (batch-close doc) |
| `query` | none | fail-loud on empty | matches |
| `start_line` | default 0 | `max(int(...), 0)` | matches |
| `max_lines` | default 200, max 500 | 200, cap 500 | matches; **truncated field surfaced** ✓ |
| `file_type` | none | `''` → all types | matches |

## 6. Hidden filters

- **BLOCKED_FILES + BLOCKED_DIRS** (line 91-92) applied in `_safe_path` + tree walk + search post-filter. Not surfaced when filter fires. Documentation-worthy — batch-close.
- Tree walk skips `.git / node_modules / .venv / __pycache__ / dist / .next` (line 126) in addition to BLOCKED_DIRS. Consistent with BLOCKED_DIRS but slightly larger set.

## 7. Limits inventory

- `tree` — `depth ≤ 4`, `files[:50]` per dir, `entries ≤ 500`. All silent (except the literal string appended in the 500-cap case). **F-RT-2 target.**
- `read_file` — `max_lines ≤ 500`, `size ≤ 500KB`. Truncated field surfaced. Size limit surfaces typed error. **BEST-IN-CLASS.**
- `search` — `grep timeout=10s` (typed error), `files[:30]`, `sample_matches[:30]`, first-10-files-for-matches, 5-lines-per-file. Multiple silent caps. **F-RT-5 target.**
- `git_info` — `log -10` (10 commits), `status[:20]` (line 244). Silent caps.

## 8. Silent-truncation test

- `tree` with > 500 entries → appends literal `"... (truncated at 500 entries)"` to entries list. **Human-readable only.** F-RT-2.
- `search` with > 30 files → silent truncation. F-RT-5.

## 9. Silent-filter test

- Files in BLOCKED_DIRS excluded from search + tree without signal. Documented-in-code but not surfaced.

## 10. Silent-fallback test

- Outer `except Exception` at line 259 returns generic error string. **F-RT-11.** Less severe than F-RG-1 (this one DOES include the error message) but still no traceback log.
- Unknown action returns typed error with valid-action list (implicit via the fallthrough at line 255).

## 11. Staleness test

- Filesystem state is always current at read time. `git_info` reflects live git state via subprocess.

## 12. Freshness signal

- N/A — filesystem is inherently fresh.

## 13. Provenance signal

- Response includes `path` echo for read_file / search. Sufficient for Rigby to cite.
- No `file_hash` or `git_head` echo — Rigby can't tell if the file changed between a search + read pair.

## 14. Authority / workspace assumptions

- No authority carriage. This is a read-only codebase tool; no user/workspace scoping.
- Security invariant: `_safe_path` enforces within-project-root.

## 15. Runtime dependencies

- stdlib `os`, `subprocess`, `os.walk`.
- Filesystem access to project root.
- `git` binary in PATH for `git_info` action.

## 16. Recoverable failure modes

- Missing path on read_file → typed error.
- Missing query on search → typed error.
- Path outside project → ValueError → typed error.
- Blocked file/dir → ValueError → typed error.
- File too large → typed error naming size.
- grep timeout → typed error.
- Individual git subprocess failure → WARN log + default value.

## 17. STOP-and-report failure modes

- Outer `except Exception` at line 259 catches everything else silently (no traceback log). **F-RT-11.**

## 18. Operator-action failure modes

- `git` binary missing → all `git_info` fields → `'unknown' / [] / 0` with WARN log.
- `grep` binary missing → outer except → generic error string (no traceback).

## 19. Existing test coverage

**No dedicated test file for `repo_tool` at HEAD.** Grep across `core/tests/` shows only `test_codebase_awareness_retirement.py` (unrelated — deprecating a different tool).

**Coverage gap identified:** zero regression tests for `repo_tool` behaviors including the security invariant (`_safe_path` blocking). Every finding below is uncovered.

## 20. Change list

**Code patches (one commit per defect per campaign plan §12.1):**

| File | Lines (post-patch) | Defect | Change |
|---|---|---|---|
| `core/services/td_handlers_gateway.py` | 110-186 | F-RT-2 | `tree` action declares `_DEPTH_HARD_MAX = 4`, `_FILES_PER_DIR_HARD_MAX = 50`, `_ENTRIES_HARD_MAX = 500`. Surfaces `depth_capped/requested_depth/effective_depth/depth_hard_max`, `entries_truncated/entries_hard_max`, `files_capped_per_dir/files_per_dir_hard_max` — attached only when the respective cap fires (mirrors F-D-5 pattern; happy path stays quiet). |
| `core/services/td_handlers_gateway.py` | 213-262 | F-RT-5 | `search` action declares 4 explicit hard maxes (`_FILES_LIST_HARD_MAX=30`, `_SAMPLE_MATCHES_HARD_MAX=30`, `_MATCH_SOURCE_FILES_HARD_MAX=10`, `_LINES_PER_FILE_HARD_MAX=5`). Tracks per-file line-cap firing. Surfaces `files_truncated/files_hard_max` and `sample_matches_truncated/sample_matches_hard_max/match_source_files_hard_max/lines_per_file_hard_max` — attached only when the respective cap fires. |
| `core/services/td_handlers_gateway.py` | 306-317 | F-RT-11 | Outer `except Exception` now logs at ERROR with `exc_info=True` — action + error class + message + traceback. Response contract unchanged (still `{'error': f'repo_tool error: {str(e)}'}`). Non-breaking add. |

**Test files added:**

- `core/tests/test_repo_tool_validation_2728.py` — **first regression test file for `repo_tool` at HEAD.** 15 tests across 5 test classes: F-RT-2 tree cap envelope (3 tests: baseline mocked, depth_capped, entries_truncated); F-RT-5 search cap envelope (3 tests: baseline mocked, files_truncated, sample_matches_truncated); F-RT-11 outer except logs traceback (1 test); security invariant baseline (4 tests: env / env.local / credentials.json / out-of-root); action baseline (4 tests: read_file requires path, read_file truncated field, git_info baseline, unknown action typed error).

**Docs updated:**

- Validation report (this file) records the trace + findings + patches + tests + first-coverage-at-HEAD observation.

**Docs NOT updated (per campaign plan §2 anti-scope):**

- No schema description changes (patches are additive to response shape only).
- `docs/topics/personal-assistant.md` — pending Batch B close.

**Test verification:**

- `python manage.py test core.tests.test_repo_tool_validation_2728` → **15/15 pass** (12.1s — most of the runtime is real filesystem walks for the cap-firing tests).
- Full Batch A + Batch B cross-tool regression: **85/85 pass** (14.4s) across all 7 validation-2728 test files. Zero cross-tool interference.

---

## Findings

### F-RT-2 — `tree` action silent truncation on entries cap + per-dir cap (MEDIUM)
- **Class:** DEFECT-CLASS-D10 (analog of F-D-5).
- **Evidence:** `td_handlers_gateway.py:130` (`sorted(files)[:50]` per dir); `td_handlers_gateway.py:133-135` (500 entries hard cap with literal string appended, no `truncated` field).
- **Severity:** MEDIUM. Rigby scanning a large directory tree gets silent truncation; only visual scan of entries list reveals the cap.
- **Action:** PATCH — add explicit `entries_truncated: bool` field to `tree` response when caller-exceeded any cap; also add `files_capped_per_dir: bool` when per-dir 50-cap fires. Mirror F-D-5 pattern.

### F-RT-5 — `search` action silent truncation on files + matches (MEDIUM)
- **Class:** DEFECT-CLASS-D10.
- **Evidence:** `td_handlers_gateway.py:205-206` — `files[:30]` and `sample_matches[:30]`. Sample only from first 10 files; 5 matches per file. Multiple silent caps.
- **Severity:** MEDIUM. Rigby using `search` to find callers of a symbol (before deleting "dead" code per MEMORY `feedback_verify_before_deleting_dead_code`) gets bounded results with no cap signal.
- **Action:** PATCH — add `files_truncated: bool` (fires when `files_matched > 30`) and `sample_matches_truncated: bool` (fires when at cap OR when file-count > sample source of 10). Response already has `files_matched` for the total-file signal; now surface the sample-matches truncation explicitly.

### F-RT-11 — Outer `except Exception` swallows tracebacks (LOW-MEDIUM)
- **Class:** operational-visibility gap (narrower than F-RG-1 but same class).
- **Evidence:** `td_handlers_gateway.py:259-260`. Catches any non-ValueError exception without a traceback log.
- **Severity:** LOW-MEDIUM. This is a read-only tool; the outer except is a defensive net rather than a silent-degrade path (the response DOES carry `error: <message>`). Adding `exc_info=True` to a log call would preserve the response contract while giving operators visibility.
- **Action:** PATCH — add `logger.error(..., exc_info=True)` inside the outer except; keep the response contract unchanged (still `{'error': ...}`). Non-breaking add.

### F-RT-BC-* — batch-close observations
- **F-RT-1** action defaults to `'tree'` despite schema `required` (schema-violation class shared with all Batch A/B tools).
- **F-RT-BC-1** BLOCKED_FILES + BLOCKED_DIRS silently filter without response signal.
- **F-RT-BC-2** `git_info` result caps (`log -10`, `status[:20]`) silent.
- **F-RT-BC-3** Unknown action + error responses lack `ok: false` (systemic cross-tool).
- **F-RT-BC-4** No dedicated test file for `repo_tool` — coverage gap.

---

## Rigby-safe assessment (post-patch)

- **R1 (no dangerous defaults):** CLEARED.
- **R2 (no silent action substitution):** CLEARED.
- **R3 (no silent truncation):** CLEARED. F-RT-2 patched (`tree` cap envelope); F-RT-5 patched (`search` cap envelope). read_file's existing `truncated: bool` field remains best-in-class.
- **R4 (hidden filters surfaced):** PARTIAL — deferred to batch-close (F-RT-BC-1 BLOCKED_FILES/BLOCKED_DIRS not surfaced).
- **R5 (workspace/authority carriage):** N/A (read-only tool).
- **R6 (freshness surface):** CLEARED.
- **R7 (provenance surface):** PARTIAL — deferred to batch-close (no `file_hash` / `git_head` echo).
- **R8 (worker/env preconditions):** CLEARED by F-RT-11 patch (outer except now logs traceback with `exc_info=True`; operators see grep/git binary missing + I/O errors).

---

## Verdict

Tool status: **DEFECT-PATCHED-VERIFIED** at HEAD post-Session 2728 patches.

**Code trace coverage:** all 4 actions (`tree`, `read_file`, `search`, `git_info`) + `_safe_path` security invariant + outer error handling.

**Findings summary:**

- **Valid at HEAD → patched:** F-RT-2 (tree cap silent), F-RT-5 (search cap silent), F-RT-11 (outer except traceback silent).
- **Batch-close cleanup observations (deferred per Chris):** F-RT-1 (action default vs schema `required`), F-RT-BC-1 (BLOCKED_FILES/BLOCKED_DIRS not surfaced), F-RT-BC-2 (`git_info` result caps silent), F-RT-BC-3 (error envelopes lack `ok: false`), F-RT-BC-4 (coverage gap — now closed by the new test file).

**Coverage improvement:**

- **Before Batch B tool 2:** zero regression tests for `repo_tool`.
- **After Batch B tool 2:** 15 regression tests covering all three patched behaviors + security invariant baseline + read_file/git_info/unknown-action baselines. Establishes coverage for future refactors.

**Regression sweep at HEAD:**

- 15 new regression tests in `test_repo_tool_validation_2728.py`: **15/15 pass** (12.1s).
- Full Batch A + Batch B cross-tool sweep (85 tests across 7 validation-2728 files): **85/85 pass** (14.4s). Zero cross-tool interference.

**Follow-ups filed:**

- Batch-close observations for cross-tool consistency (F-RT-1 schema-vs-handler action default; F-RT-BC-* error envelope + BLOCKED filter surfacing + git_info cap signal).

**Tool closure statement:** `repo_tool` is VERIFIED at HEAD + 3 patches. Rigby's codebase-introspection workflows (tree scans + code searches for callers before deletion + git status checks) are now bounded-and-surfaced instead of bounded-and-silent. The security invariant enforcing `_safe_path` blocking of env files, credentials, and out-of-root paths is now regression-tested for the first time.
