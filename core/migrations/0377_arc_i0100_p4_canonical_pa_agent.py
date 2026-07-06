"""Arc I-0100 P4 (IB-1799-T1-02) migration — canonical PersonalAssistant
Agent row per ADR-0002 §3.2 Sub-option 1(i).

Per Arc I-0100 scoping §5 P4 + ADR-0002 §3.2 F3 fold: create the
canonical ``Agent(name='PersonalAssistant', ...)`` row that PA-authored
``AgentExecution`` rows will FK to. Preserves the non-null-FK invariant
that current consumers of ``AgentExecution.agent`` rely on.

F3 fold (SIGN Cycle 1 verified): migration MUST populate every
Yes-required Agent field. Per Stage 3 pre-flight enumeration of the
``core.models_unified_system.Agent`` model:

- ``name`` (CharField, unique=True) — Yes-required; value ``'PersonalAssistant'``
- ``agent_type`` (CharField) — Yes-required; value ``'meta'``
- ``description`` (TextField) — Yes-required
- ``specialization`` (CharField) — Yes-required; value ``'personal_assistant'``

All other Agent fields have defaults (``capabilities`` dict,
``effectiveness_score`` 85, ``is_active`` True, etc.) or are optional
(``category`` FK is nullable). ``id`` is auto-populated via
``uuid.uuid4``.

F4 fold: uniqueness constraint verified at Stage 3 pre-flight —
``name`` is the sole ``unique=True`` field; ``Meta.unique_together``
is empty; no ``UniqueConstraint`` set. ``get_or_create(name=...)`` is
sufficient for the migration.

Idempotent: uses ``get_or_create`` — safe to re-run.
"""

from django.db import migrations


def create_canonical_pa_agent(apps, schema_editor):
    """Create the canonical PersonalAssistant Agent row.

    Idempotent via ``get_or_create``. If a PA row already exists (from
    a prior migration run OR manual creation), preserve it — do not
    overwrite fields.
    """
    Agent = apps.get_model('core', 'Agent')

    agent, created = Agent.objects.get_or_create(
        name='PersonalAssistant',
        defaults={
            'agent_type': 'meta',
            'description': (
                'Canonical PA / Rigby meta-agent row for AgentExecution FK '
                '(ADR-0002 Sub-option 1(i)). Represents the Personal '
                'Assistant agentic loop as a foreign-key target so '
                'PA-authored AgentExecution rows preserve the non-null-FK '
                'invariant existing consumers rely on. See '
                'docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md '
                '§3.2 for the ratified design decision.'
            ),
            'specialization': 'personal_assistant',
        },
    )
    if created:
        print(f"  [0377] created canonical PersonalAssistant Agent row id={agent.id}")
    else:
        print(f"  [0377] PersonalAssistant Agent row already exists id={agent.id} — noop")


def reverse_create_canonical_pa_agent(apps, schema_editor):
    """Reverse: delete the canonical PA Agent row iff no
    ``AgentExecution`` rows FK to it. Safe pattern per ADR-0002 §6.2.
    """
    Agent = apps.get_model('core', 'Agent')
    AgentExecution = apps.get_model('core', 'AgentExecution')

    pa_agents = list(Agent.objects.filter(name='PersonalAssistant'))
    if not pa_agents:
        print("  [0377] no PersonalAssistant Agent row to reverse — noop")
        return

    for pa_agent in pa_agents:
        dependent_count = AgentExecution.objects.filter(agent_id=pa_agent.id).count()
        if dependent_count > 0:
            print(
                f"  [0377] REFUSING to delete PersonalAssistant Agent id={pa_agent.id} "
                f"— {dependent_count} AgentExecution rows depend on it. "
                f"Truncate PA-source rows first: "
                f"AgentExecution.objects.filter(input_data__source='pa').delete()"
            )
            continue
        agent_id = pa_agent.id
        pa_agent.delete()
        print(f"  [0377] deleted PersonalAssistant Agent row id={agent_id} (0 dependents)")


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0376_session_1267_flip_bug_triage_beat_enabled'),
    ]

    operations = [
        migrations.RunPython(
            create_canonical_pa_agent,
            reverse_code=reverse_create_canonical_pa_agent,
        ),
    ]
