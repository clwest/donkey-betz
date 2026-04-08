"""
Classification Integration Service
==================================

Session 349: Bridges QueryClassifier to PersonalAIAssistant for intelligent routing.

This service provides:
1. Pre-classification of user messages before GPT calls
2. Tool filtering based on query type (QUESTION = no tools)
3. Clarification tracking to avoid over-asking
4. Structured delegation briefs for agent calls
5. Parameter validation before tool execution

Key Behaviors:
- QUESTION/CONVERSATION: Disable tools, answer directly
- CREATION/WORKFLOW/ANALYSIS: Enable appropriate tools
- Low confidence (<0.6): Consider clarification
- Priority phrases override keyword classification
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ClarificationState:
    """Tracks clarification questions asked in a conversation."""
    clarifications_asked: int = 0
    max_clarifications: int = 1  # Default: allow 1 clarifying question
    last_clarification_type: Optional[str] = None
    missing_parameters: List[str] = field(default_factory=list)

    def can_ask_clarification(self) -> bool:
        """Check if we can still ask a clarifying question."""
        return self.clarifications_asked < self.max_clarifications

    def record_clarification(self, clarification_type: str, missing_params: List[str] = None):
        """Record that a clarification was asked."""
        self.clarifications_asked += 1
        self.last_clarification_type = clarification_type
        if missing_params:
            self.missing_parameters = missing_params


@dataclass
class DelegationBrief:
    """
    Structured brief for delegating to an agent.

    This ensures consistent, complete information is passed to agents
    instead of ad-hoc tool arguments.
    """
    agent_name: str
    task_objective: str  # One-sentence description
    deliverable_type: str  # image, video, audio, research, etc.
    style_preferences: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    reference_ids: List[str] = field(default_factory=list)
    count: int = 1
    priority: str = "normal"  # normal, high, urgent
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'agent_name': self.agent_name,
            'task_objective': self.task_objective,
            'deliverable_type': self.deliverable_type,
            'style_preferences': self.style_preferences,
            'constraints': self.constraints,
            'reference_ids': self.reference_ids,
            'count': self.count,
            'priority': self.priority,
            'context': self.context,
        }

    def is_complete(self) -> bool:
        """Check if the brief has minimum required information."""
        return bool(self.agent_name and self.task_objective and self.deliverable_type)

    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields."""
        missing = []
        if not self.agent_name:
            missing.append('agent_name')
        if not self.task_objective:
            missing.append('task_objective')
        if not self.deliverable_type:
            missing.append('deliverable_type')
        return missing


@dataclass
class ClassificationDecision:
    """
    The decision made by the classification integration service.

    This tells the PersonalAIAssistant how to handle the request.
    """
    query_type: str  # From QueryType enum
    confidence: float
    should_use_tools: bool
    allowed_tool_categories: Set[str]  # e.g., {'image', 'video'} or empty
    should_clarify: bool
    clarification_question: Optional[str]
    suggested_agents: List[str]
    detected_entities: Dict[str, List[str]]
    delegation_brief: Optional[DelegationBrief]
    requires_spider_data: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'query_type': self.query_type,
            'confidence': self.confidence,
            'should_use_tools': self.should_use_tools,
            'allowed_tool_categories': list(self.allowed_tool_categories),
            'should_clarify': self.should_clarify,
            'clarification_question': self.clarification_question,
            'suggested_agents': self.suggested_agents,
            'detected_entities': self.detected_entities,
            'delegation_brief': self.delegation_brief.to_dict() if self.delegation_brief else None,
            'requires_spider_data': self.requires_spider_data,
            'metadata': self.metadata,
        }


# =============================================================================
# TOOL CATEGORY MAPPINGS
# =============================================================================

# Which tool categories are allowed for each query type
QUERY_TYPE_TOOL_CATEGORIES: Dict[str, Set[str]] = {
    'question': set(),  # No tools - answer directly
    'conversation': set(),  # No tools - casual chat
    'creation': {'image', 'video', 'audio', '3d', 'character_training'},
    'workflow': {'workflow', 'image', 'video', 'research'},
    'analysis': {'research', 'competitor', 'customer', 'brand', 'content', 'marketing'},
    'memory': {'memory'},
    'collaboration': {'hive_mind', 'coleadership'},
    'opportunity': {'opportunity', 'revenue'},
    'system': {'system'},
}

# Map tool names to categories for filtering
TOOL_CATEGORIES: Dict[str, str] = {
    # Image tools
    'image_generation_agent': 'image',
    'image_editing_agent': 'image',

    # Video tools
    'video_generation_agent': 'video',
    'video_editing_agent': 'video',
    'talking_character_agent': 'video',

    # Audio tools
    'audio_generation_agent': 'audio',

    # 3D tools
    'three_d_generation_agent': '3d',

    # Training tools
    'character_training_agent': 'character_training',

    # Workflow tools
    'workflow_orchestration_agent': 'workflow',

    # Research tools
    'web_search': 'research',
    'competitor_analysis_agent': 'competitor',
    'customer_research_agent': 'customer',
    'brand_strategy_agent': 'brand',
    'content_strategy_agent': 'content',
    'marketing_strategy_agent': 'marketing',
    'strategic_review': 'research',

    # Collaboration tools
    'coleadership_agent': 'coleadership',

    # Project tools
    'create_project_from_research': 'workflow',
    'create_brand_video': 'video',
}

