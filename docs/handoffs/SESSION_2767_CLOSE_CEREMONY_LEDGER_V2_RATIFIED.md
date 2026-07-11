---
session: 2767
date: 2026-07-11
title: "Close-Ceremony Ledger v2 (hover-preview + docs viewer navigation) ratified"
status: complete
outcome: shipped
scope: net-new-engineering-N4
canonical_authority: repo_canonical
ratification_envelope: docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md
---

# Session 2767 — Close-Ceremony Ledger v2 ratified

## §1. TL;DR

Chris selected N4 from the S2767 candidate menu. Joint Claude+Rigby SIGN cycle reached PASS/MODIFY-accepted on all three asks (interpretation / backend choice / risks). Chris D-verdict "approved" on the final plan. Shipped the LedgerRow hover-preview + click-to-open-DocumentViewer behavior in a single frontend-only edit to `OpsConsoleTab.tsx`. Zero new backend routes — reuses the pre-existing public-by-design `/api/platform/doc-content/` endpoint.

**First close-cycle after PLAYBOOK-7.4.4 codification** to dogfood the constitutional recycle-after-merge step. Also the first N-lane (net-new engineering) ship since S2765 — the S2745 bias-engineering rule turned a docs-only playbook session (S2766) into a net-new UI ship (S2767) at the next open.

## §2. Timeline

| Time (approx) | Event | Reference |
|---|---|---|
| S2767 open | `context-kit orient` + START-NEXT read | this session log |
| N4 selected | Chris: "lets continue with N4" | this session |
| Pin minted | `pa-d2f1f7bd302f47d2` scoped to `s2767-close-ceremony-ledger-v2` | `session_lifecycle open` |
| Rigby SIGN | one round-trip, Q1/Q2/Q3 asks batched | pin above |
| Verify-before-build | `/api/platform/doc-content/` auth confirmed public-by-design (`auth_middleware.py:436`); existing `DocumentViewer` at `frontend/src/components/platform/DocumentViewer.tsx` (S818) | this session |
| Code + build + smoke | LedgerRow component + Suspense wrapper wired; Vite build 3.20s; Django shell 200 OK | this session |
| Envelope + handoff | this doc + `RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md` | filesystem |
| Docs cascade | 4-step + provenance rebuild (post-merge) | `make docs-cascade` equivalent |
| PR merge | filled at merge | GitHub |
| `make recycle-all` | dogfood PLAYBOOK-7.4.4 (first cycle where rule is constitutional, not just memory) | Makefile emitter |

## §3. What shipped

**Files touched:**

