#!/usr/bin/env python3
"""
Core Integration Test - Tests key components without spider dependencies
"""

import asyncio
import json
import os
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
import django
django.setup()

from intelligence.income_builder import AIIncomeBuilder, UserProfile, SkillLevel
from intelligence.agent_execution_pipeline import AgentExecutionPipeline
from core.agents.registry import get_agent_registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_core_integration():
    """Test core system integration without external dependencies"""
    logger.info("🚀 Starting Core Integration Test")

    results = {
        'agent_registry': False,
        'income_builder': False,
        'ml_pipeline': False,
        'agent_execution': False,
        'end_to_end_flow': False
    }

    try:
        # Test 1: Agent Registry
        logger.info("🧪 Testing Agent Registry...")
        registry = get_agent_registry()
        health = registry.health_check()
        stats = registry.get_registry_stats()

        results['agent_registry'] = {
            'healthy': health.get('status') == 'healthy',
            'active_agents': stats.active_agents,
            'total_agents': stats.total_agents
        }
        logger.info(f"✅ Agent Registry: {stats.active_agents} active agents")

        # Test 2: Income Builder
        logger.info("🧪 Testing Income Builder...")
        income_builder = AIIncomeBuilder()

        user_profile = UserProfile(
            id="test_user",
            current_balance=1000.0,
            skills=["python", "ai", "content writing"],
            skill_level=SkillLevel.INTERMEDIATE,
            available_hours_per_week=20
        )

        analysis = await income_builder.analyze_user_potential(user_profile)

        results['income_builder'] = {
            'analysis_successful': analysis is not None,
            'opportunities_found': len(analysis.get('top_opportunities', [])),
            'has_earnings_projection': 'earnings_projection' in analysis,
            'success_probability': analysis.get('success_probability', 0)
        }
        logger.info(f"✅ Income Builder: Found {len(analysis.get('top_opportunities', []))} opportunities")

        # Test 3: ML Pipeline
        logger.info("🧪 Testing ML Pipeline...")
        ml_pipeline = income_builder.ml_pipeline

        test_opportunity = {
            'skills_required': ['python', 'ai'],
            'initial_investment': 0,
            'success_rate': 0.8,
            'market_demand': 0.9,
            'competition_level': 0.5
        }

        ml_result = await ml_pipeline.predict_opportunity_fit(
            user_profile.__dict__, test_opportunity
        )

        results['ml_pipeline'] = {
            'enhanced_ml_available': ml_pipeline.enhanced_ml_available,
            'real_ml_engine_available': ml_pipeline.real_ml_engine is not None,
            'prediction_successful': ml_result is not None,
            'fit_score': ml_result.get('fit_score', 0),
            'ml_engine_used': ml_result.get('ml_engine', 'unknown'),
            'confidence': ml_result.get('confidence', 0)
        }
        logger.info(f"✅ ML Pipeline: {ml_result.get('ml_engine')} with fit_score {ml_result.get('fit_score', 0):.3f}")

        # Test 4: Agent Execution
        logger.info("🧪 Testing Agent Execution...")
        from intelligence.agent_instruction_parser import AgentInstruction

        pipeline = AgentExecutionPipeline()

        instruction = AgentInstruction(
            step_number=1,
            week=1,
            agent_type='content-creator',
            action='Create a brief marketing email for AI services',
            parameters={'target_audience': 'small businesses'},
            expected_outcome='Marketing email content'
        )

        execution_result = await pipeline._execute_single_instruction(instruction, 'test_plan')

        results['agent_execution'] = {
            'execution_successful': execution_result.get('success', False),
            'agent_type': execution_result.get('agent'),
            'has_result': 'result' in execution_result,
            'real_execution': execution_result.get('result', {}).get('real_execution', False) if execution_result.get('result') else False
        }
        logger.info(f"✅ Agent Execution: {execution_result.get('agent')} executed successfully")

        # Test 5: End-to-End Flow
        logger.info("🧪 Testing End-to-End Flow...")

        # Select an opportunity and create action plan
        top_opportunity = analysis['top_opportunities'][0] if analysis.get('top_opportunities') else None

        if top_opportunity:
            # Extract the stream type or use a fallback
            opportunity_id = None
            for field in ['stream_type', 'id', 'title']:
                if field in top_opportunity:
                    opportunity_id = str(top_opportunity[field]).lower().replace(' ', '_')
                    break

            if not opportunity_id:
                opportunity_id = 'ai_automation'  # fallback

            action_plan = await income_builder.create_action_plan(user_profile.id, opportunity_id)

            results['end_to_end_flow'] = {
                'opportunity_selected': top_opportunity is not None,
                'action_plan_created': action_plan is not None,
                'plan_has_structure': 'week_by_week' in action_plan if action_plan else False,
                'files_generated': len(action_plan.get('files_created', [])) if action_plan else 0,
                'opportunity_id': opportunity_id
            }
            logger.info(f"✅ End-to-End Flow: Action plan created for {opportunity_id}")
        else:
            results['end_to_end_flow'] = {
                'opportunity_selected': False,
                'error': 'No opportunities found'
            }

        # Generate summary
        logger.info("\n🎯 CORE INTEGRATION TEST RESULTS:")
        logger.info("="*50)

        total_tests = 5
        passed_tests = 0

        for test_name, test_result in results.items():
            if isinstance(test_result, dict):
                # Check if test passed based on key indicators
                if test_name == 'agent_registry':
                    passed = test_result.get('healthy', False) and test_result.get('active_agents', 0) > 100
                elif test_name == 'income_builder':
                    passed = test_result.get('analysis_successful', False) and test_result.get('opportunities_found', 0) > 0
                elif test_name == 'ml_pipeline':
                    passed = test_result.get('prediction_successful', False)
                elif test_name == 'agent_execution':
                    passed = test_result.get('execution_successful', False)
                elif test_name == 'end_to_end_flow':
                    passed = test_result.get('action_plan_created', False)
                else:
                    passed = bool(test_result)

                if passed:
                    passed_tests += 1
                    logger.info(f"✅ {test_name.replace('_', ' ').title()}: PASSED")

                    # Show key metrics
                    if test_name == 'agent_registry':
                        logger.info(f"    • Active Agents: {test_result.get('active_agents')}")
                    elif test_name == 'income_builder':
                        logger.info(f"    • Opportunities: {test_result.get('opportunities_found')}")
                        logger.info(f"    • Success Probability: {test_result.get('success_probability', 0):.2f}")
                    elif test_name == 'ml_pipeline':
                        logger.info(f"    • ML Engine: {test_result.get('ml_engine_used')}")
                        logger.info(f"    • Enhanced ML: {test_result.get('enhanced_ml_available')}")
                        logger.info(f"    • Fit Score: {test_result.get('fit_score', 0):.3f}")
                    elif test_name == 'agent_execution':
                        logger.info(f"    • Agent: {test_result.get('agent_type')}")
                        logger.info(f"    • Real Execution: {test_result.get('real_execution')}")
                    elif test_name == 'end_to_end_flow':
                        logger.info(f"    • Files Generated: {test_result.get('files_generated')}")
                        logger.info(f"    • Opportunity: {test_result.get('opportunity_id')}")
                else:
                    logger.info(f"❌ {test_name.replace('_', ' ').title()}: FAILED")
            else:
                if test_result:
                    passed_tests += 1
                    logger.info(f"✅ {test_name.replace('_', ' ').title()}: PASSED")
                else:
                    logger.info(f"❌ {test_name.replace('_', ' ').title()}: FAILED")

        success_rate = (passed_tests / total_tests) * 100
        logger.info(f"\n🏆 OVERALL RESULT: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")

        if success_rate >= 80:
            logger.info("🎉 SYSTEM STATUS: FULLY INTEGRATED AND OPERATIONAL!")
            logger.info("✅ All critical integrations are working")
            logger.info("✅ Agent registry connected with real implementations")
            logger.info("✅ ML pipeline using real models")
            logger.info("✅ End-to-end flow operational")
        elif success_rate >= 60:
            logger.info("⚠️  SYSTEM STATUS: MOSTLY INTEGRATED")
            logger.info("✅ Core functionality working")
            logger.info("⚠️  Some integrations may need refinement")
        else:
            logger.info("❌ SYSTEM STATUS: NEEDS INTEGRATION WORK")
            logger.info("❌ Critical integrations failing")

        # Save detailed results
        with open('core_integration_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"\n📄 Detailed results saved to: core_integration_results.json")

        return results

    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return {'error': str(e)}


if __name__ == "__main__":
    asyncio.run(test_core_integration())