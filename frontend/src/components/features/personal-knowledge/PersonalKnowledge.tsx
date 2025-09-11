import React, { useState, useEffect, useRef } from 'react';
import { Upload, FileText, Search, Tag, Folder, Download, Trash2, Edit, Plus, X, CheckCircle, AlertCircle, BookOpen, Brain, Hash, ChevronDown, ChevronUp, Eye } from 'lucide-react';
import { useAuthStore } from '../../../store/authStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface KnowledgeEntry {
  id: string;
  title: string;
  description: string;
  content_preview: string;
  full_content?: string;  // Added for full content display
  content_type: string;
  file_type: string;
  category: string;
  tags: string[];
  word_count: number;
  use_in_generation: boolean;
  times_used: number;
  last_used: string | null;
  created_at: string;
}

interface KnowledgeStats {
  total_entries: number;
  total_words: number;
  categories: string[];
  most_used_title: string | null;
  total_embeddings?: number;
}

const PersonalKnowledge: React.FC = () => {
  const { token } = useAuthStore();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [knowledge, setKnowledge] = useState<KnowledgeEntry[]>([]);
  const [stats, setStats] = useState<KnowledgeStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedEntry, setSelectedEntry] = useState<KnowledgeEntry | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadType, setUploadType] = useState<'file' | 'text'>('text');
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set());
  const [detailEntry, setDetailEntry] = useState<KnowledgeEntry | null>(null);
  
  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 12;
  
  // Form states for new knowledge
  const [newKnowledge, setNewKnowledge] = useState({
    title: '',
    description: '',
    content: '',
    category: '',
    tags: '',
    content_type: 'note',
    use_in_generation: true
  });

  const contentTypes = [
    { value: 'note', label: 'Personal Note', icon: FileText },
    { value: 'document', label: 'Document', icon: FileText },
    { value: 'snippet', label: 'Code Snippet', icon: Hash },
    { value: 'reference', label: 'Reference Material', icon: BookOpen },
    { value: 'style_guide', label: 'Style Guide', icon: Edit },
    { value: 'brand_guide', label: 'Brand Guidelines', icon: Tag },
    { value: 'portfolio', label: 'Portfolio Item', icon: Folder },
    { value: 'research', label: 'Research', icon: Brain },
    { value: 'template', label: 'Template', icon: FileText },
    { value: 'other', label: 'Other', icon: Folder }
  ];

  useEffect(() => {
    // Reset to first page when search or category changes
    if (selectedCategory || searchQuery) {
      setCurrentPage(1);
    }
  }, [selectedCategory, searchQuery]);
  
  useEffect(() => {
    fetchKnowledge();
  }, [selectedCategory, searchQuery, currentPage]);

  const fetchKnowledge = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      if (searchQuery) params.append('search', searchQuery);
      params.append('page', currentPage.toString());
      params.append('per_page', itemsPerPage.toString());
      
      const response = await fetch(`${API_BASE_URL}/personal-knowledge/list/?${params}`, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setKnowledge(data.knowledge || []);
        setStats(data.stats);
        
        // Calculate pagination
        const total = data.stats?.total_entries || data.knowledge?.length || 0;
        setTotalItems(total);
        setTotalPages(Math.ceil(total / itemsPerPage));
        
        // Embeddings count is already included in stats.total_embeddings
        // fetchEmbeddingsCount();  // Not needed - data comes from personal-knowledge/list
      }
    } catch (error) {
      console.error('Error fetching knowledge:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmbeddingsCount = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/embeddings-stats/`, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        // Get Personal Knowledge embeddings count
        const pkEmbeddings = data.breakdown?.['Personal Knowledge']?.documents || 0;
        
        // Update stats with embeddings count
        setStats(prevStats => ({
          ...prevStats!,
          total_embeddings: pkEmbeddings
        }));
      }
    } catch (error) {
      console.error('Error fetching embeddings count:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', newKnowledge.title || file.name);
    formData.append('description', newKnowledge.description);
    formData.append('category', newKnowledge.category);
    formData.append('tags', JSON.stringify(newKnowledge.tags.split(',').map(t => t.trim()).filter(t => t)));
    formData.append('content_type', newKnowledge.content_type);
    formData.append('use_in_generation', String(newKnowledge.use_in_generation));
    
    try {
      console.log('Uploading file to:', `${API_BASE_URL}/personal-knowledge/upload/`);
      const response = await fetch(`${API_BASE_URL}/personal-knowledge/upload/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`
        },
        body: formData
      });
      
      console.log('Upload response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        await fetchKnowledge();
        setShowUploadModal(false);
        resetForm();
        showNotification('File uploaded successfully!', 'success');
      } else {
        let errorMsg = 'Upload failed';
        try {
          const error = await response.json();
          errorMsg = error.error || errorMsg;
        } catch (e) {
          console.error('Failed to parse error response:', e);
        }
        showNotification(errorMsg, 'error');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      showNotification('Upload failed', 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleTextSubmit = async () => {
    if (!newKnowledge.title || !newKnowledge.content) {
      showNotification('Title and content are required', 'error');
      return;
    }
    
    setUploading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/personal-knowledge/upload/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...newKnowledge,
          tags: newKnowledge.tags.split(',').map(t => t.trim()).filter(t => t)
        })
      });
      
      if (response.ok) {
        await fetchKnowledge();
        setShowUploadModal(false);
        resetForm();
        showNotification('Knowledge added successfully!', 'success');
      } else {
        let errorMsg = 'Failed to add knowledge';
        try {
          const error = await response.json();
          errorMsg = error.error || errorMsg;
        } catch (e) {
          console.error('Failed to parse error response:', e);
        }
        showNotification(errorMsg, 'error');
      }
    } catch (error) {
      console.error('Error adding knowledge:', error);
      showNotification('Failed to add knowledge', 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this knowledge entry?')) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/personal-knowledge/${id}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      
      if (response.ok) {
        await fetchKnowledge();
        showNotification('Knowledge deleted successfully', 'success');
      }
    } catch (error) {
      console.error('Error deleting knowledge:', error);
      showNotification('Failed to delete knowledge', 'error');
    }
  };

  const resetForm = () => {
    setNewKnowledge({
      title: '',
      description: '',
      content: '',
      category: '',
      tags: '',
      content_type: 'note',
      use_in_generation: true
    });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const showNotification = (message: string, type: 'success' | 'error') => {
    // This would integrate with your notification system
    console.log(`${type}: ${message}`);
  };

  const toggleExpanded = (id: string) => {
    setExpandedEntries(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Personal Knowledge Base
          </h1>
          <p className="text-gray-400">Upload and manage your personal content for AI learning</p>
        </div>

        {/* Stats Bar */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Entries</p>
                  <p className="text-2xl font-bold">{stats.total_entries}</p>
                </div>
                <FileText className="w-8 h-8 text-blue-400" />
              </div>
            </div>
            
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Words</p>
                  <p className="text-2xl font-bold">{stats.total_words.toLocaleString()}</p>
                </div>
                <Hash className="w-8 h-8 text-green-400" />
              </div>
            </div>
            
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Categories</p>
                  <p className="text-2xl font-bold">{stats.categories.length}</p>
                </div>
                <Folder className="w-8 h-8 text-purple-400" />
              </div>
            </div>
            
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Embeddings</p>
                  <p className="text-2xl font-bold">{stats.total_embeddings || 0}</p>
                </div>
                <Brain className="w-8 h-8 text-orange-400" />
              </div>
            </div>
          </div>
        )}

        {/* Action Bar */}
        <div className="flex flex-wrap gap-4 mb-8">
          <button
            onClick={() => setShowUploadModal(true)}
            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg font-medium hover:from-blue-600 hover:to-purple-600 transition-all flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Add Knowledge
          </button>
          
          <div className="flex-1 min-w-[300px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search your knowledge base..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
              />
            </div>
          </div>
          
          {stats && stats.categories.length > 0 && (
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
            >
              <option value="">All Categories</option>
              {stats.categories.map((cat, index) => (
                <option key={`${cat}-${index}`} value={cat}>{cat || 'Uncategorized'}</option>
              ))}
            </select>
          )}
        </div>

        {/* Knowledge Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
          </div>
        ) : knowledge.length === 0 ? (
          <div className="text-center py-16 bg-gray-800/30 rounded-lg border border-gray-700">
            <Brain className="w-16 h-16 mx-auto mb-4 text-gray-600" />
            <h3 className="text-xl font-semibold mb-2">No knowledge entries yet</h3>
            <p className="text-gray-400 mb-4">Start building your personal knowledge base</p>
            <button
              onClick={() => setShowUploadModal(true)}
              className="px-6 py-2 bg-blue-500 rounded-lg hover:bg-blue-600 transition-colors"
            >
              Add Your First Entry
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {knowledge.map((entry) => {
              const Icon = contentTypes.find(t => t.value === entry.content_type)?.icon || FileText;
              
              return (
                <div
                  key={entry.id}
                  className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-5 border border-gray-700 hover:border-gray-600 transition-all group"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <Icon className="w-5 h-5 text-blue-400 flex-shrink-0" />
                      <h3 className="font-semibold truncate flex-1" title={entry.title}>
                        {entry.title}
                      </h3>
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => setDetailEntry(entry)}
                        className="p-1 hover:bg-gray-700 rounded transition-colors"
                        title="View full content"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setSelectedEntry(entry)}
                        className="p-1 hover:bg-gray-700 rounded transition-colors"
                        title="Edit"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(entry.id)}
                        className="p-1 hover:bg-gray-700 rounded transition-colors text-red-400"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  {entry.description && (
                    <p className="text-sm text-gray-400 mb-2">{entry.description}</p>
                  )}
                  
                  <div className="mb-3">
                    <p className={`text-sm text-gray-300 ${!expandedEntries.has(entry.id) ? 'line-clamp-3' : ''}`}>
                      {expandedEntries.has(entry.id) ? (entry.full_content || entry.content) : entry.content_preview}
                    </p>
                    {entry.word_count > 100 && (
                      <button
                        onClick={() => toggleExpanded(entry.id)}
                        className="mt-2 text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1 transition-colors"
                      >
                        {expandedEntries.has(entry.id) ? (
                          <>
                            <ChevronUp className="w-4 h-4" />
                            Show less
                          </>
                        ) : (
                          <>
                            <ChevronDown className="w-4 h-4" />
                            Show more
                          </>
                        )}
                      </button>
                    )}
                  </div>
                  
                  <div className="flex flex-wrap gap-1 mb-3">
                    {/* Show important tags first, then others */}
                    {entry.tags
                      .filter(tag => !['documentation', 'ai-content-studio', 'reference'].includes(tag))
                      .slice(0, 3)
                      .map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-blue-900/30 border border-blue-700/50 rounded text-xs text-blue-300"
                          title={tag}
                        >
                          #{tag}
                        </span>
                      ))}
                    {entry.tags.filter(tag => !['documentation', 'ai-content-studio', 'reference'].includes(tag)).length > 3 && (
                      <span className="px-2 py-1 text-xs text-gray-500">
                        +{entry.tags.filter(tag => !['documentation', 'ai-content-studio', 'reference'].includes(tag)).length - 3} more
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{entry.word_count} words</span>
                    <div className="flex items-center gap-2">
                      {entry.use_in_generation ? (
                        <CheckCircle className="w-4 h-4 text-green-400" title="Active in AI generation" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-gray-600" title="Not used in AI generation" />
                      )}
                      {entry.times_used > 0 && (
                        <span className="text-blue-400">Used {entry.times_used}x</span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
        
        {/* Pagination */}
        {!loading && knowledge.length > 0 && totalPages > 1 && (
          <div className="flex justify-center items-center gap-2 mt-8">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg hover:bg-gray-700/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            <div className="flex items-center gap-2">
              {/* Show page numbers */}
              {[...Array(Math.min(5, totalPages))].map((_, idx) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = idx + 1;
                } else if (currentPage <= 3) {
                  pageNum = idx + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + idx;
                } else {
                  pageNum = currentPage - 2 + idx;
                }
                
                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`px-3 py-2 rounded-lg transition-colors ${
                      currentPage === pageNum
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-800/50 border border-gray-700 hover:bg-gray-700/50'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
              
              {totalPages > 5 && currentPage < totalPages - 2 && (
                <>
                  <span className="text-gray-500">...</span>
                  <button
                    onClick={() => setCurrentPage(totalPages)}
                    className="px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg hover:bg-gray-700/50 transition-colors"
                  >
                    {totalPages}
                  </button>
                </>
              )}
            </div>
            
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg hover:bg-gray-700/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}
        
        {/* Page info */}
        {!loading && knowledge.length > 0 && (
          <div className="text-center mt-4 text-sm text-gray-400">
            Showing {((currentPage - 1) * itemsPerPage) + 1} - {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems} entries
          </div>
        )}

        {/* Upload Modal */}
        {showUploadModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Add to Knowledge Base</h2>
                <button
                  onClick={() => {
                    setShowUploadModal(false);
                    resetForm();
                  }}
                  className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              {/* Upload Type Selector */}
              <div className="flex gap-2 mb-6">
                <button
                  onClick={() => setUploadType('text')}
                  className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
                    uploadType === 'text'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  <FileText className="w-5 h-5 inline mr-2" />
                  Text/Note
                </button>
                <button
                  onClick={() => setUploadType('file')}
                  className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
                    uploadType === 'file'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  <Upload className="w-5 h-5 inline mr-2" />
                  Upload File
                </button>
              </div>
              
              {/* Form Fields */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Title *</label>
                  <input
                    type="text"
                    value={newKnowledge.title}
                    onChange={(e) => setNewKnowledge({...newKnowledge, title: e.target.value})}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
                    placeholder="Give your knowledge a title..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Description</label>
                  <input
                    type="text"
                    value={newKnowledge.description}
                    onChange={(e) => setNewKnowledge({...newKnowledge, description: e.target.value})}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
                    placeholder="Brief description..."
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Content Type</label>
                    <select
                      value={newKnowledge.content_type}
                      onChange={(e) => setNewKnowledge({...newKnowledge, content_type: e.target.value})}
                      className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
                    >
                      {contentTypes.map(type => (
                        <option key={type.value} value={type.value}>{type.label}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Category</label>
                    <input
                      type="text"
                      value={newKnowledge.category}
                      onChange={(e) => setNewKnowledge({...newKnowledge, category: e.target.value})}
                      className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
                      placeholder="e.g., Marketing, Development"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Tags (comma-separated)</label>
                  <input
                    type="text"
                    value={newKnowledge.tags}
                    onChange={(e) => setNewKnowledge({...newKnowledge, tags: e.target.value})}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
                    placeholder="tag1, tag2, tag3"
                  />
                </div>
                
                {uploadType === 'text' ? (
                  <div>
                    <label className="block text-sm font-medium mb-2">Content *</label>
                    <textarea
                      value={newKnowledge.content}
                      onChange={(e) => setNewKnowledge({...newKnowledge, content: e.target.value})}
                      className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500 min-h-[200px]"
                      placeholder="Enter your content here..."
                    />
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm font-medium mb-2">Upload File</label>
                    <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center hover:border-gray-600 transition-colors">
                      <Upload className="w-12 h-12 mx-auto mb-3 text-gray-500" />
                      <p className="text-gray-400 mb-2">Click to upload or drag and drop</p>
                      <p className="text-xs text-gray-500">
                        Supports: PDF, DOCX, TXT, MD, CSV, XLSX, JSON, HTML, RTF
                      </p>
                      <input
                        ref={fileInputRef}
                        type="file"
                        onChange={handleFileUpload}
                        accept=".pdf,.docx,.doc,.txt,.md,.csv,.xlsx,.xls,.json,.html,.htm,.rtf"
                        className="hidden"
                      />
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="mt-4 px-4 py-2 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
                      >
                        Choose File
                      </button>
                    </div>
                  </div>
                )}
                
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="use_in_generation"
                    checked={newKnowledge.use_in_generation}
                    onChange={(e) => setNewKnowledge({...newKnowledge, use_in_generation: e.target.checked})}
                    className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-blue-500 focus:ring-blue-500"
                  />
                  <label htmlFor="use_in_generation" className="text-sm">
                    Use this knowledge in AI content generation
                  </label>
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowUploadModal(false);
                    resetForm();
                  }}
                  className="px-6 py-2 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={uploadType === 'text' ? handleTextSubmit : () => fileInputRef.current?.click()}
                  disabled={uploading || (uploadType === 'text' && (!newKnowledge.title || !newKnowledge.content))}
                  className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? 'Processing...' : uploadType === 'text' ? 'Add Knowledge' : 'Upload File'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Detail Modal */}
        {detailEntry && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1 min-w-0">
                  <h2 className="text-2xl font-bold mb-2">{detailEntry.title}</h2>
                  {detailEntry.description && (
                    <p className="text-gray-400">{detailEntry.description}</p>
                  )}
                </div>
                <button
                  onClick={() => setDetailEntry(null)}
                  className="p-2 hover:bg-gray-800 rounded-lg transition-colors ml-4"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              {/* Metadata */}
              <div className="flex flex-wrap gap-4 mb-6 text-sm text-gray-400">
                <div className="flex items-center gap-1">
                  <FileText className="w-4 h-4" />
                  <span>{detailEntry.content_type}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Hash className="w-4 h-4" />
                  <span>{detailEntry.word_count} words</span>
                </div>
                {detailEntry.times_used > 0 && (
                  <div className="flex items-center gap-1">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span>Used {detailEntry.times_used} times</span>
                  </div>
                )}
                <div className="flex items-center gap-1">
                  {detailEntry.use_in_generation ? (
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-gray-600" />
                  )}
                  <span>{detailEntry.use_in_generation ? 'Active in AI generation' : 'Not used in AI generation'}</span>
                </div>
              </div>
              
              {/* Tags */}
              {detailEntry.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-6">
                  {detailEntry.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-blue-900/30 border border-blue-700/50 rounded-full text-sm text-blue-300"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
              
              {/* Content */}
              <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
                <div className="prose prose-invert max-w-none">
                  <pre className="whitespace-pre-wrap text-gray-300 font-sans text-sm leading-relaxed">
                    {detailEntry.full_content || detailEntry.content}
                  </pre>
                </div>
              </div>
              
              {/* Actions */}
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => {
                    setSelectedEntry(detailEntry);
                    setDetailEntry(null);
                  }}
                  className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  <Edit className="w-4 h-4 inline mr-2" />
                  Edit
                </button>
                <button
                  onClick={() => setDetailEntry(null)}
                  className="px-4 py-2 bg-blue-500 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonalKnowledge;