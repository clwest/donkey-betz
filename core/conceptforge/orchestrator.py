"""
ConceptForge Orchestrator
=========================

Session 863: Orchestrates the ConceptForge pipeline execution.

Responsibilities:
1. Gate validation (quality_score, strategic_tags)
2. Domain routing (determine which lab handles content)
3. Panel selection and snapshot
4. Stage execution coordination
5. Artifact creation (dossier)

Key design:
- Legendary advisors provide CONSTRAINTS (debate positions, risk framing)
- Core agents do the WRITING (citations, structure)
- All inputs/outputs are snapshotted for reproducibility
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from django.utils import timezone
from django.db import transaction

from .labs import (
    DOMAIN_LABS,
    get_lab_config,
    get_lab_for_tags,
    get_stage_names,
    LabConfig,
    StageConfig,
)
from .panels import (
    select_panel_for_domain,
    get_debate_positions,
    get_advisor_wisdom,
)

logger = logging.getLogger(__name__)


class ConceptForgeOrchestrator:
    """
    Main orchestrator for ConceptForge pipeline execution.

    Usage:
        orchestrator = ConceptForgeOrchestrator()

        # Check if content qualifies for ConceptForge
        if orchestrator.should_trigger(blog):
            run = orchestrator.start_pipeline(
                source_type='blog',
                source_id=blog.id,
                source_title=blog.title,
                domain='legal',  # or auto-detect from tags
                quality_score=0.85
            )

        # Execute the pipeline (usually done async via Celery)
        orchestrator.execute_run(run)
    """

    # Gate thresholds
    MIN_QUALITY_SCORE = 0.80
    STRATEGIC_TAGS = [
        'legal-tech', 'legal', 'policy', 'regulation',
        'market', 'investment', 'trading', 'finance',
        'tech', 'ai', 'product', 'saas',
        'startup', 'venture', 'funding',
        'content', 'marketing', 'media',
        'career', 'jobs', 'skills',
    ]

    def __init__(self, user=None):
        """
        Initialize orchestrator.

        Args:
            user: Optional user for permission context
        """
        self.user = user

    def should_trigger(
        self,
        quality_score: float,
        tags: Optional[List[str]] = None,
        force: bool = False
    ) -> tuple:
        """
        Check if content should trigger ConceptForge pipeline.

        Returns:
            Tuple of (should_trigger: bool, reason: str, domain: str or None)
        """
        if force:
            domain = get_lab_for_tags(tags or [])
            return True, 'forced', domain or 'tech'

        # Check quality score
        if quality_score < self.MIN_QUALITY_SCORE:
            return False, f'quality_score {quality_score:.2f} < {self.MIN_QUALITY_SCORE}', None

        # Determine domain from tags if available
        domain = get_lab_for_tags(tags or [])

        # If tags match a strategic tag, use that domain
        if tags:
            tags_lower = [t.lower() for t in tags]
            has_strategic_tag = any(
                tag in self.STRATEGIC_TAGS
                for tag in tags_lower
            )
            if has_strategic_tag and domain:
                return True, 'qualifies', domain

        # Quality alone is sufficient — default to 'tech' domain if no tags match
        return True, 'qualifies_by_quality', domain or 'tech'

    def start_pipeline(
        self,
        source_type: str,
        source_id: str,
        source_title: str,
        domain: str,
        quality_score: float = 0.0,
        triggered_by: str = 'system',
        celery_task_id: str = ''
    ):
        """
        Create a new ConceptForge run.

        Args:
            source_type: Type of source content (blog, decision_summary, etc.)
            source_id: UUID of source content
            source_title: Title for display
            domain: Domain lab to use
            quality_score: Quality score of source content
            triggered_by: What triggered this run
            celery_task_id: Optional Celery task ID

        Returns:
            ConceptForgeRun instance
        """
        from core.models_conceptforge import ConceptForgeRun, ConceptForgeStageRun

        # Select and snapshot advisor panel
        panel_snapshot = select_panel_for_domain(domain)

        # Create the run
        run = ConceptForgeRun.objects.create(
            source_type=source_type,
            source_id=source_id,
            source_title=source_title,
            domain=domain,
            advisor_panel_snapshot=panel_snapshot,
            quality_score=quality_score,
            triggered_by=triggered_by,
            celery_task_id=celery_task_id,
            user=self.user,
        )

        # Pre-create stage records
        stage_names = get_stage_names()
        for i, stage_name in enumerate(stage_names, 1):
            ConceptForgeStageRun.objects.create(
                run=run,
                stage_name=stage_name,
                stage_order=i,
            )

        logger.info(f"Created ConceptForge run {run.id} for '{source_title}' in {domain}Lab")
        return run

    def execute_run(self, run) -> bool:
        """
        Execute all stages of a ConceptForge run.

        This is the main execution loop. Usually called from a Celery task.

        Args:
            run: ConceptForgeRun instance

        Returns:
            True if completed successfully, False otherwise
        """
        from core.models_conceptforge import ConceptForgeArtifact

        try:
            run.start()

            lab_config = get_lab_config(run.domain)
            if not lab_config:
                run.fail(f"No lab configuration found for domain: {run.domain}")
                return False

            # Execute each stage
            stages = run.stages.order_by('stage_order')
            previous_outputs = {}

            for stage in stages:
                logger.info(f"Executing stage: {stage.stage_name}")

                success = self._execute_stage(
                    run=run,
                    stage=stage,
                    lab_config=lab_config,
                    previous_outputs=previous_outputs,
                )

                if not success:
                    stage_config = lab_config.stages.get(stage.stage_name)
                    if stage_config and not stage_config.optional:
                        run.fail(f"Required stage '{stage.stage_name}' failed: {stage.error}")
                        return False

                # Store output for next stages
                if stage.output_text:
                    previous_outputs[stage.stage_name] = stage.output_text

            # Create the final dossier artifact
            dossier_content = self._create_dossier_content(run, previous_outputs)
            ConceptForgeArtifact.create_dossier(
                run=run,
                content=dossier_content,
                metadata={
                    'stage_count': len(previous_outputs),
                    'domain': run.domain,
                    'advisor_panel': run.advisor_panel_snapshot.get('advisors', []),
                }
            )

            run.complete()
            logger.info(f"ConceptForge run {run.id} completed successfully")
            return True

        except Exception as e:
            logger.exception(f"ConceptForge run {run.id} failed: {e}")
            run.fail(str(e))
            return False

    def _execute_stage(
        self,
        run,
        stage,
        lab_config: LabConfig,
        previous_outputs: Dict[str, str]
    ) -> bool:
        """
        Execute a single pipeline stage.

        Args:
            run: ConceptForgeRun instance
            stage: ConceptForgeStageRun instance
            lab_config: Lab configuration
            previous_outputs: Outputs from previous stages

        Returns:
            True if successful, False otherwise
        """
        stage_config = lab_config.stages.get(stage.stage_name)
        if not stage_config:
            stage.skip(f"No configuration for stage: {stage.stage_name}")
            return True  # Skip unknown stages

        try:
            stage.start()

            # Build inputs for this stage
            inputs = self._build_stage_inputs(
                run=run,
                stage=stage,
                stage_config=stage_config,
                previous_outputs=previous_outputs,
            )

            # Snapshot inputs
            stage.inputs_snapshot = inputs

            # Get persona advisor advice (if configured)
            advisor_advice = self._get_persona_advice(
                stage_config=stage_config,
                topic=run.source_title,
                context=inputs,
            )

            # For debate stage, get legendary advisor positions
            legendary_positions = None
            if stage.stage_name == 'debate':
                legendary_positions = self._get_legendary_positions(
                    run=run,
                    topic=run.source_title,
                    previous_outputs=previous_outputs,
                )
                stage.legendary_advisors_used = list(legendary_positions.keys()) if legendary_positions else []

            # Execute the core agent
            output = self._execute_agent(
                agent_name=stage_config.agent_name,
                stage_name=stage.stage_name,
                inputs=inputs,
                advisor_advice=advisor_advice,
                legendary_positions=legendary_positions,
            )

            # Update stage
            stage.agent_used = stage_config.agent_name
            stage.advisors_used = stage_config.persona_advisors

            # Session 920: Add provenance header to stage output metadata
            output_metadata = output.get('metadata', {})
            quality_score = run.quality_score or 0.0
            provenance_header = {
                'generated_at': timezone.now().isoformat(),
                'generated_at_local': timezone.localtime().strftime('%Y-%m-%d %H:%M %Z'),
                'inputs_used': list(previous_outputs.keys()) + [f"source:{run.source_id}"],
                'freshness_window': '72h',
                'validation_status': 'validated' if output_metadata.get('is_valid') else 'unvalidated',
                'publishable': quality_score >= 0.80,
            }
            output_metadata['provenance'] = provenance_header

            stage.complete(
                output_text=output.get('text', ''),
                output_metadata=output_metadata,
            )

            return True

        except Exception as e:
            logger.exception(f"Stage {stage.stage_name} failed: {e}")
            stage.fail(str(e))
            return False

    # Session 920: Invalid topic placeholders that indicate data quality issues
    INVALID_TOPICS = {'target', 'unknown', 'none', 'untitled', '[learned]', 'n/a', ''}

    def _build_stage_inputs(
        self,
        run,
        stage,
        stage_config: StageConfig,
        previous_outputs: Dict[str, str]
    ) -> Dict:
        """Build input context for a stage."""
        # Get source content
        source_content = self._get_source_content(run)

        # Session 920: Validate source_title is not a placeholder
        source_title = run.source_title or ''
        if source_title.lower().strip() in self.INVALID_TOPICS:
            logger.warning(f"Invalid panel_topic detected: '{source_title}'")
            # Attempt to auto-generate from source content if available
            if source_content and len(source_content) > 20:
                # Extract first line or first 50 chars as fallback title
                first_line = source_content.split('\n')[0].strip()
                source_title = first_line[:50] if len(first_line) > 50 else first_line
                logger.info(f"Auto-generated topic from content: '{source_title}'")
            else:
                # Last resort: use domain + timestamp
                source_title = f"{run.domain} Analysis - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                logger.info(f"Generated fallback topic: '{source_title}'")

        inputs = {
            'source_title': source_title,
            'source_content': source_content,
            'domain': run.domain,
            'stage_name': stage.stage_name,
            'advisor_panel': run.advisor_panel_snapshot,
        }

        # Add previous stage outputs
        for stage_name, output in previous_outputs.items():
            inputs[f'{stage_name}_output'] = output

        return inputs

    def _get_source_content(self, run) -> str:
        """Get the source content text."""
        try:
            if run.source_type == 'blog':
                from core.models_unified_system import SelfBlog
                blog = SelfBlog.objects.get(id=run.source_id)
                return blog.full_text or blog.intro or ''
        except Exception as e:
            logger.warning(f"Could not get source content: {e}")
        return ''

    def _get_persona_advice(
        self,
        stage_config: StageConfig,
        topic: str,
        context: Dict
    ) -> Dict[str, str]:
        """Get advice from persona agents for this stage."""
        advice = {}

        if not stage_config.persona_advisors:
            return advice

        try:
            from core.services.persona_advisor_service import PersonaAdvisorService
            service = PersonaAdvisorService()

            for persona_name in stage_config.persona_advisors:
                result = service.get_advice(
                    persona_name=persona_name,
                    topic=topic,
                    advice_type=stage_config.advice_type,
                    context=context,
                )
                if result and result.advice:
                    advice[persona_name] = result.advice

        except Exception as e:
            logger.warning(f"Failed to get persona advice: {e}")

        return advice

    def _get_legendary_positions(
        self,
        run,
        topic: str,
        previous_outputs: Dict[str, str]
    ) -> Dict[str, Dict]:
        """Get debate positions from legendary advisors."""
        positions = {}
        panel = run.advisor_panel_snapshot
        debate_info = get_debate_positions(panel)

        if not debate_info.get('pro') or not debate_info.get('con'):
            return positions

        try:
            from core.services.advisor_context_builder import AdvisorContextBuilder
            builder = AdvisorContextBuilder()

            # Get research output for context
            research = previous_outputs.get('research', '')

            # Pro position
            pro_advisor = debate_info['pro']
            pro_wisdom = get_advisor_wisdom(pro_advisor['key'])
            positions[pro_advisor['name']] = {
                'stance': 'pro',
                'frameworks': pro_advisor.get('frameworks', []),
                'style': pro_advisor.get('style', 'analytical'),
                'wisdom': pro_wisdom,
                'prompt': self._build_debate_prompt(
                    advisor_name=pro_advisor['name'],
                    stance='pro',
                    topic=topic,
                    research=research,
                    frameworks=pro_advisor.get('frameworks', []),
                ),
            }

            # Con position
            con_advisor = debate_info['con']
            con_wisdom = get_advisor_wisdom(con_advisor['key'])
            positions[con_advisor['name']] = {
                'stance': 'con',
                'frameworks': con_advisor.get('frameworks', []),
                'style': con_advisor.get('style', 'analytical'),
                'wisdom': con_wisdom,
                'prompt': self._build_debate_prompt(
                    advisor_name=con_advisor['name'],
                    stance='con',
                    topic=topic,
                    research=research,
                    frameworks=con_advisor.get('frameworks', []),
                ),
            }

        except Exception as e:
            logger.warning(f"Failed to get legendary positions: {e}")

        return positions

    def _build_debate_prompt(
        self,
        advisor_name: str,
        stance: str,
        topic: str,
        research: str,
        frameworks: List[str]
    ) -> str:
        """Build a debate prompt for a legendary advisor."""
        stance_instruction = (
            "Argue IN FAVOR of this opportunity"
            if stance == 'pro'
            else "Argue AGAINST or identify critical risks"
        )

        return f"""You are {advisor_name}, providing your perspective on:

