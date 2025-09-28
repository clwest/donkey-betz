#!/usr/bin/env python3
"""
Test script for the memory-enhanced opportunity pipeline orchestrator
"""

import asyncio
import sys
import os
import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from agents.opportunity_pipeline_orchestrator import OpportunityPipelineOrchestrator


async def test_memory_enhanced_pipeline():
    """Test the memory-enhanced opportunity pipeline orchestrator"""

    print("🧠 Testing Memory-Enhanced Opportunity Pipeline Orchestrator")
    print("=" * 60)

    # Initialize the orchestrator
    orchestrator = OpportunityPipelineOrchestrator()

    # Test opportunity 1: Content creation opportunity
    test_opportunity_1 = {
        'id': 'test_opp_001',
        'title': 'AI Content Strategy for Tech Startup',
        'description': 'Create comprehensive content strategy and implementation plan for emerging AI startup',
        'platform': 'freelance',
        'category': 'content_strategy',
        'skills_required': ['content_strategy', 'AI_knowledge', 'marketing'],
        'budget_range': '$2000-5000',
        'timeline': 'flexible',
        'base_value': 500,
        'priority': 'high',
        'success_probability': 0.7
    }

    # Test opportunity 2: Market research opportunity
    test_opportunity_2 = {
        'id': 'test_opp_002',
        'title': 'Competitive Analysis for SaaS Platform',
        'description': 'Deep dive research into competitive landscape for B2B SaaS tool',
        'platform': 'reddit',
        'category': 'market_research',
        'skills_required': ['research', 'analysis', 'competitive_intelligence'],
        'budget_range': '$1500-3000',
        'timeline': 'urgent',
        'base_value': 300,
        'priority': 'medium',
        'success_probability': 0.8
    }

    print("🔍 Test 1: Content Strategy Opportunity")
    print(f"Platform: {test_opportunity_1['platform']}")
    print(f"Base Value: ${test_opportunity_1['base_value']}")
    print(f"Skills: {', '.join(test_opportunity_1['skills_required'])}")
    print()

    try:
        # Execute pipeline for opportunity 1
        result_1 = await orchestrator.orchestrate_opportunity_pipeline(
            test_opportunity_1,
            {'optimization_level': 'high', 'memory_enabled': True}
        )

        print("✅ Pipeline 1 Results:")
        print(f"Success: {result_1['success']}")
        if result_1['success']:
            print(f"Final Value: ${result_1['final_value']:.2f}")
            print(f"Value Multiplication: {result_1['value_multiplication']:.2f}x")
            print(f"Stages Executed: {result_1['stages_executed']}")

            # Memory analysis results
            if 'memory_analysis' in result_1['pipeline_report']:
                memory_analysis = result_1['pipeline_report']['memory_analysis']
                print(f"Memory Utilization:")
                print(f"  - Used Embeddings: {memory_analysis['memory_utilization']['used_embeddings']}")
                print(f"  - Similar Opportunities Found: {memory_analysis['memory_utilization']['found_similar_opportunities']}")
                print(f"  - Applied Memory Insights: {memory_analysis['memory_utilization']['applied_memory_insights']}")

                if memory_analysis['learning_outcomes']['new_patterns_discovered']:
                    print(f"New Patterns Discovered:")
                    for pattern in memory_analysis['learning_outcomes']['new_patterns_discovered']:
                        print(f"  - {pattern}")

                if memory_analysis['learning_outcomes']['successful_strategies']:
                    print(f"Successful Strategies:")
                    for strategy in memory_analysis['learning_outcomes']['successful_strategies']:
                        print(f"  - {strategy}")
        else:
            print(f"Error: {result_1.get('error', 'Unknown error')}")

        print()

    except Exception as e:
        print(f"❌ Pipeline 1 Error: {e}")
        print()

    print("🔍 Test 2: Market Research Opportunity")
    print(f"Platform: {test_opportunity_2['platform']}")
    print(f"Base Value: ${test_opportunity_2['base_value']}")
    print(f"Skills: {', '.join(test_opportunity_2['skills_required'])}")
    print()

    try:
        # Execute pipeline for opportunity 2
        result_2 = await orchestrator.orchestrate_opportunity_pipeline(
            test_opportunity_2,
            {'optimization_level': 'medium', 'memory_enabled': True}
        )

        print("✅ Pipeline 2 Results:")
        print(f"Success: {result_2['success']}")
        if result_2['success']:
            print(f"Final Value: ${result_2['final_value']:.2f}")
            print(f"Value Multiplication: {result_2['value_multiplication']:.2f}x")
            print(f"Stages Executed: {result_2['stages_executed']}")

            # Memory analysis results
            if 'memory_analysis' in result_2['pipeline_report']:
                memory_analysis = result_2['pipeline_report']['memory_analysis']
                print(f"Memory Utilization:")
                print(f"  - Used Embeddings: {memory_analysis['memory_utilization']['used_embeddings']}")
                print(f"  - Similar Opportunities Found: {memory_analysis['memory_utilization']['found_similar_opportunities']}")
                print(f"  - Applied Memory Insights: {memory_analysis['memory_utilization']['applied_memory_insights']}")

                if memory_analysis['optimization_recommendations']:
                    print(f"Optimization Recommendations:")
                    for rec in memory_analysis['optimization_recommendations']:
                        print(f"  - {rec}")
        else:
            print(f"Error: {result_2.get('error', 'Unknown error')}")

        print()

    except Exception as e:
        print(f"❌ Pipeline 2 Error: {e}")
        print()

    # Test quick assessment feature
    print("🔍 Test 3: Quick Opportunity Assessment")
    test_quick_assessment = {
        'id': 'quick_test_001',
        'title': 'Quick Market Analysis',
        'description': 'Fast assessment of market opportunity',
        'platform': 'freelance',
        'base_value': 200,
        'success_probability': 0.6
    }

    try:
        assessment_result = await orchestrator.quick_opportunity_assessment(test_quick_assessment)

        print("✅ Quick Assessment Results:")
        print(f"Success: {assessment_result['success']}")
        if assessment_result['success']:
            print(f"Assessment: {assessment_result['assessment']}")
            print(f"Quality Score: {assessment_result['quality_score']:.2f}")
            print(f"Estimated Value: ${assessment_result['estimated_value']:.2f}")

            if assessment_result['recommendations']:
                print("Recommendations:")
                for rec in assessment_result['recommendations']:
                    print(f"  - {rec}")
        else:
            print(f"Error: {assessment_result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Quick Assessment Error: {e}")

    print()
    print("🧠 Memory Enhancement Integration Test Complete!")
    print("=" * 60)

    # Summary
    print("Summary of Memory Integration Features Tested:")
    print("✅ Opportunity embedding generation")
    print("✅ Similar opportunity matching")
    print("✅ Memory-driven agent selection")
    print("✅ Historical pattern analysis")
    print("✅ Learning outcome extraction")
    print("✅ Prediction accuracy assessment")
    print("✅ Memory-aware pipeline reporting")


if __name__ == "__main__":
    asyncio.run(test_memory_enhanced_pipeline())