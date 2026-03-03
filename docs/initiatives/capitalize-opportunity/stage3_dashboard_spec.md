# Stage 3 Dashboard Spec (1-page) — Capitalize Opportunity

> Practical, wire-it-up-fast spec for the Stage 3 Evaluation Dashboard.
> Primary metric: **Action-Taken Rate (ATR) within 24h** of synthesis delivery.

---

## 1) Scope

This dashboard tracks the **RoleAware ingestion-to-playbook pilot + synthesis templates rollout** for the "Capitalizing on manager, position, developer opportunity" initiative (Stage 3).

---

## 2) Existing platform infrastructure tie-in (no over-engineering)

### 2.1 Spiders → signals → agents → deliverables (content path)
- **Spiders** collect raw sources (news, jobs, odds, reddit, etc.) and feed into the platform's ingestion/signal pipelines.
- **Agents** generate:
  - Role playbooks (what to do with signals)
  - Synthesis outputs (how signals are packaged)
- **Deliverables** are the canonical stored artifacts used for review, reuse, and downstream action tracking.

### 2.2 What we measure (behavior/outcome path)
We measure actionability with **events** captured by `core_deliverable_events` (the `DeliverableEvent` model).
Auto-emitted on: deliverable detail view (frontend + PA), save, export. Manual via `POST /api/deliverables/<id>/event/`.

### 2.3 "Action taken" definition (Stage 3)
A synthesis is considered "acted on" if, within 24 hours of synthesis creation, we observe either:
- **Explicit action event**: `action_taken` (best)
- OR an acceptable **proxy action**:
  - `task_created`
  - `followup_created`
  - `deliverable_exported`
  - `shared`
  - `deliverable_saved`

> NOTE: Proxies are acceptable for Stage 3 MVP; you can later tighten "action" to explicit only.

---

## 3) Minimal data contracts (what must be consistent)

### 3.1 In-scope deliverables (synthesis outputs)
A deliverable is a "synthesis output" for this dashboard if:
- `category = 'Initiatives'`
- `tags` includes `initiative:capitalize-opportunity`
- and either:
  - `title` starts with `Synthesis` (examples now, live syntheses later), **or**
  - `deliverable_type` contains `synthesis`

**Recommended tags to standardize going forward**
- `initiative:capitalize-opportunity`
- `stage:3`
- `pilot`
- `role:manager` / `role:recruiter` / `role:developer`
- Optional (if available):
  - `source:<spider_name>`
  - `signal:<cluster_id>`
  - `playbook:<role>` or `template:<name>`

### 3.2 Join key between events and deliverables (built-in)
`DeliverableEvent.deliverable` is a direct FK to `Deliverable`. Join is natural — no metadata parsing needed.
The SQL queries below use `e.deliverable_id::text` to match against `d.id::text`.

### 3.3 Role attribution (manager/recruiter/developer)
Role should be available either as:
- Tag: `role:manager|role:recruiter|role:developer` (preferred)
- Fallback: infer from `title` containing "Manager / Recruiter / Developer"

---

## 4) Dashboard layout (single page)

### Panel A — Headline KPI cards (top row)
Cards:
1) **Syntheses generated** (count)
2) **ATR-24h (overall)** (%)
3) **Median hours to first action** (hours)
4) **Viewed rate** (% of syntheses viewed/opened)

Mini-cards (or one small table) to the right:
- **ATR-24h by role** (manager / recruiter / developer)

### Panel B — Funnel (simple table)
| Step | Count | % of syntheses |
|---|---:|---:|
| Syntheses generated | N | 100% |
| Viewed/opened | N | % |
| Saved/exported/shared | N | % |
| Action taken (<=24h) | N | % |

### Panel C — Role breakdown (table)
| Role | Syntheses | Viewed | Saved/Exported/Shared | Acted <=24h | ATR-24h | Median hrs to action |
|---|---:|---:|---:|---:|---:|---:|

### Panel D — Top producers (two quick ranking tables)
**D1: Top agents by ATR-24h**
| agent_name | syntheses | acted_24h | atr_24h |

**D2: Top sources by ATR-24h (if available)**
| source | syntheses | acted_24h | atr_24h |

