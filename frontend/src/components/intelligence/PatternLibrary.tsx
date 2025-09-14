import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
// import { ScrollArea } from '@/components/ui/scroll-area';
// Using native select for now to avoid hydration issues
import {
  BookOpen, TrendingUp, Calendar, Globe,
  RefreshCw, ChevronRight, Activity
} from 'lucide-react';
import {
  getPatternLibrary,
  type Pattern
} from '@/features/sports/api/sports';

interface PatternLibraryProps {
  domain?: string;
  onPatternSelect?: (pattern: Pattern) => void;
}

export function PatternLibrary({ domain: initialDomain, onPatternSelect }: PatternLibraryProps) {
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState(initialDomain || 'all');

  const loadPatterns = async () => {
    setLoading(true);
    try {
      const result = await getPatternLibrary(selectedDomain === 'all' ? undefined : selectedDomain);
      setPatterns(result);
    } catch (error) {
      console.error('Failed to load patterns:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPatterns();
  }, [selectedDomain]);

  const getDomainColor = (domains: string[]) => {
    if (domains.length > 1) return 'bg-gradient-to-r from-purple-500 to-indigo-500';
    const colors: Record<string, string> = {
      SPORTS_BETTING: 'bg-green-500',
      TRADING: 'bg-blue-500',
      CRYPTO: 'bg-orange-500',
      REAL_ESTATE: 'bg-purple-500',
      BUSINESS: 'bg-indigo-500'
    };
    return colors[domains[0]] || 'bg-gray-500';
  };

  const getSuccessColor = (rate: number) => {
    if (rate >= 0.7) return 'text-green-600';
    if (rate >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Card className="gaming-card">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-purple-500" />
            Pattern Library
          </div>
          <div className="flex items-center gap-2">
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="w-[150px] bg-dark-800 border border-dark-700 rounded-lg px-3 py-2 text-sm text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All Domains</option>
              <option value="SPORTS_BETTING">Sports Betting</option>
              <option value="TRADING">Trading</option>
              <option value="CRYPTO">Crypto</option>
              <option value="REAL_ESTATE">Real Estate</option>
              <option value="BUSINESS">Business</option>
            </select>
            <Button
              variant="ghost"
              size="sm"
              onClick={loadPatterns}
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[500px] overflow-y-auto">
          <div className="space-y-4">
            {patterns.map((pattern) => (
              <div
                key={pattern.id}
                className="rounded-lg border p-4 space-y-3 hover:bg-muted/50 transition-colors cursor-pointer"
                onClick={() => onPatternSelect && onPatternSelect(pattern)}
              >
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <h4 className="font-medium">{pattern.name}</h4>
                    <p className="text-sm text-muted-foreground">{pattern.description}</p>
                  </div>
                  <Badge className={`${getDomainColor(pattern.domains)} text-white`}>
                    {pattern.domains.length > 1 ? 'Cross-Domain' : pattern.domains[0]}
                  </Badge>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-1">
                      <Activity className="h-3 w-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">Frequency</span>
                    </div>
                    <p className="text-sm font-medium">{pattern.frequency} times</p>
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-1">
                      <TrendingUp className="h-3 w-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">Success Rate</span>
                    </div>
                    <p className={`text-sm font-medium ${getSuccessColor(pattern.success_rate)}`}>
                      {(pattern.success_rate * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">Last Seen</span>
                    </div>
                    <p className="text-sm font-medium">
                      {new Date(pattern.last_seen).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                {/* Success Rate Progress */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Pattern Reliability</span>
                    <span>{(pattern.success_rate * 100).toFixed(0)}%</span>
                  </div>
                  <Progress
                    value={pattern.success_rate * 100}
                    className="h-2"
                  />
                </div>

                {/* Examples */}
                {pattern.examples.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-xs text-muted-foreground">Recent Examples:</span>
                    <div className="space-y-1">
                      {pattern.examples.slice(0, 2).map((example, idx) => (
                        <div key={idx} className="flex items-center justify-between text-xs">
                          <div className="flex items-center gap-2">
                            <Globe className="h-3 w-3 text-muted-foreground" />
                            <span>{example.domain}</span>
                            <ChevronRight className="h-3 w-3 text-muted-foreground" />
                            <span className="text-muted-foreground">{example.entity_id}</span>
                          </div>
                          <Badge
                            variant={example.outcome === 'SUCCESS' ? 'default' : 'destructive'}
                            className="text-xs"
                          >
                            {example.outcome}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Domains */}
                {pattern.domains.length > 1 && (
                  <div className="flex flex-wrap gap-1">
                    {pattern.domains.map((domain) => (
                      <Badge key={domain} variant="outline" className="text-xs">
                        {domain}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Empty State */}
        {patterns.length === 0 && !loading && (
          <div className="text-center py-8 text-muted-foreground">
            <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm">No patterns found</p>
            <p className="text-xs mt-2">Patterns will appear as the system learns</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}