import { useState } from 'react'
import { AlertCircle, HelpCircle, Lightbulb, Loader2, Sparkles, X } from 'lucide-react'
import { cn } from '@/lib/cn'
import { legalApi } from '@/lib/api'

interface FormRecommendation {
  relief_type: string
  form_number: string
  official_title: string
  required_attachments: string[]
  criteria: string
  filing_notes: string
  score: number
}

interface FormRecommendationResponse {
  success: boolean
  situation?: string
  top_match: FormRecommendation | null
  alternates: FormRecommendation[]
  confidence: 'high' | 'medium' | 'low' | 'none'
  clarifying_questions: string[]
  disclaimer: string
  error?: string
}

interface FormPickerModalProps {
  open: boolean
  onClose: () => void
}

const CONFIDENCE_BADGE = {
  high: 'bg-accent-green/20 text-accent-green border-accent-green/40',
  medium: 'bg-accent-amber/20 text-accent-amber border-accent-amber/40',
  low: 'bg-accent-amber/20 text-accent-amber border-accent-amber/40',
  none: 'bg-accent-red/20 text-accent-red border-accent-red/40',
} as const

function RecommendationCard({ rec, label }: { rec: FormRecommendation; label: string }) {
  return (
    <div className="rounded-lg border border-dark-border p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
          <p className="text-lg font-semibold text-primary-400">{rec.form_number}</p>
          <p className="text-sm text-gray-200 mt-1">{rec.official_title}</p>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg-alt text-gray-400 border border-dark-border">
          {rec.relief_type}
        </span>
      </div>
      {rec.criteria && (
        <div>
          <p className="text-xs font-semibold text-gray-400 mb-1">Criteria</p>
          <p className="text-sm text-gray-300">{rec.criteria}</p>
        </div>
      )}
      {rec.required_attachments.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-400 mb-1">Required attachments</p>
          <ul className="text-sm text-gray-300 list-disc list-inside space-y-0.5">
            {rec.required_attachments.map((a) => (
              <li key={a}>{a}</li>
            ))}
          </ul>
        </div>
      )}
      {rec.filing_notes && (
        <div>
          <p className="text-xs font-semibold text-gray-400 mb-1">Filing notes</p>
          <p className="text-sm text-gray-300">{rec.filing_notes}</p>
        </div>
      )}
    </div>
  )
}

export default function FormPickerModal({ open, onClose }: FormPickerModalProps) {
  const [situation, setSituation] = useState('')
  const [caseType, setCaseType] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<FormRecommendationResponse | null>(null)

  if (!open) return null

  const handleClose = () => {
    if (submitting) return
    setSituation('')
    setCaseType('')
    setError(null)
    setResult(null)
    onClose()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (submitting) return
    if (!situation.trim()) {
      setError('Describe the situation before submitting.')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      const resp = await legalApi.selectForm({
        situation: situation.trim(),
        case_type: caseType.trim() || undefined,
      })
      setResult(resp.data as FormRecommendationResponse)
    } catch (err) {
      const anyErr = err as { response?: { data?: { error?: string } }; message?: string }
      setError(
        anyErr?.response?.data?.error ||
        anyErr?.message ||
        'Failed to look up form recommendation.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={handleClose}
    >
      <div
        className="w-full max-w-3xl max-h-[90vh] rounded-lg border border-dark-border bg-dark-bg shadow-xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-6 border-b border-dark-border flex-shrink-0">
          <div className="flex items-center gap-3">
            <Sparkles size={22} className="text-primary-400" />
            <h2 className="text-lg font-semibold">Pick the right JDF form</h2>
          </div>
          <button
            onClick={handleClose}
            disabled={submitting}
            className={cn(
              'text-gray-400 hover:text-white',
              submitting && 'opacity-50 cursor-not-allowed'
            )}
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          <form onSubmit={handleSubmit} className="p-6 space-y-4 border-b border-dark-border">
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-gray-300">
                Describe your situation
                <span className="text-accent-red ml-1">*</span>
              </span>
              <textarea
                value={situation}
                onChange={(e) => setSituation(e.target.value)}
                rows={4}
                placeholder='e.g., "The other parent moved to Denver with our kids and changed the schedule without telling me."'
                className="rounded border border-dark-border bg-dark-bg-alt px-3 py-2 text-sm text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none"
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-gray-300">Case type (optional)</span>
              <input
                type="text"
                value={caseType}
                onChange={(e) => setCaseType(e.target.value)}
                placeholder="custody / divorce / modification"
                className="rounded border border-dark-border bg-dark-bg-alt px-3 py-2 text-sm text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none"
              />
            </label>

            {error && (
              <div className="rounded border border-accent-red/40 bg-accent-red/10 px-3 py-2 text-sm text-accent-red flex items-start gap-2">
                <AlertCircle size={14} className="mt-0.5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => {
                  setSituation('')
                  setResult(null)
                  setError(null)
                }}
                disabled={submitting}
                className="btn btn-secondary text-sm"
              >
                Clear
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="btn btn-primary text-sm flex items-center gap-2"
              >
                {submitting ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    Looking up…
                  </>
                ) : (
                  'Recommend a form'
                )}
              </button>
            </div>
          </form>

          {result && (
            <div className="p-6 space-y-4">
              <div className="flex items-center gap-2">
                <span className={cn(
                  'text-xs px-2 py-1 rounded border font-medium uppercase tracking-wide',
                  CONFIDENCE_BADGE[result.confidence]
                )}>
                  {result.confidence} confidence
                </span>
                {result.top_match && (
                  <span className="text-xs text-gray-500">
                    match score {result.top_match.score}
                  </span>
                )}
              </div>

              {result.top_match ? (
                <RecommendationCard rec={result.top_match} label="Top match" />
              ) : (
                <div className="rounded border border-accent-amber/40 bg-accent-amber/10 px-4 py-3 text-sm text-accent-amber flex items-start gap-2">
                  <HelpCircle size={16} className="mt-0.5 flex-shrink-0" />
                  <span>
                    No keyword match found. Try describing the situation with more
                    specifics, or contact your local court's self-help center for guidance.
                  </span>
                </div>
              )}

              {result.alternates.length > 0 && (
                <div className="space-y-3">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                    Also consider
                  </p>
                  {result.alternates.map((alt, idx) => (
                    <RecommendationCard
                      key={alt.relief_type}
                      rec={alt}
                      label={`Alternate #${idx + 1}`}
                    />
                  ))}
                </div>
              )}

              {result.clarifying_questions.length > 0 && (
                <div className="rounded border border-primary-500/40 bg-primary-500/10 px-4 py-3 space-y-2">
                  <div className="flex items-center gap-2 text-sm font-semibold text-primary-400">
                    <Lightbulb size={14} />
                    Clarifying questions to narrow this down
                  </div>
                  <ul className="text-sm text-gray-200 list-disc list-inside space-y-1">
                    {result.clarifying_questions.map((q) => (
                      <li key={q}>{q}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.disclaimer && (
                <p className="text-xs text-gray-500 italic border-t border-dark-border pt-3">
                  {result.disclaimer}
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
