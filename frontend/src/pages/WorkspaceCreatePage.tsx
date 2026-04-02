/**
 * WorkspaceCreatePage — Create a new workspace from a template.
 *
 * Template selection + naming → provisions a complete business workspace
 * with pre-configured pipeline, agents, and deliverable categories.
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import {
  Rocket, ArrowLeft, ArrowRight, Check, Sparkles,
  Newspaper, Target, FlaskConical, Wrench, Users, Zap,
} from 'lucide-react'

interface PipelineStage {
  name: string
  agent: string | null
  auto: boolean
  requires_approval?: boolean
  description?: string
}

interface Template {
  id: string
  name: string
  slug: string
  description: string
  icon: string
  category: string
  is_featured: boolean
  pipeline_stage_count: number
  agent_count: number
  spider_count?: number
  pipeline_stages: PipelineStage[]
  agent_pool: string[]
  deliverable_categories: string[]
  default_settings: Record<string, unknown>
}

const ICON_MAP: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  newsletter: Newspaper,
  leadgen: Target,
  research: FlaskConical,
  custom: Wrench,
}

export default function WorkspaceCreatePage() {
  const navigate = useNavigate()
  const [templates, setTemplates] = useState<Template[]>([])
  const [selected, setSelected] = useState<Template | null>(null)
  const [step, setStep] = useState<'select' | 'configure' | 'creating'>('select')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/workspace-templates/').then(res => {
      if (res.data.success) setTemplates(res.data.templates)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const handleCreate = async () => {
    if (!selected || !name.trim()) return
    setCreating(true)
    setError('')
    setStep('creating')

    try {
      const res = await api.post('/workspaces/create-from-template/', {
        template_slug: selected.slug,
        name: name.trim(),
        description: description.trim(),
      })
      if (res.data.success) {
        // Navigate to the new workspace dashboard
        navigate(`/workspace/${res.data.workspace.id}`)
      } else {
        setError(res.data.error || 'Failed to create workspace')
        setStep('configure')
      }
    } catch (err) {
      setError('Failed to create workspace. Please try again.')
      setStep('configure')
    } finally {
      setCreating(false)
    }
  }

  const IconComponent = selected ? (ICON_MAP[selected.slug] || Sparkles) : Sparkles

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-white">
            <ArrowLeft size={20} />
          </button>
          <Rocket className="text-blue-400" size={24} />
          <h1 className="text-2xl font-bold text-white">Create Workspace</h1>
        </div>

        {/* Step 1: Template Selection */}
        {step === 'select' && (
          <div>
            <p className="text-gray-400 mb-6">
              Choose a template to get started. Each template comes pre-configured with the right
              agents, pipeline stages, and data feeds for your business.
            </p>

            {loading ? (
              <div className="text-center text-gray-500 py-12">Loading templates...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templates.map(tmpl => {
                  const Icon = ICON_MAP[tmpl.slug] || Sparkles
                  return (
                    <button
                      key={tmpl.id}
                      onClick={() => { setSelected(tmpl); setStep('configure') }}
                      className={`text-left p-6 rounded-xl border transition-all hover:border-blue-500/50 hover:bg-gray-900/50 ${
                        tmpl.is_featured
                          ? 'border-blue-800/30 bg-blue-950/10'
                          : 'border-gray-800 bg-gray-900/30'
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <div className="p-3 rounded-lg bg-gray-800">
                          <Icon size={24} className="text-blue-400" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-lg font-semibold text-white">{tmpl.name}</h3>
                            {tmpl.is_featured && (
                              <span className="text-xs bg-blue-600/20 text-blue-300 px-2 py-0.5 rounded-full">Featured</span>
                            )}
                          </div>
                          <p className="text-sm text-gray-400 mb-3">{tmpl.description}</p>
                          <div className="flex gap-4 text-xs text-gray-500">
                            <span className="flex items-center gap-1">
                              <Zap size={12} /> {tmpl.pipeline_stage_count} stages
                            </span>
                            <span className="flex items-center gap-1">
                              <Users size={12} /> {tmpl.agent_count} agents
                            </span>
                          </div>
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        )}

        {/* Step 2: Configure */}
        {step === 'configure' && selected && (
          <div>
            <button
              onClick={() => setStep('select')}
              className="text-sm text-gray-400 hover:text-white mb-6 flex items-center gap-1"
            >
              <ArrowLeft size={14} /> Back to templates
            </button>

            <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 mb-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-lg bg-gray-800">
                  <IconComponent size={24} className="text-blue-400" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-white">{selected.name}</h2>
                  <p className="text-sm text-gray-400">{selected.description}</p>
                </div>
              </div>

              {/* Name input */}
              <div className="space-y-4 mt-6">
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Workspace Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    placeholder={`My ${selected.name}...`}
                    className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
                    autoFocus
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Description (optional)</label>
                  <textarea
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                    placeholder="What is this workspace for?"
                    rows={2}
                    className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500 resize-none"
                  />
                </div>
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-900/30 border border-red-800 rounded-lg text-red-300 text-sm">
                  {error}
                </div>
              )}
            </div>

            {/* Pipeline Preview */}
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 mb-6">
              <h3 className="text-sm font-medium text-gray-300 mb-4">Pipeline Stages</h3>
              <div className="space-y-2">
                {selected.pipeline_stages.map((stage, i) => (
                  <div key={i} className="flex items-center gap-3 text-sm">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      stage.auto ? 'bg-green-900/50 text-green-300' : 'bg-yellow-900/50 text-yellow-300'
                    }`}>
                      {i + 1}
                    </div>
                    <div className="flex-1">
                      <span className="text-white">{stage.name}</span>
                      {stage.agent && (
                        <span className="text-gray-500 ml-2">({stage.agent})</span>
                      )}
                    </div>
                    <div className="flex gap-2">
                      {stage.auto && (
                        <span className="text-xs bg-green-900/30 text-green-300 px-2 py-0.5 rounded">Auto</span>
                      )}
                      {stage.requires_approval && (
                        <span className="text-xs bg-yellow-900/30 text-yellow-300 px-2 py-0.5 rounded">Approval</span>
                      )}
                      {!stage.auto && !stage.requires_approval && (
                        <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded">Manual</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Agents & Categories */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
                <h3 className="text-sm font-medium text-gray-300 mb-3">Agent Pool</h3>
                <div className="flex flex-wrap gap-1.5">
                  {selected.agent_pool.map(agent => (
                    <span key={agent} className="text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded">
                      {agent}
                    </span>
                  ))}
                </div>
              </div>
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
                <h3 className="text-sm font-medium text-gray-300 mb-3">Output Categories</h3>
                <div className="flex flex-wrap gap-1.5">
                  {selected.deliverable_categories.map(cat => (
                    <span key={cat} className="text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded">
                      {cat}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Create Button */}
            <button
              onClick={handleCreate}
              disabled={!name.trim() || creating}
              className="w-full py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
            >
              {creating ? (
                <>Creating workspace...</>
              ) : (
                <>
                  <Check size={18} /> Create {selected.name}
                </>
              )}
            </button>
          </div>
        )}

        {/* Step 3: Creating (animation) */}
        {step === 'creating' && (
          <div className="text-center py-20">
            <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Setting up your workspace</h2>
            <p className="text-gray-400">Configuring pipeline, agents, and data feeds...</p>
          </div>
        )}
      </div>
    </div>
  )
}
