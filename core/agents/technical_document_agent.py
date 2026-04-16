"""
Technical Document Agent - Session 622
=======================================

Creates professional technical documents for the research-to-deliverable pipeline.
Unlike ContentWriterAgent (which writes blog-style content), this agent produces
formal, structured technical documents suitable for product development.

Document Types Supported:
    - research_brief: Discovery + framing document (Stage 1)
    - prototype_plan: Implementation/prototype planning (Stage 2)
    - evaluation_protocol: Pre-pilot gate with PASS/LEARN/FAIL criteria (Stage 3)
    - design_doc: Technical design specification
    - recommendations: Formal recommendations report
    - compliance_mapping: Regulatory/compliance documentation
    - testing_framework: Testing specification with cases

Key Differences from ContentWriterAgent:
    - NO blog-style phrasing ("In this blog post...")
    - Formal, professional tone throughout
    - Includes governance language and FAIL conditions
    - Stage-aware: Documents know their position in the lifecycle
    - Structured for decision-making, not engagement

Usage:
    from core.agents.technical_document_agent import TechnicalDocumentAgent
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

    agent = TechnicalDocumentAgent()
    result = agent.execute(
        task="Create evaluation protocol for AI Humanizer",
        context={
            'doc_type': 'evaluation_protocol',
            'stage': 3,
            'topic': 'AI Humanizer for podcast production',
            'research_context': '...'
        }
    )
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_document_with_ml(document_data: dict) -> dict:
    """Analyze technical document data using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=document_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'document_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML document analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


# Document stage definitions - the product development lifecycle
DOCUMENT_STAGES = {
    1: {
        'name': 'Research Brief',
        'purpose': 'Discovery + framing - Why does this matter?',
        'doc_types': ['research_brief', 'brief', 'discovery'],
        'outputs': ['problem statement', 'market signal', 'initial risk assessment', 'stakeholder impact'],
    },
    2: {
        'name': 'Prototype Plan',
        'purpose': 'Translation layer - How would we build this?',
        'doc_types': ['prototype_plan', 'implementation_plan', 'plan', 'roadmap'],
        'outputs': ['success metrics', 'tooling', 'architecture', 'pilot approach', 'risk management'],
    },
    3: {
        'name': 'Evaluation Protocol',
        'purpose': 'Pre-pilot gate - Should we proceed?',
        'doc_types': ['evaluation_protocol', 'testing_framework', 'validation', 'protocol'],
        'outputs': ['PASS criteria', 'LEARN criteria', 'FAIL criteria', 'kill switch', 'governance'],
    },
    4: {
        'name': 'Technical Design',
        'purpose': 'Implementation specification - Exactly what to build',
        'doc_types': ['design_doc', 'technical_design', 'specification', 'architecture'],
        'outputs': ['system design', 'data models', 'API contracts', 'security considerations'],
    },
    5: {
        'name': 'Compliance Mapping',
        'purpose': 'Regulatory alignment - Are we allowed to do this?',
        'doc_types': ['compliance_mapping', 'regulatory', 'compliance', 'legal'],
        'outputs': ['regulatory requirements', 'consent framework', 'audit trail', 'policy alignment'],
    },
}


# Document templates with governance language
DOCUMENT_TEMPLATES = {
    'research_brief': """## {title}

### Executive Summary
[2-3 sentence overview of the research topic and key finding]

### Problem Statement
What problem does this solve? Who experiences it? What's the cost of inaction?

### Market Signal
- What evidence suggests this matters?
- Source credibility assessment
- Confidence level: [HIGH/MEDIUM/LOW]

### Initial Risk Assessment
| Risk Category | Level | Notes |
|--------------|-------|-------|
| Technical | | |
| Market | | |
| Regulatory | | |
| Reputational | | |

### Stakeholder Impact
- Primary beneficiaries:
- Potential negative impacts:
- Internal resource requirements:

### Recommendation
[PROCEED TO PROTOTYPE PLAN / NEEDS MORE RESEARCH / ARCHIVE]

### Next Steps
If approved, the next deliverable is: Stage 2 - Prototype Plan

---
*Document Stage: 1 of 5 - Research Brief*
*Generated: {date}*
*Classification: {classification}*
""",

    'prototype_plan': """## {title}

### Purpose
This document translates research findings into an actionable prototype plan.

### Success Criteria
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| | | |

### Proposed Architecture
[High-level technical approach]

### Implementation Phases
1. **Phase 1: Foundation** (Week 1-2)
   - Deliverables:
   - Dependencies:

2. **Phase 2: Core Features** (Week 3-4)
   - Deliverables:
   - Dependencies:

3. **Phase 3: Integration** (Week 5-6)
   - Deliverables:
   - Dependencies:

### Resource Requirements
- Engineering:
- Design:
- Data:
- External:

### Risk Management
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| | | | |

### Pilot Approach
- Scope:
- Duration:
- Participants:
- Exit criteria:

### Go/No-Go Checkpoint
Before proceeding to Stage 3 (Evaluation Protocol), confirm:
- [ ] Architecture validated
- [ ] Resources secured
- [ ] Stakeholder alignment
- [ ] Pilot scope approved

---
*Document Stage: 2 of 5 - Prototype Plan*
*Generated: {date}*
*Classification: {classification}*
""",

    'evaluation_protocol': """## {title}

### Purpose
This document defines the criteria for evaluating {topic} before full deployment.
It establishes clear PASS, LEARN, and FAIL conditions to de-risk the initiative.

### Evaluation Scope
- **Feature/Product:** {topic}
- **Evaluation Period:** [Duration]
- **Sample Size:** [Target N]
- **Primary Stakeholders:** [List]

---

## PASS Criteria (Green Light for Deployment)
To PASS, ALL of the following must be true:

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Primary KPI | ≥ [target] | [how measured] |
| User Satisfaction | ≥ [target]% | Survey/NPS |
| Error Rate | < [target]% | Monitoring |
| Safety Incidents | 0 critical | Incident log |

---

## LEARN Criteria (Proceed with Modifications)
If PASS criteria are not met but the following are true, we LEARN and iterate:

| Criterion | Threshold | Action Required |
|-----------|-----------|-----------------|
| Partial Success | ≥ [partial target] | Document gaps, iterate |
| Identified Fix | Clear path exists | Prioritize fix, re-test |
| Stakeholder Support | Maintains confidence | Continue with adjustments |

---

## FAIL Criteria (Immediate Halt - Kill Switch)
If ANY of the following occur, we FAIL and halt immediately:

| Criterion | Trigger | Response Protocol |
|-----------|---------|-------------------|
| Safety Breach | Any harm to users | Immediate shutdown, incident review |
| Data Breach | Unauthorized access | Security protocol, legal notification |
| Consent Violation | Processing without consent | Stop processing, notify users |
| Persona Drift | AI behaves unexpectedly | Quarantine, model review |
| Regulatory Flag | Compliance violation | Legal review, pause operations |

### Kill Switch Protocol
1. **Automatic Trigger:** [Conditions for automatic shutdown]
2. **Manual Trigger:** [Who can invoke, how to invoke]
3. **Post-Halt Actions:** [Immediate steps after halt]
4. **Communication Plan:** [Who to notify, timeline]

---

## Governance & Consent

### Data Governance
- **Data Used:** [Types of data]
- **Retention Period:** [Duration]
- **Access Controls:** [Who can access]
- **Audit Trail:** [How tracked]

### Consent Framework
- **Collection Method:** [How consent obtained]
- **Scope of Consent:** [What's covered]
- **Revocation Process:** [How users can revoke]
- **Re-consent Triggers:** [When to refresh consent]

### Escalation Path
| Severity | Response Time | Escalation To |
|----------|--------------|---------------|
| Low | 24 hours | Team Lead |
| Medium | 4 hours | Director |
| High | 1 hour | VP + Legal |
| Critical | Immediate | Executive + Board |

---

## Testing Protocol

### Test Categories
1. **Functional Testing**
   - [Test case 1]
   - [Test case 2]

2. **Adversarial Testing**
   - Input fuzzing
   - Edge cases
   - Abuse scenarios

3. **User Acceptance Testing**
   - [Participant criteria]
   - [Test scenarios]
   - [Feedback collection]

### Monitoring During Pilot
- Real-time metrics: [List]
- Daily reviews: [Who, what]
- Weekly reports: [Format, distribution]

---

## Sign-off Requirements

| Role | Name | Approval Status |
|------|------|-----------------|
| Product Owner | | [ ] Approved |
| Engineering Lead | | [ ] Approved |
| Legal/Compliance | | [ ] Approved |
| Security | | [ ] Approved |
| Executive Sponsor | | [ ] Approved |

---
*Document Stage: 3 of 5 - Evaluation Protocol*
*Generated: {date}*
*Classification: CONFIDENTIAL - INTERNAL USE ONLY*
""",

    'design_doc': """## {title}

### Overview
[Brief description of what this design covers]

### Goals & Non-Goals
**Goals:**
-

**Non-Goals:**
-

### Technical Design

#### Architecture
[System architecture description]

#### Data Models
[Key data structures and relationships]

#### API Contracts
[Key endpoints/interfaces]

#### Security Considerations
[Authentication, authorization, data protection]

### Implementation Plan
[Phases and milestones]

### Dependencies
[External dependencies and risks]

### Alternatives Considered
[Other approaches evaluated]

---
*Document Stage: 4 of 5 - Technical Design*
*Generated: {date}*
*Classification: {classification}*
""",

    'compliance_mapping': """## {title}

### Regulatory Landscape
[Applicable regulations and requirements]

### Compliance Requirements

| Regulation | Requirement | Current Status | Gap |
|------------|-------------|----------------|-----|
| | | | |

### Consent Framework
[Consent collection and management approach]

### Audit Trail Requirements
[Logging and tracking requirements]

### Policy Alignment
[Internal policy compliance]

---
*Document Stage: 5 of 5 - Compliance Mapping*
*Generated: {date}*
*Classification: {classification}*
""",
}


class TechnicalDocumentAgent(BaseAgent):
    """
    Agent that creates formal technical documents for the product development lifecycle.

    Unlike ContentWriterAgent, this agent:
    - Uses formal, professional language (no blog-style phrasing)
    - Includes governance and compliance language
    - Defines explicit PASS/LEARN/FAIL criteria where appropriate
    - Is stage-aware within the document lifecycle
    """

    name = "TechnicalDocumentAgent"
    requires_system_context = True  # Session 820: Inject CLAUDE.md + critical docs

    system_prompt = """You are TechnicalDocumentAgent, a professional technical writer who creates formal product development documentation.

CRITICAL RULES:
1. NEVER use blog-style phrasing like:
   - "In this blog post..."
   - "Welcome to..."
   - "Let's dive in..."
   - "Join us as we explore..."
   - Any casual, marketing-oriented language

2. ALWAYS use formal, professional language:
   - "This document outlines..."
   - "The purpose of this specification is..."
   - "This section defines..."
   - Direct, declarative statements

3. INCLUDE governance language for Stage 3+ documents:
   - PASS/LEARN/FAIL criteria
   - Kill switch conditions
   - Consent and data governance
   - Escalation paths

4. STRUCTURE for decision-making:
   - Clear sections with actionable content
   - Tables for criteria and thresholds
   - Explicit approval checkboxes where needed
   - Document stage footer

Document Types You Create:
- Research Brief (Stage 1): Discovery + framing
- Prototype Plan (Stage 2): Implementation translation
- Evaluation Protocol (Stage 3): Pre-pilot gate with PASS/LEARN/FAIL
- Technical Design (Stage 4): Implementation specification
- Compliance Mapping (Stage 5): Regulatory alignment

Your output should be ready for executive review and formal approval processes."""

    tools = []  # Document generation via direct GPT call

    def __init__(self, user=None):
        """Initialize the technical document agent."""
        super().__init__(user)

    def execute(
        self,
        task: str,
        context: Dict[str, Any] = None,
        scifi_context: Dict[str, Any] = None,
        spider_context: Dict[str, Any] = None
    ) -> AgentResult:
        """
        Execute document generation.

        Args:
            task: The document generation task
            context: Must include:
                - doc_type: Type of document (research_brief, prototype_plan, etc.)
                - stage: Stage number (1-5)
                - topic: The subject matter
                - research_context: Background research (optional)
            scifi_context: Sci-fi features context (optional)
            spider_context: Spider data context (optional)

        Returns:
            AgentResult with the generated document
        """
        context = context or {}
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        start_time = datetime.now()

        # Session 750: Time Travel integration
        with self.time_travel_session("technical_document_generation", task, input_data=context):
            # Handle simple diagnostic/identification queries
            task_lower = task.lower() if task else ''
            if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                return AgentResult(
                    success=True,
                    message=f"I am {self.name}, a specialist in generating structured technical documentation. One capability: I create 5-stage technical documents from Research Briefs through Analysis Reports to Implementation Specs, following templates with proper classification and formatting.",
                    data={'type': 'self_description', 'stages': ['Research Brief', 'Technical Assessment', 'Prototype Plan', 'Analysis Report', 'Implementation Spec']},
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

            self.record_decision(
                decision_type="planning",
                action="Starting technical document generation",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip generation", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

        try:
            doc_type = context.get('doc_type', 'research_brief')
            stage = context.get('stage', 1)
            topic = context.get('topic', 'Untitled Topic')
            research_context = context.get('research_context', '')
            classification = context.get('classification', 'INTERNAL')

            # Get template if available
            template = DOCUMENT_TEMPLATES.get(doc_type, '')

            # Build the generation prompt
            generation_prompt = self._build_generation_prompt(
                task=task,
                doc_type=doc_type,
                stage=stage,
                topic=topic,
                research_context=research_context,
                template=template,
                classification=classification
            )

            # Session 819: Use intelligent prompting for full context
            intelligent_prompt = self._build_intelligent_prompt(
                task=task,
                scifi_context=scifi_context,
                spider_context=spider_context,
                additional_context=""
            )

            # Call GPT to generate the document
            messages = [
                {"role": "system", "content": intelligent_prompt},
                {"role": "user", "content": generation_prompt}
            ]

            response = self._call_llm(messages)

            if not response:
                return AgentResult(
                    success=False,
                    message="Failed to generate document - no response from LLM",
                    data={}
                )

            # Extract the document content
            document_content = response.strip()

            # Session 814: Save to workspace for UI visibility via SKIN layer
            doc_title = f"Stage {stage} - {DOCUMENT_STAGES.get(stage, {}).get('name', 'Document')}: {topic}"
            workspace_result = self._save_to_workspace(
                title=doc_title,
                content=document_content,
                doc_type=doc_type,
                stage=stage,
                topic=topic,
                classification=classification,
                user=context.get('user')
            )

            # Build result
            # Session 814: Check workspace_result.get('success') for proper status
            workspace_saved = workspace_result and workspace_result.get('success', False)
            result_data = {
                'content': {
                    'full_text': document_content,
                    'title': doc_title,
                    'doc_type': doc_type,
                    'stage': stage,
                    'stage_name': DOCUMENT_STAGES.get(stage, {}).get('name', 'Document'),
                    'topic': topic,
                    'workspace_file': workspace_result.get('path') if workspace_saved else None,
                    'workspace': workspace_result.get('workspace') if workspace_saved else None,
                },
                'metadata': {
                    'classification': classification,
                    'generated_at': datetime.now().isoformat(),
                    'stage_purpose': DOCUMENT_STAGES.get(stage, {}).get('purpose', ''),
                    'saved_to_workspace': workspace_saved,
                    'workspace_reason': workspace_result.get('reason') if workspace_result and not workspace_saved else None,
                }
            }

            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Session 861: Persist to Deliverable model
            self._save_to_deliverable(
                title=doc_title,
                content=document_content,
                deliverable_type='document',
                category='Development',
                tags=[doc_type, f'stage-{stage}', topic[:30] if topic else ''],
                content_format='markdown',
                metadata={
                    'doc_type': doc_type,
                    'stage': stage,
                    'stage_name': DOCUMENT_STAGES.get(stage, {}).get('name', 'Document'),
                    'topic': topic,
                    'classification': classification,
                    'workspace_saved': workspace_saved,
                },
                user=context.get('user'),
            )

            workspace_msg = ""
            if workspace_saved:
                workspace_msg = f" (saved to workspace: {workspace_result.get('workspace', 'default')})"
            elif workspace_result and workspace_result.get('reason'):
                workspace_msg = f" (workspace: {workspace_result.get('reason')})"

            return AgentResult(
                success=True,
                message=f"Generated Stage {stage} - {DOCUMENT_STAGES.get(stage, {}).get('name', 'Document')}{workspace_msg}",
                data=result_data,
                execution_time_ms=execution_time_ms,
                agent_name=self.name
            )

        except Exception as e:
            logger.error(f"TechnicalDocumentAgent error: {e}")
            return AgentResult(
                success=False,
                message=f"Error generating document: {str(e)}",
                data={}
            )

    def _save_to_workspace(
        self,
        title: str,
        content: str,
        doc_type: str,
        stage: int,
        topic: str,
        classification: str,
        user=None
    ):
        """
        Session 814: Save technical document to workspace for UI visibility.
        Documents are stored in the workspace with audit trail via SKIN layer.
        """
        try:
            # Generate filename from title
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in topic)
            safe_title = safe_title.replace(' ', '_').lower()[:50]
            filename = f"stage_{stage}_{doc_type}_{safe_title}.md"

            # Add metadata header to document
            metadata_header = f"""---
title: {title}
type: {doc_type}
stage: {stage}
classification: {classification}
generated_by: {self.name}
generated_at: {datetime.now().isoformat()}
---

"""
            full_content = metadata_header + content

            # Use workspace write via SKIN layer
            files_to_write = [{
                'path': f"documents/{filename}",
                'content': full_content
            }]

            write_result = self._write_files_to_workspace(
                files=files_to_write,
                user=user,
                base_path=""
            )

            # Session 814: Check 'written' key (not 'success') per SKIN layer API
            if write_result.get('written'):
                logger.info(f"📝 [Session 814] Saved technical document to workspace: {filename}")
                return {
                    'success': True,
                    'filename': filename,
                    'path': f"documents/{filename}",
                    'workspace': write_result.get('workspace'),
                    'operations': write_result.get('operations', [])
                }
            else:
                reason = write_result.get('reason', 'Unknown error')
                logger.warning(f"Failed to write document to workspace: {reason}")
                return {
                    'success': False,
                    'reason': reason,
                    'files_generated': write_result.get('files_generated', 1)
                }

        except Exception as e:
            logger.error(f"Failed to save technical document to workspace: {e}")
            return None

    def _build_generation_prompt(
        self,
        task: str,
        doc_type: str,
        stage: int,
        topic: str,
        research_context: str,
        template: str,
        classification: str
    ) -> str:
        """Build the document generation prompt."""
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')

        stage_info = DOCUMENT_STAGES.get(stage, {})
        stage_name = stage_info.get('name', 'Document')
        stage_purpose = stage_info.get('purpose', '')
        expected_outputs = stage_info.get('outputs', [])

        # Session 814: Inject critical system docs for context awareness
        critical_docs_context = self._get_critical_system_context(task=task)

        prompt = f"""Create a {stage_name} document for the following:

**Topic:** {topic}
**Document Type:** {doc_type}
**Stage:** {stage} of 5 - {stage_name}
**Purpose:** {stage_purpose}
**Classification:** {classification}
**Date:** {date_str}

**Task:** {task}

"""
        # Session 814: Add critical system context if available
        if critical_docs_context:
            prompt += f"""
{critical_docs_context}

"""

        if research_context:
            prompt += f"""**Research Context:**
{research_context}

"""

        if expected_outputs:
            prompt += f"""**Expected Sections:**
{chr(10).join(f'- {output}' for output in expected_outputs)}

"""

        if template:
            prompt += f"""**Template Structure (use as guide, adapt as needed):**
{template}

"""

        prompt += """**Instructions:**
1. Create a comprehensive, formal technical document
2. Use the template structure as a guide but adapt content to the specific topic
3. Fill in ALL sections with substantive content based on the research context
4. Use tables for criteria, thresholds, and structured data
5. Include explicit approval checkboxes where appropriate
6. Add the document stage footer
7. NEVER use casual or blog-style language
8. Make all criteria specific and measurable (not vague)
9. **CRITICAL: If System Context is provided above, you MUST reference specific details from it:**
   - Mention exact counts (e.g., "74 agents", "77 spiders", "228 Celery tasks")
   - Reference specific systems (HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN)
   - Include session numbers and features mentioned in the context
   - Your output should be specific to THIS system, NOT generic

Generate the complete document now:"""

        return prompt

    def _call_llm(self, messages: List[Dict]) -> Optional[str]:
        """Call the LLM to generate content."""
        try:
            from django.conf import settings

            client = get_openai_client(api_key=settings.OPENAI_API_KEY)

            # Use GPT-4 for high-quality technical writing
            # Session 814: Increased max_tokens to handle large context + response
            response = client.chat.completions.create(
                model="gpt-5.2",  # or gpt-4-turbo for cost savings
                messages=messages,
                max_completion_tokens=8000,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None

    def _get_critical_system_context(self, task: str = "") -> str:
        """
        Session 814: Get critical system documentation context.

        Uses DocsContextBuilder to inject CLAUDE.md and 00-START-NEXT-SESSION.md
        so the agent has full awareness of the system it's documenting.
        """
        try:
            from core.services.docs_context_builder import DocsContextBuilder

            builder = DocsContextBuilder()
            # Get critical docs with full content
            context = builder.build_context_for_agent(
                agent_name=self.name,
                task=task,
                include_critical_docs=True,
                include_content_snippets=True,  # Enable full content
                max_docs=5  # Focus on most relevant
            )

            if context and context.get('has_docs'):
                # Extract the summary string from the context dict
                summary = context.get('summary', '')
                if summary and len(summary) > 100:  # Has meaningful content
                    return f"""## System Context (Auto-Injected)
The following provides critical context about the system being documented:

{summary}

Use this context to make your documentation specific to THIS system, not generic.
Reference specific details (agent counts, service counts, features) from above.
"""
            return ""
        except Exception as e:
            logger.warning(f"Failed to load critical system context: {e}")
            return ""


def get_stage_for_doc_type(doc_type: str) -> Dict[str, Any]:
    """
    Determine the stage information for a given document type.

    Returns:
        Dict with stage number, name, and purpose
    """
    doc_type_lower = doc_type.lower()

    for stage_num, stage_info in DOCUMENT_STAGES.items():
        if doc_type_lower in stage_info['doc_types']:
            return {
                'stage': stage_num,
                'name': stage_info['name'],
                'purpose': stage_info['purpose'],
            }

    # Default to Stage 1 if unknown
    return {
        'stage': 1,
        'name': 'Research Brief',
        'purpose': 'Discovery + framing',
    }


def infer_stage_from_deliverable(deliverable_name: str) -> Dict[str, Any]:
    """
    Infer the stage and document type from a deliverable name.

    This is the enhanced version of _infer_document_type() that returns
    stage information for proper lifecycle ordering.

    Returns:
        Dict with stage, doc_type, and stage_name
    """
    name_lower = deliverable_name.lower()

    # Stage 1: Research Brief patterns
    if any(kw in name_lower for kw in ['brief', 'research', 'discovery', 'summary', 'overview']):
        return {
            'stage': 1,
            'doc_type': 'research_brief',
            'stage_name': 'Research Brief',
            'prefix': 'Stage 1 - Research Brief',
        }

    # Stage 2: Prototype Plan patterns
    if any(kw in name_lower for kw in ['plan', 'prototype', 'implementation', 'roadmap', 'architecture']):
        return {
            'stage': 2,
            'doc_type': 'prototype_plan',
            'stage_name': 'Prototype Plan',
            'prefix': 'Stage 2 - Prototype Plan',
        }

    # Stage 3: Evaluation Protocol patterns
    if any(kw in name_lower for kw in ['evaluation', 'protocol', 'testing', 'validation', 'criteria', 'framework']):
        return {
            'stage': 3,
            'doc_type': 'evaluation_protocol',
            'stage_name': 'Evaluation Protocol',
            'prefix': 'Stage 3 - Evaluation Protocol',
        }

    # Stage 4: Technical Design patterns
    if any(kw in name_lower for kw in ['design doc', 'technical', 'specification', 'spec', 'api']):
        return {
            'stage': 4,
            'doc_type': 'design_doc',
            'stage_name': 'Technical Design',
            'prefix': 'Stage 4 - Technical Design',
        }

    # Stage 5: Compliance patterns
    if any(kw in name_lower for kw in ['compliance', 'regulatory', 'consent', 'gdpr', 'legal', 'policy']):
        return {
            'stage': 5,
            'doc_type': 'compliance_mapping',
            'stage_name': 'Compliance Mapping',
            'prefix': 'Stage 5 - Compliance Mapping',
        }

    # Stage 2 fallback for recommendation-type docs
    if any(kw in name_lower for kw in ['recommendation', 'guide', 'how-to']):
        return {
            'stage': 2,
            'doc_type': 'prototype_plan',
            'stage_name': 'Prototype Plan',
            'prefix': 'Stage 2 - Prototype Plan',
        }

    # Default to Stage 1 Research Brief
    return {
        'stage': 1,
        'doc_type': 'research_brief',
        'stage_name': 'Research Brief',
        'prefix': 'Stage 1 - Research Brief',
    }
