---
title: "Agent Exchange Protocol (AEP) v0.1 — Design Proposal for Claude↔Rigby Machine-to-Machine Communication"
status: ratified (Chris D-verdict 2026-07-19 S2838; Stage 1 trial authorized at S2839 T5 cycle 1)
authority: architectural design review artifact
ratification:
  date: 2026-07-19
  session: 2838
  ratifier: Chris
  verbatim_directive: "Go ahead"
  scope: |
    Full AEP v0.1 design proposal as-authored, including Stage 1 trial
    authorization at S2839 T5 cycle 1 SIGN routing (opt-in; prose
    fallback available; both agents may accept AEP or classic prose).
    NO implementation authorization; NO Playbook amendment; NO workflow
    changes to downstream artifacts.
  envelope: docs/research/implementation/RATIFICATION_2026-07-19_agent_exchange_protocol_v0_1.md
  sign_cycles: 0 (direct Chris commission + direct Chris D-verdict; no Rigby joint SIGN required at Stage 0 per proposal-only scope; Stage 3 Playbook amendment WOULD require full SIGN + fold + D-verdict methodology per §14)
  next_action: Stage 1 trial at S2839 T5 cycle 1; post-trial evaluation deliverable if ≥50% token reduction + zero verification-check failures
session: 2838
date: 2026-07-19
authors: Claude Code (Chris directed post-S2838 close)
scope: |
  Design proposal for a compact, deterministic, machine-to-machine
  message protocol between Claude Code (CD) and Rigby (RGB) that
  preserves every current verification guarantee while reducing token
  volume by 50-70% and eliminating human-oriented framing.
non_goals:
  - implementation (no code changes proposed)
  - Playbook amendment (no rule edits proposed)
  - workflow changes (no SIGN/D-verdict/close-cascade changes)
  - prompt / constitution / schema modifications
  - platform behavior changes
  - retroactive migration of prior SIGN cycles
delegates_to: none
owner: Chris (ratified); Claude (proposer)
---

# Agent Exchange Protocol (AEP) v0.1 — Design Proposal

> **What this doc is.** A design-only proposal for a protocol that
> would replace the current prose-formatted SIGN messages between
> Claude Code (CD) and Rigby (RGB) with a compact, structured,
> deterministic exchange format. No code changes. No behavior
> changes. Chris ratifies or rejects.
>
> **What this doc is not.** An implementation plan. A Playbook
> amendment. A schema change. A prompt rewrite. A workflow revision.

---

## 1. Design philosophy

Recent SIGN cycles (S2834-S2838) demonstrate two reasoning agents
exchanging **prose reports** as if writing for a human reader:

- Ceremonial framing per cycle (`SIGN CYCLE N — S2838 T4 handoff...`)
- Repeated context restatement (audit doc lines, scanner filepath,
  consumed pre-clustering) that both agents already know from the
  pin conversation history
- Politeness / conversational conventions ("please cycle-2 verify",
  "Rigby: please AGREE/DISAGREE", "reply with verdicts")
- Verbose findings restatement instead of section-reference
- Repeated verdict labels ("AGREE / DISAGREE / STRENGTHEN") per Q
- Repeated `tool_runs (verbatim):` prefixing per Q
- Prose re-summary of prior cycles as narrative

**Both agents are machines** operating on:
- A shared pin conversation with full prior history
- Shared filesystem access to audit docs + scanner outputs
- Deterministic schemas (§10.1 v1.1) with known field semantics
- Deterministic fold classes (same_pr_mitigatable / future_trigger /
  needs_review / out_of_scope)
- Deterministic verdict grammar (AGREE / DISAGREE / STRENGTHEN /
  DEFER / RE-ROUTE)

**The prose report is the wrong communication substrate.** It
optimizes for human readability at the cost of:
- ~60-70% redundant token usage
- Non-deterministic parseability
- Ambiguity in verdict extraction
- Rework when restating prior-cycle folds

**AEP v0.1 optimizes for:**
1. Highest information density per token
2. Deterministic machine parseability
3. Preservation of every current verification property
4. Zero-ambiguity verdict extraction
5. Compact reference to prior state
6. **Prose reserved for zones where reasoning risk demands it**

**The core insight:** compress the deterministic parts (structure,
routing, verdict codes, tool_runs, fold classification). Preserve
prose where reasoning-risk demands it (verdict rationale on S|D,
zoom-out asks, novel findings, Chris routing narratives). Never
compress the rationale — only the ceremony.

---

