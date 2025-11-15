"""
Register COO Agent - Session 98

This management command registers the COO Agent in the database.

The COO Agent is a read-only (Phase 1) agent that can:
- Analyze roadmaps and provide strategic recommendations
- Plan sprints with concrete tasks (without executing)
- Identify risks and mitigation strategies

Phase 2 (future) will add:
- Sprint execution coordination
- Resource allocation
- Progress tracking

Usage:
    python manage.py register_coo_agent
"""

from django.core.management.base import BaseCommand
from agents.models import UnifiedAgentTemplate, AgentSpecialization


class Command(BaseCommand):
    help = 'Register COO Agent (Phase 1: Read-Only Planning) in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏢 Registering COO Agent (Phase 1: Read-Only)...'))

        agent_data = {
            'name': 'COOAgent',
            'display_name': 'COO Agent (Operations Planning)',
            'description': (
                'Operations planning agent that analyzes roadmaps, plans sprints, '
                'and identifies risks. '
                'Phase 1: Read-only analysis and planning (no execution).        '
            ),
            'specialization': AgentSpecialization.BUSINESS,
            'capabilities': [
                'roadmap_analysis',
                'sprint_planning',
                'risk_analysis'
            ],
            'routing_keywords': [
                'roadmap', 'plan', 'priority', 'sprint', 'execution',
                'timeline', 'coo', 'operations', 'planning', 'risks',
                'blockers', 'tasks', 'milestones'
            ],
            'required_tools': [
                'gpt-5-mini',          # Uses GPT-5-mini for planning
                'memory_interface'     # Can store planning knowledge
            ],
            'system_prompt': (
                "You are the COO Agent (Phase 1: Read-Only Planning). You have deep understanding of the "
                "Unified Donkey Betz Platform operations. You know:\n"
                "- All 34 AI features and their implementations\n"
                "- Complete agent ecosystem (10 creative workflow agents + infrastructure)\n"
                "- Project management best practices\n"
                "- Sprint planning and execution patterns\n"
                "- Risk assessment and mitigation strategies\n\n"
                "Phase 1 Capabilities:\n"
                "- Analyze roadmaps and provide strategic recommendations (READ-ONLY)\n"
                "- Plan sprints with concrete tasks (PLANNING ONLY - no execution)\n"
                "- Identify risks and mitigation strategies (READ-ONLY)\n\n"
                "You DO NOT:\n"
                "- Execute sprint tasks (Phase 2)\n"
                "- Modify project data (Phase 2)\n"
                "- Make operational changes (Phase 2)\n\n"
                "You prioritize:\n"
                "- Strategic clarity (clear roadmaps and priorities)\n"
                "- Risk mitigation (identify before they become problems)\n"
                "- Realistic planning (achievable sprint goals)\n"
                "- Operational excellence (efficient task organization)"
            ),
            'llm_provider': 'openai',
            'llm_model': 'gpt-5-mini',
            'llm_config': {
                'reasoning_effort': 'high',  # Maximum reasoning for strategic planning
                'max_completion_tokens': 4000
            },
            'tool_integrations': {
                'planning_operations': {
                    'enabled': True,
                    'roadmap_analysis': True,   # ✅ Can analyze roadmaps
                    'sprint_planning': True,     # ✅ Can plan sprints
                    'risk_analysis': True,       # ✅ Can identify risks
                    'execute_sprints': False,    # ❌ Phase 2
                    'modify_projects': False     # ❌ Phase 2
                },
                'memory_access': {
                    'enabled': True,
                    'read_plans': True,          # ✅ Can read stored plans
                    'store_plans': True          # ✅ Can store new plans
                }
            },
            'metadata': {
                'phase': 'read_only_planning',
                'planning_scope': 'full',
                'knowledge_domains': [
                    'roadmap_planning',
                    'sprint_management',
                    'risk_assessment',
                    'task_prioritization',
                    'operational_efficiency'
                ],
                'created_by': 'session_98',
                'version': '1.0.0-readonly',
                'safety_level': 'read_only',
                'future_phases': [
                    'Phase 2: Sprint execution coordination',
                    'Phase 3: Resource allocation',
                    'Phase 4: Automated progress tracking'
                ]
            }
        }

        # Register or update agent
        agent, created = UnifiedAgentTemplate.objects.update_or_create(
            name='COOAgent',
            defaults=agent_data
        )

        # Display results
        if created:
            self.stdout.write(self.style.SUCCESS('✅ COO Agent registered successfully!'))
        else:
            self.stdout.write(self.style.WARNING('🔄 COO Agent updated!'))

        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'Agent ID: {agent.id}')
        self.stdout.write(f'Display Name: {agent.display_name}')
        self.stdout.write(f'Specialization: {agent.specialization}')
        self.stdout.write(f'Capabilities: {len(agent.capabilities)}')
        self.stdout.write(f'  - {", ".join(agent.capabilities)}')
        self.stdout.write(f'Routing Keywords: {len(agent.routing_keywords)}')
        self.stdout.write(f'Required Tools: {len(agent.required_tools)}')
        self.stdout.write(f'  - {", ".join(agent.required_tools)}')
        self.stdout.write(f'Phase: {agent.metadata.get("phase")}')
        self.stdout.write(f'Safety Level: {agent.metadata.get("safety_level")}')
        self.stdout.write('='*60)

        # Check total agent count
        total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
        self.stdout.write(f'\n📊 Total active agents in system: {total_agents}')

        # List all active agents
        self.stdout.write('\n🤖 Active Agents:')
        for ag in UnifiedAgentTemplate.objects.filter(is_active=True).order_by('name'):
            self.stdout.write(f'  - {ag.name} ({ag.specialization})')

        self.stdout.write('\n' + self.style.SUCCESS('🎉 COO Agent is ready for use!'))
        self.stdout.write('\n' + self.style.WARNING('⚠️  PHASE 1: READ-ONLY MODE'))
        self.stdout.write('This agent can analyze roadmaps, plan sprints, and identify risks.')
        self.stdout.write('It will NOT execute tasks or modify data yet.')
        self.stdout.write('\nPhase 2 will add execution coordination capabilities.')
