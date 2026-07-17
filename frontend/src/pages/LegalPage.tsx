import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { legalApi } from '@/lib/api'
import {
  Scale, FileText, Upload, FolderOpen,
  Loader2, CheckCircle, XCircle, Plus,
  Gavel, ChevronRight, Network, AlertTriangle,
  Sparkles, X, Copy, Eye
} from 'lucide-react'
import { cn } from '@/lib/cn'
import CreateCaseWizardModal from './legal/CreateCaseWizardModal'
import FormPickerModal from './legal/FormPickerModal'

type TabType = 'overview' | 'documents' | 'cases' | 'litigation'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface LegalDocument {
  id: string
  title: string
  file_name?: string
  document_type?: string
  status?: string
  uploaded_at?: string
  created_at?: string
}

interface LegalCase {
  id: string
  case_number: string
  case_type?: string
  case_type_display?: string
  case_title?: string
  county?: string
  state?: string
  status?: string
  status_display?: string
  petitioner_name?: string
  respondent_name?: string
  children_count?: number
  documents_count?: number
  created_at?: string
  updated_at?: string
  // Legacy fields still referenced elsewhere (Litigation/Overview active-case cards)
  title?: string
  name?: string
  children?: unknown[]
  documents?: unknown[]
}

const tabs = [
  { id: 'overview' as TabType, label: 'Overview', icon: Scale },
  { id: 'documents' as TabType, label: 'Documents', icon: FileText },
  { id: 'cases' as TabType, label: 'Cases', icon: FolderOpen },
  { id: 'litigation' as TabType, label: 'Litigation', icon: Network },
]

