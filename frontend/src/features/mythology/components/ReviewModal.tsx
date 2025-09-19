/**
 * Review Modal Component
 * Detailed view for reviewing flagged content with action buttons
 */
import React, { useState } from 'react';
import { 
  X, 
  Flag, 
  User, 
  Calendar, 
  FileText, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Edit3,
  MessageSquare
} from 'lucide-react';
import { format } from 'date-fns';
import { toast } from 'sonner';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../../../components/ui/dialog';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Textarea } from '../../../components/ui/textarea';
import { Label } from '../../../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';

import { 
  useFlaggedContentDetail, 
  useSubmitReview, 
  type FlaggedContent,
  type ReviewAction 
} from '../api/mythology';

interface ReviewModalProps {
  contentId: number;
  onClose: () => void;
}

export const ReviewModal: React.FC<ReviewModalProps> = ({ contentId, onClose }) => {
  const [reviewNotes, setReviewNotes] = useState('');
  const [editedContent, setEditedContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  // API hooks
  const { data: content, isLoading, error } = useFlaggedContentDetail(contentId);
  const submitReviewMutation = useSubmitReview();

  // Initialize edited content when data loads
  React.useEffect(() => {
    if (content && !editedContent) {
      setEditedContent(content.content_preview);
    }
  }, [content, editedContent]);

  // Handle review action
  const handleReviewAction = async (action: ReviewAction['action']) => {
    try {
      const reviewData: ReviewAction = {
        content_id: contentId,
        action,
        notes: reviewNotes || undefined,
      };

      // Add edited content if action is 'edit'
      if (action === 'edit' && editedContent !== content?.content_preview) {
        reviewData.edit_content = editedContent;
      }

      await submitReviewMutation.mutateAsync(reviewData);
      
      toast.success('Review submitted successfully', {
        description: `Content has been ${action === 'approve' ? 'approved' : action === 'remove' ? 'removed' : action === 'edit' ? 'edited' : 'marked as false positive'}.`,
      });
      
      onClose();
    } catch (error) {
      toast.error('Failed to submit review', {
        description: 'Please try again or contact support if the issue persists.',
      });
    }
  };

  // Priority and status configurations
  const priorityConfig = {
    critical: { color: 'bg-red-500 text-foreground', label: 'Critical' },
    high: { color: 'bg-orange-500 text-foreground', label: 'High' },
    medium: { color: 'bg-yellow-500 text-black', label: 'Medium' },
    low: { color: 'bg-green-500 text-foreground', label: 'Low' },
  };

  const flagTypeLabels = {
    misinformation: 'Misinformation',
    harmful: 'Harmful Content',
    inappropriate: 'Inappropriate',
    spam: 'Spam',
    other: 'Other',
  };

  if (error) {
    return (
      <Dialog open onOpenChange={onClose}>
        <DialogContent className="max-w-2xl">
          <Alert className="border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              Failed to load content details. Please try again.
            </AlertDescription>
          </Alert>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Flag className="h-5 w-5" />
            <span>Review Flagged Content #{contentId}</span>
          </DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="space-y-4">
            {/* Loading skeleton */}
            <div className="h-8 w-full bg-muted/20 animate-pulse rounded" />
            <div className="h-32 w-full bg-muted/20 animate-pulse rounded" />
            <div className="h-24 w-full bg-muted/20 animate-pulse rounded" />
          </div>
        ) : content ? (
          <div className="space-y-6">
            {/* Content Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center space-x-2">
                    <FileText className="h-5 w-5" />
                    <span>Content Details</span>
                  </span>
                  <div className="flex items-center space-x-2">
                    <Badge className={priorityConfig[content.priority as keyof typeof priorityConfig]?.color}>
                      {priorityConfig[content.priority as keyof typeof priorityConfig]?.label || content.priority}
                    </Badge>
                    <Badge variant="outline">
                      {flagTypeLabels[content.flag_type as keyof typeof flagTypeLabels] || content.flag_type}
                    </Badge>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Content Type</Label>
                    <p className="text-sm">{content.content_type}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Content ID</Label>
                    <p className="text-sm">{content.content_id}</p>
                  </div>
                </div>

                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Content Preview</Label>
                  {isEditing ? (
                    <Textarea
                      value={editedContent}
                      onChange={(e) => setEditedContent(e.target.value)}
                      className="mt-1 min-h-[100px]"
                      placeholder="Edit content..."
                    />
                  ) : (
                    <div className="mt-1 p-3 bg-muted rounded-md">
                      <p className="text-sm whitespace-pre-wrap">{content.content_preview}</p>
                    </div>
                  )}
                </div>

                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Flag Reason</Label>
                  <div className="mt-1 p-3 bg-orange-50 border border-orange-200 rounded-md">
                    <p className="text-sm text-orange-800">{content.reason}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Flag Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <User className="h-5 w-5" />
                    <span>Flagged By</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {content.flagged_by ? (
                    <>
                      <div>
                        <Label className="text-sm font-medium text-muted-foreground">User</Label>
                        <p className="text-sm">{content.flagged_by.username || 'Unknown User'}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium text-muted-foreground">Email</Label>
                        <p className="text-sm">{content.flagged_by.email || 'No email provided'}</p>
                      </div>
                    </>
                  ) : (
                    <div>
                      <Label className="text-sm font-medium text-muted-foreground">User</Label>
                      <p className="text-sm">System Generated</p>
                    </div>
                  )}
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Date</Label>
                    <p className="text-sm">{content.flagged_at ? format(new Date(content.flagged_at), 'PPpp') : 'Unknown'}</p>
                  </div>
                </CardContent>
              </Card>

              {content.reviewed_by && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <CheckCircle className="h-5 w-5" />
                      <span>Previous Review</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div>
                      <Label className="text-sm font-medium text-muted-foreground">Reviewed By</Label>
                      <p className="text-sm">{content.reviewed_by?.username || 'Unknown Reviewer'}</p>
                    </div>
                    {content.reviewed_at && (
                      <div>
                        <Label className="text-sm font-medium text-muted-foreground">Review Date</Label>
                        <p className="text-sm">{format(new Date(content.reviewed_at), 'PPpp')}</p>
                      </div>
                    )}
                    {content.review_notes && (
                      <div>
                        <Label className="text-sm font-medium text-muted-foreground">Review Notes</Label>
                        <p className="text-sm">{content.review_notes}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Metadata */}
            {content.metadata && Object.keys(content.metadata).length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Additional Information</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(content.metadata).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <Label className="text-sm font-medium text-muted-foreground">{key}</Label>
                        <span className="text-sm">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Review Actions */}
            {content.status === 'pending' && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <MessageSquare className="h-5 w-5" />
                    <span>Review Actions</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="review-notes">Review Notes</Label>
                    <Textarea
                      id="review-notes"
                      value={reviewNotes}
                      onChange={(e) => setReviewNotes(e.target.value)}
                      placeholder="Add your review notes here..."
                      className="mt-1"
                    />
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsEditing(!isEditing)}
                    >
                      <Edit3 className="h-4 w-4 mr-2" />
                      {isEditing ? 'Cancel Edit' : 'Edit Content'}
                    </Button>
                    {isEditing && editedContent !== content.content_preview && (
                      <Badge variant="secondary">Content Modified</Badge>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2 pt-4 border-t">
                    <Button
                      onClick={() => handleReviewAction('approve')}
                      disabled={submitReviewMutation.isPending}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Approve
                    </Button>
                    
                    <Button
                      onClick={() => handleReviewAction('remove')}
                      disabled={submitReviewMutation.isPending}
                      variant="destructive"
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Remove
                    </Button>
                    
                    {isEditing && editedContent !== content.content_preview && (
                      <Button
                        onClick={() => handleReviewAction('edit')}
                        disabled={submitReviewMutation.isPending}
                        variant="outline"
                      >
                        <Edit3 className="h-4 w-4 mr-2" />
                        Save Edit
                      </Button>
                    )}
                    
                    <Button
                      onClick={() => handleReviewAction('flag_false_positive')}
                      disabled={submitReviewMutation.isPending}
                      variant="outline"
                    >
                      <Flag className="h-4 w-4 mr-2" />
                      False Positive
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
};