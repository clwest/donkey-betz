// Helper script to restore lost Action Plans from localStorage
// Run this in the browser console at http://localhost:3000/income-builder

console.log('🔍 Checking for saved Action Plans...\n');

function restorePlans() {
  const stored = localStorage.getItem('incomeBuilderActionPlans');

  if (!stored) {
    console.log('❌ No saved plans found in localStorage');
    console.log('\n💡 Tip: If you recently lost plans, try checking browser history or session storage');
    return null;
  }

  try {
    const plans = JSON.parse(stored);
    console.log('✅ Found', plans.length, 'saved plans in localStorage:\n');

    plans.forEach((plan, index) => {
      console.log(`${index + 1}. ${plan.opportunity_title || 'Untitled Plan'}`);
      console.log(`   - Status: ${plan.status}`);
      console.log(`   - Created: ${plan.created_at ? new Date(plan.created_at).toLocaleString() : 'Unknown'}`);
      console.log(`   - Has Advisor Review: ${!!plan.advisor_review}`);
      console.log(`   - Backend ID: ${plan.backend_id || 'none'}`);

      if (plan.results?.files_created?.length > 0) {
        console.log(`   - Files Generated: ${plan.results.files_created.length}`);
      }
      console.log('');
    });

    console.log('📋 Plans are in localStorage and should appear on page refresh.');
    console.log('If they\'re not showing, try:');
    console.log('1. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)');
    console.log('2. Clear React cache: Open DevTools > Application > Storage > Clear site data');
    console.log('3. Or manually trigger a state update (see below)\n');

    return plans;
  } catch (error) {
    console.error('❌ Error parsing stored plans:', error);
    console.log('🔧 Attempting to fix corrupted data...');

    // Try to recover what we can
    try {
      // Remove the corrupted data
      localStorage.removeItem('incomeBuilderActionPlans');
      console.log('✅ Cleared corrupted data. Please recreate your plans.');
    } catch (e) {
      console.error('Failed to clear corrupted data:', e);
    }

    return null;
  }
}

// Function to force React to load the plans
function forceLoadPlans() {
  const plans = restorePlans();

  if (plans && plans.length > 0) {
    // Try to trigger a React state update by dispatching a storage event
    window.dispatchEvent(new StorageEvent('storage', {
      key: 'incomeBuilderActionPlans',
      newValue: JSON.stringify(plans),
      url: window.location.href
    }));

    console.log('🚀 Triggered storage event to force React update');
    console.log('If plans still don\'t appear, refresh the page now.');
  }
}

// Check for backup in sessionStorage
function checkBackups() {
  const sessionBackup = sessionStorage.getItem('incomeBuilderActionPlans_backup');
  if (sessionBackup) {
    console.log('📦 Found backup in sessionStorage!');
    try {
      const backupPlans = JSON.parse(sessionBackup);
      console.log('   Backup contains', backupPlans.length, 'plans');
      return backupPlans;
    } catch (e) {
      console.error('   Backup is corrupted:', e);
    }
  }

  // Check IndexedDB for any cached data
  if (window.indexedDB) {
    console.log('🔍 Checking IndexedDB for cached data...');
    // This would require more complex code to properly check IndexedDB
  }

  return null;
}

// Main execution
console.log('=== ACTION PLAN RECOVERY TOOL ===\n');

const currentPlans = restorePlans();
const backupPlans = checkBackups();

if (!currentPlans || currentPlans.length === 0) {
  if (backupPlans && backupPlans.length > 0) {
    console.log('\n💡 Found backup plans! Restoring...');
    localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(backupPlans));
    console.log('✅ Restored', backupPlans.length, 'plans from backup');
    console.log('🔄 Please refresh the page now');
  } else {
    console.log('\n😔 No plans found in localStorage or backups');
    console.log('Unfortunately, the plans may have been lost.');
  }
} else {
  console.log('\n✅ Your plans are saved in localStorage');
  console.log('🔄 If they\'re not showing, try refreshing the page');
}

// Export recovery functions for manual use
window.planRecovery = {
  restore: restorePlans,
  forceLoad: forceLoadPlans,
  checkBackups: checkBackups,

  // Manual backup creation
  createBackup: function() {
    const stored = localStorage.getItem('incomeBuilderActionPlans');
    if (stored) {
      sessionStorage.setItem('incomeBuilderActionPlans_backup', stored);
      console.log('✅ Created backup in sessionStorage');
    } else {
      console.log('❌ No plans to backup');
    }
  },

  // Debug function to see all storage
  debugStorage: function() {
    console.log('\n=== STORAGE DEBUG ===');
    console.log('localStorage keys:', Object.keys(localStorage));
    console.log('sessionStorage keys:', Object.keys(sessionStorage));

    for (let key of Object.keys(localStorage)) {
      if (key.includes('income') || key.includes('action') || key.includes('plan')) {
        console.log(`\nFound related key: ${key}`);
        const value = localStorage.getItem(key);
        console.log('Value preview:', value ? value.substring(0, 100) + '...' : 'empty');
      }
    }
  }
};

console.log('\n📚 Recovery functions available:');
console.log('  window.planRecovery.restore()     - Check and restore plans');
console.log('  window.planRecovery.forceLoad()   - Force React to reload plans');
console.log('  window.planRecovery.createBackup() - Create backup of current plans');
console.log('  window.planRecovery.debugStorage() - Debug all storage');