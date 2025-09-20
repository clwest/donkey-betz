"""
Freelance Job Analyzer Agent
Analyzes freelance opportunities and creates detailed project plans
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FreelanceJobAnalyzer:
    """
    Agent that analyzes freelance opportunities and creates actionable project plans.
    Works with human-in-the-loop for approval at key stages.
    """

    def __init__(self, llm_integration=None, redis_client=None):
        self.llm_integration = llm_integration
        self.redis_client = redis_client

    async def analyze_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deeply analyze a freelance opportunity to create a comprehensive project plan.

        Returns:
            - Detailed requirements breakdown
            - Agent team composition
            - Deliverables list
            - Timeline with milestones
            - Risk assessment
            - Profit calculation
        """
        logger.info(f"📊 Analyzing opportunity: {opportunity['title']}")

        # Step 1: Use LLM to understand requirements
        requirements = await self._extract_requirements(opportunity)

        # Step 2: Select optimal agent team
        agent_team = await self._select_agent_team(opportunity, requirements)

        # Step 3: Create project breakdown
        project_plan = await self._create_project_plan(opportunity, requirements, agent_team)

        # Step 4: Calculate profitability
        profit_analysis = self._calculate_profitability(opportunity, project_plan)

        # Step 5: Assess risks
        risk_assessment = await self._assess_risks(opportunity, project_plan)

        # Step 6: Generate proposal template
        proposal = await self._generate_proposal(opportunity, project_plan)

        analysis = {
            'job_id': opportunity['job_id'],
            'title': opportunity['title'],
            'platform': opportunity['platform'],
            'requirements': requirements,
            'agent_team': agent_team,
            'project_plan': project_plan,
            'profit_analysis': profit_analysis,
            'risk_assessment': risk_assessment,
            'proposal': proposal,
            'recommendation': self._make_recommendation(profit_analysis, risk_assessment),
            'analyzed_at': datetime.now().isoformat(),
            'status': 'analyzed',
            'human_approval_needed': True
        }

        # Store analysis
        if self.redis_client:
            await self._store_analysis(analysis)

        return analysis

    async def _extract_requirements(self, opportunity: Dict) -> Dict[str, Any]:
        """Use LLM to extract detailed requirements from job description"""
        if self.llm_integration:
            from backend.agents.agent_llm_integration import agent_llm_integration

            prompt = f"""
            Analyze this freelance job and extract detailed requirements:

            Title: {opportunity['title']}
            Description: {opportunity['description']}
            Skills Required: {', '.join(opportunity['skills_required'])}
            Budget: ${opportunity['budget']} ({opportunity['budget_type']})

            Extract:
            1. Core deliverables (be specific)
            2. Technical requirements
            3. Quality expectations
            4. Communication needs
            5. Hidden requirements (read between the lines)
            6. Success criteria

            Format as structured JSON.
            """

            result = await agent_llm_integration.generate_for_agent(
                'freelance_analyzer',
                prompt
            )

            if result['success']:
                try:
                    # Parse LLM response as JSON
                    requirements = json.loads(result['response'])
                except:
                    # Fallback to text parsing
                    requirements = {
                        'raw_analysis': result['response'],
                        'deliverables': self._extract_deliverables_from_text(result['response']),
                        'technical': opportunity['skills_required'],
                        'quality': 'High quality expected',
                        'success_criteria': 'Meet all requirements on time'
                    }
            else:
                requirements = self._fallback_requirements(opportunity)
        else:
            requirements = self._fallback_requirements(opportunity)

        return requirements

    def _fallback_requirements(self, opportunity: Dict) -> Dict:
        """Fallback requirements extraction without LLM"""
        return {
            'deliverables': self._extract_deliverables_from_text(opportunity['description']),
            'technical': opportunity['skills_required'],
            'quality': 'Professional quality',
            'communication': 'Regular updates',
            'hidden': [],
            'success_criteria': 'Complete all deliverables on time'
        }

    def _extract_deliverables_from_text(self, text: str) -> List[str]:
        """Extract deliverables from job description text"""
        deliverables = []

        # Look for common deliverable patterns
        if 'blog post' in text.lower():
            count = self._extract_number(text, 'post')
            deliverables.append(f"{count} blog posts")

        if 'api' in text.lower():
            deliverables.append("REST API implementation")

        if 'report' in text.lower():
            deliverables.append("Comprehensive report")

        if 'script' in text.lower():
            deliverables.append("Python/JavaScript script")

        if 'dashboard' in text.lower():
            deliverables.append("Interactive dashboard")

        return deliverables if deliverables else ["Complete project deliverables"]

    def _extract_number(self, text: str, keyword: str) -> int:
        """Extract number associated with keyword"""
        import re
        pattern = r'(\d+)\s*' + keyword
        match = re.search(pattern, text.lower())
        return int(match.group(1)) if match else 1

    async def _select_agent_team(self, opportunity: Dict, requirements: Dict) -> Dict[str, Any]:
        """Select the optimal team of agents for this job"""
        team = {
            'lead_agent': None,
            'support_agents': [],
            'specialist_agents': [],
            'review_agents': [],
            'capabilities': []
        }

        # Map skills to agents
        for agent in opportunity.get('recommended_agents', []):
            if 'content' in agent:
                if not team['lead_agent']:
                    team['lead_agent'] = agent
                else:
                    team['support_agents'].append(agent)
                team['capabilities'].append('Content Creation')

            elif 'data' in agent or 'analyst' in agent:
                team['specialist_agents'].append(agent)
                team['capabilities'].append('Data Analysis')

            elif 'code' in agent or 'api' in agent:
                team['specialist_agents'].append(agent)
                team['capabilities'].append('Code Generation')

            elif 'seo' in agent or 'optimizer' in agent:
                team['review_agents'].append(agent)
                team['capabilities'].append('Optimization')

        # Ensure we have a lead
        if not team['lead_agent'] and opportunity.get('recommended_agents'):
            team['lead_agent'] = opportunity['recommended_agents'][0]

        team['total_agents'] = len(set([team['lead_agent']] +
                                      team['support_agents'] +
                                      team['specialist_agents'] +
                                      team['review_agents']))

        return team

    async def _create_project_plan(self, opportunity: Dict, requirements: Dict,
                                  agent_team: Dict) -> Dict[str, Any]:
        """Create detailed project execution plan"""
        plan = {
            'phases': [],
            'timeline': {},
            'milestones': [],
            'deliverables': [],
            'resources_needed': []
        }

        # Phase 1: Research & Planning
        plan['phases'].append({
            'phase': 1,
            'name': 'Research & Planning',
            'duration_hours': 2,
            'agent': agent_team['lead_agent'],
            'tasks': [
                'Analyze client requirements in detail',
                'Research similar projects',
                'Create detailed outline',
                'Set up project structure'
            ],
            'human_approval': True
        })

        # Phase 2: Core Development
        core_duration = opportunity.get('estimated_completion_time', 8) - 4
        plan['phases'].append({
            'phase': 2,
            'name': 'Core Development',
            'duration_hours': core_duration,
            'agents': agent_team['specialist_agents'] or [agent_team['lead_agent']],
            'tasks': requirements.get('deliverables', ['Create main deliverables']),
            'human_approval': False
        })

        # Phase 3: Review & Optimization
        plan['phases'].append({
            'phase': 3,
            'name': 'Review & Optimization',
            'duration_hours': 1,
            'agents': agent_team['review_agents'] or [agent_team['lead_agent']],
            'tasks': [
                'Quality assurance check',
                'Optimize for requirements',
                'Final polish'
            ],
            'human_approval': True
        })

        # Phase 4: Delivery
        plan['phases'].append({
            'phase': 4,
            'name': 'Delivery & Handoff',
            'duration_hours': 1,
            'agent': agent_team['lead_agent'],
            'tasks': [
                'Package deliverables',
                'Create documentation',
                'Submit to client',
                'Handle revisions if needed'
            ],
            'human_approval': True
        })

        # Set timeline
        total_hours = sum(phase['duration_hours'] for phase in plan['phases'])
        plan['timeline'] = {
            'total_hours': total_hours,
            'start': 'Upon approval',
            'end': f"{total_hours} hours after start",
            'buffer_hours': 4
        }

        # Set milestones
        plan['milestones'] = [
            {'milestone': 'Project Plan Approved', 'hour': 0},
            {'milestone': 'Research Complete', 'hour': 2},
            {'milestone': '50% Development Complete', 'hour': total_hours // 2},
            {'milestone': 'Development Complete', 'hour': total_hours - 2},
            {'milestone': 'Final Delivery', 'hour': total_hours}
        ]

        # List deliverables
        plan['deliverables'] = requirements.get('deliverables', [])

        return plan

    def _calculate_profitability(self, opportunity: Dict, project_plan: Dict) -> Dict[str, Any]:
        """Calculate the profitability of taking this job"""
        budget = opportunity.get('budget', 0)
        total_hours = project_plan['timeline']['total_hours']

        # Cost calculation (agent time is essentially free, but we account for oversight)
        human_oversight_hours = sum(1 for phase in project_plan['phases']
                                   if phase.get('human_approval'))
        human_cost_per_hour = 50  # Your time value
        total_cost = human_oversight_hours * human_cost_per_hour

        # Revenue
        revenue = budget

        # Profit
        profit = revenue - total_cost
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0

        # Hourly rate
        effective_hourly = revenue / total_hours if total_hours > 0 else 0

        return {
            'revenue': revenue,
            'cost': total_cost,
            'profit': profit,
            'profit_margin': profit_margin,
            'effective_hourly_rate': effective_hourly,
            'human_hours_needed': human_oversight_hours,
            'agent_hours': total_hours - human_oversight_hours,
            'roi': (profit / total_cost * 100) if total_cost > 0 else float('inf'),
            'recommendation': 'ACCEPT' if profit > 100 and profit_margin > 50 else 'CONSIDER'
        }

    async def _assess_risks(self, opportunity: Dict, project_plan: Dict) -> Dict[str, Any]:
        """Assess risks associated with the project"""
        risks = {
            'level': 'LOW',  # LOW, MEDIUM, HIGH
            'factors': [],
            'mitigation': []
        }

        # Check deadline risk
        if opportunity.get('deadline'):
            days_available = self._days_until(opportunity['deadline'])
            days_needed = project_plan['timeline']['total_hours'] / 24

            if days_needed > days_available * 0.8:
                risks['factors'].append('Tight deadline')
                risks['mitigation'].append('Allocate multiple agents in parallel')
                risks['level'] = 'MEDIUM'

        # Check technical complexity
        if len(opportunity.get('skills_required', [])) > 5:
            risks['factors'].append('High technical complexity')
            risks['mitigation'].append('Assign specialist agents')

        # Check client rating
        if opportunity.get('client_rating', 5) < 4.0:
            risks['factors'].append('Potentially difficult client')
            risks['mitigation'].append('Clear communication and documentation')
            risks['level'] = 'MEDIUM'

        # Check budget adequacy
        if opportunity.get('budget', 0) < 200:
            risks['factors'].append('Low budget')
            risks['mitigation'].append('Streamline delivery process')

        # Determine overall risk level
        if len(risks['factors']) >= 3:
            risks['level'] = 'HIGH'
        elif len(risks['factors']) >= 1:
            risks['level'] = 'MEDIUM'

        risks['acceptable'] = risks['level'] != 'HIGH'

        return risks

    async def _generate_proposal(self, opportunity: Dict, project_plan: Dict) -> Dict[str, Any]:
        """Generate a professional proposal for the client"""
        proposal = {
            'greeting': f"Hello! I'm excited about your project '{opportunity['title']}'.",
            'understanding': "Based on your requirements, I understand you need...",
            'approach': "Here's how I'll deliver excellent results:",
            'phases': [],
            'timeline': f"I can complete this within {project_plan['timeline']['total_hours']} hours",
            'why_me': "Why I'm perfect for this job:",
            'qualifications': [],
            'call_to_action': "I'm ready to start immediately. Let's discuss your project!",
            'attachments': []
        }

        # Customize based on job type
        if 'content' in ' '.join(opportunity.get('skills_required', [])).lower():
            proposal['qualifications'] = [
                "Experienced in SEO-optimized content creation",
                "Deep knowledge of AI and technology topics",
                "Proven track record of viral content",
                "Fast turnaround with high quality"
            ]

        elif 'data' in ' '.join(opportunity.get('skills_required', [])).lower():
            proposal['qualifications'] = [
                "Expert in data analysis and visualization",
                "Proficient in Python, pandas, and ML libraries",
                "Experience with business intelligence",
                "Clear, actionable insights delivery"
            ]

        # Add phases
        for phase in project_plan['phases'][:3]:  # Don't reveal all internal phases
            proposal['phases'].append(f"{phase['name']}: {', '.join(phase['tasks'][:2])}")

        return proposal

    def _make_recommendation(self, profit_analysis: Dict, risk_assessment: Dict) -> Dict[str, Any]:
        """Make final recommendation on whether to pursue this opportunity"""
        score = 0

        # Profit score (0-40 points)
        if profit_analysis['profit'] > 500:
            score += 40
        elif profit_analysis['profit'] > 200:
            score += 30
        elif profit_analysis['profit'] > 100:
            score += 20
        elif profit_analysis['profit'] > 0:
            score += 10

        # ROI score (0-30 points)
        if profit_analysis['roi'] > 200:
            score += 30
        elif profit_analysis['roi'] > 100:
            score += 20
        elif profit_analysis['roi'] > 50:
            score += 10

        # Risk score (0-30 points)
        if risk_assessment['level'] == 'LOW':
            score += 30
        elif risk_assessment['level'] == 'MEDIUM':
            score += 15

        # Determine recommendation
        if score >= 70:
            action = 'PURSUE_IMMEDIATELY'
            confidence = 'HIGH'
        elif score >= 50:
            action = 'PURSUE'
            confidence = 'MEDIUM'
        elif score >= 30:
            action = 'CONSIDER'
            confidence = 'LOW'
        else:
            action = 'SKIP'
            confidence = 'LOW'

        return {
            'action': action,
            'confidence': confidence,
            'score': score,
            'reasoning': self._generate_reasoning(profit_analysis, risk_assessment, score)
        }

    def _generate_reasoning(self, profit: Dict, risk: Dict, score: int) -> str:
        """Generate reasoning for the recommendation"""
        reasons = []

        if profit['profit'] > 200:
            reasons.append(f"Strong profit potential: ${profit['profit']}")
        if profit['roi'] > 100:
            reasons.append(f"Excellent ROI: {profit['roi']:.0f}%")
        if risk['level'] == 'LOW':
            reasons.append("Low risk profile")
        if profit['human_hours_needed'] <= 2:
            reasons.append("Minimal human oversight needed")

        return ". ".join(reasons) if reasons else "Based on comprehensive analysis"

    def _days_until(self, date_str: str) -> int:
        """Calculate days until deadline"""
        try:
            from datetime import datetime
            deadline = datetime.strptime(date_str, '%Y-%m-%d')
            delta = deadline - datetime.now()
            return delta.days
        except:
            return 30

    async def _store_analysis(self, analysis: Dict):
        """Store analysis in Redis"""
        if self.redis_client:
            key = f"freelance:analysis:{analysis['job_id']}"
            self.redis_client.setex(key, 86400, json.dumps(analysis))

            # Update opportunity status
            opp_key = f"freelance:opportunity:{analysis['job_id']}"
            if self.redis_client.exists(opp_key):
                opp_data = json.loads(self.redis_client.get(opp_key))
                opp_data['status'] = 'analyzed'
                opp_data['recommendation'] = analysis['recommendation']['action']
                self.redis_client.setex(opp_key, 86400, json.dumps(opp_data))

            # Add to human review queue if recommended
            if analysis['recommendation']['action'] in ['PURSUE_IMMEDIATELY', 'PURSUE']:
                self.redis_client.lpush('freelance:queue:review', analysis['job_id'])