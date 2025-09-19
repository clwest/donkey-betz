import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Search, Database, Clock, Target, Brain, Filter,
  RefreshCw, ChevronRight, AlertTriangle, CheckCircle
} from 'lucide-react';

interface MemorySearchProps {
  domain: string;
  onMemorySelect: (memory: any) => void;
}

export function MemorySearch({ domain, onMemorySelect }: MemorySearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // Mock search results for now
      setTimeout(() => {
        const mockResults = [
          {
            id: 'mem_001',
            domain: 'SPORTS_BETTING',
            entity_id: 'game_12345',
            timestamp: '2024-01-15T10:30:00Z',
            context: {
              teams: 'Lakers vs Warriors',
              spread: -7.5,
              outcome: 'Lakers covered'
            },
            decision: 'EXECUTE',
            outcome: 'SUCCESS',
            similarity_score: 0.95
          },
          {
            id: 'mem_002',
            domain: 'CRYPTO',
            entity_id: 'btc_pattern_001',
            timestamp: '2024-01-14T14:20:00Z',
            context: {
              asset: 'BTC/USD',
              pattern: 'Ascending Triangle',
              resistance: 45000
            },
            decision: 'WAIT',
            outcome: 'SUCCESS',
            similarity_score: 0.87
          }
        ];

        setResults(mockResults);
        setLoading(false);
      }, 1000);
    } catch (err) {
      setError('Failed to search memory');
      setLoading(false);
    }
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 0.9) return 'text-green-500';
    if (score >= 0.7) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <Card className="bg-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5 text-purple-500" />
          Intelligence Memory Search
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search Input */}
        <div className="flex gap-2">
          <Input
            placeholder="Search patterns, decisions, outcomes..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="flex-1"
          />
          <Button onClick={handleSearch} disabled={loading || !query.trim()}>
            {loading ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Domain Filter */}
        <div className="flex items-center gap-2 text-sm">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-muted-foreground">Domain:</span>
          <Badge variant="outline">{domain}</Badge>
        </div>

        {/* Results */}
        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {loading && (
          <div className="text-center py-8">
            <RefreshCw className="h-8 w-8 mx-auto mb-4 animate-spin text-purple-500" />
            <p className="text-muted-foreground">Searching intelligence memory...</p>
          </div>
        )}

        {!loading && results.length === 0 && query && (
          <div className="text-center py-8">
            <Database className="h-8 w-8 mx-auto mb-4 opacity-50 text-muted-foreground" />
            <p className="text-muted-foreground">No memories found for "{query}"</p>
          </div>
        )}

        {!loading && results.length === 0 && !query && (
          <div className="text-center py-8">
            <Search className="h-8 w-8 mx-auto mb-4 opacity-50 text-muted-foreground" />
            <p className="text-muted-foreground">Enter a search term to explore intelligence memory</p>
          </div>
        )}

        {results.length > 0 && (
          <div className="space-y-3">
            {results.map((result) => (
              <div key={result.id} className="rounded-lg border border-gray-700/50 p-3 bg-gradient-to-r from-purple-900/10 to-transparent">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Brain className="h-4 w-4 text-purple-500" />
                    <span className="font-medium text-sm">{result.entity_id}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {result.domain}
                    </Badge>
                    <Badge className={`${getSimilarityColor(result.similarity_score)} bg-black/50 border-current`}>
                      {(result.similarity_score * 100).toFixed(0)}% match
                    </Badge>
                  </div>
                </div>

                <div className="space-y-2 mb-3">
                  <div className="text-sm text-muted-foreground">
                    <strong>Context:</strong> {JSON.stringify(result.context).slice(1, -1)}
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <div className="flex items-center gap-1">
                      <Target className="h-3 w-3 text-blue-500" />
                      <span>Decision: {result.decision}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      {result.outcome === 'SUCCESS' ? (
                        <CheckCircle className="h-3 w-3 text-green-500" />
                      ) : (
                        <AlertTriangle className="h-3 w-3 text-red-500" />
                      )}
                      <span>Outcome: {result.outcome}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <span>{new Date(result.timestamp).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-gray-700/50">
                  <span className="text-xs text-muted-foreground">
                    Similarity: {(result.similarity_score * 100).toFixed(1)}%
                  </span>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onMemorySelect(result)}
                    className="h-6 text-xs"
                  >
                    <ChevronRight className="h-3 w-3 mr-1" />
                    Apply Pattern
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {results.length > 0 && (
          <div className="text-center text-xs text-muted-foreground pt-4 border-t border-gray-700/50">
            Found {results.length} similar patterns in intelligence memory
          </div>
        )}
      </CardContent>
    </Card>
  );
}