---
title: "Close-Ceremony Ledger v2 (hover-preview + docs viewer navigation) Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2767
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (freshness FRESH · SHA be898addc + design SIGN one-round-trip) + Chris candidate selection (N4) + Chris D-verdict on final plan + local build + shell smoke test
scope: S2767 — N4: extend the Recent Close-Ceremonies ledger with hover-preview tooltips and click-to-open navigation via the existing DocumentViewer drawer; zero new backend routes
serves_arc: platform observability (Ops Console at Workspace → System → Ops); operator context re-load speed
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md (S2763 — v1 filesystem-backed ledger, fixed-root safety pattern)
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile_v2_slo.md (S2764 — extend-not-fork discipline reused)
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_recent_recycles.md (S2765 — sibling operator surface)
ratified_documents:
  - frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx (amended — LedgerRow component with hover-preview + click-to-open; lazy-loaded DocumentViewer wired via Suspense)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2767 open freshness (fresh pin pa-d2f1f7bd302f47d2) — verdict FRESH · SHA be898addc matches HEAD (FIRST corroboration cycle after PLAYBOOK-7.4.4 codified at S2766 — dogfoods the rule)
  - S2767 design SIGN (Rigby) — PASS on interpretation + MODIFY on backend choice (accept Option A Phase 1 with debounce+cancel+staleTime) + MODIFY on lazy-load DocumentViewer + PASS on focus-triggered a11y tweak
frozen: true
---

# Close-Ceremony Ledger v2 — Ratification Record

Frozen canonical record of Chris's ratification of the Close-Ceremony Ledger v2 operator surface on 2026-07-11. Extends the S2763 v1 ledger (session-number + title + copy-path rows) with hover-triggered preview tooltips and click-to-open navigation into the existing `DocumentViewer` drawer. Zero new backend routes: reuses `/api/platform/doc-content/` (verified auth-exempt public read-only endpoint at `auth_middleware.py:436`). Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** last-mile UI extension of the S2763 v1 ledger (N4 in S2767 candidate menu).
- **Motivation:** v1 rows required the operator to copy the handoff/envelope path and paste into a shell/editor to inspect it. For an operator surface designed for *fast context re-load*, the extra copy-paste step defeats the purpose. v2 makes preview one hover away and full-content one click away — the operator never leaves the Ops Console tab to decide whether a handoff is worth reading.
- **Ratifier:** Chris (candidate selection at S2767 open: "lets continue with N4"; D-verdict on the final plan: "approved")
- **First cycle after PLAYBOOK-7.4.4 codification:** S2767 open verified FRESH · SHA-match at `be898addc` — the rule that S2766 promoted to constitutional force passed its first post-codification test at S2767 open. Rigby's `ops_tool.recent_recycles` returned both S2766 close (`be898addc`) and S2765 close (`f2cba2917`) as the top two recycle events.

---

## §2. Ratified Deliverables

### §2.1 `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — LedgerRow with hover-preview + click-to-open

Two behaviors added to each Recent Close-Ceremonies row:

1. **Hover-preview** (mouse-hover or focus). After a `HOVER_DEBOUNCE_MS = 150ms` stable-hover window, the row fires a react-query fetch to `/api/platform/doc-content/?path=<handoff_path>` and renders the first `PREVIEW_LINE_LIMIT = 10` lines as sanitized plain text in an absolutely-positioned tooltip below the row. Cache staleTime `5min` per path (spec key includes the path); re-hovering the same row within 5 minutes is a cache hit. Preview closes on mouse-leave / blur.

2. **Click-to-open.** Clicking the row header opens the existing `DocumentViewer` drawer (`frontend/src/components/platform/DocumentViewer.tsx`) with the handoff loaded. A secondary "envelope" button opens the envelope in the same drawer. The copy-path buttons remain but shrink to small `handoff path` / `copy envelope` chips beside the primary open action.

`DocumentViewer` is imported via `React.lazy` + wrapped in `Suspense` at the tab's return root, so the ReactMarkdown / rehype-sanitize / remark-gfm dependency chain only enters the bundle chunk graph when the operator actually opens a doc. Vite build confirms the split: `DocumentViewer-<hash>.js = 4.94 kB` (gzip 1.77 kB) as its own chunk, `purify.es` + `index.es` chunks for the markdown deps.

### §2.2 Interfaces added

```ts
interface DocContentResponse {
  content: string
  metadata: { path, name, title, lines, size_bytes, modified_at }
}

interface LedgerRowProps {
  item: CloseCeremonyItem
  onOpen: (path: string, title: string) => void
  onCopy: (path: string) => void
  copiedPath: string | null
}
```

### §2.3 Constants

```ts
const PREVIEW_LINE_LIMIT = 10
const HOVER_DEBOUNCE_MS = 150
const PREVIEW_STALE_TIME_MS = 5 * 60 * 1000
```

---

## §3. What Was NOT Changed

