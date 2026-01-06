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

            # Call GPT to generate the document
            messages = [
                {"role": "system", "content": self.system_prompt},
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

            # Build result
            result_data = {
                'content': {
                    'full_text': document_content,
                    'title': f"Stage {stage} - {DOCUMENT_STAGES.get(stage, {}).get('name', 'Document')}: {topic}",
                    'doc_type': doc_type,
                    'stage': stage,
                    'stage_name': DOCUMENT_STAGES.get(stage, {}).get('name', 'Document'),
                    'topic': topic,
                },
                'metadata': {
                    'classification': classification,
                    'generated_at': datetime.now().isoformat(),
                    'stage_purpose': DOCUMENT_STAGES.get(stage, {}).get('purpose', ''),
                }
            }

            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            return AgentResult(
                success=True,
                message=f"Generated Stage {stage} - {DOCUMENT_STAGES.get(stage, {}).get('name', 'Document')}",
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

        prompt = f"""Create a {stage_name} document for the following:

**Topic:** {topic}
**Document Type:** {doc_type}
**Stage:** {stage} of 5 - {stage_name}
**Purpose:** {stage_purpose}
**Classification:** {classification}
**Date:** {date_str}

**Task:** {task}

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

Generate the complete document now:"""

        return prompt

    def _call_llm(self, messages: List[Dict]) -> Optional[str]:
        """Call the LLM to generate content."""
        try:
            from openai import OpenAI
            from django.conf import settings

            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            # Use GPT-4 for high-quality technical writing
            response = client.chat.completions.create(
                model="gpt-4o",  # or gpt-4-turbo for cost savings
                messages=messages,
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for consistent, formal output
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None


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
