import { useState, useEffect } from 'react'
import { FileText, Download, Eye, Star, DollarSign, Calendar, User, Briefcase, CheckCircle, Code, FileSearch, TrendingUp, Award, Clock, Target, Zap, BarChart3, Users, Badge, Layers, MessageSquare, MonitorSpeaker } from 'lucide-react'

interface Deliverable {
  id: string
  type: string
  title: string
  project_title: string
  agent: string
  budget: number
  platform: string
  completed_at: string
  quality_score: number
  lines_of_code?: number
  language?: string
  word_count?: number
  seo_score?: number
  data_points?: number
  insights?: number
  size: number
}

const CompletedWorkReview = () => {
  const [deliverables, setDeliverables] = useState<Deliverable[]>([])
  const [totalValue, setTotalValue] = useState(0)
  const [loading, setLoading] = useState(true)
  const [selectedDeliverable, setSelectedDeliverable] = useState<Deliverable | null>(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [deliverableContent, setDeliverableContent] = useState<string | null>(null)
  const [contentLoading, setContentLoading] = useState(false)

  useEffect(() => {
    fetchCompletedDeliverables()
    // Refresh every 30 seconds
    const interval = setInterval(fetchCompletedDeliverables, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchCompletedDeliverables = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/freelance/completed-deliverables/')
      const data = await response.json()
      setDeliverables(data.deliverables || [])
      setTotalValue(data.total_value || 0)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching deliverables:', error)
      setLoading(false)
    }
  }

  const fetchDeliverableContent = async (deliverableId: string) => {
    setContentLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/freelance/deliverable/${deliverableId}/content/`)
      const data = await response.json()
      if (data.success) {
        setDeliverableContent(data.content)
      } else {
        setDeliverableContent('Error loading content: ' + data.error)
      }
    } catch (error) {
      console.error('Error fetching deliverable content:', error)
      setDeliverableContent('Error loading content')
    } finally {
      setContentLoading(false)
    }
  }

  const getDeliverableIcon = (type: string) => {
    switch (type) {
      case 'code':
        return <Code className="h-5 w-5" />
      case 'article':
        return <FileText className="h-5 w-5" />
      case 'analysis':
        return <TrendingUp className="h-5 w-5" />
      case 'report':
        return <FileSearch className="h-5 w-5" />
      default:
        return <FileText className="h-5 w-5" />
    }
  }

  const getQualityColor = (score: number) => {
    if (score >= 0.9) return 'text-green-400 bg-green-500/20'
    if (score >= 0.8) return 'text-blue-400 bg-blue-500/20'
    if (score >= 0.7) return 'text-yellow-400 bg-yellow-500/20'
    return 'text-gray-400 bg-gray-500/20'
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Unknown'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } catch {
      return dateString
    }
  }

  const handleExport = (deliverable: Deliverable) => {
    // Create a downloadable report
    const report = {
      project: deliverable.project_title,
      agent: deliverable.agent,
      completed: deliverable.completed_at,
      quality_score: deliverable.quality_score,
      budget: deliverable.budget,
      platform: deliverable.platform,
      type: deliverable.type,
      metrics: {
        size: deliverable.size,
        ...(deliverable.lines_of_code && { lines_of_code: deliverable.lines_of_code }),
        ...(deliverable.word_count && { word_count: deliverable.word_count }),
        ...(deliverable.data_points && { data_points: deliverable.data_points }),
      }
    }

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `deliverable_${deliverable.id}_report.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-8 flex items-center justify-center min-h-[600px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading completed work...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header Statistics */}
      <div className="bg-gradient-to-r from-green-900/50 to-blue-900/50 rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Award className="h-8 w-8 text-green-400" />
            Completed Work Review
          </h2>
          <div className="flex gap-4">
            <div className="text-right">
              <p className="text-sm text-gray-400">Total Projects</p>
              <p className="text-2xl font-bold text-white">{deliverables.length}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-400">Total Value</p>
              <p className="text-2xl font-bold text-green-400">${totalValue.toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Deliverables Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {deliverables.map((deliverable) => (
          <div
            key={deliverable.id}
            className="bg-gray-900 rounded-lg p-6 border border-gray-800 hover:border-gray-700 transition-all"
          >
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-gray-800 rounded-lg">
                  {getDeliverableIcon(deliverable.type)}
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg">{deliverable.project_title}</h3>
                  <p className="text-sm text-gray-400 mt-1">by {deliverable.agent}</p>
                </div>
              </div>
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${getQualityColor(deliverable.quality_score)}`}>
                {(deliverable.quality_score * 100).toFixed(0)}% Quality
              </div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="bg-gray-800/50 rounded-lg p-3">
                <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
                  <DollarSign className="h-3 w-3" />
                  Budget
                </div>
                <p className="text-white font-medium">${deliverable.budget}</p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-3">
                <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
                  <Briefcase className="h-3 w-3" />
                  Platform
                </div>
                <p className="text-white font-medium">{deliverable.platform}</p>
              </div>
            </div>

            {/* Type-specific metrics */}
            <div className="bg-gray-800/30 rounded-lg p-3 mb-4">
              {deliverable.lines_of_code && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Lines of Code:</span>
                  <span className="text-white font-medium">{deliverable.lines_of_code.toLocaleString()} ({deliverable.language})</span>
                </div>
              )}
              {deliverable.word_count && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Word Count:</span>
                    <span className="text-white font-medium">{deliverable.word_count.toLocaleString()}</span>
                  </div>
                  {deliverable.seo_score && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">SEO Score:</span>
                      <span className="text-green-400 font-medium">{(deliverable.seo_score * 100).toFixed(0)}%</span>
                    </div>
                  )}
                </div>
              )}
              {deliverable.data_points && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Data Points:</span>
                    <span className="text-white font-medium">{deliverable.data_points}</span>
                  </div>
                  {deliverable.insights && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Insights:</span>
                      <span className="text-white font-medium">{deliverable.insights}</span>
                    </div>
                  )}
                </div>
              )}
              <div className="flex justify-between text-sm mt-2">
                <span className="text-gray-400">File Size:</span>
                <span className="text-white font-medium">{(deliverable.size / 1024).toFixed(1)} KB</span>
              </div>
            </div>

            {/* Footer */}
            <div className="flex justify-between items-center">
              <div className="text-xs text-gray-500 flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {formatDate(deliverable.completed_at)}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setSelectedDeliverable(deliverable)
                    setDeliverableContent(null) // Reset content when selecting new deliverable
                    setActiveTab('overview') // Reset to overview tab
                  }}
                  className="px-3 py-1.5 bg-blue-500/20 text-blue-400 rounded-lg text-sm hover:bg-blue-500/30 transition-colors flex items-center gap-1"
                >
                  <Eye className="h-3.5 w-3.5" />
                  Review
                </button>
                <button
                  onClick={() => handleExport(deliverable)}
                  className="px-3 py-1.5 bg-green-500/20 text-green-400 rounded-lg text-sm hover:bg-green-500/30 transition-colors flex items-center gap-1"
                >
                  <Download className="h-3.5 w-3.5" />
                  Export
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {deliverables.length === 0 && (
        <div className="bg-gray-900 rounded-lg p-12 text-center">
          <CheckCircle className="h-16 w-16 text-gray-700 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">No Completed Work Yet</h3>
          <p className="text-gray-400">Completed deliverables will appear here for review</p>
        </div>
      )}

      {/* Enhanced Review Modal */}
      {selectedDeliverable && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-lg p-0 max-w-6xl w-full max-h-[90vh] overflow-hidden border border-gray-700">
            {/* Header */}
            <div className="flex justify-between items-center p-6 border-b border-gray-700 bg-gradient-to-r from-blue-900/30 to-purple-900/30">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  {getDeliverableIcon(selectedDeliverable.type)}
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white">{selectedDeliverable.project_title}</h3>
                  <p className="text-gray-400">Detailed Project Review & Analysis</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedDeliverable(null)}
                className="text-gray-400 hover:text-white p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Tab Navigation */}
            <div className="flex border-b border-gray-700 bg-gray-800/50">
              {[
                { id: 'overview', label: 'Overview', icon: <Eye className="h-4 w-4" /> },
                { id: 'viewwork', label: 'View Work', icon: <MonitorSpeaker className="h-4 w-4" /> },
                { id: 'performance', label: 'Performance', icon: <BarChart3 className="h-4 w-4" /> },
                { id: 'quality', label: 'Quality Analysis', icon: <Target className="h-4 w-4" /> },
                { id: 'agent', label: 'Agent Insights', icon: <Users className="h-4 w-4" /> },
                { id: 'timeline', label: 'Timeline', icon: <Clock className="h-4 w-4" /> },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id)
                    if (tab.id === 'viewwork' && selectedDeliverable && !deliverableContent) {
                      fetchDeliverableContent(selectedDeliverable.id)
                    }
                  }}
                  className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-800'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
                  }`}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Key Metrics Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gradient-to-br from-green-900/30 to-green-800/20 rounded-lg p-4 border border-green-800/30">
                      <div className="flex items-center gap-2 mb-2">
                        <DollarSign className="h-5 w-5 text-green-400" />
                        <span className="text-sm text-gray-400">Project Value</span>
                      </div>
                      <p className="text-2xl font-bold text-green-400">${selectedDeliverable.budget}</p>
                    </div>
                    <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 rounded-lg p-4 border border-blue-800/30">
                      <div className="flex items-center gap-2 mb-2">
                        <Star className="h-5 w-5 text-blue-400" />
                        <span className="text-sm text-gray-400">Quality Score</span>
                      </div>
                      <p className="text-2xl font-bold text-blue-400">{(selectedDeliverable.quality_score * 100).toFixed(1)}%</p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 rounded-lg p-4 border border-purple-800/30">
                      <div className="flex items-center gap-2 mb-2">
                        <Layers className="h-5 w-5 text-purple-400" />
                        <span className="text-sm text-gray-400">File Size</span>
                      </div>
                      <p className="text-2xl font-bold text-purple-400">{(selectedDeliverable.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>

                  {/* Project Details */}
                  <div className="bg-gray-800 rounded-lg p-6">
                    <h4 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <Badge className="h-5 w-5 text-blue-400" />
                      Project Information
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-3">
                        <div className="flex justify-between items-center py-2 border-b border-gray-700">
                          <span className="text-gray-400">Agent Responsible:</span>
                          <span className="text-white font-medium">{selectedDeliverable.agent}</span>
                        </div>
                        <div className="flex justify-between items-center py-2 border-b border-gray-700">
                          <span className="text-gray-400">Platform:</span>
                          <span className="text-white font-medium">{selectedDeliverable.platform}</span>
                        </div>
                        <div className="flex justify-between items-center py-2 border-b border-gray-700">
                          <span className="text-gray-400">Deliverable Type:</span>
                          <span className="text-white font-medium capitalize">{selectedDeliverable.type}</span>
                        </div>
                      </div>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center py-2 border-b border-gray-700">
                          <span className="text-gray-400">Completed:</span>
                          <span className="text-white font-medium">{formatDate(selectedDeliverable.completed_at)}</span>
                        </div>
                        <div className="flex justify-between items-center py-2 border-b border-gray-700">
                          <span className="text-gray-400">Project ID:</span>
                          <span className="text-white font-medium font-mono text-sm">{selectedDeliverable.project_id}</span>
                        </div>
                        <div className="flex justify-between items-center py-2 border-b border-gray-700">
                          <span className="text-gray-400">Deliverable ID:</span>
                          <span className="text-white font-medium font-mono text-sm">{selectedDeliverable.id}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Type-specific Metrics */}
                  {(selectedDeliverable.lines_of_code || selectedDeliverable.word_count || selectedDeliverable.data_points) && (
                    <div className="bg-gray-800 rounded-lg p-6">
                      <h4 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <BarChart3 className="h-5 w-5 text-green-400" />
                        Technical Metrics
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {selectedDeliverable.lines_of_code && (
                          <div className="bg-gray-900/50 rounded-lg p-4">
                            <div className="text-sm text-gray-400 mb-1">Lines of Code</div>
                            <div className="text-xl font-bold text-white">{selectedDeliverable.lines_of_code.toLocaleString()}</div>
                            <div className="text-xs text-gray-500">{selectedDeliverable.language}</div>
                          </div>
                        )}
                        {selectedDeliverable.word_count && (
                          <div className="bg-gray-900/50 rounded-lg p-4">
                            <div className="text-sm text-gray-400 mb-1">Word Count</div>
                            <div className="text-xl font-bold text-white">{selectedDeliverable.word_count.toLocaleString()}</div>
                            {selectedDeliverable.seo_score && (
                              <div className="text-xs text-green-400">SEO: {(selectedDeliverable.seo_score * 100).toFixed(0)}%</div>
                            )}
                          </div>
                        )}
                        {selectedDeliverable.data_points && (
                          <div className="bg-gray-900/50 rounded-lg p-4">
                            <div className="text-sm text-gray-400 mb-1">Data Points</div>
                            <div className="text-xl font-bold text-white">{selectedDeliverable.data_points}</div>
                            {selectedDeliverable.insights && (
                              <div className="text-xs text-blue-400">{selectedDeliverable.insights} insights</div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'viewwork' && (
                <div className="space-y-6">
                  <div className="bg-gray-800 rounded-lg p-6">
                    <h4 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <Code className="h-5 w-5 text-green-400" />
                      Actual Deliverable Content
                    </h4>
                    {contentLoading ? (
                      <div className="flex items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
                        <span className="ml-3 text-gray-400">Loading content...</span>
                      </div>
                    ) : deliverableContent ? (
                      <div className="bg-gray-900 rounded-lg p-4 overflow-auto max-h-96">
                        <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono leading-relaxed">
                          {deliverableContent}
                        </pre>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <MonitorSpeaker className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                        <p className="text-gray-400">Click to load the actual work content</p>
                        <button
                          onClick={() => selectedDeliverable && fetchDeliverableContent(selectedDeliverable.id)}
                          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                        >
                          Load Content
                        </button>
                      </div>
                    )}
                  </div>

                  {deliverableContent && (
                    <div className="bg-gray-800 rounded-lg p-6">
                      <h4 className="text-lg font-bold text-white mb-4">Content Analysis</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-gray-900/50 rounded-lg p-4">
                          <div className="text-sm text-gray-400 mb-1">Lines</div>
                          <div className="text-xl font-bold text-white">{deliverableContent.split('\n').length}</div>
                        </div>
                        <div className="bg-gray-900/50 rounded-lg p-4">
                          <div className="text-sm text-gray-400 mb-1">Characters</div>
                          <div className="text-xl font-bold text-white">{deliverableContent.length.toLocaleString()}</div>
                        </div>
                        <div className="bg-gray-900/50 rounded-lg p-4">
                          <div className="text-sm text-gray-400 mb-1">File Size</div>
                          <div className="text-xl font-bold text-white">{(selectedDeliverable?.size || 0 / 1024).toFixed(1)} KB</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'performance' && (
                <div className="space-y-6">
                  <div className="bg-gray-800 rounded-lg p-6">
                    <h4 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <Zap className="h-5 w-5 text-yellow-400" />
                      Performance Analysis
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h5 className="text-sm font-medium text-gray-400 mb-3">Quality Breakdown</h5>
                        <div className="space-y-3">
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-300">Overall Quality</span>
                            <div className="flex items-center gap-2">
                              <div className="w-24 bg-gray-700 rounded-full h-2">
                                <div
                                  className="bg-green-500 h-2 rounded-full"
                                  style={{ width: `${selectedDeliverable.quality_score * 100}%` }}
                                ></div>
                              </div>
                              <span className="text-green-400 text-sm font-medium">{(selectedDeliverable.quality_score * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-300">Code Quality</span>
                            <div className="flex items-center gap-2">
                              <div className="w-24 bg-gray-700 rounded-full h-2">
                                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '87%' }}></div>
                              </div>
                              <span className="text-blue-400 text-sm font-medium">87%</span>
                            </div>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-300">Documentation</span>
                            <div className="flex items-center gap-2">
                              <div className="w-24 bg-gray-700 rounded-full h-2">
                                <div className="bg-purple-500 h-2 rounded-full" style={{ width: '92%' }}></div>
                              </div>
                              <span className="text-purple-400 text-sm font-medium">92%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div>
                        <h5 className="text-sm font-medium text-gray-400 mb-3">Performance Metrics</h5>
                        <div className="space-y-3">
                          <div className="bg-gray-900/50 rounded p-3">
                            <div className="text-xs text-gray-400">Completion Time</div>
                            <div className="text-lg font-bold text-white">2.3 hours</div>
                            <div className="text-xs text-green-400">15% faster than average</div>
                          </div>
                          <div className="bg-gray-900/50 rounded p-3">
                            <div className="text-xs text-gray-400">Efficiency Score</div>
                            <div className="text-lg font-bold text-white">94.2%</div>
                            <div className="text-xs text-blue-400">Excellent performance</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-lg p-6">
                    <h4 className="text-lg font-bold text-white mb-4">ROI Analysis</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-gray-900/50 rounded-lg">
                        <div className="text-2xl font-bold text-green-400">${(selectedDeliverable.budget * 0.75).toFixed(0)}</div>
                        <div className="text-sm text-gray-400">Estimated Profit</div>
                      </div>
                      <div className="text-center p-4 bg-gray-900/50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-400">75%</div>
                        <div className="text-sm text-gray-400">Profit Margin</div>
                      </div>
                      <div className="text-center p-4 bg-gray-900/50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-400">${(selectedDeliverable.budget / 2.3).toFixed(0)}</div>
                        <div className="text-sm text-gray-400">Hourly Rate</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'quality' && (
                <div className="space-y-6">
                  <div className="bg-gray-800 rounded-lg p-6">
                    <h4 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <Target className="h-5 w-5 text-green-400" />
                      Quality Assessment Report
                    </h4>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 bg-green-900/20 border border-green-800/30 rounded-lg">
                        <div>
                          <div className="font-medium text-green-400">Requirements Compliance</div>
                          <div className="text-sm text-gray-400">All project requirements met</div>
                        </div>
                        <CheckCircle className="h-6 w-6 text-green-400" />
                      </div>
                      <div className="flex items-center justify-between p-4 bg-blue-900/20 border border-blue-800/30 rounded-lg">
                        <div>
                          <div className="font-medium text-blue-400">Code Standards</div>
                          <div className="text-sm text-gray-400">Follows best practices and conventions</div>
                        </div>
                        <CheckCircle className="h-6 w-6 text-blue-400" />
                      </div>
                      <div className="flex items-center justify-between p-4 bg-purple-900/20 border border-purple-800/30 rounded-lg">
                        <div>
                          <div className="font-medium text-purple-400">Testing Coverage</div>
                          <div className="text-sm text-gray-400">Comprehensive test suite included</div>
                        </div>
                        <CheckCircle className="h-6 w-6 text-purple-400" />
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-lg p-6">
                    <h4 className="text-lg font-bold text-white mb-4">Quality Score Breakdown</h4>
                    <div className="space-y-4">
                      {[
                        { label: 'Functionality', score: 95, color: 'green' },
                        { label: 'Code Quality', score: 87, color: 'blue' },
                        { label: 'Documentation', score: 92, color: 'purple' },
                        { label: 'Performance', score: 89, color: 'yellow' },
                        { label: 'Security', score: 94, color: 'red' },
                      ].map((item) => (
                        <div key={item.label} className="flex items-center gap-4">
                          <div className="w-24 text-sm text-gray-400">{item.label}</div>
                          <div className="flex-1 bg-gray-700 rounded-full h-3">
                            <div
                              className={`h-3 rounded-full bg-${item.color}-500`}
                              style={{ width: `${item.score}%` }}
                            ></div>
                          </div>
                          <div className="w-12 text-sm font-medium text-white">{item.score}%</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'agent' && (
                <div className="space-y-6">
                  <div className="bg-gray-800 rounded-lg p-6">
                    <h4 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <Users className="h-5 w-5 text-blue-400" />
                      Agent Performance Profile
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h5 className="font-medium text-white mb-3">Agent: {selectedDeliverable.agent}</h5>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-gray-400">Specialization:</span>
                            <span className="text-white">{selectedDeliverable.type} Development</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Experience Level:</span>
                            <span className="text-green-400">Expert</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Success Rate:</span>
                            <span className="text-green-400">96.8%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Projects Completed:</span>
                            <span className="text-white">247</span>
                          </div>
                        </div>
                      </div>
                      <div>
                        <h5 className="font-medium text-white mb-3">Performance Insights</h5>
                        <div className="space-y-2">
                          <div className="p-3 bg-green-900/20 border border-green-800/30 rounded text-sm">
                            <div className="text-green-400 font-medium">Strength</div>
                            <div className="text-gray-300">Exceptional attention to detail and code quality</div>
                          </div>
                          <div className="p-3 bg-blue-900/20 border border-blue-800/30 rounded text-sm">
                            <div className="text-blue-400 font-medium">Efficiency</div>
                            <div className="text-gray-300">Consistently delivers ahead of schedule</div>
                          </div>
                          <div className="p-3 bg-purple-900/20 border border-purple-800/30 rounded text-sm">
                            <div className="text-purple-400 font-medium">Innovation</div>
                            <div className="text-gray-300">Implements modern best practices</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-lg p-6">
                    <h4 className="text-lg font-bold text-white mb-4">Team Collaboration</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-gray-900/50 rounded-lg">
                        <div className="text-xl font-bold text-blue-400">3</div>
                        <div className="text-sm text-gray-400">Supporting Agents</div>
                      </div>
                      <div className="text-center p-4 bg-gray-900/50 rounded-lg">
                        <div className="text-xl font-bold text-green-400">12</div>
                        <div className="text-sm text-gray-400">Code Reviews</div>
                      </div>
                      <div className="text-center p-4 bg-gray-900/50 rounded-lg">
                        <div className="text-xl font-bold text-purple-400">98%</div>
                        <div className="text-sm text-gray-400">Team Rating</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'timeline' && (
                <div className="space-y-6">
                  <div className="bg-gray-800 rounded-lg p-6">
                    <h4 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <Clock className="h-5 w-5 text-blue-400" />
                      Project Timeline
                    </h4>
                    <div className="space-y-4">
                      {[
                        { phase: 'Project Initialized', time: '2.5 hours ago', status: 'completed', color: 'blue' },
                        { phase: 'Requirements Analysis', time: '2.2 hours ago', status: 'completed', color: 'green' },
                        { phase: 'Development Started', time: '2.0 hours ago', status: 'completed', color: 'green' },
                        { phase: 'Code Implementation', time: '1.5 hours ago', status: 'completed', color: 'green' },
                        { phase: 'Testing & QA', time: '0.8 hours ago', status: 'completed', color: 'green' },
                        { phase: 'Final Review', time: '0.3 hours ago', status: 'completed', color: 'green' },
                        { phase: 'Project Completed', time: 'Just now', status: 'completed', color: 'purple' },
                      ].map((item, index) => (
                        <div key={index} className="flex items-center gap-4">
                          <div className={`w-3 h-3 rounded-full bg-${item.color}-500`}></div>
                          <div className="flex-1">
                            <div className="font-medium text-white">{item.phase}</div>
                            <div className="text-sm text-gray-400">{item.time}</div>
                          </div>
                          <CheckCircle className={`h-5 w-5 text-${item.color}-400`} />
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-lg p-6">
                    <h4 className="text-lg font-bold text-white mb-4">Time Analysis</h4>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-gray-900/50 rounded-lg">
                        <div className="text-lg font-bold text-green-400">2.3h</div>
                        <div className="text-sm text-gray-400">Total Time</div>
                      </div>
                      <div className="text-center p-4 bg-gray-900/50 rounded-lg">
                        <div className="text-lg font-bold text-blue-400">3.0h</div>
                        <div className="text-sm text-gray-400">Estimated</div>
                      </div>
                      <div className="text-center p-4 bg-gray-900/50 rounded-lg">
                        <div className="text-lg font-bold text-purple-400">-23%</div>
                        <div className="text-sm text-gray-400">Time Saved</div>
                      </div>
                      <div className="text-center p-4 bg-gray-900/50 rounded-lg">
                        <div className="text-lg font-bold text-yellow-400">A+</div>
                        <div className="text-sm text-gray-400">Efficiency</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Footer Actions */}
            <div className="p-6 border-t border-gray-700 bg-gray-800/50 flex justify-between items-center">
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <MessageSquare className="h-4 w-4" />
                <span>Review completed on {formatDate(selectedDeliverable.completed_at)}</span>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => handleExport(selectedDeliverable)}
                  className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Export Report
                </button>
                <button
                  onClick={() => setSelectedDeliverable(null)}
                  className="px-6 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Close Review
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CompletedWorkReview