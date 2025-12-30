"""
System Reality Checker Service
==============================

Session 624: Comprehensive verification that all autonomous systems
are functioning as designed.

Monitors 10 autonomous systems:
1. Celery Beat - 97 scheduled tasks
2. SituationTriggers - Event-driven alerts
3. Learning Loops - Agent knowledge transfers
4. Agent Dreams - Creative ideation pipeline
5. Dream Productization - Promotion and implementation
6. Boardroom - Human-in-loop decisions
7. ThinkingAgent - Autonomous reasoning
8. Agent Conversations - Hive mind sessions
9. Spider Network - Data collection
10. Pilots/Gates - Experiment progression
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from django.utils import timezone
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


@dataclass
class SystemCheck:
    """Result of checking a single system"""
    name: str
    score: int  # 0-100
    status: str  # healthy, warning, critical
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)


class SystemRealityChecker:
    """
    Comprehensive system health checker that verifies all autonomous
    systems are functioning as designed.
    """

    # Score thresholds
    HEALTHY_THRESHOLD = 70
    WARNING_THRESHOLD = 50

    def __init__(self, lookback_hours: int = 6):
        self.lookback_hours = lookback_hours
        self.lookback = timedelta(hours=lookback_hours)
        self.now = timezone.now()
        self.cutoff = self.now - self.lookback
        self.checks: List[SystemCheck] = []

    def run(self) -> Dict[str, Any]:
        """Run all system checks and return comprehensive results"""
        self.checks = []

        # Run all checks
        self.check_celery_beat()
        self.check_triggers()
        self.check_learning_loops()
        self.check_dreams_pipeline()
        self.check_boardroom()
        self.check_thinking_agent()
        self.check_agent_conversations()
        self.check_spider_network()
        self.check_pilots_gates()

        return self.compile_results()

    def calculate_score(
        self,
        activity_ratio: float = 1.0,
        progress_ratio: float = 1.0,
        health_ratio: float = 1.0
    ) -> int:
        """
        Calculate reality score (0-100) based on:
        - Activity (40%): Is there recent activity?
        - Progress (30%): Are things moving through pipeline?
        - Health (30%): Are there errors or backlogs?
        """
        activity_score = min(100, activity_ratio * 100)
        progress_score = min(100, progress_ratio * 100)
        health_score = min(100, health_ratio * 100)

        return int((activity_score * 0.4) + (progress_score * 0.3) + (health_score * 0.3))

    def get_status(self, score: int) -> str:
        """Get status string based on score"""
        if score >= self.HEALTHY_THRESHOLD:
            return "healthy"
        elif score >= self.WARNING_THRESHOLD:
            return "warning"
        return "critical"

    def check_celery_beat(self):
        """Check if scheduled Celery tasks are running on time"""
        try:
            from django_celery_beat.models import PeriodicTask

            enabled_tasks = PeriodicTask.objects.filter(enabled=True)
            total_tasks = enabled_tasks.count()

            if total_tasks == 0:
                self.checks.append(SystemCheck(
                    name="Celery Beat",
                    score=0,
                    status="critical",
                    message="No enabled tasks found",
                    metrics={"total": 0, "ran": 0}
                ))
                return

            # Check how many tasks have run recently using last_run_at
            # (Result backend stores to Redis, not Django DB)
            ran_recently = enabled_tasks.filter(last_run_at__gte=self.cutoff).count()

            # Find tasks that never ran or are stale
            stale_tasks = []
            for task in enabled_tasks.filter(
                Q(last_run_at__isnull=True) | Q(last_run_at__lt=self.cutoff)
            )[:10]:
                stale_tasks.append(task.name)

            activity_ratio = ran_recently / total_tasks if total_tasks > 0 else 0
            score = self.calculate_score(activity_ratio=activity_ratio, health_ratio=activity_ratio)

            issues = []
            if stale_tasks[:5]:
                issues.append(f"Stale tasks: {', '.join(stale_tasks[:5])}")
                if len(stale_tasks) > 5:
                    issues.append(f"...and {len(stale_tasks) - 5} more")

            self.checks.append(SystemCheck(
                name="Celery Beat",
                score=score,
                status=self.get_status(score),
                message=f"{ran_recently}/{total_tasks} tasks ran in {self.lookback_hours}h",
                metrics={"total": total_tasks, "ran": ran_recently, "stale": len(stale_tasks)},
                issues=issues
            ))
        except Exception as e:
            logger.exception("Celery Beat check failed")
            self.checks.append(SystemCheck(
                name="Celery Beat",
                score=0,
                status="critical",
                message=f"Check failed: {str(e)}",
                issues=[str(e)]
            ))

    def check_triggers(self):
        """Check if situation triggers are firing"""
        try:
            from core.models_situation_triggers import SituationTrigger, TriggerEvent

            active_triggers = SituationTrigger.objects.filter(is_active=True).count()
            recent_fires = TriggerEvent.objects.filter(
                processed_at__gte=self.cutoff,
                status='completed'
            ).count()

            # Triggers are event-driven, so we check if any have fired
            # If there are active triggers but none have fired, it's a warning
            if active_triggers == 0:
                score = 50  # No triggers configured
                message = "No active triggers configured"
            elif recent_fires == 0:
                score = 40  # Triggers exist but none fired
                message = f"{active_triggers} active triggers, 0 fires in {self.lookback_hours}h"
            else:
                # Some fires is good
                score = min(100, 50 + (recent_fires * 5))
                message = f"{recent_fires} triggers fired in {self.lookback_hours}h"

            pending = TriggerEvent.objects.filter(status='pending').count()
            failed = TriggerEvent.objects.filter(
                processed_at__gte=self.cutoff,
                status='failed'
            ).count()

            issues = []
            if pending > 10:
                issues.append(f"{pending} pending trigger events")
            if failed > 0:
                issues.append(f"{failed} failed trigger events")

            self.checks.append(SystemCheck(
                name="Triggers",
                score=score,
                status=self.get_status(score),
                message=message,
                metrics={
                    "active_triggers": active_triggers,
                    "recent_fires": recent_fires,
                    "pending": pending,
                    "failed": failed
                },
                issues=issues
            ))
        except Exception as e:
            logger.exception("Trigger check failed")
            self.checks.append(SystemCheck(
                name="Triggers",
                score=0,
                status="critical",
                message=f"Check failed: {str(e)}",
                issues=[str(e)]
            ))

    def check_learning_loops(self):
        """Check if agents are learning from each other"""
        try:
            from core.models_unified_system import KnowledgeTransfer

            # Note: AgentLearning model exists but is unused - learning uses KnowledgeTransfer
            recent_transfers = KnowledgeTransfer.objects.filter(
                created_at__gte=self.cutoff
            ).count()

            applied_transfers = KnowledgeTransfer.objects.filter(
                created_at__gte=self.cutoff,
                was_applied=True
            ).count()

            # Expected: ~10 min cycle = 6 per hour, each creates ~1-3 transfers
            # So in 6h we expect ~10-20 transfers minimum
            expected_min = self.lookback_hours * 2  # At least 2 per hour
            activity_ratio = min(1.0, recent_transfers / max(1, expected_min))

            progress_ratio = applied_transfers / max(1, recent_transfers) if recent_transfers > 0 else 0.5

            score = self.calculate_score(activity_ratio=activity_ratio, progress_ratio=progress_ratio)

            issues = []
            if recent_transfers == 0:
                issues.append("No learning activity detected")

            self.checks.append(SystemCheck(
                name="Learning Loops",
                score=score,
                status=self.get_status(score),
                message=f"{recent_transfers} transfers in {self.lookback_hours}h",
                metrics={
                    "recent_transfers": recent_transfers,
                    "applied_transfers": applied_transfers
                },
                issues=issues
            ))
        except Exception as e:
            logger.exception("Learning loops check failed")
            self.checks.append(SystemCheck(
                name="Learning Loops",
                score=0,
                status="critical",
                message=f"Check failed: {str(e)}",
                issues=[str(e)]
            ))

    def check_dreams_pipeline(self):
        """Check if agent dreams are being generated and addressed"""
        try:
            from core.models_unified_system import AgentDream

            # Try to import DreamImplementation if it exists
            try:
                from core.models_unified_system import DreamImplementation
                has_implementation = True
            except ImportError:
                has_implementation = False

            dreams_generated = AgentDream.objects.filter(
                dreamed_at__gte=self.cutoff
            ).count()

            dreams_promoted = AgentDream.objects.filter(
                dreamed_at__gte=self.cutoff,
                promoted_to_decision=True
            ).count()

            dreams_decided = AgentDream.objects.filter(
                dreamed_at__gte=self.cutoff,
                decision_outcome__in=['approved', 'deferred', 'rejected']
            ).count()

            # Expected: ~15 min cycle = ~24 dreams per 6h
            expected_dreams = self.lookback_hours * 4
            activity_ratio = min(1.0, dreams_generated / max(1, expected_dreams))

            # Progress: expect ~10% promotion rate as healthy (not all dreams should be promoted)
            # Dreams are ideas - a 10% promotion rate indicates good filtering
            if dreams_generated > 10:
                promotion_rate = dreams_promoted / dreams_generated
                expected_promotion_rate = 0.10  # 10% is healthy
                progress_ratio = min(1.0, promotion_rate / expected_promotion_rate)
            else:
                progress_ratio = 0.5  # Not enough data

            score = self.calculate_score(activity_ratio=activity_ratio, progress_ratio=progress_ratio)

            issues = []
            if dreams_generated == 0:
                issues.append("No dreams generated")
            elif dreams_promoted == 0 and dreams_generated > 10:
                issues.append("Dreams generated but none promoted")

            pending_dreams = AgentDream.objects.filter(
                promoted_to_decision=True,
                decision_outcome='pending'
            ).count()
            if pending_dreams > 20:
                issues.append(f"{pending_dreams} dreams awaiting decision")

            metrics = {
                "generated": dreams_generated,
                "promoted": dreams_promoted,
                "decided": dreams_decided,
                "pending": pending_dreams
            }

            if has_implementation:
                implemented = DreamImplementation.objects.filter(
                    created_at__gte=self.cutoff,
                    status='completed'
                ).count()
                metrics["implemented"] = implemented

            self.checks.append(SystemCheck(
                name="Dreams Pipeline",
                score=score,
                status=self.get_status(score),
                message=f"{dreams_generated} dreams, {dreams_promoted} promoted in {self.lookback_hours}h",
                metrics=metrics,
                issues=issues
            ))
        except Exception as e:
            logger.exception("Dreams pipeline check failed")
            self.checks.append(SystemCheck(
                name="Dreams Pipeline",
                score=0,
                status="critical",
                message=f"Check failed: {str(e)}",
                issues=[str(e)]
            ))

    def check_boardroom(self):
        """Check if boardroom decisions are being made"""
        try:
            from core.models_conversation_artifacts import ReviewDocument, ExtractedArtifact

            pending_reviews = ReviewDocument.objects.filter(
                status='awaiting_human'
            ).count()

            recent_decisions = ReviewDocument.objects.filter(
                decided_at__gte=self.cutoff,
                status__in=['approved', 'approved_with_conditions', 'declined', 'deferred']
            ).count()

            total_reviews = ReviewDocument.objects.filter(
                created_at__gte=self.cutoff
            ).count()

            # Artifacts extracted (uses extracted_at, not created_at)
            recent_artifacts = ExtractedArtifact.objects.filter(
                extracted_at__gte=self.cutoff
            ).count()

            approved_artifacts = ExtractedArtifact.objects.filter(
                extracted_at__gte=self.cutoff,
                status='approved'
            ).count()

            # Activity: are reviews being created?
            activity_ratio = min(1.0, total_reviews / max(1, self.lookback_hours))

            # Progress: are decisions being made?
            if pending_reviews > 0 and recent_decisions == 0:
                progress_ratio = 0.3  # Backlog growing
            elif recent_decisions > 0:
                progress_ratio = min(1.0, recent_decisions / max(1, pending_reviews + recent_decisions))
            else:
                progress_ratio = 0.5  # No pending, no decisions = neutral

            # Health: is backlog manageable?
            health_ratio = max(0, 1.0 - (pending_reviews / 50))  # Penalty for large backlog

            score = self.calculate_score(
                activity_ratio=activity_ratio,
                progress_ratio=progress_ratio,
                health_ratio=health_ratio
            )

            issues = []
            if pending_reviews > 10:
                issues.append(f"{pending_reviews} decisions awaiting human review")
            if recent_decisions == 0 and pending_reviews > 0:
                issues.append("No decisions made despite pending reviews")

            self.checks.append(SystemCheck(
                name="Boardroom",
                score=score,
                status=self.get_status(score),
                message=f"{recent_decisions} decisions, {pending_reviews} pending",
                metrics={
                    "pending_reviews": pending_reviews,
                    "recent_decisions": recent_decisions,
                    "total_reviews": total_reviews,
                    "recent_artifacts": recent_artifacts,
                    "approved_artifacts": approved_artifacts
                },
                issues=issues
            ))
        except Exception as e:
            logger.exception("Boardroom check failed")
            self.checks.append(SystemCheck(
                name="Boardroom",
                score=0,
                status="critical",
                message=f"Check failed: {str(e)}",
                issues=[str(e)]
            ))

    def check_thinking_agent(self):
        """Check if ThinkingAgent is running its cycles"""
        try:
            from core.models_unified_system import ThoughtRecord

            # Check ThoughtRecord directly (TaskResult stores to Redis)
            thinking_runs = ThoughtRecord.objects.filter(
                started_at__gte=self.cutoff,
                execution_status='completed'
            ).count()

            failed_runs = ThoughtRecord.objects.filter(
                started_at__gte=self.cutoff,
                execution_status='failed'
            ).count()

            # Expected: 1 per hour = lookback_hours runs
            expected_runs = self.lookback_hours
            activity_ratio = min(1.0, thinking_runs / max(1, expected_runs))

            health_ratio = 1.0 - (failed_runs / max(1, thinking_runs + failed_runs))

            score = self.calculate_score(activity_ratio=activity_ratio, health_ratio=health_ratio)

            issues = []
            if thinking_runs == 0:
                issues.append("No ThinkingAgent cycles completed")
            if failed_runs > 0:
                issues.append(f"{failed_runs} ThinkingAgent cycles failed")

            self.checks.append(SystemCheck(
                name="ThinkingAgent",
                score=score,
                status=self.get_status(score),
                message=f"{thinking_runs} cycles completed in {self.lookback_hours}h",
                metrics={
                    "successful_runs": thinking_runs,
                    "failed_runs": failed_runs,
                    "expected_runs": expected_runs
                },
                issues=issues
            ))
        except Exception as e:
            logger.exception("ThinkingAgent check failed")
            self.checks.append(SystemCheck(
                name="ThinkingAgent",
                score=0,
                status="critical",
                message=f"Check failed: {str(e)}",
                issues=[str(e)]
            ))

    def check_agent_conversations(self):
        """Check if agent conversations are happening"""
        try:
            from core.models_unified_system import HiveMindSession, AgentConversation

            recent_hive_minds = HiveMindSession.objects.filter(
                created_at__gte=self.cutoff,
                status='completed'
            ).count()

            recent_conversations = AgentConversation.objects.filter(
                started_at__gte=self.cutoff
            ).count()

            # Expected: ~30 min cycle = ~12 per 6h
            expected = self.lookback_hours * 2
            activity_ratio = min(1.0, (recent_hive_minds + recent_conversations) / max(1, expected))

            score = self.calculate_score(activity_ratio=activity_ratio)

            issues = []
            if recent_hive_minds == 0 and recent_conversations == 0:
                issues.append("No agent conversations detected")

            self.checks.append(SystemCheck(
                name="Agent Conversations",
                score=score,
                status=self.get_status(score),
                message=f"{recent_hive_minds} hive minds, {recent_conversations} conversations in {self.lookback_hours}h",
                metrics={
                    "hive_minds": recent_hive_minds,
                    "conversations": recent_conversations
                },
                issues=issues
            ))
        except Exception as e:
            logger.exception("Agent conversations check failed")
            self.checks.append(SystemCheck(
                name="Agent Conversations",
                score=0,
                status="critical",
                message=f"Check failed: {str(e)}",
                issues=[str(e)]
            ))

    def check_spider_network(self):
        """Check if spiders are collecting data"""
        try:
            from core.models_unified_system import SpiderData

            recent_data = SpiderData.objects.filter(
                created_at__gte=self.cutoff
            ).count()

            unique_spiders = SpiderData.objects.filter(
                created_at__gte=self.cutoff
            ).values('spider_name').distinct().count()

            # Expected: 77 spiders, ~15 min cycles = lots of data
            expected_spiders = 50  # Not all spiders run every cycle
            activity_ratio = min(1.0, unique_spiders / expected_spiders)

            # Data volume check
            expected_data = self.lookback_hours * 100  # ~100 items per hour
            data_ratio = min(1.0, recent_data / max(1, expected_data))

            score = self.calculate_score(
                activity_ratio=activity_ratio,
                progress_ratio=data_ratio
            )

            issues = []
            if unique_spiders < 30:
                issues.append(f"Only {unique_spiders}/77 spiders active")
            if recent_data == 0:
                issues.append("No spider data collected")

            self.checks.append(SystemCheck(
                name="Spider Network",
                score=score,
                status=self.get_status(score),
                message=f"{unique_spiders} spiders, {recent_data} items in {self.lookback_hours}h",
                metrics={
                    "unique_spiders": unique_spiders,
                    "total_spiders": 77,
                    "data_items": recent_data
                },
                issues=issues
            ))
        except Exception as e:
            logger.exception("Spider network check failed")
            self.checks.append(SystemCheck(
                name="Spider Network",
                score=0,
                status="critical",
                message=f"Check failed: {str(e)}",
                issues=[str(e)]
            ))

    def check_pilots_gates(self):
        """Check if pilots and gates are being processed"""
        try:
            from django.db.utils import ProgrammingError

            # Try to import the models
            try:
                from core.models_pilot_readiness import PilotReadinessGate, PilotExecution, Experiment
            except ImportError:
                self.checks.append(SystemCheck(
                    name="Pilots/Gates",
                    score=50,
                    status="warning",
                    message="Pilots system not installed",
                    metrics={},
                    issues=["PilotReadinessGate models not found"]
                ))
                return

            # Check if tables exist by catching the ProgrammingError
            try:
                pending_gates = PilotReadinessGate.objects.filter(status='pending').count()
            except ProgrammingError:
                # Tables don't exist yet
                self.checks.append(SystemCheck(
                    name="Pilots/Gates",
                    score=50,
                    status="warning",
                    message="Pilots tables not migrated yet",
                    metrics={},
                    issues=["Run migrations for pilot_readiness models"]
                ))
                return

            approved_gates = PilotReadinessGate.objects.filter(
                gate_approved_at__gte=self.cutoff
            ).count()

            # Pilots
            running_pilots = PilotExecution.objects.filter(status='running').count()
            completed_pilots = PilotExecution.objects.filter(
                completed_at__gte=self.cutoff
            ).count()

            # Experiments
            active_experiments = Experiment.objects.filter(status='active').count()

            # Activity: gates being processed
            activity_ratio = min(1.0, approved_gates / max(1, self.lookback_hours))

            # Progress: pilots completing
            if running_pilots > 0:
                progress_ratio = min(1.0, completed_pilots / max(1, running_pilots / 10))
            else:
                progress_ratio = 0.5

            # Health: not too many stuck
            if pending_gates > 100:
                health_ratio = 0.5
            else:
                health_ratio = 1.0

            score = self.calculate_score(
                activity_ratio=activity_ratio,
                progress_ratio=progress_ratio,
                health_ratio=health_ratio
            )

            issues = []
            if pending_gates > 50:
                issues.append(f"{pending_gates} gates pending approval")
            if running_pilots > 200 and completed_pilots == 0:
                issues.append("Many pilots running but none completing")

            self.checks.append(SystemCheck(
                name="Pilots/Gates",
                score=score,
                status=self.get_status(score),
                message=f"{running_pilots} pilots running, {completed_pilots} completed in {self.lookback_hours}h",
                metrics={
                    "pending_gates": pending_gates,
                    "approved_gates": approved_gates,
                    "running_pilots": running_pilots,
                    "completed_pilots": completed_pilots,
                    "active_experiments": active_experiments
                },
                issues=issues
            ))
        except Exception as e:
            logger.exception("Pilots/Gates check failed")
            self.checks.append(SystemCheck(
                name="Pilots/Gates",
                score=0,
                status="critical",
                message=f"Check failed: {str(e)}",
                issues=[str(e)]
            ))

    def compile_results(self) -> Dict[str, Any]:
        """Compile all check results into a summary"""
        if not self.checks:
            return {
                "timestamp": self.now.isoformat(),
                "lookback_hours": self.lookback_hours,
                "overall_score": 0,
                "overall_status": "critical",
                "systems": [],
                "issues": ["No checks completed"]
            }

        # Calculate overall score
        total_score = sum(check.score for check in self.checks)
        overall_score = total_score // len(self.checks)

        # Collect all issues
        all_issues = []
        for check in self.checks:
            for issue in check.issues:
                all_issues.append(f"{check.name}: {issue}")

        # Determine overall status
        critical_count = sum(1 for c in self.checks if c.status == "critical")
        warning_count = sum(1 for c in self.checks if c.status == "warning")

        if critical_count > 2:
            overall_status = "critical"
        elif critical_count > 0 or warning_count > 3:
            overall_status = "warning"
        else:
            overall_status = "healthy"

        return {
            "timestamp": self.now.isoformat(),
            "lookback_hours": self.lookback_hours,
            "overall_score": overall_score,
            "overall_status": overall_status,
            "systems": [
                {
                    "name": check.name,
                    "score": check.score,
                    "status": check.status,
                    "message": check.message,
                    "metrics": check.metrics,
                    "issues": check.issues
                }
                for check in self.checks
            ],
            "issues": all_issues,
            "summary": {
                "healthy": sum(1 for c in self.checks if c.status == "healthy"),
                "warning": warning_count,
                "critical": critical_count
            }
        }
