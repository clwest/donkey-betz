/**
 * Unified Bridge Service
 * =====================
 *
 * This service connects the mobile app to the real money-making backend.
 * It replaces mock data with actual functionality across all components.
 */

import { apiClient } from './apiClient';

export interface UserProfile {
  id?: string;
  user_id?: number;
  display_name: string;
  bio: string;
  occupation: string;
  location: string;
  skills: string[];
  experience_years: number;
  current_role: string;
  industries: string[];
  portfolio_url: string;
  linkedin_url: string;
  github_url: string;
  remote_only: boolean;
  contract_work: boolean;
  full_time: boolean;
  hourly_rate_min: number;
  salary_min: number;
  preferred_ai_model: string;
  default_content_tone: string;
  auto_save: boolean;
  dark_mode: boolean;
  email_notifications: boolean;
}

export interface JobOpportunity {
  id: string;
  title: string;
  company: string;
  description: string;
  url: string;
  match_score: number;
  salary_range: string;
  location: string;
  discovered_at: string;
  source: string;
  is_real: boolean;
  is_searching?: boolean;
  reasons?: string[];
  action_plan?: string[];
}

export interface ApplicationResult {
  success: boolean;
  application_id?: string;
  submitted_at?: string;
  platform?: string;
  next_steps?: string[];
  error?: string;
  suggestion?: string;
}

export interface RevenueData {
  amount: number;
  source: string;
  project_type?: string;
  currency?: string;
  description?: string;
  date?: string;
}

export interface DecisionRecommendation {
  should_apply: boolean;
  confidence: number;
  reasoning: string[];
  action_plan?: string[];
  metrics: {
    skill_match: number;
    competition_level: number;
    earning_potential: number;
    time_investment: number;
    success_probability: number;
  };
  alternatives?: JobOpportunity[];
  error?: boolean;
}

export interface DashboardData {
  profile: {
    name: string;
    role: string;
    experience_years: number;
    skills_count: number;
    completeness: number;
  };
  opportunities: {
    total: number;
    high_match: number;
    applied_today: number;
    response_rate: number;
  };
  applications: {
    total: number;
    in_progress: number;
    successful: number;
    success_rate: number;
  };
  revenue: {
    total_earnings: number;
    this_month: number;
    projects_completed: number;
    avg_project_value: number;
  };
  activity: {
    last_login: string;
    actions_today: number;
    streak_days: number;
    engagement_score: number;
  };
}

class UnifiedBridgeService {

  // ==================== PROFILE SYNCHRONIZATION ====================

  /**
   * Sync user profile across ALL platform components.
   * This makes profiles persistent and updates everywhere at once.
   */
  async syncUserProfile(profileData: Partial<UserProfile>): Promise<{
    success: boolean;
    message?: string;
    components_updated?: string[];
    error?: string;
  }> {
    try {
      const response = await apiClient.post('/bridge/profile/sync/', profileData);
      return response;
    } catch (error: any) {
      console.error('Failed to sync user profile:', error);
      return {
        success: false,
        error: error.userMessage || 'Failed to sync profile across components'
      };
    }
  }

  // ==================== REAL JOB OPPORTUNITIES ====================

  /**
   * Get real job opportunities from spider network, scored for this user.
   * This replaces fake data in Income Builder with actual jobs.
   */
  async getRealOpportunities(): Promise<{
    success: boolean;
    opportunities: JobOpportunity[];
    total: number;
    source: string;
    last_updated?: string;
    error?: string;
  }> {
    try {
      const response = await apiClient.get('/bridge/opportunities/real/');
      return response;
    } catch (error: any) {
      console.error('Failed to get real opportunities:', error);

      // Return fallback data while spider network activates
      return {
        success: false,
        opportunities: [
          {
            id: 'spider_activating',
            title: 'Spider Network Activating...',
            company: 'AI Job Hunter',
            description: 'Our AI spiders are searching job boards for opportunities matching your profile. This usually takes 30-60 seconds.',
            url: '',
            match_score: 0.0,
            salary_range: 'Searching...',
            location: 'Various',
            discovered_at: new Date().toISOString(),
            source: 'spider_activation',
            is_real: false,
            is_searching: true
          }
        ],
        total: 0,
        source: 'fallback',
        error: error.userMessage || 'Spider network activation in progress'
      };
    }
  }

  // ==================== REAL APPLICATION SUBMISSION ====================

  /**
   * Submit actual job application to external job board.
   * This makes Quick Apply functional instead of fake.
   */
  async submitRealApplication(
    jobData: JobOpportunity,
    applicationData: {
      cover_letter?: string;
      custom_resume?: boolean;
      notes?: string;
    }
  ): Promise<ApplicationResult> {
    try {
      const response = await apiClient.post('/bridge/apply/submit/', {
        job_data: jobData,
        application_data: applicationData
      });
      return response;
    } catch (error: any) {
      console.error('Failed to submit real application:', error);
      return {
        success: false,
        error: error.userMessage || 'Failed to submit application',
        suggestion: 'Please check your profile completeness and try again'
      };
    }
  }

  // ==================== REVENUE TRACKING ====================

  /**
   * Record actual revenue from completed work.
   * This makes the Revenue Dashboard show real earnings.
   */
  async recordRevenue(revenueData: RevenueData): Promise<{
    success: boolean;
    message?: string;
    celebration?: boolean;
    total_earnings?: number;
    error?: string;
  }> {
    try {
      const response = await apiClient.post('/bridge/revenue/record/', revenueData);
      return response;
    } catch (error: any) {
      console.error('Failed to record revenue:', error);
      return {
        success: false,
        error: error.userMessage || 'Failed to record revenue'
      };
    }
  }

