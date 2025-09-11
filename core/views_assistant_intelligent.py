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
        
        # Determine routing strategy
        if force_direct or not use_intelligent_routing:
            # Direct processing without agent routing
            logger.info("Using direct processing (routing disabled)")
            result = _process_direct(user, message, context, response_metadata)
        else:
            # Intelligent routing through specialized agents
            result = _process_with_intelligent_routing(
                user, message, context, agent_router, prompt_optimizer, response_metadata
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


def _process_with_intelligent_routing(user, message: str, context: str, 
                                    agent_router: AgentRouter, prompt_optimizer: IntelligentPromptOptimizer,
                                    response_metadata: Dict[str, Any]) -> Dict[str, Any]:
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
        
        # Route through Intelligent Prompting Agent
        prompt_result = agent_router.execute_intelligent_prompting(message, optimization_context)
        
        if prompt_result.get('success'):
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
        
        if best_agent and best_agent['score'] > 0.8:  # High confidence threshold
            logger.info(f"Routing to specialized agent: {best_agent['agent_name']}")
            
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
                
                return {
                    'message': agent_result['content'],
                    'provider': agent_result.get('provider', 'openai'),
                    'model': agent_result.get('model', 'gpt-4'),
                    'token_usage': agent_result.get('token_usage', {}),
                    'generation_time_ms': agent_result.get('generation_time_ms', 0)
                }
            else:
                logger.warning(f"Specialized agent {best_agent['agent_name']} failed: {agent_result.get('error')}")
                # Fall through to direct processing
    
    # Step 3: Fall back to direct processing with enhanced prompt
    logger.info("Using enhanced direct processing")
    return _process_direct(user, message, context, response_metadata)


def _process_direct(user, message: str, context: str, response_metadata: Dict[str, Any]) -> Dict[str, Any]:
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
        system_prompt = f"""You are {getattr(user, 'username', user.email)}'s personal AI assistant with access to their conversation history and knowledge base.

You have learned from all our previous conversations and can recall what we've discussed. Use this knowledge naturally when relevant.

Response Guidelines:
- Be conversational and natural, like talking to a knowledgeable friend
- Reference our past conversations when relevant ("As we discussed earlier...")
- Provide helpful, accurate responses based on the context
- If you find relevant information in the knowledge base, use it seamlessly
- Keep responses focused but not overly terse - aim for clarity

Remember: You're learning and growing from every conversation. Each interaction helps you understand the user better."""
        
        # Add context to user message if available
        enhanced_message = message
        if context:
            enhanced_message = f"""Knowledge Base Context:
{context[:1000]}...

User Question: {message}

Please provide a comprehensive response using both your general knowledge and the specific context provided."""
        
        # Generate AI response with correct parameters
        if 'gpt-5' in model.lower():
            config = {'max_completion_tokens': 1200}
        else:
            config = {'max_tokens': 1200, 'temperature': 0.7}
        
        result = ai_manager.generate_content(
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            user_prompt=enhanced_message,
            config=config
        )
        
        if result.success and result.content:
            # Save conversation to memory for learning
            try:
                logger.info(f"Attempting to save conversation in intelligent assistant...")
                from core.conversation_memory import conversation_memory
                saved = conversation_memory.save_conversation(
                    user_id=str(user.id),  # Convert UUID to string
                    user_message=message,
                    assistant_response=result.content,
                    metadata={
                        'conversation_id': response_metadata.get('conversation_id'),
                        'provider': provider,
                        'model': result.model_used or model,
                        'rag_used': response_metadata.get('rag_used', False),
                        'routing': 'direct'
                    }
                )
                logger.info(f"Conversation save result in intelligent assistant: {saved}")
            except Exception as e:
                logger.error(f"Failed to save conversation in intelligent assistant: {e}")
            
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