import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider, QueryCache, MutationCache } from '@tanstack/react-query'
import App from './App'
import { handleQueryClientError } from './lib/queryClientErrorHandler'
import './index.css'

// ADR-0005 §3.1 γ Layer 1 — QueryCache + MutationCache onError defaults.
// React Query v5 removed defaultOptions.queries.onError; the v5-canonical
// pattern is QueryCache({onError}) + MutationCache({onError}) at QueryClient
// construction. Handler is shape-agnostic per §3.3 and defers redirect to
// interceptor for auth endpoints / to (future T-ENVELOPE-3 modal) for others.
const queryClient = new QueryClient({
  queryCache: new QueryCache({ onError: handleQueryClientError }),
  mutationCache: new MutationCache({ onError: handleQueryClientError }),
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
