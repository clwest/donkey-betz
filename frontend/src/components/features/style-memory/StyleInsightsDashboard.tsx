import { useEffect } from 'react';
import { 
  ChartBarIcon, 
  HeartIcon, 
  SparklesIcon, 
  LightBulbIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { useStyleMemoryStore } from '../../../store/styleMemoryStore';
import { GeneratedImage } from '../../common/GeneratedImage';

export function StyleInsightsDashboard() {
  const {
    insights,
    suggestions,
    showInsights,
    isLoading,
    toggleInsights,
    loadInsights,
    loadSuggestions,
    useSuggestion,
    dismissSuggestion,
  } = useStyleMemoryStore();

  useEffect(() => {
    if (showInsights && !insights) {
      loadInsights();
      loadSuggestions();
    }
  }, [showInsights, insights, loadInsights, loadSuggestions]);

  if (!showInsights) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm">
      <div className="min-h-full flex items-start justify-center p-4">
        <div className="relative w-full max-w-6xl glass rounded-xl shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-primary rounded-lg">
                <SparklesIcon className="h-6 w-6 text-foreground" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground">Style Insights</h2>
                <p className="text-muted-foreground">Your AI-powered style analysis</p>
              </div>
            </div>
            <Button variant="ghost" onClick={toggleInsights}>
              <XMarkIcon className="h-5 w-5" />
            </Button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
                <span className="ml-3 text-muted-foreground">Analyzing your style preferences...</span>
              </div>
            ) : insights ? (
              <>
                {/* Stats Overview */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card className="text-center">
                    <ChartBarIcon className="h-8 w-8 text-primary-400 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-foreground">{insights.total_memories}</div>
                    <div className="text-sm text-muted-foreground">Total Memories</div>
                  </Card>
                  
                  <Card className="text-center">
                    <HeartIcon className="h-8 w-8 text-red-500 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-foreground">{insights.loved_count}</div>
                    <div className="text-sm text-muted-foreground">Loved Styles</div>
                  </Card>
                  
                  <Card className="text-center">
                    <SparklesIcon className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-foreground">{insights.preferred_cfg}</div>
                    <div className="text-sm text-muted-foreground">Preferred CFG</div>
                  </Card>
                  
                  <Card className="text-center">
                    <EyeIcon className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-foreground">{insights.preferred_steps}</div>
                    <div className="text-sm text-muted-foreground">Preferred Steps</div>
                  </Card>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Favorite Styles */}
                  <Card>
                    <h3 className="text-lg font-semibold text-foreground mb-4">Favorite Styles</h3>
                    <div className="space-y-2">
                      {insights.favorite_styles?.slice(0, 5).map((style, index) => (
                        <div key={style.style} className="flex items-center justify-between">
                          <span className="text-muted-foreground">{index + 1}. {style.style}</span>
                          <span className="text-primary-400 font-medium">{style.count} uses</span>
                        </div>
                      ))}
                    </div>
                  </Card>

                  {/* Detected Patterns */}
                  <Card>
                    <h3 className="text-lg font-semibold text-foreground mb-4">Detected Patterns</h3>
                    <div className="space-y-3">
                      {insights.patterns?.slice(0, 5).map((pattern) => (
                        <div key={pattern.id} className="flex items-start gap-3">
                          <div className="w-2 h-2 bg-primary-500 rounded-full mt-2" />
                          <div>
                            <div className="text-foreground font-medium">{pattern.pattern_name}</div>
                            <div className="text-sm text-muted-foreground">{pattern.pattern_description}</div>
                            <div className="text-xs text-primary-400 mt-1">
                              {Math.round(pattern.confidence * 100)}% confidence
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>

                  {/* Evolution Trends */}
                  <Card>
                    <h3 className="text-lg font-semibold text-foreground mb-4">Style Evolution</h3>
                    <div className="space-y-4">
                      {insights.evolution?.trending_up?.length > 0 && (
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
                            <span className="text-sm font-medium text-green-500">Trending Up</span>
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {insights.evolution?.trending_up?.map((trend) => (
                              <span key={trend} className="px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded-full">
                                {trend}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {insights.evolution?.trending_down?.length > 0 && (
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <ArrowTrendingDownIcon className="h-4 w-4 text-orange-400" />
                            <span className="text-sm font-medium text-orange-400">Trending Down</span>
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {insights.evolution?.trending_down?.map((trend) => (
                              <span key={trend} className="px-2 py-1 bg-orange-500/20 text-orange-300 text-xs rounded-full">
                                {trend}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </Card>

                  {/* AI Suggestions */}
                  <Card>
                    <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                      <LightBulbIcon className="h-5 w-5 text-yellow-500" />
                      AI Suggestions
                    </h3>
                    <div className="space-y-3">
                      {suggestions.length === 0 ? (
                        <p className="text-muted-foreground text-sm">No suggestions available. Generate more content to get AI recommendations!</p>
                      ) : (
                        suggestions.slice(0, 3).map((suggestion) => (
                          <div key={suggestion.id} className="bg-card/50 rounded-lg p-3">
                            <div className="text-foreground font-medium mb-1">{suggestion.title}</div>
                            <div className="text-sm text-muted-foreground mb-2">{suggestion.description}</div>
                            <div className="text-xs text-muted-foreground mb-3">{suggestion.reasoning}</div>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                onClick={() => useSuggestion(suggestion.id)}
                                className="text-xs"
                              >
                                Try This
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => dismissSuggestion(suggestion.id)}
                                className="text-xs"
                              >
                                Dismiss
                              </Button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </Card>
                </div>

                {/* Top Memories Gallery */}
                {insights.top_memories?.length > 0 && (
                  <Card>
                    <h3 className="text-lg font-semibold text-foreground mb-4">Your Best Generations</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {insights.top_memories?.slice(0, 8).map((memory) => (
                        <div key={memory.id} className="aspect-square">
                          <GeneratedImage
                            id={memory.content_id}
                            src={`/api/content/${memory.content_id}/image/`} // Assuming this endpoint exists
                            prompt={memory.prompt_text}
                            parameters={{
                              cfg_scale: memory.cfg_scale,
                              steps: memory.steps,
                              style: memory.style_name,
                            }}
                            showStyleControls={false}
                            className="h-full"
                          />
                        </div>
                      ))}
                    </div>
                  </Card>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <SparklesIcon className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-foreground mb-2">Start Building Your Style Profile</h3>
                <p className="text-muted-foreground mb-6">
                  Generate some images and use the ❤️ Love button to build your personal style memory!
                </p>
                <Button onClick={() => window.location.href = '/studio'}>
                  Generate Your First Image
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}