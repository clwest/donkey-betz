import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Search, Zap, Clock, RefreshCw, CheckCircle, AlertCircle,
  Bot, Briefcase, DollarSign, MapPin, Tag, ExternalLink,
  Play, Pause, Settings, TrendingUp, Users, Target
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary: string;
  description: string;
  source: string;
  url: string;
  tags: string[];
  posted_date: string;
  agent_match?: {
    agent: { name: string };
    confidence: number;
    match_score: number;
  };
  match_score: number;
  selected?: boolean;
}

interface ScanCriteria {
  keywords: string[];
  locations: string[];
  job_types: string[];
  min_budget: number;
  max_budget?: number;
  experience_level: string[];
}

export function JobDiscoveryPanel() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobs, setSelectedJobs] = useState<Set<string>>(new Set());
  const [isScanning, setIsScanning] = useState(false);
  const [autoScanEnabled, setAutoScanEnabled] = useState(false);
  const [scanInterval, setScanInterval] = useState(300); // 5 minutes default
  const [lastScanTime, setLastScanTime] = useState<string | null>(null);
  const [scanStatus, setScanStatus] = useState<string>('Ready to scan');
  const [applicationStatus, setApplicationStatus] = useState<Map<string, string>>(new Map());

  // Scan criteria state
  const [keywords, setKeywords] = useState('python, AI, machine learning, remote');
  const [locations, setLocations] = useState('remote, worldwide');
  const [minBudget, setMinBudget] = useState(1000);
  const [selectedJobTypes, setSelectedJobTypes] = useState(['full-time', 'contract', 'freelance']);

  // WebSocket connection for job scanner
  const { isConnected, sendMessage } = useWebSocket({
    url: '/ws/job-scanner/',
    onMessage: (data: any) => {
      handleWebSocketMessage(data);
    }
  });

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'scan_results':
        setJobs(data.jobs || []);
        setLastScanTime(data.scan_time);
        setIsScanning(false);
        setScanStatus(`Found ${data.jobs?.length || 0} opportunities`);
        break;

      case 'scan_status':
        setScanStatus(data.message);
        if (data.status === 'scanning') {
          setIsScanning(true);
        } else if (data.status === 'complete' || data.status === 'error') {
          setIsScanning(false);
        }
        break;

      case 'auto_scan_enabled':
        setAutoScanEnabled(true);
        setScanInterval(data.interval);
        break;

      case 'auto_scan_disabled':
        setAutoScanEnabled(false);
        break;

      case 'application_progress':
        setScanStatus(`Applying to jobs: ${data.completed}/${data.total}`);
        break;

      case 'application_complete':
        setScanStatus(`Applied to ${data.success_count} jobs successfully`);
        // Update application status for each job
        const newStatus = new Map(applicationStatus);
        data.results.forEach((result: any) => {
          newStatus.set(result.job_id, result.status);
        });
        setApplicationStatus(newStatus);
        break;
    }
  };

  const scanForJobs = () => {
    const criteria: ScanCriteria = {
      keywords: keywords.split(',').map(k => k.trim()),
      locations: locations.split(',').map(l => l.trim()),
      job_types: selectedJobTypes,
      min_budget: minBudget,
      experience_level: ['mid', 'senior']
    };

    sendMessage({
      type: 'scan_jobs',
      criteria
    });
  };

  const toggleAutoScan = () => {
    if (autoScanEnabled) {
      sendMessage({ type: 'disable_auto_scan' });
    } else {
      sendMessage({
        type: 'enable_auto_scan',
        interval: scanInterval
      });
    }
  };

  const toggleJobSelection = (jobId: string) => {
    const newSelection = new Set(selectedJobs);
    if (newSelection.has(jobId)) {
      newSelection.delete(jobId);
    } else {
      newSelection.add(jobId);
    }
    setSelectedJobs(newSelection);
  };

  const selectAllJobs = () => {
    if (selectedJobs.size === jobs.length) {
      setSelectedJobs(new Set());
    } else {
      setSelectedJobs(new Set(jobs.map(job => job.id)));
    }
  };

  const applyToSelectedJobs = () => {
    const jobIds = Array.from(selectedJobs);

    // First notify the scanner about selection
    sendMessage({
      type: 'select_jobs',
      job_ids: jobIds
    });

    // Then apply to the jobs
    sendMessage({
      type: 'apply_to_jobs',
      job_ids: jobIds
    });
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-500';
    if (score >= 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getApplicationStatusBadge = (jobId: string) => {
    const status = applicationStatus.get(jobId);
    if (!status) return null;

    switch (status) {
      case 'submitted':
        return <Badge className="bg-green-500">Applied</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <Card className="bg-card">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Job Discovery Scanner
            </CardTitle>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="px-3 py-1">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} mr-2 animate-pulse`} />
                {isConnected ? 'Connected' : 'Offline'}
              </Badge>
              {lastScanTime && (
                <span className="text-sm text-muted-foreground">
                  Last scan: {new Date(lastScanTime).toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Scan Criteria */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="keywords">Keywords</Label>
              <Input
                id="keywords"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="python, AI, remote..."
                disabled={isScanning}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="locations">Locations</Label>
              <Input
                id="locations"
                value={locations}
                onChange={(e) => setLocations(e.target.value)}
                placeholder="remote, USA, worldwide..."
                disabled={isScanning}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="budget">Min Budget ($)</Label>
              <Input
                id="budget"
                type="number"
                value={minBudget}
                onChange={(e) => setMinBudget(parseInt(e.target.value))}
                placeholder="1000"
                disabled={isScanning}
              />
            </div>
          </div>

          {/* Job Types */}
          <div className="space-y-2">
            <Label>Job Types</Label>
            <div className="flex flex-wrap gap-2">
              {['full-time', 'contract', 'freelance', 'part-time'].map((type) => (
                <label key={type} className="flex items-center gap-2 cursor-pointer">
                  <Checkbox
                    checked={selectedJobTypes.includes(type)}
                    onCheckedChange={(checked) => {
                      if (checked) {
                        setSelectedJobTypes([...selectedJobTypes, type]);
                      } else {
                        setSelectedJobTypes(selectedJobTypes.filter(t => t !== type));
                      }
                    }}
                    disabled={isScanning}
                  />
                  <span className="text-sm capitalize">{type}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Scan Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                onClick={scanForJobs}
                disabled={!isConnected || isScanning}
                className="min-w-[120px]"
              >
                {isScanning ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Scanning...
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-2" />
                    Scan Now
                  </>
                )}
              </Button>

              <div className="flex items-center gap-2">
                <Switch
                  id="auto-scan"
                  checked={autoScanEnabled}
                  onCheckedChange={toggleAutoScan}
                  disabled={!isConnected}
                />
                <Label htmlFor="auto-scan" className="cursor-pointer">
                  Auto-scan every
                </Label>
                <Select
                  value={scanInterval.toString()}
                  onValueChange={(value) => setScanInterval(parseInt(value))}
                  disabled={!isConnected || autoScanEnabled}
                >
                  <SelectTrigger className="w-[120px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="60">1 minute</SelectItem>
                    <SelectItem value="300">5 minutes</SelectItem>
                    <SelectItem value="900">15 minutes</SelectItem>
                    <SelectItem value="1800">30 minutes</SelectItem>
                    <SelectItem value="3600">1 hour</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="text-sm text-muted-foreground">
              {scanStatus}
            </div>
          </div>

          {/* Auto-scan indicator */}
          {autoScanEnabled && (
            <Alert>
              <Clock className="h-4 w-4" />
              <AlertDescription>
                Auto-scan is active. Jobs will be scanned every {scanInterval / 60} minute{scanInterval !== 60 ? 's' : ''}.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Job Results */}
      {jobs.length > 0 && (
        <Card className="bg-card">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="h-5 w-5" />
                Discovered Opportunities ({jobs.length})
              </CardTitle>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={selectAllJobs}
                >
                  {selectedJobs.size === jobs.length ? 'Deselect All' : 'Select All'}
                </Button>
                {selectedJobs.size > 0 && (
                  <Button
                    size="sm"
                    onClick={applyToSelectedJobs}
                    className="min-w-[140px]"
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Apply to {selectedJobs.size} Jobs
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {jobs.map((job) => (
                <div
                  key={job.id}
                  className={`p-4 border rounded-lg transition-colors ${
                    selectedJobs.has(job.id) ? 'bg-accent/20 border-accent' : 'hover:bg-accent/10'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <Checkbox
                        checked={selectedJobs.has(job.id)}
                        onCheckedChange={() => toggleJobSelection(job.id)}
                      />
                      <div className="space-y-2 flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-semibold">{job.title}</h3>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                              <span className="flex items-center gap-1">
                                <Briefcase className="h-3 w-3" />
                                {job.company}
                              </span>
                              <span className="flex items-center gap-1">
                                <MapPin className="h-3 w-3" />
                                {job.location}
                              </span>
                              <span className="flex items-center gap-1">
                                <DollarSign className="h-3 w-3" />
                                {job.salary}
                              </span>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {getApplicationStatusBadge(job.id)}
                            <Badge variant="outline">{job.source}</Badge>
                            <a
                              href={job.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-500 hover:text-blue-600"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </div>
                        </div>

                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {job.description}
                        </p>

                        <div className="flex items-center justify-between">
                          <div className="flex flex-wrap gap-1">
                            {job.tags.slice(0, 5).map((tag) => (
                              <Badge key={tag} variant="secondary" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                            {job.tags.length > 5 && (
                              <Badge variant="secondary" className="text-xs">
                                +{job.tags.length - 5} more
                              </Badge>
                            )}
                          </div>

                          {job.agent_match && (
                            <div className="flex items-center gap-2">
                              <Bot className="h-4 w-4 text-blue-500" />
                              <span className="text-sm">
                                {job.agent_match.agent.name}
                              </span>
                              <span className={`text-sm font-bold ${getMatchScoreColor(job.agent_match.confidence)}`}>
                                {(job.agent_match.confidence * 100).toFixed(0)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {!isScanning && jobs.length === 0 && (
        <Card className="bg-card">
          <CardContent className="py-12">
            <div className="text-center space-y-4">
              <Search className="h-12 w-12 mx-auto text-muted-foreground" />
              <div>
                <h3 className="text-lg font-semibold">No jobs discovered yet</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Click "Scan Now" to discover job opportunities matching your criteria
                </p>
              </div>
              <Button onClick={scanForJobs} disabled={!isConnected}>
                <Search className="h-4 w-4 mr-2" />
                Start Scanning
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Scanning Animation */}
      {isScanning && (
        <Card className="bg-card">
          <CardContent className="py-12">
            <div className="text-center space-y-4">
              <div className="relative h-24 w-24 mx-auto">
                <RefreshCw className="h-24 w-24 text-blue-500 animate-spin" />
                <Bot className="h-12 w-12 absolute inset-0 m-auto text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Scanning for opportunities...</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Our spider network is searching across multiple job platforms
                </p>
              </div>
              <Progress value={33} className="w-[200px] mx-auto" />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}