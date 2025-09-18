import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Briefcase, MapPin, DollarSign, Clock, Award,
  Plus, X, Edit2, Save, ChevronRight, Target,
  TrendingUp, Users, Building, Globe, Star
} from 'lucide-react';
import { extendedProfileService, type ExtendedUserProfile, type WorkHistoryItem } from '../../services/extendedProfileService';
import { toast } from 'sonner';

export const ProfessionalProfile: React.FC = () => {
  const [profile, setProfile] = useState<ExtendedUserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editingSection, setEditingSection] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<ExtendedUserProfile>>({});
  const [newSkill, setNewSkill] = useState('');
  const [showSkillInput, setShowSkillInput] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await extendedProfileService.getExtendedProfile();
      setProfile(data);
      setFormData(data);
    } catch (error) {
      console.error('Failed to load extended profile:', error);
      // If profile doesn't exist, initialize with defaults
      setFormData({
        full_name: '',
        current_title: '',
        years_experience: 0,
        location: '',
        remote_preference: 'no_preference',
        skills: [],
        work_history: [],
        education: [],
        desired_salary_min: null,
        desired_salary_max: null,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (section?: string) => {
    try {
      const updated = await extendedProfileService.updateExtendedProfile(formData);
      setProfile(updated);
      toast.success(`${section || 'Profile'} updated successfully`);
      setEditingSection(null);
      setEditing(false);
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  const handleAddSkill = async () => {
    if (!newSkill.trim()) return;

    const updatedSkills = [...(formData.skills || []), newSkill.trim()];
    setFormData({ ...formData, skills: updatedSkills });

    try {
      await extendedProfileService.updateSkills(updatedSkills);
      toast.success('Skill added');
      setNewSkill('');
      setShowSkillInput(false);
    } catch (error) {
      toast.error('Failed to add skill');
    }
  };

  const handleRemoveSkill = async (skill: string) => {
    const updatedSkills = (formData.skills || []).filter(s => s !== skill);
    setFormData({ ...formData, skills: updatedSkills });

    try {
      await extendedProfileService.removeSkill(skill);
      toast.success('Skill removed');
    } catch (error) {
      toast.error('Failed to remove skill');
    }
  };

  const getExperienceLevel = (years: number): string => {
    if (years < 2) return 'Entry Level';
    if (years < 5) return 'Mid Level';
    if (years < 10) return 'Senior Level';
    return 'Executive Level';
  };

  const getCompletionColor = (percentage: number): string => {
    if (percentage < 30) return 'bg-red-500';
    if (percentage < 60) return 'bg-yellow-500';
    if (percentage < 90) return 'bg-blue-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Profile Completion Banner */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-xl p-6 border border-purple-500/30"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold text-white mb-2">Profile Completion</h3>
            <p className="text-gray-400">Complete your profile to get better job matches</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-white mb-1">
              {Math.round(profile?.profile_completeness || 0)}%
            </div>
            <p className="text-sm text-gray-400">Complete</p>
          </div>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${getCompletionColor(profile?.profile_completeness || 0)}`}
            style={{ width: `${profile?.profile_completeness || 0}%` }}
          />
        </div>
      </motion.div>

      {/* Professional Summary */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white">Professional Summary</h3>
          {editingSection !== 'summary' ? (
            <button
              onClick={() => setEditingSection('summary')}
              className="text-purple-400 hover:text-purple-300"
            >
              <Edit2 className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={() => handleSave('summary')}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              <Save className="w-4 h-4" />
              Save
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-gray-400 mb-2">Current Title</label>
            <input
              type="text"
              value={formData.current_title || ''}
              onChange={(e) => setFormData({ ...formData, current_title: e.target.value })}
              disabled={editingSection !== 'summary'}
              placeholder="e.g., Senior Software Engineer"
              className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-gray-400 mb-2">Years of Experience</label>
            <input
              type="number"
              value={formData.years_experience || 0}
              onChange={(e) => setFormData({ ...formData, years_experience: parseInt(e.target.value) || 0 })}
              disabled={editingSection !== 'summary'}
              className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-gray-400 mb-2">Location</label>
            <input
              type="text"
              value={formData.location || ''}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              disabled={editingSection !== 'summary'}
              placeholder="e.g., San Francisco, CA"
              className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-gray-400 mb-2">Remote Preference</label>
            <select
              value={formData.remote_preference || 'no_preference'}
              onChange={(e) => setFormData({ ...formData, remote_preference: e.target.value as any })}
              disabled={editingSection !== 'summary'}
              className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
            >
              <option value="remote">Remote Only</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">On-site</option>
              <option value="no_preference">No Preference</option>
            </select>
          </div>
        </div>

        {/* Experience Level Badge */}
        <div className="mt-6 flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Award className="w-5 h-5 text-yellow-500" />
            <span className="text-gray-400">Experience Level:</span>
            <span className="px-3 py-1 bg-purple-600/20 text-purple-400 rounded-full text-sm font-semibold">
              {getExperienceLevel(formData.years_experience || 0)}
            </span>
          </div>
        </div>
      </div>

      {/* Salary Expectations */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-green-500" />
            Salary Expectations
          </h3>
          {editingSection !== 'salary' ? (
            <button
              onClick={() => setEditingSection('salary')}
              className="text-purple-400 hover:text-purple-300"
            >
              <Edit2 className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={() => handleSave('salary')}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              <Save className="w-4 h-4" />
              Save
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-gray-400 mb-2">Minimum Salary (Annual)</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">$</span>
              <input
                type="number"
                value={formData.desired_salary_min || ''}
                onChange={(e) => setFormData({ ...formData, desired_salary_min: parseInt(e.target.value) || null })}
                disabled={editingSection !== 'salary'}
                placeholder="120000"
                className="w-full pl-8 pr-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
              />
            </div>
          </div>

          <div>
            <label className="block text-gray-400 mb-2">Maximum Salary (Annual)</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">$</span>
              <input
                type="number"
                value={formData.desired_salary_max || ''}
                onChange={(e) => setFormData({ ...formData, desired_salary_max: parseInt(e.target.value) || null })}
                disabled={editingSection !== 'salary'}
                placeholder="160000"
                className="w-full pl-8 pr-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
              />
            </div>
          </div>
        </div>

        {formData.desired_salary_min && formData.desired_salary_max && (
          <div className="mt-4 p-4 bg-gray-900/50 rounded-lg">
            <p className="text-gray-400 text-sm">Expected Range:</p>
            <p className="text-xl font-semibold text-white">
              ${formData.desired_salary_min?.toLocaleString()} - ${formData.desired_salary_max?.toLocaleString()}
            </p>
          </div>
        )}
      </div>

      {/* Skills Section */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Star className="w-5 h-5 text-yellow-500" />
            Skills & Expertise
          </h3>
          <button
            onClick={() => setShowSkillInput(true)}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            <Plus className="w-4 h-4" />
            Add Skill
          </button>
        </div>

        {showSkillInput && (
          <div className="mb-4 flex gap-2">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
              placeholder="Enter a skill..."
              className="flex-1 px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
              autoFocus
            />
            <button
              onClick={handleAddSkill}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Add
            </button>
            <button
              onClick={() => {
                setShowSkillInput(false);
                setNewSkill('');
              }}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
            >
              Cancel
            </button>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {(formData.skills || []).map((skill, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="group relative px-4 py-2 bg-purple-600/20 text-purple-400 rounded-full border border-purple-500/30 hover:border-purple-500/50"
            >
              {skill}
              <button
                onClick={() => handleRemoveSkill(skill)}
                className="absolute -top-1 -right-1 w-5 h-5 bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
              >
                <X className="w-3 h-3" />
              </button>
            </motion.div>
          ))}
          {(!formData.skills || formData.skills.length === 0) && (
            <p className="text-gray-500 italic">No skills added yet. Add your skills to improve job matching!</p>
          )}
        </div>
      </div>

      {/* Work History */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-blue-500" />
            Work History
          </h3>
          <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            <Plus className="w-4 h-4" />
            Add Position
          </button>
        </div>

        {(!formData.work_history || formData.work_history.length === 0) && (
          <div className="text-center py-8">
            <Briefcase className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-500">No work history added yet</p>
            <p className="text-gray-600 text-sm mt-1">Add your work experience to strengthen your profile</p>
          </div>
        )}
      </div>

      {/* AI Job Application Settings */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-purple-500" />
            AI Job Application Settings
          </h3>
          <button
            onClick={() => setEditingSection(editingSection === 'ai_settings' ? null : 'ai_settings')}
            className="text-purple-400 hover:text-purple-300"
          >
            <Edit2 className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Auto Apply Toggle */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white font-medium">Auto Apply</p>
              <p className="text-gray-400 text-sm">Automatically apply to matched jobs</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={formData.job_preferences?.auto_apply || false}
                onChange={(e) => setFormData({
                  ...formData,
                  job_preferences: {
                    ...formData.job_preferences,
                    auto_apply: e.target.checked
                  }
                })}
                disabled={editingSection !== 'ai_settings'}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>

          {/* Match Score Threshold */}
          <div>
            <p className="text-white font-medium mb-2">Min Match Score</p>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0"
                max="100"
                value={(formData.job_preferences?.min_match_score || 0.7) * 100}
                onChange={(e) => setFormData({
                  ...formData,
                  job_preferences: {
                    ...formData.job_preferences,
                    min_match_score: parseInt(e.target.value) / 100
                  }
                })}
                disabled={editingSection !== 'ai_settings'}
                className="flex-1"
              />
              <span className="text-purple-400 font-medium w-12">
                {Math.round((formData.job_preferences?.min_match_score || 0.7) * 100)}%
              </span>
            </div>
          </div>

          {/* Application Tone */}
          <div>
            <p className="text-white font-medium mb-2">Application Tone</p>
            <select
              value={formData.job_preferences?.application_tone || 'professional'}
              onChange={(e) => setFormData({
                ...formData,
                job_preferences: {
                  ...formData.job_preferences,
                  application_tone: e.target.value as any
                }
              })}
              disabled={editingSection !== 'ai_settings'}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
            >
              <option value="professional">Professional</option>
              <option value="friendly">Friendly</option>
              <option value="enthusiastic">Enthusiastic</option>
              <option value="formal">Formal</option>
            </select>
          </div>

          {/* Max Applications Per Day */}
          <div>
            <p className="text-white font-medium mb-2">Max Applications/Day</p>
            <input
              type="number"
              min="1"
              max="50"
              value={formData.job_preferences?.max_applications_per_day || 10}
              onChange={(e) => setFormData({
                ...formData,
                job_preferences: {
                  ...formData.job_preferences,
                  max_applications_per_day: parseInt(e.target.value)
                }
              })}
              disabled={editingSection !== 'ai_settings'}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
            />
          </div>
        </div>

        {editingSection === 'ai_settings' && (
          <div className="mt-4 flex justify-end">
            <button
              onClick={() => handleSave('AI Settings')}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save Settings
            </button>
          </div>
        )}
      </div>

      {/* Professional Summary */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Award className="w-5 h-5 text-yellow-500" />
            Professional Summary
          </h3>
          <button
            onClick={() => setEditingSection(editingSection === 'summary' ? null : 'summary')}
            className="text-purple-400 hover:text-purple-300"
          >
            <Edit2 className="w-4 h-4" />
          </button>
        </div>

        {editingSection === 'summary' ? (
          <div>
            <textarea
              value={formData.professional_summary || ''}
              onChange={(e) => setFormData({ ...formData, professional_summary: e.target.value })}
              placeholder="Write a compelling professional summary that highlights your key strengths and career objectives..."
              rows={6}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none resize-none"
            />
            <div className="mt-4 flex justify-end gap-2">
              <button
                onClick={() => setEditingSection(null)}
                className="px-4 py-2 text-gray-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={() => handleSave('Professional Summary')}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                Save
              </button>
            </div>
          </div>
        ) : (
          <p className="text-gray-300">
            {formData.professional_summary ||
            <span className="text-gray-500 italic">Add a professional summary to make your profile stand out to potential employers.</span>}
          </p>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => window.location.href = '/ai-job-tracker'}
          className="p-4 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl text-white font-semibold hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
        >
          <Target className="w-5 h-5" />
          Go to AI Job Tracker
        </button>
        <button className="p-4 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl text-white font-semibold hover:opacity-90 transition-opacity flex items-center justify-center gap-2">
          <TrendingUp className="w-5 h-5" />
          Optimize Profile
        </button>
        <button className="p-4 bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl text-white font-semibold hover:opacity-90 transition-opacity flex items-center justify-center gap-2">
          <Users className="w-5 h-5" />
          Export Resume
        </button>
      </div>
    </div>
  );
};