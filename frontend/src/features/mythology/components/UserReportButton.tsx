/**
 * User Report Button Component
 * Allows users to report suspicious content for mythology review
 */
import React, { useState } from 'react';
import { Flag, AlertTriangle, MessageSquare } from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Label } from '../../../components/ui/label';
import { Textarea } from '../../../components/ui/textarea';
import { Input } from '../../../components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../../../components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../../components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';

import { useReportContent, type ReportContent } from '../api/mythology';

interface UserReportButtonProps {
  contentType?: string;
  contentId?: number;
  variant?: 'button' | 'icon' | 'text';
  size?: 'sm' | 'default' | 'lg';
  className?: string;
}

export const UserReportButton: React.FC<UserReportButtonProps> = ({
  contentType,
  contentId,
  variant = 'button',
  size = 'default',
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState<Partial<ReportContent>>({
    content_type: contentType || '',
    content_id: contentId || 0,
    flag_type: '',
    reason: '',
    additional_info: '',
  });

  const reportMutation = useReportContent();

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.content_type || !formData.content_id || !formData.flag_type || !formData.reason) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const result = await reportMutation.mutateAsync(formData as ReportContent);
      
      toast.success('Content reported successfully', {
        description: `Thank you for helping keep our platform safe. Report ID: ${result.flag_id}`,
      });
      
      setIsOpen(false);
      setFormData({
        content_type: contentType || '',
        content_id: contentId || 0,
        flag_type: '',
        reason: '',
        additional_info: '',
      });
    } catch (error) {
      toast.error('Failed to submit report', {
        description: 'Please try again or contact support if the issue persists.',
      });
    }
  };

  // Flag type options
  const flagTypes = [
    { value: 'misinformation', label: 'Misinformation', description: 'False or misleading information' },
    { value: 'harmful', label: 'Harmful Content', description: 'Content that could cause harm' },
    { value: 'inappropriate', label: 'Inappropriate', description: 'Violates community guidelines' },
    { value: 'spam', label: 'Spam', description: 'Unwanted or repetitive content' },
    { value: 'other', label: 'Other', description: 'Other concerns not listed above' },
  ];

  // Content type options
  const contentTypes = [
    'post', 'comment', 'article', 'video', 'image', 'user_profile', 'other'
  ];

  // Render trigger button based on variant
  const TriggerButton = () => {
    switch (variant) {
      case 'icon':
        return (
          <Button variant="ghost" size="sm" className={className}>
            <Flag className="h-4 w-4" />
          </Button>
        );
      case 'text':
        return (
          <button className={`text-sm text-muted-foreground hover:text-foreground ${className}`}>
            Report
          </button>
        );
      default:
        return (
          <Button variant="outline" size={size} className={className}>
            <Flag className="h-4 w-4 mr-2" />
            Report Content
          </Button>
        );
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <TriggerButton />
      </DialogTrigger>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Flag className="h-5 w-5 text-orange-600" />
            <span>Report Content</span>
          </DialogTitle>
          <DialogDescription>
            Help us maintain a safe and accurate platform by reporting content that violates our guidelines.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Content Information */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Content Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="content-type">Content Type *</Label>
                  <Select 
                    value={formData.content_type} 
                    onValueChange={(value) => setFormData(prev => ({ ...prev, content_type: value }))}
                  >
                    <SelectTrigger id="content-type">
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      {contentTypes.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="content-id">Content ID *</Label>
                  <Input
                    id="content-id"
                    type="number"
                    value={formData.content_id || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, content_id: parseInt(e.target.value) || 0 }))}
                    placeholder="Enter content ID"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Flag Type */}
          <div>
            <Label htmlFor="flag-type">What's the issue? *</Label>
            <Select 
              value={formData.flag_type} 
              onValueChange={(value) => setFormData(prev => ({ ...prev, flag_type: value }))}
            >
              <SelectTrigger id="flag-type">
                <SelectValue placeholder="Select the type of issue" />
              </SelectTrigger>
              <SelectContent>
                {flagTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    <div className="flex flex-col">
                      <span className="font-medium">{type.label}</span>
                      <span className="text-xs text-muted-foreground">{type.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Reason */}
          <div>
            <Label htmlFor="reason">Detailed Reason *</Label>
            <Textarea
              id="reason"
              value={formData.reason}
              onChange={(e) => setFormData(prev => ({ ...prev, reason: e.target.value }))}
              placeholder="Please describe why you're reporting this content..."
              className="min-h-[80px]"
            />
          </div>

          {/* Additional Information */}
          <div>
            <Label htmlFor="additional-info">Additional Information (Optional)</Label>
            <Textarea
              id="additional-info"
              value={formData.additional_info}
              onChange={(e) => setFormData(prev => ({ ...prev, additional_info: e.target.value }))}
              placeholder="Any additional context or information that might be helpful..."
              className="min-h-[60px]"
            />
          </div>

          {/* Guidelines Note */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-start space-x-2">
              <MessageSquare className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">Report Guidelines</p>
                <ul className="text-xs space-y-1">
                  <li>• Be specific about the issue you're reporting</li>
                  <li>• Provide clear evidence when possible</li>
                  <li>• False reports may result in account restrictions</li>
                  <li>• Reports are reviewed by our moderation team</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-between pt-4 border-t">
            <Button type="button" variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={reportMutation.isPending || !formData.content_type || !formData.content_id || !formData.flag_type || !formData.reason}
              className="bg-orange-600 hover:bg-orange-700"
            >
              {reportMutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                  Submitting...
                </>
              ) : (
                <>
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Submit Report
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// Export standalone hook for programmatic reporting
export const useReportContentModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [contentInfo, setContentInfo] = useState<{ type?: string; id?: number }>({});

  const openReportModal = (contentType: string, contentId: number) => {
    setContentInfo({ type: contentType, id: contentId });
    setIsOpen(true);
  };

  const ReportModal = () => (
    <UserReportButton
      contentType={contentInfo.type}
      contentId={contentInfo.id}
    />
  );

  return {
    openReportModal,
    isOpen,
    setIsOpen,
    ReportModal,
  };
};