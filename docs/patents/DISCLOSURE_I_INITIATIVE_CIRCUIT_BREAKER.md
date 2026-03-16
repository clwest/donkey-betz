# Invention Disclosure I: Four-Gate Initiative Circuit Breaker with Jaccard Deduplication and Quality-Gated Status Promotion

**Date:** March 16, 2026
**Inventors:** Chris West (DonkeyKing)
**Status:** Draft — Attorney Review Pending

---

## 1. Working Title

Four-Gate Autonomous Initiative Creation Control with Jaccard Keyword Deduplication, TRIAGE Status Quarantine, and Quality-Gated Active Promotion

---

## 2. Field / Technical Domain

Autonomous project management for AI platforms. Specifically, methods for controlling the rate and quality of autonomously created project initiatives through a four-gate circuit breaker (environment pause, database pause, backlog threshold, daily creation limit), Jaccard keyword deduplication against existing initiatives, TRIAGE quarantine for unvetted initiatives, and quality-gated promotion requiring owner assignment and evidence linkage before active execution.

---

## 3. Problem

**a) Autonomous systems create too many initiatives.** When signal intelligence detects patterns 24/7, the pipeline can create dozens of initiatives per day. Without creation controls, the backlog grows faster than human review capacity.

**b) Duplicate initiatives waste resources.** Similar signals from different sources or time windows generate near-duplicate initiatives ("AI Agent Trends" vs. "Trending AI Agents"). Without deduplication, the same work is planned multiple times.

**c) Auto-created initiatives lack vetting.** Initiatives created from automated signal processing may be low-quality (vague topics, no clear owner, insufficient evidence). Putting them directly into active status wastes pipeline resources on unvetted work.

---

## 4. Solution Summary

A three-layer creation control system:

1. **Four-Gate Circuit Breaker**: Environment variable pause (instant kill switch), database configuration pause (PA-controllable), backlog threshold (auto-pause when pending >= 20), daily creation limit (rolling 24h cap of 15).

2. **Jaccard Keyword Deduplication**: Before creating an initiative, compute Jaccard similarity of extracted keywords against all active/triage + recently completed initiatives. Threshold 0.6 — reuse existing initiative instead of creating duplicate.

3. **TRIAGE Quarantine + Quality-Gated Promotion**: Auto-created initiatives start as TRIAGE. Promotion to ACTIVE requires: owner_agent assigned AND at least one evidence indicator (next_action, signal_cluster link, substantive parent_topic, or deliverable keywords in description).

---

## 5. As-Built Mechanism

### Gate 1: Environment Variable Pause

**File:** `core/services/initiative_circuit_breaker.py` (lines 42-45)

```python
def is_creation_paused_by_env() -> bool:
    paused = os.environ.get('INITIATIVE_CREATION_PAUSED', '').lower()
    return paused in ('true', '1', 'yes')
```

**Use case:** Emergency kill switch. Set `INITIATIVE_CREATION_PAUSED=true` in Railway environment variables to immediately halt all initiative creation. No deploy required.

### Gate 2: Database Configuration Pause

**File:** `core/services/initiative_circuit_breaker.py` (lines 48-62)

Queries `SystemConfiguration` for `key='initiative_creation_paused'`. Handles value as bool, string ('true'/'1'/'yes'), or truthy value.

**Use case:** PA-controllable pause. Rigby can pause initiative creation via `ops_tool` without environment access.

### Gate 3: Backlog Threshold

**File:** `core/services/initiative_circuit_breaker.py` (lines 74-124)

```python
INITIATIVE_BACKLOG_THRESHOLD = int(os.environ.get('INITIATIVE_BACKLOG_THRESHOLD', '20'))

def is_backlog_too_high() -> bool:
    threshold = get_backlog_threshold()  # Default: 20, min: 10
    pending = get_pending_initiative_count()  # ACTIVE + TRIAGE count
    return pending >= threshold
```

**Caching:** `_backlog_cache` with 60-second TTL prevents database query on every creation check.

**Use case:** Automatic pause when the system is overwhelmed. When ACTIVE + TRIAGE initiatives >= 20, no new initiatives are created until the backlog is worked down.

### Gate 4: Daily Creation Limit

**File:** `core/services/initiative_circuit_breaker.py` (lines 127-154)

