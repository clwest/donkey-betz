import { useState, useEffect } from 'react';
import { Modal } from '../../common/Modal';
import { Button } from '../../common/Button';
import { contentService } from '../../../services/content.service';
import { Logger } from '../../../utils/logger';
import { toast } from 'sonner';
import { 
  ArrowsRightLeftIcon,
  HashtagIcon,
  MicrophoneIcon,
  BookOpenIcon,
  SparklesIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

interface BlogPost {
  id: number;
  title: string;
  content?: string;
  word_count: number;
  tags: string[];
  tone: string;
  length: string;
  preview?: string;
}

interface ContentTransformModalProps {
  isOpen: boolean;
  onClose: () => void;
  blog: BlogPost;
  onSuccess?: () => void;
}

export function ContentTransformModal({ isOpen, onClose, blog, onSuccess }: ContentTransformModalProps) {
  const [transforming, setTransforming] = useState(false);
  const [selectedType, setSelectedType] = useState<'social' | 'podcast' | 'ebook' | null>(null);
  const [fullBlogContent, setFullBlogContent] = useState<string>('');
  const [loadingContent, setLoadingContent] = useState(false);

  // Fetch full blog content when modal opens
  useEffect(() => {
    if (isOpen && blog && (!blog.content || blog.content.length < 100)) {
      setLoadingContent(true);
      contentService.getBlogPost(blog.id)
        .then(response => {
          const blogData = response.blog_post || response;
          setFullBlogContent(blogData.content || blog.preview || '');
        })
        .catch(error => {
          Logger.error('ContentTransformModal.fetchBlogContent', error);
          setFullBlogContent(blog.preview || '');
        })
        .finally(() => setLoadingContent(false));
    } else if (blog?.content) {
      setFullBlogContent(blog.content);
    }
  }, [isOpen, blog]);

  const transformOptions = [
    {
      type: 'social' as const,
      title: 'Social Media Posts',
      description: 'Convert to social media posts for multiple platforms',
      icon: HashtagIcon,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
      platforms: ['Twitter', 'LinkedIn', 'Facebook', 'Instagram']
    },
    {
      type: 'podcast' as const,
      title: 'Podcast Script',
      description: 'Create a podcast script with segments and talking points',
      icon: MicrophoneIcon,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      features: ['Introduction', 'Main Content', 'Key Points', 'Conclusion']
    },
    {
      type: 'ebook' as const,
      title: 'eBook Chapter',
      description: 'Expand into a comprehensive eBook chapter',
      icon: BookOpenIcon,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
      features: ['Detailed Expansion', 'Chapter Structure', 'Additional Sections']
    }
  ];

  const handleTransform = async () => {
    if (!selectedType) {
      toast.error('Please select a transformation type');
      return;
    }

    if (loadingContent) {
      toast.error('Please wait while we load the blog content');
      return;
    }

    if (!fullBlogContent || fullBlogContent.trim().length === 0) {
      toast.error('Blog content could not be loaded');
      return;
    }

    setTransforming(true);
    try {
      Logger.component('ContentTransformModal', `Transforming blog ${blog.id} to ${selectedType}`);

      let result;
      switch (selectedType) {
        case 'social':
          result = await contentService.generateSocialFromBlog({
            blogContent: fullBlogContent,
            topic: blog.title,
            tone: blog.tone,
            platforms: ['twitter', 'linkedin', 'facebook', 'instagram']
          });
          break;
        
        case 'podcast':
          result = await contentService.generatePodcastFromBlog({
            blogContent: fullBlogContent,
            title: blog.title,
            tone: blog.tone,
            duration: 'medium'
          });
          break;
        
        case 'ebook':
          result = await contentService.generateEbookFromBlog({
            blogContent: fullBlogContent,
            title: blog.title,
            tone: blog.tone,
            targetWordCount: blog.word_count * 3 // Expand to 3x the original length
          });
          break;
      }

      if (result?.success) {
        toast.success(`Successfully transformed blog to ${selectedType}!`);
        Logger.state('ContentTransformModal', 'Transformation successful', { 
          blogId: blog.id, 
          type: selectedType,
          result 
        });
        onSuccess?.();
        onClose();
      } else {
        toast.error(`Failed to transform content to ${selectedType}`);
      }
    } catch (error: any) {
      Logger.error('ContentTransformModal.handleTransform', error);
      toast.error('Failed to transform content');
    } finally {
      setTransforming(false);
    }
  };

  const handleClose = () => {
    if (!transforming) {
      setSelectedType(null);
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Transform Content"
      maxWidth="2xl"
    >
      <div className="space-y-6">
        {/* Source Content Info */}
        <div className="bg-dark-700 rounded-lg p-4 border border-dark-600">
          <div className="flex items-center gap-3 mb-2">
            <DocumentTextIcon className="h-5 w-5 text-primary-400" />
            <h3 className="font-semibold text-foreground">Source: Blog Post</h3>
          </div>
          <p className="text-muted-foreground font-medium">{blog.title}</p>
          <div className="flex items-center gap-4 text-sm text-muted-foreground mt-2">
            <span>{blog.word_count} words</span>
            <span className="capitalize">{blog.tone} tone</span>
            <span className="capitalize">{blog.length} length</span>
          </div>
        </div>

        {/* Transformation Options */}
        <div className="space-y-3">
          <h4 className="text-lg font-semibold text-foreground mb-3">Choose Transformation Type:</h4>
          
          {transformOptions.map((option) => (
            <div
              key={option.type}
              onClick={() => setSelectedType(option.type)}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                selectedType === option.type
                  ? 'border-primary-500 bg-primary-500/10'
                  : 'border-dark-600 bg-dark-700 hover:border-gray-500'
              }`}
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg ${option.bgColor}`}>
                  <option.icon className={`h-6 w-6 ${option.color}`} />
                </div>
                <div className="flex-1">
                  <h5 className="font-semibold text-foreground mb-1">{option.title}</h5>
                  <p className="text-muted-foreground text-sm mb-3">{option.description}</p>
                  
                  <div className="flex flex-wrap gap-2">
                    {('platforms' in option ? option.platforms : option.features).map((item, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 text-xs bg-gray-600 text-muted-foreground rounded"
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
                
                {selectedType === option.type && (
                  <div className="text-primary-400">
                    <ArrowsRightLeftIcon className="h-5 w-5" />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex justify-between items-center pt-4 border-t border-dark-600">
          <div className="text-sm text-muted-foreground">
            {selectedType && `Ready to transform to ${transformOptions.find(o => o.type === selectedType)?.title}`}
          </div>
          <div className="flex gap-3">
            <Button variant="ghost" onClick={handleClose} disabled={transforming}>
              Cancel
            </Button>
            <Button
              onClick={handleTransform}
              disabled={!selectedType || transforming || loadingContent}
              variant="primary"
            >
              {transforming ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Transforming...
                </>
              ) : loadingContent ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Loading Content...
                </>
              ) : (
                <>
                  <SparklesIcon className="h-4 w-4 mr-2" />
                  Transform Content
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}