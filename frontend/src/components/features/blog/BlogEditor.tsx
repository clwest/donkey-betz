import { useState, useEffect } from 'react';
import { contentService } from '../../../services/content.service';
import { BlockEditor } from '../../editor/BlockEditor';
import type { ContentBlock } from '../../../types/blockEditor';
import { blocksToMarkdown, markdownToBlocks } from '../../../utils/blockEditorUtils';
import { Logger } from '../../../utils/logger';
import { toast } from 'sonner';
import { 
  XMarkIcon, 
  CheckIcon,
  PencilIcon
} from '@heroicons/react/24/outline';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';

interface BlogPost {
  id: number;
  title: string;
  content: string;
  meta_description?: string;
  tags: string[];
  word_count: number;
  tone: string;
  length: string;
  created_at: string;
}

interface BlogEditorProps {
  blog: BlogPost;
  isOpen: boolean;
  onClose: () => void;
  onSaved?: (updatedBlog: BlogPost) => void;
}

export function BlogEditor({ blog, isOpen, onClose, onSaved }: BlogEditorProps) {
  const [title, setTitle] = useState('');
  const [contentBlocks, setContentBlocks] = useState<ContentBlock[]>([]);
  const [metaDescription, setMetaDescription] = useState('');
  const [tagsText, setTagsText] = useState('');
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (isOpen && blog) {
      setTitle(blog.title);
      setContentBlocks(markdownToBlocks(blog.content));
      setMetaDescription(blog.meta_description || '');
      setTagsText(blog.tags.join(', '));
      setHasChanges(false);
    }
  }, [isOpen, blog]);

  // Track changes
  useEffect(() => {
    if (blog) {
      const currentContent = blocksToMarkdown(contentBlocks);
      const changed = 
        title !== blog.title ||
        currentContent !== blog.content ||
        metaDescription !== (blog.meta_description || '') ||
        tagsText !== blog.tags.join(', ');
      setHasChanges(changed);
    }
  }, [title, contentBlocks, metaDescription, tagsText, blog]);

  const handleSave = async () => {
    const content = blocksToMarkdown(contentBlocks);
    if (!blog || !title.trim() || !content.trim()) {
      toast.error('Title and content are required');
      return;
    }

    setSaving(true);
    try {
      Logger.component('BlogEditor', `Saving changes to blog ${blog.id}`);
      
      const tags = tagsText
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);

      const result = await contentService.updateBlogPost(blog.id, {
        title: title.trim(),
        content: content.trim(),
        meta_description: metaDescription.trim(),
        tags
      });

      if (result.success) {
        toast.success('Blog post updated successfully!');
        Logger.state('BlogEditor', 'Blog updated', result.blog_post);
        
        if (onSaved && result.blog_post) {
          onSaved(result.blog_post);
        }
        
        setHasChanges(false);
        onClose();
      } else {
        toast.error('Failed to update blog post');
      }
    } catch (error: any) {
      Logger.error('BlogEditor.handleSave', error);
      toast.error('Failed to update blog post');
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    if (hasChanges) {
      if (confirm('You have unsaved changes. Are you sure you want to close?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  const getWordCount = () => {
    const content = blocksToMarkdown(contentBlocks);
    return content.trim().split(/\s+/).filter(word => word.length > 0).length;
  };


  if (!isOpen || !blog) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-lg w-full max-w-5xl h-full max-h-[95vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <PencilIcon className="h-6 w-6 text-primary-400" />
            <h2 className="text-xl font-semibold text-foreground">Edit Blog Post</h2>
            {hasChanges && (
              <span className="px-2 py-1 text-xs bg-yellow-500/20 text-yellow-300 rounded">
                Unsaved changes
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={handleSave}
              disabled={!hasChanges || saving}
              variant="primary"
              size="sm"
              className="min-w-[100px]"
            >
              {saving ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Saving...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <CheckIcon className="h-4 w-4" />
                  Save Changes
                </div>
              )}
            </Button>
            <Button
              onClick={handleClose}
              variant="secondary"
              size="sm"
            >
              <XMarkIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-foreground placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg font-semibold"
              placeholder="Enter blog post title..."
            />
          </div>

          {/* Meta Description */}
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">
              Meta Description
              <span className="text-muted-foreground font-normal ml-2">(SEO description, 150-160 chars recommended)</span>
            </label>
            <textarea
              value={metaDescription}
              onChange={(e) => setMetaDescription(e.target.value)}
              rows={2}
              maxLength={160}
              className="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-foreground placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              placeholder="Brief description for search engines..."
            />
            <div className="text-xs text-muted-foreground mt-1">
              {metaDescription.length}/160 characters
            </div>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">
              Tags
              <span className="text-muted-foreground font-normal ml-2">(comma-separated)</span>
            </label>
            <input
              type="text"
              value={tagsText}
              onChange={(e) => setTagsText(e.target.value)}
              className="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-foreground placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="marketing, social media, business..."
            />
          </div>

          {/* Content */}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-muted-foreground">
                Content
              </label>
              <div className="text-xs text-muted-foreground">
                {getWordCount()} words
              </div>
            </div>
            <div className="bg-dark-700 border border-dark-600 rounded-lg p-4" style={{ minHeight: '500px' }}>
              <BlockEditor
                blocks={contentBlocks}
                onChange={setContentBlocks}
                placeholder="Start writing your blog post..."
              />
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              💡 Tip: Hover over content to see controls. Click + between blocks to add images, headings, or text.
            </div>
          </div>

          {/* Info Card */}
          <Card className="bg-blue-500/10 border-blue-500/20">
            <div className="p-4">
              <h3 className="text-sm font-semibold text-blue-300 mb-2">Original Blog Details</h3>
              <div className="grid grid-cols-2 gap-4 text-xs text-blue-100">
                <div>
                  <span className="font-medium">Tone:</span> {blog.tone}
                </div>
                <div>
                  <span className="font-medium">Length:</span> {blog.length}
                </div>
                <div>
                  <span className="font-medium">Original Word Count:</span> {blog.word_count}
                </div>
                <div>
                  <span className="font-medium">Created:</span> {new Date(blog.created_at).toLocaleDateString()}
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Footer */}
        <div className="border-t border-border p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              {hasChanges ? 'You have unsaved changes' : 'All changes saved'}
            </div>
            <div className="flex gap-3">
              <Button
                onClick={handleClose}
                variant="secondary"
              >
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={!hasChanges || saving}
                variant="primary"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}