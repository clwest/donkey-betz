// Clear action plans from localStorage
console.log('🧹 Clearing action plans from localStorage...');

// Clear the action plans
localStorage.removeItem('incomeBuilderActionPlans');

// Check if it's cleared
const remaining = localStorage.getItem('incomeBuilderActionPlans');
if (!remaining) {
  console.log('✅ Action plans cleared successfully!');
} else {
  console.log('⚠️ Action plans still present:', remaining);
}

// Show all localStorage keys
console.log('\n📦 All localStorage keys:');
for (let i = 0; i < localStorage.length; i++) {
  const key = localStorage.key(i);
  console.log(`  - ${key}`);
}

console.log('\n🔄 Refresh the page to see the changes!');