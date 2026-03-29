import { useState, useMemo } from 'react'
import { useDeliverables, useMedia } from '@/hooks/cockpitQueries'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import LibraryFilters from '@/components/cockpit/library/LibraryFilters'
import DeliverablesTable from '@/components/cockpit/library/DeliverablesTable'
import MediaGrid from '@/components/cockpit/library/MediaGrid'
import { FolderOpen, FileText, Image } from 'lucide-react'

type Tab = 'deliverables' | 'media'

const DELIVERABLE_TYPE_OPTIONS = [
  { value: '', label: 'All types' },
  { value: 'document', label: 'Document' },
  { value: 'image', label: 'Image' },
  { value: 'video', label: 'Video' },
  { value: 'audio', label: 'Audio' },
  { value: 'code', label: 'Code' },
  { value: 'analysis', label: 'Analysis' },
  { value: 'report', label: 'Report' },
  { value: 'research', label: 'Research' },
  { value: 'strategy', label: 'Strategy' },
  { value: 'plan', label: 'Plan' },
  { value: 'script', label: 'Script' },
]

const MEDIA_TYPE_OPTIONS = [
  { value: 'all', label: 'All media' },
  { value: 'image', label: 'Images' },
  { value: 'video', label: 'Videos' },
]

export default function CockpitLibraryPage() {
  const activeWorkspace = useWorkspaceStore((s) => s.activeWorkspace)
  const wsId = activeWorkspace?.id

  const [tab, setTab] = useState<Tab>('deliverables')
  const [search, setSearch] = useState('')
  const [dType, setDType] = useState('')
  const [mType, setMType] = useState('all')
  const [days, setDays] = useState(0)
  const [delOffset, setDelOffset] = useState(0)

  const delParams = useMemo(() => ({
    q: search || undefined,
    type: dType || undefined,
    days,
    limit: 50,
    offset: delOffset || undefined,
    workspace: wsId || undefined,
  }), [search, dType, days, delOffset, wsId])

  const mediaParams = useMemo(() => ({
    media_type: mType,
    days,
    limit: 50,
  }), [mType, days])

  const { data: delData, isLoading: delLoading } = useDeliverables(tab === 'deliverables' ? delParams : undefined)
  const { data: mediaData, isLoading: mediaLoading } = useMedia(tab === 'media' ? mediaParams : undefined)

  const tabs: { id: Tab; label: string; icon: typeof FileText; count?: number }[] = [
    { id: 'deliverables', label: 'Deliverables', icon: FileText, count: delData?.total },
    { id: 'media', label: 'Media', icon: Image, count: mediaData?.total },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <FolderOpen size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Library</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-dark-border">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t.id
                ? 'border-primary-500 text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}
          >
            <t.icon size={14} />
            {t.label}
            {t.count !== undefined && (
              <span className="ml-1 text-xs text-gray-500">{t.count}</span>
            )}
          </button>
        ))}
      </div>

      {/* Filters */}
      <LibraryFilters
        search={tab === 'deliverables' ? search : ''}
        onSearchChange={(v) => { setSearch(v); setDelOffset(0) }}
        typeFilter={tab === 'deliverables' ? dType : mType}
        onTypeChange={tab === 'deliverables' ? (v) => { setDType(v); setDelOffset(0) } : setMType}
        typeOptions={tab === 'deliverables' ? DELIVERABLE_TYPE_OPTIONS : MEDIA_TYPE_OPTIONS}
        daysFilter={days}
        onDaysChange={(v) => { setDays(v); setDelOffset(0) }}
      />

      {/* Content */}
      {tab === 'deliverables' && (
        delLoading ? (
          <div className="card p-6"><SkeletonRows count={6} /></div>
        ) : (
          <DeliverablesTable
            items={delData?.items ?? []}
            total={delData?.total ?? 0}
            offset={delOffset}
            limit={50}
            onPageChange={setDelOffset}
          />
        )
      )}

      {tab === 'media' && (
        mediaLoading ? (
          <div className="card p-6"><SkeletonRows count={6} /></div>
        ) : (
          <MediaGrid items={mediaData?.items ?? []} total={mediaData?.total ?? 0} />
        )
      )}
    </div>
  )
}
