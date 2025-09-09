import { apiClient, createFormData } from './api.config';

// Research & Books Types
export interface ResearchSource {
  type: 'url' | 'youtube' | 'pdf' | 'text';
  content: string;
  title?: string;
  metadata?: Record<string, any>;
}

export interface BookGenerationOptions {
  include_citations: boolean;
  chapter_count: number;
  words_per_chapter: number;
  genre: 'technical' | 'business' | 'educational' | 'fiction' | 'non-fiction';
  target_audience: 'general' | 'academic' | 'professional' | 'beginner' | 'expert';
  tone: 'professional' | 'casual' | 'academic' | 'friendly';
  language: string;
}

export interface Book {
  id: string;
  title: string;
  description: string;
  chapters: Chapter[];
  table_of_contents: string;
  word_count: number;
  status: 'draft' | 'generating' | 'completed' | 'error';
  created_at: string;
  updated_at: string;
  sources?: ResearchSource[];
  citations?: Citation[];
  options: BookGenerationOptions;
}

export interface Chapter {
  id: string;
  title: string;
  content: string;
  chapter_number: number;
  word_count: number;
  status: 'pending' | 'generating' | 'completed' | 'error';
  citations?: Citation[];
}

export interface Citation {
  id: string;
  source_url?: string;
  source_title: string;
  excerpt: string;
  page_number?: number;
  accessed_date: string;
}

export interface DocumentIngest {
  id: string;
  filename: string;
  content_preview: string;
  status: 'processing' | 'completed' | 'error';
  pages: number;
  word_count: number;
  uploaded_at: string;
}

// Research & Books Service
export const researchBooksService = {
  // Create book from research sources
  async createFromResearch(
    title: string, 
    sources: ResearchSource[], 
    options: Partial<BookGenerationOptions> = {},
    documentIds: string[] = []
  ): Promise<Book> {
    const defaultOptions: BookGenerationOptions = {
      include_citations: true,
      chapter_count: 10,
      words_per_chapter: 1500,
      genre: 'technical',
      target_audience: 'general',
      tone: 'professional',
      language: 'en'
    };

    const mergedOptions = { ...defaultOptions, ...options };

    // Convert frontend sources to backend format
    const backendSources: any = {
      urls: [],
      youtube: [],
      pdf_ids: documentIds // Include selected document IDs
    };

    // Process sources by type
    sources.forEach(source => {
      if (source.type === 'url' && source.metadata?.source_url) {
        backendSources.urls.push(source.metadata.source_url);
      } else if (source.type === 'youtube' && source.metadata?.source_url) {
        backendSources.youtube.push(source.metadata.source_url);
      } else if (source.type === 'pdf' && source.metadata?.document_id) {
        backendSources.pdf_ids.push(source.metadata.document_id);
      }
      // Note: 'text' sources need different handling as they're not URLs
    });

    const { data } = await apiClient.post('/research-to-book/', {
      title,
      sources: backendSources,
      options: mergedOptions,
    });
    return data;
  },

  // Upload and ingest PDF documents
  async ingestDocument(file: File): Promise<DocumentIngest> {
    const formData = createFormData({ document: file });
    
    const { data } = await apiClient.post('/research/ingest/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Get ingested documents
  async getDocuments(): Promise<DocumentIngest[]> {
    const { data } = await apiClient.get('/research/documents/');
    return data;
  },

  // Delete document
  async deleteDocument(documentId: string): Promise<void> {
    await apiClient.delete(`/research/documents/${documentId}/`);
  },

  // Extract content from URL
  async extractFromUrl(url: string): Promise<ResearchSource> {
    const { data } = await apiClient.post('/research/extract-url/', { url });
    return {
      type: 'url',
      content: data.content,
      title: data.title,
      metadata: data.metadata,
    };
  },

  // Extract content from YouTube video
  async extractFromYoutube(url: string): Promise<ResearchSource> {
    const { data } = await apiClient.post('/research/extract-youtube/', { url });
    return {
      type: 'youtube',
      content: data.transcript,
      title: data.title,
      metadata: {
        duration: data.duration,
        channel: data.channel,
        published_date: data.published_date,
      },
    };
  },

  // Generate book outline
  async generateOutline(title: string, sources: ResearchSource[]): Promise<{
    chapters: { title: string; description: string }[];
    estimated_length: number;
  }> {
    const { data } = await apiClient.post('/research/generate-outline/', {
      title,
      sources,
    });
    return data;
  },

  // Get book generation status
  async getBookStatus(bookId: string): Promise<Book> {
    const { data } = await apiClient.get(`/research/books/${bookId}/`);
    return data;
  },

  // Get all books
  async getBooks(): Promise<Book[]> {
    const { data } = await apiClient.get('/research/books/');
    return data;
  },

  // Delete book
  async deleteBook(bookId: string): Promise<void> {
    await apiClient.delete(`/research/books/${bookId}/delete/`);
  },

  // Generate specific chapter
  async generateChapter(bookId: string, chapterNumber: number): Promise<Chapter> {
    const { data } = await apiClient.post(`/research/books/${bookId}/chapters/${chapterNumber}/generate/`);
    return data;
  },

  // Update chapter content
  async updateChapter(bookId: string, chapterNumber: number, content: string): Promise<Chapter> {
    const { data } = await apiClient.put(`/research/books/${bookId}/chapters/${chapterNumber}/`, {
      content,
    });
    return data;
  },

  // Export book
  async exportBook(bookId: string, format: 'pdf' | 'docx' | 'epub' | 'txt'): Promise<Blob> {
    const { data } = await apiClient.post(`/research/books/${bookId}/export/`, {
      format,
    }, {
      responseType: 'blob',
    });
    return data;
  },

  // Search within book content
  async searchBooks(query: string): Promise<{
    books: Array<{ book: Book; matches: string[] }>;
    total_results: number;
  }> {
    const { data } = await apiClient.get('/research/search/', {
      params: { q: query },
    });
    return data;
  },

  // Get book analytics
  async getBookAnalytics(bookId: string): Promise<{
    word_count: number;
    reading_time_minutes: number;
    complexity_score: number;
    topics: string[];
    sentiment: 'positive' | 'neutral' | 'negative';
    citations_count: number;
  }> {
    const { data } = await apiClient.get(`/research/books/${bookId}/analytics/`);
    return data;
  },

  // Batch generate multiple chapters
  async batchGenerateChapters(bookId: string, chapterNumbers: number[]): Promise<{
    task_id: string;
    status: 'started';
  }> {
    const { data } = await apiClient.post(`/research/books/${bookId}/batch-generate/`, {
      chapters: chapterNumbers,
    });
    return data;
  },

  // Get batch generation status
  async getBatchStatus(taskId: string): Promise<{
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    progress: number;
    completed_chapters: number[];
    failed_chapters: number[];
  }> {
    const { data } = await apiClient.get(`/research/batch-status/${taskId}/`);
    return data;
  },
};