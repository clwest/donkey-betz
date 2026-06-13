"""
ToolDispatcher NewsletterHandlersMixin — newsletter_tool handler.

Session 1077+: POC 1 — Autopilot Ops Newsletter

Actions:
  prepare     — Transform an issue deliverable into publish-ready artifact
  outline     — Generate a Template v1 outline for a new issue
  validate    — Check an issue draft against Template v1 completeness
  metrics     — Compute/store metrics for an issue
  list_issues — List newsletter issue deliverables
  config      — View/update newsletter config (provider, URLs, etc.)
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class NewsletterHandlersMixin:
    """Mixin providing newsletter_tool handler for ToolDispatcher."""

    def _handle_newsletter(self, tool_name, payload, user_id, trace_id):
        """Handle newsletter_tool actions."""
        action = payload.get('action', 'list_issues')

        if action == 'prepare':
            return self._newsletter_prepare(payload, user_id, trace_id)
        elif action == 'outline':
            return self._newsletter_outline(payload, user_id, trace_id)
        elif action == 'validate':
            return self._newsletter_validate(payload, user_id, trace_id)
        elif action == 'metrics':
            return self._newsletter_metrics(payload, user_id, trace_id)
        elif action == 'list_issues':
            return self._newsletter_list_issues(payload, user_id, trace_id)
        elif action == 'config':
            return self._newsletter_config(payload, user_id, trace_id)
        elif action == 'sources':
            return self._newsletter_sources(payload, user_id, trace_id)
        else:
            return {'error': f'Unknown newsletter action: {action}', 'action': action}

    # ── prepare ─────────────────────────────────────────────────────────────

    def _load_newsletter_config(self):
        """Load saved newsletter config from the config deliverable."""
        from core.models_deliverables import Deliverable
        defaults = {
            'provider': 'substack_manual',
            'subscribe_url': 'https://autopilotops.substack.com',
            'sponsor_email': 'sponsor@autopilotops.com',
            'publication_name': 'Autopilot Ops',
        }
        config_del = Deliverable.objects.filter(
            title='Newsletter Config — Autopilot Ops',
            category='Newsletter',
        ).order_by('-created_at').first()
        if config_del and config_del.metadata:
            logger.info(f"Newsletter config loaded from deliverable {config_del.id}")
            for key in defaults:
                val = config_del.metadata.get(key)
                if val and str(val).strip():
                    defaults[key] = val
        else:
            logger.warning("No newsletter config deliverable found; using defaults")
        logger.info(f"Newsletter config resolved: subscribe_url={defaults['subscribe_url']}")
        return defaults

    def _newsletter_prepare(self, payload, user_id, trace_id):
        """Transform an issue deliverable into a publish-ready artifact."""
        from core.models_deliverables import Deliverable
        from core.services.newsletter_publisher import get_publisher

        # Load saved config, then allow payload overrides
        saved_config = self._load_newsletter_config()
        deliverable_id = payload.get('id') or payload.get('deliverable_id')
        provider_name = payload.get('provider') or saved_config['provider']
        subscribe_url = payload.get('subscribe_url') or saved_config['subscribe_url']
        sponsor_email = payload.get('sponsor_email') or saved_config['sponsor_email']

        if not deliverable_id:
            return {'error': 'id (deliverable_id) is required', 'action': 'prepare'}

        try:
            deliverable = Deliverable.objects.get(id=deliverable_id)
        except Deliverable.DoesNotExist:
            return {'error': f'Deliverable {deliverable_id} not found', 'action': 'prepare'}

        # Extract issue number from title or metadata
        issue_number = (
            deliverable.metadata.get('issue_number')
            if deliverable.metadata else None
        )
        if not issue_number:
            import re
            m = re.search(r'#(\d+)', deliverable.title)
            issue_number = int(m.group(1)) if m else 1

        publisher = get_publisher(provider_name)
        metadata = {
            'title': deliverable.title,
            'issue_number': issue_number,
            'subscribe_url': subscribe_url,
            'sponsor_email': sponsor_email,
        }

        result = publisher.prepare_issue(deliverable.content, metadata)

        # Save the publish-ready artifacts — update existing if re-prepared
        # Inherit workspace + initiative from source deliverable, allow payload override
        workspace_id = payload.get('workspace_id') or getattr(deliverable, 'workspace_id', None)
        initiative_id = deliverable.initiative_id if deliverable.initiative_id else None

        # Lookup key for dedup: title + category + agent_name
        _lookup = lambda title: dict(title=title, category='Newsletter', agent_name='NewsletterTool')

        # Save markdown version (update if exists)
        md_deliverable, _ = Deliverable.objects.update_or_create(
            **_lookup(f"Newsletter #{issue_number} — Publish-Ready (Markdown)"),
            defaults=dict(
                deliverable_type='document',
                content=result['markdown'],
                content_format='markdown',
                user_id=user_id,
                workspace_id=workspace_id,
                initiative_id=initiative_id,
                is_saved=True,
                metadata={
                    'newsletter': True,
                    'issue_number': issue_number,
                    'provider': provider_name,
                    'source_deliverable_id': str(deliverable_id),
                    'subjects': result['subjects'],
                    'preview_text': result['preview_text'],
                    'stats': result['stats'],
                    'artifact_type': 'publish_ready_markdown',
                },
            ),
        )

        # Save HTML version (update if exists)
        html_deliverable, _ = Deliverable.objects.update_or_create(
            **_lookup(f"Newsletter #{issue_number} — Publish-Ready (HTML)"),
            defaults=dict(
                deliverable_type='document',
                content=result['html'],
                content_format='html',
                user_id=user_id,
                workspace_id=workspace_id,
                initiative_id=initiative_id,
                is_saved=True,
                metadata={
                    'newsletter': True,
                    'issue_number': issue_number,
                    'provider': provider_name,
                    'source_deliverable_id': str(deliverable_id),
                    'artifact_type': 'publish_ready_html',
                },
            ),
        )

        # Save publish checklist
        checklist_content = f"# Publish Checklist — Issue #{issue_number}\n\n"
        checklist_content += f"**Provider:** {provider_name}\n"
        checklist_content += f"**Source:** {deliverable.title}\n\n"
        checklist_content += "## Subject Line Options\n"
        for i, subj in enumerate(result['subjects'], 1):
            checklist_content += f"{i}. {subj}\n"
        checklist_content += f"\n**Preview text:** {result['preview_text']}\n\n"
        checklist_content += "## Validation\n"
        if result['validation_issues']:
            for issue in result['validation_issues']:
                icon = '❌' if issue['severity'] == 'error' else '⚠️'
                checklist_content += f"- {icon} {issue['message']}\n"
        else:
            checklist_content += "- All sections present and meet length targets.\n"
        checklist_content += f"\n## Stats\n"
        for k, v in result['stats'].items():
            checklist_content += f"- **{k}:** {v}\n"
        checklist_content += f"\n## Steps\n"
        for step in result['checklist']:
            checklist_content += f"- [ ] {step}\n"

        checklist_deliverable, _ = Deliverable.objects.update_or_create(
            **_lookup(f"Newsletter #{issue_number} — Publish Checklist"),
            defaults=dict(
                deliverable_type='document',
                content=checklist_content,
                content_format='markdown',
                user_id=user_id,
                workspace_id=workspace_id,
                initiative_id=initiative_id,
                is_saved=True,
                metadata={
                    'newsletter': True,
                    'issue_number': issue_number,
                    'provider': provider_name,
                    'source_deliverable_id': str(deliverable_id),
                    'artifact_type': 'publish_checklist',
                },
            ),
        )

        # Save subject + preheader options as a deliverable
        subject_content = f"# Newsletter #{issue_number} — Subject & Preheader Options\n\n"
        subject_content += "## Subject Line Options\n"
        for i, subj in enumerate(result['subjects'], 1):
            subject_content += f"{i}. {subj}\n"
        subject_content += f"\n## Preview Text (Preheader)\n{result['preview_text']}\n"
        subject_content += f"\n## Stats\n"
        subject_content += f"- Word count: {result['stats']['word_count']}\n"
        subject_content += f"- Reading time: {result['stats']['reading_time_min']} min\n"
        subject_content += f"- Links: {result['stats']['link_count']}\n"
        subject_content += f"- Sections: {result['stats']['section_count']}\n"

        subject_deliverable, _ = Deliverable.objects.update_or_create(
            **_lookup(f"Newsletter #{issue_number} — Subject + Preheader Options"),
            defaults=dict(
                deliverable_type='document',
                content=subject_content,
                content_format='markdown',
                user_id=user_id,
                workspace_id=workspace_id,
                initiative_id=initiative_id,
                is_saved=True,
                metadata={
                    'newsletter': True,
                    'issue_number': issue_number,
                    'provider': provider_name,
                    'source_deliverable_id': str(deliverable_id),
                    'artifact_type': 'subject_preheader',
                    'subjects': result['subjects'],
                    'preview_text': result['preview_text'],
                },
            ),
        )

        return {
            'action': 'prepare',
            'provider': provider_name,
            'source_deliverable_id': str(deliverable_id),
            'issue_number': issue_number,
            'artifacts': {
                'markdown_id': str(md_deliverable.id),
                'html_id': str(html_deliverable.id),
                'checklist_id': str(checklist_deliverable.id),
                'subject_id': str(subject_deliverable.id),
            },
            'subjects': result['subjects'],
            'preview_text': result['preview_text'],
            'stats': result['stats'],
            'validation_issues': result['validation_issues'],
            'sections_found': result['sections_found'],
            'sections_missing': result['sections_missing'],
            'checklist_steps': len(result['checklist']),
        }

    # ── outline ─────────────────────────────────────────────────────────────

    def _newsletter_outline(self, payload, user_id, trace_id):
        """Generate a Template v1 outline for a new issue."""
        from core.models_deliverables import Deliverable
        from core.services.newsletter_publisher import generate_issue_outline

        issue_number = payload.get('issue_number', 1)
        workspace_id = payload.get('workspace_id')
        initiative_id = payload.get('initiative_id')

        # Load sources — from explicit deliverable or from built-in source pack.
        # Session 1103c: was 'except Deliverable.DoesNotExist: pass'
        # which silently fell back to the built-in source pack when a
        # caller passed an explicit source_pack_id that no longer
        # existed. The newsletter would generate with the wrong sources
        # and the caller wouldn't know their pack reference was stale.
        sources = None
        source_pack_id = payload.get('source_pack_id')
        if source_pack_id:
            try:
                sp = Deliverable.objects.get(id=source_pack_id)
                if sp.metadata and sp.metadata.get('sources'):
                    sources = sp.metadata['sources']
            except Deliverable.DoesNotExist:
                logger.warning(
                    "td_handlers_newsletter: source_pack_id=%s not found "
                    "— falling back to built-in source pack. Caller "
                    "passed a stale or invalid pack reference.",
                    source_pack_id,
                )
        if not sources:
            from core.services.newsletter_sources import get_sources
            raw = get_sources()
            sources = [{'title': s['name'], 'url': s['url'], 'category': s['category']} for s in raw]

        outline = generate_issue_outline(issue_number, sources)

        # Save as deliverable (update if re-generated)
        deliverable, _ = Deliverable.objects.update_or_create(
            title=f"Autopilot Ops — Issue #{issue_number} (Outline)",
            category='Newsletter',
            agent_name='NewsletterTool',
            defaults=dict(
                deliverable_type='document',
                content=outline,
                content_format='markdown',
                user_id=user_id,
                workspace_id=workspace_id,
                initiative_id=initiative_id,
                is_saved=True,
                metadata={
                    'newsletter': True,
                    'issue_number': issue_number,
                    'artifact_type': 'outline',
                    'status': 'outline',
                },
            ),
        )

        return {
            'action': 'outline',
            'id': str(deliverable.id),
            'title': deliverable.title,
            'issue_number': issue_number,
            'message': f"Created outline for Issue #{issue_number}. Edit the deliverable to fill in content.",
        }

    # ── validate ────────────────────────────────────────────────────────────

    def _newsletter_validate(self, payload, user_id, trace_id):
        """Validate an issue draft against Template v1 completeness."""
        from core.models_deliverables import Deliverable
        from core.services.newsletter_publisher import (
            _extract_sections, _validate_sections, _word_count, _count_links,
            TEMPLATE_V1_SECTIONS,
        )

        deliverable_id = payload.get('id') or payload.get('deliverable_id')
        if not deliverable_id:
            return {'error': 'id (deliverable_id) is required', 'action': 'validate'}

        try:
            deliverable = Deliverable.objects.get(id=deliverable_id)
        except Deliverable.DoesNotExist:
            return {'error': f'Deliverable {deliverable_id} not found', 'action': 'validate'}

        sections = _extract_sections(deliverable.content)
        issues = _validate_sections(sections)

        total_words = _word_count(deliverable.content)
        in_range = 1000 <= total_words <= 1600

        section_details = {}
        for spec in TEMPLATE_V1_SECTIONS:
            key = spec['key']
            text = sections.get(key, '')
            section_details[spec['label']] = {
                'present': bool(text),
                'word_count': _word_count(text) if text else 0,
                'target_min': spec['min_words'],
                'required': spec['required'],
            }

        errors = [i for i in issues if i['severity'] == 'error']
        warnings = [i for i in issues if i['severity'] == 'warning']

        return {
            'action': 'validate',
            'deliverable_id': str(deliverable_id),
            'title': deliverable.title,
            'pass': len(errors) == 0 and in_range,
            'total_words': total_words,
            'word_count_in_range': in_range,
            'target_range': '1000-1600',
            'link_count': _count_links(deliverable.content),
            'errors': errors,
            'warnings': warnings,
            'sections': section_details,
        }

    # ── metrics ─────────────────────────────────────────────────────────────

    def _newsletter_metrics(self, payload, user_id, trace_id):
        """Compute or update metrics for an issue."""
        from core.models_deliverables import Deliverable
        from core.services.newsletter_publisher import compute_issue_metrics

        deliverable_id = payload.get('id') or payload.get('deliverable_id')
        if not deliverable_id:
            return {'error': 'id (deliverable_id) is required', 'action': 'metrics'}

        try:
            deliverable = Deliverable.objects.get(id=deliverable_id)
        except Deliverable.DoesNotExist:
            return {'error': f'Deliverable {deliverable_id} not found', 'action': 'metrics'}

        issue_number = (
            deliverable.metadata.get('issue_number')
            if deliverable.metadata else None
        ) or 0

        metrics = compute_issue_metrics(deliverable.content, issue_number, deliverable.title)

        # Allow manual metric updates via payload
        manual_fields = ['send_date', 'opens', 'clicks', 'unsubscribes', 'new_subscribers']
        for field in manual_fields:
            if payload.get(field) is not None:
                metrics[field] = payload[field]

        # Save metrics to deliverable metadata
        meta = deliverable.metadata or {}
        meta['newsletter_metrics'] = metrics
        deliverable.metadata = meta
        deliverable.save(update_fields=['metadata'])

        return {
            'action': 'metrics',
            'deliverable_id': str(deliverable_id),
            'title': deliverable.title,
            'metrics': metrics,
        }

    # ── list_issues ─────────────────────────────────────────────────────────

    def _newsletter_list_issues(self, payload, user_id, trace_id):
        """List newsletter issue deliverables."""
        from core.models_deliverables import Deliverable

        limit = min(payload.get('limit', 20), 50)
        offset = payload.get('offset', 0)
        artifact_type = payload.get('artifact_type')  # outline, draft, publish_ready, etc.

        qs = Deliverable.objects.filter(
            category='Newsletter',
        ).order_by('-created_at')

        if user_id:
            from django.db.models import Q
            qs = qs.filter(Q(user_id=user_id) | Q(user__isnull=True))

        if artifact_type:
            qs = qs.filter(metadata__artifact_type=artifact_type)

        total = qs.count()
        items = []
        for d in qs[offset:offset + limit]:
            meta = d.metadata or {}
            items.append({
                'id': str(d.id),
                'title': d.title,
                'issue_number': meta.get('issue_number'),
                'artifact_type': meta.get('artifact_type', 'unknown'),
                'provider': meta.get('provider'),
                'content_format': d.content_format,
                'is_saved': d.is_saved,
                'created_at': str(d.created_at),
            })

        return {
            'action': 'list_issues',
            'total': total,
            'offset': offset,
            'limit': limit,
            'count': len(items),
            'items': items,
        }

    # ── config ──────────────────────────────────────────────────────────────

    def _newsletter_config(self, payload, user_id, trace_id):
        """View or update newsletter configuration."""
        from core.models_deliverables import Deliverable

        config_title = 'Newsletter Config — Autopilot Ops'
        defaults = {
            'newsletter_config': True,
            'provider': 'substack_manual',
            'subscribe_url': 'https://autopilotops.substack.com',
            'sponsor_email': 'sponsor@autopilotops.com',
            'publication_name': 'Autopilot Ops',
        }

        updates = {}
        for key in ['provider', 'subscribe_url', 'sponsor_email', 'publication_name', 'publication_slug']:
            val = payload.get(key)
            if val is not None and val != '':
                updates[key] = val

        config_del, created = Deliverable.objects.get_or_create(
            title=config_title,
            category='Newsletter',
            defaults={
                'content': 'Newsletter configuration — see metadata.',
                'agent_name': 'NewsletterTool',
                'deliverable_type': 'document',
                'content_format': 'text',
                'is_saved': True,
                'metadata': {**defaults, **updates},
            },
        )

        meta = config_del.metadata or {}
        meta = {**defaults, **meta, **updates}
        config_del.metadata = meta
        config_del.save(update_fields=['metadata'])

        return {
            'action': 'config',
            'updated': bool(updates) or created,
            'created': created,
            'config': config_del.metadata or {},
        }

    # ── sources ─────────────────────────────────────────────────────────────

    def _newsletter_sources(self, payload, user_id, trace_id):
        """View the newsletter source pack."""
        from core.services.newsletter_sources import get_sources, get_source_summary

        category = payload.get('category')
        section = payload.get('section')

        if category or section:
            sources = get_sources(category=category, section=section)
            return {
                'action': 'sources',
                'filter': {'category': category, 'section': section},
                'count': len(sources),
                'sources': sources,
            }

        summary = get_source_summary()
        return {
            'action': 'sources',
            'summary': summary,
            'sources': get_sources(),
        }
