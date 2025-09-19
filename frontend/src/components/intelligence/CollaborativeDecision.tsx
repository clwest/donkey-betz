import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import {
  Users, MessageSquare, Share2, Crown, Star, ThumbsUp,
  ThumbsDown, Clock, Send, Plus, UserPlus, Settings,
  CheckCircle, XCircle, AlertTriangle, TrendingUp,
  Calendar, Eye, Edit3, Trash2, Copy, ExternalLink
} from 'lucide-react';

interface Advisor {
  id: string;
  name: string;
  title: string;
  avatar?: string;
  expertise: string[];
  reputation: number;
  successRate: number;
  totalDecisions: number;
  trustLevel: 'high' | 'medium' | 'low';
  isOnline: boolean;
  lastSeen?: string;
}

interface DecisionCollaboration {
  id: string;
  title: string;
  description: string;
  domain: string;
  entity: string;
  creator: string;
  createdAt: string;
  deadline?: string;
  status: 'draft' | 'review' | 'voting' | 'decided' | 'executed';
  privacy: 'private' | 'team' | 'public';
  advisors: string[];
  votes: DecisionVote[];
  comments: DecisionComment[];
  finalDecision?: string;
  confidence: number;
  consensus: number;
}

interface DecisionVote {
  id: string;
  advisorId: string;
  advisorName: string;
  vote: 'approve' | 'reject' | 'abstain';
  confidence: number;
  reasoning: string;
  timestamp: string;
  stake?: number; // How much they're willing to stake on this decision
}

interface DecisionComment {
  id: string;
  advisorId: string;
  advisorName: string;
  content: string;
  timestamp: string;
  type: 'comment' | 'analysis' | 'question' | 'concern';
  reactions: { [key: string]: number };
  replies: DecisionComment[];
}

interface GroupIntelligence {
  totalAnalysts: number;
  diversityScore: number;
  experienceLevel: number;
  consensusStrength: number;
  riskAlignment: number;
  historicalAccuracy: number;
}

