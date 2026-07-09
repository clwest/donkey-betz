"""
Core app configuration for Django

Session 623: Added database startup health check to verify
all Django models have corresponding PostgreSQL tables.
"""
import os
import sys
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    """Django app configuration for the core app"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Unified Platform Core'

    def ready(self):
        """Initialize core services when Django starts"""
        # Import signals to register them
        self._register_signals()

        # Only run startup health check in the main process
        # Skip during migrations, makemigrations, and other management commands
        if self._should_run_startup_check():
            self._run_database_health_check()

    def _register_signals(self):
        """Register Django signals for the core app"""
        try:
            from core.learning_bridges import apps as learning_apps
            # Learning bridges register their own signals
        except ImportError:
            pass  # Learning bridges not available

        # Session 766: Connect dream execution signals
        try:
            from core.signals import connect_dream_signals
            connect_dream_signals()
        except ImportError:
            pass  # Dream signals not available

        # Session 822: Connect revenue tracking signals
        try:
            from core.signals import connect_revenue_signals
            connect_revenue_signals()
        except ImportError:
            pass  # Revenue signals not available

        # Session 861: Connect feedback processing signals
        try:
            from core.models_feedback_processing import connect_feedback_signals
            connect_feedback_signals()
        except ImportError:
            pass  # Feedback processing not available

        # Session 863: Connect ConceptForge signals
        try:
            from core.signals import connect_conceptforge_signals
            connect_conceptforge_signals()
        except ImportError:
            pass  # ConceptForge signals not available

        # Session 1095: Connect Deliverable status-transition signals
        # for the COO rework/bounce gate.
        try:
            from core.signals import connect_deliverable_status_signals
            connect_deliverable_status_signals()
        except ImportError:
            pass  # Deliverable status signals not available

        # Cycle 1A KFI-1 (ADR-0110): connect the Deliverable → Document
        # mirror signal (fires on new ratification_record deliverables).
        try:
            from core.signals.deliverable_mirror_signals import (
                connect_deliverable_mirror_signals,
            )
            connect_deliverable_mirror_signals()
        except ImportError:
            pass  # Deliverable mirror signals not available

        # Session 1250 PR 8: Connect Rigby Mission Delegation lifecycle
        # signals — observes AgentExecution.post_save for delegated
        # executions and appends agent_assigned / agent_completed /
        # verification_* / mission_closed events to the parent MissionRun.
        # Gated by settings.RIGBY_DELEGATION_ENABLED (default False).
        try:
            from core.signals import connect_rigby_delegation_signals
            connect_rigby_delegation_signals()
        except ImportError:
            pass  # Rigby delegation signals not available

        # Session 1095 Tier 1b: Connect MythologyAlert → HAI bridge so
        # critical/high mythology alerts surface in the governance inbox.
        try:
            from core.signals import connect_mythology_alert_signals
            connect_mythology_alert_signals()
        except ImportError:
            pass  # Mythology alert signals not available

        # Session 873: Connect experiment linker signals for halt system instrumentation
        try:
            from core.services.experiment_linker import connect_experiment_linker_signals
            connect_experiment_linker_signals()
        except ImportError:
            pass  # Experiment linker not available

        # Session 1073: Connect push notification signals
        try:
            import core.signals_push_notifications  # noqa: F401
        except ImportError:
            pass  # Push notification signals not available

        # Session 1115 batch-7: Connect Document + NarrativeShift signals so
        # process_document_async and trigger_content_from_shift fire when
        # their source rows are saved.
        try:
            from core.signals import connect_document_processing_signals
            connect_document_processing_signals()
        except ImportError:
            pass  # Document processing signals not available

        # Session 1196 PR #2 — Initiative no-orphan diagnostic signal.
        # Post-save handler marks newly-created Initiative rows
        # ``diagnostic`` when ``target_workspace_id`` is NULL. Mirrors
        # Plan C Phase 1 (Session 1195 PR #2403) shape on Deliverable
        # but routed through a signal because Initiative has 8+ create
        # callsites with no single factory to wrap. Kill switch via
        # ``INITIATIVE_DIAGNOSTICS_ENABLED`` (default True).
        try:
            from core.signals import connect_initiative_diagnostic_signals
            connect_initiative_diagnostic_signals()
        except ImportError:
            pass  # Initiative diagnostic signals not available

        # Session 2734 — Capability Chain §1 Mission Completion.
        # Post-save handler on OpsRunEvent broadcasts a
        # ``mission_verdict`` system event when
        # ``label.startswith('verdict_issued:')`` on a mission-domain
        # run. Wired via ``transaction.on_commit`` so a rolled-back
        # transaction produces no phantom broadcast.
        try:
            from core.signals import connect_mission_verdict_signals
            connect_mission_verdict_signals()
        except ImportError:
            pass  # Mission verdict signals not available

        # Session 2734 — Capability Chain §6 Signal Detection.
        # Post-save handler on SignalCluster escalates high-strength
        # patterns (>= configurable threshold via SystemConfiguration
        # key 'signal_pattern_criticality_threshold', default 0.9) into
        # HumanAttentionItem via HumanAttentionBridge. Kill switch:
        # ``settings.SIGNAL_PATTERN_CRITICALITY_ENABLED`` (default True).
        try:
            from core.signals import connect_signal_pattern_criticality_signals
            connect_signal_pattern_criticality_signals()
        except ImportError:
            pass  # Signal pattern criticality signals not available

        # Session 2734 — Capability Chain §14 Platform Health.
        # Post-save handler on HeartBeat escalates critical/offline
        # ``overall_status`` into HumanAttentionItem via
        # HumanAttentionBridge. Includes 1-hour dedup gate to prevent
        # 6× duplicate HAI rows across a persistent-critical hour of
        # 10-min scans. Kill switch:
        # ``settings.BODY_SYSTEM_DEGRADATION_HAI_ENABLED`` (default True).
        try:
            from core.signals import connect_body_system_degradation_signals
            connect_body_system_degradation_signals()
        except ImportError:
            pass  # Body system degradation signals not available

        # Session 2734 — Platform Closure Category B: Capability Chain
        # §1 Item 9 HAI on mission verdict. Second post_save receiver
        # on OpsRunEvent (distinct dispatch_uid from the WS-broadcast
        # receiver). Filters on mission-domain rows with label
        # 'verdict_issued:rejected' or 'verdict_issued:deferred' and
        # dispatches HumanAttentionBridge.create_mission_verdict_attention.
        # Kill switch: settings.MISSION_VERDICT_HAI_ENABLED (default True).
        try:
            from core.signals import connect_mission_verdict_attention_signals
            connect_mission_verdict_attention_signals()
        except ImportError:
            pass  # Mission verdict attention signals not available

    def _should_run_startup_check(self):
        """Determine if we should run the startup health check"""
        # Check if DATABASE_AUDIT_ON_STARTUP is enabled
        if not os.environ.get('DATABASE_AUDIT_ON_STARTUP', '').lower() in ('1', 'true', 'yes'):
            return False

        # Skip during management commands that shouldn't trigger checks
        skip_commands = [
            'migrate', 'makemigrations', 'showmigrations',
            'sqlmigrate', 'squashmigrations',
            'createsuperuser', 'shell', 'dbshell',
            'inspectdb', 'flush', 'dumpdata', 'loaddata',
            'collectstatic', 'compilemessages',
            'audit_database',  # Don't double-run during audit
        ]

        for cmd in skip_commands:
            if cmd in sys.argv:
                return False

        # Only run in the main process for runserver
        # (RUN_MAIN is set by the reloader)
        if 'runserver' in sys.argv:
            return os.environ.get('RUN_MAIN') == 'true'

        return True

    def _run_database_health_check(self):
        """Run a quick database schema health check on startup"""
        try:
            from django.apps import apps as django_apps
            from django.db import connection

            # Get all tables that should exist
            model_tables = set()
            for model in django_apps.get_models():
                model_tables.add(model._meta.db_table)

            # Get existing tables
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                """)
                existing_tables = {row[0] for row in cursor.fetchall()}

            # Find missing tables
            missing = model_tables - existing_tables

            if missing:
                logger.warning(
                    f"🚨 DATABASE HEALTH CHECK: {len(missing)} model(s) missing tables! "
                    f"Run 'python manage.py audit_database --verbose' for details."
                )
                # Log first 5 missing tables for quick reference
                for table in list(missing)[:5]:
                    logger.warning(f"   Missing: {table}")
                if len(missing) > 5:
                    logger.warning(f"   ... and {len(missing) - 5} more")

                # Optionally fail fast if DATABASE_AUDIT_STRICT is set
                if os.environ.get('DATABASE_AUDIT_STRICT', '').lower() in ('1', 'true', 'yes'):
                    raise RuntimeError(
                        f"Database integrity check failed: {len(missing)} tables missing. "
                        "Run 'python manage.py migrate' to fix or set "
                        "DATABASE_AUDIT_STRICT=false to disable strict mode."
                    )
            else:
                logger.info(
                    f"✅ Database health check passed: "
                    f"{len(model_tables)} models verified"
                )

        except Exception as e:
            # Don't crash Django startup on health check failures
            # Just log the error
            logger.error(f"Database health check error: {e}")