- No new backend routes. `/api/platform/doc-content/` served as-is; existing traversal + `docs/**` prefix guards + markdown-suffix filter satisfy the security profile.
- No auth changes. Endpoint remains in the intentionally auth-exempt public read-only list at `core/auth_middleware.py:436`.
- No changes to the S2763 ledger backend view (`core/views_ops_console.py::close_ceremony_ledger`) or its URL.
- No changes to `DocumentViewer.tsx` — imported unchanged from `@/components/platform/DocumentViewer`.
- Copy-path behavior preserved (secondary chips) — nothing removed from v1 UX, only demoted.

---

## §4. Rigby SIGN Summary

Joint SIGN routed via pin `pa-d2f1f7bd302f47d2` (label `s2767-close-ceremony-ledger-v2`).

### §4.1 Q1 — Interpretation
- **Rigby verdict:** PASS.
- **Content:** "hover → tooltip/popover preview + click → open DocumentViewer drawer" matches the START-NEXT phrasing. Smallest delta from v1 that reuses the already-built viewer surface.

### §4.2 Q2 — Backend choice (reuse doc-content vs new preview route)
- **Rigby verdict:** MODIFY.
- **Content:** Ship Option A (reuse `/api/platform/doc-content/`) with strict guardrails; upgrade to Option B (dedicated `/api/ops/doc-preview/`) in Phase 2 once UX is validated. Guardrails applied: 150ms debounce, cancel in-flight on hover-out (via `enabled` flip + react-query cache), react-query `staleTime 5m` cache keyed by path, "only fetch on stable-hover" (the 150ms window IS the stable-hover check).

### §4.3 Q3 — Risks (auth, a11y, bundle size)
- **Rigby verdict:** MODIFY on (a) + (c); PASS with tweak on (b).
- **(a) auth check:** Verified in-repo — `/api/platform/doc-content/` is at `auth_middleware.py:436` in the intentionally auth-exempt public read-only list; docs/ tree is public by design. N4 does not increase exposure.
- **(b) accessibility:** `startHover` / `stopHover` bound to `onFocus` / `onBlur` on the primary row button as well as `onMouseEnter` / `onMouseLeave` on the outer row div. Focus-visible ring on the button. Tooltip has `role="tooltip"` and is `pointer-events-none` so it can't intercept keyboard navigation.
- **(c) bundle size:** `DocumentViewer` behind `React.lazy` + `Suspense`; verified split via Vite output (dedicated chunk `DocumentViewer-DTY1RNV2.js = 4.94 kB` gzip 1.77 kB).

Rigby's two extra risks — preview content safety (plain-text sanitized) and rate-limit / caching layer — handled by rendering preview inside a `<pre>` (no markdown re-parse) and the react-query 5min staleTime.

---

## §5. Empirical smoke tests

### §5.1 Vite production build
- Command: `npm run build`
- Result: passed in 3.20s. Zero new TS errors. `DocumentViewer` split confirmed (4.94 kB chunk, gzip 1.77 kB). Pre-existing `api.ts` static/dynamic import warning is repo-wide and unrelated to N4.

### §5.2 Django shell smoke of `/api/platform/doc-content/`
- Input: `path=docs/handoffs/SESSION_2763_CLOSE_CEREMONY_LEDGER_RATIFIED.md`
- Result: `status=200`; metadata `{title: 'Session 2763 — Close-Ceremony Ledger Ratified', lines: 152, size_bytes: 8894}`; first 5 lines returned verbatim as expected.

### §5.3 Post-merge browser eyeball
- Owner: Chris.
- Steps: hard-refresh `localhost:8000/workspace?tab=system&sub=ops`; hover a Recent Close-Ceremonies row for ~150ms → verify preview tooltip appears with first 10 lines; click a row → verify DocumentViewer drawer opens with the full handoff; click "envelope" chip → verify envelope opens in the same drawer; copy chips still copy paths as before.

---

## §6. Post-ratification bindings

- **Head at ratification:** filled at merge.
- **Merged PR:** filled at merge.
- **Workspace mirrors (S2754a twin-canonical rule):**
  - Governance envelope mirror → `RUR-C1 Tenant Boundary Lockdown` workspace `fcd7e683-3bfe-4d35-9704-0e54dd587ea1` (deliverable_type `ratification_record`, category `governance`).
  - Content mirror → same workspace (deliverable_type `initiative_phase_doc`, category `implementation`).
- **PLAYBOOK-7.4.4 dogfood:** `make recycle-all` invoked post-merge — first close-ceremony to run the recycle step under the constitutional rule that requires it (rather than merely under the memory rule that motivated it).

---

## §7. Forward carry

- **Phase 2 candidate — dedicated preview endpoint.** If the S2767→S2770 open-cycle data shows the client-side slice is wasteful (measurable bandwidth or DB read spikes on hover-storm), promote Option B: `/api/ops/doc-preview/?path=&lines=10` with a ledger-scoped path allowlist reusing S2763's `_safe_relpath` + `_HANDOFFS_ROOT` / `_ENVELOPES_ROOT` guardrails.
- **Reusable pattern.** The lazy-DocumentViewer + hover-preview idiom is now available for other operator surfaces (Deliverables, Initiatives) if similar "fast context re-load" needs surface. Not codified as a Playbook rule pending a second independent trigger.
