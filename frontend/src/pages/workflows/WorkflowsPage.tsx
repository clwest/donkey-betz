import { useState, useEffect } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { useNavigate } from 'react-router-dom';
import { PlusIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { campaignService } from '../../services/campaign.service';
import { toast } from 'react-hot-toast';

export function WorkflowsPage() {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const templates = await campaignService.getTemplates();
      
      // Transform templates to workflow template format
      const templateData = templates.map((template: any) => ({
        id: template.id,
        name: template.name,
        description: template.description,
        category: template.campaign_type === 'email' ? 'Email' : template.campaign_type === 'multi' ? 'Marketing' : 'Content',
        popularity: Math.floor(Math.random() * 30) + 70, // Random popularity for now
      }));
      setTemplates(templateData);
    } catch (error) {
      console.error('Failed to load templates:', error);
      // Use fallback mock data if API fails
      setTemplates([
        {
          id: 't1',
          name: 'Blog to Social Pipeline',
          description: 'Convert blog posts into social media content',
          category: 'Content',
          popularity: 95,
        },
        {
          id: 't2',
          name: 'Research Paper Generator',
          description: 'Transform documents into academic papers',
          category: 'Research',
          popularity: 78,
        },
        {
          id: 't3',
          name: 'Marketing Campaign',
          description: 'Complete multi-channel marketing workflow',
          category: 'Marketing',
          popularity: 88,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };


  const handleTemplateClick = async (templateId: string, templateName: string) => {
    try {
      const loadingToast = toast.loading('Creating campaign from template...');
      const campaign = await campaignService.createFromTemplate(templateId, {
        title: `New ${templateName}`,
        target_audience: 'General audience',
      });
      toast.dismiss(loadingToast);
      toast.success('Campaign created successfully!');
      navigate(`/campaigns/${campaign.id}`);
    } catch (error) {
      toast.error('Failed to create campaign from template');
      console.error(error);
    }
  };

  const handleCreateCustom = async () => {
    try {
      // Create a blank campaign
      const campaign = await campaignService.createCampaign({
        title: 'Custom Campaign',
        description: 'AI-powered custom workflow',
        campaign_type: 'multi' as any,
        target_audience: 'Define your audience',
      });
      
      toast.success('Custom campaign created!');
      navigate(`/campaigns/${campaign.id}`);
    } catch (error) {
      toast.error('Failed to create custom campaign');
      console.error(error);
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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Workflow Templates</h1>
          <p className="text-gray-400 mt-1">Choose a template or create your own custom workflow</p>
        </div>
        <Button onClick={() => handleCreateCustom()}>
          <PlusIcon className="h-4 w-4" />
          Custom Workflow
        </Button>
      </div>


      {/* Workflow Templates */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Custom Workflow Card */}
        <Card 
          hover
          onClick={handleCreateCustom}
          className="border-2 border-dashed border-primary-500/30 hover:border-primary-500/50"
        >
          <div className="mb-4">
            <div className="flex items-start justify-between">
              <h3 className="font-semibold text-white">Create Custom Workflow</h3>
              <SparklesIcon className="h-5 w-5 text-primary-400" />
            </div>
            <p className="text-sm text-gray-400 mt-2">
              Build your own AI-powered workflow from scratch with custom prompts and settings
            </p>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-xs text-primary-400 bg-primary-500/10 px-2 py-1 rounded">
              AI Assistant
            </span>
            <div className="text-sm text-gray-400">
              Fully customizable
            </div>
          </div>
        </Card>

        {/* Template Cards */}
        {templates.map((template) => (
          <Card 
            key={template.id} 
            hover
            onClick={() => handleTemplateClick(template.id, template.name)}
          >
            <div className="mb-4">
              <div className="flex items-start justify-between">
                <h3 className="font-semibold text-white">{template.name}</h3>
                <span className="px-2 py-1 text-xs bg-primary-500/20 text-primary-400 rounded-full">
                  {template.category}
                </span>
              </div>
              <p className="text-sm text-gray-400 mt-2">{template.description}</p>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex -space-x-2">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="w-6 h-6 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 border-2 border-dark-900" />
                ))}
              </div>
              <div className="text-sm text-gray-400">
                {template.popularity}% popularity
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}