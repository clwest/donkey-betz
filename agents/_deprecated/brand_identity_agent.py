"""
Brand Identity Creator Agent
=============================

Session 241: Created as part of agent cleanup - building real, valuable agents.
Session 308: Added learning infrastructure hooks for cross-agent knowledge sharing.

This agent manages brand consistency across generated content by:
- Remembering user's brand colors, fonts, and style preferences
- Applying consistent branding across all generated content
- Building brand guidelines from generated assets
- Suggesting brand-appropriate colors and styles

Example:
    agent = BrandIdentityAgent(user=request.user)

    # Set brand colors
    agent.set_brand_colors(primary='#FF5733', secondary='#3498DB', accent='#2ECC71')

    # Get brand-enhanced prompt
    result = agent.enhance_prompt("Create a logo for tech startup")
    # Returns prompt with brand colors and style applied

    # Generate brand guidelines
    result = agent.generate_guidelines()
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


class BrandIdentityLearningMixin:
    """
    Learning infrastructure mixin for BrandIdentityAgent.
    Session 308: Enables cross-agent knowledge sharing for brand patterns.
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
                    name='BrandIdentityAgent',
                    defaults={
                        'agent_type': 'deprecated',
                        'specialization': 'brand_identity',
                        'description': 'Manages brand consistency across generated content.',
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
    ):
        """Record execution outcome for XP and pattern learning."""
        if not self.learning_loop:
            return None

        try:
            outcome_id = self.learning_loop.record_outcome(
                query_type='brand_identity',
                query_text=task,
                execution_mode='agent',
                agents_used=['BrandIdentityAgent'],
                response=str(result),
                execution_time_ms=result.get('execution_time_ms', 0),
                success=result.get('success', False),
                spider_data_used=False,
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
        """Create a memory from the brand identity execution."""
        if not self.memory_service or not self.agent_model:
            return None

        try:
            memory = self.memory_service.create_memory(
                agent=self.agent_model,
                title=f"Brand: {task[:50]}...",
                content=str(result),
                memory_type=memory_type,
                valence="positive" if result.get('success') else "negative",
                importance_score=importance,
                source_type='agent_execution',
                tags=['brand_identity', 'branding', 'success' if result.get('success') else 'failure']
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
        """Share learned brand knowledge for cross-agent learning."""
        if not self.agent_model:
            return None

        try:
            from core.models_unified_system import AgentKnowledgeSource

            type_mapping = {
                'color_palette': 'content_idea',
                'style': 'content_idea',
                'brand': 'content_idea',
                'industry': 'market',
            }
            mapped_type = type_mapping.get(knowledge_type, 'content_idea')

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
        """Retrieve knowledge from other agents."""
        try:
            from core.models_unified_system import AgentKnowledgeSource

            queryset = AgentKnowledgeSource.objects.filter(is_active=True)

            if knowledge_type:
                queryset = queryset.filter(knowledge_type=knowledge_type)

            if title_contains:
                queryset = queryset.filter(title__icontains=title_contains)

            if from_agents:
                queryset = queryset.filter(agent__name__in=from_agents)

            if self.agent_model:
                queryset = queryset.exclude(agent=self.agent_model)

            return [
                {
                    'source_agent': ks.agent.name,
                    'title': ks.title,
                    'type': ks.knowledge_type,
                    'value': json.loads(ks.summary) if ks.summary else {},
                    'confidence': ks.confidence_score,
                }
                for ks in queryset.order_by('-confidence_score')[:10]
            ]
        except Exception as e:
            logger.debug(f"Failed to get shared knowledge: {e}")
            return []


class BrandIdentityAgent(BrandIdentityLearningMixin):
    """
    Manages brand consistency across all generated content.

    Stores and applies brand preferences (colors, fonts, styles) to ensure
    consistent branding across logos, social content, and other assets.

    Session 308: Added BrandIdentityLearningMixin for cross-agent knowledge sharing.
    """

    # Color palette templates
    COLOR_PALETTES = {
        'tech_modern': {
            'primary': '#2563EB',  # Blue
            'secondary': '#1E293B',  # Dark slate
            'accent': '#10B981',  # Green
            'background': '#F8FAFC',
            'text': '#0F172A'
        },
        'creative_bold': {
            'primary': '#EC4899',  # Pink
            'secondary': '#8B5CF6',  # Purple
            'accent': '#F59E0B',  # Orange
            'background': '#FFFFFF',
            'text': '#1F2937'
        },
        'professional_corporate': {
            'primary': '#1E40AF',  # Navy
            'secondary': '#475569',  # Gray
            'accent': '#0EA5E9',  # Light blue
            'background': '#F9FAFB',
            'text': '#111827'
        },
        'eco_natural': {
            'primary': '#059669',  # Green
            'secondary': '#065F46',  # Dark green
            'accent': '#D97706',  # Amber
            'background': '#ECFDF5',
            'text': '#1F2937'
        },
        'luxury_elegant': {
            'primary': '#1C1917',  # Near black
            'secondary': '#78716C',  # Warm gray
            'accent': '#CA8A04',  # Gold
            'background': '#FAFAF9',
            'text': '#1C1917'
        },
        'startup_energetic': {
            'primary': '#7C3AED',  # Violet
            'secondary': '#2DD4BF',  # Teal
            'accent': '#FB923C',  # Orange
            'background': '#FFFFFF',
            'text': '#18181B'
        }
    }

    # Style presets
    BRAND_STYLES = {
        'minimalist': {
            'characteristics': ['clean lines', 'white space', 'simple shapes'],
            'avoid': ['clutter', 'gradients', 'complex patterns'],
            'fonts': ['sans-serif', 'geometric']
        },
        'modern': {
            'characteristics': ['bold', 'contemporary', 'dynamic'],
            'avoid': ['ornate details', 'traditional elements'],
            'fonts': ['sans-serif', 'modern serif']
        },
        'playful': {
            'characteristics': ['fun', 'colorful', 'energetic', 'rounded shapes'],
            'avoid': ['corporate', 'formal', 'straight lines'],
            'fonts': ['rounded', 'handwritten']
        },
        'professional': {
            'characteristics': ['trustworthy', 'clean', 'established'],
            'avoid': ['casual', 'trendy', 'experimental'],
            'fonts': ['classic serif', 'traditional sans-serif']
        },
        'artistic': {
            'characteristics': ['creative', 'unique', 'expressive'],
            'avoid': ['generic', 'corporate', 'template-like'],
            'fonts': ['display', 'decorative']
        },
        'tech': {
            'characteristics': ['futuristic', 'digital', 'innovative'],
            'avoid': ['organic', 'traditional', 'handmade'],
            'fonts': ['geometric sans-serif', 'monospace']
        }
    }

    def __init__(self, user: Optional[User] = None, project_id: Optional[str] = None):
        """
        Initialize Brand Identity Agent.

        Args:
            user: User context
            project_id: Optional project context
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = 'BrandIdentityAgent'
        self._brand_data = None

        logger.info(f"🎨 BrandIdentityAgent initialized for user: {user.username if user else 'system'}")

    @property
    def brand_data(self) -> Dict[str, Any]:
        """Get or load brand data for user."""
        if self._brand_data is None:
            self._brand_data = self._load_brand_data()
        return self._brand_data

    def _load_brand_data(self) -> Dict[str, Any]:
        """Load brand data from user preferences or project."""
        try:
            # Try to load from user preferences
            if self.user:
                from core.models import UserPreference
                try:
                    pref = UserPreference.objects.get(user=self.user, key='brand_identity')
                    return json.loads(pref.value) if pref.value else {}
                except UserPreference.DoesNotExist:
                    pass

            # Try to load from project
            if self.project_id:
                from content.models import Project
                try:
                    project = Project.objects.get(id=self.project_id)
                    if hasattr(project, 'metadata') and project.metadata:
                        return project.metadata.get('brand_identity', {})
                except Exception:
                    pass

        except Exception as e:
            logger.warning(f"Could not load brand data: {e}")

        return {}

    def _save_brand_data(self):
        """Save brand data to user preferences."""
        try:
            if self.user:
                from core.models import UserPreference
                pref, created = UserPreference.objects.get_or_create(
                    user=self.user,
                    key='brand_identity',
                    defaults={'value': json.dumps(self._brand_data)}
                )
                if not created:
                    pref.value = json.dumps(self._brand_data)
                    pref.save()
                return True
        except Exception as e:
            logger.warning(f"Could not save brand data: {e}")
        return False

    def set_brand_colors(
        self,
        primary: str,
        secondary: Optional[str] = None,
        accent: Optional[str] = None,
        background: Optional[str] = None,
        text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set brand colors.

        Args:
            primary: Primary brand color (hex)
            secondary: Secondary color (hex)
            accent: Accent color (hex)
            background: Background color (hex)
            text: Text color (hex)

        Returns:
            Updated brand colors
        """
        logger.info(f"🎨 Setting brand colors: primary={primary}")

        self._brand_data = self.brand_data  # Ensure loaded
        self._brand_data['colors'] = {
            'primary': primary,
            'secondary': secondary or self._generate_secondary(primary),
            'accent': accent or self._generate_accent(primary),
            'background': background or '#FFFFFF',
            'text': text or '#1F2937'
        }
        self._brand_data['updated_at'] = timezone.now().isoformat()

        self._save_brand_data()

        result = {
            'success': True,
            'colors': self._brand_data['colors'],
            'message': 'Brand colors updated successfully'
        }

        # Session 308: Learning Infrastructure Hooks
        self._record_learning_outcome(
            result=result,
            task=f"Set brand colors: primary={primary}",
            context={'primary': primary, 'secondary': secondary, 'accent': accent}
        )

        # Share successful color palettes
        self._share_knowledge(
            knowledge_type='color_palette',
            title=f"Brand colors: {primary}",
            knowledge_value={
                'primary': primary,
                'secondary': self._brand_data['colors']['secondary'],
                'accent': self._brand_data['colors']['accent'],
            },
            confidence=0.75
        )

        return result

    def set_brand_style(self, style: str) -> Dict[str, Any]:
        """
        Set brand style preference.

        Args:
            style: Style preset (minimalist, modern, playful, professional, artistic, tech)

        Returns:
            Updated brand style
        """
        logger.info(f"🎨 Setting brand style: {style}")

        if style not in self.BRAND_STYLES:
            return {
                'success': False,
                'error': f"Unknown style: {style}. Available: {list(self.BRAND_STYLES.keys())}"
            }

        self._brand_data = self.brand_data
        self._brand_data['style'] = style
        self._brand_data['style_details'] = self.BRAND_STYLES[style]
        self._brand_data['updated_at'] = timezone.now().isoformat()

        self._save_brand_data()

        result = {
            'success': True,
            'style': style,
            'details': self.BRAND_STYLES[style],
            'message': f'Brand style set to "{style}"'
        }

        # Session 308: Learning Infrastructure Hooks
        self._record_learning_outcome(
            result=result,
            task=f"Set brand style: {style}",
            context={'style': style, 'characteristics': self.BRAND_STYLES[style].get('characteristics', [])}
        )

        # Share style preferences
        self._share_knowledge(
            knowledge_type='style',
            title=f"Brand style: {style}",
            knowledge_value={
                'style': style,
                'characteristics': self.BRAND_STYLES[style].get('characteristics', []),
                'fonts': self.BRAND_STYLES[style].get('fonts', []),
            },
            confidence=0.8
        )

        return result

    def set_brand_name(self, name: str, tagline: Optional[str] = None) -> Dict[str, Any]:
        """
        Set brand name and tagline.

        Args:
            name: Brand name
            tagline: Optional brand tagline

        Returns:
            Updated brand info
        """
        logger.info(f"🎨 Setting brand name: {name}")

        self._brand_data = self.brand_data
        self._brand_data['name'] = name
        if tagline:
            self._brand_data['tagline'] = tagline
        self._brand_data['updated_at'] = timezone.now().isoformat()

        self._save_brand_data()

        return {
            'success': True,
            'name': name,
            'tagline': tagline,
            'message': f'Brand name set to "{name}"'
        }

    def apply_palette(self, palette_name: str) -> Dict[str, Any]:
        """
        Apply a preset color palette.

        Args:
            palette_name: Palette name from COLOR_PALETTES

        Returns:
            Applied palette colors
        """
        logger.info(f"🎨 Applying palette: {palette_name}")

        if palette_name not in self.COLOR_PALETTES:
            return {
                'success': False,
                'error': f"Unknown palette: {palette_name}. Available: {list(self.COLOR_PALETTES.keys())}"
            }

        palette = self.COLOR_PALETTES[palette_name]
        return self.set_brand_colors(**palette)

    def get_brand_profile(self) -> Dict[str, Any]:
        """
        Get complete brand profile.

        Returns:
            Complete brand profile with colors, style, name, etc.
        """
        data = self.brand_data

        return {
            'success': True,
            'has_brand': bool(data),
            'name': data.get('name'),
            'tagline': data.get('tagline'),
            'colors': data.get('colors', {}),
            'style': data.get('style'),
            'style_details': data.get('style_details', {}),
            'updated_at': data.get('updated_at'),
            'completeness': self._calculate_completeness(data)
        }

    def enhance_prompt(self, prompt: str, apply_colors: bool = True, apply_style: bool = True) -> Dict[str, Any]:
        """
        Enhance a prompt with brand elements.

        Args:
            prompt: Original prompt
            apply_colors: Whether to add brand colors
            apply_style: Whether to add brand style

        Returns:
            Enhanced prompt with brand elements
        """
        logger.info(f"🎨 Enhancing prompt with brand: {prompt[:50]}...")

        data = self.brand_data
        enhancements = []
        enhanced_prompt = prompt

        # Add brand name context if relevant
        if data.get('name') and 'logo' in prompt.lower():
            enhanced_prompt = enhanced_prompt.replace('logo', f"logo for {data['name']}")

        # Add colors
        if apply_colors and data.get('colors'):
            colors = data['colors']
            color_text = f"using {colors.get('primary', 'blue')} as primary color"
            if colors.get('secondary'):
                color_text += f" and {colors['secondary']} as secondary"
            enhancements.append(color_text)

        # Add style
        if apply_style and data.get('style'):
            style_info = self.BRAND_STYLES.get(data['style'], {})
            characteristics = style_info.get('characteristics', [])
            if characteristics:
                enhancements.append(f"{data['style']} style with {', '.join(characteristics[:2])}")

        # Combine
        if enhancements:
            enhanced_prompt = f"{enhanced_prompt}, {', '.join(enhancements)}"

        return {
            'success': True,
            'original_prompt': prompt,
            'enhanced_prompt': enhanced_prompt,
            'enhancements_applied': enhancements,
            'brand_name': data.get('name'),
            'brand_style': data.get('style')
        }

    def generate_guidelines(self) -> Dict[str, Any]:
        """
        Generate brand guidelines document.

        Returns:
            Brand guidelines with colors, typography, usage rules
        """
        logger.info("🎨 Generating brand guidelines")

        data = self.brand_data

        if not data:
            return {
                'success': False,
                'error': 'No brand data found. Set brand colors and style first.'
            }

        guidelines = {
            'brand_name': data.get('name', 'Your Brand'),
            'tagline': data.get('tagline'),
            'color_palette': {
                'primary': {
                    'hex': data.get('colors', {}).get('primary', '#000000'),
                    'usage': 'Main brand color - logos, headers, CTAs'
                },
                'secondary': {
                    'hex': data.get('colors', {}).get('secondary', '#666666'),
                    'usage': 'Supporting color - subheadings, borders, accents'
                },
                'accent': {
                    'hex': data.get('colors', {}).get('accent', '#FF0000'),
                    'usage': 'Highlight color - buttons, links, emphasis'
                },
                'background': {
                    'hex': data.get('colors', {}).get('background', '#FFFFFF'),
                    'usage': 'Background color - page backgrounds, cards'
                },
                'text': {
                    'hex': data.get('colors', {}).get('text', '#000000'),
                    'usage': 'Body text color'
                }
            },
            'style': {
                'name': data.get('style', 'custom'),
                'characteristics': data.get('style_details', {}).get('characteristics', []),
                'avoid': data.get('style_details', {}).get('avoid', []),
                'fonts': data.get('style_details', {}).get('fonts', ['sans-serif'])
            },
            'usage_guidelines': [
                f"Use {data.get('colors', {}).get('primary', 'primary color')} for all main branding elements",
                "Maintain consistent spacing and alignment",
                f"Follow {data.get('style', 'brand')} style principles in all designs",
                "Ensure sufficient contrast for accessibility"
            ],
            'generated_at': timezone.now().isoformat()
        }

        return {
            'success': True,
            'guidelines': guidelines,
            'message': 'Brand guidelines generated successfully'
        }

    def suggest_colors_for_industry(self, industry: str) -> Dict[str, Any]:
        """
        Suggest brand colors based on industry.

        Args:
            industry: Industry name (tech, healthcare, food, finance, etc.)

        Returns:
            Suggested color palettes
        """
        logger.info(f"🎨 Suggesting colors for industry: {industry}")

        industry_suggestions = {
            'tech': ['tech_modern', 'startup_energetic'],
            'healthcare': ['professional_corporate', 'eco_natural'],
            'food': ['creative_bold', 'eco_natural'],
            'finance': ['professional_corporate', 'luxury_elegant'],
            'creative': ['creative_bold', 'startup_energetic'],
            'eco': ['eco_natural'],
            'luxury': ['luxury_elegant'],
            'education': ['professional_corporate', 'creative_bold'],
            'fitness': ['startup_energetic', 'eco_natural'],
            'retail': ['creative_bold', 'startup_energetic']
        }

        # Find matching industry
        industry_lower = industry.lower()
        suggested_palettes = []

        for key, palettes in industry_suggestions.items():
            if key in industry_lower:
                suggested_palettes = palettes
                break

        if not suggested_palettes:
            suggested_palettes = ['tech_modern', 'professional_corporate']

        suggestions = []
        for palette_name in suggested_palettes:
            if palette_name in self.COLOR_PALETTES:
                suggestions.append({
                    'name': palette_name,
                    'colors': self.COLOR_PALETTES[palette_name]
                })

        result = {
            'success': True,
            'industry': industry,
            'suggestions': suggestions,
            'message': f'Suggested {len(suggestions)} color palettes for {industry}'
        }

        # Session 308: Learning Infrastructure Hooks
        self._record_learning_outcome(
            result=result,
            task=f"Suggest colors for industry: {industry}",
            context={'industry': industry, 'suggestions': [s['name'] for s in suggestions]}
        )

        # Share industry-specific palette knowledge
        if suggestions:
            self._share_knowledge(
                knowledge_type='industry',
                title=f"Industry palette: {industry}",
                knowledge_value={
                    'industry': industry,
                    'recommended_palettes': [s['name'] for s in suggestions],
                    'primary_colors': [s['colors']['primary'] for s in suggestions],
                },
                confidence=0.7
            )

            # Create memory for industry palette suggestion
            self._create_execution_memory(
                result=result,
                task=f"Industry colors: {industry}",
                memory_type="success",
                importance=0.6
            )

        return result

    # Private helper methods

    def _generate_secondary(self, primary: str) -> str:
        """Generate a secondary color from primary."""
        # Simple darkening of primary
        try:
            # Remove # and convert to RGB
            hex_color = primary.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Darken by 30%
            r = int(r * 0.7)
            g = int(g * 0.7)
            b = int(b * 0.7)
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            return '#475569'

    def _generate_accent(self, primary: str) -> str:
        """Generate an accent color from primary."""
        # Complementary color approach
        try:
            hex_color = primary.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Shift hue
            r = (r + 128) % 256
            g = (g + 64) % 256
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            return '#10B981'

    def _calculate_completeness(self, data: Dict[str, Any]) -> int:
        """Calculate brand profile completeness percentage."""
        checks = [
            bool(data.get('name')),
            bool(data.get('colors', {}).get('primary')),
            bool(data.get('colors', {}).get('secondary')),
            bool(data.get('style')),
            bool(data.get('tagline'))
        ]
        return int(sum(checks) / len(checks) * 100)


# Convenience function
def get_brand_identity_agent(user=None, project_id=None) -> BrandIdentityAgent:
    """Get BrandIdentityAgent instance."""
    return BrandIdentityAgent(user=user, project_id=project_id)


__all__ = [
    'BrandIdentityAgent',
    'get_brand_identity_agent'
]
