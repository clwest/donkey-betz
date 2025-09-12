import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { campaignService } from '../../services/campaign.service';
import { toast } from 'react-hot-toast';
import { 
  ArrowLeftIcon, 
  PlayIcon, 
  PauseIcon, 
  PlusIcon,
  EnvelopeIcon,
  ChatBubbleLeftIcon,
  MegaphoneIcon,
  DocumentTextIcon,
  ChartBarIcon,
  XMarkIcon,
  ClipboardDocumentIcon,
  PencilIcon,
  BookOpenIcon,
  MicrophoneIcon,
  PresentationChartBarIcon,
  ChartPieIcon,
  NewspaperIcon,
  SparklesIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

export function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [campaign, setCampaign] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [content, setContent] = useState<any[]>([]);
  const [viewingContent, setViewingContent] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<any>({});
  const [customPrompt, setCustomPrompt] = useState('');
  const [showPromptModal, setShowPromptModal] = useState(false);
  const [selectedContentType, setSelectedContentType] = useState('');
  const [generating, setGenerating] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    if (id) {
      loadCampaign(id);
    }
  }, [id]);

  const loadCampaign = async (campaignId: string) => {
    try {
      setLoading(true);
      const campaignData = await campaignService.getCampaign(campaignId);
      setCampaign(campaignData);
      setEditForm({
        name: campaignData.name || campaignData.title || '',
        description: campaignData.description || '',
        target_audience: typeof campaignData.target_audience === 'object' 
          ? campaignData.target_audience.description 
          : campaignData.target_audience || '',
        business_name: campaignData.config?.business || '',
        product: campaignData.config?.product || '',
        tone: campaignData.tone || 'professional',
      });
      
      // Load campaign content if available
      if (campaignData.content_items) {
        setContent(campaignData.content_items);
      } else if (campaignData.content) {
        setContent(campaignData.content);
      }
    } catch (error) {
      console.error('Failed to load campaign:', error);
      toast.error('Failed to load campaign');
      // Navigate back to campaigns list on error
      navigate('/campaigns');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateContent = async (contentType: string) => {
    if (!id) return;
    
    setGenerating(true);
    
    // For complex content types, show prompt modal
    if (['blog', 'ebook', 'podcast', 'pitch_deck', 'infographic'].includes(contentType)) {
      setSelectedContentType(contentType);
      setShowPromptModal(true);
      setGenerating(false);
      return;
    }
    
    try {
      // Build the prompt with campaign context for simple content
      const prompt = `Generate ${contentType} content for ${campaign?.name || 'this campaign'}. 
Business: ${editForm.business_name || 'our company'}
Product: ${editForm.product || 'our product/service'}
Audience: ${editForm.target_audience || 'general audience'}
Tone: ${editForm.tone || 'professional'}`;
      
      const result = await campaignService.generateCampaignContent(
        id,
        contentType as any,
        prompt
      );
      
      toast.success('Content generated successfully!');
      
      // Reload campaign to get updated content
      await loadCampaign(id);
    } catch (error) {
      toast.error('Failed to generate content');
      console.error(error);
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateWithPrompt = async () => {
    if (!customPrompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }
    
    if (!id) return;
    
    try {
      setGenerating(true);
      setShowPromptModal(false);
      
      // Build context-aware prompt
      const fullPrompt = `${customPrompt}\n\nBusiness Context:\n- Company: ${editForm.business_name || 'Not specified'}\n- Product/Service: ${editForm.product || 'Not specified'}\n- Target Audience: ${editForm.target_audience || 'General audience'}\n- Tone: ${editForm.tone || 'Professional'}`;
      
      const result = await campaignService.generateCampaignContent(
        id!,
        selectedContentType as any,
        fullPrompt
      );
      
      toast.success(`${selectedContentType.replace('_', ' ')} generated!`);
      
      // Clear prompt and reload
      setCustomPrompt('');
      setSelectedContentType('');
      
      await loadCampaign(id);
    } catch (error) {
      console.error('Failed to generate content:', error);
      toast.error('Failed to generate content');
    } finally {
      setGenerating(false);
    }
  };

  const handleLaunchCampaign = async () => {
    if (!id) return;
    
    try {
      const loadingToast = toast.loading('Launching campaign...');
      await campaignService.launchCampaign(id);
      toast.dismiss(loadingToast);
      toast.success('Campaign launched successfully!');
      loadCampaign(id);
    } catch (error) {
      toast.error('Failed to launch campaign');
      console.error(error);
    }
  };

  const handlePauseCampaign = async () => {
    if (!id) return;
    
    try {
      await campaignService.pauseCampaign(id);
      toast.success('Campaign paused');
      loadCampaign(id);
    } catch (error) {
      toast.error('Failed to pause campaign');
      console.error(error);
    }
  };

  const handleResumeCampaign = async () => {
    if (!id) return;
    
    try {
      await campaignService.resumeCampaign(id);
      toast.success('Campaign resumed');
      loadCampaign(id);
    } catch (error) {
      toast.error('Failed to resume campaign');
      console.error(error);
    }
  };

  const handleViewContent = (item: any) => {
    setViewingContent(item);
    setIsModalOpen(true);
  };

  const handleCopyContent = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const handleDeleteCampaign = async () => {
    if (!id) return;
    
    try {
      await campaignService.deleteCampaign(id);
      toast.success('Campaign deleted successfully');
      navigate('/campaigns');
    } catch (error) {
      toast.error('Failed to delete campaign');
      console.error('Delete campaign error:', error);
    }
  };

  const handleSaveEdit = async () => {
    if (!id) return;
    
    try {
      const updates = {
        name: editForm.name,
        description: editForm.description,
        target_audience: {
          description: editForm.target_audience
        },
        config: {
          business: editForm.business_name,
          product: editForm.product,
        },
        tone: editForm.tone,
      };
      
      console.log('Saving campaign updates:', updates);
      const result = await campaignService.updateCampaign(id, updates);
      console.log('Campaign update result:', result);
      
      toast.success('Campaign updated successfully!');
      setIsEditing(false);
      
      // If the backend returns the updated campaign, use it directly
      if (result.campaign) {
        setCampaign(result.campaign);
        setEditForm({
          name: result.campaign.name || '',
          description: result.campaign.description || '',
          target_audience: typeof result.campaign.target_audience === 'object' 
            ? result.campaign.target_audience.description 
            : result.campaign.target_audience || '',
          business_name: result.campaign.config?.business || '',
          product: result.campaign.config?.product || '',
          tone: result.campaign.tone || 'professional',
        });
      } else {
        // Otherwise reload from server
        await loadCampaign(id);
      }
    } catch (error) {
      toast.error('Failed to update campaign');
      console.error('Campaign update error:', error);
    }
  };

  const getContentIcon = (type: string) => {
    switch (type) {
      case 'email':
        return <EnvelopeIcon className="h-5 w-5" />;
      case 'sms':
        return <ChatBubbleLeftIcon className="h-5 w-5" />;
      case 'social_post':
        return <MegaphoneIcon className="h-5 w-5" />;
      case 'blog_post':
        return <DocumentTextIcon className="h-5 w-5" />;
      default:
        return <DocumentTextIcon className="h-5 w-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-400 bg-green-400/10';
      case 'paused':
        return 'text-yellow-400 bg-yellow-400/10';
      case 'completed':
        return 'text-blue-400 bg-blue-400/10';
      default:
        return 'text-gray-400 bg-gray-400/10';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400 mb-4">Campaign not found</p>
        <Button onClick={() => navigate('/campaigns')}>
          Back to Campaigns
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6" style={{ backgroundColor: 'var(--gaming-bg-primary)', minHeight: '100vh' }}>
      {/* Header - Gaming Style */}
      <div className="gaming-neural-card p-6">
        <div className="gaming-border-glow"></div>
        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/campaigns')}
            >
              <ArrowLeftIcon className="h-4 w-4" />
              Back
            </Button>
            {isEditing ? (
              <div className="space-y-2">
                <input
                  type="text"
                  value={editForm.name}
                  onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                  className="gaming-neural-input text-2xl font-bold font-mono px-3 py-1 rounded-lg"
                style={{
                  background: 'var(--gaming-bg-elevated)',
                  border: '1px solid var(--gaming-border)',
                  color: 'var(--gaming-text-primary)'
                }}
                placeholder="Campaign Name"
              />
              <input
                type="text"
                value={editForm.description}
                onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                className="gaming-neural-input font-mono px-3 py-1 rounded-lg w-full"
                style={{
                  background: 'var(--gaming-bg-elevated)',
                  border: '1px solid var(--gaming-border)',
                  color: 'var(--gaming-text-secondary)'
                }}
                placeholder="Campaign Description"
              />
            </div>
          ) : (
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-3xl font-black uppercase tracking-wider" 
                    style={{ 
                      fontFamily: 'var(--font-mono)',
                      color: 'var(--gaming-neon-cyan)',
                      textShadow: '0 0 20px rgba(0, 255, 255, 0.5)'
                    }}>
                  {campaign.name || campaign.title || 'UNTITLED CAMPAIGN'}
                </h1>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setIsEditing(true)}
                >
                  <PencilIcon className="h-4 w-4" />
                </Button>
              </div>
              <p className="mt-3 font-mono" style={{ color: 'var(--gaming-text-secondary)' }}>
                {campaign.description || 'NO DESCRIPTION'}
              </p>
            </div>
          )}
          </div>
        <div className="flex items-center gap-2">
          <span className={`px-4 py-2 rounded-xl text-sm font-bold font-mono uppercase tracking-wider ${getStatusColor(campaign.status)}`}
                style={{
                  border: '1px solid var(--gaming-border)',
                  boxShadow: '0 0 10px rgba(0, 255, 255, 0.2)'
                }}>
            {campaign.status}
          </span>
          {campaign.status === 'draft' && (
            <Button onClick={handleLaunchCampaign}>
              <PlayIcon className="h-4 w-4" />
              Launch Campaign
            </Button>
          )}
          {campaign.status === 'active' && (
            <Button onClick={handlePauseCampaign} variant="secondary">
              <PauseIcon className="h-4 w-4" />
              Pause Campaign
            </Button>
          )}
          {campaign.status === 'paused' && (
            <Button onClick={handleResumeCampaign}>
              <PlayIcon className="h-4 w-4" />
              Resume Campaign
            </Button>
          )}
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => setShowDeleteConfirm(true)}
            className="text-red-400 hover:text-red-300"
          >
            <TrashIcon className="h-4 w-4" />
            Delete
          </Button>
        </div>
        </div>
      </div>

      {/* Campaign Info - Gaming Style */}
      {isEditing ? (
        <div className="gaming-neural-card p-6">
          <div className="gaming-border-glow"></div>
          <div className="relative z-10">
          <h3 className="text-xl font-bold font-mono uppercase tracking-wider mb-6" 
              style={{ color: 'var(--gaming-neon-cyan)' }}>CAMPAIGN NEURAL DATA</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-mono uppercase tracking-wider block mb-2" 
                     style={{ color: 'var(--gaming-text-secondary)' }}>BUSINESS ENTITY</label>
              <input
                type="text"
                value={editForm.business_name}
                onChange={(e) => setEditForm({...editForm, business_name: e.target.value})}
                className="gaming-neural-input w-full px-3 py-2 rounded-lg font-mono"
                style={{
                  background: 'var(--gaming-bg-elevated)',
                  border: '1px solid var(--gaming-border)',
                  color: 'var(--gaming-text-primary)'
                }}
                placeholder="Your Company Name"
              />
            </div>
            <div>
              <label className="text-sm font-mono uppercase tracking-wider block mb-2" 
                     style={{ color: 'var(--gaming-text-secondary)' }}>PRODUCT MODULE</label>
              <input
                type="text"
                value={editForm.product}
                onChange={(e) => setEditForm({...editForm, product: e.target.value})}
                className="gaming-neural-input w-full px-3 py-2 rounded-lg font-mono"
                style={{
                  background: 'var(--gaming-bg-elevated)',
                  border: '1px solid var(--gaming-border)',
                  color: 'var(--gaming-text-primary)'
                }}
                placeholder="What you're promoting"
              />
            </div>
            <div>
              <label className="text-sm font-mono uppercase tracking-wider block mb-2" 
                     style={{ color: 'var(--gaming-text-secondary)' }}>TARGET MATRIX</label>
              <input
                type="text"
                value={editForm.target_audience}
                onChange={(e) => setEditForm({...editForm, target_audience: e.target.value})}
                className="gaming-neural-input w-full px-3 py-2 rounded-lg font-mono"
                style={{
                  background: 'var(--gaming-bg-elevated)',
                  border: '1px solid var(--gaming-border)',
                  color: 'var(--gaming-text-primary)'
                }}
                placeholder="Who is your audience?"
              />
            </div>
            <div>
              <label className="text-sm font-mono uppercase tracking-wider block mb-2" 
                     style={{ color: 'var(--gaming-text-secondary)' }}>NEURAL TONE</label>
              <select
                value={editForm.tone}
                onChange={(e) => setEditForm({...editForm, tone: e.target.value})}
                className="gaming-neural-input w-full px-3 py-2 rounded-lg font-mono"
                style={{
                  background: 'var(--gaming-bg-elevated)',
                  border: '1px solid var(--gaming-border)',
                  color: 'var(--gaming-text-primary)'
                }}
              >
                <option value="professional" style={{ background: 'var(--gaming-bg-elevated)', color: 'var(--gaming-text-primary)' }}>PROFESSIONAL</option>
                <option value="casual" style={{ background: 'var(--gaming-bg-elevated)', color: 'var(--gaming-text-primary)' }}>CASUAL</option>
                <option value="friendly" style={{ background: 'var(--gaming-bg-elevated)', color: 'var(--gaming-text-primary)' }}>FRIENDLY</option>
                <option value="excited" style={{ background: 'var(--gaming-bg-elevated)', color: 'var(--gaming-text-primary)' }}>EXCITED</option>
                <option value="urgent" style={{ background: 'var(--gaming-bg-elevated)', color: 'var(--gaming-text-primary)' }}>URGENT</option>
                <option value="technical" style={{ background: 'var(--gaming-bg-elevated)', color: 'var(--gaming-text-primary)' }}>TECHNICAL</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2 mt-4">
            <Button onClick={handleSaveEdit}>Save Changes</Button>
            <Button variant="secondary" onClick={() => setIsEditing(false)}>Cancel</Button>
          </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="gaming-neural-card p-4">
            <div className="gaming-border-glow"></div>
            <div className="relative z-10">
              <div className="text-sm font-mono uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>BUSINESS ENTITY</div>
              <div className="text-lg font-bold font-mono" style={{ color: 'var(--gaming-neon-cyan)' }}>
                {(campaign.config?.business || 'NOT SPECIFIED').toUpperCase()}
              </div>
            </div>
          </div>
          <div className="gaming-neural-card p-4">
            <div className="gaming-border-glow"></div>
            <div className="relative z-10">
              <div className="text-sm font-mono uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>PRODUCT MODULE</div>
              <div className="text-lg font-bold font-mono" style={{ color: 'var(--gaming-neon-cyan)' }}>
                {(campaign.config?.product || 'NOT SPECIFIED').toUpperCase()}
              </div>
            </div>
          </div>
          <div className="gaming-neural-card p-4">
            <div className="gaming-border-glow"></div>
            <div className="relative z-10">
              <div className="text-sm font-mono uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>TARGET MATRIX</div>
              <div className="text-lg font-bold font-mono" style={{ color: 'var(--gaming-neon-cyan)' }}>
                {(typeof campaign.target_audience === 'object' 
                  ? campaign.target_audience.description 
                  : campaign.target_audience || 'NOT SPECIFIED').toUpperCase()}
              </div>
            </div>
          </div>
          <div className="gaming-neural-card p-4">
            <div className="gaming-border-glow"></div>
            <div className="relative z-10">
              <div className="text-sm font-mono uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>NEURAL TONE</div>
              <div className="text-lg font-bold font-mono uppercase" style={{ color: 'var(--gaming-neon-cyan)' }}>
                {(campaign.tone || 'PROFESSIONAL').toUpperCase()}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Content Generation - Gaming Style */}
      <div className="gaming-neural-card p-6">
        <div className="gaming-border-glow"></div>
        <div className="relative z-10">
          <div className="mb-6">
            <h2 className="text-2xl font-black font-mono uppercase tracking-wider mb-3" 
                style={{ 
                  color: 'var(--gaming-neon-cyan)',
                  textShadow: '0 0 15px rgba(0, 255, 255, 0.5)'
                }}>NEURAL CONTENT FORGE</h2>
            <p className="text-sm font-mono mb-2" style={{ color: 'var(--gaming-text-secondary)' }}>
              GENERATE ANY TYPE OF CONTENT FOR THIS CAMPAIGN MATRIX. MIX AND MATCH AS NEEDED!
            </p>
            <p className="text-xs font-mono flex items-center gap-2" style={{ color: 'var(--gaming-neon-purple)' }}>
              <span className="animate-pulse">⚡</span>
              NEURAL TIP: IF YOUR PODCAST GOES VIRAL, GENERATE SOCIAL POSTS AND BLOGS TO AMPLIFY IT!
            </p>
          </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {/* Quick Content */}
          <Button size="sm" variant="secondary" onClick={() => handleGenerateContent('email')} disabled={generating}>
            <EnvelopeIcon className="h-4 w-4" />
            Email
          </Button>
          <Button size="sm" variant="secondary" onClick={() => handleGenerateContent('sms')} disabled={generating}>
            <ChatBubbleLeftIcon className="h-4 w-4" />
            SMS
          </Button>
          <Button size="sm" variant="secondary" onClick={() => handleGenerateContent('social_post')} disabled={generating}>
            <MegaphoneIcon className="h-4 w-4" />
            Social Post
          </Button>
          <Button size="sm" variant="secondary" onClick={() => handleGenerateContent('blog')} disabled={generating}>
            <NewspaperIcon className="h-4 w-4" />
            Blog Post
          </Button>
          
          {/* Advanced Content */}
          <Button size="sm" variant="secondary" onClick={() => handleGenerateContent('ebook')} disabled={generating}>
            <BookOpenIcon className="h-4 w-4" />
            eBook
          </Button>
          <Button size="sm" variant="secondary" onClick={() => handleGenerateContent('podcast')} disabled={generating}>
            <MicrophoneIcon className="h-4 w-4" />
            Podcast
          </Button>
          <Button size="sm" variant="secondary" onClick={() => handleGenerateContent('pitch_deck')} disabled={generating}>
            <PresentationChartBarIcon className="h-4 w-4" />
            Pitch Deck
          </Button>
          <Button size="sm" variant="secondary" onClick={() => handleGenerateContent('infographic')} disabled={generating}>
            <ChartPieIcon className="h-4 w-4" />
            Infographic
          </Button>
        </div>

        <div className="border-t border-dark-700 pt-4">
          <h3 className="text-lg font-semibold text-white mb-3">Generated Content</h3>

          {content.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <p className="mb-4">No content generated yet</p>
              <p className="text-sm">Click the buttons above to generate content for your campaign</p>
            </div>
          ) : (
            <div className="space-y-3">
              {content.map((item, index) => (
                <div
                  key={item.id || index}
                  className="p-4 bg-dark-800 rounded-lg border border-dark-700 hover:border-dark-600 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className="text-primary-400 mt-1">
                        {getContentIcon(item.content_type)}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-white mb-1">
                          {item.title || item.subject || item.content_type}
                        </div>
                        <p className="text-sm text-gray-400 line-clamp-2">
                          {item.content || item.body || item.preview_text || 'No preview available'}
                        </p>
                        {item.cta_text && (
                          <div className="mt-2">
                            <span className="text-xs text-primary-400 bg-primary-500/10 px-2 py-1 rounded">
                              CTA: {item.cta_text}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                    <Button 
                      size="sm" 
                      variant="ghost"
                      onClick={() => handleViewContent(item)}
                    >
                      View
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Analytics Preview - Gaming Style */}
      {campaign.status !== 'draft' && (
        <div className="gaming-neural-card p-6">
          <div className="gaming-border-glow"></div>
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-6">
              <ChartBarIcon className="h-6 w-6" style={{ 
                color: 'var(--gaming-neon-purple)',
                filter: 'drop-shadow(0 0 8px rgba(157, 78, 221, 0.8))'
              }} />
              <h2 className="text-xl font-bold font-mono uppercase tracking-wider" 
                  style={{ color: 'var(--gaming-neon-purple)' }}>NEURAL METRICS</h2>
            </div>
            <div className="text-center py-12" style={{ color: 'var(--gaming-text-secondary)' }}>
              <div className="gaming-loading-matrix mb-4 mx-auto"></div>
              <p className="font-mono uppercase tracking-wide">ANALYTICS MATRIX INITIALIZING...</p>
              <p className="font-mono text-sm mt-2">METRICS WILL APPEAR ONCE CAMPAIGN IS ACTIVE</p>
            </div>
          </div>
        </div>
      )}

      {/* Content Viewer Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setViewingContent(null);
        }}
        title={viewingContent?.subject || viewingContent?.title || 'Content Details'}
      >
        {viewingContent && (
          <div className="space-y-4">
            {/* Content Type Badge */}
            <div className="flex items-center gap-2">
              <div className="text-primary-400">
                {getContentIcon(viewingContent.content_type)}
              </div>
              <span className="text-sm font-medium text-gray-400">
                {viewingContent.content_type?.replace('_', ' ').toUpperCase()}
              </span>
            </div>

            {/* Subject Line (for emails) */}
            {viewingContent.subject && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-1">Subject</h3>
                <p className="text-white">{viewingContent.subject}</p>
              </div>
            )}

            {/* Preview Text (for emails) */}
            {viewingContent.preview_text && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-1">Preview</h3>
                <p className="text-gray-300">{viewingContent.preview_text}</p>
              </div>
            )}

            {/* Main Content */}
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-2">Content</h3>
              <div className="bg-dark-800 rounded-lg p-4 max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-gray-300 font-sans text-sm">
                  {viewingContent.body || viewingContent.content || 'No content available'}
                </pre>
              </div>
            </div>

            {/* CTA Button (if available) */}
            {viewingContent.cta_text && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-1">Call to Action</h3>
                <div className="inline-block bg-primary-500 text-white px-4 py-2 rounded-lg">
                  {viewingContent.cta_text}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-4 border-t border-dark-700">
              <Button
                variant="secondary"
                onClick={() => handleCopyContent(
                  viewingContent.body || viewingContent.content || ''
                )}
              >
                <ClipboardDocumentIcon className="h-4 w-4" />
                Copy Content
              </Button>
              <Button onClick={() => setIsModalOpen(false)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Custom Prompt Modal */}
      {showPromptModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-dark-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-semibold text-white">Generate {selectedContentType?.replace('_', ' ')}</h3>
                <p className="text-gray-400 text-sm mt-1">
                  Provide specific instructions for your {selectedContentType?.replace('_', ' ')} content
                </p>
              </div>
              <button
                onClick={() => {
                  setShowPromptModal(false);
                  setCustomPrompt('');
                  setSelectedContentType('');
                }}
                className="text-gray-400 hover:text-white"
                aria-label="Close modal"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            {/* Show business context */}
            <div className="bg-dark-700 rounded-lg p-4 mb-4">
              <h4 className="text-sm font-medium text-gray-400 mb-2">Business Context</h4>
              <div className="space-y-1 text-sm">
                <p className="text-gray-300">
                  <span className="text-gray-500">Company:</span> {editForm.business_name || 'Not specified'}
                </p>
                <p className="text-gray-300">
                  <span className="text-gray-500">Product:</span> {editForm.product || 'Not specified'}
                </p>
                <p className="text-gray-300">
                  <span className="text-gray-500">Audience:</span> {editForm.target_audience || 'Not specified'}
                </p>
                <p className="text-gray-300">
                  <span className="text-gray-500">Tone:</span> {editForm.tone || 'Professional'}
                </p>
              </div>
            </div>

            {/* Prompt templates based on content type */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-400 mb-2">
                {selectedContentType === 'blog' && 'Blog post topic and key points to cover:'}
                {selectedContentType === 'ebook' && 'eBook title, chapters, and main themes:'}
                {selectedContentType === 'podcast' && 'Podcast episode topic, guests, and discussion points:'}
                {selectedContentType === 'pitch_deck' && 'Pitch deck purpose, key slides, and data to include:'}
                {selectedContentType === 'infographic' && 'Infographic topic, data points, and visual style:'}
              </label>
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder={
                  selectedContentType === 'blog' ? 'Write a comprehensive blog post about [topic]. Include sections on [point 1], [point 2], and [point 3]. Make it SEO-optimized with relevant keywords.' :
                  selectedContentType === 'ebook' ? 'Create an ebook titled "[Title]" with [X] chapters covering [main theme]. Include actionable insights and case studies.' :
                  selectedContentType === 'podcast' ? 'Create a [duration]-minute podcast script about [topic]. Include intro, main discussion with [guest type], and outro with call-to-action.' :
                  selectedContentType === 'pitch_deck' ? 'Create a pitch deck for [purpose]. Include slides for problem, solution, market size, business model, team, and financials.' :
                  selectedContentType === 'infographic' ? 'Design an infographic about [topic] with [X] key statistics, comparison charts, and a compelling visual narrative.' :
                  'Describe what you want to generate...'
                }
                className="w-full h-32 px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            {/* Quick suggestions */}
            <div className="mb-4">
              <p className="text-sm text-gray-400 mb-2">Quick templates:</p>
              <div className="flex flex-wrap gap-2">
                {selectedContentType === 'blog' && [
                  'How-to guide',
                  'Industry trends',
                  'Case study',
                  'Best practices',
                  'Product update'
                ].map(template => (
                  <button
                    key={template}
                    onClick={() => setCustomPrompt(`Write a ${template} blog post about `)}
                    className="px-3 py-1 text-xs bg-dark-700 text-gray-300 rounded-full hover:bg-dark-600"
                  >
                    {template}
                  </button>
                ))}
                {selectedContentType === 'ebook' && [
                  'Ultimate guide',
                  'Industry report',
                  'How-to manual',
                  'Whitepaper',
                  'Research study'
                ].map(template => (
                  <button
                    key={template}
                    onClick={() => setCustomPrompt(`Create a ${template} ebook about `)}
                    className="px-3 py-1 text-xs bg-dark-700 text-gray-300 rounded-full hover:bg-dark-600"
                  >
                    {template}
                  </button>
                ))}
                {selectedContentType === 'podcast' && [
                  'Interview',
                  'Solo episode',
                  'Panel discussion',
                  'Q&A session',
                  'News roundup'
                ].map(template => (
                  <button
                    key={template}
                    onClick={() => setCustomPrompt(`Create a podcast ${template} about `)}
                    className="px-3 py-1 text-xs bg-dark-700 text-gray-300 rounded-full hover:bg-dark-600"
                  >
                    {template}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <Button
                variant="ghost"
                onClick={() => {
                  setShowPromptModal(false);
                  setCustomPrompt('');
                  setSelectedContentType('');
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={handleGenerateWithPrompt}
                disabled={!customPrompt.trim() || generating}
              >
                {generating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    Generating...
                  </>
                ) : (
                  <>
                    <SparklesIcon className="h-4 w-4" />
                    Generate {selectedContentType?.replace('_', ' ')}
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-dark-800 rounded-lg p-6 max-w-md w-full">
            <div className="flex items-start gap-3 mb-4">
              <div className="flex-shrink-0 w-10 h-10 bg-red-500/20 rounded-full flex items-center justify-center">
                <TrashIcon className="h-5 w-5 text-red-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Delete Campaign</h3>
                <p className="text-gray-400 text-sm mt-1">
                  Are you sure you want to delete "{campaign?.name || 'this campaign'}"? This action cannot be undone.
                </p>
              </div>
            </div>
            
            <div className="bg-dark-700 rounded-lg p-3 mb-4">
              <p className="text-sm text-gray-300">
                <span className="text-red-400">Warning:</span> All content generated for this campaign will be permanently deleted.
              </p>
            </div>
            
            <div className="flex justify-end gap-3">
              <Button
                variant="ghost"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </Button>
              <Button
                variant="secondary"
                onClick={() => {
                  handleDeleteCampaign();
                  setShowDeleteConfirm(false);
                }}
                className="bg-red-500/20 text-red-400 hover:bg-red-500/30"
              >
                Delete Campaign
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
    </div>
  );
}
