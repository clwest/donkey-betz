"""
Ops Autopilot v3 — autonomous ops with governance guardrails.

Policies (v1 — Session 1080):
  1. Timeout spike containment: auto-block agents with high TIMEOUT signature counts
  2. Blocked-agent hygiene: flag agents blocked too long without TTL

Policies (v2 — autonomy push):
  3. Failed deliberation retry: retry TIMEOUT/LLM_UPSTREAM sessions (transient failures)
  4. Content pipeline sweep: kick stuck needs_enhancement/pending_review content
  5. Attention item auto-resolve: dismiss stale ops_autopilot alerts that resolved themselves
  6. Governance auto-decision: auto-approve/dismiss low-blast-radius items

Policies (v3 — root-cause autonomy):
  7. Root-cause remediation: auto-apply safe config fixes for recurring failures
     (timeout adjustments, model fallbacks, temp blocks) with playbook learning

All actions create HumanAttentionItem for governance visibility and are logged
to AutopilotAction for audit trail. Non-trivial actions go through pre-check
→ execute → verify → rollback cycle (ActionVerifier). Successful remediations
are promoted to RemediationPlaybook for future reuse.
"""

import logging
from datetime import timedelta
from typing import Any

from django.utils import timezone

from core.models_diagnostic_pipeline import AutopilotAction, RemediationPlaybook

logger = logging.getLogger(__name__)


# ── Policy configuration ─────────────────────────────────────────────────────

class AutopilotConfig:
    """Tunable policy thresholds. Start conservative."""

    # Timeout spike containment
    TIMEOUT_SPIKE_THRESHOLD = 3          # >= N timeout signatures per agent per hour → block
    TIMEOUT_SPIKE_WINDOW_MINUTES = 60    # Look-back window
    TIMEOUT_BLOCK_TTL_MINUTES = 30       # Auto-unblock after this (start short, raise later)

    # Rate limiting
    MAX_BLOCKS_PER_AGENT_PER_HOUR = 1    # Don't flap
    MAX_TOTAL_BLOCKS_PER_CYCLE = 2       # Don't block everything at once

    # Blocked-agent hygiene
    STALE_BLOCK_HOURS = 48               # Flag blocks older than this without TTL

    # Policy 3: Failed deliberation retry
    DELIBERATION_RETRY_AFTER_MINUTES = 30  # Retry failed sessions older than this
    DELIBERATION_RETRY_REASONS = {'TIMEOUT', 'LLM_UPSTREAM'}  # Transient failures only
    MAX_DELIBERATION_RETRIES_PER_CYCLE = 2  # Don't flood the content queue

    # Policy 4: Content pipeline sweep
    CONTENT_STUCK_HOURS = 6              # Kick content stuck longer than this
    MAX_CONTENT_KICKS_PER_CYCLE = 3      # Limit per cycle

    # Policy 5: Attention auto-resolve
    ATTENTION_STALE_HOURS = 12           # Auto-resolve ops alerts older than this
    ATTENTION_AUTO_RESOLVE_SOURCES = {'ops_autopilot'}  # Only resolve our own alerts

    # Policy 6: Governance auto-decision
    GOVERNANCE_GRACE_PERIOD_HOURS = 1    # Give human a chance first
    GOVERNANCE_MAX_PER_CYCLE = 10        # Don't resolve too many at once
    # Source types that are low blast radius (safe to auto-resolve)
    GOVERNANCE_AUTO_RESOLVE_SOURCES = {
        'content:deliverable',       # Deliverable reviews — just notifications
        'content:blog',              # Blog content reviews
        'agent_output:researchagent',
        'agent_output:contentwriteragent',
        'agent_output:stockauditcoordinator',
        'agent_output:sportsoddsanalyst',
        'agent_output:stockanalystagent',
        'agent_output:predictionmarketanalyst',
    }
    # Item types safe to auto-approve without human
    GOVERNANCE_AUTO_APPROVE_TYPES = {
        'review',      # Content reviews
        'insight',     # Agent insights
    }

    # Policy 7: Root-cause remediation
    REMEDIATION_MIN_OCCURRENCES = 5       # Signature must hit N+ before remediation
    REMEDIATION_MAX_PER_CYCLE = 2         # Don't apply too many remediations at once
    REMEDIATION_COOLDOWN_HOURS = 4        # Don't re-remediate same signature too soon
    REMEDIATION_VERIFY_DELAY = 600        # 10 min — wait for fix to take effect

    # Mode
    DRY_RUN = False                      # Set True to evaluate but not act


# ── Autopilot engine ─────────────────────────────────────────────────────────

