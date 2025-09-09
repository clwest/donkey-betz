import { useState, useEffect } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { ChapterEditorModal } from '../../components/editor/ChapterEditorModal';
import { MetadataEditorModal } from '../../components/editor/MetadataEditorModal';
import { PublishingModal } from '../../components/publishing/PublishingModal';
import { toast } from 'react-hot-toast';
import { 
  BookOpenIcon, 
  PlusIcon, 
  DocumentTextIcon,
  ClockIcon,
  ChartBarIcon,
  SparklesIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  TrashIcon,
  PencilIcon,
  CheckCircleIcon,
  XCircleIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline';

interface Chapter {
  id: number;
  chapter_number: number;
  title: string;
  subtitle?: string;
  content: string;
  word_count: number;
  summary?: string;
  key_points?: string[];
  status?: 'draft' | 'generated' | 'edited';
}

interface EBook {
  id: number;
  title: string;
  subtitle?: string;
  author?: string;
  description: string;
  genre: string;
  target_audience: string;
  status: 'draft' | 'generating' | 'completed' | 'published';
  chapters: Chapter[] | number; // Array from detail API, number from list API
  word_count?: number; // From list API
  actual_word_count?: number; // From detail API  
  total_word_count?: number; // Legacy field
  word_count_target?: number;
  estimated_reading_time?: number;
  created_at: string;
  updated_at: string;
  cover_image_url?: string;
}

export function EbooksPage() {
  const [ebooks, setEbooks] = useState<EBook[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedEbook, setSelectedEbook] = useState<EBook | null>(null);
  const [viewingChapter, setViewingChapter] = useState<Chapter | null>(null);
  const [loadingChapter, setLoadingChapter] = useState(false);
  const [generating, setGenerating] = useState(false);
  
  // Editing states
  const [editingChapter, setEditingChapter] = useState<Chapter | null>(null);
  const [editingMetadata, setEditingMetadata] = useState<EBook | null>(null);
  const [publishingEbook, setPublishingEbook] = useState<EBook | null>(null);
  
  // Form state for new ebook
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    genre: 'business',
    target_audience: 'professional',
    chapter_count: 10,
    words_per_chapter: 1500
  });

  useEffect(() => {
    loadEbooks();
  }, []);

  const loadEbooks = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8001/api/ebooks/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`
        }
      });
      const data = await response.json();
      
      // Get deleted IDs from localStorage to filter them out
      const deletedIds = JSON.parse(localStorage.getItem('deletedEbookIds') || '[]');
      
      let ebooks = [];
      if (data.ebooks) {
        ebooks = data.ebooks;
      } else if (Array.isArray(data)) {
        ebooks = data;
      }
      
      // Filter out deleted eBooks
      const filteredEbooks = ebooks.filter((ebook: any) => !deletedIds.includes(ebook.id));
      setEbooks(filteredEbooks);
      
    } catch (error) {
      console.error('Failed to load ebooks:', error);
      toast.error('Failed to load eBooks');
    } finally {
      setLoading(false);
    }
  };

  const createEbook = async () => {
    if (!formData.title.trim()) {
      toast.error('Please enter a title');
      return;
    }

    try {
      setGenerating(true);
      const response = await fetch('http://localhost:8001/api/ebooks/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        toast.success('eBook created successfully!');
        setShowCreateModal(false);
        setFormData({
          title: '',
          description: '',
          genre: 'business',
          target_audience: 'professional',
          chapter_count: 10,
          words_per_chapter: 1500
        });
        loadEbooks();
      } else {
        toast.error(data.error || 'Failed to create eBook');
      }
    } catch (error) {
      console.error('Failed to create ebook:', error);
      toast.error('Failed to create eBook');
    } finally {
      setGenerating(false);
    }
  };

  const generateFullEbook = async (ebookId: number) => {
    try {
      setGenerating(true);
      const response = await fetch(`http://localhost:8001/api/ebooks/${ebookId}/generate-full/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        toast.success('eBook generation started!');
        loadEbooks();
      } else {
        toast.error(data.error || 'Failed to generate eBook');
      }
    } catch (error) {
      console.error('Failed to generate ebook:', error);
      toast.error('Failed to generate eBook');
    } finally {
      setGenerating(false);
    }
  };

  const deleteEbook = async (ebookId: number) => {
    if (!confirm('Are you sure you want to delete this eBook? This will remove it from your library view but it will still exist on the server.')) {
      return;
    }
    
    try {
      // Since the backend doesn't support DELETE method for ebooks,
      // we'll implement client-side deletion similar to the blog force-delete pattern
      console.log('Removing eBook from client-side view (backend does not support DELETE)');
      
      // Remove from local state immediately
      setEbooks(prev => prev.filter(e => e.id !== ebookId));
      
      // Store deleted IDs in localStorage to persist hiding
      const deletedIds = JSON.parse(localStorage.getItem('deletedEbookIds') || '[]');
      deletedIds.push(ebookId);
      localStorage.setItem('deletedEbookIds', JSON.stringify(deletedIds));
      
      toast.success('eBook removed from library view (still exists on server)');
    } catch (error) {
      console.error('Failed to delete ebook:', error);
      toast.error('Failed to remove eBook');
    }
  };

  const exportEbook = async (ebookId: number, format: 'pdf' | 'epub' | 'docx') => {
    try {
      const response = await fetch(`http://localhost:8001/api/ebooks/${ebookId}/export/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ format })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ebook-${ebookId}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
        toast.success(`Exported as ${format.toUpperCase()}`);
      } else {
        toast.error('Export not yet implemented');
      }
    } catch (error) {
      console.error('Failed to export ebook:', error);
      toast.error('Export feature coming soon!');
    }
  };

  const loadEbookDetails = async (ebookId: number) => {
    try {
      const response = await fetch(`http://localhost:8001/api/ebooks/${ebookId}/`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`
        }
      });
      
      if (response.ok) {
        const ebookData = await response.json();
        setSelectedEbook(ebookData);
      } else {
        toast.error('Failed to load eBook details');
      }
    } catch (error) {
      console.error('Failed to load eBook details:', error);
      toast.error('Failed to load eBook details');
    }
  };

  const loadChapterContent = async (ebook: EBook, chapter: Chapter) => {
    setLoadingChapter(true);
    try {
      const response = await fetch(`http://localhost:8001/api/ebooks/${ebook.id}/chapters/${chapter.id}/`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`
        }
      });
      
      if (response.ok) {
        const chapterData = await response.json();
        setViewingChapter(chapterData);
      } else {
        toast.error('Failed to load chapter content');
        // Fall back to showing chapter without content
        setViewingChapter(chapter);
      }
    } catch (error) {
      console.error('Failed to load chapter:', error);
      toast.error('Failed to load chapter content');
      // Fall back to showing chapter without content
      setViewingChapter(chapter);
    } finally {
      setLoadingChapter(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'text-green-400 bg-green-400/10';
      case 'completed':
        return 'text-blue-400 bg-blue-400/10';
      case 'generating':
        return 'text-yellow-400 bg-yellow-400/10';
      default:
        return 'text-gray-400 bg-gray-400/10';
    }
  };

  const formatReadingTime = (minutes: number) => {
    if (minutes < 60) return `${minutes} min read`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m read`;
  };

  const handleChapterSave = (updatedChapter: Chapter) => {
    // Update the chapter in the selected eBook
    if (selectedEbook && Array.isArray(selectedEbook.chapters)) {
      const updatedChapters = selectedEbook.chapters.map(ch => 
        ch.id === updatedChapter.id ? updatedChapter : ch
      );
      setSelectedEbook({ ...selectedEbook, chapters: updatedChapters });
    }

    // Update in the main ebooks list
    setEbooks(prev => prev.map(ebook => {
      if (ebook.id === selectedEbook?.id) {
        return { ...ebook, actual_word_count: selectedEbook.actual_word_count };
      }
      return ebook;
    }));

    setEditingChapter(null);
  };

  const handleMetadataSave = (updatedEbook: EBook) => {
    // Update the selected eBook
    if (selectedEbook) {
      setSelectedEbook({ ...selectedEbook, ...updatedEbook });
    }

    // Update in the main ebooks list
    setEbooks(prev => prev.map(ebook => 
      ebook.id === updatedEbook.id ? { ...ebook, ...updatedEbook } : ebook
    ));

    setEditingMetadata(null);
  };

  const handlePublish = (updatedEbook: EBook) => {
    // Update the selected eBook
    if (selectedEbook) {
      setSelectedEbook({ ...selectedEbook, ...updatedEbook });
    }

    // Update in the main ebooks list
    setEbooks(prev => prev.map(ebook => 
      ebook.id === updatedEbook.id ? { ...ebook, ...updatedEbook } : ebook
    ));

    setPublishingEbook(null);
  };

  const handleChapterDelete = async () => {
    if (!editingChapter || !selectedEbook) return;

    if (!confirm(`Are you sure you want to delete "${editingChapter.title}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8001/api/ebooks/${selectedEbook.id}/chapters/`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            chapter_id: editingChapter.id
          })
        }
      );

      const data = await response.json();

      if (response.ok) {
        toast.success(data.message || 'Chapter deleted successfully');
        
        // Update the selected eBook chapters
        if (Array.isArray(selectedEbook.chapters)) {
          const updatedChapters = selectedEbook.chapters.filter(ch => ch.id !== editingChapter.id);
          setSelectedEbook({ ...selectedEbook, chapters: updatedChapters });
        }

        setEditingChapter(null);
      } else {
        toast.error(data.error || 'Failed to delete chapter');
      }
    } catch (error) {
      console.error('Failed to delete chapter:', error);
      toast.error('Failed to delete chapter');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">eBooks</h1>
          <p className="text-gray-400 mt-1">Create and manage long-form content</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <PlusIcon className="h-4 w-4" />
          Create eBook
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Total eBooks</p>
              <p className="text-2xl font-bold text-white">{ebooks.length}</p>
            </div>
            <BookOpenIcon className="h-8 w-8 text-primary-400" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Published</p>
              <p className="text-2xl font-bold text-green-400">
                {ebooks.filter(e => e.status === 'published').length}
              </p>
            </div>
            <CheckCircleIcon className="h-8 w-8 text-green-400" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Total Words</p>
              <p className="text-2xl font-bold text-white">
                {ebooks.reduce((sum, e) => sum + (e.word_count || 0), 0).toLocaleString()}
              </p>
            </div>
            <DocumentTextIcon className="h-8 w-8 text-blue-400" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Chapters</p>
              <p className="text-2xl font-bold text-white">
                {ebooks.reduce((sum, e) => sum + (e.chapters || 0), 0)}
              </p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-purple-400" />
          </div>
        </Card>
      </div>

      {/* eBooks Grid */}
      {ebooks.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <BookOpenIcon className="h-12 w-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400 mb-4">No eBooks yet</p>
            <p className="text-sm text-gray-500 mb-4">Create your first eBook to get started</p>
            <Button onClick={() => setShowCreateModal(true)}>
              Create Your First eBook
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {ebooks.map((ebook) => (
            <Card key={ebook.id} hover className="flex flex-col">
              {/* Cover Image or Placeholder */}
              <div className="h-48 bg-gradient-to-br from-primary-500/20 to-purple-500/20 rounded-lg mb-4 flex items-center justify-center">
                {ebook.cover_image_url ? (
                  <img 
                    src={ebook.cover_image_url} 
                    alt={ebook.title}
                    className="h-full w-full object-cover rounded-lg"
                  />
                ) : (
                  <BookOpenIcon className="h-16 w-16 text-primary-400/50" />
                )}
              </div>
              
              {/* eBook Info */}
              <div className="flex-1">
                <h3 className="font-semibold text-white mb-1">{ebook.title}</h3>
                <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                  {ebook.description || 'No description'}
                </p>
                
                <div className="flex items-center gap-3 text-xs text-gray-500 mb-3">
                  <span className="capitalize">{ebook.genre}</span>
                  <span>•</span>
                  <span>{ebook.chapters || 0} chapters</span>
                  <span>•</span>
                  <span>{formatReadingTime(ebook.estimated_reading_time || 0)}</span>
                </div>
                
                <div className="flex items-center justify-between mb-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(ebook.status)}`}>
                    {ebook.status}
                  </span>
                  <span className="text-xs text-gray-500">
                    {(ebook.word_count || 0).toLocaleString()} words
                  </span>
                </div>
              </div>
              
              {/* Actions */}
              <div className="flex gap-2">
                {ebook.status === 'draft' && (
                  <Button
                    size="sm"
                    onClick={() => generateFullEbook(ebook.id)}
                    disabled={generating}
                    className="flex-1"
                  >
                    <SparklesIcon className="h-4 w-4" />
                    Generate
                  </Button>
                )}
                
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => loadEbookDetails(ebook.id)}
                  className="flex-1"
                >
                  <EyeIcon className="h-4 w-4" />
                  View
                </Button>
                
                {/* Edit button for draft and completed eBooks */}
                {(ebook.status === 'draft' || ebook.status === 'completed') && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setEditingMetadata(ebook)}
                    className="text-blue-400 hover:text-blue-300"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </Button>
                )}
                
                {/* Status-specific action button */}
                {ebook.status === 'published' ? (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => exportEbook(ebook.id, 'pdf')}
                  >
                    <ArrowDownTrayIcon className="h-4 w-4" />
                  </Button>
                ) : ebook.status === 'completed' ? (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setPublishingEbook(ebook)}
                    className="text-green-400 hover:text-green-300"
                  >
                    <RocketLaunchIcon className="h-4 w-4" />
                  </Button>
                ) : ebook.status === 'draft' ? (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => deleteEbook(ebook.id)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </Button>
                ) : null}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create eBook Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-dark-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-semibold text-white mb-4">Create New eBook</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Enter eBook title"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 h-24"
                  placeholder="Brief description of your eBook"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Genre</label>
                  <select
                    value={formData.genre}
                    onChange={(e) => setFormData({...formData, genre: e.target.value})}
                    className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="business">Business</option>
                    <option value="technical">Technical</option>
                    <option value="educational">Educational</option>
                    <option value="self-help">Self-Help</option>
                    <option value="fiction">Fiction</option>
                    <option value="non-fiction">Non-Fiction</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Target Audience</label>
                  <select
                    value={formData.target_audience}
                    onChange={(e) => setFormData({...formData, target_audience: e.target.value})}
                    className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="general">General</option>
                    <option value="professional">Professional</option>
                    <option value="academic">Academic</option>
                    <option value="beginner">Beginner</option>
                    <option value="expert">Expert</option>
                  </select>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Number of Chapters</label>
                  <input
                    type="number"
                    value={formData.chapter_count}
                    onChange={(e) => setFormData({...formData, chapter_count: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    min="3"
                    max="30"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Words per Chapter</label>
                  <input
                    type="number"
                    value={formData.words_per_chapter}
                    onChange={(e) => setFormData({...formData, words_per_chapter: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    min="500"
                    max="5000"
                    step="500"
                  />
                </div>
              </div>
              
              <div className="bg-dark-700 rounded-lg p-3">
                <p className="text-sm text-gray-400">
                  Estimated length: ~{(formData.chapter_count * formData.words_per_chapter).toLocaleString()} words
                  ({Math.round(formData.chapter_count * formData.words_per_chapter / 250)} pages)
                </p>
              </div>
            </div>
            
            <div className="flex justify-end gap-3 mt-6">
              <Button
                variant="ghost"
                onClick={() => {
                  setShowCreateModal(false);
                  setFormData({
                    title: '',
                    description: '',
                    genre: 'business',
                    target_audience: 'professional',
                    chapter_count: 10,
                    words_per_chapter: 1500
                  });
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={createEbook}
                disabled={generating || !formData.title.trim()}
              >
                {generating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    Creating...
                  </>
                ) : (
                  <>
                    <PlusIcon className="h-4 w-4" />
                    Create eBook
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* View eBook Modal */}
      {selectedEbook && (
        <Modal
          isOpen={!!selectedEbook}
          onClose={() => {
            setSelectedEbook(null);
            setViewingChapter(null);
            setLoadingChapter(false);
          }}
          title={selectedEbook.title}
          actions={
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setEditingMetadata(selectedEbook)}
              className="text-gray-400 hover:text-white"
            >
              <PencilIcon className="h-4 w-4 mr-1" />
              Edit Metadata
            </Button>
          }
        >
          <div className="space-y-4">
            {!viewingChapter ? (
              <>
                <p className="text-gray-400">{selectedEbook.description}</p>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Genre:</span>
                    <span className="ml-2 text-white capitalize">{selectedEbook.genre}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Audience:</span>
                    <span className="ml-2 text-white capitalize">{selectedEbook.target_audience}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Word Count:</span>
                    <span className="ml-2 text-white">{(selectedEbook.actual_word_count || selectedEbook.word_count || 0).toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Reading Time:</span>
                    <span className="ml-2 text-white">{formatReadingTime(Math.ceil((selectedEbook.actual_word_count || selectedEbook.word_count || 0) / 200))}</span>
                  </div>
                </div>
                
                <div className="border-t border-dark-700 pt-4">
                  <h3 className="font-semibold text-white mb-3">Chapters</h3>
                  {Array.isArray(selectedEbook.chapters) && selectedEbook.chapters.length > 0 ? (
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {selectedEbook.chapters.map((chapter) => (
                        <div
                          key={chapter.id}
                          className="p-3 bg-dark-800 rounded-lg border border-dark-700 transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <div 
                              className="flex-1 cursor-pointer hover:bg-dark-700/50 p-1 -m-1 rounded"
                              onClick={() => loadChapterContent(selectedEbook, chapter)}
                            >
                              <h4 className="text-sm font-medium text-white">
                                Chapter {chapter.chapter_number}: {chapter.title}
                              </h4>
                              <p className="text-xs text-gray-500">
                                {chapter.word_count.toLocaleString()} words
                              </p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => setEditingChapter(chapter)}
                                className="text-gray-400 hover:text-white"
                              >
                                <PencilIcon className="h-4 w-4" />
                              </Button>
                              <DocumentTextIcon className="h-5 w-5 text-gray-400" />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">
                      {typeof selectedEbook.chapters === 'number' && selectedEbook.chapters > 0
                        ? 'Loading chapters...'
                        : 'No chapters generated yet'}
                    </p>
                  )}
                </div>
              </>
            ) : (
              <>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    setViewingChapter(null);
                    setLoadingChapter(false);
                  }}
                >
                  ← Back to chapters
                </Button>
                
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">
                    Chapter {viewingChapter.chapter_number}: {viewingChapter.title}
                  </h3>
                  <p className="text-xs text-gray-500 mb-4">
                    {viewingChapter.word_count.toLocaleString()} words
                  </p>
                  
                  <div className="prose prose-invert max-w-none">
                    {loadingChapter ? (
                      <div className="flex items-center justify-center py-8">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                        <span className="ml-2 text-gray-400">Loading chapter content...</span>
                      </div>
                    ) : viewingChapter.content ? (
                      <div className="text-gray-300 whitespace-pre-wrap">
                        {viewingChapter.content}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-gray-500 mb-2">No content available for this chapter yet</p>
                        <p className="text-xs text-gray-600">Content may need to be generated</p>
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </Modal>
      )}

      {/* Chapter Editor Modal */}
      {editingChapter && selectedEbook && (
        <ChapterEditorModal
          isOpen={!!editingChapter}
          onClose={() => setEditingChapter(null)}
          chapter={editingChapter}
          ebookId={selectedEbook.id}
          onSave={handleChapterSave}
          onDelete={handleChapterDelete}
        />
      )}

      {/* Metadata Editor Modal */}
      {editingMetadata && (
        <MetadataEditorModal
          isOpen={!!editingMetadata}
          onClose={() => setEditingMetadata(null)}
          ebook={editingMetadata}
          onSave={handleMetadataSave}
        />
      )}

      {/* Publishing Modal */}
      {publishingEbook && (
        <PublishingModal
          isOpen={!!publishingEbook}
          onClose={() => setPublishingEbook(null)}
          ebook={publishingEbook}
          onPublish={handlePublish}
        />
      )}
    </div>
  );
}