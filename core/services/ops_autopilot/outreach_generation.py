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
    OFFER_BLURBS = {
        'ai_automation': 'automating a manual workflow or reducing ops time',
        'content_engine': 'turning signals into a daily/weekly content pipeline',
        'consulting': 'a diagnostic → roadmap → build engagement',
    }
    SEED_SPIDER_NAME = 'opportunity_outreach_seed'
    SEED_DATA_TYPE = 'opportunity_seed'
    LLM_MODEL = 'gpt-5-mini'
    MAX_CANDIDATES_WALKED = 200

    SYSTEM_PROMPT = (
        "You are writing a cold email for consulting/freelance services on "
        "behalf of Chris from Donkey Betz.\n\n"
        "Tone: concise, credible, non-hype. No fabricated facts — only use "
        "fields supplied in the user payload. If a field is missing, write "
        "generically rather than inventing.\n\n"
        "Rules:\n"
        "- Subject: 7 words or fewer.\n"
        "- Body: 120-180 words.\n"
        "- Open with one specific reference (title or domain) drawn from "
        "the payload.\n"
        "- Include exactly one concrete 'quick win' aligned to offer_key:\n"
        "    ai_automation: automating a manual workflow / reducing ops time\n"
        "    content_engine: turning signals into a content pipeline\n"
        "    consulting: diagnostic → roadmap → build\n"
        "- CTA: 15-minute discovery call.\n"
        "- Sign as 'Chris / Donkey Betz'.\n\n"
        "Output ONLY a JSON object with keys: subject, body. No prose, no "
        "markdown."
    )

    # ───────────────────────────────────────────────────────────────────
    # Contactability
    # ───────────────────────────────────────────────────────────────────

    @classmethod
    def is_contactable(cls, opportunity) -> bool:
        metadata = opportunity.metadata or {}
        if metadata.get('contact_email'):
            return True
        if metadata.get('company_name') and (metadata.get('domain') or opportunity.url):
            return True
        return bool(cls._extract_domain(opportunity.url or ''))

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
        metadata = opportunity.metadata or {}
        domain = cls._extract_domain(opportunity.url or '') or metadata.get('domain', '')
        age_hours = int(
            (timezone.now() - opportunity.created_at).total_seconds() / 3600
        )
        return {
            'offer_key': offer_key,
            'offer_blurb': cls.OFFER_BLURBS.get(offer_key, ''),
            'opportunity': {
                'title': opportunity.title,
                'description': (opportunity.description or '')[:1500],
                'company_name': metadata.get('company_name', ''),
                'contact_name': metadata.get('contact_name', ''),
                'contact_email': metadata.get('contact_email', ''),
                'source': opportunity.source,
                'source_url': opportunity.url or '',
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
                max_completion_tokens=800,
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

    @classmethod
    def _fallback_email(cls, opportunity, offer_key: str, payload: dict) -> dict:
        """Deterministic skeleton when LLM is unreachable or returns unusable output."""
        opp = payload['opportunity']
        ref = opp['company_name'] or opp['domain'] or opp['title'][:80]
        blurb = cls.OFFER_BLURBS.get(offer_key, '')
        subject = f"Quick idea for {ref}"[:200]
        body = (
            f"Hi{(' ' + opp['contact_name']) if opp['contact_name'] else ''},\n\n"
            f"Saw {ref} and wanted to send a short note. I help operators with {blurb}.\n\n"
            f"Happy to share one concrete idea over a 15-minute call if useful — "
            f"no pitch, just the idea.\n\n"
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
                draft = OutreachDraft.objects.create(
                    spider_data_id=seed.id,
                    opportunity=opp,
                    lead_title=opp.title[:200],
                    lead_source=cls.SEED_SPIDER_NAME,
                    lead_url=(opp.url or '')[:500],
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
