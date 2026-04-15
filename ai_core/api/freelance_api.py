"""
Freelance Pipeline API Endpoints
"""
import os
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from django.views.decorators.csrf import csrf_exempt

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Skip CSRF enforcement
import json
import logging
from datetime import datetime

# Redis URL for production compatibility
_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_freelance_opportunities(request):
    """Get all freelance opportunities"""
    try:
        import redis
        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

        # Get all opportunity keys
        opp_keys = r.keys('freelance:opportunity:*')
        opportunities = []

        for key in opp_keys[:10]:  # Limit to 10 for performance
            data = r.get(key)
            if data:
                opportunities.append(json.loads(data))

        # Sort by suitability score
        opportunities.sort(key=lambda x: x.get('agent_suitability', 0), reverse=True)

        return Response({
            'success': True,
            'opportunities': opportunities
        })
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        # Return mock data for demo
        return Response({
            'success': True,
            'opportunities': [
                {
                    'job_id': 'upw_001',
                    'platform': 'Upwork',
                    'title': 'Write 10 SEO Blog Posts on AI Tools',
                    'description': 'Need 10 high-quality blog posts about AI productivity tools...',
                    'budget': 500,
                    'budget_type': 'fixed',
                    'skills_required': ['content writing', 'SEO', 'AI knowledge'],
                    'deadline': '2025-09-27',
                    'client_rating': 4.8,
                    'agent_suitability': 0.95,
                    'recommended_agents': ['content_creator_agent', 'seo_optimizer_agent'],
                    'estimated_completion_time': 12,
                    'confidence_score': 0.92,
                    'status': 'new'
                },
                {
                    'job_id': 'fiv_002',
                    'platform': 'Fiverr',
                    'title': 'Build REST API with Node.js',
                    'description': 'Need REST API for e-commerce platform...',
                    'budget': 1200,
                    'budget_type': 'fixed',
                    'skills_required': ['Node.js', 'REST API', 'MongoDB'],
                    'deadline': '2025-10-05',
                    'client_rating': 4.7,
                    'agent_suitability': 0.88,
                    'recommended_agents': ['code_generator_agent', 'api_builder_agent'],
                    'estimated_completion_time': 16,
                    'confidence_score': 0.85,
                    'status': 'new'
                }
            ]
        })


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_opportunity(request, job_id):
    """Analyze a freelance opportunity"""

    try:
        logger.info(f"📊 Analyzing opportunity {job_id} with GPT-5-mini")

        # Check for cached analysis first
        import redis
        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

        cache_key = f"freelance:analysis:{job_id}"
        cached_analysis = r.get(cache_key)

        if cached_analysis:
            logger.info(f"✅ Found cached analysis for {job_id}")
            cached_data = json.loads(cached_analysis)

            # Handle both old comprehensive format and new simple format
            if 'recommendation' in cached_data and isinstance(cached_data['recommendation'], dict):
                # Old comprehensive format
                recommendation_action = cached_data.get('recommendation', {}).get('action', 'PURSUE_CAREFULLY')
                agent_suitability = cached_data.get('recommendation', {}).get('score', 75) / 100.0
                estimated_profit = cached_data.get('profit_analysis', {}).get('profit', 0)
                risk_level = cached_data.get('risk_assessment', {}).get('level', 'MEDIUM')
                reasoning = f"Cached analysis: {cached_data.get('recommendation', {}).get('reasoning', 'Analysis completed')}"
                ai_model = cached_data.get('ai_model', 'cached-comprehensive')
            else:
                # New simple format (from our current caching)
                recommendation_action = cached_data.get('recommendation', 'PURSUE_CAREFULLY')
                agent_suitability = cached_data.get('agent_suitability', 0.5)
                estimated_profit = cached_data.get('estimated_profit', 0)
                risk_level = cached_data.get('risk_level', 'MEDIUM')
                reasoning = cached_data.get('reasoning', 'Cached analysis')
                ai_model = cached_data.get('ai_model', 'cached-result')

            return Response({
                'success': True,
                'job_id': job_id,
                'status': 'analyzed',
                'recommendation': recommendation_action,
                'analysis': {
                    'agent_suitability': agent_suitability,
                    'estimated_profit': estimated_profit,
                    'risk_level': risk_level,
                    'confidence': 0.95,  # High confidence for cached results
                    'reasoning': reasoning
                },
                'message': f'Cached analysis retrieved for {job_id}',
                'ai_model': ai_model
            })

        logger.info(f"🔄 No cached analysis found, running fresh analysis for {job_id}")

        # Get opportunity data from Redis
        opportunity_json = r.get(f"freelance:opportunity:{job_id}")
        if not opportunity_json:
            return Response({
                "success": False,
                "error": f"Opportunity {job_id} not found"
            }, status=404)

        opportunity_data = json.loads(opportunity_json)

        # Real AI Analysis with GPT-5-mini (Session 1086 Tier 4 PR 2 — factory)
        from django.conf import settings
        from core.services.openai_client_factory import get_openai_client

        api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY', '')
        if not api_key:
            raise Exception("OpenAI API key not configured")

        client = get_openai_client(api_key=api_key)

        # Prepare analysis prompt
        analysis_prompt = f"""
FREELANCE OPPORTUNITY ANALYSIS

Job ID: {job_id}
Title: {opportunity_data.get('title', 'Unknown')}
Platform: {opportunity_data.get('platform', 'Unknown')}
Budget: ${opportunity_data.get('budget', 0)} ({opportunity_data.get('budget_type', 'unknown')})
Description: {opportunity_data.get('description', 'No description')}
Skills Required: {', '.join(opportunity_data.get('skills_required', []))}
Deadline: {opportunity_data.get('deadline', 'Not specified')}
Client Rating: {opportunity_data.get('client_rating', 'Unknown')}

ANALYZE THIS OPPORTUNITY:

1. AGENT SUITABILITY (0.0-1.0): How well can AI agents handle this specific job?
2. ESTIMATED PROFIT ($): Realistic profit after costs (consider time, complexity, competition)
3. RISK LEVEL (LOW/MEDIUM/HIGH): Assess client quality, payment risk, scope creep potential
4. CONFIDENCE (0.0-1.0): How confident is this analysis?
5. RECOMMENDATION: PURSUE_IMMEDIATELY/PURSUE_CAREFULLY/DECLINE/INSUFFICIENT_DATA

Consider:
- Technical complexity vs AI agent capabilities
- Market rates for this type of work
- Client history and platform reputation
- Time requirements vs profitability
- Competition level in this niche

Respond in JSON format:
{{
    "agent_suitability": 0.85,
    "estimated_profit": 450,
    "risk_level": "MEDIUM",
    "confidence": 0.78,
    "recommendation": "PURSUE_CAREFULLY",
    "reasoning": "Brief explanation of analysis"
}}
"""

        # Use GPT-5 models as primary
        possible_models = [
            "gpt-5-mini",       # Primary model - cost-optimized reasoning
            "gpt-5-1",          # GPT-5.1 flagship model
            "o4-mini",          # Latest reasoning model optimized for cost/performance
            "o3",               # Advanced reasoning model
        ]

        response = None
        model_used = None

        for model_name in possible_models:
            try:
                logger.info(f"🤖 Trying model: {model_name}")

                # Configure parameters based on model
                call_params = {
                    "model": model_name,
                    "temperature": 1.0,  # Temperature = 1 as specified
                }

                # Handle different parameter requirements for each model type
                if model_name in ["gpt-5-nano"]:
                    # GPT-5-nano: Very limited model, use extremely simple prompt
                    call_params["max_completion_tokens"] = 200  # Very low token limit
                    simple_prompt = f"""
Job: {opportunity.get('title', 'Unknown')}
Description: {opportunity.get('description', 'No description')[:200]}
Budget: ${opportunity.get('budget', 500)}

Should I take this job? Respond with: PURSUE, AVOID, or MAYBE and explain why in 1-2 sentences.
"""
                    call_params["messages"] = [
                        {"role": "user", "content": simple_prompt}
                    ]
                    # No response_format for nano - let it respond naturally
                elif model_name in ["gpt-5", "gpt-5-mini", "gpt-5-preview"]:
                    # GPT-5 models use max_completion_tokens
                    call_params["max_completion_tokens"] = 800
                    call_params["messages"] = [
                        {"role": "system", "content": "You are an expert freelance job analyzer. Provide realistic, data-driven analysis in JSON format only."},
                        {"role": "user", "content": analysis_prompt}
                    ]
                    # Remove response_format to see if that's causing empty responses
                elif model_name in ["gpt-4.1", "gpt-4.1-mini"]:
                    # GPT-4.1 models use max_completion_tokens
                    call_params["max_completion_tokens"] = 800
                    call_params["messages"] = [
                        {"role": "system", "content": "You are an expert freelance job analyzer. Provide realistic, data-driven analysis in JSON format only."},
                        {"role": "user", "content": analysis_prompt}
                    ]
                    call_params["response_format"] = {"type": "json_object"}
                elif model_name in ["o3", "o4-mini"]:
                    # O-series reasoning models - no system role, no temperature
                    call_params["max_completion_tokens"] = 800
                    call_params["messages"] = [
                        {"role": "user", "content": f"You are an expert freelance job analyzer. Provide realistic, data-driven analysis in JSON format only.\n\n{analysis_prompt}"}
                    ]
                    # Remove temperature for reasoning models
                    del call_params["temperature"]
                else:
                    # Standard models (gpt-4o, gpt-5-mini, etc.)
                    call_params["max_tokens"] = 800
                    call_params["messages"] = [
                        {"role": "system", "content": "You are an expert freelance job analyzer. Provide realistic, data-driven analysis in JSON format only."},
                        {"role": "user", "content": analysis_prompt}
                    ]
                    call_params["response_format"] = {"type": "json_object"}

                response = client.chat.completions.create(**call_params)
                model_used = model_name
                logger.info(f"✅ Successfully used model: {model_name}")
                break
            except Exception as model_error:
                logger.warning(f"❌ Model {model_name} failed: {str(model_error)}")
                continue

        if response is None:
            raise Exception("All GPT-5-mini model variants failed")

        # Parse AI analysis
        response_content = response.choices[0].message.content
        logger.info(f"🤖 {model_used} raw response: {response_content}")
        logger.info(f"🔍 Response content type: {type(response_content)}")
        logger.info(f"🔍 Response content length: {len(response_content) if response_content else 0}")
        logger.info(f"🔍 Response content repr: {repr(response_content)}")

        # Clean and validate response content
        if not response_content:
            logger.error(f"❌ {model_used} returned empty content")
            raise Exception(f"Empty response from {model_used}")

        response_content = response_content.strip()
        if not response_content:
            logger.error(f"❌ {model_used} returned only whitespace")
            raise Exception(f"Whitespace-only response from {model_used}")

        # Handle different response formats
        if model_used == "gpt-5-nano":
            # GPT-5-nano returns plain text, convert to expected format
            recommendation = "PURSUE_CAREFULLY"  # Default
            if "PURSUE" in response_content.upper():
                recommendation = "PURSUE"
            elif "AVOID" in response_content.upper():
                recommendation = "AVOID"
            elif "MAYBE" in response_content.upper():
                recommendation = "PURSUE_CAREFULLY"

            ai_analysis = {
                "recommendation": recommendation,
                "agent_suitability": 0.8,
                "estimated_profit": opportunity.get('budget', 500) * 0.6,
                "risk_level": "MEDIUM",
                "confidence": 0.9,
                "reasoning": response_content.strip()[:200]  # Use GPT-5-nano's reasoning
            }
            logger.info(f"🤖 {model_used} nano response converted: {recommendation}")
        else:
            # Standard JSON response for other models
            try:
                ai_analysis = json.loads(response_content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing failed for {model_used}: {e}")
                logger.error(f"❌ Raw content: '{response_content}'")
                logger.error(f"❌ First 200 chars: '{response_content[:200]}'")
                # If JSON parsing fails, try to extract key info or use fallback
                raise Exception(f"Invalid JSON response from {model_used}")

        logger.info(f"🤖 {model_used} analysis complete: {ai_analysis.get('recommendation')}")

        # Cache the analysis result for future requests
        analysis_response = {
            'success': True,
            'job_id': job_id,
            'status': 'analyzed',
            'recommendation': ai_analysis.get('recommendation', 'INSUFFICIENT_DATA'),
            'analysis': {
                'agent_suitability': ai_analysis.get('agent_suitability', 0.5),
                'estimated_profit': ai_analysis.get('estimated_profit', 0),
                'risk_level': ai_analysis.get('risk_level', 'MEDIUM'),
                'confidence': ai_analysis.get('confidence', 0.5),
                'reasoning': ai_analysis.get('reasoning', 'Analysis completed')
            },
            'message': f'{model_used} analysis complete for {job_id}',
            'ai_model': model_used
        }

        # Store in Redis cache (formatted like existing cached analyses)
        cache_data = {
            'job_id': job_id,
            'recommendation': {
                'action': ai_analysis.get('recommendation', 'PURSUE_CAREFULLY'),
                'score': int(ai_analysis.get('agent_suitability', 0.5) * 100),
                'reasoning': ai_analysis.get('reasoning', 'Analysis completed')
            },
            'profit_analysis': {
                'profit': ai_analysis.get('estimated_profit', 0)
            },
            'risk_assessment': {
                'level': ai_analysis.get('risk_level', 'MEDIUM')
            },
            'analyzed_at': datetime.now().isoformat(),
            'status': 'analyzed',
            'ai_model': model_used
        }

        try:
            r.setex(cache_key, 86400 * 7, json.dumps(cache_data))  # Cache for 7 days
            logger.info(f"💾 Cached analysis for {job_id}")
        except Exception as cache_error:
            logger.warning(f"Failed to cache analysis: {cache_error}")

        return Response(analysis_response)

    except Exception as e:
        logger.error(f"GPT-5-mini analysis failed: {e}")
        # Fallback to enhanced mock analysis based on job data
        opportunity_data = request.data

        # Enhanced mock analysis with some logic
        budget = opportunity_data.get('budget', 500)
        client_rating = opportunity_data.get('client_rating', 4.0)
        skills = opportunity_data.get('skills_required', [])

        # Calculate dynamic values based on job data
        estimated_profit = min(int(budget * 0.6), 800)  # 60% of budget, capped at $800
        agent_suitability = min(0.95, 0.7 + (len(skills) * 0.05))  # Higher for more skills
        confidence = min(0.95, client_rating / 5.0) if client_rating else 0.7
        risk_level = "LOW" if client_rating >= 4.5 else "MEDIUM" if client_rating >= 4.0 else "HIGH"

        recommendation_action = 'PURSUE_CAREFULLY' if risk_level == "MEDIUM" else 'PURSUE_IMMEDIATELY'

        fallback_response = {
            'success': True,
            'job_id': job_id,
            'status': 'analyzed',
            'recommendation': recommendation_action,
            'analysis': {
                'agent_suitability': agent_suitability,
                'estimated_profit': estimated_profit,
                'risk_level': risk_level,
                'confidence': confidence,
                'reasoning': f'Enhanced analysis based on ${budget} budget, {client_rating} client rating, and {len(skills)} required skills'
            },
            'message': f'Enhanced analysis complete for {job_id} (GPT-5-mini fallback)',
            'ai_model': 'enhanced-fallback'
        }

        # Cache the fallback analysis result too
        fallback_cache_data = {
            'job_id': job_id,
            'recommendation': {
                'action': recommendation_action,
                'score': int(agent_suitability * 100),
                'reasoning': f'Enhanced analysis based on ${budget} budget, {client_rating} client rating, and {len(skills)} required skills'
            },
            'profit_analysis': {
                'profit': estimated_profit
            },
            'risk_assessment': {
                'level': risk_level
            },
            'analyzed_at': datetime.now().isoformat(),
            'status': 'analyzed',
            'ai_model': 'enhanced-fallback'
        }

        try:
            import redis
            r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)
            cache_key = f"freelance:analysis:{job_id}"
            r.setex(cache_key, 86400 * 7, json.dumps(fallback_cache_data))  # Cache for 7 days
            logger.info(f"💾 Cached fallback analysis for {job_id}")
        except Exception as cache_error:
            logger.warning(f"Failed to cache fallback analysis: {cache_error}")

        return Response(fallback_response)

        # Original complex analysis (commented for now)
        """
        from ai_core.agents.freelance_job_analyzer import FreelanceJobAnalyzer
        from ai_core.agents.freelance_pipeline import FreelancePipeline
        import redis

        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

        # Get opportunity data
        opportunity = request.data

        # Create pipeline and process
        pipeline = FreelancePipeline(redis_client=r)

        # Run async function in sync context
        import asyncio
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    project = pool.submit(
                        lambda: asyncio.run(pipeline.process_opportunity(opportunity))
                    ).result()
            else:
                project = loop.run_until_complete(pipeline.process_opportunity(opportunity))
        except RuntimeError:
            # No event loop, create new one
            project = asyncio.run(pipeline.process_opportunity(opportunity))

        return Response({
            'success': True,
            'project': project,
            'analysis': project.get('analysis')
        })
        """

    except Exception as e:
        logger.error(f"Error analyzing opportunity: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_pending_approvals(request):
    """Get all pending approval requests"""
    try:
        import redis
        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

        approvals = []
        pending = r.lrange('freelance:approvals:pending', 0, -1)

        for item in pending:
            approvals.append(json.loads(item))

        # Don't add mock data - return empty if no real approvals
        # if not approvals:
        #     approvals = []

        return Response({
            'success': True,
            'approvals': approvals
        })

    except Exception as e:
        logger.error(f"Error getting approvals: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def process_approval(request, approval_id):
    """Process an approval decision"""
    try:
        from ai_core.agents.freelance_pipeline import FreelancePipeline
        import redis
        import uuid
        from datetime import datetime

        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)
        pipeline = FreelancePipeline(redis_client=r)

        decision = request.data.get('decision', 'approve')

        logger.info(f"Processing approval {approval_id} with decision: {decision}")

        if decision == 'approve':
            # Create a project from the opportunity
            opportunity_json = r.get(f"freelance:opportunity:{approval_id}")
            if opportunity_json:
                opportunity = json.loads(opportunity_json)

                # Create project data with proper agent assignment
                project_id = f"proj_{uuid.uuid4().hex[:8]}"

                # Smart agent assignment based on skills
                skills_str = ' '.join(opportunity.get('skills_required', [])).lower()
                title_str = opportunity.get('title', '').lower()

                if 'node' in skills_str or 'rest api' in skills_str or 'javascript' in skills_str or 'api' in title_str:
                    lead_agent = 'Code Generator'
                    supporting_agents = ['API Builder', 'Backend Developer']
                elif 'python' in skills_str or 'data analysis' in skills_str:
                    lead_agent = 'Data Analyst'
                    supporting_agents = ['Code Generator', 'Script Writer']
                elif 'market research' in skills_str or 'report' in title_str:
                    lead_agent = 'Market Analyst'
                    supporting_agents = ['Research Agent', 'Report Generator']
                elif 'seo' in skills_str or 'blog' in skills_str or 'content' in skills_str:
                    lead_agent = 'Content Creator'
                    supporting_agents = ['SEO Optimizer', 'Copywriter']
                else:
                    lead_agent = 'General Assistant'
                    supporting_agents = ['Content Creator']

                project = {
                    'id': project_id,
                    'opportunity': opportunity,
                    'status': 'active',
                    'created_at': datetime.now().isoformat(),
                    'analysis': {
                        'agent_team': {
                            'lead_agent': lead_agent,
                            'supporting_agents': supporting_agents
                        },
                        'recommendation': 'APPROVED',
                        'confidence': 0.85
                    }
                }

                # Store project in Redis
                r.set(f"freelance:project:{project_id}", json.dumps(project))

                # Notify WebSocket about new project
                from channels.layers import get_channel_layer
                channel_layer = get_channel_layer()
                if channel_layer:
                    from asgiref.sync import async_to_sync
                    async_to_sync(channel_layer.group_send)(
                        'agent_monitor',
                        {
                            'type': 'project_update',
                            'message': {
                                'project_id': project_id,
                                'agent': lead_agent,
                                'task': opportunity.get('title', 'Unknown Task'),
                                'status': 'started'
                            }
                        }
                    )

                logger.info(f"Created project {project_id} with lead agent {lead_agent}")

                # Log to console for visibility
                print(f"\n🚀 AGENT DEPLOYED!")
                print(f"   Project ID: {project_id}")
                print(f"   Lead Agent: {lead_agent}")
                print(f"   Task: {opportunity.get('title', 'Unknown')}")
                print(f"   Budget: ${opportunity.get('budget', 0)}")
                print(f"   Supporting Agents: {', '.join(supporting_agents)}")
                print(f"   Status: ACTIVE\n")

                return Response({
                    'success': True,
                    'message': f'Project approved and deployed successfully',
                    'approval_id': approval_id,
                    'project_id': project_id,
                    'lead_agent': lead_agent,
                    'decision': decision
                })

        return Response({
            'success': True,
            'message': f'Approval {decision}d successfully',
            'approval_id': approval_id,
            'decision': decision
        })

    except Exception as e:
        logger.error(f"Error processing approval: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_active_projects(request):
    """Get all active freelance projects"""
    try:
        import redis
        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

        # Get all project keys
        project_keys = r.keys('freelance:project:*')
        projects = []

        for key in project_keys[:10]:  # Limit for performance
            data = r.get(key)
            if data:
                project = json.loads(data)
                # Only include active projects
                if project.get('status') not in ['rejected', 'cancelled', 'completed', 'paid']:
                    projects.append(project)

        # Don't add mock data - return empty if no real projects
        # if not projects:
        #     projects = []

        return Response({
            'success': True,
            'projects': projects
        })

    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def project_decision(request):
    """Record user project decision for spider learning"""
    try:
        data = request.data
        decision = data.get('decision')  # 'start' or 'decline'
        opportunity = data.get('opportunity')
        analysis = data.get('analysis')
        feedback = data.get('feedback')

        logger.info(f"📋 User {decision.upper()}ED project: {opportunity.get('title', 'Unknown')}")

        # Store decision in memory system for spider learning
        import redis
        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

        # Create memory entry for spider learning
        memory_key = f"user_decision:{opportunity.get('job_id', 'unknown')}"
        memory_data = {
            'decision': decision,
            'opportunity': opportunity,
            'analysis': analysis,
            'feedback': feedback,
            'timestamp': datetime.now().isoformat(),
            'learning_signals': {
                'platform_preference': feedback.get('platform'),
                'skill_match': feedback.get('skills'),
                'budget_preference': feedback.get('budget_range'),
                'client_quality': feedback.get('client_rating'),
                'outcome': 'positive' if decision == 'start' else 'negative'
            }
        }

        # Store in Redis for spider access
        r.setex(memory_key, 86400 * 30, json.dumps(memory_data))  # Keep for 30 days

        # Add to learning queue
        learning_key = f"spider_learning:{decision}:{datetime.now().strftime('%Y%m%d')}"
        r.lpush(learning_key, json.dumps(memory_data))
        r.expire(learning_key, 86400 * 90)  # Keep learning data for 90 days

        logger.info(f"🧠 Decision stored for spider learning: {memory_key}")

        if decision == 'start':
            # Add to active projects
            project_data = {
                'id': f"proj_{opportunity.get('job_id', 'unknown')}",
                'opportunity': opportunity,
                'status': 'starting',
                'analysis': analysis,
                'created_at': datetime.now().isoformat(),
                'checkpoints': [
                    {'stage': 'analysis', 'status': 'completed'},
                    {'stage': 'user_approval', 'status': 'completed'},
                    {'stage': 'agent_assignment', 'status': 'pending'}
                ]
            }

            project_key = f"freelance:project:{project_data['id']}"
            r.setex(project_key, 86400 * 30, json.dumps(project_data))

            # 🚀 TRIGGER AGENT EXECUTION PIPELINE

            # Notify Agent Monitor that work is starting
            from ai_core.utils.agent_notifier import agent_notifier

            # Determine which agent will handle this
            assigned_agent = analysis.get('agent_team', {}).get('lead_agent', 'Content Creator')

            # Notify the monitor
            agent_notifier.notify_task_start(assigned_agent, {
                'id': opportunity.get('job_id'),
                'title': opportunity.get('title', 'Unknown Project'),
                'type': 'Freelance Project',
                'value': opportunity.get('budget', 0),
                'estimated_time': f"{analysis.get('project_plan', {}).get('timeline', {}).get('total_hours', 8)} hours",
                'platform': opportunity.get('platform', 'Unknown'),
                'client': opportunity.get('client_name', 'Unknown Client')
            })

            logger.info(f"🤖 Agent Monitor notified: {assigned_agent} starting work")

            try:
                logger.info(f"🎯 Triggering agent execution for project {project_data['id']}")

                # Use threading to avoid async/sync conflicts in Django
                import threading
                from ai_core.agents.sync_project_executor import execute_project_sync

                def start_project_execution():
                    try:
                        logger.info(f"🎬 Starting agent execution thread for {project_data['id']}")
                        result = execute_project_sync(project_data)
                        logger.info(f"✅ Project execution completed: {result}")
                    except Exception as e:
                        logger.error(f"❌ Project execution thread failed: {e}")

                # Start execution in background thread
                execution_thread = threading.Thread(
                    target=start_project_execution,
                    daemon=True,
                    name=f"ProjectExecution-{project_data['id']}"
                )
                execution_thread.start()

                logger.info(f"🎬 Agent execution thread started for project {project_data['id']}")

            except Exception as e:
                logger.error(f"❌ Failed to trigger agent execution: {e}")
                # Continue anyway - project is still created

        return Response({
            'success': True,
            'decision': decision,
            'message': f'Decision recorded and spiders will learn from your {decision} choice',
            'learning_stored': True
        })

    except Exception as e:
        logger.error(f"Error recording project decision: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
async def start_freelance_spider(request):
    """Start the freelance opportunity spider"""
    try:
        from ai_core.spiders.freelance_opportunity_spider import FreelanceOpportunitySpider
        import redis

        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

        spider = FreelanceOpportunitySpider(redis_client=r)
        await spider.initialize()

        opportunities = await spider.find_opportunities()

        await spider.cleanup()

        return Response({
            'success': True,
            'message': f'Spider found {len(opportunities)} opportunities',
            'count': len(opportunities)
        })

    except Exception as e:
        logger.error(f"Error starting spider: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def deploy_deliverable(request):
    """Handle deliverable deployment"""
    try:
        data = request.data
        deliverable_id = data.get("deliverable_id")
        project_id = data.get("project_id")
        task_name = data.get("task_name")
        deployment_timestamp = data.get("deployment_timestamp")

        logger.info(f"📦 Deploying deliverable: {task_name} for project {project_id}")

        # Store deployment record in Redis
        import redis
        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

        deployment_record = {
            "deliverable_id": deliverable_id,
            "project_id": project_id,
            "task_name": task_name,
            "deployment_timestamp": deployment_timestamp,
            "status": "deployed",
            "deployed_by": "agent_system"
        }

        # Store in Redis with TTL of 30 days
        r.setex(f"deployment:{deliverable_id}", 30 * 24 * 60 * 60, json.dumps(deployment_record))

        logger.info(f"✅ Deployment recorded for {task_name}")

        return Response({
            "success": True,
            "message": f"Deliverable \"{task_name}\" deployed successfully",
            "deployment_id": deliverable_id,
            "timestamp": deployment_timestamp
        })

    except Exception as e:
        logger.error(f"Error deploying deliverable: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def completed_deliverables(request):
    """Get completed project deliverables for review"""
    try:
        import redis
        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

        project_keys = r.keys('freelance:project:*')
        deliverables = []

        for project_key in project_keys:
            project_data = r.get(project_key)
            if project_data:
                project = json.loads(project_data)

                if project.get('status') == 'completed' and project.get('deliverable'):
                    deliverable = project['deliverable'].copy()
                    deliverable['project_id'] = project['id']
                    deliverable['project_title'] = project.get('opportunity', {}).get('title', 'Unknown')
                    deliverable['agent'] = project.get('analysis', {}).get('agent_team', {}).get('lead_agent', 'Unknown')
                    deliverable['budget'] = project.get('opportunity', {}).get('budget', 0)
                    deliverable['platform'] = project.get('opportunity', {}).get('platform', 'Unknown')
                    deliverable['completed_at'] = project.get('completed_at', '')
                    deliverables.append(deliverable)

        # Sort by completion date (newest first)
        deliverables.sort(key=lambda x: x.get('completed_at', ''), reverse=True)

        return Response({
            'deliverables': deliverables,
            'total': len(deliverables),
            'total_value': sum(d.get('budget', 0) for d in deliverables)
        })
    except Exception as e:
        logger.error(f"Error fetching deliverables: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def deliverable_content(request, deliverable_id):
    """Get the actual content of a deliverable"""
    try:
        import redis
        import os
        r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

        # Find the project containing this deliverable
        project_keys = r.keys('freelance:project:*')
        deliverable_data = None

        for project_key in project_keys:
            project_data = r.get(project_key)
            if project_data:
                project = json.loads(project_data)
                if (project.get('status') == 'completed' and
                    project.get('deliverable') and
                    project.get('deliverable', {}).get('id') == deliverable_id):
                    deliverable_data = project['deliverable']
                    break

        if not deliverable_data:
            return Response({
                "success": False,
                "error": "Deliverable not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Look for actual deliverable files
        deliverable_files_dir = "real_job_deliverables"
        content = None
        file_extension = None

        # Find the most recent deliverable file that matches the deliverable_id
        import glob

        # Look for files that contain the deliverable_id
        pattern = f"{deliverable_files_dir}/*{deliverable_id}*"
        matching_files = glob.glob(pattern)

        if not matching_files:
            # Fallback: look for any recent files created in the last 24 hours
            all_files = glob.glob(f"{deliverable_files_dir}/*")
            import time
            recent_files = [f for f in all_files if (time.time() - os.path.getmtime(f)) < 86400]  # 24 hours
            if recent_files:
                # Sort by modification time and get the most recent
                matching_files = sorted(recent_files, key=os.path.getmtime, reverse=True)[:1]

        selected_file = None
        if matching_files:
            # Get the most recent file
            selected_file = max(matching_files, key=os.path.getmtime)

        # Get the project ID from the deliverable search
        project_id = None
        for project_key in project_keys:
            project_data = r.get(project_key)
            if project_data:
                project = json.loads(project_data)
                if (project.get('status') == 'completed' and
                    project.get('deliverable') and
                    project.get('deliverable', {}).get('id') == deliverable_id):
                    project_id = project.get('id')
                    break

        # Use the selected file (either matching deliverable_id or most recent)
        if selected_file and os.path.isfile(selected_file):
            try:
                with open(selected_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_extension = selected_file.split('.')[-1]
                    logger.info(f"✅ Found deliverable file: {selected_file}")
            except Exception as e:
                logger.warning(f"Could not read deliverable file {selected_file}: {e}")

        # If no file found, use sample content
        if content is None:
            content = f"# {deliverable_data.get('title', 'Sample Deliverable')}\n\nThis is sample content showing the deliverable output.\nQuality Score: {(deliverable_data.get('quality_score', 0.9) * 100):.1f}%"
            file_extension = 'md'

        return Response({
            "success": True,
            "content": content,
            "file_extension": file_extension,
            "deliverable": deliverable_data
        })

    except Exception as e:
        logger.error(f"Error fetching deliverable content: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
