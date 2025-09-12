import React, { useState, useEffect, useRef } from 'react';
import { Upload, FileText, Search, Tag, Folder, Download, Trash2, Edit, Plus, X, CheckCircle, AlertCircle, BookOpen, Brain, Hash, ChevronDown, ChevronUp, Eye } from 'lucide-react';
import { useAuthStore } from '../../../store/authStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
      // Fetch documents from content API
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      if (searchQuery) params.append('search', searchQuery);
      params.append('page', currentPage.toString());
      params.append('page_size', itemsPerPage.toString());
      
      const response = await fetch(`${API_BASE_URL}/api/v1/content/documents/?${params}`, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Transform API response to match our interface
        const transformedKnowledge = (data.results || []).map((doc: any) => ({
          id: doc.id,
          title: doc.title,
          description: doc.description || '',
          content_preview: (doc.processed_content || doc.raw_content || '').substring(0, 200),
          full_content: doc.processed_content || doc.raw_content || '',
          content_type: doc.document_type || 'note',
          file_type: doc.mime_type || 'text',
          category: doc.category || 'general',
          tags: doc.tags || [],
          word_count: doc.word_count || 0,
          use_in_generation: doc.is_public !== false,
          times_used: doc.view_count || 0,
          last_used: doc.last_accessed,
          created_at: doc.created_at
        }));
        
        setKnowledge(transformedKnowledge);
        
        // Set stats from API response
        setStats({
          total_entries: data.count || 0,
          total_words: transformedKnowledge.reduce((sum: number, k: any) => sum + k.word_count, 0),
          categories: [...new Set(transformedKnowledge.map((k: any) => k.category))],
          most_used_title: transformedKnowledge.length > 0 ? transformedKnowledge[0].title : null,
          total_embeddings: data.count || 0
        });
        
        // Calculate pagination
        setTotalItems(data.count || 0);
        setTotalPages(Math.ceil((data.count || 0) / itemsPerPage));
      }
    } catch (error) {
      console.error('Error fetching knowledge:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmbeddingsCount = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/dashboard/embeddings-stats/`, {
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
      console.log('Uploading file to:', `${API_BASE_URL}/api/v1/content/documents/upload/`);
      // Note: The documents endpoint might need multipart/form-data
      // For now, we'll read the file content and send as JSON
      const fileContent = await file.text();
      
      const documentData = {
        title: newKnowledge.title || file.name,
        description: newKnowledge.description,
        raw_content: fileContent,
        document_type: newKnowledge.content_type || 'documentation',
        category: newKnowledge.category || 'general',
        tags: newKnowledge.tags.split(',').map(t => t.trim()).filter(t => t),
        is_public: newKnowledge.use_in_generation,
        source: 'upload',
        original_filename: file.name,
        mime_type: file.type
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/content/documents/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(documentData)
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
      // Create document in content API
      const documentData = {
        title: newKnowledge.title,
        description: newKnowledge.description,
        raw_content: newKnowledge.content,
        document_type: newKnowledge.content_type || 'documentation',
        category: newKnowledge.category || 'general',
        tags: newKnowledge.tags.split(',').map(t => t.trim()).filter(t => t),
        is_public: newKnowledge.use_in_generation,
        source: 'manual'
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/content/documents/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(documentData)
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
      const response = await fetch(`${API_BASE_URL}/api/v1/content/documents/${id}/`, {
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
    <div className="min-h-screen p-6" style={{ background: 'var(--gaming-bg-primary)', color: 'var(--gaming-text-primary)' }}>
      <div className="max-w-7xl mx-auto">
        {/* Gaming Neural Header */}
        <div className="mb-8 relative">
          <div className="gaming-matrix-header p-8 text-center relative overflow-hidden">
            <div className="relative z-10">
              <h1 className="text-5xl font-bold mb-3 gaming-text-gradient font-mono uppercase tracking-widest">
                NEURAL KNOWLEDGE BASE
              </h1>
              <div className="flex items-center justify-center gap-4 mb-4">
                <div className="h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent flex-1"></div>
                <span className="text-sm font-mono tracking-[0.3em] px-4" style={{ color: 'var(--gaming-neon-cyan)' }}>
                  &gt;&gt;&gt; ACCESSING MEMORY CORES
                </span>
                <div className="h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent flex-1"></div>
              </div>
              <p className="text-lg font-mono" style={{ color: 'var(--gaming-text-secondary)' }}>
                KNOWLEDGE MATRIX ONLINE • NEURAL PATHWAYS SYNCHRONIZED
              </p>
            </div>
            {/* Animated background grid */}
            <div className="absolute inset-0 gaming-matrix-grid opacity-30"></div>
          </div>
        </div>

        {/* Neural Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {/* Total Entries - Cyan Theme */}
            <div className="gaming-neural-card p-6 group">
              <div className="gaming-border-glow"></div>
              <div className="flex items-center justify-between relative z-10">
                <div>
                  <p className="text-sm font-mono uppercase tracking-wider mb-2" style={{ color: 'var(--gaming-text-muted)' }}>
                    NEURAL ENTRIES
                  </p>
                  <p className="text-3xl font-bold font-mono gaming-text-neon">{stats.total_entries}</p>
                </div>
                <div className="p-3 rounded-lg" style={{ background: 'rgba(0, 255, 255, 0.1)', border: '1px solid var(--gaming-neon-cyan)' }}>
                  <FileText className="w-8 h-8" style={{ color: 'var(--gaming-neon-cyan)' }} />
                </div>
              </div>
            </div>
            
            {/* Total Words - Matrix Green */}
            <div className="gaming-neural-card p-6 group">
              <div className="gaming-border-glow"></div>
              <div className="flex items-center justify-between relative z-10">
                <div>
                  <p className="text-sm font-mono uppercase tracking-wider mb-2" style={{ color: 'var(--gaming-text-muted)' }}>
                    DATA VOLUME
                  </p>
                  <p className="text-3xl font-bold font-mono gaming-text-matrix">{stats.total_words.toLocaleString()}</p>
                </div>
                <div className="p-3 rounded-lg" style={{ background: 'rgba(57, 255, 20, 0.1)', border: '1px solid var(--gaming-neon-green)' }}>
                  <Hash className="w-8 h-8" style={{ color: 'var(--gaming-neon-green)' }} />
                </div>
              </div>
            </div>
            
            {/* Categories - Purple Theme */}
            <div className="gaming-neural-card p-6 group">
              <div className="gaming-border-glow"></div>
              <div className="flex items-center justify-between relative z-10">
                <div>
                  <p className="text-sm font-mono uppercase tracking-wider mb-2" style={{ color: 'var(--gaming-text-muted)' }}>
                    CATEGORIES
                  </p>
                  <p className="text-3xl font-bold font-mono" style={{ color: 'var(--gaming-neon-purple)' }}>{stats.categories.length}</p>
                </div>
                <div className="p-3 rounded-lg" style={{ background: 'rgba(157, 78, 221, 0.1)', border: '1px solid var(--gaming-neon-purple)' }}>
                  <Folder className="w-8 h-8" style={{ color: 'var(--gaming-neon-purple)' }} />
                </div>
              </div>
            </div>
            
            {/* Embeddings - Orange Theme */}
            <div className="gaming-neural-card p-6 group">
              <div className="gaming-border-glow"></div>
              <div className="flex items-center justify-between relative z-10">
                <div>
                  <p className="text-sm font-mono uppercase tracking-wider mb-2" style={{ color: 'var(--gaming-text-muted)' }}>
                    NEURAL LINKS
                  </p>
                  <p className="text-3xl font-bold font-mono" style={{ color: 'var(--gaming-neon-orange)' }}>{stats.total_embeddings || 0}</p>
                </div>
                <div className="p-3 rounded-lg" style={{ background: 'rgba(255, 107, 0, 0.1)', border: '1px solid var(--gaming-neon-orange)' }}>
                  <Brain className="w-8 h-8" style={{ color: 'var(--gaming-neon-orange)' }} />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Neural Command Interface */}
        <div className="flex flex-wrap gap-6 mb-8">
          {/* Add Neural Data Button */}
          <button
            onClick={() => setShowUploadModal(true)}
            className="gaming-btn-active px-8 py-4 rounded-xl font-mono font-bold text-sm uppercase tracking-wider flex items-center gap-3 transition-all duration-300 hover:scale-105"
            style={{
              background: 'var(--gaming-gradient-primary)',
              border: '1px solid var(--gaming-neon-cyan)',
              boxShadow: 'var(--gaming-glow-primary)'
            }}
          >
            <Plus className="w-5 h-5" />
            UPLOAD TO MATRIX
          </button>
          
          {/* Neural Search Interface */}
          <div className="flex-1 min-w-[350px]">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/20 via-purple-400/20 to-cyan-400/20 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm"></div>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: 'var(--gaming-neon-cyan)' }} />
                <input
                  type="text"
                  placeholder=">>> SEARCH NEURAL DATABASE..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="gaming-neural-input w-full pl-12 pr-4 py-4 text-sm font-mono placeholder:font-mono"
                  style={{
                    background: 'var(--gaming-bg-elevated)',
                    border: '1px solid var(--gaming-border)',
                    borderRadius: '12px',
                    color: 'var(--gaming-text-primary)'
                  }}
                />
              </div>
            </div>
          </div>
          
          {/* Category Neural Filter */}
          {stats && stats.categories.length > 0 && (
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm"></div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="gaming-neural-input relative px-4 py-4 font-mono text-sm min-w-[200px] cursor-pointer"
                style={{
                  background: 'var(--gaming-bg-elevated)',
                  border: '1px solid var(--gaming-border)',
                  borderRadius: '12px',
                  color: 'var(--gaming-text-primary)'
                }}
              >
                <option value="" style={{ background: 'var(--gaming-bg-elevated)', color: 'var(--gaming-text-primary)' }}>ALL CATEGORIES</option>
                {stats.categories.map((cat, index) => (
                  <option key={`${cat}-${index}`} value={cat} style={{ background: 'var(--gaming-bg-elevated)', color: 'var(--gaming-text-primary)' }}>
                    {(cat || 'UNCATEGORIZED').toUpperCase()}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Neural Knowledge Grid */}
        {loading ? (
          <div className="flex flex-col items-center justify-center h-64">
            <div className="gaming-loading-matrix mb-4"></div>
            <p className="font-mono text-sm" style={{ color: 'var(--gaming-neon-cyan)' }}>ACCESSING NEURAL NETWORK...</p>
          </div>
        ) : knowledge.length === 0 ? (
          <div className="text-center py-20 gaming-neural-card relative">
            <div className="gaming-border-glow"></div>
            <div className="relative z-10">
              <Brain className="w-20 h-20 mx-auto mb-6" style={{ color: 'var(--gaming-text-muted)' }} />
              <h3 className="text-2xl font-bold font-mono mb-3 uppercase tracking-wider" style={{ color: 'var(--gaming-text-primary)' }}>
                NO NEURAL DATA DETECTED
              </h3>
              <p className="font-mono mb-6" style={{ color: 'var(--gaming-text-secondary)' }}>
                INITIALIZE KNOWLEDGE MATRIX TO BEGIN
              </p>
              <button
                onClick={() => setShowUploadModal(true)}
                className="gaming-btn-active px-8 py-4 rounded-xl font-mono font-bold text-sm uppercase tracking-wider transition-all duration-300 hover:scale-105"
                style={{
                  background: 'var(--gaming-gradient-primary)',
                  border: '1px solid var(--gaming-neon-cyan)',
                  boxShadow: 'var(--gaming-glow-primary)'
                }}
              >
                UPLOAD FIRST ENTRY
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {knowledge.map((entry) => {
              const Icon = contentTypes.find(t => t.value === entry.content_type)?.icon || FileText;
              const isActive = entry.use_in_generation;
              
              return (
                <div
                  key={entry.id}
                  className="gaming-neural-card p-6 group relative overflow-hidden"
                  style={{
                    borderColor: isActive ? 'var(--gaming-neon-green)' : 'var(--gaming-border)'
                  }}
                >
                  <div className="gaming-border-glow"></div>
                  
                  {/* Neural Header */}
                  <div className="flex items-start justify-between mb-4 relative z-10">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="p-2 rounded-lg" style={{ 
                        background: isActive ? 'rgba(57, 255, 20, 0.1)' : 'rgba(0, 255, 255, 0.1)', 
                        border: `1px solid ${isActive ? 'var(--gaming-neon-green)' : 'var(--gaming-neon-cyan)'}` 
                      }}>
                        <Icon className="w-5 h-5" style={{ 
                          color: isActive ? 'var(--gaming-neon-green)' : 'var(--gaming-neon-cyan)' 
                        }} />
                      </div>
                      <h3 className="font-bold font-mono text-sm uppercase tracking-wide truncate flex-1" 
                          title={entry.title}
                          style={{ color: 'var(--gaming-text-primary)' }}>
                        {entry.title}
                      </h3>
                    </div>
                    
                    {/* Action Controls */}
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all duration-300">
                      <button
                        onClick={() => setDetailEntry(entry)}
                        className="p-2 rounded-lg transition-all duration-200 hover:scale-110"
                        style={{ 
                          background: 'rgba(0, 255, 255, 0.1)', 
                          border: '1px solid var(--gaming-neon-cyan)',
                          color: 'var(--gaming-neon-cyan)'
                        }}
                        title="View Neural Data"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setSelectedEntry(entry)}
                        className="p-2 rounded-lg transition-all duration-200 hover:scale-110"
                        style={{ 
                          background: 'rgba(157, 78, 221, 0.1)', 
                          border: '1px solid var(--gaming-neon-purple)',
                          color: 'var(--gaming-neon-purple)'
                        }}
                        title="Modify Data"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(entry.id)}
                        className="p-2 rounded-lg transition-all duration-200 hover:scale-110"
                        style={{ 
                          background: 'rgba(255, 20, 147, 0.1)', 
                          border: '1px solid var(--gaming-neon-pink)',
                          color: 'var(--gaming-neon-pink)'
                        }}
                        title="Delete Entry"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  {/* Description */}
                  {entry.description && (
                    <p className="text-sm font-mono mb-3" style={{ color: 'var(--gaming-text-secondary)' }}>
                      {entry.description}
                    </p>
                  )}
                  
                  {/* Content Preview */}
                  <div className="mb-4">
                    <p className={`text-sm font-mono leading-relaxed ${!expandedEntries.has(entry.id) ? 'line-clamp-3' : ''}`}
                       style={{ color: 'var(--gaming-text-secondary)' }}>
                      {expandedEntries.has(entry.id) ? (entry.full_content || entry.content) : entry.content_preview}
                    </p>
                    {entry.word_count > 100 && (
                      <button
                        onClick={() => toggleExpanded(entry.id)}
                        className="mt-2 text-sm flex items-center gap-1 transition-all duration-200 hover:scale-105 font-mono"
                        style={{ color: 'var(--gaming-neon-cyan)' }}
                      >
                        {expandedEntries.has(entry.id) ? (
                          <>
                            <ChevronUp className="w-4 h-4" />
                            COLLAPSE DATA
                          </>
                        ) : (
                          <>
                            <ChevronDown className="w-4 h-4" />
                            EXPAND DATA
                          </>
                        )}
                      </button>
                    )}
                  </div>
                  
                  {/* Neural Tags */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {entry.tags
                      .filter(tag => !['documentation', 'ai-content-studio', 'reference'].includes(tag))
                      .slice(0, 3)
                      .map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 rounded-full text-xs font-mono font-bold uppercase tracking-wider"
                          style={{
                            background: 'rgba(0, 255, 255, 0.1)',
                            border: '1px solid var(--gaming-neon-cyan)',
                            color: 'var(--gaming-neon-cyan)'
                          }}
                          title={tag}
                        >
                          #{tag}
                        </span>
                      ))}
                    {entry.tags.filter(tag => !['documentation', 'ai-content-studio', 'reference'].includes(tag)).length > 3 && (
                      <span className="px-3 py-1 text-xs font-mono" style={{ color: 'var(--gaming-text-muted)' }}>
                        +{entry.tags.filter(tag => !['documentation', 'ai-content-studio', 'reference'].includes(tag)).length - 3} MORE
                      </span>
                    )}
                  </div>
                  
                  {/* Neural Status */}
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span style={{ color: 'var(--gaming-text-muted)' }}>
                      {entry.word_count} WORDS
                    </span>
                    <div className="flex items-center gap-3">
                      {entry.use_in_generation ? (
                        <div className="gaming-status gaming-status-running px-2 py-1 rounded-full">
                          <div className="gaming-pulse-dot"></div>
                          ACTIVE
                        </div>
                      ) : (
                        <div className="gaming-status px-2 py-1 rounded-full">
                          INACTIVE
                        </div>
                      )}
                      {entry.times_used > 0 && (
                        <span style={{ color: 'var(--gaming-neon-green)' }}>
                          USED {entry.times_used}X
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
        
        {/* Neural Pagination */}
        {!loading && knowledge.length > 0 && totalPages > 1 && (
          <div className="flex justify-center items-center gap-4 mt-12">
            {/* Previous Page */}
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-6 py-3 rounded-xl font-mono font-bold text-sm uppercase tracking-wider transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              style={{
                background: currentPage === 1 ? 'var(--gaming-bg-elevated)' : 'var(--gaming-bg-elevated)',
                border: currentPage === 1 ? '1px solid var(--gaming-border)' : '1px solid var(--gaming-neon-cyan)',
                color: currentPage === 1 ? 'var(--gaming-text-muted)' : 'var(--gaming-neon-cyan)'
              }}
            >
              &lt;&lt; PREV
            </button>
            
            {/* Page Numbers */}
            <div className="flex items-center gap-3">
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
                
                const isActive = currentPage === pageNum;
                
                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`w-12 h-12 rounded-xl font-mono font-bold text-sm transition-all duration-300 hover:scale-110 ${
                      isActive ? 'gaming-btn-active' : ''
                    }`}
                    style={{
                      background: isActive 
                        ? 'var(--gaming-gradient-primary)' 
                        : 'var(--gaming-bg-elevated)',
                      border: isActive 
                        ? '1px solid var(--gaming-neon-cyan)' 
                        : '1px solid var(--gaming-border)',
                      color: isActive 
                        ? 'var(--gaming-text-primary)' 
                        : 'var(--gaming-text-secondary)',
                      boxShadow: isActive 
                        ? 'var(--gaming-glow-primary)' 
                        : 'none'
                    }}
                  >
                    {pageNum}
                  </button>
                );
              })}
              
              {/* Ellipsis and Last Page */}
              {totalPages > 5 && currentPage < totalPages - 2 && (
                <>
                  <span className="font-mono text-lg" style={{ color: 'var(--gaming-text-muted)' }}>...</span>
                  <button
                    onClick={() => setCurrentPage(totalPages)}
                    className="w-12 h-12 rounded-xl font-mono font-bold text-sm transition-all duration-300 hover:scale-110"
                    style={{
                      background: 'var(--gaming-bg-elevated)',
                      border: '1px solid var(--gaming-border)',
                      color: 'var(--gaming-text-secondary)'
                    }}
                  >
                    {totalPages}
                  </button>
                </>
              )}
            </div>
            
            {/* Next Page */}
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-6 py-3 rounded-xl font-mono font-bold text-sm uppercase tracking-wider transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              style={{
                background: currentPage === totalPages ? 'var(--gaming-bg-elevated)' : 'var(--gaming-bg-elevated)',
                border: currentPage === totalPages ? '1px solid var(--gaming-border)' : '1px solid var(--gaming-neon-cyan)',
                color: currentPage === totalPages ? 'var(--gaming-text-muted)' : 'var(--gaming-neon-cyan)'
              }}
            >
              NEXT &gt;&gt;
            </button>
          </div>
        )}
        
        {/* Neural Data Statistics */}
        {!loading && knowledge.length > 0 && (
          <div className="text-center mt-6">
            <p className="font-mono text-sm uppercase tracking-wider" style={{ color: 'var(--gaming-text-muted)' }}>
              NEURAL DISPLAY: {((currentPage - 1) * itemsPerPage) + 1} - {Math.min(currentPage * itemsPerPage, totalItems)} OF {totalItems} ENTRIES
            </p>
          </div>
        )}

        {/* Neural Upload Interface */}
        {showUploadModal && (
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4" 
               style={{ background: 'var(--gaming-bg-overlay)', backdropFilter: 'blur(20px)' }}>
            <div className="gaming-neural-card max-w-2xl w-full max-h-[90vh] overflow-y-auto relative">
              <div className="gaming-border-glow"></div>
              
              {/* Neural Header */}
              <div className="flex items-center justify-between mb-8 relative z-10 p-6 pb-0">
                <div>
                  <h2 className="text-3xl font-bold font-mono uppercase tracking-wider gaming-text-gradient mb-2">
                    NEURAL DATA UPLOAD
                  </h2>
                  <p className="font-mono text-sm" style={{ color: 'var(--gaming-text-secondary)' }}>
                    &gt;&gt;&gt; INITIALIZING KNOWLEDGE MATRIX PROTOCOL
                  </p>
                </div>
                <button
                  onClick={() => {
                    setShowUploadModal(false);
                    resetForm();
                  }}
                  className="p-3 rounded-lg transition-all duration-200 hover:scale-110"
                  style={{ 
                    background: 'rgba(255, 20, 147, 0.1)', 
                    border: '1px solid var(--gaming-neon-pink)',
                    color: 'var(--gaming-neon-pink)'
                  }}
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="p-6 pt-0 relative z-10">
              
                {/* Neural Data Type Selector */}
                <div className="flex gap-4 mb-8">
                  <button
                    onClick={() => setUploadType('text')}
                    className={`flex-1 py-4 px-6 rounded-xl font-mono font-bold text-sm uppercase tracking-wider transition-all duration-300 flex items-center justify-center gap-3 ${
                      uploadType === 'text'
                        ? 'gaming-btn-active'
                        : ''
                    }`}
                    style={{
                      background: uploadType === 'text' 
                        ? 'var(--gaming-gradient-primary)' 
                        : 'var(--gaming-bg-elevated)',
                      border: uploadType === 'text' 
                        ? '1px solid var(--gaming-neon-cyan)' 
                        : '1px solid var(--gaming-border)',
                      color: uploadType === 'text' 
                        ? 'var(--gaming-text-primary)' 
                        : 'var(--gaming-text-muted)',
                      boxShadow: uploadType === 'text' 
                        ? 'var(--gaming-glow-primary)' 
                        : 'none'
                    }}
                  >
                    <FileText className="w-5 h-5" />
                    NEURAL TEXT
                  </button>
                  <button
                    onClick={() => setUploadType('file')}
                    className={`flex-1 py-4 px-6 rounded-xl font-mono font-bold text-sm uppercase tracking-wider transition-all duration-300 flex items-center justify-center gap-3 ${
                      uploadType === 'file'
                        ? 'gaming-btn-active'
                        : ''
                    }`}
                    style={{
                      background: uploadType === 'file' 
                        ? 'var(--gaming-gradient-primary)' 
                        : 'var(--gaming-bg-elevated)',
                      border: uploadType === 'file' 
                        ? '1px solid var(--gaming-neon-cyan)' 
                        : '1px solid var(--gaming-border)',
                      color: uploadType === 'file' 
                        ? 'var(--gaming-text-primary)' 
                        : 'var(--gaming-text-muted)',
                      boxShadow: uploadType === 'file' 
                        ? 'var(--gaming-glow-primary)' 
                        : 'none'
                    }}
                  >
                    <Upload className="w-5 h-5" />
                    DATA FILE
                  </button>
                </div>
              
                {/* Neural Form Fields */}
                <div className="space-y-6">
                  {/* Neural Title */}
                  <div>
                    <label className="block text-sm font-mono font-bold uppercase tracking-wider mb-3" 
                           style={{ color: 'var(--gaming-text-primary)' }}>
                      NEURAL IDENTIFIER *
                    </label>
                    <input
                      type="text"
                      value={newKnowledge.title}
                      onChange={(e) => setNewKnowledge({...newKnowledge, title: e.target.value})}
                      className="gaming-neural-input w-full px-4 py-3 font-mono"
                      placeholder=">>> ENTER DATA IDENTIFIER..."
                    />
                  </div>
                  
                  {/* Neural Description */}
                  <div>
                    <label className="block text-sm font-mono font-bold uppercase tracking-wider mb-3" 
                           style={{ color: 'var(--gaming-text-primary)' }}>
                      DATA DESCRIPTION
                    </label>
                    <input
                      type="text"
                      value={newKnowledge.description}
                      onChange={(e) => setNewKnowledge({...newKnowledge, description: e.target.value})}
                      className="gaming-neural-input w-full px-4 py-3 font-mono"
                      placeholder=">>> BRIEF NEURAL SUMMARY..."
                    />
                  </div>
                
                  {/* Neural Classification Grid */}
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-mono font-bold uppercase tracking-wider mb-3" 
                             style={{ color: 'var(--gaming-text-primary)' }}>
                        DATA TYPE
                      </label>
                      <select
                        value={newKnowledge.content_type}
                        onChange={(e) => setNewKnowledge({...newKnowledge, content_type: e.target.value})}
                        className="gaming-neural-input w-full px-4 py-3 font-mono cursor-pointer"
                      >
                        {contentTypes.map(type => (
                          <option key={type.value} value={type.value} 
                                  style={{ background: 'var(--gaming-bg-elevated)', color: 'var(--gaming-text-primary)' }}>
                            {type.label.toUpperCase()}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-mono font-bold uppercase tracking-wider mb-3" 
                             style={{ color: 'var(--gaming-text-primary)' }}>
                        NEURAL CATEGORY
                      </label>
                      <input
                        type="text"
                        value={newKnowledge.category}
                        onChange={(e) => setNewKnowledge({...newKnowledge, category: e.target.value})}
                        className="gaming-neural-input w-full px-4 py-3 font-mono"
                        placeholder=">>> CLASSIFICATION..."
                      />
                    </div>
                  </div>
                
                  {/* Neural Tags */}
                  <div>
                    <label className="block text-sm font-mono font-bold uppercase tracking-wider mb-3" 
                           style={{ color: 'var(--gaming-text-primary)' }}>
                      NEURAL TAGS
                    </label>
                    <input
                      type="text"
                      value={newKnowledge.tags}
                      onChange={(e) => setNewKnowledge({...newKnowledge, tags: e.target.value})}
                      className="gaming-neural-input w-full px-4 py-3 font-mono"
                      placeholder=">>> tag1, tag2, tag3"
                    />
                  </div>
                
                  {/* Neural Content Input */}
                  {uploadType === 'text' ? (
                    <div>
                      <label className="block text-sm font-mono font-bold uppercase tracking-wider mb-3" 
                             style={{ color: 'var(--gaming-text-primary)' }}>
                        NEURAL CONTENT *
                      </label>
                      <textarea
                        value={newKnowledge.content}
                        onChange={(e) => setNewKnowledge({...newKnowledge, content: e.target.value})}
                        className="gaming-neural-input w-full px-4 py-4 font-mono min-h-[200px] resize-none"
                        placeholder=">>> ENTER NEURAL DATA CONTENT..."
                      />
                    </div>
                  ) : (
                    <div>
                      <label className="block text-sm font-mono font-bold uppercase tracking-wider mb-3" 
                             style={{ color: 'var(--gaming-text-primary)' }}>
                        DATA FILE UPLOAD
                      </label>
                      <div className="gaming-neural-card p-8 text-center group cursor-pointer" 
                           onClick={() => fileInputRef.current?.click()}
                           style={{ border: '2px dashed var(--gaming-border)' }}>
                        <div className="gaming-border-glow"></div>
                        <div className="relative z-10">
                          <div className="p-4 rounded-xl mx-auto mb-4 w-fit" 
                               style={{ background: 'rgba(0, 255, 255, 0.1)', border: '1px solid var(--gaming-neon-cyan)' }}>
                            <Upload className="w-12 h-12" style={{ color: 'var(--gaming-neon-cyan)' }} />
                          </div>
                          <p className="font-mono font-bold uppercase tracking-wider mb-2" 
                             style={{ color: 'var(--gaming-text-primary)' }}>
                            NEURAL FILE INTERFACE
                          </p>
                          <p className="text-sm font-mono mb-4" style={{ color: 'var(--gaming-text-secondary)' }}>
                            CLICK TO UPLOAD OR DRAG AND DROP
                          </p>
                          <p className="text-xs font-mono" style={{ color: 'var(--gaming-text-muted)' }}>
                            SUPPORTED: PDF, DOCX, TXT, MD, CSV, XLSX, JSON, HTML, RTF
                          </p>
                          <input
                            ref={fileInputRef}
                            type="file"
                            onChange={handleFileUpload}
                            accept=".pdf,.docx,.doc,.txt,.md,.csv,.xlsx,.xls,.json,.html,.htm,.rtf"
                            className="hidden"
                          />
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              fileInputRef.current?.click();
                            }}
                            className="mt-6 px-6 py-3 rounded-xl font-mono font-bold text-sm uppercase tracking-wider transition-all duration-300 hover:scale-105"
                            style={{
                              background: 'var(--gaming-bg-elevated)',
                              border: '1px solid var(--gaming-neon-cyan)',
                              color: 'var(--gaming-neon-cyan)'
                            }}
                          >
                            SELECT FILE
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                
                  {/* Neural AI Integration Toggle */}
                  <div className="flex items-center gap-4 p-4 rounded-xl" 
                       style={{ background: 'rgba(0, 255, 255, 0.05)', border: '1px solid var(--gaming-border)' }}>
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        id="use_in_generation"
                        checked={newKnowledge.use_in_generation}
                        onChange={(e) => setNewKnowledge({...newKnowledge, use_in_generation: e.target.checked})}
                        className="w-5 h-5 rounded" 
                        style={{
                          accentColor: 'var(--gaming-neon-cyan)',
                          backgroundColor: newKnowledge.use_in_generation ? 'var(--gaming-neon-cyan)' : 'var(--gaming-bg-elevated)'
                        }}
                      />
                      <label htmlFor="use_in_generation" className="font-mono font-bold text-sm uppercase tracking-wider" 
                             style={{ color: 'var(--gaming-text-primary)' }}>
                        ENABLE AI NEURAL INTEGRATION
                      </label>
                    </div>
                    <div className={`gaming-status px-3 py-1 rounded-full ${
                      newKnowledge.use_in_generation ? 'gaming-status-running' : ''
                    }`}>
                      {newKnowledge.use_in_generation ? (
                        <><div className="gaming-pulse-dot"></div>ACTIVE</>
                      ) : (
                        'INACTIVE'
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
                {/* Neural Command Buttons */}
                <div className="flex justify-end gap-4 mt-8">
                  <button
                    onClick={() => {
                      setShowUploadModal(false);
                      resetForm();
                    }}
                    className="px-8 py-4 rounded-xl font-mono font-bold text-sm uppercase tracking-wider transition-all duration-300 hover:scale-105"
                    style={{
                      background: 'var(--gaming-bg-elevated)',
                      border: '1px solid var(--gaming-border)',
                      color: 'var(--gaming-text-muted)'
                    }}
                  >
                    ABORT UPLOAD
                  </button>
                  <button
                    onClick={uploadType === 'text' ? handleTextSubmit : () => fileInputRef.current?.click()}
                    disabled={uploading || (uploadType === 'text' && (!newKnowledge.title || !newKnowledge.content))}
                    className="gaming-btn-active px-8 py-4 rounded-xl font-mono font-bold text-sm uppercase tracking-wider transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3"
                    style={{
                      background: uploading ? 'var(--gaming-bg-elevated)' : 'var(--gaming-gradient-primary)',
                      border: '1px solid var(--gaming-neon-cyan)',
                      boxShadow: uploading ? 'none' : 'var(--gaming-glow-primary)'
                    }}
                  >
                    {uploading && <div className="gaming-loading-matrix w-4 h-4"></div>}
                    {uploading 
                      ? 'PROCESSING...' 
                      : uploadType === 'text' 
                        ? 'UPLOAD TO MATRIX' 
                        : 'SELECT DATA FILE'
                    }
                  </button>
                </div>
              </div>
            </div>
        )}

        {/* Neural Data Viewer */}
        {detailEntry && (
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4" 
               style={{ background: 'var(--gaming-bg-overlay)', backdropFilter: 'blur(20px)' }}>
            <div className="gaming-neural-card max-w-6xl w-full max-h-[90vh] overflow-y-auto relative">
              <div className="gaming-border-glow"></div>
              
              {/* Neural Header */}
              <div className="flex items-start justify-between mb-8 relative z-10 p-8 pb-0">
                <div className="flex-1 min-w-0">
                  <h2 className="text-3xl font-bold font-mono uppercase tracking-wider gaming-text-gradient mb-3">
                    {detailEntry.title}
                  </h2>
                  {detailEntry.description && (
                    <p className="font-mono text-lg" style={{ color: 'var(--gaming-text-secondary)' }}>
                      {detailEntry.description}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => setDetailEntry(null)}
                  className="p-3 rounded-lg transition-all duration-200 hover:scale-110 ml-6"
                  style={{ 
                    background: 'rgba(255, 20, 147, 0.1)', 
                    border: '1px solid var(--gaming-neon-pink)',
                    color: 'var(--gaming-neon-pink)'
                  }}
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="p-8 pt-0 relative z-10">
              
                {/* Neural Metadata Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                  <div className="gaming-neural-card p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="w-5 h-5" style={{ color: 'var(--gaming-neon-cyan)' }} />
                      <span className="font-mono text-xs uppercase tracking-wider" 
                            style={{ color: 'var(--gaming-text-muted)' }}>TYPE</span>
                    </div>
                    <p className="font-mono font-bold" style={{ color: 'var(--gaming-text-primary)' }}>
                      {detailEntry.content_type.toUpperCase()}
                    </p>
                  </div>
                  
                  <div className="gaming-neural-card p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Hash className="w-5 h-5" style={{ color: 'var(--gaming-neon-green)' }} />
                      <span className="font-mono text-xs uppercase tracking-wider" 
                            style={{ color: 'var(--gaming-text-muted)' }}>WORDS</span>
                    </div>
                    <p className="font-mono font-bold" style={{ color: 'var(--gaming-text-primary)' }}>
                      {detailEntry.word_count.toLocaleString()}
                    </p>
                  </div>
                  
                  {detailEntry.times_used > 0 && (
                    <div className="gaming-neural-card p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle className="w-5 h-5" style={{ color: 'var(--gaming-neon-green)' }} />
                        <span className="font-mono text-xs uppercase tracking-wider" 
                              style={{ color: 'var(--gaming-text-muted)' }}>USAGE</span>
                      </div>
                      <p className="font-mono font-bold" style={{ color: 'var(--gaming-text-primary)' }}>
                        {detailEntry.times_used} TIMES
                      </p>
                    </div>
                  )}
                  
                  <div className="gaming-neural-card p-4">
                    <div className="flex items-center gap-2 mb-2">
                      {detailEntry.use_in_generation ? (
                        <CheckCircle className="w-5 h-5" style={{ color: 'var(--gaming-neon-green)' }} />
                      ) : (
                        <AlertCircle className="w-5 h-5" style={{ color: 'var(--gaming-text-muted)' }} />
                      )}
                      <span className="font-mono text-xs uppercase tracking-wider" 
                            style={{ color: 'var(--gaming-text-muted)' }}>AI STATUS</span>
                    </div>
                    <div className={`gaming-status px-2 py-1 rounded-full ${
                      detailEntry.use_in_generation ? 'gaming-status-running' : ''
                    }`}>
                      {detailEntry.use_in_generation ? (
                        <><div className="gaming-pulse-dot"></div>ACTIVE</>
                      ) : (
                        'INACTIVE'
                      )}
                    </div>
                  </div>
                </div>
              
                {/* Neural Tags */}
                {detailEntry.tags.length > 0 && (
                  <div className="mb-8">
                    <h3 className="font-mono font-bold text-sm uppercase tracking-wider mb-4" 
                        style={{ color: 'var(--gaming-text-primary)' }}>
                      NEURAL TAGS
                    </h3>
                    <div className="flex flex-wrap gap-3">
                      {detailEntry.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-4 py-2 rounded-full font-mono font-bold text-sm uppercase tracking-wider"
                          style={{
                            background: 'rgba(0, 255, 255, 0.1)',
                            border: '1px solid var(--gaming-neon-cyan)',
                            color: 'var(--gaming-neon-cyan)'
                          }}
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              
                {/* Neural Content Display */}
                <div className="mb-8">
                  <h3 className="font-mono font-bold text-sm uppercase tracking-wider mb-4" 
                      style={{ color: 'var(--gaming-text-primary)' }}>
                    NEURAL CONTENT DATA
                  </h3>
                  <div className="gaming-neural-card p-6 relative">
                    <div className="gaming-border-glow"></div>
                    <div className="relative z-10">
                      <div className="max-w-none">
                        <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed" 
                             style={{ color: 'var(--gaming-text-secondary)' }}>
                          {detailEntry.full_content || detailEntry.content}
                        </pre>
                      </div>
                    </div>
                  </div>
                </div>
              
                {/* Neural Command Actions */}
                <div className="flex justify-end gap-4">
                  <button
                    onClick={() => {
                      setSelectedEntry(detailEntry);
                      setDetailEntry(null);
                    }}
                    className="px-6 py-3 rounded-xl font-mono font-bold text-sm uppercase tracking-wider transition-all duration-300 hover:scale-105 flex items-center gap-3"
                    style={{
                      background: 'var(--gaming-bg-elevated)',
                      border: '1px solid var(--gaming-neon-purple)',
                      color: 'var(--gaming-neon-purple)'
                    }}
                  >
                    <Edit className="w-5 h-5" />
                    MODIFY DATA
                  </button>
                  <button
                    onClick={() => setDetailEntry(null)}
                    className="gaming-btn-active px-6 py-3 rounded-xl font-mono font-bold text-sm uppercase tracking-wider transition-all duration-300 hover:scale-105"
                    style={{
                      background: 'var(--gaming-gradient-primary)',
                      border: '1px solid var(--gaming-neon-cyan)',
                      boxShadow: 'var(--gaming-glow-primary)'
                    }}
                  >
                    CLOSE VIEWER
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonalKnowledge;