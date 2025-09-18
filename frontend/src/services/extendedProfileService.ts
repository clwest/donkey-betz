import { apiClient } from './api.config';

// Extended Profile Types
export interface ExtendedUserProfile {
  id: string;
  user: string;
  full_name: string;
  phone: string;
  location: string;
  timezone: string;
  current_title: string;
  years_experience: number;
  experience_level: 'entry' | 'mid' | 'senior' | 'executive';
  desired_salary_min: number | null;
  desired_salary_max: number | null;
  skills: string[];
  certifications: string[];
  work_history: WorkHistoryItem[];
  education: EducationItem[];
  resume: string | null;
  portfolio_url: string;
  cover_letters: CoverLetter[];
  linkedin_url: string;
  indeed_profile: string;
  github_username: string;
  job_preferences: JobPreferences;
  remote_preference: 'remote' | 'hybrid' | 'onsite' | 'no_preference';
  willing_to_relocate: boolean;
  profile_completeness: number;
  // AI Job Application Fields
  professional_summary?: string;
  key_achievements?: string[];
  languages?: { language: string; proficiency: string }[];
  availability?: 'immediate' | '2_weeks' | '1_month' | 'flexible';
  contract_preference?: 'full_time' | 'part_time' | 'contract' | 'any';
  visa_status?: string;
  security_clearance?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkHistoryItem {
  company: string;
  title: string;
  start_date: string;
  end_date?: string;
  current: boolean;
  description: string;
  achievements: string[];
}

export interface EducationItem {
  institution: string;
  degree: string;
  field_of_study: string;
  graduation_year: number;
  gpa?: number;
}

export interface CoverLetter {
  name: string;
  content: string;
  created_at: string;
}

export interface JobPreferences {
  industries: string[];
  job_types: string[];
  company_sizes: string[];
  cultures: string[];
  // AI Job Application Settings
  auto_apply?: boolean;
  min_match_score?: number;
  application_tone?: 'professional' | 'friendly' | 'enthusiastic' | 'formal';
  max_applications_per_day?: number;
  preferred_platforms?: string[];
}

export interface ProfileCompletion {
  overall_percentage: number;
  sections: {
    basic_info: number;
    professional_info: number;
    skills: number;
    experience: number;
    education: number;
    preferences: number;
  };
  suggestions: string[];
}

export interface JobOpportunity {
  id: string;
  job_title: string;
  company: string;
  location: string;
  remote_type: string;
  salary_range: string;
  match_score: number;
  skills_matched: string[];
  posted_date: string;
  platform: string;
  job_url: string;
  description: string;
  requirements: string[];
}

export interface JobApplication {
  id: string;
  job_id: string;
  position: string;
  company: string;
  status: 'draft' | 'applied' | 'viewed' | 'interview' | 'offer' | 'rejected';
  applied_date: string;
  platform: string;
  match_score: number;
  notes: string;
}

class ExtendedProfileService {
  // Profile Management
  async getExtendedProfile(): Promise<ExtendedUserProfile> {
    const response = await apiClient.get('/profile/extended/');
    return response.data;
  }

  async updateExtendedProfile(data: Partial<ExtendedUserProfile>): Promise<ExtendedUserProfile> {
    const response = await apiClient.patch('/profile/extended/', data);
    return response.data;
  }

  async getProfileCompletion(): Promise<ProfileCompletion> {
    const response = await apiClient.get('/profile/completion/');
    return response.data;
  }

  // Skills Management
  async addSkill(skill: string, proficiency: 'beginner' | 'intermediate' | 'advanced' | 'expert'): Promise<void> {
    await apiClient.post('/profile/skills/', { skill, proficiency });
  }

  async removeSkill(skill: string): Promise<void> {
    await apiClient.delete(`/api/profile/skills/${encodeURIComponent(skill)}/`);
  }

  async updateSkills(skills: string[]): Promise<void> {
    await apiClient.put('/profile/skills/', { skills });
  }

  // Work History
  async addWorkHistory(item: WorkHistoryItem): Promise<void> {
    await apiClient.post('/profile/work-history/', item);
  }

  async updateWorkHistory(index: number, item: WorkHistoryItem): Promise<void> {
    await apiClient.put(`/api/profile/work-history/${index}/`, item);
  }

  async deleteWorkHistory(index: number): Promise<void> {
    await apiClient.delete(`/api/profile/work-history/${index}/`);
  }

  // Education
  async addEducation(item: EducationItem): Promise<void> {
    await apiClient.post('/profile/education/', item);
  }

  async updateEducation(index: number, item: EducationItem): Promise<void> {
    await apiClient.put(`/api/profile/education/${index}/`, item);
  }

  async deleteEducation(index: number): Promise<void> {
    await apiClient.delete(`/api/profile/education/${index}/`);
  }

  // Resume Management
  async uploadResume(file: File, version_name?: string): Promise<{ id: string; url: string }> {
    const formData = new FormData();
    formData.append('resume', file);
    if (version_name) {
      formData.append('version_name', version_name);
    }

    const response = await apiClient.post('/profile/resume/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getResumes(): Promise<Array<{ id: string; name: string; url: string; created_at: string }>> {
    const response = await apiClient.get('/profile/resumes/');
    return response.data;
  }

  async deleteResume(resumeId: string): Promise<void> {
    await apiClient.delete(`/api/profile/resume/${resumeId}/`);
  }

  // Job Opportunities
  async getJobOpportunities(filters?: {
    min_match_score?: number;
    location?: string;
    remote_only?: boolean;
    salary_min?: number;
  }): Promise<JobOpportunity[]> {
    const response = await apiClient.get('/jobs/opportunities/', { params: filters });
    return response.data;
  }

  async applyToJob(jobId: string, resumeId?: string, coverLetter?: string): Promise<JobApplication> {
    const response = await apiClient.post('/jobs/quick-apply/', {
      job_id: jobId,
      resume_id: resumeId,
      cover_letter: coverLetter,
    });
    return response.data;
  }

  async getApplications(filters?: {
    status?: string;
    platform?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<JobApplication[]> {
    const response = await apiClient.get('/jobs/applications/', { params: filters });
    return response.data;
  }

  async updateApplicationStatus(applicationId: string, status: string, notes?: string): Promise<void> {
    await apiClient.patch(`/api/jobs/applications/${applicationId}/status/`, { status, notes });
  }

  // Profile Export
  async exportProfile(format: 'json' | 'pdf' = 'json'): Promise<Blob> {
    const response = await apiClient.get(`/api/profile/export/`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }
}

const extendedProfileService = new ExtendedProfileService();

export { extendedProfileService };
export default extendedProfileService;