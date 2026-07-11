---
title: "Close-Ceremony Ledger Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2763
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (freshness + design) + Chris candidate selection + local build verify + backend smoke test
scope: S2763 — new operator surface listing last N session close-ceremonies (handoff + paired ratification envelope) as read-only cards at the bottom of Workspace → System → Ops
serves_arc: platform observability / session-open context re-load (proposed as N3 in S2762 candidate menu)
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md (S2761 — canonical health_summary composition pattern for views_ops_console.py)
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md (S2762 — canonical api.get pattern for OpsConsoleTab.tsx)
ratified_documents:
  - core/views_ops_console.py (amended — close_ceremony_ledger view + fixed roots + safe path helpers)
  - core/urls.py (amended — /api/ops/close-ceremony-ledger/ route)
  - frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx (amended — CloseCeremonyLedger types + ledgerQuery + Recent Close-Ceremonies section with copy-to-clipboard cards)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2763 open freshness check (fresh pin pa-2e382508b79d478b) — verdict FRESH, SHA 7db82c84… — corroborates S2762 recycle-after-merge rule
  - S2763 design SIGN (Rigby) — PASS with legitimate path-traversal risk flagged; hardening applied (fixed roots, resolve-then-relative-to check, no caller-supplied paths)
frozen: true
---

# Close-Ceremony Ledger Ratification Record

Frozen canonical record of Chris's ratification of the Close-Ceremony Ledger tile on 2026-07-11. Ships session-open context re-load as a browser-visible operator surface. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** net-new operator surface (per S2745 engineering-bias directive). Chris explicitly picked candidate **N3** from the S2762 close-out menu.
- **Motivation:** at session open, Claude reads `context-kit orient` + `00-START-NEXT-SESSION.md` + the latest handoff. Chris re-loads the same context via terminal + editor. The last N close-ceremonies are the highest-signal indicator of "what's recently in flight" and are already file-backed under `docs/handoffs/` + `docs/research/implementation/`. This ledger surfaces them at Workspace → System → Ops so Chris can visually scan recent sessions without terminal round-trips.
- **Ratifier:** Chris (candidate selection at S2762 close: "let's do N3 next")

---

## §2. Ratified Deliverables

### §2.1 `core/views_ops_console.py` — `close_ceremony_ledger` view

New endpoint `GET /api/ops/close-ceremony-ledger/?limit=<N>` returning:

```json
{
  "items": [
    {
      "session_number": 2762,
      "title": "Ops Console Sibling 401 Fix Ratified",
      "date": "2026-07-11",
      "handoff_path": "docs/handoffs/SESSION_2762_OPS_SIBLING_401_FIX_RATIFIED.md",
      "envelope_path": "docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md",
      "envelope_exists": true
    },
    ...
  ],
  "count": <N>,
  "limit": <N>
}
```

**Implementation:**

- **Fixed filesystem roots** — `_HANDOFFS_ROOT = BASE_DIR / 'docs' / 'handoffs'` and `_ENVELOPES_ROOT = BASE_DIR / 'docs' / 'research' / 'implementation'`. Module-level constants; no caller input contributes to path construction.
- **Handoff enumeration** — `_HANDOFFS_ROOT.glob('SESSION_*.md')` filtered through `_SESSION_FILENAME_RE = re.compile(r'^SESSION_(\d+)_')`; sorted descending by session number; sliced to `limit`.
- **Title extraction** — `_H1_TITLE_RE = re.compile(r'^#\s+Session\s+\d+\s+[—-]\s+(.+?)\s*$', re.MULTILINE)` on the first 4KB of each handoff.
- **Date extraction** — `_DATE_LINE_RE = re.compile(r'^\*\*Date:\*\*\s+(\d{4}-\d{2}-\d{2})', re.MULTILINE)`; null when absent.
- **Envelope pairing** — one-shot index of `_ENVELOPES_ROOT.glob('RATIFICATION_*.md')` mapping `session_added: <N>` frontmatter → relative envelope path. Cheap because envelopes total ~a few hundred.
- **Auth** — `@require_GET + @login_required`, matching sibling ops endpoints.

### §2.2 `core/urls.py` — route registration

New line adjacent to the four existing ops endpoints:

```python
path('api/ops/close-ceremony-ledger/', lambda r: __import__('core.views_ops_console', fromlist=['close_ceremony_ledger']).close_ceremony_ledger(r), name='ops-close-ceremony-ledger'),
```

### §2.3 `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — Recent Close-Ceremonies section

New section appended below Blocked Agents. Structure:

- **Header row:** `<Layers />` icon + "Recent Close-Ceremonies (last N)".
- **Card list** — one card per session:
  - Left: `S<num>` mono badge in primary accent color.
  - Right: title + date + envelope-status pill (green "envelope" / gray "handoff-only").
  - Under: two copy-to-clipboard buttons (handoff path + envelope path when present). Icon toggles to `<Check />` for 1500ms on successful copy.
- **useQuery** with `staleTime: 60000` (60s cache). Section hidden entirely when `items.length === 0`.

TypeScript interfaces `CloseCeremonyItem` and `CloseCeremonyLedger` mirror the backend JSON shape.

---

## §3. Security Hardening (§4.2 Rigby SIGN concern addressed)

Rigby's SIGN response flagged path-traversal / unintended-directory-disclosure risk. Applied hardening:

1. **No caller-controlled paths.** The only query parameter is `limit` (clamped to `max(1, min(50, int_or_default_10))`).
2. **Fixed roots.** `_HANDOFFS_ROOT` and `_ENVELOPES_ROOT` are module-level `Path(BASE_DIR)` compositions. Not derived from request data.
3. **Resolve-then-check.** `_safe_relpath()` calls `Path.resolve()` and then `Path.relative_to(BASE_DIR)`. Any file that resolves outside `BASE_DIR` (symlink escape, `..` traversal) returns `None` and is dropped from the response.
4. **Relative paths only.** Response contains only paths relative to repo root — never absolute paths, never `file://` URIs, never OS-specific tokens.
5. **Read-only.** No file writes; no upload; no delete. Endpoint is `@require_GET`.
6. **Auth.** `@login_required` — same authorization contract as sibling ops endpoints.

**Defense-in-depth:** the docs/handoffs/ + docs/research/implementation/ directories are already checked into git and readable by any operator with repo access. Exposing "here are the paths to those files" to an authenticated user does not materially increase attack surface — but the safe-globbing discipline still holds for any future extension.

---

## §4. Rigby SIGN

### §4.1 Freshness corroboration (S2763 open, pin `pa-2e382508b79d478b`)

`ops_tool.version` → **FRESH**, `head_commit_sha 7db82c84…` matches HEAD of `main` (post-S2762 merge).

**Corroboration signal for `feedback_recycle_after_merge.md`:** S2762 close ran `make recycle-all` immediately after PR #3151 merged. Post-recycle Rigby freshness check → FRESH. S2763 open (this session) rechecked and again → FRESH · same SHA. **Two data points now support codifying the recycle-after-merge rule into the Playbook.** Third corroboration signal deferred until at least one more session close-recycle-open cycle.

### §4.2 Design SIGN

**SIGN LEAN: PASS.** Rigby: "clean, low-scope, reuses the proven ops_console proxy + react-query patterns; filesystem-as-source matches the 'git is ground truth' premise."

**Risk called out:** path traversal / unintended file disclosure via relative paths + globbing, particularly if any future slug pairing uses user-provided params. Rigby recommended hard-pinning search roots and validating that returned paths resolve within those roots (no `..`, no symlinks).

**Response:** hardening applied per §3 above.

---

## §5. Chris D-Verdict

Sequence:

1. **Session-open candidate selection:** "let's do N3 next" (picked N3 from S2762 close menu).
2. **Joint agreement:** no F-BLOCKING decisions surfaced; Rigby's path-traversal risk resolved before code landed.
3. **Post-merge verify (pending):** browser hard-refresh Workspace → System → Ops to confirm the Recent Close-Ceremonies section renders below Blocked Agents with the last 10 sessions listed.

**Effect:** operator surface for fast session-open context re-load. Complements the S2761 Ops Health tile and the S2762 sibling-401 fixes — the entire Ops Console tab is now a single-glance summary of what the platform is doing AND what the platform has recently done.

---

## §6. Verify-Before-Build

- **Existing patterns reused:**
  - `core/views_ops_console.py:87-131` — `health_summary` view established the "compose fixed dispatches into a single tile payload" shape.
  - `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx:36-45` — `healthQuery` established the `api.get` + `try/catch → null` shape.
- **What's new:** filesystem-backed enumeration (not `_handle_ops` dispatch). The pattern is close to sibling but the data source is repo files, not the Celery/DB observability substrate. Justified because handoff + ratification envelope files are the canonical git-tracked artifacts of session close-ceremonies.
- **Reuse/extend/correct verdict:** extend `views_ops_console.py` with a new view; reuse the sibling shape but with a new data source. No new abstraction, no new module.

---

## §7. Provenance Chain

- **Predecessor sessions:** S2761 (tile) → S2762 (sibling 401 fix) → **S2763 (this ledger)**
- **Reference infra:** `core/views_ops_console.py:87-131` (health_summary composition pattern), `frontend/src/lib/api.ts:13-40` (axios instance)
- **Engineering Playbook v0.5.0:** PLAYBOOK-7.4.1 (close-ceremony 1-PR bundle) + Cycle 1A verify-before-build applied (§6 above)
- **Memory rules applied:** `feedback_last_mile_ui.md` (browser-visible operator surface), `feedback_recycle_after_merge.md` (post-merge recycle → next-session-open FRESH; second corroboration this session), `feedback_local_truth_no_production.md` (local build pass = shipped), `feedback_claude_rigby_agree_first_chris_yes_no.md` (Rigby SIGN reached PASS before code landed)
- **New codification candidate:** `feedback_recycle_after_merge` now has 2 corroborating data points; propose Playbook amendment after third arc-independent corroboration.
