import React, { useState, useEffect } from 'react';
import { 
  Brain, Sparkles, Zap, Settings, TrendingUp,
  BarChart3, Lightbulb, ChevronRight
} from 'lucide-react';
import { promptingService } from '../../services/promptingService';
import toast from 'react-hot-toast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';

export function AISettingsPage() {
  const [activeTab, setActiveTab] = useState<'settings' | 'stats' | 'test'>('settings');
  const [settings, setSettings] = useState<any>({
    enabled: true,
    default_level: 'advanced',
    use_memory: false,
    auto_enhance: false,
    content_preferences: {
      blog: true,
      social: true,
      email: true,
      video: true,
      image: true,
      ebook: true,
    }
  });
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Test enhancement state
  const [testPrompt, setTestPrompt] = useState('');
  const [testLevel, setTestLevel] = useState('advanced');
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);
  const [promptIndex, setPromptIndex] = useState(0);

  // Sample prompts organized by category with variety
  const samplePrompts = {
    blog: [
      "Write a comprehensive guide on sustainable living practices for urban dwellers",
      "Explain the impact of artificial intelligence on healthcare innovation",
      "Create a beginner's tutorial for learning Python programming",
      "Discuss the psychological benefits of minimalism in modern life",
      "Analyze the future of remote work post-pandemic",
      "Review the latest trends in renewable energy technology",
      "Guide to starting a successful podcast in 2024",
      "The science behind habit formation and breaking bad habits",
      "How blockchain is revolutionizing supply chain management",
      "Mental health strategies for high-stress professionals"
    ],
    social: [
      "Announce the launch of our new eco-friendly product line",
      "Share 5 productivity tips for remote workers",
      "Celebrate reaching 10,000 community members milestone",
      "Promote our upcoming webinar on digital marketing",
      "Share customer success story about transformation",
      "Create engagement post about industry trends",
      "Behind-the-scenes look at our company culture",
      "Quick tip Tuesday: Time management hack",
      "Motivational Monday message for entrepreneurs",
      "Feature Friday: Spotlight on team member achievements"
    ],
    email: [
      "Welcome new subscribers to our monthly newsletter",
      "Announce exclusive Black Friday deals to VIP customers",
      "Re-engage inactive users with special offer",
      "Thank customers for their loyalty this year",
      "Invite to exclusive product beta testing program",
      "Share quarterly company updates and achievements",
      "Promote upcoming workshop with early bird discount",
      "Follow up after networking event connection",
      "Apologize for service disruption and offer compensation",
      "Survey request for product feedback and improvement"
    ],
    creative: [
      "Describe a futuristic city powered entirely by nature",
      "Write a mystery story opening set in a bookstore",
      "Create a recipe for the world's most unique smoothie",
      "Design a workout routine for busy parents",
      "Invent a new holiday tradition for modern families",
      "Describe the perfect remote work setup",
      "Create a travel itinerary for solo adventure seekers",
      "Write product descriptions that tell a story",
      "Develop a morning routine for maximum creativity",
      "Craft a compelling elevator pitch for startup idea"
    ],
    technical: [
      "Explain quantum computing to a 10-year-old",
      "Compare React vs Vue for frontend development",
      "Best practices for API security implementation",
      "Optimize database queries for better performance",
      "Implement user authentication with JWT tokens",
      "Deploy applications using Docker and Kubernetes",
      "Build a real-time chat application architecture",
      "Create automated testing strategy for CI/CD",
      "Migrate legacy systems to cloud infrastructure",
      "Design scalable microservices architecture patterns"
    ]
  };

  const [currentCategory, setCurrentCategory] = useState<keyof typeof samplePrompts>('blog');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load settings and stats separately to handle individual failures
      let settingsData = null;
      let statsData = null;
      
      try {
        settingsData = await promptingService.getSettings();
        setSettings(settingsData);
      } catch (error) {
        console.error('Failed to load settings:', error);
        // Use default settings if loading fails
        setSettings({
          enabled: true,
          default_level: 'advanced',
          use_memory: true,
          auto_enhance: true,
          content_preferences: {
            blog: true,
            social: true,
            email: true,
            video: true,
            image: true,
            ebook: true,
          }
        });
      }
      
      try {
        statsData = await promptingService.getStats(30);
        setStats(statsData);
      } catch (error) {
        console.error('Failed to load stats:', error);
        // Stats are optional, just log the error
      }
    } catch (error) {
      console.error('Failed to load AI settings:', error);
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
        content_type: currentCategory === 'creative' || currentCategory === 'technical' ? 'blog' : currentCategory,
        use_memory: settings?.use_memory || false
      });
      setTestResult(result);
    } catch (error) {
      toast.error('Enhancement test failed');
    } finally {
      setTesting(false);
    }
  };

  const loadSamplePrompt = () => {
    const prompts = samplePrompts[currentCategory];
    const nextIndex = (promptIndex + 1) % prompts.length;
    setPromptIndex(nextIndex);
    setTestPrompt(prompts[nextIndex]);
    setTestResult(null); // Clear previous results
    toast.success('Sample prompt loaded!');
  };

  const getRandomPrompt = () => {
    const prompts = samplePrompts[currentCategory];
    const randomIndex = Math.floor(Math.random() * prompts.length);
    setPromptIndex(randomIndex);
    setTestPrompt(prompts[randomIndex]);
    setTestResult(null); // Clear previous results
    toast.success('Random prompt loaded!');
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

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Brain className="w-8 h-8 text-purple-400" />
          AI Intelligence Settings
        </h1>
        <p className="text-gray-400 mt-1">Configure how AI enhances your content generation</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: 'settings', label: 'Settings', icon: Settings },
          { id: 'stats', label: 'Statistics', icon: BarChart3 },
          { id: 'test', label: 'Test Lab', icon: Sparkles }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${
              activeTab === tab.id
                ? 'bg-purple-600 text-white'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
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
              <Card>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="p-2 bg-purple-600/20 rounded-lg mt-1">
                      <Zap className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-1">
                        Intelligent Prompting
                      </h3>
                      <p className="text-gray-400 text-sm">
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
                    <div className="w-14 h-7 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-purple-600"></div>
                  </label>
                </div>
              </Card>

              {/* Enhancement Level */}
              <Card>
                <h3 className="text-lg font-semibold text-white mb-4">Enhancement Level</h3>
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
                          ? 'bg-purple-600/20 border-purple-500 text-white'
                          : 'bg-gray-900/50 border-gray-700 text-gray-400 hover:border-gray-600'
                      }`}
                    >
                      <div className="text-2xl mb-2">{option.icon}</div>
                      <div className="font-medium">{option.label}</div>
                      <div className="text-xs mt-1 opacity-80">{option.description}</div>
                    </button>
                  ))}
                </div>
              </Card>

              {/* Additional Options */}
              <Card>
                <h3 className="text-lg font-semibold text-white mb-4">Enhancement Options</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-1.5 bg-blue-600/20 rounded">
                        <Brain className="w-4 h-4 text-blue-400" />
                      </div>
                      <div>
                        <p className="text-white font-medium">Use Memory Context</p>
                        <p className="text-gray-400 text-xs">Include previous interactions for consistency</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={!!settings.use_memory}
                        onChange={() => toggleSetting('use_memory')}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-1.5 bg-green-600/20 rounded">
                        <Sparkles className="w-4 h-4 text-green-400" />
                      </div>
                      <div>
                        <p className="text-white font-medium">Auto-Enhance</p>
                        <p className="text-gray-400 text-xs">Automatically enhance all prompts</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={!!settings.auto_enhance}
                        onChange={() => toggleSetting('auto_enhance')}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                    </label>
                  </div>
                </div>
              </Card>

              {/* Content-Specific Settings */}
              <Card>
                <h3 className="text-lg font-semibold text-white mb-4">Content-Specific Enhancement</h3>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(settings.content_preferences || {}).map(([type, enabled]) => (
                    <div key={type} className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg">
                      <span className="text-gray-300 capitalize">{type}</span>
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
              </Card>

              {/* Save Button */}
              <div className="flex justify-end">
                <Button
                  onClick={handleSaveSettings}
                  loading={saving}
                  variant="primary"
                >
                  <Settings className="w-4 h-4" />
                  Save Settings
                </Button>
              </div>
            </div>
          )}

          {/* Statistics Tab */}
          {activeTab === 'stats' && (
            <div className="space-y-6">
              {/* Help Text */}
              <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                <p className="text-sm text-blue-400">
                  💡 <span className="font-semibold">Memory Context</span> shows the percentage of your content that has associated AI memory for maintaining consistency across generations.
                </p>
              </div>

              {/* Overview Cards */}
              <div className="grid grid-cols-4 gap-4">
                <Card>
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    <span className="text-gray-400 text-sm">Enhancement Rate</span>
                  </div>
                  <p className="text-2xl font-bold text-white">
                    {stats?.overview?.enhancement_rate?.toFixed(1) || 0}%
                  </p>
                </Card>
                
                <Card>
                  <div className="flex items-center gap-2 mb-2">
                    <Brain className="w-4 h-4 text-blue-500" />
                    <span className="text-gray-400 text-sm">Memory Context</span>
                  </div>
                  <p className="text-2xl font-bold text-white">
                    {stats?.overview?.memory_usage_rate?.toFixed(1) || 0}%
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {stats?.overview?.total_memories || 0} memories
                  </p>
                </Card>
                
                <Card>
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-purple-500" />
                    <span className="text-gray-400 text-sm">Enhanced Content</span>
                  </div>
                  <p className="text-2xl font-bold text-white">
                    {stats?.overview?.enhanced_content || 0}
                  </p>
                </Card>
                
                <Card>
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="w-4 h-4 text-yellow-500" />
                    <span className="text-gray-400 text-sm">Total Content</span>
                  </div>
                  <p className="text-2xl font-bold text-white">
                    {stats?.overview?.total_content || 0}
                  </p>
                </Card>
              </div>

              {/* Enhancement by Level */}
              <Card>
                <h3 className="text-lg font-semibold text-white mb-4">Enhancement by Level</h3>
                <div className="space-y-3">
                  {Object.entries(stats?.by_level || {}).map(([level, count]) => (
                    <div key={level} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          level === 'expert' ? 'bg-purple-500' :
                          level === 'advanced' ? 'bg-blue-500' : 'bg-green-500'
                        }`} />
                        <span className="text-gray-300 capitalize">{level}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-32 bg-gray-700 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              level === 'expert' ? 'bg-purple-500' :
                              level === 'advanced' ? 'bg-blue-500' : 'bg-green-500'
                            }`}
                            style={{ 
                              width: `${((count as number) / (stats?.overview?.total_content || 1)) * 100}%` 
                            }}
                          />
                        </div>
                        <span className="text-white font-medium w-12 text-right">
                          {count as number}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* Test Lab Tab */}
          {activeTab === 'test' && (
            <div className="space-y-6">
              <Card>
                <h3 className="text-lg font-semibold text-white mb-4">Test Prompt Enhancement</h3>
                
                <div className="space-y-4">
                  {/* Category Selector */}
                  <div>
                    <label className="block text-gray-400 text-sm mb-2">Prompt Category</label>
                    <div className="grid grid-cols-5 gap-2">
                      {Object.keys(samplePrompts).map((category) => (
                        <button
                          key={category}
                          onClick={() => {
                            setCurrentCategory(category as keyof typeof samplePrompts);
                            setPromptIndex(0);
                            setTestResult(null);
                          }}
                          className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                            currentCategory === category
                              ? 'bg-purple-600 text-white'
                              : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800'
                          }`}
                        >
                          {category.charAt(0).toUpperCase() + category.slice(1)}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Sample Prompt Buttons */}
                  <div className="flex gap-2">
                    <Button
                      onClick={loadSamplePrompt}
                      variant="secondary"
                      size="small"
                    >
                      <ChevronRight className="w-4 h-4" />
                      Next Sample
                    </Button>
                    <Button
                      onClick={getRandomPrompt}
                      variant="secondary"
                      size="small"
                    >
                      <Sparkles className="w-4 h-4" />
                      Random Sample
                    </Button>
                    <Button
                      onClick={() => {
                        setTestPrompt('');
                        setTestResult(null);
                      }}
                      variant="secondary"
                      size="small"
                    >
                      Clear
                    </Button>
                  </div>

                  <div>
                    <label className="block text-gray-400 text-sm mb-2">
                      Your Prompt 
                      <span className="text-xs text-gray-500 ml-2">
                        ({currentCategory} • Sample {promptIndex + 1}/{samplePrompts[currentCategory].length})
                      </span>
                    </label>
                    <textarea
                      value={testPrompt}
                      onChange={(e) => setTestPrompt(e.target.value)}
                      placeholder="Enter a prompt or load a sample to see how it gets enhanced..."
                      className="w-full px-4 py-3 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                      rows={3}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-400 text-sm mb-2">Enhancement Level</label>
                      <select
                        value={testLevel}
                        onChange={(e) => setTestLevel(e.target.value)}
                        className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white focus:border-purple-500 focus:outline-none"
                      >
                        <option value="basic">Basic</option>
                        <option value="advanced">Advanced</option>
                        <option value="expert">Expert</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-gray-400 text-sm mb-2">Content Type</label>
                      <input
                        type="text"
                        value={currentCategory === 'creative' || currentCategory === 'technical' ? 'blog' : currentCategory}
                        disabled
                        className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-gray-400"
                      />
                    </div>
                  </div>

                  <Button
                    onClick={handleTestEnhancement}
                    loading={testing}
                    variant="primary"
                  >
                    <Sparkles className="w-4 h-4" />
                    Test Enhancement
                  </Button>
                </div>

                {testResult && (
                  <div className="mt-6 space-y-4">
                    <div className="p-4 bg-gray-900/50 rounded-lg border border-gray-700">
                      <h4 className="text-sm font-medium text-gray-400 mb-2">Enhanced Prompt</h4>
                      <p className="text-white whitespace-pre-wrap">{testResult.enhanced}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-3 bg-gray-900/50 rounded-lg">
                        <p className="text-xs text-gray-400 mb-1">Techniques Applied</p>
                        <div className="flex flex-wrap gap-1">
                          {testResult.techniques?.map((tech: string) => (
                            <span key={tech} className="px-2 py-1 bg-purple-600/20 text-purple-400 text-xs rounded">
                              {tech}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="p-3 bg-gray-900/50 rounded-lg">
                        <p className="text-xs text-gray-400 mb-1">Memory Context</p>
                        <p className="text-white font-medium">{testResult.memory_context} items</p>
                      </div>
                    </div>
                  </div>
                )}
              </Card>

              {/* Pro Tips */}
              <Card>
                <div className="flex items-center gap-2 mb-4">
                  <Lightbulb className="w-5 h-5 text-yellow-500" />
                  <h3 className="text-lg font-semibold text-white">Pro Tips</h3>
                </div>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-4 h-4 text-purple-400 mt-0.5" />
                    <p className="text-gray-300 text-sm">
                      Use <span className="text-purple-400 font-medium">Sample Prompts</span> to explore different enhancement styles across categories
                    </p>
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-4 h-4 text-purple-400 mt-0.5" />
                    <p className="text-gray-300 text-sm">
                      Try the same prompt with different <span className="text-purple-400 font-medium">Enhancement Levels</span> to see the progression
                    </p>
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-4 h-4 text-purple-400 mt-0.5" />
                    <p className="text-gray-300 text-sm">
                      <span className="text-purple-400 font-medium">Expert level</span> adds deep reasoning and nuanced context
                    </p>
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-4 h-4 text-purple-400 mt-0.5" />
                    <p className="text-gray-300 text-sm">
                      Enable <span className="text-purple-400 font-medium">Memory Context</span> to maintain consistency across related content
                    </p>
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-4 h-4 text-purple-400 mt-0.5" />
                    <p className="text-gray-300 text-sm">
                      Mix <span className="text-purple-400 font-medium">Categories</span> to discover creative cross-domain enhancements
                    </p>
                  </li>
                </ul>
              </Card>
            </div>
          )}
        </>
      )}
    </div>
  );
}