import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import IncomeBuilder from '../IncomeBuilder'
import { createMockOpportunity, waitForNextTick } from '../../test/setup'

// Mock fetch globally
global.fetch = vi.fn()

// Mock API responses
const mockOpportunities = [
  {
    id: '1',
    title: 'Content Creation',
    stream_type: 'content',
    description: 'Create engaging content for social media',
    time_to_income: '2-4 weeks',
    potential_monthly: '$2,000-$5,000',
    difficulty: 'Medium',
    initial_investment: 100,
    success_rate: 75,
    market_demand: 85,
    required_skills: ['Writing', 'Social Media', 'Marketing'],
    action_steps: [
      'Set up social media accounts',
      'Create content calendar',
      'Start posting consistently'
    ],
    resources: [
      { name: 'Social Media Guide', url: 'https://example.com/guide' }
    ]
  },
  {
    id: '2',
    title: 'AI Consulting',
    stream_type: 'ai_services',
    description: 'Provide AI implementation consulting',
    time_to_income: '1-2 weeks',
    potential_monthly: '$5,000-$10,000',
    difficulty: 'High',
    initial_investment: 0,
    success_rate: 90,
    market_demand: 95,
    required_skills: ['AI', 'Python', 'Consulting'],
    action_steps: [
      'Create service packages',
      'Build portfolio',
      'Find first clients'
    ],
    resources: []
  }
]

const mockRevenueData = {
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
}

