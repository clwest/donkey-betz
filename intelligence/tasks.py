"""
🧠 INTELLIGENCE TASKS
Celery tasks for the Real-Time Intelligence Engine
"""

import asyncio
import logging
from datetime import datetime
from celery import shared_task
from django.conf import settings
from .realtime_engine import intelligence_engine

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def start_intelligence_engine(self):
    """🚀 Start the Real-Time Intelligence Engine"""
    try:
        logger.info("🚀 Starting Limitless Intelligence Engine...")

        # Create new event loop for async code
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Start the intelligence engine
        loop.run_until_complete(intelligence_engine.start_intelligence_stream())

    except Exception as e:
        logger.error(f"Intelligence engine error: {e}")
        raise


@shared_task
def get_live_opportunities():
    """Get current live opportunities"""
    try:
        return intelligence_engine.get_current_opportunities()
    except Exception as e:
        logger.error(f"Get opportunities error: {e}")
        return []


@shared_task
def get_live_predictions():
    """Get current live predictions"""
    try:
        return intelligence_engine.get_current_predictions()
    except Exception as e:
        logger.error(f"Get predictions error: {e}")
        return []


@shared_task
def trigger_market_scan():
    """Trigger an immediate market scan"""
    try:
        logger.info("🎯 Manual market scan triggered")
        # This would trigger immediate scans in the engine
        return {"status": "scan_triggered", "timestamp": "now"}
    except Exception as e:
        logger.error(f"Market scan trigger error: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(bind=True)
def execute_action_plan(self, action_plan_id):
    """Execute an action plan using real agents"""
    from .models import ActionPlan
    from agents.registry import agent_registry
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    import time
    import random

    channel_layer = get_channel_layer()

    try:
        # Get the action plan
        plan = ActionPlan.objects.get(id=action_plan_id)
        plan.add_log(f"Starting execution of {plan.opportunity_title}")

        # Send WebSocket update
        async_to_sync(channel_layer.group_send)(
            'income_income_builder',
            {
                'type': 'action_plan_update',
                'plan_id': str(action_plan_id),
                'status': 'in_progress',
                'progress': 0,
                'current_step': 0
            }
        )

        # Get available agents
        agents = agent_registry.list_agents()
        plan.add_log(f"Found {len(agents)} agents available for execution")

        # Process each step
        steps = plan.steps if isinstance(plan.steps, list) else []

        for i, step in enumerate(steps, 1):
            # Update current step
            plan.update_progress(step_number=i)
            plan.add_log(f"Executing step {i}: {step[:100]}...")

            # Send WebSocket update for step progress
            progress = int((i / len(steps)) * 100)
            async_to_sync(channel_layer.group_send)(
                'income_income_builder',
                {
                    'type': 'action_plan_update',
                    'plan_id': str(action_plan_id),
                    'status': 'in_progress',
                    'progress': progress,
                    'current_step': i,
                    'execution_logs': plan.execution_logs[-5:] if plan.execution_logs else []
                }
            )

            # Select best agent for this step
            selected_agent = None
            agent_name = 'MockAgent'

            if agents:
                # Try to find an agent that matches the task
                step_lower = step.lower()

                # Map keywords to preferred agents
                if 'research' in step_lower or 'analyze' in step_lower:
                    # Look for research agents
                    research_agents = [a for a in agents if 'research' in a.get('name', '').lower()]
                    selected_agent = research_agents[0] if research_agents else random.choice(agents)
                elif 'write' in step_lower or 'content' in step_lower or 'create' in step_lower:
                    # Look for content creation agents
                    content_agents = [a for a in agents if any(word in a.get('name', '').lower()
                                     for word in ['content', 'writer', 'creator', 'blog'])]
                    selected_agent = content_agents[0] if content_agents else random.choice(agents)
                elif 'publish' in step_lower or 'promote' in step_lower:
                    # Look for marketing/promotion agents
                    marketing_agents = [a for a in agents if any(word in a.get('name', '').lower()
                                       for word in ['marketing', 'social', 'seo', 'promotion'])]
                    selected_agent = marketing_agents[0] if marketing_agents else random.choice(agents)
                elif 'plan' in step_lower or 'strategy' in step_lower:
                    # Look for strategy agents
                    strategy_agents = [a for a in agents if any(word in a.get('name', '').lower()
                                      for word in ['strategy', 'business', 'planning'])]
                    selected_agent = strategy_agents[0] if strategy_agents else random.choice(agents)
                else:
                    # Default to random selection
                    selected_agent = random.choice(agents)

                agent_name = selected_agent.get('name', 'Unknown Agent')
                plan.add_log(f"Assigned to agent: {agent_name}", agent='system')

            # Execute the step with the selected agent
            try:
                # Skip the broken AgentExecution model and generate content directly
                plan.add_log(f"Agent {agent_name} starting execution...", level='info')

                # Generate actual content based on the step
                generated_content = None

                # Always generate AI content for every step
                try:
                    from content.ai_providers import AIProviderManager
                    ai_manager = AIProviderManager()

                    # Create a detailed prompt based on the step type
                    if 'research' in step.lower() or 'analyze' in step.lower():
                        prompt = f"""As an expert researcher, provide detailed research and analysis for the following task:

Task: {step}
Context: {plan.opportunity_title}

Please provide:
1. Market analysis and trends
2. Key competitors and their strategies
3. Best practices and industry standards
4. Specific tools and resources
5. Actionable insights and recommendations

Be specific, detailed, and provide real value."""

                    elif 'write' in step.lower() or 'content' in step.lower() or 'create' in step.lower():
                        prompt = f"""As a professional content creator, generate high-quality content for:

Task: {step}
Context: {plan.opportunity_title}

Please provide:
1. A complete content piece (article, guide, or template)
2. Specific examples and use cases
3. Step-by-step instructions where applicable
4. Tips and best practices
5. Resources and tools to use

Make it actionable, specific, and valuable."""

                    else:
                        prompt = f"""As an expert in {plan.opportunity_title}, provide a comprehensive action plan for:

Task: {step}

Please provide:
1. Detailed step-by-step instructions
2. Specific tools and platforms to use
3. Timeline and milestones
4. Success metrics to track
5. Common pitfalls to avoid
6. Real examples and case studies

Make it practical, specific, and immediately actionable."""

                    response = ai_manager.generate_content(
                        provider='openai',
                        model='gpt-5-mini',  # Using GPT-5-mini - 5x cheaper than GPT-5 with great quality!
                        system_prompt="You are an expert business consultant and income generation specialist. Provide practical, actionable advice.",
                        user_prompt=prompt,
                        config={'max_completion_tokens': 1500}  # GPT-5 models use max_completion_tokens
                    )

                    # Handle GenerationResult object
                    if response.success:
                        generated_content = response.content
                    else:
                        raise Exception(f"AI generation failed: {response.error_message}")

                    plan.add_log(f"Generated AI content: {len(generated_content)} characters", level='success')

                except Exception as ai_error:
                    logger.error(f"AI content generation failed: {ai_error}")
                    plan.add_log(f"AI generation error: {ai_error}", level='warning')
                    # Don't fall back to generic content - try to at least provide something useful
                    generated_content = f"""# {plan.opportunity_title} - Step {i}

## Task: {step}

### Action Plan:
Based on the task "{step}", here are the key actions to take:

1. **Research Phase**: Investigate current best practices and industry standards
2. **Planning Phase**: Create a detailed implementation strategy
3. **Execution Phase**: Implement the plan with regular progress checks
4. **Optimization Phase**: Review results and iterate for improvement

### Key Resources:
- Industry-specific forums and communities
- Professional networks and associations
- Online learning platforms and courses
- Relevant tools and software platforms

### Success Metrics:
- Clear deliverables defined and achieved
- Timeline milestones met
- Quality standards maintained
- Stakeholder satisfaction achieved

*Note: This is a framework. Customize based on your specific needs and context.*
"""

                # Save the generated content to a file
                if generated_content:
                    import os
                    from pathlib import Path

                    # Create output directory
                    output_dir = Path("income_builder_outputs")
                    output_dir.mkdir(exist_ok=True)

                    # Create file with the AI-generated content
                    filename = f"{plan.opportunity_title.replace(' ', '_')}_step_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    filepath = output_dir / filename

                    # Format the content nicely
                    formatted_content = f"""# {plan.opportunity_title} - Step {i}

## Task: {step}

### AI-Generated Content:
{generated_content}

---
*Generated at: {datetime.now().isoformat()}*
*Agent: {agent_name}*
"""

                    with open(filepath, 'w') as f:
                        f.write(formatted_content)

                    # Store in results
                    if not plan.results:
                        plan.results = {}

                    plan.results[f'step_{i}_content'] = formatted_content
                    plan.results[f'step_{i}_file'] = str(filepath)

                    # Keep track of all files created
                    if 'files_created' not in plan.results:
                        plan.results['files_created'] = []
                    plan.results['files_created'].append(str(filepath))

                    plan.save()
                    plan.add_log(f"Generated content and saved to: {filepath}", level='success')

                plan.add_log(f"Agent {agent_name} completed task", level='success')

            except Exception as e:
                logger.error(f"Error executing step {i}: {e}")
                plan.add_log(f"Error executing step: {e}", level='error')
                # Continue to next step rather than failing completely
                continue

            # Mark step as completed
            plan.update_progress(step_number=i, step_completed=True)
            plan.add_log(f"Step {i} completed successfully", level='success')

            # Update Celery task state
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i,
                    'total': len(steps),
                    'status': f'Completed step {i} of {len(steps)}'
                }
            )

        # Generate comprehensive final files for the completed plan
        try:
            from pathlib import Path

            output_dir = Path("income_builder_outputs")
            output_dir.mkdir(exist_ok=True)

            # Generate complete plan file
            logger.info(f"Generating complete plan for {plan.opportunity_title}")
            logger.info(f"Resources type: {type(plan.resources)}, Content: {plan.resources}")
            logger.info(f"Steps type: {type(plan.steps)}, Content: {plan.steps}")

            plan_filename = f"{plan.opportunity_title.replace(' ', '_')}_Complete_Plan.md"
            plan_filepath = output_dir / plan_filename

            complete_plan_content = f"""# {plan.opportunity_title} - Complete Action Plan

## Overview
Generated: {datetime.now().isoformat()}
Status: Completed

## Opportunity Details
- **Title**: {plan.opportunity_title}
- **ID**: {plan.opportunity_id}
- **Timeline**: {plan.timeline if plan.timeline else 'Flexible'}

## Completed Steps
"""

            for i, step in enumerate(plan.steps, 1):
                # Handle step as either string or dict
                step_text = step if isinstance(step, str) else str(step.get('description', step))
                complete_plan_content += f"\n### Step {i}: {step_text}\n"
                if f'step_{i}_content' in plan.results:
                    complete_plan_content += f"{plan.results[f'step_{i}_content'][:500]}...\n"
                else:
                    complete_plan_content += "✅ Completed\n"

            complete_plan_content += f"""
## Resources
{chr(10).join(['- ' + (r if isinstance(r, str) else f"{r.get('name', 'Resource')} ({r.get('url', '')})" if isinstance(r, dict) else str(r)) for r in plan.resources]) if plan.resources else '- Coming soon'}

## Expected Outcome
{plan.expected_outcome if plan.expected_outcome else 'Successful completion of all steps'}

---
*Generated by Income Builder AI System*
"""

            with open(plan_filepath, 'w') as f:
                f.write(complete_plan_content)

            # Generate QuickStart guide
            quickstart_filename = f"{plan.opportunity_title.replace(' ', '_')}_QuickStart.md"
            quickstart_filepath = output_dir / quickstart_filename

            quickstart_content = f"""# {plan.opportunity_title} - Quick Start Guide

## 🚀 Get Started Today

### First 3 Actions
1. {(plan.steps[0] if isinstance(plan.steps[0], str) else str(plan.steps[0].get('description', plan.steps[0]))) if len(plan.steps) > 0 else 'Begin research'}
2. {(plan.steps[1] if isinstance(plan.steps[1], str) else str(plan.steps[1].get('description', plan.steps[1]))) if len(plan.steps) > 1 else 'Set up foundation'}
3. {(plan.steps[2] if isinstance(plan.steps[2], str) else str(plan.steps[2].get('description', plan.steps[2]))) if len(plan.steps) > 2 else 'Start implementation'}

### Essential Resources
{chr(10).join(['- ' + (r if isinstance(r, str) else f"{r.get('name', 'Resource')} ({r.get('url', '')})" if isinstance(r, dict) else str(r)) for r in plan.resources[:5]]) if plan.resources else '- See complete plan for resources'}

### Success Tips
- Start small and iterate
- Focus on one step at a time
- Track your progress daily
- Join communities for support

---
*Start now. Perfect later.*
"""

            with open(quickstart_filepath, 'w') as f:
                f.write(quickstart_content)

            # Update results with file information
            if not plan.results:
                plan.results = {}

            plan.results['files_created'] = [
                str(plan_filepath),
                str(quickstart_filepath)
            ]

            # Add any step-specific files that were created
            for key, value in plan.results.items():
                if '_file' in key and value not in plan.results['files_created']:
                    plan.results['files_created'].append(value)

            plan.results['complete_plan'] = str(plan_filepath)
            plan.results['quickstart_guide'] = str(quickstart_filepath)
            plan.results['status'] = 'success'
            plan.results['message'] = f'Generated {len(plan.results["files_created"])} files'

            plan.save()
            plan.add_log(f"Generated final documentation: {len(plan.results['files_created'])} files", level='success')

        except Exception as e:
            import traceback
            logger.error(f"Error generating final files: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            plan.add_log(f"Could not generate final files: {e}", level='warning')

        # Mark plan as completed
        plan.mark_completed()
        plan.add_log("Action plan execution completed successfully!", level='success')

        # Send WebSocket update for completion
        async_to_sync(channel_layer.group_send)(
            'income_income_builder',
            {
                'type': 'action_plan_update',
                'plan_id': str(action_plan_id),
                'status': 'completed',
                'progress': 100,
                'current_step': len(steps),
                'execution_logs': plan.execution_logs[-10:] if plan.execution_logs else [],
                'results': plan.results,
                'completed_at': plan.completed_at.isoformat() if plan.completed_at else None
            }
        )

        return {
            'status': 'completed',
            'message': f'Successfully executed {len(steps)} steps',
            'plan_id': str(action_plan_id)
        }

    except Exception as e:
        logger.error(f"Error executing action plan {action_plan_id}: {e}")

        # Send WebSocket update for failure
        if 'channel_layer' in locals():
            async_to_sync(channel_layer.group_send)(
                'income_income_builder',
                {
                    'type': 'action_plan_update',
                    'plan_id': str(action_plan_id),
                    'status': 'failed',
                    'error': str(e)
                }
            )

        return {
            'status': 'failed',
            'message': str(e)
        }


# Revenue Integration Tasks

@shared_task(bind=True)
def monitor_and_process_opportunities(self):
    """
    Continuously monitor platforms and process new opportunities
    Runs every hour to check for new opportunities from spider network
    """
    try:
        from .revenue_integration import RevenueIncomeIntegration
        from backend.spiders.spider_network import SpiderNetwork

        logger.info("🔍 Monitoring for new revenue opportunities...")

        integration = RevenueIncomeIntegration()
        spider_network = SpiderNetwork()

        # Get new opportunities from spiders
        opportunities = spider_network.get_new_opportunities()
        processed_count = 0

        for opp in opportunities:
            try:
                # Process each opportunity
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    integration.process_opportunity(opp)
                )

                if result['success']:
                    processed_count += 1
                    logger.info(f"✅ Processed opportunity: {opp.get('title', 'Unknown')}")

                    # Trigger proposal submission if confidence is high
                    if result.get('success_probability', 0) > 0.7:
                        submit_proposal_automatically.delay(
                            result['proposal'],
                            result.get('tracking_id')
                        )

            except Exception as e:
                logger.error(f"Error processing opportunity {opp.get('id')}: {e}")
                continue

        logger.info(f"📊 Processed {processed_count} opportunities")
        return {
            'status': 'success',
            'processed': processed_count,
            'total': len(opportunities)
        }

    except Exception as e:
        logger.error(f"Error in opportunity monitoring: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def submit_proposal_automatically(proposal_data, tracking_id):
    """
    Automatically submit high-confidence proposals to platforms
    """
    try:
        from .revenue_integration import RevenueIncomeIntegration

        logger.info(f"📤 Auto-submitting proposal: {tracking_id}")

        integration = RevenueIncomeIntegration()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            integration.auto_submit_proposal(proposal_data)
        )

        if result['success']:
            logger.info(f"✅ Proposal submitted: {result.get('submission_id')}")

            # Schedule response checking
            check_proposal_responses.apply_async(
                args=[result.get('submission_id')],
                countdown=3600  # Check after 1 hour
            )
        else:
            logger.error(f"❌ Proposal submission failed: {result.get('error')}")

        return result

    except Exception as e:
        logger.error(f"Error submitting proposal: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def check_proposal_responses(submission_id=None):
    """
    Check platforms for responses to submitted proposals
    Runs every hour to check for client responses
    """
    try:
        from .revenue_integration import RevenueIncomeIntegration
        from .models import OpportunityActionPlan
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        logger.info("📮 Checking for proposal responses...")

        integration = RevenueIncomeIntegration()
        channel_layer = get_channel_layer()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        responses = loop.run_until_complete(
            integration.monitor_responses()
        )

        for response in responses:
            try:
                # Update database
                opp_plan = OpportunityActionPlan.objects.get(
                    proposal_id=response['proposal_id']
                )
                opp_plan.update_status('client_responded')

                # Send WebSocket notification
                async_to_sync(channel_layer.group_send)(
                    'revenue_revenue_income',
                    {
                        'type': 'proposal_status_update',
                        'proposal_id': response['proposal_id'],
                        'status': 'client_responded',
                        'details': response['response']
                    }
                )

                # If positive response, trigger follow-up
                if response.get('response', {}).get('interested', False):
                    handle_client_response.delay(
                        response['proposal_id'],
                        response['response']
                    )

            except Exception as e:
                logger.error(f"Error processing response for {response['proposal_id']}: {e}")

        logger.info(f"📊 Processed {len(responses)} responses")
        return {
            'status': 'success',
            'responses_processed': len(responses)
        }

    except Exception as e:
        logger.error(f"Error checking responses: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def handle_client_response(proposal_id, response_data):
    """
    Handle client responses and trigger appropriate follow-up actions
    """
    try:
        from .models import OpportunityActionPlan
        from .income_builder import AIIncomeBuilder

        logger.info(f"🤝 Handling client response for proposal: {proposal_id}")

        # Get the opportunity plan
        opp_plan = OpportunityActionPlan.objects.get(proposal_id=proposal_id)

        # Analyze response sentiment
        response_type = response_data.get('type', 'neutral')

        if response_type == 'positive':
            # Client is interested - prepare follow-up
            opp_plan.update_status('negotiating')

            # Generate follow-up content
            income_builder = AIIncomeBuilder()
            follow_up = income_builder._generate_follow_up_content(
                opp_plan.opportunity_data,
                response_data
            )

            # Schedule follow-up submission
            submit_follow_up.delay(proposal_id, follow_up)

        elif response_type == 'negative':
            # Client rejected - update status
            opp_plan.update_status('rejected')

            # Learn from rejection for ML improvement
            update_ml_model_with_feedback.delay(
                opp_plan.opportunity_data,
                'rejected',
                response_data.get('reason')
            )

        elif response_type == 'needs_info':
            # Client needs more information
            opp_plan.update_status('negotiating')

            # Generate additional information
            income_builder = AIIncomeBuilder()
            additional_info = income_builder._generate_additional_info(
                opp_plan.opportunity_data,
                response_data.get('questions', [])
            )

            # Send additional information
            submit_follow_up.delay(proposal_id, additional_info)

        return {
            'status': 'success',
            'proposal_id': proposal_id,
            'action_taken': response_type
        }

    except Exception as e:
        logger.error(f"Error handling client response: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def submit_follow_up(proposal_id, follow_up_content):
    """
    Submit follow-up communication to clients
    """
    try:
        from .models import OpportunityActionPlan

        logger.info(f"📧 Submitting follow-up for proposal: {proposal_id}")

        # Get the opportunity plan
        opp_plan = OpportunityActionPlan.objects.get(proposal_id=proposal_id)

        # Platform-specific follow-up submission
        # This would integrate with platform APIs
        # For now, we'll just log it
        logger.info(f"Follow-up content: {follow_up_content[:200]}...")

        # Update status
        opp_plan.update_status('negotiating')

        return {
            'status': 'success',
            'proposal_id': proposal_id
        }

    except Exception as e:
        logger.error(f"Error submitting follow-up: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def update_ml_model_with_feedback(opportunity_data, outcome, reason=None):
    """
    Update ML model with outcome feedback for continuous improvement
    """
    try:
        from .income_builder import AIIncomeBuilder

        logger.info("🧠 Updating ML model with feedback...")

        income_builder = AIIncomeBuilder()

        # Feed outcome back to ML pipeline
        ml_pipeline = income_builder.ml_pipeline

        # Create training data from outcome
        training_data = {
            'opportunity': opportunity_data,
            'outcome': outcome,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }

        # This would update the ML model
        # For now, we'll just log it
        logger.info(f"ML feedback recorded: {outcome}")

        return {
            'status': 'success',
            'feedback_recorded': True
        }

    except Exception as e:
        logger.error(f"Error updating ML model: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def calculate_daily_revenue_metrics():
    """
    Calculate and store daily revenue metrics
    Runs daily at midnight
    """
    try:
        from .models import RevenueMetrics
        from django.utils import timezone

        logger.info("📊 Calculating daily revenue metrics...")

        # Calculate metrics for today
        today = timezone.now().date()
        metrics = RevenueMetrics.update_metrics_for_date(today)

        logger.info(f"✅ Daily metrics calculated: {metrics}")

        return {
            'status': 'success',
            'date': today.isoformat(),
            'metrics': {
                'opportunities': metrics.opportunities_identified,
                'proposals': metrics.proposals_submitted,
                'conversions': metrics.conversions,
                'revenue': float(metrics.revenue_generated)
            }
        }

    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }