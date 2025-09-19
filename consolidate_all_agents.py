#!/usr/bin/env python
"""
Agent Consolidation Script
Imports agents from all three projects into unified-donkey-betz platform
"""

import os
import sys
import django
import json
import hashlib
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from agents.models import UnifiedAgentTemplate

User = get_user_model()

class AgentConsolidator:
    def __init__(self):
        self.chris_user = User.objects.get(username='chris')
        self.imported_agents = []
        self.duplicates = []
        self.errors = []
        
    def normalize_specialization(self, spec):
        """Normalize specialization names"""
        spec_map = {
            'sports_betting': 'sports-analytics',
            'business': 'business-development', 
            'implementation': 'technical',
            'rag-diagnostics': 'rag-analysis',
            'dependency-scanner': 'technical',
            'glossary-anchor-curator': 'content',
            'token-budget': 'optimization'
        }
        return spec_map.get(spec, spec)
        
    def create_agent_hash(self, name, specialization):
        """Create unique hash for deduplication"""
        key = f"{name.lower().strip()}_{specialization.lower().strip()}"
        return hashlib.md5(key.encode()).hexdigest()[:8]
        
    def import_dbao_agents(self):
        """Import agents from donkey-betz-agent-orchestra"""
        dbao_path = "/Users/donkeyking/development/donkey-betz-agent-orchestra/agent_prompts_dump.json"
        
        if not os.path.exists(dbao_path):
            self.errors.append(f"DBAO file not found: {dbao_path}")
            return
            
        with open(dbao_path, 'r') as f:
            dbao_agents = json.load(f)
            
        print(f"🔄 Importing {len(dbao_agents)} agents from DBAO...")
        
        for agent_data in dbao_agents:
            try:
                name = agent_data.get('name', 'Unknown Agent')
                specialization = self.normalize_specialization(agent_data.get('specialization', 'general'))
                
                # Check for duplicates
                agent_hash = self.create_agent_hash(name, specialization)
                if UnifiedAgentTemplate.objects.filter(creator=self.chris_user, name__iexact=name).exists():
                    self.duplicates.append(f"DBAO: {name}")
                    continue
                    
                agent = UnifiedAgentTemplate.objects.create(
                    name=name.lower().replace(' ', '-'),
                    display_name=name,
                    description=agent_data.get('system_prompt', '')[:500] + '...' if len(agent_data.get('system_prompt', '')) > 500 else agent_data.get('system_prompt', ''),
                    specialization=specialization,
                    capabilities=agent_data.get('capabilities', []),
                    system_prompt=agent_data.get('system_prompt', ''),
                    creator=self.chris_user,
                    llm_provider='openai',
                    llm_model='gpt-5-mini',
                    is_active=True,
                    is_public=True
                )
                self.imported_agents.append(f"DBAO: {agent.display_name}")
                
            except Exception as e:
                self.errors.append(f"Error importing DBAO agent {name}: {e}")
                
    def import_ai_studio_agents(self):
        """Import agents from ai-content-studio"""
        ai_studio_path = "/Users/donkeyking/development/ai-content-studio/populate_agents.py"
        
        if not os.path.exists(ai_studio_path):
            self.errors.append(f"AI Studio file not found: {ai_studio_path}")
            return
            
        # Extract AGENTS list from populate_agents.py
        with open(ai_studio_path, 'r') as f:
            content = f.read()
            
        # Find the AGENTS array
        start_marker = 'AGENTS = ['
        start_idx = content.find(start_marker)
        if start_idx == -1:
            self.errors.append("Could not find AGENTS array in AI Studio file")
            return
            
        # Find the matching closing bracket
        bracket_count = 0
        agents_start = start_idx + len(start_marker) - 1  # Include the opening bracket
        idx = agents_start
        while idx < len(content):
            if content[idx] == '[':
                bracket_count += 1
            elif content[idx] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    agents_end = idx + 1
                    break
            idx += 1
        else:
            self.errors.append("Could not find end of AGENTS array")
            return
            
        agents_str = content[agents_start:agents_end]
        
        try:
            ai_studio_agents = eval(agents_str)
            print(f"🔄 Importing {len(ai_studio_agents)} agents from AI Content Studio...")
            
            for agent_data in ai_studio_agents:
                try:
                    name = agent_data.get('name', 'Unknown Agent')
                    specialization = self.normalize_specialization(agent_data.get('specialization', 'general'))
                    
                    # Check for duplicates
                    if UnifiedAgentTemplate.objects.filter(creator=self.chris_user, name__iexact=name.lower().replace(' ', '-')).exists():
                        self.duplicates.append(f"AI Studio: {name}")
                        continue
                        
                    agent = UnifiedAgentTemplate.objects.create(
                        name=name.lower().replace(' ', '-').replace('_', '-'),
                        display_name=name,
                        description=agent_data.get('description', ''),
                        specialization=specialization,
                        capabilities=agent_data.get('capabilities', []),
                        creator=self.chris_user,
                        llm_provider='openai',
                        llm_model='gpt-5-mini',
                        is_active=True,
                        is_public=True
                    )
                    self.imported_agents.append(f"AI Studio: {agent.display_name}")
                    
                except Exception as e:
                    self.errors.append(f"Error importing AI Studio agent {name}: {e}")
                    
        except Exception as e:
            self.errors.append(f"Error parsing AI Studio agents: {e}")
            
    def import_donkey_betz_agents(self):
        """Import agents from main donkey_betz project"""
        # For now, we'll create a subset based on the agent-inventory.md
        # This would need manual extraction or a proper parser
        
        donkey_betz_sample_agents = [
            {"name": "Business Strategy Agent", "specialization": "business-development", "description": "Strategic business consultant expert in business model development"},
            {"name": "Market Research Agent", "specialization": "research", "description": "Comprehensive market research and analysis specialist"},
            {"name": "Financial Analyst Agent", "specialization": "financial", "description": "Advanced financial analysis and forecasting expert"},
            {"name": "Technical Implementation Agent", "specialization": "technical", "description": "Technical implementation and system architecture expert"},
            {"name": "Content Strategy Agent", "specialization": "content", "description": "Content strategy and marketing specialist"},
            {"name": "Risk Assessment Agent", "specialization": "risk-assessment", "description": "Comprehensive risk analysis and mitigation expert"},
            {"name": "Competitive Intelligence Agent", "specialization": "research", "description": "Competitive analysis and market intelligence specialist"},
            {"name": "Legal Compliance Agent", "specialization": "legal", "description": "Legal compliance and regulatory analysis expert"},
            {"name": "Creative Design Agent", "specialization": "creative", "description": "Creative design and brand strategy specialist"},
            {"name": "Marketing Growth Agent", "specialization": "marketing", "description": "Marketing strategy and growth optimization expert"}
        ]
        
        print(f"🔄 Importing {len(donkey_betz_sample_agents)} sample agents from Donkey Betz...")
        
        for agent_data in donkey_betz_sample_agents:
            try:
                name = agent_data.get('name', 'Unknown Agent')
                specialization = agent_data.get('specialization', 'general')
                
                # Check for duplicates
                if UnifiedAgentTemplate.objects.filter(creator=self.chris_user, name__iexact=name.lower().replace(' ', '-')).exists():
                    self.duplicates.append(f"Donkey Betz: {name}")
                    continue
                    
                agent = UnifiedAgentTemplate.objects.create(
                    name=name.lower().replace(' ', '-'),
                    display_name=name,
                    description=agent_data.get('description', ''),
                    specialization=specialization,
                    creator=self.chris_user,
                    llm_provider='openai',
                    llm_model='gpt-5-mini',
                    is_active=True,
                    is_public=True
                )
                self.imported_agents.append(f"Donkey Betz: {agent.display_name}")
                
            except Exception as e:
                self.errors.append(f"Error importing Donkey Betz agent {name}: {e}")
                
    def run_consolidation(self):
        """Execute the full consolidation process"""
        print("🚀 Starting Agent Consolidation Process...")
        print(f"👤 Target User: {self.chris_user.username}")
        
        initial_count = UnifiedAgentTemplate.objects.filter(creator=self.chris_user).count()
        print(f"📊 Initial agent count: {initial_count}")
        
        # Import from all three projects
        self.import_dbao_agents()
        self.import_ai_studio_agents()
        self.import_donkey_betz_agents()
        
        final_count = UnifiedAgentTemplate.objects.filter(creator=self.chris_user).count()
        
        # Print results
        print("\n" + "="*60)
        print("🎯 CONSOLIDATION RESULTS")
        print("="*60)
        print(f"📈 Total agents imported: {len(self.imported_agents)}")
        print(f"🔄 Initial count: {initial_count}")
        print(f"✅ Final count: {final_count}")
        print(f"➕ Net increase: {final_count - initial_count}")
        
        if self.duplicates:
            print(f"\n⚠️  Duplicates skipped ({len(self.duplicates)}):")
            for dup in self.duplicates[:10]:  # Show first 10
                print(f"   - {dup}")
            if len(self.duplicates) > 10:
                print(f"   ... and {len(self.duplicates) - 10} more")
                
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors[:5]:  # Show first 5
                print(f"   - {error}")
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more")
                
        print(f"\n✨ Successfully imported {len(self.imported_agents)} new agents!")
        
        # Show breakdown by specialization
        print("\n📊 Agent Breakdown by Specialization:")
        from collections import Counter
        agents = UnifiedAgentTemplate.objects.filter(creator=self.chris_user)
        specs = Counter([a.specialization for a in agents])
        for spec, count in specs.most_common():
            print(f"   {spec}: {count}")

if __name__ == "__main__":
    consolidator = AgentConsolidator()
    consolidator.run_consolidation()