```python
INITIATIVE_DAILY_LIMIT = int(os.environ.get('INITIATIVE_DAILY_LIMIT', '15'))

def is_daily_limit_reached() -> bool:
    limit = get_daily_creation_limit()
    cutoff = timezone.now() - timedelta(hours=24)
    created_24h = Initiative.objects.filter(created_at__gte=cutoff).count()
    return created_24h >= limit
```

**Use case:** Rate limiting. Even if backlog is low (initiatives complete quickly), cap at 15 per 24h rolling window to prevent budget runaway.

### Main Check Function

**File:** `core/services/initiative_circuit_breaker.py` (lines 157-198)

```python
def can_create_initiative(bypass_check: bool = False) -> bool:
    if bypass_check: return True  # Admin override

    if is_creation_paused_by_env(): return False      # Gate 1
    if is_creation_paused_by_db(): return False       # Gate 2
    if is_backlog_too_high(): return False             # Gate 3
    if is_daily_limit_reached(): return False          # Gate 4

    return True
```

**Priority order:** Explicit pauses checked first (fastest), then computed limits.

### Jaccard Keyword Deduplication

**File:** `core/services/initiative_circuit_breaker.py` (lines 222-274)

**Step 1 — Keyword Extraction:**
```python
def extract_keywords(name: str) -> set:
    stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', ...}
    normalized = name.lower().strip()
    words = set(normalized.split())
    return words - stopwords
```

**Step 2 — Jaccard Similarity:**
```python
def calculate_similarity(name1: str, name2: str) -> float:
    kw1 = extract_keywords(name1)
    kw2 = extract_keywords(name2)
    if not kw1 or not kw2: return 0.0
    intersection = len(kw1 & kw2)
    union = len(kw1 | kw2)
    return intersection / union if union > 0 else 0.0
```

**Step 3 — Candidate Search (Session 1059 fix):**
- Candidates = ACTIVE + TRIAGE initiatives (limit 200) + COMPLETED in last 48h (limit 200)
- Including recently completed prevents fast-completing initiatives from escaping dedup
- Returns best match with score >= 0.6

**Step 4 — Reuse:** When a match is found, the existing initiative is returned instead of creating a new one. Caller logs: `"Reusing similar initiative '{existing.name}' instead of creating duplicate"`

### TRIAGE Quarantine

Auto-created initiatives start with `status='TRIAGE'` (not 'ACTIVE'). This prevents unvetted initiatives from consuming pipeline resources.

### Quality-Gated Promotion (TRIAGE → ACTIVE)

**File:** `core/services/hivemind_execution_pipeline.py` (lines 277-325)

```python
def can_promote_to_active(initiative) -> bool:
    # REQUIRED: Must have owner_agent
    if not getattr(initiative, 'owner_agent', None):
        return False

    # REQUIRED: At least 1 evidence indicator
    checks_passed = 0
    if getattr(initiative, 'next_action', None): checks_passed += 1
    if getattr(initiative, 'signal_cluster_id', None) or \
       getattr(initiative, 'source_decision_id', None): checks_passed += 1
    if len((getattr(initiative, 'parent_topic', '') or '').strip()) > 20: checks_passed += 1
    if any(kw in (initiative.description or '').lower()
           for kw in ['deliverable', 'output', 'produce', 'create', 'build', 'implement', 'publish']):
        checks_passed += 1

    return checks_passed >= 1
```

**Requirements:** owner_agent (mandatory) + at least 1 of: next_action, signal link, substantive topic, or deliverable intent.

---

## 6. Novelty Hooks (Section 102)

**a) Four-gate circuit breaker with distinct control mechanisms.** The four gates operate at different layers (environment, database, computed threshold, rate limit) and serve different purposes (emergency kill, PA control, backlog control, budget control). No known project management system implements four distinct creation control gates.

**b) Jaccard dedup against active + recently completed initiatives.** Comparing against COMPLETED initiatives from the last 48 hours prevents fast-completing initiatives from escaping dedup. Standard dedup only checks against active items.

**c) TRIAGE quarantine for auto-created initiatives.** Auto-created initiatives enter a holding status before active execution, requiring explicit quality-gated promotion. No known autonomous project system quarantines auto-generated projects before activation.

**d) Quality gate requiring owner + evidence.** Promotion requires both an owner (who is responsible) and evidence (why this initiative exists). This dual requirement is absent from project management systems where projects can be created without ownership or evidence.

---

## 7. Non-Obviousness Hooks (Section 103)

