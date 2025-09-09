import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  User, Mail, MapPin, Briefcase, Settings, 
  Save, Camera, Trash2, Lock, Bell, Moon, 
  Download, CreditCard, HardDrive, Award,
  BookOpen, FileText, Image, Video, TrendingUp
} from 'lucide-react';
import { profileService, type UserProfile, type UserStats } from '../../services/profileService';

interface ProfileUpdateData {
  first_name?: string;
  last_name?: string;
  email?: string;
  bio?: string;
  display_name?: string;
  occupation?: string;
  location?: string;
  preferred_ai_model?: string;
  default_content_tone?: string;
  auto_save?: boolean;
  dark_mode?: boolean;
  email_notifications?: boolean;
  default_citation_style?: string;
  preferred_book_length?: string;
  research_topics?: string[];
}
import { useAuthStore } from '../../store/authStore';
import { toast } from 'sonner';

export const ProfilePage: React.FC = () => {
  const { user, setToken } = useAuthStore();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [activeTab, setActiveTab] = useState<'profile' | 'settings' | 'stats'>('profile');
  const [formData, setFormData] = useState<ProfileUpdateData>({});
  const [passwordData, setPasswordData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  useEffect(() => {
    loadProfile();
    loadStats();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await profileService.getProfile();
      setProfile(data);
      setFormData({
        first_name: data.user.first_name,
        last_name: data.user.last_name,
        email: data.user.email,
        bio: data.profile.bio,
        display_name: data.profile.display_name,
        occupation: data.profile.occupation,
        location: data.profile.location,
      });
    } catch (error) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await profileService.getUserStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleSaveProfile = async () => {
    try {
      await profileService.updateProfile(formData);
      toast.success('Profile updated successfully');
      setEditing(false);
      loadProfile();
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB');
      return;
    }

    try {
      const result = await profileService.uploadAvatar(file);
      toast.success('Avatar uploaded successfully');
      loadProfile();
    } catch (error) {
      toast.error('Failed to upload avatar');
    }
  };

  const handleDeleteAvatar = async () => {
    if (!confirm('Are you sure you want to delete your avatar?')) return;
    
    try {
      await profileService.deleteAvatar();
      toast.success('Avatar deleted');
      loadProfile();
    } catch (error) {
      toast.error('Failed to delete avatar');
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (passwordData.newPassword.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    try {
      const result = await profileService.changePassword(
        passwordData.oldPassword,
        passwordData.newPassword
      );
      setToken(result.token);
      localStorage.setItem('authToken', result.token);
      toast.success('Password changed successfully');
      setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      toast.error('Failed to change password');
    }
  };

  const handleSettingToggle = async (setting: string, value: boolean | string) => {
    try {
      await profileService.updateProfile({ [setting]: value } as any);
      toast.success('Setting updated');
      loadProfile();
    } catch (error) {
      toast.error('Failed to update setting');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-white mb-2">Failed to load profile</h2>
          <p className="text-gray-400">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Account Settings</h1>
        <p className="text-gray-400">Manage your profile and preferences</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-8 bg-gray-800/50 p-1 rounded-lg w-fit">
        {['profile', 'settings', 'stats'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-6 py-2 rounded-md transition-all capitalize ${
              activeTab === tab
                ? 'bg-purple-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Avatar Section */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Profile Picture</h3>
              
              <div className="relative w-32 h-32 mx-auto mb-4">
                {profile.profile.avatar ? (
                  <img
                    src={profile.profile.avatar}
                    alt="Avatar"
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                    <span className="text-4xl font-bold text-white">
                      {profile.user.username[0].toUpperCase()}
                    </span>
                  </div>
                )}
                
                <label className="absolute bottom-0 right-0 bg-purple-600 p-2 rounded-full cursor-pointer hover:bg-purple-700 transition-colors">
                  <Camera className="w-4 h-4 text-white" />
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                    className="hidden"
                  />
                </label>
              </div>

              {profile.profile.avatar && (
                <button
                  onClick={handleDeleteAvatar}
                  className="w-full py-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors flex items-center justify-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Remove Avatar
                </button>
              )}

              {/* Account Info */}
              <div className="mt-6 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Account Type</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    profile.profile.account_type === 'pro' 
                      ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-black'
                      : profile.profile.account_type === 'enterprise'
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                      : 'bg-gray-700 text-gray-300'
                  }`}>
                    {profile.profile.account_type.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Credits</span>
                  <span className="text-white font-semibold">{profile.profile.credits_remaining}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Storage Used</span>
                  <span className="text-white">{profile.profile.storage_used_mb} MB</span>
                </div>
              </div>
            </div>
          </div>

          {/* Profile Form */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">Profile Information</h3>
                {!editing ? (
                  <button
                    onClick={() => setEditing(true)}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    Edit Profile
                  </button>
                ) : (
                  <div className="flex gap-2">
                    <button
                      onClick={() => setEditing(false)}
                      className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveProfile}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
                    >
                      <Save className="w-4 h-4" />
                      Save Changes
                    </button>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-400 mb-2">First Name</label>
                  <input
                    type="text"
                    value={formData.first_name || ''}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    disabled={!editing}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>
                
                <div>
                  <label className="block text-gray-400 mb-2">Last Name</label>
                  <input
                    type="text"
                    value={formData.last_name || ''}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    disabled={!editing}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Display Name</label>
                  <input
                    type="text"
                    value={formData.display_name || ''}
                    onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                    disabled={!editing}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Email</label>
                  <input
                    type="email"
                    value={formData.email || ''}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    disabled={!editing}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Occupation</label>
                  <input
                    type="text"
                    value={formData.occupation || ''}
                    onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                    disabled={!editing}
                    placeholder="e.g., Content Creator"
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Location</label>
                  <input
                    type="text"
                    value={formData.location || ''}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    disabled={!editing}
                    placeholder="e.g., San Francisco, CA"
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-gray-400 mb-2">Bio</label>
                  <textarea
                    value={formData.bio || ''}
                    onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                    disabled={!editing}
                    rows={4}
                    placeholder="Tell us about yourself..."
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Preferences */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-6">Preferences</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Moon className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-white">Dark Mode</p>
                    <p className="text-sm text-gray-400">Use dark theme</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={profile.profile.dark_mode}
                    onChange={(e) => handleSettingToggle('dark_mode', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Bell className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-white">Email Notifications</p>
                    <p className="text-sm text-gray-400">Receive email updates</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={profile.profile.email_notifications}
                    onChange={(e) => handleSettingToggle('email_notifications', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Save className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-white">Auto-Save</p>
                    <p className="text-sm text-gray-400">Automatically save drafts</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={profile.profile.auto_save}
                    onChange={(e) => handleSettingToggle('auto_save', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-700">
              <h4 className="text-white font-medium mb-4">Content Preferences</h4>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-400 mb-2">Default AI Model</label>
                  <select
                    value={profile.profile.preferred_ai_model}
                    onChange={(e) => handleSettingToggle('preferred_ai_model', e.target.value)}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="claude">Claude</option>
                    <option value="gemini">Gemini</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Default Content Tone</label>
                  <select
                    value={profile.profile.default_content_tone}
                    onChange={(e) => handleSettingToggle('default_content_tone', e.target.value)}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="friendly">Friendly</option>
                    <option value="technical">Technical</option>
                    <option value="creative">Creative</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Citation Style</label>
                  <select
                    value={profile.profile.default_citation_style}
                    onChange={(e) => handleSettingToggle('default_citation_style', e.target.value)}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                  >
                    <option value="APA">APA</option>
                    <option value="MLA">MLA</option>
                    <option value="Chicago">Chicago</option>
                    <option value="Harvard">Harvard</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Security */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-6">Security</h3>
            
            <div className="space-y-4">
              <h4 className="text-white font-medium">Change Password</h4>
              
              <div>
                <label className="block text-gray-400 mb-2">Current Password</label>
                <input
                  type="password"
                  value={passwordData.oldPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, oldPassword: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-2">New Password</label>
                <input
                  type="password"
                  value={passwordData.newPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-2">Confirm New Password</label>
                <input
                  type="password"
                  value={passwordData.confirmPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                />
              </div>

              <button
                onClick={handleChangePassword}
                disabled={!passwordData.oldPassword || !passwordData.newPassword}
                className="w-full py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Lock className="w-4 h-4" />
                Update Password
              </button>
            </div>

            <div className="mt-8 pt-6 border-t border-gray-700">
              <h4 className="text-white font-medium mb-4">Account Info</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Username</span>
                  <span className="text-white">{profile.user.username}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Member Since</span>
                  <span className="text-white">
                    {new Date(profile.user.date_joined).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Last Active</span>
                  <span className="text-white">
                    {new Date(profile.profile.last_active).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Tab */}
      {activeTab === 'stats' && stats && (
        <div className="space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Contents', value: stats.content_breakdown.texts || 0, icon: FileText, color: 'from-blue-500 to-cyan-500' },
              { label: 'Images Created', value: stats.content_breakdown.images || 0, icon: Image, color: 'from-purple-500 to-pink-500' },
              { label: 'Videos Generated', value: stats.content_breakdown.saved_videos || 0, icon: Video, color: 'from-green-500 to-emerald-500' },
              { label: 'Blogs Written', value: stats.content_breakdown.blogs || 0, icon: BookOpen, color: 'from-orange-500 to-red-500' },
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700"
              >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${stat.color} p-2.5 mb-4`}>
                  <stat.icon className="w-full h-full text-white" />
                </div>
                <p className="text-3xl font-bold text-white mb-1">{stat.value}</p>
                <p className="text-gray-400 text-sm">{stat.label}</p>
              </motion.div>
            ))}
          </div>

          {/* Activity Chart */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-900/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-green-500" />
                  <span className="text-gray-400">Last 7 Days</span>
                </div>
                <p className="text-2xl font-bold text-white">{stats.recent_activity.last_7_days}</p>
                <p className="text-sm text-gray-500">items created</p>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-blue-500" />
                  <span className="text-gray-400">Last 30 Days</span>
                </div>
                <p className="text-2xl font-bold text-white">{stats.recent_activity.last_30_days}</p>
                <p className="text-sm text-gray-500">items created</p>
              </div>
            </div>
          </div>

          {/* Top Styles & Storage */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Styles */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Top Styles Used</h3>
              <div className="space-y-3">
                {stats.top_styles.slice(0, 5).map((style, index) => {
                  const styleName = style.style || style['metadata__style'] || 'Default';
                  const maxCount = stats.top_styles[0]?.count || 1;
                  return (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-gray-300">{styleName}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                            style={{ width: `${(style.count / maxCount) * 100}%` }}
                          />
                        </div>
                        <span className="text-white font-medium w-8 text-right">{style.count}</span>
                      </div>
                    </div>
                  );
                })}
                {stats.top_styles.length === 0 && (
                  <p className="text-gray-500 text-center py-4">No style data available yet</p>
                )}
              </div>
            </div>

            {/* Storage Usage */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Storage Usage</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-gray-400">Images</span>
                    <span className="text-white">{stats.storage.images_mb} MB</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full"
                      style={{ width: `${stats.storage.total_mb > 0 ? (stats.storage.images_mb / stats.storage.total_mb) * 100 : 0}%` }}
                    />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-gray-400">Videos</span>
                    <span className="text-white">{stats.storage.videos_mb} MB</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                      style={{ width: `${stats.storage.total_mb > 0 ? (stats.storage.videos_mb / stats.storage.total_mb) * 100 : 0}%` }}
                    />
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-700">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <HardDrive className="w-5 h-5 text-gray-400" />
                      <span className="text-gray-400">Total Storage</span>
                    </div>
                    <span className="text-xl font-bold text-white">{stats.storage.total_mb} MB</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};