#!/usr/bin/env python
"""
Complete Donkey Betz Agent Importer
Parses the full agent-inventory.md to extract all 74 agents with advanced deduplication
"""

import os
import sys
import django
import re
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from agents.models import UnifiedAgentTemplate

User = get_user_model()

class DonkeyBetzAgentParser:
    def __init__(self):
        self.chris_user = User.objects.get(username='chris')
        self.inventory_path = "/Users/donkeyking/development/donkey_betz/documentation/02-core-systems/agent-orchestra/agent-inventory.md"
        self.imported_agents = []
        self.duplicates = []
        self.errors = []
        self.existing_agents = set()
        
        # Load existing agents for deduplication
        existing = UnifiedAgentTemplate.objects.filter(creator=self.chris_user)
        self.existing_agents = set(agent.name.lower() for agent in existing)
        self.existing_display_names = set(agent.display_name.lower() for agent in existing)
        
    def normalize_agent_name(self, name):
        """Convert display name to database-friendly name"""
        return name.lower().replace(' ', '-').replace('&', 'and').replace('/', '-').replace('(', '').replace(')', '').replace(',', '').replace("'", '').strip('-')
        
    def is_duplicate(self, display_name, description=""):
        """Advanced duplicate detection"""
        normalized_name = self.normalize_agent_name(display_name)
        
        # Check exact name match
        if normalized_name in self.existing_agents:
            return True
            
        # Check display name similarity
        if display_name.lower() in self.existing_display_names:
            return True
            
        # Check for semantic duplicates
        semantic_duplicates = {
            'business agent': ['business-strategy-agent', 'business-development'],
            'research agent': ['research-assistant', 'research-specialist'],
            'content agent': ['content-creator', 'content-strategy-agent'],
            'financial agent': ['financial-analyst-agent', 'financial-analysis'],
            'technical agent': ['technical-implementation-agent', 'technical-specialist'],
            'marketing agent': ['marketing-growth-agent', 'marketing-specialist'],
            'legal agent': ['legal-compliance-agent', 'legal-specialist']
        }
        
        display_lower = display_name.lower()
        for key_term, variations in semantic_duplicates.items():
            if key_term in display_lower:
                for variation in variations:
                    if variation in self.existing_agents:
                        return True
                        
        return False
        
    def extract_specialization_from_category(self, category):
        """Map category headers to specializations"""
        category_map = {
            'Business Development': 'business-development',
            'Financial Analysis': 'financial',
            'Technical Analysis': 'technical',
            'Research & Analysis': 'research',
            'Marketing & Growth': 'marketing',
            'Content Creation': 'content',
            'Creative Design': 'creative',
            'Communication & Outreach': 'communication',
            'Career Development': 'career',
            'Legal & Compliance': 'legal',
            'Operational & Technical': 'operations'
        }
        return category_map.get(category, 'general')
        
    def parse_agent_inventory(self):
        """Parse the complete agent-inventory.md file"""
        if not os.path.exists(self.inventory_path):
            self.errors.append(f"Inventory file not found: {self.inventory_path}")
            return []
            
        with open(self.inventory_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        agents = []
        current_category = "general"
        
        # Split into sections by headers
        sections = re.split(r'\n## (.+?)\n', content)
        
        for i in range(1, len(sections), 2):  # Skip first empty section, then take pairs
            if i + 1 < len(sections):
                category_header = sections[i].strip()
                section_content = sections[i + 1]
                
                # Skip non-agent sections
                if any(skip in category_header.lower() for skip in ['overview', 'table of contents']):
                    continue
                    
                current_category = self.extract_specialization_from_category(category_header)
                
                # Extract individual agents from this section
                agent_blocks = re.split(r'\n### (.+?)\n', section_content)
                
                for j in range(1, len(agent_blocks), 2):
                    if j + 1 < len(agent_blocks):
                        agent_name = agent_blocks[j].strip()
                        agent_content = agent_blocks[j + 1]
                        
                        # Extract description (first line after name)
                        description_match = re.search(r'- \*\*Description\*\*: (.+?)(?:\n|$)', agent_content)
                        description = description_match.group(1) if description_match else f"Specialized {current_category} agent"
                        
                        # Extract capabilities
                        capabilities_match = re.search(r'- \*\*Capabilities\*\*: (.+?)(?:\n|$)', agent_content)
                        capabilities_str = capabilities_match.group(1) if capabilities_match else ""
                        capabilities = [cap.strip() for cap in capabilities_str.split(',') if cap.strip()] if capabilities_str else []
                        
                        # Extract tools
                        tools_match = re.search(r'- \*\*Required Tools\*\*: (.+?)(?:\n|$)', agent_content)
                        tools_str = tools_match.group(1) if tools_match else ""
                        tools = [tool.strip() for tool in tools_str.split(',') if tool.strip()] if tools_str else []
                        
                        # Extract LLM provider
                        llm_match = re.search(r'- \*\*LLM Provider\*\*: (.+?)(?:\n|$)', agent_content)
                        llm_info = llm_match.group(1) if llm_match else "OpenAI (gpt-4)"
                        llm_provider = "anthropic" if "anthropic" in llm_info.lower() or "claude" in llm_info.lower() else "openai"
                        llm_model = "gpt-5-mini" if "gpt-5-mini" in llm_info.lower() else "gpt-5-nano"
                        
                        agent_data = {
                            'name': agent_name,
                            'description': description,
                            'specialization': current_category,
                            'capabilities': capabilities,
                            'tools': tools,
                            'llm_provider': llm_provider,
                            'llm_model': llm_model
                        }
                        agents.append(agent_data)
                        
        return agents
        
    def import_all_agents(self):
        """Import all parsed agents"""
        agents = self.parse_agent_inventory()
        
        if not agents:
            self.errors.append("No agents found in inventory file")
            return
            
        print(f"🔍 Found {len(agents)} agents in donkey_betz inventory")
        print(f"📊 Current existing agents: {len(self.existing_agents)}")
        
        for agent_data in agents:
            try:
                display_name = agent_data['name']
                
                # Check for duplicates
                if self.is_duplicate(display_name, agent_data['description']):
                    self.duplicates.append(f"Donkey Betz: {display_name}")
                    continue
                    
                normalized_name = self.normalize_agent_name(display_name)
                
                # Create the agent
                agent = UnifiedAgentTemplate.objects.create(
                    name=normalized_name,
                    display_name=display_name,
                    description=agent_data['description'],
                    specialization=agent_data['specialization'],
                    capabilities=agent_data['capabilities'],
                    required_tools=agent_data.get('tools', []),
                    creator=self.chris_user,
                    llm_provider=agent_data['llm_provider'],
                    llm_model=agent_data['llm_model'],
                    is_active=True,
                    is_public=True,
                    confidence_score=0.85,  # High confidence for well-documented agents
                    success_rate=0.95
                )
                
                self.imported_agents.append(f"Donkey Betz: {agent.display_name}")
                self.existing_agents.add(normalized_name)  # Update for future duplicate checks
                self.existing_display_names.add(display_name.lower())
                
            except Exception as e:
                self.errors.append(f"Error importing agent {display_name}: {str(e)}")
                
    def run_import(self):
        """Execute the complete import process"""
        print("🚀 Starting Complete Donkey Betz Agent Import...")
        
        initial_count = UnifiedAgentTemplate.objects.filter(creator=self.chris_user).count()
        print(f"📊 Initial agent count: {initial_count}")
        
        self.import_all_agents()
        
        final_count = UnifiedAgentTemplate.objects.filter(creator=self.chris_user).count()
        
        # Print results
        print("\n" + "="*70)
        print("🎯 DONKEY BETZ IMPORT RESULTS")
        print("="*70)
        print(f"📈 New agents imported: {len(self.imported_agents)}")
        print(f"🔄 Initial count: {initial_count}")
        print(f"✅ Final count: {final_count}")
        print(f"➕ Net increase: {final_count - initial_count}")
        
        if self.duplicates:
            print(f"\n⚠️  Duplicates skipped ({len(self.duplicates)}):")
            for dup in self.duplicates[:15]:
                print(f"   - {dup}")
            if len(self.duplicates) > 15:
                print(f"   ... and {len(self.duplicates) - 15} more")
                
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors[:5]:
                print(f"   - {error}")
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more")
                
        print(f"\n✨ Successfully imported {len(self.imported_agents)} agents from donkey_betz!")
        
        # Show final breakdown
        print("\n📊 Final Agent Breakdown by Specialization:")
        from collections import Counter
        agents = UnifiedAgentTemplate.objects.filter(creator=self.chris_user)
        specs = Counter([a.specialization for a in agents])
        for spec, count in specs.most_common(15):
            print(f"   {spec}: {count}")
        
        if len(specs) > 15:
            print(f"   ... and {len(specs) - 15} more specializations")
            
        print(f"\n🎉 TOTAL UNIFIED PLATFORM AGENTS: {final_count}")

if __name__ == "__main__":
    parser = DonkeyBetzAgentParser()
    parser.run_import()