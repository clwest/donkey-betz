// BPaaS: Build Packet Wizard — Guided intake form for new client projects
// Produces a structured build packet that can be sent to create-from-packet API

import { useState } from 'react'
import {
  Rocket, ChevronRight, ChevronLeft, Check, Users, Workflow,
  Monitor, Database, Plug, Palette, Target, Clock, X,
  Plus, Trash2, Loader2,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { previewApi } from '@/lib/api'

interface BuildPacketWizardProps {
  workspaceId: string
  onComplete: (result: Record<string, unknown>) => void
  onCancel: () => void
}

const STEPS = [
  { id: 'project', label: 'Project', icon: Rocket },
  { id: 'users', label: 'Users', icon: Users },
  { id: 'flows', label: 'Flows', icon: Workflow },
  { id: 'screens', label: 'Screens', icon: Monitor },
  { id: 'data', label: 'Data Model', icon: Database },
  { id: 'integrations', label: 'Integrations', icon: Plug },
  { id: 'brand', label: 'Brand', icon: Palette },
  { id: 'criteria', label: 'Done Criteria', icon: Target },
  { id: 'review', label: 'Review & Create', icon: Check },
]

const BUSINESS_TYPES = [
  { value: 'service_business', label: 'Service Business' },
  { value: 'marketplace', label: 'Marketplace' },
  { value: 'saas', label: 'SaaS' },
  { value: 'internal_tool', label: 'Internal Tool' },
  { value: 'ecommerce', label: 'E-Commerce' },
  { value: 'content_platform', label: 'Content Platform' },
  { value: 'other', label: 'Other' },
]

const COMMON_INTEGRATIONS = [
  'Stripe', 'Twilio', 'SendGrid', 'Google Maps', 'AWS S3',
  'Firebase', 'Auth0', 'Mailchimp', 'Zapier', 'Slack',
]

export function BuildPacketWizard({ workspaceId, onComplete, onCancel }: BuildPacketWizardProps) {
  const [step, setStep] = useState(0)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  // Project
  const [projectName, setProjectName] = useState('')
  const [problemStatement, setProblemStatement] = useState('')
  const [businessType, setBusinessType] = useState('service_business')
  const [targetAudience, setTargetAudience] = useState('')
  const [geoFocus, setGeoFocus] = useState('')

  // Users
  const [users, setUsers] = useState([
    { role: '', description: '', platform: 'web', auth_required: false, tech_comfort: 'medium' },
  ])

  // Flows
  const [flows, setFlows] = useState([
    { name: '', actor: '', steps: [''], priority: 'must_have' },
  ])

  // Screens
  const [screens, setScreens] = useState([
    { name: '', platform: 'web', description: '', public: false },
  ])

  // Data model
  const [entities, setEntities] = useState([
    { name: '', description: '', key_fields: [''], statuses: [''] },
  ])

  // Integrations
  const [integrations, setIntegrations] = useState<Array<{ service: string; purpose: string; mvp_required: boolean }>>([])

  // Brand
  const [brandName, setBrandName] = useState('')
  const [tagline, setTagline] = useState('')
  const [colorPalette, setColorPalette] = useState('trust_navy')
  const [tone, setTone] = useState('professional')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')

  // Criteria
  const [criteria, setCriteria] = useState([''])
  const [outOfScope, setOutOfScope] = useState([''])
  const [timeline, setTimeline] = useState('2 weeks')

  function buildPacket() {
    return {
      project: {
        name: projectName,
        slug: projectName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''),
        problem_statement: problemStatement,
        business_type: businessType,
        target_audience: targetAudience,
        geographic_focus: geoFocus,
      },
      users: users.filter(u => u.role),
      flows: flows.filter(f => f.name).map(f => ({
        ...f,
        steps: f.steps.filter(s => s),
      })),
      screens: screens.filter(s => s.name),
      data_model: entities.filter(e => e.name).map(e => ({
        ...e,
        key_fields: e.key_fields.filter(f => f),
        statuses: e.statuses.filter(s => s),
      })),
      integrations: integrations.filter(i => i.service),
      tech_stack: {
        backend: 'django',
        web_frontend: 'nextjs',
        mobile: 'expo',
        database: 'postgresql',
        hosting: 'railway_vercel',
        auth: 'token',
      },
      brand: {
        business_name: brandName || projectName,
        tagline,
        color_palette: colorPalette,
        tone,
        phone,
        email,
      },
      acceptance_criteria: criteria.filter(c => c),
      timeline: { target_delivery: timeline },
      out_of_scope: outOfScope.filter(o => o),
    }
  }

  async function handleCreate() {
    setCreating(true)
    setError('')
    try {
      const packet = buildPacket()
      const res = await fetch('/api/bpaas/create-from-packet/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace_id: workspaceId, packet }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.error || 'Failed to create project')
      }
      const result = await res.json()
      onComplete(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project')
    } finally {
      setCreating(false)
    }
  }

  const canNext = () => {
    if (step === 0) return projectName && problemStatement
    if (step === 7) return criteria.some(c => c.trim())
    return true
  }

  const currentStep = STEPS[step]

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-card border border-dark-border rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <Rocket size={20} className="text-primary" />
            <h2 className="text-lg font-bold">New Build Packet</h2>
          </div>
          <button onClick={onCancel} className="p-1 hover:bg-dark-border rounded">
            <X size={18} />
          </button>
        </div>

        {/* Step indicators */}
        <div className="flex items-center gap-1 px-5 py-3 border-b border-dark-border overflow-x-auto">
          {STEPS.map((s, i) => {
            const Icon = s.icon
            return (
              <button
                key={s.id}
                onClick={() => setStep(i)}
                className={cn(
                  'flex items-center gap-1.5 px-2 py-1 rounded text-xs whitespace-nowrap transition',
                  i === step ? 'bg-primary/10 text-primary font-medium' :
                  i < step ? 'text-green-400' : 'text-muted-foreground'
                )}
              >
                {i < step ? <Check size={12} /> : <Icon size={12} />}
                {s.label}
              </button>
            )
          })}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4 text-sm text-red-400">
              {error}
            </div>
          )}

          {/* Step 0: Project */}
          {step === 0 && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Project Details</h3>
              <Field label="Project Name *" value={projectName} onChange={setProjectName} placeholder="e.g. Norman Handyman MVP" />
              <Field label="Problem Statement *" value={problemStatement} onChange={setProblemStatement} placeholder="What problem does this solve? Who has this problem?" multiline />
              <div className="grid grid-cols-2 gap-4">
                <SelectField label="Business Type" value={businessType} onChange={setBusinessType} options={BUSINESS_TYPES} />
                <Field label="Geographic Focus" value={geoFocus} onChange={setGeoFocus} placeholder="e.g. Norman, OK" />
              </div>
              <Field label="Target Audience" value={targetAudience} onChange={setTargetAudience} placeholder="Who are the users? Age, tech comfort, context." multiline />
            </div>
          )}

          {/* Step 1: Users */}
          {step === 1 && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">User Roles</h3>
              <p className="text-sm text-muted-foreground">Who will use this app?</p>
              {users.map((u, i) => (
                <div key={i} className="bg-dark-bg rounded-lg p-4 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">User {i + 1}</span>
                    {users.length > 1 && (
                      <button onClick={() => setUsers(users.filter((_, j) => j !== i))} className="text-red-400 hover:text-red-300">
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Role" value={u.role} onChange={v => { const n = [...users]; n[i].role = v; setUsers(n) }} placeholder="e.g. customer, operator" />
                    <SelectField label="Platform" value={u.platform} onChange={v => { const n = [...users]; n[i].platform = v; setUsers(n) }}
                      options={[{ value: 'web', label: 'Web' }, { value: 'mobile', label: 'Mobile' }, { value: 'both', label: 'Both' }]} />
                  </div>
                  <Field label="Description" value={u.description} onChange={v => { const n = [...users]; n[i].description = v; setUsers(n) }} placeholder="What does this user do?" />
                </div>
              ))}
              <button onClick={() => setUsers([...users, { role: '', description: '', platform: 'web', auth_required: false, tech_comfort: 'medium' }])}
                className="flex items-center gap-1.5 text-sm text-primary hover:underline">
                <Plus size={14} /> Add User Role
              </button>
            </div>
          )}

          {/* Step 2: Flows */}
          {step === 2 && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Core Workflows</h3>
              <p className="text-sm text-muted-foreground">What are the key user journeys?</p>
              {flows.map((f, i) => (
                <div key={i} className="bg-dark-bg rounded-lg p-4 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Flow {i + 1}</span>
                    {flows.length > 1 && (
                      <button onClick={() => setFlows(flows.filter((_, j) => j !== i))} className="text-red-400"><Trash2 size={14} /></button>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Flow Name" value={f.name} onChange={v => { const n = [...flows]; n[i].name = v; setFlows(n) }} placeholder="e.g. Book Appointment" />
                    <Field label="Actor" value={f.actor} onChange={v => { const n = [...flows]; n[i].actor = v; setFlows(n) }} placeholder="Which user role?" />
                  </div>
                  <div>
                    <label className="block text-xs text-muted-foreground mb-1">Steps</label>
                    {f.steps.map((s, si) => (
                      <div key={si} className="flex gap-2 mb-1">
                        <span className="text-xs text-muted-foreground mt-2 w-5">{si + 1}.</span>
                        <input className="flex-1 bg-dark-card border border-dark-border rounded px-3 py-1.5 text-sm"
                          value={s} onChange={e => { const n = [...flows]; n[i].steps[si] = e.target.value; setFlows(n) }} placeholder="Step description" />
                        {f.steps.length > 1 && (
                          <button onClick={() => { const n = [...flows]; n[i].steps = n[i].steps.filter((_, k) => k !== si); setFlows(n) }} className="text-red-400"><X size={14} /></button>
                        )}
                      </div>
                    ))}
                    <button onClick={() => { const n = [...flows]; n[i].steps.push(''); setFlows(n) }}
                      className="text-xs text-primary hover:underline mt-1">+ Add Step</button>
                  </div>
                </div>
              ))}
              <button onClick={() => setFlows([...flows, { name: '', actor: '', steps: [''], priority: 'must_have' }])}
                className="flex items-center gap-1.5 text-sm text-primary hover:underline">
                <Plus size={14} /> Add Flow
              </button>
            </div>
          )}

          {/* Step 3: Screens */}
          {step === 3 && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Screens & Pages</h3>
              {screens.map((s, i) => (
                <div key={i} className="flex gap-3 items-start bg-dark-bg rounded-lg p-3">
                  <div className="flex-1 grid grid-cols-3 gap-2">
                    <input className="bg-dark-card border border-dark-border rounded px-3 py-1.5 text-sm col-span-1"
                      value={s.name} onChange={e => { const n = [...screens]; n[i].name = e.target.value; setScreens(n) }} placeholder="Screen name" />
                    <select className="bg-dark-card border border-dark-border rounded px-3 py-1.5 text-sm"
                      value={s.platform} onChange={e => { const n = [...screens]; n[i].platform = e.target.value; setScreens(n) }}>
                      <option value="web">Web</option><option value="mobile">Mobile</option><option value="both">Both</option>
                    </select>
                    <label className="flex items-center gap-1.5 text-sm">
                      <input type="checkbox" checked={s.public} onChange={e => { const n = [...screens]; n[i].public = e.target.checked; setScreens(n) }} />
                      Public
                    </label>
                  </div>
                  {screens.length > 1 && (
                    <button onClick={() => setScreens(screens.filter((_, j) => j !== i))} className="text-red-400 mt-1"><Trash2 size={14} /></button>
                  )}
                </div>
              ))}
              <button onClick={() => setScreens([...screens, { name: '', platform: 'web', description: '', public: false }])}
                className="flex items-center gap-1.5 text-sm text-primary hover:underline">
                <Plus size={14} /> Add Screen
              </button>
            </div>
          )}

          {/* Step 4: Data Model */}
          {step === 4 && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Data Model</h3>
              <p className="text-sm text-muted-foreground">What are the core entities?</p>
              {entities.map((e, i) => (
                <div key={i} className="bg-dark-bg rounded-lg p-4 space-y-2">
                  <div className="flex justify-between">
                    <Field label="Entity Name" value={e.name} onChange={v => { const n = [...entities]; n[i].name = v; setEntities(n) }} placeholder="e.g. Customer, Job, Invoice" />
                    {entities.length > 1 && (
                      <button onClick={() => setEntities(entities.filter((_, j) => j !== i))} className="text-red-400 mt-4"><Trash2 size={14} /></button>
                    )}
                  </div>
                  <Field label="Description" value={e.description} onChange={v => { const n = [...entities]; n[i].description = v; setEntities(n) }} placeholder="What is this?" />
                  <ListField label="Key Fields" items={e.key_fields}
                    onChange={v => { const n = [...entities]; n[i].key_fields = v; setEntities(n) }} placeholder="e.g. name, email, status" />
                  <ListField label="Statuses (if applicable)" items={e.statuses}
                    onChange={v => { const n = [...entities]; n[i].statuses = v; setEntities(n) }} placeholder="e.g. DRAFT, ACTIVE, COMPLETED" />
                </div>
              ))}
              <button onClick={() => setEntities([...entities, { name: '', description: '', key_fields: [''], statuses: [''] }])}
                className="flex items-center gap-1.5 text-sm text-primary hover:underline">
                <Plus size={14} /> Add Entity
              </button>
            </div>
          )}

          {/* Step 5: Integrations */}
          {step === 5 && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Integrations</h3>
              <div className="flex flex-wrap gap-2">
                {COMMON_INTEGRATIONS.map(svc => {
                  const selected = integrations.some(i => i.service === svc)
                  return (
                    <button key={svc} onClick={() => {
                      if (selected) setIntegrations(integrations.filter(i => i.service !== svc))
                      else setIntegrations([...integrations, { service: svc, purpose: '', mvp_required: true }])
                    }} className={cn(
                      'px-3 py-1.5 rounded-lg text-sm border transition',
                      selected ? 'bg-primary/10 border-primary text-primary' : 'border-dark-border hover:border-dark-border/80'
                    )}>
                      {svc}
                    </button>
                  )
                })}
              </div>
              {integrations.map((ig, i) => (
                <div key={i} className="flex gap-3 items-center bg-dark-bg rounded-lg p-3">
                  <span className="text-sm font-medium w-24">{ig.service}</span>
                  <input className="flex-1 bg-dark-card border border-dark-border rounded px-3 py-1.5 text-sm"
                    value={ig.purpose} onChange={e => { const n = [...integrations]; n[i].purpose = e.target.value; setIntegrations(n) }}
                    placeholder="What is it used for?" />
                </div>
              ))}
            </div>
          )}

          {/* Step 6: Brand */}
          {step === 6 && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Brand & Design</h3>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Business Name" value={brandName} onChange={setBrandName} placeholder={projectName || 'Business name'} />
                <Field label="Tagline" value={tagline} onChange={setTagline} placeholder="Short tagline" />
                <Field label="Phone" value={phone} onChange={setPhone} placeholder="(405) 555-0123" />
                <Field label="Email" value={email} onChange={setEmail} placeholder="info@business.com" />
              </div>
              <SelectField label="Color Palette" value={colorPalette} onChange={setColorPalette} options={[
                { value: 'trust_navy', label: 'Trust Navy (professional)' },
                { value: 'warm_green', label: 'Warm Green (approachable)' },
                { value: 'modern_dark', label: 'Modern Dark (tech)' },
                { value: 'clean_light', label: 'Clean Light (minimal)' },
                { value: 'custom', label: 'Custom' },
              ]} />
              <SelectField label="Tone" value={tone} onChange={setTone} options={[
                { value: 'professional', label: 'Professional' },
                { value: 'friendly', label: 'Friendly' },
                { value: 'premium', label: 'Premium' },
                { value: 'playful', label: 'Playful' },
                { value: 'minimal', label: 'Minimal' },
              ]} />
            </div>
          )}

          {/* Step 7: Acceptance Criteria */}
          {step === 7 && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Definition of Done</h3>
              <ListField label="Acceptance Criteria *" items={criteria} onChange={setCriteria}
                placeholder="What must be true for the MVP to be done?" />
              <ListField label="Out of Scope (explicit)" items={outOfScope} onChange={setOutOfScope}
                placeholder="Things NOT included in MVP" />
              <Field label="Target Timeline" value={timeline} onChange={setTimeline} placeholder="e.g. 2 weeks" />
            </div>
          )}

          {/* Step 8: Review */}
          {step === 8 && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Review & Create</h3>
              <div className="bg-dark-bg rounded-lg p-4 space-y-3 text-sm">
                <div><span className="text-muted-foreground">Project:</span> <strong>{projectName}</strong></div>
                <div><span className="text-muted-foreground">Type:</span> {businessType}</div>
                <div><span className="text-muted-foreground">Users:</span> {users.filter(u => u.role).map(u => u.role).join(', ') || 'None'}</div>
                <div><span className="text-muted-foreground">Flows:</span> {flows.filter(f => f.name).length}</div>
                <div><span className="text-muted-foreground">Screens:</span> {screens.filter(s => s.name).length}</div>
                <div><span className="text-muted-foreground">Entities:</span> {entities.filter(e => e.name).map(e => e.name).join(', ') || 'None'}</div>
                <div><span className="text-muted-foreground">Integrations:</span> {integrations.map(i => i.service).join(', ') || 'None'}</div>
                <div><span className="text-muted-foreground">Criteria:</span> {criteria.filter(c => c).length} items</div>
                <div><span className="text-muted-foreground">Timeline:</span> {timeline}</div>
              </div>
              <p className="text-sm text-muted-foreground">
                This will create a WorkspaceProject with repos, preview environment, and a magic link for client review.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-5 border-t border-dark-border">
          <button onClick={() => step > 0 ? setStep(step - 1) : onCancel()}
            className="flex items-center gap-1.5 px-4 py-2 border border-dark-border rounded-lg text-sm hover:bg-dark-bg">
            <ChevronLeft size={14} /> {step === 0 ? 'Cancel' : 'Back'}
          </button>
          {step < STEPS.length - 1 ? (
            <button onClick={() => setStep(step + 1)} disabled={!canNext()}
              className="flex items-center gap-1.5 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium disabled:opacity-50">
              Next <ChevronRight size={14} />
            </button>
          ) : (
            <button onClick={handleCreate} disabled={creating}
              className="flex items-center gap-1.5 px-6 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50">
              {creating ? <Loader2 size={14} className="animate-spin" /> : <Rocket size={14} />}
              {creating ? 'Creating...' : 'Create Project'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Reusable form components ──────────────────────────────────────────────

function Field({ label, value, onChange, placeholder, multiline }: {
  label: string; value: string; onChange: (v: string) => void; placeholder?: string; multiline?: boolean
}) {
  const cls = "w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm focus:ring-1 focus:ring-primary outline-none"
  return (
    <div>
      <label className="block text-xs text-muted-foreground mb-1">{label}</label>
      {multiline ? (
        <textarea className={cn(cls, 'min-h-[80px] resize-y')} value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} />
      ) : (
        <input className={cls} value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} />
      )}
    </div>
  )
}

function SelectField({ label, value, onChange, options }: {
  label: string; value: string; onChange: (v: string) => void; options: Array<{ value: string; label: string }>
}) {
  return (
    <div>
      <label className="block text-xs text-muted-foreground mb-1">{label}</label>
      <select className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm" value={value} onChange={e => onChange(e.target.value)}>
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  )
}

function ListField({ label, items, onChange, placeholder }: {
  label: string; items: string[]; onChange: (items: string[]) => void; placeholder?: string
}) {
  return (
    <div>
      <label className="block text-xs text-muted-foreground mb-1">{label}</label>
      {items.map((item, i) => (
        <div key={i} className="flex gap-2 mb-1">
          <input className="flex-1 bg-dark-card border border-dark-border rounded px-3 py-1.5 text-sm"
            value={item} onChange={e => { const n = [...items]; n[i] = e.target.value; onChange(n) }} placeholder={placeholder} />
          {items.length > 1 && (
            <button onClick={() => onChange(items.filter((_, j) => j !== i))} className="text-red-400"><X size={14} /></button>
          )}
        </div>
      ))}
      <button onClick={() => onChange([...items, ''])} className="text-xs text-primary hover:underline mt-1">+ Add</button>
    </div>
  )
}
