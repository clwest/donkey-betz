import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function OperatorEdgePage() {
  const [searchParams] = useSearchParams()
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error' | 'already'>('idle')
  const [errorMsg, setErrorMsg] = useState('')
  const [subscriberCount, setSubscriberCount] = useState<number | null>(null)

  useEffect(() => {
    fetch(`${API_BASE}/api/newsletter/count/`)
      .then(r => r.json())
      .then(d => setSubscriberCount(d.count))
      .catch(() => {})
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return
    setStatus('loading')
    setErrorMsg('')

    try {
      const res = await fetch(`${API_BASE}/api/newsletter/subscribe/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          name,
          source: 'landing_page',
          utm_source: searchParams.get('utm_source') || '',
          utm_medium: searchParams.get('utm_medium') || '',
          utm_campaign: searchParams.get('utm_campaign') || '',
          referral_code: searchParams.get('ref') || '',
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        setStatus('error')
        setErrorMsg(data.error || 'Something went wrong')
        return
      }
      setStatus(data.created ? 'success' : 'already')
      if (data.created && subscriberCount !== null) {
        setSubscriberCount(subscriberCount + 1)
      }
    } catch {
      setStatus('error')
      setErrorMsg('Network error. Please try again.')
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Hero */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-950/50 via-gray-950 to-emerald-950/30" />
        <div className="relative max-w-4xl mx-auto px-6 pt-16 pb-20 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Weekly intelligence brief
          </div>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4">
            <span className="text-white">Operator</span>{' '}
            <span className="bg-gradient-to-r from-indigo-400 to-emerald-400 bg-clip-text text-transparent">Edge</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-2 max-w-2xl mx-auto">
            Signal, not noise. For builders running AI in production.
          </p>
          <p className="text-gray-400 mb-10 max-w-xl mx-auto">
            Weekly briefings on what moved in AI ops, automation, and agent infrastructure
            &mdash; sourced from real-time data, reviewed by AI agents, delivered Friday mornings.
          </p>

          {/* Signup Form */}
          {status === 'success' ? (
            <div className="max-w-md mx-auto p-6 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
              <div className="text-3xl mb-2">&#10003;</div>
              <h3 className="text-xl font-semibold text-emerald-300 mb-1">You're in.</h3>
              <p className="text-gray-400">
                Welcome to Operator Edge. Your first issue arrives this Friday.
              </p>
            </div>
          ) : status === 'already' ? (
            <div className="max-w-md mx-auto p-6 rounded-xl bg-indigo-500/10 border border-indigo-500/30">
              <h3 className="text-xl font-semibold text-indigo-300 mb-1">Already subscribed</h3>
              <p className="text-gray-400">You're on the list. Next issue drops Friday.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="max-w-md mx-auto">
              <div className="flex flex-col gap-3">
                <input
                  type="text"
                  placeholder="Your name (optional)"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-gray-800/80 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <div className="flex gap-2">
                  <input
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    required
                    className="flex-1 px-4 py-3 rounded-lg bg-gray-800/80 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                  <button
                    type="submit"
                    disabled={status === 'loading'}
                    className="px-6 py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                  >
                    {status === 'loading' ? 'Joining...' : 'Subscribe'}
                  </button>
                </div>
                {status === 'error' && (
                  <p className="text-red-400 text-sm">{errorMsg}</p>
                )}
              </div>
              <p className="text-gray-500 text-xs mt-3">
                Free. Weekly. Unsubscribe anytime.
                {subscriberCount !== null && subscriberCount > 0 && (
                  <span> Join {subscriberCount.toLocaleString()} operators.</span>
                )}
              </p>
            </form>
          )}
        </div>
      </div>

      {/* What You Get */}
      <div className="max-w-4xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-center mb-12 text-white">Every Friday, in your inbox</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon="&#9889;"
            title="Top Signal"
            description="The one trend or data point that matters most this week. No filler, no hot takes."
          />
          <FeatureCard
            icon="&#128295;"
            title="What Broke"
            description="Real incidents, failures, and lessons from teams running agents in production."
          />
          <FeatureCard
            icon="&#9881;"
            title="Autopilot Move"
            description="One concrete automation or workflow you can implement this week."
          />
          <FeatureCard
            icon="&#128176;"
            title="Cost Watch"
            description="Where AI ops budgets are leaking and how teams are fixing it."
          />
          <FeatureCard
            icon="&#128200;"
            title="What Changed"
            description="Capital flows, new tools, and shifts in the agent infrastructure landscape."
          />
          <FeatureCard
            icon="&#128640;"
            title="Deep Dive"
            description="One long-form analysis per month on how operators are monetizing AI systems."
          />
        </div>
      </div>

      {/* How It's Made */}
      <div className="border-t border-gray-800">
        <div className="max-w-4xl mx-auto px-6 py-16">
          <h2 className="text-2xl font-bold text-center mb-4 text-white">Built different</h2>
          <p className="text-center text-gray-400 mb-12 max-w-2xl mx-auto">
            Operator Edge is produced by an AI-powered intelligence pipeline &mdash;
            79 data spiders, signal clustering, multi-agent writing, and a 3-reviewer editorial panel.
            Faster cycle time. Higher freshness. Every claim cited.
          </p>
          <div className="grid md:grid-cols-4 gap-6 text-center">
            <Stat value="79" label="Data spiders" />
            <Stat value="218" label="AI agents" />
            <Stat value="3" label="Editorial reviewers" />
            <Stat value="72h" label="Data freshness" />
          </div>
        </div>
      </div>

      {/* Who It's For */}
      <div className="border-t border-gray-800">
        <div className="max-w-4xl mx-auto px-6 py-16">
          <h2 className="text-2xl font-bold text-center mb-12 text-white">For operators who ship</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <AudienceCard
              title="SREs & DevOps"
              items={['Agent fleet monitoring', 'Incident runbooks', 'Cost optimization']}
            />
            <AudienceCard
              title="AI Product Leads"
              items={['Deployment patterns', 'Safety guardrails', 'Production metrics']}
            />
            <AudienceCard
              title="Founders & Builders"
              items={['Market signals', 'Capital flows', 'Revenue plays']}
            />
          </div>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="border-t border-gray-800">
        <div className="max-w-4xl mx-auto px-6 py-16 text-center">
          <h2 className="text-2xl font-bold mb-4 text-white">Stop scrolling. Start operating.</h2>
          <p className="text-gray-400 mb-8">One email. Every Friday. The signals that matter.</p>
          {status !== 'success' && status !== 'already' && (
            <form onSubmit={handleSubmit} className="max-w-sm mx-auto flex gap-2">
              <input
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                className="flex-1 px-4 py-3 rounded-lg bg-gray-800/80 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="submit"
                disabled={status === 'loading'}
                className="px-6 py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-colors disabled:opacity-50"
              >
                Join
              </button>
            </form>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-800 py-8 text-center text-gray-600 text-sm">
        <p>Operator Edge &mdash; by Donkey Betz AI Studio</p>
      </div>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="p-6 rounded-xl bg-gray-900/50 border border-gray-800 hover:border-gray-700 transition-colors">
      <div className="text-2xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
    </div>
  )
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="text-3xl font-bold text-indigo-400">{value}</div>
      <div className="text-gray-500 text-sm mt-1">{label}</div>
    </div>
  )
}

function AudienceCard({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="p-6 rounded-xl bg-gray-900/50 border border-gray-800">
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex items-center gap-2 text-gray-400 text-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 flex-shrink-0" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}