Source extraction rules (MVP):
- Prefer `core_deliverable_events.metadata->>'source'`
- Else parse deliverable tags like `source:<spider_name>`

---

## 5) SQL queries (copy-paste ready)

### 5.1 Syntheses generated (count)
```sql
SELECT COUNT(*) AS total_syntheses
FROM core_deliverables d
WHERE d.category = 'Initiatives'
  AND d.tags @> ARRAY['initiative:capitalize-opportunity']
  AND (d.title ILIKE 'Synthesis%' OR d.deliverable_type ILIKE '%synthesis%');
```

### 5.2 Common CTEs (reuse in all queries below)
```sql
-- Syntheses CTE
WITH syntheses AS (
  SELECT d.id::text AS deliverable_id, d.created_at
  FROM core_deliverables d
  WHERE d.category = 'Initiatives'
    AND d.tags @> ARRAY['initiative:capitalize-opportunity']
    AND (d.title ILIKE 'Synthesis%' OR d.deliverable_type ILIKE '%synthesis%')
),
-- Actions CTE
actions AS (
  SELECT
    e.deliverable_id::text AS deliverable_id,
    MIN(e.created_at) AS first_action_at
  FROM core_deliverable_events e
  WHERE e.event_type IN (
    'action_taken',
    'task_created',
    'followup_created',
    'deliverable_exported',
    'shared',
    'deliverable_saved'
  )
  GROUP BY 1
)
```

### 5.3 ATR-24h overall (explicit + proxy)
```sql
WITH syntheses AS (
  SELECT d.id::text AS deliverable_id, d.created_at
  FROM core_deliverables d
  WHERE d.category = 'Initiatives'
    AND d.tags @> ARRAY['initiative:capitalize-opportunity']
    AND (d.title ILIKE 'Synthesis Example:%' OR d.deliverable_type ILIKE '%synthesis%')
),
actions AS (
  SELECT
    e.deliverable_id::text AS deliverable_id,
    MIN(e.created_at) AS first_action_at
  FROM core_deliverable_events e
  WHERE e.event_type IN (
    'action_taken',
    'task_created',
    'followup_created',
    'deliverable_exported',
    'shared',
    'deliverable_saved'
  )
  GROUP BY 1
)
SELECT
  COUNT(*) AS total_syntheses,
  COUNT(*) FILTER (
    WHERE a.first_action_at IS NOT NULL
      AND a.first_action_at <= s.created_at + INTERVAL '24 hours'
  ) AS acted_within_24h,
  ROUND(
    (COUNT(*) FILTER (WHERE a.first_action_at IS NOT NULL AND a.first_action_at <= s.created_at + INTERVAL '24 hours'))::numeric
    / NULLIF(COUNT(*), 0),
    4
  ) AS atr_24h
FROM syntheses s
LEFT JOIN actions a USING (deliverable_id);
```

### 5.4 Median hours to first action (overall)
```sql
WITH syntheses AS (
  SELECT d.id::text AS deliverable_id, d.created_at
  FROM core_deliverables d
  WHERE d.category = 'Initiatives'
    AND d.tags @> ARRAY['initiative:capitalize-opportunity']
    AND (d.title ILIKE 'Synthesis%' OR d.deliverable_type ILIKE '%synthesis%')
),
actions AS (
  SELECT
    e.deliverable_id::text AS deliverable_id,
    MIN(e.created_at) AS first_action_at
  FROM core_deliverable_events e
  WHERE e.event_type IN (
    'action_taken',
    'task_created',
    'followup_created',
    'deliverable_exported',
    'shared',
    'deliverable_saved'
  )
  GROUP BY 1
),
joined AS (
  SELECT
    s.deliverable_id,
    EXTRACT(EPOCH FROM (a.first_action_at - s.created_at)) / 3600.0 AS hours_to_action
  FROM syntheses s
  JOIN actions a USING (deliverable_id)
  WHERE a.first_action_at IS NOT NULL
)
SELECT
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY hours_to_action) AS median_hours_to_action
FROM joined;
```

