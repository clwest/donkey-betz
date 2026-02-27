import { formatRelative, formatDateTime } from '@/lib/time'
import { Image as ImageIcon, Film } from 'lucide-react'
import type { MediaItem } from '@/types/cockpit'

interface MediaGridProps {
  items: MediaItem[]
  total: number
}

export default function MediaGrid({ items, total }: MediaGridProps) {
  if (items.length === 0) {
    return (
      <div className="card p-8 text-center text-gray-500">
        No media found.
      </div>
    )
  }

  return (
    <>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {items.map((m) => (
          <div key={m.id} className="card overflow-hidden group">
            <div className="aspect-video bg-dark-border/30 relative flex items-center justify-center">
              {m.thumbnail_url ? (
                <img
                  src={m.thumbnail_url}
                  alt={m.title}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              ) : m.url && m.kind === 'image' ? (
                <img
                  src={m.url}
                  alt={m.title}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              ) : (
                <div className="text-gray-600">
                  {m.kind === 'video' ? <Film size={32} /> : <ImageIcon size={32} />}
                </div>
              )}
              <span className="absolute top-2 right-2 px-1.5 py-0.5 rounded text-[10px] font-medium bg-black/60 text-gray-300 uppercase">
                {m.kind}
              </span>
            </div>
            <div className="px-3 py-2">
              <p className="text-sm text-gray-200 truncate" title={m.title}>{m.title}</p>
              {m.prompt && (
                <p className="text-xs text-gray-500 truncate mt-0.5" title={m.prompt}>{m.prompt}</p>
              )}
              <p className="text-xs text-gray-600 mt-1" title={formatDateTime(m.created_at)}>
                {formatRelative(m.created_at)}
              </p>
            </div>
          </div>
        ))}
      </div>
      {total > items.length && (
        <div className="text-xs text-gray-500 text-center mt-2">
          Showing {items.length} of {total}
        </div>
      )}
    </>
  )
}