Topic: {topic}

{stance_instruction}

Apply your key frameworks: {', '.join(frameworks)}

Research context:
{research[:2000] if research else 'No prior research available'}

Provide a structured argument (2-3 key points) in your characteristic style.
Focus on substance over length. Be specific and actionable."""

    def _execute_agent(
        self,
        agent_name: str,
        stage_name: str,
        inputs: Dict,
        advisor_advice: Optional[Dict[str, str]] = None,
        legendary_positions: Optional[Dict[str, Dict]] = None
    ) -> Dict:
        """
        Execute a core agent for a stage.

        This is where the actual LLM call happens. Core agents do the writing,
        legendary advisors provide constraints/positions injected into prompts.
        """
        try:
            # Build the prompt based on stage
            prompt = self._build_stage_prompt(
                stage_name=stage_name,
                inputs=inputs,
                advisor_advice=advisor_advice or {},
                legendary_positions=legendary_positions or {},
            )

            # Route to agent
            from core.agent_router import route_to_agent
            result = route_to_agent(
                agent_name=agent_name,
                task=prompt,
                context={
                    'stage': stage_name,
                    'domain': inputs.get('domain'),
                    'conceptforge': True,
                }
            )

            return {
                'text': result.get('response', '') if isinstance(result, dict) else str(result),
                'metadata': {
                    'agent': agent_name,
                    'stage': stage_name,
                }
            }

        except Exception as e:
            logger.exception(f"Agent execution failed: {e}")
            return {
                'text': f"Stage {stage_name} execution failed: {str(e)}",
                'metadata': {'error': str(e)}
            }

    def _build_stage_prompt(
        self,
        stage_name: str,
        inputs: Dict,
        advisor_advice: Dict[str, str],
        legendary_positions: Dict[str, Dict]
    ) -> str:
        """Build the prompt for a stage execution."""
        source_title = inputs.get('source_title', 'Unknown Topic')
        source_content = inputs.get('source_content', '')[:3000]
        domain = inputs.get('domain', 'general')

        # Stage-specific prompts
        prompts = {
            'research': f"""Conduct comprehensive research on: {source_title}

Source content:
{source_content}

Domain: {domain}Lab

Advisor input:
{self._format_advisor_advice(advisor_advice)}

Provide a research brief with:
1. Key findings from current trends
2. Relevant statistics and data
3. Expert opinions and citations
4. Gap analysis - what's missing in current solutions
5. Opportunity assessment

Be thorough but concise. Cite sources where possible.""",

            'debate': f"""Facilitate a structured debate on: {source_title}

Research context:
{inputs.get('research_output', 'No research available')}

LEGENDARY ADVISOR POSITIONS:
{self._format_legendary_positions(legendary_positions)}

As the debate facilitator:
1. Present the pro case (optimist/opportunity perspective)
2. Present the con case (skeptic/risk perspective)
3. Identify points of agreement and contention
4. Synthesize key takeaways from both sides

Maintain balance and intellectual rigor.""",

            'feasibility': f"""Assess technical feasibility for: {source_title}

Prior research:
{inputs.get('research_output', '')[:1500]}

Debate summary:
{inputs.get('debate_output', '')[:1500]}

Advisor input:
{self._format_advisor_advice(advisor_advice)}

Provide feasibility analysis:
1. Technical requirements and architecture
2. Data and API dependencies
3. Integration considerations
4. Resource and timeline estimates
5. Technical risks and mitigations

