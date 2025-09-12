import { useState, useEffect, useRef } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { getAuthHeaderWithDevFallback } from '../../../utils/auth';
import { 
  BookOpenIcon,
  DocumentArrowUpIcon,
  LinkIcon,
  VideoCameraIcon,
  DocumentTextIcon,
  PlayIcon,
  PlusIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  SparklesIcon,
  XMarkIcon,
  PencilIcon,
  EyeIcon,
  PhotoIcon,
  CloudArrowUpIcon,
} from '@heroicons/react/24/outline';
import { toast } from 'sonner';
import { researchBooksService } from '../../../services/research-books.service';
import type { ResearchSource, Book, BookGenerationOptions, DocumentIngest } from '../../../services/research-books.service';
import { Logger } from '../../../utils/logger';

type TabType = 'sources' | 'outline' | 'generate' | 'library' | 'analytics';

export function ResearchBooks() {
  const [activeTab, setActiveTab] = useState<TabType>('sources');
  const [sources, setSources] = useState<ResearchSource[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [documents, setDocuments] = useState<DocumentIngest[]>([]);
  const [currentBook, setCurrentBook] = useState<Book | null>(null);
  const [editingChapter, setEditingChapter] = useState<Chapter | null>(null);
  const [chapterContent, setChapterContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedImages, setSelectedImages] = useState<string[]>([]);
  const [imagePrompt, setImagePrompt] = useState('');
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [showImageModal, setShowImageModal] = useState(false);
  
  // Form states
  const [bookTitle, setBookTitle] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [youtubeInput, setYoutubeInput] = useState('');
  const [textInput, setTextInput] = useState('');
  const [selectedDocuments, setSelectedDocuments] = useState<Set<string>>(new Set());
  const [bookOptions, setBookOptions] = useState<BookGenerationOptions>({
    include_citations: true,
    chapter_count: 10,
    words_per_chapter: 1500,
    genre: 'technical',
    target_audience: 'general',
    tone: 'professional',
    language: 'en'
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  const tabs = [
    { id: 'sources', name: 'Research Sources', icon: DocumentTextIcon },
    { id: 'outline', name: 'Book Outline', icon: BookOpenIcon },
    { id: 'generate', name: 'Generate Book', icon: SparklesIcon },
    { id: 'library', name: 'Book Library', icon: BookOpenIcon },
    { id: 'analytics', name: 'Analytics', icon: ChartBarIcon },
  ] as const;

  useEffect(() => {
    Logger.component('ResearchBooks', 'Mounting', { activeTab });
    loadBooks();
    loadDocuments();
    
    return () => {
      Logger.component('ResearchBooks', 'Unmounting');
    };
  }, []);

  const loadBooks = async () => {
    try {
      Logger.api('GET', '/api/research/books/', { loading: true });
      const booksData = await researchBooksService.getBooks();
      Logger.apiResponse('/api/research/books/', { count: booksData.length });
      setBooks(booksData);
      Logger.state('ResearchBooks', 'Books loaded', { count: booksData.length });
    } catch (error) {
      Logger.error('ResearchBooks.loadBooks', error);
    }
  };

  const loadDocuments = async () => {
    try {
      Logger.api('GET', '/api/research/documents/', { loading: true });
      const docsData = await researchBooksService.getDocuments();
      Logger.apiResponse('/api/research/documents/', { count: docsData.length });
      setDocuments(docsData);
      Logger.state('ResearchBooks', 'Documents loaded', { count: docsData.length });
    } catch (error) {
      Logger.error('ResearchBooks.loadDocuments', error);
    }
  };

  const deleteDocument = async (doc: DocumentIngest) => {
    if (!confirm(`Are you sure you want to delete "${doc.filename}"? This action cannot be undone.`)) {
      return;
    }

    try {
      Logger.api('DELETE', `/api/research/documents/${doc.id}/`);
      await researchBooksService.deleteDocument(doc.id);
      
      // Remove from local state
      setDocuments(prev => prev.filter(d => d.id !== doc.id));
      
      // Remove from selected documents if it was selected
      setSelectedDocuments(prev => {
        const newSelection = new Set(prev);
        newSelection.delete(doc.id);
        return newSelection;
      });
      
      toast.success('Document deleted successfully');
      Logger.state('ResearchBooks', 'Document deleted', { documentId: doc.id, filename: doc.filename });
    } catch (error: any) {
      Logger.error('ResearchBooks.deleteDocument', error);
      toast.error(error.userMessage || 'Failed to delete document');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    Logger.event('ResearchBooks', 'File upload started', { fileName: file.name, size: file.size });

    // Supported file types
    const supportedTypes = [
      'application/pdf',
      'text/plain',
      'text/markdown',
      'text/csv',
      'application/json',
      'text/html',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
      'application/msword', // .doc
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
      'application/vnd.ms-excel', // .xls
      'text/rtf',
      'application/rtf'
    ];
    
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    const validExtensions = ['pdf', 'txt', 'md', 'csv', 'json', 'html', 'docx', 'doc', 'xlsx', 'xls', 'rtf'];
    
    // Check by MIME type or file extension
    if (!supportedTypes.includes(file.type) && !validExtensions.includes(fileExtension || '')) {
      Logger.warn('ResearchBooks', 'Invalid file type', { type: file.type, extension: fileExtension });
      toast.error(`Please upload a supported file type: ${validExtensions.join(', ')}`);
      return;
    }

    setIsUploading(true);
    try {
      Logger.api('POST', '/api/research/documents/ingest/', { fileName: file.name });
      const result = await researchBooksService.ingestDocument(file);
      setDocuments(prev => [result, ...prev]);
      
      // Add as a source
      // Determine source type based on file extension
      const fileExtension = file.name.split('.').pop()?.toLowerCase();
      let sourceType = 'document';
      if (fileExtension === 'pdf') sourceType = 'pdf';
      else if (['txt', 'md'].includes(fileExtension || '')) sourceType = 'text';
      else if (fileExtension === 'csv') sourceType = 'csv';
      else if (['doc', 'docx'].includes(fileExtension || '')) sourceType = 'doc';
      else if (['xls', 'xlsx'].includes(fileExtension || '')) sourceType = 'spreadsheet';
      
      setSources(prev => [...prev, {
        type: sourceType,
        content: result.content_preview,
        title: result.filename,
        metadata: { 
          document_id: result.id,
          pages: result.pages,
          word_count: result.word_count 
        }
      }]);
      
      toast.success('PDF uploaded and processed successfully');
      Logger.state('ResearchBooks', 'PDF processed', { documentId: result.id });
    } catch (error: any) {
      Logger.error('ResearchBooks.handleFileUpload', error);
      toast.error(error.userMessage || 'Failed to upload PDF');
    } finally {
      setIsUploading(false);
    }
  };

  const addUrlSource = async () => {
    if (!urlInput.trim()) return;
    
    Logger.event('ResearchBooks', 'Adding URL source', { url: urlInput });
    
    try {
      Logger.api('POST', '/api/research/extract-url/', { url: urlInput });
      const source = await researchBooksService.extractFromUrl(urlInput);
      // Ensure the original URL is stored in metadata
      source.metadata = { 
        ...source.metadata, 
        source_url: urlInput 
      };
      setSources(prev => [...prev, source]);
      setUrlInput('');
      toast.success('URL content extracted successfully');
      Logger.state('ResearchBooks', 'URL source added', { url: urlInput });
    } catch (error: any) {
      Logger.error('ResearchBooks.addUrlSource', error);
      toast.error(error.userMessage || 'Failed to extract URL content');
    }
  };

  const addYoutubeSource = async () => {
    if (!youtubeInput.trim()) return;
    
    Logger.event('ResearchBooks', 'Adding YouTube source', { url: youtubeInput });
    
    try {
      Logger.api('POST', '/api/research/extract-youtube/', { url: youtubeInput });
      const source = await researchBooksService.extractFromYoutube(youtubeInput);
      // Ensure the original URL is stored in metadata
      source.metadata = { 
        ...source.metadata, 
        source_url: youtubeInput 
      };
      setSources(prev => [...prev, source]);
      setYoutubeInput('');
      toast.success('YouTube transcript extracted successfully');
      Logger.state('ResearchBooks', 'YouTube source added', { url: youtubeInput });
    } catch (error: any) {
      Logger.error('ResearchBooks.addYoutubeSource', error);
      toast.error(error.userMessage || 'Failed to extract YouTube content');
    }
  };

  const addTextSource = () => {
    if (!textInput.trim()) return;
    
    const source: ResearchSource = {
      type: 'text',
      content: textInput,
      title: `Text Input ${sources.length + 1}`,
    };
    
    setSources(prev => [...prev, source]);
    setTextInput('');
    toast.success('Text source added');
  };

  const removeSource = (index: number) => {
    setSources(prev => prev.filter((_, i) => i !== index));
  };

  const generateBook = async () => {
    if (!bookTitle.trim()) {
      toast.error('Please enter a book title');
      return;
    }

    if (sources.length === 0 && selectedDocuments.size === 0) {
      toast.error('Please add at least one research source or select existing documents');
      return;
    }

    setIsGenerating(true);
    try {
      Logger.event('ResearchBooks', 'Book generation started', { 
        title: bookTitle, 
        newSources: sources.length, 
        selectedDocuments: selectedDocuments.size,
        options: bookOptions 
      });

      const documentIds = Array.from(selectedDocuments);
      const book = await researchBooksService.createFromResearch(bookTitle, sources, bookOptions, documentIds);
      
      setCurrentBook(book);
      setBooks(prev => [book, ...prev]);
      setActiveTab('generate');
      
      toast.success('Book generation started! This may take several minutes.');
      Logger.state('ResearchBooks', 'Book generation started', { bookId: book.id, title: book.title });
    } catch (error: any) {
      Logger.error('ResearchBooks.generateBook', error);
      toast.error(error.userMessage || 'Failed to start book generation');
    } finally {
      setIsGenerating(false);
    }
  };

  const exportBook = async (book: Book, format: 'pdf' | 'docx' | 'epub' | 'txt') => {
    try {
      const blob = await researchBooksService.exportBook(book.id, format);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${book.title}.${format}`;
      link.click();
      URL.revokeObjectURL(url);
      toast.success(`Book exported as ${format.toUpperCase()}`);
    } catch (error: any) {
      console.error('Error exporting book:', error);
      toast.error(error.userMessage || 'Failed to export book');
    }
  };

  const deleteBook = async (book: Book) => {
    if (!confirm(`Are you sure you want to delete "${book.title}"? This action cannot be undone.`)) {
      return;
    }

    try {
      Logger.api('DELETE', `/api/research/books/${book.id}/`);
      await researchBooksService.deleteBook(book.id);
      
      // Remove from local state
      setBooks(prev => prev.filter(b => b.id !== book.id));
      
      // Clear current book if it was the deleted one
      if (currentBook?.id === book.id) {
        setCurrentBook(null);
      }
      
      toast.success('Book deleted successfully');
      Logger.state('ResearchBooks', 'Book deleted', { bookId: book.id, title: book.title });
    } catch (error: any) {
      Logger.error('ResearchBooks.deleteBook', error);
      toast.error(error.userMessage || 'Failed to delete book');
    }
  };

  const transferToEbooks = async (book: Book) => {
    if (!confirm(`Transfer "${book.title}" to the eBooks section? This will create a new eBook entry with all ${book.chapters?.length || 0} chapters.`)) {
      return;
    }

    try {
      Logger.component('ResearchBooks', 'Transferring book to eBooks', { 
        bookId: book.id, 
        title: book.title,
        chapterCount: book.chapters?.length || 0
      });
      
      // Prepare eBook data from the research book
      const ebookData = {
        title: book.title,
        subtitle: '',
        author: 'Research & Books AI',
        genre: book.options?.genre || 'non_fiction',
        format: 'pdf',
        description: book.description,
        target_audience: book.options?.target_audience || 'general',
        keywords: [],
        word_count_target: book.word_count || 10000,
        // Include chapter data for transfer
        chapters: book.chapters?.map(chapter => ({
          chapter_number: chapter.chapter_number,
          title: chapter.title,
          content: chapter.content,
          word_count: chapter.word_count,
          summary: '',
          key_points: []
        })) || []
      };

      // Try to create eBook with chapters via a transfer-specific endpoint first
      let response = await fetch('http://localhost:8000/api/ebooks/transfer/', {
        method: 'POST',
        headers: {
          ...getAuthHeaderWithDevFallback(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(ebookData)
      });

      // If transfer endpoint doesn't exist, fall back to regular creation + manual chapter creation
      if (!response.ok && response.status === 404) {
        Logger.component('ResearchBooks', 'Transfer endpoint not found, using fallback approach');
        
        // Create basic eBook first
        response = await fetch('http://localhost:8000/api/ebooks/', {
          method: 'POST',
          headers: {
            ...getAuthHeaderWithDevFallback(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title: book.title,
            subtitle: '',
            author: 'Research & Books AI',
            genre: book.options?.genre || 'non_fiction',
            format: 'pdf',
            description: book.description,
            target_audience: book.options?.target_audience || 'general',
            keywords: [],
            word_count_target: book.word_count || 10000
          })
        });

        if (response.ok) {
          const ebookResult = await response.json();
          const ebookId = ebookResult.id;
          
          // Now try to create chapters if we have them
          if (book.chapters && book.chapters.length > 0) {
            Logger.component('ResearchBooks', 'Creating chapters for transferred eBook', { 
              ebookId,
              chapterCount: book.chapters.length 
            });
            
            // Note: This would require a chapters creation endpoint that may not exist
            // For now, we'll just show a message that chapters need to be recreated
            toast.warning(`eBook "${book.title}" transferred successfully, but chapters will need to be regenerated. Use the eBook generation features to create the content.`);
          } else {
            toast.success(`Successfully transferred "${book.title}" to eBooks! You can now find it in the eBooks section.`);
          }
          
          Logger.state('ResearchBooks', 'Book transferred to eBooks (fallback)', { 
            originalBookId: book.id,
            newEbookId: ebookId,
            title: book.title,
            chapterTransfer: false
          });
          return;
        }
      }

      if (response.ok) {
        const result = await response.json();
        toast.success(`Successfully transferred "${book.title}" to eBooks with all ${book.chapters?.length || 0} chapters! You can now find it in the eBooks section.`);
        Logger.state('ResearchBooks', 'Book transferred to eBooks with chapters', { 
          originalBookId: book.id,
          newEbookId: result.id,
          title: book.title,
          chapterCount: book.chapters?.length || 0
        });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create eBook');
      }
    } catch (error: any) {
      Logger.error('ResearchBooks.transferToEbooks', error);
      toast.error(`Failed to transfer book to eBooks: ${error.message}`);
    }
  };

  const startEditingChapter = (chapter: Chapter) => {
    setEditingChapter(chapter);
    setChapterContent(chapter.content || '');
  };

  const saveChapterEdit = async () => {
    if (!editingChapter || !currentBook) return;

    try {
      Logger.api('PUT', `/api/research/books/${currentBook.id}/chapters/${editingChapter.chapter_number}/`);
      const updatedChapter = await researchBooksService.updateChapter(
        currentBook.id, 
        editingChapter.chapter_number, 
        chapterContent
      );

      // Update the current book's chapters
      setCurrentBook(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          chapters: prev.chapters.map(ch => 
            ch.id === editingChapter.id ? { ...ch, content: chapterContent } : ch
          )
        };
      });

      // Update the books list
      setBooks(prev => prev.map(book => 
        book.id === currentBook.id 
          ? {
              ...book,
              chapters: book.chapters.map(ch => 
                ch.id === editingChapter.id ? { ...ch, content: chapterContent } : ch
              )
            }
          : book
      ));

      setEditingChapter(null);
      setChapterContent('');
      toast.success('Chapter updated successfully');
      Logger.state('ResearchBooks', 'Chapter updated', { 
        bookId: currentBook.id, 
        chapterNumber: editingChapter.chapter_number 
      });
    } catch (error: any) {
      Logger.error('ResearchBooks.saveChapterEdit', error);
      toast.error(error.userMessage || 'Failed to save chapter');
    }
  };

  const cancelChapterEdit = () => {
    setEditingChapter(null);
    setChapterContent('');
  };

  const generateBookImage = async () => {
    if (!imagePrompt.trim()) {
      toast.error('Please enter an image description');
      return;
    }

    setIsGeneratingImage(true);
    try {
      Logger.api('POST', '/api/content/create/', { prompt: imagePrompt, type: 'image' });
      
      // Call the content creation API
      const response = await fetch('/api/content/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaderWithDevFallback(),
        },
        body: JSON.stringify({
          prompt: imagePrompt,
          type: 'image',
          book_context: bookTitle.trim() || 'Book illustration'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate image');
      }

      const result = await response.json();
      
      if (result.images && result.images.length > 0) {
        // Add generated images to selected images
        const newImageUrls = result.images.map((img: any) => img.url);
        setSelectedImages(prev => [...prev, ...newImageUrls]);
        setImagePrompt('');
        toast.success(`Generated ${result.images.length} image(s) for your book`);
        Logger.state('ResearchBooks', 'Images generated', { count: result.images.length });
      }
    } catch (error: any) {
      Logger.error('ResearchBooks.generateBookImage', error);
      toast.error('Failed to generate image');
    } finally {
      setIsGeneratingImage(false);
    }
  };

  const removeSelectedImage = (imageUrl: string) => {
    setSelectedImages(prev => prev.filter(url => url !== imageUrl));
  };

  const openImageModal = () => {
    setShowImageModal(true);
  };

  const selectImageFromGallery = async (imageUrl: string) => {
    if (!selectedImages.includes(imageUrl)) {
      setSelectedImages(prev => [...prev, imageUrl]);
      toast.success('Image added to your book');
    }
    setShowImageModal(false);
  };

  const renderOutlineTab = () => (
    <div className="space-y-6">
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Build Your Book Outline</h3>
        <p className="text-gray-400 text-sm mb-6">
          Search your research library, select relevant sources, and add your personal insights to create a unique book.
        </p>
        
        {/* Book Topic & Search */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            What's your book about?
          </label>
          <div className="flex gap-2">
            <input
              className="input flex-1"
              placeholder="e.g., Building AI Applications, React Best Practices, Python Data Science..."
              value={bookTitle}
              onChange={(e) => setBookTitle(e.target.value)}
            />
            <Button variant="secondary">
              <MagnifyingGlassIcon className="h-4 w-4" />
              Search Research
            </Button>
          </div>
        </div>
      </Card>

      {/* Search Results / Available Research */}
      {documents.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">
            Available Research ({selectedDocuments.size} selected)
          </h3>
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="bg-dark-900/50 rounded-lg p-4 border border-dark-700">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <input
                      type="checkbox"
                      checked={selectedDocuments.has(doc.id)}
                      onChange={() => {
                        setSelectedDocuments(prev => {
                          const newSelection = new Set(prev);
                          if (newSelection.has(doc.id)) {
                            newSelection.delete(doc.id);
                          } else {
                            newSelection.add(doc.id);
                          }
                          return newSelection;
                        });
                      }}
                      className="w-4 h-4 mt-1 rounded border-gray-600 bg-dark-700 text-primary-500 focus:ring-primary-500"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <DocumentTextIcon className="h-4 w-4 text-blue-400" />
                        <span className="text-sm font-medium text-white">
                          {doc.filename}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs ${
                          doc.status === 'completed' ? 'bg-green-900/20 text-green-400' :
                          doc.status === 'processing' ? 'bg-blue-900/20 text-blue-400' :
                          'bg-red-900/20 text-red-400'
                        }`}>
                          {doc.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 line-clamp-2">
                        {doc.content_preview.length > 150 
                          ? `${doc.content_preview.slice(0, 150)}...` 
                          : doc.content_preview}
                      </p>
                      <div className="flex gap-4 mt-2 text-xs text-gray-500">
                        <span>Pages: {doc.pages}</span>
                        <span>Words: {doc.word_count.toLocaleString()}</span>
                        <span>Uploaded: {new Date(doc.uploaded_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <Button
                    onClick={() => deleteDocument(doc)}
                    variant="destructive"
                    size="sm"
                    className="ml-3"
                    title="Delete from research library"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
          {selectedDocuments.size > 0 && (
            <div className="mt-4 p-3 bg-blue-900/20 border border-blue-700 rounded-lg">
              <p className="text-blue-300 text-sm">
                ✓ {selectedDocuments.size} document{selectedDocuments.size !== 1 ? 's' : ''} selected for your book
              </p>
            </div>
          )}
        </Card>
      )}

      {/* Visual Assets Management */}
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Visual Assets for Your Book</h3>
        <p className="text-gray-400 text-sm mb-6">
          Generate custom illustrations, upload images, or select from your gallery to enhance your book.
        </p>
        
        {/* Image Generation */}
        <div className="mb-6">
          <h4 className="font-medium text-white mb-3 flex items-center gap-2">
            <PhotoIcon className="h-4 w-4" />
            Generate Book Illustrations
          </h4>
          <div className="space-y-3">
            <textarea
              className="w-full h-20 px-4 py-3 bg-dark-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 resize-none"
              placeholder="Describe the illustration you want... e.g., 'A futuristic AI workspace with holographic displays', 'Python code visualization with colorful data flows'"
              value={imagePrompt}
              onChange={(e) => setImagePrompt(e.target.value)}
            />
            <div className="flex gap-2">
              <Button 
                onClick={generateBookImage}
                loading={isGeneratingImage}
                disabled={!imagePrompt.trim()}
                className="flex-1"
              >
                <PhotoIcon className="h-4 w-4" />
                {isGeneratingImage ? 'Generating...' : 'Generate Image'}
              </Button>
              <Button 
                onClick={openImageModal}
                variant="secondary"
              >
                <CloudArrowUpIcon className="h-4 w-4" />
                Browse Gallery
              </Button>
            </div>
          </div>
        </div>

        {/* Selected Images */}
        {selectedImages.length > 0 && (
          <div className="mb-6">
            <h4 className="font-medium text-white mb-3">
              Selected Images ({selectedImages.length})
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {selectedImages.map((imageUrl, index) => (
                <div key={index} className="relative group">
                  <img
                    src={imageUrl}
                    alt={`Book image ${index + 1}`}
                    className="w-full h-24 object-cover rounded-lg border border-dark-600"
                  />
                  <button
                    onClick={() => removeSelectedImage(imageUrl)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Remove image"
                  >
                    <XMarkIcon className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Personal Thoughts & Insights */}
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Add Your Personal Touch</h3>
        <p className="text-gray-400 text-sm mb-4">
          Add your own thoughts, insights, or unique perspectives to make this book uniquely yours.
        </p>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Personal Notes & Insights
            </label>
            <textarea
              className="w-full h-32 px-4 py-3 bg-dark-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 resize-none"
              placeholder="Add your personal thoughts, experiences, or unique perspectives that should be woven into the book content..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
            />
          </div>
          
          <div className="flex justify-between items-center">
            <p className="text-xs text-gray-400">
              These insights will be incorporated throughout your book to add personal value
            </p>
            <Button onClick={addTextSource} disabled={!textInput.trim()} size="sm">
              <PlusIcon className="h-4 w-4" />
              Add Insights
            </Button>
          </div>
        </div>
      </Card>

      {/* Added Insights */}
      {sources.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">
            Your Insights ({sources.length})
          </h3>
          <div className="space-y-3">
            {sources.map((source, index) => (
              <div key={index} className="bg-dark-900/50 rounded-lg p-4 border border-dark-700">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <DocumentTextIcon className="h-4 w-4 text-purple-400" />
                      <span className="text-sm font-medium text-white">
                        Personal Insight {index + 1}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300 leading-relaxed">
                      {source.content.length > 200 
                        ? `${source.content.slice(0, 200)}...` 
                        : source.content}
                    </p>
                  </div>
                  <Button
                    onClick={() => removeSource(index)}
                    variant="secondary"
                    size="sm"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Outline Preview & Actions */}
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Outline Management</h3>
        <p className="text-gray-400 text-sm mb-4">
          Preview your book structure and manage your outline before generating the full book.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <Button variant="secondary" className="p-4 h-auto">
            <div className="text-center">
              <BookOpenIcon className="h-6 w-6 mx-auto mb-2" />
              <div className="font-medium">Generate Preview Outline</div>
              <div className="text-xs text-gray-400 mt-1">
                See how your book will be structured
              </div>
            </div>
          </Button>
          
          <Button variant="secondary" className="p-4 h-auto">
            <div className="text-center">
              <DocumentTextIcon className="h-6 w-6 mx-auto mb-2" />
              <div className="font-medium">Save Draft</div>
              <div className="text-xs text-gray-400 mt-1">
                Save your current progress
              </div>
            </div>
          </Button>
        </div>

        {/* Progress Summary */}
        {(selectedDocuments.size > 0 || sources.length > 0 || selectedImages.length > 0) && (
          <div className="bg-primary-500/10 border border-primary-500/20 rounded-lg p-4">
            <h4 className="font-medium text-white mb-2">Your Book Foundation</h4>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
              <div>
                <div className="text-lg font-bold text-blue-400">{selectedDocuments.size}</div>
                <div className="text-xs text-gray-400">Research Sources</div>
              </div>
              <div>
                <div className="text-lg font-bold text-purple-400">{sources.length}</div>
                <div className="text-xs text-gray-400">Personal Insights</div>
              </div>
              <div>
                <div className="text-lg font-bold text-pink-400">{selectedImages.length}</div>
                <div className="text-xs text-gray-400">Visual Assets</div>
              </div>
              <div>
                <div className="text-lg font-bold text-green-400">
                  {bookTitle.trim() ? '✓' : '○'}
                </div>
                <div className="text-xs text-gray-400">Book Topic</div>
              </div>
              <div>
                <div className="text-lg font-bold text-yellow-400">Ready</div>
                <div className="text-xs text-gray-400">Status</div>
              </div>
            </div>
            
            <div className="mt-4 flex justify-center">
              <Button 
                onClick={() => setActiveTab('generate')}
                disabled={!bookTitle.trim() || (selectedDocuments.size === 0 && sources.length === 0)}
                className="px-6"
              >
                <SparklesIcon className="h-4 w-4 mr-2" />
                Configure & Generate Book
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* Empty State */}
      {documents.length === 0 && (
        <Card>
          <div className="text-center py-12">
            <DocumentTextIcon className="h-16 w-16 mx-auto mb-4 text-gray-600" />
            <p className="text-gray-400 mb-2">No research available yet</p>
            <p className="text-sm text-gray-500 mb-4">
              Go to Research Sources to upload documents and build your research library
            </p>
            <Button 
              onClick={() => setActiveTab('sources')}
              variant="secondary"
            >
              Add Research Sources
            </Button>
          </div>
        </Card>
      )}
    </div>
  );

  const renderSourcesTab = () => (
    <div className="space-y-6">
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Research Collection</h3>
        <p className="text-gray-400 text-sm mb-6">
          Build your research library by uploading documents, extracting content from URLs, and processing videos.
        </p>
        
        {/* PDF Upload */}
        <div className="mb-6">
          <h4 className="font-medium text-white mb-2 flex items-center gap-2">
            <DocumentArrowUpIcon className="h-4 w-4" />
            Upload PDF Documents
          </h4>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md,.csv,.json,.html,.docx,.doc,.xlsx,.xls,.rtf"
            onChange={handleFileUpload}
            className="hidden"
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            loading={isUploading}
            variant="secondary"
            className="w-full"
          >
            <DocumentArrowUpIcon className="h-4 w-4" />
            {isUploading ? 'Uploading...' : 'Upload PDF'}
          </Button>
        </div>

        {/* URL Input */}
        <div className="mb-6">
          <h4 className="font-medium text-white mb-2 flex items-center gap-2">
            <LinkIcon className="h-4 w-4" />
            Web Articles & Pages
          </h4>
          <div className="flex gap-2">
            <input
              className="input flex-1"
              placeholder="https://example.com/article"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addUrlSource()}
            />
            <Button onClick={addUrlSource} disabled={!urlInput.trim()}>
              <PlusIcon className="h-4 w-4" />
              Extract
            </Button>
          </div>
        </div>

        {/* YouTube Input */}
        <div className="mb-6">
          <h4 className="font-medium text-white mb-2 flex items-center gap-2">
            <VideoCameraIcon className="h-4 w-4" />
            YouTube Videos
          </h4>
          <div className="flex gap-2">
            <input
              className="input flex-1"
              placeholder="https://youtube.com/watch?v=..."
              value={youtubeInput}
              onChange={(e) => setYoutubeInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addYoutubeSource()}
            />
            <Button onClick={addYoutubeSource} disabled={!youtubeInput.trim()}>
              <PlusIcon className="h-4 w-4" />
              Extract
            </Button>
          </div>
        </div>

        {/* Text Input */}
        <div className="mb-6">
          <h4 className="font-medium text-white mb-2 flex items-center gap-2">
            <DocumentTextIcon className="h-4 w-4" />
            Direct Text Input
          </h4>
          <div className="space-y-2">
            <textarea
              className="input min-h-[120px]"
              placeholder="Paste your research notes, quotes, or any text content..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
            />
            <Button onClick={addTextSource} disabled={!textInput.trim()} size="sm">
              <PlusIcon className="h-4 w-4" />
              Add Research Note
            </Button>
          </div>
        </div>
      </Card>

      {/* Research Library Status */}
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Your Research Library</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-dark-700 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-400">{documents.length}</div>
            <div className="text-sm text-gray-400">Processed Documents</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-400">{sources.length}</div>
            <div className="text-sm text-gray-400">Active Sources</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-400">
              {documents.reduce((acc, doc) => acc + (doc.word_count || 0), 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-400">Total Words</div>
          </div>
        </div>
        
        {(documents.length > 0 || sources.length > 0) && (
          <div className="mt-4 p-4 bg-primary-500/10 border border-primary-500/20 rounded-lg">
            <p className="text-primary-300 text-sm">
              📚 Your research is ready! Go to <strong>Book Outline</strong> to search and select sources for your next book.
            </p>
          </div>
        )}
      </Card>

      {/* Uploaded Documents Management */}
      {documents.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">Manage Uploaded Documents</h3>
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="bg-dark-900/50 rounded-lg p-4 border border-dark-700">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <DocumentTextIcon className="h-4 w-4 text-blue-400" />
                      <span className="text-sm font-medium text-white">
                        {doc.filename}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        doc.status === 'completed' ? 'bg-green-900/20 text-green-400' :
                        doc.status === 'processing' ? 'bg-blue-900/20 text-blue-400' :
                        'bg-red-900/20 text-red-400'
                      }`}>
                        {doc.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 line-clamp-2">
                      {doc.content_preview.length > 150 
                        ? `${doc.content_preview.slice(0, 150)}...` 
                        : doc.content_preview}
                    </p>
                    <div className="flex gap-4 mt-2 text-xs text-gray-500">
                      <span>Pages: {doc.pages}</span>
                      <span>Words: {doc.word_count.toLocaleString()}</span>
                      <span>Uploaded: {new Date(doc.uploaded_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <Button
                    onClick={() => deleteDocument(doc)}
                    variant="destructive"
                    size="sm"
                    className="ml-3"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Active Sources Management */}
      {sources.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">Manage Extracted Sources</h3>
          <div className="space-y-3">
            {sources.map((source, index) => (
              <div key={index} className="bg-dark-900/50 rounded-lg p-4 border border-dark-700">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {source.type === 'url' && <LinkIcon className="h-4 w-4 text-blue-400" />}
                      {source.type === 'youtube' && <VideoCameraIcon className="h-4 w-4 text-red-400" />}
                      {source.type === 'pdf' && <DocumentArrowUpIcon className="h-4 w-4 text-green-400" />}
                      {source.type === 'text' && <DocumentTextIcon className="h-4 w-4 text-gray-400" />}
                      {source.type === 'csv' && <DocumentTextIcon className="h-4 w-4 text-blue-400" />}
                      {source.type === 'doc' && <DocumentTextIcon className="h-4 w-4 text-blue-500" />}
                      {source.type === 'spreadsheet' && <DocumentTextIcon className="h-4 w-4 text-green-500" />}
                      {source.type === 'document' && <DocumentArrowUpIcon className="h-4 w-4 text-purple-400" />}
                      <span className="text-sm font-medium text-white">
                        {source.title || `${source.type.toUpperCase()} Source`}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 line-clamp-2">
                      {source.content.length > 150 
                        ? `${source.content.slice(0, 150)}...` 
                        : source.content}
                    </p>
                    {source.metadata && (
                      <div className="flex gap-4 mt-2 text-xs text-gray-500">
                        {source.metadata.pages && <span>Pages: {source.metadata.pages}</span>}
                        {source.metadata.word_count && <span>Words: {source.metadata.word_count.toLocaleString()}</span>}
                        {source.metadata.duration && <span>Duration: {source.metadata.duration}</span>}
                        {source.metadata.source_url && (
                          <span className="truncate max-w-xs" title={source.metadata.source_url}>
                            URL: {source.metadata.source_url}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  <Button
                    onClick={() => removeSource(index)}
                    variant="destructive"
                    size="sm"
                    className="ml-3"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );

  const renderGenerateTab = () => (
    <div className="space-y-6">
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Book Configuration</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Book Title</label>
            <input
              className="input"
              placeholder="Enter your book title..."
              value={bookTitle}
              onChange={(e) => setBookTitle(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Genre</label>
              <select 
                className="input"
                value={bookOptions.genre}
                onChange={(e) => setBookOptions(prev => ({ ...prev, genre: e.target.value as any }))}
              >
                <option value="technical">Technical</option>
                <option value="business">Business</option>
                <option value="educational">Educational</option>
                <option value="non-fiction">Non-Fiction</option>
                <option value="fiction">Fiction</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Target Audience</label>
              <select 
                className="input"
                value={bookOptions.target_audience}
                onChange={(e) => setBookOptions(prev => ({ ...prev, target_audience: e.target.value as any }))}
              >
                <option value="general">General</option>
                <option value="academic">Academic</option>
                <option value="professional">Professional</option>
                <option value="beginner">Beginner</option>
                <option value="expert">Expert</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Chapter Count</label>
              <input
                className="input"
                type="number"
                min="3"
                max="20"
                value={bookOptions.chapter_count}
                onChange={(e) => setBookOptions(prev => ({ ...prev, chapter_count: parseInt(e.target.value) }))}
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Words per Chapter</label>
              <input
                className="input"
                type="number"
                min="500"
                max="5000"
                step="100"
                value={bookOptions.words_per_chapter}
                onChange={(e) => setBookOptions(prev => ({ ...prev, words_per_chapter: parseInt(e.target.value) }))}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Tone</label>
              <select 
                className="input"
                value={bookOptions.tone}
                onChange={(e) => setBookOptions(prev => ({ ...prev, tone: e.target.value as any }))}
              >
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
                <option value="academic">Academic</option>
                <option value="friendly">Friendly</option>
              </select>
            </div>

            <div className="flex items-center gap-2 pt-6">
              <input
                type="checkbox"
                id="citations"
                checked={bookOptions.include_citations}
                onChange={(e) => setBookOptions(prev => ({ ...prev, include_citations: e.target.checked }))}
                className="w-4 h-4"
              />
              <label htmlFor="citations" className="text-sm text-gray-300">
                Include citations
              </label>
            </div>
          </div>

          <div className="pt-4 border-t border-dark-700">
            <div className="flex justify-between items-center mb-4">
              <div>
                <p className="text-white font-medium">Ready to Generate</p>
                <p className="text-sm text-gray-400">
                  {sources.length} new sources • {selectedDocuments.size} selected documents • {bookOptions.chapter_count} chapters • 
                  ~{(bookOptions.chapter_count * bookOptions.words_per_chapter).toLocaleString()} words
                </p>
              </div>
              <Button
                onClick={generateBook}
                loading={isGenerating}
                disabled={!bookTitle.trim() || (sources.length === 0 && selectedDocuments.size === 0)}
                className="px-8"
              >
                <SparklesIcon className="h-4 w-4" />
                {isGenerating ? 'Generating...' : 'Generate Book'}
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {/* Current Generation Status */}
      {currentBook && (
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">Generation Progress</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-white">{currentBook.title}</h4>
                <p className="text-sm text-gray-400">Status: {currentBook.status}</p>
              </div>
              <div className="flex items-center gap-2">
                {currentBook.status === 'generating' && (
                  <div className="animate-spin h-5 w-5 border-2 border-primary-500 border-t-transparent rounded-full" />
                )}
                {currentBook.status === 'completed' && (
                  <CheckCircleIcon className="h-5 w-5 text-green-400" />
                )}
                {currentBook.status === 'error' && (
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
                )}
              </div>
            </div>

            {currentBook.chapters && currentBook.chapters.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {currentBook.chapters.map((chapter) => (
                  <div
                    key={chapter.id}
                    className={`p-2 rounded text-xs text-center ${
                      chapter.status === 'completed' ? 'bg-green-900/20 text-green-400' :
                      chapter.status === 'generating' ? 'bg-blue-900/20 text-blue-400' :
                      chapter.status === 'error' ? 'bg-red-900/20 text-red-400' :
                      'bg-dark-700 text-gray-400'
                    }`}
                  >
                    Ch. {chapter.chapter_number}
                  </div>
                ))}
              </div>
            )}

            {currentBook.status === 'completed' && (
              <div className="flex gap-2">
                <Button onClick={() => exportBook(currentBook, 'pdf')} size="sm" variant="secondary">
                  <ArrowDownTrayIcon className="h-4 w-4" />
                  PDF
                </Button>
                <Button onClick={() => exportBook(currentBook, 'docx')} size="sm" variant="secondary">
                  <ArrowDownTrayIcon className="h-4 w-4" />
                  DOCX
                </Button>
                <Button onClick={() => exportBook(currentBook, 'epub')} size="sm" variant="secondary">
                  <ArrowDownTrayIcon className="h-4 w-4" />
                  EPUB
                </Button>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );

  const renderLibraryTab = () => (
    <div className="space-y-6">
      {books.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {books.map((book) => (
            <Card key={book.id}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-white mb-1">{book.title}</h3>
                  <p className="text-sm text-gray-400 mb-2 line-clamp-2">
                    {book.description}
                  </p>
                  <div className="flex gap-4 text-xs text-gray-500">
                    <span>{book.chapters?.length || 0} chapters</span>
                    <span>{book.word_count?.toLocaleString() || 0} words</span>
                    <span className={`px-2 py-1 rounded ${
                      book.status === 'completed' ? 'bg-green-900/20 text-green-400' :
                      book.status === 'generating' ? 'bg-blue-900/20 text-blue-400' :
                      book.status === 'error' ? 'bg-red-900/20 text-red-400' :
                      'bg-gray-900/20 text-gray-400'
                    }`}>
                      {book.status}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                {book.status === 'completed' && (
                  <>
                    <Button onClick={() => exportBook(book, 'pdf')} size="sm" variant="secondary">
                      PDF
                    </Button>
                    <Button onClick={() => exportBook(book, 'docx')} size="sm" variant="secondary">
                      DOCX
                    </Button>
                    <Button onClick={() => transferToEbooks(book)} size="sm" variant="primary" title="Send to eBooks section">
                      📚 Send to eBooks
                    </Button>
                  </>
                )}
                <Button 
                  onClick={() => setCurrentBook(book)}
                  size="sm"
                >
                  View Details
                </Button>
                <Button 
                  onClick={() => deleteBook(book)}
                  size="sm"
                  variant="destructive"
                  className="p-2"
                  title="Delete book"
                >
                  <TrashIcon className="h-4 w-4" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <div className="text-center py-12">
            <BookOpenIcon className="h-16 w-16 mx-auto mb-4 text-gray-600" />
            <p className="text-gray-400 mb-2">No books generated yet</p>
            <p className="text-sm text-gray-500">
              Add research sources and generate your first book
            </p>
            <Button 
              onClick={() => setActiveTab('sources')}
              className="mt-4"
            >
              Get Started
            </Button>
          </div>
        </Card>
      )}
    </div>
  );

  const renderCurrentTab = () => {
    switch (activeTab) {
      case 'sources':
        return renderSourcesTab();
      case 'outline':
        return renderOutlineTab();
      case 'generate':
        return renderGenerateTab();
      case 'library':
        return renderLibraryTab();
      default:
        return (
          <Card>
            <div className="text-center py-12">
              <SparklesIcon className="h-16 w-16 mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400">Coming soon!</p>
            </div>
          </Card>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <Card>
        <div className="flex flex-wrap gap-2">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-primary-500 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                {tab.name}
              </button>
            );
          })}
        </div>
      </Card>

      {/* Tab Content */}
      {renderCurrentTab()}

      {/* Book Details Modal */}
      {currentBook && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-dark-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <h2 className="text-xl font-semibold text-white">{currentBook.title}</h2>
              <button
                onClick={() => setCurrentBook(null)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <div className="space-y-6">
                {/* Book Status & Info */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-dark-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-400 mb-1">Status</h3>
                    <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                      currentBook.status === 'completed' ? 'bg-green-900/20 text-green-400' :
                      currentBook.status === 'generating' ? 'bg-blue-900/20 text-blue-400' :
                      currentBook.status === 'error' ? 'bg-red-900/20 text-red-400' :
                      'bg-gray-900/20 text-gray-400'
                    }`}>
                      {currentBook.status}
                    </span>
                  </div>
                  
                  <div className="bg-dark-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-400 mb-1">Word Count</h3>
                    <p className="text-white font-medium">{currentBook.word_count?.toLocaleString() || 'N/A'}</p>
                  </div>
                  
                  <div className="bg-dark-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-400 mb-1">Chapters</h3>
                    <p className="text-white font-medium">{currentBook.chapters?.length || 0}</p>
                  </div>
                </div>

                {/* Description */}
                {currentBook.description && (
                  <div>
                    <h3 className="text-lg font-medium text-white mb-2">Description</h3>
                    <p className="text-gray-300 text-sm leading-relaxed">{currentBook.description}</p>
                  </div>
                )}

                {/* Chapters */}
                {currentBook.chapters && currentBook.chapters.length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-white mb-4">Chapters</h3>
                    <div className="space-y-3">
                      {currentBook.chapters.map((chapter, index) => (
                        <div key={chapter.id} className="bg-dark-700 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-white">
                              Chapter {chapter.chapter_number}: {chapter.title}
                            </h4>
                            <div className="flex items-center gap-2">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                chapter.status === 'completed' ? 'bg-green-900/20 text-green-400' :
                                chapter.status === 'generating' ? 'bg-blue-900/20 text-blue-400' :
                                chapter.status === 'error' ? 'bg-red-900/20 text-red-400' :
                                'bg-gray-900/20 text-gray-400'
                              }`}>
                                {chapter.status || 'completed'}
                              </span>
                              {chapter.content && (
                                <>
                                  <Button
                                    onClick={() => startEditingChapter(chapter)}
                                    size="sm"
                                    variant="secondary"
                                    className="p-1.5"
                                    title="Edit chapter"
                                  >
                                    <PencilIcon className="h-3 w-3" />
                                  </Button>
                                </>
                              )}
                            </div>
                          </div>
                          
                          {chapter.content && (
                            <div className="mt-3">
                              <p className="text-gray-300 text-sm line-clamp-3">
                                {chapter.content.substring(0, 200)}...
                              </p>
                              <Button
                                onClick={() => startEditingChapter(chapter)}
                                variant="ghost"
                                size="sm"
                                className="mt-2 p-0 h-auto text-xs"
                              >
                                <EyeIcon className="h-3 w-3 mr-1" />
                                Read Full Chapter
                              </Button>
                            </div>
                          )}
                          
                          {chapter.word_count && (
                            <p className="text-xs text-gray-400 mt-2">
                              {chapter.word_count} words
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex justify-between items-center pt-4 border-t border-gray-700">
                  <div className="flex gap-3">
                    {currentBook.status === 'completed' && (
                      <>
                        <Button onClick={() => exportBook(currentBook, 'pdf')} size="sm" variant="secondary">
                          <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                          Export PDF
                        </Button>
                        <Button onClick={() => exportBook(currentBook, 'docx')} size="sm" variant="secondary">
                          <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                          Export DOCX
                        </Button>
                        <Button onClick={() => exportBook(currentBook, 'epub')} size="sm" variant="secondary">
                          <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                          Export EPUB
                        </Button>
                        <Button onClick={() => transferToEbooks(currentBook)} size="sm" variant="primary">
                          📚 Send to eBooks
                        </Button>
                      </>
                    )}
                  </div>
                  
                  <Button 
                    onClick={() => deleteBook(currentBook)}
                    variant="destructive"
                    size="sm"
                  >
                    <TrashIcon className="h-4 w-4 mr-2" />
                    Delete Book
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chapter Reading/Editing Modal */}
      {editingChapter && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] p-4">
          <div className="bg-dark-800 rounded-lg max-w-5xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <h2 className="text-xl font-semibold text-white">
                Chapter {editingChapter.chapter_number}: {editingChapter.title}
              </h2>
              <button
                onClick={cancelChapterEdit}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
              <div className="space-y-4">
                {/* Chapter Info */}
                <div className="flex items-center justify-between bg-dark-700 rounded-lg p-4">
                  <div>
                    <h3 className="font-medium text-white">Chapter Details</h3>
                    <p className="text-sm text-gray-400">
                      {editingChapter.word_count || 0} words
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    editingChapter.status === 'completed' ? 'bg-green-900/20 text-green-400' :
                    editingChapter.status === 'generating' ? 'bg-blue-900/20 text-blue-400' :
                    editingChapter.status === 'error' ? 'bg-red-900/20 text-red-400' :
                    'bg-gray-900/20 text-gray-400'
                  }`}>
                    {editingChapter.status || 'completed'}
                  </span>
                </div>

                {/* Chapter Content Editor */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Chapter Content
                  </label>
                  <textarea
                    value={chapterContent}
                    onChange={(e) => setChapterContent(e.target.value)}
                    className="w-full h-96 px-4 py-3 bg-dark-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 resize-none font-mono text-sm leading-relaxed"
                    placeholder="Chapter content..."
                  />
                  <p className="text-xs text-gray-400 mt-2">
                    {chapterContent.split(' ').filter(word => word.length > 0).length} words
                  </p>
                </div>
              </div>
            </div>
            
            {/* Modal Actions */}
            <div className="flex justify-between items-center p-6 border-t border-gray-700">
              <div className="text-sm text-gray-400">
                Use this editor to review and make changes to the chapter before publishing.
              </div>
              
              <div className="flex gap-3">
                <Button
                  onClick={cancelChapterEdit}
                  variant="secondary"
                  size="sm"
                >
                  Cancel
                </Button>
                <Button
                  onClick={saveChapterEdit}
                  size="sm"
                  disabled={chapterContent.trim() === ''}
                >
                  Save Changes
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Gallery Modal */}
      {showImageModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[70] p-4">
          <div className="bg-dark-800 rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <h2 className="text-xl font-semibold text-white">Select Images from Gallery</h2>
              <button
                onClick={() => setShowImageModal(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {/* Placeholder for gallery images - would integrate with actual gallery service */}
                <div className="text-center py-12 col-span-full">
                  <PhotoIcon className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                  <p className="text-gray-400 mb-2">Gallery integration coming soon</p>
                  <p className="text-sm text-gray-500">
                    Use the "Generate Image" feature to create custom illustrations for your book
                  </p>
                  <Button 
                    onClick={() => setShowImageModal(false)}
                    className="mt-4"
                  >
                    Close
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}