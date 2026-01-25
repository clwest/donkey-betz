/**
 * Session 814: Dedicated Blogs Page
 * Direct access to all AI-generated blog posts from SelfBlog model
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
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
} from 'lucide-react'

interface Blog {
  id: string
  title: string
  intro: string
  tags: string[]
  word_count: number
  tone: string
  created_at: string
}

interface BlogPagination {
  page: number
  per_page: number
  total: number
  total_pages: number
}

export default function BlogsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['blogs-page', page, search],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '12',
        ...(search && { search }),
      })
      const response = await fetch(`/api/v1/research/self-blog/list/?${params}`)
      return response.json()
    },
  })

  // Session 814: Defensive handling for API response
  const rawBlogs = data?.blogs || data?.results || []
  const blogs: Blog[] = rawBlogs.map((blog: Record<string, unknown>) => ({
    ...blog,
    id: String(blog.id || ''),
    title: String(blog.title || 'Untitled'),
    intro: String(blog.intro || ''),
    tags: Array.isArray(blog.tags) ? blog.tags : [],
    word_count: Number(blog.word_count) || 0,
    tone: String(blog.tone || ''),
    created_at: String(blog.created_at || new Date().toISOString()),
  }))
  const pagination: BlogPagination = data?.pagination || {
    page: 1,
    per_page: 12,
    total: 0,
    total_pages: 0,
  }

  const handleSearch = () => {
    setSearch(searchInput)
    setPage(1)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className="space-y-6">
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

      {/* Search */}
      <div className="card">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
            <input
              type="text"
              placeholder="Search blogs by title, content, or tags..."
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
          {blogs.map((blog) => (
            <Link
              key={blog.id}
              to={`/blog/${blog.id}`}
              className="card hover:border-primary-500/50 transition-colors cursor-pointer group"
            >
              <h3 className="font-semibold mb-2 line-clamp-2 group-hover:text-primary-400 transition-colors">
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
          ))}
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
