import React, { useState, useEffect } from 'react';
import {
  User,
  Briefcase,
  Target,
  TrendingUp,
  FileText,
  CheckCircle,
  AlertCircle,
  Edit,
  Download,
  BarChart3,
  Clock,
  MapPin,
  DollarSign,
  Calendar,
  Award,
  ExternalLink
} from 'lucide-react';

interface ProfileCompleteness {
  percentage: number;
  missing_fields: Array<{
    field: string;
    display_name: string;
    priority: string;
  }>;
  suggestions: string[];
  next_priority: any;
}

interface ApplicationAnalytics {
  total_applications: number;
  successful_applications: number;
  success_rate: number;
  average_response_time_days: number | null;
}

interface ExtendedProfile {
  id: string;
  full_name: string;
  phone: string;
  location: string;
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
  certifications: any[];
  work_history: any[];
  education: any[];
  portfolio_url: string;
  linkedin_url: string;
  github_username: string;
  remote_preference: string;
  willing_to_relocate: boolean;
  profile_completeness: number;
}

const ProfileDashboard: React.FC = () => {
  const [profile, setProfile] = useState<ExtendedProfile | null>(null);
  const [completeness, setCompleteness] = useState<ProfileCompleteness | null>(null);
  const [analytics, setAnalytics] = useState<ApplicationAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditMode, setIsEditMode] = useState(false);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setIsLoading(true);

        // Load profile data
        const [profileRes, completionRes, analyticsRes] = await Promise.all([
          fetch('/api/profile/extended/'),
          fetch('/api/profile/completion/'),
          fetch('/api/profile/applications/')
        ]);

        if (profileRes.ok) {
          const profileData = await profileRes.json();
          setProfile(profileData.profile);
        }

        if (completionRes.ok) {
          const completionData = await completionRes.json();
          setCompleteness(completionData.completion);
        }

        if (analyticsRes.ok) {
          const analyticsData = await analyticsRes.json();
          setAnalytics(analyticsData.analytics);
        }
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const getExperienceLevelDisplay = (level: string) => {
    const levels = {
      entry: 'Entry Level',
      junior: 'Junior',
      mid: 'Mid Level',
      senior: 'Senior',
      lead: 'Lead/Principal',
      executive: 'Executive'
    };
    return levels[level as keyof typeof levels] || level;
  };

  const getRemotePreferenceDisplay = (pref: string) => {
    const prefs = {
      remote: 'Remote Only',
      hybrid: 'Hybrid',
      onsite: 'On-site Only',
      no_preference: 'No Preference'
    };
    return prefs[pref as keyof typeof prefs] || pref;
  };

  const formatSalaryRange = () => {
    if (!profile?.desired_salary_min && !profile?.desired_salary_max) {
      return 'Not specified';
    }
    const min = profile.desired_salary_min ? `$${profile.desired_salary_min.toLocaleString()}` : 'N/A';
    const max = profile.desired_salary_max ? `$${profile.desired_salary_max.toLocaleString()}` : 'N/A';
    return `${min} - ${max}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading your profile...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Profile Dashboard</h1>
            <p className="text-gray-300">
              Manage your profile and track your job search progress
            </p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => setIsEditMode(!isEditMode)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
            >
              <Edit className="w-4 h-4" />
              {isEditMode ? 'Save Changes' : 'Edit Profile'}
            </button>
          </div>
        </div>

        {/* Profile Completion Alert */}
        {completeness && completeness.percentage < 80 && (
          <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-400" />
              <div>
                <h3 className="text-yellow-400 font-semibold">
                  Profile {completeness.percentage.toFixed(1)}% Complete
                </h3>
                <p className="text-yellow-200 text-sm">
                  Complete your profile to unlock AI-powered job matching and applications
                </p>
                {completeness.next_priority && (
                  <p className="text-yellow-200 text-sm mt-1">
                    Next: Add your {completeness.next_priority.display_name}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Overview */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Information Card */}
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Profile Information
                </h2>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-green-400 text-sm">
                    {profile?.profile_completeness.toFixed(1)}% Complete
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-gray-400 text-sm">Full Name</label>
                  <p className="text-white font-medium">{profile?.full_name || 'Not provided'}</p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Phone</label>
                  <p className="text-white font-medium">{profile?.phone || 'Not provided'}</p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Location</label>
                  <p className="text-white font-medium flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    {profile?.location || 'Not provided'}
                  </p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Current Title</label>
                  <p className="text-white font-medium">{profile?.current_title || 'Not provided'}</p>
                </div>
              </div>
            </div>

            {/* Professional Details Card */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2 mb-4">
                <Briefcase className="w-5 h-5" />
                Professional Details
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-gray-400 text-sm">Experience</label>
                  <p className="text-white font-medium">
                    {profile?.years_experience} years ({getExperienceLevelDisplay(profile?.experience_level || '')})
                  </p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Desired Salary</label>
                  <p className="text-white font-medium flex items-center gap-1">
                    <DollarSign className="w-4 h-4" />
                    {formatSalaryRange()}
                  </p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Remote Preference</label>
                  <p className="text-white font-medium">
                    {getRemotePreferenceDisplay(profile?.remote_preference || '')}
                  </p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Willing to Relocate</label>
                  <p className="text-white font-medium">
                    {profile?.willing_to_relocate ? 'Yes' : 'No'}
                  </p>
                </div>
              </div>
            </div>

            {/* Skills Card */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2 mb-4">
                <Award className="w-5 h-5" />
                Skills & Expertise
              </h2>

              {profile?.skills && profile.skills.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {profile.skills.slice(0, 8).map((skill, index) => (
                    <div key={index} className="bg-gray-700 rounded-lg p-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="text-white font-medium">{skill.name}</h4>
                          <p className="text-gray-400 text-sm">
                            {skill.proficiency} • {skill.years} year{skill.years !== 1 ? 's' : ''}
                          </p>
                        </div>
                        <div className="bg-blue-600 text-white text-xs px-2 py-1 rounded">
                          {skill.proficiency}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 text-center py-8">
                  No skills added yet. Add your skills to improve job matching.
                </p>
              )}

              {profile?.skills && profile.skills.length > 8 && (
                <p className="text-gray-400 text-sm mt-4 text-center">
                  +{profile.skills.length - 8} more skills
                </p>
              )}
            </div>

            {/* Links & Profiles */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2 mb-4">
                <ExternalLink className="w-5 h-5" />
                Professional Links
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {profile?.portfolio_url && (
                  <a
                    href={profile.portfolio_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-gray-700 rounded-lg p-3 hover:bg-gray-600 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
                        <FileText className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <p className="text-white font-medium text-sm">Portfolio</p>
                        <p className="text-gray-400 text-xs">View Work</p>
                      </div>
                    </div>
                  </a>
                )}

                {profile?.linkedin_url && (
                  <a
                    href={profile.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-gray-700 rounded-lg p-3 hover:bg-gray-600 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                        <User className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <p className="text-white font-medium text-sm">LinkedIn</p>
                        <p className="text-gray-400 text-xs">Professional</p>
                      </div>
                    </div>
                  </a>
                )}

                {profile?.github_username && (
                  <a
                    href={`https://github.com/${profile.github_username}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-gray-700 rounded-lg p-3 hover:bg-gray-600 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center">
                        <FileText className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <p className="text-white font-medium text-sm">GitHub</p>
                        <p className="text-gray-400 text-xs">Code</p>
                      </div>
                    </div>
                  </a>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Application Analytics */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2 mb-4">
                <BarChart3 className="w-5 h-5" />
                Application Stats
              </h2>

              {analytics ? (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Total Applications</span>
                    <span className="text-white font-semibold">{analytics.total_applications}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Success Rate</span>
                    <span className="text-green-400 font-semibold">{analytics.success_rate.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Avg Response Time</span>
                    <span className="text-white font-semibold">
                      {analytics.average_response_time_days
                        ? `${analytics.average_response_time_days} days`
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Offers Received</span>
                    <span className="text-blue-400 font-semibold">{analytics.successful_applications}</span>
                  </div>
                </div>
              ) : (
                <p className="text-gray-400 text-center py-4">
                  No applications yet. Start applying to track your progress!
                </p>
              )}
            </div>

            {/* Profile Completion */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2 mb-4">
                <Target className="w-5 h-5" />
                Profile Completion
              </h2>

              {completeness && (
                <div className="space-y-4">
                  {/* Progress Circle */}
                  <div className="flex items-center justify-center">
                    <div className="relative w-24 h-24">
                      <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
                        <path
                          className="text-gray-700"
                          d="M18 2.0845
                            a 15.9155 15.9155 0 0 1 0 31.831
                            a 15.9155 15.9155 0 0 1 0 -31.831"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="3"
                        />
                        <path
                          className="text-blue-500"
                          d="M18 2.0845
                            a 15.9155 15.9155 0 0 1 0 31.831
                            a 15.9155 15.9155 0 0 1 0 -31.831"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="3"
                          strokeDasharray={`${completeness.percentage}, 100`}
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-white font-bold text-lg">
                          {completeness.percentage.toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Missing Fields */}
                  {completeness.missing_fields.length > 0 && (
                    <div>
                      <h4 className="text-white font-medium mb-2">Still Needed:</h4>
                      <div className="space-y-2">
                        {completeness.missing_fields.slice(0, 3).map((field, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Circle className="w-3 h-3 text-gray-400" />
                            <span className="text-gray-300 text-sm">{field.display_name}</span>
                            {field.priority === 'high' && (
                              <span className="text-xs bg-red-600 text-white px-1 rounded">
                                High
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Suggestions */}
                  {completeness.suggestions.length > 0 && (
                    <div>
                      <h4 className="text-white font-medium mb-2">Recommendations:</h4>
                      <div className="space-y-1">
                        {completeness.suggestions.slice(0, 2).map((suggestion, index) => (
                          <p key={index} className="text-gray-400 text-sm">
                            • {suggestion}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors text-sm">
                  Update Skills
                </button>
                <button className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors text-sm">
                  Upload New Resume
                </button>
                <button className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors text-sm">
                  Find Jobs
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileDashboard;