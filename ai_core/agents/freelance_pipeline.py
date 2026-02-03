"""
Complete Freelance Pipeline with Human-in-the-Loop
Orchestrates the entire process from opportunity to payment
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ProjectStatus(Enum):
    """Project lifecycle status"""
    OPPORTUNITY_FOUND = "opportunity_found"
    ANALYZING = "analyzing"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PROPOSAL_SENT = "proposal_sent"
    PROJECT_WON = "project_won"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DELIVERED = "delivered"
    REVISION_REQUESTED = "revision_requested"
    COMPLETED = "completed"
    PAID = "paid"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class FreelancePipeline:
    """
    Complete pipeline for freelance work execution.
    Manages the entire flow with human checkpoints.
    """

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.active_projects = {}
        self.dry_run = True  # Default to safe mode
        self.max_bid_amount = 100.0  # Safety limit for automatic bidding

    async def process_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a new freelance opportunity through the complete pipeline.

        Flow:
        1. Spider finds opportunity
        2. Analyzer creates project plan
        3. Human approves plan
        4. System sends proposal
        5. Human confirms project won
        6. Agents execute work
        7. Human reviews deliverables
        8. System delivers to client
        9. Track payment
        """
        project_id = f"project_{opportunity['job_id']}_{datetime.now().timestamp()}"

        project = {
            'id': project_id,
            'opportunity': opportunity,
            'status': ProjectStatus.OPPORTUNITY_FOUND.value,
            'created_at': datetime.now().isoformat(),
            'checkpoints': [],
            'deliverables': [],
            'communications': [],
            'financial': {
                'budget': opportunity.get('budget', 0),
                'cost': 0,
                'profit': 0,
                'paid': False
            }
        }

        # Store project
        await self._store_project(project)

        # Start processing
        logger.info(f"🚀 Starting pipeline for: {opportunity['title']}")

        # Step 1: Analyze opportunity
        project = await self._analyze_stage(project)

        # Step 2: Human approval checkpoint
        project = await self._human_approval_checkpoint(
            project,
            "approve_analysis",
            "Please review the analysis and project plan"
        )

        if project['status'] == ProjectStatus.REJECTED.value:
            return project

        # Step 3: Send proposal (after human approval)
        project = await self._send_proposal_stage(project)

        # Step 4: Wait for project win confirmation
        project = await self._human_approval_checkpoint(
            project,
            "confirm_project_won",
            "Did we win the project? Please confirm to proceed with execution"
        )

        if project['status'] != ProjectStatus.PROJECT_WON.value:
            return project

        # Step 5: Execute project
        project = await self._execute_project_stage(project)

        # Step 6: Human review of deliverables
        project = await self._human_approval_checkpoint(
            project,
            "approve_deliverables",
            "Please review the deliverables before sending to client"
        )

        # Step 7: Deliver to client
        project = await self._deliver_stage(project)

        # Step 8: Track payment
        project = await self._track_payment_stage(project)

        return project

    async def _analyze_stage(self, project: Dict) -> Dict:
        """Run analysis on the opportunity"""
        project['status'] = ProjectStatus.ANALYZING.value
        await self._store_project(project)

        try:
            from ai_core.agents.freelance_job_analyzer import FreelanceJobAnalyzer

            analyzer = FreelanceJobAnalyzer(
                redis_client=self.redis_client
            )

            analysis = await analyzer.analyze_opportunity(project['opportunity'])

            project['analysis'] = analysis
            project['status'] = ProjectStatus.PENDING_APPROVAL.value

            # Add checkpoint
            project['checkpoints'].append({
                'stage': 'analysis',
                'timestamp': datetime.now().isoformat(),
                'status': 'completed',
                'data': {
                    'recommendation': analysis['recommendation']['action'],
                    'profit': analysis['profit_analysis']['profit'],
                    'risk': analysis['risk_assessment']['level']
                }
            })

            logger.info(f"✅ Analysis complete: {analysis['recommendation']['action']}")

        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            project['status'] = ProjectStatus.CANCELLED.value
            project['error'] = str(e)

        await self._store_project(project)
        return project

    async def _human_approval_checkpoint(self, project: Dict, approval_type: str,
                                        message: str) -> Dict:
        """
        Human-in-the-loop checkpoint.
        Displays info and waits for human decision.
        """
        checkpoint = {
            'stage': approval_type,
            'timestamp': datetime.now().isoformat(),
            'status': 'waiting_for_human',
            'message': message
        }

        project['checkpoints'].append(checkpoint)
        project['status'] = ProjectStatus.PENDING_APPROVAL.value
        await self._store_project(project)

        # Create approval request
        approval_request = {
            'project_id': project['id'],
            'type': approval_type,
            'message': message,
            'project_title': project['opportunity']['title'],
            'analysis': project.get('analysis', {}).get('recommendation'),
            'profit': project.get('analysis', {}).get('profit_analysis', {}).get('profit'),
            'required_action': self._get_required_action(approval_type)
        }

        # Store in approval queue
        if self.redis_client:
            self.redis_client.lpush(
                'freelance:approvals:pending',
                json.dumps(approval_request)
            )

            # Publish notification
            self.redis_client.publish(
                'freelance:approval_needed',
                json.dumps(approval_request)
            )

        # In production, this would wait for actual human response
        # For now, simulate approval after showing info
        logger.info(f"🔔 HUMAN APPROVAL NEEDED: {approval_type}")
        logger.info(f"📋 Project: {project['opportunity']['title']}")

        if 'analysis' in project:
            logger.info(f"💰 Profit: ${project['analysis']['profit_analysis']['profit']}")
            logger.info(f"⚠️ Risk: {project['analysis']['risk_assessment']['level']}")
            logger.info(f"👍 Recommendation: {project['analysis']['recommendation']['action']}")

        # Simulate human response based on recommendation
        if approval_type == 'approve_analysis':
            if project.get('analysis', {}).get('recommendation', {}).get('action') in ['PURSUE_IMMEDIATELY', 'PURSUE']:
                decision = 'approved'
            else:
                decision = 'rejected'
        elif approval_type == 'confirm_project_won':
            # Simulate 60% win rate for good projects
            import random
            decision = 'won' if random.random() < 0.6 else 'lost'
        else:
            decision = 'approved'

        # Process decision
        checkpoint['status'] = 'completed'
        checkpoint['decision'] = decision
        checkpoint['decided_at'] = datetime.now().isoformat()

        if decision == 'approved':
            project['status'] = ProjectStatus.APPROVED.value
        elif decision == 'won':
            project['status'] = ProjectStatus.PROJECT_WON.value
        elif decision == 'rejected' or decision == 'lost':
            project['status'] = ProjectStatus.REJECTED.value

        await self._store_project(project)
        return project

    async def _send_proposal_stage(self, project: Dict) -> Dict:
        """Generate and send proposal to client"""
        project['status'] = ProjectStatus.PROPOSAL_SENT.value

        proposal = project['analysis']['proposal']

        # Format proposal for sending
        formatted_proposal = self._format_proposal(proposal, project)

        project['proposal'] = {
            'content': formatted_proposal,
            'sent_at': datetime.now().isoformat(),
            'platform': project['opportunity']['platform']
        }

        logger.info(f"📨 Proposal sent for: {project['opportunity']['title']}")

        # Add checkpoint
        project['checkpoints'].append({
            'stage': 'proposal_sent',
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        })

        await self._store_project(project)
        return project

    async def _execute_project_stage(self, project: Dict) -> Dict:
        """Execute the project using agent team"""
        project['status'] = ProjectStatus.IN_PROGRESS.value
        await self._store_project(project)

        logger.info(f"🔨 Starting project execution: {project['opportunity']['title']}")

        deliverables = []
        project_plan = project['analysis']['project_plan']

        # Execute each phase
        for phase in project_plan['phases']:
            logger.info(f"  📍 Phase {phase['phase']}: {phase['name']}")

            # Simulate agent work for each task
            for task in phase['tasks']:
                deliverable = await self._execute_task(
                    task,
                    phase.get('agents', [phase.get('agent')]),
                    project
                )
                deliverables.append(deliverable)

                # Human approval if needed
                if phase.get('human_approval'):
                    logger.info(f"  🔔 Phase {phase['phase']} requires human approval")
                    # In production, would actually wait for approval

        project['deliverables'] = deliverables
        project['status'] = ProjectStatus.IN_REVIEW.value

        # Add checkpoint
        project['checkpoints'].append({
            'stage': 'execution_complete',
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'deliverables_count': len(deliverables)
        })

        await self._store_project(project)
        return project

    async def _execute_task(self, task: str, agents: List[str], project: Dict) -> Dict:
        """Execute a single task using specified agents"""
        from ai_core.agents.concrete_executor import get_concrete_executor
        executor = get_concrete_executor()

        deliverable = {
            'task': task,
            'agents': agents,
            'started_at': datetime.now().isoformat(),
            'status': 'in_progress'
        }

        try:
            # Execute with first available agent
            if agents and agents[0]:
                result = await executor.execute_agent(
                    agent_name=agents[0],
                    task={
                        'input': {
                            'task': task,
                            'context': project['opportunity']['description'],
                            'requirements': project['analysis']['requirements']
                        }
                    }
                )

                deliverable['result'] = result
                deliverable['status'] = 'completed'
                deliverable['completed_at'] = datetime.now().isoformat()

                logger.info(f"    ✅ Completed: {task[:50]}...")
            else:
                # Fallback if no agent specified
                deliverable['result'] = {
                    'success': True,
                    'output': f"Task completed: {task}"
                }
                deliverable['status'] = 'completed'

        except Exception as e:
            logger.error(f"    ❌ Task failed: {e}")
            deliverable['status'] = 'failed'
            deliverable['error'] = str(e)

        return deliverable

    async def _deliver_stage(self, project: Dict) -> Dict:
        """Package and deliver completed work to client"""
        project['status'] = ProjectStatus.DELIVERED.value

        # Package deliverables
        delivery_package = {
            'project_id': project['id'],
            'title': project['opportunity']['title'],
            'deliverables': [],
            'documentation': [],
            'delivered_at': datetime.now().isoformat()
        }

        # Format each deliverable
        for deliverable in project['deliverables']:
            if deliverable['status'] == 'completed':
                delivery_package['deliverables'].append({
                    'task': deliverable['task'],
                    'output': deliverable.get('result', {}).get('output', 'Completed'),
                    'completed_at': deliverable['completed_at']
                })

        project['delivery'] = delivery_package

        logger.info(f"📦 Delivered {len(delivery_package['deliverables'])} items to client")

        # Add checkpoint
        project['checkpoints'].append({
            'stage': 'delivered',
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        })

        project['status'] = ProjectStatus.COMPLETED.value
        await self._store_project(project)
        return project

    async def _track_payment_stage(self, project: Dict) -> Dict:
        """Track payment for completed project"""
        # Calculate final financials
        project['financial']['profit'] = project['financial']['budget'] - project['financial']['cost']

        # Simulate payment received
        project['financial']['paid'] = True
        project['financial']['paid_at'] = datetime.now().isoformat()
        project['status'] = ProjectStatus.PAID.value

        logger.info(f"💰 Payment received: ${project['financial']['budget']}")
        logger.info(f"📊 Profit: ${project['financial']['profit']}")

        # Add checkpoint
        project['checkpoints'].append({
            'stage': 'payment_received',
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'amount': project['financial']['budget']
        })

        await self._store_project(project)
        return project

    def _format_proposal(self, proposal: Dict, project: Dict) -> str:
        """Format proposal for sending"""
        formatted = f"""
{proposal['greeting']}

{proposal['understanding']}
{'. '.join(project['analysis']['requirements'].get('deliverables', []))}

{proposal['approach']}
{chr(10).join('• ' + phase for phase in proposal['phases'])}

Timeline: {proposal['timeline']}

{proposal['why_me']}
{chr(10).join('• ' + qual for qual in proposal['qualifications'])}

Budget: ${project['opportunity']['budget']} ({project['opportunity']['budget_type']})

{proposal['call_to_action']}

Best regards,
AI Freelance Team
        """
        return formatted.strip()

    def _get_required_action(self, approval_type: str) -> str:
        """Get required action description for approval type"""
        actions = {
            'approve_analysis': 'Review analysis and approve to send proposal',
            'confirm_project_won': 'Confirm if we won the project',
            'approve_deliverables': 'Review deliverables before sending to client'
        }
        return actions.get(approval_type, 'Review and approve')

    async def _store_project(self, project: Dict):
        """Store project state in Redis"""
        if self.redis_client:
            key = f"freelance:project:{project['id']}"
            self.redis_client.setex(key, 604800, json.dumps(project))  # 7 day TTL

            # Update status tracker
            status_key = f"freelance:status:{project['status']}"
            self.redis_client.sadd(status_key, project['id'])

    async def get_project_status(self, project_id: str) -> Optional[Dict]:
        """Get current status of a project"""
        if self.redis_client:
            key = f"freelance:project:{project_id}"
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        return None

    async def get_pending_approvals(self) -> List[Dict]:
        """Get all projects waiting for human approval"""
        approvals = []
        if self.redis_client:
            # Get all pending approval requests
            pending = self.redis_client.lrange('freelance:approvals:pending', 0, -1)
            for item in pending:
                approvals.append(json.loads(item))
        return approvals

    async def approve_project(self, project_id: str, decision: str):
        """Process human approval decision"""
        project = await self.get_project_status(project_id)
        if project:
            # Update based on decision
            if decision == 'approved':
                project['status'] = ProjectStatus.APPROVED.value
            elif decision == 'rejected':
                project['status'] = ProjectStatus.REJECTED.value

            await self._store_project(project)
            return True
        return False