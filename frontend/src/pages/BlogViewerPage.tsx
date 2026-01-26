/**
 * Session 742: Blog Viewer Page
 * Displays full blog content from SelfBlog model
 */

import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, FileText, Calendar, Tag, BarChart3, Loader2, AlertCircle, Trash2, X, Clock, CheckCircle, Eye, Send } from 'lucide-react'
import { blogsApi } from '@/lib/api'

interface Blog {
  id: string
  title: string
  meta_description: string
  intro: string
  sections: Array<{ title: string; content: string }>
  conclusion: string
  tags: string[]
  full_text: string
  tone: string
  word_count: number
  stats_snapshot: Record<string, unknown>
  created_at: string
  status: 'draft' | 'approved' | 'published'
}

const statusStyles = {
  draft: { bg: 'bg-amber-500/20', text: 'text-amber-400', icon: Clock, label: 'Draft' },
  approved: { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: CheckCircle, label: 'Approved' },
  published: { bg: 'bg-green-500/20', text: 'text-green-400', icon: Eye, label: 'Published' },
}

export default function BlogViewerPage() {
  const { blogId } = useParams<{ blogId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['blog', blogId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/research/self-blog/${blogId}/`)
      const json = await response.json()
      if (!json.success) {
        throw new Error(json.error || 'Failed to load blog')
      }
      return json.blog as Blog
    },
    enabled: !!blogId,
  })

  // Session 814: Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/v1/research/self-blog/${blogId}/delete/`, {
        method: 'DELETE',
      })
      const json = await response.json()
      if (!json.success) {
        throw new Error(json.error || 'Failed to delete blog')
      }
      return json
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blogs-page'] })
      navigate('/blogs')
    },
  })

  // Session 833: Approve mutation
  const approveMutation = useMutation({
    mutationFn: async () => {
      const res = await blogsApi.approve(blogId!)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blog', blogId] })
      queryClient.invalidateQueries({ queryKey: ['blogs-page'] })
    },
  })

  // Session 833: Publish mutation
  const publishMutation = useMutation({
    mutationFn: async (force?: boolean) => {
      const res = await blogsApi.publish(blogId!, force)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blog', blogId] })
      queryClient.invalidateQueries({ queryKey: ['blogs-page'] })
    },
  })

  const handleDelete = () => {
    setShowDeleteConfirm(true)
  }

  const confirmDelete = () => {
    deleteMutation.mutate()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin text-primary-500" size={32} />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="card text-center py-12">
        <AlertCircle className="mx-auto mb-4 text-accent-red" size={48} />
        <h3 className="text-lg font-semibold mb-2">Blog Not Found</h3>
        <p className="text-gray-400 mb-4">
          {error instanceof Error ? error.message : 'The requested blog could not be loaded.'}
        </p>
        <Link to="/blogs" className="btn btn-primary">
          Back to Blogs
        </Link>
      </div>
    )
  }

  const blog = data

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-dark-card border border-dark-border rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-semibold text-accent-red">Delete Blog</h3>
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>
            <p className="text-gray-300 mb-2">Are you sure you want to delete this blog?</p>
            <p className="text-sm text-gray-400 mb-4 line-clamp-2">"{blog.title}"</p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
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

      {/* Back button */}
      <Link
        to="/blogs"
        className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft size={18} />
        Back to Blogs
      </Link>

      {/* Header */}
      <div className="card">
        <div className="flex items-start gap-4">
          <div className="h-12 w-12 rounded-lg bg-primary-500/20 flex items-center justify-center flex-shrink-0">
            <FileText className="text-primary-400" size={24} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold">{blog.title}</h1>
              {/* Status badge */}
              {blog.status && statusStyles[blog.status] && (() => {
                const style = statusStyles[blog.status]
                const Icon = style.icon
                return (
                  <span className={`px-2 py-1 rounded-full ${style.bg} ${style.text} text-xs font-medium flex items-center gap-1`}>
                    <Icon size={12} />
                    {style.label}
                  </span>
                )
              })()}
            </div>
            <p className="text-gray-400 mb-4">{blog.meta_description}</p>

            {/* Meta info */}
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <Calendar size={14} />
                <span>{new Date(blog.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center gap-1">
                <BarChart3 size={14} />
                <span>{blog.word_count} words</span>
              </div>
              {blog.tone && (
                <span className="px-2 py-0.5 rounded bg-accent-purple/20 text-accent-purple capitalize">
                  {blog.tone}
                </span>
              )}
            </div>

            {/* Tags */}
            {blog.tags && blog.tags.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 mt-3">
                <Tag size={14} className="text-gray-500" />
                {blog.tags.map((tag, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded bg-dark-bg text-gray-300 text-xs"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="card space-y-6">
        {/* Intro */}
        {blog.intro && (
          <div className="prose prose-invert max-w-none">
            <p className="text-lg text-gray-300 leading-relaxed">{blog.intro}</p>
          </div>
        )}

        {/* Sections */}
        {blog.sections && blog.sections.length > 0 && (
          <div className="space-y-6">
            {blog.sections.map((section, i) => (
              <div key={i} className="border-l-2 border-primary-500/30 pl-4">
                <h2 className="text-xl font-semibold mb-3">{section.title}</h2>
                <div className="prose prose-invert max-w-none">
                  <p className="text-gray-300 whitespace-pre-wrap">{section.content}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Conclusion */}
        {blog.conclusion && (
          <div className="border-t border-dark-border pt-6">
            <h2 className="text-lg font-semibold mb-3">Conclusion</h2>
            <div className="prose prose-invert max-w-none">
              <p className="text-gray-300">{blog.conclusion}</p>
            </div>
          </div>
        )}

        {/* Full text fallback */}
        {!blog.sections?.length && !blog.intro && blog.full_text && (
          <div className="prose prose-invert max-w-none">
            <p className="text-gray-300 whitespace-pre-wrap">{blog.full_text}</p>
          </div>
        )}
      </div>

      {/* Stats snapshot */}
      {blog.stats_snapshot && Object.keys(blog.stats_snapshot).length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">System Stats at Time of Writing</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(blog.stats_snapshot).slice(0, 8).map(([key, value]) => (
              <div key={key} className="p-3 rounded-lg bg-dark-bg">
                <p className="text-xs text-gray-500 capitalize">{key.replace(/_/g, ' ')}</p>
                <p className="font-medium">
                  {typeof value === 'number' ? value.toLocaleString() : String(value)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex justify-between items-center">
        <Link to="/blogs" className="btn btn-secondary">
          <ArrowLeft size={16} className="mr-2" />
          Back to Blogs
        </Link>
        <div className="flex gap-2">
          {/* Show Approve button for drafts */}
          {blog.status === 'draft' && (
            <button
              onClick={() => approveMutation.mutate()}
              disabled={approveMutation.isPending}
              className="btn btn-primary flex items-center gap-2"
            >
              {approveMutation.isPending ? (
                <Loader2 className="animate-spin" size={16} />
              ) : (
                <CheckCircle size={16} />
              )}
              Approve for Publishing
            </button>
          )}
          {/* Show Publish button for approved blogs */}
          {blog.status === 'approved' && (
            <button
              onClick={() => publishMutation.mutate(false)}
              disabled={publishMutation.isPending}
              className="btn bg-green-500/20 text-green-400 hover:bg-green-500/30 flex items-center gap-2"
            >
              {publishMutation.isPending ? (
                <Loader2 className="animate-spin" size={16} />
              ) : (
                <Send size={16} />
              )}
              Publish
            </button>
          )}
          {/* Show Published badge when already published */}
          {blog.status === 'published' && (
            <span className="btn bg-green-500/20 text-green-400 cursor-default flex items-center gap-2">
              <Eye size={16} />
              Published
            </span>
          )}
          <button
            onClick={handleDelete}
            className="btn bg-accent-red/20 text-accent-red hover:bg-accent-red/30 flex items-center gap-2"
          >
            <Trash2 size={16} />
            Delete
          </button>
        </div>
      </div>
      {/* Error messages */}
      {(approveMutation.isError || publishMutation.isError) && (
        <div className="text-accent-red text-sm text-right">
          {approveMutation.error instanceof Error ? approveMutation.error.message : ''}
          {publishMutation.error instanceof Error ? publishMutation.error.message : ''}
        </div>
      )}
    </div>
  )
}
