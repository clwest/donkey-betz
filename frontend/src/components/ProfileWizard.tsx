import React, { useState, useEffect } from 'react';
import {
  User,
  Briefcase,
  Brain,
  Target,
  FileText,
  Settings,
  CheckCircle,
  Circle,
  ArrowRight,
  ArrowLeft,
  Upload,
  Plus,
  X
} from 'lucide-react';

interface ProfileData {
  full_name: string;
  phone: string;
  location: string;
  timezone: string;
  current_title: string;
  years_experience: number;
  experience_level: string;
  desired_salary_min: number | null;
  desired_salary_max: number | null;
  skills: Array<{
    name: string;
    proficiency: string;
    years: number;
  }>;
  certifications: Array<{
    name: string;
    issued_by: string;
    date: string;
  }>;
  work_history: Array<{
    company: string;
    title: string;
    start_date: string;
    end_date: string;
    responsibilities: string[];
  }>;
  education: Array<{
    degree: string;
    institution: string;
    graduation_year: number;
    field_of_study: string;
  }>;
  portfolio_url: string;
  linkedin_url: string;
  github_username: string;
  job_preferences: {
    preferred_industries: string[];
    preferred_roles: string[];
    company_sizes: string[];
    work_culture: string;
  };
  remote_preference: string;
  willing_to_relocate: boolean;
}

interface Step {
  id: string;
  title: string;
  icon: React.ComponentType<any>;
  component: React.ComponentType<any>;
  required?: boolean;
}

const ProfileWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [profileData, setProfileData] = useState<ProfileData>({
    full_name: '',
    phone: '',
    location: '',
    timezone: '',
    current_title: '',
    years_experience: 0,
    experience_level: 'entry',
    desired_salary_min: null,
    desired_salary_max: null,
    skills: [],
    certifications: [],
    work_history: [],
    education: [],
    portfolio_url: '',
    linkedin_url: '',
    github_username: '',
    job_preferences: {
      preferred_industries: [],
      preferred_roles: [],
      company_sizes: [],
      work_culture: ''
    },
    remote_preference: 'no_preference',
    willing_to_relocate: false
  });
  const [completionPercentage, setCompletionPercentage] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  // Step components
  const PersonalInfoStep: React.FC = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">Personal Information</h2>
        <p className="text-muted-foreground">Let's start with your basic information</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-foreground text-sm font-medium mb-2">
            Full Name *
          </label>
          <input
            type="text"
            value={profileData.full_name}
            onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
            className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder="Enter your full name"
          />
        </div>

        <div>
          <label className="block text-foreground text-sm font-medium mb-2">
            Phone Number *
          </label>
          <input
            type="tel"
            value={profileData.phone}
            onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
            className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder="+1 (555) 123-4567"
          />
        </div>

        <div>
          <label className="block text-foreground text-sm font-medium mb-2">
            Location *
          </label>
          <input
            type="text"
            value={profileData.location}
            onChange={(e) => setProfileData({ ...profileData, location: e.target.value })}
            className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder="City, State/Province, Country"
          />
        </div>

        <div>
          <label className="block text-foreground text-sm font-medium mb-2">
            Timezone
          </label>
          <select
            value={profileData.timezone}
            onChange={(e) => setProfileData({ ...profileData, timezone: e.target.value })}
            className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Select timezone</option>
            <option value="America/New_York">Eastern Time (ET)</option>
            <option value="America/Chicago">Central Time (CT)</option>
            <option value="America/Denver">Mountain Time (MT)</option>
            <option value="America/Los_Angeles">Pacific Time (PT)</option>
            <option value="Europe/London">GMT</option>
            <option value="Europe/Paris">Central European Time</option>
            <option value="Asia/Tokyo">Japan Standard Time</option>
          </select>
        </div>
      </div>
    </div>
  );

  const ProfessionalInfoStep: React.FC = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">Professional Background</h2>
        <p className="text-muted-foreground">Tell us about your career and experience</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-foreground text-sm font-medium mb-2">
            Current Job Title *
          </label>
          <input
            type="text"
            value={profileData.current_title}
            onChange={(e) => setProfileData({ ...profileData, current_title: e.target.value })}
            className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder="e.g., Senior Software Engineer"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-foreground text-sm font-medium mb-2">
              Years of Experience *
            </label>
            <input
              type="number"
              min="0"
              max="50"
              value={profileData.years_experience}
              onChange={(e) => setProfileData({ ...profileData, years_experience: parseInt(e.target.value) || 0 })}
              className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-foreground text-sm font-medium mb-2">
              Experience Level
            </label>
            <select
              value={profileData.experience_level}
              onChange={(e) => setProfileData({ ...profileData, experience_level: e.target.value })}
              className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              <option value="entry">Entry Level (0-2 years)</option>
              <option value="junior">Junior (2-4 years)</option>
              <option value="mid">Mid Level (4-7 years)</option>
              <option value="senior">Senior (7-10 years)</option>
              <option value="lead">Lead/Principal (10+ years)</option>
              <option value="executive">Executive (C-Level)</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-foreground text-sm font-medium mb-2">
              Desired Salary (Min)
            </label>
            <input
              type="number"
              min="0"
              step="1000"
              value={profileData.desired_salary_min || ''}
              onChange={(e) => setProfileData({
                ...profileData,
                desired_salary_min: e.target.value ? parseInt(e.target.value) : null
              })}
              className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              placeholder="50000"
            />
          </div>

          <div>
            <label className="block text-foreground text-sm font-medium mb-2">
              Desired Salary (Max)
            </label>
            <input
              type="number"
              min="0"
              step="1000"
              value={profileData.desired_salary_max || ''}
              onChange={(e) => setProfileData({
                ...profileData,
                desired_salary_max: e.target.value ? parseInt(e.target.value) : null
              })}
              className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              placeholder="80000"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const SkillsStep: React.FC = () => {
    const [newSkill, setNewSkill] = useState({ name: '', proficiency: 'Intermediate', years: 1 });

    const addSkill = () => {
      if (newSkill.name) {
        setProfileData({
          ...profileData,
          skills: [...profileData.skills, newSkill]
        });
        setNewSkill({ name: '', proficiency: 'Intermediate', years: 1 });
      }
    };

    const removeSkill = (index: number) => {
      setProfileData({
        ...profileData,
        skills: profileData.skills.filter((_, i) => i !== index)
      });
    };

    return (
      <div className="space-y-6">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-foreground mb-2">Skills & Expertise</h2>
          <p className="text-muted-foreground">Add your technical and professional skills</p>
        </div>

        <div className="bg-card rounded-lg p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Add New Skill</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <input
                type="text"
                value={newSkill.name}
                onChange={(e) => setNewSkill({ ...newSkill, name: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-foreground placeholder-gray-400 focus:border-blue-500"
                placeholder="Skill name (e.g., Python, Project Management)"
              />
            </div>
            <div>
              <select
                value={newSkill.proficiency}
                onChange={(e) => setNewSkill({ ...newSkill, proficiency: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-foreground focus:border-blue-500"
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
                <option value="Expert">Expert</option>
              </select>
            </div>
            <div className="flex gap-2">
              <input
                type="number"
                min="0"
                max="30"
                value={newSkill.years}
                onChange={(e) => setNewSkill({ ...newSkill, years: parseInt(e.target.value) || 1 })}
                className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-foreground focus:border-blue-500"
                placeholder="Years"
              />
              <button
                onClick={addSkill}
                className="bg-blue-600 hover:bg-blue-700 text-foreground px-4 py-2 rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-foreground">Your Skills</h3>
          {profileData.skills.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">No skills added yet. Add your first skill above!</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {profileData.skills.map((skill, index) => (
                <div
                  key={index}
                  className="bg-card rounded-lg p-4 flex justify-between items-center"
                >
                  <div>
                    <h4 className="text-foreground font-medium">{skill.name}</h4>
                    <p className="text-muted-foreground text-sm">
                      {skill.proficiency} • {skill.years} year{skill.years !== 1 ? 's' : ''}
                    </p>
                  </div>
                  <button
                    onClick={() => removeSkill(index)}
                    className="text-red-500 hover:text-red-300 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  const PreferencesStep: React.FC = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">Job Preferences</h2>
        <p className="text-muted-foreground">Help us find the perfect opportunities for you</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-foreground text-sm font-medium mb-2">
            Remote Work Preference
          </label>
          <select
            value={profileData.remote_preference}
            onChange={(e) => setProfileData({ ...profileData, remote_preference: e.target.value })}
            className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          >
            <option value="no_preference">No Preference</option>
            <option value="remote">Remote Only</option>
            <option value="hybrid">Hybrid (Remote + Office)</option>
            <option value="onsite">On-site Only</option>
          </select>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="willing_to_relocate"
            checked={profileData.willing_to_relocate}
            onChange={(e) => setProfileData({ ...profileData, willing_to_relocate: e.target.checked })}
            className="w-4 h-4 text-blue-600 bg-card border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
          />
          <label htmlFor="willing_to_relocate" className="ml-2 text-foreground">
            I'm willing to relocate for the right opportunity
          </label>
        </div>

        <div>
          <label className="block text-foreground text-sm font-medium mb-2">
            Portfolio URL
          </label>
          <input
            type="url"
            value={profileData.portfolio_url}
            onChange={(e) => setProfileData({ ...profileData, portfolio_url: e.target.value })}
            className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder="https://your-portfolio.com"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-foreground text-sm font-medium mb-2">
              LinkedIn Profile
            </label>
            <input
              type="url"
              value={profileData.linkedin_url}
              onChange={(e) => setProfileData({ ...profileData, linkedin_url: e.target.value })}
              className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              placeholder="https://linkedin.com/in/yourprofile"
            />
          </div>

          <div>
            <label className="block text-foreground text-sm font-medium mb-2">
              GitHub Username
            </label>
            <input
              type="text"
              value={profileData.github_username}
              onChange={(e) => setProfileData({ ...profileData, github_username: e.target.value })}
              className="w-full bg-card border border-gray-600 rounded-lg px-4 py-3 text-foreground placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              placeholder="yourusername"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const DocumentsStep: React.FC = () => {
    const [resumeFile, setResumeFile] = useState<File | null>(null);

    const handleResumeUpload = async () => {
      if (!resumeFile) return;

      const formData = new FormData();
      formData.append('resume', resumeFile);
      formData.append('version_name', 'Primary Resume');
      formData.append('is_primary', 'true');

      try {
        const response = await fetch('/api/profile/resume/', {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          const result = await response.json();
          console.log('Resume uploaded successfully:', result);
        }
      } catch (error) {
        console.error('Error uploading resume:', error);
      }
    };

    return (
      <div className="space-y-6">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-foreground mb-2">Documents & Resume</h2>
          <p className="text-muted-foreground">Upload your resume to enable AI-powered applications</p>
        </div>

        <div className="bg-card rounded-lg p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Resume Upload</h3>
          <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
            <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-foreground mb-2">Upload your resume</p>
            <p className="text-muted-foreground text-sm mb-4">PDF, DOC, or DOCX files only</p>

            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
              className="hidden"
              id="resume-upload"
            />
            <label
              htmlFor="resume-upload"
              className="bg-blue-600 hover:bg-blue-700 text-foreground px-6 py-2 rounded-lg cursor-pointer transition-colors inline-block"
            >
              Choose File
            </label>

            {resumeFile && (
              <div className="mt-4">
                <p className="text-green-500">Selected: {resumeFile.name}</p>
                <button
                  onClick={handleResumeUpload}
                  className="mt-2 bg-green-600 hover:bg-green-700 text-foreground px-4 py-2 rounded-lg transition-colors"
                >
                  Upload Resume
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const IntegrationsStep: React.FC = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">Platform Integrations</h2>
        <p className="text-muted-foreground">Connect your professional accounts for better job matching</p>
      </div>

      <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-lg p-6 text-center">
        <CheckCircle className="w-16 h-16 text-foreground mx-auto mb-4" />
        <h3 className="text-2xl font-bold text-foreground mb-2">Profile Complete!</h3>
        <p className="text-green-100 mb-4">
          Your profile is {completionPercentage}% complete and ready for AI-powered job matching.
        </p>
        <p className="text-green-100 text-sm">
          Our AI agents now have everything they need to help you find and apply to the perfect opportunities.
        </p>
      </div>
    </div>
  );

  const steps: Step[] = [
    { id: 'personal', title: 'Personal Info', icon: User, component: PersonalInfoStep, required: true },
    { id: 'professional', title: 'Professional', icon: Briefcase, component: ProfessionalInfoStep, required: true },
    { id: 'skills', title: 'Skills', icon: Brain, component: SkillsStep, required: true },
    { id: 'preferences', title: 'Preferences', icon: Target, component: PreferencesStep },
    { id: 'documents', title: 'Documents', icon: FileText, component: DocumentsStep, required: true },
    { id: 'integrations', title: 'Complete', icon: Settings, component: IntegrationsStep }
  ];

  const saveProfile = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/profile/extended/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        const result = await response.json();
        setCompletionPercentage(result.profile_completeness);
      }
    } catch (error) {
      console.error('Error saving profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const nextStep = async () => {
    if (currentStep < steps.length - 1) {
      await saveProfile();
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  useEffect(() => {
    // Load existing profile data on mount
    const loadProfile = async () => {
      try {
        const response = await fetch('/api/profile/extended/');
        if (response.ok) {
          const result = await response.json();
          if (result.success) {
            setProfileData(result.profile);
            setCompletionPercentage(result.profile.profile_completeness);
          }
        }
      } catch (error) {
        console.error('Error loading profile:', error);
      }
    };

    loadProfile();
  }, []);

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Progress Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-foreground">Profile Setup</h1>
            <div className="text-foreground text-sm">
              Step {currentStep + 1} of {steps.length}
            </div>
          </div>

          {/* Step Progress */}
          <div className="flex items-center space-x-4 mb-6">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isCompleted = index < currentStep;
              const isCurrent = index === currentStep;

              return (
                <div key={step.id} className="flex items-center">
                  <div
                    className={`flex items-center justify-center w-10 h-10 rounded-full transition-colors ${
                      isCompleted
                        ? 'bg-green-500 text-foreground'
                        : isCurrent
                        ? 'bg-blue-500 text-foreground'
                        : 'bg-gray-700 text-muted-foreground'
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                  </div>
                  <span
                    className={`ml-2 text-sm font-medium ${
                      isCompleted || isCurrent ? 'text-foreground' : 'text-muted-foreground'
                    }`}
                  >
                    {step.title}
                  </span>
                  {index < steps.length - 1 && (
                    <ArrowRight className="w-4 h-4 text-gray-600 mx-4" />
                  )}
                </div>
              );
            })}
          </div>

          {/* Completion Progress Bar */}
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-background rounded-lg p-8 mb-8">
          <CurrentStepComponent />
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={prevStep}
            disabled={currentStep === 0}
            className={`flex items-center px-6 py-3 rounded-lg transition-colors ${
              currentStep === 0
                ? 'bg-gray-700 text-muted-foreground cursor-not-allowed'
                : 'bg-gray-700 text-foreground hover:bg-gray-600'
            }`}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Previous
          </button>

          <button
            onClick={nextStep}
            disabled={currentStep === steps.length - 1 || isLoading}
            className={`flex items-center px-6 py-3 rounded-lg transition-colors ${
              currentStep === steps.length - 1
                ? 'bg-green-600 text-foreground hover:bg-green-700'
                : 'bg-blue-600 text-foreground hover:bg-blue-700'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isLoading ? (
              'Saving...'
            ) : currentStep === steps.length - 1 ? (
              'Complete'
            ) : (
              <>
                Next
                <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfileWizard;