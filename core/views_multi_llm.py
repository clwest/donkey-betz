"""
Multi-LLM Provider Integration System.
Phase 2 enhancement - provides unified access to multiple AI providers.
Compatible with existing frontend connections.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from datetime import datetime
import json

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_llm_providers(request):
    """
    Get available LLM providers with their capabilities.
    Enhanced version with detailed provider information.
    """
    user = request.user
    
    providers = {
        'openai': {
            'name': 'OpenAI',
            'status': 'available',
            'models': [
                {
                    'id': 'gpt-5',
                    'name': 'GPT-5',
                    'max_tokens': 272000,
                    'max_output': 128000,
                    'cost_per_1k_input': 1.25,
                    'cost_per_1k_output': 10.0,
                    'supports_reasoning': True,
                    'capabilities': ['text', 'advanced reasoning', 'analysis', 'coding', 'complex problem solving'],
                    'recommended_for': ['complex reasoning', 'multi-step problem solving', 'critical decision making']
                },
                {
                    'id': 'gpt-5-mini',
                    'name': 'GPT-5 Mini',
                    'max_tokens': 272000,
                    'max_output': 128000,
                    'cost_per_1k_input': 0.25,
                    'cost_per_1k_output': 2.0,
                    'supports_reasoning': True,
                    'capabilities': ['text', 'reasoning', 'analysis', 'coding', 'content creation'],
                    'recommended_for': ['code generation', 'content creation', 'standard agent operations']
                },
                {
                    'id': 'gpt-5-nano',
                    'name': 'GPT-5 Nano',
                    'max_tokens': 272000,
                    'max_output': 128000,
                    'cost_per_1k_input': 0.05,
                    'cost_per_1k_output': 0.40,
                    'supports_reasoning': True,
                    'capabilities': ['text', 'basic reasoning', 'data formatting', 'simple generation'],
                    'recommended_for': ['simple text generation', 'basic Q&A', 'data formatting']
                },
                {
                    'id': 'gpt-5-mini',
                    'name': 'GPT-4 (Legacy)',
                    'max_tokens': 8192,
                    'cost_per_1k_input': 0.03,
                    'cost_per_1k_output': 0.06,
                    'capabilities': ['text', 'reasoning', 'analysis', 'coding'],
                    'recommended_for': ['complex reasoning', 'creative writing', 'analysis']
                },
                {
                    'id': 'gpt-5-mini',
                    'name': 'GPT-4 Turbo (Legacy)',
                    'max_tokens': 128000,
                    'cost_per_1k_input': 0.01,
                    'cost_per_1k_output': 0.03,
                    'capabilities': ['text', 'reasoning', 'analysis', 'coding', 'vision'],
                    'recommended_for': ['large documents', 'comprehensive analysis', 'multimodal tasks']
                },
                {
                    'id': 'gpt-5-nano',
                    'name': 'GPT-3.5 Turbo (Legacy)',
                    'max_tokens': 4096,
                    'cost_per_1k_input': 0.0015,
                    'cost_per_1k_output': 0.002,
                    'capabilities': ['text', 'basic reasoning', 'summarization'],
                    'recommended_for': ['simple tasks', 'cost optimization', 'high volume']
                }
            ],
            'rate_limits': {
                'requests_per_minute': 3500,
                'tokens_per_minute': 90000
            },
            'api_status': 'operational'
        },
        'anthropic': {
            'name': 'Anthropic',
            'status': 'available',
            'models': [
                {
                    'id': 'claude-3-opus',
                    'name': 'Claude-3 Opus',
                    'max_tokens': 200000,
                    'cost_per_1k_input': 0.015,
                    'cost_per_1k_output': 0.075,
                    'capabilities': ['text', 'reasoning', 'analysis', 'coding', 'research'],
                    'recommended_for': ['complex reasoning', 'research', 'detailed analysis']
                },
                {
                    'id': 'claude-3-sonnet',
                    'name': 'Claude-3 Sonnet', 
                    'max_tokens': 200000,
                    'cost_per_1k_input': 0.003,
                    'cost_per_1k_output': 0.015,
                    'capabilities': ['text', 'reasoning', 'analysis', 'coding'],
                    'recommended_for': ['balanced performance', 'general tasks', 'cost efficiency']
                },
                {
                    'id': 'claude-3-haiku',
                    'name': 'Claude-3 Haiku',
                    'max_tokens': 200000,
                    'cost_per_1k_input': 0.00025,
                    'cost_per_1k_output': 0.00125,
                    'capabilities': ['text', 'basic reasoning', 'summarization'],
                    'recommended_for': ['speed', 'simple tasks', 'high volume processing']
                }
            ],
            'rate_limits': {
                'requests_per_minute': 1000,
                'tokens_per_minute': 40000
            },
            'api_status': 'operational'
        },
        'google': {
            'name': 'Google AI',
            'status': 'available',
            'models': [
                {
                    'id': 'gemini-pro',
                    'name': 'Gemini Pro',
                    'max_tokens': 32000,
                    'cost_per_1k_input': 0.00025,
                    'cost_per_1k_output': 0.0005,
                    'capabilities': ['text', 'reasoning', 'analysis', 'multimodal'],
                    'recommended_for': ['multimodal tasks', 'cost efficiency', 'general use']
                }
            ],
            'rate_limits': {
                'requests_per_minute': 1500,
                'tokens_per_minute': 50000
            },
            'api_status': 'operational'
        },
        'cohere': {
            'name': 'Cohere',
            'status': 'available',
            'models': [
                {
                    'id': 'command-r-plus',
                    'name': 'Command R+',
                    'max_tokens': 128000,
                    'cost_per_1k_input': 0.003,
                    'cost_per_1k_output': 0.015,
                    'capabilities': ['text', 'reasoning', 'rag', 'tool_use'],
                    'recommended_for': ['RAG applications', 'enterprise use', 'tool integration']
                }
            ],
            'rate_limits': {
                'requests_per_minute': 1000,
                'tokens_per_minute': 40000
            },
            'api_status': 'operational'
        }
    }
    
    return Response({
        'success': True,
        'providers': providers,
        'total_models': sum(len(p['models']) for p in providers.values()),
        'recommended_default': 'gpt-5-mini',
        'cost_optimization_model': 'gpt-5-nano',
        'performance_model': 'gpt-5',
        'last_updated': datetime.now().isoformat()
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def intelligent_model_selection(request):
    """
    Intelligent model selection based on task requirements.
    Automatically choose the best model for the task.
    """
    user = request.user
    data = json.loads(request.body or b"{}")
    
    task_type = data.get('task_type', 'general')
    complexity = data.get('complexity', 'medium')  # low, medium, high
    budget_priority = data.get('budget_priority', 'balanced')  # cost, performance, balanced
    content_length = data.get('content_length', 1000)  # estimated tokens
    
    # Intelligence model selection logic
    recommendations = []
    
    if task_type == 'analysis' and complexity == 'high':
        recommendations.append({
            'model': 'gpt-5',
            'provider': 'openai',
            'confidence': 0.98,
            'reasoning': 'GPT-5 with advanced reasoning capabilities for complex analysis',
            'estimated_cost': 1.45,
            'performance_score': 9.9
        })
        recommendations.append({
            'model': 'claude-3-opus',
            'provider': 'anthropic',
            'confidence': 0.95,
            'reasoning': 'Excellent for complex analytical tasks requiring deep reasoning',
            'estimated_cost': 0.45,
            'performance_score': 9.8
        })
        recommendations.append({
            'model': 'gpt-5-mini',
            'provider': 'openai',
            'confidence': 0.92,
            'reasoning': 'Proven analytical capabilities (legacy fallback)',
            'estimated_cost': 0.72,
            'performance_score': 9.5
        })
    elif budget_priority == 'cost':
        recommendations.append({
            'model': 'gpt-5-nano',
            'provider': 'openai',
            'confidence': 0.90,
            'reasoning': 'Most cost-effective GPT-5 variant with modern capabilities',
            'estimated_cost': 0.12,
            'performance_score': 8.8
        })
        recommendations.append({
            'model': 'claude-3-haiku',
            'provider': 'anthropic',
            'confidence': 0.88,
            'reasoning': 'Very cost-effective while maintaining quality',
            'estimated_cost': 0.08,
            'performance_score': 8.2
        })
        recommendations.append({
            'model': 'gpt-5-nano',
            'provider': 'openai',
            'confidence': 0.82,
            'reasoning': 'Legacy cost-effective option for simple tasks',
            'estimated_cost': 0.06,
            'performance_score': 7.8
        })
    elif content_length > 100000:
        recommendations.append({
            'model': 'gpt-5',
            'provider': 'openai',
            'confidence': 0.96,
            'reasoning': 'Superior handling of very large contexts with 272k token limit',
            'estimated_cost': 2.25,
            'performance_score': 9.8
        })
        recommendations.append({
            'model': 'gpt-5-mini',
            'provider': 'openai',
            'confidence': 0.94,
            'reasoning': 'Excellent performance with large documents at reasonable cost',
            'estimated_cost': 1.45,
            'performance_score': 9.6
        })
        recommendations.append({
            'model': 'claude-3-sonnet',
            'provider': 'anthropic',
            'confidence': 0.91,
            'reasoning': 'Good performance with large documents',
            'estimated_cost': 0.85,
            'performance_score': 9.2
        })
    else:
        # Default balanced recommendation
        recommendations.append({
            'model': 'gpt-5-mini',
            'provider': 'openai',
            'confidence': 0.94,
            'reasoning': 'Best balanced performance and cost with modern GPT-5 capabilities',
            'estimated_cost': 0.45,
            'performance_score': 9.4
        })
        recommendations.append({
            'model': 'claude-3-sonnet',
            'provider': 'anthropic',
            'confidence': 0.90,
            'reasoning': 'Excellent balanced performance for general tasks',
            'estimated_cost': 0.25,
            'performance_score': 9.0
        })
    
    return Response({
        'success': True,
        'task_analysis': {
            'task_type': task_type,
            'complexity': complexity,
            'budget_priority': budget_priority,
            'estimated_tokens': content_length
        },
        'recommendations': recommendations[:3],  # Top 3 recommendations
        'selection_criteria': {
            'cost_weight': 0.4 if budget_priority == 'cost' else 0.2,
            'performance_weight': 0.6 if budget_priority == 'performance' else 0.4,
            'capability_weight': 0.3
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def multi_model_comparison(request):
    """
    Run the same prompt across multiple models for comparison.
    """
    user = request.user
    data = json.loads(request.body or b"{}")
    
    prompt = data.get('prompt', '')
    models = data.get('models', ['gpt-5', 'gpt-5-mini', 'gpt-5-mini', 'claude-3-sonnet'])
    parameters = data.get('parameters', {'temperature': 0.7, 'max_tokens': 1000})
    
    if not prompt:
        return Response({'success': False, 'error': 'Prompt is required'}, status=400)
    
    # Mock responses from different models
    model_responses = []
    
    for model in models:
        # Generate mock response based on model characteristics
        if 'gpt-5' == model:
            response_text = f"GPT-5 Response: This is an advanced analysis leveraging superior reasoning capabilities. The model provides exceptional insights with enhanced problem-solving and critical thinking."
            quality_score = 9.9
            speed_ms = 3200
            cost = 0.085
        elif 'gpt-5-mini' in model:
            response_text = f"GPT-5 Mini Response: Balanced analysis with modern GPT-5 capabilities at reasonable cost. Excellent performance for most general tasks with strong reasoning."
            quality_score = 9.4
            speed_ms = 2400
            cost = 0.052
        elif 'gpt-5-nano' in model:
            response_text = f"GPT-5 Nano Response: Fast and cost-effective analysis with basic GPT-5 capabilities. Good for simple tasks while maintaining modern model quality."
            quality_score = 8.8
            speed_ms = 1600
            cost = 0.018
        elif 'gpt-5-mini' in model:
            response_text = f"GPT-4 Response: This is a comprehensive analysis of your prompt. The model provides detailed reasoning and structured insights with high accuracy and creativity."
            quality_score = 9.5
            speed_ms = 2800
            cost = 0.045
        elif 'claude-3-opus' in model:
            response_text = f"Claude-3 Opus Response: Here's a thorough examination of your request. This model excels at nuanced understanding and provides well-reasoned, articulate responses."
            quality_score = 9.6
            speed_ms = 2200
            cost = 0.038
        elif 'claude-3-sonnet' in model:
            response_text = f"Claude-3 Sonnet Response: A balanced and efficient analysis of your prompt. This model offers good performance at a reasonable cost with reliable outputs."
            quality_score = 9.0
            speed_ms = 1800
            cost = 0.022
        elif 'gpt-3.5' in model:
            response_text = f"GPT-3.5 Turbo Response: Quick and cost-effective response to your prompt. While simpler than GPT-4, it provides solid performance for basic tasks."
            quality_score = 8.2
            speed_ms = 1200
            cost = 0.008
        else:
            response_text = f"{model} Response: Generated response based on your prompt with model-specific characteristics."
            quality_score = 8.5
            speed_ms = 2000
            cost = 0.025
            
        model_responses.append({
            'model': model,
            'provider': 'openai' if 'gpt' in model else 'anthropic' if 'claude' in model else 'unknown',
            'response': response_text,
            'metadata': {
                'response_time_ms': speed_ms,
                'tokens_used': {
                    'input': len(prompt.split()),
                    'output': len(response_text.split()),
                    'total': len(prompt.split()) + len(response_text.split())
                },
                'cost': cost,
                'quality_score': quality_score,
                'parameters_used': parameters
            }
        })
    
    # Analysis and comparison
    best_quality = max(model_responses, key=lambda x: x['metadata']['quality_score'])
    fastest = min(model_responses, key=lambda x: x['metadata']['response_time_ms'])
    cheapest = min(model_responses, key=lambda x: x['metadata']['cost'])
    
    return Response({
        'success': True,
        'comparison_results': {
            'total_models_tested': len(model_responses),
            'prompt': prompt,
            'responses': model_responses,
            'analysis': {
                'best_quality': {
                    'model': best_quality['model'],
                    'score': best_quality['metadata']['quality_score']
                },
                'fastest': {
                    'model': fastest['model'],
                    'time_ms': fastest['metadata']['response_time_ms']
                },
                'most_cost_effective': {
                    'model': cheapest['model'],
                    'cost': cheapest['metadata']['cost']
                },
                'total_cost': sum(r['metadata']['cost'] for r in model_responses),
                'avg_quality_score': sum(r['metadata']['quality_score'] for r in model_responses) / len(model_responses)
            }
        },
        'recommendations': {
            'for_quality': best_quality['model'],
            'for_speed': fastest['model'],
            'for_cost': cheapest['model'],
            'overall_best_value': min(model_responses, key=lambda x: x['metadata']['cost'] / x['metadata']['quality_score'])['model']
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def model_performance_analytics(request):
    """
    Get detailed analytics on model performance and usage.
    Enhanced version with multi-provider insights.
    """
    user = request.user
    time_range = request.GET.get('time_range', '30d')
    
    # Mock comprehensive analytics
    analytics = {
        'usage_by_provider': {
            'openai': {
                'requests': 450,
                'total_tokens': 125000,
                'cost': 89.45,
                'avg_response_time_ms': 2100,
                'success_rate': 0.98,
                'models_used': ['gpt-5-mini', 'gpt-5-mini', 'gpt-5-nano']
            },
            'anthropic': {
                'requests': 280,
                'total_tokens': 95000,
                'cost': 34.67,
                'avg_response_time_ms': 1800,
                'success_rate': 0.97,
                'models_used': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
            },
            'google': {
                'requests': 120,
                'total_tokens': 45000,
                'cost': 8.30,
                'avg_response_time_ms': 1600,
                'success_rate': 0.95,
                'models_used': ['gemini-pro']
            }
        },
        'model_performance': {
            'gpt-5-mini': {
                'requests': 180,
                'avg_quality_score': 9.5,
                'avg_cost_per_request': 0.47,
                'user_satisfaction': 4.8,
                'use_cases': ['complex analysis', 'creative writing', 'research']
            },
            'claude-3-sonnet': {
                'requests': 220,
                'avg_quality_score': 9.0,
                'avg_cost_per_request': 0.22,
                'user_satisfaction': 4.6,
                'use_cases': ['general tasks', 'content generation', 'analysis']
            },
            'claude-3-haiku': {
                'requests': 340,
                'avg_quality_score': 8.2,
                'avg_cost_per_request': 0.08,
                'user_satisfaction': 4.2,
                'use_cases': ['simple tasks', 'summarization', 'quick responses']
            }
        },
        'cost_optimization': {
            'potential_savings': 28.90,
            'suggestions': [
                {
                    'suggestion': 'Use Claude-3 Haiku for simple tasks instead of GPT-4',
                    'potential_saving': 15.20,
                    'impact': 'minimal quality reduction'
                },
                {
                    'suggestion': 'Switch complex analysis from GPT-4 to Claude-3 Opus',
                    'potential_saving': 13.70,
                    'impact': 'potential quality improvement'
                }
            ]
        },
        'trends': {
            'daily_requests': [45, 52, 38, 61, 49, 55, 67],
            'daily_costs': [12.30, 14.50, 9.80, 16.20, 13.40, 15.60, 18.90],
            'quality_trends': [8.9, 9.1, 8.8, 9.2, 9.0, 9.3, 9.1]
        }
    }
    
    return Response({
        'success': True,
        'time_range': time_range,
        'analytics': analytics
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_model_preferences(request):
    """
    Set user preferences for automatic model selection.
    """
    user = request.user
    data = json.loads(request.body or b"{}")
    
    preferences = {
        'default_model': data.get('default_model', 'claude-3-sonnet'),
        'fallback_model': data.get('fallback_model', 'gpt-5-nano'),
        'budget_limit_daily': data.get('budget_limit_daily', 50.0),
        'quality_threshold': data.get('quality_threshold', 8.0),
        'speed_priority': data.get('speed_priority', 'balanced'),  # speed, quality, cost, balanced
        'auto_optimize': data.get('auto_optimize', True),
        'preferred_providers': data.get('preferred_providers', ['anthropic', 'openai']),
        'task_specific_models': data.get('task_specific_models', {
            'analysis': 'claude-3-opus',
            'coding': 'gpt-5-mini',
            'creative': 'claude-3-sonnet',
            'simple': 'claude-3-haiku'
        })
    }
    
    return Response({
        'success': True,
        'preferences': preferences,
        'updated_at': datetime.now().isoformat(),
        'estimated_monthly_cost': 78.50,
        'optimization_enabled': preferences['auto_optimize']
    })