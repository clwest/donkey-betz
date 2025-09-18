"""
Intelligent Personal Assistant with Agent Integration
Routes through Intelligent Prompting System and specialized agents for optimal responses.
"""

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
import uuid
import logging
import json
from typing import Dict, Any, Optional

from .agent_integration import AgentRouter, IntelligentPromptOptimizer
from .views_assistant_rag_enhanced import RAGAssistant, _get_knowledge_base_size, _get_total_embeddings
from content.ai_providers import AIProviderManager
from mythology.services import MythologyPreventionService, HallucinationFlaggingService
from .assistant_prompt_enhanced import (
    get_enhanced_system_prompt,
    format_rag_response_with_sources,
    validate_response_for_hallucinations,
    apply_mythology_guards
)
from .personal_assistant_integration import personal_assistant_integration
from .personal_assistant_agent_integration import personal_assistant_agent_integration

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assistant_chat_intelligent(request):
    """
    Intelligent Personal AI Assistant Chat with Agent Integration
    Routes through Intelligent Prompting System for optimized responses
    """
    user = request.user
    
    try:
        # Get request data
        message = request.data.get('message', '').strip()
        conversation_id = request.data.get('conversation_id', str(uuid.uuid4()))
        use_rag = request.data.get('use_rag', True)
        use_intelligent_routing = request.data.get('use_intelligent_routing', True)
        force_direct = request.data.get('force_direct', False)  # Bypass intelligent routing for testing
        
        logger.info(f"Intelligent Assistant - Message: {message[:50]}... RAG: {use_rag}, Routing: {use_intelligent_routing}")
        
        if not message:
            return Response({
                'error': 'Message is required',
                'timestamp': datetime.now().isoformat()
            }, status=400)
        
        # Initialize mythology prevention and flagging services
        mythology_service = MythologyPreventionService()
        flagging_service = HallucinationFlaggingService()
        
        # Guard the input prompt for mythology
        guard_result = mythology_service.guard_prompt(message, user=user)
        guarded_message = guard_result['prompt']
        
        # Log if mythology was detected in input
        if guard_result['mythology_detected']:
            logger.warning(f"Mythology detected in user prompt: {guard_result['patterns_found']}")
            logger.info(f"Applied guards: {guard_result['guards_applied']}")
        
        # Use the guarded message for processing
        message = guarded_message

        # Get System Self-Awareness context
        use_self_awareness = request.data.get('use_self_awareness', True)
        system_awareness_context = None
        if use_self_awareness:
            try:
                system_awareness_context = personal_assistant_integration.enhance_assistant_context(
                    message, conversation_id
                )
                logger.info(f"System awareness: {system_awareness_context.get('system_awareness', {}).get('operational_percentage', 0)}% operational")
            except Exception as e:
                logger.error(f"Error getting system awareness: {e}")

        # Initialize components
        rag_assistant = RAGAssistant(user)
        agent_router = AgentRouter(user)
        prompt_optimizer = IntelligentPromptOptimizer(user)
        
        # Build RAG context
        context = ""
        sources = []
        rag_actually_used = False
        if use_rag:
            context, sources = rag_assistant.build_context(message)
            rag_actually_used = bool(sources)
            logger.info(f"RAG search found {len(sources)} sources")
        
        # Initialize response metadata
        response_metadata = {
            'conversation_id': conversation_id,
            'timestamp': datetime.now().isoformat(),
            'rag_used': rag_actually_used,
            'sources': sources[:3] if sources else [],
            'knowledge_base_size': _get_knowledge_base_size(),
            'total_embeddings_available': _get_total_embeddings(),
            'routing_used': False,
            'agent_used': None,
            'prompt_optimized': False
        }

        # Add system awareness to metadata if available
        if system_awareness_context:
            response_metadata['system_awareness'] = {
                'operational_percentage': system_awareness_context.get('system_awareness', {}).get('operational_percentage', 0),
                'platform_reality': system_awareness_context.get('system_awareness', {}).get('platform_reality', 'unknown'),
                'real_components': system_awareness_context.get('system_awareness', {}).get('real_components', []),
                'mock_components': system_awareness_context.get('system_awareness', {}).get('mock_components', []),
                'broken_flows': system_awareness_context.get('system_awareness', {}).get('broken_flows', []),
                'recommendations': system_awareness_context.get('recommendations', []),
                'routing': system_awareness_context.get('routing', {})
            }
        
        # Check if this should be routed through our 149-agent system
        use_agent_execution = request.data.get('use_agent_execution', True)
        if use_agent_execution and personal_assistant_agent_integration.should_route_to_agents(message):
            logger.info("Routing through 149-agent system for task execution")
            # Handle async execution in Django-safe way
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(_process_with_agent_execution(
                    user, message, context, response_metadata, system_awareness_context
                ))
            finally:
                loop.close()
        elif force_direct or not use_intelligent_routing:
            # Direct processing without agent routing
            logger.info("Using direct processing (routing disabled)")
            result = _process_direct(user, message, context, response_metadata, system_awareness_context)
        else:
            # Intelligent routing through specialized agents
            result = _process_with_intelligent_routing(
                user, message, context, agent_router, prompt_optimizer, response_metadata, system_awareness_context
            )
        
        # Ensure we have a valid result
        if not result or not result.get('message'):
            logger.warning("No valid result from processing, using fallback")
            result = {
                'message': f"I received your message: '{message}'. I'm currently experiencing technical difficulties. Please try again.",
                'provider': 'fallback',
                'model': 'error_fallback'
            }
        
        # Validate response for mythology
        if result.get('message'):
            validation_result = mythology_service.validate_response(
                result['message'], 
                guard_result['original_prompt'], 
                user=user
            )
            
            # Log if mythology was detected in response
            if validation_result['mythology_risk'] > 0.3:
                logger.warning(f"Mythology detected in AI response: {validation_result['patterns_found']}")
                logger.info(f"Risk score: {validation_result['mythology_risk']:.2f}")
                
                # Flag suspicious responses for review
                try:
                    flagged = flagging_service.flag_suspicious_response(
                        original_prompt=guard_result['original_prompt'],
                        response=result['message'],
                        risk_score=validation_result['mythology_risk'],
                        patterns=validation_result['patterns_found'],
                        user=user,
                        session_id=conversation_id
                    )
                    logger.info(f"Flagged suspicious response for review: {flagged.id}")
                    
                    # Add flagging info to response metadata
                    result['flagged_for_review'] = {
                        'flagged_id': str(flagged.id),
                        'priority': flagged.priority,
                        'requires_attention': flagged.requires_immediate_attention
                    }
                except Exception as e:
                    logger.error(f"Failed to flag suspicious response: {e}")
            
            # Add mythology metadata to response
            result['mythology_analysis'] = {
                'input_guarded': guard_result['mythology_detected'],
                'input_patterns': guard_result['patterns_found'],
                'output_risk': validation_result['mythology_risk'],
                'output_patterns': validation_result['patterns_found'],
                'needs_regeneration': validation_result['needs_regeneration']
            }
            
            # If response has high mythology risk, add warning
            if validation_result['needs_regeneration']:
                result['mythology_warning'] = "Response may contain inaccurate information. Please verify claims independently."
        
        # Merge response metadata
        result.update(response_metadata)
        return Response(result)
        
    except Exception as e:
        logger.error(f"Intelligent Assistant error: {str(e)}")
        return Response({
            'message': "I'm sorry, I encountered an unexpected error. Please try again.",
            'conversation_id': conversation_id if 'conversation_id' in locals() else str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'routing_used': False
        }, status=500)


