// Test script to verify localStorage persistence for Income Builder
// Run this in the browser console at http://localhost:3000/income-builder

console.log('🧪 Testing localStorage persistence for Income Builder...\n');

// Function to check localStorage
function checkLocalStorage() {
  const stored = localStorage.getItem('incomeBuilderActionPlans');
  if (stored) {
    try {
      const plans = JSON.parse(stored);
      console.log('✅ Found', plans.length, 'action plans in localStorage:');
      plans.forEach((plan, index) => {
        console.log(`  ${index + 1}. ${plan.opportunity_title || 'Untitled'}`);
        console.log(`     - Status: ${plan.status}`);
        console.log(`     - Has Advisor Review: ${!!plan.advisor_review}`);
        if (plan.advisor_review) {
          console.log(`     - Advisor: ${plan.advisor_review.advisor}`);
          console.log(`     - Success Probability: ${(plan.advisor_review.success_probability * 100).toFixed(0)}%`);
        }
        console.log(`     - Backend ID: ${plan.backend_id || 'none'}`);
      });
      return plans;
    } catch (error) {
      console.error('❌ Error parsing localStorage data:', error);
      return null;
    }
  } else {
    console.log('⚠️ No action plans found in localStorage');
    return [];
  }
}

// Function to simulate adding a test plan
function addTestPlan() {
  const testPlan = {
    id: `test-${Date.now()}`,
    opportunity_title: 'Test Plan - ' + new Date().toLocaleString(),
    status: 'completed',
    created_at: new Date().toISOString(),
    steps: [
      { step: 1, description: 'Test step 1' },
      { step: 2, description: 'Test step 2' }
    ],
    advisor_review: null,
    backend_id: null
  };

  const stored = localStorage.getItem('incomeBuilderActionPlans');
  const plans = stored ? JSON.parse(stored) : [];
  plans.push(testPlan);
  localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(plans));
  console.log('✅ Added test plan:', testPlan.opportunity_title);
  return testPlan;
}

// Function to simulate advisor review
function addAdvisorReviewToLastPlan() {
  const stored = localStorage.getItem('incomeBuilderActionPlans');
  if (!stored) {
    console.error('❌ No plans found to add advisor review');
    return;
  }

  const plans = JSON.parse(stored);
  if (plans.length === 0) {
    console.error('❌ No plans available');
    return;
  }

  const lastPlan = plans[plans.length - 1];
  lastPlan.advisor_review = {
    advisor: 'Test Advisor',
    success_probability: 0.75,
    budget_estimate: 2500,
    immediate_actions: [
      'Validate target market',
      'Set up tracking',
      'Create MVP'
    ],
    success_metrics: [
      'First customer in 2 weeks',
      '$1000 MRR in 30 days'
    ],
    timeline_adjustment: 'Consider extending timeline to 6 weeks for better results'
  };
  lastPlan.status = 'reviewed';

  localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(plans));
  console.log('✅ Added advisor review to plan:', lastPlan.opportunity_title);
  return lastPlan;
}

// Function to clear test data
function clearTestPlans() {
  const stored = localStorage.getItem('incomeBuilderActionPlans');
  if (stored) {
    const plans = JSON.parse(stored);
    const filtered = plans.filter(p => !p.id.startsWith('test-'));
    localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(filtered));
    console.log('✅ Removed test plans. Remaining plans:', filtered.length);
  }
}

// Run tests
console.log('📊 Current State:');
checkLocalStorage();

console.log('\n🧪 Test Commands Available:');
console.log('  checkLocalStorage()       - Check current localStorage state');
console.log('  addTestPlan()            - Add a test plan');
console.log('  addAdvisorReviewToLastPlan() - Add advisor review to last plan');
console.log('  clearTestPlans()         - Remove all test plans');

console.log('\n💡 To test persistence:');
console.log('  1. Run addTestPlan() to create a test plan');
console.log('  2. Refresh the page');
console.log('  3. Check if the plan appears in the UI');
console.log('  4. Run checkLocalStorage() to verify it persisted');

// Export functions to global scope for console access
window.testPersistence = {
  check: checkLocalStorage,
  addPlan: addTestPlan,
  addReview: addAdvisorReviewToLastPlan,
  clearTest: clearTestPlans
};

console.log('\n✅ Test functions available as window.testPersistence.*');