## 2. Analysis of current communication patterns (S2834-S2838 sample)

### 2.1 What information MUST always be exchanged (preserve)

| Category | Token cost per cycle | Compressible? |
|---|---:|---|
| Question topic + scope | ~200-400 | Partially (topic slug) |
| Verdict per question | ~10-20 | Yes (single char code) |
| Tool_runs (evidence) | ~200-800 | Partially (structured) |
| Rationale on S/D verdict | ~100-300 | **No — reasoning risk zone** |
| Fold classification | ~50-100 | Yes (class code) |
| Fold target (section, line) | ~30-60 | Yes (structured) |
| Anti-pattern challenges | ~100-200 | **No — reasoning risk zone** |
| Zoom-out asks + responses | ~200-500 | **No — reasoning risk zone** |
| Cross-cutting signals | ~100-300 | **No — reasoning risk zone** |
| Chris escalation reasoning | ~100-200 | **No — reasoning risk zone** |

### 2.2 What information is currently repeated unnecessarily (compress)

| Pattern | Frequency | Token cost | Compression path |
|---|---:|---:|---|
| Session/arc/thread/cycle framing | every message | ~100 | Envelope header |
| File path recitation (audit doc + scanner + outputs) | every cycle | ~150 | Paths dict (once) |
| "SIGN CYCLE N —" ceremonial title | every cycle | ~30 | Envelope `cyc=N` |
| Findings restatement from doc | every cycle | ~500-1500 | Section reference `§N.N` |
| Verdict labels "AGREE / DISAGREE / STRENGTHEN" | every Q | ~40 | Single chars A/D/S |
| "tool_runs (verbatim):" header | every Q | ~30 | Q-scoped structured field |
| "Reply with verdict" imperative | every routing | ~50 | Implicit in envelope `act=SIGN` |
| Cycle-2 fold summary in cycle-3 | every close | ~300-800 | Fold ledger reference |
| "Anti-rubber-stamp verified" narration | every close | ~50 | ARS-VERIFIED flag |
| Politeness / conversational filler | every cycle | ~30-60 | Removed |

**Estimated total waste per cycle: 800-2500 tokens (60-75% of message).**

### 2.3 What should remain human-readable (never compress)

- **Verdict rationale on S|D** — the *why* behind challenging/strengthening
- **Zoom-out asks** — open-ended questions that pressure-test framing
- **Novel findings** — anything not yet in the audit doc
- **Cross-cutting signals** — patterns spotted mid-cycle
- **Chris routing recommendations** — the joint D-verdict routing message
- **Anti-pattern challenges** — explicit framing challenges

These are the **reasoning-risk zones**. Compressing them would risk
subtle loss of semantic content that the verification chain depends
on. AEP designates these as `PROSE_FIELD` — natural language,
uncompressed, delimited so they remain machine-parseable but
uncompressed internally.

---

## 3. Mandatory message schema

### 3.1 Envelope header (all messages)

```
AEP/0.1 sess=<N> arc=<N> thd=<T> cyc=<N> pin=<pa-...> dir=<CD→RGB|RGB→CD> act=<SIGN|ROUTE|FOLD|ESC|CLOSE>
```

Fields:
- `sess` — session number (int)
- `arc` — arc group number (int; e.g. 2800)
- `thd` — thread code (`T1`, `T2`, `T3a`, `T3b`, `T4`, `T5`, `PARENT`, `CLOSE`)
- `cyc` — SIGN cycle number (int; incremented per turn)
- `pin` — PA conversation pin
- `dir` — direction (`CD→RGB` = Claude to Rigby; `RGB→CD` = reverse; `CD→CH` = Claude to Chris via Rigby)
- `act` — action class (`SIGN` = pressure-test; `ROUTE` = to-Chris routing; `FOLD` = fold-record; `ESC` = escalation; `CLOSE` = arc/session close)

### 3.2 Paths dict (routing messages)

Referenced files declared once at message top; subsequent references use short-form keys:

```
paths:
  doc: docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md
  scan: tools/audit_2804_handoff_citation_integrity.py
  out: /tmp/t4_handoff_audit_out.json
  seed_t2: /tmp/t2_scan_out.json
  seed_t3b: /tmp/t3b_orphan_scan_out.json
  parent: docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md
```

Subsequent references: `§doc:2.5`, `§scan:150-200`, `§out:sub_loop_c_handoff_hits`.

### 3.3 Refs to prior state (routing messages)

