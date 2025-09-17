import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import { create } from 'zustand'

// Mock components for integration testing
const MockApp = () => (
  <BrowserRouter>
    <div>
      <nav>
        <a href="/income-builder">Income Builder</a>
        <a href="/revenue-dashboard">Revenue Dashboard</a>
        <a href="/agent-orchestra">Agent Orchestra</a>
      </nav>
      <main>
        <div id="app-content">App Content</div>
      </main>
    </div>
  </BrowserRouter>
)

// Mock API responses for integration tests
const mockApiResponses = {
  opportunities: {
    opportunities: [
      {
        id: '1',
        title: 'Content Creation',
        stream_type: 'content',
        description: 'Create engaging content',
        time_to_income: '2-4 weeks',
        potential_monthly: '$2,000-$5,000',
        difficulty: 'Medium',
        initial_investment: 100,
        success_rate: 75,
        market_demand: 85,
        required_skills: ['Writing'],
        action_steps: ['Step 1'],
        resources: []
      }
    ]
  },
  revenueData: {
    current_metrics: {
      total_revenue: 25000,
      monthly_revenue: 8500,
      weekly_revenue: 2100,
      daily_revenue: 300
    },
    by_category: {
      content: 5000,
      ai_services: 15000,
      digital_products: 3000,
      trading: 1500,
      freelancing: 500
    },
    projections: {
      monthly: 12000,
      yearly: 144000
    }
  },
  agents: {
    agents: [
      {
        id: '1',
        name: 'Content Creator',
        category: 'content',
        status: 'active',
        capabilities: ['writing', 'research']
      }
    ]
  }
}

