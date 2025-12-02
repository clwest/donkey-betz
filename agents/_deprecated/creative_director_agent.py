"""
Creative Director AI Agent
===========================

Session 241: Created as part of agent cleanup - building real, valuable agents.
Session 311: Added learning infrastructure hooks for cross-agent knowledge sharing.

This agent provides high-level creative guidance before generation:
- Reviews prompts and suggests improvements
- Ensures consistency across a project
- Provides creative direction based on trends and best practices
- Coordinates with other agents for cohesive output

Example:
    agent = CreativeDirectorAgent(user=request.user)

    # Get creative direction for a prompt
    result = agent.review_prompt("Create a logo for tech startup")
    # Returns: enhanced prompt, style recommendations, color suggestions

    # Get project-level creative direction
    result = agent.establish_creative_direction(
        project_brief="Launching a new SaaS product",
        target_audience="developers"
    )
"""

from __future__ import annotations

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class CreativeDirectorLearningMixin:
    """
    Learning infrastructure mixin for CreativeDirectorAgent.
    Session 311: Enables cross-agent knowledge sharing for creative direction patterns.
    """

    _learning_loop = None
    _memory_service = None
    _agent_model = None

    @property
    def learning_loop(self):
        """Lazy-load LearningLoopService."""
        if self._learning_loop is None:
            try:
                from core.super_platform.learning_loop import get_learning_loop_service
                self._learning_loop = get_learning_loop_service(None)
            except ImportError:
                logger.debug("LearningLoopService not available")
                return None
        return self._learning_loop

    @property
    def memory_service(self):
        """Lazy-load MemoryEmbeddingService."""
        if self._memory_service is None:
            try:
                from core.services.memory_embedding_service import get_memory_embedding_service
                self._memory_service = get_memory_embedding_service()
            except ImportError:
                logger.debug("MemoryEmbeddingService not available")
                return None
        return self._memory_service

    @property
    def agent_model(self):
        """Lazy-load or create Agent model instance."""
        if self._agent_model is None:
            try:
                from core.models_unified_system import Agent
                self._agent_model, _ = Agent.objects.get_or_create(
                    name='CreativeDirectorAgent',
                    defaults={
                        'agent_type': 'deprecated',
                        'specialization': 'creative_direction',
                        'description': 'Provides high-level creative guidance and direction for visual projects.',
                        'is_active': True,
                    }
                )
            except ImportError:
                logger.debug("Agent model not available")
                return None
        return self._agent_model

    def _record_learning_outcome(
        self,
        result: Dict[str, Any],
        task: str,
        context: Dict[str, Any] = None,
        spider_data_used: bool = False
    ):
        """Record execution outcome for XP and pattern learning."""
        if not self.learning_loop:
            return None

        try:
            outcome_id = self.learning_loop.record_outcome(
                query_type='creative_direction',
                query_text=task,
                execution_mode='agent',
                agents_used=['CreativeDirectorAgent'],
                response=str(result)[:500],
                execution_time_ms=result.get('execution_time_ms', 0),
                success=result.get('success', True),
                spider_data_used=spider_data_used,
                scifi_context_used=False,
                context=context or {}
            )
            return outcome_id
        except Exception as e:
            logger.debug(f"Failed to record learning outcome: {e}")
            return None

    def _create_execution_memory(
        self,
        result: Dict[str, Any],
        task: str,
        memory_type: str = "interaction",
        importance: float = 0.5
    ):
        """Create a memory from the creative direction execution."""
        if not self.memory_service or not self.agent_model:
            return None

        try:
            memory = self.memory_service.create_memory(
                agent=self.agent_model,
                title=f"Creative: {task[:50]}...",
                content=str(result)[:500],
                memory_type=memory_type,
                valence="positive" if result.get('success', True) else "negative",
                importance_score=importance,
                source_type='agent_execution',
                tags=['creative_direction', 'design', 'branding']
            )
            return memory
        except Exception as e:
            logger.debug(f"Failed to create execution memory: {e}")
            return None

    def _share_knowledge(
        self,
        knowledge_type: str,
        title: str,
        knowledge_value: Dict[str, Any],
        confidence: float = 0.8
    ):
        """Share learned creative knowledge for cross-agent learning."""
        if not self.agent_model:
            return None

        try:
            from core.models_unified_system import AgentKnowledgeSource

            type_mapping = {
                'style': 'creative_pattern',
                'color': 'creative_pattern',
                'direction': 'creative_pattern',
                'design': 'trend',
                'brand': 'creative_pattern',
            }
            mapped_type = type_mapping.get(knowledge_type, 'creative_pattern')

            knowledge, created = AgentKnowledgeSource.objects.update_or_create(
                agent=self.agent_model,
                title=title,
                knowledge_type=mapped_type,
                defaults={
                    'summary': json.dumps(knowledge_value),
                    'confidence_score': confidence,
                    'is_active': True,
                }
            )
            return knowledge
        except Exception as e:
            logger.debug(f"Failed to share knowledge: {e}")
            return None

    def _get_shared_knowledge(
        self,
        knowledge_type: str = None,
        title_contains: str = None,
        from_agents: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve knowledge from other agents and record the learning transfer."""
        try:
            from core.models_unified_system import AgentKnowledgeSource, AgentLearningConnection, KnowledgeTransfer

            queryset = AgentKnowledgeSource.objects.filter(is_active=True)

            if knowledge_type:
                queryset = queryset.filter(knowledge_type=knowledge_type)

            if title_contains:
                queryset = queryset.filter(title__icontains=title_contains)

            if from_agents:
                queryset = queryset.filter(agent__name__in=from_agents)

            if self.agent_model:
                queryset = queryset.exclude(agent=self.agent_model)

            results = []
            for ks in queryset.order_by('-confidence_score')[:10]:
                results.append({
                    'source_agent': ks.agent.name,
                    'title': ks.title,
                    'type': ks.knowledge_type,
                    'value': json.loads(ks.summary) if ks.summary else {},
                    'confidence': ks.confidence_score,
                })

                # Record the learning connection and transfer (Session 311)
                if self.agent_model and ks.agent:
                    try:
                        # Get or create learning connection
                        connection, created = AgentLearningConnection.objects.get_or_create(
                            teacher_agent=ks.agent,
                            student_agent=self.agent_model,
                            defaults={
                                'learning_type': 'knowledge_sharing',
                                'shareable_knowledge_types': [ks.knowledge_type],
                                'is_active': True,
                            }
                        )

                        # Update connection stats
                        connection.total_transfers += 1
                        connection.last_transfer_at = timezone.now()
                        connection.save()

                        # Record the transfer
                        KnowledgeTransfer.objects.create(
                            connection=connection,
                            source_knowledge=ks,
                            transfer_summary=f"Retrieved '{ks.title}' for creative direction",
                            key_points={'knowledge_type': ks.knowledge_type},
                            was_useful=True,
                            usefulness_score=ks.confidence_score,
                        )
                    except Exception as transfer_error:
                        logger.debug(f"Failed to record transfer: {transfer_error}")

            return results
        except Exception as e:
            logger.debug(f"Failed to get shared knowledge: {e}")
            return []


class CreativeDirectorAgent(CreativeDirectorLearningMixin):
    """
    Provides high-level creative guidance and direction.

    Acts as a creative consultant that reviews prompts, suggests improvements,
    and ensures consistency across projects.
    """

    # Creative principles by content type
    CREATIVE_PRINCIPLES = {
        'logo': {
            'key_principles': [
                'Simplicity and memorability',
                'Scalability (works at any size)',
                'Timelessness over trends',
                'Uniqueness in the market'
            ],
            'common_mistakes': [
                'Too much detail',
                'Overly trendy elements',
                'Poor contrast',
                'Unclear at small sizes'
            ],
            'enhancement_tips': [
                'Consider the brand personality',
                'Think about where it will be used',
                'Ensure it works in one color',
                'Test at different sizes'
            ]
        },
        'thumbnail': {
            'key_principles': [
                'Curiosity gap - make viewers want to click',
                'Bold, readable text (3-5 words max)',
                'High contrast and saturation',
                'Human faces with expressions'
            ],
            'common_mistakes': [
                'Too much text',
                'Low contrast',
                'No clear focal point',
                'Misleading content'
            ],
            'enhancement_tips': [
                'Use complementary colors for text',
                'Include a human element',
                'Create visual hierarchy',
                'Match video content'
            ]
        },
        'social_media': {
            'key_principles': [
                'Stop the scroll - first impression matters',
                'Platform-native aesthetics',
                'Clear message in 3 seconds',
                'Emotional connection'
            ],
            'common_mistakes': [
                'Generic stock imagery',
                'Too much text',
                'Off-brand colors',
                'No clear CTA'
            ],
            'enhancement_tips': [
                'Use brand colors consistently',
                'Optimize for mobile viewing',
                'Include negative space',
                'Test on target platform'
            ]
        },
        'brand_identity': {
            'key_principles': [
                'Consistency across all touchpoints',
                'Reflects brand values and personality',
                'Flexible but recognizable',
                'Differentiates from competitors'
            ],
            'common_mistakes': [
                'Copying competitors',
                'Inconsistent application',
                'Overcomplicating the system',
                'Ignoring target audience'
            ],
            'enhancement_tips': [
                'Define brand personality first',
                'Create a color story',
                'Design for flexibility',
                'Document everything'
            ]
        }
    }

    # Style-mood mappings
    STYLE_MOODS = {
        'professional': ['clean', 'minimal', 'sophisticated', 'trustworthy'],
        'playful': ['fun', 'colorful', 'energetic', 'friendly'],
        'luxury': ['elegant', 'refined', 'exclusive', 'premium'],
        'tech': ['modern', 'innovative', 'futuristic', 'digital'],
        'organic': ['natural', 'warm', 'earthy', 'sustainable'],
        'bold': ['striking', 'confident', 'powerful', 'impactful'],
        'minimal': ['simple', 'clean', 'focused', 'essential'],
        'vintage': ['nostalgic', 'classic', 'timeless', 'authentic']
    }

    # Color psychology
    COLOR_MEANINGS = {
        'blue': {'emotions': ['trust', 'reliability', 'calm'], 'industries': ['tech', 'finance', 'healthcare']},
        'red': {'emotions': ['energy', 'passion', 'urgency'], 'industries': ['food', 'entertainment', 'sports']},
        'green': {'emotions': ['growth', 'nature', 'health'], 'industries': ['eco', 'health', 'finance']},
        'yellow': {'emotions': ['optimism', 'creativity', 'warmth'], 'industries': ['food', 'children', 'creative']},
        'purple': {'emotions': ['luxury', 'creativity', 'wisdom'], 'industries': ['beauty', 'tech', 'education']},
        'orange': {'emotions': ['enthusiasm', 'confidence', 'fun'], 'industries': ['food', 'sports', 'entertainment']},
        'black': {'emotions': ['sophistication', 'power', 'elegance'], 'industries': ['luxury', 'tech', 'fashion']},
        'white': {'emotions': ['purity', 'simplicity', 'cleanliness'], 'industries': ['health', 'tech', 'minimal']}
    }

    def __init__(self, user: Optional[User] = None, project_id: Optional[str] = None):
        """
        Initialize Creative Director Agent.

        Args:
            user: User context
            project_id: Optional project context
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = 'CreativeDirectorAgent'
        self._trend_agent = None
        self._brand_agent = None

        logger.info(f"🎨 CreativeDirectorAgent initialized for user: {user.username if user else 'system'}")

    @property
    def trend_agent(self):
        """Lazy load TrendAnalysisAgent."""
        if self._trend_agent is None:
            try:
                from agents.trend_analysis_agent import TrendAnalysisAgent
                self._trend_agent = TrendAnalysisAgent(user=self.user)
            except ImportError:
                logger.warning("TrendAnalysisAgent not available")
        return self._trend_agent

    @property
    def brand_agent(self):
        """Lazy load BrandIdentityAgent."""
        if self._brand_agent is None:
            try:
                from agents.brand_identity_agent import BrandIdentityAgent
                self._brand_agent = BrandIdentityAgent(user=self.user, project_id=self.project_id)
            except ImportError:
                logger.warning("BrandIdentityAgent not available")
        return self._brand_agent

    def review_prompt(self, prompt: str, content_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Review and enhance a creative prompt.

        Args:
            prompt: Original prompt to review
            content_type: Type of content (logo, thumbnail, social_media, brand_identity)

        Returns:
            Creative direction with enhanced prompt and recommendations
        """
        logger.info(f"🎨 Reviewing prompt: {prompt[:50]}...")

        try:
            # Detect content type if not provided
            if not content_type:
                content_type = self._detect_content_type(prompt)

            # Get relevant principles
            principles = self.CREATIVE_PRINCIPLES.get(content_type, self.CREATIVE_PRINCIPLES['social_media'])

            # Analyze prompt
            analysis = self._analyze_prompt(prompt)

            # Generate suggestions
            suggestions = self._generate_suggestions(prompt, content_type, analysis)

            # Enhance prompt
            enhanced_prompt = self._enhance_prompt(prompt, suggestions)

            # Get style recommendations
            style_rec = self._recommend_style(prompt, content_type)

            # Get color recommendations
            color_rec = self._recommend_colors(prompt, content_type)

            return {
                'success': True,
                'original_prompt': prompt,
                'enhanced_prompt': enhanced_prompt,
                'content_type': content_type,
                'creative_direction': {
                    'style_recommendation': style_rec,
                    'color_recommendation': color_rec,
                    'key_principles': principles['key_principles'],
                    'avoid': principles['common_mistakes'],
                    'suggestions': suggestions
                },
                'confidence_score': analysis.get('confidence', 75),
                'message': f"Creative direction provided for {content_type}"
            }

        except Exception as e:
            logger.error(f"❌ CreativeDirectorAgent.review_prompt failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def establish_creative_direction(
        self,
        project_brief: str,
        target_audience: Optional[str] = None,
        industry: Optional[str] = None,
        competitors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Establish creative direction for an entire project.

        Args:
            project_brief: Description of the project
            target_audience: Who the content is for
            industry: Industry category
            competitors: List of competitor names (for differentiation)

        Returns:
            Comprehensive creative direction
        """
        logger.info(f"🎨 Establishing creative direction for: {project_brief[:50]}...")

        try:
            # Analyze the brief
            brief_analysis = self._analyze_brief(project_brief, target_audience, industry)

            # Determine recommended style
            recommended_style = self._determine_project_style(brief_analysis)

            # Create color palette recommendation
            color_palette = self._create_color_palette(brief_analysis)

            # Generate mood board concepts
            mood_board = self._generate_mood_concepts(recommended_style, industry)

            # Create differentiation strategy if competitors provided
            differentiation = None
            if competitors:
                differentiation = self._create_differentiation_strategy(competitors, industry)

            # Get trending elements to consider
            trend_insights = None
            if self.trend_agent:
                try:
                    trends = self.trend_agent.get_design_trends()
                    trend_insights = trends.get('trends', [])[:3]
                except Exception:
                    pass

            return {
                'success': True,
                'project_brief': project_brief,
                'creative_direction': {
                    'primary_style': recommended_style,
                    'style_attributes': self.STYLE_MOODS.get(recommended_style, []),
                    'color_palette': color_palette,
                    'mood_board_concepts': mood_board,
                    'differentiation_strategy': differentiation,
                    'trend_insights': trend_insights
                },
                'target_audience': target_audience,
                'industry': industry,
                'guidelines': [
                    f"Maintain {recommended_style} aesthetic across all materials",
                    "Use primary color for main elements, accent for CTAs",
                    "Ensure consistency in typography and spacing",
                    "Test all content with target audience in mind"
                ],
                'message': "Creative direction established successfully"
            }

        except Exception as e:
            logger.error(f"❌ CreativeDirectorAgent.establish_creative_direction failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def critique_design(self, design_description: str, intended_purpose: str) -> Dict[str, Any]:
        """
        Provide constructive critique of a design concept.

        Args:
            design_description: Description of the design
            intended_purpose: What the design is for

        Returns:
            Constructive feedback and improvement suggestions
        """
        logger.info(f"🎨 Critiquing design for: {intended_purpose}")

        try:
            # Analyze the design description
            strengths = self._identify_strengths(design_description)
            weaknesses = self._identify_weaknesses(design_description, intended_purpose)
            improvements = self._suggest_improvements(design_description, intended_purpose)

            # Determine content type for specific advice
            content_type = self._detect_content_type(intended_purpose)
            principles = self.CREATIVE_PRINCIPLES.get(content_type, {})

            return {
                'success': True,
                'critique': {
                    'strengths': strengths,
                    'areas_for_improvement': weaknesses,
                    'specific_suggestions': improvements,
                    'relevant_principles': principles.get('key_principles', [])
                },
                'overall_assessment': self._calculate_assessment(strengths, weaknesses),
                'next_steps': [
                    "Address the identified weaknesses",
                    "Build on existing strengths",
                    "Test with target audience"
                ],
                'message': "Design critique complete"
            }

        except Exception as e:
            logger.error(f"❌ CreativeDirectorAgent.critique_design failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def get_creative_insights(self, topic: str) -> Dict[str, Any]:
        """
        Get creative insights for a topic.

        Args:
            topic: Topic to get insights for

        Returns:
            Creative insights and inspiration
        """
        logger.info(f"🎨 Getting creative insights for: {topic}")

        try:
            # Get trend data if available
            trend_data = None
            if self.trend_agent:
                try:
                    trend_data = self.trend_agent.analyze_topic(topic)
                except Exception:
                    pass

            # Generate creative angles
            angles = self._generate_creative_angles(topic)

            # Get color inspiration
            color_inspiration = self._get_color_inspiration(topic)

            # Get style inspiration
            style_inspiration = self._get_style_inspiration(topic)

            return {
                'success': True,
                'topic': topic,
                'insights': {
                    'creative_angles': angles,
                    'color_inspiration': color_inspiration,
                    'style_inspiration': style_inspiration,
                    'trend_data': trend_data
                },
                'inspiration_sources': [
                    'Current design trends',
                    'Color psychology',
                    'Industry best practices',
                    'Spider intelligence data'
                ],
                'message': f"Creative insights generated for '{topic}'"
            }

        except Exception as e:
            logger.error(f"❌ CreativeDirectorAgent.get_creative_insights failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # Private helper methods

    def _detect_content_type(self, text: str) -> str:
        """Detect content type from text."""
        text_lower = text.lower()

        if any(kw in text_lower for kw in ['logo', 'brand mark', 'icon', 'emblem']):
            return 'logo'
        elif any(kw in text_lower for kw in ['thumbnail', 'youtube', 'video cover']):
            return 'thumbnail'
        elif any(kw in text_lower for kw in ['brand', 'identity', 'guidelines']):
            return 'brand_identity'
        else:
            return 'social_media'

    def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze a prompt for completeness and clarity."""
        analysis = {
            'has_subject': bool(any(kw in prompt.lower() for kw in ['logo', 'image', 'graphic', 'design'])),
            'has_style': bool(any(kw in prompt.lower() for kw in list(self.STYLE_MOODS.keys()))),
            'has_color': bool(any(color in prompt.lower() for color in self.COLOR_MEANINGS.keys())),
            'has_context': bool(any(kw in prompt.lower() for kw in ['for', 'about', 'company', 'brand'])),
            'word_count': len(prompt.split())
        }

        # Calculate confidence based on completeness
        completeness = sum([
            analysis['has_subject'],
            analysis['has_style'],
            analysis['has_color'],
            analysis['has_context'],
            analysis['word_count'] > 5
        ])
        analysis['confidence'] = min(95, completeness * 20 + 15)

        return analysis

    def _generate_suggestions(self, prompt: str, content_type: str, analysis: Dict) -> List[str]:
        """Generate improvement suggestions based on analysis."""
        suggestions = []

        if not analysis.get('has_style'):
            suggestions.append("Consider specifying a style (minimalist, modern, playful, etc.)")

        if not analysis.get('has_color'):
            suggestions.append("Adding color preferences can improve results")

        if not analysis.get('has_context'):
            suggestions.append("Include context about the brand or purpose")

        if analysis.get('word_count', 0) < 5:
            suggestions.append("More detail typically produces better results")

        # Content-specific suggestions
        principles = self.CREATIVE_PRINCIPLES.get(content_type, {})
        if principles.get('enhancement_tips'):
            suggestions.extend(principles['enhancement_tips'][:2])

        return suggestions[:5]

    def _enhance_prompt(self, prompt: str, suggestions: List[str]) -> str:
        """Enhance prompt based on suggestions."""
        # Add quality modifiers if not present
        quality_terms = ['professional', 'high-quality', 'polished']
        has_quality = any(term in prompt.lower() for term in quality_terms)

        enhanced = prompt
        if not has_quality:
            enhanced = f"professional, high-quality {enhanced}"

        return enhanced

    def _recommend_style(self, prompt: str, content_type: str) -> Dict[str, Any]:
        """Recommend style based on prompt analysis."""
        prompt_lower = prompt.lower()

        # Check for existing style mentions
        for style, moods in self.STYLE_MOODS.items():
            if style in prompt_lower or any(mood in prompt_lower for mood in moods):
                return {
                    'recommended': style,
                    'moods': moods,
                    'reason': 'Based on your prompt'
                }

        # Default recommendations by content type
        content_styles = {
            'logo': 'minimal',
            'thumbnail': 'bold',
            'social_media': 'playful',
            'brand_identity': 'professional'
        }

        style = content_styles.get(content_type, 'professional')
        return {
            'recommended': style,
            'moods': self.STYLE_MOODS[style],
            'reason': f'Recommended for {content_type}'
        }

    def _recommend_colors(self, prompt: str, content_type: str) -> Dict[str, Any]:
        """Recommend colors based on context."""
        prompt_lower = prompt.lower()

        # Check for industry mentions
        for color, data in self.COLOR_MEANINGS.items():
            if any(ind in prompt_lower for ind in data['industries']):
                return {
                    'primary': color,
                    'emotions': data['emotions'],
                    'reason': f"Common in related industries"
                }

        # Default by content type
        content_colors = {
            'logo': 'blue',
            'thumbnail': 'red',
            'social_media': 'purple',
            'brand_identity': 'blue'
        }

        color = content_colors.get(content_type, 'blue')
        return {
            'primary': color,
            'emotions': self.COLOR_MEANINGS[color]['emotions'],
            'reason': f'Versatile choice for {content_type}'
        }

    def _analyze_brief(self, brief: str, audience: Optional[str], industry: Optional[str]) -> Dict[str, Any]:
        """Analyze a project brief."""
        return {
            'keywords': self._extract_keywords(brief),
            'audience': audience,
            'industry': industry,
            'tone': self._detect_tone(brief)
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key words from text."""
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = text.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 3][:10]

    def _detect_tone(self, text: str) -> str:
        """Detect the tone of text."""
        text_lower = text.lower()

        if any(kw in text_lower for kw in ['fun', 'playful', 'exciting', 'energetic']):
            return 'playful'
        elif any(kw in text_lower for kw in ['professional', 'corporate', 'business', 'serious']):
            return 'professional'
        elif any(kw in text_lower for kw in ['luxury', 'premium', 'exclusive', 'elegant']):
            return 'luxury'
        elif any(kw in text_lower for kw in ['tech', 'innovative', 'modern', 'digital']):
            return 'tech'
        else:
            return 'neutral'

    def _determine_project_style(self, analysis: Dict) -> str:
        """Determine recommended style for project."""
        tone_styles = {
            'playful': 'playful',
            'professional': 'professional',
            'luxury': 'luxury',
            'tech': 'tech',
            'neutral': 'modern'
        }
        return tone_styles.get(analysis.get('tone', 'neutral'), 'modern')

    def _create_color_palette(self, analysis: Dict) -> Dict[str, str]:
        """Create a color palette based on analysis."""
        industry = analysis.get('industry', '').lower()

        # Industry-based palettes
        industry_palettes = {
            'tech': {'primary': '#2563EB', 'secondary': '#1E293B', 'accent': '#10B981'},
            'healthcare': {'primary': '#0EA5E9', 'secondary': '#475569', 'accent': '#22C55E'},
            'finance': {'primary': '#1E40AF', 'secondary': '#334155', 'accent': '#0EA5E9'},
            'creative': {'primary': '#8B5CF6', 'secondary': '#EC4899', 'accent': '#F59E0B'},
            'eco': {'primary': '#059669', 'secondary': '#065F46', 'accent': '#D97706'},
        }

        for key, palette in industry_palettes.items():
            if key in industry:
                return palette

        # Default palette
        return {'primary': '#3B82F6', 'secondary': '#1F2937', 'accent': '#10B981'}

    def _generate_mood_concepts(self, style: str, industry: Optional[str]) -> List[str]:
        """Generate mood board concepts."""
        base_concepts = self.STYLE_MOODS.get(style, ['modern', 'clean'])

        concepts = [
            f"{base_concepts[0].capitalize()} aesthetic with clean lines",
            f"{base_concepts[1].capitalize()} feel with purposeful whitespace",
            f"Balanced composition with {style} elements"
        ]

        if industry:
            concepts.append(f"Industry-appropriate imagery for {industry}")

        return concepts

    def _create_differentiation_strategy(self, competitors: List[str], industry: Optional[str]) -> Dict[str, Any]:
        """Create strategy to differentiate from competitors."""
        return {
            'approach': 'Stand out by zigging where they zag',
            'tactics': [
                'Use unexpected color combinations',
                'Adopt a unique visual style',
                'Focus on a distinctive brand voice',
                'Emphasize unique value propositions'
            ],
            'competitors_analyzed': len(competitors)
        }

    def _identify_strengths(self, description: str) -> List[str]:
        """Identify strengths in a design description."""
        strengths = []

        positive_indicators = {
            'clean': 'Clean, uncluttered design',
            'bold': 'Bold visual impact',
            'consistent': 'Consistent visual language',
            'simple': 'Effective simplicity',
            'colorful': 'Engaging use of color'
        }

        for indicator, strength in positive_indicators.items():
            if indicator in description.lower():
                strengths.append(strength)

        if not strengths:
            strengths.append('Unique creative approach')

        return strengths

    def _identify_weaknesses(self, description: str, purpose: str) -> List[str]:
        """Identify areas for improvement."""
        weaknesses = []

        # Generic weaknesses to check
        if 'too many' in description.lower() or 'busy' in description.lower():
            weaknesses.append('May be visually cluttered')

        if 'small' in description.lower() and 'text' in description.lower():
            weaknesses.append('Text may be hard to read at smaller sizes')

        if not weaknesses:
            weaknesses.append('Consider testing with target audience')

        return weaknesses

    def _suggest_improvements(self, description: str, purpose: str) -> List[str]:
        """Suggest specific improvements."""
        content_type = self._detect_content_type(purpose)
        principles = self.CREATIVE_PRINCIPLES.get(content_type, {})

        improvements = principles.get('enhancement_tips', [])[:3]

        if not improvements:
            improvements = [
                'Increase contrast for better visibility',
                'Simplify complex elements',
                'Ensure brand consistency'
            ]

        return improvements

    def _calculate_assessment(self, strengths: List[str], weaknesses: List[str]) -> str:
        """Calculate overall assessment."""
        strength_count = len(strengths)
        weakness_count = len(weaknesses)

        if strength_count > weakness_count:
            return 'Strong foundation with room for refinement'
        elif weakness_count > strength_count:
            return 'Needs significant improvement in key areas'
        else:
            return 'Balanced with opportunities for enhancement'

    def _generate_creative_angles(self, topic: str) -> List[str]:
        """Generate creative angles for a topic."""
        return [
            f"Metaphorical representation of {topic}",
            f"Abstract interpretation of {topic}",
            f"Human-centered approach to {topic}",
            f"Minimalist take on {topic}",
            f"Bold, maximalist vision of {topic}"
        ]

    def _get_color_inspiration(self, topic: str) -> Dict[str, Any]:
        """Get color inspiration for a topic."""
        topic_lower = topic.lower()

        for color, data in self.COLOR_MEANINGS.items():
            if any(ind in topic_lower for ind in data['industries']):
                return {
                    'suggested_color': color,
                    'emotions': data['emotions'],
                    'complementary': self._get_complementary(color)
                }

        return {
            'suggested_color': 'blue',
            'emotions': ['trust', 'reliability'],
            'complementary': 'orange'
        }

    def _get_complementary(self, color: str) -> str:
        """Get complementary color."""
        complements = {
            'blue': 'orange',
            'red': 'green',
            'yellow': 'purple',
            'green': 'red',
            'purple': 'yellow',
            'orange': 'blue'
        }
        return complements.get(color, 'gray')

    def _get_style_inspiration(self, topic: str) -> List[str]:
        """Get style inspiration for a topic."""
        return [
            'Contemporary minimalism',
            'Bold geometric shapes',
            'Organic flowing forms',
            'Retro-modern fusion',
            'Tech-forward aesthetic'
        ]


# Convenience function
def get_creative_director_agent(user=None, project_id=None) -> CreativeDirectorAgent:
    """Get CreativeDirectorAgent instance."""
    return CreativeDirectorAgent(user=user, project_id=project_id)


__all__ = [
    'CreativeDirectorAgent',
    'get_creative_director_agent'
]
