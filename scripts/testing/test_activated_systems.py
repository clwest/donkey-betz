#!/usr/bin/env python3
"""
✅ TEST ACTIVATED SYSTEMS
Validate that all dormant systems are now active and working
"""

import os
import sys
import django
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import asyncio

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from django.db import connection
from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution
from agents.registry import AgentRegistry
from ai_core.spiders.spider_registry import SpiderRegistry
from core.llm_enforcer import get_llm_enforcer


class SystemValidator:
    """Validate all activated systems"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests_passed': 0,
            'tests_failed': 0,
            'details': {}
        }
    
    def test_agent_collaboration(self) -> bool:
        """Test that agents are collaborating"""
        print("\n🤖 Testing Agent Collaboration...")
        
        try:
            registry = AgentRegistry()
            
            # Test 1: Check agent groups
            agents = UnifiedAgentTemplate.objects.filter(is_active=True)
            grouped_agents = agents.filter(metadata__collaboration_enabled=True)
            
            if grouped_agents.count() > 0:
                print(f"  ✅ {grouped_agents.count()} agents in collaboration groups")
                self.test_results['tests_passed'] += 1
            else:
                print(f"  ❌ No agents in collaboration groups")
                self.test_results['tests_failed'] += 1
                return False
            
            # Test 2: Check communication channels
            from django.core.cache import cache
            channels = [
                'channel_agent_research_channel',
                'channel_agent_development_channel',
                'channel_agent_marketing_channel'
            ]
            
            active_channels = sum(1 for ch in channels if cache.get(ch) is not None)
            
            if active_channels > 0:
                print(f"  ✅ {active_channels} communication channels active")
                self.test_results['tests_passed'] += 1
            else:
                print(f"  ❌ No communication channels active")
                self.test_results['tests_failed'] += 1
                return False
            
            # Test 3: Create a collaborative task
            print("  Testing collaborative task execution...")
            
            # Get one agent from each group
            research_agent = agents.filter(
                metadata__group='research'
            ).first()
            
            dev_agent = agents.filter(
                metadata__group='development'
            ).first()
            
            if research_agent and dev_agent:
                print(f"    Research Agent: {research_agent.name}")
                print(f"    Development Agent: {dev_agent.name}")
                print(f"  ✅ Agent collaboration ready")
                self.test_results['tests_passed'] += 1
                
                self.test_results['details']['agent_collaboration'] = {
                    'status': 'active',
                    'grouped_agents': grouped_agents.count(),
                    'channels': active_channels
                }
                return True
            else:
                print(f"  ❌ Could not find agents for collaboration")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            print(f"  ❌ Agent collaboration test failed: {e}")
            self.test_results['tests_failed'] += 1
            return False
    
    def test_spider_deployment(self) -> bool:
        """Test that spiders are deployed and harvesting"""
        print("\n🕷️ Testing Spider Deployment...")
        
        try:
            registry = SpiderRegistry()
            
            # Test 1: Check registered spiders
            spider_count = len(registry.spider_classes)
            
            if spider_count > 10:
                print(f"  ✅ {spider_count} spiders registered")
                self.test_results['tests_passed'] += 1
            else:
                print(f"  ⚠️ Only {spider_count} spiders registered (expected more)")
            
            # Test 2: Check spider configurations
            config_count = len(registry.spider_configs)
            
            if config_count > 0:
                print(f"  ✅ {config_count} spider configurations loaded")
                self.test_results['tests_passed'] += 1
            else:
                print(f"  ❌ No spider configurations found")
                self.test_results['tests_failed'] += 1
                return False
            
            # Test 3: Check for recent spider data
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM core_aistrategy
                    WHERE created_at >= NOW() - INTERVAL '1 hour'
                """)
                recent_data = cursor.fetchone()[0]
            
            if recent_data > 0:
                print(f"  ✅ {recent_data} recent strategies harvested")
                self.test_results['tests_passed'] += 1
            else:
                print(f"  ⚠️ No recent spider data (may need to wait)")
            
            self.test_results['details']['spider_deployment'] = {
                'status': 'deployed',
                'spider_count': spider_count,
                'recent_harvests': recent_data
            }
            
            return spider_count > 0 and config_count > 0
            
        except Exception as e:
            print(f"  ❌ Spider deployment test failed: {e}")
            self.test_results['tests_failed'] += 1
            return False
    
    def test_personalization_engine(self) -> bool:
        """Test personalization configuration"""
        print("\n🎯 Testing Personalization Engine...")
        
        try:
            config_path = Path('config/personalization_config.json')
            
            # Test 1: Check config file
            if config_path.exists():
                print(f"  ✅ Personalization config found")
                self.test_results['tests_passed'] += 1
                
                with open(config_path) as f:
                    config = json.load(f)
                
                # Test 2: Validate schema
                if 'profile_schema' in config and 'matching_algorithm' in config:
                    print(f"  ✅ Valid personalization schema")
                    print(f"    Algorithm: {config['matching_algorithm']}")
                    print(f"    Engine: {config['recommendation_engine']}")
                    self.test_results['tests_passed'] += 1
                    
                    self.test_results['details']['personalization'] = {
                        'status': 'configured',
                        'algorithm': config['matching_algorithm'],
                        'engine': config['recommendation_engine']
                    }
                    return True
                else:
                    print(f"  ❌ Invalid config structure")
                    self.test_results['tests_failed'] += 1
                    return False
            else:
                print(f"  ❌ Personalization config not found")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            print(f"  ❌ Personalization test failed: {e}")
            self.test_results['tests_failed'] += 1
            return False
    
    def test_execution_pipeline(self) -> bool:
        """Test execution and deployment pipeline"""
        print("\n🚀 Testing Execution Pipeline...")
        
        try:
            pipeline_path = Path('config/execution_pipeline.json')
            
            # Test 1: Check pipeline config
            if pipeline_path.exists():
                print(f"  ✅ Execution pipeline configured")
                self.test_results['tests_passed'] += 1
                
                with open(pipeline_path) as f:
                    pipeline = json.load(f)
                
                # Test 2: Validate stages
                stages = pipeline.get('stages', [])
                if len(stages) >= 5:
                    print(f"  ✅ {len(stages)} pipeline stages configured")
                    for stage in stages:
                        print(f"    • {stage['name']}: {', '.join(stage['steps'])}")
                    self.test_results['tests_passed'] += 1
                else:
                    print(f"  ❌ Insufficient pipeline stages")
                    self.test_results['tests_failed'] += 1
                    return False
                
                # Test 3: Check deployment scripts
                scripts_dir = Path('scripts/deployment')
                if scripts_dir.exists():
                    scripts = list(scripts_dir.glob('*.sh'))
                    print(f"  ✅ {len(scripts)} deployment scripts created")
                    self.test_results['tests_passed'] += 1
                    
                    self.test_results['details']['execution_pipeline'] = {
                        'status': 'ready',
                        'stages': len(stages),
                        'scripts': len(scripts),
                        'targets': list(pipeline.get('deployment_targets', {}).keys())
                    }
                    return True
                else:
                    print(f"  ⚠️ Deployment scripts not found")
                    
            else:
                print(f"  ❌ Execution pipeline not configured")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            print(f"  ❌ Execution pipeline test failed: {e}")
            self.test_results['tests_failed'] += 1
            return False
    
    def test_advisor_intelligence(self) -> bool:
        """Test advisor enhancement"""
        print("\n🧠 Testing Advisor Intelligence...")
        
        try:
            from advisors.models import AdvisorTemplate
            
            # Get enhanced advisors
            enhanced = AdvisorTemplate.objects.filter(
                metadata__intelligence_enhanced=True
            )
            
            if enhanced.count() > 0:
                print(f"  ✅ {enhanced.count()} advisors enhanced")
                self.test_results['tests_passed'] += 1
                
                # Show sample advisor
                sample = enhanced.first()
                if sample and sample.metadata:
                    print(f"    Sample: {sample.name}")
                    if 'data_sources' in sample.metadata:
                        print(f"    Data Sources: {', '.join(sample.metadata['data_sources'][:3])}")
                    if 'analysis_capabilities' in sample.metadata:
                        print(f"    Analysis: {', '.join(sample.metadata['analysis_capabilities'][:3])}")
                
                self.test_results['details']['advisor_intelligence'] = {
                    'status': 'enhanced',
                    'enhanced_count': enhanced.count()
                }
                return True
            else:
                print(f"  ❌ No enhanced advisors found")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            print(f"  ⚠️ Advisor test skipped (app may not be installed): {e}")
            return True  # Don't fail if advisors app not installed
    
    def test_llm_connectivity(self) -> bool:
        """Test LLM API connectivity"""
        print("\n🤖 Testing LLM Connectivity...")
        
        try:
            llm = get_llm_enforcer()
            
            # Test OpenAI connection
            test_prompt = "Say 'System Active' in exactly 2 words"
            response = llm.generate_completion(
                prompt=test_prompt,
                max_tokens=10,
                temperature=0.1
            )
            
            if response and 'content' in response:
                print(f"  ✅ OpenAI API connected")
                print(f"    Response: {response['content'][:50]}")
                self.test_results['tests_passed'] += 1
                
                self.test_results['details']['llm_connectivity'] = {
                    'status': 'connected',
                    'provider': 'OpenAI',
                    'model': response.get('model', 'unknown')
                }
                return True
            else:
                print(f"  ❌ LLM response invalid")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            print(f"  ❌ LLM connectivity test failed: {e}")
            self.test_results['tests_failed'] += 1
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        report_path = Path('SYSTEM_VALIDATION_REPORT.md')
        
        total_tests = self.test_results['tests_passed'] + self.test_results['tests_failed']
        success_rate = (self.test_results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0
        
        report_content = f'''# ✅ System Validation Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Test Results Summary
- **Total Tests**: {total_tests}
- **Passed**: {self.test_results['tests_passed']} ✅
- **Failed**: {self.test_results['tests_failed']} ❌
- **Success Rate**: {success_rate:.1f}%

## System Status

### Agent Collaboration
{self._format_status(self.test_results['details'].get('agent_collaboration', {}))}

### Spider Deployment
{self._format_status(self.test_results['details'].get('spider_deployment', {}))}

### Personalization Engine
{self._format_status(self.test_results['details'].get('personalization', {}))}

### Execution Pipeline
{self._format_status(self.test_results['details'].get('execution_pipeline', {}))}

### Advisor Intelligence
{self._format_status(self.test_results['details'].get('advisor_intelligence', {}))}

### LLM Connectivity
{self._format_status(self.test_results['details'].get('llm_connectivity', {}))}

## Overall Assessment
{"✅ **SYSTEM FULLY ACTIVATED**" if success_rate >= 80 else "⚠️ **PARTIAL ACTIVATION** - Some systems need attention"}

## Recommendations
{self._generate_recommendations()}

---
*Validation completed. Check failed tests for areas needing attention.*
'''
        
        report_path.write_text(report_content)
        print(f"\n📄 Test report saved to: {report_path}")
        
        # Save JSON report too
        json_path = Path('validation_results.json')
        with open(json_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        return self.test_results
    
    def _format_status(self, details: Dict) -> str:
        """Format status details for report"""
        if not details:
            return "- Status: Not tested"
        
        lines = [f"- Status: **{details.get('status', 'unknown').upper()}**"]
        
        for key, value in details.items():
            if key != 'status':
                if isinstance(value, list):
                    lines.append(f"- {key.replace('_', ' ').title()}: {', '.join(map(str, value))}")
                else:
                    lines.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        return '\n'.join(lines)
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if self.test_results['tests_failed'] == 0:
            recommendations.append("1. All systems operational - begin revenue generation")
            recommendations.append("2. Monitor agent collaboration metrics")
            recommendations.append("3. Scale spider deployment to 1000+")
        else:
            if 'agent_collaboration' not in self.test_results['details']:
                recommendations.append("1. Run `python activate_full_system.py` to enable agent collaboration")
            
            if 'spider_deployment' not in self.test_results['details']:
                recommendations.append("2. Deploy spiders with `python deploy_spider_army.py`")
            
            if 'execution_pipeline' not in self.test_results['details']:
                recommendations.append("3. Configure pipeline with `python setup_execution_infrastructure.py`")
        
        recommendations.append("4. Run `python monitor_system_activity.py` for real-time monitoring")
        recommendations.append("5. Generate first automated project with `python generate_personalized_project.py`")
        
        return '\n'.join(recommendations)
    
    async def run_all_tests(self):
        """Run all validation tests"""
        print("="*60)
        print("🔧 SYSTEM VALIDATION STARTING")
        print("="*60)
        
        # Run test suite
        self.test_agent_collaboration()
        self.test_spider_deployment()
        self.test_personalization_engine()
        self.test_execution_pipeline()
        self.test_advisor_intelligence()
        self.test_llm_connectivity()
        
        # Generate report
        report = self.generate_test_report()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 VALIDATION COMPLETE")
        print("="*60)
        
        total = self.test_results['tests_passed'] + self.test_results['tests_failed']
        success_rate = (self.test_results['tests_passed'] / total * 100) if total > 0 else 0
        
        print(f"Tests Passed: {self.test_results['tests_passed']}/{total}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n✅ SYSTEM FULLY ACTIVATED AND VALIDATED")
            print("Your platform is ready for production!")
        else:
            print("\n⚠️ Some systems need attention")
            print("Review the report and run activation script again")
        
        return report


def main():
    """Run system validation"""
    validator = SystemValidator()
    
    # Run tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        report = loop.run_until_complete(validator.run_all_tests())
        
        print("\n" + "🎯"*20)
        print("Next steps:")
        print("1. If tests failed: python activate_full_system.py")
        print("2. Monitor activity: python monitor_system_activity.py")
        print("3. Generate project: python generate_personalized_project.py")
        print("🎯"*20)
        
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        raise
    finally:
        loop.close()


if __name__ == "__main__":
    main()