async def _process_with_agent_execution(user, message: str, context: str,
                                      response_metadata: Dict[str, Any],
                                      system_awareness_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Process message through the 149-agent system for task execution
    """
    try:
        logger.info("Processing through 149-agent system")

        # Check if user wants to select specific agents
        selected_agents = None  # Could be extracted from message or context

        # Execute through agents
        execution_result = await personal_assistant_agent_integration.execute_through_agents(
            message, selected_agents
        )

        if execution_result.get('success'):
            # Create response message
            if execution_result.get('execution_type') == 'selected_agents':
                agent_summary = execution_result.get('summary', '')
                response_text = f"I executed your request through {len(execution_result['agents_used'])} specialized agents:\n\n{agent_summary}"
            else:
                primary_agent = execution_result.get('primary_agent', 'agent')
                result = execution_result.get('result', {})

                if result.get('success'):
                    response_text = f"I completed your request using the **{primary_agent}**.\n\n"

                    # Add specific result details
                    agent_result = result.get('result', {})
                    if 'file_created' in agent_result:
                        response_text += f"✅ Created: {agent_result['file_created']}\n"
                    if 'content_generated' in agent_result:
                        response_text += f"✅ Generated content successfully\n"
                    if 'image_generated' in agent_result:
                        response_text += f"✅ Generated image successfully\n"

                    # Add preview if available
                    if 'content_preview' in agent_result:
                        response_text += f"\nPreview: {agent_result['content_preview'][:200]}..."
                else:
                    response_text = f"I attempted to process your request through **{primary_agent}**, but encountered an issue: {result.get('error', 'Unknown error')}"

            # Add agent system info
            response_metadata.update({
                'agent_execution_used': True,
                'agents_involved': execution_result.get('agents_used', [execution_result.get('primary_agent')]),
                'execution_type': execution_result.get('execution_type'),
                'agent_results': execution_result
            })

            return {
                'message': response_text,
                'provider': 'agent_system',
                'model': 'multi_agent_execution',
                'execution_details': execution_result
            }
        else:
            # Agent execution failed, provide recommendations
            recommendation = personal_assistant_agent_integration.create_agent_recommendation(message)
            agent_summary = personal_assistant_agent_integration.get_available_agent_summary()

            response_text = f"I couldn't execute your request directly through agents. {recommendation}\n\nI have access to {agent_summary['active_agents']} active agents across different specializations."

            # Fall back to regular processing
            return _process_direct(user, message, context, response_metadata, system_awareness_context)

    except Exception as e:
        logger.error(f"Error in agent execution: {str(e)}")
        # Fall back to regular processing
        return _process_direct(user, message, context, response_metadata, system_awareness_context)


def _process_with_intelligent_routing(user, message: str, context: str,
                                    agent_router: AgentRouter, prompt_optimizer: IntelligentPromptOptimizer,
                                    response_metadata: Dict[str, Any], system_awareness_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Process message using intelligent agent routing
    """
    logger.info("Processing with intelligent routing")
    
    # Step 1: Check if this should go through Intelligent Prompting Agent
    if agent_router.should_use_intelligent_prompting(message):
        logger.info("Routing through Intelligent Prompting Agent")
        
        # Prepare context for prompt optimization
        optimization_context = {
            'rag_context': context[:500] if context else None,
            'user_profile': {
                'username': getattr(user, 'username', 'user'),
                'preferences': 'comprehensive_responses'
            }
        }

        # Add system awareness if available
        if system_awareness_context:
            optimization_context['system_awareness'] = {
                'operational_percentage': system_awareness_context.get('system_awareness', {}).get('operational_percentage', 0),
                'platform_reality': system_awareness_context.get('system_awareness', {}).get('platform_reality', 'unknown'),
                'recommendations': system_awareness_context.get('recommendations', [])[:3]  # Include top 3 recommendations
            }
        
        # Route through Intelligent Prompting Agent
        prompt_result = agent_router.execute_intelligent_prompting(message, optimization_context)
        
        if prompt_result.get('success') and prompt_result.get('content'):
            logger.info("Intelligent Prompting Agent successfully optimized the prompt")
            response_metadata.update({
                'routing_used': True,
                'agent_used': 'Intelligent Prompting Agent',
                'prompt_optimized': True,
                'optimization_details': {
                    'original_message': message,
                    'optimized_by': 'Intelligent Prompting Agent'
                }
            })
            
            return {
                'message': prompt_result['content'],
                'provider': prompt_result.get('provider', 'openai'),
                'model': prompt_result.get('model', 'gpt-5-mini'),
                'token_usage': prompt_result.get('token_usage', {}),
                'generation_time_ms': prompt_result.get('generation_time_ms', 0)
            }
        else:
            logger.warning(f"Intelligent Prompting Agent failed: {prompt_result.get('error')}")
            # Fall through to other routing options
    
    # Step 2: Check if this should go through other specialized agents
    if agent_router.should_use_agent_routing(message):
        logger.info("Checking for specialized agent routing")
        
        best_agent = agent_router.find_best_agent(message, exclude_agents=['Personal Assistant Agent'])
        
        if best_agent and best_agent['score'] > 0.4:  # Lowered threshold for better agent utilization
            logger.info(f"Routing to specialized agent: {best_agent['agent_name']} (score: {best_agent['score']})")
            
            agent_result = agent_router.execute_agent_for_task(
                message=message,
                agent_name=best_agent['agent_name'],
                context={'rag_context': context}
            )
            
            if agent_result.get('success'):
                logger.info(f"Specialized agent {best_agent['agent_name']} completed successfully")
                response_metadata.update({
                    'routing_used': True,
                    'agent_used': best_agent['agent_name'],
                    'agent_score': best_agent['score']
                })
                
                # Collect implicit feedback on the response
                from core.feedback_collector import FeedbackCollector, ResponseAnalyzer
                
                feedback_collector = FeedbackCollector()
                response_analyzer = ResponseAnalyzer()
                
                # Analyze response quality
                quality_analysis = response_analyzer.analyze_response_quality(
                    agent_result.get('content', ''),
                    message
                )
                
                # Collect implicit feedback
                execution_time = agent_result.get('generation_time_ms', 0) / 1000.0  # Convert to seconds
                implicit_feedback = feedback_collector.collect_implicit_feedback(
                    execution_id=agent_result.get('execution_id', ''),
                    response=agent_result.get('content', ''),
                    response_time=execution_time,
                    user=user
                )
                
                # Log quality metrics
                logger.info(f"Response quality: {quality_analysis['quality_score']:.2f}, signals: {quality_analysis['signals']}")
                
                return {
                    'message': agent_result['content'],
                    'provider': agent_result.get('provider', 'openai'),
                    'model': agent_result.get('model', 'gpt-4'),
                    'token_usage': agent_result.get('token_usage', {}),
                    'generation_time_ms': agent_result.get('generation_time_ms', 0),
                    'quality_score': quality_analysis['quality_score'],
                    'execution_id': agent_result.get('execution_id', '')
                }
            else:
                logger.warning(f"Specialized agent {best_agent['agent_name']} failed: {agent_result.get('error')}")
                # Fall through to direct processing
    
    # Step 3: Fall back to direct processing with enhanced prompt
    logger.info("Using enhanced direct processing")
    return _process_direct(user, message, context, response_metadata, system_awareness_context)


def _process_direct(user, message: str, context: str, response_metadata: Dict[str, Any], system_awareness_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Process message directly without agent routing (fallback method)
    """
    try:
        # Get AI provider
        ai_manager = AIProviderManager()
        available_providers = ai_manager.get_available_providers()

        if not available_providers:
            logger.warning("No AI providers available for direct processing")
            return {
                'message': f"I understand you asked: '{message}'. " +
                          (f"I found {len(response_metadata.get('sources', []))} relevant items in the knowledge base. " if response_metadata.get('sources') else "") +
                          "However, I'm currently running in mock mode. Please configure AI provider API keys for full functionality.",
                'provider': 'mock',
                'model': 'fallback'
            }
        
        # Select provider and model
        provider = None
        model = None
        
        if 'openai' in available_providers:
            provider = 'openai'
            model = 'gpt-5-mini'
        elif 'anthropic' in available_providers:
            provider = 'anthropic'
            model = 'claude-3-haiku-20240307'
        elif 'google' in available_providers:
            provider = 'google'
            model = 'gemini-pro'
        else:
            provider = available_providers[0]
            model = 'default'
        
        # Build enhanced system prompt (optimized for personal assistant role)
        # Use enhanced system prompt that prevents hallucinations
        has_rag_context = bool(response_metadata.get('sources'))
        source_count = len(response_metadata.get('sources', []))
        system_prompt = get_enhanced_system_prompt(user, has_rag_context, source_count)

        # Add system awareness to the prompt if available
        if system_awareness_context:
            awareness = system_awareness_context.get('system_awareness', {})
            if awareness:
                system_prompt += f"""

SYSTEM AWARENESS:
- Platform is {awareness.get('operational_percentage', 0)}% operational ({awareness.get('platform_reality', 'unknown')})
- Real Components: {', '.join(awareness.get('real_components', [])[:3]) if awareness.get('real_components') else 'None'}
- Issues: {', '.join(awareness.get('broken_flows', [])[:2]) if awareness.get('broken_flows') else 'None'}

When relevant to the user's question, briefly mention system status."""
        
        # Add compressed context to user message if available
        enhanced_message = message
        if context:
            # Very brief context format to avoid token bloat
            enhanced_message = f"Context: {context[:200]}\n\nQuestion: {message}"
        
        # Generate AI response with balanced token limits
        if 'gpt-5' in model.lower():
            config = {'max_completion_tokens': 1000}
        else:
            config = {'max_tokens': 1000, 'temperature': 0.7}
        
        result = ai_manager.generate_content(
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            user_prompt=enhanced_message,
            config=config
        )
        
        if result.success and result.content:
            # Validate and enforce response length limits
            def validate_response_length(content: str) -> str:
                """Enforce 5-sentence maximum and 800 character limit"""
                if not content:
                    logger.warning("Empty content received from AI provider")
                    return "I can provide information about your knowledge base, but I need a moment to process the request properly. Please try asking again."
                    
                # Split into sentences
                sentences = [s.strip() for s in content.split('.') if s.strip()]
                
                # Allow up to 5 sentences for comprehensive responses
                if len(sentences) > 5:
                    truncated = '. '.join(sentences[:5]) + '.'
                    logger.info(f"Truncated response from {len(sentences)} to 5 sentences")
                    return truncated
                
                # Check character length (max 800 characters - balanced approach)
                if len(content) > 800:
                    # Find a good breaking point near the limit
                    truncated = content[:797] + "..."
                    logger.info(f"Truncated response from {len(content)} to 800 characters")
                    return truncated
                    
                return content
            
            # Apply length validation
            validated_content = validate_response_length(result.content)

            # Extract confidence scores from sources
            confidence_scores = []
            if response_metadata.get('sources'):
                confidence_scores = [s.get('similarity', 0.5) for s in response_metadata['sources']]

            # Format response with source attribution
            validated_content = format_rag_response_with_sources(
                validated_content,
                response_metadata.get('sources', []),
                confidence_scores
            )

            # Check for hallucinations
            available_data = {
                'total_embeddings': response_metadata.get('total_embeddings_available', 0),
                'knowledge_base_size': response_metadata.get('knowledge_base_size', 0)
            }
            hallucination_check = validate_response_for_hallucinations(validated_content, available_data)

            if hallucination_check:
                logger.warning(f"Potential hallucinations detected: {hallucination_check}")
                # Add warning to metadata
                response_metadata['hallucination_warnings'] = hallucination_check

            # Apply mythology guards
            mythology_service = MythologyPreventionService()
            validated_content, mythology_patterns = apply_mythology_guards(validated_content, mythology_service)

            if mythology_patterns:
                logger.info(f"Mythology patterns corrected: {mythology_patterns}")
                response_metadata['mythology_corrected'] = True

            result.content = validated_content

            # Log response metrics for monitoring
            char_count = len(validated_content)
            sentence_count = len([s for s in validated_content.split('.') if s.strip()])
            logger.info(f"Response metrics - Characters: {char_count}, Sentences: {sentence_count}")
            
            # Save conversation to CHAT memory (not document embeddings)
            try:
                logger.info(f"Saving to chat memory (separate from document embeddings)...")
                from core.conversation_memory_fixed import conversation_memory_fixed
                saved = conversation_memory_fixed.save_conversation(
                    user_id=str(user.id),  # Convert UUID to string
                    user_message=message,
                    assistant_response=result.content,
                    metadata={
                        'conversation_id': response_metadata.get('conversation_id'),
                        'provider': provider,
                        'model': result.model_used or model,
                        'rag_used': response_metadata.get('rag_used', False),
                        'rag_context': context[:200] if context else None,  # Summary of RAG context used
                        'routing': 'direct',
                        'generation_time_ms': result.generation_time_ms,
                        'data_type': 'chat_conversation'  # Clear distinction
                    }
                )
                logger.info(f"Chat conversation saved (not as document embedding): {saved}")
            except Exception as e:
                logger.error(f"Failed to save chat conversation: {e}")
            
            return {
                'message': result.content,
                'provider': provider,
                'model': result.model_used or model,
                'token_usage': result.token_usage,
                'generation_time_ms': result.generation_time_ms
            }
        else:
            logger.error(f"Direct processing failed: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}")
            return {
                'message': f"I apologize, but I encountered an error processing your request: '{message}'. Please try again.",
                'provider': 'error',
                'model': 'fallback'
            }
            
    except Exception as e:
        logger.error(f"Error in direct processing: {e}")
        return {
            'message': f"I'm sorry, I encountered a technical error while processing your message. Please try again.",
            'provider': 'error',
            'model': 'fallback'
        }