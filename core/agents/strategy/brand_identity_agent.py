"""
Brand Identity Agent - Clean Architecture
==========================================

Session 280: Phase 2 - Agent Architecture Unification

This agent manages brand consistency across generated content by remembering
and applying user's brand colors, fonts, and style preferences.

Tools Available:
    - set_brand_colors: Set/update brand color palette
    - get_brand_profile: Get current brand profile
    - enhance_prompt: Add brand styling to a prompt
    - suggest_palette: Suggest a color palette based on industry

Tools NOT Available (by design):
    - image generation (that's ImageAgent)
    - actual content creation

Usage:
    from core.agents.strategy import BrandIdentityAgent

    agent = BrandIdentityAgent(user=request.user)
    result = agent.execute(
        task="Set up brand colors for a tech startup",
        context={'industry': 'tech'},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any, Optional

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_brand_with_ml(brand_data: dict) -> dict:
    """Analyze brand data using ML models (Text + Clustering)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        # Use TEXT task type for brand sentiment/style analysis
        result = router.auto_route(
            data=brand_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'brand_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML brand analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class BrandIdentityAgent(BaseAgent):
    """
    Agent specialized in brand identity management.

    This agent:
    1. Stores and retrieves brand preferences (colors, styles)
    2. Enhances prompts with brand styling
    3. Suggests palettes based on industry
    4. Ensures brand consistency

    It CANNOT:
    - Generate images, videos, or audio
    - Create actual content
    """

    name = "BrandIdentityAgent"

    system_prompt = """You are BrandIdentityAgent, a specialist in brand identity management.

Your job is to help users establish and maintain consistent branding across all their content.
You manage brand colors, styles, and preferences.

When given a task:
1. Understand the brand personality or industry
2. Suggest or apply appropriate colors and styles
3. Enhance prompts to include brand elements
4. Ensure consistency across recommendations

Available palette templates:
- tech_modern: Blue primary, dark slate secondary, green accent
- creative_bold: Pink primary, purple secondary, orange accent
- professional_corporate: Navy primary, gray secondary, light blue accent
- eco_natural: Green primary, dark green secondary, amber accent
- luxury_elegant: Near black primary, warm gray secondary, gold accent
- startup_energetic: Violet primary, teal secondary, orange accent

Style options:
- minimalist: Clean lines, white space, simple shapes
- modern: Bold, contemporary, dynamic
- playful: Fun, colorful, energetic
- professional: Trustworthy, clean, established
- artistic: Creative, unique, expressive
- tech: Futuristic, digital, innovative

You CANNOT create content - just manage brand identity. For actual creation,
the user should use ImageAgent, VideoAgent, etc."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "set_brand_colors",
                "description": "Set or update the brand color palette",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "primary": {
                            "type": "string",
                            "description": "Primary brand color (hex, e.g., #2563EB)"
                        },
                        "secondary": {
                            "type": "string",
                            "description": "Secondary brand color (hex)"
                        },
                        "accent": {
                            "type": "string",
                            "description": "Accent color (hex)"
                        },
                        "background": {
                            "type": "string",
                            "description": "Background color (hex)",
                            "default": "#FFFFFF"
                        },
                        "text": {
                            "type": "string",
                            "description": "Text color (hex)",
                            "default": "#1F2937"
                        }
                    },
                    "required": ["primary"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_brand_profile",
                "description": "Get the current brand profile including colors and styles",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "enhance_prompt",
                "description": "Add brand styling to a content creation prompt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The original prompt to enhance"
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Type of content (logo, social, thumbnail)",
                            "enum": ["logo", "social", "thumbnail", "brand_identity", "general"]
                        }
                    },
                    "required": ["prompt"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_palette",
                "description": "Suggest a color palette based on industry or style",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "industry": {
                            "type": "string",
                            "description": "Target industry",
                            "enum": ["tech", "creative", "corporate", "eco", "luxury", "startup"]
                        },
                        "style": {
                            "type": "string",
                            "description": "Desired style",
                            "enum": ["minimalist", "modern", "playful", "professional", "artistic", "tech"]
                        }
                    },
                    "required": []
                }
            }
        }
    ]

    # Color palette templates
    COLOR_PALETTES = {
        'tech_modern': {
            'primary': '#2563EB',
            'secondary': '#1E293B',
            'accent': '#10B981',
            'background': '#F8FAFC',
            'text': '#0F172A'
        },
        'creative_bold': {
            'primary': '#EC4899',
            'secondary': '#8B5CF6',
            'accent': '#F59E0B',
            'background': '#FFFFFF',
            'text': '#1F2937'
        },
        'professional_corporate': {
            'primary': '#1E40AF',
            'secondary': '#475569',
            'accent': '#0EA5E9',
            'background': '#F9FAFB',
            'text': '#111827'
        },
        'eco_natural': {
            'primary': '#059669',
            'secondary': '#065F46',
            'accent': '#D97706',
            'background': '#ECFDF5',
            'text': '#1F2937'
        },
        'luxury_elegant': {
            'primary': '#1C1917',
            'secondary': '#78716C',
            'accent': '#CA8A04',
            'background': '#FAFAF9',
            'text': '#1C1917'
        },
        'startup_energetic': {
            'primary': '#7C3AED',
            'secondary': '#2DD4BF',
            'accent': '#FB923C',
            'background': '#FFFFFF',
            'text': '#18181B'
        }
    }

    # Style definitions
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

    # Industry to palette mapping
    INDUSTRY_PALETTE_MAP = {
        'tech': 'tech_modern',
        'creative': 'creative_bold',
        'corporate': 'professional_corporate',
        'eco': 'eco_natural',
        'luxury': 'luxury_elegant',
        'startup': 'startup_energetic'
    }

    def __init__(self, user=None):
        super().__init__(user)
        self._brand_data = None

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute brand identity management based on the task.
        """
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("brand_identity", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing brand identity request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["ask_for_clarification"],
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"BrandIdentityAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Brand operation with args: {arguments}",
                            alternatives=[],
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    # Session 1200: Synthesize tool results into real analysis
                    tool_results_list = [tc.get('result', {}) for tc in tool_calls_made]
                    synthesis = self._synthesize_tool_results(tool_calls_made, tool_results_list, task)
                    analysis_msg = synthesis if synthesis else "Brand identity operation completed"

                    result = AgentResult(
                        success=True,
                        message=analysis_msg,
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                            'content': synthesis,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.7
                    )

                    # Session 1006: Persist output to Deliverable
                    self._save_to_deliverable(
                        title=f"Brand Identity: {task[:80]}",
                        content=result.message,
                        deliverable_type='analysis',
                        category='Brand Identity',
                        tags=['brand', 'identity'],
                        metadata={'task': task[:200]},
                    )

                    return result

                else:
                    result = AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.6
                    )

                    return result

            except Exception as e:
                logger.error(f"BrandIdentityAgent error: {e}")
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

                # Session 380: Learning hooks for collective intelligence (failures too)
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=bool(spider_context),
                    scifi_context_used=bool(scifi_context)
                )
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="failure",
                    importance=0.8  # Failures are important to learn from
                )

                return result

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a brand identity tool call."""
        if tool_name == "set_brand_colors":
            return self._set_brand_colors(
                primary=arguments.get('primary'),
                secondary=arguments.get('secondary'),
                accent=arguments.get('accent'),
                background=arguments.get('background', '#FFFFFF'),
                text=arguments.get('text', '#1F2937')
            )

        elif tool_name == "get_brand_profile":
            return self._get_brand_profile()

        elif tool_name == "enhance_prompt":
            return self._enhance_prompt(
                prompt=arguments.get('prompt', ''),
                content_type=arguments.get('content_type', 'general')
            )

        elif tool_name == "suggest_palette":
            return self._suggest_palette(
                industry=arguments.get('industry'),
                style=arguments.get('style')
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _set_brand_colors(
        self,
        primary: str,
        secondary: Optional[str] = None,
        accent: Optional[str] = None,
        background: str = '#FFFFFF',
        text: str = '#1F2937'
    ) -> Dict[str, Any]:
        """Set brand colors."""
        logger.info(f"Setting brand colors: primary={primary}")

        self._brand_data = {
            'colors': {
                'primary': primary,
                'secondary': secondary or '#475569',
                'accent': accent or '#10B981',
                'background': background,
                'text': text
            }
        }

        # Persist to database if user exists
        if self.user:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=self.user.id)
                if hasattr(user, 'preferences'):
                    user.preferences['brand_colors'] = self._brand_data['colors']
                    user.save()
            except Exception as e:
                logger.warning(f"Could not persist brand colors: {e}")

        return {
            'success': True,
            'message': 'Brand colors set successfully',
            'colors': self._brand_data['colors']
        }

    def _get_brand_profile(self) -> Dict[str, Any]:
        """Get current brand profile."""
        if self._brand_data:
            return {
                'success': True,
                'profile': self._brand_data
            }

        # Try to load from user preferences
        if self.user:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=self.user.id)
                if hasattr(user, 'preferences') and 'brand_colors' in user.preferences:
                    return {
                        'success': True,
                        'profile': {'colors': user.preferences['brand_colors']}
                    }
            except Exception as _e:
                logger.warning(
                    "brand_identity_agent._get_brand_profile: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

        # Return default
        return {
            'success': True,
            'profile': {
                'colors': self.COLOR_PALETTES['tech_modern'],
                'note': 'Using default palette - no brand colors set'
            }
        }

    def _enhance_prompt(
        self,
        prompt: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Enhance a prompt with brand styling."""
        profile = self._get_brand_profile()
        colors = profile.get('profile', {}).get('colors', {})

        enhancements = []

        if colors.get('primary'):
            enhancements.append(f"using brand color {colors['primary']}")
        if colors.get('secondary'):
            enhancements.append(f"with {colors['secondary']} as secondary color")

        enhanced = prompt
        if enhancements:
            enhanced = f"{prompt}, {', '.join(enhancements)}"

        return {
            'success': True,
            'original_prompt': prompt,
            'enhanced_prompt': enhanced,
            'applied_colors': colors
        }

    def _suggest_palette(
        self,
        industry: Optional[str] = None,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Suggest a color palette."""
        # Determine palette based on industry
        palette_name = self.INDUSTRY_PALETTE_MAP.get(industry, 'tech_modern')
        palette = self.COLOR_PALETTES.get(palette_name, self.COLOR_PALETTES['tech_modern'])

        # Get style info
        style_info = self.BRAND_STYLES.get(style or 'modern', self.BRAND_STYLES['modern'])

        return {
            'success': True,
            'suggested_palette': palette,
            'palette_name': palette_name,
            'style_characteristics': style_info.get('characteristics', []),
            'avoid': style_info.get('avoid', []),
            'recommended_fonts': style_info.get('fonts', [])
        }

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for brand identity."""
        return bool(task and task.strip())
