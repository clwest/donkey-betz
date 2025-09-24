#!/usr/bin/env python
"""
Fix Agent Name Mappings
=======================
This script updates the agent name mappings in proper_agent_executor.py
to map the failing theoretical agents to available registry agents.
"""

# Successful agents (confirmed in test results)
WORKING_MAPPINGS = {
    'business_agent': 'business_agent',
    'brand_strategist': 'brand_guidelines_agent',
    'computer_vision_expert': 'image_video_pipeline',
    'data_analyst': 'data_analyst',
    'data_scientist': 'data_analyst',
    'deep_learning_expert': 'ml_pipeline',
    'devops_engineer': 'devops_engineer',
    'financial_analyst': 'financial_analyst',
    'ml_engineer': 'ml_pipeline',
    'ml_recommendation_engine': 'ml_pipeline',
    'market_research_specialist': 'market_research_specialist',
    'marketing_strategist': 'marketing_agent',
    'nlp_specialist': 'rag_specialist',
    'prompt_engineer': 'prompt_engineer',
    'react_developer': 'react_developer',
    'reinforcement_learning_expert': 'ml_pipeline',
}

# Failed agents mapped to available registry agents
FAILING_AGENT_MAPPINGS = {
    '3d_designer': 'creative_design_agent',
    '5g_specialist': 'technical_agent',
    'ai_ethicist': 'legal_compliance_agent',
    'ai_researcher': 'research_agent',
    'api_developer': 'api_integrator',
    'api_gateway_architect': 'api_integrator',
    'api_integration_specialist': 'api_integrator',
    'ar/vr_designer': 'creative_design_agent',
    'arvr_designer': 'creative_design_agent',
    'aws_specialist': 'technical_agent',
    'accessibility_specialist': 'technical_agent',
    'agtech_specialist': 'technical_agent',
    'agile_coach': 'project_management_agent',
    'android_developer': 'technical_agent',
    'angular_developer': 'react_developer',
    'automation_engineer': 'technical_agent',
    'azure_specialist': 'technical_agent',
    'bi_analyst': 'data_analyst',
    'backend_engineer': 'technical_agent',
    'backup_recovery_specialist': 'technical_agent',
    'backup_&_recovery_specialist': 'technical_agent',
    'betting_analytics_expert': 'betting_analysis_specialist',
    'betting_compliance_officer': 'legal_compliance_agent',
    'betting_payment_processor': 'financial_agent',
    'betting_risk_manager': 'risk_assessment_agent',
    'big_data_engineer': 'data_analyst',
    'bioinformatics_specialist': 'data_analyst',
    'blockchain_developer': 'technical_agent',
    'budget_analyst': 'financial_analyst',
    'csharp_developer': 'technical_agent',
    'c#_developer': 'technical_agent',
    'change_management_specialist': 'project_management_agent',
    'cloud_architect': 'technical_agent',
    'college_sports_specialist': 'sports_analytics_agent',
    'compliance_officer': 'legal_compliance_agent',
    'configuration_manager': 'technical_agent',
    'content_strategist': 'content_strategy_agent',
    'contract_specialist': 'legal_agent',
    'copywriter': 'content_creator',
    'cost_optimization_specialist': 'financial_analyst',
    'crypto_analyst': 'financial_analyst',
    'customer_success_manager': 'business_agent',
    'cybersecurity_expert': 'security_auditor',
    'data_engineer': 'data_analyst',
    'database_administrator': 'database_optimizer',
    'database_architect': 'database_optimizer',
    'defi_specialist': 'financial_analyst',
    'disaster_recovery_specialist': 'technical_agent',
    'docker_specialist': 'technical_agent',
    'documentation_specialist': 'documentation_writer',
    'ecommerce_specialist': 'business_agent',
    'e-commerce_specialist': 'business_agent',
    'etl_specialist': 'data_analyst',
    'edtech_specialist': 'technical_agent',
    'edge_computing_specialist': 'technical_agent',
    'email_marketing_specialist': 'marketing_agent',
    'fintech_specialist': 'financial_agent',
    'frontend_engineer': 'react_developer',
    'fullstack_developer': 'react_developer',
    'gcp_specialist': 'technical_agent',
    'game_designer': 'creative_design_agent',
    'game_developer': 'technical_agent',
    'go_developer': 'technical_agent',
    'graphic_designer': 'creative_design_agent',
    'hr_specialist': 'business_agent',
    'handicapping_expert': 'sports_analytics_agent',
    'healthcare_specialist': 'technical_agent',
    'implementation_consultant': 'business_agent',
    'incident_manager': 'technical_agent',
    'integration_specialist': 'api_integrator',
    'interaction_designer': 'creative_design_agent',
    'iot_specialist': 'technical_agent',
    'java_developer': 'technical_agent',
    'javascript_developer': 'react_developer',
    'kubernetes_expert': 'technical_agent',
    'llm_specialist': 'prompt_engineer',
    'legaltech_specialist': 'legal_agent',
    'level_designer': 'creative_design_agent',
    'linux_administrator': 'technical_agent',
    'live_betting_engineer': 'live_betting_agent',
    'load_testing_specialist': 'technical_agent',
    'logistics_specialist': 'operations_agent',
    'metaverse_developer': 'technical_agent',
    'middleware_specialist': 'technical_agent',
    'mobile_developer': 'technical_agent',
    'monitoring_specialist': 'monitoring_dashboard',
    'motion_designer': 'creative_design_agent',
    'nft_specialist': 'technical_agent',
    'network_engineer': 'technical_agent',
    'observability_engineer': 'monitoring_dashboard',
    'odds_calculation_expert': 'odds_calculation_agent',
    'operations_manager': 'operations_agent',
    'php_developer': 'technical_agent',
    'parlay_system_developer': 'sports_analytics_agent',
    'penetration_tester': 'security_auditor',
    'performance_engineer': 'technical_agent',
    'podcast_producer': 'content_creator',
    'privacy_expert': 'legal_compliance_agent',
    'problem_manager': 'technical_agent',
    'procurement_specialist': 'business_agent',
    'product_designer': 'creative_design_agent',
    'product_manager': 'project_management_agent',
    'program_manager': 'project_management_agent',
    'project_manager': 'project_management_agent',
    'prop_bet_specialist': 'sports_analytics_agent',
    'proptech_specialist': 'technical_agent',
    'python_developer': 'technical_agent',
    'qa_engineer': 'technical_agent',
    'quantum_computing_researcher': 'research_agent',
    'release_manager': 'project_management_agent',
    'research_scientist': 'research_agent',
    'responsible_gaming_specialist': 'legal_compliance_agent',
    'robotics_engineer': 'technical_agent',
    'rust_developer': 'technical_agent',
    'seo_specialist': 'seo_specialist_agent',
    'sales_specialist': 'business_agent',
    'sales_agent': 'business_agent',
    'scrum_master': 'project_management_agent',
    'security_architect': 'security_auditor',
    'security_specialist': 'security_auditor',
    'service_desk_analyst': 'technical_agent',
    'site_reliability_engineer': 'technical_agent',
    'sre_engineer': 'technical_agent',
    'social_media_manager': 'marketing_agent',
    'solidity_developer': 'technical_agent',
    'sports_betting_specialist': 'sports_analytics_agent',
    'sports_data_integration_expert': 'sports_analytics_agent',
    'sports_statistician': 'sports_analytics_agent',
    'sportsbook_architect': 'sports_analytics_agent',
    'storage_specialist': 'technical_agent',
    'system_administrator': 'technical_agent',
    'technical_support_engineer': 'technical_agent',
    'technical_writer': 'documentation_writer',
    'terraform_expert': 'technical_agent',
    'test_automation_engineer': 'technical_agent',
    'training_specialist': 'business_agent',
    'typescript_developer': 'react_developer',
    'ui_designer': 'ui/ux_designer',
    'ux_designer': 'ui/ux_designer',
    'unity_developer': 'technical_agent',
    'unreal_developer': 'technical_agent',
    'vendor_manager': 'business_agent',
    'video_producer': 'content_creator',
    'virtualization_specialist': 'technical_agent',
    'vue_developer': 'react_developer',
    'web3_developer': 'technical_agent',
    'windows_administrator': 'technical_agent',
    'ios_developer': 'technical_agent',
}

def generate_mapping_dict():
    """Generate the complete mapping dictionary"""
    all_mappings = {}
    all_mappings.update(WORKING_MAPPINGS)
    all_mappings.update(FAILING_AGENT_MAPPINGS)

    # Format as Python dictionary string
    lines = ["            name_mappings = {"]
    lines.append("                # Working agents (confirmed successful in tests)")

    for key, value in WORKING_MAPPINGS.items():
        lines.append(f"                '{key}': '{value}',")

    lines.append("")
    lines.append("                # Map failing agents to available registry agents")

    for key, value in FAILING_AGENT_MAPPINGS.items():
        lines.append(f"                '{key}': '{value}',")

    lines.append("            }")

    return "\n".join(lines)

if __name__ == "__main__":
    print("Generated mapping dictionary:")
    print(generate_mapping_dict())