import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Heart, Mountain, Compass, Shield, Target, Brain, Sparkles, ChevronRight, Plus, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Conviction {
  id: string;
  title: string;
  description: string;
  strength: number; // 0-100
  category: 'values' | 'purpose' | 'relationships' | 'growth' | 'identity';
  dateCreated: string;
  lastTested: string;
  timesDefended: number;
  status: 'unshakeable' | 'strong' | 'developing' | 'questioning';
}

const mockConvictions: Conviction[] = [
  {
    id: '1',
    title: 'Family Always Comes First',
    description: 'No career achievement or personal goal is worth sacrificing family bonds',
    strength: 98,
    category: 'values',
    dateCreated: '2015-03-15',
    lastTested: '2024-12-28',
    timesDefended: 47,
    status: 'unshakeable'
  },
  {
    id: '2',
    title: 'Creativity is My Life Force',
    description: 'I was born to create, not just consume. Building things gives my life meaning',
    strength: 95,
    category: 'purpose',
    dateCreated: '2018-07-22',
    lastTested: '2025-01-10',
    timesDefended: 23,
    status: 'unshakeable'
  },
  {
    id: '3',
    title: 'Growth Through Discomfort',
    description: 'The moments that hurt the most teach the most valuable lessons',
    strength: 87,
    category: 'growth',
    dateCreated: '2020-01-01',
    lastTested: '2024-11-15',
    timesDefended: 15,
    status: 'strong'
  }
];

