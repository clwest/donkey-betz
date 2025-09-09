import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, TrendingUp, DollarSign, BarChart3, AlertCircle } from 'lucide-react';
import { AgentOrchestraService } from '@/services/agent-orchestra.service';
import { toast } from 'sonner';

interface FinanceAnalysisResult {
  ticker?: string;
  price?: number;
  change?: number;
  changePercent?: number;
  marketCap?: number;
  pe_ratio?: number;
  sentiment?: {
    overall: string;
    reddit: number;
    news: number;
  };
  technicals?: {
    rsi: number;
    macd: string;
    trend: string;
  };
  recommendation?: string;
  analysis?: string;
}

export const FinanceAgentPanel: React.FC = () => {
  const [analysisType, setAnalysisType] = useState<'stock' | 'market' | 'industry' | 'sentiment'>('stock');
  const [ticker, setTicker] = useState('');
  const [industry, setIndustry] = useState('');
  const [competitors, setCompetitors] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FinanceAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalysis = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let taskDescription = '';
      let parameters: Record<string, any> = {};

      switch (analysisType) {
        case 'stock':
          if (!ticker) {
            throw new Error('Please enter a stock ticker symbol');
          }
          taskDescription = `Analyze stock ${ticker.toUpperCase()} with technical indicators, fundamentals, and sentiment`;
          parameters = {
            ticker: ticker.toUpperCase(),
            include_reddit: true,
            include_sec: true
          };
          break;

        case 'market':
          taskDescription = 'Provide comprehensive market overview with major indices and trends';
          break;

        case 'industry':
          if (!industry) {
            throw new Error('Please enter an industry name');
          }
          taskDescription = `Analyze ${industry} industry landscape and competitive dynamics`;
          parameters = {
            industry,
            competitors: competitors ? competitors.split(',').map(c => c.trim()) : []
          };
          break;

        case 'sentiment':
          if (!ticker) {
            throw new Error('Please enter a stock ticker for sentiment analysis');
          }
          taskDescription = `Analyze market sentiment for ${ticker.toUpperCase()} across Reddit, news, and social media`;
          parameters = {
            ticker: ticker.toUpperCase(),
            sources: ['reddit', 'news', 'twitter']
          };
          break;
      }

      const response = await AgentOrchestraService.executeAgent({
        agent_type: 'finance_intelligence',
        task_description: taskDescription,
        parameters
      });

      if (response?.result) {
        setResult(response.result);
        toast.success('Financial analysis completed successfully');
      } else {
        throw new Error('No analysis results received');
      }
    } catch (err: any) {
      console.error('Finance analysis error:', err);
      setError(err.message || 'Failed to perform financial analysis');
      toast.error(err.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatLargeNumber = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return formatCurrency(value);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Finance Intelligence Agent
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="analysis-type">Analysis Type</Label>
            <Select value={analysisType} onValueChange={(value: any) => setAnalysisType(value)}>
              <SelectTrigger id="analysis-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="stock">Stock Analysis</SelectItem>
                <SelectItem value="market">Market Overview</SelectItem>
                <SelectItem value="industry">Industry Analysis</SelectItem>
                <SelectItem value="sentiment">Sentiment Analysis</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {(analysisType === 'stock' || analysisType === 'sentiment') && (
            <div>
              <Label htmlFor="ticker">Stock Ticker</Label>
              <Input
                id="ticker"
                placeholder="e.g., AAPL, NVDA, TSLA"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                className="uppercase"
              />
            </div>
          )}

          {analysisType === 'industry' && (
            <>
              <div>
                <Label htmlFor="industry">Industry</Label>
                <Input
                  id="industry"
                  placeholder="e.g., Technology, Healthcare, Finance"
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="competitors">Competitors (optional)</Label>
                <Input
                  id="competitors"
                  placeholder="e.g., AAPL, MSFT, GOOGL (comma-separated)"
                  value={competitors}
                  onChange={(e) => setCompetitors(e.target.value)}
                />
              </div>
            </>
          )}

          <Button 
            onClick={handleAnalysis} 
            disabled={loading}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <BarChart3 className="mr-2 h-4 w-4" />
                Run Analysis
              </>
            )}
          </Button>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {result.ticker && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Symbol</p>
                  <p className="font-semibold">{result.ticker}</p>
                </div>
                {result.price && (
                  <div>
                    <p className="text-sm text-muted-foreground">Price</p>
                    <p className="font-semibold">{formatCurrency(result.price)}</p>
                  </div>
                )}
                {result.change !== undefined && (
                  <div>
                    <p className="text-sm text-muted-foreground">Change</p>
                    <p className={`font-semibold ${result.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {result.change >= 0 ? '+' : ''}{result.changePercent?.toFixed(2)}%
                    </p>
                  </div>
                )}
                {result.marketCap && (
                  <div>
                    <p className="text-sm text-muted-foreground">Market Cap</p>
                    <p className="font-semibold">{formatLargeNumber(result.marketCap)}</p>
                  </div>
                )}
              </div>
            )}

            {result.sentiment && (
              <div>
                <h4 className="font-semibold mb-2">Sentiment Analysis</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Overall</p>
                    <p className={`font-semibold ${
                      result.sentiment.overall === 'bullish' ? 'text-green-600' : 
                      result.sentiment.overall === 'bearish' ? 'text-red-600' : 
                      'text-yellow-600'
                    }`}>
                      {result.sentiment.overall}
                    </p>
                  </div>
                  {result.sentiment.reddit !== undefined && (
                    <div>
                      <p className="text-sm text-muted-foreground">Reddit Score</p>
                      <p className="font-semibold">{result.sentiment.reddit.toFixed(2)}</p>
                    </div>
                  )}
                  {result.sentiment.news !== undefined && (
                    <div>
                      <p className="text-sm text-muted-foreground">News Score</p>
                      <p className="font-semibold">{result.sentiment.news.toFixed(2)}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {result.technicals && (
              <div>
                <h4 className="font-semibold mb-2">Technical Indicators</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">RSI</p>
                    <p className="font-semibold">{result.technicals.rsi.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">MACD</p>
                    <p className="font-semibold">{result.technicals.macd}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Trend</p>
                    <p className="font-semibold">{result.technicals.trend}</p>
                  </div>
                </div>
              </div>
            )}

            {result.recommendation && (
              <div>
                <h4 className="font-semibold mb-2">Recommendation</h4>
                <Alert>
                  <AlertDescription>{result.recommendation}</AlertDescription>
                </Alert>
              </div>
            )}

            {result.analysis && (
              <div>
                <h4 className="font-semibold mb-2">Detailed Analysis</h4>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm whitespace-pre-wrap">{result.analysis}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};