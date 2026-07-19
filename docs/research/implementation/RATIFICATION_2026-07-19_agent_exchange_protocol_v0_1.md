---
title: "Ratification envelope — AEP v0.1 design proposal (Chris commission + Chris D-verdict; Stage 1 trial authorized at S2839 T5 cycle 1)"
date: 2026-07-19
session: 2838
ratifier: Chris
verbatim_directive: "Go ahead"
target_doc: docs/research/platform/AGENT_EXCHANGE_PROTOCOL_v0_1_proposal.md
research_group: platform_architecture
thread: aep_v0_1
category: governance
deliverable_type: ratification_record
---

# S2838 (post-close extension) — AEP v0.1 design proposal RATIFICATION

## 1. Ratification statement

Chris D-verdict at S2838 close-cycle extension (2026-07-19):

> Go ahead

Chris D-verdict directly ratifies the AEP v0.1 design proposal
authored earlier this session at Chris's explicit commission.
Ratification is Stage 0 (proposal-only); Stage 1 trial is
authorized at S2839 T5 cycle 1 SIGN routing.

**Chris's original commission verbatim** (2026-07-19 S2838, post-T4 close):

> Before we open the next child audit (T5), I want to pause and
> evaluate something that has become increasingly apparent during
> the last several SIGN cycles.
>
> I believe Rigby and Claude are still communicating as if they are
> two humans writing reports to each other. That is not the system
> we are building.
>
> You are not trying to persuade each other.
> You are not writing documentation.
> You are not optimizing for human readability.
>
> You are two reasoning agents operating inside Donkey Betz, where
> the primary objective is accurate, deterministic, high-bandwidth
> state transfer with minimal ambiguity and minimal token usage.
>
> I want you to design (NOT implement) an Agent Exchange Protocol
> (AEP) for communication between you and Rigby.
>
> [full constraints + deliverable list preserved in proposal doc §0]

## 2. Scope of ratification

- **Ratified:** AEP v0.1 as a design proposal (Stage 0)
- **Ratified:** Stage 1 trial authorization at S2839 T5 cycle 1
  SIGN routing (single-cycle opt-in with prose fallback)
- **NOT ratified:** Stage 2 broader adoption (requires post-trial
  evaluation showing ≥50% token reduction + zero verification-check
  failures)
- **NOT ratified:** Stage 3 Playbook amendment (requires 4-trigger
  corroboration per Playbook §14)
- **NOT ratified:** any code changes, workflow changes, prompt
  changes, schema changes, or platform behavior changes
- **NOT ratified:** retroactive migration of prior SIGN cycles
  (AEP applies forward from Stage 1 trial only)
- **NOT ratified:** changes to downstream artifact formats (audit
  docs, envelopes, handoffs, workspace mirrors, Chris-facing
  routing messages remain their current formats)

## 3. Chris's constraints (verbatim, from commission)

- No behavior changes
- No reasoning changes
- No governance changes
- No Playbook edits
- No implementation
- Preserve backward compatibility where practical

All 6 constraints are preserved in the ratified v0.1 proposal:

1. **No behavior changes** — AEP is a communication format only;
   underlying agent behavior (Claude's reasoning, Rigby's tool
   dispatch) unchanged
2. **No reasoning changes** — verdict semantics (AGREE/DISAGREE/
   STRENGTHEN/DEFER/RE-ROUTE) preserved; PROSE_FIELD zones protect
   reasoning-risk areas from compression
3. **No governance changes** — SIGN discipline, D-verdict pattern,
   arc-close deferral policy, escalation workflows all unchanged
4. **No Playbook edits** — proposal explicitly non-goal; Stage 3
   Playbook amendment gated on 4-trigger corroboration per §14
5. **No implementation** — Stage 0 proposal only; Stage 1 trial is
   opt-in message format usage, not code change
6. **Backward compatibility preserved** — prose format accepted
   indefinitely; downstream artifacts remain markdown; Chris-facing
   messages remain prose; version stamp `AEP/0.1` allows agent
   version compatibility checks

## 4. Anti-rubber-stamp discipline for AEP itself

Chris directly commissioned + directly D-verdicted. No Rigby joint
SIGN cycle was required at Stage 0 per proposal-only scope. Rigby's
future role in AEP is:

- **Stage 1:** Rigby receives AEP-formatted SIGN routing at S2839
  T5 cycle 1; Rigby responds in AEP (per protocol schema)
- **Stage 1 post-trial:** Rigby participates in evaluation (token
  count, verdict extraction accuracy, ARS gate enforcement, fold
  ledger completeness)
- **Stage 3 (future):** if Playbook amendment proposed, Rigby joins
  full SIGN methodology per §14

**Rigby's absence from Stage 0 ratification does NOT weaken
verification:** the proposal explicitly strengthens the ARS gate
(protocol-layer enforcement) compared to today's implicit
`feedback_verify_rigby_tool_runs_before_trusting_sign` runtime
discipline.

## 5. Stage 1 trial protocol

At S2839 T5 cycle 1 SIGN routing:

1. Claude Code emits SIGN messages in AEP v0.1 format per §3 schema
2. Rigby is asked to respond in AEP v0.1 format
3. If either agent cannot parse AEP: prose fallback is authorized
   (no verification-chain break; no arc delay)
4. Both formats produce identical downstream audit-doc content
5. Post-cycle-1 evaluation (Claude, with Rigby's tool-verified
   input) measures:
   - Token count outbound (CD→RGB) — target ≥50% reduction
   - Token count inbound (RGB→CD) — target ≥50% reduction
   - Verdict extraction accuracy — target 100% (zero misparse)
   - ARS gate enforcement — target 100% (zero missing evidence
     on S|D verdicts)
   - Fold ledger completeness — target 100% (every fold that
     would exist in prose format exists in AEP fold ledger)
