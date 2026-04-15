"""
Session 594: AI-Powered Checklist Content Generator

Automatically generates content for Pilot Readiness Gate checklist items
based on the decision context. Humans review and approve instead of
writing from scratch.
"""

import logging
import json
from typing import Dict, Any, Optional
from openai import OpenAI
import os
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


class ChecklistContentGenerator:
    """
    Generates intelligent content for each checklist item type
    based on the decision being evaluated.
    """

    def __init__(self):
        self.client = get_openai_client(api_key=os.environ.get('OPENAI_API_KEY'))

    def generate_all_items(self, gate) -> Dict[str, str]:
        """
        Generate content for all checklist items on a gate.

        Args:
            gate: PilotReadinessGate instance

        Returns:
            Dict mapping item_type to generated content
        """
        decision = gate.decision
        if not decision:
            logger.warning(f"Gate {gate.id} has no decision, skipping content generation")
            return {}

        # Build context about the decision
        context = self._build_decision_context(decision)

        # Generate content for each item
        results = {}
        for item in gate.checklist_items.all():
            try:
                content = self.generate_for_item(item.item_type, context)
                if content:
                    item.documentation_notes = content
                    item.save()
                    results[item.item_type] = content
                    logger.info(f"Generated content for {item.item_type} on gate {gate.id}")
            except Exception as e:
                logger.error(f"Failed to generate content for {item.item_type}: {e}")
                results[item.item_type] = f"Generation failed: {str(e)}"

        return results

    def generate_for_item(self, item_type: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Generate content for a specific checklist item type.

        Args:
            item_type: The type of checklist item
            context: Decision context dictionary

        Returns:
            Generated content string
        """
        prompt = self._get_prompt_for_type(item_type, context)
        if not prompt:
            return None

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert in AI governance and risk management.
Generate concise, actionable content for pilot readiness checklists.
Be specific to the decision context provided. Use markdown formatting.
Keep responses focused and practical (200-400 words max)."""
                    },
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=800,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error generating {item_type}: {e}")
            return None

    def _build_decision_context(self, decision) -> Dict[str, Any]:
        """Build context dictionary from a decision."""
        # Get summary from rationale or key_insights
        summary = getattr(decision, 'rationale', '') or getattr(decision, 'key_insights', '') or 'No details available'
        if isinstance(summary, list):
            summary = '\n'.join(summary)

        return {
            'topic': decision.topic,
            'summary': summary,
            'decision_type': decision.decision_type,
            'impact_area': decision.impact_area,
            'agents_involved': getattr(decision, 'participants', []) or [],
            'status': getattr(decision, 'status', 'unknown'),
        }

    def _get_prompt_for_type(self, item_type: str, context: Dict[str, Any]) -> Optional[str]:
        """Get the generation prompt for each item type."""

        base_context = f"""
Decision Topic: {context['topic']}
Decision Type: {context['decision_type']}
Impact Area: {context['impact_area']}
Summary: {context['summary'][:500]}
Agents Involved: {', '.join(context['agents_involved']) if context['agents_involved'] else 'Not specified'}
"""

        prompts = {
            'threat_model': f"""
{base_context}

Generate a THREAT MODEL for this decision. Include:

1. **Identified Threats** (3-5 specific risks)
   - What could go wrong?
   - What are the attack vectors?
   - What data/systems are at risk?

2. **Impact Assessment**
   - Severity of each threat (Low/Medium/High)
   - Who/what is affected?

3. **Mitigation Strategies**
   - Specific countermeasures for each threat
   - Monitoring recommendations

Format as a clear, scannable document that a reviewer can quickly assess.
""",

            'rollback_procedure': f"""
{base_context}

Generate a ROLLBACK PROCEDURE for this decision. Include:

1. **Rollback Triggers**
   - What conditions would trigger a rollback?
   - Who can authorize a rollback?

2. **Rollback Steps**
   - Step-by-step procedure to revert changes
   - Estimated time to complete rollback

3. **Verification**
   - How to confirm rollback was successful
   - Post-rollback health checks

4. **Communication Plan**
   - Who needs to be notified
   - Status update templates

Keep it actionable and clear.
""",

            'success_metrics': f"""
{base_context}

Generate SUCCESS METRICS for this pilot. Include:

1. **Primary KPIs** (2-3 key metrics)
   - What numbers indicate success?
   - Target values and thresholds

2. **Secondary Indicators**
   - Supporting metrics to track
   - Early warning signals

3. **Measurement Method**
   - How will each metric be measured?
   - Data sources and frequency

4. **Success Criteria**
   - What defines pilot SUCCESS vs FAILURE?
   - Decision matrix for outcomes

Be specific with measurable targets.
""",

            'kill_switch': f"""
{base_context}

Generate KILL SWITCH CRITERIA for this decision. Include:

1. **Automatic Triggers**
   - Conditions that should auto-stop the pilot
   - Thresholds and limits

2. **Manual Triggers**
   - When should humans intervene?
   - Escalation criteria

3. **Kill Switch Mechanism**
   - Technical implementation (if applicable)
   - How quickly can it be activated?

4. **Post-Kill Actions**
   - Immediate steps after kill switch
   - Data preservation requirements

Focus on safety and quick response.
""",

            'encryption_choice': f"""
{base_context}

Generate an ENCRYPTION/DATA PROTECTION REVIEW for this decision. Include:

1. **Data Classification**
   - What data is involved?
   - Sensitivity level (Public/Internal/Confidential/Restricted)

2. **Encryption Requirements**
   - Data at rest: encryption needed?
   - Data in transit: TLS/SSL requirements
   - Key management considerations

3. **Access Controls**
   - Who needs access?
   - Authentication requirements

4. **Compliance Check**
   - Relevant regulations (GDPR, CCPA, etc.)
   - Required certifications

Be specific about security requirements.
""",

            'adversarial_test': f"""
{base_context}

Generate an ADVERSARIAL TEST PLAN for this decision. Include:

1. **Attack Scenarios**
   - How might bad actors exploit this?
   - Edge cases to test

2. **Test Cases**
   - Specific adversarial inputs to try
   - Expected vs actual behavior

3. **Red Team Checklist**
   - Prompt injection attempts
   - Data exfiltration attempts
   - Denial of service scenarios

4. **Pass/Fail Criteria**
   - What constitutes a security failure?
   - Acceptable risk thresholds

Focus on AI-specific attack vectors.
""",

            'basic_review': f"""
{base_context}

Generate a BASIC REVIEW CHECKLIST for this decision. Include:

1. **Decision Clarity**
   - Is the decision well-defined?
   - Are goals and outcomes clear?

2. **Stakeholder Alignment**
   - Who is affected?
   - Have they been consulted?

3. **Resource Assessment**
   - What resources are needed?
   - Are they available?

4. **Timeline Check**
   - Is the timeline realistic?
   - Dependencies identified?

5. **Risk Acknowledgment**
   - Key risks understood?
   - Mitigation plans in place?

Keep it simple and comprehensive.
""",

            # Session 617: Added consent_lifecycle prompt
            'consent_lifecycle': f"""
{base_context}

Generate a CONSENT LIFECYCLE document for this decision. Include:

1. **Consent Requirements**
   - What user consent is needed?
   - What data/actions require explicit consent?
   - Are there implicit vs explicit consent scenarios?

2. **Consent Collection**
   - How will consent be obtained?
   - Consent UI/UX requirements
   - Clear language requirements

3. **Consent Storage**
   - Where is consent recorded?
   - Audit trail requirements
   - Timestamp and version tracking

4. **Consent Revocation**
   - How can users withdraw consent?
   - What happens when consent is revoked?
   - Data deletion/retention implications

5. **Compliance Considerations**
   - GDPR requirements (if applicable)
   - CCPA requirements (if applicable)
   - Age verification needs

Focus on practical, implementable consent flows.
""",
        }

        return prompts.get(item_type)


def generate_checklist_content_for_gate(gate_id: str) -> Dict[str, Any]:
    """
    Convenience function to generate content for a gate by ID.

    Args:
        gate_id: UUID of the gate

    Returns:
        Dict with success status and generated content
    """
    from core.models_pilot_readiness import PilotReadinessGate

    try:
        gate = PilotReadinessGate.objects.get(id=gate_id)
        generator = ChecklistContentGenerator()
        results = generator.generate_all_items(gate)

        return {
            'success': True,
            'gate_id': str(gate_id),
            'items_generated': len(results),
            'content': results
        }
    except PilotReadinessGate.DoesNotExist:
        return {'success': False, 'error': 'Gate not found'}
    except Exception as e:
        logger.error(f"Error generating checklist content: {e}")
        return {'success': False, 'error': str(e)}
