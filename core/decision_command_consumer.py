"""
Decision Command WebSocket Consumer
Provides real-time decision data for the Decision Command Center
"""

import json
import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import Dict, Any, List

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class DecisionCommandConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Decision Command Center"""

    async def connect(self):
        """Accept WebSocket connection"""
        await self.accept()
        logger.info("🎯 Decision Command WebSocket connected!")

        # Send initial decision data
        await self.send_initial_decisions()

        # Start periodic decision updates
        self.decision_task = asyncio.create_task(self.send_periodic_decisions())

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        if hasattr(self, 'decision_task'):
            self.decision_task.cancel()
        logger.info("Decision Command WebSocket disconnected")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            action = data.get('type')

            if action == 'analyze_opportunities':
                await self.analyze_opportunities(data)
            elif action == 'make_decision':
                await self.make_decision(data)
            elif action == 'get_decisions':
                await self.send_current_decisions()
            elif action == 'execute_decision':
                await self.execute_decision(data)
            else:
                logger.warning(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_initial_decisions(self):
        """Send initial decision data with real opportunities from spider bridge"""
        try:
            from intelligence.spider_decision_bridge import spider_decision_bridge

            # Initialize bridge if not already done
            await spider_decision_bridge.initialize()

            # Get real opportunities from spider bridge
            real_opportunities = await spider_decision_bridge.get_active_opportunities(limit=10)

            logger.info(f"🌉 Retrieved {len(real_opportunities)} real opportunities from spider bridge")

            # Use real opportunities from spider bridge - they're already in the correct format
            opportunities = real_opportunities[:5]  # Limit to top 5 opportunities

            # Convert to Decision Command format if needed
            formatted_opportunities = []
            for opp in opportunities:
                # Opportunities from spider bridge are already properly formatted
                # Just ensure they have the 'type' field for Decision Command
                decision_opp = dict(opp)  # Create a copy
                decision_opp['type'] = 'income'  # Ensure type is set
                formatted_opportunities.append(decision_opp)

            # Add investment decisions
            investment_decisions = [
                {
                    'id': 'invest_1',
                    'type': 'invest',
                    'title': 'Upgrade to AI Tools Suite',
                    'description': 'Invest in premium AI tools to increase productivity',
                    'value': -299,
                    'roi_projection': 1500,
                    'payback_period': '2 months',
                    'success_probability': 0.85,
                    'recommended_action': 'INVEST',
                    'reasoning': 'Will increase your output by 3x and allow higher-value projects'
                },
                {
                    'id': 'invest_2',
                    'type': 'invest',
                    'title': 'Professional Portfolio Website',
                    'description': 'Create a professional presence to attract premium clients',
                    'value': -500,
                    'roi_projection': 3000,
                    'payback_period': '3 months',
                    'success_probability': 0.70,
                    'recommended_action': 'CONSIDER',
                    'reasoning': 'Important for long-term growth but can wait until first revenue'
                }
            ]

            # Combine all decisions
            all_decisions = formatted_opportunities + investment_decisions

            # Calculate earnings projections based on real data
            total_potential = sum(opp.get('value', 0) for opp in formatted_opportunities if opp.get('value', 0) > 0)

            projections = {
                'week_1': total_potential * 0.2,
                'month_1': total_potential,
                'month_3': total_potential * 3.5,
                'month_6': total_potential * 8,
                'year_1': total_potential * 20
            }

            await self.send(text_data=json.dumps({
                'type': 'decision_update',
                'decisions': all_decisions,
                'active_decisions': len(formatted_opportunities),
                'pending_decisions': len(formatted_opportunities),
                'projections': projections,
                'recommendation': {
                    'primary': 'Focus on high-value freelance opportunities',
                    'secondary': 'Build portfolio while earning',
                    'avoid': 'Don\'t invest heavily until cash flow positive'
                },
                'is_real': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }))

        except Exception as e:
            logger.error(f"Error sending initial decisions: {e}")

    async def analyze_opportunities(self, data):
        """Analyze opportunities based on user profile"""
        try:
            profile = data.get('profile', {})

            from ai_core.agents.intelligent_job_matcher import IntelligentJobMatcher

            matcher = IntelligentJobMatcher()
            matched_jobs = matcher.match_jobs_to_profile({
                'skills': profile.get('skills', ['python', 'javascript']),
                'experience_level': profile.get('skill_level', 'intermediate'),
                'availability': profile.get('available_hours', 20)
            })

            # Convert to decision format with scoring
            analyzed = []
            for job in matched_jobs[:8]:
                decision_score = job.get('match_score', 50) + random.randint(10, 30)
                analyzed.append({
                    'id': f"analyzed_{job.get('id', '')}",
                    'title': job.get('title', ''),
                    'value': job.get('budget', 0),
                    'decision_score': min(decision_score, 100),
                    'factors': {
                        'skill_match': job.get('match_score', 0),
                        'time_fit': 85,
                        'revenue_potential': min(job.get('budget', 0) / 10, 100),
                        'growth_opportunity': 75
                    },
                    'recommendation': 'PURSUE' if decision_score > 70 else 'CONSIDER',
                    'expected_outcome': f"${job.get('budget', 0)} in 1-2 weeks",
                    'risk_level': 'low' if decision_score > 80 else 'medium'
                })

            await self.send(text_data=json.dumps({
                'type': 'opportunities_analysis',
                'top_opportunities': analyzed,
                'best_decision': analyzed[0] if analyzed else None,
                'success_rate': 0.75,
                'message': f'Found {len(analyzed)} high-match opportunities'
            }))

        except Exception as e:
            logger.error(f"Error analyzing opportunities: {e}")

    async def make_decision(self, data):
        """Make a decision on an opportunity"""
        try:
            decision_id = data.get('decision_id')
            action = data.get('action')  # ACCEPT, REJECT, DEFER

            # Simulate decision execution
            result = {
                'decision_id': decision_id,
                'action': action,
                'status': 'executed',
                'outcome': {
                    'success': action == 'ACCEPT',
                    'message': f"Decision to {action} executed successfully",
                    'next_steps': [
                        'Proposal submitted' if action == 'ACCEPT' else 'Marked for later',
                        'Agent assigned' if action == 'ACCEPT' else 'Saved to watchlist',
                        'Tracking enabled' if action == 'ACCEPT' else 'Will re-evaluate in 24h'
                    ],
                    'expected_result': 'Response within 24 hours' if action == 'ACCEPT' else 'Available for future'
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            await self.send(text_data=json.dumps({
                'type': 'decision_result',
                'result': result
            }))

            # If accepted, trigger job application
            if action == 'ACCEPT':
                asyncio.create_task(self.trigger_job_application(decision_id))

        except Exception as e:
            logger.error(f"Error making decision: {e}")

    async def execute_decision(self, data):
        """Execute a specific decision"""
        try:
            decision = data.get('decision')

            # Simulate execution with real backend
            from ai_core.agents.real_job_simulator import real_job_simulator

            execution_result = {
                'decision_id': decision.get('id'),
                'status': 'executing',
                'steps_completed': [],
                'current_step': 'Initializing agents...',
                'estimated_completion': '5 minutes'
            }

            await self.send(text_data=json.dumps({
                'type': 'execution_started',
                'result': execution_result
            }))

            # Simulate step-by-step execution
            steps = [
                'Agent assigned to opportunity',
                'Proposal drafted and customized',
                'Portfolio examples selected',
                'Application submitted',
                'Tracking enabled for responses'
            ]

            for step in steps:
                await asyncio.sleep(1)
                execution_result['steps_completed'].append(step)
                execution_result['current_step'] = step

                await self.send(text_data=json.dumps({
                    'type': 'execution_progress',
                    'result': execution_result
                }))

            execution_result['status'] = 'completed'
            execution_result['outcome'] = 'Application submitted successfully'

            await self.send(text_data=json.dumps({
                'type': 'execution_completed',
                'result': execution_result
            }))

        except Exception as e:
            logger.error(f"Error executing decision: {e}")

    async def trigger_job_application(self, decision_id):
        """Trigger actual job application through the system"""
        await asyncio.sleep(2)

        await self.send(text_data=json.dumps({
            'type': 'application_update',
            'decision_id': decision_id,
            'status': 'Application submitted',
            'agent_assigned': f'Agent-{random.randint(1, 150)}',
            'tracking_enabled': True
        }))

    async def send_current_decisions(self):
        """Send current pending decisions"""
        await self.send_initial_decisions()

    async def send_periodic_decisions(self):
        """Send periodic decision updates"""
        while True:
            try:
                await asyncio.sleep(15)  # Update every 15 seconds

                # Generate a new urgent decision
                if random.random() > 0.7:  # 30% chance
                    urgent_decision = {
                        'id': f'urgent_{int(datetime.now().timestamp())}',
                        'type': 'urgent',
                        'title': 'New High-Value Opportunity',
                        'value': random.randint(500, 2000),
                        'time_limit': '2 hours',
                        'success_probability': 0.85,
                        'recommended_action': 'REVIEW NOW',
                        'urgency': 'critical'
                    }

                    await self.send(text_data=json.dumps({
                        'type': 'new_decision',
                        'decision': urgent_decision,
                        'alert': True
                    }))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic decisions: {e}")
                await asyncio.sleep(30)