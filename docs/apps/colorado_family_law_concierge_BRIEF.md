---
title: "Colorado Family Law Concierge — Phase 1 brief"
status: draft (Session 1135 discovery, rev. 2 post-Rigby review, pending Chris ratification)
session: 1135
generated: 2026-05-23
revised: 2026-05-23 (Rigby content-flag review applied)
workspace: Donkey Betz
companion_docs:
  - 24_7_GLOBAL_AI_APP_ATLAS.md
  - specs/FLEET_CAPABILITY_BUSINESS_SPEC.md
  - apps/rigby_standalone_BRIEF.md
  - apps/signal_studio_BRIEF.md
  - UDB_BEHAVIOR_LAYER.md
  - UDB_TRANSLATION_LAYER.md
authors: claude + jessica (discovery pass) → rigby (review pending)
note: "Internal repo + container name remains `contract-concierge` per Jessica decision (i); product brand = 'Colorado Family Law Concierge' externally. Repo rename deferred to Phase 2 if desired."
---

# Colorado Family Law Concierge — Phase 1 brief

## 1. What it is

**Phase 1 customer-facing pitch:**

> *"The pro-se assistant that knows Colorado family court — drafts motions, maps your filing to the right JDF forms, and walks you through procedure step by step."*

**Phase 1 scope: Pro-se Colorado family law support.** The product helps Coloradans representing themselves in family court generate motions, declarations, and JDF-form-mapped documents for divorce, custody, parenting time, child support, modification, and enforcement matters. **Information service, never legal advice.**

**Packaging direction: standalone product** (Jessica discovery decision), marketed parallel to Rigby standalone + Signal Studio. Internal repo + container name `contract-concierge` retained per Jessica decision (i); product brand is "Colorado Family Law Concierge" externally.

**Critical discovery (Session 1135):** The underlying engine `legal_doc_drafter_agent` is purpose-built for Colorado family law (via embedded Colorado JDF form mappings and CO-specific drafting patterns), NOT commercial contracts. Original "Contract Concierge" framing was a name-extrapolation risk Rigby flagged at session open. Jessica chose **(3) hybrid** path: ship Colorado family law Phase 1 with the existing engine; build commercial-contracts engine Phase 2 as separate product.

## 2. Who buys it

**Primary user: Colorado parents and spouses representing themselves in family court.**
- Income $40-150K (above legal-aid threshold, below comfortable-attorney-affordability)
- Acute matter: custody / parenting time / divorce filing / child support / modifications
- State of mind: emotionally distressed (family court = high stress)
- Time-pressured: court deadlines are unforgiving
- Mobile-first or desktop-flexible; motivated to figure it out

**Adjacent secondary user:** People between lawyer engagements who need partial DIY help (had counsel for one thing, can't afford ongoing representation).

**Buyer = User.** Self-pay, monthly subscription. No team / firm / B2B in Phase 1.

*Deferred to Phase 2-3:* B2B2C via Colorado family-law attorney referrals; partnerships with court self-help centers; legal-aid overflow channel.

## 3. What's built (real shipping evidence)

*Counts and behavior below verified on local as of 2026-05-23 against `core/agents/legal/legal_doc_drafter_agent.py`, `core/prompts/tool_descriptions.py`, contract-concierge repo (`contract_concierge_api` + `contract_concierge_web`), and Session 1129 + 1126 handoffs. Production parity not asserted.*

| Component | Status | Notes |
|---|---|---|
| `legal_doc_drafter_agent` (Colorado family law engine) | Live | 7,829-line agent class in `core/agents/legal/legal_doc_drafter_agent.py`; explicit "GENERAL LEGAL INFORMATION ONLY" posture in tool description |
| Colorado JDF form mappings | Live | `COLORADO_FAMILY_LAW_FORMS` dict covers divorce_with_children, parenting, child_support, general — including JDF 1111 / 1115 / 1116 / 1113 / 1220 / 1820 / 1821 etc. |
| Document type generators | Live | `_generate_motion()`, `_generate_email()`, `_generate_declaration()` methods exist + tested via Session 1129 routing |
| Case type coverage | Live | Divorce with children, custody (allocation of parental responsibilities), child support, parenting time, modification, enforcement |
| Draft Library end-to-end flow | Live (Session 1129) | Login → draft form → generate → persisted as `artifact_type="contract_draft"` *(internal legacy name from pre-pivot; Phase 2 rename candidate to `family_law_draft`)* → pull by ID → library lists past drafts |
| Artifact persistence + user-level privacy | Live | Per-user isolation enforced via `metadata.generated_by_user_id == jwt.sub` filter |
| Artifact lifecycle (push/pull/list + TTL + soft-delete) | Live | `POST /api/fleet/artifacts/`, `GET /api/fleet/artifacts/<id>/`, list with pagination, cleanup beat task emits `artifact.expired` |
| Fleet HMAC auth + audit logging | Live (Session 1129) | App identity verified per request; nonce replay protection |
| Contract-concierge Docker app | Live on local | Backend `localhost:8003`, frontend `localhost:5175`, own Postgres |
| SSE event stream (2-hop pattern) | Live | u-d-b emits → CC backend → browser |
| Fleet routing for `contract-concierge` | Live | `force_allowed = true`; default agent `legal_doc_drafter_agent` |
| Brand domain `247globalai.com` | Live | Vercel-served, marketing site |
| Consumer landing page for product | **Not built** | See §5 |

## 4. What proves it's real

**Canonical Phase 1 proof: full document-generation flow anchored on court-ready DOCX export, demoed via 45-second landing-page screen recording.**

**Today's interim proof (developer-grade, available on local):**
> Open `localhost:5175` → log in → fill draft form ("Motion to Modify Parenting Time") → click Generate → motion artifact persists via Session 1129 flow → open by ID → see draft in Library. Backend smoke: `curl http://localhost:8003/api/drafts/<id>` returns artifact.

**Launch-day proof (post-Phase 0, customer-facing):**
> Visit `family.247globalai.com` (or chosen sub-domain) → landing page hero is a 45-second screen-recorded demo:
> 1. User enters case basics (case number, parties, what they're requesting)
> 2. Click "Generate Motion"
> 3. Motion appears in proper Colorado caption block format
> 4. Click "Download as DOCX" → file downloads with Colorado court formatting + auto-bundled Certificate of Service template
> 5. Last frame: *"Ready to file. Edit in Word, sign, submit."*
>
> CTA: *"Start your free 7-day trial — $29/mo"* → Stripe.

**[BLOCKER]** Launch-day proof requires Q5's DOCX export + Certificate of Service + Phase 0 landing page + Stripe SKU. Bridge demo (Library-only view without export) drops conversion ~30-40% and undersells the product — not recommended.

## 5. What's missing (gap to "could sell for real")

### 5.1 [PHASE 0 GATING — launch-blocking]

| Item | Status | Effort | Why gating |
|---|---|---|---|
| DOCX export with Colorado court formatting | **Not built** | ~3-5 days | Customer needs filable document; web-only view doesn't justify $29/mo |
| PDF export ready for Colorado eFile or paper filing | **Not built** | ~2-3 days | Same |
| Certificate of Service auto-bundle (required with most motions) | **Not built** | ~1-2 days | Court-required document; bundled with motion exports |
| Email-format output for meet-and-confer / opposing counsel (copy-to-clipboard) | **Not built** | ~1 day | Critical workflow for family court |
| Per-template legal review (~10 templates × $300 ea) | **Not done** | 8-10 hrs legal time | UPL exposure on every unreviewed template |
| TOS + UPL-compliance audit + privacy policy + subpoena policy + LLM provider disclosure | **Not done** | Part of legal review | Required for any markets-adjacent paid product handling sensitive PII |
| Onboarding screener (matter type → DV/adoption/UCCJEA/out-of-state → decline + refer) | **Not built** | ~3-5 days | UPL safety mechanism; enforces Q4 exclusions |
| User hard-delete + account deletion + data export | **Not built** | ~1-1.5 weeks | Sensitive PII baseline; CCPA-style obligations |
| Encryption at rest on drafts table | **Verify infra** | ~1-2 days verify | PII baseline |
| Optional 2FA + account pseudonym + panic delete | **Not built** | ~3-5 days combined | DV-adjacent edge case protection |
| Per-customer cost tracking + daily $ cap (shared with Rigby + Signal Studio) | **Not done** | ~1 week shared | Same Atlas gating; tighter $1.00/day cap here (doc gen is LLM-heavy) |
| Consumer landing page at sub-domain | **Not built** | ~1 sprint | No customer acquisition without it |
| Stripe SKU + checkout (separate from Rigby + Signal Studio) | **Not built** | Small | Revenue plumbing |
| Email infra (welcome + payment receipts + account-event emails) | **Not built** | ~1 week | Required for any subscription product |

### 5.2 Other prerequisites

| Item | Status | Effort |
|---|---|---|
| Email template QA across Gmail/Outlook/Apple Mail | **Not built** | ~1-2 days |
| E&O insurance + cyber-liability insurance (annual operating cost) | **Not done** | Procurement only |

### 5.3 Not gaps, but worth naming

- **No paying customer exists.**
- No commercial-contracts product (Phase 2 build per option 3 hybrid).
- No other states (Phase 2+ per state).
- No DV / adoption / UCCJEA / high-asset / federal / criminal matter coverage (Q4 hard exclusions; enforced via onboarding screener + chat refusal rules).
- No Colorado eFile direct submission (CRESCent restrictions; Phase 2+ if regulatory path opens).
- No DocuSign / Google Docs / cloud-storage integrations (Phase 2+).
- No human support / attorney review / paralegal review (Phase 2+).

## 6. Buildable in one sprint?

**No — not buildable in one sprint end-to-end.** Phase 0 in aggregate: **LARGE (~5-6 weeks).** This is longer than Rigby (~3-4 weeks) or Signal Studio (~4-5 weeks) because of legal-review depth + privacy-feature breadth + matter-type screener. Parallel-able with both — most engineering is separate.

Per-item sizing:
- Stripe SKU + checkout: **SMALL**
- DOCX + PDF + Certificate of Service export bundle: **MEDIUM** (~1.5-2 weeks)
- Consumer landing page: **MEDIUM** (~1 sprint)
- Email infra + welcome/receipts: **MEDIUM** (~1 week)
- User hard-delete + account deletion + data export + 2FA + pseudonym + panic delete: **MEDIUM** (~1-1.5 weeks)
- Onboarding screener: **SMALL-MEDIUM** (~3-5 days)
- Per-template legal review (10 templates): **SMALL** (~8-10 legal hrs)
- TOS + UPL + subpoena + LLM disclosure legal review: **SMALL** (~3-4 legal hrs)
- Cost tracking + daily cap (shared with Rigby Phase 0): **MEDIUM** (~1 week, shared infra)
- Encryption at rest verify: **SMALL** (~1-2 days)

## 7. GTM sketch

| Lever | Plan |
|---|---|
| **Channel** | *Proposed (pending Chris greenlight + budget):* Paid ads (Meta, Reddit r/legaladvice + r/Divorce, Colorado-targeted Google Search), warm/personal network, eventual partnerships with Colorado court self-help centers + divorce coaches. No newsletter funnel (audience = 0). |
| **Pricing** | $29/mo flat, single tier, 7-day free trial, monthly billing only Phase 1 |
| **Cap behavior** | $1.00/day per customer (tighter than Rigby's $1.50; doc generation is LLM-heavier than markets briefing) |
| **CTA** | *"Start your free 7-day trial — $29/mo"* → Stripe → onboarding screener → matter-type questions → first draft |
| **What's included** | *Planned Phase-1 offer (post-Phase-0 gating, see §5.1):* AI document generation (motions, declarations, emails, JDF guidance), Draft Library, DOCX + PDF export with Colorado court formatting, Certificate of Service auto-bundle, ~10 Phase 1 templates across 5 categories (custody/parenting motions, child support, divorce filing, supporting docs, communications, procedural), in-app chat about your case (general info only), optional 2FA, account pseudonym option, "panic delete" button, 30-day TTL on trial drafts (paid users no TTL). 1 seat per subscription. |
| **Customer-facing surface** | `family.247globalai.com` (recommended) or `colorado-family-law.247globalai.com` — Chris decision in §9. |
| **Disclaimers** | "Not legal advice / general legal information only / not a lawyer / no attorney-client relationship / Colorado only / consult licensed Colorado attorney for specific situation / templates require review / laws change — verify with current Colorado Judicial Department rules" — in TOS, landing footer, onboarding acceptance, every generated document (header + footer), every AI chat reply, every email. |
| **Forbidden in product + marketing** | Outcome promises ("win your case"), dollar-guaranteed savings, "our attorneys/experts" framing, court/judge approval implication, comparative attorney claims, specific case-outcome testimonials, "replaces a lawyer." |
| **Scope** | Information service for Colorado pro-se family-court litigants (divorce / custody / parenting time / child support / modification / enforcement). NOT advisor, NOT representation, NOT trial strategy. |
| **Excluded matter types (hard refused via onboarding + chat)** | Domestic violence / protection orders, adoption, multi-state UCCJEA, high-asset (>$1M) divorce, trial strategy, federal court, criminal contempt, non-Colorado matters. Refer to local resources for DV. |
| **Execution posture** | Document generation + chat about general info only. No outbound actions, no court-system integrations, no external-account integrations Phase 1. |
| **Retention** | *Policy decision; enforced by not setting `expires_at` for paid users in the artifact lifecycle (Session 1129 infra supports this).* Paid users: no auto-TTL (matters last 6-12+ months). Trial users: 30-day TTL. Account-deleted users: hard-delete within 30-day grace period. |
| **Privacy posture** | *Mix of shipped + planned-post-Phase-0 (see §5.1):* User-level isolation (✓ built, Session 1129), encryption at rest (Phase 0 verify), no data sale/share/monetization (TOS commitment), LLM provider disclosure (per current provider API terms as of 2026-05-23, our LLM providers state they do not train on API inputs; we will update disclosure if terms change), valid-legal-process compliance with user notification when legally permitted (TOS commitment + subpoena policy). |

## 8. Spokesperson alignment (Phase 4+, parked)

Per Atlas §C.5, J.2.8: Character OS / avatar / voice = parked until a paying customer demands a face. Phase 1 is text-only (web + email). Clean upgrade path:

- **Phase 4+:** AI-voiced narration of generated docs (audio read-back for accessibility).
- **Phase 4+:** Persona-narrated walkthrough videos ("Here's what your motion does and why").
- **Phase 4+:** Brand-voice-locked avatar variants if/when we partner with attorneys or court self-help centers for co-branded versions.

## 9. Decisions still needed (escalate to Chris)

**Closed in Jessica discovery pass** (Chris ratification pending, captured for record):
- ✅ **Engine-vs-name mismatch (Contract Concierge / commercial contracts vs Colorado family law engine)** — resolved with **option (3) hybrid**: ship Colorado family law Phase 1 with existing engine; build commercial-contracts engine Phase 2 as separate product.
- ✅ **Product name** — locked as "Colorado Family Law Concierge" (state-specific naming for legal-tech specificity).
- ✅ **Repo/container naming** — keep `contract-concierge` internal, product brand external (Jessica option (i); refactor optional Phase 2).
- ✅ **Pricing direction** — $29/mo single tier, 7-day trial, monthly only.
- ✅ **Cap direction** — $1.00/day (tighter than Rigby/Signal Studio due to LLM-heavy doc gen).
- ✅ **Packaging direction** — standalone, parallel to Rigby + Signal Studio.
- ✅ **Canonical proof path** — full flow including DOCX export.

**Still open for Chris:**

| # | Question | Why it matters |
|---|---|---|
| 1 | **Contract-concierge web repo consumer-app status — what's actually shipped vs scaffolded for retail use?** | Same shape as Rigby + Signal Studio repo questions. Unlocks Phase 0 timeline math + auth/signup effort sizing. |
| 2 | **Sub-domain pick** — `family.247globalai.com` (recommended, headroom for state expansion) vs `colorado-family-law.247globalai.com` vs other? | Brand decision. State-expansion plan depends. |
| 3 | **Confirm $29/mo + 7-day trial + $1.00/day cap pricing** | Locks Stripe SKU. |
| 4 | **Same Phase 0 cost-attribution + daily cap as Rigby (Atlas-level requirement applies to all 3 paid products)** | Without this, paid ads can produce negative unit economics during trial. |
| 5 | **Paid ads budget for CFL Concierge (separate from Rigby + Signal Studio)** | Three parallel campaigns = three budget pools. |
| 6 | **Legal review greenlight (~$3-5K — more than Signal Studio's $500-1500)** | UPL + per-template review is heavier here. |
| 7 | **E&O + cyber-liability insurance budget greenlight (~$2-5K/year)** | Required for any consumer legal-tech product handling sensitive PII. |
| 8 | **Atlas deviation ratification** (standalone CFL Concierge parallel to Rigby — same call as Signal Studio) | Bends "one polished product first" rule on basis engine is built. |
| 9 | **Existing u-d-b email infra check** — reuse vs greenfield (Resend/Postmark)? | If u-d-b already has transactional email, saves 2-3 days. |
| 10 | **Colorado family-law attorney advisory board hire — Phase 1 or Phase 2?** | Strengthens marketing credibility + reduces UPL exposure if we have a Colorado attorney on advisory. Cost: stipend or equity. |

## 10. Honest claim audit (per translation layer §2)

**We do NOT claim:**
- Colorado Family Law Concierge provides legal advice, attorney representation, or attorney consultation.
- Attorney or paralegal review of generated documents (Phase 2 paid upgrade candidate).
- Specific case-outcome predictions or guarantees.
- A paying Colorado Family Law Concierge customer exists.
- The DOCX/PDF export with Colorado court formatting is built (it's not — Phase 0 GATING item).
- Certificate of Service auto-bundle is built (it's not — Phase 0 GATING item).
- The consumer landing page or sub-domain routing exists.
- Email delivery infra is wired (it isn't — Phase 0 GATING item).
- A Stripe SKU for Colorado Family Law Concierge exists.
- User hard-delete, account deletion, or data export is built (Phase 0 GATING items).
- Optional 2FA, account pseudonym, or panic-delete features are built (Phase 0 items).
- Encryption at rest is verified in production.
- Onboarding matter-type screener is built (Phase 0 item).
- Per-template legal review is complete.
- Coverage of non-Colorado states.
- Coverage of domestic violence / adoption / UCCJEA / high-asset divorce / federal court / criminal contempt matter types (hard exclusions).
- Colorado eFile direct integration, DocuSign integration, Google Docs integration, or other external integrations.
- That we file documents with the court on the user's behalf. The user is solely responsible for filing generated documents (whether by paper or via Colorado eFile). We generate; user files.
- 24/7 human support, uptime SLA, or phone support.
- Continuous monitoring of court rule changes (we do quarterly review per Q4; user must verify current rules before filing).
- Attorney-client relationship with any user.
- Court approval, judge approval, or regulatory certification.

**We DO claim:**
- The `legal_doc_drafter_agent` engine is operational on local today, with explicit "GENERAL LEGAL INFORMATION ONLY" posture baked into the tool description.
- Engine covers Colorado JDF form mappings for divorce_with_children, parenting, child_support, and general categories.
- Engine handles Colorado family-law case types: divorce, custody, parenting time, child support, modification, enforcement.
- Session 1129 draft library flow (login → form → generate → persist → pull-by-id → library lists past drafts) is verifiable on local at `localhost:5175`.
- Per-user artifact isolation is enforced (`metadata.generated_by_user_id == jwt.sub`).
- Fleet HMAC auth + audit logging operational per Session 1129.
- The brand domain `247globalai.com` is owned and live.

---

**Brief authored:** Session 1135 (Claude + Jessica discovery pass).
**Engine-vs-name discovery:** Rigby flagged `legal_doc_drafter_agent` ≠ commercial contracts at session open; Jessica chose (3) hybrid path (ship Colorado family law Phase 1, build commercial contracts Phase 2 separately).
**Rev. 2:** Rigby content-flag review applied — 5 honest-framing fixes: §1 pitch softened ("fills JDF forms" → "maps your filing to the right JDF forms"); §1 engine claim grounded ("purpose-built for Colorado family law via embedded Colorado JDF form mappings and CO-specific drafting patterns"); §3 `artifact_type="contract_draft"` labeled as internal legacy name with Phase 2 rename candidate; §7 retention marked as policy decision (not built guarantee); §7 privacy posture split into ✓ shipped vs Phase-0-planned with date-qualified LLM provider TOS claim.
**Next step:** Rigby quick "looks good?" pass on rev. 2. Then Chris ratifies the 10 open decisions in §9. Then brief becomes locked Phase 1 source-of-truth for Colorado Family Law Concierge.
