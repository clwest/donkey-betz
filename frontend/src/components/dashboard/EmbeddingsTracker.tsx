import React, { useEffect, useState } from 'react';
import { Brain, TrendingUp, Activity, Database } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

interface EmbeddingsStats {
  total_embeddings: number;
  breakdown: {
    [key: string]: {
      total?: number;
      with_embeddings?: number;
      documents?: number;
    };
  };
  recent_activity: {
    last_created?: string;
    created_today?: number;
  };
  health_status: {
    pgvector_version?: string;
    index_count?: number;
    index_type?: string;
    avg_search_ms?: number;
    status?: 'healthy' | 'warning' | 'inactive' | 'error';
  };
  trend_data: Array<{
    date: string;
    count: number;
  }>;
}

const EmbeddingsTracker: React.FC = () => {
  const [stats, setStats] = useState<EmbeddingsStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuthStore();

  const fetchStats = async () => {
    try {
      const authToken = token || localStorage.getItem('authToken') || '993f8273f70877e23b5c7d2f92ed30562a089fe3';
      // Use the API base URL from environment or default
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/v1/dashboard/embeddings-stats/`, {
        headers: {
          'Authorization': `Token ${authToken}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch embeddings stats');
      
      const data = await response.json();
      setStats(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching embeddings stats:', err);
      setError('Failed to load embeddings data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusIndicator = (status?: string) => {
    const color = status === 'healthy' ? 'bg-green-500' : 
                  status === 'warning' ? 'bg-yellow-500' : 
                  status === 'error' ? 'bg-red-500' : 'bg-gray-500';
    
    return (
      <div className={`w-2 h-2 ${color} rounded-full animate-pulse`} />
    );
  };

  const formatTime = (timestamp?: string) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
  };

  const renderSparkline = () => {
    if (!stats?.trend_data?.length) return null;
    
    const max = Math.max(...stats.trend_data.map(d => d.count), 1);
    const points = stats.trend_data.map((d, i) => {
      const x = (i / (stats.trend_data.length - 1)) * 100;
      const y = 100 - (d.count / max) * 100;
      return `${x},${y}`;
    }).join(' ');

    return (
      <svg className="w-full h-12" viewBox="0 0 100 100" preserveAspectRatio="none">
        <polyline
          points={points}
          fill="none"
          stroke="url(#gradient)"
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#60a5fa" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="1" />
          </linearGradient>
        </defs>
      </svg>
    );
  };

  if (loading) {
    return (
      <div className="bg-gray-900/50 backdrop-blur-xl rounded-xl p-6 border border-gray-800">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-8 bg-gray-700 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-700 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900/50 backdrop-blur-xl rounded-xl p-6 border border-red-800">
        <div className="flex items-center gap-2 text-red-400">
          <Brain className="w-5 h-5" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`bg-gray-900/50 backdrop-blur-xl rounded-xl p-6 border border-gray-800 cursor-pointer transition-all ${
        expanded ? 'col-span-2' : ''
      }`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/20 rounded-lg">
            <Brain className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Embeddings Tracker</h3>
            <p className="text-sm text-gray-400">Vector Database Status</p>
          </div>
        </div>
        {getStatusIndicator(stats?.health_status?.status)}
      </div>

      <div className="space-y-4">
        {/* Main Stats */}
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-white">
            {stats?.total_embeddings?.toLocaleString() || '0'}
          </span>
          <span className="text-sm text-gray-400">total vectors</span>
        </div>

        {/* Breakdown */}
        <div className="space-y-2">
          {Object.entries(stats?.breakdown || {}).map(([name, data]) => (
            <div key={name} className="flex justify-between items-center">
              <span className="text-sm text-gray-400">{name}:</span>
              <span className="text-sm text-white font-medium">
                {data.with_embeddings !== undefined ? 
                  `${data.with_embeddings?.toLocaleString()} / ${data.total?.toLocaleString()}` :
                  `${data.documents?.toLocaleString()} docs`
                }
              </span>
            </div>
          ))}
        </div>

        {/* Sparkline */}
        <div className="pt-2">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-gray-500">7-day trend</span>
            <span className="text-xs text-blue-400">
              {stats?.recent_activity?.created_today || 0} today
            </span>
          </div>
          {renderSparkline()}
        </div>

        {/* Expanded Details */}
        {expanded && (
          <div className="pt-4 border-t border-gray-800 space-y-3">
            {/* Recent Activity */}
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Recent Activity
              </h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Last embedding:</span>
                  <span className="text-gray-300">
                    {formatTime(stats?.recent_activity?.last_created)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Created today:</span>
                  <span className="text-gray-300">
                    {stats?.recent_activity?.created_today || 0}
                  </span>
                </div>
              </div>
            </div>

            {/* Health Status */}
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                <Database className="w-4 h-4" />
                System Health
              </h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">pgvector:</span>
                  <span className="text-gray-300">
                    v{stats?.health_status?.pgvector_version || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Index type:</span>
                  <span className="text-gray-300">
                    {stats?.health_status?.index_type || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Indexes:</span>
                  <span className="text-gray-300">
                    {stats?.health_status?.index_count || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Search speed:</span>
                  <span className={getStatusColor(stats?.health_status?.status)}>
                    {stats?.health_status?.avg_search_ms?.toFixed(2) || '0'} ms
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Status:</span>
                  <span className={`capitalize ${getStatusColor(stats?.health_status?.status)}`}>
                    {stats?.health_status?.status || 'Unknown'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmbeddingsTracker;