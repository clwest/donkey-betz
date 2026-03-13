// Public Review Portal — accessed via magic link /r/:token
// Customer-facing page for viewing preview and submitting feedback

import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  ExternalLink, MessageSquare, Send, CheckCircle2,
  Loader2, Globe, Server, Smartphone, AlertTriangle,
} from 'lucide-react'
import { reviewApi } from '@/lib/api'

interface ReviewContext {
  project_name: string
  preview_name: string
  scope: string
  expires_at: string
  services: Record<string, { url: string; health: string }>
  can_submit_feedback: boolean
}

const SERVICE_ICONS: Record<string, typeof Globe> = {
  web: Globe,
  api: Server,
  mobile: Smartphone,
}

export default function ReviewPortalPage() {
  const { token } = useParams<{ token: string }>()
  const [context, setContext] = useState<ReviewContext | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Feedback form
  const [message, setMessage] = useState('')
  const [severity, setSeverity] = useState('important')
  const [pageUrl, setPageUrl] = useState('')
  const [reporterName, setReporterName] = useState('')
  const [reporterEmail, setReporterEmail] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    if (!token) return
    reviewApi.context(token)
      .then(res => setContext(res.data))
      .catch(() => setError('This review link is invalid or has expired.'))
      .finally(() => setLoading(false))
  }, [token])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!token || !message.trim()) return
    setSubmitting(true)
    try {
      await reviewApi.submitFeedback(token, {
        message: message.trim(),
        page_url: pageUrl || Object.values(context?.services || {})[0]?.url || '',
        severity,
        reporter_name: reporterName,
        reporter_email: reporterEmail,
        client_context: {
          userAgent: navigator.userAgent,
          viewport: `${window.innerWidth}x${window.innerHeight}`,
          locale: navigator.language,
        },
      })
      setSubmitted(true)
      setMessage('')
    } catch {
      setError('Failed to submit feedback. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="animate-spin text-blue-600" size={32} />
      </div>
    )
  }

  if (error || !context) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md text-center">
          <AlertTriangle size={48} className="mx-auto mb-4 text-orange-500" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Link Unavailable</h1>
          <p className="text-gray-600">{error || 'This review link is no longer available.'}</p>
        </div>
      </div>
    )
  }

  const webService = context.services.web
  const expiresDate = new Date(context.expires_at)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">{context.project_name}</h1>
            <p className="text-sm text-gray-500">Preview: {context.preview_name}</p>
          </div>
          <span className="text-xs text-gray-400">
            Expires {expiresDate.toLocaleDateString()}
          </span>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8 space-y-8">
        {/* Preview Links */}
        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Preview Links</h2>
          <div className="grid gap-3">
            {Object.entries(context.services).map(([type, svc]) => {
              const Icon = SERVICE_ICONS[type] || Server
              return (
                <a
                  key={type}
                  href={svc.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between bg-white border border-gray-200 rounded-xl p-4 hover:border-blue-300 hover:shadow-sm transition"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                      <Icon size={20} className="text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 capitalize">{type} Preview</p>
                      <p className="text-sm text-gray-500 truncate max-w-[300px]">{svc.url}</p>
                    </div>
                  </div>
                  <ExternalLink size={18} className="text-gray-400" />
                </a>
              )
            })}
          </div>
          {webService && (
            <a
              href={webService.url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 w-full flex items-center justify-center gap-2 bg-blue-600 text-white font-semibold py-3 px-6 rounded-xl hover:bg-blue-700 transition"
            >
              <Globe size={18} /> Open Preview
            </a>
          )}
        </section>

        {/* Feedback Form */}
        {context.can_submit_feedback && (
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <MessageSquare size={20} /> Leave Feedback
            </h2>

            {submitted ? (
              <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
                <CheckCircle2 size={32} className="mx-auto mb-3 text-green-600" />
                <h3 className="text-lg font-semibold text-green-800">Thank you!</h3>
                <p className="text-green-700 text-sm mt-1">Your feedback has been submitted.</p>
                <button
                  onClick={() => setSubmitted(false)}
                  className="mt-4 text-sm text-green-600 hover:underline"
                >
                  Submit more feedback
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-xl p-5 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    What should change? *
                  </label>
                  <textarea
                    value={message}
                    onChange={e => setMessage(e.target.value)}
                    required
                    rows={4}
                    className="w-full border border-gray-300 rounded-lg px-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-y"
                    placeholder="Describe what you'd like to see different..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">How important is this?</label>
                  <div className="flex gap-3">
                    {[
                      { value: 'nit', label: 'Minor', color: 'bg-blue-100 text-blue-700 border-blue-200' },
                      { value: 'important', label: 'Important', color: 'bg-yellow-100 text-yellow-700 border-yellow-200' },
                      { value: 'blocker', label: 'Must Fix', color: 'bg-red-100 text-red-700 border-red-200' },
                    ].map(opt => (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => setSeverity(opt.value)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium border transition ${
                          severity === opt.value ? opt.color : 'bg-gray-50 text-gray-500 border-gray-200'
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Which page? (optional)
                  </label>
                  <input
                    type="url"
                    value={pageUrl}
                    onChange={e => setPageUrl(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="Paste the URL of the page you're reviewing"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Your name</label>
                    <input
                      type="text"
                      value={reporterName}
                      onChange={e => setReporterName(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="Optional"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      value={reporterEmail}
                      onChange={e => setReporterEmail(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="Optional"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={submitting || !message.trim()}
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white font-semibold py-3 rounded-xl hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? (
                    <Loader2 size={18} className="animate-spin" />
                  ) : (
                    <Send size={18} />
                  )}
                  {submitting ? 'Submitting...' : 'Submit Feedback'}
                </button>
              </form>
            )}
          </section>
        )}
      </main>

      <footer className="border-t border-gray-200 py-4 text-center text-xs text-gray-400">
        Powered by Donkey Betz Platform
      </footer>
    </div>
  )
}
