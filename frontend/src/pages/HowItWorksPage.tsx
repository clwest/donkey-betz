import { useEffect, useState } from 'react'
import {
  ClipboardList,
  Users,
  CheckSquare,
  Rocket,
  BarChart3,
  FileText,
  Terminal,
  Bot,
  Bug,
  Heart,
  Wrench,
  ExternalLink,
  Youtube,
} from 'lucide-react'
import Breadcrumb from '@/components/Breadcrumb'
import { api } from '@/lib/api'

const buildLoopSteps = [
  {
    icon: ClipboardList,
    title: 'Plan',
    description: 'Clarify the user, the decision, and the success metric.',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/20',
  },
  {
    icon: Users,
    title: 'Delegate',
    description: 'Hand off to specialized agents that know the domain.',
    color: 'text-purple-400',
    bg: 'bg-purple-500/10 border-purple-500/20',
  },
  {
    icon: CheckSquare,
    title: 'Review',
    description: 'Approve or reject outputs. Keep a paper trail.',
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10 border-yellow-500/20',
  },
  {
    icon: Rocket,
    title: 'Ship',
    description: 'Deploy small changes often. Every session ships something.',
    color: 'text-green-400',
    bg: 'bg-green-500/10 border-green-500/20',
  },
  {
    icon: BarChart3,
    title: 'Measure',
    description: 'Track errors, cost, accuracy, and usage.',
    color: 'text-orange-400',
    bg: 'bg-orange-500/10 border-orange-500/20',
  },
]

const DEFAULT_STATS = [
  { value: '218', label: 'Agents', icon: Bot, key: 'total_agents' },
  { value: '79', label: 'Spiders', icon: Bug, key: 'active_spiders' },
  { value: '25', label: 'Advisors', icon: Users, key: '' },
  { value: '9', label: 'Body Systems', icon: Heart, key: '' },
  { value: '130', label: 'PA Tools', icon: Wrench, key: '' },
]

export default function HowItWorksPage() {
  const [platformStats, setPlatformStats] = useState(DEFAULT_STATS)

  useEffect(() => {
    api.get('/ecosystem/stats/').then(({ data }) => {
      setPlatformStats(prev => prev.map(stat => {
        if (stat.key && data[stat.key]) {
          return { ...stat, value: String(data[stat.key]) }
        }
        return stat
      }))
    }).catch(() => {})  // Keep defaults on error
  }, [])

  return (
    <div className="space-y-8 p-6 max-w-5xl mx-auto">
      <Breadcrumb currentPage="How it Works" />

      {/* Hero */}
      <div className="text-center space-y-4 py-8">
        <h1 className="text-4xl font-bold">How It Works</h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto">
          Build platforms with AI by turning ideas into specs, specs into tasks,
          and tasks into shippable improvements.
        </p>
      </div>

      {/* The Build Loop */}
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold">The Build Loop</h2>
        <p className="text-gray-400">
          Every session follows the same five-step loop. It keeps work small,
          reviewable, and moving forward.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {buildLoopSteps.map((step, i) => (
            <div
              key={step.title}
              className={`card border ${step.bg} p-5 space-y-3 text-center`}
            >
              <div className="flex justify-center">
                <step.icon size={28} className={step.color} />
              </div>
              <div className="text-xs text-gray-500 font-mono">Step {i + 1}</div>
              <h3 className={`text-lg font-semibold ${step.color}`}>{step.title}</h3>
              <p className="text-sm text-gray-400">{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Documentation as Persistent Context */}
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold">Documentation as Persistent Context</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card p-6 space-y-3">
            <div className="flex items-center gap-3">
              <FileText size={24} className="text-primary-400" />
              <h3 className="text-lg font-semibold">Docs Injected into Agents</h3>
            </div>
            <p className="text-gray-400 text-sm leading-relaxed">
              Topic docs are embedded and injected into agent context so they
              stay aligned with current architecture, field names, and
              constraints &mdash; even across sessions.
            </p>
          </div>
          <div className="card p-6 space-y-3">
            <div className="flex items-center gap-3">
              <Terminal size={24} className="text-primary-400" />
              <h3 className="text-lg font-semibold">Claude Code Reads Project Docs</h3>
            </div>
            <p className="text-gray-400 text-sm leading-relaxed">
              CLAUDE.md and memory files give Claude Code persistent context
              about conventions, gotchas, and model field references so it
              doesn't repeat mistakes.
            </p>
          </div>
        </div>
        <div className="card p-4 border-l-4 border-primary-500 bg-primary-500/5">
          <p className="text-sm text-gray-300 italic">
            "Prompts don't scale &mdash; docs do."
          </p>
        </div>
      </section>

      {/* Platform at a Glance */}
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold">Platform at a Glance</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {platformStats.map((stat) => (
            <div key={stat.label} className="card p-5 text-center space-y-2">
              <stat.icon size={24} className="mx-auto text-primary-400" />
              <div className="text-3xl font-bold">{stat.value}</div>
              <div className="text-sm text-gray-400">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="card p-8 text-center space-y-4">
        <h2 className="text-2xl font-semibold">Want to See It in Action?</h2>
        <p className="text-gray-400 max-w-lg mx-auto">
          Follow along as we build in public &mdash; every feature shipped live
          with AI.
        </p>
        <div className="flex justify-center gap-4 flex-wrap">
          <a
            href="https://donkeybetz.com"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary inline-flex items-center gap-2"
          >
            Join the Waitlist
            <ExternalLink size={16} />
          </a>
          <a
            href="#"
            target="_blank"
            rel="noopener noreferrer"
            className="btn bg-dark-border hover:bg-dark-border/80 text-white inline-flex items-center gap-2"
          >
            Subscribe on YouTube
            <Youtube size={16} />
          </a>
        </div>
      </section>
    </div>
  )
}
