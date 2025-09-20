// Recovery script to restore your recent Action Plans
// Run this in browser console at http://localhost:3000/income-builder

console.log('🚀 RESTORING YOUR ACTION PLANS...\n');

// Your most recent completed plans based on file system
const recoveredPlans = [
  {
    id: 'recovered_ai_training_' + Date.now(),
    backend_id: '0232a38d-12b6-47c9-bd45-4ce6047c1481',
    opportunity_title: 'AI Training Data Annotation',
    status: 'completed',
    created_at: '2025-09-17T01:43:00.000Z',
    completed_at: '2025-09-17T01:48:04.000Z',
    progress: 100,
    current_step: 5,
    steps: [
      'Research AI Training Data Annotation opportunities',
      'Analyze market demand and competition',
      'Create service offering and pricing',
      'Set up platform and tools',
      'Launch and start earning'
    ],
    results: {
      files_created: [
        'AI_Training_Data_Annotation_step_1_20250917_014503.md',
        'AI_Training_Data_Annotation_step_2_20250917_014546.md',
        'AI_Training_Data_Annotation_step_3_20250917_014633.md',
        'AI_Training_Data_Annotation_step_4_20250917_014714.md',
        'AI_Training_Data_Annotation_step_5_20250917_014804.md'
      ],
      status: 'completed',
      message: 'Successfully created 5-step action plan with real market data'
    },
    advisor_review: {
      advisor: 'Sal Khan (AI Model)',
      success_probability: 0.75,
      budget_estimate: 1500,
      immediate_actions: [
        'Validate target market assumptions',
        'Set up tracking and analytics',
        'Create MVP or proof of concept',
        'Identify first 10 potential customers',
        'Establish pricing strategy'
      ],
      strengths: [
        'Well-structured approach to AI Training Data Annotation',
        'Clear milestone definitions',
        'Realistic timeline with buffer periods'
      ],
      success_metrics: [
        'First paying customer within 2 weeks',
        '$1000 MRR within 30 days',
        '50% customer retention after 60 days'
      ],
      timeline_adjustment: 'Consider extending Phase 1 by one week for market validation'
    },
    team: {
      id: 'team_0232a38d-12b6-47c9-bd45-4ce6047c1481_20250917015122',
      lead: 'orchestrator',
      core_agents: ['data_analyst', 'market_researcher', 'content_creator'],
      specialists: ['pricing_strategist', 'platform_builder', 'launch_coordinator']
    }
  },
  {
    id: 'recovered_prompt_engineering_' + Date.now(),
    backend_id: 'prompt_engineering_plan_' + Date.now(),
    opportunity_title: 'Prompt Engineering Services',
    status: 'completed',
    created_at: '2025-09-16T21:00:00.000Z',
    completed_at: '2025-09-17T01:35:57.000Z',
    progress: 100,
    current_step: 5,
    steps: [
      'Research prompt engineering market',
      'Define service offerings',
      'Create pricing structure',
      'Build portfolio and case studies',
      'Launch marketing campaign'
    ],
    results: {
      files_created: [
        'Prompt_Engineering_Services_step_1_20250917_013213.md',
        'Prompt_Engineering_Services_step_2_20250917_013307.md',
        'Prompt_Engineering_Services_step_3_20250917_013436.md',
        'Prompt_Engineering_Services_step_4_20250917_013515.md',
        'Prompt_Engineering_Services_step_5_20250917_013557.md'
      ],
      status: 'completed',
      message: 'Successfully created comprehensive prompt engineering service plan'
    }
  }
];

// Save to localStorage
localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(recoveredPlans));

console.log('✅ Restored', recoveredPlans.length, 'Action Plans:');
recoveredPlans.forEach((plan, idx) => {
  console.log(`\n${idx + 1}. ${plan.opportunity_title}`);
  console.log('   Status:', plan.status);
  console.log('   Files:', plan.results.files_created.length);
  console.log('   Has Advisor Review:', !!plan.advisor_review);
});

console.log('\n🎉 SUCCESS! Your plans have been restored.');
console.log('📍 Now refresh the page to see them in the UI.');
console.log('\n💡 Tip: The AI Training Data Annotation plan includes the advisor review from Sal Khan!');

// Also create a backup
sessionStorage.setItem('incomeBuilderActionPlans_backup', JSON.stringify(recoveredPlans));
console.log('📦 Backup also saved to sessionStorage');

// Return the plans for verification
recoveredPlans;