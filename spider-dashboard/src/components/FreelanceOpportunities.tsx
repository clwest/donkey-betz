import { useState, useEffect } from 'react'
import { Briefcase, DollarSign, Clock, TrendingUp, CheckCircle, XCircle, AlertCircle, Play, Eye } from 'lucide-react'

interface Opportunity {
  job_id: string
  platform: string
  title: string
  description: string
  budget: number
  budget_type: string
  skills_required: string[]
  deadline: string | null
  client_rating: number | null
  agent_suitability: number
  recommended_agents: string[]
  estimated_completion_time: number
  confidence_score: number
  status?: string
  analysis?: any
}

interface Project {
  id: string
  opportunity: Opportunity
  status: string
  checkpoints: any[]
  financial: {
    budget: number
    cost: number
    profit: number
    paid: boolean
  }
  deliverables?: any[]
}

const FreelanceOpportunities = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [pendingApprovals, setPendingApprovals] = useState<any[]>([])
  const [selectedOpp, setSelectedOpp] = useState<Opportunity | null>(null)
  const [activeTab, setActiveTab] = useState<'opportunities' | 'projects' | 'approvals'>('opportunities')
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState<string | null>(null)

  useEffect(() => {
    loadOpportunities()
    loadProjects()
    loadPendingApprovals()

    // Set up polling for updates
    const interval = setInterval(() => {
      loadPendingApprovals()
      loadProjects()
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const loadOpportunities = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/freelance/opportunities/')
      if (response.ok) {
        const data = await response.json()
        setOpportunities(data.opportunities || [])
      }
    } catch (error) {
      console.error('Error loading opportunities:', error)
      // Use mock data for demo
      setOpportunities(getMockOpportunities())
    }
    setLoading(false)
  }

  const loadProjects = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/freelance/projects/')
      if (response.ok) {
        const data = await response.json()
        setProjects(data.projects || [])
      }
    } catch (error) {
      console.error('Error loading projects:', error)
      setProjects(getMockProjects())
    }
  }

  const loadPendingApprovals = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/freelance/approvals/')
      if (response.ok) {
        const data = await response.json()
        setPendingApprovals(data.approvals || [])
      }
    } catch (error) {
      console.error('Error loading approvals:', error)
      setPendingApprovals(getMockApprovals())
    }
  }

  const analyzeOpportunity = async (opp: Opportunity) => {
    setAnalyzing(opp.job_id)
    try {
      const response = await fetch(`http://localhost:8000/api/freelance/analyze/${opp.job_id}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(opp)
      })

      if (response.ok) {
        const result = await response.json()
        // Reload to show updated status
        loadOpportunities()
        loadPendingApprovals()
      }
    } catch (error) {
      console.error('Error analyzing opportunity:', error)
    }
    setAnalyzing(null)
  }

  const handleApproval = async (approvalId: string, decision: 'approve' | 'reject') => {
    try {
      const response = await fetch(`http://localhost:8000/api/freelance/approve/${approvalId}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision })
      })

      if (response.ok) {
        // Reload approvals and projects
        loadPendingApprovals()
        loadProjects()
      }
    } catch (error) {
      console.error('Error processing approval:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'text-blue-400 bg-blue-900/20'
      case 'analyzing': return 'text-yellow-400 bg-yellow-900/20'
      case 'pending_approval': return 'text-orange-400 bg-orange-900/20'
      case 'approved': return 'text-green-400 bg-green-900/20'
      case 'in_progress': return 'text-purple-400 bg-purple-900/20'
      case 'completed': return 'text-green-400 bg-green-900/20'
      case 'paid': return 'text-green-500 bg-green-900/30'
      case 'rejected': return 'text-red-400 bg-red-900/20'
      default: return 'text-gray-400 bg-gray-700'
    }
  }

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'upwork': return '🟢'
      case 'fiverr': return '🟩'
      case 'freelancer': return '🔷'
      case 'toptal': return '🔵'
      default: return '💼'
    }
  }

  // Mock data functions
  const getMockOpportunities = (): Opportunity[] => [
    {
      job_id: 'upw_001',
      platform: 'Upwork',
      title: 'Write 10 SEO Blog Posts on AI Tools',
      description: 'Need 10 high-quality blog posts about AI productivity tools...',
      budget: 500,
      budget_type: 'fixed',
      skills_required: ['content writing', 'SEO', 'AI knowledge'],
      deadline: '2025-09-27',
      client_rating: 4.8,
      agent_suitability: 0.95,
      recommended_agents: ['content_creator_agent', 'seo_optimizer_agent'],
      estimated_completion_time: 12,
      confidence_score: 0.92,
      status: 'new'
    },
    {
      job_id: 'fiv_002',
      platform: 'Fiverr',
      title: 'Build REST API with Node.js',
      description: 'Need REST API for e-commerce platform...',
      budget: 1200,
      budget_type: 'fixed',
      skills_required: ['Node.js', 'REST API', 'MongoDB'],
      deadline: '2025-10-05',
      client_rating: 4.7,
      agent_suitability: 0.88,
      recommended_agents: ['code_generator_agent', 'api_builder_agent'],
      estimated_completion_time: 16,
      confidence_score: 0.85,
      status: 'new'
    }
  ]

  const getMockProjects = (): Project[] => [
    {
      id: 'proj_001',
      opportunity: getMockOpportunities()[0],
      status: 'in_progress',
      checkpoints: [
        { stage: 'analysis', status: 'completed', timestamp: new Date().toISOString() },
        { stage: 'approval', status: 'completed', timestamp: new Date().toISOString() }
      ],
      financial: {
        budget: 500,
        cost: 100,
        profit: 400,
        paid: false
      },
      deliverables: [
        { task: 'Blog Post 1: Top AI Writing Tools', status: 'completed' },
        { task: 'Blog Post 2: AI for Productivity', status: 'in_progress' }
      ]
    }
  ]

  const getMockApprovals = () => [
    {
      id: 'appr_001',
      project_id: 'proj_002',
      type: 'approve_analysis',
      title: 'Python Data Analysis Script',
      budget: 300,
      profit: 250,
      risk: 'LOW',
      recommendation: 'PURSUE'
    }
  ]

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading freelance opportunities...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-100 flex items-center space-x-2">
          <Briefcase className="h-6 w-6 text-green-400" />
          <span>Freelance Pipeline</span>
        </h3>

        {/* Tab Navigation */}
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('opportunities')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'opportunities'
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Opportunities ({opportunities.length})
          </button>
          <button
            onClick={() => setActiveTab('approvals')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors relative ${
              activeTab === 'approvals'
                ? 'bg-orange-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Approvals
            {pendingApprovals.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                {pendingApprovals.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('projects')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'projects'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Active Projects ({projects.length})
          </button>
        </div>
      </div>

      {/* Opportunities Tab */}
      {activeTab === 'opportunities' && (
        <div className="space-y-4">
          {opportunities.map((opp) => (
            <div
              key={opp.job_id}
              className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-all border border-gray-600"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-lg">{getPlatformIcon(opp.platform)}</span>
                    <h4 className="text-gray-100 font-medium">{opp.title}</h4>
                    <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor(opp.status || 'new')}`}>
                      {opp.status || 'new'}
                    </span>
                  </div>

                  <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                    {opp.description}
                  </p>

                  <div className="flex flex-wrap gap-4 text-xs">
                    <div className="flex items-center space-x-1">
                      <DollarSign className="h-3 w-3 text-green-400" />
                      <span className="text-green-400 font-medium">${opp.budget}</span>
                      <span className="text-gray-500">({opp.budget_type})</span>
                    </div>

                    <div className="flex items-center space-x-1">
                      <TrendingUp className="h-3 w-3 text-blue-400" />
                      <span className="text-blue-400">{(opp.agent_suitability * 100).toFixed(0)}% suitable</span>
                    </div>

                    <div className="flex items-center space-x-1">
                      <Clock className="h-3 w-3 text-yellow-400" />
                      <span className="text-yellow-400">{opp.estimated_completion_time}h</span>
                    </div>

                    {opp.deadline && (
                      <div className="flex items-center space-x-1">
                        <AlertCircle className="h-3 w-3 text-orange-400" />
                        <span className="text-orange-400">Due: {opp.deadline}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2 mt-3">
                    {opp.skills_required.slice(0, 3).map((skill, i) => (
                      <span key={i} className="text-xs bg-blue-900/50 text-blue-400 px-2 py-0.5 rounded">
                        {skill}
                      </span>
                    ))}
                  </div>

                  <div className="flex flex-wrap gap-2 mt-2">
                    {opp.recommended_agents.slice(0, 2).map((agent, i) => (
                      <span key={i} className="text-xs bg-purple-900/50 text-purple-400 px-2 py-0.5 rounded">
                        {agent}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col space-y-2 ml-4">
                  <button
                    onClick={() => analyzeOpportunity(opp)}
                    disabled={analyzing === opp.job_id}
                    className="flex items-center space-x-1 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 px-3 py-1.5 rounded text-xs text-white"
                  >
                    {analyzing === opp.job_id ? (
                      <>
                        <div className="animate-spin h-3 w-3 border-2 border-white border-t-transparent rounded-full" />
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <Play className="h-3 w-3" />
                        <span>Analyze</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => setSelectedOpp(opp)}
                    className="flex items-center space-x-1 bg-gray-600 hover:bg-gray-500 px-3 py-1.5 rounded text-xs text-white"
                  >
                    <Eye className="h-3 w-3" />
                    <span>Details</span>
                  </button>
                </div>
              </div>
            </div>
          ))}

          {opportunities.length === 0 && (
            <div className="text-center text-gray-400 py-8">
              No freelance opportunities found. Spiders are searching...
            </div>
          )}
        </div>
      )}

      {/* Approvals Tab */}
      {activeTab === 'approvals' && (
        <div className="space-y-4">
          {pendingApprovals.map((approval) => (
            <div
              key={approval.id}
              className="bg-yellow-900/20 border border-yellow-600/50 rounded-lg p-4"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h4 className="text-yellow-400 font-medium mb-1">
                    {approval.type === 'approve_analysis' ? '📊 Analysis Review' :
                     approval.type === 'confirm_project_won' ? '🏆 Project Won?' :
                     approval.type === 'approve_deliverables' ? '📦 Review Deliverables' :
                     '🔔 Approval Needed'}
                  </h4>
                  <p className="text-gray-100 font-medium">{approval.title}</p>
                </div>
                <div className="text-right">
                  <div className="text-green-400 font-bold text-lg">${approval.budget}</div>
                  <div className="text-sm text-gray-400">Profit: ${approval.profit}</div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 mb-4 text-sm">
                <div className="bg-gray-700 rounded p-2">
                  <div className="text-gray-400 text-xs">Risk Level</div>
                  <div className={`font-medium ${
                    approval.risk === 'LOW' ? 'text-green-400' :
                    approval.risk === 'MEDIUM' ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {approval.risk}
                  </div>
                </div>
                <div className="bg-gray-700 rounded p-2">
                  <div className="text-gray-400 text-xs">Recommendation</div>
                  <div className="text-blue-400 font-medium">{approval.recommendation}</div>
                </div>
                <div className="bg-gray-700 rounded p-2">
                  <div className="text-gray-400 text-xs">Confidence</div>
                  <div className="text-purple-400 font-medium">92%</div>
                </div>
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => handleApproval(approval.id, 'approve')}
                  className="flex-1 flex items-center justify-center space-x-2 bg-green-600 hover:bg-green-500 py-2 rounded text-white font-medium"
                >
                  <CheckCircle className="h-4 w-4" />
                  <span>Approve</span>
                </button>
                <button
                  onClick={() => handleApproval(approval.id, 'reject')}
                  className="flex-1 flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-500 py-2 rounded text-white font-medium"
                >
                  <XCircle className="h-4 w-4" />
                  <span>Reject</span>
                </button>
              </div>
            </div>
          ))}

          {pendingApprovals.length === 0 && (
            <div className="text-center text-gray-400 py-8">
              No pending approvals. All clear! ✨
            </div>
          )}
        </div>
      )}

      {/* Projects Tab */}
      {activeTab === 'projects' && (
        <div className="space-y-4">
          {projects.map((project) => (
            <div
              key={project.id}
              className="bg-gray-700 rounded-lg p-4 border border-gray-600"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="text-gray-100 font-medium">{project.opportunity.title}</h4>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-lg">{getPlatformIcon(project.opportunity.platform)}</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor(project.status)}`}>
                      {project.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-green-400 font-bold">${project.financial.profit}</div>
                  <div className="text-xs text-gray-400">profit</div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-3">
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>Progress</span>
                  <span>{project.checkpoints.length} / 7 stages</span>
                </div>
                <div className="bg-gray-600 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-green-500 h-full transition-all"
                    style={{ width: `${(project.checkpoints.length / 7) * 100}%` }}
                  />
                </div>
              </div>

              {/* Deliverables */}
              {project.deliverables && project.deliverables.length > 0 && (
                <div className="space-y-1">
                  <div className="text-xs text-gray-400 mb-1">Deliverables:</div>
                  {project.deliverables.slice(0, 3).map((del: any, i: number) => (
                    <div key={i} className="flex items-center space-x-2 text-xs">
                      {del.status === 'completed' ? (
                        <CheckCircle className="h-3 w-3 text-green-400" />
                      ) : (
                        <div className="h-3 w-3 border border-gray-500 rounded-full" />
                      )}
                      <span className={del.status === 'completed' ? 'text-gray-300' : 'text-gray-500'}>
                        {del.task}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Financial Status */}
              <div className="mt-3 pt-3 border-t border-gray-600 flex justify-between text-xs">
                <span className="text-gray-400">Budget: ${project.financial.budget}</span>
                <span className={`font-medium ${project.financial.paid ? 'text-green-400' : 'text-yellow-400'}`}>
                  {project.financial.paid ? '✅ Paid' : '⏳ Payment Pending'}
                </span>
              </div>
            </div>
          ))}

          {projects.length === 0 && (
            <div className="text-center text-gray-400 py-8">
              No active projects yet. Analyze opportunities to get started!
            </div>
          )}
        </div>
      )}

      {/* Opportunity Details Modal */}
      {selectedOpp && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <h3 className="text-xl font-bold text-gray-100 mb-4">{selectedOpp.title}</h3>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-1">Description</h4>
                <p className="text-gray-300">{selectedOpp.description}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-1">Budget</h4>
                  <p className="text-green-400 font-medium">${selectedOpp.budget} ({selectedOpp.budget_type})</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-1">Estimated Profit</h4>
                  <p className="text-green-400 font-medium">${(selectedOpp.budget * 0.8).toFixed(0)}</p>
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-1">Required Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedOpp.skills_required.map((skill, i) => (
                    <span key={i} className="text-xs bg-blue-900/50 text-blue-400 px-2 py-1 rounded">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-1">Recommended Agents</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedOpp.recommended_agents.map((agent, i) => (
                    <span key={i} className="text-xs bg-purple-900/50 text-purple-400 px-2 py-1 rounded">
                      {agent}
                    </span>
                  ))}
                </div>
              </div>
              <button
                onClick={() => setSelectedOpp(null)}
                className="w-full bg-gray-700 hover:bg-gray-600 py-2 rounded text-white"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default FreelanceOpportunities