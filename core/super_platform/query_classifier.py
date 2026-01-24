"""
Query Classifier - Understands User Intent

This module classifies user input to determine the optimal routing path
through the Super Platform. It distinguishes between:

- Questions (need spider intelligence)
- Creation requests (need agent execution)
- Workflow requests (need multi-step orchestration)
- Memory queries (need Memory Palace)
- Collaboration requests (need Hive Mind)
- Analysis requests (need research + agents)

Session 264: Phase 1 Foundation
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class QueryType(Enum):
    """The primary types of user queries."""
    QUESTION = "question"           # Informational - uses spider data
    CREATION = "creation"           # Generate content - uses agents
    WORKFLOW = "workflow"           # Multi-step - uses orchestrator
    ANALYSIS = "analysis"           # Research + insight - uses research agents
    MEMORY = "memory"               # Recall past interactions
    COLLABORATION = "collaboration" # Hive mind / multi-agent
    OPPORTUNITY = "opportunity"     # Revenue-focused queries
    SYSTEM = "system"               # Platform status, agent info
    CONVERSATION = "conversation"   # General chat, greeting


@dataclass
class ClassificationResult:
    """Result of query classification."""
    primary_type: QueryType
    confidence: float
    secondary_types: List[QueryType]
    detected_keywords: List[str]
    detected_entities: Dict[str, Any]
    suggested_agents: List[str]
    requires_spider_data: bool
    requires_memory: bool
    requires_mood_check: bool
    is_urgent: bool

    def to_dict(self) -> dict:
        return {
            'primary_type': self.primary_type.value,
            'confidence': self.confidence,
            'secondary_types': [t.value for t in self.secondary_types],
            'detected_keywords': self.detected_keywords,
            'detected_entities': self.detected_entities,
            'suggested_agents': self.suggested_agents,
            'requires_spider_data': self.requires_spider_data,
            'requires_memory': self.requires_memory,
            'requires_mood_check': self.requires_mood_check,
            'is_urgent': self.is_urgent,
        }


class QueryClassifier:
    """
    Classifies user queries to determine optimal routing.

    Uses keyword matching, pattern recognition, and entity detection
    to understand user intent with high accuracy.
    """

    # Keyword patterns for each query type
    QUERY_PATTERNS = {
        QueryType.QUESTION: {
            'keywords': [
                'what', 'who', 'where', 'when', 'why', 'how',
                'tell me', 'explain', 'describe', 'trending', 'latest',
                'news', 'update', 'happening', 'going on', 'current',
                'status of', 'price of', 'value of', 'cost of',
                'is there', 'are there', 'do you know', 'can you tell',
            ],
            'patterns': [
                r'^what\s+is\s+',
                r'^how\s+(?:do|does|can|should)',
                r'^why\s+(?:is|are|do|does)',
                r'^when\s+(?:is|was|will)',
                r'trending\s+(?:in|on|right now)',
                r'latest\s+(?:news|update|on)',
            ],
            'weight': 1.0,
        },
        QueryType.CREATION: {
            'keywords': [
                'create', 'generate', 'make', 'design', 'build',
                'draw', 'render', 'produce', 'craft', 'compose',
                'image', 'video', 'audio', 'logo', 'thumbnail',
                'illustration', 'artwork', 'graphic', 'banner',
                'icon', 'avatar', 'portrait', 'landscape', 'scene',
                'animation', 'gif', 'motion', '3d', 'model',
                'voiceover', 'narration', 'speech', 'sound',
            ],
            'patterns': [
                r'^(?:create|generate|make|design)\s+(?:a|an|the|some)',
                r'(?:image|video|audio|logo)\s+(?:of|for|with)',
                r'(?:in|using)\s+(?:style|aesthetic)',
                r'(?:pixar|disney|anime|cyberpunk|watercolor)\s+style',
            ],
            'weight': 1.2,  # Higher weight - creation is core function
        },
        QueryType.WORKFLOW: {
            'keywords': [
                'workflow', 'batch', 'series', 'package', 'kit',
                'brand identity', 'full set', 'complete', 'multiple',
                'research and create', 'thumbnail package', 'logo to video',
                'product photography', 'brand kit', 'social media pack',
            ],
            'patterns': [
                r'(?:brand|logo|thumbnail|product)\s+(?:package|kit|series)',
                r'research\s+and\s+(?:create|generate|make)',
                r'(?:full|complete)\s+(?:set|package|kit)',
                r'batch\s+(?:of|generation)',
            ],
            'weight': 1.3,  # Workflows are high-value
        },
        QueryType.ANALYSIS: {
            'keywords': [
                'analyze', 'analyse', 'review', 'assess', 'evaluate',
                'compare', 'contrast', 'examine', 'investigate',
                'research', 'study', 'look into', 'dig into',
                'find out', 'discover', 'explore', 'understand',
            ],
            'patterns': [
                r'^(?:analyze|analyse|review|assess)\s+',
                r'^(?:compare|contrast)\s+.+\s+(?:with|to|and)',
                r'^research\s+(?:about|on|into)',
            ],
            'weight': 1.0,
        },
        QueryType.MEMORY: {
            'keywords': [
                'remember', 'recall', 'last time', 'before', 'previous',
                'we did', 'you made', 'you created', 'history',
                'past', 'earlier', 'yesterday', 'last week',
                'what did we', 'show me what', 'find my',
            ],
            'patterns': [
                r'(?:remember|recall)\s+(?:when|what|how)',
                r'last\s+(?:time|week|month|session)',
                r'(?:we|you)\s+(?:did|made|created)\s+(?:before|earlier)',
                r'(?:my|our)\s+(?:history|past|previous)',
            ],
            'weight': 1.0,
        },
        QueryType.COLLABORATION: {
            'keywords': [
                'team', 'together', 'hive', 'collective', 'collaborate',
                'all agents', 'what do they think', 'group', 'consensus',
                'brainstorm', 'vote', 'decide together', 'council',
                'conference', 'meeting', 'discussion',
            ],
            'patterns': [
                r'(?:hive|collective)\s+(?:mind|intelligence)',
                r'(?:all|multiple)\s+agents?\s+(?:think|say|work)',
                r'(?:team|group)\s+(?:effort|work|collaboration)',
                r'(?:brainstorm|discuss)\s+(?:with|together)',
            ],
            'weight': 1.1,
        },
        QueryType.OPPORTUNITY: {
            'keywords': [
                'opportunity', 'opportunities', 'money', 'revenue',
                'profit', 'earn', 'income', 'monetize', 'sell',
                'market', 'trend', 'demand', 'gig', 'freelance',
                'job', 'client', 'customer', 'business',
            ],
            'patterns': [
                r'(?:make|earn)\s+(?:money|income|revenue)',
                r'(?:find|discover|show)\s+(?:opportunities|gigs|jobs)',
                r'(?:what|how)\s+(?:can|should)\s+(?:I|we)\s+(?:sell|monetize)',
                r'(?:market|business)\s+(?:opportunity|potential)',
            ],
            'weight': 1.2,
        },
        QueryType.SYSTEM: {
            'keywords': [
                'agents', 'spiders', 'system', 'platform', 'status',
                'health', 'running', 'active', 'available',
                'capabilities', 'features', 'what can you do',
                'help', 'how to use', 'settings', 'config',
            ],
            'patterns': [
                r'^(?:list|show|what)\s+(?:agents?|spiders?)',
                r'(?:system|platform)\s+(?:status|health)',
                r'what\s+(?:can|do)\s+you\s+(?:do|offer)',
                r'(?:how|what)\s+(?:to|can)\s+(?:use|do)',
            ],
            'weight': 0.9,
        },
        QueryType.CONVERSATION: {
            'keywords': [
                'hello', 'hi', 'hey', 'good morning', 'good evening',
                'thanks', 'thank you', 'bye', 'goodbye', 'see you',
                'how are you', 'nice', 'great', 'awesome', 'cool',
                'okay', 'ok', 'sure', 'yes', 'no', 'maybe',
            ],
            'patterns': [
                r'^(?:hi|hello|hey|greetings)',
                r'^(?:thanks?|thank\s+you)',
                r'^(?:bye|goodbye|see\s+you)',
                r'^(?:good\s+(?:morning|afternoon|evening|night))',
            ],
            'weight': 0.8,  # Lower weight - often combined with other intents
        },
    }

    # Entity detection patterns
    ENTITY_PATTERNS = {
        'style': [
            'pixar', 'disney', 'dreamworks', 'ghibli', 'anime', 'manga',
            'cyberpunk', 'steampunk', 'fantasy', 'scifi', 'gothic',
            'watercolor', 'oil painting', 'pencil', 'charcoal',
            'pop art', 'art deco', 'minimalist', 'realistic',
            'looney tunes', 'simpsons', 'south park', 'rick and morty',
        ],
        'content_type': [
            'image', 'video', 'audio', 'logo', 'thumbnail', '3d model',
            'animation', 'illustration', 'portrait', 'landscape',
            'icon', 'banner', 'graphic', 'voiceover', 'narration',
        ],
        'platform': [
            'youtube', 'instagram', 'twitter', 'tiktok', 'linkedin',
            'etsy', 'gumroad', 'fiverr', 'upwork', 'behance', 'dribbble',
        ],
        'agent': [
            'image agent', 'video agent', 'audio agent', 'research agent',
            'content strategy', 'seo', 'brand identity', 'creative director',
        ],
        'topic': [
            'ai', 'artificial intelligence', 'machine learning', 'crypto',
            'bitcoin', 'ethereum', 'nft', 'tech', 'startup', 'programming',
            'design', 'marketing', 'business', 'finance', 'health',
        ],
    }

    # Urgency indicators
    URGENCY_KEYWORDS = [
        'urgent', 'asap', 'immediately', 'right now', 'quickly',
        'fast', 'hurry', 'deadline', 'emergency', 'critical',
        'important', 'priority', 'rush', 'need it now',
    ]

    # Session 300: Priority phrases that OVERRIDE keyword-based classification
    # These phrases are checked first and immediately return the specified type
    # This prevents "generate a competitor analysis" from being classified as CREATION
    # Session 349: Priority phrases override keyword-based classification
    # These are checked FIRST and take precedence over keyword matching
    PRIORITY_PHRASES = {
        QueryType.QUESTION: [
            # Style/advice questions should NOT trigger tools
            'what style', 'which style', 'best style', 'what works best',
            'what would work', 'what do you recommend', 'what should i use',
            'what colors', 'which colors', 'what fonts', 'which fonts',
            'ideas for', 'suggestions for', 'recommend for', 'advice on',
            'how should', 'how would', 'how do i', 'what are trending',
            'what is trending', "what's trending", 'help me decide',
            'help me choose', 'opinion on', 'thoughts on',
        ],
        QueryType.ANALYSIS: [
            'competitor analysis', 'competitive analysis', 'market analysis',
            'swot analysis', 'analyze competitors', 'research the market',
            'business landscape', 'industry analysis', 'market research',
            'customer research', 'customer pain points', 'customer personas',
            'target audience', 'user pain points', 'customer needs',
            'pain point analysis', 'sentiment analysis', 'user research',
        ],
        QueryType.WORKFLOW: [
            # Session 349: Expanded patterns for research+create combinations
            'research and create', 'research and make', 'research and generate',
            'research then create', 'research then make',
            'research competitors and create', 'research market and create',
            'brand identity package', 'thumbnail package',
            'logo package', 'full brand kit', 'complete package',
        ],
    }

    # Agent suggestions based on query type and entities
    AGENT_SUGGESTIONS = {
        QueryType.CREATION: {
            'image': ['ImageAgent', 'PromptEngineeringAgent'],
            'video': ['VideoAgent', 'ImageAgent'],
            'audio': ['AudioAgent'],
            'logo': ['ImageAgent', 'BrandIdentityAgent'],
            'thumbnail': ['ImageAgent', 'SEOOptimizerAgent'],
            '3d': ['3DGenerationAgent'],
            'default': ['CreationAgent', 'PromptEngineeringAgent'],
        },
        QueryType.WORKFLOW: {
            'brand': ['WorkflowOrchestrationAgent', 'BrandIdentityAgent', 'ImageAgent'],
            'thumbnail': ['WorkflowOrchestrationAgent', 'ResearchAgent', 'ImageAgent'],
            'research': ['WorkflowOrchestrationAgent', 'ResearchAgent'],
            'default': ['WorkflowOrchestrationAgent'],
        },
        QueryType.ANALYSIS: {
            'competitor': ['CompetitorAnalysisAgent', 'ResearchAgent'],
            'market': ['CompetitorAnalysisAgent', 'ResearchAgent', 'TrendAnalysisAgent'],
            'customer': ['CustomerResearchAgent', 'ResearchAgent'],
            'persona': ['CustomerResearchAgent'],
            'pain': ['CustomerResearchAgent'],  # pain points
            'default': ['ResearchAgent', 'TrendAnalysisAgent', 'ContentStrategyAgent'],
        },
        QueryType.QUESTION: {
            'default': ['ResearchAgent'],
        },
        QueryType.COLLABORATION: {
            'default': ['CTOAgent', 'COOAgent', 'CreativeDirectorAgent'],
        },
        QueryType.OPPORTUNITY: {
            'default': ['OpportunityScoringAgent', 'TrendAnalysisAgent', 'ContentStrategyAgent'],
        },
    }

    def __init__(self):
        """Initialize the classifier."""
        # Pre-compile regex patterns for efficiency
        self._compiled_patterns = {}
        for query_type, config in self.QUERY_PATTERNS.items():
            self._compiled_patterns[query_type] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in config.get('patterns', [])
            ]

    def classify(self, query: str) -> ClassificationResult:
        """
        Classify a user query to determine intent and routing.

        Args:
            query: The user's input text

        Returns:
            ClassificationResult with type, confidence, and metadata
        """
        query_lower = query.lower().strip()

        # Session 300: Check priority phrases FIRST
        # These override keyword-based classification to handle cases like
        # "Generate a competitor analysis" which should be ANALYSIS not CREATION
        priority_match = self._check_priority_phrases(query_lower)
        if priority_match:
            query_type, matched_phrase = priority_match
            # Detect entities and suggest agents based on the priority match
            detected_entities = self._detect_entities(query_lower)
            suggested_agents = self._suggest_agents(query_type, detected_entities, query_lower)
            is_urgent = any(kw in query_lower for kw in self.URGENCY_KEYWORDS)

            return ClassificationResult(
                primary_type=query_type,
                confidence=0.95,  # High confidence for priority phrase match
                secondary_types=[],
                detected_keywords=[matched_phrase],
                detected_entities=detected_entities,
                suggested_agents=suggested_agents,
                requires_spider_data=query_type in [
                    QueryType.QUESTION, QueryType.ANALYSIS,
                    QueryType.OPPORTUNITY, QueryType.WORKFLOW
                ],
                requires_memory=False,
                requires_mood_check=query_type in [
                    QueryType.CREATION, QueryType.COLLABORATION, QueryType.WORKFLOW
                ],
                is_urgent=is_urgent,
            )

        # Score each query type
        scores = {}
        keyword_matches = {}

        for query_type, config in self.QUERY_PATTERNS.items():
            score = 0.0
            matches = []

            # Check keywords
            for keyword in config['keywords']:
                if keyword in query_lower:
                    score += 1.0
                    matches.append(keyword)

            # Check regex patterns (worth more)
            for pattern in self._compiled_patterns[query_type]:
                if pattern.search(query_lower):
                    score += 2.0
                    matches.append(f"pattern:{pattern.pattern}")

            # Apply weight
            score *= config.get('weight', 1.0)

            scores[query_type] = score
            keyword_matches[query_type] = matches

        # Determine primary type
        if not any(scores.values()):
            # No matches - default to conversation
            primary_type = QueryType.CONVERSATION
            confidence = 0.5
        else:
            # Get highest scoring type
            primary_type = max(scores, key=scores.get)
            max_score = scores[primary_type]

            # Calculate confidence based on score distribution
            total_score = sum(scores.values())
            if total_score > 0:
                confidence = min(0.95, (max_score / total_score) + 0.3)
            else:
                confidence = 0.5

        # Get secondary types (other high-scoring types)
        secondary_types = [
            qt for qt, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
            if qt != primary_type and score > 0
        ][:3]

        # Detect entities
        detected_entities = self._detect_entities(query_lower)

        # Suggest agents based on type, entities, and query keywords
        suggested_agents = self._suggest_agents(primary_type, detected_entities, query_lower)

        # Check urgency
        is_urgent = any(kw in query_lower for kw in self.URGENCY_KEYWORDS)

        # Session 803: Detect meta/system questions that don't need external data
        # These are questions about the platform itself, not requiring spider intelligence
        meta_question_patterns = [
            'tell me about this system', 'what is this system', 'what can you do',
            'who are you', 'what are you', 'how do you work', 'what is this platform',
            'explain yourself', 'introduce yourself', 'your capabilities',
            'what agents', 'list agents', 'show agents', 'available agents',
            'what tools', 'list tools', 'available tools', 'help me understand',
            'how does this work', 'what is donkey', 'about donkey betz',
        ]
        is_meta_question = any(pattern in query_lower for pattern in meta_question_patterns)

        # Determine data requirements
        # Session 803: Skip spider data for meta questions (they don't need external intelligence)
        requires_spider_data = (
            primary_type in [
                QueryType.QUESTION, QueryType.ANALYSIS,
                QueryType.OPPORTUNITY, QueryType.WORKFLOW
            ]
            and not is_meta_question  # Session 803: Meta questions skip spider data
        )
        requires_memory = primary_type == QueryType.MEMORY or 'remember' in query_lower
        requires_mood_check = primary_type in [
            QueryType.CREATION, QueryType.COLLABORATION, QueryType.WORKFLOW
        ]

        return ClassificationResult(
            primary_type=primary_type,
            confidence=confidence,
            secondary_types=secondary_types,
            detected_keywords=keyword_matches.get(primary_type, []),
            detected_entities=detected_entities,
            suggested_agents=suggested_agents,
            requires_spider_data=requires_spider_data,
            requires_memory=requires_memory,
            requires_mood_check=requires_mood_check,
            is_urgent=is_urgent,
        )

    def _detect_entities(self, query: str) -> Dict[str, List[str]]:
        """Detect named entities in the query."""
        entities = {}

        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            found = []
            for pattern in patterns:
                if pattern in query:
                    found.append(pattern)
            if found:
                entities[entity_type] = found

        return entities

    def _suggest_agents(
        self,
        query_type: QueryType,
        entities: Dict[str, List[str]],
        query: str = ""
    ) -> List[str]:
        """Suggest appropriate agents based on query type, entities, and query keywords."""
        suggestions = self.AGENT_SUGGESTIONS.get(query_type, {})

        # Session 300: For ANALYSIS type, check for specific keywords in query
        if query_type == QueryType.ANALYSIS and query:
            query_lower = query.lower()
            # Check for competitor/market analysis keywords
            if 'competitor' in query_lower or 'competitive' in query_lower:
                return suggestions.get('competitor', suggestions.get('default', []))
            if 'market' in query_lower and 'analysis' in query_lower:
                return suggestions.get('market', suggestions.get('default', []))
            if 'customer' in query_lower:
                return suggestions.get('customer', suggestions.get('default', []))
            if 'persona' in query_lower:
                return suggestions.get('persona', suggestions.get('default', []))
            if 'pain' in query_lower and 'point' in query_lower:
                return suggestions.get('pain', suggestions.get('default', []))

        # Check if any entity matches a specific suggestion
        for entity_type, entity_values in entities.items():
            if entity_type == 'content_type':
                for value in entity_values:
                    if value in suggestions:
                        return suggestions[value]

        # Return default for this query type
        return suggestions.get('default', [])

    def _check_priority_phrases(self, query: str) -> Optional[tuple]:
        """
        Session 300: Check for priority phrases that override keyword classification.

        These phrases take precedence over individual keyword matches.
        For example, "generate a competitor analysis" should match ANALYSIS
        because "competitor analysis" is a priority phrase, even though
        "generate" would normally trigger CREATION.

        Args:
            query: The lowercased query string

        Returns:
            Tuple of (QueryType, matched_phrase) or None if no match
        """
        for query_type, phrases in self.PRIORITY_PHRASES.items():
            for phrase in phrases:
                if phrase in query:
                    return (query_type, phrase)
        return None

    def get_routing_decision(self, classification: ClassificationResult) -> dict:
        """
        Convert classification into a routing decision.

        Returns a dict with:
        - use_spider_intelligence: bool
        - use_agent_execution: bool
        - use_workflow: bool
        - use_hive_mind: bool
        - use_memory: bool
        - primary_handler: str
        """
        routing = {
            'use_spider_intelligence': classification.requires_spider_data,
            'use_agent_execution': classification.primary_type in [
                QueryType.CREATION, QueryType.ANALYSIS
            ],
            'use_workflow': classification.primary_type == QueryType.WORKFLOW,
            'use_hive_mind': classification.primary_type == QueryType.COLLABORATION,
            'use_memory': classification.requires_memory,
            'use_opportunity_engine': classification.primary_type == QueryType.OPPORTUNITY,
            'primary_handler': self._get_primary_handler(classification.primary_type),
            'suggested_agents': classification.suggested_agents,
            'priority': 'high' if classification.is_urgent else 'normal',
        }

        return routing

    def _get_primary_handler(self, query_type: QueryType) -> str:
        """Get the primary handler name for a query type."""
        handlers = {
            QueryType.QUESTION: 'spider_intelligence',
            QueryType.CREATION: 'agent_executor',
            QueryType.WORKFLOW: 'workflow_orchestrator',
            QueryType.ANALYSIS: 'research_pipeline',
            QueryType.MEMORY: 'memory_palace',
            QueryType.COLLABORATION: 'hive_mind',
            QueryType.OPPORTUNITY: 'opportunity_engine',
            QueryType.SYSTEM: 'system_info',
            QueryType.CONVERSATION: 'conversation_handler',
        }
        return handlers.get(query_type, 'conversation_handler')