Be specific and actionable.""",

            'risk': f"""Conduct risk and compliance analysis for: {source_title}

Context from prior stages:
- Research: {inputs.get('research_output', '')[:1000]}
- Feasibility: {inputs.get('feasibility_output', '')[:1000]}

Advisor input:
{self._format_advisor_advice(advisor_advice)}

Analyze:
1. Regulatory and compliance risks
2. Legal considerations
3. Ethical implications
4. Operational risks
5. Mitigation strategies

Focus on actionable risk management.""",

            'market': f"""Conduct market and business analysis for: {source_title}

Context from prior stages:
- Research: {inputs.get('research_output', '')[:1000]}
- Feasibility: {inputs.get('feasibility_output', '')[:1000]}
- Risk: {inputs.get('risk_output', '')[:1000]}

Advisor input:
{self._format_advisor_advice(advisor_advice)}

Analyze:
1. Target market and customer segments
2. Competitive landscape
3. Business model options
4. Pricing and revenue potential
5. Go-to-market considerations

Focus on opportunity sizing and strategic positioning.""",

            'synthesis': f"""Synthesize all findings into an executive dossier for: {source_title}

=== RESEARCH FINDINGS ===
{inputs.get('research_output', '')[:1500]}

=== DEBATE SUMMARY ===
{inputs.get('debate_output', '')[:1500]}

