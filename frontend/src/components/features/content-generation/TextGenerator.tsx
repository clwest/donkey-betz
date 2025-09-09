import { useState, useEffect } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { 
  DocumentTextIcon,
  EnvelopeIcon,
  MicrophoneIcon,
  AdjustmentsHorizontalIcon,
} from '@heroicons/react/24/outline';
import { contentService } from '../../../services/content.service';
import { toast } from 'sonner';
import { Logger } from '../../../utils/logger';
import { useNavigate } from 'react-router-dom';

interface TextGenerationParams {
  prompt: string;
  type: 'blog' | 'email' | 'podcast';
  model: 'gpt-5' | 'gpt-5-mini' | 'gpt-5-nano' | 'claude' | 'gemini';
  tone?: string;
  length?: 'short' | 'medium' | 'long';
  temperature?: number;
  max_tokens?: number;
  verbosity?: 'low' | 'medium' | 'high';  // GPT-5 parameter
  reasoning_effort?: 'minimal' | 'standard' | 'maximum';  // GPT-5 parameter
}

export function TextGenerator() {
  const navigate = useNavigate();
  
  useEffect(() => {
    Logger.component('TextGenerator', 'Mounting');
    return () => {
      Logger.component('TextGenerator', 'Unmounting');
    };
  }, []);

  const [params, setParams] = useState<TextGenerationParams>({
    prompt: '',
    type: 'blog',
    model: 'gpt-5-mini',  // Updated to GPT-5 mini
    tone: 'professional',
    length: 'medium',
    temperature: 0.7,
    max_tokens: 1000,
    verbosity: 'medium',  // Default GPT-5 verbosity
    reasoning_effort: 'standard',  // Default GPT-5 reasoning level
  });
  const [generatedContent, setGeneratedContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [lastGeneratedId, setLastGeneratedId] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const contentTypes = [
    { id: 'blog', label: 'Blog Post', icon: DocumentTextIcon, desc: 'SEO-optimized articles' },
    { id: 'email', label: 'Email', icon: EnvelopeIcon, desc: 'Marketing and communication emails' },
    { id: 'podcast', label: 'Podcast Script', icon: MicrophoneIcon, desc: 'Episode scripts and outlines' },
  ];

  const handleGenerate = async () => {
    if (!params.prompt.trim()) {
      Logger.warn('TextGenerator', 'Generation attempted without prompt');
      toast.error('Please enter a prompt');
      return;
    }

    Logger.event('TextGenerator', 'Starting text generation', { type: params.type, model: params.model });
    setIsGenerating(true);
    try {
      let result;
      
      if (params.type === 'blog') {
        Logger.api('POST', '/api/content/blog/generate/', { topic: params.prompt, tone: params.tone, length: params.length });
        result = await contentService.generateBlog({
          topic: params.prompt,
          tone: params.tone,
          length: params.length,
        });
        // Blog API returns nested structure
        const blogData = result.blog_post || result;
        const title = blogData.title ? `# ${blogData.title}\n\n` : '';
        const content = blogData.content || blogData.result || '';
        setGeneratedContent(title + content);
        setLastGeneratedId(result.content_id?.toString() || blogData.id?.toString() || null);
        Logger.state('TextGenerator', 'Blog generated', { 
          title: blogData.title, 
          length: content.length,
          id: result.content_id || blogData.id
        });
      } else if (params.type === 'email') {
        Logger.api('POST', '/api/campaigns/', { prompt: params.prompt, tone: params.tone });
        // For email, we'll use campaign email generation for now
        // TODO: Create dedicated email endpoint when ready
        result = await contentService.generateText({
          prompt: `Generate a professional email about: ${params.prompt}`,
          model: params.model,
          max_tokens: params.max_tokens,
          temperature: params.temperature,
          type: 'email',
          tone: params.tone,
        });
        const emailContent = result.result || result.content || result.text || 'Generated email';
        setGeneratedContent(`# Email Draft\n\n${emailContent}`);
        const emailId = result.id || result.content_id;
        setLastGeneratedId(emailId ? emailId.toString() : null);
        Logger.state('TextGenerator', 'Email generated', { 
          length: emailContent.length,
          id: emailId,
          fullResult: result
        });
      } else if (params.type === 'podcast') {
        Logger.api('POST', '/api/podcasts/generate/', { topic: params.prompt, tone: params.tone });
        // Use the new simplified podcast generation endpoint
        const podcastRequest = {
          topic: params.prompt,
          title: params.prompt.slice(0, 100), // Use prompt as title
          format: 'solo', // Default format
          tone: params.tone,
          duration: 10, // Default 10 minutes
          enhance_prompt: aiSettings.enableEnhancement,
          use_memory: aiSettings.useMemory
        };
        
        result = await contentService.generatePodcast(podcastRequest);
        
        // The new endpoint returns the full script directly
        setGeneratedContent(result.content || `# ${result.title || 'Podcast Script'}\n\nPodcast generated successfully!`);
        setLastGeneratedId(result.id ? result.id.toString() : null);
        Logger.state('TextGenerator', 'Podcast episode created', { 
          episodeId: result.episode_id,
          title: result.title,
          segments: result.segments_count,
          duration: result.duration,
          fullResult: result
        });
      } else {
        Logger.api('POST', '/api/content/text/', { prompt: params.prompt, type: params.type, model: params.model });
        result = await contentService.generateText({
          prompt: params.prompt,
          model: params.model,
          max_tokens: params.max_tokens,
          temperature: params.temperature,
          type: params.type,
          tone: params.tone,
        });
        setGeneratedContent(result.result || result.content || result.text || 'Generated content');
        setLastGeneratedId(result.id?.toString() || null);
        Logger.state('TextGenerator', 'Content generated', { 
          length: (result.result || result.content || result.text || '').length,
          id: result.id
        });
      }
      toast.success('Content generated successfully!');
    } catch (error: any) {
      Logger.error('TextGenerator.handleGenerate', error);
      toast.error(error.userMessage || 'Failed to generate content');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    Logger.event('TextGenerator', 'Copy content', { length: generatedContent.length });
    navigator.clipboard.writeText(generatedContent);
    toast.success('Content copied to clipboard!');
  };

  const handleSave = async () => {
    if (!generatedContent) {
      toast.error('No content to save. Please generate content first.');
      return;
    }

    Logger.event('TextGenerator', 'Save content', { 
      length: generatedContent.length,
      contentId: lastGeneratedId,
      contentIdType: typeof lastGeneratedId,
      hasContentId: !!lastGeneratedId,
      type: params.type
    });
    
    // Debug logging
    console.log('Save attempt - lastGeneratedId:', lastGeneratedId, 'type:', typeof lastGeneratedId);
    
    setIsSaving(true);
    try {
      if (params.type === 'blog') {
        // Extract blog data for blog-specific save
        let title = 'Blog Post';
        let content = generatedContent;
        let meta_description = '';
        
        if (generatedContent.startsWith('# ')) {
          const titleMatch = generatedContent.match(/^# (.+)$/m);
          title = titleMatch ? titleMatch[1] : 'Blog Post';
          // Remove title from content
          content = generatedContent.replace(/^# .+\n\n/, '');
        }

        await contentService.saveBlogPost({
          title,
          content,
          meta_description,
          tags: [params.tone || 'default', 'generated']
        });
        
        toast.success('Blog post saved to library!');
      } else if (params.type === 'podcast' && lastGeneratedId) {
        // Podcast is already saved when created
        toast.success('Podcast episode saved! View in Podcasts section.');
      } else {
        // For email, we don't have a proper save endpoint yet
        toast.info('Content generated! Use the Copy button to save your content.');
      }
      Logger.state('TextGenerator', 'Content saved successfully', { 
        contentId: lastGeneratedId,
        type: params.type 
      });
    } catch (error: any) {
      Logger.error('TextGenerator.handleSave', error);
      toast.error(error.userMessage || 'Failed to save content');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Content Type Selection */}
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Content Type</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {contentTypes.map((type) => {
            const isSelected = params.type === type.id;
            return (
              <button
                key={type.id}
                onClick={() => setParams({ ...params, type: type.id as any })}
                className={`p-4 rounded-lg border-2 transition-all duration-200 text-left ${
                  isSelected
                    ? 'border-primary-500 bg-primary-500/10'
                    : 'border-dark-700 hover:border-dark-600 hover:bg-white/5'
                }`}
              >
                <type.icon className={`h-6 w-6 mb-2 ${
                  isSelected ? 'text-primary-400' : 'text-gray-400'
                }`} />
                <div className={`font-medium ${
                  isSelected ? 'text-white' : 'text-gray-300'
                }`}>
                  {type.label}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {type.desc}
                </div>
              </button>
            );
          })}
        </div>
      </Card>

      {/* Main Generation Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Panel */}
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">Generate Content</h3>
          <div className="space-y-4">
            {/* Prompt */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">Prompt</label>
              <textarea
                className="input min-h-[120px]"
                placeholder="Describe what you want to generate..."
                value={params.prompt}
                onChange={(e) => setParams({ ...params, prompt: e.target.value })}
              />
            </div>

            {/* Basic Settings */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Model</label>
                <select 
                  className="input"
                  value={params.model}
                  onChange={(e) => setParams({ ...params, model: e.target.value as any })}
                >
                  <option value="gpt-4">GPT-4 (Best)</option>
                  <option value="gpt-3.5">GPT-3.5 (Fast)</option>
                  <option value="claude">Claude (Creative)</option>
                  <option value="gemini">Gemini (Analytical)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-2">Tone</label>
                <select 
                  className="input"
                  value={params.tone}
                  onChange={(e) => setParams({ ...params, tone: e.target.value as any })}
                >
                  <option value="professional">Professional</option>
                  <option value="casual">Casual</option>
                  <option value="technical">Technical</option>
                  <option value="marketing">Marketing</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Length</label>
                <select 
                  className="input"
                  value={params.length}
                  onChange={(e) => setParams({ ...params, length: e.target.value as any })}
                >
                  <option value="short">Short (≈300 words)</option>
                  <option value="medium">Medium (≈600 words)</option>
                  <option value="long">Long (≈1200 words)</option>
                </select>
              </div>
            </div>

            {/* Advanced Settings Toggle */}
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
            >
              <AdjustmentsHorizontalIcon className="h-4 w-4" />
              Advanced Settings
            </button>

            {/* Advanced Settings */}
            {showAdvanced && (
              <div className="space-y-4 p-4 bg-dark-900/50 rounded-lg border border-dark-700">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Temperature: {params.temperature}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={params.temperature}
                    onChange={(e) => setParams({ ...params, temperature: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Focused</span>
                    <span>Creative</span>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Max Tokens</label>
                  <input
                    type="number"
                    className="input"
                    value={params.max_tokens}
                    onChange={(e) => setParams({ ...params, max_tokens: parseInt(e.target.value) })}
                    min="100"
                    max="4000"
                  />
                </div>
              </div>
            )}

            {/* Generate Button */}
            <Button 
              onClick={handleGenerate}
              loading={isGenerating}
              className="w-full"
            >
              Generate {params.type === 'blog' ? 'Blog Post' : params.type === 'email' ? 'Email' : params.type === 'podcast' ? 'Podcast Script' : 'Content'}
            </Button>
          </div>
        </Card>

        {/* Output Panel */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Generated Content</h3>
            {generatedContent && (
              <div className="flex gap-2">
                <Button size="sm" variant="secondary" onClick={handleCopy}>
                  Copy
                </Button>
                {(params.type === 'blog' || (params.type === 'podcast' && lastGeneratedId)) && (
                  <Button 
                    size="sm" 
                    variant="secondary" 
                    onClick={handleSave}
                    disabled={isSaving}
                  >
                    {isSaving ? 'Saving...' : params.type === 'podcast' ? 'Saved!' : 'Save to Library'}
                  </Button>
                )}
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={() => navigate('/gallery')}
                >
                  View Gallery
                </Button>
              </div>
            )}
          </div>
          
          {isGenerating ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
              <span className="ml-3 text-gray-400">Generating content...</span>
            </div>
          ) : generatedContent ? (
            <div className="space-y-4">
              <div className="bg-dark-900/50 rounded-lg p-4 border border-dark-700">
                <pre className="whitespace-pre-wrap text-sm text-gray-300 font-mono">
                  {generatedContent}
                </pre>
              </div>
              
              {/* Word count and stats */}
              <div className="flex gap-4 text-xs text-gray-500">
                <span>Words: {generatedContent.split(' ').length}</span>
                <span>Characters: {generatedContent.length}</span>
                <span>Est. reading time: {Math.ceil(generatedContent.split(' ').length / 200)} min</span>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <DocumentTextIcon className="h-16 w-16 mx-auto mb-4 text-gray-600" />
              <p>Generated content will appear here</p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}