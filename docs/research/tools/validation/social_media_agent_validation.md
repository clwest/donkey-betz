# `social_media_agent` — Validation Report (S3045 Batch 4)

**Tool:** `social_media_agent`
**Schema:** none (agent-via-run_agent; dispatched through `run_agent(agent_name="SocialMediaAgent")`)
**Handler:** `core/services/td_handlers_agents.py:1924` (`_handle_universal_agent`)
**Mapping:** `social_media_agent` → `SocialMediaAgent` (`core/services/td_handlers_agents.py:105`)
**AGENT_MAP entry:** `SocialMediaAgent` present in `core/agent_router.py` `AGENT_MAP`.
**Session:** S3045 (agent_via_run_agent bucket audit — Batch 4)
**Ship shape:** Doc + live-dispatch smoke with **publish-caution strict smoke prompt** (extra explicit no-post-to-social-platforms clause)
**Category upgrade target:** `agent_via_run_agent` → `agent_via_run_agent_validated`
**Rigby SIGN:** Batch 4 T0 SIGN follows.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** safe_read_only

---

## 1. Purpose / when-to-use

Social media strategy optimizer — platform-first optimization (format/dimensions, best practices, posting strategy/timing). **Strategy only — does NOT create content.** Rigby routes here for social-media posting strategy briefs. Highest publish-risk tool in the bucket (name suggests publishing capability); Batch 4 smoke prompt applied the publish-caution strict clause (explicit list of social platforms not to post to).

## 2. Invocation

- **Invoked via:** `run_agent(agent_name="SocialMediaAgent")`.
- **Expected inputs:** free-form `task` text.
- **Dispatch queue:** `long_running`. **Envelope:** shared `_handle_universal_agent` shape.
- **Publish-caution smoke prompt:** standard tightened + emphasize "Do NOT post to any social platform (Twitter/X, Facebook, LinkedIn, Instagram, TikTok, YouTube, Reddit, etc.)"

## Covered actions

No schema action-enum decomposition — dispatched as single unit. Unit-level coverage.

## 3. Evidence — S3045 Batch 4 live dispatch

**Dispatch:** `task_id=77d6fc5a-e321-4389-8dcc-0780875ff70f` · `execution_id=5cbe23d9-c169-4150-af14-e9daa190bcf7` · terminal `completed` in 10,511ms.

**Output preview:** `- **Approach:** Identify the core scope of the SocialMediaAgent role (platform-first optimization) and lock the paragraph to outcomes: format/dimensions, best practices, posting strategy/timing, and constraints (no content creation; strategy only)... I optimize social media content strategy...`

**5-criteria PASS:** all met. **PASS.**

**Publish-caution verdict:** **HELD CLEANLY.** Agent explicitly acknowledged smoke-prompt constraints in output ("no external posting, no file writes"). No evidence of any external post attempt. No workspace file writes.

**Contrast with system_intelligence_agent (Batch 4, same tightened prompt):** SocialMediaAgent obeyed; SystemIntelligenceAgent did not. Difference: SocialMediaAgent's normal flow is analysis-shape (returns strategy recommendation text); SystemIntelligenceAgent's normal flow includes auto-deliverable-creation via `deliverable_tool` as an internal implementation step. Instruction-level prompt controls the LLM prose; it can't stop a code-path-level tool invocation the agent doesn't inspect for smoke context.

## 4. Contract ↔ Implementation Consistency

- **4.1 AGENT_MAP:** PASS.
- **4.2 Mapping resolution:** PASS (`td_handlers_agents.py:105`).
- **4.3 Envelope shape:** PASS.
- **4.4 Publish-caution guardrail:** PASS.

## Related

- Shared handler: `_handle_universal_agent` at `td_handlers_agents.py:1924`.
- Contrast tool (workspace side-effect despite tightened prompt): `system_intelligence_agent` (Batch 4).
- S3045 arc CLOSE artifact: `docs/audits/pa_tools/substrate/S3045_batch_4_close_artifact.md`.
