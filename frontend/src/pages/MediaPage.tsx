import { useState, useMemo } from 'react'
import { useMedia } from '@/hooks/cockpitQueries'
import LibraryFilters from '@/components/cockpit/library/LibraryFilters'
import MediaGrid from '@/components/cockpit/library/MediaGrid'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { Image } from 'lucide-react'

const MEDIA_TYPE_OPTIONS = [
  { value: 'all', label: 'All media' },
  { value: 'image', label: 'Images' },
  { value: 'video', label: 'Videos' },
]

export default function MediaPage() {
  const [search, setSearch] = useState('')
  const [mType, setMType] = useState('all')
  const [days, setDays] = useState(30)

  const params = useMemo(() => ({
    media_type: mType,
    days,
    limit: 50,
  }), [mType, days])

  const { data, isLoading } = useMedia(params)

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Image size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Media Library</h1>
        {data?.total !== undefined && (
          <span className="text-sm text-gray-500">{data.total} items</span>
        )}
      </div>

      <LibraryFilters
        search={search}
        onSearchChange={setSearch}
        typeFilter={mType}
        onTypeChange={setMType}
        typeOptions={MEDIA_TYPE_OPTIONS}
        daysFilter={days}
        onDaysChange={setDays}
      />

      {isLoading ? (
        <div className="card p-6"><SkeletonRows count={6} /></div>
      ) : (
        <MediaGrid items={data?.items ?? []} total={data?.total ?? 0} />
      )}
    </div>
  )
}