### 5.5 ATR-24h by role
```sql
WITH syntheses AS (
  SELECT
    d.id::text AS deliverable_id,
    d.created_at,
    CASE
      WHEN d.tags @> ARRAY['role:manager'] OR d.title ILIKE '%Manager%' THEN 'manager'
      WHEN d.tags @> ARRAY['role:recruiter'] OR d.title ILIKE '%Recruiter%' THEN 'recruiter'
      WHEN d.tags @> ARRAY['role:developer'] OR d.title ILIKE '%Developer%' THEN 'developer'
      ELSE 'unknown'
    END AS role
  FROM core_deliverables d
  WHERE d.category = 'Initiatives'
    AND d.tags @> ARRAY['initiative:capitalize-opportunity']
    AND (d.title ILIKE 'Synthesis%' OR d.deliverable_type ILIKE '%synthesis%')
),
actions AS (
  SELECT
    e.deliverable_id::text AS deliverable_id,
    MIN(e.created_at) AS first_action_at
  FROM core_deliverable_events e
  WHERE e.event_type IN (
    'action_taken','task_created','followup_created','deliverable_exported','shared','deliverable_saved'
  )
  GROUP BY 1
)
SELECT
  role,
  COUNT(*) AS total_syntheses,
  COUNT(*) FILTER (
    WHERE a.first_action_at IS NOT NULL
      AND a.first_action_at <= s.created_at + INTERVAL '24 hours'
  ) AS acted_within_24h,
  ROUND(
    (COUNT(*) FILTER (WHERE a.first_action_at IS NOT NULL AND a.first_action_at <= s.created_at + INTERVAL '24 hours'))::numeric
    / NULLIF(COUNT(*), 0),
    4
  ) AS atr_24h
FROM syntheses s
LEFT JOIN actions a USING (deliverable_id)
GROUP BY role
ORDER BY role;
```

---

## 6) Stage gate decision rules

### 6.1 Stage 3 pass (advance to Stage 4)
Stage 3 is **APPROVED** when (all must be true, measured over a rolling 14-day window):
- **ATR-24h overall >= 25%**
- **ATR-24h per role >= 15%** for each of {manager, recruiter, developer}
- **Mean actionability rubric >= 4.0/5**
  - No "critical failure mode" recurring (hallucinations, wrong role framing, non-actionable recommendations)

> If you don't have rubric scoring instrumented yet, the pass condition is: **no more than 2 critical failures in the 20-sample**.

### 6.2 Stage 3 "conditional pass" (ship with fixes)
If **ATR-24h overall >= 25%** but one role is below threshold, Stage 3 can still be marked **CONDITIONALLY APPROVED** if:
- the failing role has a clear remediation plan (template tweaks or playbook changes), and
- you commit to re-check that role within 7 days.

### 6.3 Stage 3 fail (do not advance)
Stage 3 is **FAILED / needs iteration** if:
- **ATR-24h overall < 20%**, or
- **two or more roles < 10%**, or
- the rubric spot-check shows repeated critical failures (safety/accuracy/actionability).

### 6.4 What to do based on outcome (operator playbook)
- **Low viewed rate** -> fix distribution (where syntheses surface), notifications, and relevance filters.
- **High view but low action** -> template/playbook iteration (make next steps explicit; tighten to role).
- **High action but high variance** -> identify top agents/templates/sources and standardize.

---

## 7) Notes / quick implementation checklist (to wire fast)

1) **Standardize tags** on new syntheses:
   - `initiative:capitalize-opportunity`, `stage:3`, `role:<role>`
2) Ensure events include deliverable linkage:
   - `content_id = deliverable_id` OR `metadata.deliverable_id`
3) Add/confirm these `event_type` values:
   - `synthesis_viewed`, `deliverable_saved`, `deliverable_exported`, `shared`,
   - `task_created`, `followup_created`, `action_taken`
4) If "source" attribution matters now:
   - log `metadata.source = <spider_name|signal_cluster>` on events **or** add `source:<x>` tags to deliverables.
5) Build dashboard panels with the SQL in Section 5:
   - Headline, role table, funnel, top agents, exceptions.
6) Review cadence:
   - Daily: ATR-24h pulse
   - Weekly: rubric spot-check + iterate templates/playbooks
