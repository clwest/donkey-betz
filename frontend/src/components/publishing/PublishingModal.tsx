import { useState, useEffect } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { toast } from 'react-hot-toast';
import { getAuthHeaderWithDevFallback } from '../../utils/auth';
import {
  BookOpenIcon,
  DocumentArrowDownIcon,
  SparklesIcon,
  CheckCircleIcon,
  PhotoIcon,
  GlobeAltIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  DocumentIcon,
  CodeBracketIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface EBook {
  id: number;
  title: string;
  subtitle?: string;
  author?: string;
  description: string;
  genre: string;
  target_audience: string;
  keywords: string[];
  word_count?: number;
  actual_word_count?: number;
  chapters?: any[];
  cover_image_url?: string;
  is_published?: boolean;
  published_date?: string;
}

interface PublishingModalProps {
  isOpen: boolean;
  onClose: () => void;
  ebook: EBook;
  onPublish: (updatedEbook: EBook) => void;
}

export function PublishingModal({
  isOpen,
  onClose,
  ebook,
  onPublish
}: PublishingModalProps) {
  const [step, setStep] = useState(1); // 1: Review, 2: Formats, 3: Cover, 4: Publish
  const [selectedFormats, setSelectedFormats] = useState<string[]>(['pdf']);
  const [generating, setGenerating] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [generatingCover, setGeneratingCover] = useState(false);
  const [coverStyle, setCoverStyle] = useState('professional');
  const [customPrompt, setCustomPrompt] = useState('');
  const [isbn, setIsbn] = useState('');
  const [isbnError, setIsbnError] = useState('');

  const formats = [
    {
      id: 'pdf',
      name: 'PDF',
      icon: DocumentIcon,
      description: 'Professional PDF for printing and digital reading',
      recommended: true
    },
    {
      id: 'epub',
      name: 'EPUB',
      icon: DevicePhoneMobileIcon,
      description: 'Standard eBook format for e-readers and mobile devices'
    },
    {
      id: 'html',
      name: 'HTML',
      icon: GlobeAltIcon,
      description: 'Web-friendly format for online reading'
    },
    {
      id: 'markdown',
      name: 'Markdown',
      icon: CodeBracketIcon,
      description: 'Plain text format with simple markup'
    }
  ];

  const coverStyles = [
    { id: 'professional', name: 'Professional', description: 'Clean, business-oriented design' },
    { id: 'modern', name: 'Modern', description: 'Contemporary design with bold typography' },
    { id: 'classic', name: 'Classic', description: 'Traditional book cover aesthetic' },
    { id: 'minimalist', name: 'Minimalist', description: 'Simple, elegant design' },
    { id: 'creative', name: 'Creative', description: 'Artistic and eye-catching design' }
  ];

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setStep(1);
      setSelectedFormats(['pdf']);
      setGenerating(false);
      setPublishing(false);
      setGeneratingCover(false);
      setCoverStyle('professional');
      setCustomPrompt('');
      setIsbn('');
      setIsbnError('');
    }
  }, [isOpen]);

  const toggleFormat = (formatId: string) => {
    setSelectedFormats(prev => {
      if (prev.includes(formatId)) {
        return prev.filter(id => id !== formatId);
      } else {
        return [...prev, formatId];
      }
    });
  };

  const generateCover = async () => {
    try {
      setGeneratingCover(true);
      const response = await fetch(
        `http://localhost:8000/api/ebooks/${ebook.id}/generate-cover/`,
        {
          method: 'POST',
          headers: {
            ...getAuthHeaderWithDevFallback(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            style: coverStyle,
            prompt: customPrompt.trim() || undefined
          })
        }
      );

      const data = await response.json();

      if (response.ok) {
        toast.success('Cover generated successfully');
        // Update the ebook with new cover
        onPublish({ ...ebook, cover_image_url: data.cover_url });
      } else {
        toast.error(data.error || 'Failed to generate cover');
      }
    } catch (error) {
      console.error('Failed to generate cover:', error);
      toast.error('Failed to generate cover');
    } finally {
      setGeneratingCover(false);
    }
  };

  const validateISBN = (isbn: string) => {
    const cleanISBN = isbn.replace(/[-\s]/g, '');
    if (!cleanISBN) return true; // Optional field
    if (cleanISBN.length !== 10 && cleanISBN.length !== 13) {
      return false;
    }
    return /^\d+$/.test(cleanISBN);
  };

  const updateISBN = async () => {
    if (!validateISBN(isbn)) {
      setIsbnError('Invalid ISBN format. Must be 10 or 13 digits.');
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/api/ebooks/${ebook.id}/update-isbn/`,
        {
          method: 'POST',
          headers: {
            ...getAuthHeaderWithDevFallback(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ isbn })
        }
      );

      if (response.ok) {
        toast.success('ISBN updated successfully');
      } else {
        const data = await response.json();
        setIsbnError(data.error || 'Failed to update ISBN');
      }
    } catch (error) {
      console.error('Failed to update ISBN:', error);
      setIsbnError('Failed to update ISBN');
    }
  };

  const publishEbook = async () => {
    try {
      setPublishing(true);
      
      // First publish the ebook
      const publishResponse = await fetch(
        `http://localhost:8000/api/ebooks/${ebook.id}/publish/`,
        {
          method: 'POST',
          headers: {
            ...getAuthHeaderWithDevFallback(),
            'Content-Type': 'application/json'
          }
        }
      );

      if (publishResponse.ok) {
        const publishData = await publishResponse.json();
        toast.success('eBook published successfully!');
        
        // Export in selected formats
        const exportPromises = selectedFormats.map(format => 
          exportFormat(format)
        );

        await Promise.all(exportPromises);
        
        onPublish({
          ...ebook,
          is_published: true,
          published_date: publishData.published_date
        });
        
        onClose();
      } else {
        const data = await publishResponse.json();
        toast.error(data.error || 'Failed to publish eBook');
      }
    } catch (error) {
      console.error('Failed to publish eBook:', error);
      toast.error('Failed to publish eBook');
    } finally {
      setPublishing(false);
    }
  };

  const exportFormat = async (format: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/ebooks/${ebook.id}/export/?format=${format}`,
        {
          headers: {
            'Authorization': 'Token 993f8273f70877e23b5c7d2f92ed30562a089fe3'
          }
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${ebook.title.toLowerCase().replace(/\s+/g, '-')}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
        toast.success(`Downloaded ${format.toUpperCase()} version`);
      }
    } catch (error) {
      console.error(`Failed to export ${format}:`, error);
      toast.error(`Failed to export ${format.toUpperCase()}`);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Review Your eBook</h3>
              <p className="text-muted-foreground">Verify all details before publishing</p>
            </div>

            <div className="bg-card rounded-lg p-4 border border-border">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Title:</span>
                  <p className="text-foreground font-medium">{ebook.title}</p>
                </div>
                {ebook.subtitle && (
                  <div>
                    <span className="text-muted-foreground">Subtitle:</span>
                    <p className="text-foreground">{ebook.subtitle}</p>
                  </div>
                )}
                <div>
                  <span className="text-muted-foreground">Author:</span>
                  <p className="text-foreground">{ebook.author || 'Not specified'}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Genre:</span>
                  <p className="text-foreground capitalize">{ebook.genre}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Word Count:</span>
                  <p className="text-foreground">{(ebook.actual_word_count || ebook.word_count || 0).toLocaleString()}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Chapters:</span>
                  <p className="text-foreground">{Array.isArray(ebook.chapters) ? ebook.chapters.length : 0}</p>
                </div>
              </div>
              
              {ebook.description && (
                <div className="mt-4">
                  <span className="text-muted-foreground">Description:</span>
                  <p className="text-foreground mt-1">{ebook.description}</p>
                </div>
              )}
            </div>

            <div className="flex justify-between">
              <Button variant="ghost" onClick={onClose}>
                Cancel
              </Button>
              <Button onClick={() => setStep(2)}>
                Continue to Formats
              </Button>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Choose Export Formats</h3>
              <p className="text-muted-foreground">Select the formats you want to export your eBook in</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {formats.map((format) => {
                const isSelected = selectedFormats.includes(format.id);
                const IconComponent = format.icon;
                
                return (
                  <div
                    key={format.id}
                    onClick={() => toggleFormat(format.id)}
                    className={`
                      p-4 rounded-lg border-2 cursor-pointer transition-all
                      ${isSelected 
                        ? 'border-primary-500 bg-primary-500/10' 
                        : 'border-dark-600 bg-card hover:border-dark-500'
                      }
                    `}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <IconComponent className="h-5 w-5 text-primary-400" />
                        <span className="font-medium text-foreground">{format.name}</span>
                      </div>
                      {format.recommended && (
                        <span className="px-2 py-1 bg-green-400/10 text-green-500 text-xs rounded">
                          Recommended
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{format.description}</p>
                    
                    {isSelected && (
                      <div className="mt-2 flex items-center gap-1 text-primary-400 text-sm">
                        <CheckCircleIcon className="h-4 w-4" />
                        <span>Selected</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="flex justify-between">
              <Button variant="ghost" onClick={() => setStep(1)}>
                Back
              </Button>
              <Button 
                onClick={() => setStep(3)}
                disabled={selectedFormats.length === 0}
              >
                Continue to Cover
              </Button>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Book Cover</h3>
              <p className="text-muted-foreground">Generate a professional cover for your eBook</p>
            </div>

            {/* Current cover */}
            <div className="text-center">
              <div className="w-32 h-48 mx-auto bg-gradient-to-br from-primary-500/20 to-purple-500/20 rounded-lg flex items-center justify-center mb-4">
                {ebook.cover_image_url ? (
                  <img 
                    src={ebook.cover_image_url} 
                    alt="Book cover"
                    className="w-full h-full object-cover rounded-lg"
                  />
                ) : (
                  <BookOpenIcon className="h-16 w-16 text-primary-400/50" />
                )}
              </div>
              {!ebook.cover_image_url && (
                <p className="text-muted-foreground">No cover generated yet</p>
              )}
            </div>

            {/* Cover generation */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Cover Style
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {coverStyles.map((style) => (
                    <label key={style.id} className="flex items-center">
                      <input
                        type="radio"
                        name="coverStyle"
                        value={style.id}
                        checked={coverStyle === style.id}
                        onChange={(e) => setCoverStyle(e.target.value)}
                        className="sr-only"
                      />
                      <div className={`
                        flex-1 p-3 rounded-lg border-2 cursor-pointer transition-all
                        ${coverStyle === style.id 
                          ? 'border-primary-500 bg-primary-500/10' 
                          : 'border-dark-600 bg-card'
                        }
                      `}>
                        <div className="font-medium text-foreground">{style.name}</div>
                        <div className="text-xs text-muted-foreground">{style.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">
                  Custom Prompt (optional)
                </label>
                <textarea
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500 h-20"
                  placeholder="Describe specific elements you want on your cover..."
                />
              </div>

              <Button
                onClick={generateCover}
                disabled={generatingCover}
                className="w-full"
              >
                {generatingCover ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    Generating Cover...
                  </>
                ) : (
                  <>
                    <SparklesIcon className="h-4 w-4" />
                    Generate Cover
                  </>
                )}
              </Button>
            </div>

            <div className="flex justify-between">
              <Button variant="ghost" onClick={() => setStep(2)}>
                Back
              </Button>
              <Button onClick={() => setStep(4)}>
                Continue to Publish
              </Button>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Final Publishing</h3>
              <p className="text-muted-foreground">Complete your eBook publication</p>
            </div>

            {/* ISBN */}
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">
                ISBN (optional)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={isbn}
                  onChange={(e) => {
                    setIsbn(e.target.value);
                    setIsbnError('');
                  }}
                  className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="978-0-123456-78-9 or 0123456789"
                />
                <Button size="sm" onClick={updateISBN} disabled={!isbn.trim()}>
                  Update
                </Button>
              </div>
              {isbnError && (
                <p className="text-red-500 text-sm mt-1">{isbnError}</p>
              )}
            </div>

            {/* Publication summary */}
            <div className="bg-card rounded-lg p-4 border border-border">
              <h4 className="font-medium text-foreground mb-3">Publication Summary</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Export Formats:</span>
                  <span className="text-foreground">{selectedFormats.map(f => f.toUpperCase()).join(', ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Cover:</span>
                  <span className="text-foreground">{ebook.cover_image_url ? 'Generated' : 'Not generated'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Publication Date:</span>
                  <span className="text-foreground">{new Date().toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <CheckCircleIcon className="h-5 w-5 text-blue-500 mt-0.5" />
                <div>
                  <p className="text-blue-300 font-medium">Ready to Publish</p>
                  <p className="text-blue-200 text-sm mt-1">
                    Your eBook will be marked as published and exported in the selected formats.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex justify-between">
              <Button variant="ghost" onClick={() => setStep(3)}>
                Back
              </Button>
              <Button
                onClick={publishEbook}
                disabled={publishing}
                className="bg-green-600 hover:bg-green-700"
              >
                {publishing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    Publishing...
                  </>
                ) : (
                  <>
                    <DocumentArrowDownIcon className="h-4 w-4" />
                    Publish eBook
                  </>
                )}
              </Button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Publish eBook"
      maxWidth="max-w-2xl"
    >
      {/* Progress indicator */}
      <div className="flex items-center justify-between mb-6">
        {[1, 2, 3, 4].map((stepNumber) => (
          <div key={stepNumber} className="flex items-center">
            <div
              className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                ${step >= stepNumber
                  ? 'bg-primary-500 text-foreground'
                  : 'bg-dark-700 text-muted-foreground'
                }
              `}
            >
              {step > stepNumber ? (
                <CheckCircleIcon className="h-5 w-5" />
              ) : (
                stepNumber
              )}
            </div>
            {stepNumber < 4 && (
              <div
                className={`
                  w-16 h-0.5 mx-2
                  ${step > stepNumber ? 'bg-primary-500' : 'bg-dark-700'}
                `}
              />
            )}
          </div>
        ))}
      </div>

      {renderStep()}
    </Modal>
  );
}