- `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — new `LedgerRow` component (private to this file) with hover-preview tooltip and click-to-open primary action; new `LazyDocumentViewer = lazy(() => import('@/components/platform/DocumentViewer'))`; new `viewerDoc` state on `OpsConsoleTab`; Suspense-wrapped drawer at return root; imports extended with `useRef, Suspense, lazy, FileText`. Existing copy-path buttons demoted to small secondary chips.
- `docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md` — new envelope (this session).
- `docs/handoffs/SESSION_2767_CLOSE_CEREMONY_LEDGER_V2_RATIFIED.md` — this file.

Net: frontend-only. No Python touched. Per PLAYBOOK-7.4.4 mechanical waiver list, this is a *frontend-only* merge and could theoretically waive the post-merge recycle — but the diff also touches docs (index will need rebuild for handoff + envelope), and we opt to invoke `make recycle-all` anyway for consistency and to accumulate a second data point on the rule's dogfooding.

**Endpoint reuse (zero backend changes):**

`/api/platform/doc-content/?path=<safe-relpath-under-docs>` — verified as intentionally auth-exempt public read-only at `core/auth_middleware.py:436`; already guards traversal + `docs/**` prefix + markdown-suffix.

**Bundle split evidence:** Vite output shows `DocumentViewer-<hash>.js = 4.94 kB` (gzip 1.77 kB) as its own chunk. `purify.es` + `index.es` chunks carry the markdown deps.

## §4. Rigby SIGN Summary

Joint SIGN one round-trip via pin `pa-d2f1f7bd302f47d2`.

**Freshness:** verdict FRESH · SHA `be898addc` matches HEAD. **Recycle log** shows S2766 close + S2765 close — first cycle after PLAYBOOK-7.4.4 constitutional force. Recycle-after-merge rule dogfooded successfully at S2767 open.

**Design SIGN — Q1 (interpretation):** PASS. "hover → tooltip preview + click → DocumentViewer drawer" matches START-NEXT phrasing exactly.

**Design SIGN — Q2 (backend choice):** MODIFY. Accept Option A (reuse `doc-content` with debounce + cancel + staleTime + stable-hover check) for Phase 1; upgrade to Option B (dedicated `/api/ops/doc-preview/`) as a Phase 2 candidate once UX validates.

**Design SIGN — Q3 (risks):** MODIFY on (a) + (c); PASS with tweak on (b).
- (a) auth — verified public-by-design at `auth_middleware.py:436`; no new exposure.
- (b) a11y — added focus + blur handlers on primary row button in addition to hover handlers on the row wrapper; `role="tooltip"` + `pointer-events-none`.
- (c) bundle bloat — `React.lazy` + `Suspense` wrap on DocumentViewer; verified via Vite chunk output.

**One extra observation Rigby raised** ("preview content safety"): rendered inside a `<pre>` with plain text only. No markdown re-parse. No `dangerouslySetInnerHTML`.

## §5. Post-merge browser eyeball (Chris)

1. Hard-refresh `localhost:8000/workspace?tab=system&sub=ops`.
2. Verify Ops Health tile (S2761) + SLO / Signatures / Blocked (S2762) + Recent Close-Ceremonies section still render.
3. **NEW — hover a Recent Close-Ceremonies row for ~150ms** → tooltip appears below the row with the first 10 lines of the handoff. Move mouse away → tooltip dismisses.
4. **NEW — click a Recent Close-Ceremonies row** → DocumentViewer drawer opens with the handoff loaded. Fullscreen toggle + close button work.
5. **NEW — click the small "envelope" chip** → same drawer opens with the envelope loaded.
6. **REGRESSION CHECK — copy chips** ("handoff path" / "copy envelope") — still copy the path to clipboard, checkmark flashes for 1500ms.

## §6. Twin-Pointer Card

📁 **Repo `/docs/` + `/frontend/` — S2767 artifacts:**

- **Frontend edit:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` (LedgerRow component + LazyDocumentViewer + Suspense wrap)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger_v2.md`
- **Handoff:** `docs/handoffs/SESSION_2767_CLOSE_CEREMONY_LEDGER_V2_RATIFIED.md` (this file)
- **Predecessor envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md` (S2763 v1)
- **DocumentViewer component:** `frontend/src/components/platform/DocumentViewer.tsx` (S818, reused unchanged)
- **doc-content backend:** `core/views_platform_command.py:1226` (S818, reused unchanged)
- **Auth-exempt registration:** `core/auth_middleware.py:436`
- **Playbook constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2767 (created at close via ORM-direct per S2754a twin-canonical rule)
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Recent Close-Ceremonies section now hover-previewable + click-to-open

## §7. Current Repository State

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2767 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2766 diagnostic infra + operator surfaces + governance CLOSED · **S2767 close-ceremony ledger v2 CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-d2f1f7bd302f47d2` (retired at S2767 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-d2f1f7bd302f47d2` (retired; forces fresh mint at S2768 open) |
| Live infra state | S2755→S2766 diagnostic infra + operator surfaces + Playbook v0.6.0 + **S2767 CCL v2 hover-preview + docs viewer nav** operational |
| Next move | Chris selects at S2768 open |

## §8. What This Session Taught About Doing Sessions

- **N4 was the smallest ship of the S2755→S2767 arc.** ~180 lines net changed in a single frontend file, zero new routes, one component extracted, one lazy-load added. The bias-engineering rule successfully rebalanced from S2766's docs-only playbook session to a user-visible UI change at the very next open.
- **Verify-before-build paid off twice.** Cycle 1A discipline (grep the auth story for `/api/platform/doc-content/` before writing a preview fetch) surfaced the public-by-design registration, which shortened Rigby's Q3(a) response from "verify auth" to "no new exposure." Same discipline surfaced the existing DocumentViewer, which avoided building a second markdown viewer.
- **PLAYBOOK-7.4.4 dogfood is now a checklist item at every close, not just close-ceremonies of Playbook amendments.** The rule requires the recycle regardless of what the amendment ratified — S2767 is a frontend UI ship, and the recycle still fires.
- **Sub-500-line UI sessions with joint Rigby SIGN + Chris D-verdict + build + smoke + envelope + handoff are viable inside ~1 hour** if the surfaces to reuse are already identified during verify-before-build. Same shape as S2762 (Ops Console sibling 401 fix).