=== FEASIBILITY ASSESSMENT ===
{inputs.get('feasibility_output', '')[:1500]}

=== RISK ANALYSIS ===
{inputs.get('risk_output', '')[:1500]}

=== MARKET ANALYSIS ===
{inputs.get('market_output', '')[:1500]}

Create an executive dossier with:
1. Executive Summary (key opportunity and recommendation)
2. Strategic Assessment (strengths, weaknesses, opportunities, threats)
3. Implementation Roadmap (phases and milestones)
4. Resource Requirements
5. Success Metrics
6. Final Recommendation (Go / No-Go / Conditional Go)

Be decisive and actionable. This is the final synthesis for decision-makers.""",
        }

        return prompts.get(stage_name, f"Execute {stage_name} analysis for: {source_title}")

    def _format_advisor_advice(self, advice: Dict[str, str]) -> str:
        """Format persona advisor advice for prompt injection."""
        if not advice:
            return "No specific advisor input."

        formatted = []
        for advisor, text in advice.items():
            formatted.append(f"**{advisor}**: {text[:500]}")

        return "\n\n".join(formatted)

    def _format_legendary_positions(self, positions: Dict[str, Dict]) -> str:
        """Format legendary advisor positions for debate prompt."""
        if not positions:
            return "No legendary advisor positions."

        formatted = []
        for name, data in positions.items():
            stance = data.get('stance', 'unknown')
            frameworks = ', '.join(data.get('frameworks', []))
            formatted.append(f"**{name}** ({stance.upper()}): Frameworks: {frameworks}")

        return "\n".join(formatted)

    def _create_dossier_content(self, run, outputs: Dict[str, str]) -> str:
        """Create the final dossier markdown content."""
        panel = run.advisor_panel_snapshot
        advisors = panel.get('advisors', [])

        dossier = f"""# Dossier: {run.source_title}

**Domain Lab:** {run.domain}Lab
**Generated:** {timezone.now().strftime('%Y-%m-%d %H:%M')}
**Advisor Panel:** {', '.join(advisors)}

---

## Executive Summary

{outputs.get('synthesis', 'Synthesis not available.')}

---

## Stage Outputs

### Research Brief
{outputs.get('research', 'Not available.')}

### Debate Summary
{outputs.get('debate', 'Not available.')}

### Feasibility Assessment
{outputs.get('feasibility', 'Not available.')}

### Risk Analysis
{outputs.get('risk', 'Not available.')}

### Market Analysis
{outputs.get('market', 'Not available.')}

---

## Pipeline Metadata

- **Source Type:** {run.source_type}
- **Quality Score:** {run.quality_score:.2f}
- **Triggered By:** {run.triggered_by}
- **Run ID:** {run.id}

---

*Generated by ConceptForge - Autonomous Think Tank Pipeline*
"""
        return dossier
