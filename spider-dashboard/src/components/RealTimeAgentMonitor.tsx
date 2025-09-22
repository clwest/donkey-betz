import { useState, useEffect, useRef } from 'react'
import { Activity, Brain, Zap, TrendingUp, DollarSign, Eye, AlertCircle, CheckCircle, Clock, User, Bot, Code, FileText, Briefcase } from 'lucide-react'

interface Agent {
  name: string
  status: 'idle' | 'working' | 'completed'
  currentTask?: string
  completedTasks: number
  revenue: number
  successRate: number
  specialization: string
  lastActive?: string
  progress?: number
  projectStatus?: string
}

interface ActiveTask {
  id: string
  agentName: string
  taskType: string
  progress: number
  estimatedTime: string
  value: number
  status: 'analyzing' | 'executing' | 'generating' | 'completed'
  output?: string
  title?: string
  description?: string
  platform?: string
  skills?: string[]
  url?: string
}

interface Deliverable {
  id: string
  type: string
  title: string
  agent: string
  value: number
  createdAt: string
  fileSize?: number
  wordCount?: number
  status: 'generating' | 'ready' | 'delivered'
}

const RealTimeAgentMonitor = () => {
  const [agents, setAgents] = useState<Agent[]>([])
  const [activeTasks, setActiveTasks] = useState<ActiveTask[]>([])
  const [deliverables, setDeliverables] = useState<Deliverable[]>([])
  const [totalRevenue, setTotalRevenue] = useState(0)
  const [tasksCompleted, setTasksCompleted] = useState(0)
  const [activeAgents, setActiveAgents] = useState(0)
  const [revenuePerSecond, setRevenuePerSecond] = useState(0)
  const [wsConnected, setWsConnected] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)

  // Track previous state to prevent spam
  const lastLogRef = useRef({ agentCount: 0, activeCount: 0 })

  // WebSocket connection with auto-reconnect
  useEffect(() => {
    let ws: WebSocket | null = null
    let reconnectTimer: NodeJS.Timeout | null = null
    let isComponentMounted = true

    const connect = () => {
      if (!isComponentMounted) return

      ws = new WebSocket('ws://localhost:8000/ws/agent-monitor/')

      ws.onopen = () => {
        console.log('WebSocket connected to agent monitor')
        setWsConnected(true)
        // Request initial status
        ws?.send(JSON.stringify({ type: 'request_agent_status' }))
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleWebSocketMessage(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setWsConnected(false)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setWsConnected(false)
        // Auto-reconnect after 3 seconds if component is still mounted
        if (isComponentMounted) {
          console.log('Will reconnect in 3 seconds...')
          reconnectTimer = setTimeout(() => {
            console.log('Attempting to reconnect...')
            connect()
          }, 3000)
        }
      }
    }

    // Initial connection
    connect()

    return () => {
      isComponentMounted = false
      if (reconnectTimer) {
        clearTimeout(reconnectTimer)
      }
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [])

  const handleWebSocketMessage = (data: any) => {
    switch(data.type) {
      case 'agent_status':
        setAgents(data.agents || [])
        const newActiveCount = data.agents?.filter((a: Agent) => a.status === 'working').length || 0
        setActiveAgents(newActiveCount)

        // Only log if there's an actual change from last logged state
        const newAgentCount = data.agents?.length || 0

        if (lastLogRef.current.agentCount !== newAgentCount ||
            lastLogRef.current.activeCount !== newActiveCount) {

          console.log('🤖 AGENT STATUS CHANGE:', {
            total: newAgentCount,
            active: newActiveCount,
            agents: data.agents?.filter((a: any) => a.status === 'working')
              .map((a: any) => `${a.name}: ${a.currentTask}`)
          })

          // Update the ref with new values
          lastLogRef.current = {
            agentCount: newAgentCount,
            activeCount: newActiveCount
          }
        }
        break
      case 'task_update':
        updateTask(data.task)
        console.log('📋 TASK UPDATE:', data.task)
        break
      case 'deliverable_created':
        addDeliverable(data.deliverable)
        console.log('📦 DELIVERABLE CREATED:', data.deliverable)
        break
      case 'revenue_update':
        setTotalRevenue(data.totalRevenue)
        setRevenuePerSecond(data.revenuePerSecond)
        console.log('💰 REVENUE UPDATE: $', data.totalRevenue)
        break
      case 'project_update':
        console.log('🚀 PROJECT DEPLOYED:', data.message)
        break
      case 'active_tasks':
        setActiveTasks(data.tasks || [])
        console.log('📊 ACTIVE TASKS:', data.tasks)
        break
      case 'project_progress':
        // Update agent progress
        if (data.data) {
          const progressData = data.data
          console.log('📈 PROJECT PROGRESS:', progressData)

          setAgents(prevAgents =>
            prevAgents.map(agent => {
              if (agent.name === progressData.agent) {
                return {
                  ...agent,
                  progress: progressData.progress,
                  projectStatus: progressData.status
                }
              }
              return agent
            })
          )
        }
        break
    }
  }

  const loadAgentRegistry = async () => {
    // Comment out API call that doesn't exist
    // The WebSocket will provide agent data instead
    /*
    try {
      const response = await fetch('http://localhost:8000/api/agents/registry/')
      if (response.ok) {
        const data = await response.json()
        // Transform to our Agent interface
        const agentList = data.agents?.map((a: any) => ({
          name: a.name,
          status: 'idle' as const,
          completedTasks: 0,
          revenue: 0,
          successRate: a.success_rate || 0.85,
          specialization: a.specialization || 'general',
        })) || []
        setAgents(agentList)
      }
    } catch (error) {
      console.error('Error loading agent registry:', error)
      // Use mock data for demo
      // setAgents(generateMockAgents())  // Commented - using real data
    }
    */
    // Commented out - WebSocket provides real agent data
    // setAgents(generateMockAgents())
  }

  const loadActiveTasks = async () => {
    // Comment out API call that doesn't exist
    // The WebSocket will provide task data instead
    /*
    try {
      const response = await fetch('http://localhost:8000/api/agents/active-tasks/')
      if (response.ok) {
        const data = await response.json()
        setActiveTasks(data.tasks || [])
      }
    } catch (error) {
      console.error('Error loading active tasks:', error)
    }
    */
  }

  const generateMockAgents = (): Agent[] => {
    const specializations = ['content', 'development', 'design', 'analysis', 'marketing', 'translation', 'video', 'audio']
    const agentList: Agent[] = []

    // Create 152 agents with varied specializations
    for (let i = 1; i <= 152; i++) {
      agentList.push({
        name: `agent_${i.toString().padStart(3, '0')}`,
        status: Math.random() > 0.7 ? 'working' : 'idle',
        completedTasks: Math.floor(Math.random() * 50),
        revenue: Math.floor(Math.random() * 5000),
        successRate: 0.75 + Math.random() * 0.25,
        specialization: specializations[Math.floor(Math.random() * specializations.length)]
      })
    }

    // Add specific named agents
    agentList[0] = { ...agentList[0], name: 'real_content_creator', specialization: 'content' }
    agentList[1] = { ...agentList[1], name: 'code_generator_agent', specialization: 'development' }
    agentList[2] = { ...agentList[2], name: 'ui_designer_agent', specialization: 'design' }
    agentList[3] = { ...agentList[3], name: 'data_analyst_agent', specialization: 'analysis' }

    return agentList
  }

  // Commented out - using real data from WebSocket instead
  /*
  const simulateAgentActivity = () => {
    // Simulate random agent becoming active
    if (Math.random() > 0.5 && agents.length > 0) {
      const randomAgent = agents[Math.floor(Math.random() * agents.length)]

      if (randomAgent.status === 'idle') {
        // Start a new task
        const newTask: ActiveTask = {
          id: `task_${Date.now()}`,
          agentName: randomAgent.name,
          taskType: getRandomTaskType(randomAgent.specialization),
          progress: 0,
          estimatedTime: `${Math.floor(Math.random() * 30 + 10)}s`,
          value: Math.floor(Math.random() * 500 + 100),
          status: 'analyzing'
        }

        setActiveTasks(prev => [...prev, newTask])

        // Update agent status
        setAgents(prev => prev.map(a =>
          a.name === randomAgent.name
            ? { ...a, status: 'working', currentTask: newTask.taskType }
            : a
        ))

        setActiveAgents(prev => prev + 1)
      }
    }

    // Update existing tasks progress
    setActiveTasks(prev => prev.map(task => {
      if (task.status === 'completed') return task

      const newProgress = Math.min(task.progress + Math.random() * 20, 100)

      if (newProgress >= 100) {
        // Task completed - create deliverable
        const deliverable: Deliverable = {
          id: `del_${Date.now()}`,
          type: task.taskType,
          title: `${task.taskType} - ${new Date().toLocaleTimeString()}`,
          agent: task.agentName,
          value: task.value,
          createdAt: new Date().toISOString(),
          status: 'ready'
        }

        setDeliverables(prev => [deliverable, ...prev].slice(0, 20))
        setTotalRevenue(prev => prev + task.value)
        setTasksCompleted(prev => prev + 1)

        // Update agent status
        setAgents(prev => prev.map(a =>
          a.name === task.agentName
            ? {
                ...a,
                status: 'idle',
                currentTask: undefined,
                completedTasks: a.completedTasks + 1,
                revenue: a.revenue + task.value,
                lastActive: new Date().toISOString()
              }
            : a
        ))

        setActiveAgents(prev => Math.max(0, prev - 1))

        return { ...task, progress: 100, status: 'completed' }
      }

      // Update status based on progress
      let newStatus = task.status
      if (newProgress > 30 && newProgress <= 70) newStatus = 'executing'
      if (newProgress > 70) newStatus = 'generating'

      return { ...task, progress: newProgress, status: newStatus }
    }))

    // Remove completed tasks after a delay
    setActiveTasks(prev => prev.filter(t => t.status !== 'completed' || t.progress < 100))
  }
  */

  // Commented out - not needed with real data
  /*
  const getRandomTaskType = (specialization: string): string => {
    const taskTypes: { [key: string]: string[] } = {
      content: ['Blog Post', 'Article', 'Product Description', 'Email Copy'],
      development: ['React Component', 'API Endpoint', 'Database Schema', 'Python Script'],
      design: ['Logo Design', 'UI Mockup', 'Brand Identity', 'Social Media Graphics'],
      analysis: ['Data Analysis', 'Market Research', 'Performance Report', 'SEO Audit'],
      marketing: ['Campaign Strategy', 'Social Media Plan', 'Ad Copy', 'Landing Page'],
      translation: ['Document Translation', 'Website Localization', 'Subtitle Creation'],
      video: ['Video Editing', 'Motion Graphics', 'Thumbnail Design', 'Intro Animation'],
      audio: ['Podcast Editing', 'Voice Over', 'Sound Design', 'Music Production']
    }

    const tasks = taskTypes[specialization] || taskTypes.content
    return tasks[Math.floor(Math.random() * tasks.length)]
  }
  */

  const updateTask = (task: ActiveTask) => {
    setActiveTasks(prev => prev.map(t => t.id === task.id ? task : t))
  }

  const addDeliverable = (deliverable: Deliverable) => {
    setDeliverables(prev => [deliverable, ...prev].slice(0, 20))
  }

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'working': return 'text-green-500'
      case 'idle': return 'text-gray-500'
      case 'completed': return 'text-blue-500'
      default: return 'text-gray-400'
    }
  }

  const getTaskStatusColor = (status: string) => {
    switch(status) {
      case 'analyzing': return 'bg-yellow-500'
      case 'executing': return 'bg-blue-500'
      case 'generating': return 'bg-green-500'
      case 'completed': return 'bg-purple-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="bg-gray-900 text-white p-6 rounded-lg">
      {/* Header Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <Bot className="h-8 w-8 text-blue-500" />
            <span className="text-2xl font-bold">{agents.length}</span>
          </div>
          <p className="text-gray-400 text-sm">Total Agents</p>
          <p className="text-green-500 text-xs mt-1">{activeAgents} active</p>
        </div>

        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <Activity className="h-8 w-8 text-green-500" />
            <span className="text-2xl font-bold">{activeTasks.length}</span>
          </div>
          <p className="text-gray-400 text-sm">Active Tasks</p>
          <p className="text-blue-500 text-xs mt-1">{tasksCompleted} completed</p>
        </div>

        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="h-8 w-8 text-yellow-500" />
            <span className="text-2xl font-bold">${totalRevenue.toLocaleString()}</span>
          </div>
          <p className="text-gray-400 text-sm">Total Revenue</p>
          <p className="text-green-500 text-xs mt-1">+${revenuePerSecond}/sec</p>
        </div>

        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <FileText className="h-8 w-8 text-purple-500" />
            <span className="text-2xl font-bold">{deliverables.length}</span>
          </div>
          <p className="text-gray-400 text-sm">Deliverables</p>
          <p className="text-green-500 text-xs mt-1">Ready for delivery</p>
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-3 gap-6">
        {/* Agent Registry (Left) */}
        <div className="bg-gray-800 rounded-lg p-4 max-h-[600px] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold">Agent Registry</h3>
            <span className="text-xs text-green-500">
              {wsConnected ? '● Connected' : '● Disconnected'}
            </span>
          </div>

          <div className="space-y-2">
            {agents.slice(0, 20).map((agent, index) => (
              <div
                key={`${agent.name}-${index}`}
                className="bg-gray-700 p-2 rounded cursor-pointer hover:bg-gray-600 transition"
                onClick={() => setSelectedAgent(agent)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Bot className={`h-4 w-4 ${getStatusColor(agent.status)}`} />
                    <span className="text-sm font-medium">{agent.name}</span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${
                    agent.status === 'working' ? 'bg-green-900 text-green-300' :
                    agent.status === 'completed' ? 'bg-blue-900 text-blue-300' :
                    'bg-gray-600 text-gray-300'
                  }`}>
                    {agent.status}
                  </span>
                </div>
                {agent.currentTask && (
                  <>
                    <p className="text-xs text-gray-400 mt-1">Working on: {agent.currentTask}</p>
                    {agent.progress !== undefined && (
                      <div className="mt-2">
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                          <span>{agent.projectStatus || 'active'}</span>
                          <span>{agent.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-green-500 h-full transition-all duration-500"
                            style={{ width: `${agent.progress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </>
                )}
                <div className="flex justify-between mt-1">
                  <span className="text-xs text-gray-400">Tasks: {agent.completedTasks}</span>
                  <span className="text-xs text-green-400">${agent.revenue}</span>
                </div>
              </div>
            ))}
          </div>

          {agents.length > 20 && (
            <p className="text-center text-xs text-gray-500 mt-4">
              +{agents.length - 20} more agents...
            </p>
          )}
        </div>

        {/* Active Tasks (Center) */}
        <div className="bg-gray-800 rounded-lg p-4 max-h-[600px] overflow-y-auto">
          <h3 className="text-lg font-bold mb-4">Live Task Execution</h3>

          <div className="space-y-3">
            {activeTasks.map((task) => (
              <div key={task.id} className="bg-gray-700 p-3 rounded">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <Zap className="h-4 w-4 text-yellow-500" />
                    <span className="text-sm font-medium">
                      {task.title || task.taskType}
                    </span>
                  </div>
                  <span className="text-xs text-green-400">${task.value?.toLocaleString()}</span>
                </div>

                {task.platform && (
                  <div className="text-xs text-blue-400 mb-1">
                    Platform: {task.platform}
                  </div>
                )}

                {task.description && (
                  <div className="text-xs text-gray-300 mb-2 line-clamp-2">
                    {task.description}
                  </div>
                )}

                {task.skills && task.skills.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {task.skills.slice(0, 3).map((skill, idx) => (
                      <span key={idx} className="text-xs bg-gray-600 px-1.5 py-0.5 rounded">
                        {skill}
                      </span>
                    ))}
                    {task.skills.length > 3 && (
                      <span className="text-xs text-gray-500">+{task.skills.length - 3}</span>
                    )}
                  </div>
                )}

                <div className="text-xs text-gray-400 mb-2">
                  Agent: {task.agentName} • Est: {task.estimatedTime}
                </div>

                <div className="w-full bg-gray-600 rounded-full h-2 mb-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${getTaskStatusColor(task.status)}`}
                    style={{ width: `${task.progress}%` }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">
                    Status: {task.status}
                  </span>
                  <span className="text-xs text-gray-400">
                    {Math.round(task.progress)}%
                  </span>
                </div>

                {task.url && (
                  <a
                    href={task.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-400 hover:text-blue-300 mt-2 inline-block"
                  >
                    View Job →
                  </a>
                )}
              </div>
            ))}

            {activeTasks.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                <Activity className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Waiting for tasks...</p>
              </div>
            )}
          </div>
        </div>

        {/* Deliverables (Right) */}
        <div className="bg-gray-800 rounded-lg p-4 max-h-[600px] overflow-y-auto">
          <h3 className="text-lg font-bold mb-4">Generated Deliverables</h3>

          <div className="space-y-3">
            {deliverables.map((deliverable) => (
              <div key={deliverable.id} className="bg-gray-700 p-3 rounded">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-4 w-4 text-purple-500" />
                    <span className="text-sm font-medium">{deliverable.type}</span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${
                    deliverable.status === 'ready' ? 'bg-green-900 text-green-300' :
                    deliverable.status === 'delivered' ? 'bg-blue-900 text-blue-300' :
                    'bg-yellow-900 text-yellow-300'
                  }`}>
                    {deliverable.status}
                  </span>
                </div>

                <p className="text-xs text-gray-400 mb-1">
                  By: {deliverable.agent}
                </p>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    {new Date(deliverable.createdAt).toLocaleTimeString()}
                  </span>
                  <span className="text-xs text-green-400">
                    ${deliverable.value}
                  </span>
                </div>

                {deliverable.wordCount && (
                  <p className="text-xs text-gray-500 mt-1">
                    {deliverable.wordCount} words
                  </p>
                )}
              </div>
            ))}

            {deliverables.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No deliverables yet...</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Selected Agent Details */}
      {selectedAgent && (
        <div className="mt-6 bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-md font-bold">Agent Details: {selectedAgent.name}</h4>
            <button
              onClick={() => setSelectedAgent(null)}
              className="text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-gray-400">Specialization</p>
              <p className="text-sm">{selectedAgent.specialization}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Success Rate</p>
              <p className="text-sm">{(selectedAgent.successRate * 100).toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Tasks Completed</p>
              <p className="text-sm">{selectedAgent.completedTasks}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Total Revenue</p>
              <p className="text-sm text-green-400">${selectedAgent.revenue}</p>
            </div>
          </div>

          {selectedAgent.lastActive && (
            <p className="text-xs text-gray-500 mt-3">
              Last active: {new Date(selectedAgent.lastActive).toLocaleString()}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default RealTimeAgentMonitor