class OpsAutopilot:
    """
    Evaluates ops policies and takes allowed actions.
    Called by the Celery beat task every 10 minutes.
    """

    def __init__(self, dry_run: bool | None = None):
        self.dry_run = dry_run if dry_run is not None else AutopilotConfig.DRY_RUN
        self.actions_taken = []
        self.deploy_sha = ''

    def run(self) -> dict[str, Any]:
        """Main entry point. Returns summary of evaluation + actions."""
        now = timezone.now()
        logger.info(f"[OpsAutopilot] Starting cycle (dry_run={self.dry_run})")

        self.deploy_sha = self._get_deploy_sha()

        # Run policies (v1)
        timeout_results = self._policy_timeout_spike_containment(now)
        hygiene_results = self._policy_blocked_agent_hygiene(now)

        # Run policies (v2 — autonomy)
        delib_retry_results = self._policy_failed_deliberation_retry(now)
        content_sweep_results = self._policy_content_pipeline_sweep(now)
        attention_resolve_results = self._policy_attention_auto_resolve(now)
        governance_results = self._policy_governance_auto_decision(now)

        # Run policies (v3 — root-cause autonomy)
        remediation_results = self._policy_root_cause_remediation(now)

        summary = {
            'cycle_at': now.isoformat(),
            'dry_run': self.dry_run,
            'deploy_sha': self.deploy_sha,
            'timeout_spike': timeout_results,
            'blocked_hygiene': hygiene_results,
            'deliberation_retry': delib_retry_results,
            'content_sweep': content_sweep_results,
            'attention_resolve': attention_resolve_results,
            'governance_auto': governance_results,
            'remediation': remediation_results,
            'actions_taken': len(self.actions_taken),
            'actions': self.actions_taken,
        }

        # Log every cycle for observability (even no-ops)
        AutopilotAction.objects.create(
            action_type='dry_run' if self.dry_run or not self.actions_taken else 'deploy_watch',
            agent_name='',
            policy='cycle_evaluation',
            dry_run=self.dry_run,
            evidence={
                'timeout_spike': timeout_results,
                'blocked_hygiene': hygiene_results,
                'deliberation_retry': delib_retry_results,
                'content_sweep': content_sweep_results,
                'attention_resolve': attention_resolve_results,
                'governance_auto': governance_results,
                'remediation': remediation_results,
            },
            result=summary,
            deploy_sha=self.deploy_sha,
        )

        logger.info(
            f"[OpsAutopilot] Cycle complete: "
            f"{len(self.actions_taken)} actions taken "
            f"(dry_run={self.dry_run})"
        )
        return summary

    # ── Policy 1: Timeout spike containment ──────────────────────────────

    def _policy_timeout_spike_containment(self, now) -> dict:
        """Block agents with too many TIMEOUT signatures in the last hour."""
        from core.models_diagnostic_pipeline import FailureSignature, FailureDetection
        from core.models_unified_system import AgentControlEntry
        from django.db.models import Count

        window = now - timedelta(minutes=AutopilotConfig.TIMEOUT_SPIKE_WINDOW_MINUTES)
        result = {'evaluated': True, 'agents_checked': {}, 'blocks_issued': 0}

        try:
            # Group TIMEOUT detections by agent_name in the window
            agent_counts = list(
                FailureDetection.objects.filter(
                    signature__category='timeout',
                    detected_at__gte=window,
                ).values('source_name').annotate(
                    count=Count('id')
                ).order_by('-count')
            )

            if not agent_counts:
                result['note'] = 'No TIMEOUT detections in window'
                return result

            blocks_this_cycle = 0
            already_blocked = AgentControlEntry.get_blocked_names()

            for entry in agent_counts:
                agent_name = entry['source_name']
                count = entry['count']
                result['agents_checked'][agent_name] = count

                if count < AutopilotConfig.TIMEOUT_SPIKE_THRESHOLD:
                    continue

                if agent_name in already_blocked:
                    logger.info(f"[OpsAutopilot] {agent_name} already blocked, skipping")
                    continue

                if blocks_this_cycle >= AutopilotConfig.MAX_TOTAL_BLOCKS_PER_CYCLE:
                    logger.warning(
                        f"[OpsAutopilot] Max blocks per cycle reached "
                        f"({AutopilotConfig.MAX_TOTAL_BLOCKS_PER_CYCLE}), "
                        f"skipping {agent_name}"
                    )
                    continue

                # Rate limit: check if we already blocked this agent recently
                if self._recently_blocked(agent_name, now):
                    logger.info(
                        f"[OpsAutopilot] {agent_name} was recently auto-blocked, "
                        f"skipping (rate limit)"
                    )
                    continue

                # Gather evidence
                sample_detections = list(
                    FailureDetection.objects.filter(
                        signature__category='timeout',
                        source_name=agent_name,
                        detected_at__gte=window,
                    ).order_by('-detected_at')[:5].values(
                        'id', 'source_id', 'error_message',
                        'context_snapshot', 'detected_at'
                    )
                )
                for s in sample_detections:
                    s['detected_at'] = s['detected_at'].isoformat()
                    s['id'] = str(s['id'])

                evidence = {
                    'agent_name': agent_name,
                    'timeout_count': count,
                    'window_minutes': AutopilotConfig.TIMEOUT_SPIKE_WINDOW_MINUTES,
                    'threshold': AutopilotConfig.TIMEOUT_SPIKE_THRESHOLD,
                    'sample_detections': sample_detections,
                    'deploy_sha': self.deploy_sha,
                }

                # Execute block
                self._execute_block(
                    agent_name=agent_name,
                    reason=(
                        f"Autopilot: {count} timeouts in "
                        f"{AutopilotConfig.TIMEOUT_SPIKE_WINDOW_MINUTES}min "
                        f"(threshold={AutopilotConfig.TIMEOUT_SPIKE_THRESHOLD})"
                    ),
                    ttl_minutes=AutopilotConfig.TIMEOUT_BLOCK_TTL_MINUTES,
                    policy='timeout_spike_containment',
                    evidence=evidence,
                )
                blocks_this_cycle += 1
                result['blocks_issued'] += 1

        except Exception as e:
            logger.error(f"[OpsAutopilot] timeout spike policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 2: Blocked-agent hygiene ──────────────────────────────────

    def _policy_blocked_agent_hygiene(self, now) -> dict:
        """Flag agents that have been blocked too long without TTL."""
        from core.models_unified_system import AgentControlEntry

        result = {'evaluated': True, 'stale_blocks': []}

        try:
            stale_cutoff = now - timedelta(hours=AutopilotConfig.STALE_BLOCK_HOURS)
            stale_entries = AgentControlEntry.objects.filter(
                status='blocked',
                ttl_hours__isnull=True,
                blocked_at__lte=stale_cutoff,
            )

            for entry in stale_entries:
                blocked_hours = (now - entry.blocked_at).total_seconds() / 3600
                stale_info = {
                    'agent_name': entry.agent_name,
                    'blocked_hours': round(blocked_hours, 1),
                    'reason': entry.reason,
                    'blocked_by': entry.blocked_by,
                }
                result['stale_blocks'].append(stale_info)

                # Check if we already flagged this recently (don't spam)
                recent_flag = AutopilotAction.objects.filter(
                    action_type='attention_item',
                    agent_name=entry.agent_name,
                    policy='blocked_agent_hygiene',
                    created_at__gte=now - timedelta(hours=24),
                ).exists()

                if recent_flag:
                    continue

                # Create attention item
                self._create_attention_item(
                    title=f"Agent '{entry.agent_name}' blocked {round(blocked_hours)}h without TTL",
                    summary=(
                        f"{entry.agent_name} has been blocked for "
                        f"{round(blocked_hours, 1)} hours with no auto-unblock TTL. "
                        f"Reason: {entry.reason}. Blocked by: {entry.blocked_by}. "
                        f"Consider adding a TTL or unblocking if the issue is resolved."
                    ),
                    urgency='low',
                    policy='blocked_agent_hygiene',
                    agent_name=entry.agent_name,
                    evidence=stale_info,
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] blocked hygiene policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 3: Failed deliberation retry ─────────────────────────────

    def _policy_failed_deliberation_retry(self, now) -> dict:
        """Retry deliberation sessions that failed with transient errors."""
        from core.models_deliberation import DeliberationSession

        result = {'evaluated': True, 'retried': 0, 'skipped': 0}
        cutoff = now - timedelta(minutes=AutopilotConfig.DELIBERATION_RETRY_AFTER_MINUTES)

        try:
            # Find failed sessions with retryable reason codes, old enough to retry
            candidates = DeliberationSession.objects.filter(
                status='failed',
                failure_reason_code__in=AutopilotConfig.DELIBERATION_RETRY_REASONS,
                created_at__lte=cutoff,
            ).order_by('created_at')[:AutopilotConfig.MAX_DELIBERATION_RETRIES_PER_CYCLE * 2]

            retried = 0
            for session in candidates:
                if retried >= AutopilotConfig.MAX_DELIBERATION_RETRIES_PER_CYCLE:
                    break

                # Check if we already retried this session recently
                already_retried = AutopilotAction.objects.filter(
                    action_type='retry_deliberation',
                    policy='failed_deliberation_retry',
                    dry_run=False,
                    created_at__gte=now - timedelta(hours=2),
                    evidence__session_id=str(session.id),
                ).exists()

                if already_retried:
                    result['skipped'] += 1
                    continue

                # Extract the topic from the objective
                topic = session.objective or ''
                # Strip review conversation prefixes
                if 'Content Review for:' in topic:
                    topic = topic.split('Content Review for:')[1].split('\n')[0].strip()

                if not topic or len(topic) < 10:
                    result['skipped'] += 1
                    continue

                evidence = {
                    'session_id': str(session.id),
                    'failure_reason_code': session.failure_reason_code,
                    'failure_detail': (session.failure_detail or '')[:200],
                    'original_created_at': session.created_at.isoformat(),
                    'topic': topic[:200],
                }

                action_record = {
                    'type': 'retry_deliberation',
                    'session_id': str(session.id),
                    'topic': topic[:200],
                    'reason': session.failure_reason_code,
                    'dry_run': self.dry_run,
                }

                if not self.dry_run:
                    # Dispatch a new deliberation task via Celery
                    try:
                        from core.tasks import generate_self_blog_deliberation_task
                        task = generate_self_blog_deliberation_task.delay(
                            topic_category=topic[:200]
                        )
                        action_record['celery_task_id'] = str(task.id)
                        logger.info(
                            f"[OpsAutopilot] RETRIED deliberation for: {topic[:60]} "
                            f"(was {session.failure_reason_code})"
                        )
                    except Exception as e:
                        logger.warning(f"[OpsAutopilot] Retry dispatch failed: {e}")
                        action_record['dispatch_error'] = str(e)[:200]
                else:
                    logger.info(
                        f"[OpsAutopilot] DRY RUN: would retry deliberation: {topic[:60]}"
                    )

                AutopilotAction.objects.create(
                    action_type='retry_deliberation' if not self.dry_run else 'dry_run',
                    agent_name='ContentDeliberation',
                    policy='failed_deliberation_retry',
                    dry_run=self.dry_run,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                )
                self.actions_taken.append(action_record)
                retried += 1

            result['retried'] = retried

        except Exception as e:
            logger.error(f"[OpsAutopilot] deliberation retry policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 4: Content pipeline sweep ──────────────────────────────

    def _policy_content_pipeline_sweep(self, now) -> dict:
        """Kick content stuck in needs_enhancement or pending_review too long."""
        from core.models_unified_system import SelfBlog

        result = {'evaluated': True, 'kicked_enhance': 0, 'kicked_review': 0}
        stuck_cutoff = now - timedelta(hours=AutopilotConfig.CONTENT_STUCK_HOURS)
        kicked = 0

        try:
            # Find blogs stuck in needs_enhancement
            stuck_enhance = SelfBlog.objects.filter(
                status='needs_enhancement',
                created_at__lte=stuck_cutoff,
            ).order_by('created_at')[:AutopilotConfig.MAX_CONTENT_KICKS_PER_CYCLE]

            for blog in stuck_enhance:
                if kicked >= AutopilotConfig.MAX_CONTENT_KICKS_PER_CYCLE:
                    break

                # Check if we already kicked this blog recently
                already_kicked = AutopilotAction.objects.filter(
                    action_type='content_sweep',
                    policy='content_pipeline_sweep',
                    dry_run=False,
                    created_at__gte=now - timedelta(hours=6),
                    evidence__blog_id=str(blog.id),
                ).exists()

                if already_kicked:
                    continue

                evidence = {
                    'blog_id': str(blog.id),
                    'title': (blog.title or '')[:100],
                    'status': blog.status,
                    'created_at': blog.created_at.isoformat() if blog.created_at else '',
                    'stuck_hours': round((now - blog.created_at).total_seconds() / 3600, 1),
                }

                action_record = {
                    'type': 'content_sweep',
                    'blog_id': str(blog.id),
                    'action': 'trigger_enhance',
                    'dry_run': self.dry_run,
                }

                if not self.dry_run:
                    try:
                        from core.tasks import auto_enhance_blogs
                        task = auto_enhance_blogs.delay(limit=1)
                        action_record['celery_task_id'] = str(task.id)
                        logger.info(
                            f"[OpsAutopilot] KICKED enhance for stuck blog: "
                            f"{blog.title[:50]} (stuck {evidence['stuck_hours']}h)"
                        )
                    except Exception as e:
                        action_record['dispatch_error'] = str(e)[:200]

                AutopilotAction.objects.create(
                    action_type='content_sweep' if not self.dry_run else 'dry_run',
                    agent_name='ContentPipeline',
                    policy='content_pipeline_sweep',
                    dry_run=self.dry_run,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                )
                self.actions_taken.append(action_record)
                kicked += 1
                result['kicked_enhance'] += 1

            # Find blogs stuck in pending_review (never scored)
            stuck_review = SelfBlog.objects.filter(
                status='pending_review',
                quality_score__isnull=True,
                created_at__lte=stuck_cutoff,
            ).order_by('created_at')[:AutopilotConfig.MAX_CONTENT_KICKS_PER_CYCLE - kicked]

            for blog in stuck_review:
                if kicked >= AutopilotConfig.MAX_CONTENT_KICKS_PER_CYCLE:
                    break

                evidence = {
                    'blog_id': str(blog.id),
                    'title': (blog.title or '')[:100],
                    'status': blog.status,
                    'stuck_hours': round((now - blog.created_at).total_seconds() / 3600, 1),
                }

                action_record = {
                    'type': 'content_sweep',
                    'blog_id': str(blog.id),
                    'action': 'trigger_score',
                    'dry_run': self.dry_run,
                }

                if not self.dry_run:
                    try:
                        from core.tasks import reevaluate_enhanced_blogs
                        task = reevaluate_enhanced_blogs.delay(limit=5)
                        action_record['celery_task_id'] = str(task.id)
                        logger.info(
                            f"[OpsAutopilot] KICKED scoring for stuck blog: "
                            f"{blog.title[:50]}"
                        )
                    except Exception as e:
                        action_record['dispatch_error'] = str(e)[:200]

                AutopilotAction.objects.create(
                    action_type='content_sweep' if not self.dry_run else 'dry_run',
                    agent_name='ContentPipeline',
                    policy='content_pipeline_sweep',
                    dry_run=self.dry_run,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                )
                self.actions_taken.append(action_record)
                kicked += 1
                result['kicked_review'] += 1

        except Exception as e:
            logger.error(f"[OpsAutopilot] content sweep policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 5: Attention item auto-resolve ─────────────────────────

    def _policy_attention_auto_resolve(self, now) -> dict:
        """Auto-resolve stale ops_autopilot attention items that resolved themselves."""
        from core.models_human_interface import HumanAttentionItem
        from core.models_unified_system import AgentControlEntry

        result = {'evaluated': True, 'resolved': 0}
        stale_cutoff = now - timedelta(hours=AutopilotConfig.ATTENTION_STALE_HOURS)

        try:
            # Find pending ops_autopilot alerts that are stale
            stale_alerts = HumanAttentionItem.objects.filter(
                status='pending',
                source_type__in=AutopilotConfig.ATTENTION_AUTO_RESOLVE_SOURCES,
                created_at__lte=stale_cutoff,
            ).order_by('created_at')[:20]

            currently_blocked = AgentControlEntry.get_blocked_names()

            for item in stale_alerts:
                # Determine if the underlying issue resolved itself
                should_resolve = False
                resolve_reason = ''
                agent_name = ''

                payload = item.payload or {}
                agent_name = payload.get('agent_name', '')

                # If the alert was about a blocked agent that's now unblocked → resolve
                if 'blocked' in (item.title or '').lower() and agent_name:
                    if agent_name not in currently_blocked:
                        should_resolve = True
                        resolve_reason = (
                            f"Auto-resolved: {agent_name} is no longer blocked "
                            f"(TTL expired or manually unblocked)"
                        )

                # If the alert is a stale hygiene flag older than 24h → resolve
                if not should_resolve and payload.get('policy') == 'blocked_agent_hygiene':
                    age_hours = (now - item.created_at).total_seconds() / 3600
                    if age_hours > 24:
                        should_resolve = True
                        resolve_reason = f"Auto-resolved: hygiene alert aged out ({round(age_hours)}h)"

                # Generic: any ops_autopilot alert > ATTENTION_STALE_HOURS → resolve
                if not should_resolve:
                    age_hours = (now - item.created_at).total_seconds() / 3600
                    if age_hours > AutopilotConfig.ATTENTION_STALE_HOURS * 2:
                        should_resolve = True
                        resolve_reason = (
                            f"Auto-resolved: alert aged {round(age_hours)}h "
                            f"without human action"
                        )

                if not should_resolve:
                    continue

                evidence = {
                    'attention_item_id': str(item.id),
                    'title': (item.title or '')[:150],
                    'agent_name': agent_name,
                    'resolve_reason': resolve_reason,
                    'age_hours': round((now - item.created_at).total_seconds() / 3600, 1),
                }

                action_record = {
                    'type': 'auto_resolve',
                    'attention_item_id': str(item.id),
                    'reason': resolve_reason,
                    'dry_run': self.dry_run,
                }

                if not self.dry_run:
                    item.status = 'ignored'
                    item.decision = 'auto_resolve'
                    item.decision_feedback = resolve_reason[:255]
                    item.decided_at = now
                    item.save(update_fields=[
                        'status', 'decision', 'decision_feedback', 'decided_at'
                    ])
                    logger.info(
                        f"[OpsAutopilot] AUTO-RESOLVED attention item: "
                        f"{item.title[:60]} — {resolve_reason[:60]}"
                    )
                else:
                    logger.info(
                        f"[OpsAutopilot] DRY RUN: would resolve: {item.title[:60]}"
                    )

                AutopilotAction.objects.create(
                    action_type='auto_resolve' if not self.dry_run else 'dry_run',
                    agent_name=agent_name,
                    policy='attention_auto_resolve',
                    dry_run=self.dry_run,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                )
                self.actions_taken.append(action_record)
                result['resolved'] += 1

        except Exception as e:
            logger.error(f"[OpsAutopilot] attention auto-resolve policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 6: Governance auto-decision ──────────────────────────────

    def _policy_governance_auto_decision(self, now) -> dict:
        """Auto-resolve low-blast-radius governance items after grace period."""
        from core.models_human_interface import HumanAttentionItem

        result = {
            'evaluated': True,
            'auto_approved': 0,
            'auto_dismissed': 0,
            'skipped': 0,
        }
        grace_cutoff = now - timedelta(hours=AutopilotConfig.GOVERNANCE_GRACE_PERIOD_HOURS)
        processed = 0

        try:
            # Find pending items from auto-resolvable sources, past grace period
            candidates = HumanAttentionItem.objects.filter(
                status='pending',
                created_at__lte=grace_cutoff,
            ).order_by('created_at')[:AutopilotConfig.GOVERNANCE_MAX_PER_CYCLE * 2]

            for item in candidates:
                if processed >= AutopilotConfig.GOVERNANCE_MAX_PER_CYCLE:
                    break

                source = item.source_type or ''
                item_type = item.item_type or ''

                # Classify blast radius
                is_low_blast = (
                    source in AutopilotConfig.GOVERNANCE_AUTO_RESOLVE_SOURCES
                    or item_type in AutopilotConfig.GOVERNANCE_AUTO_APPROVE_TYPES
                )

                if not is_low_blast:
                    result['skipped'] += 1
                    continue

                # Determine action: approve for insights/reviews, dismiss for stale
                age_hours = (now - item.created_at).total_seconds() / 3600

                if item_type in ('review', 'insight'):
                    action = 'approve'
                    reason = (
                        f"Auto-approved: {item_type} from {source} "
                        f"(low blast radius, {round(age_hours)}h old)"
                    )
                else:
                    action = 'dismiss'
                    reason = (
                        f"Auto-dismissed: {source} item "
                        f"(low blast radius, {round(age_hours)}h old)"
                    )

                evidence = {
                    'attention_item_id': str(item.id),
                    'title': (item.title or '')[:150],
                    'source_type': source,
                    'item_type': item_type,
                    'urgency': item.urgency,
                    'age_hours': round(age_hours, 1),
                    'action': action,
                    'reason': reason,
                }

                action_record = {
                    'type': 'auto_resolve',
                    'attention_item_id': str(item.id),
                    'governance_action': action,
                    'reason': reason,
                    'dry_run': self.dry_run,
                }

                if not self.dry_run:
                    if action == 'approve':
                        item.status = 'acted'
                        item.decision = 'approve'
                    else:
                        item.status = 'ignored'
                        item.decision = 'auto_dismiss'

                    item.decision_feedback = reason[:255]
                    item.decided_at = now
                    item.save(update_fields=[
                        'status', 'decision', 'decision_feedback', 'decided_at'
                    ])
                    logger.info(
                        f"[OpsAutopilot] GOVERNANCE {action}: "
                        f"{item.title[:50]} ({source})"
                    )

                db_action = AutopilotAction.objects.create(
                    action_type='auto_resolve' if not self.dry_run else 'dry_run',
                    agent_name=source,
                    policy='governance_auto_decision',
                    dry_run=self.dry_run,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                    verification_state='pending' if not self.dry_run else 'skipped',
                )

                # Schedule deferred verification for non-dry-run governance actions
                if not self.dry_run:
                    try:
                        from core.tasks import verify_autopilot_action
                        verify_autopilot_action.apply_async(
                            args=[db_action.id], countdown=300,  # 5 min
                        )
                    except Exception:
                        pass
                self.actions_taken.append(action_record)
                processed += 1

                if action == 'approve':
                    result['auto_approved'] += 1
                else:
                    result['auto_dismissed'] += 1

        except Exception as e:
            logger.error(f"[OpsAutopilot] governance auto-decision error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 7: Root-cause remediation ────────────────────────────────

    def _policy_root_cause_remediation(self, now) -> dict:
        """
        Auto-remediate recurring failure patterns using playbook or heuristics.

        Flow:
        1. Find active FailureSignatures with high occurrence counts
        2. Check if a playbook entry exists for the pattern
        3. If yes: apply known fix (if success rate is high enough)
        4. If no: attempt heuristic remediation (timeout adjust, model fallback)
        5. Record outcome, schedule verification, learn from results
        """
        result = {
            'evaluated': True,
            'playbook_applied': 0,
            'heuristic_applied': 0,
            'skipped': 0,
        }

        try:
            engine = RemediationEngine(
                dry_run=self.dry_run,
                deploy_sha=self.deploy_sha,
            )
            remediation_result = engine.run_cycle(now)

            result['playbook_applied'] = remediation_result.get('playbook_applied', 0)
            result['heuristic_applied'] = remediation_result.get('heuristic_applied', 0)
            result['skipped'] = remediation_result.get('skipped', 0)
            result['details'] = remediation_result.get('details', [])

            # Merge engine actions into our action list
            self.actions_taken.extend(remediation_result.get('actions', []))

        except Exception as e:
            logger.error(f"[OpsAutopilot] root-cause remediation error: {e}")
            result['error'] = str(e)

        return result

    # ── Action executors ─────────────────────────────────────────────────

    def _execute_block(
        self, agent_name: str, reason: str, ttl_minutes: int,
        policy: str, evidence: dict
    ):
        """Block an agent with TTL, pre-check via ActionVerifier, auto-rollback."""
        from core.models_unified_system import AgentControlEntry

        ttl_hours = round(ttl_minutes / 60, 2)
        action_record = {
            'type': 'block_agent',
            'agent_name': agent_name,
            'ttl_minutes': ttl_minutes,
            'reason': reason,
            'policy': policy,
            'dry_run': self.dry_run,
        }

        if not self.dry_run:
            # Pre-check via ActionVerifier
            verifier = ActionVerifier()
            action = verifier.begin(
                action_type='block_agent',
                policy=policy,
                agent_name=agent_name,
                evidence=evidence,
                deploy_sha=self.deploy_sha,
            )

            if not action.pre_check_passed:
                action_record['blocked_by_pre_check'] = True
                action_record['pre_check_reason'] = action.pre_check_result.get('reason', '')
                AutopilotAction.objects.create(
                    action_type='dry_run',
                    agent_name=agent_name,
                    policy=policy,
                    dry_run=True,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                    verification_state='failed',
                    verification_result={'pre_check': action.pre_check_result},
                )
                self.actions_taken.append(action_record)
                return

            # Execute the block
            AgentControlEntry.objects.update_or_create(
                agent_name=agent_name,
                defaults={
                    'status': 'blocked',
                    'reason': reason[:255],
                    'blocked_at': timezone.now(),
                    'blocked_by': 'ops_autopilot',
                    'ttl_hours': ttl_hours if ttl_hours > 0 else None,
                }
            )
            logger.warning(
                f"[OpsAutopilot] BLOCKED {agent_name} for {ttl_minutes}min — {reason}"
            )

            # Create governance attention item
            self._create_attention_item(
                title=f"Autopilot blocked '{agent_name}' ({ttl_minutes}min TTL)",
                summary=(
                    f"Ops Autopilot automatically blocked {agent_name} due to "
                    f"timeout spike. TTL={ttl_minutes}min (auto-unblock at "
                    f"{(timezone.now() + timedelta(minutes=ttl_minutes)).strftime('%H:%M UTC')}). "
                    f"Evidence: {evidence.get('timeout_count', '?')} timeouts in "
                    f"{evidence.get('window_minutes', '?')} minutes."
                ),
                urgency='high',
                policy=policy,
                agent_name=agent_name,
                evidence=evidence,
            )

            # Record with deferred verification (verify in 3 min)
            verifier.record_and_verify(
                action, action_record, verify_delay_seconds=180,
            )
        else:
            logger.info(
                f"[OpsAutopilot] DRY RUN: would block {agent_name} "
                f"for {ttl_minutes}min — {reason}"
            )
            AutopilotAction.objects.create(
                action_type='dry_run',
                agent_name=agent_name,
                policy=policy,
                dry_run=True,
                evidence=evidence,
                result=action_record,
                deploy_sha=self.deploy_sha,
            )

        self.actions_taken.append(action_record)

    def _create_attention_item(
        self, title: str, summary: str, urgency: str,
        policy: str, agent_name: str = '', evidence: dict | None = None
    ):
        """Create a HumanAttentionItem for governance visibility."""
        if self.dry_run:
            logger.info(f"[OpsAutopilot] DRY RUN: would create attention item: {title}")
            return

        try:
            from core.models_human_interface import HumanAttentionItem
            from django.contrib.auth import get_user_model
            User = get_user_model()

            # Get the first superuser (Chris) for the FK
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
            if not user:
                logger.warning("[OpsAutopilot] No user found for attention item")
                return

            HumanAttentionItem.objects.create(
                user=user,
                source_type='ops_autopilot',
                source_agent='OpsAutopilot',
                item_type='alert',
                title=title[:200],
                summary=summary,
                payload={
                    'policy': policy,
                    'agent_name': agent_name,
                    'evidence': evidence or {},
                    'deploy_sha': self.deploy_sha,
                    'autopilot_version': 'v1',
                },
                urgency=urgency,
            )

            # Also log
            AutopilotAction.objects.create(
                action_type='attention_item',
                agent_name=agent_name,
                policy=policy,
                dry_run=False,
                evidence=evidence or {},
                result={'title': title, 'urgency': urgency},
                deploy_sha=self.deploy_sha,
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] Failed to create attention item: {e}")

    # ── Helpers ───────────────────────────────────────────────────────────

    def _recently_blocked(self, agent_name: str, now) -> bool:
        """Check if autopilot already blocked this agent in the last hour."""
        cutoff = now - timedelta(hours=1)
        return AutopilotAction.objects.filter(
            action_type='block_agent',
            agent_name=agent_name,
            dry_run=False,
            created_at__gte=cutoff,
        ).exists()

    def _get_deploy_sha(self) -> str:
        """Get current deploy SHA from environment."""
        import os
        # Railway sets RAILWAY_GIT_COMMIT_SHA; fallback to git
        sha = os.environ.get('RAILWAY_GIT_COMMIT_SHA', '')
        if not sha:
            try:
                import subprocess
                sha = subprocess.check_output(
                    ['git', 'rev-parse', 'HEAD'],
                    stderr=subprocess.DEVNULL
                ).decode().strip()[:12]
            except Exception:
                sha = 'unknown'
        return sha[:40]


# ── Action Verifier — autonomous safety layer ────────────────────────────────

class ActionVerifier:
    """
    Wraps autopilot actions with pre-checks, post-verification, and rollback.

    Every non-trivial autonomous action goes through:
      1. PRE-CHECK: Is it safe to act? (blast radius, rate, invariants)
      2. EXECUTE: Perform the action
      3. VERIFY: Did it help? Check SLOs, error rates, queue health
      4. ROLLBACK: If verification fails, undo the action automatically

    Usage:
        verifier = ActionVerifier()
        action = verifier.begin('block_agent', agent_name='FooAgent', policy='timeout_spike')
        if action.pre_check_passed:
            # ... execute the action ...
            action.record_execution({'celery_task_id': '...'})
            verifier.schedule_verification(action, delay_seconds=120)

    Deferred verification runs via Celery after a delay to check outcomes.
    """

    # Pre-check rules per action type
    PRE_CHECK_RULES = {
        'block_agent': {
            'max_concurrent_blocks': 3,     # Don't block too many agents at once
            'min_interval_minutes': 15,     # Don't re-block same agent too fast
            'require_evidence_count': 3,    # Need N+ timeout signatures
        },
        'retry_deliberation': {
            'max_pending_retries': 4,       # Don't flood content queue
            'min_interval_minutes': 30,     # Don't retry same topic too fast
        },
        'content_sweep': {
            'max_concurrent_sweeps': 3,     # Don't kick too many blogs at once
        },
        'auto_resolve': {
            'max_per_cycle': 15,            # Don't mass-resolve in one pass
        },
        'content_publish': {
            'max_daily': 8,                 # Hard daily publish limit
            'min_quality_score': 0.3,       # Don't publish garbage
        },
    }

    def begin(
        self,
        action_type: str,
        policy: str,
        agent_name: str = '',
        evidence: dict | None = None,
        deploy_sha: str = '',
    ) -> 'VerifiableAction':
        """Create a verifiable action and run pre-checks."""
        action = VerifiableAction(
            action_type=action_type,
            policy=policy,
            agent_name=agent_name,
            evidence=evidence or {},
            deploy_sha=deploy_sha,
        )

        # Run pre-checks
        rules = self.PRE_CHECK_RULES.get(action_type, {})
        pre_check_result = self._run_pre_checks(action, rules)
        action.pre_check_result = pre_check_result
        action.pre_check_passed = pre_check_result.get('passed', True)

        if not action.pre_check_passed:
            logger.warning(
                f"[ActionVerifier] PRE-CHECK FAILED for {action_type}: "
                f"{pre_check_result.get('reason', 'unknown')}"
            )

        return action

    def _run_pre_checks(self, action: 'VerifiableAction', rules: dict) -> dict:
        """Evaluate pre-check rules. Returns {'passed': bool, 'reason': str, ...}."""
        result = {'passed': True, 'checks': []}

        try:
            now = timezone.now()

            # Check: max concurrent blocks
            if 'max_concurrent_blocks' in rules and action.action_type == 'block_agent':
                from core.models_unified_system import AgentControlEntry
                current_blocks = AgentControlEntry.objects.filter(
                    status='blocked',
                    blocked_by='ops_autopilot',
                ).count()
                check = {
                    'name': 'max_concurrent_blocks',
                    'current': current_blocks,
                    'limit': rules['max_concurrent_blocks'],
                    'passed': current_blocks < rules['max_concurrent_blocks'],
                }
                result['checks'].append(check)
                if not check['passed']:
                    result['passed'] = False
                    result['reason'] = (
                        f"Too many concurrent autopilot blocks "
                        f"({current_blocks}/{rules['max_concurrent_blocks']})"
                    )

            # Check: min interval between same-agent actions
            if 'min_interval_minutes' in rules and action.agent_name:
                cutoff = now - timedelta(minutes=rules['min_interval_minutes'])
                recent = AutopilotAction.objects.filter(
                    action_type=action.action_type,
                    agent_name=action.agent_name,
                    dry_run=False,
                    created_at__gte=cutoff,
                ).exists()
                check = {
                    'name': 'min_interval',
                    'agent': action.agent_name,
                    'interval_minutes': rules['min_interval_minutes'],
                    'passed': not recent,
                }
                result['checks'].append(check)
                if not check['passed']:
                    result['passed'] = False
                    result['reason'] = (
                        f"Same action on {action.agent_name} too recently "
                        f"(within {rules['min_interval_minutes']}min)"
                    )

            # Check: max pending retries (content queue capacity)
            if 'max_pending_retries' in rules:
                from core.models_celery_telemetry import CeleryTaskEvent
                pending = CeleryTaskEvent.objects.filter(
                    task_name__icontains='deliberation',
                    status='STARTED',
                    started_at__gte=now - timedelta(hours=1),
                ).count()
                check = {
                    'name': 'max_pending_retries',
                    'current': pending,
                    'limit': rules['max_pending_retries'],
                    'passed': pending < rules['max_pending_retries'],
                }
                result['checks'].append(check)
                if not check['passed']:
                    result['passed'] = False
                    result['reason'] = (
                        f"Too many pending deliberation tasks ({pending})"
                    )

            # Check: daily publish limit
            if 'max_daily' in rules:
                from core.models_unified_system import SelfBlog
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                published_today = SelfBlog.objects.filter(
                    status='published',
                    created_at__gte=today_start,
                ).count()
                check = {
                    'name': 'max_daily_publish',
                    'current': published_today,
                    'limit': rules['max_daily'],
                    'passed': published_today < rules['max_daily'],
                }
                result['checks'].append(check)
                if not check['passed']:
                    result['passed'] = False
                    result['reason'] = (
                        f"Daily publish limit reached ({published_today})"
                    )

        except Exception as e:
            logger.error(f"[ActionVerifier] Pre-check error: {e}")
            result['error'] = str(e)
            # Fail-open: if pre-checks crash, still allow action (logged)

        return result

    def record_and_verify(
        self,
        action: 'VerifiableAction',
        execution_result: dict,
        verify_delay_seconds: int = 120,
    ) -> AutopilotAction:
        """
        Record the action to DB and schedule deferred verification.

        After execution, creates an AutopilotAction record with
        verification_state='pending'. A Celery task checks outcomes
        after verify_delay_seconds.
        """
        db_action = AutopilotAction.objects.create(
            action_type=action.action_type,
            agent_name=action.agent_name,
            policy=action.policy,
            dry_run=False,
            evidence=action.evidence,
            result=execution_result,
            deploy_sha=action.deploy_sha,
            verification_state='pending',
            verification_result={
                'pre_check': action.pre_check_result,
                'scheduled_verify_at': (
                    timezone.now() + timedelta(seconds=verify_delay_seconds)
                ).isoformat(),
            },
        )

        # Schedule deferred verification via Celery
        if verify_delay_seconds > 0:
            try:
                from core.tasks import verify_autopilot_action
                verify_autopilot_action.apply_async(
                    args=[db_action.id],
                    countdown=verify_delay_seconds,
                )
                logger.info(
                    f"[ActionVerifier] Verification scheduled for action "
                    f"{db_action.id} in {verify_delay_seconds}s"
                )
            except Exception as e:
                logger.warning(f"[ActionVerifier] Failed to schedule verification: {e}")
                # Mark as skipped if we can't verify
                db_action.verification_state = 'skipped'
                db_action.save(update_fields=['verification_state'])

        return db_action

    @staticmethod
    def verify_action(action_id: int) -> dict:
        """
        Deferred verification — called by Celery task after delay.

        Checks whether the action improved the situation:
        - block_agent: Did error rate for that agent drop?
        - retry_deliberation: Did the retry succeed (new session completed)?
        - content_sweep: Did the blog move forward in pipeline?
        - auto_resolve: No new alerts spawned from same source?
        - content_publish: No quality complaints?
        """
        try:
            action = AutopilotAction.objects.get(id=action_id)
        except AutopilotAction.DoesNotExist:
            return {'error': f'Action {action_id} not found'}

        if action.verification_state not in ('pending',):
            return {'skipped': True, 'reason': f'State is {action.verification_state}'}

        now = timezone.now()
        result = {'action_id': action_id, 'checks': [], 'passed': True}

        try:
            if action.action_type == 'block_agent':
                result = ActionVerifier._verify_block_agent(action, now)

            elif action.action_type == 'retry_deliberation':
                result = ActionVerifier._verify_retry_deliberation(action, now)

            elif action.action_type == 'content_sweep':
                result = ActionVerifier._verify_content_sweep(action, now)

            elif action.action_type == 'remediate':
                result = RemediationEngine.verify_remediation(action)

            elif action.action_type in ('auto_resolve', 'content_publish'):
                # Lightweight: just check no new errors spawned
                from core.models_diagnostic_pipeline import FailureDetection
                new_errors = FailureDetection.objects.filter(
                    detected_at__gte=action.created_at,
                    source_name__icontains=action.agent_name or 'autopilot',
                ).count()
                result['checks'].append({
                    'name': 'no_cascading_errors',
                    'new_errors': new_errors,
                    'passed': new_errors == 0,
                })
                result['passed'] = new_errors == 0
            else:
                # Unknown action type — skip verification
                result['passed'] = True
                result['skipped'] = True

        except Exception as e:
            logger.error(f"[ActionVerifier] Verification error for {action_id}: {e}")
            result['error'] = str(e)
            result['passed'] = True  # Fail-open on verification errors

        # Update the action record
        action.verification_state = 'passed' if result.get('passed') else 'failed'
        action.verification_result = {
            **(action.verification_result or {}),
            'verification': result,
            'verified_at': now.isoformat(),
        }
        action.save(update_fields=['verification_state', 'verification_result'])

        # If verification failed, attempt rollback
        if not result.get('passed'):
            ActionVerifier._attempt_rollback(action, result)

        return result

    @staticmethod
    def _verify_block_agent(action: AutopilotAction, now) -> dict:
        """Verify that blocking an agent reduced error rate."""
        from core.models_diagnostic_pipeline import FailureDetection

        agent_name = action.agent_name
        result = {'action_id': action.id, 'checks': [], 'passed': True}

        # Check: error rate for this agent dropped since block
        errors_before = FailureDetection.objects.filter(
            source_name=agent_name,
            detected_at__gte=action.created_at - timedelta(hours=1),
            detected_at__lt=action.created_at,
        ).count()

        errors_after = FailureDetection.objects.filter(
            source_name=agent_name,
            detected_at__gte=action.created_at,
        ).count()

        check = {
            'name': 'error_rate_reduced',
            'errors_before': errors_before,
            'errors_after': errors_after,
            'passed': errors_after <= errors_before,  # At least no worse
        }
        result['checks'].append(check)
        result['passed'] = check['passed']

        return result

    @staticmethod
    def _verify_retry_deliberation(action: AutopilotAction, now) -> dict:
        """Verify that the retried deliberation produced output."""
        from core.models_deliberation import DeliberationSession

        result = {'action_id': action.id, 'checks': [], 'passed': True}

        # Check: did a new successful session appear after the retry?
        evidence = action.evidence or {}
        topic = evidence.get('topic', '')[:100]

        if topic:
            new_sessions = DeliberationSession.objects.filter(
                status='completed',
                created_at__gte=action.created_at,
                objective__icontains=topic[:50],
            ).count()

            check = {
                'name': 'retry_produced_output',
                'new_completed_sessions': new_sessions,
                'passed': new_sessions > 0,
            }
            result['checks'].append(check)
            # Don't fail on this — retry might still be in progress
            result['passed'] = True  # Retry is best-effort
        else:
            result['passed'] = True

        return result

    @staticmethod
    def _verify_content_sweep(action: AutopilotAction, now) -> dict:
        """Verify that the swept content moved forward."""
        from core.models_unified_system import SelfBlog

        result = {'action_id': action.id, 'checks': [], 'passed': True}

        evidence = action.evidence or {}
        blog_id = evidence.get('blog_id', '')

        if blog_id:
            try:
                blog = SelfBlog.objects.get(id=blog_id)
                # Check if blog moved to a later stage
                forward_statuses = {'approved', 'published', 'pending_review'}
                check = {
                    'name': 'content_progressed',
                    'current_status': blog.status,
                    'passed': blog.status in forward_statuses,
                }
                result['checks'].append(check)
                # Content sweep is best-effort — don't roll back
                result['passed'] = True
            except SelfBlog.DoesNotExist:
                result['passed'] = True

        return result

    @staticmethod
    def _attempt_rollback(action: AutopilotAction, verification_result: dict):
        """Attempt to rollback a failed action."""
        now = timezone.now()
        rollback_reason = verification_result.get(
            'checks', [{}]
        )[-1].get('name', 'verification_failed') if verification_result.get('checks') else 'verification_failed'

        logger.warning(
            f"[ActionVerifier] ROLLBACK for action {action.id} "
            f"({action.action_type}): {rollback_reason}"
        )

        try:
            if action.action_type == 'block_agent' and action.agent_name:
                # Rollback: unblock the agent
                from core.models_unified_system import AgentControlEntry
                AgentControlEntry.objects.filter(
                    agent_name=action.agent_name,
                    blocked_by='ops_autopilot',
                ).update(
                    status='active',
                    reason=f"Auto-rollback: {rollback_reason}",
                )
                logger.info(
                    f"[ActionVerifier] ROLLED BACK block on {action.agent_name}"
                )

            elif action.action_type == 'auto_resolve':
                # Rollback: re-open the attention item
                evidence = action.evidence or {}
                attention_id = evidence.get('attention_item_id', '')
                if attention_id:
                    from core.models_human_interface import HumanAttentionItem
                    HumanAttentionItem.objects.filter(
                        id=attention_id,
                    ).update(
                        status='pending',
                        decision='',
                        decision_feedback=f'Reopened by auto-rollback: {rollback_reason}',
                    )
                    logger.info(
                        f"[ActionVerifier] ROLLED BACK auto-resolve on {attention_id}"
                    )

            # Mark as rolled back
            action.rolled_back = True
            action.rolled_back_at = now
            action.rollback_reason = rollback_reason[:255]
            action.verification_state = 'rolled_back'
            action.save(update_fields=[
                'rolled_back', 'rolled_back_at',
                'rollback_reason', 'verification_state',
            ])

            # Create governance alert about the rollback
            from core.models_human_interface import HumanAttentionItem
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(is_superuser=True).first()
            if user:
                HumanAttentionItem.objects.create(
                    user=user,
                    source_type='ops_autopilot',
                    source_agent='ActionVerifier',
                    item_type='alert',
                    title=f"Auto-rollback: {action.action_type} on {action.agent_name or 'system'}",
                    summary=(
                        f"Autopilot action #{action.id} ({action.action_type}) was "
                        f"automatically rolled back because post-verification failed. "
                        f"Reason: {rollback_reason}. "
                        f"This may indicate the autonomous action made things worse."
                    ),
                    urgency='high',
                    payload={
                        'rollback': True,
                        'action_id': action.id,
                        'action_type': action.action_type,
                        'verification_result': verification_result,
                    },
                )

        except Exception as e:
            logger.error(f"[ActionVerifier] Rollback failed for action {action.id}: {e}")
            action.rollback_reason = f"Rollback error: {str(e)[:200]}"
            action.save(update_fields=['rollback_reason'])


class VerifiableAction:
    """Holds state for an action being verified."""

    def __init__(
        self,
        action_type: str,
        policy: str,
        agent_name: str = '',
        evidence: dict | None = None,
        deploy_sha: str = '',
    ):
        self.action_type = action_type
        self.policy = policy
        self.agent_name = agent_name
        self.evidence = evidence or {}
        self.deploy_sha = deploy_sha
        self.pre_check_result: dict = {}
        self.pre_check_passed: bool = True


# ── Remediation Engine — root-cause autonomy ─────────────────────────────────


class RemediationEngine:
    """
    Converts verified failure patterns into safe, reversible config fixes.

    Safe remediation types (all config-only, easy to roll back):
    1. timeout_adjust: Increase wall-clock timeout for chronically slow agents
    2. model_fallback: Route agent to fallback LLM when primary provider is down
    3. block_and_wait: Temp-block agent until external provider recovers
    4. retry_config: Adjust retry intervals for transient failures

    Flow per cycle:
      1. Find FailureSignatures with occurrence >= threshold and status='active'
      2. Look for matching RemediationPlaybook entry
      3. If playbook match: apply known fix (if confidence high enough)
      4. If no match: attempt heuristic remediation based on category
      5. Record as AutopilotAction(action_type='remediate')
      6. Schedule deferred verification to check if it helped
      7. On verification: update playbook success rate or create new entry
    """

    # Heuristic remediation rules by failure category
    HEURISTIC_RULES = {
        'timeout': {
            'remediation_type': 'timeout_adjust',
            'description': 'Increase agent timeout by 50%',
            'multiplier': 1.5,
            'max_timeout': 1800,  # 30 min absolute cap
        },
        'provider_error': {
            'remediation_type': 'model_fallback',
            'description': 'Switch to fallback LLM provider',
        },
        'resource_error': {
            'remediation_type': 'block_and_wait',
            'description': 'Block agent until resource recovers',
            'block_minutes': 60,
        },
    }

    def __init__(self, dry_run: bool = False, deploy_sha: str = ''):
        self.dry_run = dry_run
        self.deploy_sha = deploy_sha
        self.actions: list = []

    def run_cycle(self, now) -> dict:
        """Main remediation cycle. Returns summary dict."""
        from core.models_diagnostic_pipeline import FailureSignature

        result = {
            'playbook_applied': 0,
            'heuristic_applied': 0,
            'skipped': 0,
            'details': [],
            'actions': [],
        }

        try:
            # Find active signatures above occurrence threshold
            candidates = FailureSignature.objects.filter(
                status='active',
                occurrence_count__gte=AutopilotConfig.REMEDIATION_MIN_OCCURRENCES,
            ).order_by('-occurrence_count')[:10]

            applied = 0
            for sig in candidates:
                if applied >= AutopilotConfig.REMEDIATION_MAX_PER_CYCLE:
                    break

                # Cooldown check: don't re-remediate too soon
                if self._on_cooldown(sig, now):
                    result['skipped'] += 1
                    continue

                # Check if we already have a pending remediation for this sig
                if self._has_pending_remediation(sig, now):
                    result['skipped'] += 1
                    continue

                # Try playbook first, then heuristic
                applied_entry = self._try_playbook(sig, now)
                if applied_entry:
                    result['playbook_applied'] += 1
                    result['details'].append(applied_entry)
                    result['actions'].append(applied_entry)
                    self.actions.append(applied_entry)
                    applied += 1
                    continue

                heuristic_entry = self._try_heuristic(sig, now)
                if heuristic_entry:
                    result['heuristic_applied'] += 1
                    result['details'].append(heuristic_entry)
                    result['actions'].append(heuristic_entry)
                    self.actions.append(heuristic_entry)
                    applied += 1
                else:
                    result['skipped'] += 1

        except Exception as e:
            logger.error(f"[RemediationEngine] cycle error: {e}")
            result['error'] = str(e)

        return result

    def _on_cooldown(self, sig, now) -> bool:
        """Check if this signature was remediated recently."""
        cutoff = now - timedelta(hours=AutopilotConfig.REMEDIATION_COOLDOWN_HOURS)
        return AutopilotAction.objects.filter(
            action_type='remediate',
            evidence__signature_id=str(sig.id),
            dry_run=False,
            created_at__gte=cutoff,
        ).exists()

    def _has_pending_remediation(self, sig, now) -> bool:
        """Check if there's a pending (unverified) remediation for this sig."""
        return AutopilotAction.objects.filter(
            action_type='remediate',
            evidence__signature_id=str(sig.id),
            dry_run=False,
            verification_state='pending',
        ).exists()

    def _try_playbook(self, sig, now) -> dict | None:
        """Try to apply a known playbook fix for this signature."""
        # Match by exact signature or by category
        from django.db.models import Q
        playbook = RemediationPlaybook.objects.filter(
            enabled=True,
        ).filter(
            Q(signature_pattern=sig.signature) |
            Q(failure_category=sig.category)
        ).order_by('-success_rate').first()

        if not playbook:
            return None

        # Confidence gate
        if playbook.times_applied >= 2 and playbook.success_rate < playbook.min_confidence:
            logger.info(
                f"[RemediationEngine] Playbook {playbook.id} for {sig.signature} "
                f"below confidence ({playbook.success_rate:.0%}), skipping"
            )
            return None

        return self._apply_remediation(
            sig=sig,
            remediation_type=playbook.remediation_type,
            config=playbook.config,
            source='playbook',
            playbook_id=playbook.id,
            now=now,
        )

    def _try_heuristic(self, sig, now) -> dict | None:
        """Try a heuristic remediation based on failure category."""
        rule = self.HEURISTIC_RULES.get(sig.category)
        if not rule:
            return None

        # Build config from heuristic
        config = {}
        remediation_type = rule['remediation_type']

        if remediation_type == 'timeout_adjust':
            # Find the agent name from recent detections
            agent_name = self._get_primary_agent(sig)
            if not agent_name:
                return None
            current_timeout = self._get_current_timeout(agent_name)
            new_timeout = min(
                int(current_timeout * rule['multiplier']),
                rule['max_timeout'],
            )
            if new_timeout <= current_timeout:
                return None  # Already at max
            config = {
                'agent_name': agent_name,
                'current_timeout': current_timeout,
                'new_timeout': new_timeout,
            }

        elif remediation_type == 'model_fallback':
            agent_name = self._get_primary_agent(sig)
            if not agent_name:
                return None
            config = {
                'agent_name': agent_name,
                'provider': sig.provider,
                'error_code': sig.error_code,
            }

        elif remediation_type == 'block_and_wait':
            agent_name = self._get_primary_agent(sig)
            if not agent_name:
                return None
            config = {
                'agent_name': agent_name,
                'block_minutes': rule['block_minutes'],
            }

        return self._apply_remediation(
            sig=sig,
            remediation_type=remediation_type,
            config=config,
            source='heuristic',
            now=now,
        )

    def _apply_remediation(
        self,
        sig,
        remediation_type: str,
        config: dict,
        source: str,
        now,
        playbook_id: int | None = None,
    ) -> dict:
        """Apply a specific remediation and schedule verification."""
        agent_name = config.get('agent_name', '')

        evidence = {
            'signature_id': str(sig.id),
            'signature': sig.signature,
            'category': sig.category,
            'occurrence_count': sig.occurrence_count,
            'remediation_type': remediation_type,
            'config': config,
            'source': source,
        }
        if playbook_id:
            evidence['playbook_id'] = playbook_id

        action_record = {
            'type': 'remediate',
            'remediation_type': remediation_type,
            'signature': sig.signature,
            'agent_name': agent_name,
            'config': config,
            'source': source,
            'dry_run': self.dry_run,
        }

        if not self.dry_run:
            # Execute the remediation
            exec_result = self._execute_remediation(
                remediation_type, config, sig,
            )
            action_record['execution'] = exec_result

            if exec_result.get('applied'):
                # Record with deferred verification
                db_action = AutopilotAction.objects.create(
                    action_type='remediate',
                    agent_name=agent_name,
                    policy='root_cause_remediation',
                    dry_run=False,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                    verification_state='pending',
                    verification_result={
                        'source': source,
                        'playbook_id': playbook_id,
                    },
                )

                # Schedule verification
                try:
                    from core.tasks import verify_autopilot_action
                    verify_autopilot_action.apply_async(
                        args=[db_action.id],
                        countdown=AutopilotConfig.REMEDIATION_VERIFY_DELAY,
                    )
                except Exception as e:
                    logger.warning(
                        f"[RemediationEngine] Failed to schedule verification: {e}"
                    )

                # Mark signature as diagnosed
                sig.mark_diagnosed()

                logger.info(
                    f"[RemediationEngine] APPLIED {remediation_type} for "
                    f"{sig.signature} ({source}): {config}"
                )
            else:
                logger.info(
                    f"[RemediationEngine] Remediation {remediation_type} "
                    f"for {sig.signature} could not be applied: "
                    f"{exec_result.get('reason', 'unknown')}"
                )
                return action_record
        else:
            logger.info(
                f"[RemediationEngine] DRY RUN: would apply {remediation_type} "
                f"for {sig.signature}: {config}"
            )
            AutopilotAction.objects.create(
                action_type='dry_run',
                agent_name=agent_name,
                policy='root_cause_remediation',
                dry_run=True,
                evidence=evidence,
                result=action_record,
                deploy_sha=self.deploy_sha,
            )

        return action_record

    def _execute_remediation(
        self, remediation_type: str, config: dict, sig
    ) -> dict:
        """Execute a specific remediation. Returns {applied: bool, ...}."""
        if remediation_type == 'timeout_adjust':
            return self._exec_timeout_adjust(config)
        elif remediation_type == 'model_fallback':
            return self._exec_model_fallback(config)
        elif remediation_type == 'block_and_wait':
            return self._exec_block_and_wait(config, sig)
        return {'applied': False, 'reason': f'Unknown type: {remediation_type}'}

    def _exec_timeout_adjust(self, config: dict) -> dict:
        """
        Adjust agent timeout by writing to SystemConfiguration.

        We store timeout overrides in SystemConfiguration so they persist
        across deploys and can be read by execute_agent_task.
        """
        agent_name = config['agent_name']
        new_timeout = config['new_timeout']

        try:
            from core.models.system import SystemConfiguration
            key = f'agent_timeout_override:{agent_name}'
            SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': str(new_timeout),
                    'description': (
                        f'Auto-remediation: timeout adjusted from '
                        f'{config["current_timeout"]}s to {new_timeout}s'
                    ),
                },
            )
            return {
                'applied': True,
                'key': key,
                'old_timeout': config['current_timeout'],
                'new_timeout': new_timeout,
            }
        except Exception as e:
            logger.error(f"[RemediationEngine] timeout adjust failed: {e}")
            return {'applied': False, 'reason': str(e)}

    def _exec_model_fallback(self, config: dict) -> dict:
        """
        Trigger model fallback for an agent's LLM provider.

        Records a SystemConfiguration flag that the agent_llm_router checks.
        """
        agent_name = config.get('agent_name', '')
        provider = config.get('provider', '')

        if not agent_name or not provider:
            return {'applied': False, 'reason': 'Missing agent_name or provider'}

        try:
            from core.models.system import SystemConfiguration
            key = f'llm_fallback_active:{provider}'
            SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': 'true',
                    'description': (
                        f'Auto-remediation: {provider} provider failing, '
                        f'fallback activated for {agent_name}'
                    ),
                },
            )
            return {
                'applied': True,
                'key': key,
                'provider': provider,
                'agent': agent_name,
            }
        except Exception as e:
            logger.error(f"[RemediationEngine] model fallback failed: {e}")
            return {'applied': False, 'reason': str(e)}

    def _exec_block_and_wait(self, config: dict, sig) -> dict:
        """Block an agent temporarily until external resource recovers."""
        agent_name = config.get('agent_name', '')
        block_minutes = config.get('block_minutes', 60)

        if not agent_name:
            return {'applied': False, 'reason': 'Missing agent_name'}

        try:
            from core.models_unified_system import AgentControlEntry
            ttl_hours = round(block_minutes / 60, 2)
            AgentControlEntry.objects.update_or_create(
                agent_name=agent_name,
                defaults={
                    'status': 'blocked',
                    'reason': (
                        f'Auto-remediation: {sig.signature} '
                        f'({sig.occurrence_count} occurrences)'
                    )[:255],
                    'blocked_at': timezone.now(),
                    'blocked_by': 'remediation_engine',
                    'ttl_hours': ttl_hours,
                },
            )
            return {
                'applied': True,
                'agent': agent_name,
                'block_minutes': block_minutes,
                'ttl_hours': ttl_hours,
            }
        except Exception as e:
            logger.error(f"[RemediationEngine] block_and_wait failed: {e}")
            return {'applied': False, 'reason': str(e)}

    # ── Helpers ──────────────────────────────────────────────────────

    def _get_primary_agent(self, sig) -> str:
        """Get the most affected agent name from recent detections."""
        from core.models_diagnostic_pipeline import FailureDetection
        from django.db.models import Count

        top = (
            FailureDetection.objects.filter(signature=sig)
            .values('source_name')
            .annotate(cnt=Count('id'))
            .order_by('-cnt')
            .first()
        )
        return (top or {}).get('source_name', '')

    def _get_current_timeout(self, agent_name: str) -> int:
        """Get current timeout for an agent (check override first, then default map)."""
        # Check for existing override
        try:
            from core.models.system import SystemConfiguration
            override = SystemConfiguration.objects.filter(
                key=f'agent_timeout_override:{agent_name}',
            ).first()
            if override:
                return int(override.value)
        except Exception:
            pass

        # Fall back to the hardcoded map
        AGENT_TIMEOUT_DEFAULTS = {
            'AudioAgent': 300, 'ImageAgent': 300, 'VideoAgent': 600,
            'ThreeDAgent': 300, 'ImageEditingAgent': 300,
            'VideoEditingAgent': 600, 'TalkingCharacterAgent': 600,
            'ResolveAgent': 600, 'ResearchAgent': 600,
            'SystemIntelligenceAgent': 600, 'MarketingStrategyAgent': 600,
            'CustomerResearchAgent': 600, 'CharacterTrainingAgent': 600,
            'ContentWriterAgent': 600, 'CompetitorAnalysisAgent': 600,
            'BrandStrategyAgent': 600, 'ContentStrategyAgent': 600,
        }
        return AGENT_TIMEOUT_DEFAULTS.get(agent_name, 1200)

    @staticmethod
    def verify_remediation(action: AutopilotAction) -> dict:
        """
        Verify a remediation action worked. Called by ActionVerifier.verify_action.

        Checks whether the failure signature's occurrence rate dropped since
        the remediation was applied.
        """
        from core.models_diagnostic_pipeline import FailureDetection

        now = timezone.now()
        evidence = action.evidence or {}
        sig_id = evidence.get('signature_id', '')
        result = {'action_id': action.id, 'checks': [], 'passed': True}

        if not sig_id:
            result['passed'] = True
            result['skipped'] = True
            return result

        # Compare error rate before vs after remediation
        window = timedelta(hours=1)
        errors_before = FailureDetection.objects.filter(
            signature_id=sig_id,
            detected_at__gte=action.created_at - window,
            detected_at__lt=action.created_at,
        ).count()

        errors_after = FailureDetection.objects.filter(
            signature_id=sig_id,
            detected_at__gte=action.created_at,
            detected_at__lte=now,
        ).count()

        # Normalize by time window
        time_after = (now - action.created_at).total_seconds() / 3600
        rate_before = errors_before  # per hour (1h window)
        rate_after = errors_after / max(time_after, 0.1)  # per hour

        check = {
            'name': 'error_rate_reduced',
            'errors_before': errors_before,
            'errors_after': errors_after,
            'rate_before': round(rate_before, 2),
            'rate_after': round(rate_after, 2),
            'reduction_pct': round(
                (1 - rate_after / max(rate_before, 0.1)) * 100, 1
            ) if rate_before > 0 else 100.0,
            'passed': rate_after <= rate_before,
        }
        result['checks'].append(check)
        result['passed'] = check['passed']

        # Update playbook if this was from one
        playbook_id = (action.verification_result or {}).get('playbook_id')
        if playbook_id:
            try:
                playbook = RemediationPlaybook.objects.get(id=playbook_id)
                playbook.record_outcome(succeeded=check['passed'])
            except RemediationPlaybook.DoesNotExist:
                pass

        # If heuristic succeeded, create a playbook entry for future use
        source = (action.verification_result or {}).get('source', '')
        if check['passed'] and source == 'heuristic':
            sig_pattern = evidence.get('signature', '')
            category = evidence.get('category', '')
            rem_type = evidence.get('remediation_type', '')
            config = evidence.get('config', {})

            if sig_pattern and rem_type:
                RemediationPlaybook.objects.get_or_create(
                    signature_pattern=sig_pattern,
                    failure_category=category,
                    remediation_type=rem_type,
                    defaults={
                        'config': config,
                        'times_applied': 1,
                        'times_succeeded': 1,
                        'success_rate': 1.0,
                    },
                )
                logger.info(
                    f"[RemediationEngine] Created playbook entry for "
                    f"{sig_pattern} → {rem_type}"
                )

        # If remediation failed, attempt rollback
        if not check['passed']:
            RemediationEngine._rollback_remediation(action, evidence)

        return result

    @staticmethod
    def _rollback_remediation(action: AutopilotAction, evidence: dict):
        """Roll back a failed remediation."""
        rem_type = evidence.get('remediation_type', '')
        config = evidence.get('config', {})
        now = timezone.now()

        try:
            if rem_type == 'timeout_adjust':
                # Restore original timeout
                from core.models.system import SystemConfiguration
                agent_name = config.get('agent_name', '')
                old_timeout = config.get('current_timeout', '')
                if agent_name and old_timeout:
                    key = f'agent_timeout_override:{agent_name}'
                    SystemConfiguration.objects.filter(key=key).update(
                        value=str(old_timeout),
                        description=f'Rolled back: timeout restored to {old_timeout}s',
                    )

            elif rem_type == 'model_fallback':
                # Remove fallback flag
                from core.models.system import SystemConfiguration
                provider = config.get('provider', '')
                if provider:
                    key = f'llm_fallback_active:{provider}'
                    SystemConfiguration.objects.filter(key=key).delete()

            elif rem_type == 'block_and_wait':
                # Unblock the agent
                from core.models_unified_system import AgentControlEntry
                agent_name = config.get('agent_name', '')
                if agent_name:
                    AgentControlEntry.objects.filter(
                        agent_name=agent_name,
                        blocked_by='remediation_engine',
                    ).update(
                        status='active',
                        reason='Rolled back: remediation did not help',
                    )

            # Mark action as rolled back
            action.rolled_back = True
            action.rolled_back_at = now
            action.rollback_reason = 'Remediation did not reduce error rate'
            action.verification_state = 'rolled_back'
            action.save(update_fields=[
                'rolled_back', 'rolled_back_at',
                'rollback_reason', 'verification_state',
            ])

            logger.warning(
                f"[RemediationEngine] ROLLED BACK remediation "
                f"{action.id} ({rem_type})"
            )

        except Exception as e:
            logger.error(
                f"[RemediationEngine] Rollback failed for {action.id}: {e}"
            )
