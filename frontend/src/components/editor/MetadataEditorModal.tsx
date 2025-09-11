import { useState, useEffect } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { toast } from 'react-hot-toast';
import {
  BookOpenIcon,
  UserIcon,
  TagIcon,
  ClockIcon,
  CheckIcon,
  XMarkIcon,
  PlusIcon
} from '@heroicons/react/24/outline';

interface EBookMetadata {
  id: number;
  title: string;
  subtitle?: string;
  author?: string;
  description: string;
  genre: string;
  target_audience: string;
  keywords: string[];
}

interface EBookVersion {
  id: number;
  version_number: number;
  title: string;
  edit_summary: string;
  edited_by: string;
  created_at: string;
}

interface MetadataEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  ebook: EBookMetadata;
  onSave: (updatedEbook: EBookMetadata) => void;
}

export function MetadataEditorModal({
  isOpen,
  onClose,
  ebook,
  onSave
}: MetadataEditorModalProps) {
  const [editedEbook, setEditedEbook] = useState<EBookMetadata>(ebook);
  const [saving, setSaving] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const [versions, setVersions] = useState<EBookVersion[]>([]);
  const [loadingVersions, setLoadingVersions] = useState(false);
  const [editSummary, setEditSummary] = useState('');
  const [newKeyword, setNewKeyword] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Update local state when ebook prop changes
  useEffect(() => {
    setEditedEbook(ebook);
    setHasUnsavedChanges(false);
  }, [ebook]);

  // Track unsaved changes
  useEffect(() => {
    const hasChanges = (
      editedEbook.title !== ebook.title ||
      editedEbook.subtitle !== ebook.subtitle ||
      editedEbook.author !== ebook.author ||
      editedEbook.description !== ebook.description ||
      editedEbook.genre !== ebook.genre ||
      editedEbook.target_audience !== ebook.target_audience ||
      JSON.stringify(editedEbook.keywords) !== JSON.stringify(ebook.keywords)
    );
    setHasUnsavedChanges(hasChanges);
  }, [editedEbook, ebook]);

  const handleInputChange = (field: keyof EBookMetadata, value: any) => {
    setEditedEbook(prev => ({ ...prev, [field]: value }));
  };

  const addKeyword = () => {
    if (newKeyword.trim() && !editedEbook.keywords.includes(newKeyword.trim())) {
      handleInputChange('keywords', [...editedEbook.keywords, newKeyword.trim()]);
      setNewKeyword('');
    }
  };

  const removeKeyword = (index: number) => {
    const newKeywords = editedEbook.keywords.filter((_, i) => i !== index);
    handleInputChange('keywords', newKeywords);
  };

  const handleKeywordKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addKeyword();
    }
  };

  const handleSave = async () => {
    if (!editedEbook.title.trim()) {
      toast.error('Title is required');
      return;
    }

    try {
      setSaving(true);
      const response = await fetch(
        `http://localhost:8000/api/ebooks/${ebook.id}/update/`,
        {
          method: 'PUT',
          headers: {
            'Authorization': 'Token 993f8273f70877e23b5c7d2f92ed30562a089fe3',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title: editedEbook.title,
            subtitle: editedEbook.subtitle,
            author: editedEbook.author,
            description: editedEbook.description,
            genre: editedEbook.genre,
            target_audience: editedEbook.target_audience,
            keywords: editedEbook.keywords,
            edit_summary: editSummary || 'Updated metadata'
          })
        }
      );

      const data = await response.json();

      if (response.ok) {
        toast.success('Metadata updated successfully');
        onSave(editedEbook);
        setHasUnsavedChanges(false);
        setEditSummary('');
        onClose();
      } else {
        toast.error(data.error || 'Failed to update metadata');
      }
    } catch (error) {
      console.error('Save failed:', error);
      toast.error('Failed to update metadata');
    } finally {
      setSaving(false);
    }
  };

  const loadVersions = async () => {
    try {
      setLoadingVersions(true);
      const response = await fetch(
        `http://localhost:8000/api/ebooks/${ebook.id}/versions/`,
        {
          headers: {
            'Authorization': 'Token 993f8273f70877e23b5c7d2f92ed30562a089fe3'
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

  const handleClose = () => {
    if (hasUnsavedChanges) {
      if (confirm('You have unsaved changes. Are you sure you want to close?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  const genres = [
    { value: 'business', label: 'Business' },
    { value: 'technical', label: 'Technical' },
    { value: 'self_help', label: 'Self-Help' },
    { value: 'educational', label: 'Educational' },
    { value: 'fiction', label: 'Fiction' },
    { value: 'non_fiction', label: 'Non-Fiction' },
    { value: 'guide', label: 'How-To Guide' },
    { value: 'whitepaper', label: 'Whitepaper' },
    { value: 'report', label: 'Research Report' },
    { value: 'manual', label: 'Manual' }
  ];

  const audiences = [
    { value: 'general', label: 'General Audience' },
    { value: 'professional', label: 'Professional' },
    { value: 'academic', label: 'Academic' },
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'expert', label: 'Expert' },
    { value: 'students', label: 'Students' },
    { value: 'executives', label: 'Executives' }
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Edit eBook Metadata"
      maxWidth="2xl"
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BookOpenIcon className="h-6 w-6 text-primary-400" />
            <div>
              <h3 className="text-lg font-semibold text-white">eBook Information</h3>
              <p className="text-sm text-gray-400">Edit your eBook's metadata and details</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={loadVersions}
              disabled={loadingVersions}
            >
              <ClockIcon className="h-4 w-4" />
              History
            </Button>
          </div>
        </div>

        {!showVersions ? (
          <>
            {/* Basic Information */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  value={editedEbook.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Enter eBook title"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Subtitle
                </label>
                <input
                  type="text"
                  value={editedEbook.subtitle || ''}
                  onChange={(e) => handleInputChange('subtitle', e.target.value)}
                  className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Optional subtitle"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Author
                </label>
                <div className="relative">
                  <UserIcon className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    value={editedEbook.author || ''}
                    onChange={(e) => handleInputChange('author', e.target.value)}
                    className="w-full pl-10 pr-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Author name"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Description
                </label>
                <textarea
                  value={editedEbook.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 h-24"
                  placeholder="Brief description of your eBook"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Genre
                  </label>
                  <select
                    value={editedEbook.genre}
                    onChange={(e) => handleInputChange('genre', e.target.value)}
                    className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {genres.map(genre => (
                      <option key={genre.value} value={genre.value}>
                        {genre.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Target Audience
                  </label>
                  <select
                    value={editedEbook.target_audience}
                    onChange={(e) => handleInputChange('target_audience', e.target.value)}
                    className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {audiences.map(audience => (
                      <option key={audience.value} value={audience.value}>
                        {audience.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Keywords */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Keywords (SEO)
                </label>
                <div className="space-y-2">
                  {/* Add new keyword */}
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <TagIcon className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                      <input
                        type="text"
                        value={newKeyword}
                        onChange={(e) => setNewKeyword(e.target.value)}
                        onKeyDown={handleKeywordKeyDown}
                        className="w-full pl-10 pr-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="Add a keyword"
                      />
                    </div>
                    <Button
                      size="sm"
                      onClick={addKeyword}
                      disabled={!newKeyword.trim()}
                    >
                      <PlusIcon className="h-4 w-4" />
                      Add
                    </Button>
                  </div>

                  {/* Keyword tags */}
                  {editedEbook.keywords.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {editedEbook.keywords.map((keyword, index) => (
                        <div
                          key={index}
                          className="flex items-center gap-1 px-2 py-1 bg-primary-500/20 text-primary-300 rounded-md text-sm"
                        >
                          <span>{keyword}</span>
                          <button
                            onClick={() => removeKeyword(index)}
                            className="text-primary-400 hover:text-primary-300"
                          >
                            <XMarkIcon className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Edit Summary */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Edit Summary (optional)
                </label>
                <input
                  type="text"
                  value={editSummary}
                  onChange={(e) => setEditSummary(e.target.value)}
                  className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Describe what you changed (for version history)"
                />
              </div>
            </div>
          </>
        ) : (
          /* Version history */
          <div>
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-white">Metadata History</h4>
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
                      </div>
                    </div>
                    <p className="text-sm text-gray-300 mb-2">{version.edit_summary}</p>
                    <div className="text-xs text-gray-500">
                      Title: "{version.title}"
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
                onClick={handleSave}
                disabled={saving || !hasUnsavedChanges || !editedEbook.title.trim()}
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    Saving...
                  </>
                ) : (
                  <>
                    <CheckIcon className="h-4 w-4" />
                    Save Changes
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