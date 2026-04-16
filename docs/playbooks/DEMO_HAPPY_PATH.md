# Demo Happy Path — "Cross-Domain Incident Room"

**Created:** Session 1090, April 16, 2026
**Recording environment:** Local (`DEMO_MODE=true`)
**Time budget:** 3-5 minutes total

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
- Intelligence Desk / Search
- Governance / Decisions
- Agents / Run Agent
- Deliverables library

---

## Step 1: Prove "real signal" (10-20s)

**Action:** Spider search for a live signal.

**Prompt:**
> Search for a current signal about AI infrastructure demand, energy markets, or chip supply constraints. Return top 5 items with 1-line summary each.

**What to say:** "We start with live signals — real scraped feeds, not a canned prompt."

**Pick one result** that links AI infra to markets/energy.

---

## Step 2: Signal → Incident Card (ContentWriterAgent, 45-75s)

**Task prompt:**
> Create an "Incident Card" for: [paste selected signal].
> Format EXACTLY as:
> 1) Title (max 12 words)
> 2) What happened (3 bullets)
> 3) Why it matters (3 bullets)
> 4) Cross-domain impact map (Markets / Regulation / Tech / Ops) — 2 bullets each
> 5) What we should do in the next 24 hours (5 bullets, each starts with a verb)
> Keep it under 450 words.

**Context:** `content_type: article, tone: professional, word_count: 450`

**Say:** "This isn't just writing — this is a structured operating artifact."

---

## Step 3: Command Staff Briefs (CTO + COO, 60-90s total)

### 3A: CTO Brief (30-45s)

**Task prompt:**
> As CTO, assess technical implications and operational risks from this Incident Card.
> Provide: Risks (3), Unknowns (3), Immediate mitigations (3), and "What telemetry to check" (5 items).

### 3B: COO Brief (30-45s)

**Task prompt:**
> As COO, assess execution priorities and stakeholder impact from this Incident Card.
> Provide: Priority actions (5), Owners/roles for each, and a 24-hour timeline.

**Say:** "Same signal, two lenses — tech risk and operations execution."

---

## Step 4: Governed Decision (20-40s)

**Create a governance decision:**

**Title:** `Incident Response: Approve 24h monitoring + artifact ship for [Signal Title]`

**Summary:**
> Based on Incident Card + CTO/COO briefs:
> - Approve immediate monitoring checklist
> - Approve one publish-ready executive summary
> - Defer outbound/publishing automations (demo-safe)
> - Track: 3 KPIs for next 24h

**Action:** Approve.

**Say:** "The system doesn't just act. It requests a decision when it matters — governance is built in."

---

## Step 5: Ship Executive Brief (EditorAgent, 45-75s)

**Task prompt:**
> Turn the Incident Card + CTO + COO briefs into a publish-ready Executive Brief.
> Requirements:
> - Strong hook headline + 2-sentence lead
> - Sections: Situation, Impact, Decision, Next 24 Hours
> - Make it skimmable (bullets, short paragraphs)
> - Keep under 600 words
> - Tone: professional, clear, actionable

---

## Step 6: Platform Self-Audit (PlatformAuditAgent, 30-60s)

**Task prompt:**
> Quick demo audit: confirm DEMO_MODE is active, list allowlisted agents, and report any missing critical integrations. Output top 5 risks + 5 green checks.

**Say:** "Before we automate anything, we audit the platform state."

---

## Step 7: Final "Ship" Moment (10-20s)

Open Deliverables and show all 5 artifacts:
1. Incident Card
2. CTO Brief
3. COO Brief
4. Executive Brief (publish-ready)
5. Audit Snapshot

**Say:** "In about 3 minutes: signal → cross-domain analysis → governed decision → shipped artifacts. All real data, all governed."

---

## Plan B (if something fails)

| Failure | Pivot |
|---------|-------|
| ContentWriter fails | Use ResearchAgent for analysis instead, skip to CTO/COO |
| CTO/COO hangs | Skip to EditorAgent on whatever content exists |
| EditorAgent fails | Show raw Incident Card as the artifact |
| Spider search empty | Use a pre-researched topic: "OpenAI GPT-5.2 infrastructure scaling" |

## Agents to NEVER trigger on camera

- AudioAgent (ElevenLabs quota exhausted)
- VideoAgent (slow, flaky)
- AISeriesWorkflowAgent (3+ min, multi-step)
- Any agent NOT in DEMO_AUTONOMY_ALLOWLIST
