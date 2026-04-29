"""Shared runtime primitives for the task domain.

Helpers that are called by Celery tasks across multiple sibling
modules (tasks_agents, tasks_content, tasks_financial). Extracted
from core/tasks.py in Phase 3 of the Wave B refactor.

Adding helpers here:

- Pure Python; no module-level Celery imports needed (these are
  helpers, not tasks).
- Module-level imports must NOT touch core.tasks or any sibling
  task module — those modules transitively import this one. Keep
  cross-module dependencies inside function bodies as lazy imports.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def _run_agent_group(group_name: str, agent_names: list, task_generator, emoji: str = "🤖"):
    """
    Helper function to run a group of agents with a task.

    Session 787: Creates shared project ID for agent group to enable collaboration tracking.
    Session 944: Updated to use universal_agent_workspace_output for SKIN layer integration.

    Args:
        group_name: Name of the agent group for logging
        agent_names: List of agent names to execute
        task_generator: Function that takes agent_name and returns a task string
        emoji: Emoji for logging
    """
    from django.utils import timezone
    from core.tasks_agents import universal_agent_workspace_output

    logger.info(f"{emoji} [{group_name}] Starting scheduled agent group...")

    results = []

    # Session 787: Create a shared project ID for this agent group run
    shared_project_id = f"{group_name.lower().replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M')}"

    for agent_name in agent_names:
        try:
            task = task_generator(agent_name)

            # Session 944: Use universal_agent_workspace_output to create WorkspaceOperations
            # This ensures agent outputs appear in the Operations Tab
            result = universal_agent_workspace_output(
                agent_name=agent_name,
                topic=task,
                trigger_source='schedule',
                force_production=True  # These are real scheduled runs, not warmups
            )

            success = result.get('success', False) if isinstance(result, dict) else False

            # Session 787: Track contribution with shared project ID for collaboration
            _track_group_contribution(agent_name, group_name, shared_project_id, success)

            results.append({
                'agent': agent_name,
                'success': success,
                'project_id': shared_project_id,
                'file': result.get('file') if isinstance(result, dict) else None,
            })

            status = '✅' if success else '❌'
            logger.info(f"{emoji} [{group_name}] {agent_name}: {status}")

        except Exception as e:
            logger.warning(f"{emoji} [{group_name}] {agent_name} failed: {e}")
            results.append({'agent': agent_name, 'success': False, 'error': str(e)})

    succeeded = len([r for r in results if r.get('success')])
    logger.info(f"{emoji} [{group_name}] Complete: {succeeded}/{len(results)} succeeded (project: {shared_project_id})")
    return results


def _track_group_contribution(agent_name: str, group_name: str, project_id: str, success: bool):
    """
    Session 787: Track agent contribution with shared project ID.
    This creates proper collaboration records when multiple agents work together.

    Session 800 fix: project field requires PartnershipProject instance, not string.
    Since scheduled runs don't have real projects, we create contributions without project.
    """
    try:
        from core.models.agents_registry import AgentContribution, UnifiedAgentTemplate

        # Get or create the agent template
        agent_template, _ = UnifiedAgentTemplate.objects.get_or_create(
            name=agent_name,
            defaults={
                'display_name': agent_name.replace('Agent', ' Agent'),
                'description': f'{agent_name} scheduled execution',
                'specialization': 'general',
            }
        )

        # Session 800: Create contribution without project (project is nullable since Session 752)
        # Scheduled agent runs don't have real PartnershipProject instances
        AgentContribution.objects.create(
            agent=agent_template,
            project=None,  # Session 800: Was passing string, but field requires PartnershipProject instance
            contribution_type='orchestration',
            contribution_role='Collaborator',
            task_description=f'{agent_name} participating in {group_name} scheduled run (project: {project_id})',
            contribution_percentage=100 if success else 0,
        )

        logger.debug(f"✓ Tracked collaboration: {agent_name} -> group {group_name}")

    except Exception as e:
        logger.warning(f"Could not track contribution for {agent_name}: {e}")

