"""
Opportunity → OutreachDraft (touch=1) generator.

Session 1224 P1 — Option B. Closes the gap between Opportunity rows
(populated by spider pipeline + curation) and the OutreachDraft inbox
(populated only with follow-ups by OutreachSequencer.evaluate today).

Plan deliverable: 329165f4-d5c1-420c-a6ea-d5393ec3e343

Pipeline:
  1. Select contactable Opportunity rows (active, scope-bound, no
     existing active touch-1 draft).
  2. Round-robin across offers (ai_automation / content_engine /
     consulting).
  3. ensure_spider_data_seed — create a purposeful SpiderData row
     (spider_name='opportunity_outreach_seed') so the OutreachDraft
     NOT NULL constraint on spider_data_id is satisfied without a
     migration. Idempotent per opportunity.
  4. render_email — LLM call (gpt-5-mini, JSON-mode) returns subject
     + body. Falls back to a deterministic skeleton if the LLM returns
     unparseable output, so the slice never crashes the beat task.
  5. Persist OutreachDraft (touch_number=1, status='draft', channel='email').

Caps:
  - DAILY_GENERATE_CAP=5 (per UTC day, counted by lead_source tag).
  - Dedupe: an Opportunity with ANY active touch-1 draft is skipped
    (conservative interpretation of "don't double-pitch the same opp
    before they reply"). The (opp_id, offer_key) variant can come later.

Triggered by:
  - autopilot_tool action='outreach_generate' (on-demand, PA tool).
  - generate_outreach_drafts_daily Celery beat task (7:30am MT).
"""
from __future__ import annotations

import json
import logging
from typing import Iterable, Optional
from urllib.parse import urlparse

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class OpportunityDraftGenerator:
    """Generates touch=1 OutreachDraft rows from contactable Opportunity rows."""

    DAILY_GENERATE_CAP = 5
    OFFER_KEYS = ('ai_automation', 'content_engine', 'consulting')
    # Session 1225 — Rigby envelope: each blurb names the actual scope being
    # offered, not a vague capability claim. The SYSTEM_PROMPT hard-binds the
    # delivery shape (timebox, definition of done, what's explicitly excluded)
    # so the LLM can't drift into guaranteed-outcome territory.
    OFFER_BLURBS = {
        'ai_automation': 'a diagnostic + one-day thin-slice prototype (demo video + handoff docs)',
        'content_engine': 'a signal-source audit + one sample pipeline draft',
        'consulting': 'a diagnostic + roadmap',
    }
    SEED_SPIDER_NAME = 'opportunity_outreach_seed'
    SEED_DATA_TYPE = 'opportunity_seed'
    LLM_MODEL = 'gpt-5-mini'
    MAX_CANDIDATES_WALKED = 200

    # Session 1225 — Rigby's envelope: hard-binds the prompt to the exact
    # delivery shape per offer so the LLM never drifts into guaranteed-outcome
    # marketing copy. Every per-offer block names what is offered AND what is
    # explicitly excluded. Every body must end with a scoping/qualification
    # question so the email earns the meeting instead of asking for it.
    SYSTEM_PROMPT = (
        "You are drafting a cold email on behalf of Chris from Donkey Betz, an "
        "operator-builder who runs small, scoped engagements.\n\n"
        "TONE:\n"
        "- Concise, credible, non-hype. Plain English. No marketing voice.\n"
        "- No fabricated facts — use ONLY fields supplied in the user payload. "
        "If a field is missing, write generically rather than inventing.\n"
        "- No guaranteed outcomes anywhere. Forbidden phrases: 'we will save you', "
        "'guaranteed', 'double your', 'X% improvement', 'ROI of N%', "
        "'production-ready', 'enterprise-grade'. If you catch yourself promising "
        "a result, rewrite as a scoped exploration instead.\n\n"
        "GLOBAL RULES:\n"
        "- Subject: 7 words or fewer.\n"
        "- Body: 120-180 words.\n"
        "- Open with one specific reference (title, company, or domain) drawn "
        "from the payload — never generic.\n"
        "- Body MUST end with a scoping/qualification question (see per-offer "
        "rules below) BEFORE the sign-off. The question goes on its own line.\n"
        "- Sign as 'Chris / Donkey Betz' on the final line.\n"
        "- CTA: 15-minute call AFTER they answer the question, not as the first ask.\n\n"
        "PER-OFFER DELIVERY ENVELOPE (branch on offer_key in user payload):\n\n"
        "offer_key='ai_automation':\n"
        "  WHAT YOU'RE OFFERING: a one-day thin-slice prototype — diagnostic "
        "of one specific workflow + one prototype slice built in either a "
        "no-code/low-code environment OR a code-based repo+PR (recipient picks).\n"
        "  DEFINITION OF DONE: short demo video + handoff docs explaining how it "
        "works and what would have to be true to extend it.\n"
        "  EXPLICITLY NOT INCLUDED: production deployment, access to live data "
        "or systems, ROI guarantees, ongoing maintenance. Name at least one of "
        "these exclusions in the body.\n"
        "  REQUIRED CHECKPOINT QUESTION: ask one scoping question that helps "
        "Chris decide whether the prototype is even feasible. Examples: "
        "'Which workflow currently eats the most manual hours?' or 'Do you have "
        "a sandbox dataset we could prototype against without touching production?'\n\n"
        "offer_key='consulting':\n"
        "  WHAT YOU'RE OFFERING: a diagnostic + written roadmap. Output is the "
        "roadmap document itself, not implementation.\n"
        "  EXPLICITLY NOT INCLUDED: build work, guaranteed outcomes from "
        "following the roadmap, retainer commitment.\n"
        "  REQUIRED QUALIFICATION QUESTIONS: ask 1-2 questions that qualify "
        "whether a roadmap is the right next step. Examples: 'What's the "
        "current bottleneck — clarity, capacity, or capability?' or "
        "'Have you done a similar diagnostic in the last 12 months?'\n\n"
        "offer_key='content_engine':\n"
        "  WHAT YOU'RE OFFERING: a signal-source audit (which inputs you "
        "already have) + one sample pipeline draft showing how a single "
        "signal becomes one published piece.\n"
        "  EXPLICITLY NOT INCLUDED: engagement or conversion guarantees, "
        "ongoing publishing operations, audience-growth promises.\n"
        "  REQUIRED QUALIFICATION QUESTIONS: ask 1-2 questions about the "
        "current content workflow. Examples: 'Where do you source signals "
        "today?' or 'Who edits the final piece before it goes out?'\n\n"
        "OUTPUT:\n"
        "Output ONLY a JSON object with keys: subject, body. No prose outside "
        "the JSON, no markdown fences."
    )

    # ───────────────────────────────────────────────────────────────────
    # Contactability
    # ───────────────────────────────────────────────────────────────────

    @classmethod
    def is_contactable(cls, opportunity) -> bool:
        # Field-name fan-out — Session 1224 smoke surfaced that spider-ingested
        # opps (RemoteOK + others) populate `metadata.url` / `metadata.company`
        # rather than `metadata.contact_email` / `metadata.company_name` /
        # `metadata.domain`. Accept either schema. Top-level `url` column on
        # those rows is empty by design.
        metadata = opportunity.metadata or {}
        # 1. Explicit email anywhere → contactable
        if metadata.get('contact_email') or metadata.get('email'):
            return True
        # 2. Real domain anywhere (top-level or metadata) → contactable
        candidate_urls = (
            opportunity.url,
            metadata.get('url'),
            metadata.get('source_url'),
            metadata.get('domain'),
        )
        has_domain = any(u and cls._extract_domain(u) for u in candidate_urls)
        if has_domain:
            return True
        # 3. Company name + ANY url-shaped field also counts (matches the
        #    original gate intent: company alone isn't enough — need a way to
        #    reference where we saw them).
        company = metadata.get('company_name') or metadata.get('company')
        if company and any(candidate_urls):
            return True
        return False

    @staticmethod
    def _extract_domain(url: str) -> str:
        if not url:
            return ''
        try:
            host = urlparse(url).hostname or ''
        except Exception:
            return ''
        return host.lower().removeprefix('www.')

    # ───────────────────────────────────────────────────────────────────
    # Selection
    # ───────────────────────────────────────────────────────────────────

    @classmethod
    def select_candidate_queryset(cls, scope: str = 'all', user=None):
        from core.models_unified_system import Opportunity
        from core.models_outreach import OutreachDraft

        qs = Opportunity.objects.filter(status='active')
        if scope == 'mine' and user is not None:
            qs = qs.filter(user=user)

        # Exclude opps with any active touch-1 draft already
        active_states = ('draft', 'approved', 'sent', 'replied')
        used_opp_ids = OutreachDraft.objects.filter(
            touch_number=1,
            status__in=active_states,
            opportunity__isnull=False,
        ).values_list('opportunity_id', flat=True)
        qs = qs.exclude(id__in=used_opp_ids)

        return qs.order_by('-match_score', '-potential_revenue', '-created_at')

    @classmethod
    def daily_generated_count(cls, now=None) -> int:
        from core.models_outreach import OutreachDraft

        now = now or timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return OutreachDraft.objects.filter(
            created_at__gte=today_start,
            touch_number=1,
            lead_source=cls.SEED_SPIDER_NAME,
        ).count()

    # ───────────────────────────────────────────────────────────────────
    # Synthetic SpiderData seed (Option A — no migration)
    # ───────────────────────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def ensure_spider_data_seed(cls, opportunity):
        from core.models_unified_system import SpiderData

        existing = SpiderData.objects.filter(
            spider_name=cls.SEED_SPIDER_NAME,
            data_type=cls.SEED_DATA_TYPE,
            raw_data__opportunity_id=str(opportunity.id),
        ).first()
        if existing:
            return existing

        return SpiderData.objects.create(
            spider_name=cls.SEED_SPIDER_NAME,
            source_url=(opportunity.url or '')[:500],
            data_type=cls.SEED_DATA_TYPE,
            raw_data={
                'opportunity_id': str(opportunity.id),
                'title': opportunity.title,
                'description': (opportunity.description or '')[:2000],
                'source': opportunity.source,
                'opportunity_type': opportunity.opportunity_type,
                'url': opportunity.url or '',
                'metadata': opportunity.metadata or {},
            },
            relevance_score=opportunity.match_score,
            is_processed=True,
            is_actionable=True,
        )

    # ───────────────────────────────────────────────────────────────────
    # LLM-rendered email body
    # ───────────────────────────────────────────────────────────────────

    @classmethod
    def build_prompt_payload(cls, opportunity, offer_key: str) -> dict:
        # Field-name fan-out matches is_contactable — spider-ingested opps use
        # metadata.url / metadata.company; user-curated opps may use
        # metadata.company_name / metadata.domain etc.
        metadata = opportunity.metadata or {}
        primary_url = (
            opportunity.url
            or metadata.get('url', '')
            or metadata.get('source_url', '')
        )
        domain = cls._extract_domain(primary_url) or metadata.get('domain', '')
        company = (
            metadata.get('company_name')
            or metadata.get('company')
            or ''
        )
        contact_email = (
            metadata.get('contact_email')
            or metadata.get('email')
            or ''
        )
        age_hours = int(
            (timezone.now() - opportunity.created_at).total_seconds() / 3600
        )
        return {
            'offer_key': offer_key,
            'offer_blurb': cls.OFFER_BLURBS.get(offer_key, ''),
            'opportunity': {
                'title': opportunity.title,
                'description': (opportunity.description or '')[:1500],
                'company_name': company,
                'contact_name': metadata.get('contact_name', ''),
                'contact_email': contact_email,
                'source': opportunity.source,
                'source_url': primary_url,
                'domain': domain,
                'potential_revenue': float(opportunity.potential_revenue or 0),
                'age_hours': age_hours,
            },
        }

    @classmethod
    def render_email(cls, opportunity, offer_key: str) -> dict:
        """Call LLM. On parse/network failure, return a safe deterministic fallback."""
        from core.services.openai_client_factory import get_openai_client

        payload = cls.build_prompt_payload(opportunity, offer_key)
        user_msg = json.dumps(payload, ensure_ascii=False)

        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model=cls.LLM_MODEL,
                messages=[
                    {'role': 'system', 'content': cls.SYSTEM_PROMPT},
                    {'role': 'user', 'content': user_msg},
                ],
                max_completion_tokens=4000,  # Session 1224: gpt-5-mini reasoning needs ≥2000; 4000 leaves comfortable headroom for JSON output
                response_format={'type': 'json_object'},
            )
            raw = response.choices[0].message.content or '{}'
            data = json.loads(raw)
            subject = (data.get('subject') or '').strip()
            body = (data.get('body') or '').strip()
            if subject and body:
                return {'subject': subject[:200], 'body': body, 'fallback': False}
        except Exception as exc:
            logger.warning(
                'OpportunityDraftGenerator.render_email LLM failure opp=%s offer=%s err=%s',
                opportunity.id, offer_key, exc,
            )

        return cls._fallback_email(opportunity, offer_key, payload)

    # Session 1225 — Per-offer scoping/qualification questions used in the
    # fallback skeleton. Match the spirit of the SYSTEM_PROMPT envelope so the
    # fallback path doesn't drift into different framing than the LLM path.
    _FALLBACK_QUESTIONS = {
        'ai_automation': (
            "Which workflow currently eats the most manual hours, and is there "
            "a sandbox dataset we could prototype against without touching "
            "production?"
        ),
        'consulting': (
            "What's the current bottleneck — clarity, capacity, or capability "
            "— and have you done a similar diagnostic in the last 12 months?"
        ),
        'content_engine': (
            "Where do you source signals today, and who edits the final piece "
            "before it goes out?"
        ),
    }

    @classmethod
    def _fallback_email(cls, opportunity, offer_key: str, payload: dict) -> dict:
        """Deterministic skeleton when LLM is unreachable or returns unusable output.

        Session 1225 — Rigby envelope: same delivery shape constraints as
        SYSTEM_PROMPT. No guaranteed outcomes; explicit per-offer scope; ends
        with a qualification question before sign-off.
        """
        opp = payload['opportunity']
        ref = opp['company_name'] or opp['domain'] or opp['title'][:80]
        blurb = cls.OFFER_BLURBS.get(offer_key, 'a small, scoped engagement')
        question = cls._FALLBACK_QUESTIONS.get(
            offer_key,
            'What would a useful 30-minute conversation cover from your side?',
        )
        greeting = f"Hi{(' ' + opp['contact_name']) if opp['contact_name'] else ''},"
        subject = f"Quick idea for {ref}"[:200]
        body = (
            f"{greeting}\n\n"
            f"Saw {ref} and wanted to send a short, no-pitch note. I run "
            f"small, scoped engagements as an operator-builder. For this "
            f"kind of opportunity I typically offer {blurb}.\n\n"
            f"To be clear about what's NOT included: no production deployment, "
            f"no live-system access, no guaranteed outcomes — just a focused "
            f"first slice you can evaluate honestly.\n\n"
            f"Before booking anything, a scoping question:\n"
            f"{question}\n\n"
            f"If your answer points somewhere useful, happy to set up a "
            f"15-minute call.\n\n"
            f"Chris / Donkey Betz"
        )
        return {'subject': subject, 'body': body, 'fallback': True}

    # ───────────────────────────────────────────────────────────────────
    # Top-level entrypoint
    # ───────────────────────────────────────────────────────────────────

    @classmethod
    def generate(
        cls,
        limit: Optional[int] = None,
        scope: str = 'all',
        offers: Optional[Iterable[str]] = None,
        user=None,
        now=None,
    ) -> dict:
        """Generate up to `limit` touch-1 drafts. Respects the daily cap."""
        from core.models_outreach import OutreachDraft

        now = now or timezone.now()
        offers = list(offers) if offers else list(cls.OFFER_KEYS)
        limit = cls.DAILY_GENERATE_CAP if limit is None else int(limit)

        already_today = cls.daily_generated_count(now)
        remaining = max(0, cls.DAILY_GENERATE_CAP - already_today)
        target = min(limit, remaining)

        result = {
            'requested': limit,
            'scope': scope,
            'offers': offers,
            'already_today': already_today,
            'daily_cap': cls.DAILY_GENERATE_CAP,
            'remaining_before': remaining,
            'created': 0,
            'skipped_uncontactable': 0,
            'candidates_walked': 0,
            'errors': [],
            'drafts': [],
        }
        if target <= 0:
            result['note'] = 'daily cap reached'
            return result

        offer_cycle = _round_robin(offers)
        candidates_qs = cls.select_candidate_queryset(scope=scope, user=user)

        for opp in candidates_qs.iterator(chunk_size=50):
            if result['created'] >= target:
                break
            if result['candidates_walked'] >= cls.MAX_CANDIDATES_WALKED:
                break
            result['candidates_walked'] += 1

            if not cls.is_contactable(opp):
                result['skipped_uncontactable'] += 1
                continue

            offer_key = next(offer_cycle)
            try:
                seed = cls.ensure_spider_data_seed(opp)
                rendered = cls.render_email(opp, offer_key)
                # Same field-name fan-out as is_contactable / build_prompt_payload
                opp_md = opp.metadata or {}
                effective_url = (
                    opp.url
                    or opp_md.get('url', '')
                    or opp_md.get('source_url', '')
                    or ''
                )
                draft = OutreachDraft.objects.create(
                    spider_data_id=seed.id,
                    opportunity=opp,
                    lead_title=opp.title[:200],
                    lead_source=cls.SEED_SPIDER_NAME,
                    lead_url=effective_url[:500],
                    lead_score=opp.match_score,
                    offer_key=offer_key,
                    subject_line=rendered['subject'],
                    body_text=rendered['body'],
                    channel='email',
                    touch_number=1,
                    status='draft',
                    user=opp.user,
                    trace_id=(
                        f"opp_gen:{now.strftime('%Y%m%d')}:"
                        f"{result['created'] + 1}"
                    ),
                )
                result['created'] += 1
                result['drafts'].append({
                    'id': str(draft.id),
                    'opportunity_id': str(opp.id),
                    'offer_key': offer_key,
                    'subject': draft.subject_line,
                    'fallback': rendered.get('fallback', False),
                })
            except Exception as exc:
                logger.exception(
                    'OpportunityDraftGenerator.generate failed opp=%s', opp.id,
                )
                result['errors'].append({
                    'opportunity_id': str(opp.id),
                    'error': str(exc)[:200],
                })

        return result


def _round_robin(items: Iterable[str]):
    """Yield items in round-robin order forever (caller controls termination)."""
    seq = list(items)
    if not seq:
        return
    i = 0
    while True:
        yield seq[i % len(seq)]
        i += 1
