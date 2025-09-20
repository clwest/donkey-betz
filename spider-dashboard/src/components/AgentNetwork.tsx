import { useState, useEffect } from 'react'
import { Users, Bot, Zap, ChevronRight, Search, Play, Loader2 } from 'lucide-react'

interface Agent {
  name: string
  display_name: string
  class_name: string
  module: string
  status: string
}

interface AgentCategories {
  content: { count: number; agents: string[] }
  trading: { count: number; agents: string[] }
  sports: { count: number; agents: string[] }
  income: { count: number; agents: string[] }
  research: { count: number; agents: string[] }
  analysis: { count: number; agents: string[] }
  automation: { count: number; agents: string[] }
  general: { count: number; agents: string[] }
}

const AgentNetwork = () => {
  const [agents, setAgents] = useState<Agent[]>([])
  const [categories, setCategories] = useState<AgentCategories | null>(null)
  const [totalAgents, setTotalAgents] = useState(0)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(true)
  const [executingAgents, setExecutingAgents] = useState<Set<string>>(new Set())
  const [executionResults, setExecutionResults] = useState<{ [key: string]: { success: boolean; message: string } }>({})

  const executeAgent = async (agentName: string) => {
    setExecutingAgents(prev => new Set(prev).add(agentName))

    try {
      const response = await fetch(`http://localhost:8000/api/agents/execute/${agentName}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: 'analyze' })
      })

      const data = await response.json()

      setExecutionResults(prev => ({
        ...prev,
        [agentName]: {
          success: data.success,
          message: data.success ? 'Execution started' : data.error
        }
      }))

      // Clear result after 3 seconds
      setTimeout(() => {
        setExecutionResults(prev => {
          const newResults = { ...prev }
          delete newResults[agentName]
          return newResults
        })
      }, 3000)

    } catch (error) {
      setExecutionResults(prev => ({
        ...prev,
        [agentName]: { success: false, message: 'Failed to execute' }
      }))
    } finally {
      setExecutingAgents(prev => {
        const newSet = new Set(prev)
        newSet.delete(agentName)
        return newSet
      })
    }
  }

  useEffect(() => {
    // Fetch agent list
    const fetchAgents = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/agents/simple/list/')
        const data = await response.json()
        if (data.success) {
          setAgents(data.agents.filter((a: Agent) => a.name)) // Filter out empty names
          setTotalAgents(data.total)
        }
      } catch (error) {
        console.error('Error fetching agents:', error)
      }
    }

    // Fetch categories
    const fetchCategories = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/agents/simple/categories/')
        const data = await response.json()
        if (data.success) {
          setCategories(data.categories)
        }
        setLoading(false)
      } catch (error) {
        console.error('Error fetching categories:', error)
        setLoading(false)
      }
    }

    fetchAgents()
    fetchCategories()

    // Refresh every 10 seconds
    const interval = setInterval(() => {
      fetchAgents()
      fetchCategories()
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  // Filter agents based on search and category
  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.name.toLowerCase().includes(searchTerm.toLowerCase())

    if (selectedCategory === 'all') return matchesSearch

    // Check if agent is in selected category
    if (categories && categories[selectedCategory as keyof AgentCategories]) {
      const categoryAgents = categories[selectedCategory as keyof AgentCategories].agents
      return matchesSearch && categoryAgents.includes(agent.name)
    }

    return matchesSearch
  })

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'content': return '📝'
      case 'trading': return '📈'
      case 'sports': return '⚽'
      case 'income': return '💰'
      case 'research': return '🔍'
      case 'analysis': return '📊'
      case 'automation': return '🤖'
      default: return '🎯'
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'content': return 'text-purple-400 bg-purple-900/20'
      case 'trading': return 'text-green-400 bg-green-900/20'
      case 'sports': return 'text-blue-400 bg-blue-900/20'
      case 'income': return 'text-yellow-400 bg-yellow-900/20'
      case 'research': return 'text-cyan-400 bg-cyan-900/20'
      case 'analysis': return 'text-orange-400 bg-orange-900/20'
      case 'automation': return 'text-red-400 bg-red-900/20'
      default: return 'text-gray-400 bg-gray-700'
    }
  }

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading agent network...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-100 flex items-center space-x-2">
          <Users className="h-6 w-6 text-cyan-400" />
          <span>AI Agent Network</span>
          <span className="text-sm text-cyan-400 ml-2">({totalAgents} agents)</span>
        </h3>
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="h-4 w-4 text-gray-400 absolute left-2 top-2.5" />
            <input
              type="text"
              placeholder="Search agents..."
              className="bg-gray-700 text-gray-100 pl-8 pr-3 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={() => setSelectedCategory('all')}
          className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
            selectedCategory === 'all'
              ? 'bg-cyan-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          All ({totalAgents})
        </button>
        {categories && Object.entries(categories).map(([key, value]) => (
          <button
            key={key}
            onClick={() => setSelectedCategory(key)}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1 ${
              selectedCategory === key
                ? getCategoryColor(key)
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <span>{getCategoryIcon(key)}</span>
            <span className="capitalize">{key}</span>
            <span>({value.count})</span>
          </button>
        ))}
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
        {filteredAgents.slice(0, 30).map((agent, index) => (
          <div
            key={index}
            className="bg-gray-700 rounded-lg p-3 hover:bg-gray-600 transition-all cursor-pointer border border-gray-600"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-2">
                <Bot className="h-5 w-5 text-cyan-400 mt-0.5" />
                <div className="flex-1">
                  <h4 className="text-gray-100 font-medium text-sm line-clamp-1">
                    {agent.display_name}
                  </h4>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-1">
                    {agent.name}
                  </p>
                </div>
              </div>
              {agent.status === 'active' && (
                <div className="flex items-center">
                  <Zap className="h-4 w-4 text-green-400" />
                </div>
              )}
            </div>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-xs text-gray-500">
                {agent.class_name.replace('Agent', '')}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  executeAgent(agent.name)
                }}
                disabled={executingAgents.has(agent.name)}
                className="flex items-center space-x-1 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:cursor-not-allowed px-2 py-1 rounded text-xs text-white transition-colors"
              >
                {executingAgents.has(agent.name) ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <Play className="h-3 w-3" />
                )}
                <span>Execute</span>
              </button>
            </div>
            {executionResults[agent.name] && (
              <div className={`mt-2 text-xs px-2 py-1 rounded ${
                executionResults[agent.name].success ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'
              }`}>
                {executionResults[agent.name].message}
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredAgents.length > 30 && (
        <div className="mt-4 text-center text-sm text-gray-400">
          Showing 30 of {filteredAgents.length} agents
        </div>
      )}

      {filteredAgents.length === 0 && (
        <div className="text-center text-gray-400 py-8">
          No agents found matching your search
        </div>
      )}
    </div>
  )
}

export default AgentNetwork