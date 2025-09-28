"""
Phase 5 Integration Test Suite
Comprehensive testing for the Money-Making Pipeline

Tests all Phase 5 components working together:
- Opportunity scoring system
- Auto-application system
- Revenue tracking system
- A/B testing framework
- ROI measurement system

Run with: python tests/spiders/test_phase5_integration.py
"""

import asyncio
import sys
import os
import unittest
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Phase 5 imports
from ai_core.spiders.opportunity_scorer import (
    OpportunityScorer, opportunity_scorer
)
from ai_core.spiders.auto_apply import (
    AutoApplicationSystem, register_user_profile, process_user_opportunities,
    submit_user_applications, get_auto_application_stats, ProposalTemplate
)
from ai_core.spiders.revenue_tracker import (
    RevenueTracker, create_project_revenue, record_payment,
    update_project_phase, get_revenue_insights, ProjectPhase
)
from ai_core.spiders.ab_testing import (
    ABTestingFramework, create_ab_test, start_ab_test,
    assign_user_to_test, track_ab_conversion, get_ab_test_results
)
from ai_core.spiders.roi_calculator import (
    ROICalculator, calculate_overall_roi, add_system_cost,
    generate_comprehensive_roi_report, CostCategory
)


class TestPhase5Integration(unittest.TestCase):
    """Comprehensive Phase 5 integration tests"""

    def setUp(self):
        """Set up test environment"""
        print("\n🧪 Setting up Phase 5 Integration Test Environment...")

        # Initialize test data
        self.test_user_id = "test_user_001"
        self.test_client = "Acme Corp"

        # Sample opportunities for testing
        self.test_opportunities = [
            {
                'id': 'opp_001',
                'title': 'Full-Stack Django Developer',
                'description': 'Build a comprehensive web application using Django, React, and PostgreSQL',
                'budget': 5000.0,
                'duration': '6 weeks',
                'skills_required': ['Python', 'Django', 'React', 'PostgreSQL'],
                'company': 'Tech Startup Inc',
                'type': 'web_development',
                'remote': True,
                'urgency': 'high'
            },
            {
                'id': 'opp_002',
                'title': 'AI/ML Data Analysis Project',
                'description': 'Analyze large datasets and build predictive models for business insights',
                'budget': 3500.0,
                'duration': '4 weeks',
                'skills_required': ['Python', 'Machine Learning', 'Pandas', 'Scikit-learn'],
                'company': 'Data Solutions LLC',
                'type': 'data_science',
                'remote': True,
                'urgency': 'medium'
            },
            {
                'id': 'opp_003',
                'title': 'Mobile App Development',
                'description': 'Create a cross-platform mobile app using React Native',
                'budget': 4200.0,
                'duration': '8 weeks',
                'skills_required': ['React Native', 'JavaScript', 'Mobile Development'],
                'company': 'Mobile First Co',
                'type': 'mobile_development',
                'remote': True,
                'urgency': 'low'
            }
        ]

        # Test user profile
        self.test_profile = {
            'name': 'John Developer',
            'email': 'john@example.com',
            'skills': ['Python', 'Django', 'React', 'PostgreSQL', 'Machine Learning', 'JavaScript'],
            'experience_years': 5,
            'portfolio_url': 'https://johndeveloper.com',
            'resume_text': 'Experienced full-stack developer with 5 years in web and data science',
            'hourly_rate': 75.0,
            'availability': 'full-time',
            'certifications': ['AWS Certified', 'Django Professional'],
            'preferred_industries': ['tech', 'fintech', 'healthcare'],
            'bio': 'Passionate developer who loves solving complex problems'
        }

    async def test_1_opportunity_scoring_system(self):
        """Test opportunity scoring functionality"""
        print("\n🎯 Testing Opportunity Scoring System...")

        try:
            scorer = OpportunityScorer()

            # Test scoring individual opportunity
            opportunity = self.test_opportunities[0]
            user_profile = self.test_profile

            score_result = await scorer.score_opportunity(opportunity, user_profile)

            # Validate score structure (score_result is an OpportunityScore object)
            self.assertIsNotNone(score_result.total_score)
            self.assertIsNotNone(score_result.scores)
            self.assertIsNotNone(score_result.estimated_revenue)

            # Validate score range
            self.assertGreaterEqual(score_result.total_score, 0)
            self.assertLessEqual(score_result.total_score, 10)

            print(f"✅ Opportunity scored: {score_result.total_score:.1f}/10")
            print(f"   Revenue estimate: ${score_result.estimated_revenue:.2f}")

            # Test bulk scoring
            bulk_scores = await scorer.score_opportunities(self.test_opportunities, user_profile)
            self.assertEqual(len(bulk_scores), len(self.test_opportunities))

            print(f"✅ Bulk scoring completed: {len(bulk_scores)} opportunities")

            return True

        except Exception as e:
            print(f"❌ Opportunity scoring failed: {e}")
            return False

    async def test_2_auto_application_system(self):
        """Test auto-application system"""
        print("\n🤖 Testing Auto-Application System...")

        try:
            # Register user profile
            success = await register_user_profile(self.test_user_id, self.test_profile)
            self.assertTrue(success)
            print("✅ User profile registered")

            # Process opportunities and create applications
            applications = await process_user_opportunities(
                self.test_opportunities,
                self.test_user_id,
                min_score=0.1,  # Lower threshold for testing
                max_applications=3
            )

            self.assertGreater(len(applications), 0)
            print(f"✅ Created {len(applications)} applications")

            # Test application submission
            application_ids = [app.id for app in applications]
            submission_results = await submit_user_applications(application_ids[:2])

            successful_submissions = sum(1 for success in submission_results.values() if success)
            print(f"✅ Submitted {successful_submissions} applications successfully")

            # Get system statistics
            stats = get_auto_application_stats()
            self.assertIn('applications', stats)
            print(f"✅ Auto-application stats: {stats['applications']['total_created']} total created")

            return len(applications) > 0

        except Exception as e:
            print(f"❌ Auto-application system failed: {e}")
            return False

    async def test_3_revenue_tracking_system(self):
        """Test revenue tracking functionality"""
        print("\n💰 Testing Revenue Tracking System...")

        try:
            # Create revenue records for completed projects
            revenue_records = []

            for i, opportunity in enumerate(self.test_opportunities[:2]):
                record_id = await create_project_revenue(
                    application_id=f"app_00{i+1}",
                    user_id=self.test_user_id,
                    client_name=opportunity['company'],
                    project_title=opportunity['title'],
                    contract_value=opportunity['budget'],
                    hourly_rate=self.test_profile['hourly_rate'],
                    estimated_hours=opportunity['budget'] / self.test_profile['hourly_rate']
                )

                self.assertIsNotNone(record_id)
                revenue_records.append(record_id)
                print(f"✅ Created revenue record: ${opportunity['budget']}")

            # Test payment recording
            payment_success = await record_payment(
                revenue_records[0],
                2500.0,  # Partial payment
                datetime.now()
            )
            self.assertTrue(payment_success)
            print("✅ Recorded partial payment: $2,500")

            # Test project status updates
            status_success = await update_project_phase(
                revenue_records[0],
                ProjectPhase.COMPLETED,
                datetime.now(),
                8.5  # Client satisfaction score
            )
            self.assertTrue(status_success)
            print("✅ Updated project to completed status")

            # Generate revenue insights
            insights = await get_revenue_insights(self.test_user_id)
            self.assertIn('summary', insights)
            print(f"✅ Generated revenue insights for user")

            return len(revenue_records) > 0

        except Exception as e:
            print(f"❌ Revenue tracking failed: {e}")
            return False

    async def test_4_ab_testing_framework(self):
        """Test A/B testing functionality"""
        print("\n🧪 Testing A/B Testing Framework...")

        try:
            # Create A/B test experiment
            variants = [
                {
                    'name': 'Professional Template',
                    'type': 'control',
                    'is_control': True,
                    'traffic_allocation': 0.5,
                    'config': {'template': 'professional', 'tone': 'formal'},
                    'description': 'Standard professional proposal template'
                },
                {
                    'name': 'Creative Template',
                    'type': 'variant_a',
                    'is_control': False,
                    'traffic_allocation': 0.5,
                    'config': {'template': 'creative', 'tone': 'engaging'},
                    'description': 'Creative and engaging proposal template'
                }
            ]

            experiment_id = await create_ab_test(
                name="Proposal Template Test",
                description="Testing which proposal template generates better response rates",
                hypothesis="Creative templates will achieve higher response rates than professional templates",
                variants=variants,
                success_metric="response_rate",
                duration_days=14
            )

            self.assertIsNotNone(experiment_id)
            print(f"✅ Created A/B test experiment: {experiment_id[:8]}...")

            # Start experiment
            start_success = await start_ab_test(experiment_id)
            self.assertTrue(start_success)
            print("✅ Started A/B test experiment")

            # Assign test users and track conversions
            test_users = [f"user_{i:03d}" for i in range(20)]
            conversions = 0

            for user_id in test_users:
                # Assign user to variant
                variant_id = await assign_user_to_test(user_id, experiment_id)
                self.assertIsNotNone(variant_id)

                # Simulate some conversions (40% conversion rate)
                if hash(user_id) % 100 < 40:
                    conversion_success = await track_ab_conversion(
                        user_id,
                        experiment_id,
                        conversion_type="response",
                        revenue=1500.0,
                        metadata={'response_type': 'positive'}
                    )
                    if conversion_success:
                        conversions += 1

            print(f"✅ Assigned {len(test_users)} users, tracked {conversions} conversions")

            # Get experiment results
            results = await get_ab_test_results(experiment_id)
            self.assertIsNotNone(results)
            self.assertIn('variants', results)

            print(f"✅ Generated A/B test results: {len(results['variants'])} variants analyzed")

            return True

        except Exception as e:
            print(f"❌ A/B testing failed: {e}")
            return False

    async def test_5_roi_measurement_system(self):
        """Test ROI calculation and analysis"""
        print("\n📊 Testing ROI Measurement System...")

        try:
            # Add some system costs
            cost_records = []

            # Infrastructure costs
            cost_id1 = await add_system_cost(
                category="infrastructure",
                description="Server hosting for spider pool",
                amount=250.0,
                recurring=True
            )
            cost_records.append(cost_id1)

            # API usage costs
            cost_id2 = await add_system_cost(
                category="api_usage",
                description="External job board API calls",
                amount=180.0,
                recurring=True
            )
            cost_records.append(cost_id2)

            print(f"✅ Added {len(cost_records)} cost records")

            # Calculate system-wide ROI
            roi_analysis = await calculate_overall_roi(
                time_period_days=30,
                include_human_costs=False
            )

            self.assertIsNotNone(roi_analysis)
            self.assertIsInstance(roi_analysis.roi_percentage, float)

            print(f"✅ System ROI: {roi_analysis.roi_percentage:.2f}%")
            print(f"   Revenue: ${float(roi_analysis.total_revenue):.2f}")
            print(f"   Costs: ${float(roi_analysis.total_costs):.2f}")
            print(f"   Profit: ${float(roi_analysis.net_profit):.2f}")

            # Generate comprehensive ROI report
            roi_report = await generate_comprehensive_roi_report(
                time_period_days=30,
                include_breakdowns=True
            )

            self.assertIn('system_roi', roi_report)
            self.assertIn('efficiency_metrics', roi_report)
            self.assertIn('spider_breakdown', roi_report)

            print("✅ Generated comprehensive ROI report")

            # Validate key metrics
            if roi_analysis.roi_percentage > 0:
                print("✅ System is profitable!")
            else:
                print("⚠️ System needs optimization for profitability")

            return True

        except Exception as e:
            print(f"❌ ROI measurement failed: {e}")
            return False

    async def test_6_end_to_end_pipeline(self):
        """Test complete end-to-end revenue generation pipeline"""
        print("\n🚀 Testing End-to-End Revenue Pipeline...")

        try:
            pipeline_success = True

            # Step 1: Score opportunities
            print("Step 1: Scoring opportunities...")
            scorer = OpportunityScorer()
            scored_opps = await scorer.score_opportunities(self.test_opportunities, self.test_profile)

            if not scored_opps:
                print("❌ No opportunities scored")
                return False

            # Step 2: Auto-generate applications
            print("Step 2: Generating applications...")
            applications = await process_user_opportunities(
                self.test_opportunities,
                self.test_user_id,
                min_score=0.1,  # Lower threshold for testing
                max_applications=5
            )

            if not applications:
                print("❌ No applications generated")
                return False

            # Step 3: Submit applications (simulate)
            print("Step 3: Submitting applications...")
            app_ids = [app.id for app in applications[:2]]
            submissions = await submit_user_applications(app_ids)
            successful_submissions = sum(1 for success in submissions.values() if success)

            if successful_submissions == 0:
                print("❌ No applications submitted successfully")
                return False

            # Step 4: Track revenue (simulate project completion)
            print("Step 4: Tracking revenue...")
            revenue_id = await create_project_revenue(
                application_id=applications[0].id,
                user_id=self.test_user_id,
                client_name=self.test_client,
                project_title="End-to-End Pipeline Test Project",
                contract_value=4500.0,
                hourly_rate=75.0
            )

            if not revenue_id:
                print("❌ Failed to create revenue record")
                return False

            # Simulate payment
            payment_success = await record_payment(revenue_id, 4500.0)
            if not payment_success:
                print("❌ Failed to record payment")
                return False

            # Step 5: Calculate ROI
            print("Step 5: Calculating ROI...")
            final_roi = await calculate_overall_roi(time_period_days=30)

            if final_roi.roi_percentage == 0:
                print("⚠️ ROI calculation returned 0%")
            else:
                print(f"✅ Final pipeline ROI: {final_roi.roi_percentage:.2f}%")

            # Pipeline summary
            print(f"\n🎉 End-to-End Pipeline Summary:")
            print(f"   • Opportunities analyzed: {len(scored_opps)}")
            print(f"   • Applications created: {len(applications)}")
            print(f"   • Applications submitted: {successful_submissions}")
            print(f"   • Revenue tracked: $4,500")
            print(f"   • Final ROI: {final_roi.roi_percentage:.2f}%")

            return True

        except Exception as e:
            print(f"❌ End-to-end pipeline failed: {e}")
            return False

    async def run_all_tests(self):
        """Run all Phase 5 integration tests"""
        print("🚀 Starting Phase 5 Integration Test Suite")
        print("=" * 60)

        test_results = []

        # Run individual component tests
        tests = [
            ("Opportunity Scoring", self.test_1_opportunity_scoring_system()),
            ("Auto-Application", self.test_2_auto_application_system()),
            ("Revenue Tracking", self.test_3_revenue_tracking_system()),
            ("A/B Testing", self.test_4_ab_testing_framework()),
            ("ROI Measurement", self.test_5_roi_measurement_system()),
            ("End-to-End Pipeline", self.test_6_end_to_end_pipeline())
        ]

        for test_name, test_coro in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = await test_coro
                test_results.append((test_name, result))

                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")

            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                test_results.append((test_name, False))

        # Final results summary
        print("\n" + "=" * 60)
        print("🏁 PHASE 5 INTEGRATION TEST RESULTS")
        print("=" * 60)

        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)

        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:.<30} {status}")

        print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

        if passed == total:
            print("🎉 ALL TESTS PASSED! Phase 5 is ready for revenue generation!")
        elif passed >= total * 0.8:
            print("⚠️  Most tests passed. Minor issues need fixing before full deployment.")
        else:
            print("❌ Major issues detected. Phase 5 needs significant fixes.")

        return passed, total


async def main():
    """Main test execution"""
    try:
        # Create test instance and run all tests
        test_suite = TestPhase5Integration()
        test_suite.setUp()

        passed, total = await test_suite.run_all_tests()

        # Exit with appropriate code
        if passed == total:
            print(f"\n🚀 Phase 5 Money-Making Pipeline: READY FOR PRODUCTION!")
            exit(0)
        else:
            print(f"\n⚠️  Phase 5 needs attention: {total-passed} tests failed")
            exit(1)

    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        exit(2)


if __name__ == "__main__":
    # Run the async test suite
    asyncio.run(main())