**a) Four gates at different layers is non-obvious because it appears redundant.** If the backlog threshold works, why also have a daily limit? The insight: each gate catches a different failure mode. The backlog threshold catches accumulation; the daily limit catches rapid creation bursts. The env pause catches emergencies; the DB pause enables PA control. The redundancy is deliberate.

**b) Including recently completed initiatives in dedup is non-obvious.** Standard dedup only checks active items. Including COMPLETED initiatives from the last 48h is counter-intuitive because completed work shouldn't block new work. The insight: if an initiative completed in 3 hours, a near-duplicate arriving 4 hours later should not generate new work.

**c) TRIAGE quarantine slows the pipeline deliberately.** The obvious design for an autonomous system is to create initiatives in ACTIVE status for immediate processing. Quarantining in TRIAGE introduces delay. The non-obvious insight: the delay enables quality filtering that prevents pipeline waste.

**d) 60-second cache on backlog count is a non-obvious performance optimization.** Checking `can_create_initiative()` queries the database for initiative count. Caching for 60 seconds means the count can be stale — a new initiative created 30 seconds ago might not be counted. This staleness is acceptable because the backlog threshold (20) provides sufficient margin for a 60-second delay.

---

## 8. Operational Benefits

- **Emergency stop:** `INITIATIVE_CREATION_PAUSED=true` halts all creation within seconds
- **Budget protection:** Daily limit of 15 caps LLM spend on stage document generation
- **Backlog prevention:** Threshold of 20 prevents runaway initiative accumulation
- **Duplicate elimination:** Jaccard >= 0.6 catches "AI Agent Trends" vs. "Trending AI Agents"
- **Quality assurance:** TRIAGE → ACTIVE gate ensures every active initiative has an owner and evidence
- **Recently-completed coverage:** 48h window in dedup prevents fast-cycling duplicates

---

## 9. Alternative Embodiments

**a) Adaptive backlog threshold.** Instead of fixed 20, the threshold could adapt based on team velocity: if initiatives complete faster, allow more in backlog.

**b) Embedding-based dedup instead of Jaccard.** Semantic similarity via embeddings could catch duplicates with different wording ("market trends for AI" vs. "artificial intelligence market dynamics").

**c) Graduated creation limits.** Instead of a hard daily limit, a graduated system could allow N high-priority, M medium-priority, and K low-priority initiatives per day.

**d) Automatic TRIAGE expiry.** Initiatives in TRIAGE for more than N days without promotion could be automatically archived, preventing abandoned initiatives from consuming backlog capacity.

**e) Multi-user initiative ownership.** Instead of a single `owner_agent`, initiatives could have a team with roles (owner, reviewer, executor), enabling more nuanced quality gates.

---

## 10. Claim Skeleton

### Independent Method Claim

A computer-implemented method for controlling the creation of project initiatives in an autonomous AI system, the method comprising:

(a) receiving a request to create a new project initiative from an automated signal processing pipeline;

(b) evaluating the request against a plurality of independent creation gates, each gate implementing a different control mechanism, the gates comprising at least: an environment-level pause flag, a database-level pause setting, a backlog threshold comparing pending initiative count to a configurable maximum, and a rolling daily creation limit;

(c) upon all gates permitting creation, computing a keyword similarity score between the proposed initiative name and existing active, triage, and recently completed initiatives using Jaccard similarity of extracted keywords;

(d) upon the similarity score exceeding a configurable threshold, returning the existing similar initiative instead of creating a new one;

(e) upon no similar initiative being found, creating the new initiative with a triage status that prevents the initiative from entering the active execution pipeline; and

(f) promoting the initiative from triage to active status only upon verification that the initiative has an assigned owner and at least one evidence indicator linking the initiative to its originating signal source.

### Dependent Claims

1. The method of the independent claim, wherein the environment-level pause flag is read from an environment variable and the database-level pause setting is read from a system configuration record, enabling independent control by operations staff and AI assistants respectively.

2. The method of the independent claim, wherein the backlog threshold counts initiatives in both active and triage statuses, and the count is cached for a configurable duration to reduce database queries.

3. The method of the independent claim, wherein the rolling daily creation limit counts initiatives created within the last 24 hours and compares against a configurable maximum.

4. The method of the independent claim, wherein the recently completed initiatives used for deduplication comparison comprise initiatives completed within a configurable time window.

