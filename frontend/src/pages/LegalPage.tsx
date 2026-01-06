import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { legalApi } from '@/lib/api'
import {
  Scale, FileText, Search, Upload, FolderOpen,
  Loader2, CheckCircle, XCircle, Plus,
  BookOpen, Gavel, FileSearch, ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'overview' | 'documents' | 'cases' | 'research' | 'templates'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface LegalDocument {
  id: string
  title: string
  type: string
  status: 'pending' | 'analyzed' | 'reviewed'
  uploaded_at: string
  analysis_summary?: string
}

interface LegalCase {
  id: string
  title: string
  case_type: string
  status: 'open' | 'closed' | 'pending'
  created_at: string
  documents_count: number
}

interface LegalTemplate {
  id: string
  name: string
  category: string
  description: string
  uses: number
}

const tabs = [
  { id: 'overview' as TabType, label: 'Overview', icon: Scale },
  { id: 'documents' as TabType, label: 'Documents', icon: FileText },
  { id: 'cases' as TabType, label: 'Cases', icon: FolderOpen },
  { id: 'research' as TabType, label: 'Research', icon: Search },
  { id: 'templates' as TabType, label: 'Templates', icon: BookOpen },
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

export default function LegalPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const queryClient = useQueryClient()

  // Fetch stats
  const { data: statsData } = useQuery({
    queryKey: ['legal-stats'],
    queryFn: () => legalApi.stats(),
  })

  // Fetch documents
  const { data: documentsData, isLoading: loadingDocuments } = useQuery({
    queryKey: ['legal-documents'],
    queryFn: () => legalApi.documents(),
    enabled: activeTab === 'documents' || activeTab === 'overview',
  })

  // Fetch cases
  const { data: casesData, isLoading: loadingCases } = useQuery({
    queryKey: ['legal-cases'],
    queryFn: () => legalApi.cases(),
    enabled: activeTab === 'cases' || activeTab === 'overview',
  })

  // Fetch templates
  const { data: templatesData, isLoading: loadingTemplates } = useQuery({
    queryKey: ['legal-templates'],
    queryFn: () => legalApi.templates(),
    enabled: activeTab === 'templates',
  })

  // Research mutation
  const researchMutation = useMutation({
    mutationFn: (query: string) => legalApi.research(query),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Research completed! Check results below.' })
      queryClient.invalidateQueries({ queryKey: ['legal-research'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Research failed. Please try again.' })
    },
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

  const stats = statsData?.data || {}
  const documents: LegalDocument[] = documentsData?.data?.documents || documentsData?.data || []
  const cases: LegalCase[] = casesData?.data?.cases || casesData?.data || []
  const templates: LegalTemplate[] = templatesData?.data?.templates || templatesData?.data || []

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  const handleResearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      researchMutation.mutate(searchQuery)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-lg bg-accent-amber/20 flex items-center justify-center">
            <Scale size={28} className="text-accent-amber" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Legal Assistant</h1>
            <p className="text-gray-400">AI-powered legal research and document analysis</p>
          </div>
        </div>
        <button
          className="btn btn-primary flex items-center gap-2"
          onClick={() => setActionResult({ type: 'success', message: 'Upload dialog coming soon!' })}
        >
          <Upload size={16} />
          Upload Document
        </button>
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
                  <p className="text-2xl font-bold">{stats.total_documents || documents.length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <FolderOpen className="text-accent-green" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Active Cases</p>
                  <p className="text-2xl font-bold">{stats.active_cases || cases.filter(c => c.status === 'open').length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <FileSearch className="text-accent-amber" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Pending Analysis</p>
                  <p className="text-2xl font-bold">{stats.pending_analysis || documents.filter(d => d.status === 'pending').length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Search className="text-accent-cyan" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Researches</p>
                  <p className="text-2xl font-bold">{stats.total_researches || 0}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Research */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Quick Legal Research</h3>
            <form onSubmit={handleResearch} className="flex gap-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter your legal question or search term..."
                className="flex-1 bg-dark-bg border border-dark-border rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
              />
              <button
                type="submit"
                className="btn btn-primary flex items-center gap-2"
                disabled={researchMutation.isPending}
              >
                {researchMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
                Research
              </button>
            </form>
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
                    >
                      <div className="flex items-center gap-3">
                        <FileText size={18} className="text-primary-400" />
                        <div>
                          <p className="font-medium text-sm">{doc.title}</p>
                          <p className="text-xs text-gray-500">{doc.type}</p>
                        </div>
                      </div>
                      <span className={cn(
                        'text-xs px-2 py-1 rounded',
                        doc.status === 'analyzed' ? 'bg-accent-green/20 text-accent-green' :
                        doc.status === 'reviewed' ? 'bg-accent-cyan/20 text-accent-cyan' : 'bg-accent-amber/20 text-accent-amber'
                      )}>
                        {doc.status}
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

            {/* Recent Cases */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Active Cases</h3>
              {loadingCases ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="animate-spin" size={24} />
                </div>
              ) : cases.length > 0 ? (
                <div className="space-y-3">
                  {cases.filter(c => c.status === 'open').slice(0, 5).map((legalCase) => (
                    <div
                      key={legalCase.id}
                      className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center gap-3">
                        <Gavel size={18} className="text-accent-amber" />
                        <div>
                          <p className="font-medium text-sm">{legalCase.title}</p>
                          <p className="text-xs text-gray-500">{legalCase.case_type}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm">{legalCase.documents_count} docs</p>
                        <p className="text-xs text-gray-500">{new Date(legalCase.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <FolderOpen className="mx-auto mb-2" size={32} />
                  <p>No active cases</p>
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
            <h3 className="text-lg font-semibold">Legal Documents</h3>
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
                  className="flex items-center justify-between p-4 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className={cn(
                      'h-10 w-10 rounded-lg flex items-center justify-center',
                      doc.status === 'analyzed' ? 'bg-accent-green/20' :
                      doc.status === 'reviewed' ? 'bg-accent-cyan/20' : 'bg-accent-amber/20'
                    )}>
                      <FileText size={20} className={
                        doc.status === 'analyzed' ? 'text-accent-green' :
                        doc.status === 'reviewed' ? 'text-accent-cyan' : 'text-accent-amber'
                      } />
                    </div>
                    <div>
                      <p className="font-medium">{doc.title}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">{doc.type}</span>
                        <span className="text-xs text-gray-500">{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'text-xs px-2 py-1 rounded',
                      doc.status === 'analyzed' ? 'bg-accent-green/20 text-accent-green' :
                      doc.status === 'reviewed' ? 'bg-accent-cyan/20 text-accent-cyan' : 'bg-accent-amber/20 text-accent-amber'
                    )}>
                      {doc.status}
                    </span>
                    {doc.status === 'pending' && (
                      <button
                        className="btn btn-secondary text-sm"
                        onClick={() => analyzeMutation.mutate(doc.id)}
                        disabled={analyzeMutation.isPending}
                      >
                        {analyzeMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : 'Analyze'}
                      </button>
                    )}
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
            <h3 className="text-lg font-semibold">Legal Cases</h3>
            <button
              className="btn btn-primary text-sm flex items-center gap-2"
              onClick={() => setActionResult({ type: 'success', message: 'Create case coming soon!' })}
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
                    <div className={cn(
                      'h-10 w-10 rounded-lg flex items-center justify-center',
                      legalCase.status === 'open' ? 'bg-accent-green/20' :
                      legalCase.status === 'closed' ? 'bg-gray-500/20' : 'bg-accent-amber/20'
                    )}>
                      <Gavel size={20} className={
                        legalCase.status === 'open' ? 'text-accent-green' :
                        legalCase.status === 'closed' ? 'text-gray-400' : 'text-accent-amber'
                      } />
                    </div>
                    <div>
                      <p className="font-medium">{legalCase.title}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">{legalCase.case_type}</span>
                        <span className="text-xs text-gray-500">{legalCase.documents_count} documents</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <span className={cn(
                        'text-xs px-2 py-1 rounded',
                        legalCase.status === 'open' ? 'bg-accent-green/20 text-accent-green' :
                        legalCase.status === 'closed' ? 'bg-gray-500/20 text-gray-400' : 'bg-accent-amber/20 text-accent-amber'
                      )}>
                        {legalCase.status}
                      </span>
                    </div>
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

      {/* Research Tab */}
      {activeTab === 'research' && (
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Legal Research</h3>
            <form onSubmit={handleResearch} className="space-y-4">
              <textarea
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter your legal question, case citation, or topic to research..."
                className="w-full h-32 bg-dark-bg border border-dark-border rounded-lg p-4 text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
              />
              <div className="flex justify-end">
                <button
                  type="submit"
                  className="btn btn-primary flex items-center gap-2"
                  disabled={researchMutation.isPending || !searchQuery.trim()}
                >
                  {researchMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
                  Start Research
                </button>
              </div>
            </form>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Research Tips</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-dark-bg">
                <h4 className="font-medium mb-2">Case Law Search</h4>
                <p className="text-sm text-gray-400">Search for specific cases using citations like "Brown v. Board of Education"</p>
              </div>
              <div className="p-4 rounded-lg bg-dark-bg">
                <h4 className="font-medium mb-2">Statute Lookup</h4>
                <p className="text-sm text-gray-400">Find statutes by entering the code section, e.g., "26 U.S.C. 501(c)(3)"</p>
              </div>
              <div className="p-4 rounded-lg bg-dark-bg">
                <h4 className="font-medium mb-2">Topic Research</h4>
                <p className="text-sm text-gray-400">Explore legal topics like "landlord tenant rights Colorado"</p>
              </div>
              <div className="p-4 rounded-lg bg-dark-bg">
                <h4 className="font-medium mb-2">Document Analysis</h4>
                <p className="text-sm text-gray-400">Upload contracts or legal documents for AI-powered analysis</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Document Templates</h3>
          {loadingTemplates ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : templates.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templates.map((template) => (
                <div
                  key={template.id}
                  className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                  onClick={() => setActionResult({ type: 'success', message: `Using template: ${template.name}` })}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs px-2 py-0.5 rounded bg-accent-amber/20 text-accent-amber">
                      {template.category}
                    </span>
                    <span className="text-xs text-gray-500">{template.uses} uses</span>
                  </div>
                  <h4 className="font-medium mb-1">{template.name}</h4>
                  <p className="text-sm text-gray-400">{template.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <BookOpen className="mx-auto mb-2" size={48} />
              <p>No templates available</p>
              <p className="text-sm text-gray-500 mt-1">Legal document templates will appear here</p>
            </div>
          )}
        </div>
      )}

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
