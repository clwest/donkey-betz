import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Star, TrendingUp, TrendingDown, MessageSquare,
  ThumbsUp, ThumbsDown, BarChart3, Calendar,
  Filter, Download, ChevronRight
} from 'lucide-react';
import { feedbackService } from '../../services/feedbackService';
import type { FeedbackAnalytics } from '../../services/feedbackService';

export const FeedbackDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<FeedbackAnalytics | null>(null);
  const [feedbackHistory, setFeedbackHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [selectedType, setSelectedType] = useState<string>('all');

  useEffect(() => {
    loadData();
  }, [selectedPeriod, selectedType]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [analyticsData, historyData] = await Promise.all([
        feedbackService.getAnalytics(selectedPeriod, selectedType === 'all' ? undefined : selectedType),
        feedbackService.getFeedbackHistory({ content_type: selectedType === 'all' ? undefined : selectedType })
      ]);
      
      setAnalytics(analyticsData);
      setFeedbackHistory(historyData.feedback);
    } catch (error) {
      console.error('Failed to load feedback data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      text: 'from-blue-500 to-cyan-500',
      image: 'from-purple-500 to-pink-500',
      video: 'from-green-500 to-emerald-500',
      blog: 'from-orange-500 to-red-500',
      social: 'from-indigo-500 to-purple-500',
      ebook: 'from-yellow-500 to-orange-500',
      voice: 'from-teal-500 to-green-500',
      research: 'from-pink-500 to-rose-500',
    };
    return colors[type] || 'from-gray-500 to-gray-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Feedback Analytics</h1>
        <p className="text-gray-400">Track and analyze user feedback across all content</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 mb-8">
        <div className="flex items-center gap-2 bg-gray-800/50 rounded-lg p-1">
          {[7, 30, 90].map((days) => (
            <button
              key={days}
              onClick={() => setSelectedPeriod(days)}
              className={`px-4 py-2 rounded-md transition-all ${
                selectedPeriod === days
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {days}d
            </button>
          ))}
        </div>

        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white"
        >
          <option value="all">All Content Types</option>
          <option value="text">Text</option>
          <option value="image">Images</option>
          <option value="video">Videos</option>
          <option value="blog">Blog Posts</option>
          <option value="social">Social Posts</option>
          <option value="ebook">eBooks</option>
          <option value="voice">Voice</option>
          <option value="research">Research</option>
        </select>

        <button className="ml-auto px-4 py-2 bg-gray-800/50 text-gray-400 rounded-lg hover:text-white transition-colors flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export
        </button>
      </div>

      {analytics && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700"
            >
              <div className="flex items-center justify-between mb-4">
                <MessageSquare className="w-8 h-8 text-purple-500" />
                <span className="text-2xl font-bold text-white">
                  {analytics.total_feedback}
                </span>
              </div>
              <p className="text-gray-400 text-sm">Total Feedback</p>
              <p className="text-xs text-gray-500 mt-1">Last {selectedPeriod} days</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700"
            >
              <div className="flex items-center justify-between mb-4">
                <Star className="w-8 h-8 text-yellow-500" />
                <span className="text-2xl font-bold text-white">
                  {(Object.values(analytics.by_content_type)
                    .reduce((sum, item) => sum + item.average_rating, 0) / 
                    Object.keys(analytics.by_content_type).length || 0
                  ).toFixed(1)}
                </span>
              </div>
              <p className="text-gray-400 text-sm">Average Rating</p>
              <div className="flex items-center gap-1 mt-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`w-3 h-3 ${
                      star <= Math.round(4.2) 
                        ? 'fill-yellow-500 text-yellow-500'
                        : 'text-gray-600'
                    }`}
                  />
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700"
            >
              <div className="flex items-center justify-between mb-4">
                <ThumbsUp className="w-8 h-8 text-green-500" />
                <span className="text-2xl font-bold text-white">
                  {Object.values(analytics.by_content_type)
                    .reduce((sum, item) => sum + item.positive, 0)}
                </span>
              </div>
              <p className="text-gray-400 text-sm">Positive Feedback</p>
              <p className="text-xs text-green-500 mt-1">4-5 star ratings</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700"
            >
              <div className="flex items-center justify-between mb-4">
                <TrendingUp className="w-8 h-8 text-blue-500" />
                <span className="text-2xl font-bold text-white">
                  {analytics.user_contribution}
                </span>
              </div>
              <p className="text-gray-400 text-sm">Your Contribution</p>
              <p className="text-xs text-gray-500 mt-1">Feedback given</p>
            </motion.div>
          </div>

          {/* Content Type Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-6">Feedback by Content Type</h3>
              <div className="space-y-4">
                {Object.entries(analytics.by_content_type).map(([type, data]) => (
                  <div key={type} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300 capitalize">{type}</span>
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-gray-400">
                          {data.total_feedback} reviews
                        </span>
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                          <span className="text-white font-medium">
                            {data.average_rating.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <div
                        className="h-2 bg-green-500 rounded-l"
                        style={{ width: `${(data.positive / data.total_feedback) * 100}%` }}
                      />
                      <div
                        className="h-2 bg-yellow-500"
                        style={{ width: `${(data.neutral / data.total_feedback) * 100}%` }}
                      />
                      <div
                        className="h-2 bg-red-500 rounded-r"
                        style={{ width: `${(data.negative / data.total_feedback) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Feedback */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-6">Recent Feedback</h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {feedbackHistory.slice(0, 5).map((feedback) => (
                  <div
                    key={feedback.id}
                    className="p-3 bg-gray-900/50 rounded-lg border border-gray-700"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium bg-gradient-to-r ${
                          getTypeColor(feedback.content_type)
                        } text-white`}>
                          {feedback.content_type}
                        </span>
                        <div className="flex items-center gap-1">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-3 h-3 ${
                                i < feedback.overall_rating
                                  ? 'fill-yellow-500 text-yellow-500'
                                  : 'text-gray-600'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(feedback.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {feedback.comments && (
                      <p className="text-sm text-gray-300 line-clamp-2">
                        {feedback.comments}
                      </p>
                    )}
                  </div>
                ))}
              </div>
              
              <button className="mt-4 w-full py-2 bg-purple-600/20 text-purple-400 rounded-lg hover:bg-purple-600/30 transition-colors flex items-center justify-center gap-2">
                View All Feedback
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};