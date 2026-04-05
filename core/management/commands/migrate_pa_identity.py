"""
Management command: Normalize PA identity across all models.

Finds records where agent_name/source_agent/actor_id/created_by/author
contains any of the 6 PA identity variants and normalizes them to the
canonical PA_IDENTITY value.

Usage:
    # Dry run — show what would change
    python manage.py migrate_pa_identity

    # Apply changes
    python manage.py migrate_pa_identity --apply

    # Verbose — show per-model counts
    python manage.py migrate_pa_identity --verbose
"""

from django.core.management.base import BaseCommand
from django.db.models import Q

from core.services.pa_identity import PA_IDENTITY, PA_IDENTITY_VARIANTS


# Non-canonical variants to normalize (exclude the canonical one)
VARIANTS_TO_FIX = PA_IDENTITY_VARIANTS - {PA_IDENTITY}

# Every model + field pair that could contain PA identity strings.
# Format: (app_label.ModelName, field_name)
MODEL_FIELDS = [
    ('core.Deliverable', 'agent_name'),
    ('core.HumanAttentionItem', 'source_agent'),
    ('core.ImpactEvent', 'agent_name'),
    ('core.WorkspaceOperation', 'agent_name'),
    ('core.ToolCallRecord', 'agent_name'),
    ('core.ToolCallAggregate', 'agent_name'),
    ('core.LLMCallLog', 'agent_name'),
    ('core.Initiative', 'created_by'),
    # InitiativeStage has no created_by field — skip
    ('core.AuditLog', 'actor_id'),
    # AgentExecution uses FK 'agent' not agent_name — needs separate handling
    ('core.AgentExecutionMemory', 'agent_name'),
    ('core.AgentPerformanceStats', 'agent_name'),
    ('core.IntelligentPromptMetric', 'agent_name'),
    ('core.SharedKnowledge', 'source_agent'),
    ('core.AgentPerformanceMetric', 'agent_name'),
    ('core.BusinessResearchResult', 'agent_name'),
    ('core.AgentAccuracyMetrics', 'agent_name'),
    ('core.SelfBlog', 'author'),
    ('core.BadContextEvent', 'agent_name'),
    ('core.FounderFeedback', 'created_by'),
    ('core.DecisionRecord', 'agent_name'),
    ('core.DecisionAggregate', 'agent_name'),
    ('core.ImpactCredit', 'agent_name'),
    ('core.OrchestrationStepExecution', 'agent_name'),
    ('core.WiringDefect', 'agent_name'),
    ('core.CitationViolation', 'agent_name'),
    ('core.DeliberationTurn', 'agent_name'),
    ('core.CampaignResearch', 'agent_name'),
    ('core.WorkspaceTrigger', 'source_agent'),
    ('core.AgentInteractionRecord', 'agent_name'),
    ('core.LearnedPreferenceRecord', 'agent_name'),
    ('core.AgentImprovementRecord', 'agent_name'),
    ('core.ArtifactExecution', 'agent_name'),
    # AutopilotAction table may not exist yet — skip
    ('core.CodeArtifact', 'agent_name'),
    ('core.CockpitAgentState', 'agent_name'),
    ('core.Quarantine', 'created_by'),
    ('core.PolicyExperiment', 'created_by'),
    ('core.SyntheticUserProfile', 'created_by'),
    ('core.UserAgentLearning', 'agent_name'),
    ('core.AgentLLMConfig', 'agent_name'),
]


class Command(BaseCommand):
    help = 'Audit and normalize PA identity variants across all models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help='Actually apply changes (default is dry run)',
        )
        parser.add_argument(
            '--verbose', action='store_true',
            help='Show per-variant breakdown for each model',
        )

    def handle(self, *args, **options):
        apply = options['apply']
        verbose = options['verbose']

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n{'APPLYING' if apply else 'DRY RUN'}: PA Identity Normalization"
        ))
        self.stdout.write(f"Canonical identity: {PA_IDENTITY}")
        self.stdout.write(f"Variants to fix: {sorted(VARIANTS_TO_FIX)}\n")

        total_found = 0
        total_updated = 0
        errors = []

        for model_path, field_name in MODEL_FIELDS:
            try:
                Model = self._get_model(model_path)
                if Model is None:
                    if verbose:
                        self.stdout.write(f"  SKIP  {model_path}.{field_name} — model not found")
                    continue

                # Build Q filter for all non-canonical variants
                q_filter = Q(**{f'{field_name}__in': VARIANTS_TO_FIX})
                count = Model.objects.filter(q_filter).count()

                if count == 0:
                    if verbose:
                        self.stdout.write(f"  OK    {model_path}.{field_name} — 0 variant records")
                    continue

                total_found += count

                if verbose:
                    # Show per-variant breakdown
                    for variant in sorted(VARIANTS_TO_FIX):
                        vc = Model.objects.filter(**{field_name: variant}).count()
                        if vc > 0:
                            self.stdout.write(f"         {variant}: {vc}")

                if apply:
                    updated = Model.objects.filter(q_filter).update(**{field_name: PA_IDENTITY})
                    total_updated += updated
                    self.stdout.write(self.style.SUCCESS(
                        f"  FIXED {model_path}.{field_name} — {updated} records normalized"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"  FOUND {model_path}.{field_name} — {count} records need normalization"
                    ))

            except Exception as e:
                errors.append(f"{model_path}.{field_name}: {e}")
                self.stdout.write(self.style.ERROR(
                    f"  ERROR {model_path}.{field_name} — {e}"
                ))

        # Summary
        self.stdout.write(self.style.MIGRATE_HEADING("\n--- Summary ---"))
        self.stdout.write(f"Models checked: {len(MODEL_FIELDS)}")
        self.stdout.write(f"Records with non-canonical PA identity: {total_found}")

        if apply:
            self.stdout.write(self.style.SUCCESS(f"Records normalized: {total_updated}"))
        else:
            self.stdout.write(self.style.WARNING(
                f"Records to normalize: {total_found} (run with --apply to fix)"
            ))

        if errors:
            self.stdout.write(self.style.ERROR(f"\nErrors: {len(errors)}"))
            for e in errors:
                self.stdout.write(self.style.ERROR(f"  {e}"))

    def _get_model(self, model_path: str):
        """Resolve 'core.ModelName' to Django model class."""
        from django.apps import apps
        try:
            app_label, model_name = model_path.split('.')
            return apps.get_model(app_label, model_name)
        except Exception:
            return None