6. Deliverable at post-trial evaluation:
   - **If PASS all 5 metrics:** propose Stage 2 authorization for
     full-arc AEP use (S2839 T5 cycles 2+ and all future SIGN
     cycles)
   - **If FAIL any metric:** author
     `docs/research/platform/AGENT_EXCHANGE_PROTOCOL_v0_1_evaluation.md`
     documenting failures and lessons learned; discard AEP v0.1
     without prejudice against v0.2 revision

## 6. Post-ratification cascade (this envelope)

1. Envelope authored + committed with body commit SHA filled at merge
2. AEP proposal doc frontmatter updated: proposed → ratified with
   Chris verbatim directive block
3. `00-START-NEXT-SESSION.md` updated: Stage 1 AEP trial
   authorization flagged at S2839 T5 cycle 1
4. Twin workspace mirror: proposal doc + ratification envelope via
   Rigby PA `deliverable_tool.create` per
   `feedback_rigby_writes_workspace_deliverables` (fifth exercise)
5. Docs cascade: `build_docs_index` + `build_rag_corpus` +
   `sync_docs_index_to_documents` + `embed_documents --all-unembedded`
   per `feedback_docs_pipeline_4_step_cascade`
6. `build_docs_provenance` + `make recycle-all` post-merge per
   PLAYBOOK-7.4.4
7. Session pin fresh mint for cascade routing (short-lived) →
   retire at cascade close

## 7. Non-goals of this ratification (explicit)

- ❌ NO Playbook edits
- ❌ NO code changes
- ❌ NO workflow changes to SIGN, D-verdict, close-cascade
- ❌ NO changes to audit doc / envelope / handoff / workspace mirror formats
- ❌ NO changes to Chris-facing routing messages
- ❌ NO retroactive migration of prior SIGN cycles (S2834-S2838 remain in current prose format)
- ❌ NO changes to memory / feedback rules
- ❌ NO changes to Group 2800 T5 opening protocol (T5 opens at S2839 as previously ratified default; AEP is orthogonal Stage 1 trial)
- ❌ NO obligation on Rigby to respond in AEP — prose fallback available

## 8. What Stage 1 trial specifically tests

Per proposal §7.2 estimated ~68% outbound + ~73% inbound reduction on S2838 T4 cycle 1 sample. Stage 1 trial validates whether these estimates hold across:

- A fresh SIGN cycle (T5 cycle 1) with fresh context
- Rigby's actual parsing capability of `AEP/0.1` envelope
- Rigby's actual emission capability of AEP response format
- PROSE_FIELD delimiter recognition + preservation
- ARS gate enforcement (Claude's parsing of `ars=ARS-VERIFIED(evidence=N)`)
- Fold ledger completeness across cycle folds

Stage 1 does NOT test:
- Multi-cycle AEP durability (Stage 2 concern)
- Cross-arc AEP durability (Stage 2 concern)
- Playbook integration (Stage 3 concern)
- Chris-facing routing format changes (out of scope permanently)

## 9. Cross-links

- **Proposal doc:** `docs/research/platform/AGENT_EXCHANGE_PROTOCOL_v0_1_proposal.md` (~500 lines, status ratified)
- **Playbook:** `docs/ENGINEERING_PLAYBOOK.md` — v0.8.0 (unchanged; no amendment proposed)
- **S2838 T4 handoff:** `docs/handoffs/SESSION_2838_T4_HANDOFF_CITATION_INTEGRITY_AUDIT.md` (source of most-recent SIGN cycle sample used for §2 waste analysis)
- **§14 Playbook methodology:** Stage 3 Playbook amendment gate (four-trigger corroboration)
- **feedback_verify_rigby_tool_runs_before_trusting_sign** (memory) — current implicit ARS discipline that AEP §3.8 formalizes at protocol layer
- **feedback_zoom_out_ask_per_rigby_sign** (memory) — Q5 zoom-out discipline preserved via `PROSE_FIELD` + `ARS-INAPPLICABLE(q_type=zoom_out)`
- **feedback_claude_directs_rigby_then_verifies** (memory) — collaboration shape unchanged; only communication format changes
- **feedback_claude_rigby_agree_first_chris_yes_no** (memory) — Chris-facing routing stays prose (`act=ROUTE`) permanently
- **feedback_read_full_rigby_response_not_just_tail** (memory) — `PROSE_FIELD` delimiter makes tail-only-parsing safe (nothing outside delimiters carries body content)

## 10. Prohibitions carried forward

Same DO NOTs from S2838 T4 close apply, PLUS:

- DO NOT modify AEP v0.1 schema mid-Stage-1 trial (freeze until evaluation deliverable)
- DO NOT extend AEP format to Chris-facing routing messages (permanent scope boundary)
- DO NOT retroactively re-emit S2834-S2838 SIGN cycles in AEP (forward-only)
- DO NOT reduce ARS gate strictness under any circumstance (protocol-layer enforcement is a strengthening, not a weakening)
- DO NOT compress PROSE_FIELD zones under any circumstance (reasoning-risk zones are the load-bearing preservation guarantee)
- DO NOT propose Stage 2 authorization without post-Stage-1 evaluation showing ≥50% token reduction + zero verification-check failures (Chris gate)
- DO NOT propose Stage 3 Playbook amendment without 4-trigger corroboration per §14 (Playbook gate)
