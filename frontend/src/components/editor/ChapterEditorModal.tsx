import { useState, useEffect } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { BlockEditor } from './BlockEditor';
import type { ContentBlock } from '../../types/blockEditor';
import { blocksToMarkdown, markdownToBlocks } from '../../utils/blockEditorUtils';
import { toast } from 'react-hot-toast';
import {
  DocumentTextIcon,
  ClockIcon,
  SparklesIcon,
  ArrowPathIcon,
  TrashIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

interface Chapter {
  id: number;
  chapter_number: number;
  title: string;
  subtitle?: string;
  content: string;
  summary?: string;
  key_points?: string[];
  word_count: number;
  status?: 'draft' | 'generated' | 'edited';
}

interface ChapterVersion {
  id: number;
  version_number: number;
  title: string;
  content: string;
  summary: string;
  key_points: string[];
  word_count: number;
  edit_summary: string;
  edited_by: string;
  auto_saved: boolean;
  created_at: string;
}

interface ChapterEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  chapter: Chapter;
  ebookId: number;
  onSave: (updatedChapter: Chapter) => void;
  onDelete?: () => void;
}

export function ChapterEditorModal({
  isOpen,
  onClose,
  chapter,
  ebookId,
  onSave,
  onDelete
}: ChapterEditorModalProps) {
  const [editedChapter, setEditedChapter] = useState<Chapter>(chapter);
  const [contentBlocks, setContentBlocks] = useState<ContentBlock[]>([]);
  const [saving, setSaving] = useState(false);
  const [autoSaving, setAutoSaving] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const [versions, setVersions] = useState<ChapterVersion[]>([]);
  const [loadingVersions, setLoadingVersions] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Update local state when chapter prop changes
  useEffect(() => {
    setEditedChapter(chapter);
    setContentBlocks(markdownToBlocks(chapter.content));
    setHasUnsavedChanges(false);
  }, [chapter]);

  // Track unsaved changes
  useEffect(() => {
    const currentContent = blocksToMarkdown(contentBlocks);
    const hasChanges = (
      editedChapter.title !== chapter.title ||
      editedChapter.subtitle !== chapter.subtitle ||
      currentContent !== chapter.content ||
      editedChapter.summary !== chapter.summary ||
      JSON.stringify(editedChapter.key_points) !== JSON.stringify(chapter.key_points)
    );
    setHasUnsavedChanges(hasChanges);
  }, [editedChapter, contentBlocks, chapter]);

  // Auto-save after 30 seconds of no changes  
  useEffect(() => {
    if (hasUnsavedChanges) {
      const timer = setTimeout(() => {
        handleAutoSave();
      }, 30000);
      return () => clearTimeout(timer);
    }
  }, [hasUnsavedChanges]);

  const handleInputChange = (field: keyof Chapter, value: any) => {
    setEditedChapter(prev => ({ ...prev, [field]: value }));
  };

  const handleAutoSave = async () => {
    if (!hasUnsavedChanges) return;

    try {
      setAutoSaving(true);
      const content = blocksToMarkdown(contentBlocks);
      const response = await fetch(
        `http://localhost:8000/api/ebooks/${ebookId}/chapters/${chapter.id}/auto-save/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            content: content
          })
        }
      );

      if (response.ok) {
        const data = await response.json();
        setEditedChapter(prev => ({ ...prev, word_count: data.word_count }));
      }
    } catch (error) {
      console.error('Auto-save failed:', error);
    } finally {
      setAutoSaving(false);
    }
  };

  const handleSave = async (editSummary?: string) => {
    try {
      setSaving(true);
      const content = blocksToMarkdown(contentBlocks);
      const response = await fetch(
        `http://localhost:8000/api/ebooks/${ebookId}/chapters/${chapter.id}/update/`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title: editedChapter.title,
            subtitle: editedChapter.subtitle,
            content: content,
            summary: editedChapter.summary,
            key_points: editedChapter.key_points,
            edit_summary: editSummary || 'Chapter updated'
          })
        }
      );

      const data = await response.json();

      if (response.ok) {
        toast.success('Chapter saved successfully');
        onSave({ ...editedChapter, content: content, word_count: data.word_count });
        setHasUnsavedChanges(false);
      } else {
        toast.error(data.error || 'Failed to save chapter');
      }
    } catch (error) {
      console.error('Save failed:', error);
      toast.error('Failed to save chapter');
    } finally {
      setSaving(false);
    }
  };

  const loadVersions = async () => {
    try {
      setLoadingVersions(true);
      const response = await fetch(
        `http://localhost:8000/api/ebooks/${ebookId}/chapters/${chapter.id}/versions/`,
        {
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setVersions(data.versions);
        setShowVersions(true);
      } else {
        toast.error('Failed to load version history');
      }
    } catch (error) {
      console.error('Failed to load versions:', error);
      toast.error('Failed to load version history');
    } finally {
      setLoadingVersions(false);
    }
  };

  const restoreVersion = async (versionId: number, versionNumber: number) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/ebooks/${ebookId}/chapters/${chapter.id}/versions/${versionId}/restore/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const data = await response.json();

      if (response.ok) {
        toast.success(`Restored to version ${versionNumber}`);
        setEditedChapter(data.chapter);
        setContentBlocks(markdownToBlocks(data.chapter.content));
        setShowVersions(false);
        onSave(data.chapter);
      } else {
        toast.error(data.error || 'Failed to restore version');
      }
    } catch (error) {
      console.error('Failed to restore version:', error);
      toast.error('Failed to restore version');
    }
  };

  const addKeyPoint = () => {
    const newKeyPoints = [...(editedChapter.key_points || []), ''];
    handleInputChange('key_points', newKeyPoints);
  };

  const updateKeyPoint = (index: number, value: string) => {
    const newKeyPoints = [...(editedChapter.key_points || [])];
    newKeyPoints[index] = value;
    handleInputChange('key_points', newKeyPoints);
  };

  const removeKeyPoint = (index: number) => {
    const newKeyPoints = editedChapter.key_points?.filter((_, i) => i !== index) || [];
    handleInputChange('key_points', newKeyPoints);
  };

  const handleClose = () => {
    if (hasUnsavedChanges) {
      if (confirm('You have unsaved changes. Are you sure you want to close?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };


  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={`Edit Chapter ${chapter.chapter_number}`}
      maxWidth="4xl"
    >
      <div className="space-y-6">
        {/* Header with actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <DocumentTextIcon className="h-6 w-6 text-primary-400" />
            <div>
              <h3 className="text-lg font-semibold text-white">Chapter Editor</h3>
              <p className="text-sm text-gray-400">
                {editedChapter.word_count?.toLocaleString() || 0} words • 
                {Math.ceil((editedChapter.word_count || 0) / 200)} min read
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {autoSaving && (
              <div className="flex items-center gap-1 text-xs text-yellow-400">
                <div className="animate-spin rounded-full h-3 w-3 border border-yellow-400 border-t-transparent" />
                Auto-saving...
              </div>
            )}
            <Button
              size="sm"
              variant="ghost"
              onClick={loadVersions}
              disabled={loadingVersions}
            >
              <ClockIcon className="h-4 w-4" />
              Versions
            </Button>
            {onDelete && (
              <Button
                size="sm"
                variant="ghost"
                onClick={onDelete}
                className="text-red-400 hover:text-red-300"
              >
                <TrashIcon className="h-4 w-4" />
                Delete
              </Button>
            )}
          </div>
        </div>

        {!showVersions ? (
          <>
            {/* Chapter metadata */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Chapter Title
                </label>
                <input
                  type="text"
                  value={editedChapter.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Subtitle (optional)
                </label>
                <input
                  type="text"
                  value={editedChapter.subtitle || ''}
                  onChange={(e) => handleInputChange('subtitle', e.target.value)}
                  className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>

            {/* Chapter content */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Chapter Content
              </label>
              <div className="bg-dark-700 border border-dark-600 rounded-lg p-4" style={{ minHeight: '400px' }}>
                <BlockEditor
                  blocks={contentBlocks}
                  onChange={setContentBlocks}
                  placeholder="Start writing your chapter..."
                />
              </div>
              <div className="text-xs text-gray-400 mt-1">
                💡 Tip: Hover over content to see controls. Click + between blocks to add images, headings, or text.
              </div>
            </div>

            {/* Chapter summary */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">
                Chapter Summary (optional)
              </label>
              <textarea
                value={editedChapter.summary || ''}
                onChange={(e) => handleInputChange('summary', e.target.value)}
                className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 h-20"
                placeholder="Brief summary of this chapter..."
              />
            </div>

            {/* Key points */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-400">
                  Key Points (optional)
                </label>
                <Button size="sm" variant="ghost" onClick={addKeyPoint}>
                  <SparklesIcon className="h-4 w-4" />
                  Add Point
                </Button>
              </div>
              {editedChapter.key_points?.map((point, index) => (
                <div key={index} className="flex items-center gap-2 mb-2">
                  <input
                    type="text"
                    value={point}
                    onChange={(e) => updateKeyPoint(index, e.target.value)}
                    className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder={`Key point ${index + 1}`}
                  />
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => removeKeyPoint(index)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <XMarkIcon className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </>
        ) : (
          /* Version history */
          <div>
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-white">Version History</h4>
              <Button size="sm" variant="ghost" onClick={() => setShowVersions(false)}>
                ← Back to Editor
              </Button>
            </div>
            
            {loadingVersions ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white" />
                <span className="ml-2">Loading versions...</span>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {versions.map((version) => (
                  <div
                    key={version.id}
                    className="p-4 bg-dark-700 rounded-lg border border-dark-600"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-white">
                          v{version.version_number}
                        </span>
                        <span className="text-xs text-gray-400">
                          by {version.edited_by}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(version.created_at).toLocaleString()}
                        </span>
                        {version.auto_saved && (
                          <span className="px-2 py-1 bg-yellow-400/10 text-yellow-400 text-xs rounded">
                            Auto-saved
                          </span>
                        )}
                      </div>
                      <Button
                        size="sm"
                        onClick={() => restoreVersion(version.id, version.version_number)}
                      >
                        <ArrowPathIcon className="h-4 w-4" />
                        Restore
                      </Button>
                    </div>
                    <p className="text-sm text-gray-300 mb-2">{version.edit_summary}</p>
                    <div className="text-xs text-gray-500">
                      {version.word_count.toLocaleString()} words • "{version.title}"
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        {!showVersions && (
          <div className="flex justify-between items-center pt-4 border-t border-dark-600">
            <div className="text-sm text-gray-400">
              {hasUnsavedChanges && (
                <span className="text-yellow-400">You have unsaved changes</span>
              )}
            </div>
            <div className="flex gap-3">
              <Button variant="ghost" onClick={handleClose}>
                Cancel
              </Button>
              <Button
                onClick={() => handleSave()}
                disabled={saving || !hasUnsavedChanges}
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    Saving...
                  </>
                ) : (
                  <>
                    <CheckIcon className="h-4 w-4" />
                    Save Chapter
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}