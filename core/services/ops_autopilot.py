"""
Session 1080: Ops Autopilot — automated incident response with governance guardrails.

Narrow, allowlisted actions with TTL-based reversibility:
  1. Timeout spike containment: auto-block agents with high TIMEOUT signature counts
  2. Blocked-agent hygiene: flag agents blocked too long without TTL
  3. Post-deploy watch: run SLOs since deploy, surface verdict

All actions create HumanAttentionItem for governance visibility and are logged
to AutopilotAction for audit trail.
"""

import logging
from datetime import timedelta
from typing import Any

from django.utils import timezone

from core.models_diagnostic_pipeline import AutopilotAction

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

        # Run policies
        timeout_results = self._policy_timeout_spike_containment(now)
        hygiene_results = self._policy_blocked_agent_hygiene(now)

        summary = {
            'cycle_at': now.isoformat(),
            'dry_run': self.dry_run,
            'deploy_sha': self.deploy_sha,
            'timeout_spike': timeout_results,
            'blocked_hygiene': hygiene_results,
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

    # ── Action executors ─────────────────────────────────────────────────

    def _execute_block(
        self, agent_name: str, reason: str, ttl_minutes: int,
        policy: str, evidence: dict
    ):
        """Block an agent with TTL and create governance item."""
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
        else:
            logger.info(
                f"[OpsAutopilot] DRY RUN: would block {agent_name} "
                f"for {ttl_minutes}min — {reason}"
            )

        # Log to audit table
        AutopilotAction.objects.create(
            action_type='block_agent' if not self.dry_run else 'dry_run',
            agent_name=agent_name,
            policy=policy,
            dry_run=self.dry_run,
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
