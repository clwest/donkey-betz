"""
Phase 4: Content Deliberation Runner

Full pipeline:
  Spider signals -> ClaimsPack -> ContentWriter draft (citing claims) ->
  3-reviewer panel -> DecisionEnforcer (PUBLISH/REVISE/KILL) ->
  PublishGate -> SelfBlog with stats_snapshot['deliberation']

Uses ConversationOrchestrator for the review conversation to get
DeliberationSession, turn persistence, evidence/trace, and DecisionEnforcer.

Graceful degradation: every step is try/except, failures -> draft status.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ContentDeliberationRunner:
    """Runs the full content deliberation pipeline."""

    def run_blog(self, topic: str, voice: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a blog through the deliberation pipeline.

        Returns:
            {
                'status': 'published' | 'draft' | 'killed',
                'selfblog_id': str | None,
                'deliberation_session_id': str | None,
                'decision': 'PUBLISH' | 'REVISE' | 'KILL',
                'gate_result': dict | None,
                'summary': {claims_used, sources, reviewers, revisions},
            }
        """
        result = {
            'status': 'draft',
            'selfblog_id': None,
            'deliberation_session_id': None,
            'decision': 'REVISE',
            'gate_result': None,
            'summary': {
                'claims_used': 0,
                'sources': 0,
                'reviewers': [],
                'revisions': 0,
            },
        }

        # ── Step 1: Build ClaimsPack ──
        claims_pack = None
        try:
            from core.services.claims_pack_builder import get_claims_pack_builder
            claims_pack = get_claims_pack_builder().build(topic)
            result['summary']['claims_used'] = len(claims_pack.claims)
            result['summary']['sources'] = len(claims_pack.sources)
        except Exception as e:
            logger.warning(f"[Phase 4] ClaimsPack build failed, continuing without claims: {e}")

        # ── Step 2: Draft via ContentWriterAgent ──
        draft_text = ''
        generated_content = {}
        try:
            draft_text, generated_content = self._generate_draft(topic, claims_pack, voice)
        except Exception as e:
            logger.error(f"[Phase 4] Draft generation failed: {e}")
            result['failure_reason_code'] = 'DRAFT_FAILED'
            result['failure_detail'] = str(e)[:500]
            return result  # Can't proceed without a draft

        if not draft_text:
            logger.error("[Phase 4] Draft generation returned empty text")
            result['failure_reason_code'] = 'DRAFT_FAILED'
            result['failure_detail'] = 'Draft generation returned empty text'
            return result

        # ── Step 3: Review conversation via ConversationOrchestrator ──
        review_results = []
        session_id = None
        mandate_dict = None
        try:
            review_results, session_id, mandate_dict = self._run_review_conversation(
                draft_text, claims_pack, topic
            )
            result['deliberation_session_id'] = session_id
            result['summary']['reviewers'] = [
                r.get('reviewer', 'unknown') for r in review_results
            ]
        except Exception as e:
            logger.warning(f"[Phase 4] Review conversation failed: {e}")
            # All reviewers fail -> save as draft with 'panel_failed'
            result['decision'] = 'REVISE'

        # ── Step 4: Extract decision ──
        decision = self._extract_decision(mandate_dict, review_results)

        # ── Step 4b: Block PUBLISH without research backing ──
        claims_count = len(claims_pack.claims) if claims_pack else 0
        if decision == 'PUBLISH' and claims_count == 0:
            logger.info("[Phase 4] Downgrading PUBLISH → REVISE: no research claims backing content")
            decision = 'REVISE'

        result['decision'] = decision

        # ── Step 5: If REVISE, one rewrite pass ──
        if decision == 'REVISE':
            try:
                rewrite = self._rewrite_draft(topic, draft_text, review_results, claims_pack, voice)
                if rewrite:
                    draft_text = rewrite[0]
                    generated_content = rewrite[1]
                    result['summary']['revisions'] = 1
            except Exception as e:
                logger.warning(f"[Phase 4] Rewrite failed, using original draft: {e}")

        # ── Step 6: Append ClaimsPack to evidence pack ──
        if session_id and claims_pack:
            try:
                self._append_claims_to_evidence(session_id, claims_pack)
            except Exception as e:
                logger.warning(f"[Phase 4] Evidence pack append failed: {e}")

        # ── Step 7: Save blog ──
        blog = None
        try:
            blog = self._save_blog(
                topic, draft_text, generated_content, claims_pack,
                decision, session_id, review_results, voice
            )
            result['selfblog_id'] = str(blog.id)
        except Exception as e:
            logger.error(f"[Phase 4] Blog save failed: {e}")
            return result

        # ── Step 8: PublishGate (only if decision=PUBLISH) ──
        if decision == 'PUBLISH' and blog:
            try:
                gate_result = self._run_publish_gate(blog)
                result['gate_result'] = {
                    'decision': gate_result.decision,
                    'quality_score': gate_result.quality_score,
                    'novelty_score': gate_result.novelty_score,
                    'structure_score': gate_result.structure_score,
                    'mythology_score': gate_result.mythology_score,
                }
                if gate_result.decision == 'publish':
                    blog.status = 'approved'  # Session 1008: Direct to approved (was pending_review, blocking auto-publish)
                    blog.content_type = 'public'
                    blog.publish_ready = True  # Session 998: Gate passed → mark publish-ready
                    blog.save(update_fields=['status', 'content_type', 'publish_ready'])
                    result['status'] = 'published'
                else:
                    blog.gate_notes = gate_result.notes
                    blog.save(update_fields=['gate_notes'])
                    result['status'] = 'draft'
            except Exception as e:
                logger.warning(f"[Phase 4] PublishGate failed: {e}")

        # ── Step 9: Status mapping ──
        if result['status'] != 'published':
            if decision == 'KILL':
                result['status'] = 'killed'
            elif decision == 'REVISE':
                # Session 1007: REVISE blogs → needs_enhancement for auto-revision loop
                result['status'] = 'needs_enhancement'
            else:
                result['status'] = 'draft'

        logger.info(
            f"[Phase 4] Deliberation complete: decision={decision}, "
            f"status={result['status']}, blog={result['selfblog_id']}, "
            f"session={result['deliberation_session_id']}"
        )
        return result

    def _generate_draft(self, topic, claims_pack, voice):
        """Generate initial draft using ContentWriterAgent."""
        from core.agents.content_writer_agent import ContentWriterAgent

        agent = ContentWriterAgent()

        # Build research context with claims block
        research = ''
        if claims_pack and claims_pack.claims:
            research = claims_pack.to_prompt_block()

        # Session 1001: Inject real operational telemetry
        try:
            from core.tasks import _build_operational_context
            operational_context = _build_operational_context()
            if operational_context:
                research += f"\n\n{operational_context}"
        except Exception as e:
            logger.warning(f"[Phase 4] Operational context injection failed: {e}")

        task_str = f'Write a blog post about: {topic}'
        context = {
            'research': research,
            'topic': topic,
            'tone': voice or 'professional',
            'target_audience': 'general',
            'word_count': 1500,
            'content_type': 'blog_post',
        }

        result = agent.execute(
            task=task_str,
            context=context,
            scifi_context={},
            spider_context={},
        )

        if not result or not result.success:
            raise RuntimeError(f"ContentWriterAgent failed: {result}")

        generated_content = result.data.get('content', {})
        full_text = generated_content.get('full_text', '') if isinstance(generated_content, dict) else ''

        return full_text, generated_content

    def _run_review_conversation(self, draft_text, claims_pack, topic):
        """Run 3-reviewer panel then ConversationOrchestrator critique."""
        from core.services.content_review_panel_v2 import run_reviews, _detect_domain

        domain = _detect_domain(topic)
        review_results = run_reviews(draft_text, claims_pack, topic, domain)

        # Build review summary for the orchestrator critique conversation
        review_summary_lines = []
        for r in review_results:
            reviewer = r.get('reviewer', 'unknown')
            verdict = r.get('verdict', 'FAIL')
            issues = r.get('top_issues', [])
            issue_text = '; '.join(i.get('detail', '')[:100] for i in issues[:3])
            review_summary_lines.append(f"{reviewer}: {verdict} — {issue_text}")

        review_block = '\n'.join(review_summary_lines)

        # Run orchestrator critique conversation with review context
        from core.conversation_orchestrator import ConversationOrchestrator
        orchestrator = ConversationOrchestrator()

        critique_topic = (
            f"Content Review for: {topic}\n\n"
            f"REVIEWER FEEDBACK:\n{review_block}\n\n"
            f"DRAFT (first 3000 chars):\n{draft_text[:3000]}"
        )

        conv_result = orchestrator.generate_conversation(
            agent1={'name': 'EditorAgent', 'type': 'EditorAgent', 'specialization': 'Content editing'},
            agent2={'name': 'ContentStrategyAgent', 'type': 'ContentStrategyAgent', 'specialization': 'Content strategy'},
            topic=critique_topic,
            conversation_type='critique',
            num_turns=4,
            objective=f'Decide whether to PUBLISH, REVISE, or KILL the blog about {topic}',
            success_criteria=['Clear PUBLISH/REVISE/KILL decision', 'Specific improvement recommendations'],
        )

        session_id = conv_result.get('deliberation_session_id')
        mandate_dict = conv_result.get('execution_mandate')

        return review_results, session_id, mandate_dict

    def _extract_decision(self, mandate_dict, review_results):
        """Extract PUBLISH/REVISE/KILL from mandate or reviewer verdicts."""
        # Try mandate first
        if mandate_dict and isinstance(mandate_dict, dict):
            chosen = (mandate_dict.get('chosen_path') or '').upper()
            for keyword in ('PUBLISH', 'KILL', 'REVISE'):
                if keyword in chosen:
                    return keyword

        # Fallback: if all reviewers PASS -> PUBLISH, any FAIL -> REVISE
        if review_results:
            verdicts = [r.get('verdict', 'FAIL') for r in review_results]
            if all(v == 'PASS' for v in verdicts):
                return 'PUBLISH'
            if any(v == 'FAIL' for v in verdicts):
                return 'REVISE'

        # Default
        return 'REVISE'

    def _rewrite_draft(self, topic, draft_text, review_results, claims_pack, voice):
        """One rewrite pass incorporating review feedback."""
        from core.agents.content_writer_agent import ContentWriterAgent

        feedback_lines = []
        for r in review_results:
            changes = r.get('required_changes', [])
            feedback_lines.extend(changes[:3])

        if not feedback_lines:
            return None

        agent = ContentWriterAgent()

        research = ''
        if claims_pack and claims_pack.claims:
            research = claims_pack.to_prompt_block()

        feedback_block = '\n'.join(f'- {line}' for line in feedback_lines)

        task_str = (
            f'Rewrite this blog post about: {topic}\n\n'
            f'REVIEWER FEEDBACK TO ADDRESS:\n{feedback_block}\n\n'
            f'ORIGINAL DRAFT:\n{draft_text[:4000]}'
        )
        context = {
            'research': research,
            'topic': topic,
            'tone': voice or 'professional',
            'target_audience': 'general',
            'word_count': 1500,
            'content_type': 'blog_post',
        }

        result = agent.execute(
            task=task_str,
            context=context,
            scifi_context={},
            spider_context={},
        )
        if not result or not result.success:
            return None

        generated_content = result.data.get('content', {})
        full_text = generated_content.get('full_text', '') if isinstance(generated_content, dict) else ''
        if not full_text:
            return None

        return full_text, generated_content

    def _append_claims_to_evidence(self, session_id, claims_pack):
        """Append ClaimsPack sources and claims to the evidence pack."""
        from core.models_deliberation import DeliberationSession
        from core.services.evidence_pack_builder import get_evidence_pack_builder

        session = DeliberationSession.objects.get(id=session_id)
        builder = get_evidence_pack_builder()

        for source in claims_pack.to_evidence_sources():
            builder.append_source(session, source)

        builder.append_claims(session, claims_pack.to_evidence_claims())

    def _save_blog(
        self, topic, draft_text, generated_content, claims_pack,
        decision, session_id, review_results, voice
    ):
        """Save blog to SelfBlog with deliberation metadata in stats_snapshot."""
        from core.models_unified_system import SelfBlog

        # Status mapping
        if decision == 'KILL':
            status = 'draft'
            content_type = 'internal'
        elif decision == 'PUBLISH':
            status = 'pending_review'
            content_type = 'public'
        else:
            # Session 1007: REVISE → needs_enhancement so EditorAgent picks them up
            status = 'needs_enhancement'
            content_type = 'public'

        # Check if all reviewers failed
        gate_notes = ''
        if review_results and all(
            r.get('verdict') == 'FAIL' and
            any(i.get('type') == 'reviewer_error' for i in r.get('top_issues', []))
            for r in review_results
        ):
            gate_notes = 'panel_failed'
            status = 'draft'

        # Build deliberation metadata
        deliberation_meta = {
            'session_id': session_id,
            'decision': decision,
            'claims_count': len(claims_pack.claims) if claims_pack else 0,
            'sources_count': len(claims_pack.sources) if claims_pack else 0,
            'reviewers': [r.get('reviewer', 'unknown') for r in review_results],
            'review_verdicts': [r.get('verdict', 'FAIL') for r in review_results],
            'gate_result': None,  # Updated later by PublishGate
        }

        title = generated_content.get('title', topic[:255])
        sections = generated_content.get('sections', [])
        intro = generated_content.get('intro', '')
        conclusion = generated_content.get('conclusion', '')
        meta_description = generated_content.get('meta_description', '')
        tags = generated_content.get('keywords', [])
        if topic and topic not in tags:
            tags.append(topic)
        tags = self._sanitize_tags(tags)

        blog = SelfBlog.objects.create(
            title=title[:255],
            author='ContentDeliberation',
            category='blog',
            content_type=content_type,
            status=status,
            gate_notes=gate_notes,
            meta_description=meta_description[:500] if meta_description else '',
            intro=intro,
            sections=sections,
            conclusion=conclusion,
            tags=tags,
            full_text=draft_text,
            tone=voice or 'professional',
            stats_snapshot={'deliberation': deliberation_meta},
        )

        logger.info(
            f"[Phase 4] SelfBlog created: id={blog.id}, status={status}, "
            f"decision={decision}, title={title[:50]}"
        )
        return blog

    @staticmethod
    def _sanitize_tags(tags, max_tags=8):
        """Strip prompt-leaked, oversized, or empty tags."""
        blacklist = ['##', 'REVIEW', 'Write an article', 'Write a blog',
                     'Real-Time Research', 'research data', 'BLOG POST',
                     'stage ', '[stage', 'spider data', '\n']
        clean = []
        for tag in tags:
            if not isinstance(tag, str) or not tag.strip():
                continue
            tag = tag.strip()
            if len(tag) > 50:
                continue
            tag_lower = tag.lower()
            if any(frag.lower() in tag_lower for frag in blacklist):
                continue
            clean.append(tag)
        return clean[:max_tags]

    def _run_publish_gate(self, blog):
        """Run PublishGate and return GateResult."""
        from core.services.publish_gate import PublishGate

        gate = PublishGate()
        return gate.apply_to_blog(blog)


def get_content_deliberation_runner() -> ContentDeliberationRunner:
    """Factory function."""
    return ContentDeliberationRunner()
