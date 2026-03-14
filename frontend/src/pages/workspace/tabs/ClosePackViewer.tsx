// BPaaS: Close Pack Viewer — Displays SOW, Delivery Checklist, and Proposal

import { useState } from 'react'
import {
  FileText, CheckSquare, Briefcase, Copy, Check, Download,
  ChevronDown, ChevronRight, X,
} from 'lucide-react'
import { cn } from '@/lib/cn'

interface ClosePackViewerProps {
  closePack: {
    sow: { title: string; sections: Record<string, unknown> }
    checklist: { title: string; items: Array<{ category: string; items: string[] }> }
    proposal: { title: string; [key: string]: unknown }
  }
  onClose: () => void
}

const TABS = [
  { id: 'proposal', label: 'Proposal', icon: Briefcase },
  { id: 'sow', label: 'SOW', icon: FileText },
  { id: 'checklist', label: 'Checklist', icon: CheckSquare },
]

export function ClosePackViewer({ closePack, onClose }: ClosePackViewerProps) {
  const [activeTab, setActiveTab] = useState('proposal')
  const [copied, setCopied] = useState(false)

  function copyToClipboard() {
    const content = activeTab === 'proposal'
      ? formatProposal(closePack.proposal)
      : activeTab === 'sow'
      ? formatSOW(closePack.sow)
      : formatChecklist(closePack.checklist)
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-card border border-dark-border rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-dark-border">
          <h2 className="text-lg font-bold">Close Pack</h2>
          <div className="flex items-center gap-2">
            <button onClick={copyToClipboard}
              className="flex items-center gap-1.5 px-3 py-1.5 border border-dark-border rounded-lg text-xs hover:bg-dark-bg">
              {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
              {copied ? 'Copied' : 'Copy'}
            </button>
            <button onClick={onClose} className="p-1 hover:bg-dark-border rounded">
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-dark-border">
          {TABS.map(tab => {
            const Icon = tab.icon
            return (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 transition',
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                )}>
                <Icon size={14} /> {tab.label}
              </button>
            )
          })}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5">
          {activeTab === 'proposal' && <ProposalView data={closePack.proposal} />}
          {activeTab === 'sow' && <SOWView data={closePack.sow} />}
          {activeTab === 'checklist' && <ChecklistView data={closePack.checklist} />}
        </div>
      </div>
    </div>
  )
}

function ProposalView({ data }: { data: Record<string, unknown> }) {
  return (
    <div className="space-y-5">
      <h3 className="text-xl font-bold">{data.title as string}</h3>

      <Section title="Problem">
        <p className="text-sm text-muted-foreground">{data.problem as string}</p>
      </Section>

      <Section title="Solution">
        <p className="text-sm">{data.solution_summary as string}</p>
      </Section>

      <Section title="Key Flows">
        <ul className="space-y-1">
          {(data.key_flows as string[])?.map((f, i) => (
            <li key={i} className="text-sm flex items-center gap-2">
              <ChevronRight size={12} className="text-primary" /> {f}
            </li>
          ))}
        </ul>
      </Section>

      <Section title="What's Included">
        <ul className="space-y-1">
          {(data.includes as string[])?.map((item, i) => (
            <li key={i} className="text-sm flex items-start gap-2">
              <Check size={14} className="text-green-400 mt-0.5 flex-shrink-0" /> {item}
            </li>
          ))}
        </ul>
      </Section>

      {(data.excludes as string[])?.length > 0 && (
        <Section title="Not Included (Out of Scope)">
          <ul className="space-y-1">
            {(data.excludes as string[]).map((item, i) => (
              <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                <X size={14} className="text-red-400 mt-0.5 flex-shrink-0" /> {item}
              </li>
            ))}
          </ul>
        </Section>
      )}

      <Section title="Timeline">
        <p className="text-sm font-medium">{data.timeline as string}</p>
      </Section>
    </div>
  )
}

function SOWView({ data }: { data: { title: string; sections: Record<string, unknown> } }) {
  const s = data.sections
  return (
    <div className="space-y-5">
      <h3 className="text-xl font-bold">{data.title}</h3>

      <Section title="Project Overview">
        <p className="text-sm">{s.project_overview as string}</p>
      </Section>

      <Section title="Deliverables">
        <ul className="space-y-1">
          {(s.deliverables as string[])?.map((d, i) => (
            <li key={i} className="text-sm flex items-start gap-2">
              <Check size={14} className="text-green-400 mt-0.5 flex-shrink-0" /> {d}
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Acceptance Criteria">
        <ol className="space-y-1 list-decimal list-inside">
          {(s.acceptance_criteria as string[])?.map((c, i) => (
            <li key={i} className="text-sm">{c}</li>
          ))}
        </ol>
      </Section>

      <Section title="Timeline">
        <p className="text-sm font-medium">{s.timeline as string}</p>
      </Section>

      <Section title="Revision Policy">
        <p className="text-sm text-muted-foreground">{s.revision_policy as string}</p>
      </Section>

      <Section title="Payment Terms">
        <p className="text-sm font-medium">{s.payment_terms as string}</p>
      </Section>
    </div>
  )
}

function ChecklistView({ data }: { data: { title: string; items: Array<{ category: string; items: string[] }> } }) {
  const [checked, setChecked] = useState<Set<string>>(new Set())

  function toggle(key: string) {
    const next = new Set(checked)
    if (next.has(key)) next.delete(key)
    else next.add(key)
    setChecked(next)
  }

  const totalItems = data.items.reduce((sum, cat) => sum + cat.items.length, 0)
  const checkedCount = checked.size

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold">{data.title}</h3>
        <span className="text-sm text-muted-foreground">{checkedCount}/{totalItems} complete</span>
      </div>

      <div className="w-full bg-dark-bg rounded-full h-2">
        <div className="bg-green-500 h-2 rounded-full transition-all"
          style={{ width: `${totalItems > 0 ? (checkedCount / totalItems) * 100 : 0}%` }} />
      </div>

      {data.items.map((cat, ci) => (
        <div key={ci}>
          <h4 className="font-semibold text-sm mb-2">{cat.category}</h4>
          <div className="space-y-1">
            {cat.items.map((item, ii) => {
              const key = `${ci}-${ii}`
              const isChecked = checked.has(key)
              return (
                <button key={key} onClick={() => toggle(key)}
                  className={cn(
                    'flex items-center gap-2 w-full text-left px-3 py-2 rounded-lg text-sm transition',
                    isChecked ? 'bg-green-500/10 text-green-400 line-through' : 'bg-dark-bg hover:bg-dark-bg/80'
                  )}>
                  <div className={cn(
                    'w-4 h-4 rounded border flex items-center justify-center flex-shrink-0',
                    isChecked ? 'bg-green-500 border-green-500' : 'border-dark-border'
                  )}>
                    {isChecked && <Check size={10} className="text-white" />}
                  </div>
                  {item}
                </button>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-2">{title}</h4>
      {children}
    </div>
  )
}

// ── Formatters for clipboard copy ─────────────────────────────────────────

function formatProposal(data: Record<string, unknown>): string {
  const lines = [`# ${data.title}\n`, `## Problem\n${data.problem}\n`, `## Solution\n${data.solution_summary}\n`]
  if ((data.key_flows as string[])?.length) lines.push(`## Key Flows\n${(data.key_flows as string[]).map(f => `- ${f}`).join('\n')}\n`)
  if ((data.includes as string[])?.length) lines.push(`## Included\n${(data.includes as string[]).map(i => `- ${i}`).join('\n')}\n`)
  if ((data.excludes as string[])?.length) lines.push(`## Not Included\n${(data.excludes as string[]).map(i => `- ${i}`).join('\n')}\n`)
  lines.push(`## Timeline\n${data.timeline}\n`)
  return lines.join('\n')
}

function formatSOW(data: { title: string; sections: Record<string, unknown> }): string {
  const s = data.sections
  const lines = [`# ${data.title}\n`]
  if (s.project_overview) lines.push(`## Project Overview\n${s.project_overview}\n`)
  if ((s.deliverables as string[])?.length) lines.push(`## Deliverables\n${(s.deliverables as string[]).map(d => `- ${d}`).join('\n')}\n`)
  if ((s.acceptance_criteria as string[])?.length) lines.push(`## Acceptance Criteria\n${(s.acceptance_criteria as string[]).map((c, i) => `${i + 1}. ${c}`).join('\n')}\n`)
  lines.push(`## Timeline\n${s.timeline}\n`, `## Revision Policy\n${s.revision_policy}\n`, `## Payment Terms\n${s.payment_terms}\n`)
  return lines.join('\n')
}

function formatChecklist(data: { title: string; items: Array<{ category: string; items: string[] }> }): string {
  const lines = [`# ${data.title}\n`]
  for (const cat of data.items) {
    lines.push(`## ${cat.category}`)
    for (const item of cat.items) lines.push(`- [ ] ${item}`)
    lines.push('')
  }
  return lines.join('\n')
}
