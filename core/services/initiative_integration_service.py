"""
Initiative Integration Service - Session 847

Wires ThinkingAgent outputs to the Initiative 5-stage pipeline.
This is the "missing middle" that connects autonomous actions to structured projects.

Key Functions:
1. Auto-create Initiatives when ThinkingAgent triggers actions
2. Auto-link documents (SelfBlog, Deliverable) to Initiative stages
3. Stage promotion state machine
4. Initiative health tracking

Stage Mapping:
- Stage 1 (Research Brief): research_brief, research, investigation
- Stage 2 (Prototype Plan): prototype_plan, prototype, design_doc
- Stage 3 (Evaluation Protocol): evaluation, audit, assessment, gate
- Stage 4 (Technical Design): technical_document, specification, architecture
- Stage 5 (Pilot Execution): pilot, blog, report, postmortem

ChatGPT Feedback (Session 847):
"You're missing the middle. ThinkingAgent -> Initiative (Project) -> Stages (1-5) -> Documents -> Actions"
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)

# Session 996: Map programs to default owner agents for auto-assignment
PROGRAM_OWNER_MAP = {
    'content_pipeline': 'ContentStrategyAgent',
    'growth_intelligence': 'MarketIntelligenceAgent',
    'monetization': 'OpportunityScoringAgent',
    'platform_health': 'SystemIntelligenceAgent',
    'ai_capabilities': 'ThinkingAgent',
    'infrastructure': 'DevOpsAgent',
    'research': 'ResearchAgent',
    'experiments': 'ResearchAgent',
}


class InitiativeCreationBlocked(Exception):
    """Session 994: Raised when circuit breaker blocks initiative creation."""
    pass


# Stage mapping based on document category/type
CATEGORY_TO_STAGE = {
    # Stage 1 - Research Brief
    'research_brief': 1,
    'research': 1,
    'investigation': 1,
    'discovery': 1,
    'market_research': 1,

    # Stage 2 - Prototype Plan
    'prototype_plan': 1,  # Note: SelfBlog category is 'prototype_plan' but maps to Stage 2
    'prototype': 2,
    'design_doc': 2,
    'proposal': 2,
    'planning': 2,

    # Stage 3 - Evaluation Protocol
    'evaluation': 3,
    'audit': 3,
    'assessment': 3,
    'gate': 3,
    'review': 3,

    # Stage 4 - Technical Design
    'technical_document': 4,
    'specification': 4,
    'architecture': 4,
    'implementation': 4,

    # Stage 5 - Pilot Execution
    'pilot': 5,
    'blog': 5,
    'report': 5,
    'postmortem': 5,
    'execution': 5,
}

# Fix the Stage 2 mapping (SelfBlog uses 'prototype_plan' as category)
CATEGORY_TO_STAGE['prototype_plan'] = 2


class InitiativeIntegrationService:
    """
    Service to integrate ThinkingAgent outputs with the Initiative pipeline.

    This creates the "project spine" that organizes floating documents
    into a coherent 5-stage workflow.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_or_create_initiative(
        self,
        topic: str,
        description: str = "",
        source_decision_id: str = None,
        created_by: str = "ThinkingAgent",
        bypass_circuit_breaker: bool = False,
    ) -> Tuple['Initiative', bool]:
        """
        Get or create an Initiative for a given topic.

        This is the core method that ensures every autonomous action
        has an associated Initiative to track its lifecycle.

        Session 994: Circuit breaker enforced at this layer so no caller can bypass it.
        Exception: bypass_circuit_breaker=True for explicit human-initiated creation via PA.

        Args:
            topic: The topic/name for the initiative
            description: Optional description
            source_decision_id: Optional ID of the decision that triggered this
            created_by: Who/what created this initiative
            bypass_circuit_breaker: If True, skip circuit breaker (for human PA requests)

        Returns:
            Tuple of (Initiative, created_bool)

        Raises:
            InitiativeCreationBlocked: When circuit breaker is tripped
        """
        from core.models_document_registry import Initiative

        # Normalize topic name
        normalized_topic = self._normalize_topic(topic)

        try:
            # Check if initiative already exists (always allowed — no creation)
            existing = Initiative.objects.filter(name=normalized_topic).first()
            if existing:
                self.logger.info(f"[Session 847] Found existing Initiative: {normalized_topic}")
                return existing, False

            # Session 1020: Similarity dedup — catch near-duplicates that differ in wording
            from core.services.initiative_circuit_breaker import find_similar_initiative
            similar = find_similar_initiative(normalized_topic)
            if similar:
                self.logger.info(
                    f"[Session 1020] Similar initiative found for '{normalized_topic[:40]}' "
                    f"→ reusing '{similar.name[:40]}'"
                )
                return similar, False

            # Session 994: Circuit breaker at the lowest creation layer.
            # bypass_circuit_breaker=True for explicit human-initiated PA creation.
            from core.services.initiative_circuit_breaker import can_create_initiative
            if not can_create_initiative(bypass_check=bypass_circuit_breaker):
                self.logger.warning(
                    f"[Session 994] Circuit breaker BLOCKED initiative creation: "
                    f"'{normalized_topic[:60]}' (source: {created_by})"
                )
                raise InitiativeCreationBlocked(
                    f"Initiative creation blocked by circuit breaker (source: {created_by})"
                )

            # Session 994: Auto-created initiatives land in TRIAGE, not ACTIVE.
            # Only human-confirmed or manually promoted initiatives become ACTIVE.
            initiative = Initiative.objects.create(
                name=normalized_topic,
                description=description or f"Auto-created initiative for: {topic}",
                created_by=created_by,
                parent_topic=topic,
                source_decision_id=source_decision_id,
                status=Initiative.Status.TRIAGE,
                current_stage=1,
            )

            # Session 1003: Auto-set founder intent so auto-progression works
            initiative.set_founder_intent(
                execution_speed='balanced',
                risk_tolerance='balanced',
                set_by='system_auto'
            )

            self.logger.info(f"[Session 847] Created new Initiative: {normalized_topic}")
            # Initialize all 5 stages
            self._initialize_stages(initiative)
            # Session 996: Auto-assign owner
            self._auto_assign_owner(initiative)

            # Session 1016: Auto-link to signal cluster
            try:
                from core.services.initiative_signal_linker import auto_link_initiative_signals
                auto_link_initiative_signals(initiative)
            except Exception as e:
                self.logger.debug(f"Signal auto-link skipped: {e}")

            return initiative, True

        except InitiativeCreationBlocked:
            raise
        except Exception as e:
            self.logger.error(f"[Session 847] Error creating initiative for '{topic}': {e}")
            raise

    def _normalize_topic(self, topic: str) -> str:
        """
        Normalize a topic string for Initiative naming.

        Removes common prefixes, trims length, and standardizes format.
        """
        # Remove common prefixes
        prefixes_to_remove = [
            '[Report]', '[Research]', '[Stage 1 -', '[Stage 2 -', '[Stage 3 -',
            '[Stage 4 -', '[Stage 5 -', 'Auto-', 'Autonomous ', 'Investigation:',
            'Research:', 'Report:', 'Analysis:'
        ]

        normalized = topic
        for prefix in prefixes_to_remove:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):].strip()

        # Also handle prefixes like "[Stage 1 - Research Brief]"
        import re
        normalized = re.sub(r'^\[Stage \d+ - [^\]]+\]\s*', '', normalized)

        # Trim to reasonable length
        if len(normalized) > 150:
            normalized = normalized[:147] + '...'

        return normalized.strip()

    def _auto_assign_owner(self, initiative) -> None:
        """
        Session 996: Auto-assign owner_agent based on program or created_by.

        Rules:
        1. If program is set and not 'uncategorized' → use PROGRAM_OWNER_MAP
        2. Else if created_by looks like an agent name → use created_by
        3. Otherwise leave unowned
        """
        if initiative.owner_id or initiative.owner_agent:
            return  # Already has an owner

        program = getattr(initiative, 'program', '') or ''
        if program and program != 'uncategorized' and program in PROGRAM_OWNER_MAP:
            initiative.owner_agent = PROGRAM_OWNER_MAP[program]
            initiative.save(update_fields=['owner_agent'])
            self.logger.info(
                f"[Session 996] Auto-assigned owner_agent={initiative.owner_agent} "
                f"for initiative '{initiative.name}' (program={program})"
            )
            return

        created_by = getattr(initiative, 'created_by', '') or ''
        skip_names = {'system', 'pa', 'human', 'admin', ''}
        if created_by.lower() not in skip_names and not created_by.startswith('HiveMind:'):
            initiative.owner_agent = created_by
            initiative.save(update_fields=['owner_agent'])
            self.logger.info(
                f"[Session 996] Auto-assigned owner_agent={created_by} "
                f"for initiative '{initiative.name}' (from created_by)"
            )
            return

        # Session 1037: Fallback — assign ResearchAgent if still unowned
        if not initiative.owner_agent:
            initiative.owner_agent = 'ResearchAgent'
            initiative.save(update_fields=['owner_agent'])
            self.logger.info(
                f"[Session 1037] Fallback owner_agent=ResearchAgent "
                f"for initiative '{initiative.name}' (created_by={created_by})"
            )

    def _initialize_stages(self, initiative: 'Initiative') -> None:
        """
        Initialize all 5 stages for a new Initiative.

        Creates placeholder InitiativeStage records in PENDING status.

        Session 915: Also triggers Stage 1 document generation automatically.
        """
        from core.models_document_registry import InitiativeStage

        for stage_num in range(1, 6):
            InitiativeStage.objects.get_or_create(
                initiative=initiative,
                stage=stage_num,
                defaults={
                    'status': InitiativeStage.StageStatus.PENDING,
                }
            )

        self.logger.info(f"[Session 847] Initialized 5 stages for Initiative: {initiative.name}")

        # Session 915: Trigger Stage 1 document generation
        # This ensures all new initiatives get their Research Brief created automatically
        try:
            from core.tasks import generate_initiative_stage_document
            task = generate_initiative_stage_document.delay(str(initiative.id), 1)
            self.logger.info(f"[Session 915] Triggered Stage 1 document generation for {initiative.name}: task {task.id}")
        except Exception as e:
            # Don't fail initiative creation if task scheduling fails
            self.logger.warning(f"[Session 915] Could not trigger Stage 1 generation for {initiative.name}: {e}")

    def link_document_to_stage(
        self,
        document: 'SelfBlog',
        initiative: 'Initiative' = None,
        topic: str = None,
        force_stage: int = None
    ) -> Optional['InitiativeStage']:
        """
        Link a SelfBlog document to the appropriate Initiative stage.

        Auto-detects the stage from document category or stats_snapshot.

        Args:
            document: The SelfBlog to link
            initiative: Optional - specific initiative to link to
            topic: Optional - topic to find/create initiative for
            force_stage: Optional - force link to specific stage

        Returns:
            The InitiativeStage that was linked, or None if failed
        """
        from core.models_document_registry import Initiative, InitiativeStage

        try:
            # Get or create the initiative
            if not initiative:
                # Try to extract topic from document
                if not topic:
                    topic = self._extract_topic_from_document(document)

                if not topic:
                    self.logger.warning(f"[Session 847] Cannot determine topic for document: {document.id}")
                    return None

                initiative, _ = self.get_or_create_initiative(topic)

            # Determine the stage
            stage_num = force_stage or self._determine_stage(document)

            # Get or create the stage record
            stage, stage_created = InitiativeStage.objects.get_or_create(
                initiative=initiative,
                stage=stage_num,
                defaults={'status': InitiativeStage.StageStatus.PENDING}
            )

            # Session 860: Check if stage already has a document
            old_document_id = stage.document_id
            if old_document_id and old_document_id != document.id:
                self.logger.info(
                    f"[Session 860] Replacing existing document {old_document_id} "
                    f"with {document.id} for Stage {stage_num}"
                )

            # Link the document
            stage.document = document
            # Session 860: Don't downgrade status if stage was already APPROVED
            if stage.status != InitiativeStage.StageStatus.APPROVED:
                stage.status = InitiativeStage.StageStatus.DRAFT
            stage.save()

            self.logger.info(
                f"[Session 847] Linked document '{document.title[:50]}' "
                f"to Initiative '{initiative.name}' Stage {stage_num}"
            )

            # Update initiative's current stage if needed
            self._update_initiative_current_stage(initiative)

            return stage

        except Exception as e:
            self.logger.error(f"[Session 847] Error linking document: {e}")
            return None

    def _extract_topic_from_document(self, document: 'SelfBlog') -> Optional[str]:
        """
        Extract the topic/initiative name from a SelfBlog document.

        Looks at stats_snapshot.parent_topic first, then title.
        """
        # Check stats_snapshot for parent_topic
        if document.stats_snapshot:
            parent_topic = document.stats_snapshot.get('parent_topic')
            if parent_topic:
                return parent_topic

        # Fall back to title
        return self._normalize_topic(document.title)

    def _determine_stage(self, document: 'SelfBlog') -> int:
        """
        Determine which stage a document belongs to.

        Priority:
        1. stats_snapshot.stage (explicitly set during creation)
        2. Document category mapping
        3. Title pattern matching
        4. Default to Stage 5 (report/output)
        """
        # Check explicit stage in stats_snapshot
        if document.stats_snapshot:
            explicit_stage = document.stats_snapshot.get('stage')
            if explicit_stage and isinstance(explicit_stage, int):
                return explicit_stage

        # Check category mapping
        category = document.category.lower() if document.category else ''
        if category in CATEGORY_TO_STAGE:
            return CATEGORY_TO_STAGE[category]

        # Check title for stage hints
        title_lower = document.title.lower()
        for keyword, stage in CATEGORY_TO_STAGE.items():
            if keyword in title_lower:
                return stage

        # Default to Stage 5 (execution/output)
        return 5

    def _update_initiative_current_stage(self, initiative: 'Initiative') -> None:
        """
        Update the initiative's current_stage based on linked documents.

        The current stage is the highest stage with a linked document,
        or the next stage after the highest approved stage.
        """
        from core.models_document_registry import InitiativeStage
        from django.db.models import Max

        # Find highest stage with a document
        stages_with_docs = initiative.stages.filter(document__isnull=False)
        max_with_doc = stages_with_docs.aggregate(Max('stage'))['stage__max'] or 0

        # Find highest approved stage
        approved_stages = initiative.stages.filter(status=InitiativeStage.StageStatus.APPROVED)
        max_approved = approved_stages.aggregate(Max('stage'))['stage__max'] or 0

        # Current stage is the higher of: max with doc, or next after approved
        new_current = max(max_with_doc, max_approved + 1, 1)
        new_current = min(new_current, 5)  # Cap at 5

        if initiative.current_stage != new_current:
            initiative.current_stage = new_current
            initiative.save()
            self.logger.info(f"[Session 847] Updated Initiative '{initiative.name}' current_stage to {new_current}")

    def promote_stage(
        self,
        initiative: 'Initiative',
        stage_num: int,
        approved_by: str = "ThinkingAgent"
    ) -> bool:
        """
        Promote a stage to APPROVED status.

        This unlocks the next stage in the pipeline.

        Args:
            initiative: The initiative
            stage_num: The stage number to approve
            approved_by: Who approved it

        Returns:
            True if promotion succeeded
        """
        from core.models_document_registry import InitiativeStage

        try:
            stage = initiative.stages.get(stage=stage_num)

            # Check if stage has a document
            if not stage.document:
                self.logger.warning(
                    f"[Session 847] Cannot promote Stage {stage_num} - no document linked"
                )
                return False

            # Approve the stage
            stage.approve(approved_by=approved_by)

            self.logger.info(
                f"[Session 847] Promoted Stage {stage_num} for Initiative '{initiative.name}'"
            )

            # Update initiative current stage
            self._update_initiative_current_stage(initiative)

            return True

        except InitiativeStage.DoesNotExist:
            self.logger.error(f"[Session 847] Stage {stage_num} not found for initiative")
            return False
        except Exception as e:
            self.logger.error(f"[Session 847] Error promoting stage: {e}")
            return False

    def auto_promote_if_ready(self, initiative: 'Initiative') -> List[int]:
        """
        Automatically promote stages that have documents and are ready.

        A stage is ready for auto-promotion if:
        - It has a linked document
        - The document is marked as approved/published
        - Previous stages are all approved

        Returns:
            List of stage numbers that were promoted
        """
        from core.models_document_registry import InitiativeStage

        promoted = []

        for stage_num in range(1, 6):
            try:
                stage = initiative.stages.get(stage=stage_num)

                # Skip if already approved
                if stage.status == InitiativeStage.StageStatus.APPROVED:
                    continue

                # Skip if no document
                if not stage.document:
                    break  # Can't skip stages

                # Check if previous stages are approved
                if stage_num > 1:
                    prev_stages_approved = initiative.stages.filter(
                        stage__lt=stage_num,
                        status=InitiativeStage.StageStatus.APPROVED
                    ).count() == stage_num - 1

                    if not prev_stages_approved:
                        break  # Can't skip stages

                # Check document status
                doc = stage.document
                if doc.status in ['approved', 'published']:
                    if self.promote_stage(initiative, stage_num, approved_by="auto_promote"):
                        promoted.append(stage_num)

            except InitiativeStage.DoesNotExist:
                break

        return promoted

    def get_initiative_health(self, initiative: 'Initiative') -> Dict[str, Any]:
        """
        Calculate health metrics for an initiative.

        Returns metrics like:
        - Completion percentage
        - Stage status summary
        - Stale indicator (no updates in X days)
        - Blocked indicator (stage stuck without docs)
        """
        from core.models_document_registry import InitiativeStage

        now = timezone.now()
        days_since_update = (now - initiative.updated_at).days

        # Count stages by status
        stages = initiative.stages.all()
        status_counts = {
            'pending': 0,
            'draft': 0,
            'in_review': 0,
            'approved': 0,
            'rejected': 0,
        }

        for stage in stages:
            status_key = stage.status.lower()
            if status_key in status_counts:
                status_counts[status_key] += 1

        # Determine health status
        health = 'healthy'
        health_issues = []

        if days_since_update > 14:
            health = 'stale'
            health_issues.append(f'No updates for {days_since_update} days')

        if status_counts['rejected'] > 0:
            health = 'blocked'
            health_issues.append(f'{status_counts["rejected"]} stage(s) rejected')

        # Check if current stage is stuck (no document for > 7 days)
        try:
            current_stage = initiative.stages.get(stage=initiative.current_stage)
            if not current_stage.document:
                stage_age = (now - current_stage.created_at).days
                if stage_age > 7:
                    health = 'blocked'
                    health_issues.append(f'Stage {initiative.current_stage} needs document')
        except initiative.stages.model.DoesNotExist:
            pass  # Stage not created yet
        except Exception as e:
            logger.warning(f"Initiative {initiative.id} stage health check failed: {e}")

        return {
            'initiative_id': str(initiative.id),
            'name': initiative.name,
            'status': initiative.status,
            'current_stage': initiative.current_stage,
            'completion_percentage': initiative.completion_percentage,
            'health': health,
            'health_issues': health_issues,
            'stage_counts': status_counts,
            'days_since_update': days_since_update,
            'updated_at': initiative.updated_at.isoformat(),
        }

    def get_all_initiatives_dashboard(self) -> Dict[str, Any]:
        """
        Get dashboard data for all initiatives.

        Returns summary stats and list of initiatives with health.
        """
        from core.models_document_registry import Initiative

        initiatives = Initiative.objects.filter(
            status__in=[Initiative.Status.ACTIVE, Initiative.Status.ON_HOLD]
        ).order_by('-updated_at')[:50]

        dashboard = {
            'total': initiatives.count(),
            'by_status': {},
            'by_health': {'healthy': 0, 'stale': 0, 'blocked': 0},
            'initiatives': [],
        }

        for init in initiatives:
            health = self.get_initiative_health(init)
            dashboard['initiatives'].append(health)

            # Count by status
            status = init.status
            dashboard['by_status'][status] = dashboard['by_status'].get(status, 0) + 1

            # Count by health
            dashboard['by_health'][health['health']] += 1

        return dashboard

    def link_action_to_initiative(
        self,
        action_type: str,
        action_params: Dict[str, Any],
        reasoning: str,
        result: Dict[str, Any]
    ) -> Optional['Initiative']:
        """
        Link an executed autonomous action to an Initiative.

        This is called from AutonomousActionExecutor after each action.

        Args:
            action_type: The type of action (request_research, create_report, etc.)
            action_params: The action parameters
            reasoning: The reasoning behind the action
            result: The result from executing the action

        Returns:
            The Initiative that was linked/created, or None
        """
        # Extract topic from action
        topic = action_params.get('topic') or action_params.get('name', '')

        if not topic:
            # Try to extract from result
            topic = result.get('topic', '')

        if not topic:
            self.logger.warning(f"[Session 847] Cannot link action {action_type} - no topic found")
            return None

        # Create/get the initiative
        # Session 994: Handle circuit breaker block gracefully
        description = f"Auto-created from {action_type} action. {reasoning[:200]}"
        try:
            initiative, created = self.get_or_create_initiative(
                topic=topic,
                description=description,
                created_by="ThinkingAgent"
            )
        except InitiativeCreationBlocked:
            self.logger.info(f"[Session 994] Circuit breaker blocked initiative for action {action_type}")
            return None

        # If a blog/document was created, link it
        blog_id = result.get('blog_id') or result.get('report_id') or result.get('research_blog_id')
        if blog_id:
            # Session 906: Force stage 1 for research actions to ensure proper linking
            force_stage = 1 if action_type == 'request_research' else None
            self._link_result_document(initiative, blog_id, action_type, force_stage=force_stage)

        # Link any synthesized deliverables
        synthesized = result.get('synthesized_deliverables', [])
        for synth in synthesized:
            if synth.get('success') and synth.get('blog_id'):
                self._link_result_document(
                    initiative,
                    synth['blog_id'],
                    'synthesized_deliverable',
                    force_stage=synth.get('stage')
                )

        return initiative

    def _link_result_document(
        self,
        initiative: 'Initiative',
        blog_id: str,
        action_type: str,
        force_stage: int = None
    ) -> None:
        """
        Link a result document to an initiative.
        """
        from core.models_unified_system import SelfBlog

        try:
            document = SelfBlog.objects.get(id=blog_id)
            self.link_document_to_stage(
                document=document,
                initiative=initiative,
                force_stage=force_stage
            )
        except SelfBlog.DoesNotExist:
            self.logger.warning(f"[Session 847] Document {blog_id} not found")
        except Exception as e:
            self.logger.error(f"[Session 847] Error linking document {blog_id}: {e}")

    def backfill_unlinked_documents(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Session 860: Backfill unlinked documents that have parent_topic.

        Finds all SelfBlog documents with parent_topic in stats_snapshot
        that are not yet linked to any InitiativeStage, and links them.

        Args:
            dry_run: If True, only report what would be done without making changes

        Returns:
            Summary of backfill results
        """
        from core.models_unified_system import SelfBlog
        from core.models_document_registry import InitiativeStage
        from django.db.models import Q

        results = {
            'total_unlinked': 0,
            'linked': [],
            'skipped': [],
            'errors': [],
            'dry_run': dry_run,
        }

        # Find documents with parent_topic that are not linked to any stage
        # Using raw SQL-style filter since stats_snapshot is JSONField
        all_docs_with_parent = SelfBlog.objects.filter(
            stats_snapshot__parent_topic__isnull=False
        ).exclude(
            stats_snapshot__parent_topic=''
        )

        # Filter out those already linked
        linked_doc_ids = InitiativeStage.objects.filter(
            document__isnull=False
        ).values_list('document_id', flat=True)

        unlinked_docs = all_docs_with_parent.exclude(id__in=linked_doc_ids)
        results['total_unlinked'] = unlinked_docs.count()

        self.logger.info(
            f"[Session 860] Found {results['total_unlinked']} unlinked documents with parent_topic"
        )

        for doc in unlinked_docs:
            parent_topic = doc.stats_snapshot.get('parent_topic')
            stage = doc.stats_snapshot.get('stage')

            try:
                if dry_run:
                    results['linked'].append({
                        'doc_id': str(doc.id),
                        'title': doc.title[:60],
                        'parent_topic': parent_topic,
                        'stage': stage,
                        'action': 'would_link'
                    })
                else:
                    result = self.link_document_to_stage(
                        document=doc,
                        topic=parent_topic,
                        force_stage=stage
                    )
                    if result:
                        results['linked'].append({
                            'doc_id': str(doc.id),
                            'title': doc.title[:60],
                            'parent_topic': parent_topic,
                            'stage': stage,
                            'action': 'linked'
                        })
                    else:
                        results['skipped'].append({
                            'doc_id': str(doc.id),
                            'title': doc.title[:60],
                            'reason': 'link_document_to_stage returned None'
                        })

            except Exception as e:
                self.logger.error(f"[Session 860] Error backfilling document {doc.id}: {e}")
                results['errors'].append({
                    'doc_id': str(doc.id),
                    'title': doc.title[:60],
                    'error': str(e)
                })

        self.logger.info(
            f"[Session 860] Backfill {'preview' if dry_run else 'complete'}: "
            f"{len(results['linked'])} linked, {len(results['skipped'])} skipped, "
            f"{len(results['errors'])} errors"
        )

        return results


# Singleton instance
_initiative_service = None

def get_initiative_integration_service() -> InitiativeIntegrationService:
    """Get the singleton InitiativeIntegrationService instance."""
    global _initiative_service
    if _initiative_service is None:
        _initiative_service = InitiativeIntegrationService()
    return _initiative_service
