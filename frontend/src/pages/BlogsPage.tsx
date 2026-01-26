/**
 * Session 814: Dedicated Blogs Page
 * Direct access to all AI-generated blog posts from SelfBlog model
 * Session 833: Added approval workflow with status badges and filtering
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  BookOpen,
  Search,
  FileText,
  Calendar,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  RefreshCw,
  Trash2,
  X,
  CheckCircle,
  Eye,
  Clock,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { blogsApi, Blog } from '@/lib/api'

interface BlogPagination {
  page: number
  per_page: number
  total: number
  total_pages: number
}

// Session 833: Status badge styling
const statusStyles: Record<string, { bg: string; text: string; icon: typeof Clock }> = {
  draft: { bg: 'bg-amber-500/20', text: 'text-amber-400', icon: Clock },
  approved: { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: CheckCircle },
  published: { bg: 'bg-green-500/20', text: 'text-green-400', icon: Eye },
}

export default function BlogsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('') // Session 833
  const [deleteConfirm, setDeleteConfirm] = useState<Blog | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['blogs-page', page, search, statusFilter],
    queryFn: async () => {
      const res = await blogsApi.list({
        page,
        per_page: 12,
        ...(search && { search }),
        ...(statusFilter && { status: statusFilter }),
      })
      return res.data
    },
  })

  // Session 814: Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (blogId: string) => {
      const res = await blogsApi.delete(blogId)
      if (!res.data.success) {
        throw new Error('Failed to delete blog')
      }
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blogs-page'] })
      setDeleteConfirm(null)
    },
  })

  // Session 833: Approve mutation
  const approveMutation = useMutation({
    mutationFn: async (blogId: string) => {
      const res = await blogsApi.approve(blogId)
      if (!res.data.success) {
        throw new Error('Failed to approve blog')
      }
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blogs-page'] })
    },
  })

  // Session 833: Publish mutation
  const publishMutation = useMutation({
    mutationFn: async (blogId: string) => {
      const res = await blogsApi.publish(blogId)
      if (!res.data.success) {
        throw new Error('Failed to publish blog')
      }
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blogs-page'] })
    },
  })

  const blogs: Blog[] = data?.blogs || []
  const pagination: BlogPagination = data?.pagination || {
    page: 1,
    per_page: 12,
    total: 0,
    total_pages: 0,
  }
  const statusCounts = data?.status_counts || { all: 0, draft: 0, approved: 0, published: 0 }

  const handleSearch = () => {
    setSearch(searchInput)
    setPage(1)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const handleDelete = (blog: Blog, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDeleteConfirm(blog)
  }

  const confirmDelete = () => {
    if (deleteConfirm) {
      deleteMutation.mutate(deleteConfirm.id)
    }
  }

  const handleApprove = (blogId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    approveMutation.mutate(blogId)
  }

  const handlePublish = (blogId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    publishMutation.mutate(blogId)
  }

  return (
    <div className="space-y-6">
      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-dark-card border border-dark-border rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-semibold text-accent-red">Delete Blog</h3>
              <button
                onClick={() => setDeleteConfirm(null)}
                className="text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>
            <p className="text-gray-300 mb-2">Are you sure you want to delete this blog?</p>
            <p className="text-sm text-gray-400 mb-4 line-clamp-2">"{deleteConfirm.title}"</p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="btn btn-secondary"
                disabled={deleteMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="btn bg-accent-red/20 text-accent-red hover:bg-accent-red/30 flex items-center gap-2"
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? (
                  <Loader2 className="animate-spin" size={16} />
                ) : (
                  <Trash2 size={16} />
                )}
                Delete
              </button>
            </div>
            {deleteMutation.isError && (
              <p className="text-accent-red text-sm mt-3">
                {deleteMutation.error instanceof Error
                  ? deleteMutation.error.message
                  : 'Failed to delete'}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
            <BookOpen className="text-primary-400" size={20} />
          </div>
          <div>
            <h1 className="text-2xl font-bold">AI-Generated Blogs</h1>
            <p className="text-gray-400 text-sm">
              Blog posts written by the system about itself and various topics
            </p>
          </div>
        </div>
        <button
          onClick={() => refetch()}
          className="btn btn-secondary flex items-center gap-2"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Session 833: Status Filter Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        <button
          onClick={() => { setStatusFilter(''); setPage(1); }}
          className={cn(
            'px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
            !statusFilter
              ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
              : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
          )}
        >
          All ({statusCounts.all})
        </button>
        <button
          onClick={() => { setStatusFilter('draft'); setPage(1); }}
          className={cn(
            'px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-colors flex items-center gap-2',
            statusFilter === 'draft'
              ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
              : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
          )}
        >
          <Clock size={14} />
          Draft ({statusCounts.draft})
        </button>
        <button
          onClick={() => { setStatusFilter('approved'); setPage(1); }}
          className={cn(
            'px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-colors flex items-center gap-2',
            statusFilter === 'approved'
              ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
              : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
          )}
        >
          <CheckCircle size={14} />
          Approved ({statusCounts.approved})
        </button>
        <button
          onClick={() => { setStatusFilter('published'); setPage(1); }}
          className={cn(
            'px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-colors flex items-center gap-2',
            statusFilter === 'published'
              ? 'bg-green-500/20 text-green-400 border border-green-500/30'
              : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
          )}
        >
          <Eye size={14} />
          Published ({statusCounts.published})
        </button>
      </div>

      {/* Search */}
      <div className="card">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
            <input
              type="text"
              placeholder="Search by title, content, or tags..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="w-full pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none"
            />
          </div>
          <button onClick={handleSearch} className="btn btn-primary">
            Search
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-400">
          {pagination.total} blog posts
          {search && ` matching "${search}"`}
          {statusFilter && ` (${statusFilter})`}
        </p>
        {pagination.total_pages > 1 && (
          <p className="text-sm text-gray-400">
            Page {pagination.page} of {pagination.total_pages}
          </p>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-primary-500" size={32} />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="card text-center py-12">
          <AlertCircle className="mx-auto mb-4 text-accent-red" size={48} />
          <h3 className="text-lg font-semibold mb-2">Failed to Load Blogs</h3>
          <p className="text-gray-400 mb-4">
            {error instanceof Error ? error.message : 'An error occurred'}
          </p>
          <button onClick={() => refetch()} className="btn btn-primary">
            Try Again
          </button>
        </div>
      )}

      {/* Blog Grid */}
      {!isLoading && !error && blogs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {blogs.map((blog) => {
            const style = statusStyles[blog.status] || statusStyles.draft
            const StatusIcon = style.icon
            return (
              <div key={blog.id} className="card hover:border-primary-500/50 transition-colors group relative">
                <Link to={`/blog/${blog.id}`} className="block">
                  {/* Session 833: Status Badge */}
                  <div className="flex items-center justify-between mb-2">
                    <span className={cn('text-xs px-2 py-0.5 rounded flex items-center gap-1', style.bg, style.text)}>
                      <StatusIcon size={12} />
                      {blog.status}
                    </span>
                  </div>

                  <h3 className="font-semibold mb-2 line-clamp-2 group-hover:text-primary-400 transition-colors pr-8">
                    {blog.title}
                  </h3>
                  <p className="text-sm text-gray-400 mb-3 line-clamp-3">{blog.intro}</p>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1 mb-3">
                    {blog.tags.slice(0, 3).map((tag, i) => (
                      <span
                        key={i}
                        className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400"
                      >
                        {tag}
                      </span>
                    ))}
                    {blog.tags.length > 3 && (
                      <span className="text-xs text-gray-500">+{blog.tags.length - 3} more</span>
                    )}
                  </div>

                  {/* Meta */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <FileText size={12} />
                      {blog.word_count} words
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar size={12} />
                      {new Date(blog.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Tone badge */}
                  {blog.tone && (
                    <div className="mt-2">
                      <span className="text-xs px-2 py-0.5 rounded bg-accent-purple/20 text-accent-purple capitalize">
                        {blog.tone}
                      </span>
                    </div>
                  )}
                </Link>

                {/* Session 833: Action buttons */}
                <div className="absolute top-4 right-4 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {blog.status === 'draft' && (
                    <button
                      onClick={(e) => handleApprove(blog.id, e)}
                      className="p-1.5 rounded bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors"
                      title="Approve"
                      disabled={approveMutation.isPending}
                    >
                      <CheckCircle size={14} />
                    </button>
                  )}
                  {blog.status === 'approved' && (
                    <button
                      onClick={(e) => handlePublish(blog.id, e)}
                      className="p-1.5 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors"
                      title="Publish"
                      disabled={publishMutation.isPending}
                    >
                      <Eye size={14} />
                    </button>
                  )}
                  <button
                    onClick={(e) => handleDelete(blog, e)}
                    className="p-1.5 rounded bg-dark-bg/80 text-gray-400 hover:text-accent-red hover:bg-accent-red/20 transition-colors"
                    title="Delete blog"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && blogs.length === 0 && (
        <div className="card text-center py-12">
          <BookOpen className="mx-auto mb-4 text-gray-500" size={48} />
          <h3 className="text-lg font-semibold mb-2">No Blogs Found</h3>
          <p className="text-gray-400">
            {search
              ? `No blogs match "${search}"`
              : statusFilter
              ? `No ${statusFilter} blogs found`
              : 'No AI-generated blogs yet. The system will create them automatically.'}
          </p>
        </div>
      )}

      {/* Pagination */}
      {pagination.total_pages > 1 && (
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn btn-secondary disabled:opacity-50"
          >
            <ChevronLeft size={16} />
            Previous
          </button>

          {/* Page numbers */}
          <div className="flex items-center gap-1">
            {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
              let pageNum: number
              if (pagination.total_pages <= 5) {
                pageNum = i + 1
              } else if (page <= 3) {
                pageNum = i + 1
              } else if (page >= pagination.total_pages - 2) {
                pageNum = pagination.total_pages - 4 + i
              } else {
                pageNum = page - 2 + i
              }
              return (
                <button
                  key={pageNum}
                  onClick={() => setPage(pageNum)}
                  className={`px-3 py-1 rounded ${
                    page === pageNum
                      ? 'bg-primary-500 text-white'
                      : 'bg-dark-card hover:bg-dark-border'
                  }`}
                >
                  {pageNum}
                </button>
              )
            })}
          </div>

          <button
            onClick={() => setPage((p) => Math.min(pagination.total_pages, p + 1))}
            disabled={page === pagination.total_pages}
            className="btn btn-secondary disabled:opacity-50"
          >
            Next
            <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  )
}