export function LifeConvictionsPage() {
  const navigate = useNavigate();
  const [convictions] = useState<Conviction[]>(mockConvictions);
  const [selectedConviction, setSelectedConviction] = useState<Conviction | null>(null);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'values': return <Shield className="h-4 w-4" />;
      case 'purpose': return <Target className="h-4 w-4" />;
      case 'relationships': return <Heart className="h-4 w-4" />;
      case 'growth': return <Brain className="h-4 w-4" />;
      case 'identity': return <Star className="h-4 w-4" />;
      default: return <Compass className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'unshakeable': return 'bg-purple-500';
      case 'strong': return 'bg-blue-500';
      case 'developing': return 'bg-green-500';
      case 'questioning': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-8">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-purple-900 to-indigo-900 rounded-lg p-8 text-white">
        <div className="flex items-center gap-4 mb-4">
          <Mountain className="h-12 w-12" />
          <div>
            <h1 className="text-4xl font-bold">Your Life Convictions</h1>
            <p className="text-lg opacity-90">The unshakeable beliefs that define who you are</p>
          </div>
        </div>
        <p className="max-w-2xl opacity-80">
          A "donkey bet" isn't about sports or gambling - it's a life conviction so deeply held that 
          moving a mountain would be easier than changing your mind. These are the beliefs that shape 
          your identity and guide your decisions.
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Convictions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{convictions.length}</div>
            <p className="text-xs text-muted-foreground">Life-defining beliefs</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Unshakeable</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {convictions.filter(c => c.status === 'unshakeable').length}
            </div>
            <p className="text-xs text-muted-foreground">Mountain-moving strong</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Times Defended</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {convictions.reduce((acc, c) => acc + c.timesDefended, 0)}
            </div>
            <p className="text-xs text-muted-foreground">Stood your ground</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">AI Agents Available</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">100+</div>
            <p className="text-xs text-muted-foreground">To test & strengthen</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="convictions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="convictions">My Convictions</TabsTrigger>
          <TabsTrigger value="test">Test & Strengthen</TabsTrigger>
          <TabsTrigger value="discover">Discover New</TabsTrigger>
          <TabsTrigger value="ai-council">AI Council</TabsTrigger>
        </TabsList>

        <TabsContent value="convictions" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-semibold">Your Core Beliefs</h2>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Conviction
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {convictions.map((conviction) => (
              <Card 
                key={conviction.id} 
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => setSelectedConviction(conviction)}
              >
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="space-y-1">
                      <CardTitle className="flex items-center gap-2">
                        {getCategoryIcon(conviction.category)}
                        {conviction.title}
                      </CardTitle>
                      <CardDescription>{conviction.description}</CardDescription>
                    </div>
                    <Badge className={getStatusColor(conviction.status)}>
                      {conviction.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Conviction Strength</span>
                        <span className="font-medium">{conviction.strength}%</span>
                      </div>
                      <Progress value={conviction.strength} className="h-2" />
                    </div>
                    <div className="flex justify-between text-sm text-muted-foreground">
                      <span>Defended {conviction.timesDefended} times</span>
                      <span>Since {new Date(conviction.dateCreated).getFullYear()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="test" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Test Your Convictions</CardTitle>
              <CardDescription>
                Use AI agents to challenge, strengthen, and validate your beliefs
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button variant="outline" className="justify-start">
                  <Brain className="h-4 w-4 mr-2" />
                  Devil's Advocate Challenge
                </Button>
                <Button variant="outline" className="justify-start">
                  <Compass className="h-4 w-4 mr-2" />
                  Values Alignment Check
                </Button>
                <Button variant="outline" className="justify-start">
                  <Shield className="h-4 w-4 mr-2" />
                  Conviction Strength Test
                </Button>
                <Button variant="outline" className="justify-start">
                  <Target className="h-4 w-4 mr-2" />
                  Life Path Validator
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="discover" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Discover Your Hidden Convictions</CardTitle>
              <CardDescription>
                AI-guided exploration to uncover beliefs you didn't know you held
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button className="w-full" size="lg">
                  <Sparkles className="h-5 w-5 mr-2" />
                  Start Conviction Discovery Session
                </Button>
                <div className="grid grid-cols-2 gap-4 pt-4">
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-center">
                        <Brain className="h-8 w-8 mx-auto mb-2 text-purple-500" />
                        <p className="font-medium">Deep Analysis</p>
                        <p className="text-sm text-muted-foreground">
                          100+ AI agents analyze your patterns
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-center">
                        <Mountain className="h-8 w-8 mx-auto mb-2 text-blue-500" />
                        <p className="font-medium">Unshakeable Results</p>
                        <p className="text-sm text-muted-foreground">
                          Find your mountain-moving beliefs
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ai-council" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Your AI Advisory Council</CardTitle>
              <CardDescription>
                100+ specialized agents to help you navigate life's biggest decisions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Decision Analysts</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2 text-sm">
                        <li className="flex items-center gap-2">
                          <ChevronRight className="h-3 w-3" />
                          Pro/Con Deep Analyzer
                        </li>
                        <li className="flex items-center gap-2">
                          <ChevronRight className="h-3 w-3" />
                          Scenario Simulator
                        </li>
                        <li className="flex items-center gap-2">
                          <ChevronRight className="h-3 w-3" />
                          Regret Minimization Calculator
                        </li>
                      </ul>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Life Planners</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2 text-sm">
                        <li className="flex items-center gap-2">
                          <ChevronRight className="h-3 w-3" />
                          Path Optimizer
                        </li>
                        <li className="flex items-center gap-2">
                          <ChevronRight className="h-3 w-3" />
                          Milestone Mapper
                        </li>
                        <li className="flex items-center gap-2">
                          <ChevronRight className="h-3 w-3" />
                          Resource Allocator
                        </li>
                      </ul>
                    </CardContent>
                  </Card>
                </div>
                <Button 
                  className="w-full" 
                  onClick={() => navigate('/agents')}
                >
                  Access Full AI Council
                  <ChevronRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Knowledge Base Link */}
      <Card className="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-950 dark:to-indigo-950">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            Explore Life Conviction Philosophy
          </CardTitle>
          <CardDescription>
            Deep dive into the knowledge base about unshakeable beliefs and life decisions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={() => navigate('/knowledge')}>
            Visit Personal Knowledge Base
            <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}