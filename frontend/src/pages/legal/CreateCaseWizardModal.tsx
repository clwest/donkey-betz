import { useState } from 'react'
import { Loader2, Plus, Scale, Trash2, X } from 'lucide-react'
import { cn } from '@/lib/cn'

const CASE_TYPE_OPTIONS = [
  { value: 'divorce', label: 'Divorce' },
  { value: 'custody', label: 'Child Custody' },
  { value: 'modification', label: 'Modification' },
  { value: 'enforcement', label: 'Enforcement' },
  { value: 'paternity', label: 'Paternity' },
  { value: 'protection_order', label: 'Protection Order' },
  { value: 'other', label: 'Other' },
] as const

interface PartyForm {
  full_name: string
  address: string
  city: string
  state: string
  zip_code: string
  phone: string
  email: string
  is_pro_se: boolean
}

interface ChildForm {
  full_name: string
  date_of_birth: string
}

interface CasePayload {
  case_number: string
  case_type: string
  case_title: string
  county: string
  state: string
  district: string
  division: string
  filing_date: string
  notes: string
  petitioner: PartyForm
  respondent: PartyForm
  children: ChildForm[]
}

interface CreateCaseWizardModalProps {
  open: boolean
  onClose: () => void
  onSubmit: (payload: CasePayload) => Promise<void>
  submitting?: boolean
}

const EMPTY_PARTY: PartyForm = {
  full_name: '',
  address: '',
  city: '',
  state: '',
  zip_code: '',
  phone: '',
  email: '',
  is_pro_se: true,
}

function buildInitialPayload(): CasePayload {
  return {
    case_number: '',
    case_type: 'custody',
    case_title: '',
    county: '',
    state: 'Colorado',
    district: '',
    division: '',
    filing_date: '',
    notes: '',
    petitioner: { ...EMPTY_PARTY },
    respondent: { ...EMPTY_PARTY },
    children: [],
  }
}

function TextInput({
  label, value, onChange, placeholder, required = false, type = 'text',
}: {
  label: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
  required?: boolean
  type?: string
}) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="text-gray-300">
        {label}{required && <span className="text-accent-red ml-1">*</span>}
      </span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="rounded border border-dark-border bg-dark-bg-alt px-3 py-2 text-sm text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none"
      />
    </label>
  )
}

function PartySection({
  title, party, onChange,
}: {
  title: string
  party: PartyForm
  onChange: (patch: Partial<PartyForm>) => void
}) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-200">{title}</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <TextInput
          label="Full name"
          value={party.full_name}
          onChange={(v) => onChange({ full_name: v })}
          required
        />
        <TextInput
          label="Email"
          type="email"
          value={party.email}
          onChange={(v) => onChange({ email: v })}
        />
        <TextInput
          label="Phone"
          value={party.phone}
          onChange={(v) => onChange({ phone: v })}
        />
        <TextInput
          label="Address"
          value={party.address}
          onChange={(v) => onChange({ address: v })}
        />
        <TextInput
          label="City"
          value={party.city}
          onChange={(v) => onChange({ city: v })}
        />
        <div className="grid grid-cols-2 gap-3">
          <TextInput
            label="State"
            value={party.state}
            onChange={(v) => onChange({ state: v })}
          />
          <TextInput
            label="Zip"
            value={party.zip_code}
            onChange={(v) => onChange({ zip_code: v })}
          />
        </div>
      </div>
      <label className="inline-flex items-center gap-2 text-sm text-gray-300">
        <input
          type="checkbox"
          checked={party.is_pro_se}
          onChange={(e) => onChange({ is_pro_se: e.target.checked })}
          className="h-4 w-4"
        />
        Representing self (pro se)
      </label>
    </div>
  )
}

export default function CreateCaseWizardModal({
  open, onClose, onSubmit, submitting = false,
}: CreateCaseWizardModalProps) {
  const [payload, setPayload] = useState<CasePayload>(buildInitialPayload)
  const [error, setError] = useState<string | null>(null)

  if (!open) return null

  const patchPayload = (patch: Partial<CasePayload>) => {
    setPayload((prev) => ({ ...prev, ...patch }))
  }

  const patchParty = (which: 'petitioner' | 'respondent', patch: Partial<PartyForm>) => {
    setPayload((prev) => ({ ...prev, [which]: { ...prev[which], ...patch } }))
  }

  const addChild = () => {
    setPayload((prev) => ({
      ...prev,
      children: [...prev.children, { full_name: '', date_of_birth: '' }],
    }))
  }

  const patchChild = (idx: number, patch: Partial<ChildForm>) => {
    setPayload((prev) => ({
      ...prev,
      children: prev.children.map((c, i) => (i === idx ? { ...c, ...patch } : c)),
    }))
  }

  const removeChild = (idx: number) => {
    setPayload((prev) => ({
      ...prev,
      children: prev.children.filter((_, i) => i !== idx),
    }))
  }

  const handleClose = () => {
    if (submitting) return
    setPayload(buildInitialPayload())
    setError(null)
    onClose()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (submitting) return
    if (!payload.case_number.trim()) {
      setError('Case number is required.')
      return
    }
    if (!payload.county.trim()) {
      setError('County is required.')
      return
    }
    if (!payload.petitioner.full_name.trim()) {
      setError('Petitioner name is required.')
      return
    }
    if (!payload.respondent.full_name.trim()) {
      setError('Respondent name is required.')
      return
    }
    setError(null)
    try {
      await onSubmit(payload)
      setPayload(buildInitialPayload())
    } catch (err) {
      const anyErr = err as { response?: { data?: { error?: string } }; message?: string }
      setError(anyErr?.response?.data?.error || anyErr?.message || 'Failed to create case.')
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
            <Scale size={22} className="text-primary-400" />
            <h2 className="text-lg font-semibold">New Case</h2>
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

        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto">
          <div className="p-6 space-y-6">
            <section className="space-y-3">
              <h3 className="text-sm font-semibold text-gray-200">Case Info</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <TextInput
                  label="Case number"
                  value={payload.case_number}
                  onChange={(v) => patchPayload({ case_number: v })}
                  placeholder="e.g., 2025DR576"
                  required
                />
                <label className="flex flex-col gap-1 text-sm">
                  <span className="text-gray-300">
                    Case type<span className="text-accent-red ml-1">*</span>
                  </span>
                  <select
                    value={payload.case_type}
                    onChange={(e) => patchPayload({ case_type: e.target.value })}
                    className="rounded border border-dark-border bg-dark-bg-alt px-3 py-2 text-sm text-white focus:border-primary-500 focus:outline-none"
                  >
                    {CASE_TYPE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </label>
                <TextInput
                  label="Case title"
                  value={payload.case_title}
                  onChange={(v) => patchPayload({ case_title: v })}
                  placeholder="Optional descriptive title"
                />
                <TextInput
                  label="Filing date"
                  type="date"
                  value={payload.filing_date}
                  onChange={(v) => patchPayload({ filing_date: v })}
                />
                <TextInput
                  label="County"
                  value={payload.county}
                  onChange={(v) => patchPayload({ county: v })}
                  required
                />
                <TextInput
                  label="State"
                  value={payload.state}
                  onChange={(v) => patchPayload({ state: v })}
                />
                <TextInput
                  label="District"
                  value={payload.district}
                  onChange={(v) => patchPayload({ district: v })}
                  placeholder="Judicial district"
                />
                <TextInput
                  label="Division"
                  value={payload.division}
                  onChange={(v) => patchPayload({ division: v })}
                />
              </div>
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-gray-300">Notes</span>
                <textarea
                  value={payload.notes}
                  onChange={(e) => patchPayload({ notes: e.target.value })}
                  rows={3}
                  className="rounded border border-dark-border bg-dark-bg-alt px-3 py-2 text-sm text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none"
                />
              </label>
            </section>

            <div className="border-t border-dark-border" />

            <PartySection
              title="Petitioner"
              party={payload.petitioner}
              onChange={(patch) => patchParty('petitioner', patch)}
            />

            <div className="border-t border-dark-border" />

            <PartySection
              title="Respondent"
              party={payload.respondent}
              onChange={(patch) => patchParty('respondent', patch)}
            />

            <div className="border-t border-dark-border" />

            <section className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-200">Children (optional)</h3>
                <button
                  type="button"
                  onClick={addChild}
                  className="btn btn-secondary text-xs flex items-center gap-1"
                >
                  <Plus size={12} />
                  Add child
                </button>
              </div>
              {payload.children.length === 0 ? (
                <p className="text-xs text-gray-500">No children added.</p>
              ) : (
                <div className="space-y-2">
                  {payload.children.map((child, idx) => (
                    <div key={idx} className="grid grid-cols-[1fr,180px,auto] gap-2 items-end">
                      <TextInput
                        label={idx === 0 ? 'Full name' : ''}
                        value={child.full_name}
                        onChange={(v) => patchChild(idx, { full_name: v })}
                      />
                      <TextInput
                        label={idx === 0 ? 'Date of birth' : ''}
                        type="date"
                        value={child.date_of_birth}
                        onChange={(v) => patchChild(idx, { date_of_birth: v })}
                      />
                      <button
                        type="button"
                        onClick={() => removeChild(idx)}
                        className="text-gray-400 hover:text-accent-red p-2"
                        aria-label="Remove child"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {error && (
              <div className="rounded border border-accent-red/40 bg-accent-red/10 px-3 py-2 text-sm text-accent-red">
                {error}
              </div>
            )}
          </div>

          <div className="flex items-center justify-end gap-3 p-4 border-t border-dark-border flex-shrink-0">
            <button
              type="button"
              onClick={handleClose}
              disabled={submitting}
              className="btn btn-secondary text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="btn btn-primary text-sm flex items-center gap-2"
            >
              {submitting ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Creating…
                </>
              ) : (
                'Create case'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
