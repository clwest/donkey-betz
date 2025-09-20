import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Progress } from './ui/progress';
import {
  Play,
  Download,
  Save,
  Eye,
  FileText,
  Code,
  DollarSign,
  Clock,
  CheckCircle,
  AlertCircle,
  Briefcase,
  User,
  Building
} from 'lucide-react';

interface Job {
  id: string;
  title: string;
  platform: string;
  client: string;
  budget: string;
  job_type: string;
  urgency: string;
  skills: string[];
  description: string;
}

interface Deliverable {
  job_id: string;
  job_title: string;
  agent: string;
  client: string;
  platform: string;
  value: string;
  lines_of_code: number;
  estimated_hours: number;
  file_name: string;
  status: string;
  created_at: string;
  description: string;
}

interface ExecutionSummary {
  total_jobs: number;
  total_value: string;
  total_lines_of_code: number;
  total_hours: number;
  success_rate: string;
  deliverables: Deliverable[];
  agents_used: string[];
  platforms: string[];
}

interface Message {
  type: string;
  message: string;
  timestamp: string;
  job?: Job;
  deliverable?: Deliverable;
  summary?: ExecutionSummary;
  progress?: number;
  agent?: string;
  step?: string;
  job_index?: number;
  total_jobs?: number;
}

const RealJobExecution: React.FC = () => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [availableJobs, setAvailableJobs] = useState<Job[]>([]);
  const [completedDeliverables, setCompletedDeliverables] = useState<Deliverable[]>([]);
  const [executionSummary, setExecutionSummary] = useState<ExecutionSummary | null>(null);
  const [currentProgress, setCurrentProgress] = useState<{ [key: number]: number }>({});
  const [isRecording, setIsRecording] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/real-job-execution/');

    ws.onopen = () => {
      console.log('Connected to Real Job Execution WebSocket');
      setSocket(ws);

      // Get available jobs on connect
      ws.send(JSON.stringify({
        type: 'get_available_jobs'
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message:', data);

      setMessages(prev => [...prev, data]);

      if (data.type === 'available_jobs') {
        setAvailableJobs(data.jobs);
      } else if (data.type === 'execution_started') {
        setIsExecuting(true);
        setCompletedDeliverables([]);
        setExecutionSummary(null);
        setCurrentProgress({});
      } else if (data.type === 'job_progress') {
        setCurrentProgress(prev => ({
          ...prev,
          [data.job_index]: data.progress
        }));
      } else if (data.type === 'job_completed') {
        setCompletedDeliverables(prev => [...prev, data.deliverable]);
      } else if (data.type === 'execution_complete') {
        setIsExecuting(false);
        setExecutionSummary(data.summary);
      }
    };

    ws.onclose = () => {
      console.log('Disconnected from Real Job Execution WebSocket');
      setSocket(null);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, []);

  const startJobExecution = () => {
    if (socket) {
      setMessages([]);
      socket.send(JSON.stringify({
        type: 'start_job_execution'
      }));
    }
  };

  const saveProjectToPortfolio = (deliverable: Deliverable) => {
    if (socket) {
      socket.send(JSON.stringify({
        type: 'save_project',
        project: deliverable
      }));
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'High': return 'bg-red-100 text-red-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'Low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'Upwork': return 'bg-green-100 text-green-800';
      case 'Freelancer.com': return 'bg-blue-100 text-blue-800';
      case 'Fiverr': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'execution_started': return <Play className="w-4 h-4 text-green-600" />;
      case 'job_started': return <Briefcase className="w-4 h-4 text-blue-600" />;
      case 'job_progress': return <Code className="w-4 h-4 text-yellow-600" />;
      case 'job_completed': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'execution_complete': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-600" />;
      default: return <FileText className="w-4 h-4 text-gray-600" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="text-2xl font-bold text-gray-900">
                  🎬 Real Job Execution Studio
                </CardTitle>
                <p className="text-gray-600 mt-1">
                  Watch AI agents complete real freelance jobs in real-time • Perfect for recording & advertising
                </p>
              </div>
              <div className="flex gap-3">
                <Button
                  onClick={() => setIsRecording(!isRecording)}
                  variant={isRecording ? "destructive" : "secondary"}
                  className={isRecording ? "animate-pulse" : ""}
                >
                  {isRecording ? "🔴 Recording" : "📹 Start Recording"}
                </Button>
                <Button
                  onClick={startJobExecution}
                  disabled={isExecuting || !socket}
                  className="bg-green-600 hover:bg-green-700"
                >
                  {isExecuting ? "🤖 Executing..." : "🚀 Execute Jobs"}
                </Button>
              </div>
            </div>
          </CardHeader>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Available Jobs */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="w-5 h-5" />
                Available Jobs ({availableJobs.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-4">
                  {availableJobs.map((job, index) => (
                    <div key={job.id} className="border rounded-lg p-4 bg-white">
                      <div className="flex justify-between items-start mb-2">
                        <Badge className={getPlatformColor(job.platform)}>
                          {job.platform}
                        </Badge>
                        <Badge className={getUrgencyColor(job.urgency)}>
                          {job.urgency}
                        </Badge>
                      </div>

                      <h4 className="font-semibold text-sm mb-2">{job.title}</h4>

                      <div className="space-y-1 text-xs text-gray-600">
                        <div className="flex items-center gap-1">
                          <Building className="w-3 h-3" />
                          {job.client}
                        </div>
                        <div className="flex items-center gap-1">
                          <DollarSign className="w-3 h-3" />
                          {job.budget}
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-1 mt-2">
                        {job.skills.slice(0, 3).map((skill, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                        {job.skills.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{job.skills.length - 3} more
                          </Badge>
                        )}
                      </div>

                      {currentProgress[index + 1] && (
                        <div className="mt-3">
                          <Progress value={currentProgress[index + 1]} className="h-2" />
                          <p className="text-xs text-gray-500 mt-1">
                            {currentProgress[index + 1]}% complete
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Real-time Execution Log */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="w-5 h-5" />
                Real-time Execution Log
                {isExecuting && (
                  <Badge className="bg-green-100 text-green-800 animate-pulse">
                    LIVE
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-3">
                  {messages.map((message, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      {getMessageIcon(message.type)}
                      <div className="flex-1">
                        <p className="text-sm font-medium">{message.message}</p>
                        {message.step && (
                          <p className="text-xs text-gray-500 mt-1">{message.step}</p>
                        )}
                        {message.progress !== undefined && (
                          <Progress value={message.progress} className="h-1 mt-2" />
                        )}
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Completed Deliverables */}
        {completedDeliverables.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                Completed Deliverables ({completedDeliverables.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {completedDeliverables.map((deliverable, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-white">
                    <div className="flex justify-between items-start mb-3">
                      <Badge className={getPlatformColor(deliverable.platform)}>
                        {deliverable.platform}
                      </Badge>
                      <Badge className="bg-green-100 text-green-800">
                        {deliverable.status}
                      </Badge>
                    </div>

                    <h4 className="font-semibold text-sm mb-2">{deliverable.job_title}</h4>

                    <div className="space-y-2 text-xs text-gray-600">
                      <div className="flex items-center gap-1">
                        <Building className="w-3 h-3" />
                        {deliverable.client}
                      </div>
                      <div className="flex items-center gap-1">
                        <User className="w-3 h-3" />
                        {deliverable.agent}
                      </div>
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-3 h-3" />
                        {deliverable.value}
                      </div>
                      <div className="flex items-center gap-1">
                        <Code className="w-3 h-3" />
                        {deliverable.lines_of_code.toLocaleString()} lines
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {deliverable.estimated_hours} hours
                      </div>
                    </div>

                    <p className="text-xs text-gray-500 mt-2 line-clamp-2">
                      {deliverable.description}
                    </p>

                    <div className="flex gap-2 mt-3">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => saveProjectToPortfolio(deliverable)}
                        className="flex-1"
                      >
                        <Save className="w-3 h-3 mr-1" />
                        Save to Portfolio
                      </Button>
                    </div>

                    <p className="text-xs text-gray-400 mt-2">
                      File: {deliverable.file_name}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Execution Summary */}
        {executionSummary && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                🎉 Execution Complete - Portfolio Ready!
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {executionSummary.total_jobs}
                  </div>
                  <div className="text-sm text-gray-600">Jobs Completed</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {executionSummary.total_value}
                  </div>
                  <div className="text-sm text-gray-600">Total Value</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {executionSummary.total_lines_of_code.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Lines of Code</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    {executionSummary.total_hours}h
                  </div>
                  <div className="text-sm text-gray-600">Dev Time</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Agents Deployed</h4>
                  <div className="space-y-1">
                    {executionSummary.agents_used.map((agent, index) => (
                      <Badge key={index} variant="secondary">{agent}</Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Platforms</h4>
                  <div className="space-y-1">
                    {executionSummary.platforms.map((platform, index) => (
                      <Badge key={index} className={getPlatformColor(platform)}>
                        {platform}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Success Rate</h4>
                  <div className="text-2xl font-bold text-green-600">
                    {executionSummary.success_rate}
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="font-semibold text-yellow-800 mb-2">
                  🎬 Recording Complete - Ready for Marketing!
                </h4>
                <p className="text-sm text-yellow-700">
                  These are real deliverables that demonstrate AI agents completing actual freelance work.
                  Perfect for client presentations, marketing videos, and portfolio showcases.
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default RealJobExecution;