```
refs:
  prev_cycles: [1, 2]      # cycle numbers already exchanged in this pin
  prev_folds: [F1, F2, F3] # fold IDs from prior cycles (in fold ledger)
  parent_sess: 2837        # prior close session
  substrate: [T2, T3b]     # consumed pre-clustering scans
```

### 3.4 Question block (SIGN messages)

Per question, mandatory fields:

```
Q<N>:
  topic: <slug>                              # e.g. severity_taxonomy, probe_query_set
  claim: <compact-claim>                     # 1-line assertion the Q tests
  expect: <verdict|verdict+evidence|verdict+prose>
  verify_via: <tool-list>                    # e.g. repo_tool.read(§doc:14-20), jq(§out.field)
  prose_zone: <optional; used for zoom-out>
```

Optional fields:
- `substrate_ref:` — reference to prior fold or Q
- `deferral_note:` — if question is intentionally deferred to later cycle
- `escalation_class:` — if answer might route to Chris

### 3.5 Response block (SIGN messages, RGB→CD)

Per question, mandatory fields:

```
Q<N>: <verdict> | evidence: <tool_runs> | <fold_or_reroute>
```

Where:
- `<verdict>` ∈ {A, D, S, F, R} (single-char)
- `evidence:` — structured tool_runs; each item = `<tool>(<args>) → <result-summary>`
- On S|D: `reason:` field MANDATORY (PROSE_FIELD zone; no compression)
- On R (re-route): `gap:` + `reroute_directive:` MANDATORY
- On F (defer): `defer_to_cycle:` MANDATORY

### 3.6 Fold ledger block (append-only per cycle)

Structured record of every fold created in this cycle:

```
folds:
  - id: F<N>          # sequential per pin conversation
    q: Q<N>           # source question
    class: <fold-class>
    target: §<paths-key>:<section>
    body: <compact-fold-description-or-PROSE_FIELD>
```

`fold-class` codes:
- `SPM` — same_pr_mitigatable (fold into current doc same PR)
- `FT` — future_trigger (record for future arc; no current-arc action)
- `NR` — needs_review (defer to Chris judgment at 2899 workshop)
- `OS` — out_of_scope (record then drop)

### 3.7 PROSE_FIELD delimiter

Zones that require natural language are delimited:

```
<<<PROSE
[free-form English content — no character-level compression;
 preserves reasoning, verdicts on S|D, zoom-out asks and answers,
 novel findings, Chris routing narratives]
PROSE>>>
```

Machine-parseable by delimiter; human-readable inside.

### 3.8 Anti-rubber-stamp gate

Every SIGN response MUST include one of:

- `ars: [ARS-VERIFIED evidence=<N-tool-runs>]` — at least N ≥ 1 tool run verified
- `ars: [ARS-PENDING gap=<description>]` — explicit re-route required
- `ars: [ARS-INAPPLICABLE q_type=zoom_out]` — Q was zoom-out (prose judgment, no tool required)

This field is **mandatory + enforceable** at protocol layer, replacing
today's implicit `feedback_verify_rigby_tool_runs_before_trusting_sign`
inspection discipline.

---

## 4. Optional message schema

### 4.1 Substrate consumption declaration (arc-open messages)

```
consumes_pre_clustering:
  - substrate: T2
    path: §paths:seed_t2
    contract: "load-only; do NOT re-derive"
  - substrate: T3b
    path: §paths:seed_t3b
    contract: "load-only per §5.4 T5 workflow directive"
```

### 4.2 Session context carry-over (session-open messages)

```
carry_forward:
  - id: CF1
    class: policy_carryover      # e.g. S2836 arc-close deferral policy
    ref: <memory-key or feedback-slug>
  - id: CF2
    class: substrate_available
    paths: [§paths:t2, §paths:t3b, §paths:t4]
```

### 4.3 Deferral / escalation queue update

```
escalate_queue:
  cumulative: 99
  this_cycle: 22
  breakdown:
    P1_path_form: 6
    P2_retrieval_harm: 13
    P2_fragment_form: 3
```

---

## 5. Standard field definitions

| Field | Type | Semantics |
|---|---|---|
| `sess` | int | Session number |
| `arc` | int | Arc group number (Group 2800 etc) |
| `thd` | string | Thread code (`T1`..`T5`, `PARENT`, `CLOSE`) |
| `cyc` | int | SIGN cycle number within pin |
| `pin` | string | PA conversation pin identifier |
| `dir` | enum | Direction (`CD→RGB`, `RGB→CD`, `CD→CH`, `RGB→CH`) |
| `act` | enum | Action class (`SIGN`, `ROUTE`, `FOLD`, `ESC`, `CLOSE`) |
| `verdict` | enum | `A`, `D`, `S`, `F`, `R` |
| `evidence` | list | Structured tool_runs |
| `fold_class` | enum | `SPM`, `FT`, `NR`, `OS` |
| `severity` | enum | `P0`, `P1`, `P2`, `P3` (unchanged from §10.1) |
| `action` | enum | 8-action taxonomy (unchanged from §10.1) |
| `ars` | enum | `ARS-VERIFIED`, `ARS-PENDING`, `ARS-INAPPLICABLE` |
| `PROSE_FIELD` | delimited | Reasoning-risk zone; uncompressed |

---

## 6. Proposed abbreviations / symbols

### 6.1 Verdict codes

| Long form | AEP code |
|---|---|
| AGREE | `A` |
| DISAGREE | `D` |
| STRENGTHEN | `S` |
| DEFER | `F` |
| RE-ROUTE | `R` |

### 6.2 Role codes

| Long form | AEP code |
|---|---|
| Claude Code | `CD` |
| Rigby (PA) | `RGB` |
| Chris | `CH` |

### 6.3 Direction symbols

- `→` (U+2192) — "to" (e.g. `CD→RGB`)

### 6.4 Fold classification codes

| Long form | AEP code |
|---|---|
| same_pr_mitigatable | `SPM` |
| future_trigger | `FT` |
| needs_review | `NR` |
| out_of_scope | `OS` |

### 6.5 Section reference syntax

- `§doc:2.5` — section 2.5 of doc file (paths-key `doc`)
- `§out.sub_loop_c` — JSON path expression against paths-key `out`
- `§scan:L200-L250` — line range in scanner file
- `§corpus.file_cite.BROKEN_404` — schema field reference

### 6.6 Cross-doc reference syntax

- `→T2 §5.6` — cross-child thread reference (already established convention)
- `←T3b §5.4` — inbound consumption of prior-child substrate

---

## 7. Example: current vs AEP exchange

### 7.1 Current SIGN Cycle 1 outbound (CD→RGB), estimated ~800 tokens

```
SIGN CYCLE 1 — S2838 T4 handoff citation-integrity + retrieval-harm audit joint SIGN pressure test.

Audit doc (896 lines): docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md
Scanner (550 lines): tools/audit_2804_handoff_citation_integrity.py
Scanner output: /tmp/t4_handoff_audit_out.json
Consumed pre-clustering: /tmp/t2_scan_out.json + /tmp/t3b_orphan_scan_out.json

**Findings headline (§2.1):** Zero P0. Handoff citation surface small (145 path-form + 17 short-form = 162 edges across 1061 handoffs); 90.3% of citations trace to anchor-reachable canonical docs (T3b cited-multi-graph-OK); 89.6% of handoffs never cited (write-once-terminal healthy state); decay curve peaks at recent S2500-2999 (26.8%) and S1000-1499 (17.7%).

**Sub-loop (b) empirical falsification:** Only 3 fragment-form citations exist corpus-wide; all 3 broken; ZERO #K chunk-ID form citations. Parent §4 T4 concern about post-1143 chunk-ID reset breaking #K fragments is EMPIRICALLY UNFOUNDED at current corpus state.

[... 4 more sections of findings restated ...]

Route 5 questions with tool-grounded verification. Any AGREE verdict without tool_runs = insufficient; route again with explicit tool directives. Include Q5 zoom-out per feedback_zoom_out_ask_per_rigby_sign.

**Q1 — severity taxonomy (verify via tool):** T4 uses 5-class severity (broken_citation_path_form / broken_citation_short_form / retrieval_harm_candidate / citation_healthy / uncited_never_retrieved). Should broken_citation_short_form split into prose_ref (P3 keep) vs link_form_ref (P2 fix)? VERIFY: repo_tool.read docs/HANDOFF_NUMBERING_GAPS.md line 14-20 to confirm prose-ref shape + inspect 3 T2 short-form BROKEN_404 entries in /tmp/t2_scan_out.json to confirm none are markdown-link-form.

[Q2, Q3, Q4, Q5 similarly verbose]
```

### 7.2 Equivalent AEP Cycle 1 outbound (CD→RGB), estimated ~250 tokens

