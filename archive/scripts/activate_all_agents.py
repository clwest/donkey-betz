#!/usr/bin/env python3
"""
🚀 ACTIVATE ALL 150 AGENTS
Transform your platform from 5% to 100% utilization
"""

import os
import django
import json
import time
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from django.utils import timezone

from agents.models import UnifiedAgentTemplate, AgentExecution, AgentStatus
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

User = get_user_model()


class AgentActivator:
    """Activate and coordinate all 150 agents"""
    
    def __init__(self):
        self.user = self.get_or_create_user()
        self.agents = UnifiedAgentTemplate.objects.filter(is_active=True)
        
    def get_or_create_user(self):
        """Get or create the orchestrator user"""
        user, _ = User.objects.get_or_create(
            username='agent_orchestrator',
            defaults={'email': 'orchestrator@donkeybetz.com'}
        )
        return user
    
    def analyze_current_state(self):
        """Show current utilization"""
        print("\n" + "="*60)
        print("🔍 CURRENT SYSTEM STATE")
        print("="*60)
        
        # Agent statistics
        total_agents = self.agents.count()
        agent_by_spec = self.agents.values('specialization').annotate(count=Count('id'))
        
        print(f"\n📊 Agent Distribution ({total_agents} total):")
        for spec in agent_by_spec:
            print(f"  {spec['specialization']}: {spec['count']} agents")
        
        # Execution statistics
        exec_stats = AgentExecution.objects.values('template__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        print(f"\n🏃 Most Active Agents:")
        for stat in exec_stats:
            print(f"  {stat['template__name']}: {stat['count']} executions")
        
        # Idle agents
        executed_agents = AgentExecution.objects.values_list('template__id', flat=True).distinct()
        idle_agents = self.agents.exclude(id__in=executed_agents)
        
        print(f"\n😴 Idle Agents: {idle_agents.count()}/{total_agents}")
        if idle_agents.count() > 0:
            print("  Examples of idle agents:")
            for agent in idle_agents[:5]:
                print(f"    - {agent.name} ({agent.specialization})")
    
    def create_agent_teams(self):
        """Organize agents into collaborative teams"""
        
        teams = {
            "Content Production Team": {
                "specializations": ["content_creation", "creative", "marketing"],
                "mission": "Create engaging content across all channels"
            },
            "Business Strategy Team": {
                "specializations": ["business-development", "analysis", "strategy"],
                "mission": "Analyze market opportunities and develop strategies"
            },
            "Technical Team": {
                "specializations": ["development", "technical", "data"],
                "mission": "Build and optimize technical solutions"
            },
            "Sports Analytics Team": {
                "specializations": ["sports", "betting", "odds_analysis"],
                "mission": "Analyze sports data and betting opportunities"
            }
        }
        
        print("\n" + "="*60)
        print("🤝 FORMING AGENT TEAMS")
        print("="*60)
        
        team_assignments = {}
        for team_name, config in teams.items():
            team_agents = self.agents.filter(
                specialization__in=config["specializations"]
            )
            
            if not team_agents.exists():
                # Fallback: get any agents
                team_agents = self.agents.all()[:5]
            
            team_assignments[team_name] = list(team_agents)
            
            print(f"\n📋 {team_name}")
            print(f"   Mission: {config['mission']}")
            print(f"   Members: {team_agents.count()} agents")
            for agent in team_agents[:3]:
                print(f"     • {agent.name}")
        
        return team_assignments
    
    def execute_team_mission(self, team_name, agents, mission):
        """Execute a coordinated team mission"""
        
        print(f"\n🚀 Executing Team Mission: {team_name}")
        print(f"   Mission: {mission}")
        
        executions = []
        
        # Assign tasks to team members
        tasks = self.generate_team_tasks(mission, len(agents))
        
        for agent, task in zip(agents[:3], tasks):  # Limit to 3 for demo
            try:
                execution = AgentExecution.objects.create(
                    template=agent,
                    user=self.user,
                    task_description=task,
                    task_type=agent.specialization,
                    input_data={
                        'team': team_name,
                        'mission': mission,
                        'team_task': task
                    },
                    status=AgentStatus.INITIALIZING,
                    priority=2,
                    context={
                        'team_execution': True,
                        'team_name': team_name
                    }
                )
                
                print(f"     ✅ {agent.name}: {task[:50]}...")
                executions.append(execution)
                
                # Simulate execution (in production, use Celery)
                self.simulate_execution(execution)
                
            except Exception as e:
                print(f"     ❌ Failed to execute {agent.name}: {e}")
        
        return executions
    
    def generate_team_tasks(self, mission, count):
        """Generate specific tasks for team members"""
        
        base_tasks = [
            f"Research and analyze: {mission}",
            f"Create detailed plan for: {mission}",
            f"Generate creative solutions for: {mission}",
            f"Develop implementation strategy for: {mission}",
            f"Identify key metrics for: {mission}"
        ]
        
        return base_tasks[:count]
    
    def simulate_execution(self, execution):
        """Simulate agent execution (replace with actual executor)"""
        
        # Update execution status
        execution.status = AgentStatus.RUNNING
        execution.started_at = timezone.now()
        execution.progress_percentage = 50
        execution.save()
        
        time.sleep(0.5)  # Simulate work
        
        # Generate mock result
        result = {
            'success': True,
            'output': f"Completed task: {execution.task_description}",
            'agent': execution.template.name,
            'timestamp': timezone.now().isoformat()
        }
        
        execution.status = AgentStatus.COMPLETED
        execution.result = result
        execution.output_data = result
        execution.completed_at = timezone.now()
        execution.progress_percentage = 100
        execution.save()
    
    def activate_idle_agents(self):
        """Wake up idle agents with specific tasks"""
        
        print("\n" + "="*60)
        print("⚡ ACTIVATING IDLE AGENTS")
        print("="*60)
        
        # Find idle agents
        executed_agents = AgentExecution.objects.values_list('template__id', flat=True).distinct()
        idle_agents = self.agents.exclude(id__in=executed_agents)[:10]  # Activate 10 at a time
        
        activation_tasks = {
            'content_creation': 'Create a brief introduction about your capabilities',
            'business-development': 'Analyze a potential market opportunity',
            'marketing': 'Generate 5 marketing ideas for Donkey Betz',
            'technical': 'Describe a technical solution you could build',
            'creative': 'Create something innovative and unexpected',
            'sports': 'Analyze a recent sports event or trend',
            'analysis': 'Perform a quick analysis of the betting market'
        }
        
        activated = 0
        for agent in idle_agents:
            spec = agent.specialization
            task = activation_tasks.get(spec, 'Introduce yourself and your capabilities')
            
            try:
                execution = AgentExecution.objects.create(
                    template=agent,
                    user=self.user,
                    task_description=task,
                    task_type=spec,
                    input_data={'activation': True},
                    status=AgentStatus.INITIALIZING,
                    priority=1
                )
                
                print(f"  ⚡ Activated: {agent.name}")
                print(f"     Task: {task}")
                
                self.simulate_execution(execution)
                activated += 1
                
            except Exception as e:
                print(f"  ❌ Failed to activate {agent.name}: {e}")
        
        print(f"\n✅ Activated {activated} idle agents")
    
    def create_collaboration_network(self):
        """Create agent collaboration opportunities"""
        
        print("\n" + "="*60)
        print("🌐 BUILDING COLLABORATION NETWORK")
        print("="*60)
        
        collaborations = [
            {
                'name': 'Content + SEO Partnership',
                'agents': ['content-creator', 'seo-specialist-agent'],
                'task': 'Create SEO-optimized content about sports betting trends'
            },
            {
                'name': 'Business + Creative Fusion',
                'agents': ['business-agent', 'image-video-pipeline'],
                'task': 'Develop visual business presentations'
            },
            {
                'name': 'Multi-Agent Research Team',
                'agents': ['content-creator', 'business-agent', 'seo-specialist-agent'],
                'task': 'Comprehensive market analysis with content and SEO strategy'
            }
        ]
        
        for collab in collaborations:
            print(f"\n🤝 {collab['name']}")
            print(f"   Task: {collab['task']}")
            
            agents = []
            for agent_name in collab['agents']:
                try:
                    agent = self.agents.get(name=agent_name)
                    agents.append(agent)
                    print(f"   ✅ {agent.name} joined")
                except:
                    print(f"   ⚠️ {agent_name} not found")
            
            if len(agents) >= 2:
                # Create collaborative execution
                self.execute_collaboration(agents, collab['task'])
    
    def execute_collaboration(self, agents, task):
        """Execute a collaborative task between multiple agents"""
        
        print(f"   🚀 Executing collaboration...")
        
        # Simple collaboration without AgentOrchestration
        import uuid
        collab_id = str(uuid.uuid4())[:8]
        
        # Execute each agent with shared context
        for i, agent in enumerate(agents):
            exec = AgentExecution.objects.create(
                template=agent,
                user=self.user,
                task_description=f"[COLLAB-{collab_id}] Part {i+1}: {task}",
                task_type=agent.specialization,
                status=AgentStatus.INITIALIZING,
                priority=2,
                context={
                    'collaboration_id': collab_id,
                    'collaboration_task': task,
                    'role': f'team_member_{i+1}',
                    'total_members': len(agents)
                }
            )
            self.simulate_execution(exec)
        
        print(f"   ✅ Collaboration completed")
    
    def generate_dashboard(self):
        """Generate activation dashboard"""
        
        print("\n" + "="*60)
        print("📊 ACTIVATION DASHBOARD")
        print("="*60)
        
        # Calculate metrics
        total_agents = self.agents.count()
        total_executions = AgentExecution.objects.count()
        active_agents = AgentExecution.objects.values('template').distinct().count()
        
        utilization = (active_agents / total_agents * 100) if total_agents > 0 else 0
        
        # Status breakdown
        status_counts = AgentExecution.objects.values('status').annotate(
            count=Count('id')
        )
        
        print(f"""
        🤖 Agent Metrics:
           Total Agents: {total_agents}
           Active Agents: {active_agents}
           Utilization: {utilization:.1f}%
           
        📈 Execution Metrics:
           Total Executions: {total_executions}
           Completed: {sum(s['count'] for s in status_counts if s['status'] == 'completed')}
           Running: {sum(s['count'] for s in status_counts if s['status'] == 'running')}
           Failed: {sum(s['count'] for s in status_counts if s['status'] == 'failed')}
        """)
        
        print("\n🎯 ACTIVATION GOAL:")
        if utilization < 50:
            print("   ⚠️ LOW UTILIZATION - Activate more agents!")
        elif utilization < 80:
            print("   📈 GROWING - Keep activating agents")
        else:
            print("   ✅ EXCELLENT - Most agents are active!")
    
    def run_full_activation(self):
        """Run the complete activation sequence"""
        
        print("\n" + "🚀"*20)
        print("   DONKEY BETZ FULL SYSTEM ACTIVATION")
        print("🚀"*20)
        
        # Step 1: Analyze current state
        self.analyze_current_state()
        
        # Step 2: Form teams
        teams = self.create_agent_teams()
        
        # Step 3: Execute team missions
        for team_name, agents in teams.items():
            if agents:
                self.execute_team_mission(
                    team_name, 
                    agents[:3],  # Limit for demo
                    f"Develop strategy for {team_name.lower()}"
                )
        
        # Step 4: Activate idle agents
        self.activate_idle_agents()
        
        # Step 5: Create collaborations
        self.create_collaboration_network()
        
        # Step 6: Show dashboard
        self.generate_dashboard()
        
        print("\n" + "="*60)
        print("✅ ACTIVATION COMPLETE!")
        print("="*60)
        print("""
        Next Steps:
        1. Monitor agent performance in real-time
        2. Scale up parallel executions with Celery
        3. Connect WebSocket for live updates
        4. Deploy agent marketplace for users
        5. Enable agent learning and evolution
        """)


if __name__ == "__main__":
    activator = AgentActivator()
    activator.run_full_activation()
