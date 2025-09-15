// Quick script to simulate action plan progress
// Run this in your browser console while on the Income Builder page

function simulateActionPlanProgress() {
    // Get current plans from localStorage
    let plans = JSON.parse(localStorage.getItem('incomeBuilderActionPlans') || '[]');

    if (plans.length === 0) {
        console.log('No action plans found');
        return;
    }

    // Find in-progress plans
    const inProgressPlans = plans.map((plan, index) => ({ ...plan, index }))
        .filter(p => p.status === 'in_progress');

    if (inProgressPlans.length === 0) {
        console.log('No plans in progress. Start a plan first!');
        return;
    }

    console.log(`Simulating progress for ${inProgressPlans.length} plan(s)...`);

    // Simulate progress updates
    let progress = 0;
    const interval = setInterval(() => {
        progress += 10;

        // Update each in-progress plan
        inProgressPlans.forEach(plan => {
            plans[plan.index] = {
                ...plans[plan.index],
                progress: progress,
                currentStep: Math.floor(progress / 25) + 1,
                lastUpdate: new Date().toISOString()
            };
        });

        // Save to localStorage
        localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(plans));

        // Trigger storage event to update UI
        window.dispatchEvent(new Event('storage'));

        console.log(`Progress: ${progress}%`);

        if (progress >= 100) {
            clearInterval(interval);

            // Mark as completed
            inProgressPlans.forEach(plan => {
                plans[plan.index] = {
                    ...plans[plan.index],
                    status: 'completed',
                    completed_at: new Date().toISOString(),
                    progress: 100
                };
            });

            localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(plans));
            window.dispatchEvent(new Event('storage'));

            console.log('✅ Action plans completed!');
            console.log('Refresh the page to see the completed status.');
        }
    }, 2000); // Update every 2 seconds
}

// Run it
simulateActionPlanProgress();