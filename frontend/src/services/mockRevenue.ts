/**
 * Mock Revenue Data Generator
 * Creates realistic revenue tracking data for the Revenue Dashboard
 */

export interface RevenueEntry {
  id: string;
  date: string;
  amount: number;
  source: string;
  type: 'freelance' | 'job' | 'gig' | 'passive' | 'affiliate';
  platform: string;
  description: string;
  status: 'pending' | 'completed' | 'processing';
  agent?: string;
  client?: string;
}

export interface RevenueStats {
  total: number;
  monthly: number;
  weekly: number;
  daily: number;
  growth: number;
  projected: number;
  bySource: Record<string, number>;
  byType: Record<string, number>;
}

const revenueTemplates = [
  {
    source: 'Website Development',
    type: 'freelance',
    amount_range: [1500, 5000],
    platform: 'Upwork',
    agents: ['CodeMaster-7', 'ReactNinja-X']
  },
  {
    source: 'Mobile App Features',
    type: 'freelance',
    amount_range: [2000, 8000],
    platform: 'Freelancer',
    agents: ['MobileGenius-3', 'AppBuilder-Pro']
  },
  {
    source: 'Content Writing',
    type: 'gig',
    amount_range: [200, 800],
    platform: 'Fiverr',
    agents: ['ContentPro-5', 'BlogMaster-AI']
  },
  {
    source: 'Data Analysis',
    type: 'job',
    amount_range: [3000, 10000],
    platform: 'AngelList',
    agents: ['DataWizard-3', 'AnalyticsPro-8']
  },
  {
    source: 'AI Model Development',
    type: 'freelance',
    amount_range: [5000, 15000],
    platform: 'Toptal',
    agents: ['MLExpert-9', 'AIBuilder-7']
  },
  {
    source: 'API Integration',
    type: 'gig',
    amount_range: [500, 2000],
    platform: 'Upwork',
    agents: ['APIGuru-2', 'IntegrationPro-6']
  },
  {
    source: 'Blog Monetization',
    type: 'passive',
    amount_range: [100, 500],
    platform: 'Medium Partner',
    agents: ['ContentGen-AI']
  },
  {
    source: 'Affiliate Marketing',
    type: 'affiliate',
    amount_range: [50, 300],
    platform: 'Amazon Associates',
    agents: ['MarketingBot-4']
  }
];

const clients = [
  'TechStart Inc', 'Digital Solutions', 'AI Ventures',
  'CloudFirst', 'MobileApps Co', 'DataDriven LLC',
  'StartupHub', 'Innovation Labs', 'Future Systems'
];

export function generateMockRevenue(days: number = 30): RevenueEntry[] {
  const entries: RevenueEntry[] = [];
  const now = new Date();

  // Generate 2-4 revenue entries per day for the past N days
  for (let day = 0; day < days; day++) {
    const date = new Date(now);
    date.setDate(date.getDate() - day);

    const entriesPerDay = 2 + Math.floor(Math.random() * 3);

    for (let i = 0; i < entriesPerDay; i++) {
      const template = revenueTemplates[Math.floor(Math.random() * revenueTemplates.length)];
      const amount = template.amount_range[0] + Math.random() * (template.amount_range[1] - template.amount_range[0]);

      const entry: RevenueEntry = {
        id: `rev_${Date.now()}_${day}_${i}`,
        date: date.toISOString(),
        amount: Math.round(amount),
        source: template.source,
        type: template.type as any,
        platform: template.platform,
        description: `${template.source} for ${clients[Math.floor(Math.random() * clients.length)]}`,
        status: day < 3 ? 'pending' : (day < 7 ? 'processing' : 'completed'),
        agent: template.agents[Math.floor(Math.random() * template.agents.length)],
        client: clients[Math.floor(Math.random() * clients.length)]
      };

      entries.push(entry);
    }
  }

  return entries.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

export function calculateRevenueStats(entries: RevenueEntry[]): RevenueStats {
  const now = new Date();
  const oneMonthAgo = new Date(now);
  oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);

  const oneWeekAgo = new Date(now);
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

  const oneDayAgo = new Date(now);
  oneDayAgo.setDate(oneDayAgo.getDate() - 1);

  // Calculate totals
  const completedEntries = entries.filter(e => e.status === 'completed');
  const total = completedEntries.reduce((sum, e) => sum + e.amount, 0);

  const monthlyEntries = completedEntries.filter(e => new Date(e.date) >= oneMonthAgo);
  const monthly = monthlyEntries.reduce((sum, e) => sum + e.amount, 0);

  const weeklyEntries = completedEntries.filter(e => new Date(e.date) >= oneWeekAgo);
  const weekly = weeklyEntries.reduce((sum, e) => sum + e.amount, 0);

  const dailyEntries = completedEntries.filter(e => new Date(e.date) >= oneDayAgo);
  const daily = dailyEntries.reduce((sum, e) => sum + e.amount, 0);

  // Calculate growth (comparing last week to previous week)
  const twoWeeksAgo = new Date(now);
  twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
  const previousWeekEntries = completedEntries.filter(e => {
    const date = new Date(e.date);
    return date >= twoWeeksAgo && date < oneWeekAgo;
  });
  const previousWeek = previousWeekEntries.reduce((sum, e) => sum + e.amount, 0);
  const growth = previousWeek > 0 ? ((weekly - previousWeek) / previousWeek) * 100 : 0;

  // Calculate projected (based on current trend)
  const dailyAverage = monthly / 30;
  const projected = dailyAverage * 365;

  // Calculate by source
  const bySource: Record<string, number> = {};
  completedEntries.forEach(e => {
    bySource[e.source] = (bySource[e.source] || 0) + e.amount;
  });

  // Calculate by type
  const byType: Record<string, number> = {};
  completedEntries.forEach(e => {
    byType[e.type] = (byType[e.type] || 0) + e.amount;
  });

  return {
    total: Math.round(total),
    monthly: Math.round(monthly),
    weekly: Math.round(weekly),
    daily: Math.round(daily),
    growth: Math.round(growth * 10) / 10,
    projected: Math.round(projected),
    bySource,
    byType
  };
}

export function generateAgentPerformance(entries: RevenueEntry[]) {
  const agentStats: Record<string, { revenue: number; tasks: number; rating: number }> = {};

  entries.forEach(entry => {
    if (entry.agent && entry.status === 'completed') {
      if (!agentStats[entry.agent]) {
        agentStats[entry.agent] = { revenue: 0, tasks: 0, rating: 4.5 + Math.random() * 0.5 };
      }
      agentStats[entry.agent].revenue += entry.amount;
      agentStats[entry.agent].tasks += 1;
    }
  });

  // Convert to array and sort by revenue
  return Object.entries(agentStats)
    .map(([agent, stats]) => ({
      agent,
      ...stats,
      avgPerTask: Math.round(stats.revenue / stats.tasks)
    }))
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, 10); // Top 10 agents
}