function Toast({ result, onClose }: { result: ActionResult; onClose: () => void }) {
  return (
    <div className={cn(
      'fixed bottom-4 right-4 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg animate-in slide-in-from-bottom-4 z-50',
      result.type === 'success' ? 'bg-accent-green/20 text-accent-green border border-accent-green/30' : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
    )}>
      {result.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
      <span className="text-sm">{result.message}</span>
      <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">&times;</button>
    </div>
  )
}

interface DraftStatus {
  status: 'dispatched' | 'completed' | 'failed'
  celery_state?: string
  error_message?: string | null
  document_id?: string | null
}

interface LegalDocumentDetail {
  id: string
  title: string
  document_type?: string
  content: string
  original_query?: string
  generation_context?: Record<string, unknown>
  status?: string
  word_count?: number
  created_at?: string
}

export default function LegalPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [draftModalOpen, setDraftModalOpen] = useState(false)
  const [draftTaskDescription, setDraftTaskDescription] = useState('')
  const [draftAckChecked, setDraftAckChecked] = useState(false)
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null)
  const [draftStatus, setDraftStatus] = useState<DraftStatus | null>(null)
  const [viewingDocId, setViewingDocId] = useState<string | null>(null)
  const [caseWizardOpen, setCaseWizardOpen] = useState(false)
  const [creatingCase, setCreatingCase] = useState(false)
  const [formPickerOpen, setFormPickerOpen] = useState(false)
  const queryClient = useQueryClient()

  // Fetch documents (case files)
  const { data: documentsData, isLoading: loadingDocuments } = useQuery({
    queryKey: ['legal-documents'],
    queryFn: () => legalApi.documents(),
  })

  // Fetch cases
  const { data: casesData, isLoading: loadingCases } = useQuery({
    queryKey: ['legal-cases'],
    queryFn: () => legalApi.cases(),
  })

  // Fetch active case
  const { data: activeCaseData } = useQuery({
    queryKey: ['legal-active-case'],
    queryFn: () => legalApi.activeCase(),
  })

  // Analyze document mutation
  const analyzeMutation = useMutation({
    mutationFn: (docId: string) => legalApi.analyzeDocument(docId),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Document analysis started!' })
      queryClient.invalidateQueries({ queryKey: ['legal-documents'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Analysis failed.' })
    },
  })

  // S2806 Phase 3.2 — create case then set-active in one flow
  const handleCreateCase = async (payload: Record<string, unknown>) => {
    setCreatingCase(true)
    try {
      const createResp = await legalApi.createCase(payload)
      const newCaseId: string | undefined = createResp.data?.case_id
      // Refresh the cases list regardless of set-active outcome
      queryClient.invalidateQueries({ queryKey: ['legal-cases'] })
      if (newCaseId) {
        try {
          await legalApi.setActiveCase(newCaseId)
          queryClient.invalidateQueries({ queryKey: ['legal-active-case'] })
          setActionResult({
            type: 'success',
            message: `Case ${createResp.data?.case_number || ''} created and set active.`.trim(),
          })
        } catch {
          // Case was created; only the set-active step failed. Recoverable.
          setActionResult({
            type: 'error',
            message: 'Case created — could not set as active. Select the case from the list to activate it.',
          })
        }
      } else {
        setActionResult({ type: 'success', message: 'Case created.' })
      }
      setCaseWizardOpen(false)
    } finally {
      setCreatingCase(false)
    }
  }

  // S2804 Phase 3.1a — document detail query (fires only when a row is selected)
  const { data: viewingDocData, isLoading: loadingViewingDoc } = useQuery({
    queryKey: ['legal-document-detail', viewingDocId],
    queryFn: () => legalApi.documentDetail(viewingDocId as string),
    enabled: !!viewingDocId,
  })
  const viewingDoc: LegalDocumentDetail | null = viewingDocData?.data?.document || null

  // S2803 Phase 3.0 — draft dispatch mutation
  const draftMutation = useMutation({
    mutationFn: (payload: { task_description: string; disclaimer_acknowledged: boolean }) =>
      legalApi.draftMotion(payload),
    onSuccess: (resp) => {
      const taskId = resp.data?.task_id
      if (taskId) {
        setActiveTaskId(taskId)
        setDraftStatus({ status: 'dispatched', celery_state: 'PENDING' })
      }
    },
    onError: (err: unknown) => {
      const anyErr = err as { response?: { data?: { error?: string; error_code?: string } } }
      const msg = anyErr?.response?.data?.error || 'Draft dispatch failed'
      setActionResult({ type: 'error', message: msg })
    },
  })

  // S2803 Phase 3.0 — poll draft status every 5s until terminal
  useEffect(() => {
    if (!activeTaskId) return
    if (draftStatus?.status === 'completed' || draftStatus?.status === 'failed') return

    let cancelled = false
    const poll = async () => {
      try {
        const resp = await legalApi.draftStatus(activeTaskId)
        if (cancelled) return
        const data = resp.data as DraftStatus
        setDraftStatus(data)
        if (data.status === 'completed') {
          setActionResult({ type: 'success', message: 'Draft ready! See Documents tab.' })
          queryClient.invalidateQueries({ queryKey: ['legal-documents'] })
        } else if (data.status === 'failed') {
          setActionResult({
            type: 'error',
            message: `Drafting failed: ${data.error_message || 'unknown error'}`,
          })
        }
      } catch {
        // transient — keep polling
      }
    }

    poll()
    const interval = setInterval(poll, 5000)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [activeTaskId, draftStatus?.status, queryClient])

  const documents: LegalDocument[] = documentsData?.data?.documents || documentsData?.data || []
  const cases: LegalCase[] = casesData?.data?.cases || casesData?.data || []
  const activeCase = activeCaseData?.data

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  const openDraftModal = () => {
    setDraftTaskDescription('')
    setDraftAckChecked(false)
    setActiveTaskId(null)
    setDraftStatus(null)
    setDraftModalOpen(true)
  }

  const submitDraft = () => {
    if (!draftTaskDescription.trim() || !draftAckChecked) return
    draftMutation.mutate({
      task_description: draftTaskDescription.trim(),
      disclaimer_acknowledged: true,
    })
  }

  return (
    <div className="space-y-6">
      {/* S2803 Phase 3.0 — non-dismissable legal disclaimer banner (Rigby SIGN Fold 3 mandatory floor) */}
      <div className="flex items-start gap-3 rounded-lg border border-accent-amber/40 bg-accent-amber/10 px-4 py-3">
        <AlertTriangle size={20} className="text-accent-amber flex-shrink-0 mt-0.5" />
        <div className="text-sm text-accent-amber">
          <p className="font-semibold">This tool provides general legal information, not legal advice.</p>
          <p className="text-accent-amber/90 mt-1">
            It does not create an attorney-client relationship. Consult a licensed Colorado attorney
            for advice on specific legal matters. Generated documents are templates that require your
            review before filing.
          </p>
        </div>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-lg bg-accent-amber/20 flex items-center justify-center">
            <Scale size={28} className="text-accent-amber" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Legal Assistant</h1>
            <p className="text-gray-400">AI-powered legal document analysis and case management</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            className="btn btn-primary flex items-center gap-2"
            onClick={openDraftModal}
          >
            <Sparkles size={16} />
            Draft New Motion
          </button>
          <button
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => setFormPickerOpen(true)}
          >
            <Sparkles size={16} />
            Pick a Form
          </button>
          <button
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => setActionResult({ type: 'success', message: 'Upload dialog coming soon!' })}
          >
            <Upload size={16} />
            Upload Document
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2 overflow-x-auto">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap',
              activeTab === id
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-bg'
            )}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center gap-3">
                <FileText className="text-primary-400" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Documents</p>
                  <p className="text-2xl font-bold">{documents.length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <FolderOpen className="text-accent-green" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Cases</p>
                  <p className="text-2xl font-bold">{cases.length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Gavel className="text-accent-amber" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Active Case</p>
                  <p className="text-lg font-bold truncate">{activeCase?.name || 'None'}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Network className="text-accent-cyan" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Litigation Docs</p>
                  <p className="text-2xl font-bold">{activeCase?.documents?.length || 0}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Documents & Cases */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Recent Documents */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Recent Documents</h3>
              {loadingDocuments ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="animate-spin" size={24} />
                </div>
              ) : documents.length > 0 ? (
                <div className="space-y-3">
                  {documents.slice(0, 5).map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                      onClick={() => setViewingDocId(doc.id)}
                    >
                      <div className="flex items-center gap-3">
                        <FileText size={18} className="text-primary-400" />
                        <div>
                          <p className="font-medium text-sm">{doc.title || doc.file_name || 'Untitled'}</p>
                          <p className="text-xs text-gray-500">{doc.document_type || 'Document'}</p>
                        </div>
                      </div>
                      <span className={cn(
                        'text-xs px-2 py-1 rounded',
                        doc.status === 'analyzed' ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-amber/20 text-accent-amber'
                      )}>
                        {doc.status || 'pending'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <FileText className="mx-auto mb-2" size={32} />
                  <p>No documents yet</p>
                </div>
              )}
            </div>

            {/* Cases */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Case Profiles</h3>
              {loadingCases ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="animate-spin" size={24} />
                </div>
              ) : cases.length > 0 ? (
                <div className="space-y-3">
                  {cases.slice(0, 5).map((legalCase) => (
                    <div
                      key={legalCase.id}
                      className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center gap-3">
                        <Gavel size={18} className="text-accent-amber" />
                        <div>
                          <p className="font-medium text-sm">
                            {legalCase.case_title || legalCase.case_number || 'Untitled Case'}
                          </p>
                          <p className="text-xs text-gray-500">
                            {legalCase.case_type_display || legalCase.case_type || 'Case'}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm">{legalCase.documents_count ?? 0} docs</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <FolderOpen className="mx-auto mb-2" size={32} />
                  <p>No cases created</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Documents Tab */}
      {activeTab === 'documents' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Case Files</h3>
            <button
              className="btn btn-primary text-sm flex items-center gap-2"
              onClick={() => setActionResult({ type: 'success', message: 'Upload dialog coming soon!' })}
            >
              <Plus size={14} />
              Upload
            </button>
          </div>
          {loadingDocuments ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : documents.length > 0 ? (
            <div className="space-y-3">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                  onClick={() => setViewingDocId(doc.id)}
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-lg bg-primary-600/20 flex items-center justify-center">
                      <FileText size={20} className="text-primary-400" />
                    </div>
                    <div>
                      <p className="font-medium">{doc.title || doc.file_name || 'Untitled'}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">{doc.document_type || 'Document'}</span>
                        <span className="text-xs text-gray-500">
                          {doc.uploaded_at || doc.created_at ? new Date(doc.uploaded_at || doc.created_at || '').toLocaleDateString() : ''}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'text-xs px-2 py-1 rounded',
                      doc.status === 'analyzed' ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-amber/20 text-accent-amber'
                    )}>
                      {doc.status || 'pending'}
                    </span>
                    <button
                      className="btn btn-secondary text-sm"
                      onClick={(e) => { e.stopPropagation(); setViewingDocId(doc.id) }}
                    >
                      <Eye size={14} className="mr-1 inline" />
                      View
                    </button>
                    <button
                      className="btn btn-secondary text-sm"
                      onClick={(e) => { e.stopPropagation(); analyzeMutation.mutate(doc.id) }}
                      disabled={analyzeMutation.isPending}
                    >
                      {analyzeMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : 'Analyze'}
                    </button>
                    <ChevronRight size={16} className="text-gray-500" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <FileText className="mx-auto mb-2" size={48} />
              <p>No documents uploaded</p>
              <p className="text-sm text-gray-500 mt-1">Upload your first legal document to get started</p>
            </div>
          )}
        </div>
      )}

      {/* Cases Tab */}
      {activeTab === 'cases' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Case Profiles</h3>
            <button
              className="btn btn-primary text-sm flex items-center gap-2"
              onClick={() => setCaseWizardOpen(true)}
            >
              <Plus size={14} />
              New Case
            </button>
          </div>
          {loadingCases ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : cases.length > 0 ? (
            <div className="space-y-3">
              {cases.map((legalCase) => (
                <div
                  key={legalCase.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-lg bg-accent-amber/20 flex items-center justify-center">
                      <Gavel size={20} className="text-accent-amber" />
                    </div>
                    <div>
                      <p className="font-medium">
                        {legalCase.case_title || legalCase.case_number || 'Untitled Case'}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">
                          {legalCase.case_type_display || legalCase.case_type || 'Case'}
                        </span>
                        {legalCase.county && (
                          <span className="text-xs text-gray-500">
                            {legalCase.county}, {legalCase.state || 'CO'}
                          </span>
                        )}
                        <span className="text-xs text-gray-500">
                          {legalCase.documents_count ?? 0} documents
                        </span>
                        <span className="text-xs text-gray-500">
                          {legalCase.children_count ?? 0} children
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <ChevronRight size={16} className="text-gray-500" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <FolderOpen className="mx-auto mb-2" size={48} />
              <p>No cases created</p>
              <p className="text-sm text-gray-500 mt-1">Create your first case to organize your legal work</p>
            </div>
          )}
        </div>
      )}

      {/* Litigation Tab */}
      {activeTab === 'litigation' && (
        <div className="space-y-6">
          {activeCase ? (
            <>
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Active Case: {activeCase.name}</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 rounded-lg bg-dark-bg">
                    <p className="text-sm text-gray-400">Documents</p>
                    <p className="text-xl font-bold">{activeCase.documents?.length || 0}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-dark-bg">
                    <p className="text-sm text-gray-400">Children</p>
                    <p className="text-xl font-bold">{activeCase.children?.length || 0}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-dark-bg">
                    <p className="text-sm text-gray-400">Case Type</p>
                    <p className="text-xl font-bold">{activeCase.case_type || 'N/A'}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-dark-bg">
                    <p className="text-sm text-gray-400">Status</p>
                    <p className="text-xl font-bold">{activeCase.status || 'Active'}</p>
                  </div>
                </div>
              </div>
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Knowledge Graph</h3>
                <p className="text-gray-400">View and manage the case knowledge graph for enhanced litigation support.</p>
                <button
                  className="btn btn-primary mt-4"
                  onClick={() => setActionResult({ type: 'success', message: 'Knowledge graph view coming soon!' })}
                >
                  <Network size={16} className="mr-2" />
                  View Knowledge Graph
                </button>
              </div>
            </>
          ) : (
            <div className="card text-center py-12">
              <Network className="mx-auto mb-4 text-gray-400" size={48} />
              <h3 className="text-lg font-semibold mb-2">No Active Case</h3>
              <p className="text-gray-400">Select a case from the Cases tab to access litigation features.</p>
            </div>
          )}
        </div>
      )}

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}

      {/* S2804 Phase 3.1a — View Document modal */}
      {viewingDocId && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          onClick={() => setViewingDocId(null)}
        >
          <div
            className="w-full max-w-3xl max-h-[90vh] rounded-lg border border-dark-border bg-dark-bg shadow-xl flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between p-6 border-b border-dark-border flex-shrink-0">
              <div className="flex items-center gap-3">
                <FileText size={22} className="text-primary-400" />
                <div>
                  <h2 className="text-lg font-semibold">
                    {viewingDoc?.title || (loadingViewingDoc ? 'Loading…' : 'Document')}
                  </h2>
                  {viewingDoc && (
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <span className="text-xs px-2 py-0.5 rounded bg-dark-bg-alt text-gray-400 border border-dark-border">
                        {viewingDoc.document_type || 'document'}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded bg-dark-bg-alt text-gray-400 border border-dark-border">
                        {viewingDoc.status || 'draft'}
                      </span>
                      {viewingDoc.word_count !== undefined && (
                        <span className="text-xs text-gray-500">{viewingDoc.word_count} words</span>
                      )}
                      {viewingDoc.created_at && (
                        <span className="text-xs text-gray-500">
                          {new Date(viewingDoc.created_at).toLocaleString()}
                        </span>
                      )}
                      {(viewingDoc.generation_context as { phase3_1_fallback_used?: boolean } | undefined)?.phase3_1_fallback_used && (
                        <span className="text-xs px-2 py-0.5 rounded bg-accent-amber/20 text-accent-amber border border-accent-amber/40">
                          Auto-recovered draft
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
              <button
                onClick={() => setViewingDocId(null)}
                className="text-gray-400 hover:text-white flex-shrink-0"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-6 overflow-y-auto flex-1">
              {loadingViewingDoc ? (
                <div className="flex items-center justify-center py-16">
                  <Loader2 size={32} className="animate-spin text-gray-500" />
                </div>
              ) : viewingDoc?.content ? (
                <pre className="whitespace-pre-wrap font-sans text-sm text-gray-200 leading-relaxed">
                  {viewingDoc.content}
                </pre>
              ) : (
                <p className="text-gray-400 text-center py-16">No content available.</p>
              )}
            </div>

            {viewingDoc?.content && (
              <div className="flex items-center justify-between p-4 border-t border-dark-border flex-shrink-0">
                <p className="text-xs text-gray-500">
                  Review before filing. Generated documents are templates.
                </p>
                <button
                  className="btn btn-secondary text-sm flex items-center gap-2"
                  onClick={async () => {
                    try {
                      await navigator.clipboard.writeText(viewingDoc.content)
                      setActionResult({ type: 'success', message: 'Copied to clipboard.' })
                    } catch {
                      setActionResult({ type: 'error', message: 'Copy failed.' })
                    }
                  }}
                >
                  <Copy size={14} />
                  Copy
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* S2803 Phase 3.0 — Draft Motion modal */}
      {draftModalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          onClick={() => !activeTaskId && setDraftModalOpen(false)}
        >
          <div
            className="w-full max-w-2xl rounded-lg border border-dark-border bg-dark-bg p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Sparkles size={22} className="text-accent-amber" />
                <h2 className="text-lg font-semibold">Draft a Legal Document</h2>
              </div>
              {!activeTaskId && (
                <button
                  onClick={() => setDraftModalOpen(false)}
                  className="text-gray-400 hover:text-white"
                >
                  <X size={20} />
                </button>
              )}
            </div>

            {!activeTaskId && (
              <>
                <label className="block text-sm text-gray-300 mb-2">
                  Describe what you need drafted (motion type, key facts, requested relief)
                </label>
                <textarea
                  value={draftTaskDescription}
                  onChange={(e) => setDraftTaskDescription(e.target.value)}
                  placeholder="e.g. Draft a Motion to Modify Parenting Time based on a schedule change. Current order is 18 months old. Requested new schedule: alternating full weeks."
                  className="w-full h-40 rounded-lg border border-dark-border bg-black/40 p-3 text-sm text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none"
                  autoFocus
                />

                <label className="flex items-start gap-2 mt-4 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={draftAckChecked}
                    onChange={(e) => setDraftAckChecked(e.target.checked)}
                    className="mt-1"
                  />
                  <span className="text-sm text-gray-300">
                    I understand this is <strong>general legal information, not legal advice</strong>.
                    I will review the generated draft with a licensed attorney before filing.
                  </span>
                </label>

                <div className="flex items-center justify-end gap-2 mt-6">
                  <button
                    className="btn btn-secondary"
                    onClick={() => setDraftModalOpen(false)}
                  >
                    Cancel
                  </button>
                  <button
                    className="btn btn-primary flex items-center gap-2"
                    disabled={
                      !draftTaskDescription.trim() ||
                      !draftAckChecked ||
                      draftMutation.isPending
                    }
                    onClick={submitDraft}
                  >
                    {draftMutation.isPending ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <Sparkles size={16} />
                    )}
                    Draft
                  </button>
                </div>
              </>
            )}

            {activeTaskId && draftStatus?.status !== 'completed' && draftStatus?.status !== 'failed' && (
              <div className="flex flex-col items-center py-8 gap-4">
                <Loader2 size={32} className="animate-spin text-accent-amber" />
                <div className="text-center">
                  <p className="font-medium">Drafting your document…</p>
                  <p className="text-sm text-gray-400 mt-1">
                    This typically takes 1–3 minutes.
                    {draftStatus?.celery_state && ` (${draftStatus.celery_state})`}
                  </p>
                </div>
              </div>
            )}

            {draftStatus?.status === 'completed' && (
              <div className="flex flex-col items-center py-8 gap-4">
                <CheckCircle size={32} className="text-accent-green" />
                <div className="text-center">
                  <p className="font-medium text-accent-green">Draft ready!</p>
                  <p className="text-sm text-gray-400 mt-1">
                    Find it in the Documents tab. Review before filing.
                  </p>
                </div>
                <button
                  className="btn btn-primary"
                  onClick={() => {
                    setDraftModalOpen(false)
                    setActiveTab('documents')
                  }}
                >
                  View Documents
                </button>
              </div>
            )}

            {draftStatus?.status === 'failed' && (
              <div className="flex flex-col items-center py-8 gap-4">
                <XCircle size={32} className="text-accent-red" />
                <div className="text-center">
                  <p className="font-medium text-accent-red">Drafting failed</p>
                  <p className="text-sm text-gray-400 mt-1 max-w-md">
                    {draftStatus.error_message || 'Unknown error — try again.'}
                  </p>
                </div>
                <button
                  className="btn btn-secondary"
                  onClick={() => setDraftModalOpen(false)}
                >
                  Close
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* S2806 Phase 3.2 — Create Case wizard modal */}
      <CreateCaseWizardModal
        open={caseWizardOpen}
        onClose={() => setCaseWizardOpen(false)}
        onSubmit={handleCreateCase}
        submitting={creatingCase}
      />

      {/* S2808 Phase 4a — Form-selection modal */}
      <FormPickerModal
        open={formPickerOpen}
        onClose={() => setFormPickerOpen(false)}
      />
    </div>
  )
}
