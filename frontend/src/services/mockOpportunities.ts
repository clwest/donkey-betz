/**
 * Mock Opportunities Generator for Income Builder
 * Generates realistic opportunities to show in the UI
 */

export interface Opportunity {
  id: string;
  title: string;
  company: string;
  location: string;
  type: 'job' | 'gig' | 'freelance' | 'contract' | 'business';
  category: string;
  description: string;
  requirements: string[];
  compensation: {
    min: number;
    max: number;
    type: 'hourly' | 'fixed' | 'annual';
    currency: string;
  };
  estimated_earnings: number;
  success_rate: number;
  market_demand: number;
  competition_level: 'low' | 'medium' | 'high';
  source: string;
  posted_date: string;
  deadline?: string;
  skills_match: number;
  ai_score: number;
  ai_recommendation: string;
  quick_apply_available: boolean;
  url?: string;
  tags: string[];
}

const jobTemplates = [
  {
    title: 'Full Stack Developer for E-commerce Platform',
    category: 'Software Development',
    skills: ['React', 'Node.js', 'PostgreSQL', 'AWS'],
    budget_range: [3000, 8000],
    hourly_range: [75, 150],
    duration: '3-6 months'
  },
  {
    title: 'React Native Mobile App Developer',
    category: 'Mobile Development',
    skills: ['React Native', 'iOS', 'Android', 'Firebase'],
    budget_range: [5000, 15000],
    hourly_range: [80, 160],
    duration: '2-4 months'
  },
  {
    title: 'Python Backend Developer for AI Startup',
    category: 'Backend Development',
    skills: ['Python', 'Django', 'FastAPI', 'Machine Learning'],
    budget_range: [4000, 10000],
    hourly_range: [90, 180],
    duration: '3-6 months'
  },
  {
    title: 'LLM Integration Specialist',
    category: 'AI/ML',
    skills: ['OpenAI API', 'LangChain', 'Python', 'NLP'],
    budget_range: [2000, 6000],
    hourly_range: [100, 200],
    duration: '1-2 months'
  },
  {
    title: 'Technical Content Writer for SaaS Blog',
    category: 'Content Creation',
    skills: ['Technical Writing', 'SEO', 'Marketing'],
    budget_range: [500, 2000],
    hourly_range: [30, 75],
    duration: 'Ongoing'
  },
  {
    title: 'UI/UX Designer for Mobile App',
    category: 'Design',
    skills: ['Figma', 'UI Design', 'UX Research'],
    budget_range: [2000, 6000],
    hourly_range: [50, 120],
    duration: '1-2 months'
  }
];

const companies = [
  'TechStart Solutions', 'Digital Innovations Inc', 'CloudFirst Systems',
  'AI Ventures', 'DataDriven Analytics', 'MobileFirst Apps',
  'E-commerce Plus', 'StartupHub', 'Remote Work Co', 'Global Tech Services'
];

const platforms = ['Upwork', 'Freelancer', 'Fiverr', 'Indeed', 'AngelList', 'RemoteOK'];

function generateRecommendation(skills_match: number, market_demand: number, earnings: number): string {
  if (skills_match > 0.85 && market_demand > 0.8) {
    return `Excellent match! Your skills align perfectly with this opportunity. High success probability with potential earnings of $${earnings.toLocaleString()}. Apply immediately.`;
  } else if (skills_match > 0.75) {
    return `Good opportunity with ${Math.round(skills_match * 100)}% skills match. Market demand is strong at ${Math.round(market_demand * 100)}%. Worth pursuing.`;
  } else if (earnings > 5000) {
    return `High-value opportunity worth $${earnings.toLocaleString()}. Consider upskilling on missing requirements to increase success rate.`;
  }
  return `Decent opportunity for skill building. ${Math.round(skills_match * 100)}% skills match with room for growth.`;
}

export function generateMockOpportunities(count: number = 10): Opportunity[] {
  const opportunities: Opportunity[] = [];

  for (let i = 0; i < count; i++) {
    const template = jobTemplates[Math.floor(Math.random() * jobTemplates.length)];
    const platform = platforms[Math.floor(Math.random() * platforms.length)];
    const company = companies[Math.floor(Math.random() * companies.length)];

    const isHourly = Math.random() > 0.4;
    let estimated_earnings: number;
    let compensation: any;

    if (isHourly) {
      const hourlyRate = template.hourly_range[0] + Math.random() * (template.hourly_range[1] - template.hourly_range[0]);
      const estimatedHours = 20 + Math.random() * 140;
      estimated_earnings = hourlyRate * estimatedHours;
      compensation = {
        min: Math.round(hourlyRate),
        max: Math.round(hourlyRate + 20),
        type: 'hourly',
        currency: 'USD'
      };
    } else {
      const budget = template.budget_range[0] + Math.random() * (template.budget_range[1] - template.budget_range[0]);
      estimated_earnings = budget;
      compensation = {
        min: Math.round(budget * 0.8),
        max: Math.round(budget * 1.2),
        type: 'fixed',
        currency: 'USD'
      };
    }

    const skills_match = 0.65 + Math.random() * 0.3;
    const market_demand = 0.6 + Math.random() * 0.35;
    const success_rate = (skills_match + market_demand) / 2;

    const opportunity: Opportunity = {
      id: `${platform.toLowerCase()}_${Date.now()}_${i}`,
      title: template.title,
      company,
      location: Math.random() > 0.2 ? 'Remote' : ['San Francisco, CA', 'New York, NY', 'Austin, TX'][Math.floor(Math.random() * 3)],
      type: ['job', 'contract', 'freelance', 'gig'][Math.floor(Math.random() * 4)] as any,
      category: template.category,
      description: `We are looking for a talented ${template.category} professional to help with ${template.title.toLowerCase()}. This is an exciting opportunity to work with our team on cutting-edge projects.`,
      requirements: template.skills,
      compensation,
      estimated_earnings: Math.round(estimated_earnings),
      success_rate,
      market_demand,
      competition_level: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as any,
      source: `🕷️ ${platform}`,
      posted_date: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      deadline: Math.random() > 0.5 ? new Date(Date.now() + Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString() : undefined,
      skills_match,
      ai_score: 0.7 + Math.random() * 0.25,
      ai_recommendation: generateRecommendation(skills_match, market_demand, estimated_earnings),
      quick_apply_available: Math.random() > 0.3,
      url: `https://${platform.toLowerCase()}.com/jobs/${Date.now()}_${i}`,
      tags: [...template.skills.slice(0, 3), template.category, platform]
    };

    opportunities.push(opportunity);
  }

  // Sort by AI score
  return opportunities.sort((a, b) => b.ai_score - a.ai_score);
}

export function generateEarningsProjection(opportunities: Opportunity[]) {
  const totalValue = opportunities.reduce((sum, opp) => sum + opp.estimated_earnings, 0);

  return {
    week_1: Math.round(totalValue * 0.1),
    month_1: Math.round(totalValue * 0.25),
    month_3: Math.round(totalValue * 0.6),
    month_6: Math.round(totalValue * 0.85),
    year_1: Math.round(totalValue * 1.5)
  };
}