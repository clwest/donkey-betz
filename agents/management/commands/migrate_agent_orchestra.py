"""
Management command to migrate agents from donkey-betz-agent-orchestra
"""

import os
import sys
import json
import logging
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from core.models.agents_registry import UnifiedAgentTemplate, AgentRegistry, AgentTool


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate agents from donkey-betz-agent-orchestra to unified platform'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--orchestra-path',
            type=str,
            default='/Users/donkeyking/development/donkey-betz-agent-orchestra',
            help='Path to the donkey-betz-agent-orchestra directory'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration even if agents already exist'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )
    
    def handle(self, *args, **options):
        orchestra_path = Path(options['orchestra_path'])
        dry_run = options['dry_run']
        force = options['force']
        verbose = options['verbose']
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.stdout.write(self.style.SUCCESS(
            f"Starting agent migration from {orchestra_path}"
        ))
        
        if not orchestra_path.exists():
            raise CommandError(f"Orchestra path does not exist: {orchestra_path}")
        
        # Check if orchestra directory has the expected structure
        backend_path = orchestra_path / 'backend'
        if not backend_path.exists():
            raise CommandError(f"Backend directory not found: {backend_path}")
        
        # Import agent templates from the orchestra
        agents_path = backend_path / 'agents'
        if not agents_path.exists():
            raise CommandError(f"Agents directory not found: {agents_path}")
        
        # Look for agent templates
        templates_file = agents_path / 'templates.py'
        if not templates_file.exists():
            raise CommandError(f"Templates file not found: {templates_file}")
        
        try:
            migrated_count = self._migrate_agent_templates(
                templates_file, dry_run=dry_run, force=force, verbose=verbose
            )
            
            if dry_run:
                self.stdout.write(self.style.WARNING(
                    f"DRY RUN: Would migrate {migrated_count} agents"
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully migrated {migrated_count} agents"
                ))
                
                # Rebuild agent registry indexes
                registry, created = AgentRegistry.objects.get_or_create(
                    registry_name='unified_agent_registry'
                )
                registry.rebuild_indexes()
                
                self.stdout.write(self.style.SUCCESS(
                    f"Agent registry updated: {registry.total_agents} total agents"
                ))
        
        except Exception as e:
            logger.exception("Error during migration")
            raise CommandError(f"Migration failed: {str(e)}")
    
    def _migrate_agent_templates(self, templates_file, dry_run=False, force=False, verbose=False):
        """Migrate agent templates from the orchestra templates.py file"""
        
        # Read and parse the templates file
        templates_content = templates_file.read_text()
        
        # Extract AGENT_TEMPLATES dictionary
        # This is a bit hacky, but we need to safely evaluate the Python file
        agent_templates = {}
        
        try:
            # Create a safe namespace for execution
            namespace = {
                '__builtins__': {
                    'dict': dict,
                    'list': list,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'None': None,
                    'True': True,
                    'False': False,
                }
            }
            
            # Execute the file to get AGENT_TEMPLATES
            exec(templates_content, namespace)
            agent_templates = namespace.get('AGENT_TEMPLATES', {})
            
            if not agent_templates:
                raise CommandError("No AGENT_TEMPLATES found in templates.py")
            
        except Exception as e:
            logger.error(f"Error parsing templates file: {e}")
            # Fallback: try to extract templates using text parsing
            agent_templates = self._parse_templates_manually(templates_content)
        
        if verbose:
            self.stdout.write(f"Found {len(agent_templates)} agent templates")
        
        migrated_count = 0
        
        with transaction.atomic():
            for template_key, template_data in agent_templates.items():
                try:
                    if self._migrate_single_agent(
                        template_key, template_data, dry_run=dry_run, 
                        force=force, verbose=verbose
                    ):
                        migrated_count += 1
                        
                except Exception as e:
                    logger.error(f"Error migrating agent {template_key}: {e}")
                    continue
        
        return migrated_count
    
    def _migrate_single_agent(self, template_key, template_data, dry_run=False, force=False, verbose=False):
        """Migrate a single agent template"""
        
        agent_name = template_data.get('name', template_key)
        
        # Check if agent already exists
        if UnifiedAgentTemplate.objects.filter(name=agent_name).exists():
            if not force:
                if verbose:
                    self.stdout.write(f"Skipping existing agent: {agent_name}")
                return False
            else:
                if verbose:
                    self.stdout.write(f"Overwriting existing agent: {agent_name}")
        
        if dry_run:
            self.stdout.write(f"Would migrate: {agent_name}")
            return True
        
        # Map orchestra specialization to unified specialization
        specialization = self._map_specialization(template_data.get('specialization', 'research'))
        
        # Extract and clean data
        capabilities = template_data.get('capabilities', [])
        if isinstance(capabilities, str):
            capabilities = [capabilities]
        
        required_tools = template_data.get('required_tools', [])
        if isinstance(required_tools, str):
            required_tools = [required_tools]
        
        routing_keywords = template_data.get('routing_keywords', [])
        if isinstance(routing_keywords, str):
            routing_keywords = [routing_keywords]
        
        # Create or update agent template
        agent_template, created = UnifiedAgentTemplate.objects.update_or_create(
            name=agent_name,
            defaults={
                'display_name': template_data.get('name', agent_name),
                'description': template_data.get('description', ''),
                'specialization': specialization,
                'capabilities': capabilities,
                'required_tools': required_tools,
                'optional_tools': [],
                'system_prompt': template_data.get('system_prompt', ''),
                'personality_traits': template_data.get('personality_traits', {}),
                'llm_provider': template_data.get('llm_provider', 'openai'),
                'llm_model': template_data.get('llm_model', 'gpt-5-mini'),
                'llm_config': template_data.get('llm_config', {}),
                'routing_keywords': routing_keywords,
                'routing_patterns': [],
                'domain_tags': self._extract_domain_tags(template_data),
                'confidence_score': template_data.get('confidence_score', 0.5),
                'avg_completion_time': template_data.get('avg_completion_time', 300),
                'success_rate': template_data.get('success_rate', 0.95),
                'usage_count': template_data.get('usage_count', 0),
                'is_public': True,
                'is_verified': False,
                'supports_streaming': False,
                'supports_collaboration': True,
                'learning_enabled': True,
                'self_improvement_enabled': False,
            }
        )
        
        action = "Created" if created else "Updated"
        if verbose:
            self.stdout.write(f"{action} agent: {agent_name} ({specialization})")
        
        return True
    
    def _map_specialization(self, orchestra_specialization):
        """Map orchestra specialization to unified platform specialization"""
        
        # Direct mappings
        mapping = {
            'research': 'research',
            'content': 'content',
            'business': 'business',
            'career': 'career',
            'technical': 'technical',
            'creative': 'creative',
            'marketing': 'marketing',
            'financial': 'financial',
            'legal': 'legal',
            'communication': 'communication',
            'risk-assessment': 'risk-assessment',
            'sports-analytics': 'sports-analytics',
            'implementation': 'implementation',
            'odds-calculation': 'odds-calculation',
            'token-budget': 'token-budget',
            'rag-diagnostics': 'rag-diagnostics',
            'glossary-anchor-curator': 'glossary-anchor-curator',
            'memory-bridge-coordinator': 'memory-bridge-coordinator',
            'core-agents-enablement-coordinator': 'core-agents-enablement-coordinator',
            'narrative-predictor-agent': 'narrative-predictor-agent',
            'empire-builder-orchestrator': 'empire-builder-orchestrator',
            'correlation-hunter': 'correlation-hunter',
            'shit-talker': 'shit-talker',
            'autonomous-knowledge-evolution-engine': 'autonomous-knowledge-evolution-engine',
        }
        
        return mapping.get(orchestra_specialization, 'research')
    
    def _extract_domain_tags(self, template_data):
        """Extract domain tags from template data"""
        tags = []
        
        specialization = template_data.get('specialization', '')
        capabilities = template_data.get('capabilities', [])
        
        # Add tags based on specialization
        if 'sports' in specialization or 'betting' in specialization or 'odds' in specialization:
            tags.append('sports')
        if 'content' in specialization:
            tags.append('content')
        if 'business' in specialization or 'marketing' in specialization:
            tags.append('business')
        if 'technical' in specialization or 'implementation' in specialization:
            tags.append('technical')
        
        # Add tags based on capabilities
        if isinstance(capabilities, list):
            for capability in capabilities:
                if isinstance(capability, str):
                    if 'sports' in capability.lower() or 'betting' in capability.lower():
                        tags.append('sports')
                    if 'content' in capability.lower():
                        tags.append('content')
                    if 'orchestration' in capability.lower():
                        tags.append('orchestration')
        
        return list(set(tags))  # Remove duplicates
    
    def _parse_templates_manually(self, content):
        """Manually parse templates if exec() fails"""
        # This is a fallback method for when exec() doesn't work
        # We'll look for patterns in the file
        
        templates = {}
        
        # Look for basic template definitions
        lines = content.split('\n')
        current_template = None
        
        for line in lines:
            line = line.strip()
            
            # Look for template start
            if line.startswith("'") and line.endswith(": {"):
                template_name = line.split("'")[1]
                current_template = template_name
                templates[template_name] = {
                    'name': template_name.replace('_', ' ').title(),
                    'description': f'Migrated {template_name} agent',
                    'specialization': 'research',
                    'capabilities': [],
                    'required_tools': [],
                    'system_prompt': f'You are a {template_name} agent.',
                    'personality_traits': {},
                    'routing_keywords': [template_name]
                }
        
        return templates