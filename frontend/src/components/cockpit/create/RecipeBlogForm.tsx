import { useState } from 'react'

export interface BlogFormData {
  topic: string
  style: string
  length: string
  citations: boolean
}

interface RecipeBlogFormProps {
  onChange: (data: BlogFormData) => void
  data: BlogFormData
}

const STYLE_OPTIONS = ['engaging', 'pragmatic', 'technical', 'conversational', 'persuasive']
const LENGTH_OPTIONS = ['short', 'medium', 'long']

export default function RecipeBlogForm({ onChange, data }: RecipeBlogFormProps) {
  const update = (field: keyof BlogFormData, value: string | boolean) => {
    onChange({ ...data, [field]: value })
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-xs font-medium text-gray-400 mb-1">Topic *</label>
        <input
          type="text"
          value={data.topic}
          onChange={(e) => update('topic', e.target.value)}
          placeholder="e.g. AI trends in 2026"
          className="input w-full"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Style</label>
          <select
            value={data.style}
            onChange={(e) => update('style', e.target.value)}
            className="input w-full text-sm"
          >
            {STYLE_OPTIONS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Length</label>
          <select
            value={data.length}
            onChange={(e) => update('length', e.target.value)}
            className="input w-full text-sm"
          >
            {LENGTH_OPTIONS.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </div>
      </div>
      <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
        <input
          type="checkbox"
          checked={data.citations}
          onChange={(e) => update('citations', e.target.checked)}
          className="rounded border-dark-border bg-dark-bg text-primary-600 focus:ring-primary-500"
        />
        Include citations
      </label>
    </div>
  )
}
