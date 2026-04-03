"""
DecisionEnforcerAgent - The Prefrontal Cortex
==============================================

Session 872: Based on ChatGPT feedback about missing "executive function."

"Right now you have: Cortex (thinking), Sensors (spiders), Speech (blogs/docs)
But you're missing: Prefrontal Cortex (decisions)
That's why loops happen.
You need a meta-agent that says: 'Enough. Do X.'"

This agent:
1. Triggers AFTER synthesis/debate completes
2. Reads the debate log
3. FORCES a decision with structured output
4. Assigns owners and deadlines
5. Defines kill criteria
6. Spawns actual tasks

No more "further analysis recommended."
No more "productive discussion."
DECIDE. ASSIGN. EXECUTE.

Usage:
    from core.agents.decision_enforcer_agent import DecisionEnforcerAgent

    agent = DecisionEnforcerAgent()
    result = agent.execute(
        task="Enforce decision from salary negotiation debate",
        context={
            'debate_messages': [...],  # Conversation transcript
            'synthesis': {...},        # Optional synthesis result
            'topic': 'salary negotiation MVP',
        }
    )

    # Result contains ExecutionMandate
    mandate = result.data.get('mandate')
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from .base_agent import BaseAgent, AgentResult, OutputCategory
from core.contracts.execution_mandate import (
    ExecutionMandate,
    MandateStatus,
    SpawnedTask,
    extract_experiments_from_debate,
    extract_kill_criteria_from_debate,
)

logger = logging.getLogger(__name__)


class DecisionEnforcerAgent(BaseAgent):
    """
    The Prefrontal Cortex - Forces decisions after debate/synthesis.

    This agent breaks loop attractors by:
    1. Analyzing debate transcript
    2. Identifying the strongest path
    3. Forcing a decisive mandate
    4. Spawning actionable tasks

    It rejects weasel words and non-decisions.
    """

    # Class attributes
    name = "DecisionEnforcerAgent"
    description = "Forces decisive action after debate - the 'prefrontal cortex' that breaks analysis paralysis"
    specialization = "decision enforcement"

    # Output configuration
    output_category = OutputCategory.DECISION

    # System prompt that enforces decisiveness
    system_prompt = """You are the DecisionEnforcerAgent - the PREFRONTAL CORTEX of this AI system.

Your job is to END debates and FORCE decisions.

## Your Mission
After agents have debated, you MUST:
1. Pick a winner - which path is strongest?
2. Kill weak alternatives - be explicit about what we're NOT doing
3. Assign ownership - who executes this?
4. Set deadlines - when must we see results?
5. Define kill criteria - how do we know if this fails?
6. Spawn tasks - what EXACTLY needs to happen next?

## STRICT RULES

### You MUST NOT use these phrases:
- "Further analysis recommended"
- "More research needed"
- "Consider exploring"
- "Should validate"
- "Needs investigation"
- "Productive discussion"
- "We should look into"

### You MUST:
- Be DECISIVE - pick ONE path
- Be SPECIFIC - concrete actions, not vague goals
- Be MEASURABLE - numbers, dates, percentages
- Be ACCOUNTABLE - name an owner for everything
- Be KILLABLE - define explicit failure criteria

## Output Format
You MUST respond with valid JSON matching this structure:
{
    "chosen_path": "Specific, actionable decision",
    "reason": "Why this path, with ACTUAL evidence from the debate (use real numbers from context)",
    "decision_owner": "AgentName or role responsible",
    "confidence": 0.0-1.0,
    "confidence_reason": "Why this confidence level",
    "experiments": [
        "Specific experiment with measurable criteria"
    ],
    "kill_criteria": [
        "Measurable failure condition with specific threshold"
    ],
    "deadline": "ISO date or relative timeframe",
    "rejected_paths": {
        "Alternative": "Why rejected based on debate"
    },
    "acknowledged_risks": [
        "Risk we're accepting"
    ],
    "spawned_tasks": [
        {
            "agent": "AgentName",
            "action": "Specific action to take",
            "deadline": "When",
            "priority": 1
        }
    ]
}

## Example Structure (use YOUR data, not these placeholder values):
{
    "chosen_path": "Build [feature] MVP for [target users] with [key capability]",
    "reason": "[X]% market signal from debate, [N/M] agents supported, [specific evidence from context]",
    "decision_owner": "[Agent from debate]",
    "confidence": 0.XX,
    "confidence_reason": "[Based on actual sample size and data quality from debate]",
    "experiments": [
        "Launch to [N] beta users, measure [specific metric]",
        "A/B test: [variant A] vs [variant B]"
    ],
    "kill_criteria": [
        "<[X]% [metric] after [N] days",
        "No [outcome] within [timeframe]"
    ],
    "deadline": "[realistic date based on scope]",
    "rejected_paths": {
        "[Alternative from debate]": "[Why rejected based on debate evidence]"
    },
    "acknowledged_risks": [
        "[Actual risks identified in debate]"
    ],
    "spawned_tasks": [
        {"agent": "[Appropriate agent]", "action": "[Specific action]", "priority": 1}
    ]
}

IMPORTANT: Use ACTUAL numbers and evidence from the debate context. Do NOT copy the placeholder values above.

Remember: Your job is to DECIDE, not to defer. Break the loop."""

    tools = []  # This agent uses LLM reasoning, not tools

    def __init__(self, user=None):
        super().__init__(user=user)

    def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        scifi_context: Optional[str] = None,
        spider_context: Optional[str] = None
    ) -> AgentResult:
        """
        Analyze debate and force a decision.

        Args:
            task: Description of what decision to enforce
            context: Must contain:
                - debate_messages: List of conversation messages
                - synthesis: Optional synthesis result
                - topic: What the debate was about
            scifi_context: Optional sci-fi context
            spider_context: Optional spider context

        Returns:
            AgentResult with ExecutionMandate in data
        """
        import time
        start_time = time.time()

        context = context or {}
        debate_messages = context.get('debate_messages', [])
        synthesis = context.get('synthesis', {})
        topic = context.get('topic', 'unknown topic')

        if not debate_messages and not synthesis:
            return AgentResult(
                success=False,
                message="No debate transcript or synthesis provided",
                error="Missing debate_messages or synthesis in context",
                agent_name=self.name,
                output_category=self.output_category.value,
            )

        # Build the debate summary for the LLM
        debate_summary = self._summarize_debate(debate_messages, synthesis, topic)

        # Pre-extract hints from debate (these help but LLM makes final call)
        experiment_hints = extract_experiments_from_debate(debate_messages)
        kill_hints = extract_kill_criteria_from_debate(debate_messages)

        # Build the prompt
        prompt = self._build_decision_prompt(
            topic=topic,
            debate_summary=debate_summary,
            experiment_hints=experiment_hints,
            kill_hints=kill_hints,
        )

        try:
            # Call LLM to make the decision
            decision_json = self._call_llm_for_decision(prompt)

            # Parse and validate the mandate
            mandate = self._parse_mandate(decision_json, debate_messages, synthesis)

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            return AgentResult(
                success=True,
                message=f"Decision enforced: {mandate.chosen_path}",
                data={
                    'mandate': mandate.to_dict(),
                    'mandate_markdown': mandate.to_markdown(),
                    'topic': topic,
                    'debate_length': len(debate_messages),
                    'tasks_spawned': len(mandate.spawned_tasks),
                },
                agent_name=self.name,
                execution_time_ms=execution_time_ms,
                output_category=self.output_category.value,
                confidence=mandate.confidence,
            )

        except ValueError as e:
            # Validation error - mandate was rejected
            execution_time_ms = int((time.time() - start_time) * 1000)
            return AgentResult(
                success=False,
                message=f"Decision rejected: {str(e)}",
                error=str(e),
                agent_name=self.name,
                execution_time_ms=execution_time_ms,
                output_category=self.output_category.value,
            )

        except Exception as e:
            logger.exception(f"DecisionEnforcerAgent error: {e}")
            execution_time_ms = int((time.time() - start_time) * 1000)
            return AgentResult(
                success=False,
                message=f"Failed to enforce decision: {str(e)}",
                error=str(e),
                agent_name=self.name,
                execution_time_ms=execution_time_ms,
                output_category=self.output_category.value,
            )

    def _summarize_debate(
        self,
        messages: List[Dict[str, Any]],
        synthesis: Dict[str, Any],
        topic: str
    ) -> str:
        """Create a concise debate summary for the LLM."""
        lines = [f"## Debate Topic: {topic}\n"]

        # Add synthesis if present
        if synthesis:
            if synthesis.get('insights'):
                lines.append("### Synthesis Insights:")
                for insight in synthesis.get('insights', [])[:5]:
                    lines.append(f"- {insight}")
                lines.append("")

            if synthesis.get('proposed_feature'):
                lines.append(f"### Proposed Feature: {synthesis.get('proposed_feature')}")
                lines.append("")

            if synthesis.get('next_steps'):
                lines.append("### Suggested Next Steps:")
                for step in synthesis.get('next_steps', [])[:3]:
                    lines.append(f"- {step}")
                lines.append("")

        # Add key debate points
        if messages:
            lines.append("### Debate Positions:")
            seen_agents = set()
            for msg in messages:
                agent = msg.get('agent', msg.get('role', 'Unknown'))
                if agent not in seen_agents:
                    seen_agents.add(agent)
                    content = msg.get('content', '')[:500]  # Truncate
                    lines.append(f"\n**{agent}:**\n{content}...")
                    if len(seen_agents) >= 4:  # Limit to 4 agents
                        break

        return "\n".join(lines)

    def _build_decision_prompt(
        self,
        topic: str,
        debate_summary: str,
        experiment_hints: List[str],
        kill_hints: List[str],
    ) -> str:
        """Build the prompt for the LLM decision."""
        prompt = f"""Analyze this debate and FORCE a decision.

{debate_summary}

### Hints Extracted from Debate:

**Potential Experiments:** {experiment_hints or ['None explicitly mentioned - propose your own']}

**Potential Kill Criteria:** {kill_hints or ['None explicitly mentioned - propose your own']}

---

NOW DECIDE.

1. Pick the STRONGEST path from the debate
2. Reject the alternatives with clear reasons
3. Assign an owner
4. Set a deadline (within 2 weeks)
5. Define kill criteria (measurable!)
6. List experiments to run
7. Spawn specific tasks

Respond with ONLY valid JSON. No markdown, no explanation outside JSON.
"""
        return prompt

    def _call_llm_for_decision(self, prompt: str) -> Dict[str, Any]:
        """Call the LLM to get a decision."""
        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model="gpt-5.2",  # Use GPT-4 for decision quality
            messages=messages,
            max_completion_tokens=2000,
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON from response
        try:
            # Try to parse directly
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                return json.loads(json_match.group(1))
            # Try to find JSON object in content
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Could not parse JSON from LLM response: {content[:200]}")

    def _parse_mandate(
        self,
        decision_json: Dict[str, Any],
        debate_messages: List[Dict[str, Any]],
        synthesis: Dict[str, Any]
    ) -> ExecutionMandate:
        """Parse LLM response into validated ExecutionMandate."""

        # Parse deadline
        deadline = decision_json.get('deadline', '')
        if not deadline:
            # Default to 7 days from now
            deadline = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        elif deadline.lower().endswith('d'):
            # Handle relative deadline like "7d"
            days = int(deadline[:-1])
            deadline = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')

        # Parse spawned tasks
        spawned_tasks = []
        for task_data in decision_json.get('spawned_tasks', []):
            spawned_tasks.append(SpawnedTask(
                agent=task_data.get('agent', 'UnassignedAgent'),
                action=task_data.get('action', ''),
                deadline=task_data.get('deadline'),
                priority=task_data.get('priority', 1),
            ))

        # Create the mandate
        mandate = ExecutionMandate(
            chosen_path=decision_json.get('chosen_path', ''),
            reason=decision_json.get('reason', ''),
            decision_owner=decision_json.get('decision_owner', ''),
            kill_criteria=decision_json.get('kill_criteria', []),
            deadline=deadline,
            experiments=decision_json.get('experiments', []),
            rejected_paths=decision_json.get('rejected_paths', {}),
            acknowledged_risks=decision_json.get('acknowledged_risks', []),
            confidence=decision_json.get('confidence', 0.6),
            confidence_reason=decision_json.get('confidence_reason', ''),
            spawned_tasks=spawned_tasks,
            status=MandateStatus.ACTIVE,
            source_conversation_id=synthesis.get('conversation_id') if synthesis else None,
        )

        # Validate - this will raise if invalid
        mandate.validate()

        return mandate

    def spawn_tasks_from_mandate(self, mandate: ExecutionMandate) -> List[str]:
        """
        Actually spawn tasks from the mandate.

        This creates real Celery tasks or Initiative stages.

        Returns:
            List of task IDs created
        """
        task_ids = []

        try:
            from core.tasks import queue_agent_task

            for spawned in mandate.spawned_tasks:
                # Queue the agent task
                task = queue_agent_task.delay(
                    agent_name=spawned.agent,
                    task_description=spawned.action,
                    context={
                        'mandate_id': mandate.created_at,
                        'mandate_owner': mandate.decision_owner,
                        'deadline': spawned.deadline or mandate.deadline,
                        'priority': spawned.priority,
                    }
                )
                spawned.task_id = task.id
                task_ids.append(task.id)
                logger.info(f"Spawned task {task.id} for {spawned.agent}: {spawned.action}")

        except Exception as e:
            logger.error(f"Failed to spawn tasks: {e}")

        return task_ids


# Utility function for integration with conversation orchestrator
def enforce_decision_after_synthesis(
    debate_messages: List[Dict[str, Any]],
    synthesis: Dict[str, Any],
    topic: str,
    auto_spawn: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to enforce decision after conversation ends.

    Args:
        debate_messages: The conversation transcript
        synthesis: The synthesis/decision summary
        topic: What was debated
        auto_spawn: Whether to automatically spawn tasks

    Returns:
        Dict with mandate and optional task_ids
    """
    agent = DecisionEnforcerAgent()
    result = agent.execute(
        task=f"Enforce decision from debate on: {topic}",
        context={
            'debate_messages': debate_messages,
            'synthesis': synthesis,
            'topic': topic,
        }
    )

    if result.success and auto_spawn:
        mandate_data = result.data.get('mandate', {})
        # Reconstruct mandate for spawning
        mandate = ExecutionMandate(
            chosen_path=mandate_data.get('chosen_path', ''),
            reason=mandate_data.get('reason', ''),
            decision_owner=mandate_data.get('decision_owner', ''),
            kill_criteria=mandate_data.get('kill_criteria', []),
            deadline=mandate_data.get('deadline', ''),
            experiments=mandate_data.get('experiments', []),
            spawned_tasks=[
                SpawnedTask(**t) for t in mandate_data.get('spawned_tasks', [])
            ]
        )
        task_ids = agent.spawn_tasks_from_mandate(mandate)
        result.data['task_ids'] = task_ids

    return result.to_dict()
