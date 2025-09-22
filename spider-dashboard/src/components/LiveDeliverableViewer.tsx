import { useState, useEffect } from 'react'
import { FileText, Code, Image, Video, Music, File, Download, Eye, CheckCircle, Clock, TrendingUp, Zap } from 'lucide-react'

interface Deliverable {
  id: string
  type: 'blog_post' | 'code' | 'design' | 'video' | 'audio' | 'document' | 'data_analysis'
  title: string
  description: string
  agent: string
  createdAt: string
  status: 'generating' | 'processing' | 'ready' | 'delivered'
  progress: number
  value: number
  fileSize?: string
  wordCount?: number
  linesOfCode?: number
  duration?: string
  preview?: string
  downloadUrl?: string
}

const LiveDeliverableViewer = () => {
  const [deliverables, setDeliverables] = useState<Deliverable[]>([])
  const [selectedDeliverable, setSelectedDeliverable] = useState<Deliverable | null>(null)
  const [wsConnected, setWsConnected] = useState(false)
  const [totalValue, setTotalValue] = useState(0)
  const [generatingCount, setGeneratingCount] = useState(0)
  const [showFullPreview, setShowFullPreview] = useState(false)

  useEffect(() => {
    let ws: WebSocket | null = null
    let reconnectTimer: NodeJS.Timeout | null = null
    let isComponentMounted = true

    const connect = () => {
      if (!isComponentMounted) return

      ws = new WebSocket('ws://localhost:8000/ws/deliverables/')

      ws.onopen = () => {
        console.log('Connected to deliverables WebSocket')
        setWsConnected(true)
        // Request initial data
        ws?.send(JSON.stringify({ type: 'request_deliverables' }))
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
        setWsConnected(false)
        // Auto-reconnect after 3 seconds if component is still mounted
        if (isComponentMounted) {
          console.log('Will reconnect deliverables WebSocket in 3 seconds...')
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
      case 'deliverable_started':
        addDeliverable(data.deliverable)
        break
      case 'deliverable_progress':
        updateDeliverableProgress(data.id, data.progress)
        break
      case 'deliverable_completed':
        completeDeliverable(data.id, data.details)
        break
    }
  }

  const generateInitialDeliverables = (): Deliverable[] => {
    return [
      {
        id: 'del_001',
        type: 'blog_post',
        title: '10 AI Productivity Tools for Remote Workers',
        description: 'Comprehensive guide covering the latest AI tools that boost productivity for remote teams',
        agent: 'real_content_creator',
        createdAt: new Date(Date.now() - 3600000).toISOString(),
        status: 'ready',
        progress: 100,
        value: 250,
        wordCount: 2500,
        preview: 'In today\'s rapidly evolving digital landscape, remote workers are increasingly turning to AI-powered tools to enhance their productivity...'
      },
      {
        id: 'del_002',
        type: 'code',
        title: 'E-commerce Analytics Dashboard',
        description: 'React dashboard with real-time sales analytics and data visualization',
        agent: 'code_generator_agent',
        createdAt: new Date(Date.now() - 1800000).toISOString(),
        status: 'ready',
        progress: 100,
        value: 750,
        linesOfCode: 1245,
        preview: `import React from 'react'\nimport { LineChart, BarChart } from 'recharts'\n\nconst Dashboard = () => {\n  // Real-time data processing\n  ...`
      },
      {
        id: 'del_003',
        type: 'design',
        title: 'Modern Tech Startup Logo Package',
        description: 'Complete brand identity with logo variations, color palette, and usage guidelines',
        agent: 'ui_designer_agent',
        createdAt: new Date(Date.now() - 900000).toISOString(),
        status: 'processing',
        progress: 75,
        value: 500,
        fileSize: '15.2 MB'
      }
    ]
  }

  // Full content samples for realistic previews
  const getFullContent = (type: Deliverable['type']): string => {
    const contents = {
      blog_post: `# The Future of AI in Remote Work: A Comprehensive Guide

## Introduction

In the rapidly evolving landscape of remote work, artificial intelligence has emerged as a game-changing force that's reshaping how we collaborate, communicate, and achieve productivity from anywhere in the world. This comprehensive guide explores the transformative impact of AI on remote work environments and provides actionable insights for both individuals and organizations.

## The Current State of Remote Work

Remote work has transitioned from a temporary pandemic measure to a permanent fixture in the modern workplace. According to recent studies, over 35% of workers in knowledge-based industries now work remotely at least part-time, with this number expected to reach 50% by 2025.

### Key Statistics:
- 74% of companies plan to permanently shift to remote work
- Remote workers report 22% higher productivity levels
- Organizations save an average of $11,000 per year per remote worker
- 87% of workers offered remote work embrace the opportunity

## How AI is Transforming Remote Collaboration

### 1. Intelligent Meeting Assistants

AI-powered meeting assistants have revolutionized virtual collaboration by:
- Automatically transcribing meetings in real-time
- Generating actionable meeting summaries
- Identifying key decisions and action items
- Providing sentiment analysis to gauge team engagement

**Example Tools:**
- Otter.ai for transcription and note-taking
- Fireflies.ai for meeting intelligence
- Fellow for meeting management and follow-ups

### 2. Smart Project Management

AI enhances project management through:
- Predictive analytics for deadline estimation
- Automated task allocation based on team member skills
- Risk identification and mitigation suggestions
- Progress tracking and bottleneck detection

### 3. Enhanced Communication

Natural Language Processing (NLP) improvements enable:
- Real-time translation for global teams
- Tone analysis to prevent miscommunication
- Smart email categorization and prioritization
- Automated response suggestions

## The Productivity Revolution

### Time Management Optimization

AI algorithms analyze work patterns to:
- Identify peak productivity hours
- Suggest optimal break times
- Block focus time automatically
- Minimize context switching

### Automated Workflows

Repetitive tasks are eliminated through:
- Intelligent document processing
- Automated data entry and validation
- Smart scheduling and calendar management
- Predictive text and code completion

## Challenges and Considerations

While AI offers tremendous benefits, organizations must address:

### Privacy and Security
- Data protection in AI-powered tools
- Compliance with international regulations
- Employee monitoring ethics
- Secure handling of sensitive information

### Human Connection
- Maintaining team cohesion
- Preventing AI over-reliance
- Preserving creativity and innovation
- Ensuring inclusive technology adoption

## Best Practices for Implementation

### 1. Start Small
Begin with pilot programs in specific departments before company-wide rollout.

### 2. Prioritize Training
Invest in comprehensive training programs to ensure effective tool adoption.

### 3. Measure Impact
Establish KPIs to track productivity improvements and ROI.

### 4. Gather Feedback
Regularly solicit employee feedback to optimize AI tool selection and usage.

### 5. Maintain Balance
Ensure AI enhances rather than replaces human interaction and creativity.

## The Future Outlook

As we look ahead, several trends will shape the future of AI in remote work:

### Emerging Technologies
- Virtual Reality (VR) workspaces for immersive collaboration
- Advanced AI avatars for more natural virtual presence
- Quantum computing for complex problem-solving
- Brain-computer interfaces for direct thought communication

### Predicted Developments
- 90% of remote workers will use AI tools daily by 2026
- AI will automate 40% of current administrative tasks
- Personalized AI assistants will become standard for all workers
- Hybrid AI-human teams will outperform traditional structures

## Conclusion

The integration of AI into remote work represents not just a technological shift, but a fundamental reimagining of how we approach productivity, collaboration, and work-life balance. Organizations that embrace these changes thoughtfully and strategically will find themselves at the forefront of the next evolution in work.

As we continue to navigate this transformation, the key lies not in replacing human capabilities but in augmenting them—creating a synergy between human creativity and AI efficiency that unlocks unprecedented levels of innovation and productivity.

---

*This article was generated using advanced AI content generation technology, demonstrating the very capabilities discussed within. The future of work is not coming—it's already here.*`,

      code: `"""
Advanced E-commerce Analytics Dashboard
========================================
A comprehensive React-based analytics system with real-time data processing,
predictive analytics, and automated reporting capabilities.
"""

import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { format, subDays, startOfMonth, endOfMonth, eachDayOfInterval } from 'date-fns'
import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, Users, Package, AlertCircle, CheckCircle } from 'lucide-react'
import axios from 'axios'

// Custom hooks for data fetching and processing
const useRealtimeData = (endpoint, interval = 5000) => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(endpoint)
        setData(response.data)
        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const timer = setInterval(fetchData, interval)

    return () => clearInterval(timer)
  }, [endpoint, interval])

  return { data, loading, error }
}

// Predictive Analytics Engine
class PredictiveAnalytics {
  constructor(historicalData) {
    this.data = historicalData
    this.model = this.trainModel()
  }

  trainModel() {
    // Simple linear regression for demo
    const n = this.data.length
    const sumX = this.data.reduce((sum, _, i) => sum + i, 0)
    const sumY = this.data.reduce((sum, d) => sum + d.value, 0)
    const sumXY = this.data.reduce((sum, d, i) => sum + i * d.value, 0)
    const sumX2 = this.data.reduce((sum, _, i) => sum + i * i, 0)

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
    const intercept = (sumY - slope * sumX) / n

    return { slope, intercept }
  }

  predict(daysAhead = 30) {
    const predictions = []
    const lastIndex = this.data.length - 1

    for (let i = 1; i <= daysAhead; i++) {
      const predictedValue = this.model.slope * (lastIndex + i) + this.model.intercept
      predictions.push({
        date: format(subDays(new Date(), -i), 'MMM dd'),
        value: Math.max(0, predictedValue),
        isPrediction: true
      })
    }

    return predictions
  }

  calculateTrend() {
    return this.model.slope > 0 ? 'increasing' : 'decreasing'
  }

  calculateGrowthRate() {
    const firstValue = this.data[0]?.value || 1
    const lastValue = this.data[this.data.length - 1]?.value || 1
    return ((lastValue - firstValue) / firstValue * 100).toFixed(2)
  }
}

// Main Dashboard Component
const AnalyticsDashboard = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('7d')
  const [selectedMetric, setSelectedMetric] = useState('revenue')
  const [showPredictions, setShowPredictions] = useState(true)

  // Fetch real-time data
  const { data: salesData, loading: salesLoading } = useRealtimeData('/api/sales')
  const { data: customerData, loading: customerLoading } = useRealtimeData('/api/customers')
  const { data: productData, loading: productLoading } = useRealtimeData('/api/products')

  // Process data for charts
  const processedData = useMemo(() => {
    if (!salesData) return null

    const processed = salesData.map(item => ({
      ...item,
      revenue: item.amount * item.quantity,
      profit: item.amount * item.quantity * 0.3,
      date: format(new Date(item.date), 'MMM dd')
    }))

    // Add predictions if enabled
    if (showPredictions) {
      const analytics = new PredictiveAnalytics(processed)
      const predictions = analytics.predict()
      return [...processed, ...predictions]
    }

    return processed
  }, [salesData, showPredictions])

  // Calculate KPIs
  const kpis = useMemo(() => {
    if (!processedData) return {}

    const totalRevenue = processedData
      .filter(d => !d.isPrediction)
      .reduce((sum, d) => sum + d.revenue, 0)

    const avgOrderValue = totalRevenue / processedData.filter(d => !d.isPrediction).length

    const conversionRate = (Math.random() * 5 + 2).toFixed(2) // Mock for demo

    const analytics = new PredictiveAnalytics(processedData.filter(d => !d.isPrediction))

    return {
      totalRevenue,
      avgOrderValue,
      conversionRate,
      growthRate: analytics.calculateGrowthRate(),
      trend: analytics.calculateTrend()
    }
  }, [processedData])

  // Render metric cards
  const MetricCard = ({ title, value, icon: Icon, change, trend }) => (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Icon className="h-8 w-8 text-blue-500 mr-3" />
          <h3 className="text-lg font-semibold text-gray-700">{title}</h3>
        </div>
        {trend && (
          <div className={\`flex items-center \${trend === 'up' ? 'text-green-500' : 'text-red-500'}\`}>
            {trend === 'up' ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
            <span className="ml-1 text-sm font-medium">{change}%</span>
          </div>
        )}
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  )

  // Render main dashboard
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">E-commerce Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Real-time insights and predictive analytics</p>
        </div>

        {/* Period Selector */}
        <div className="mb-6 flex items-center space-x-4">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
          </select>

          <button
            onClick={() => setShowPredictions(!showPredictions)}
            className={\`px-4 py-2 rounded-lg transition-colors \${
              showPredictions
                ? 'bg-blue-500 text-white hover:bg-blue-600'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }\`}
          >
            {showPredictions ? 'Hide' : 'Show'} Predictions
          </button>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Revenue"
            value={\`$\${kpis.totalRevenue?.toLocaleString() || '0'}\`}
            icon={DollarSign}
            change={kpis.growthRate}
            trend={kpis.trend === 'increasing' ? 'up' : 'down'}
          />
          <MetricCard
            title="Average Order Value"
            value={\`$\${kpis.avgOrderValue?.toFixed(2) || '0'}\`}
            icon={ShoppingCart}
            change="12.5"
            trend="up"
          />
          <MetricCard
            title="Conversion Rate"
            value={\`\${kpis.conversionRate || '0'}%\`}
            icon={Users}
            change="8.3"
            trend="up"
          />
          <MetricCard
            title="Active Products"
            value={productData?.length || '0'}
            icon={Package}
            change="5.2"
            trend="up"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Revenue Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Revenue Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={processedData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => \`$\${value.toFixed(2)}\`} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#3B82F6"
                  fill="#93C5FD"
                  strokeWidth={2}
                />
                {showPredictions && (
                  <Area
                    type="monotone"
                    dataKey="isPrediction"
                    stroke="#10B981"
                    fill="#86EFAC"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                  />
                )}
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Product Performance */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Top Products</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={productData?.slice(0, 5)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="sales" fill="#8B5CF6" />
                <Bar dataKey="revenue" fill="#EC4899" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Real-time Activity Feed */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Real-time Activity</h3>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  <div>
                    <p className="text-sm font-medium">New order #{1000 + i}</p>
                    <p className="text-xs text-gray-600">{format(new Date(), 'HH:mm:ss')}</p>
                  </div>
                </div>
                <span className="text-sm font-semibold text-green-600">
                  +${(Math.random() * 500 + 50).toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AnalyticsDashboard`,

      design: `<!-- Modern Tech Startup Brand Identity Package -->
<!-- Complete HTML/CSS Design System -->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NexusAI - Brand Identity System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            /* Primary Brand Colors */
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --primary-color: #667eea;
            --primary-dark: #5a67d8;
            --primary-light: #818cf8;

            /* Secondary Colors */
            --secondary-color: #764ba2;
            --accent-color: #f6ad55;
            --success-color: #48bb78;
            --warning-color: #ed8936;
            --error-color: #f56565;

            /* Neutral Colors */
            --gray-900: #1a202c;
            --gray-800: #2d3748;
            --gray-700: #4a5568;
            --gray-600: #718096;
            --gray-500: #a0aec0;
            --gray-400: #cbd5e0;
            --gray-300: #e2e8f0;
            --gray-200: #edf2f7;
            --gray-100: #f7fafc;

            /* Typography */
            --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-display: 'Poppins', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        body {
            font-family: var(--font-primary);
            line-height: 1.6;
            color: var(--gray-900);
            background: var(--gray-100);
        }

        /* Logo Variations */
        .logo-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 2rem;
        }

        .logo-card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .logo-primary {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            background: var(--primary-gradient);
            border-radius: 8px;
        }

        .logo-mark {
            width: 60px;
            height: 60px;
            background: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 24px;
            color: var(--primary-color);
            margin-right: 1rem;
        }

        .logo-text {
            color: white;
            font-size: 32px;
            font-weight: 700;
            font-family: var(--font-display);
        }

        /* Color Palette */
        .color-palette {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 1rem;
            padding: 2rem;
        }

        .color-swatch {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .color-display {
            height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }

        .color-info {
            padding: 1rem;
            text-align: center;
        }

        .color-name {
            font-weight: 600;
            color: var(--gray-800);
        }

        .color-code {
            font-size: 12px;
            color: var(--gray-600);
            font-family: var(--font-mono);
        }

        /* Typography Specimens */
        .typography-section {
            padding: 2rem;
            background: white;
            margin: 2rem;
            border-radius: 12px;
        }

        h1.display { font-size: 4rem; font-weight: 900; line-height: 1.1; }
        h1 { font-size: 3rem; font-weight: 800; }
        h2 { font-size: 2.25rem; font-weight: 700; }
        h3 { font-size: 1.875rem; font-weight: 600; }
        h4 { font-size: 1.5rem; font-weight: 600; }
        h5 { font-size: 1.25rem; font-weight: 500; }
        h6 { font-size: 1rem; font-weight: 500; }

        .lead { font-size: 1.25rem; color: var(--gray-600); }
        .body { font-size: 1rem; line-height: 1.75; }
        .small { font-size: 0.875rem; color: var(--gray-600); }
        .caption { font-size: 0.75rem; color: var(--gray-500); }

        /* UI Components */
        .component-showcase {
            padding: 2rem;
            display: grid;
            gap: 2rem;
        }

        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
        }

        .btn-primary {
            background: var(--primary-gradient);
            color: white;
        }

        .btn-secondary {
            background: var(--gray-200);
            color: var(--gray-800);
        }

        .btn-outline {
            background: transparent;
            border: 2px solid var(--primary-color);
            color: var(--primary-color);
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .input {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid var(--gray-300);
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }

        .input:focus {
            outline: none;
            border-color: var(--primary-color);
        }

        /* Icon System */
        .icon-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            gap: 1rem;
            padding: 2rem;
        }

        .icon-item {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.3s ease;
        }

        .icon-item:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }

        /* Pattern Library */
        .pattern {
            height: 200px;
            border-radius: 8px;
            margin: 1rem 0;
        }

        .pattern-dots {
            background-image: radial-gradient(circle, var(--primary-color) 1px, transparent 1px);
            background-size: 20px 20px;
        }

        .pattern-grid {
            background-image:
                linear-gradient(var(--gray-300) 1px, transparent 1px),
                linear-gradient(90deg, var(--gray-300) 1px, transparent 1px);
            background-size: 20px 20px;
        }

        .pattern-waves {
            background: linear-gradient(135deg, var(--primary-color) 25%, transparent 25%) -50px 0,
                        linear-gradient(225deg, var(--primary-color) 25%, transparent 25%) -50px 0,
                        linear-gradient(315deg, var(--primary-color) 25%, transparent 25%),
                        linear-gradient(45deg, var(--primary-color) 25%, transparent 25%);
            background-size: 100px 100px;
            background-color: var(--primary-light);
        }
    </style>
</head>
<body>
    <!-- Brand Identity Content Here -->
    <div class="container">
        <h1 class="display">NexusAI Brand Identity</h1>
        <!-- Full design system implementation continues... -->
    </div>
</body>
</html>`,

      data_analysis: `# Comprehensive Market Analysis Report
## Q4 2024 Performance Metrics & Strategic Insights

### Executive Summary

This comprehensive analysis examines market performance across 15 key sectors, identifying growth opportunities, risk factors, and strategic recommendations based on advanced data analytics and machine learning models.

### Key Findings

1. **Market Growth**: Overall market expansion of 23.7% YoY
2. **Top Performers**: Technology (+42%), Healthcare (+31%), Renewable Energy (+28%)
3. **Risk Areas**: Traditional Retail (-12%), Commercial Real Estate (-8%)
4. **Emerging Opportunities**: AI/ML Services, Sustainable Tech, Digital Health

### Detailed Analysis

#### Sector Performance

| Sector | Q4 Growth | YoY Change | Market Share | Trend |
|--------|-----------|------------|--------------|-------|
| Technology | 12.3% | +42% | 24.5% | ↑ Strong |
| Healthcare | 8.7% | +31% | 18.2% | ↑ Strong |
| Finance | 5.2% | +15% | 21.3% | ↑ Moderate |
| Energy | 9.1% | +28% | 12.7% | ↑ Strong |
| Retail | -3.2% | -12% | 8.4% | ↓ Weak |

#### Customer Behavior Patterns

**Digital Transformation Impact:**
- 78% increase in online transactions
- Average transaction value up 34%
- Mobile commerce now represents 67% of total e-commerce
- Customer acquisition cost decreased by 23%

**Demographic Shifts:**
- Millennials: 42% of total market spend
- Gen Z: Fastest growing segment (+156% YoY)
- Baby Boomers: Shifting to digital channels (+89%)

#### Competitive Landscape

**Market Concentration:**
- Top 5 players control 43% market share
- New entrants captured 12% in 2024
- M&A activity increased by 67%

**Innovation Index:**
- R&D spending up 45% industry-wide
- 234 new patents filed in Q4
- AI integration in 73% of new products

### Statistical Models & Predictions

#### Regression Analysis Results

\`\`\`python
# Multiple Linear Regression Model
# Dependent Variable: Market Growth
# Independent Variables: Tech Adoption, Consumer Confidence, Interest Rates

Model Summary:
R-squared: 0.847
Adjusted R-squared: 0.834
F-statistic: 156.23 (p < 0.001)

Coefficients:
- Tech Adoption: β = 0.523 (p < 0.001)
- Consumer Confidence: β = 0.312 (p < 0.01)
- Interest Rates: β = -0.198 (p < 0.05)
\`\`\`

#### Time Series Forecast

Using ARIMA(2,1,2) model with seasonal adjustment:

**Q1 2025 Projections:**
- Expected Growth: 7.8% (CI: 6.2% - 9.4%)
- Revenue Forecast: $2.34B (CI: $2.18B - $2.51B)
- Market Expansion: 14.2% probability of exceeding targets

### Risk Assessment Matrix

| Risk Factor | Probability | Impact | Mitigation Strategy |
|-------------|------------|--------|-------------------|
| Supply Chain Disruption | Medium (43%) | High | Diversify suppliers, increase inventory |
| Regulatory Changes | High (67%) | Medium | Compliance monitoring, legal consultation |
| Economic Recession | Low (22%) | Very High | Cash reserves, flexible operations |
| Cyber Security | Medium (51%) | High | Enhanced security protocols, insurance |

### Strategic Recommendations

#### Immediate Actions (0-3 months)
1. Accelerate digital transformation initiatives
2. Optimize supply chain for resilience
3. Enhance customer retention programs
4. Implement dynamic pricing strategies

#### Medium-term Strategy (3-12 months)
1. Expand into high-growth segments
2. Develop AI-powered analytics capabilities
3. Build strategic partnerships
4. Launch sustainability initiatives

#### Long-term Vision (1-3 years)
1. Position for market leadership
2. Create ecosystem-based business model
3. Invest in emerging technologies
4. Develop global expansion strategy

### Data Methodology

**Data Sources:**
- Primary: 10,000+ customer surveys, 500+ stakeholder interviews
- Secondary: Industry reports, government statistics, academic research
- Real-time: API integrations with 25+ data providers

**Analytical Techniques:**
- Machine Learning: Random Forest, XGBoost, Neural Networks
- Statistical Analysis: Regression, Time Series, Clustering
- Visualization: Tableau, Power BI, Custom D3.js dashboards

### Conclusion

The market presents significant opportunities despite emerging challenges. Organizations that embrace digital transformation, maintain operational agility, and focus on customer-centric innovation will be best positioned for success in 2025 and beyond.

---

*This report was generated using advanced AI analytics and should be reviewed in conjunction with human expertise for strategic decision-making.*`,

      document: `# Technical Documentation: Microservices Architecture Implementation Guide

## Version 2.0.0 | Last Updated: September 2024

### Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Service Definitions](#service-definitions)
4. [API Specifications](#api-specifications)
5. [Deployment Guide](#deployment-guide)
6. [Monitoring & Logging](#monitoring--logging)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

This comprehensive technical documentation provides detailed guidance for implementing and maintaining a microservices architecture using Docker, Kubernetes, and cloud-native technologies. This guide is intended for DevOps engineers, system architects, and development teams working on distributed systems.

### Prerequisites

- Docker 24.0+ and Docker Compose 2.20+
- Kubernetes 1.28+ cluster (EKS, GKE, or AKS)
- Helm 3.12+ for package management
- Basic understanding of RESTful APIs and gRPC
- Familiarity with CI/CD pipelines

### System Requirements

**Minimum Development Environment:**
- CPU: 4 cores (8 recommended)
- RAM: 16GB (32GB recommended)
- Storage: 100GB SSD
- OS: Linux (Ubuntu 22.04 LTS) / macOS 13+ / Windows 11 with WSL2

## Architecture Overview

### High-Level Design

The system implements a distributed microservices architecture with the following key components:

\`\`\`yaml
services:
  api-gateway:
    type: "Kong Gateway"
    port: 8080
    features:
      - rate-limiting
      - authentication
      - request-routing
      - load-balancing

  service-mesh:
    type: "Istio"
    version: "1.19"
    features:
      - traffic-management
      - security
      - observability
      - policy-enforcement

  message-broker:
    type: "Apache Kafka"
    version: "3.5"
    configuration:
      replicas: 3
      partitions: 10
      retention: "7d"
\`\`\`

### Service Communication Patterns

1. **Synchronous Communication**: REST/gRPC for real-time requests
2. **Asynchronous Communication**: Event-driven using Kafka
3. **Service Discovery**: Consul/Kubernetes DNS
4. **Circuit Breaker**: Hystrix pattern implementation

## Service Definitions

### User Service

**Purpose**: Manages user authentication, authorization, and profile management

**Technology Stack:**
- Language: Node.js 18 LTS
- Framework: Express.js 4.18
- Database: PostgreSQL 15
- Cache: Redis 7.2

**API Endpoints:**

\`\`\`typescript
interface UserService {
  // Authentication
  POST   /auth/login
  POST   /auth/logout
  POST   /auth/refresh
  POST   /auth/register

  // User Management
  GET    /users/:id
  PUT    /users/:id
  DELETE /users/:id
  GET    /users/profile

  // Authorization
  GET    /users/:id/permissions
  POST   /users/:id/roles
}
\`\`\`

### Order Service

**Purpose**: Handles order processing, inventory management, and fulfillment

**Database Schema:**

\`\`\`sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
\`\`\`

## API Specifications

### OpenAPI 3.0 Specification

\`\`\`yaml
openapi: 3.0.0
info:
  title: Microservices API
  version: 2.0.0
  description: Comprehensive API documentation for microservices

servers:
  - url: https://api.production.example.com
    description: Production server
  - url: https://api.staging.example.com
    description: Staging server

paths:
  /health:
    get:
      summary: Health check endpoint
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "healthy"
                  timestamp:
                    type: string
                    format: date-time
\`\`\`

## Deployment Guide

### Kubernetes Deployment

**1. Create Namespace:**

\`\`\`bash
kubectl create namespace microservices
kubectl config set-context --current --namespace=microservices
\`\`\`

**2. Deploy Services:**

\`\`\`yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: microservices
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: registry.example.com/user-service:2.0.0
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
\`\`\`

### Docker Compose Development

\`\`\`yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: microservices
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7.2-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  user-service:
    build:
      context: ./services/user
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://admin:secure_password@postgres:5432/microservices
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    ports:
      - "3001:3000"
    volumes:
      - ./services/user:/app
      - /app/node_modules

volumes:
  postgres_data:
  redis_data:
\`\`\`

## Monitoring & Logging

### Prometheus Configuration

\`\`\`yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
\`\`\`

### Grafana Dashboard Configuration

Key metrics to monitor:
- Request rate (req/sec)
- Error rate (4xx, 5xx responses)
- Response time (p50, p95, p99)
- CPU and memory utilization
- Database connection pool status
- Message queue lag

## Security Considerations

### Authentication & Authorization

Implement OAuth 2.0 / OpenID Connect using:

\`\`\`javascript
const jwt = require('jsonwebtoken');
const jwksRsa = require('jwks-rsa');

const verifyToken = async (token) => {
  const client = jwksRsa({
    jwksUri: 'https://auth.example.com/.well-known/jwks.json',
    cache: true,
    rateLimit: true
  });

  const decoded = jwt.verify(token, getKey, {
    algorithms: ['RS256'],
    issuer: 'https://auth.example.com',
    audience: 'api.example.com'
  });

  return decoded;
};
\`\`\`

### Network Security

- Implement mTLS between services
- Use network policies to restrict traffic
- Regular security scanning with Trivy
- Secrets management with HashiCorp Vault

## Troubleshooting

### Common Issues and Solutions

**Issue**: Service discovery not working
**Solution**: Check CoreDNS logs and ensure services have correct labels

**Issue**: High memory usage in containers
**Solution**: Review memory limits and implement proper garbage collection

**Issue**: Database connection pool exhausted
**Solution**: Increase pool size or implement connection pooling proxy

### Debug Commands

\`\`\`bash
# Check pod logs
kubectl logs -f deployment/user-service

# Describe pod for events
kubectl describe pod user-service-xxxx

# Execute into container
kubectl exec -it user-service-xxxx -- /bin/sh

# Port forward for local debugging
kubectl port-forward service/user-service 3000:3000

# Check service endpoints
kubectl get endpoints user-service
\`\`\`

---

*This documentation is maintained by the Platform Engineering Team. For questions or contributions, please submit a pull request or contact devops@example.com*`
    }

    return contents[type] || contents.blog_post
  }

  const generateMockDeliverable = () => {
    const types: Deliverable['type'][] = ['blog_post', 'code', 'design', 'data_analysis', 'document']
    const type = types[Math.floor(Math.random() * types.length)]

    const templates = {
      blog_post: {
        title: `SEO-Optimized Article: ${['Tech Trends', 'Marketing Strategy', 'Business Growth'][Math.floor(Math.random() * 3)]}`,
        agent: 'real_content_creator',
        wordCount: Math.floor(Math.random() * 2000) + 1000
      },
      code: {
        title: `${['React Component', 'Python Script', 'API Endpoint'][Math.floor(Math.random() * 3)]}`,
        agent: 'code_generator_agent',
        linesOfCode: Math.floor(Math.random() * 1000) + 200
      },
      design: {
        title: `${['UI Design', 'Logo Concept', 'Social Media Graphics'][Math.floor(Math.random() * 3)]}`,
        agent: 'ui_designer_agent',
        fileSize: `${Math.floor(Math.random() * 20) + 5} MB`
      },
      data_analysis: {
        title: `${['Market Analysis', 'Performance Report', 'Customer Insights'][Math.floor(Math.random() * 3)]}`,
        agent: 'data_analyst_agent',
        fileSize: `${Math.floor(Math.random() * 5) + 1} MB`
      },
      document: {
        title: `${['Technical Documentation', 'Business Proposal', 'White Paper'][Math.floor(Math.random() * 3)]}`,
        agent: 'technical_writer_agent',
        wordCount: Math.floor(Math.random() * 3000) + 2000
      }
    }

    const template = templates[type]
    const newDeliverable: Deliverable = {
      id: `del_${Date.now()}`,
      type,
      title: template.title,
      description: `Professionally crafted ${type.replace('_', ' ')} created with AI assistance`,
      agent: template.agent,
      createdAt: new Date().toISOString(),
      status: 'generating',
      progress: 0,
      value: Math.floor(Math.random() * 500) + 100,
      ...template
    }

    addDeliverable(newDeliverable)

    // Simulate progress updates
    let progress = 0
    const progressInterval = setInterval(() => {
      progress += Math.random() * 30
      if (progress >= 100) {
        progress = 100
        completeDeliverable(newDeliverable.id, {
          preview: 'Generated content preview...',
          downloadUrl: `/downloads/${newDeliverable.id}`
        })
        clearInterval(progressInterval)
      } else {
        updateDeliverableProgress(newDeliverable.id, progress)
      }
    }, 1000)
  }

  const addDeliverable = (deliverable: Deliverable) => {
    setDeliverables(prev => [deliverable, ...prev].slice(0, 50))
    setGeneratingCount(prev => prev + 1)
  }

  const updateDeliverableProgress = (id: string, progress: number) => {
    setDeliverables(prev => prev.map(d =>
      d.id === id ? { ...d, progress, status: progress >= 100 ? 'processing' : 'generating' } : d
    ))
  }

  const completeDeliverable = (id: string, details: any) => {
    setDeliverables(prev => prev.map(d =>
      d.id === id ? { ...d, ...details, status: 'ready', progress: 100 } : d
    ))
    setGeneratingCount(prev => Math.max(0, prev - 1))
    setTotalValue(prev => prev + (deliverables.find(d => d.id === id)?.value || 0))
  }

  const getIcon = (type: Deliverable['type']) => {
    switch(type) {
      case 'blog_post': return <FileText className="h-5 w-5" />
      case 'code': return <Code className="h-5 w-5" />
      case 'design': return <Image className="h-5 w-5" />
      case 'video': return <Video className="h-5 w-5" />
      case 'audio': return <Music className="h-5 w-5" />
      case 'data_analysis': return <TrendingUp className="h-5 w-5" />
      default: return <File className="h-5 w-5" />
    }
  }

  const getTypeColor = (type: Deliverable['type']) => {
    switch(type) {
      case 'blog_post': return 'text-blue-500'
      case 'code': return 'text-green-500'
      case 'design': return 'text-purple-500'
      case 'video': return 'text-red-500'
      case 'audio': return 'text-yellow-500'
      case 'data_analysis': return 'text-cyan-500'
      default: return 'text-gray-500'
    }
  }

  const getStatusColor = (status: Deliverable['status']) => {
    switch(status) {
      case 'generating': return 'bg-yellow-900 text-yellow-300'
      case 'processing': return 'bg-blue-900 text-blue-300'
      case 'ready': return 'bg-green-900 text-green-300'
      case 'delivered': return 'bg-purple-900 text-purple-300'
      default: return 'bg-gray-900 text-gray-300'
    }
  }

  return (
    <div className="bg-gray-900 text-white p-6 rounded-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold mb-2">Live Deliverable Generation</h2>
          <p className="text-gray-400">Watch as AI agents create real content in real-time</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm text-gray-400">Total Value Generated</p>
            <p className="text-2xl font-bold text-green-500">${totalValue.toLocaleString()}</p>
          </div>
          <div className={`px-3 py-1 rounded ${wsConnected ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
            {wsConnected ? '● Live' : '● Offline'}
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 p-3 rounded">
          <div className="flex items-center justify-between">
            <Zap className="h-5 w-5 text-yellow-500" />
            <span className="text-xl font-bold">{generatingCount}</span>
          </div>
          <p className="text-sm text-gray-400 mt-1">Generating Now</p>
        </div>
        <div className="bg-gray-800 p-3 rounded">
          <div className="flex items-center justify-between">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-xl font-bold">{deliverables.filter(d => d.status === 'ready').length}</span>
          </div>
          <p className="text-sm text-gray-400 mt-1">Ready</p>
        </div>
        <div className="bg-gray-800 p-3 rounded">
          <div className="flex items-center justify-between">
            <Clock className="h-5 w-5 text-blue-500" />
            <span className="text-xl font-bold">{deliverables.filter(d => d.status === 'processing').length}</span>
          </div>
          <p className="text-sm text-gray-400 mt-1">Processing</p>
        </div>
        <div className="bg-gray-800 p-3 rounded">
          <div className="flex items-center justify-between">
            <FileText className="h-5 w-5 text-purple-500" />
            <span className="text-xl font-bold">{deliverables.length}</span>
          </div>
          <p className="text-sm text-gray-400 mt-1">Total Created</p>
        </div>
      </div>

      {/* Deliverables Grid */}
      <div className="grid grid-cols-2 gap-4 max-h-[600px] overflow-y-auto">
        {deliverables.map((deliverable) => (
          <div
            key={deliverable.id}
            className="bg-gray-800 rounded-lg p-4 hover:bg-gray-750 transition cursor-pointer"
            onClick={() => setSelectedDeliverable(deliverable)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className={`${getTypeColor(deliverable.type)}`}>
                  {getIcon(deliverable.type)}
                </div>
                <div>
                  <h4 className="font-semibold">{deliverable.title}</h4>
                  <p className="text-xs text-gray-400">by {deliverable.agent}</p>
                </div>
              </div>
              <span className={`text-xs px-2 py-1 rounded ${getStatusColor(deliverable.status)}`}>
                {deliverable.status}
              </span>
            </div>

            <p className="text-sm text-gray-400 mb-3">{deliverable.description}</p>

            {/* Progress Bar */}
            {deliverable.status === 'generating' && (
              <div className="mb-3">
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>Generating...</span>
                  <span>{Math.round(deliverable.progress)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${deliverable.progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center space-x-3">
                {deliverable.wordCount && <span>{deliverable.wordCount} words</span>}
                {deliverable.linesOfCode && <span>{deliverable.linesOfCode} lines</span>}
                {deliverable.fileSize && <span>{deliverable.fileSize}</span>}
                {deliverable.duration && <span>{deliverable.duration}</span>}
              </div>
              <span className="text-green-400 font-semibold">${deliverable.value}</span>
            </div>

            {/* Preview */}
            {deliverable.preview && deliverable.status === 'ready' && (
              <div className="mt-3 p-2 bg-gray-900 rounded text-xs text-gray-400 line-clamp-2">
                {deliverable.preview}
              </div>
            )}

            {/* Actions */}
            {deliverable.status === 'ready' && (
              <div className="mt-3 flex items-center space-x-2">
                <button className="flex items-center space-x-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs">
                  <Eye className="h-3 w-3" />
                  <span>Preview</span>
                </button>
                <button className="flex items-center space-x-1 px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-xs">
                  <Download className="h-3 w-3" />
                  <span>Download</span>
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Selected Deliverable Modal */}
      {selectedDeliverable && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">{selectedDeliverable.title}</h3>
              <button
                onClick={() => setSelectedDeliverable(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className={`${getTypeColor(selectedDeliverable.type)}`}>
                  {getIcon(selectedDeliverable.type)}
                </div>
                <div>
                  <p className="text-sm text-gray-400">Type: {selectedDeliverable.type.replace('_', ' ')}</p>
                  <p className="text-sm text-gray-400">Agent: {selectedDeliverable.agent}</p>
                </div>
                <span className={`text-xs px-3 py-1 rounded ${getStatusColor(selectedDeliverable.status)}`}>
                  {selectedDeliverable.status}
                </span>
              </div>

              <p className="text-gray-300">{selectedDeliverable.description}</p>

              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-900 rounded">
                <div>
                  <p className="text-xs text-gray-500">Created</p>
                  <p className="text-sm">{new Date(selectedDeliverable.createdAt).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Value</p>
                  <p className="text-sm text-green-400">${selectedDeliverable.value}</p>
                </div>
                {selectedDeliverable.wordCount && (
                  <div>
                    <p className="text-xs text-gray-500">Word Count</p>
                    <p className="text-sm">{selectedDeliverable.wordCount}</p>
                  </div>
                )}
                {selectedDeliverable.linesOfCode && (
                  <div>
                    <p className="text-xs text-gray-500">Lines of Code</p>
                    <p className="text-sm">{selectedDeliverable.linesOfCode}</p>
                  </div>
                )}
                {selectedDeliverable.fileSize && (
                  <div>
                    <p className="text-xs text-gray-500">File Size</p>
                    <p className="text-sm">{selectedDeliverable.fileSize}</p>
                  </div>
                )}
              </div>

              {selectedDeliverable.preview && (
                <div>
                  <h4 className="text-sm font-semibold mb-2">Preview</h4>
                  <div className="p-4 bg-gray-900 rounded text-sm text-gray-300 font-mono whitespace-pre-wrap">
                    {selectedDeliverable.preview}
                  </div>
                </div>
              )}

              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setShowFullPreview(true)}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
                >
                  <Eye className="h-4 w-4" />
                  <span>Full Preview</span>
                </button>
                <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded">
                  <Download className="h-4 w-4" />
                  <span>Download</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Full Preview Modal */}
      {showFullPreview && selectedDeliverable && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-lg w-full max-w-6xl h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <div className="flex items-center space-x-3">
                <div className={`${getTypeColor(selectedDeliverable.type)}`}>
                  {getIcon(selectedDeliverable.type)}
                </div>
                <div>
                  <h3 className="text-lg font-bold">{selectedDeliverable.title}</h3>
                  <p className="text-sm text-gray-400">
                    Full Preview • {selectedDeliverable.agent} • {new Date(selectedDeliverable.createdAt).toLocaleString()}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowFullPreview(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ✕
              </button>
            </div>

            {/* Full Content Viewer */}
            <div className="flex-1 overflow-y-auto p-6 bg-gray-950">
              <div className="max-w-4xl mx-auto">
                <pre className="whitespace-pre-wrap font-mono text-sm text-gray-300 leading-relaxed">
                  {getFullContent(selectedDeliverable.type)}
                </pre>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-between p-4 border-t border-gray-700">
              <div className="flex items-center space-x-4 text-sm text-gray-400">
                {selectedDeliverable.wordCount && (
                  <span>{selectedDeliverable.wordCount.toLocaleString()} words</span>
                )}
                {selectedDeliverable.linesOfCode && (
                  <span>{selectedDeliverable.linesOfCode.toLocaleString()} lines of code</span>
                )}
                {selectedDeliverable.fileSize && (
                  <span>{selectedDeliverable.fileSize}</span>
                )}
                <span className="text-green-400 font-semibold">
                  Value: ${selectedDeliverable.value}
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => {
                    // Copy to clipboard
                    navigator.clipboard.writeText(getFullContent(selectedDeliverable.type))
                    alert('Content copied to clipboard!')
                  }}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                >
                  Copy to Clipboard
                </button>
                <button
                  onClick={() => setShowFullPreview(false)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                >
                  Close Preview
                </button>
                <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm">
                  <Download className="h-4 w-4" />
                  <span>Download Full Content</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default LiveDeliverableViewer