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
    <div className="space-y-6" style={{ backgroundColor: 'var(--gaming-bg-primary)', minHeight: '100vh' }}>
      {/* Header - Gaming Style */}
      <div className="gaming-neural-card p-6">
        <div className="gaming-border-glow"></div>
        <div className="relative z-10 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-black font-mono uppercase tracking-wider" 
                style={{ 
                  color: 'var(--gaming-neon-cyan)',
                  textShadow: '0 0 20px rgba(0, 255, 255, 0.5)'
                }}>CAMPAIGN MATRIX</h1>
            <p className="mt-3 font-mono" style={{ color: 'var(--gaming-text-secondary)' }}>
              MANAGE YOUR MULTI-CHANNEL NEURAL CAMPAIGNS
            </p>
          </div>
          <button
            onClick={handleCreateCampaign}
            className="gaming-btn-active px-8 py-4 rounded-xl font-mono font-bold text-sm uppercase tracking-wider flex items-center gap-3 transition-all duration-300 hover:scale-105"
            style={{
              background: 'var(--gaming-gradient-primary)',
              border: '1px solid var(--gaming-neon-cyan)',
              boxShadow: 'var(--gaming-glow-primary)'
            }}
          >
            <PlusIcon className="h-5 w-5" />
            NEW CAMPAIGN
          </button>
        </div>
      </div>

      {/* Neural Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div 
          className={`gaming-neural-card p-4 cursor-pointer transition-all duration-300 hover:scale-105 ${
            filter === 'all' ? 'ring-2' : ''
          }`}
          style={{
            borderColor: filter === 'all' ? 'var(--gaming-neon-cyan)' : 'var(--gaming-border)',
            boxShadow: filter === 'all' ? 'var(--gaming-glow-primary)' : undefined
          }}
          onClick={() => setFilter('all')}
        >
          <div className="gaming-border-glow"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div>
              <p className="text-sm font-mono uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>TOTAL</p>
              <p className="text-2xl font-bold font-mono" style={{ color: 'var(--gaming-neon-cyan)' }}>{stats.total}</p>
            </div>
            <ChartBarIcon className="h-8 w-8" style={{ color: 'var(--gaming-neon-cyan)' }} />
          </div>
        </div>
        
        <div 
          className={`gaming-neural-card p-4 cursor-pointer transition-all duration-300 hover:scale-105 ${
            filter === 'active' ? 'ring-2' : ''
          }`}
          style={{
            borderColor: filter === 'active' ? 'var(--gaming-neon-green)' : 'var(--gaming-border)',
            boxShadow: filter === 'active' ? '0 0 20px rgba(57, 255, 20, 0.3)' : undefined
          }}
          onClick={() => setFilter('active')}
        >
          <div className="gaming-border-glow"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div>
              <p className="text-sm font-mono uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>ACTIVE</p>
              <p className="text-2xl font-bold font-mono" style={{ color: 'var(--gaming-neon-green)' }}>{stats.active}</p>
            </div>
            <PlayIcon className="h-8 w-8" style={{ color: 'var(--gaming-neon-green)' }} />
          </div>
        </div>

        <div 
          className={`gaming-neural-card p-4 cursor-pointer transition-all duration-300 hover:scale-105 ${
            filter === 'draft' ? 'ring-2' : ''
          }`}
          style={{
            borderColor: filter === 'draft' ? 'var(--gaming-text-secondary)' : 'var(--gaming-border)',
            boxShadow: filter === 'draft' ? '0 0 20px rgba(128, 128, 128, 0.3)' : undefined
          }}
          onClick={() => setFilter('draft')}
        >
          <div className="gaming-border-glow"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div>
              <p className="text-sm font-mono uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>DRAFT</p>
              <p className="text-2xl font-bold font-mono" style={{ color: 'var(--gaming-text-secondary)' }}>{stats.draft}</p>
            </div>
            <ClockIcon className="h-8 w-8" style={{ color: 'var(--gaming-text-secondary)' }} />
          </div>
        </div>

        <div 
          className={`gaming-neural-card p-4 cursor-pointer transition-all duration-300 hover:scale-105 ${
            filter === 'paused' ? 'ring-2' : ''
          }`}
          style={{
            borderColor: filter === 'paused' ? '#FFD700' : 'var(--gaming-border)',
            boxShadow: filter === 'paused' ? '0 0 20px rgba(255, 215, 0, 0.3)' : undefined
          }}
          onClick={() => setFilter('paused')}
        >
          <div className="gaming-border-glow"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div>
              <p className="text-sm font-mono uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>PAUSED</p>
              <p className="text-2xl font-bold font-mono" style={{ color: '#FFD700' }}>{stats.paused}</p>
            </div>
            <PauseIcon className="h-8 w-8" style={{ color: '#FFD700' }} />
          </div>
        </div>

        <div 
          className={`gaming-neural-card p-4 cursor-pointer transition-all duration-300 hover:scale-105 ${
            filter === 'completed' ? 'ring-2' : ''
          }`}
          style={{
            borderColor: filter === 'completed' ? 'var(--gaming-neon-purple)' : 'var(--gaming-border)',
            boxShadow: filter === 'completed' ? '0 0 20px rgba(157, 78, 221, 0.3)' : undefined
          }}
          onClick={() => setFilter('completed')}
        >
          <div className="gaming-border-glow"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div>
              <p className="text-sm font-mono uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>COMPLETED</p>
              <p className="text-2xl font-bold font-mono" style={{ color: 'var(--gaming-neon-purple)' }}>{stats.completed}</p>
            </div>
            <CheckCircleIcon className="h-8 w-8" style={{ color: 'var(--gaming-neon-purple)' }} />
          </div>
        </div>
      </div>

      {/* Neural Campaign Registry */}
      <div>
        <h2 className="text-2xl font-bold font-mono uppercase tracking-wider mb-6" 
            style={{ color: 'var(--gaming-neon-cyan)' }}>
          {filter === 'all' ? 'ALL CAMPAIGNS' : `${filter.toUpperCase()} CAMPAIGNS`}
        </h2>
        
        {filteredCampaigns.length === 0 ? (
          <div className="gaming-neural-card p-12 text-center">
            <div className="gaming-border-glow"></div>
            <div className="relative z-10">
              <div className="gaming-loading-matrix mb-6 mx-auto"></div>
              <p className="font-mono mb-6" style={{ color: 'var(--gaming-text-secondary)' }}>
                {filter === 'all' 
                  ? 'NO CAMPAIGNS IN THE MATRIX YET. INITIALIZE YOUR FIRST CAMPAIGN TO BEGIN.'
                  : `NO ${filter.toUpperCase()} CAMPAIGNS DETECTED.`}
              </p>
              {filter === 'all' && (
                <button
                  onClick={handleCreateCampaign}
                  className="gaming-btn-active px-8 py-4 rounded-xl font-mono font-bold text-sm uppercase tracking-wider transition-all duration-300 hover:scale-105"
                  style={{
                    background: 'var(--gaming-gradient-primary)',
                    border: '1px solid var(--gaming-neon-cyan)',
                    boxShadow: 'var(--gaming-glow-primary)'
                  }}
                >
                  CREATE FIRST CAMPAIGN
                </button>
              )}
            </div>
          </div>
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