import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { campaignService } from '../../services/campaign.service';
import { toast } from 'react-hot-toast';
import { 
  PlusIcon, 
  PlayIcon, 
  PauseIcon,
  ChartBarIcon,
  CalendarIcon,
  UsersIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

export function CampaignsPage() {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'active' | 'draft' | 'paused' | 'completed'>('all');

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      setLoading(true);
      const allCampaigns = await campaignService.getCampaigns();
      setCampaigns(allCampaigns);
    } catch (error) {
      console.error('Failed to load campaigns:', error);
      toast.error('Failed to load campaigns');
    } finally {
      setLoading(false);
    }
  };

  const filteredCampaigns = campaigns.filter(campaign => {
    if (filter === 'all') return true;
    return campaign.status === filter;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'paused':
        return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 'completed':
        return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      case 'draft':
      default:
        return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <PlayIcon className="h-4 w-4" />;
      case 'paused':
        return <PauseIcon className="h-4 w-4" />;
      case 'completed':
        return <CheckCircleIcon className="h-4 w-4" />;
      case 'draft':
      default:
        return <ClockIcon className="h-4 w-4" />;
    }
  };

  const handleCreateCampaign = () => {
    navigate('/workflows'); // Go to workflows page to create from template
    toast.success('Choose a template to create your campaign');
  };

  const stats = {
    total: campaigns.length,
    active: campaigns.filter(c => c.status === 'active').length,
    draft: campaigns.filter(c => c.status === 'draft').length,
    paused: campaigns.filter(c => c.status === 'paused').length,
    completed: campaigns.filter(c => c.status === 'completed').length,
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
          <h1 className="text-3xl font-bold text-white">Campaigns</h1>
          <p className="text-gray-400 mt-1">Manage your multi-channel marketing campaigns</p>
        </div>
        <Button onClick={handleCreateCampaign}>
          <PlusIcon className="h-4 w-4" />
          New Campaign
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card 
          className={`cursor-pointer transition-all ${filter === 'all' ? 'ring-2 ring-primary-500' : ''}`}
          onClick={() => setFilter('all')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Total</p>
              <p className="text-2xl font-bold text-white">{stats.total}</p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-gray-400" />
          </div>
        </Card>
        
        <Card 
          className={`cursor-pointer transition-all ${filter === 'active' ? 'ring-2 ring-green-500' : ''}`}
          onClick={() => setFilter('active')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Active</p>
              <p className="text-2xl font-bold text-green-400">{stats.active}</p>
            </div>
            <PlayIcon className="h-8 w-8 text-green-400" />
          </div>
        </Card>

        <Card 
          className={`cursor-pointer transition-all ${filter === 'draft' ? 'ring-2 ring-gray-500' : ''}`}
          onClick={() => setFilter('draft')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Draft</p>
              <p className="text-2xl font-bold text-gray-400">{stats.draft}</p>
            </div>
            <ClockIcon className="h-8 w-8 text-gray-400" />
          </div>
        </Card>

        <Card 
          className={`cursor-pointer transition-all ${filter === 'paused' ? 'ring-2 ring-yellow-500' : ''}`}
          onClick={() => setFilter('paused')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Paused</p>
              <p className="text-2xl font-bold text-yellow-400">{stats.paused}</p>
            </div>
            <PauseIcon className="h-8 w-8 text-yellow-400" />
          </div>
        </Card>

        <Card 
          className={`cursor-pointer transition-all ${filter === 'completed' ? 'ring-2 ring-blue-500' : ''}`}
          onClick={() => setFilter('completed')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Completed</p>
              <p className="text-2xl font-bold text-blue-400">{stats.completed}</p>
            </div>
            <CheckCircleIcon className="h-8 w-8 text-blue-400" />
          </div>
        </Card>
      </div>

      {/* Campaign List */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">
          {filter === 'all' ? 'All Campaigns' : `${filter.charAt(0).toUpperCase() + filter.slice(1)} Campaigns`}
        </h2>
        
        {filteredCampaigns.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-gray-400 mb-4">
              {filter === 'all' 
                ? 'No campaigns yet. Create your first campaign to get started.'
                : `No ${filter} campaigns found.`}
            </p>
            {filter === 'all' && (
              <Button onClick={handleCreateCampaign}>
                Create Your First Campaign
              </Button>
            )}
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {filteredCampaigns.map((campaign) => (
              <Card 
                key={campaign.id} 
                hover 
                onClick={() => navigate(`/campaigns/${campaign.id}`)}
                className="cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-white">
                        {campaign.name || campaign.title || 'Untitled Campaign'}
                      </h3>
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(campaign.status)}`}>
                        {getStatusIcon(campaign.status)}
                        {campaign.status}
                      </span>
                    </div>
                    
                    <p className="text-gray-400 mb-3">
                      {campaign.description || 'No description provided'}
                    </p>
                    
                    <div className="flex items-center gap-6 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <CalendarIcon className="h-4 w-4" />
                        Created: {campaign.created_at ? new Date(campaign.created_at).toLocaleDateString() : 'Unknown'}
                      </div>
                      
                      {campaign.target_audience && (
                        <div className="flex items-center gap-1">
                          <UsersIcon className="h-4 w-4" />
                          {typeof campaign.target_audience === 'string' 
                            ? campaign.target_audience 
                            : campaign.target_audience.description || 'General'}
                        </div>
                      )}
                      
                      {campaign.content_count !== undefined && (
                        <div className="flex items-center gap-1">
                          <ChartBarIcon className="h-4 w-4" />
                          {campaign.content_count} content items
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/campaigns/${campaign.id}`);
                    }}
                  >
                    View Details
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}