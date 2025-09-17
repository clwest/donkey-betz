"""
Agent Instruction Parser
Extracts executable tasks from Income Builder generated plans
Transforms AI-generated content into agent-ready instructions
"""

import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentInstruction:
    """Represents a single instruction for an agent"""
    agent_type: str
    agent_name: str
    action: str
    tool: str
    expected_outcome: str
    parameters: Dict[str, Any]
    step_number: int
    week: str
    original_text: str


class AgentInstructionParser:
    """Parses Income Builder plans into executable agent instructions"""

    # Agent mapping from plan references to actual agent types
    AGENT_MAPPING = {
        'Content Creator Agent': 'content-creator',
        'Content-Creator Agent': 'content-creator',
        'ML Analytics & Optimization': 'ml-analytics',
        'ML Analytics': 'ml-analytics',
        'AI Content Studio': 'ai-content-studio',
        'Publishing Automation System': 'publishing-automation',
        'Real-time Collaboration Tools': 'collaboration-tools',
        'Revenue Engine': 'revenue-engine',
        'Agent Network': 'agent-network',
        'Distribution System': 'distribution-system',

        # Map to actual registered agents
        'Social Media Manager': 'social-media-manager',
        'SEO Optimizer': 'seo-optimizer',
        'Email Marketing': 'email-marketer',
        'Content Writer': 'content-writer',
        'Data Analyst': 'data-analyst',
        'Market Researcher': 'market-researcher',
    }

    def __init__(self):
        self.instructions = []

    def parse_plan(self, plan_content: str) -> List[AgentInstruction]:
        """
        Parse a complete action plan into individual agent instructions

        Args:
            plan_content: The markdown content from Income Builder

        Returns:
            List of AgentInstruction objects ready for execution
        """
        self.instructions = []

        # Split content into steps
        steps = self._extract_steps(plan_content)

        for step_num, step_content in enumerate(steps, 1):
            # Extract week information
            week = self._extract_week(step_content)

            # Find all action items in this step
            actions = self._extract_actions(step_content)

            for action in actions:
                instruction = self._create_instruction(
                    action,
                    step_num,
                    week,
                    step_content
                )
                if instruction:
                    self.instructions.append(instruction)

        logger.info(f"Parsed {len(self.instructions)} agent instructions from plan")
        return self.instructions

    def _extract_steps(self, content: str) -> List[str]:
        """Extract individual steps from the plan"""
        # Look for Step headers
        step_pattern = r'### Step \d+:.*?(?=### Step \d+:|## |$)'
        steps = re.findall(step_pattern, content, re.DOTALL)

        # Also check for Week-based sections
        if not steps:
            week_pattern = r'# Step \d+: Week \d+:.*?(?=# Step \d+:|## |$)'
            steps = re.findall(week_pattern, content, re.DOTALL)

        return steps

    def _extract_week(self, step_content: str) -> str:
        """Extract week information from step content"""
        week_match = re.search(r'Week (\d+)', step_content)
        if week_match:
            return f"Week {week_match.group(1)}"
        return "Immediate"

    def _extract_actions(self, step_content: str) -> List[Dict[str, str]]:
        """Extract action items from step content"""
        actions = []

        # Pattern to match action blocks
        # Looking for - **Action:** followed by - **Tool:** and - **Expected Outcome:**
        action_pattern = r'- \*\*Action:\*\* (.*?)(?=- \*\*|$)'
        tool_pattern = r'- \*\*Tool:\*\* (.*?)(?=- \*\*|$)'
        outcome_pattern = r'- \*\*Expected Outcome:\*\* (.*?)(?=- \*\*|###|$)'

        # ALSO look for bold agent references in GPT-5 format
        # Pattern: **Agent Name** or **Agent Name Agent**
        bold_agent_pattern = r'\*\*([^*]+(?:Agent|agent)[^*]*)\*\*'

        # Find all actions in the content
        action_matches = re.finditer(action_pattern, step_content, re.DOTALL)

        for match in action_matches:
            action_text = match.group(1).strip()

            # Find the corresponding tool and outcome
            remaining_text = step_content[match.end():]

            tool_match = re.search(tool_pattern, remaining_text)
            outcome_match = re.search(outcome_pattern, remaining_text)

            # If no tool found, try to extract from bold text in action
            tool_name = tool_match.group(1).strip() if tool_match else ''
            if not tool_name:
                bold_match = re.search(bold_agent_pattern, action_text)
                if bold_match:
                    tool_name = bold_match.group(1).strip()
                    logger.info(f"Found agent in bold text: {tool_name}")

            action_dict = {
                'action': action_text,
                'tool': tool_name,
                'outcome': outcome_match.group(1).strip() if outcome_match else ''
            }

            actions.append(action_dict)

        # ALSO scan for any lines with "Utilize" or "Use" followed by bold agents
        utilize_pattern = r'(?:Utilize|Use|Deploy|Leverage|Activate)\s+.*?\*\*([^*]+Agent[^*]*)\*\*'
        utilize_matches = re.finditer(utilize_pattern, step_content, re.IGNORECASE)

        for match in utilize_matches:
            agent_name = match.group(1).strip()
            full_line = step_content[match.start():match.end()]

            # Create an action from this
            action_dict = {
                'action': full_line,
                'tool': agent_name,
                'outcome': f"Successfully executed {agent_name}"
            }
            actions.append(action_dict)
            logger.info(f"Found GPT-5 style agent reference: {agent_name}")

        return actions

    def _create_instruction(
        self,
        action: Dict[str, str],
        step_num: int,
        week: str,
        full_content: str
    ) -> Optional[AgentInstruction]:
        """Create an AgentInstruction from parsed action data"""

        if not action['tool']:
            return None

        # Map tool to agent type
        agent_type = self._map_to_agent(action['tool'])
        if not agent_type:
            logger.warning(f"No agent mapping for tool: {action['tool']}")
            return None

        # Extract parameters from action text
        parameters = self._extract_parameters(action['action'])

        return AgentInstruction(
            agent_type=agent_type,
            agent_name=action['tool'],
            action=action['action'],
            tool=action['tool'],
            expected_outcome=action['outcome'],
            parameters=parameters,
            step_number=step_num,
            week=week,
            original_text=full_content[:500]  # Keep first 500 chars for context
        )

    def _map_to_agent(self, tool_name: str) -> Optional[str]:
        """Map tool name to agent type"""
        # Direct mapping
        if tool_name in self.AGENT_MAPPING:
            return self.AGENT_MAPPING[tool_name]

        # Fuzzy matching
        tool_lower = tool_name.lower()
        for key, value in self.AGENT_MAPPING.items():
            if key.lower() in tool_lower or tool_lower in key.lower():
                return value

        # Default mapping based on keywords
        if 'content' in tool_lower:
            return 'content-creator'
        elif 'analytic' in tool_lower or 'ml' in tool_lower:
            return 'ml-analytics'
        elif 'publish' in tool_lower:
            return 'publishing-automation'

        return None

    def _extract_parameters(self, action_text: str) -> Dict[str, Any]:
        """Extract parameters from action text"""
        parameters = {}

        # Extract quoted strings as parameters
        quoted = re.findall(r'"([^"]*)"', action_text)
        if quoted:
            parameters['keywords'] = quoted

        # Extract numbers
        numbers = re.findall(r'\b(\d+)\b', action_text)
        if numbers:
            parameters['count'] = int(numbers[0]) if numbers else None

        # Extract specific directives
        if 'generate' in action_text.lower():
            parameters['action_type'] = 'generate'
        elif 'analyze' in action_text.lower():
            parameters['action_type'] = 'analyze'
        elif 'create' in action_text.lower():
            parameters['action_type'] = 'create'
        elif 'schedule' in action_text.lower():
            parameters['action_type'] = 'schedule'

        # Extract platform mentions
        platforms = ['instagram', 'twitter', 'facebook', 'linkedin', 'tiktok']
        for platform in platforms:
            if platform in action_text.lower():
                if 'platforms' not in parameters:
                    parameters['platforms'] = []
                parameters['platforms'].append(platform)

        return parameters

    def to_json(self) -> str:
        """Convert parsed instructions to JSON"""
        return json.dumps([
            {
                'agent_type': inst.agent_type,
                'agent_name': inst.agent_name,
                'action': inst.action,
                'tool': inst.tool,
                'expected_outcome': inst.expected_outcome,
                'parameters': inst.parameters,
                'step_number': inst.step_number,
                'week': inst.week
            }
            for inst in self.instructions
        ], indent=2)

    def get_execution_order(self) -> List[List[AgentInstruction]]:
        """
        Group instructions by execution order (by week/step)
        Returns list of instruction groups that can be executed in parallel
        """
        from collections import defaultdict

        grouped = defaultdict(list)
        for inst in self.instructions:
            key = f"{inst.week}_{inst.step_number}"
            grouped[key].append(inst)

        # Sort by week and step number
        sorted_groups = sorted(grouped.items(), key=lambda x: x[0])
        return [group[1] for group in sorted_groups]