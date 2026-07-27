# S2989 Phase B — DocResearchFinding table for docs/research/ finding registry.
# Hand-written minimal migration so we don't accidentally touch unrelated
# drifted schema in the makemigrations autopick.

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0397_s2987_memory_supersede"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DocResearchFinding",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("doc_path", models.CharField(db_index=True, max_length=500)),
                (
                    "domain_slug",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=100
                    ),
                ),
                (
                    "source_type",
                    models.CharField(
                        choices=[
                            ("audit", "Audit"),
                            ("canonical_summary", "Canonical Summary"),
                            ("implementation_debt", "Implementation Debt"),
                        ],
                        db_index=True,
                        default="audit",
                        max_length=32,
                    ),
                ),
                (
                    "source_heading",
                    models.CharField(blank=True, default="", max_length=500),
                ),
                ("text", models.TextField()),
                ("text_hash", models.CharField(db_index=True, max_length=64)),
                (
                    "confidence",
                    models.CharField(
                        choices=[
                            ("high", "High"),
                            ("medium", "Medium"),
                            ("low", "Low"),
                        ],
                        default="medium",
                        max_length=16,
                    ),
                ),
                ("tags", models.JSONField(blank=True, default=list)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("fixed", "Fixed"),
                            ("dismissed", "Dismissed"),
                        ],
                        db_index=True,
                        default="open",
                        max_length=16,
                    ),
                ),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "resolved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="resolved_audit_findings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("resolution_note", models.TextField(blank=True, default="")),
                ("deliverable_id", models.CharField(blank=True, default="", max_length=64)),
                ("first_seen_at", models.DateTimeField(auto_now_add=True)),
                ("last_seen_at", models.DateTimeField(auto_now=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "db_table": "core_doc_research_finding",
            },
        ),
        migrations.AddIndex(
            model_name="docresearchfinding",
            index=models.Index(
                fields=["status", "doc_path"], name="drf_status_docpath_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="docresearchfinding",
            index=models.Index(
                fields=["status", "domain_slug"], name="drf_status_domain_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="docresearchfinding",
            constraint=models.UniqueConstraint(
                fields=("doc_path", "text_hash"),
                name="uniq_doc_research_finding_doc_hash",
            ),
        ),
    ]