# Clarification templates for different missing info scenarios
CLARIFICATION_TEMPLATES: Dict[str, str] = {
    'content_type': "I'd be happy to help! Could you clarify what type of content you'd like? For example: a logo, banner, video, or something else?",
    'style': "What style are you envisioning? For example: minimalist, cyberpunk, professional, playful, or something specific?",
    'count': "How many would you like me to create?",
    'subject': "What subject or topic should this be about?",
    'ambiguous': "I want to make sure I understand correctly. Could you tell me a bit more about what you're looking for?",
    'format': "What format works best for you? Image, video, or something else?",
}


# =============================================================================
# CLASSIFICATION INTEGRATION SERVICE
# =============================================================================

class ClassificationIntegrationService:
    """
    Bridges QueryClassifier to PersonalAIAssistant for intelligent routing.

    This service:
    1. Classifies user messages before GPT calls
    2. Determines if tools should be enabled
    3. Tracks clarification state
    4. Builds delegation briefs for agent calls
    5. Validates parameters before tool execution

    Usage:
        service = ClassificationIntegrationService()
        decision = service.classify_and_decide(message, clarification_state)

        if decision.should_clarify:
            return decision.clarification_question
        elif decision.should_use_tools:
            # Include only allowed tools in GPT call
            tools = filter_tools(all_tools, decision.allowed_tool_categories)
        else:
            # No tools - direct answer
            tools = None
    """

    def __init__(self):
        """Initialize the service."""
        self._classifier = None

    @property
    def classifier(self):
        """Lazy-load the QueryClassifier."""
        if self._classifier is None:
            try:
                from core.super_platform.query_classifier import QueryClassifier
                self._classifier = QueryClassifier()
            except ImportError as e:
                logger.error(f"Failed to import QueryClassifier: {e}")
                raise
        return self._classifier

    def classify_and_decide(
        self,
        message: str,
        clarification_state: Optional[ClarificationState] = None,
        conversation_context: Optional[List[Dict[str, str]]] = None
    ) -> ClassificationDecision:
        """
        Classify a message and decide how to handle it.

        Args:
            message: The user's message
            clarification_state: Current clarification tracking state
            conversation_context: Recent conversation for context

        Returns:
            ClassificationDecision with routing instructions
        """
        if clarification_state is None:
            clarification_state = ClarificationState()

        # Step 1: Classify the message
        classification = self.classifier.classify(message)
        query_type = classification.primary_type.value
        confidence = classification.confidence

        logger.info(
            f"[Classification] Type: {query_type}, "
            f"Confidence: {confidence:.2f}, "
            f"Entities: {classification.detected_entities}"
        )

        # Step 2: Determine tool categories for this query type
        allowed_categories = QUERY_TYPE_TOOL_CATEGORIES.get(query_type, set())
        should_use_tools = len(allowed_categories) > 0

        # Step 3: Check if clarification is needed
        should_clarify = False
        clarification_question = None

        if should_use_tools and clarification_state.can_ask_clarification():
            # Check for low confidence
            if confidence < 0.6:
                should_clarify = True
                clarification_question = CLARIFICATION_TEMPLATES['ambiguous']
                logger.info(f"[Clarification] Low confidence ({confidence:.2f}), suggesting clarification")

            # Check for missing content type in creation requests
            elif query_type == 'creation':
                entities = classification.detected_entities
                if 'content_type' not in entities or not entities.get('content_type'):
                    # Try to infer from keywords
                    message_lower = message.lower()
                    has_image_hint = any(w in message_lower for w in ['logo', 'banner', 'image', 'picture', 'illustration'])
                    has_video_hint = any(w in message_lower for w in ['video', 'animate', 'animation', 'clip'])

                    if not has_image_hint and not has_video_hint:
                        should_clarify = True
                        clarification_question = CLARIFICATION_TEMPLATES['content_type']
                        logger.info("[Clarification] Missing content type for creation request")

        # Step 4: Build delegation brief if this is an actionable request
        delegation_brief = None
        if should_use_tools and not should_clarify:
            delegation_brief = self._build_delegation_brief(
                message=message,
                classification=classification,
                query_type=query_type
            )

        # Step 5: Build the decision
        decision = ClassificationDecision(
            query_type=query_type,
            confidence=confidence,
            should_use_tools=should_use_tools,
            allowed_tool_categories=allowed_categories,
            should_clarify=should_clarify,
            clarification_question=clarification_question,
            suggested_agents=classification.suggested_agents,
            detected_entities=classification.detected_entities,
            delegation_brief=delegation_brief,
            requires_spider_data=classification.requires_spider_data,
            metadata={
                'secondary_types': [t.value for t in classification.secondary_types],
                'is_urgent': classification.is_urgent,
                'detected_keywords': classification.detected_keywords,
            }
        )

        return decision

    def _build_delegation_brief(
        self,
        message: str,
        classification,
        query_type: str
    ) -> DelegationBrief:
        """
        Build a structured delegation brief from classification results.

        Args:
            message: Original user message
            classification: ClassificationResult from QueryClassifier
            query_type: The primary query type

        Returns:
            DelegationBrief with structured information
        """
        entities = classification.detected_entities

        # Determine deliverable type
        content_types = entities.get('content_type', [])
        deliverable_type = content_types[0] if content_types else 'unknown'

        # Extract styles
        styles = entities.get('style', [])

        # Determine agent
        suggested_agents = classification.suggested_agents
        agent_name = suggested_agents[0] if suggested_agents else self._infer_agent(query_type, deliverable_type)

        # Extract count (look for numbers in message)
        count = self._extract_count(message)

        # Determine priority
        priority = 'urgent' if classification.is_urgent else 'normal'

        brief = DelegationBrief(
            agent_name=agent_name,
            task_objective=message[:200],  # Use message as objective
            deliverable_type=deliverable_type,
            style_preferences=styles,
            constraints=[],
            reference_ids=[],
            count=count,
            priority=priority,
            context={
                'original_message': message,
                'detected_entities': entities,
                'query_type': query_type,
            }
        )

        return brief

    def _infer_agent(self, query_type: str, deliverable_type: str) -> str:
        """Infer the best agent based on query type and deliverable."""
        # Default agent mapping
        if query_type == 'creation':
            type_to_agent = {
                'image': 'ImageAgent',
                'logo': 'ImageAgent',
                'banner': 'ImageAgent',
                'illustration': 'ImageAgent',
                'video': 'VideoAgent',
                'animation': 'VideoAgent',
                'audio': 'AudioAgent',
                'voiceover': 'AudioAgent',
                '3d': 'ThreeDAgent',
                '3d model': 'ThreeDAgent',
            }
            return type_to_agent.get(deliverable_type, 'ImageAgent')

        elif query_type == 'workflow':
            return 'WorkflowAgent'

        elif query_type == 'analysis':
            return 'ResearchAgent'

        else:
            return 'ThinkingAgent'  # Apr 2026: was PersonalAssistantAgent (deprecated)

    def _extract_count(self, message: str) -> int:
        """Extract count from message like 'create 3 logos'."""
        import re

        # Look for patterns like "3 logos", "create 5", etc.
        patterns = [
            r'(\d+)\s+(?:logo|image|banner|video|thumbnail)s?',
            r'create\s+(\d+)',
            r'make\s+(\d+)',
            r'generate\s+(\d+)',
        ]

        message_lower = message.lower()
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                return min(int(match.group(1)), 10)  # Cap at 10

        return 1  # Default to 1

    def filter_tools_by_categories(
        self,
        all_tools: List[Dict[str, Any]],
        allowed_categories: Set[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter tool definitions to only include allowed categories.

        Args:
            all_tools: Full list of tool definitions
            allowed_categories: Set of allowed category names

        Returns:
            Filtered list of tools
        """
        if not allowed_categories:
            return []

        filtered = []
        for tool in all_tools:
            tool_name = tool.get('function', {}).get('name', '')
            category = TOOL_CATEGORIES.get(tool_name)

            if category and category in allowed_categories:
                filtered.append(tool)

        logger.debug(f"Filtered {len(all_tools)} tools to {len(filtered)} for categories: {allowed_categories}")
        return filtered

    def validate_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        delegation_brief: Optional[DelegationBrief] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a tool call before execution.

        Args:
            tool_name: Name of the tool being called
            arguments: Arguments passed to the tool
            delegation_brief: Optional brief for context

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation - tool must exist
        if tool_name not in TOOL_CATEGORIES:
            return False, f"Unknown tool: {tool_name}"

        # Tool-specific validation
        if tool_name == 'image_generation_agent':
            if not arguments.get('prompt'):
                return False, "Image generation requires a prompt"

        elif tool_name == 'video_generation_agent':
            if not arguments.get('prompt') and not arguments.get('image_id'):
                return False, "Video generation requires a prompt or image_id"

        elif tool_name == 'image_editing_agent':
            if not arguments.get('image_id'):
                return False, "Image editing requires an image_id"
            if not arguments.get('operation'):
                return False, "Image editing requires an operation"

        elif tool_name == 'workflow_orchestration_agent':
            if not arguments.get('workflow') and not arguments.get('topic'):
                return False, "Workflow requires a workflow type or topic"

        return True, None


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_service_instance: Optional[ClassificationIntegrationService] = None


def get_classification_integration_service() -> ClassificationIntegrationService:
    """Get the singleton ClassificationIntegrationService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = ClassificationIntegrationService()
    return _service_instance