  // ==================== DECISION ENGINE ====================

  /**
   * Get AI-powered decision on whether to pursue an opportunity.
   * This connects Decision Command to real ML insights.
   */
  async getOpportunityDecision(opportunity: JobOpportunity): Promise<DecisionRecommendation> {
    try {
      const response = await apiClient.post('/bridge/decision/analyze/', {
        opportunity: opportunity
      });
      return response.recommendation;
    } catch (error: any) {
      console.error('Failed to get opportunity decision:', error);
      return {
        should_apply: false,
        confidence: 0.0,
        reasoning: [error.userMessage || 'Unable to analyze opportunity'],
        metrics: {
          skill_match: 0,
          competition_level: 0,
          earning_potential: 0,
          time_investment: 0,
          success_probability: 0
        },
        error: true
      };
    }
  }

  // ==================== UNIFIED DASHBOARD ====================

  /**
   * Get unified dashboard data showing real activity across all components.
   * This makes the Revenue Dashboard show actual data.
   */
  async getDashboardData(): Promise<{
    success: boolean;
    dashboard: DashboardData;
    last_updated: string;
    error?: string;
  }> {
    try {
      const response = await apiClient.get('/bridge/dashboard/unified/');
      return response;
    } catch (error: any) {
      console.error('Failed to get dashboard data:', error);

      // Return fallback dashboard data
      return {
        success: false,
        dashboard: {
          profile: {
            name: 'Loading...',
            role: 'Loading...',
            experience_years: 0,
            skills_count: 0,
            completeness: 0
          },
          opportunities: {
            total: 0,
            high_match: 0,
            applied_today: 0,
            response_rate: 0.0
          },
          applications: {
            total: 0,
            in_progress: 0,
            successful: 0,
            success_rate: 0.0
          },
          revenue: {
            total_earnings: 0.0,
            this_month: 0.0,
            projects_completed: 0,
            avg_project_value: 0.0
          },
          activity: {
            last_login: new Date().toISOString(),
            actions_today: 0,
            streak_days: 0,
            engagement_score: 0
          }
        },
        last_updated: new Date().toISOString(),
        error: error.userMessage || 'Dashboard data unavailable'
      };
    }
  }

  // ==================== COMPONENT SYNCHRONIZATION ====================

  /**
   * Manually trigger synchronization between all components.
   * Emergency sync button for when things get out of sync.
   */
  async triggerComponentSync(): Promise<{
    success: boolean;
    message?: string;
    components?: string[];
    error?: string;
  }> {
    try {
      const response = await apiClient.post('/bridge/sync/trigger/', {});
      return response;
    } catch (error: any) {
      console.error('Failed to trigger component sync:', error);
      return {
        success: false,
        error: error.userMessage || 'Failed to synchronize components'
      };
    }
  }

  // ==================== CONVENIENCE METHODS ====================

  /**
   * Complete onboarding flow: sync profile and get initial opportunities
   */
  async completeOnboarding(profileData: UserProfile): Promise<{
    profileSynced: boolean;
    opportunitiesFound: boolean;
    totalOpportunities: number;
    error?: string;
  }> {
    try {
      // 1. Sync profile first
      const profileResult = await this.syncUserProfile(profileData);

      if (!profileResult.success) {
        return {
          profileSynced: false,
          opportunitiesFound: false,
          totalOpportunities: 0,
          error: profileResult.error
        };
      }

      // 2. Wait a moment for backend processing
      await new Promise(resolve => setTimeout(resolve, 2000));

      // 3. Get opportunities
      const opportunitiesResult = await this.getRealOpportunities();

      return {
        profileSynced: true,
        opportunitiesFound: opportunitiesResult.success,
        totalOpportunities: opportunitiesResult.total,
        error: opportunitiesResult.error
      };
    } catch (error: any) {
      return {
        profileSynced: false,
        opportunitiesFound: false,
        totalOpportunities: 0,
        error: 'Onboarding failed: ' + error.message
      };
    }
  }

  /**
   * Quick Apply flow: get decision, then submit if recommended
   */
  async smartQuickApply(
    opportunity: JobOpportunity,
    forceApply: boolean = false
  ): Promise<{
    analysisComplete: boolean;
    shouldApply: boolean;
    applicationSubmitted: boolean;
    recommendation?: DecisionRecommendation;
    application?: ApplicationResult;
    error?: string;
  }> {
    try {
      // 1. Get AI recommendation
      const recommendation = await this.getOpportunityDecision(opportunity);

      if (recommendation.error) {
        return {
          analysisComplete: false,
          shouldApply: false,
          applicationSubmitted: false,
          error: 'Failed to analyze opportunity'
        };
      }

      // 2. Apply if recommended or forced
      const shouldApply = recommendation.should_apply || forceApply;
      let application: ApplicationResult | undefined;

      if (shouldApply) {
        application = await this.submitRealApplication(opportunity, {
          cover_letter: `Based on my ${recommendation.metrics.skill_match * 100}% skill match, I believe I'd be an excellent fit for this role.`,
          notes: `AI confidence: ${recommendation.confidence * 100}%`
        });
      }

      return {
        analysisComplete: true,
        shouldApply,
        applicationSubmitted: shouldApply && (application?.success || false),
        recommendation,
        application
      };
    } catch (error: any) {
      return {
        analysisComplete: false,
        shouldApply: false,
        applicationSubmitted: false,
        error: error.message
      };
    }
  }
}

// Export singleton instance
export const unifiedBridgeService = new UnifiedBridgeService();
export default unifiedBridgeService;