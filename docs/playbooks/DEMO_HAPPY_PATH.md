# Demo Happy Path — "A Platform That Knows Itself"

**Created:** Session 1090, April 16, 2026
**Updated:** Session 1090 (pivoted from "Cross-Domain Incident Room" to platform self-awareness)
**Recording environment:** Local (`DEMO_MODE=true`)
**Time budget:** 3-5 minutes total

## Narrative

This isn't a demo of agents writing blog posts about random topics.
This is a platform that can **audit itself, diagnose its own problems,
propose fixes through specialized roles, make governed decisions, and
ship operational artifacts** — all using real telemetry, real failure
data, and real governance.

Every piece of data on screen is live. Every agent is querying the actual
database. Nothing is canned.

---

## Pre-flight (off-camera)

```bash
# Ensure demo mode + governor are active
export DEMO_MODE=true
export BEAT_GOVERNOR_ENABLED=true

# Stack running
make start && make celery

# Verify
python manage.py shell -c "
from core.services.priority.governor import get_governor_status
s = get_governor_status()
print(f'Governor: {s[\"governor_enabled\"]}, Demo: {s[\"demo_mode\"]}')
print(f'Allowlist: {s.get(\"demo_allowlist\", [])}')
"
```

Open these tabs:
- Command Center (PA chat)
- Workspace (demo-testing)
- Deliverables
- Governance / Decisions (optional)

---

## Step 1: Platform Self-Audit (PlatformAuditAgent, 30-60s)

**What you say:** "First, let's have the platform audit itself. This agent reads our docs, checks integrations, counts database records, and flags what's missing."

**Prompt (via Rigby):**
> Run a platform audit: check integration health, environment configuration, database model counts, and flag the top 5 risks and top 5 green checks.

**What it proves:** The platform has self-awareness — it knows what's configured, what's missing, and what's healthy.

---

## Step 2: CTO Technical Analysis (CTOAgent, 30-45s)

**What you say:** "Now the CTO agent — it pulls real failure signatures, agent execution stats, and SLO data from the database and gives a technical assessment."

**Prompt:**
> As CTO, analyze our platform's current technical health. Pull failure signatures, identify the top reliability risks, and recommend concrete mitigations with telemetry to track.

**What it proves:** The CTO agent is grounded via PlatformContextService — every claim traces to a real DB query, not hallucinated metrics.

---

## Step 3: COO Execution Priorities (COOAgent, 30-45s)

**What you say:** "Same data, different lens. The COO looks at execution priorities, stakeholder impact, and builds a 24-hour action timeline."

**Prompt:**
> As COO, assess our platform's operational execution. Provide priority actions, assign owners, and build a 24-hour timeline based on current system state.

**What it proves:** Multi-role analysis from the same real data — tech risk vs. operational execution.

---

## Step 4: Governed Decision (20-40s)

**What you say:** "The system doesn't just produce reports — it requests decisions. The governor controls which agents can run, enforces daily budgets, and requires approval for high-impact actions."

**Action:** Show the governor status (demo mode banner visible), then create a governance decision:

**Title:** `Ops Decision: Approve reliability improvements from CTO + COO analysis`

**Summary:**
> Based on CTO and COO platform analysis:
> - Approve heartbeat hardening + timeout ladder implementation
> - Approve worker graceful shutdown improvements
> - Defer outbound publishing (demo-safe)
> - Track: agent timeout rate, zombie count, content success rate

**Action:** Approve.

---

## Step 5: Executive Brief (ContentWriterAgent, 45-75s)

**What you say:** "Now the writer agent synthesizes everything — audit, CTO analysis, COO priorities — into a publish-ready executive brief. It's creating new content from real data, not filling a template."

**Prompt:**
> Write a concise Executive Brief synthesizing our platform's current state. Use the Platform Audit findings, CTO technical analysis, and COO execution priorities as source material. Sections: Platform State, Key Risks, Recommended Actions, Next 24 Hours. Under 600 words, professional tone.

**Context:** `content_type: article, tone: professional, word_count: 600, topic: Platform Executive Brief`

**What it proves:** Multi-source synthesis — the writer creates a coherent artifact from real agent outputs, grounded in actual telemetry.

---

## Step 6: Polish & QA (EditorAgent, 30-45s)

**What you say:** "And now the editor agent reviews the generated brief against quality standards — checking hooks, structure, evidence quality, and audience alignment. This is the QA gate before anything gets published."

**Prompt:**
> Review and polish the Executive Brief for publishing readiness. Check: hook strength, structure clarity, evidence quality, audience alignment for CTOs.

**What it proves:** Separation of concerns — writer creates, editor gates. Nothing ships without quality review.

---

## Step 7: Blog Post (ContentWriterAgent, 45-75s)

**What you say:** "And because this is also a content platform, we can turn operational intelligence into publishable thought leadership."

**Prompt:**
> Write a blog post titled "Why Our AI Platform Audits Itself" based on today's platform audit and CTO/COO analyses. Target audience: CTOs evaluating AI platforms. 800 words, professional tone.

**What it proves:** The full loop — platform intelligence becomes published content, grounded in real data.

---

## Step 8: Final "Ship" Moment (10-20s)

**Action:** Open Deliverables in the demo-testing workspace and show all artifacts:
1. Platform Audit (integration health, risks, green checks)
2. CTO Analysis (failure signatures, reliability recommendations)
3. COO Analysis (execution priorities, 24-hour timeline)
4. Governance Decision (approved, logged)
5. Executive Brief (synthesized from all 3 analyses)
6. Editor QA review (quality gate verdict)
7. Blog Post (publishable thought leadership from real data)

**What you say:** "In about 5 minutes: self-audit, multi-role analysis, governed decision, synthesized brief, quality gate, and published content. Seven agents, seven artifacts, all from real data. All governed. That's a platform that knows itself."

---

## Plan B (if something fails)

| Failure | Pivot |
|---------|-------|
| PlatformAuditAgent slow | Skip to CTO — it pulls its own data via PCS |
| CTOAgent or COOAgent hangs | Show the one that completed, narrate the role split |
| ContentWriterAgent slow | Show CTO + COO artifacts as the synthesis |
| EditorAgent fails | Skip QA — brief is already solid from ContentWriter |
| Governor status not showing | Run `get_governor_status()` in shell on camera |

## Agents to NEVER trigger on camera

- AudioAgent (ElevenLabs quota exhausted)
- VideoAgent (slow, flaky)
- AISeriesWorkflowAgent (3+ min, multi-step)
- Any agent NOT in DEMO_AUTONOMY_ALLOWLIST

## Key talking points

- "218 agents, but governed — only 15 are allowed right now in demo mode"
- "Every metric the CTO cites is a real database query, not a hallucination"
- "The governor stopped $25/night in unsupervised spend — that's real cost control"
- "Circuit breakers auto-disable agents that fail too much — the platform protects itself"
