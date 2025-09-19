import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain, Sparkles, Zap, Settings, Info, TrendingUp,
  BarChart3, Lightbulb, X, ChevronRight
} from 'lucide-react';
import { promptingService } from '../../services/promptingService';
import toast from 'react-hot-toast';

interface AISettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AISettingsModal: React.FC<AISettingsModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'settings' | 'stats' | 'test'>('settings');
  const [settings, setSettings] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Test enhancement state
  const [testPrompt, setTestPrompt] = useState('');
  const [testLevel, setTestLevel] = useState('advanced');
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [settingsData, statsData] = await Promise.all([
        promptingService.getSettings(),
        promptingService.getStats(30)
      ]);
      setSettings(settingsData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load AI settings:', error);
      toast.error('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      await promptingService.updateSettings(settings);
      toast.success('AI settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleTestEnhancement = async () => {
    if (!testPrompt) {
      toast.error('Please enter a prompt to test');
      return;
    }

    setTesting(true);
    try {
      const result = await promptingService.testEnhancement({
        prompt: testPrompt,
        level: testLevel,
        content_type: 'blog',
        use_memory: settings?.use_memory || false
      });
      setTestResult(result);
    } catch (error) {
      toast.error('Enhancement test failed');
    } finally {
      setTesting(false);
    }
  };

  const toggleSetting = (key: string, value?: any) => {
    if (key.includes('.')) {
      // Handle nested settings
      const [parent, child] = key.split('.');
      setSettings({
        ...settings,
        [parent]: {
          ...settings[parent],
          [child]: value !== undefined ? value : !settings[parent][child]
        }
      });
    } else {
      setSettings({
        ...settings,
        [key]: value !== undefined ? value : !settings[key]
      });
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/90 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-black border-2 border-cyan-500/50 rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden relative shadow-[0_0_20px_rgba(0,255,255,0.3)] shadow-cyan-500/30 before:absolute before:inset-0 before:border-2 before:border-cyan-500/30 before:rounded-lg before:animate-pulse"
          >
          {/* Gaming corner decorations */}
          <div className="absolute top-2 left-2 w-3 h-3 border-l-2 border-t-2 border-cyan-500 z-10" />
          <div className="absolute top-2 right-2 w-3 h-3 border-r-2 border-t-2 border-cyan-500 z-10" />
          <div className="absolute bottom-2 left-2 w-3 h-3 border-l-2 border-b-2 border-cyan-500 z-10" />
          <div className="absolute bottom-2 right-2 w-3 h-3 border-r-2 border-b-2 border-cyan-500 z-10" />
          
          {/* Gaming Header */}
          <div className="bg-gradient-to-r from-black to-gray-900 p-6 border-b border-cyan-500/30 relative">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-cyan-500/20 rounded-lg border border-cyan-500/50">
                  <Brain className="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-cyan-400 uppercase font-mono tracking-wider drop-shadow-[0_0_8px_rgba(0,255,255,0.5)]">NEURAL AI SETTINGS</h2>
                  <p className="text-muted-foreground text-sm mt-1 font-mono">
                    Configure how AI enhances your content generation
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-cyan-500/20 rounded-lg transition-all duration-200 hover:text-cyan-400 hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.5)] hover:scale-110 border border-transparent hover:border-cyan-500/50"
              >
                <X className="w-5 h-5 text-muted-foreground" />
              </button>
            </div>

            {/* Gaming Tabs */}
            <div className="flex gap-2 mt-6 relative">
              {/* Subtle glow line */}
              <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500 to-transparent" />
              {[
                { id: 'settings', label: 'SETTINGS', icon: Settings },
                { id: 'stats', label: 'STATISTICS', icon: BarChart3 },
                { id: 'test', label: 'TEST LAB', icon: Sparkles }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all font-mono uppercase tracking-wider ${
                    activeTab === tab.id
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 shadow-[0_0_10px_rgba(0,255,255,0.3)]'
                      : 'bg-background/50 text-muted-foreground hover:bg-card/50 hover:text-cyan-300 border border-transparent hover:border-cyan-500/30'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(80vh - 180px)' }}>
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
              </div>
            ) : (
              <>
                {/* Settings Tab */}
                {activeTab === 'settings' && settings && (
                  <div className="space-y-6">
                    {/* Master Toggle */}
                    <div className="bg-background/50 rounded-lg p-6 border border-cyan-500/30 relative">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-4">
                          <div className="p-2 bg-cyan-500/20 rounded-lg mt-1 border border-cyan-500/50">
                            <Zap className="w-5 h-5 text-cyan-400" />
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-cyan-400 mb-1 uppercase font-mono tracking-wider">
                              INTELLIGENT PROMPTING
                            </h3>
                            <p className="text-muted-foreground text-sm font-mono">
                              Automatically enhance your prompts for better AI responses
                            </p>
                          </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={settings.enabled}
                            onChange={() => toggleSetting('enabled')}
                            className="sr-only peer"
                          />
                          <div className="w-14 h-7 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-cyan-500 border border-cyan-500/30"></div>
                        </label>
                      </div>
                    </div>

                    {/* Enhancement Level */}
                    <div className="bg-background/50 rounded-lg p-6 border border-cyan-500/30 relative">
                      <h3 className="text-lg font-semibold text-cyan-400 mb-4 uppercase font-mono tracking-wider">ENHANCEMENT LEVEL</h3>
                      <div className="grid grid-cols-3 gap-3">
                        {[
                          { 
                            level: 'basic', 
                            label: 'Basic', 
                            description: 'Simple improvements',
                            icon: '⚡' 
                          },
                          { 
                            level: 'advanced', 
                            label: 'Advanced', 
                            description: 'Smart optimization',
                            icon: '🚀' 
                          },
                          { 
                            level: 'expert', 
                            label: 'Expert', 
                            description: 'Maximum intelligence',
                            icon: '🧠' 
                          }
                        ].map((option) => (
                          <button
                            key={option.level}
                            onClick={() => toggleSetting('default_level', option.level)}
                            className={`p-4 rounded-lg border transition-all ${
                              settings.default_level === option.level
                                ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400 shadow-[0_0_10px_rgba(0,255,255,0.3)]'
                                : 'bg-background/50 border-gray-700 text-muted-foreground hover:border-cyan-500/50 hover:text-cyan-300'
                            }`}
                          >
                            <div className="text-2xl mb-2">{option.icon}</div>
                            <div className="font-medium">{option.label}</div>
                            <div className="text-xs mt-1 opacity-80">{option.description}</div>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Additional Options */}
                    <div className="bg-card/50 rounded-xl p-6 border border-gray-700 space-y-4">
                      <h3 className="text-lg font-semibold text-foreground mb-4">Enhancement Options</h3>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="p-1.5 bg-blue-600/20 rounded">
                            <Brain className="w-4 h-4 text-blue-500" />
                          </div>
                          <div>
                            <p className="text-foreground font-medium">Use Memory Context</p>
                            <p className="text-muted-foreground text-xs">Include previous interactions for consistency</p>
                          </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={settings.use_memory}
                            onChange={() => toggleSetting('use_memory')}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="p-1.5 bg-green-600/20 rounded">
                            <Sparkles className="w-4 h-4 text-green-500" />
                          </div>
                          <div>
                            <p className="text-foreground font-medium">Auto-Enhance</p>
                            <p className="text-muted-foreground text-xs">Automatically enhance all prompts</p>
                          </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={settings.auto_enhance}
                            onChange={() => toggleSetting('auto_enhance')}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                        </label>
                      </div>
                    </div>

                    {/* Content-Specific Settings */}
                    <div className="bg-card/50 rounded-xl p-6 border border-gray-700">
                      <h3 className="text-lg font-semibold text-foreground mb-4">Content-Specific Enhancement</h3>
                      <div className="grid grid-cols-2 gap-3">
                        {Object.entries(settings.content_preferences || {}).map(([type, enabled]) => (
                          <div key={type} className="flex items-center justify-between p-3 bg-background/50 rounded-lg">
                            <span className="text-muted-foreground capitalize">{type}</span>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={enabled as boolean}
                                onChange={() => toggleSetting(`content_preferences.${type}`)}
                                className="sr-only peer"
                              />
                              <div className="w-9 h-5 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-purple-600"></div>
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Statistics Tab */}
                {activeTab === 'stats' && stats && (
                  <div className="space-y-6">
                    {/* Overview Cards */}
                    <div className="grid grid-cols-4 gap-4">
                      <div className="bg-card/50 rounded-xl p-4 border border-gray-700">
                        <div className="flex items-center gap-2 mb-2">
                          <TrendingUp className="w-4 h-4 text-green-500" />
                          <span className="text-muted-foreground text-sm">Enhancement Rate</span>
                        </div>
                        <p className="text-2xl font-bold text-foreground">
                          {stats.overview?.enhancement_rate?.toFixed(1) || 0}%
                        </p>
                      </div>
                      
                      <div className="bg-card/50 rounded-xl p-4 border border-gray-700">
                        <div className="flex items-center gap-2 mb-2">
                          <Brain className="w-4 h-4 text-blue-500" />
                          <span className="text-muted-foreground text-sm">Memory Usage</span>
                        </div>
                        <p className="text-2xl font-bold text-foreground">
                          {stats.overview?.memory_usage_rate?.toFixed(1) || 0}%
                        </p>
                      </div>
                      
                      <div className="bg-card/50 rounded-xl p-4 border border-gray-700">
                        <div className="flex items-center gap-2 mb-2">
                          <Sparkles className="w-4 h-4 text-purple-500" />
                          <span className="text-muted-foreground text-sm">Enhanced Content</span>
                        </div>
                        <p className="text-2xl font-bold text-foreground">
                          {stats.overview?.enhanced_content || 0}
                        </p>
                      </div>
                      
                      <div className="bg-card/50 rounded-xl p-4 border border-gray-700">
                        <div className="flex items-center gap-2 mb-2">
                          <Zap className="w-4 h-4 text-yellow-500" />
                          <span className="text-muted-foreground text-sm">Total Content</span>
                        </div>
                        <p className="text-2xl font-bold text-foreground">
                          {stats.overview?.total_content || 0}
                        </p>
                      </div>
                    </div>

                    {/* Enhancement by Level */}
                    <div className="bg-card/50 rounded-xl p-6 border border-gray-700">
                      <h3 className="text-lg font-semibold text-foreground mb-4">Enhancement by Level</h3>
                      <div className="space-y-3">
                        {Object.entries(stats.by_level || {}).map(([level, count]) => (
                          <div key={level} className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className={`w-2 h-2 rounded-full ${
                                level === 'expert' ? 'bg-purple-500' :
                                level === 'advanced' ? 'bg-blue-500' : 'bg-green-500'
                              }`} />
                              <span className="text-muted-foreground capitalize">{level}</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <div className="w-32 bg-gray-700 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full ${
                                    level === 'expert' ? 'bg-purple-500' :
                                    level === 'advanced' ? 'bg-blue-500' : 'bg-green-500'
                                  }`}
                                  style={{ 
                                    width: `${((count as number) / stats.overview?.total_content) * 100}%` 
                                  }}
                                />
                              </div>
                              <span className="text-foreground font-medium w-12 text-right">
                                {count as number}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Content Type Usage */}
                    <div className="bg-card/50 rounded-xl p-6 border border-gray-700">
                      <h3 className="text-lg font-semibold text-foreground mb-4">Enhancement by Content Type</h3>
                      <div className="grid grid-cols-2 gap-4">
                        {Object.entries(stats.by_content_type || {}).map(([type, data]: [string, any]) => (
                          <div key={type} className="bg-background/50 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-muted-foreground capitalize font-medium">{type}</span>
                              <span className="text-xs text-purple-400">
                                {data.total > 0 ? ((data.enhanced / data.total) * 100).toFixed(0) : 0}%
                              </span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                              <span className="text-muted-foreground">Enhanced:</span>
                              <span className="text-foreground">{data.enhanced}</span>
                              <span className="text-muted-foreground">/</span>
                              <span className="text-muted-foreground">{data.total}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Test Lab Tab */}
                {activeTab === 'test' && (
                  <div className="space-y-6">
                    <div className="bg-card/50 rounded-xl p-6 border border-gray-700">
                      <h3 className="text-lg font-semibold text-foreground mb-4">Test Prompt Enhancement</h3>
                      
                      <div className="space-y-4">
                        <div>
                          <label className="block text-muted-foreground text-sm mb-2">Your Prompt</label>
                          <textarea
                            value={testPrompt}
                            onChange={(e) => setTestPrompt(e.target.value)}
                            placeholder="Enter a prompt to see how it gets enhanced..."
                            className="w-full px-4 py-3 bg-background/50 border border-gray-700 rounded-lg text-foreground placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                            rows={3}
                          />
                        </div>

                        <div>
                          <label className="block text-muted-foreground text-sm mb-2">Enhancement Level</label>
                          <select
                            value={testLevel}
                            onChange={(e) => setTestLevel(e.target.value)}
                            className="w-full px-4 py-2 bg-background/50 border border-gray-700 rounded-lg text-foreground focus:border-purple-500 focus:outline-none"
                          >
                            <option value="basic">Basic</option>
                            <option value="advanced">Advanced</option>
                            <option value="expert">Expert</option>
                          </select>
                        </div>

                        <button
                          onClick={handleTestEnhancement}
                          disabled={testing}
                          className="px-6 py-2 bg-gradient-to-r from-cyan-600 to-purple-600 text-foreground rounded-lg hover:from-cyan-700 hover:to-purple-700 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed font-mono uppercase tracking-wider border border-cyan-500/50 shadow-[0_0_10px_rgba(0,255,255,0.3)]"
                        >
                          {testing ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                              EXECUTING...
                            </>
                          ) : (
                            <>
                              <Sparkles className="w-4 h-4" />
                              EXECUTE TEST
                            </>
                          )}
                        </button>
                      </div>

                      {testResult && (
                        <div className="mt-6 space-y-4">
                          <div className="p-4 bg-background/50 rounded-lg border border-gray-700">
                            <h4 className="text-sm font-medium text-muted-foreground mb-2">Enhanced Prompt</h4>
                            <p className="text-foreground whitespace-pre-wrap">{testResult.enhanced}</p>
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div className="p-3 bg-background/50 rounded-lg">
                              <p className="text-xs text-muted-foreground mb-1">Techniques Applied</p>
                              <div className="flex flex-wrap gap-1">
                                {testResult.techniques?.map((tech: string) => (
                                  <span key={tech} className="px-2 py-1 bg-purple-600/20 text-purple-400 text-xs rounded">
                                    {tech}
                                  </span>
                                ))}
                              </div>
                            </div>
                            <div className="p-3 bg-background/50 rounded-lg">
                              <p className="text-xs text-muted-foreground mb-1">Memory Context</p>
                              <p className="text-foreground font-medium">{testResult.memory_context} items</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Suggestions */}
                    <div className="bg-card/50 rounded-xl p-6 border border-gray-700">
                      <div className="flex items-center gap-2 mb-4">
                        <Lightbulb className="w-5 h-5 text-yellow-500" />
                        <h3 className="text-lg font-semibold text-foreground">Pro Tips</h3>
                      </div>
                      <ul className="space-y-2">
                        <li className="flex items-start gap-2">
                          <ChevronRight className="w-4 h-4 text-purple-400 mt-0.5" />
                          <p className="text-muted-foreground text-sm">
                            Use <span className="text-purple-400 font-medium">Expert level</span> for complex, nuanced content that requires deep reasoning
                          </p>
                        </li>
                        <li className="flex items-start gap-2">
                          <ChevronRight className="w-4 h-4 text-purple-400 mt-0.5" />
                          <p className="text-muted-foreground text-sm">
                            Enable <span className="text-purple-400 font-medium">Memory Context</span> to maintain consistency across related content
                          </p>
                        </li>
                        <li className="flex items-start gap-2">
                          <ChevronRight className="w-4 h-4 text-purple-400 mt-0.5" />
                          <p className="text-muted-foreground text-sm">
                            <span className="text-purple-400 font-medium">Advanced level</span> provides the best balance between quality and speed
                          </p>
                        </li>
                        <li className="flex items-start gap-2">
                          <ChevronRight className="w-4 h-4 text-purple-400 mt-0.5" />
                          <p className="text-muted-foreground text-sm">
                            Review enhanced prompts to learn how to write better prompts yourself
                          </p>
                        </li>
                      </ul>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Footer */}
          {activeTab === 'settings' && !loading && (
            <div className="p-6 border-t border-gray-800 bg-background/50">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  Changes are saved automatically
                </p>
                <button
                  onClick={handleSaveSettings}
                  disabled={saving}
                  className="px-6 py-2 bg-gradient-to-r from-cyan-600 to-purple-600 text-foreground rounded-lg hover:from-cyan-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-mono uppercase tracking-wider border border-cyan-500/50 shadow-[0_0_10px_rgba(0,255,255,0.3)]"
                >
                  {saving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                      SAVING...
                    </>
                  ) : (
                    <>
                      <Settings className="w-4 h-4" />
                      SAVE SETTINGS
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
          </motion.div>
        </div>
      )}
    </>
  );
};