```
AEP/0.1 sess=2838 arc=2800 thd=T4 cyc=1 pin=pa-683fb793ab944cd0 dir=CD→RGB act=SIGN

paths:
  doc: docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md
  scan: tools/audit_2804_handoff_citation_integrity.py
  out: /tmp/t4_handoff_audit_out.json
  t2: /tmp/t2_scan_out.json
  t3b: /tmp/t3b_orphan_scan_out.json

refs: {substrate: [T2, T3b], findings_head: §doc:2.1, prev_cyc: null}

require: ars∈{ARS-VERIFIED, ARS-PENDING}; on S|D reason MANDATORY (PROSE_FIELD)

Q1: topic=severity_taxonomy
  claim: 5-class taxonomy; consider split short_form→prose_ref|link_form
  verify_via: repo_tool.read(HANDOFF_NUMBERING_GAPS.md:L14-20) + jq(§t2:results[].findings[]|select(.ref_class=="session" and .status=="BROKEN_404"))|.[0:3]

Q2: topic=probe_query_set
  claim: 10 heuristic queries; ask for operator-hot additions
  verify_via: search_docs(<proposed>, k=8) → report handoff hits

Q3: topic=banner_rank_threshold
  claim: 12 hits across rank 1-8; consider filter to rank 1-3
  verify_via: jq(§out:sub_loop_c_handoff_hits) → similarity elbow?

Q4: topic=corpus_delta
  claim: 1061 handoff; S2837 pointer said 1058; +3 unexplained
  verify_via: find(docs/handoffs -name '*.md' | wc -l) + git log --diff-filter=A --since='2026-07-18' -- docs/handoffs/

Q5: topic=zoom_out
  <<<PROSE
  Parent §4 T4 spec said "citation-integrity + retrieval-harm audit."
  T4 as-authored measures citation-graph SHAPE + top-K RETRIEVAL. The
  underlying operator concern: how much operator-time is currently lost
  to Rigby returning stale handoff context for live operational queries?
  Is current shape correct (graph size small enough that shape IS the
  finding + banner recommendation IS actionable), or would behavioral
  measurement produce more actionable finding worth splitting into
  separate post-2899 audit thread?
  PROSE>>>
```

**Token reduction: ~68% (800 → 250).** Every semantic bit preserved.
Q5 zoom-out retains full prose (reasoning-risk zone).

### 7.3 Current SIGN Cycle 1 response (RGB→CD), estimated ~1500 tokens

```
## Q1 — severity taxonomy
**Verdict:** **STRENGTHEN** (but **cannot certify** without the /tmp JSON evidence you requested)

**What I can verify right now**
- `HANDOFF_NUMBERING_GAPS.md` is clearly **prose-purpose text** ("Action: none…") and not a link-form citation. That supports the idea that at least *some* "BROKEN_404 short-form" flags can be legitimate prose refs.
**tool_runs (verbatim):**
- `repo_tool.read_file path=docs/HANDOFF_NUMBERING_GAPS.md start_line=13 max_lines=15` → shows lines 16–28 incl. "Status: intentional… Action: none." (see returned content)

**What I cannot verify yet (required by your question)**
- "inspect 3 T2 short-form BROKEN_404 entries in /tmp/t2_scan_out.json" — that file is not accessible via `workspace_tool.read` from this environment...

[continues verbose per Q2-Q5]
```

### 7.4 Equivalent AEP Cycle 1 response (RGB→CD), estimated ~400 tokens

```
AEP/0.1 sess=2838 arc=2800 thd=T4 cyc=1 pin=pa-683fb793ab944cd0 dir=RGB→CD act=SIGN

Q1: S | ars=ARS-PENDING(partial)
  evidence: [repo_tool.read(HANDOFF_NUMBERING_GAPS.md:L14-28) → "Status: intentional; Action: none" = prose_ref]
  gap: §t2 access blocked (workspace_tool.read → File not found: /tmp/*)
  reroute_directive: claude_code_tool must extract 3 samples via shell
  reason: <<<PROSE
  Single sample supports prose_ref hypothesis; extrapolation to full 17
  requires shell-accessible eval which Rigby cannot execute.
  PROSE>>>

Q2: S | ars=ARS-VERIFIED(2 tool_runs)
  evidence:
    - search_docs(q="recycle-all make recycle-all stale daphne celery", k=8) → SESSION_2759_STALE_DAPHNE#{1-4} handoff prominent
    - search_docs(q="governor throttle freeze safe_mode autonomy mode kill switch", k=8) → EMPLOYEE_OS_PRIMITIVES#4 + 1903_authority_enforcement_cat_c#9 canonical
  props: [recycle_all_ops_recovery, governor_control_plane]
  fold: {class: SPM, target: §doc:2.5, add: SESSION_2759 to banner list}

Q3: R | ars=ARS-PENDING(tool_access_gap)
  gap: §out access blocked (workspace_tool.read /tmp inaccessible)
  reroute_directive: claude to inspect similarity distribution via jq shell

Q4: R | ars=ARS-PENDING(tool_access_gap)
  gap: shell git-log unavailable in RGB surface
  reroute_directive: claude to run find + git log --diff-filter=A

Q5: S | ars=ARS-INAPPLICABLE(q_type=zoom_out)
  <<<PROSE
  T4's framing decomposes into (1) citation-graph shape + (2) probe-query
  retrieval. Correct structural first-order question — bounds problem size,
  falsifies speculative risks, produces actionable banner queue.

  T4 does NOT measure behavioral concern: "how many operator minutes are
  lost to stale-handoff retrieval." Requires instrumentation (query-log
  sampling / conversation correction proxy). No available proxy at current
  substrate.

  Recommendation: keep T4 outputs as 2899 workshop input. Record follow-on
  audit-thread proposal as future_trigger for post-2899 Chris arc-open
  evaluation. Two substrate candidates: (a) operator query log sampling;
  (b) conversation correction proxy.
  PROSE>>>
  fold: {class: FT, target: §doc:5.7a, class_addendum: scope-creep guardrail sentence}

folds_this_cycle:
  - F1: {q: Q2, class: SPM, target: §doc:2.5, delta: +SESSION_2759 banner}
  - F2: {q: Q2, class: FT, target: §doc:5.7, delta: +2 canonical probe queries}
  - F3: {q: Q5, class: FT, target: §doc:5.7a, delta: follow-on audit thread proposal}
```

**Token reduction: ~73% (1500 → 400).** Verdict, evidence, and folds
all preserved. Reasoning-risk zones (Q1 reason + Q5 zoom-out) remain
in full prose. ARS gate enforced at protocol layer.

---

## 8. Migration strategy

### 8.1 Proposed 3-stage rollout (NOT authorized; Chris to review)

**Stage 0 — Ratification (this doc):**
- Chris reviews AEP v0.1 proposal
- Chris D-verdict: ratify | reject | request-revisions
- No code changes; no prompt changes; no workflow changes

**Stage 1 — Opt-in trial (post-ratification, if approved):**
- Trial in ONE session's SIGN cycles (e.g., S2839 T5 cycle 1)
- Claude Code emits AEP; asks Rigby to respond in AEP
- Prose fallback allowed if either agent can't parse
- Compare: token count, verdict extraction accuracy, ARS gate enforcement, fold ledger completeness
- No downstream changes (audit doc, ratification envelope, workspace mirrors all remain human-oriented markdown)

**Stage 2 — Broader adoption (if Stage 1 shows ≥50% token reduction + 0 verification-check failures):**
- Adopt for all Claude+Rigby SIGN exchanges
- Legacy prose still accepted (backward-compat)
- Downstream artifacts (audit docs, envelopes) still emitted as human-readable markdown
- After 4-trigger corroboration per Playbook §14 → propose Playbook amendment

**Stage 3 (future, post-corroboration):**
- Playbook amendment: codify AEP v0.1 as SIGN-cycle communication standard
- Add ARS-VERIFIED / ARS-PENDING / ARS-INAPPLICABLE enforcement at protocol layer
- Retire the implicit `feedback_verify_rigby_tool_runs_before_trusting_sign` runtime discipline in favor of enforceable protocol gate

### 8.2 Backward compatibility guarantees

- Both agents accept legacy prose SIGN format indefinitely (no removal)
- Downstream artifacts (audit docs, envelopes, handoffs, workspace mirrors) remain markdown
- Chris-facing routing messages remain natural language (`act=ROUTE` uses PROSE_FIELD by default)
- Cross-session pin conversations can mix AEP + prose without semantic drift
- Playbook, memory, feedback rules unchanged during Stages 0-2

### 8.3 What does NOT migrate to AEP (permanent prose zones)

- `docs/research/domains/**` audit docs
- `docs/research/implementation/RATIFICATION_*.md` envelopes
- `docs/handoffs/**` handoffs
- `docs/research/OPEN_ARCS.md` narrative rows
- `CLAUDE.md` session-history banner
- `00-START-NEXT-SESSION.md` pointer
- Workspace deliverable bodies
- Chris-facing routing messages (`act=ROUTE`)

These are **human-consumption artifacts**. AEP is a
machine-to-machine transport layer, not a documentation format.

---

## 9. Risks

### 9.1 Semantic loss on compressed fields

- **Risk:** compressing verdict rationale on S/D verdicts loses subtle framing signal.
- **Mitigation:** verdict rationale is a MANDATORY `PROSE_FIELD` on S|D; no character-level compression allowed.
- **Residual risk:** LOW.

### 9.2 Parser divergence between agents

- **Risk:** Claude and Rigby parse AEP differently, silently drift semantics.
- **Mitigation:** Stage 1 trial includes side-by-side comparison of extracted verdicts / folds / ARS states.
- **Residual risk:** MEDIUM until parser tests validated.

### 9.3 Anti-rubber-stamp gate regression

- **Risk:** ARS-VERIFIED becomes rubber-stamped ("just add the tag").
- **Mitigation:** ARS-VERIFIED requires **structured `evidence:` list with tool + args + result-summary**. Empty evidence with ARS-VERIFIED = protocol violation.
- **Residual risk:** LOW; matches or improves current implicit-inspection discipline.

### 9.4 Zoom-out ask quality degradation

- **Risk:** `Q5: topic=zoom_out` becomes a checkbox instead of substantive challenge.
- **Mitigation:** zoom-out Q inside `<<<PROSE ... PROSE>>>` block; response requires `<<<PROSE`; ARS-INAPPLICABLE(q_type=zoom_out) explicit.
- **Residual risk:** LOW (same risk exists in prose format; not worsened).

### 9.5 Chris readability loss

- **Risk:** Chris can't skim SIGN cycles because format is machine-oriented.
- **Mitigation:** Chris does NOT consume raw SIGN cycles today; consumes joint routing message (`act=ROUTE`) which stays PROSE_FIELD. Chris also consumes downstream artifacts (audit docs, envelopes, handoffs) which stay markdown.
- **Residual risk:** ZERO if Stage 2 adoption preserves `act=ROUTE` as prose.

### 9.6 Overhead > gains on small messages

- **Risk:** AEP envelope header adds ~30 tokens; for tiny messages (~100 tokens total) this is overhead.
- **Mitigation:** AEP-adoption threshold: messages > 200 tokens; smaller messages stay prose.
- **Residual risk:** LOW; small-message case is rare (SIGN cycles are always > 500 tokens).

### 9.7 Fold ledger under-recording

- **Risk:** compact fold syntax `{q, class, target, delta}` misses subtlety captured in prose fold descriptions.
- **Mitigation:** fold `body:` is optional PROSE_FIELD; use when compression loses semantics.
- **Residual risk:** LOW.

### 9.8 Future_trigger drift

- **Risk:** `class: FT` fold entries accumulate without proper Playbook §14 corroboration tracking.
- **Mitigation:** current corroboration-tracking discipline is unchanged; FT class in fold ledger is IDENTICAL in semantics to today's `future_trigger` prose.
- **Residual risk:** ZERO.

### 9.9 Backward-compat break at agent version boundaries

- **Risk:** future Claude model or Rigby update breaks AEP parsing.
- **Mitigation:** version stamp in envelope (`AEP/0.1`); agents check version; unrecognized versions fall back to prose.
- **Residual risk:** LOW.

### 9.10 Adoption without Playbook amendment

- **Risk:** AEP adopted at Stage 2 without Playbook amendment creates governance mismatch (protocol not codified).
- **Mitigation:** Stage 3 explicitly gates on Playbook amendment per §14 four-trigger threshold; adopt-first, codify-after is the CD-50 pattern (S2740) and matches current Playbook methodology.
- **Residual risk:** ZERO; matches existing constitutional-change pattern.

---

## 10. What is NOT changed (explicit non-goals reiteration)

Per Chris's constraints:

- ❌ NO Playbook edits proposed
- ❌ NO workflow changes proposed
- ❌ NO prompt / constitution / schema modifications proposed
- ❌ NO platform behavior changes proposed
- ❌ NO implementation authorized
- ❌ NO retroactive migration of prior SIGN cycles
- ❌ NO downstream artifact format changes (audit docs, envelopes, handoffs stay markdown)
- ❌ NO Chris-facing message format changes (routing messages stay prose)
- ❌ NO memory / feedback rules changed
- ❌ NO SIGN discipline weakened (ARS gate strengthened, not weakened)

---

## 11. Recommendation

**Ratify AEP v0.1 as design proposal** with Stage 1 trial authorization at S2839 T5 cycle 1 SIGN, gated on:

1. Chris explicit D-verdict authorizing Stage 1 trial
2. Both agents opt-in to AEP format for that one cycle
3. Prose fallback available if either agent can't parse
4. Post-cycle-1 evaluation: measure token count, verdict-extraction accuracy, ARS gate enforcement, fold ledger completeness
5. If Stage 1 shows ≥50% token reduction + zero verification-check failures, propose Stage 2 authorization for full-arc use
6. If Stage 1 shows regressions, discard proposal + document lessons learned in a new `docs/research/platform/AGENT_EXCHANGE_PROTOCOL_v0_1_evaluation.md`

**Alternative recommendations:**

- **Reject:** current prose format acceptable; token cost tolerable; complexity not warranted. Discard proposal.
- **Revise:** issue specific revision requests (e.g., different verdict codes, different envelope structure, different PROSE_FIELD delimiters). Claude re-drafts v0.2.
- **Defer:** hold proposal until post-Group 2800 arc close (2899) to avoid mid-arc protocol change. Revisit S2900+.

**Claude's judgment:** the token cost is real (recent S2838 cycles
consumed ~5000 tokens per SIGN cycle × 3 cycles × 6 threads × 6-8
sessions per arc = ~500k+ tokens on Rigby↔Claude ceremony per arc).
AEP would save ~60-70% of that. But the design is untested; Stage 1
trial is the right risk-managed adoption path.

---

## 12. Cross-links

- `docs/ENGINEERING_PLAYBOOK.md` — v0.8.0 (governance frame; no amendment proposed)
- `docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md` — S2838 T4 (source of most-recent SIGN cycle sample)
- `docs/handoffs/SESSION_2838_T4_HANDOFF_CITATION_INTEGRITY_AUDIT.md` — S2838 handoff (SIGN-cycle patterns visible in §5)
- `feedback_verify_rigby_tool_runs_before_trusting_sign` (memory) — current implicit ARS discipline
- `feedback_zoom_out_ask_per_rigby_sign` (memory) — Q5 zoom-out discipline preserved via PROSE_FIELD
- `feedback_claude_directs_rigby_then_verifies` (memory) — collaboration shape unchanged; only communication format changes
- `feedback_claude_rigby_agree_first_chris_yes_no` (memory) — routing to Chris stays prose (`act=ROUTE`)
- `feedback_read_full_rigby_response_not_just_tail` (memory) — PROSE_FIELD delimiter makes tail-only-parsing safe (nothing outside delimiters carries body content)

---

## Appendix A — Estimated token savings per arc

Recent S2838 T4 arc measurements:
- 3 SIGN cycles × avg ~4500 tokens per cycle (outbound + inbound) = ~13500 tokens
- AEP equivalent: ~4500 tokens (70% reduction)
- Saving per arc: ~9000 tokens

Group 2800 arc (6 children + parent + close = 8 sessions × 3 cycles):
- Current cost: ~108000 tokens on SIGN ceremony
- AEP cost: ~36000 tokens
- Saving: ~72000 tokens per Group arc

Extrapolated across future arcs (assuming 6-arc per quarter):
- Saving: ~432000 tokens per quarter
- Cost saving depends on model pricing; illustrative only

---

## Appendix B — Open design questions for Chris review

1. **Verdict code choice:** single-char (`A/D/S/F/R`) vs 3-char (`AGR/DIS/STR/DEF/REO`)?
2. **Envelope header line length:** should envelope wrap or stay one-line?
3. **PROSE_FIELD delimiter choice:** `<<<PROSE ... PROSE>>>` vs Markdown fence \```prose ... ```?
4. **Fold ledger persistence:** per-cycle only, or accumulated across pin lifetime?
5. **ARS-VERIFIED threshold:** minimum tool_run count = 1, or context-dependent?
6. **Zoom-out ARS gate:** ARS-INAPPLICABLE the right escape, or should zoom-out require a prose-quality gate instead?
7. **Chris routing format:** `act=ROUTE` stays 100% prose, or partial-structure allowed (e.g., verdict-summary at top)?
8. **Backward-compat sunset:** ever, or forever?
9. **Corroboration threshold for Stage 3 Playbook amendment:** default 4 triggers (per Playbook §14 default), or different?
10. **Stage 1 trial length:** single cycle, single session, single arc, or single quarter?

---

**End of proposal. Chris to review + D-verdict.**
