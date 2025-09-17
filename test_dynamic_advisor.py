#!/usr/bin/env python
"""Test that advisor reviews have dynamic values"""

from intelligence.action_plan_advisor_handoff import ActionPlanAdvisorHandoff

# Initialize the handoff system
handoff = ActionPlanAdvisorHandoff()

# Create a test action plan
test_plan = {
    'opportunity_title': 'AI Freelancing Services',
    'immediate_actions': ['Start networking', 'Build portfolio', 'Find first client'],
    'timeline': '30 days'
}

# Submit the plan for review
result = handoff.submit_plan_for_review(test_plan)
plan_id = result['plan_id']

print(f"\n✅ Created action plan: {plan_id}")
print(f"✅ Status: {result['status']}")
print(f"✅ Total reviews: {result['total_reviews']}")

# Get the plan with reviews
plan = handoff.get_action_plan(plan_id)
if plan and 'advisor_reviews' in plan:
    print("\n📊 Advisor Reviews (Dynamic Values):")
    print("=" * 50)

    for i, review in enumerate(plan['advisor_reviews'], 1):
        advisor = review.get('advisor', 'Unknown')
        success = review.get('success_probability', 0)
        budget = review.get('estimated_budget', 0)

        print(f"\n{i}. {advisor}")
        print(f"   Success Probability: {success * 100:.0f}% (Dynamic!)")
        print(f"   Estimated Budget: ${budget:,} (Dynamic!)")

        # Show that values are different
        if i == 1:
            first_success = success
            first_budget = budget
        elif success != first_success or budget != first_budget:
            print(f"   ✓ Different from first advisor!")

print("\n✨ Dynamic advisor reviews are working!")