# Session 1086: Sync diagnostic pipeline + AutopilotAction into migration state
#
# Background:
# - Diagnostic pipeline models (FailureSignature, etc.) were created in 0197
#   but registered via core/models.py (file). When core/models/__init__.py
#   (package) became primary, Django lost track of them in migration state.
# - 0282 accidentally included DeleteModel('AutopilotAction').
# - This migration re-syncs: state-only for existing tables, RunPython for
#   AutopilotAction table recreation + verification columns.

import django.db.models.deletion
import uuid
from django.db import migrations, models


def create_or_update_autopilot_table(apps, schema_editor):
    """Create AutopilotAction table or add verification columns if it exists."""
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'core_autopilotaction' LIMIT 1"
        )
        if cursor.fetchone():
            # Table exists — add new verification columns if missing
            for col_sql in [
                "ALTER TABLE core_autopilotaction ADD COLUMN IF NOT EXISTS verification_state varchar(20) DEFAULT 'skipped' NOT NULL",
                "ALTER TABLE core_autopilotaction ADD COLUMN IF NOT EXISTS verification_result jsonb DEFAULT '{}' NOT NULL",
                "ALTER TABLE core_autopilotaction ADD COLUMN IF NOT EXISTS rolled_back boolean DEFAULT false NOT NULL",
                "ALTER TABLE core_autopilotaction ADD COLUMN IF NOT EXISTS rolled_back_at timestamp with time zone NULL",
                "ALTER TABLE core_autopilotaction ADD COLUMN IF NOT EXISTS rollback_reason varchar(255) DEFAULT '' NOT NULL",
            ]:
                try:
                    cursor.execute(col_sql)
                except Exception:
                    pass
        else:
            cursor.execute("""
                CREATE TABLE core_autopilotaction (
                    id serial PRIMARY KEY,
                    created_at timestamp with time zone NOT NULL DEFAULT NOW(),
                    action_type varchar(30) NOT NULL,
                    agent_name varchar(100) NOT NULL DEFAULT '',
                    policy varchar(100) NOT NULL,
                    dry_run boolean NOT NULL DEFAULT false,
                    evidence jsonb NOT NULL DEFAULT '{}',
                    result jsonb NOT NULL DEFAULT '{}',
                    deploy_sha varchar(40) NOT NULL DEFAULT '',
                    verification_state varchar(20) NOT NULL DEFAULT 'skipped',
                    verification_result jsonb NOT NULL DEFAULT '{}',
                    rolled_back boolean NOT NULL DEFAULT false,
                    rolled_back_at timestamp with time zone NULL,
                    rollback_reason varchar(255) NOT NULL DEFAULT ''
                )
            """)

        # Create indexes idempotently
        for idx_name, col_sql in [
            ('core_autopi_action__5361f6_idx', 'action_type, created_at DESC'),
            ('core_autopi_agent_n_ac2dc2_idx', 'agent_name, created_at DESC'),
            ('core_autopilotaction_created_at_idx', 'created_at DESC'),
            ('core_autopilotaction_verif_idx', 'verification_state'),
        ]:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON core_autopilotaction ({col_sql})')
            except Exception:
                pass


def create_diagnostic_indexes(apps, schema_editor):
    """Create any missing indexes for diagnostic pipeline models."""
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        indexes = [
            ('core_failur_status_fa107d_idx', 'core_failure_signature', 'status'),
            ('core_failur_categor_19cd7e_idx', 'core_failure_signature', 'category'),
            ('core_failur_provide_787924_idx', 'core_failure_signature', 'provider'),
            ('core_failur_last_se_62319b_idx', 'core_failure_signature', 'last_seen_at DESC'),
            ('core_failur_status_6eb24e_idx', 'core_failure_prescription', 'status'),
            ('core_failur_scope_09be7c_idx', 'core_failure_prescription', 'scope'),
            ('core_failur_priorit_ca8ca3_idx', 'core_failure_prescription', 'priority_score DESC'),
            ('core_failur_source__1d4b48_idx', 'core_failure_detection', 'source_type'),
            ('core_failur_is_diag_3acb80_idx', 'core_failure_detection', 'is_diagnosed'),
            ('core_failur_detecte_b4989b_idx', 'core_failure_detection', 'detected_at DESC'),
            ('core_failur_signatu_617706_idx', 'core_failure_detection', 'signature_id, is_diagnosed'),
        ]
        for idx_name, table, cols in indexes:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON "{table}" ({cols})')
            except Exception:
                pass


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0283_add_deliberation_failure_tracking"),
    ]

    operations = [
        # All operations are state-only — tables already exist on Railway.
        # RunPython handles any DB changes needed (AutopilotAction recreation,
        # new verification columns, missing indexes).
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="AutopilotAction",
                    fields=[
                        ("id", models.AutoField(primary_key=True, serialize=False)),
                        ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                        ("action_type", models.CharField(choices=[("block_agent", "Block Agent"), ("unblock_agent", "Unblock Agent"), ("attention_item", "Created Attention Item"), ("deploy_watch", "Deploy Watch Verdict"), ("dry_run", "Dry Run (no action taken)"), ("retry_deliberation", "Retry Failed Deliberation"), ("content_sweep", "Content Pipeline Sweep"), ("auto_resolve", "Auto-resolve Attention Item"), ("content_publish", "Content Auto-Publish")], max_length=30)),
                        ("agent_name", models.CharField(blank=True, default="", max_length=100)),
                        ("policy", models.CharField(help_text="Policy rule that triggered this action", max_length=100)),
                        ("dry_run", models.BooleanField(default=False)),
                        ("evidence", models.JSONField(default=dict, help_text="Signature IDs, counts, sample exec IDs, etc.")),
                        ("result", models.JSONField(default=dict, help_text="Outcome of the action")),
                        ("deploy_sha", models.CharField(blank=True, default="", max_length=40)),
                        ("verification_state", models.CharField(choices=[("pending", "Pending Verification"), ("passed", "Verification Passed"), ("failed", "Verification Failed"), ("rolled_back", "Rolled Back"), ("skipped", "Verification Skipped")], db_index=True, default="skipped", help_text="Pre/post verification outcome", max_length=20)),
                        ("verification_result", models.JSONField(blank=True, default=dict, help_text="Pre-check results, post-verification SLO deltas, rollback details")),
                        ("rolled_back", models.BooleanField(default=False)),
                        ("rolled_back_at", models.DateTimeField(blank=True, null=True)),
                        ("rollback_reason", models.CharField(blank=True, default="", max_length=255)),
                    ],
                    options={"ordering": ["-created_at"], "indexes": [
                        models.Index(fields=["action_type", "-created_at"], name="core_autopi_action__5361f6_idx"),
                        models.Index(fields=["agent_name", "-created_at"], name="core_autopi_agent_n_ac2dc2_idx"),
                    ]},
                ),
                migrations.CreateModel(
                    name="FailureSignature",
                    fields=[
                        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ("signature", models.CharField(db_index=True, help_text="Stable signature like OPENAI_429_QUOTA", max_length=255, unique=True)),
                        ("signature_hash", models.CharField(help_text="MD5 hash for fast lookup", max_length=32, unique=True)),
                        ("category", models.CharField(choices=[("provider_error", "Provider Error"), ("timeout", "Timeout"), ("data_error", "Data Error"), ("execution_error", "Execution Error"), ("resource_error", "Resource Error"), ("unknown", "Unknown")], default="unknown", max_length=30)),
                        ("provider", models.CharField(blank=True, help_text="Provider name if provider-related (openai, anthropic, etc.)", max_length=50)),
                        ("error_code", models.CharField(blank=True, help_text="HTTP status code or error code (429, 500, etc.)", max_length=50)),
                        ("occurrence_count", models.PositiveIntegerField(default=0, help_text="Total times this signature has been seen")),
                        ("first_seen_at", models.DateTimeField(auto_now_add=True)),
                        ("last_seen_at", models.DateTimeField(auto_now=True)),
                        ("last_diagnosed_at", models.DateTimeField(blank=True, help_text="Last time this signature was diagnosed (for cooldown)", null=True)),
                        ("status", models.CharField(choices=[("active", "Active"), ("known_outage", "Known Outage"), ("diagnosed", "Diagnosed"), ("resolved", "Resolved"), ("ignored", "Ignored")], default="active", max_length=20)),
                        ("description", models.TextField(blank=True, help_text="Human-readable explanation of this failure type")),
                        ("metadata", models.JSONField(default=dict)),
                    ],
                    options={"db_table": "core_failure_signature", "ordering": ["-occurrence_count", "-last_seen_at"], "indexes": [
                        models.Index(fields=["status"], name="core_failur_status_fa107d_idx"),
                        models.Index(fields=["category"], name="core_failur_categor_19cd7e_idx"),
                        models.Index(fields=["provider"], name="core_failur_provide_787924_idx"),
                        models.Index(fields=["-last_seen_at"], name="core_failur_last_se_62319b_idx"),
                    ]},
                ),
                migrations.CreateModel(
                    name="FailureDiagnosis",
                    fields=[
                        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ("root_cause", models.TextField(help_text="Detailed explanation of why this is happening")),
                        ("root_cause_confidence", models.FloatField(default=0.0, help_text="Confidence score 0-1")),
                        ("evidence_sources", models.JSONField(default=list, help_text="List of evidence types used: ['exception', 'provider', 'rate_limit', 'system_event', 'llm_synthesis']")),
                        ("evidence_details", models.JSONField(default=dict, help_text="Detailed evidence per source type")),
                        ("blast_radius", models.CharField(choices=[("isolated", "Isolated (single component)"), ("limited", "Limited (few components)"), ("widespread", "Widespread (many components)"), ("critical", "Critical (system-wide)")], default="isolated", max_length=20)),
                        ("affected_components", models.JSONField(default=list, help_text="List of affected components/agents/services")),
                        ("sample_count", models.PositiveIntegerField(default=0, help_text="Number of detections used for this diagnosis")),
                        ("sample_time_range", models.JSONField(default=dict, help_text="{'from': ISO timestamp, 'to': ISO timestamp}")),
                        ("diagnosed_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        ("signature", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="diagnosis", to="core.failuresignature")),
                    ],
                    options={"db_table": "core_failure_diagnosis", "ordering": ["-diagnosed_at"]},
                ),
                migrations.CreateModel(
                    name="FailurePrescription",
                    fields=[
                        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ("title", models.CharField(max_length=255)),
                        ("description", models.TextField()),
                        ("scope", models.CharField(choices=[("immediate", "Immediate (stop bleeding)"), ("structural", "Structural (prevent recurrence)"), ("observability", "Observability (make obvious)")], max_length=20)),
                        ("expected_impact", models.CharField(choices=[("high", "High Impact"), ("medium", "Medium Impact"), ("low", "Low Impact")], default="medium", max_length=10)),
                        ("effort", models.CharField(choices=[("trivial", "Trivial (<30 min)"), ("small", "Small (1-2 hours)"), ("medium", "Medium (half day)"), ("large", "Large (full day+)")], default="small", max_length=10)),
                        ("confidence", models.FloatField(default=0.0, help_text="Confidence that this fix will work (0-1)")),
                        ("priority_score", models.FloatField(default=0.0, help_text="Computed priority score for ranking")),
                        ("technical_steps", models.JSONField(default=list, help_text="List of technical steps to implement")),
                        ("files_to_modify", models.JSONField(default=list, help_text="List of file paths that need changes")),
                        ("commands_to_run", models.JSONField(default=list, help_text="Shell commands to execute")),
                        ("success_criteria", models.TextField(blank=True, help_text="How we'll know this fix worked")),
                        ("verification_steps", models.JSONField(default=list, help_text="Steps to verify the fix")),
                        ("status", models.CharField(choices=[("proposed", "Proposed"), ("approved", "Approved"), ("in_progress", "In Progress"), ("completed", "Completed"), ("verified", "Verified"), ("rejected", "Rejected")], default="proposed", max_length=20)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        ("completed_at", models.DateTimeField(blank=True, null=True)),
                        ("verified_at", models.DateTimeField(blank=True, null=True)),
                        ("diagnosis", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="prescriptions", to="core.failurediagnosis")),
                        ("initiative", models.ForeignKey(blank=True, help_text="Auto-created Initiative for tracking remediation", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="prescriptions", to="core.initiative")),
                    ],
                    options={"db_table": "core_failure_prescription", "ordering": ["-priority_score", "scope"], "indexes": [
                        models.Index(fields=["status"], name="core_failur_status_6eb24e_idx"),
                        models.Index(fields=["scope"], name="core_failur_scope_09be7c_idx"),
                        models.Index(fields=["-priority_score"], name="core_failur_priorit_ca8ca3_idx"),
                    ]},
                ),
                migrations.CreateModel(
                    name="FailureDetection",
                    fields=[
                        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ("source_type", models.CharField(choices=[("experiment", "Experiment"), ("agent_execution", "Agent Execution"), ("spider", "Spider"), ("celery_task", "Celery Task"), ("api_call", "API Call"), ("provider", "Provider"), ("http_request", "HTTP Request")], max_length=30)),
                        ("source_id", models.UUIDField(blank=True, help_text="ID of the failed entity (experiment, execution, etc.)", null=True)),
                        ("source_name", models.CharField(blank=True, help_text="Human-readable name of what failed", max_length=255)),
                        ("error_message", models.TextField(help_text="The actual error message")),
                        ("error_code", models.CharField(blank=True, help_text="HTTP status or error code", max_length=50)),
                        ("stack_trace", models.TextField(blank=True, help_text="Full stack trace if available")),
                        ("context_snapshot", models.JSONField(default=dict, help_text="Context data: provider, endpoint, model, params, etc.")),
                        ("is_diagnosed", models.BooleanField(default=False, help_text="Has this detection been processed for diagnosis?")),
                        ("detected_at", models.DateTimeField(auto_now_add=True)),
                        ("diagnosed_at", models.DateTimeField(blank=True, null=True)),
                        ("signature", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="detections", to="core.failuresignature")),
                    ],
                    options={"db_table": "core_failure_detection", "ordering": ["-detected_at"], "indexes": [
                        models.Index(fields=["source_type"], name="core_failur_source__1d4b48_idx"),
                        models.Index(fields=["is_diagnosed"], name="core_failur_is_diag_3acb80_idx"),
                        models.Index(fields=["-detected_at"], name="core_failur_detecte_b4989b_idx"),
                        models.Index(fields=["signature", "is_diagnosed"], name="core_failur_signatu_617706_idx"),
                    ]},
                ),
            ],
            database_operations=[],
        ),
        # DB operations: create/update AutopilotAction table and add all indexes
        migrations.RunPython(create_or_update_autopilot_table, noop),
        migrations.RunPython(create_diagnostic_indexes, noop),
    ]
