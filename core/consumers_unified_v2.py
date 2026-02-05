"""
WebSocket consumers for Unified Platform V2

Session 931: Updated to use UnifiedPAEntrypoint as single front door.
All PA requests now go through the unified entrypoint for:
- Consistent behavior
- ToolDispatcher integration (no silent failures)
- Structured responses with trace_id
"""
import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class PersonalAssistantConsumer(AsyncWebsocketConsumer):
    """
    Personal Assistant WebSocket consumer with authentication.

    Session 931: Now routes through UnifiedPAEntrypoint for consistent behavior.
    """

    async def connect(self):
        """Accept WebSocket connection if user is authenticated"""
        # Get user from scope (set by AuthMiddleware)
        self.user = self.scope.get("user")

        # Reject if not authenticated
        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close(code=4001)
            return

        self.user_id = str(self.user.id)
        self.room_group_name = f"assistant_{self.user_id}"

        # Session 931: Initialize UnifiedPA entrypoint
        self.unified_pa = None  # Lazy load to avoid import issues

        # Join user-specific channel group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send welcome message through unified PA
        welcome_response = await self._process_through_unified_pa(
            "Generate a friendly welcome message explaining what you can help with.",
            is_welcome=True
        )

        await self.send(text_data=json.dumps(welcome_response))

    async def disconnect(self, close_code):
        """Leave channel group on disconnect"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'message':
                content = data.get('content', '')
                generate_audio = data.get('generate_audio', False)

                # Session 931: Route through UnifiedPA entrypoint
                response = await self._process_through_unified_pa(
                    content,
                    generate_audio=generate_audio
                )

                # Send response
                await self.send(text_data=json.dumps(response))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format',
                'trace_id': None
            }))
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing message: {str(e)}',
                'trace_id': None
            }))

    async def _process_through_unified_pa(
        self,
        message: str,
        is_welcome: bool = False,
        generate_audio: bool = False
    ) -> dict:
        """
        Session 931: Process message through UnifiedPAEntrypoint.

        Returns structured response with trace_id.
        """
        try:
            # Lazy load UnifiedPA to avoid circular imports
            if self.unified_pa is None:
                from core.services.unified_pa_entrypoint import get_unified_pa
                self.unified_pa = get_unified_pa(self.user)

            # Process through unified entrypoint
            result = await self.unified_pa.process_message(
                message=message,
                context={'is_welcome': is_welcome},
                generate_audio=generate_audio
            )

            # Convert to WebSocket response format
            return {
                'type': 'message',
                'content': result.content,
                'trace_id': result.trace_id,
                'tool_runs': result.tool_runs,
                'audio_url': result.audio_url,
                'intent': result.intent,
                'profile_completeness': result.profile_completeness,
                'latency_ms': result.latency_ms,
            }

        except Exception as e:
            logger.error(f"UnifiedPA processing failed: {e}", exc_info=True)
            # Fallback to basic response
            return await self._generate_fallback_response(message, is_welcome)

    async def _generate_fallback_response(self, message: str, is_welcome: bool = False) -> dict:
        """
        Fallback response if UnifiedPA fails.
        Uses old LLM-based approach as backup.
        """
        try:
            from core.llm_enforcer import LLMEnforcer
            enforcer = LLMEnforcer()

            user_name = getattr(self.user, 'first_name', None) or getattr(self.user, 'username', 'there')

            system_context = f"""You are a helpful AI assistant for {user_name}.
Be friendly and helpful. If this is a welcome message, introduce yourself briefly."""

            result = await asyncio.to_thread(
                enforcer.enforce_real_ai,
                prompt=message if not is_welcome else f"Welcome {user_name}",
                context=system_context,
                agent_name="PersonalAssistantFallback",
                task_type="conversation",
                max_tokens=300
            )

            content = result.get('response', f"Hi {user_name}! How can I help you today?") if result.get('success') else f"Hi {user_name}! How can I help you today?"

            return {
                'type': 'message',
                'content': content,
                'trace_id': 'fallback',
                'tool_runs': [],
                'audio_url': None,
                'intent': 'fallback',
                'profile_completeness': None,
                'latency_ms': 0,
            }
        except Exception as e:
            logger.error(f"Fallback response also failed: {e}")
            return {
                'type': 'message',
                'content': "Hi! I'm here to help. What would you like to do?",
                'trace_id': 'error-fallback',
                'tool_runs': [],
                'audio_url': None,
                'intent': None,
                'profile_completeness': None,
                'latency_ms': 0,
            }

    # =========================================================================
    # LEGACY METHODS (kept for backward compatibility, not primary path)
    # =========================================================================

    def detect_intent(self, message):
        """
        Detect user intent from message content.
        Returns intent category for routing.
        """
        message_lower = message.lower()

        # Income generation keywords
        if any(word in message_lower for word in [
            'work', 'job', 'freelance', 'income', 'money', 'earn', 'gig',
            'opportunity', 'opportunities', 'employment', 'hire', 'contract'
        ]):
            return 'income_generation'

        # Investment advice keywords
        elif any(word in message_lower for word in [
            'invest', 'stock', 'advisor', 'buffett', 'cathie', 'dalio',
            'portfolio', 'market', 'trading', 'dividend', 'finance'
        ]):
            return 'investment_advice'

        # Content creation keywords
        elif any(word in message_lower for word in [
            'create', 'generate', 'blog', 'image', 'video', 'content',
            'write', 'design', 'social', 'twitter', 'instagram', 'article'
        ]):
            return 'content_creation'

        # Data analysis keywords
        elif any(word in message_lower for word in [
            'data', 'spider', 'intelligence', 'analyze', 'search',
            'find', 'discover', 'collect', 'scrape', 'monitor'
        ]):
            return 'data_analysis'

        # Agent execution keywords
        elif any(word in message_lower for word in [
            'agent', 'execute', 'run', 'task', 'automate', 'ai'
        ]):
            return 'agent_execution'

        # Advisor consultation
        elif any(word in message_lower for word in [
            'advice', 'consult', 'ask', 'recommend', 'suggest', 'expert'
        ]):
            return 'advisor_consultation'

        else:
            return 'general'

    async def generate_ai_response(self, message, is_welcome=False):
        """
        Generate response using REAL AI (GPT-5-mini).
        """
        user_name = self.user.first_name or self.user.username

        # Get system stats for context
        agent_count = await self.get_agent_count()
        advisor_count = await self.get_advisor_count()
        spider_count = await self.get_spider_count()
        data_count = await self.get_spider_data_count()
        opportunity_count = await self.get_opportunity_count()

        # Session 930: Get profile completeness context
        profile_context = await self.get_profile_context()

        # Build profile section for system context
        profile_section = ""
        if profile_context['has_gaps'] and profile_context['completeness_percent'] < 80:
            profile_section = f"""

USER PROFILE STATUS:
- Profile completeness: {profile_context['completeness_percent']}%
- Missing information in: {profile_context['question_category'] or 'various areas'}

PROFILE PROMPTING GUIDELINES:
When natural and conversational, consider asking about missing profile information.
Suggested question to weave in naturally: "{profile_context['suggested_question']}"
- Only ask if it fits the conversation flow
- Don't force it if user is focused on a specific task
- Frame it as helping you serve them better
- If they answer, acknowledge and thank them"""
        elif profile_context['completeness_percent'] >= 80:
            profile_section = f"""

USER PROFILE STATUS:
- Profile completeness: {profile_context['completeness_percent']}% (well-filled!)
- You have good context about this user to personalize responses"""

        # Build system context
        system_context = f"""You are an intelligent Personal Assistant for {user_name} in the Unified AI Platform.

SYSTEM CAPABILITIES:
- {agent_count} AI Agents available for task execution
- {advisor_count} Legendary Advisors (Warren Buffett, Cathie Wood, Ray Dalio, etc.)
- {spider_count} Active Spiders collecting real-time intelligence
- {data_count}+ data items in Intelligence Hub
- {opportunity_count} income opportunities currently available
- Content Studio with 70+ image styles, blog generation, video scripts, social media
- Real-time data analysis and monitoring

AVAILABLE FEATURES:
1. Income Generation - Find work opportunities, freelance gigs, job matches
2. Investment Advice - Consult with legendary investors and advisors
3. Content Creation - Generate images, blogs, videos, social media content
4. Data Intelligence - Access spider network data and opportunities
5. Agent Execution - Run any of the {agent_count} specialized AI agents
6. Advisor Consultation - Get expert guidance from {advisor_count} advisors
{profile_section}

INSTRUCTIONS:
- Be friendly, conversational, and helpful
- Address the user by name: {user_name}
- Provide specific, actionable responses
- Reference real system capabilities and stats
- Suggest concrete next steps
- Use emojis sparingly (max 2-3 per message)
{"- This is a welcome message - explain what you can do and ask what they'd like help with" if is_welcome else "- Respond directly to their request"}
"""

        try:
            # Call REAL AI using LLMEnforcer
            result = await asyncio.to_thread(
                self.llm_enforcer.enforce_real_ai,
                prompt=message,
                context=system_context,
                agent_name="PersonalAssistantV2",
                task_type="conversation",
                max_tokens=400
            )

            if result['success']:
                logger.info(f"✅ Generated REAL AI response using {result.get('model', 'GPT-5-mini')}")

                # Session 930: Record profile prompt if we suggested one
                if profile_context['has_gaps'] and profile_context['question_field']:
                    await self.record_profile_prompt(
                        field_name=profile_context['question_field'],
                        prompt_text=profile_context['suggested_question'] or ''
                    )

                return result['response']
            else:
                logger.warning(f"⚠️ AI generation failed: {result.get('error')}")
                return self.get_fallback_response(message, user_name, agent_count, advisor_count, spider_count)

        except Exception as e:
            logger.error(f"❌ Error calling LLM: {e}")
            return self.get_fallback_response(message, user_name, agent_count, advisor_count, spider_count)

    def get_fallback_response(self, message, user_name, agent_count, advisor_count, spider_count):
        """Fallback response if AI fails"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['work', 'job', 'income', 'money']):
            return f"Hi {user_name}! I can help you find income opportunities. We have {spider_count} spiders searching right now. Would you like to see current opportunities?"
        elif any(word in message_lower for word in ['invest', 'advisor', 'stock']):
            return f"Hi {user_name}! I can connect you with {advisor_count} legendary advisors for investment guidance. Who would you like to consult?"
        elif any(word in message_lower for word in ['create', 'content', 'image', 'blog']):
            return f"Hi {user_name}! The Content Studio is ready with 70+ image styles, blog generation, and more. What would you like to create?"
        else:
            return f"Hi {user_name}! I have {agent_count} AI agents, {advisor_count} advisors, and {spider_count} spiders ready to help. What would you like to do?"

    async def handle_intent(self, intent, message):
        """
        Generate intelligent response using REAL AI instead of hardcoded responses.
        Returns response dictionary.
        """
        # Use REAL AI to generate response
        ai_response = await self.generate_ai_response(message)

        return {
            'type': 'message',
            'content': ai_response
        }

    # Database query methods (async)

    @database_sync_to_async
    def get_agent_count(self):
        """Get count of available agents"""
        from core.models_unified_system import Agent
        return Agent.objects.count()

    @database_sync_to_async
    def get_advisor_count(self):
        """Get count of available advisors"""
        from core.models_unified_system import Advisor
        return Advisor.objects.count()

    @database_sync_to_async
    def get_spider_count(self):
        """Get count of active spiders"""
        from ai_core.spiders.spider_registry import spider_registry
        return len(spider_registry.list_spiders())

    @database_sync_to_async
    def get_spider_data_count(self):
        """Get count of spider data items"""
        from core.models_unified_system import SpiderData
        return SpiderData.objects.count()

    @database_sync_to_async
    def get_opportunity_count(self):
        """Get count of available opportunities"""
        from core.models_unified_system import Opportunity
        return Opportunity.objects.filter(status='active').count()

    @database_sync_to_async
    def get_profile_context(self):
        """
        Session 930: Get profile completeness context for natural prompting.

        Returns dict with completeness score and suggested question.
        """
        try:
            from core.services.profile_completeness_service import get_profile_completeness_service

            service = get_profile_completeness_service()
            score = service.get_completeness_score(self.user)
            next_question = service.get_next_question(self.user)

            context = {
                'completeness_score': score,
                'completeness_percent': int(score * 100),
                'has_gaps': next_question is not None,
                'suggested_question': None,
                'question_field': None,
                'question_category': None,
            }

            if next_question:
                # Format as conversational prompt
                context['suggested_question'] = service._format_conversational_prompt(
                    next_question, context=None
                )
                context['question_field'] = next_question.field_name
                context['question_category'] = next_question.category

            return context
        except Exception as e:
            logger.debug(f"Profile context fetch failed: {e}")
            return {
                'completeness_score': 0,
                'completeness_percent': 0,
                'has_gaps': False,
                'suggested_question': None,
                'question_field': None,
                'question_category': None,
            }

    @database_sync_to_async
    def record_profile_prompt(self, field_name: str, prompt_text: str):
        """
        Session 930: Record that we suggested a profile question to the AI.

        This tracks which questions were offered so we don't repeat them frequently.
        """
        try:
            from core.services.profile_completeness_service import get_profile_completeness_service

            service = get_profile_completeness_service()
            service.record_prompt(self.user, field_name, prompt_text)
            logger.debug(f"Recorded profile prompt for field: {field_name}")
        except Exception as e:
            logger.debug(f"Profile prompt recording failed: {e}")
