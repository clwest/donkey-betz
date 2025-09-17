import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers)

// Mock global objects commonly used in the app
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

global.matchMedia = vi.fn().mockImplementation(query => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(), // deprecated
  removeListener: vi.fn(), // deprecated
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}))

// Mock WebSocket for real-time features
class MockWebSocket {
  constructor(url: string) {
    this.url = url
    this.readyState = WebSocket.CONNECTING
    setTimeout(() => {
      this.readyState = WebSocket.OPEN
      this.onopen?.({ type: 'open' } as Event)
    }, 0)
  }

  url: string
  readyState: number
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  send = vi.fn()
  close = vi.fn()

  // Static constants
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3
}

global.WebSocket = MockWebSocket as any

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.sessionStorage = sessionStorageMock

// Mock scrollTo
global.scrollTo = vi.fn()

// Clean up after each test case
afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

// Global test utilities
export const createMockUser = () => ({
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  profile: {
    first_name: 'Test',
    last_name: 'User',
  },
})

export const createMockAgent = () => ({
  id: '1',
  name: 'Test Agent',
  category: 'content',
  description: 'A test agent',
  status: 'active',
  capabilities: ['writing', 'analysis'],
})

export const createMockOpportunity = () => ({
  id: '1',
  title: 'Test Opportunity',
  description: 'A test income opportunity',
  potential_income: 1000,
  difficulty: 'medium',
  time_investment: '5-10 hours/week',
  category: 'content',
})

export const waitForNextTick = () => new Promise(resolve => setTimeout(resolve, 0))