describe('IncomeBuilder Component', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    vi.clearAllMocks()

    // Mock successful API responses
    global.fetch = vi.fn().mockImplementation((url) => {
      if (url.includes('/api/v1/intelligence/opportunities/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ opportunities: mockOpportunities })
        })
      }

      if (url.includes('/api/v1/intelligence/revenue-data/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockRevenueData)
        })
      }

      if (url.includes('/api/v1/intelligence/action-plans/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ action_plans: [] })
        })
      }

      if (url.includes('/api/v1/intelligence/automation-workflows/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ workflows: [] })
        })
      }

      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      })
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Component Rendering', () => {
    it('renders the main IncomeBuilder interface', async () => {
      render(<IncomeBuilder />)

      expect(screen.getByText('Income Builder')).toBeInTheDocument()
      expect(screen.getByText('AI-Powered Revenue Opportunities')).toBeInTheDocument()

      // Check for main tabs
      expect(screen.getByText('Opportunities')).toBeInTheDocument()
      expect(screen.getByText('Revenue Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Action Plans')).toBeInTheDocument()
      expect(screen.getByText('Automation')).toBeInTheDocument()
    })

    it('shows loading state initially', () => {
      render(<IncomeBuilder />)

      // Should show some loading indication
      expect(screen.getByText('Discovering opportunities...')).toBeInTheDocument()
    })

    it('displays opportunities after loading', async () => {
      render(<IncomeBuilder />)

      await waitFor(() => {
        expect(screen.getByText('Content Creation')).toBeInTheDocument()
        expect(screen.getByText('AI Consulting')).toBeInTheDocument()
      })
    })
  })

  describe('Opportunities Tab', () => {
    it('displays opportunity cards with correct information', async () => {
      render(<IncomeBuilder />)

      await waitFor(() => {
        expect(screen.getByText('Content Creation')).toBeInTheDocument()
      })

      // Check for opportunity details
      expect(screen.getByText('Create engaging content for social media')).toBeInTheDocument()
      expect(screen.getByText('$2,000-$5,000')).toBeInTheDocument()
      expect(screen.getByText('Medium')).toBeInTheDocument()
      expect(screen.getByText('75%')).toBeInTheDocument()
    })

    it('filters opportunities by difficulty', async () => {
      render(<IncomeBuilder />)

      await waitFor(() => {
        expect(screen.getByText('Content Creation')).toBeInTheDocument()
      })

      // Click on High difficulty filter (assuming it exists)
      const highFilter = screen.getByText('High')
      await user.click(highFilter)

      // Should only show high difficulty opportunities
      expect(screen.getByText('AI Consulting')).toBeInTheDocument()
      expect(screen.queryByText('Content Creation')).not.toBeInTheDocument()
    })

    it('opens opportunity details when clicked', async () => {
      render(<IncomeBuilder />)

      await waitFor(() => {
        expect(screen.getByText('Content Creation')).toBeInTheDocument()
      })

      // Click on an opportunity
      await user.click(screen.getByText('Content Creation'))

      // Should show detailed view
      expect(screen.getByText('Action Steps')).toBeInTheDocument()
      expect(screen.getByText('Set up social media accounts')).toBeInTheDocument()
    })
  })

  describe('Revenue Dashboard Tab', () => {
    it('displays current revenue metrics', async () => {
      render(<IncomeBuilder />)

      // Switch to revenue dashboard tab
      await user.click(screen.getByText('Revenue Dashboard'))

      await waitFor(() => {
        expect(screen.getByText('$25,000')).toBeInTheDocument() // Total revenue
        expect(screen.getByText('$8,500')).toBeInTheDocument()  // Monthly revenue
      })
    })

    it('shows revenue breakdown by category', async () => {
      render(<IncomeBuilder />)

      await user.click(screen.getByText('Revenue Dashboard'))

      await waitFor(() => {
        expect(screen.getByText('$15,000')).toBeInTheDocument() // AI services
        expect(screen.getByText('$5,000')).toBeInTheDocument()  // Content
      })
    })

    it('displays revenue projections', async () => {
      render(<IncomeBuilder />)

      await user.click(screen.getByText('Revenue Dashboard'))

      await waitFor(() => {
        expect(screen.getByText('$144,000')).toBeInTheDocument() // Yearly projection
      })
    })
  })

  describe('Action Plans Tab', () => {
    it('renders action plans section', async () => {
      render(<IncomeBuilder />)

      await user.click(screen.getByText('Action Plans'))

      expect(screen.getByText('Your Action Plans')).toBeInTheDocument()
      expect(screen.getByText('Generate Action Plan')).toBeInTheDocument()
    })

    it('can generate new action plan', async () => {
      // Mock the action plan generation API
      global.fetch = vi.fn().mockImplementation((url) => {
        if (url.includes('/api/v1/intelligence/income-builder/action-plan/')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              action_plan: {
                id: '1',
                title: 'Content Creation Plan',
                steps: ['Step 1', 'Step 2'],
                timeline: '30 days'
              }
            })
          })
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
      })

      render(<IncomeBuilder />)

      await user.click(screen.getByText('Action Plans'))
      await user.click(screen.getByText('Generate Action Plan'))

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/intelligence/income-builder/action-plan/'),
          expect.any(Object)
        )
      })
    })
  })

  describe('WebSocket Integration', () => {
    it('establishes WebSocket connection', async () => {
      render(<IncomeBuilder />)

      await waitForNextTick()

      // Check that WebSocket was created
      // Note: We mocked WebSocket in setup.ts
      expect(global.WebSocket).toHaveBeenCalledWith(
        expect.stringContaining('/ws/income-builder/')
      )
    })

    it('displays connection status', async () => {
      render(<IncomeBuilder />)

      await waitFor(() => {
        // Should show connection indicator
        expect(screen.getByTestId('ws-status')).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('handles API errors gracefully', async () => {
      // Mock API failure
      global.fetch = vi.fn().mockRejectedValue(new Error('API Error'))

      render(<IncomeBuilder />)

      await waitFor(() => {
        expect(screen.getByText('Error loading opportunities')).toBeInTheDocument()
      })
    })

    it('shows retry button on error', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('API Error'))

      render(<IncomeBuilder />)

      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument()
      })
    })

    it('retries API call when retry button is clicked', async () => {
      global.fetch = vi.fn()
        .mockRejectedValueOnce(new Error('API Error'))
        .mockResolvedValue({
          ok: true,
          json: () => Promise.resolve({ opportunities: mockOpportunities })
        })

      render(<IncomeBuilder />)

      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Retry'))

      await waitFor(() => {
        expect(screen.getByText('Content Creation')).toBeInTheDocument()
      })
    })
  })

  describe('User Interactions', () => {
    it('allows switching between tabs', async () => {
      render(<IncomeBuilder />)

      // Switch to different tabs
      await user.click(screen.getByText('Revenue Dashboard'))
      expect(screen.getByText('Current Revenue')).toBeInTheDocument()

      await user.click(screen.getByText('Action Plans'))
      expect(screen.getByText('Your Action Plans')).toBeInTheDocument()

      await user.click(screen.getByText('Automation'))
      expect(screen.getByText('Income Automation')).toBeInTheDocument()
    })

    it('updates UI state correctly', async () => {
      render(<IncomeBuilder />)

      await waitFor(() => {
        expect(screen.getByText('Content Creation')).toBeInTheDocument()
      })

      // Select an opportunity
      await user.click(screen.getByText('Content Creation'))

      // Should update selected opportunity state
      expect(screen.getByText('Required Skills')).toBeInTheDocument()
      expect(screen.getByText('Writing')).toBeInTheDocument()
    })
  })

  describe('File Export Functionality', () => {
    it('shows export options for action plans', async () => {
      render(<IncomeBuilder />)

      await user.click(screen.getByText('Action Plans'))

      // Assuming there's an export button
      const exportButton = screen.getByText('Export')
      expect(exportButton).toBeInTheDocument()
    })

    it('handles file downloads', async () => {
      // Mock URL.createObjectURL
      global.URL.createObjectURL = vi.fn(() => 'blob:test-url')
      global.URL.revokeObjectURL = vi.fn()

      render(<IncomeBuilder />)

      await user.click(screen.getByText('Action Plans'))

      // Click export (assuming it exists)
      const exportButton = screen.getByText('Export')
      await user.click(exportButton)

      // Should have created blob URL
      expect(global.URL.createObjectURL).toHaveBeenCalled()
    })
  })

  describe('Performance', () => {
    it('memoizes expensive calculations', async () => {
      const { rerender } = render(<IncomeBuilder />)

      await waitFor(() => {
        expect(screen.getByText('Content Creation')).toBeInTheDocument()
      })

      // Re-render with same props
      rerender(<IncomeBuilder />)

      // Should not make duplicate API calls
      expect(global.fetch).toHaveBeenCalledTimes(4) // Initial calls only
    })

    it('handles large datasets efficiently', async () => {
      // Mock large dataset
      const largeOpportunities = Array.from({ length: 100 }, (_, i) => ({
        ...mockOpportunities[0],
        id: `${i}`,
        title: `Opportunity ${i}`
      }))

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ opportunities: largeOpportunities })
      })

      const startTime = performance.now()
      render(<IncomeBuilder />)

      await waitFor(() => {
        expect(screen.getByText('Opportunity 0')).toBeInTheDocument()
      })

      const endTime = performance.now()

      // Should render within reasonable time (less than 1 second)
      expect(endTime - startTime).toBeLessThan(1000)
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA labels', async () => {
      render(<IncomeBuilder />)

      expect(screen.getByRole('tablist')).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: 'Opportunities' })).toBeInTheDocument()
    })

    it('supports keyboard navigation', async () => {
      render(<IncomeBuilder />)

      // Tab navigation should work
      await user.tab()
      expect(document.activeElement).toHaveAttribute('role', 'tab')
    })

    it('provides screen reader announcements', async () => {
      render(<IncomeBuilder />)

      await waitFor(() => {
        expect(screen.getByText('Content Creation')).toBeInTheDocument()
      })

      // Should have appropriate aria-live regions for updates
      expect(screen.getByRole('status')).toBeInTheDocument()
    })
  })
})