5. The method of claim 4, wherein the configurable time window is 48 hours, preventing fast-completing initiatives from escaping deduplication.

6. The method of the independent claim, wherein the evidence indicators comprise at least one of: a concrete next action description, a foreign key link to an originating signal cluster, a substantive parent topic exceeding a minimum length, or the presence of deliverable-indicating keywords in the initiative description.

7. The method of the independent claim, further comprising an administrative bypass flag that permits creation regardless of gate evaluations.

8. The method of the independent claim, wherein the Jaccard similarity is computed after extracting keywords from initiative names by tokenizing, lowercasing, and removing stopwords.

9. A system comprising one or more processors and memory storing instructions that, when executed, perform the method of the independent claim.

---

## 11. Diagrams to Draft

**Figure 1 — Four-Gate Circuit Breaker**
```
[Create Initiative Request]
      |
[Gate 1: Env paused?] --YES--> [BLOCKED]
      |NO
[Gate 2: DB paused?]  --YES--> [BLOCKED]
      |NO
[Gate 3: Backlog >= 20?] --YES--> [BLOCKED]
      |NO
[Gate 4: Daily count >= 15?] --YES--> [BLOCKED]
      |NO
[All gates passed]
      |
[Jaccard Dedup Check]
```

**Figure 2 — Jaccard Deduplication**
```
New: "AI Agent Market Trends"
Keywords: {ai, agent, market, trends}

Existing: "Trending AI Agents"
Keywords: {trending, ai, agents}

Intersection: {ai} (note: "agent" ≠ "agents" after split)
Union: {ai, agent, market, trends, trending, agents}

Jaccard = 1/6 = 0.17 → BELOW 0.6 → CREATE NEW

Existing: "AI Agent Trend Analysis"
Keywords: {ai, agent, trend, analysis}

Intersection: {ai, agent} + partial "trend"/"trends"
(After normalization: {ai, agent, trend})
Union: {ai, agent, market, trends, trend, analysis}

Jaccard = 3/6 = 0.50 → BELOW 0.6 → CREATE NEW

Existing: "AI Agent Market Trends Report"
Keywords: {ai, agent, market, trends, report}

Intersection: {ai, agent, market, trends}
Union: {ai, agent, market, trends, report}

Jaccard = 4/5 = 0.80 → ABOVE 0.6 → REUSE EXISTING
```

**Figure 3 — TRIAGE → ACTIVE Promotion Gate**
```
[Initiative created (TRIAGE)]
      |
[Has owner_agent?] --NO--> [Stay TRIAGE]
      |YES
[Has next_action?]      → +1
[Has signal_cluster?]   → +1
[Has parent_topic>20ch?] → +1
[Has deliverable kw?]   → +1
      |
[checks_passed >= 1?] --NO--> [Stay TRIAGE]
      |YES
[Promote to ACTIVE]
```

---

## 12. Prior Art Buckets

**a) Rate Limiting (API Gateways, Token Buckets)** — Teaches request rate limiting but not project-level creation control with backlog awareness.

**b) Circuit Breakers (Hystrix, Resilience4j)** — Teaches failure-based circuit breaking but not creation-volume-based gating.

**c) Deduplication Systems (Elasticsearch dedup, MinHash LSH)** — Teaches text/document dedup but not project-level Jaccard keyword dedup with recently-completed inclusion.

**d) Project Management (Jira, Linear)** — Teaches project status workflows but not autonomous creation control or quality-gated status promotion.

**e) Queue Management (RabbitMQ, SQS)** — Teaches queue depth monitoring and backpressure but not project-level backlog thresholds.

---

## Examiner Story

Prior art teaches API rate limiting (token buckets), circuit breakers for failure containment (Hystrix), text deduplication (MinHash), and project status workflows (Jira). However, no single reference teaches a system that (1) evaluates autonomous initiative creation requests against four independent gates operating at different control layers (environment, database, computed backlog, rolling daily limit), (2) deduplicates proposed initiatives against active, triage, and recently completed initiatives using Jaccard keyword similarity, (3) quarantines auto-created initiatives in a triage status preventing active execution, and (4) promotes initiatives to active status only upon verifying both owner assignment and evidence linkage. The combination is non-predictable because rate limiters operate on request volume not project semantics, circuit breakers trigger on failures not creation volume, dedup systems don't include recently completed items, and project tools don't quarantine auto-created items.
