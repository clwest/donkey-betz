"""
Management command to validate data integrity across the unified platform
after migration from source projects.
"""

import logging
from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth import get_user_model

from core.models.agents_registry import UnifiedAgentTemplate, AgentRegistry
from sports.models import League, Team, Sportsbook
from content.models import ContentTemplate, KnowledgeBase
from self_awareness.models import SystemMetrics, SelfAnalysisReport, CodebaseSnapshot

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Validate data integrity and relationships across the unified platform'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Automatically fix detected issues where possible'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output with detailed checks'
        )
        parser.add_argument(
            '--component',
            choices=['agents', 'sports', 'content', 'self_awareness', 'all'],
            default='all',
            help='Validate specific component only'
        )
    
    def handle(self, *args, **options):
        self.fix_issues = options['fix_issues']
        self.verbose = options['verbose']
        component = options['component']
        
        if self.verbose:
            logger.setLevel(logging.DEBUG)
        
        self.stdout.write(self.style.SUCCESS(
            "🔍 Starting Data Integrity Validation for Unified Donkey Betz Platform"
        ))
        
        # Track validation results
        validation_results = {
            'agents': {'passed': 0, 'failed': 0, 'issues': []},
            'sports': {'passed': 0, 'failed': 0, 'issues': []},
            'content': {'passed': 0, 'failed': 0, 'issues': []},
            'self_awareness': {'passed': 0, 'failed': 0, 'issues': []},
            'database': {'passed': 0, 'failed': 0, 'issues': []},
            'relationships': {'passed': 0, 'failed': 0, 'issues': []}
        }
        
        # Run validations based on component selection
        if component in ['agents', 'all']:
            validation_results['agents'] = self.validate_agents()
        
        if component in ['sports', 'all']:
            validation_results['sports'] = self.validate_sports()
        
        if component in ['content', 'all']:
            validation_results['content'] = self.validate_content()
        
        if component in ['self_awareness', 'all']:
            validation_results['self_awareness'] = self.validate_self_awareness()
        
        if component == 'all':
            validation_results['database'] = self.validate_database_constraints()
            validation_results['relationships'] = self.validate_cross_system_relationships()
        
        # Print summary
        self.print_validation_summary(validation_results)
    
    def validate_agents(self):
        """Validate agent system integrity"""
        self.stdout.write(self.style.WARNING("🤖 Validating Agent System..."))
        
        result = {'passed': 0, 'failed': 0, 'issues': []}
        
        try:
            # Check agent templates
            agents = UnifiedAgentTemplate.objects.all()
            
            if agents.count() == 0:
                result['issues'].append("No agent templates found")
                result['failed'] += 1
            else:
                result['passed'] += 1
                if self.verbose:
                    self.stdout.write(f"✅ Found {agents.count()} agent templates")
            
            # Validate each agent
            for agent in agents:
                agent_issues = []
                
                # Check required fields
                if not agent.name:
                    agent_issues.append(f"Agent {agent.id} missing name")
                
                if not agent.description:
                    agent_issues.append(f"Agent {agent.name} missing description")
                
                if not agent.system_prompt:
                    agent_issues.append(f"Agent {agent.name} missing system prompt")
                
                if not agent.capabilities:
                    agent_issues.append(f"Agent {agent.name} has no capabilities")
                
                # Check specialization is valid
                valid_specializations = [choice[0] for choice in UnifiedAgentTemplate._meta.get_field('specialization').choices]
                if agent.specialization not in valid_specializations:
                    agent_issues.append(f"Agent {agent.name} has invalid specialization: {agent.specialization}")
                
                if agent_issues:
                    result['failed'] += 1
                    result['issues'].extend(agent_issues)
                    if self.fix_issues:
                        self.fix_agent_issues(agent, agent_issues)
                else:
                    result['passed'] += 1
            
            # Check agent registry
            try:
                registry = AgentRegistry.objects.get(registry_name='unified_agent_registry')
                if registry.total_agents != agents.count():
                    issue = f"Agent registry count mismatch: {registry.total_agents} vs {agents.count()}"
                    result['issues'].append(issue)
                    result['failed'] += 1
                    
                    if self.fix_issues:
                        registry.rebuild_indexes()
                        self.stdout.write("🔧 Fixed agent registry count")
                else:
                    result['passed'] += 1
                    if self.verbose:
                        self.stdout.write(f"✅ Agent registry is synchronized")
            
            except AgentRegistry.DoesNotExist:
                issue = "Agent registry does not exist"
                result['issues'].append(issue)
                result['failed'] += 1
                
                if self.fix_issues:
                    registry = AgentRegistry.objects.create(registry_name='unified_agent_registry')
                    registry.rebuild_indexes()
                    self.stdout.write("🔧 Created and initialized agent registry")
        
        except Exception as e:
            result['issues'].append(f"Agent validation error: {str(e)}")
            result['failed'] += 1
        
        return result
    
    def validate_sports(self):
        """Validate sports system integrity"""
        self.stdout.write(self.style.WARNING("⚽ Validating Sports System..."))
        
        result = {'passed': 0, 'failed': 0, 'issues': []}
        
        try:
            # Check leagues
            leagues = League.objects.all()
            if leagues.count() == 0:
                result['issues'].append("No leagues found")
                result['failed'] += 1
            else:
                result['passed'] += 1
                if self.verbose:
                    self.stdout.write(f"✅ Found {leagues.count()} leagues")
            
            # Check sportsbooks
            sportsbooks = Sportsbook.objects.all()
            if sportsbooks.count() == 0:
                result['issues'].append("No sportsbooks found")
                result['failed'] += 1
            else:
                result['passed'] += 1
                if self.verbose:
                    self.stdout.write(f"✅ Found {sportsbooks.count()} sportsbooks")
            
            # Validate each league
            for league in leagues:
                league_issues = []
                
                if not league.name:
                    league_issues.append(f"League {league.id} missing name")
                
                if not league.abbreviation:
                    league_issues.append(f"League {league.name} missing abbreviation")
                
                # Check valid sport type
                valid_sport_types = [choice[0] for choice in League._meta.get_field('sport_type').choices]
                if league.sport_type not in valid_sport_types:
                    league_issues.append(f"League {league.name} has invalid sport type: {league.sport_type}")
                
                if league_issues:
                    result['failed'] += 1
                    result['issues'].extend(league_issues)
                else:
                    result['passed'] += 1
            
            # Check teams have valid leagues
            teams = Team.objects.all()
            for team in teams:
                if team.league is None:
                    result['issues'].append(f"Team {team.name} has no league")
                    result['failed'] += 1
                elif team.league not in leagues:
                    result['issues'].append(f"Team {team.name} has invalid league reference")
                    result['failed'] += 1
                else:
                    result['passed'] += 1
        
        except Exception as e:
            result['issues'].append(f"Sports validation error: {str(e)}")
            result['failed'] += 1
        
        return result
    
    def validate_content(self):
        """Validate content system integrity"""
        self.stdout.write(self.style.WARNING("📚 Validating Content System..."))
        
        result = {'passed': 0, 'failed': 0, 'issues': []}
        
        try:
            # Check content templates
            templates = ContentTemplate.objects.all()
            if templates.count() == 0:
                result['issues'].append("No content templates found")
                result['failed'] += 1
            else:
                result['passed'] += 1
                if self.verbose:
                    self.stdout.write(f"✅ Found {templates.count()} content templates")
            
            # Check knowledge bases
            kbs = KnowledgeBase.objects.all()
            if kbs.count() == 0:
                result['issues'].append("No knowledge bases found")
                result['failed'] += 1
            else:
                result['passed'] += 1
                if self.verbose:
                    self.stdout.write(f"✅ Found {kbs.count()} knowledge bases")
            
            # Validate templates
            for template in templates:
                template_issues = []
                
                if not template.name:
                    template_issues.append(f"Template {template.id} missing name")
                
                if not template.system_prompt:
                    template_issues.append(f"Template {template.name} missing system prompt")
                
                if not template.user_prompt_template:
                    template_issues.append(f"Template {template.name} missing user prompt template")
                
                # Check valid template type
                valid_types = [choice[0] for choice in ContentTemplate._meta.get_field('template_type').choices]
                if template.template_type not in valid_types:
                    template_issues.append(f"Template {template.name} has invalid type: {template.template_type}")
                
                if template_issues:
                    result['failed'] += 1
                    result['issues'].extend(template_issues)
                else:
                    result['passed'] += 1
            
            # Validate knowledge bases
            for kb in kbs:
                kb_issues = []
                
                if not kb.name:
                    kb_issues.append(f"Knowledge base {kb.id} missing name")
                
                if kb.owner is None:
                    kb_issues.append(f"Knowledge base {kb.name} has no owner")
                
                # Check valid domain
                valid_domains = [choice[0] for choice in KnowledgeBase._meta.get_field('domain').choices]
                if kb.domain not in valid_domains:
                    kb_issues.append(f"Knowledge base {kb.name} has invalid domain: {kb.domain}")
                
                if kb_issues:
                    result['failed'] += 1
                    result['issues'].extend(kb_issues)
                else:
                    result['passed'] += 1
        
        except Exception as e:
            result['issues'].append(f"Content validation error: {str(e)}")
            result['failed'] += 1
        
        return result
    
    def validate_self_awareness(self):
        """Validate self-awareness system integrity"""
        self.stdout.write(self.style.WARNING("🧠 Validating Self-Awareness System..."))
        
        result = {'passed': 0, 'failed': 0, 'issues': []}
        
        try:
            # Check if models exist and are accessible
            try:
                metrics = SystemMetrics.objects.all()
                result['passed'] += 1
                if self.verbose:
                    self.stdout.write(f"✅ Found {metrics.count()} system metrics")
            except Exception as e:
                result['issues'].append(f"System metrics inaccessible: {str(e)}")
                result['failed'] += 1
            
            try:
                reports = SelfAnalysisReport.objects.all()
                result['passed'] += 1
                if self.verbose:
                    self.stdout.write(f"✅ Found {reports.count()} analysis reports")
            except Exception as e:
                result['issues'].append(f"Analysis reports inaccessible: {str(e)}")
                result['failed'] += 1
            
            try:
                snapshots = CodebaseSnapshot.objects.all()
                result['passed'] += 1
                if self.verbose:
                    self.stdout.write(f"✅ Found {snapshots.count()} codebase snapshots")
            except Exception as e:
                result['issues'].append(f"Codebase snapshots inaccessible: {str(e)}")
                result['failed'] += 1
        
        except Exception as e:
            result['issues'].append(f"Self-awareness validation error: {str(e)}")
            result['failed'] += 1
        
        return result
    
    def validate_database_constraints(self):
        """Validate database-level constraints and indexes"""
        self.stdout.write(self.style.WARNING("🗄️ Validating Database Constraints..."))
        
        result = {'passed': 0, 'failed': 0, 'issues': []}
        
        try:
            with connection.cursor() as cursor:
                # Check for foreign key constraint violations
                # This is a simplified check - in production you'd want more comprehensive tests
                
                # Check agent executions reference valid templates
                cursor.execute("""
                    SELECT COUNT(*) FROM agents_agentexecution 
                    WHERE template_id NOT IN (SELECT id FROM agents_unifiedagenttemplate)
                """)
                orphaned_executions = cursor.fetchone()[0]
                
                if orphaned_executions > 0:
                    result['issues'].append(f"{orphaned_executions} agent executions reference invalid templates")
                    result['failed'] += 1
                else:
                    result['passed'] += 1
                
                # Check teams reference valid leagues
                cursor.execute("""
                    SELECT COUNT(*) FROM sports_team 
                    WHERE league_id NOT IN (SELECT id FROM sports_league)
                """)
                orphaned_teams = cursor.fetchone()[0]
                
                if orphaned_teams > 0:
                    result['issues'].append(f"{orphaned_teams} teams reference invalid leagues")
                    result['failed'] += 1
                else:
                    result['passed'] += 1
                
                # Check documents have valid owners
                cursor.execute("""
                    SELECT COUNT(*) FROM content_document 
                    WHERE owner_id NOT IN (SELECT id FROM auth_user)
                """)
                orphaned_documents = cursor.fetchone()[0]
                
                if orphaned_documents > 0:
                    result['issues'].append(f"{orphaned_documents} documents have invalid owners")
                    result['failed'] += 1
                else:
                    result['passed'] += 1
        
        except Exception as e:
            result['issues'].append(f"Database validation error: {str(e)}")
            result['failed'] += 1
        
        return result
    
    def validate_cross_system_relationships(self):
        """Validate relationships between different systems"""
        self.stdout.write(self.style.WARNING("🔗 Validating Cross-System Relationships..."))
        
        result = {'passed': 0, 'failed': 0, 'issues': []}
        
        try:
            # Check that sports agents exist for sports system
            sports_agents = UnifiedAgentTemplate.objects.filter(
                specialization__in=['sports-analytics', 'odds-calculation']
            )
            
            if sports_agents.count() == 0:
                result['issues'].append("No sports-specialized agents found")
                result['failed'] += 1
            else:
                result['passed'] += 1
                if self.verbose:
                    self.stdout.write(f"✅ Found {sports_agents.count()} sports agents")
            
            # Check that content agents exist for content system
            content_agents = UnifiedAgentTemplate.objects.filter(
                specialization='content'
            )
            
            if content_agents.count() == 0:
                result['issues'].append("No content-specialized agents found")
                result['failed'] += 1
            else:
                result['passed'] += 1
                if self.verbose:
                    self.stdout.write(f"✅ Found {content_agents.count()} content agents")
            
            # Check knowledge bases have appropriate content templates
            sports_kb = KnowledgeBase.objects.filter(domain='sports').first()
            if sports_kb:
                sports_templates = ContentTemplate.objects.filter(
                    template_type__in=['sports_report', 'betting_guide']
                )
                if sports_templates.count() == 0:
                    result['issues'].append("Sports knowledge base exists but no sports content templates")
                    result['failed'] += 1
                else:
                    result['passed'] += 1
            
        except Exception as e:
            result['issues'].append(f"Cross-system validation error: {str(e)}")
            result['failed'] += 1
        
        return result
    
    def fix_agent_issues(self, agent, issues):
        """Fix common agent issues"""
        fixed_any = False
        
        for issue in issues:
            if "missing description" in issue and not agent.description:
                agent.description = f"Auto-generated description for {agent.name}"
                fixed_any = True
            
            if "missing system prompt" in issue and not agent.system_prompt:
                agent.system_prompt = f"You are {agent.name}, a {agent.specialization} specialist."
                fixed_any = True
            
            if "has no capabilities" in issue and not agent.capabilities:
                agent.capabilities = [agent.specialization]
                fixed_any = True
        
        if fixed_any:
            agent.save()
            self.stdout.write(f"🔧 Fixed issues for agent {agent.name}")
    
    def print_validation_summary(self, results):
        """Print comprehensive validation summary"""
        self.stdout.write(self.style.SUCCESS("\n" + "="*70))
        self.stdout.write(self.style.SUCCESS("🔍 VALIDATION SUMMARY"))
        self.stdout.write(self.style.SUCCESS("="*70))
        
        total_passed = 0
        total_failed = 0
        
        for component, data in results.items():
            passed = data['passed']
            failed = data['failed']
            
            total_passed += passed
            total_failed += failed
            
            if failed > 0:
                status = self.style.ERROR(f"❌ FAILED")
            else:
                status = self.style.SUCCESS(f"✅ PASSED")
            
            self.stdout.write(
                f"{status} {component.title()}: {passed} passed, {failed} failed"
            )
            
            # Show first 3 issues
            for issue in data['issues'][:3]:
                self.stdout.write(f"   ⚠️  {issue}")
            
            if len(data['issues']) > 3:
                self.stdout.write(f"   ... and {len(data['issues']) - 3} more issues")
        
        self.stdout.write(self.style.SUCCESS("-" * 70))
        
        if total_failed > 0:
            self.stdout.write(self.style.ERROR(
                f"🚨 OVERALL STATUS: FAILED ({total_passed} passed, {total_failed} failed)"
            ))
            self.stdout.write(self.style.WARNING(
                "\n💡 TIP: Run with --fix-issues to automatically fix common problems"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"🎉 OVERALL STATUS: PASSED ({total_passed} checks passed)"
            ))
        
        self.stdout.write(self.style.SUCCESS("="*70))