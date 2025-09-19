import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Star, ThumbsUp, ThumbsDown, MessageSquare, 
  Send, X, ChevronDown, TrendingUp, AlertCircle 
} from 'lucide-react';
import { feedbackService } from '../../services/feedbackService';
import type { Feedback, FeedbackStats } from '../../services/feedbackService';
import toast from 'react-hot-toast';

interface FeedbackWidgetProps {
  contentType: Feedback['content_type'];
  contentId: number;
  contentTitle?: string;
  inline?: boolean;
  showStats?: boolean;
  onFeedbackSubmit?: () => void;
}

export const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({
  contentType,
  contentId,
  contentTitle = 'this content',
  inline = false,
  showStats = true,
  onFeedbackSubmit,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [userFeedback, setUserFeedback] = useState<Feedback | null>(null);
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comments, setComments] = useState('');
  const [suggestions, setSuggestions] = useState('');
  const [detailedRatings, setDetailedRatings] = useState({
    quality: 0,
    accuracy: 0,
    usefulness: 0,
  });
  const [quickAnswers, setQuickAnswers] = useState({
    would_recommend: null as boolean | null,
    met_expectations: null as boolean | null,
    saved_time: null as boolean | null,
  });
  const [loading, setLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    loadFeedback();
  }, [contentType, contentId]);

  const loadFeedback = async () => {
    try {
      const data = await feedbackService.getContentFeedback(contentType, contentId);
      if (data.user_feedback) {
        setUserFeedback(data.user_feedback);
        setRating(data.user_feedback.overall_rating);
        setComments(data.user_feedback.comments || '');
        setSuggestions(data.user_feedback.suggestions || '');
        setDetailedRatings({
          quality: data.user_feedback.quality_rating || 0,
          accuracy: data.user_feedback.accuracy_rating || 0,
          usefulness: data.user_feedback.usefulness_rating || 0,
        });
        setQuickAnswers({
          would_recommend: data.user_feedback.would_recommend || null,
          met_expectations: data.user_feedback.met_expectations || null,
          saved_time: data.user_feedback.saved_time || null,
        });
      }
      setStats(data.stats);
    } catch (error) {
      console.error('Failed to load feedback:', error);
    }
  };

  const handleQuickFeedback = async (isPositive: boolean) => {
    try {
      await feedbackService.quickFeedback(contentType, contentId, isPositive);
      toast.success(`Thank you for your feedback!`);
      loadFeedback();
      onFeedbackSubmit?.();
    } catch (error) {
      toast.error('Failed to submit feedback');
    }
  };

  const handleSubmit = async () => {
    if (rating === 0) {
      toast.error('Please select a rating');
      return;
    }

    setLoading(true);
    try {
      const feedback: Feedback = {
        content_type: contentType,
        content_id: contentId,
        overall_rating: rating,
        quality_rating: detailedRatings.quality || undefined,
        accuracy_rating: detailedRatings.accuracy || undefined,
        usefulness_rating: detailedRatings.usefulness || undefined,
        comments,
        suggestions,
        would_recommend: quickAnswers.would_recommend || undefined,
        met_expectations: quickAnswers.met_expectations || undefined,
        saved_time: quickAnswers.saved_time || undefined,
        feedback_type: rating <= 2 ? 'quality' : rating >= 4 ? 'usefulness' : 'general',
      };

      await feedbackService.submitFeedback(feedback);
      toast.success('Feedback submitted successfully!');
      setIsOpen(false);
      loadFeedback();
      onFeedbackSubmit?.();
    } catch (error) {
      toast.error('Failed to submit feedback');
    } finally {
      setLoading(false);
    }
  };

  const StarRating = ({ value, onChange, size = 'md' }: any) => {
    const sizes = {
      sm: 'w-4 h-4',
      md: 'w-6 h-6',
      lg: 'w-8 h-8',
    };

    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => onChange(star)}
            onMouseEnter={() => setHoverRating(star)}
            onMouseLeave={() => setHoverRating(0)}
            className="transition-transform hover:scale-110"
          >
            <Star
              className={`${sizes[size]} ${
                (hoverRating || value) >= star
                  ? 'fill-yellow-500 text-yellow-500'
                  : 'text-muted-foreground'
              }`}
            />
          </button>
        ))}
      </div>
    );
  };

  if (inline) {
    return (
      <div className="bg-card/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium text-foreground">Rate {contentTitle}</h4>
          {stats && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Star className="w-3 h-3 fill-current" />
              <span>{stats.average_rating?.toFixed(1) || 'N/A'}</span>
              <span>({stats.total_feedback} reviews)</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-4">
          <StarRating value={rating} onChange={setRating} size="sm" />
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleQuickFeedback(true)}
              className="p-1.5 rounded-lg bg-green-600/20 text-green-500 hover:bg-green-600/30 transition-colors"
            >
              <ThumbsUp className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleQuickFeedback(false)}
              className="p-1.5 rounded-lg bg-red-600/20 text-red-500 hover:bg-red-600/30 transition-colors"
            >
              <ThumbsDown className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsOpen(true)}
              className="p-1.5 rounded-lg bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 transition-colors"
            >
              <MessageSquare className="w-4 h-4" />
            </button>
          </div>
        </div>

        {userFeedback && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <p className="text-xs text-muted-foreground">
              You rated this {userFeedback.overall_rating} stars
              {userFeedback.created_at && ` on ${new Date(userFeedback.created_at).toLocaleDateString()}`}
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <>
      {/* Floating Feedback Button */}
      {!inline && (
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          whileHover={{ scale: 1.1 }}
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full shadow-lg flex items-center justify-center text-foreground z-40"
        >
          <MessageSquare className="w-6 h-6" />
        </motion.button>
      )}

      {/* Feedback Modal */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setIsOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-background rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              {/* Header */}
              <div className="sticky top-0 bg-background border-b border-gray-800 p-6 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-foreground">Share Your Feedback</h2>
                  <p className="text-sm text-muted-foreground mt-1">Help us improve {contentTitle}</p>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-card rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-muted-foreground" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6">
                {/* Overall Rating */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-3">
                    Overall Rating
                  </label>
                  <div className="flex items-center gap-4">
                    <StarRating value={rating} onChange={setRating} size="lg" />
                    <span className="text-muted-foreground">
                      {rating === 0 ? 'Select rating' : 
                       rating === 1 ? 'Poor' :
                       rating === 2 ? 'Fair' :
                       rating === 3 ? 'Good' :
                       rating === 4 ? 'Very Good' : 'Excellent'}
                    </span>
                  </div>
                </div>

                {/* Quick Questions */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Quick Questions
                  </label>
                  
                  <div className="flex items-center justify-between p-3 bg-card/50 rounded-lg">
                    <span className="text-sm text-muted-foreground">Would you recommend this?</span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, would_recommend: true })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.would_recommend === true
                            ? 'bg-green-600 text-foreground'
                            : 'bg-gray-700 text-muted-foreground hover:bg-gray-600'
                        }`}
                      >
                        Yes
                      </button>
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, would_recommend: false })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.would_recommend === false
                            ? 'bg-red-600 text-foreground'
                            : 'bg-gray-700 text-muted-foreground hover:bg-gray-600'
                        }`}
                      >
                        No
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-card/50 rounded-lg">
                    <span className="text-sm text-muted-foreground">Did it meet expectations?</span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, met_expectations: true })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.met_expectations === true
                            ? 'bg-green-600 text-foreground'
                            : 'bg-gray-700 text-muted-foreground hover:bg-gray-600'
                        }`}
                      >
                        Yes
                      </button>
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, met_expectations: false })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.met_expectations === false
                            ? 'bg-red-600 text-foreground'
                            : 'bg-gray-700 text-muted-foreground hover:bg-gray-600'
                        }`}
                      >
                        No
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-card/50 rounded-lg">
                    <span className="text-sm text-muted-foreground">Did it save you time?</span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, saved_time: true })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.saved_time === true
                            ? 'bg-green-600 text-foreground'
                            : 'bg-gray-700 text-muted-foreground hover:bg-gray-600'
                        }`}
                      >
                        Yes
                      </button>
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, saved_time: false })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.saved_time === false
                            ? 'bg-red-600 text-foreground'
                            : 'bg-gray-700 text-muted-foreground hover:bg-gray-600'
                        }`}
                      >
                        No
                      </button>
                    </div>
                  </div>
                </div>

                {/* Detailed Ratings */}
                <div>
                  <button
                    onClick={() => setShowDetails(!showDetails)}
                    className="flex items-center gap-2 text-sm text-purple-400 hover:text-purple-300 transition-colors"
                  >
                    <ChevronDown className={`w-4 h-4 transition-transform ${showDetails ? 'rotate-180' : ''}`} />
                    Detailed Ratings (Optional)
                  </button>
                  
                  {showDetails && (
                    <div className="mt-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Quality</span>
                        <StarRating 
                          value={detailedRatings.quality} 
                          onChange={(v: number) => setDetailedRatings({ ...detailedRatings, quality: v })}
                          size="sm"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Accuracy</span>
                        <StarRating 
                          value={detailedRatings.accuracy} 
                          onChange={(v: number) => setDetailedRatings({ ...detailedRatings, accuracy: v })}
                          size="sm"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Usefulness</span>
                        <StarRating 
                          value={detailedRatings.usefulness} 
                          onChange={(v: number) => setDetailedRatings({ ...detailedRatings, usefulness: v })}
                          size="sm"
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Comments */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Comments (Optional)
                  </label>
                  <textarea
                    value={comments}
                    onChange={(e) => setComments(e.target.value)}
                    placeholder="What did you like or dislike?"
                    rows={3}
                    className="w-full px-4 py-2 bg-card/50 border border-gray-700 rounded-lg text-foreground placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                  />
                </div>

                {/* Suggestions */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Suggestions for Improvement (Optional)
                  </label>
                  <textarea
                    value={suggestions}
                    onChange={(e) => setSuggestions(e.target.value)}
                    placeholder="How can we make this better?"
                    rows={3}
                    className="w-full px-4 py-2 bg-card/50 border border-gray-700 rounded-lg text-foreground placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                  />
                </div>

                {/* Statistics */}
                {showStats && stats && (
                  <div className="bg-card/30 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-foreground mb-3">Community Feedback</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Average Rating</span>
                        <div className="flex items-center gap-2 mt-1">
                          <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                          <span className="text-foreground font-medium">
                            {stats.average_rating?.toFixed(1) || 'N/A'}
                          </span>
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Total Reviews</span>
                        <p className="text-foreground font-medium mt-1">{stats.total_feedback}</p>
                      </div>
                    </div>
                    
                    {stats.rating_distribution && (
                      <div className="mt-4 space-y-2">
                        {[5, 4, 3, 2, 1].map((star) => (
                          <div key={star} className="flex items-center gap-2">
                            <span className="text-xs text-muted-foreground w-3">{star}</span>
                            <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
                            <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-yellow-500 to-orange-500"
                                style={{
                                  width: `${(stats.rating_distribution[star] / stats.total_feedback) * 100}%`,
                                }}
                              />
                            </div>
                            <span className="text-xs text-muted-foreground w-8 text-right">
                              {stats.rating_distribution[star]}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="sticky bottom-0 bg-background border-t border-gray-800 p-6">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">
                    {userFeedback && (
                      <span className="flex items-center gap-1">
                        <AlertCircle className="w-4 h-4" />
                        You already rated this content
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => setIsOpen(false)}
                      className="px-4 py-2 text-muted-foreground hover:text-foreground transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSubmit}
                      disabled={loading || rating === 0}
                      className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-foreground rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {loading ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          Submit Feedback
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};