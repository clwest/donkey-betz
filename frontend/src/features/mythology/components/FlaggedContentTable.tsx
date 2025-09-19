/**
 * Flagged Content Table Component
 * Sortable and filterable table for displaying flagged content with priority indicators
 */
import React, { useState, useMemo } from 'react';
import { 
  ChevronDown, 
  ChevronUp, 
  Eye, 
  Filter, 
  Search, 
  AlertTriangle,
  Clock,
  CheckCircle,
  XCircle,
  MoreHorizontal
} from 'lucide-react';
import { format } from 'date-fns';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../../../components/ui/table';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../../components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../../../components/ui/dropdown-menu';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Alert, AlertDescription } from '../../../components/ui/alert';

import { useFlaggedContent, type FlaggedContent } from '../api/mythology';
import { cn } from '../../../lib/utils';

interface FlaggedContentTableProps {
  filters?: {
    status?: string;
    priority?: string;
    flag_type?: string;
    limit?: number;
  };
  onReviewClick?: (contentId: string) => void;
  compact?: boolean;
  showReviewDetails?: boolean;
}

type SortField = 'flagged_at' | 'priority' | 'status' | 'flag_type';
type SortOrder = 'asc' | 'desc';

export const FlaggedContentTable: React.FC<FlaggedContentTableProps> = ({
  filters = {},
  onReviewClick,
  compact = false,
  showReviewDetails = false,
}) => {
  // Local state - initialize with filters from props
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>(filters.status || 'all');
  const [priorityFilter, setPriorityFilter] = useState<string>(filters.priority || 'all');
  const [flagTypeFilter, setFlagTypeFilter] = useState<string>(filters.flag_type || 'all');
  const [sortField, setSortField] = useState<SortField>('flagged_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = compact ? 5 : 10;
  
  // Update filters when props change
  React.useEffect(() => {
    if (filters.status) setStatusFilter(filters.status);
    if (filters.priority) setPriorityFilter(filters.priority);
    if (filters.flag_type) setFlagTypeFilter(filters.flag_type);
  }, [filters.status, filters.priority, filters.flag_type]);

  // Build query parameters
  const queryParams = useMemo(() => {
    const params: any = {
      page: currentPage,
      limit: pageSize,
      sort_by: sortField,
      sort_order: sortOrder,
    };

    if (statusFilter !== 'all') params.status = statusFilter;
    if (priorityFilter !== 'all') params.priority = priorityFilter;
    if (flagTypeFilter !== 'all') params.flag_type = flagTypeFilter;
    if (filters.limit) params.limit = filters.limit;

    return params;
  }, [currentPage, pageSize, sortField, sortOrder, statusFilter, priorityFilter, flagTypeFilter, filters.limit]);

  // API query
  const { data, isLoading, error } = useFlaggedContent(queryParams);

  // Filter data based on search term (client-side)
  const filteredData = useMemo(() => {
    if (!data?.results) return [];
    
    if (!searchTerm) return data.results;
    
    return data.results.filter(item => 
      item.content_preview.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.reason.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.flagged_by?.username || '').toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [data?.results, searchTerm]);

  // Handle sorting
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
    setCurrentPage(1);
  };

  // Priority configurations
  const priorityConfig = {
    critical: { 
      color: 'bg-red-500 text-foreground',
      icon: AlertTriangle,
      label: 'Critical'
    },
    high: { 
      color: 'bg-orange-500 text-foreground',
      icon: AlertTriangle,
      label: 'High'
    },
    medium: { 
      color: 'bg-yellow-500 text-black',
      icon: Clock,
      label: 'Medium'
    },
    low: { 
      color: 'bg-green-500 text-foreground',
      icon: CheckCircle,
      label: 'Low'
    },
  };

  // Status configurations
  const statusConfig = {
    pending: { 
      color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      icon: Clock,
      label: 'Pending'
    },
    reviewing: { 
      color: 'bg-blue-100 text-blue-800 border-blue-200',
      icon: Eye,
      label: 'Reviewing'
    },
    resolved: { 
      color: 'bg-green-100 text-green-800 border-green-200',
      icon: CheckCircle,
      label: 'Resolved'
    },
    dismissed: { 
      color: 'bg-muted/10 text-gray-800 border-border',
      icon: XCircle,
      label: 'Dismissed'
    },
  };

  // Flag type labels
  const flagTypeLabels = {
    misinformation: 'Misinformation',
    harmful: 'Harmful Content',
    inappropriate: 'Inappropriate',
    spam: 'Spam',
    other: 'Other',
  };

  // Render sort icon
  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return sortOrder === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />;
  };

  // Render priority badge
  const PriorityBadge = ({ priority }: { priority: string }) => {
    const config = priorityConfig[priority as keyof typeof priorityConfig];
    if (!config) return <Badge variant="outline">{priority}</Badge>;
    
    const Icon = config.icon;
    return (
      <Badge className={cn('flex items-center space-x-1', config.color)}>
        <Icon className="h-3 w-3" />
        <span>{config.label}</span>
      </Badge>
    );
  };

  // Render status badge
  const StatusBadge = ({ status }: { status: string }) => {
    const config = statusConfig[status as keyof typeof statusConfig];
    if (!config) return <Badge variant="outline">{status}</Badge>;
    
    const Icon = config.icon;
    return (
      <Badge variant="outline" className={config.color}>
        <Icon className="h-3 w-3 mr-1" />
        {config.label}
      </Badge>
    );
  };

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <AlertDescription className="text-red-800">
          Failed to load flagged content. Please try again.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters and Search */}
      {!compact && (
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search content, reason, or user..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Select status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="reviewing">Reviewing</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
              <SelectItem value="dismissed">Dismissed</SelectItem>
            </SelectContent>
          </Select>

          <Select value={priorityFilter} onValueChange={setPriorityFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Select priority" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priority</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>

          <Select value={flagTypeFilter} onValueChange={setFlagTypeFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="misinformation">Misinformation</SelectItem>
              <SelectItem value="harmful">Harmful Content</SelectItem>
              <SelectItem value="inappropriate">Inappropriate</SelectItem>
              <SelectItem value="spam">Spam</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Table */}
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('priority')}
                  className="h-8 px-2"
                >
                  Priority
                  <SortIcon field="priority" />
                </Button>
              </TableHead>
              <TableHead>Content Preview</TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('flag_type')}
                  className="h-8 px-2"
                >
                  Type
                  <SortIcon field="flag_type" />
                </Button>
              </TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('status')}
                  className="h-8 px-2"
                >
                  Status
                  <SortIcon field="status" />
                </Button>
              </TableHead>
              <TableHead>Flagged By</TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('flagged_at')}
                  className="h-8 px-2"
                >
                  Date
                  <SortIcon field="flagged_at" />
                </Button>
              </TableHead>
              {showReviewDetails && <TableHead>Reviewed By</TableHead>}
              <TableHead className="w-12">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              // Loading skeleton
              Array.from({ length: pageSize }).map((_, index) => (
                <TableRow key={index}>
                  <TableCell><div className="h-6 w-16 bg-muted/20 animate-pulse rounded" /></TableCell>
                  <TableCell><div className="h-4 w-full bg-muted/20 animate-pulse rounded" /></TableCell>
                  <TableCell><div className="h-6 w-20 bg-muted/20 animate-pulse rounded" /></TableCell>
                  <TableCell><div className="h-6 w-20 bg-muted/20 animate-pulse rounded" /></TableCell>
                  <TableCell><div className="h-4 w-24 bg-muted/20 animate-pulse rounded" /></TableCell>
                  <TableCell><div className="h-4 w-20 bg-muted/20 animate-pulse rounded" /></TableCell>
                  {showReviewDetails && <TableCell><div className="h-4 w-24 bg-muted/20 animate-pulse rounded" /></TableCell>}
                  <TableCell><div className="h-8 w-8 bg-muted/20 animate-pulse rounded" /></TableCell>
                </TableRow>
              ))
            ) : filteredData.length === 0 ? (
              <TableRow>
                <TableCell 
                  colSpan={showReviewDetails ? 8 : 7} 
                  className="text-center py-8 text-muted-foreground"
                >
                  No flagged content found matching your criteria.
                </TableCell>
              </TableRow>
            ) : (
              filteredData.map((item) => (
                <TableRow 
                  key={item.id} 
                  className="hover:bg-muted/50 cursor-pointer" 
                  onClick={() => {
                    console.log('Row clicked for item:', item.id);
                    onReviewClick?.(item.id);
                  }}
                >
                  <TableCell>
                    <PriorityBadge priority={item.priority} />
                  </TableCell>
                  <TableCell className="max-w-xs">
                    <div className="truncate" title={item.content_preview}>
                      {item.content_preview}
                    </div>
                    <div className="text-sm text-muted-foreground truncate" title={item.reason}>
                      {item.reason}
                    </div>
                    {/* Add a subtle indicator that this is clickable */}
                    <div className="text-xs text-blue-500 opacity-70 mt-1">
                      Click to review →
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {flagTypeLabels[item.flag_type as keyof typeof flagTypeLabels] || item.flag_type}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={item.status} />
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      {item.flagged_by?.username || 'Unknown User'}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {item.flagged_by?.email || 'No email provided'}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      {format(new Date(item.flagged_at), 'MMM d, yyyy')}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {format(new Date(item.flagged_at), 'HH:mm')}
                    </div>
                  </TableCell>
                  {showReviewDetails && (
                    <TableCell>
                      {item.reviewed_by ? (
                        <div>
                          <div className="text-sm">{item.reviewed_by?.username || 'Unknown Reviewer'}</div>
                          {item.reviewed_at && (
                            <div className="text-xs text-muted-foreground">
                              {format(new Date(item.reviewed_at), 'MMM d, yyyy')}
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                  )}
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-8 w-8 p-0"
                          onClick={(e) => {
                            e.stopPropagation();
                            console.log('Dropdown button clicked for item:', item.id);
                          }}
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem 
                          onClick={(e) => {
                            e.stopPropagation();
                            console.log('Review menu item clicked for item:', item.id);
                            onReviewClick?.(item.id);
                          }}
                          className="flex items-center space-x-2"
                        >
                          <Eye className="h-4 w-4" />
                          <span>Review</span>
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {!compact && data && data.count > pageSize && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, data.count)} of {data.count} items
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={!data.previous}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => prev + 1)}
              disabled={!data.next}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};