export function CollaborativeDecision() {
  const [collaborations, setCollaborations] = useState<DecisionCollaboration[]>([]);
  const [advisors, setAdvisors] = useState<Advisor[]>([]);
  const [groupIntelligence, setGroupIntelligence] = useState<GroupIntelligence>({
    totalAnalysts: 12,
    diversityScore: 0.82,
    experienceLevel: 0.76,
    consensusStrength: 0.68,
    riskAlignment: 0.71,
    historicalAccuracy: 0.74
  });
  const [selectedTab, setSelectedTab] = useState('active');
  const [newComment, setNewComment] = useState('');
  const [selectedCollaboration, setSelectedCollaboration] = useState<string | null>(null);

  useEffect(() => {
    // Mock advisor data
    const mockAdvisors: Advisor[] = [
      {
        id: 'adv_001',
        name: 'Sarah Chen',
        title: 'Crypto Strategy Lead',
        avatar: '/avatars/sarah.jpg',
        expertise: ['Cryptocurrency', 'DeFi', 'Market Analysis'],
        reputation: 4.8,
        successRate: 0.73,
        totalDecisions: 147,
        trustLevel: 'high',
        isOnline: true
      },
      {
        id: 'adv_002',
        name: 'Mike Rodriguez',
        title: 'Sports Analytics Director',
        expertise: ['Sports Betting', 'Statistical Modeling', 'NBA/NFL'],
        reputation: 4.6,
        successRate: 0.68,
        totalDecisions: 203,
        trustLevel: 'high',
        isOnline: false,
        lastSeen: '2h ago'
      },
      {
        id: 'adv_003',
        name: 'Emily Watson',
        title: 'Options Trader',
        expertise: ['Options Trading', 'Risk Management', 'Volatility'],
        reputation: 4.4,
        successRate: 0.71,
        totalDecisions: 89,
        trustLevel: 'medium',
        isOnline: true
      },
      {
        id: 'adv_004',
        name: 'David Kim',
        title: 'Real Estate Analyst',
        expertise: ['Real Estate', 'Market Valuation', 'Austin Market'],
        reputation: 4.7,
        successRate: 0.69,
        totalDecisions: 156,
        trustLevel: 'high',
        isOnline: true
      }
    ];

    // Mock collaboration data
    const mockCollaborations: DecisionCollaboration[] = [
      {
        id: 'collab_001',
        title: 'Bitcoin Position Size for Q4',
        description: 'Analyzing optimal BTC allocation considering current market conditions and portfolio risk',
        domain: 'CRYPTO',
        entity: 'BTC/USD',
        creator: 'You',
        createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
        status: 'voting',
        privacy: 'team',
        advisors: ['adv_001', 'adv_003'],
        confidence: 0.78,
        consensus: 0.65,
        votes: [
          {
            id: 'vote_001',
            advisorId: 'adv_001',
            advisorName: 'Sarah Chen',
            vote: 'approve',
            confidence: 0.85,
            reasoning: 'Technical indicators suggest strong support at $62K. Recommend 25% allocation.',
            timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
            stake: 5000
          }
        ],
        comments: [
          {
            id: 'comment_001',
            advisorId: 'adv_001',
            advisorName: 'Sarah Chen',
            content: 'Looking at the whale accumulation patterns, I see strong conviction building around these levels. The risk/reward is favorable.',
            timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
            type: 'analysis',
            reactions: { '👍': 2, '🔥': 1 },
            replies: []
          }
        ]
      },
      {
        id: 'collab_002',
        title: 'Lakers vs Warriors Spread Analysis',
        description: 'Evaluating the line movement and betting opportunity for tonight\'s game',
        domain: 'SPORTS_BETTING',
        entity: 'Lakers vs Warriors',
        creator: 'You',
        createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        deadline: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(),
        status: 'review',
        privacy: 'private',
        advisors: ['adv_002'],
        confidence: 0.82,
        consensus: 0.91,
        votes: [],
        comments: []
      }
    ];

    setAdvisors(mockAdvisors);
    setCollaborations(mockCollaborations);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-muted/50';
      case 'review': return 'bg-blue-500';
      case 'voting': return 'bg-yellow-500';
      case 'decided': return 'bg-green-500';
      case 'executed': return 'bg-purple-500';
      default: return 'bg-muted/50';
    }
  };

  const getTrustColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-green-500';
      case 'medium': return 'text-yellow-500';
      case 'low': return 'text-red-500';
      default: return 'text-muted-foreground';
    }
  };

  const getVoteIcon = (vote: string) => {
    switch (vote) {
      case 'approve': return <ThumbsUp className="h-4 w-4 text-green-500" />;
      case 'reject': return <ThumbsDown className="h-4 w-4 text-red-500" />;
      case 'abstain': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default: return null;
    }
  };

  const handleComment = (collaborationId: string) => {
    if (!newComment.trim()) return;

    const comment: DecisionComment = {
      id: `comment_${Date.now()}`,
      advisorId: 'you',
      advisorName: 'You',
      content: newComment,
      timestamp: new Date().toISOString(),
      type: 'comment',
      reactions: {},
      replies: []
    };

    setCollaborations(prev =>
      prev.map(collab =>
        collab.id === collaborationId
          ? { ...collab, comments: [...collab.comments, comment] }
          : collab
      )
    );
    setNewComment('');
  };

  const getTimeRemaining = (deadline: string) => {
    const now = new Date().getTime();
    const target = new Date(deadline).getTime();
    const diff = target - now;

    if (diff <= 0) return 'Expired';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days}d ${hours % 24}h`;
    }

    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-green-500 bg-clip-text text-transparent">
            Collaborative Decision Making
          </h2>
          <p className="text-muted-foreground text-sm mt-1">
            Share decisions with trusted advisors and leverage group intelligence
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Collaboration
          </Button>
          <Button size="sm" variant="outline">
            <UserPlus className="h-4 w-4 mr-2" />
            Invite Advisor
          </Button>
          <Button size="sm" variant="outline">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Group Intelligence Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Analysts</span>
              <Users className="h-4 w-4 text-blue-500" />
            </div>
            <p className="text-2xl font-bold mt-2">{groupIntelligence.totalAnalysts}</p>
            <p className="text-sm text-muted-foreground mt-1">Active advisors</p>
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Diversity</span>
              <Star className="h-4 w-4 text-purple-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-purple-500">
              {(groupIntelligence.diversityScore * 100).toFixed(0)}%
            </p>
            <Progress value={groupIntelligence.diversityScore * 100} className="mt-2 h-1" />
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Experience</span>
              <Crown className="h-4 w-4 text-yellow-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-yellow-500">
              {(groupIntelligence.experienceLevel * 100).toFixed(0)}%
            </p>
            <Progress value={groupIntelligence.experienceLevel * 100} className="mt-2 h-1" />
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Consensus</span>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-green-500">
              {(groupIntelligence.consensusStrength * 100).toFixed(0)}%
            </p>
            <Progress value={groupIntelligence.consensusStrength * 100} className="mt-2 h-1" />
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Risk Alignment</span>
              <TrendingUp className="h-4 w-4 text-orange-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-orange-500">
              {(groupIntelligence.riskAlignment * 100).toFixed(0)}%
            </p>
            <Progress value={groupIntelligence.riskAlignment * 100} className="mt-2 h-1" />
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Accuracy</span>
              <Star className="h-4 w-4 text-blue-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-blue-500">
              {(groupIntelligence.historicalAccuracy * 100).toFixed(0)}%
            </p>
            <p className="text-sm text-muted-foreground mt-1">Historical</p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="active">Active Decisions</TabsTrigger>
          <TabsTrigger value="advisors">Advisors</TabsTrigger>
          <TabsTrigger value="history">Decision History</TabsTrigger>
        </TabsList>

        {/* Active Decisions Tab */}
        <TabsContent value="active" className="space-y-4">
          {collaborations.map(collaboration => (
            <Card key={collaboration.id} className="bg-card">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-lg font-semibold">{collaboration.title}</h3>
                      <Badge className={`${getStatusColor(collaboration.status)} text-foreground`}>
                        {collaboration.status.toUpperCase()}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {collaboration.domain}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {collaboration.privacy}
                      </Badge>
                    </div>
                    <p className="text-muted-foreground text-sm">{collaboration.description}</p>
                  </div>
                  {collaboration.deadline && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Clock className="h-4 w-4" />
                      {getTimeRemaining(collaboration.deadline)}
                    </div>
                  )}
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Progress Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-muted-foreground">Confidence</span>
                      <span className="text-sm font-bold">{(collaboration.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <Progress value={collaboration.confidence * 100} className="h-2" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-muted-foreground">Consensus</span>
                      <span className="text-sm font-bold">{(collaboration.consensus * 100).toFixed(0)}%</span>
                    </div>
                    <Progress value={collaboration.consensus * 100} className="h-2" />
                  </div>
                </div>

                {/* Advisors */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Advisors ({collaboration.advisors.length})</span>
                    <Button size="sm" variant="outline">
                      <Plus className="h-3 w-3 mr-1" />
                      Add
                    </Button>
                  </div>
                  <div className="flex items-center gap-2">
                    {collaboration.advisors.map(advisorId => {
                      const advisor = advisors.find(a => a.id === advisorId);
                      if (!advisor) return null;

                      return (
                        <div key={advisorId} className="flex items-center gap-1">
                          <Avatar className="h-6 w-6">
                            <AvatarImage src={advisor.avatar} />
                            <AvatarFallback className="text-xs">
                              {advisor.name.split(' ').map(n => n[0]).join('')}
                            </AvatarFallback>
                          </Avatar>
                          <div className={`w-2 h-2 rounded-full ${advisor.isOnline ? 'bg-green-500' : 'bg-muted/50'}`} />
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Votes */}
                {collaboration.votes.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2">Votes ({collaboration.votes.length})</h4>
                    <div className="space-y-2">
                      {collaboration.votes.map(vote => (
                        <div key={vote.id} className="bg-card rounded-lg p-3">
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-2">
                              {getVoteIcon(vote.vote)}
                              <span className="font-medium">{vote.advisorName}</span>
                              <Badge variant="outline" className="text-xs">
                                {(vote.confidence * 100).toFixed(0)}% confident
                              </Badge>
                              {vote.stake && (
                                <Badge variant="outline" className="text-xs text-green-500">
                                  ${vote.stake.toLocaleString()} stake
                                </Badge>
                              )}
                            </div>
                            <span className="text-xs text-muted-foreground">
                              {new Date(vote.timestamp).toLocaleString()}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-2">{vote.reasoning}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Comments */}
                {collaboration.comments.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2">Discussion ({collaboration.comments.length})</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {collaboration.comments.map(comment => (
                        <div key={comment.id} className="bg-card rounded-lg p-3">
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-sm">{comment.advisorName}</span>
                              <Badge variant="outline" className="text-xs">
                                {comment.type}
                              </Badge>
                            </div>
                            <span className="text-xs text-muted-foreground">
                              {new Date(comment.timestamp).toLocaleString()}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">{comment.content}</p>
                          {Object.keys(comment.reactions).length > 0 && (
                            <div className="flex items-center gap-2 mt-2">
                              {Object.entries(comment.reactions).map(([emoji, count]) => (
                                <Badge key={emoji} variant="outline" className="text-xs">
                                  {emoji} {count}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Add Comment */}
                <div className="flex gap-2">
                  <Input
                    placeholder="Add your thoughts..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    className="flex-1"
                  />
                  <Button
                    size="sm"
                    onClick={() => handleComment(collaboration.id)}
                    disabled={!newComment.trim()}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2 border-t border-gray-700">
                  <Button size="sm">
                    <Eye className="h-4 w-4 mr-2" />
                    View Details
                  </Button>
                  <Button size="sm" variant="outline">
                    <Share2 className="h-4 w-4 mr-2" />
                    Share
                  </Button>
                  <Button size="sm" variant="outline">
                    <Copy className="h-4 w-4 mr-2" />
                    Copy Link
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Advisors Tab */}
        <TabsContent value="advisors" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {advisors.map(advisor => (
              <Card key={advisor.id} className="bg-card">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={advisor.avatar} />
                      <AvatarFallback>
                        {advisor.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold">{advisor.name}</h3>
                        <div className="flex items-center gap-1">
                          <div className={`w-2 h-2 rounded-full ${advisor.isOnline ? 'bg-green-500' : 'bg-muted/50'}`} />
                          <span className="text-xs text-muted-foreground">
                            {advisor.isOnline ? 'Online' : advisor.lastSeen || 'Offline'}
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground">{advisor.title}</p>

                      <div className="flex items-center gap-2 mt-2">
                        <div className="flex items-center gap-1">
                          <Star className="h-3 w-3 text-yellow-500" />
                          <span className="text-sm">{advisor.reputation}</span>
                        </div>
                        <Badge className={getTrustColor(advisor.trustLevel)}>
                          {advisor.trustLevel} trust
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                        <div>
                          <span className="text-muted-foreground">Success Rate:</span>
                          <span className="font-bold ml-1">{(advisor.successRate * 100).toFixed(0)}%</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Decisions:</span>
                          <span className="font-bold ml-1">{advisor.totalDecisions}</span>
                        </div>
                      </div>

                      <div className="mt-3">
                        <p className="text-xs text-muted-foreground mb-1">Expertise:</p>
                        <div className="flex flex-wrap gap-1">
                          {advisor.expertise.slice(0, 2).map(skill => (
                            <Badge key={skill} variant="outline" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                          {advisor.expertise.length > 2 && (
                            <Badge variant="outline" className="text-xs">
                              +{advisor.expertise.length - 2}
                            </Badge>
                          )}
                        </div>
                      </div>

                      <div className="flex gap-1 mt-3">
                        <Button size="sm" className="flex-1">
                          <MessageSquare className="h-3 w-3 mr-1" />
                          Invite
                        </Button>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-4">
          <Card className="bg-card">
            <CardContent className="text-center py-12">
              <Calendar className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h3 className="text-lg font-semibold mb-2">Decision History</h3>
              <p className="text-muted-foreground">
                Past collaborative decisions and their outcomes will appear here.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}