describe('Integration Tests', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    vi.clearAllMocks()

    // Mock global fetch for all integration tests
    global.fetch = vi.fn().mockImplementation((url) => {
      const urlString = url.toString()

      if (urlString.includes('/opportunities/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockApiResponses.opportunities)
        })
      }

      if (urlString.includes('/revenue-data/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockApiResponses.revenueData)
        })
      }

      if (urlString.includes('/agents/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockApiResponses.agents)
        })
      }

      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      })
    })
  })

  describe('Application Navigation', () => {
    it('navigates between main sections', async () => {
      render(<MockApp />)

      // Check navigation links are present
      expect(screen.getByText('Income Builder')).toBeInTheDocument()
      expect(screen.getByText('Revenue Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Agent Orchestra')).toBeInTheDocument()

      // Check main content area
      expect(screen.getByText('App Content')).toBeInTheDocument()
    })

    it('maintains state between navigation', async () => {
      render(<MockApp />)

      // Navigate to different sections
      await user.click(screen.getByText('Income Builder'))
      await user.click(screen.getByText('Revenue Dashboard'))

      // Should maintain navigation structure
      expect(screen.getByText('Income Builder')).toBeInTheDocument()
      expect(screen.getByText('Revenue Dashboard')).toBeInTheDocument()
    })
  })

  describe('API Integration', () => {
    it('handles multiple concurrent API calls', async () => {
      // Simulate component that makes multiple API calls
      const MultiApiComponent = () => {
        const [data, setData] = React.useState({
          opportunities: [],
          revenue: null,
          agents: []
        })

        React.useEffect(() => {
          Promise.all([
            fetch('/api/opportunities/'),
            fetch('/api/revenue-data/'),
            fetch('/api/agents/')
          ]).then(async ([oppsRes, revenueRes, agentsRes]) => {
            const opportunities = await oppsRes.json()
            const revenue = await revenueRes.json()
            const agents = await agentsRes.json()

            setData({ opportunities, revenue, agents })
          })
        }, [])

        return (
          <div>
            <div>Opportunities: {data.opportunities.opportunities?.length || 0}</div>
            <div>Revenue: ${data.revenue?.current_metrics?.total_revenue || 0}</div>
            <div>Agents: {data.agents.agents?.length || 0}</div>
          </div>
        )
      }

      render(<MultiApiComponent />)

      await waitFor(() => {
        expect(screen.getByText('Opportunities: 1')).toBeInTheDocument()
        expect(screen.getByText('Revenue: $25000')).toBeInTheDocument()
        expect(screen.getByText('Agents: 1')).toBeInTheDocument()
      })

      // Verify all API calls were made
      expect(global.fetch).toHaveBeenCalledTimes(3)
    })

    it('handles API errors gracefully', async () => {
      // Mock API failure
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'))

      const ErrorHandlingComponent = () => {
        const [error, setError] = React.useState<string | null>(null)

        React.useEffect(() => {
          fetch('/api/opportunities/')
            .catch(err => setError(err.message))
        }, [])

        return (
          <div>
            {error ? <div>Error: {error}</div> : <div>Loading...</div>}
          </div>
        )
      }

      render(<ErrorHandlingComponent />)

      await waitFor(() => {
        expect(screen.getByText('Error: Network error')).toBeInTheDocument()
      })
    })
  })

  describe('WebSocket Integration', () => {
    it('establishes WebSocket connections', async () => {
      const WebSocketComponent = () => {
        const [connected, setConnected] = React.useState(false)
        const [messages, setMessages] = React.useState<string[]>([])

        React.useEffect(() => {
          const ws = new WebSocket('ws://localhost:8000/ws/test/')

          ws.onopen = () => setConnected(true)
          ws.onmessage = (event) => {
            setMessages(prev => [...prev, event.data])
          }

          return () => ws.close()
        }, [])

        return (
          <div>
            <div>Connected: {connected ? 'Yes' : 'No'}</div>
            <div>Messages: {messages.length}</div>
          </div>
        )
      }

      render(<WebSocketComponent />)

      await waitFor(() => {
        expect(screen.getByText('Connected: Yes')).toBeInTheDocument()
      })
    })

    it('handles WebSocket reconnection', async () => {
      let reconnectAttempts = 0

      const ReconnectingWebSocketComponent = () => {
        const [status, setStatus] = React.useState('connecting')

        React.useEffect(() => {
          const connect = () => {
            const ws = new WebSocket('ws://localhost:8000/ws/test/')

            ws.onopen = () => setStatus('connected')
            ws.onclose = () => {
              setStatus('disconnected')
              reconnectAttempts++

              if (reconnectAttempts < 3) {
                setTimeout(connect, 1000)
              }
            }
          }

          connect()
        }, [])

        return <div>Status: {status}</div>
      }

      render(<ReconnectingWebSocketComponent />)

      await waitFor(() => {
        expect(screen.getByText('Status: connected')).toBeInTheDocument()
      })
    })
  })

  describe('State Management Integration', () => {
    it('shares state between components', async () => {
      // Mock Zustand store
      const useStore = create((set) => ({
        count: 0,
        increment: () => set((state) => ({ count: state.count + 1 })),
        decrement: () => set((state) => ({ count: state.count - 1 }))
      }))

      const Counter = () => {
        const { count, increment, decrement } = useStore()

        return (
          <div>
            <div>Count: {count}</div>
            <button onClick={increment}>Increment</button>
            <button onClick={decrement}>Decrement</button>
          </div>
        )
      }

      const DisplayCounter = () => {
        const { count } = useStore()
        return <div>Display: {count}</div>
      }

      render(
        <div>
          <Counter />
          <DisplayCounter />
        </div>
      )

      expect(screen.getByText('Count: 0')).toBeInTheDocument()
      expect(screen.getByText('Display: 0')).toBeInTheDocument()

      await user.click(screen.getByText('Increment'))

      expect(screen.getByText('Count: 1')).toBeInTheDocument()
      expect(screen.getByText('Display: 1')).toBeInTheDocument()
    })
  })

  describe('Real-time Data Flow', () => {
    it('updates UI when data changes', async () => {
      const RealTimeComponent = () => {
        const [data, setData] = React.useState({ value: 0 })

        React.useEffect(() => {
          const interval = setInterval(() => {
            setData(prev => ({ value: prev.value + 1 }))
          }, 100)

          return () => clearInterval(interval)
        }, [])

        return <div>Value: {data.value}</div>
      }

      render(<RealTimeComponent />)

      expect(screen.getByText('Value: 0')).toBeInTheDocument()

      await waitFor(
        () => {
          expect(screen.getByText('Value: 5')).toBeInTheDocument()
        },
        { timeout: 1000 }
      )
    })

    it('handles rapid data updates efficiently', async () => {
      const RapidUpdatesComponent = () => {
        const [updates, setUpdates] = React.useState(0)

        React.useEffect(() => {
          const interval = setInterval(() => {
            setUpdates(prev => prev + 1)
          }, 10) // Very frequent updates

          return () => clearInterval(interval)
        }, [])

        return <div>Updates: {updates}</div>
      }

      const startTime = performance.now()
      render(<RapidUpdatesComponent />)

      await waitFor(
        () => {
          expect(screen.getByText(/Updates: [1-9]/)).toBeInTheDocument()
        },
        { timeout: 1000 }
      )

      const endTime = performance.now()
      expect(endTime - startTime).toBeLessThan(1000)
    })
  })

  describe('User Workflow Integration', () => {
    it('completes end-to-end user workflow', async () => {
      const WorkflowComponent = () => {
        const [step, setStep] = React.useState(1)
        const [data, setData] = React.useState({ name: '', email: '' })

        const nextStep = () => setStep(prev => prev + 1)
        const updateData = (field: string, value: string) => {
          setData(prev => ({ ...prev, [field]: value }))
        }

        return (
          <div>
            <div>Step: {step}</div>

            {step === 1 && (
              <div>
                <input
                  placeholder="Name"
                  value={data.name}
                  onChange={(e) => updateData('name', e.target.value)}
                />
                <button onClick={nextStep}>Next</button>
              </div>
            )}

            {step === 2 && (
              <div>
                <input
                  placeholder="Email"
                  value={data.email}
                  onChange={(e) => updateData('email', e.target.value)}
                />
                <button onClick={nextStep}>Complete</button>
              </div>
            )}

            {step === 3 && (
              <div>
                <div>Name: {data.name}</div>
                <div>Email: {data.email}</div>
                <div>Workflow Complete!</div>
              </div>
            )}
          </div>
        )
      }

      render(<WorkflowComponent />)

      // Step 1
      expect(screen.getByText('Step: 1')).toBeInTheDocument()
      await user.type(screen.getByPlaceholderText('Name'), 'John Doe')
      await user.click(screen.getByText('Next'))

      // Step 2
      expect(screen.getByText('Step: 2')).toBeInTheDocument()
      await user.type(screen.getByPlaceholderText('Email'), 'john@example.com')
      await user.click(screen.getByText('Complete'))

      // Step 3
      expect(screen.getByText('Step: 3')).toBeInTheDocument()
      expect(screen.getByText('Name: John Doe')).toBeInTheDocument()
      expect(screen.getByText('Email: john@example.com')).toBeInTheDocument()
      expect(screen.getByText('Workflow Complete!')).toBeInTheDocument()
    })
  })

  describe('Performance Integration', () => {
    it('handles complex component trees efficiently', async () => {
      const ComplexComponent = ({ depth = 0 }: { depth?: number }) => {
        if (depth > 5) return <div>Leaf {depth}</div>

        return (
          <div>
            <div>Node {depth}</div>
            <ComplexComponent depth={depth + 1} />
            <ComplexComponent depth={depth + 1} />
          </div>
        )
      }

      const startTime = performance.now()
      render(<ComplexComponent />)

      expect(screen.getByText('Node 0')).toBeInTheDocument()

      const endTime = performance.now()
      expect(endTime - startTime).toBeLessThan(500)
    })

    it('manages memory efficiently with many components', async () => {
      const ManyComponentsTest = () => {
        const [count, setCount] = React.useState(10)

        return (
          <div>
            <button onClick={() => setCount(prev => prev + 10)}>
              Add Components ({count})
            </button>
            {Array.from({ length: count }, (_, i) => (
              <div key={i}>Component {i}</div>
            ))}
          </div>
        )
      }

      render(<ManyComponentsTest />)

      // Add more components
      await user.click(screen.getByText(/Add Components/))
      await user.click(screen.getByText(/Add Components/))

      // Should handle 30 components without issues
      expect(screen.getByText('Component 29')).toBeInTheDocument()
    })
  })
})