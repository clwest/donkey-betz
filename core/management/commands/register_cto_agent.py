"""
Register CTO Agent - Session 98

This management command registers the CTO Agent in the database.

The CTO Agent is a read-only (Phase 1) agent that can:
- Analyze codebase and features
- Plan implementations (without executing)
- Coordinate with other agents
- Analyze documentation gaps

Phase 2 (future) will add:
- Safe code modifications
- Documentation updates
- Refactoring with approval

Usage:
    python manage.py register_cto_agent
"""

from django.core.management.base import BaseCommand
from core.models.agents_registry import UnifiedAgentTemplate, AgentSpecialization


class Command(BaseCommand):
    help = 'Register CTO Agent (Phase 1: Read-Only Analysis) in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏗️ Registering CTO Agent (Phase 1: Read-Only)...'))

        agent_data = {
            'name': 'CTOAgent',
            'display_name': 'CTO Agent (System Architect)',
            'description': (
                'Deep codebase understanding agent that analyzes architecture, '
                'plans implementations, and coordinates platform evolution. '
                'Phase 1: Read-only analysis and planning (no file modifications).'
            ),
            'specialization': AgentSpecialization.TECHNICAL,
            'capabilities': [
                'codebase_analysis',
                'architectural_planning',
                'documentation_analysis',
                'agent_coordination',
                'implementation_planning'
            ],
            'routing_keywords': [
                'cto', 'architecture', 'codebase', 'analyze', 'plan',
                'technical', 'system', 'infrastructure', 'review',
                'code review', 'analyze docs', 'coordinate', 'planning'
            ],
            'required_tools': [
                'file_read',           # Can read files
                'code_analysis',       # Can analyze code
                'gpt-5-mini',          # Uses GPT-5-mini for reasoning
                'agent_query_protocol', # Can query other agents
                'memory_interface'     # Can store knowledge
            ],
            'system_prompt': (
                "You are the CTO Agent (Phase 1: Read-Only Analysis). You have deep understanding of the "
                "Unified Donkey Betz Platform codebase. You know:\n"
                "- All 34 AI features and their implementations\n"
                "- Complete agent ecosystem (10 creative workflow agents + infrastructure)\n"
                "- All 6 external API integrations (Stability AI, Runway ML, ElevenLabs, Replicate, OpenAI, DaVinci)\n"
                "- Database schema and models\n"
                "- Architecture patterns and conventions\n\n"
                "Phase 1 Capabilities:\n"
                "- Analyze code quality and architecture (READ-ONLY)\n"
                "- Plan implementations (PLANNING ONLY - no execution)\n"
                "- Analyze documentation gaps (READ-ONLY)\n"
                "- Coordinate with other agents for complex tasks\n\n"
                "You DO NOT:\n"
                "- Write or modify files (Phase 2)\n"
                "- Execute code changes (Phase 2)\n"
                "- Make destructive changes (Phase 2)\n\n"
                "You prioritize:\n"
                "- Safety (analysis only, no changes)\n"
                "- Quality (maintain 99.9% reality score)\n"
                "- Clarity (detailed plans and recommendations)\n"
                "- Coordination (work with other agents)"
            ),
            'llm_provider': 'openai',
            'llm_model': 'gpt-5-mini',
            'llm_config': {
                'reasoning_effort': 'high',  # Maximum reasoning for CTO decisions
                'max_completion_tokens': 4000
            },
            'tool_integrations': {
                'file_operations': {
                    'enabled': True,
                    'read': True,       # ✅ Can read files
                    'analyze': True,    # ✅ Can analyze code
                    'write': False,     # ❌ Phase 2
                    'edit': False       # ❌ Phase 2
                },
                'database_access': {
                    'enabled': True,
                    'schema_query': True,   # ✅ Can query schema
                    'read_models': True,    # ✅ Can read models
                    'modify_schema': False  # ❌ Phase 2
                },
                'agent_coordination': {
                    'enabled': True,
                    'can_query_agents': True,  # ✅ Can query agents
                    'can_coordinate': True     # ✅ Can coordinate agents
                }
            },
            'metadata': {
                'phase': 'read_only_analysis',
                'codebase_scope': 'full',
                'knowledge_domains': [
                    'stability_ai',
                    'runway_ml',
                    'elevenlabs',
                    'replicate',
                    'openai',
                    'davinci_resolve',
                    'agent_system',
                    'database',
                    'frontend'
                ],
                'created_by': 'session_98',
                'version': '1.0.0-readonly',
                'safety_level': 'read_only',
                'future_phases': [
                    'Phase 2: Safe code modifications with approval',
                    'Phase 3: Automated refactoring',
                    'Phase 4: Self-improving architecture'
                ]
            }
        }

        # Register or update agent
        agent, created = UnifiedAgentTemplate.objects.update_or_create(
            name='CTOAgent',
            defaults=agent_data
        )

        # Display results
        if created:
            self.stdout.write(self.style.SUCCESS('✅ CTO Agent registered successfully!'))
        else:
            self.stdout.write(self.style.WARNING('🔄 CTO Agent updated!'))

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

        self.stdout.write('\n' + self.style.SUCCESS('🎉 CTO Agent is ready for use!'))
        self.stdout.write('\n' + self.style.WARNING('⚠️  PHASE 1: READ-ONLY MODE'))
        self.stdout.write('This agent can analyze, plan, and coordinate.')
        self.stdout.write('It will NOT modify files or execute changes yet.')
        self.stdout.write('\nPhase 2 will add safe code modification capabilities.')
