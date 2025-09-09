export interface Category {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  bgColor: string;
}

export const BLOG_CATEGORIES: Category[] = [
  {
    id: 'technology',
    name: 'Technology',
    description: 'Tech trends, software development, AI & innovation',
    icon: '💻',
    color: 'text-blue-300',
    bgColor: 'bg-blue-500/20'
  },
  {
    id: 'business',
    name: 'Business',
    description: 'Strategy, entrepreneurship, finance & growth',
    icon: '📊',
    color: 'text-green-300',
    bgColor: 'bg-green-500/20'
  },
  {
    id: 'marketing',
    name: 'Marketing',
    description: 'Digital marketing, content strategy & branding',
    icon: '📢',
    color: 'text-purple-300',
    bgColor: 'bg-purple-500/20'
  },
  {
    id: 'lifestyle',
    name: 'Lifestyle',
    description: 'Health, wellness, travel & personal development',
    icon: '🌟',
    color: 'text-yellow-300',
    bgColor: 'bg-yellow-500/20'
  },
  {
    id: 'education',
    name: 'Education',
    description: 'Learning, tutorials, guides & knowledge sharing',
    icon: '📚',
    color: 'text-indigo-300',
    bgColor: 'bg-indigo-500/20'
  },
  {
    id: 'creative',
    name: 'Creative',
    description: 'Design, art, writing & creative processes',
    icon: '🎨',
    color: 'text-pink-300',
    bgColor: 'bg-pink-500/20'
  },
  {
    id: 'science',
    name: 'Science',
    description: 'Research, discoveries, analysis & insights',
    icon: '🔬',
    color: 'text-cyan-300',
    bgColor: 'bg-cyan-500/20'
  },
  {
    id: 'opinion',
    name: 'Opinion',
    description: 'Thoughts, perspectives, commentary & analysis',
    icon: '💭',
    color: 'text-orange-300',
    bgColor: 'bg-orange-500/20'
  }
];

export function categorizeContent(title: string, tags: string[], tone: string): string | null {
  const contentText = `${title} ${tags.join(' ')} ${tone}`.toLowerCase();
  
  // Technology keywords
  if (/(tech|software|ai|artificial intelligence|programming|code|development|digital|app|platform|innovation|computer|data|algorithm|automation|api|cloud|cybersecurity)/.test(contentText)) {
    return 'technology';
  }
  
  // Business keywords
  if (/(business|startup|entrepreneur|finance|strategy|growth|revenue|profit|investment|sales|market|company|corporate|leadership|management|success)/.test(contentText)) {
    return 'business';
  }
  
  // Marketing keywords
  if (/(marketing|brand|advertising|content|social media|seo|campaign|promotion|audience|engagement|conversion|customer|digital marketing|email|influencer)/.test(contentText)) {
    return 'marketing';
  }
  
  // Education keywords
  if (/(education|learning|tutorial|guide|how to|tips|course|study|knowledge|skill|training|teach|lesson|student|academic|university)/.test(contentText)) {
    return 'education';
  }
  
  // Lifestyle keywords
  if (/(lifestyle|health|wellness|fitness|travel|food|fashion|home|personal|self-improvement|mindfulness|habits|relationships|family)/.test(contentText)) {
    return 'lifestyle';
  }
  
  // Creative keywords
  if (/(creative|design|art|writing|photography|music|video|storytelling|inspiration|aesthetic|visual|artistic|craft|imagination)/.test(contentText)) {
    return 'creative';
  }
  
  // Science keywords
  if (/(science|research|study|analysis|data|experiment|discovery|theory|scientific|medical|psychology|biology|physics|chemistry)/.test(contentText)) {
    return 'science';
  }
  
  // Opinion keywords (check last since it's more general)
  if (/(opinion|thought|perspective|commentary|review|analysis|insight|reflection|viewpoint|discussion|debate|consider)/.test(contentText)) {
    return 'opinion';
  }
  
  return null; // No category detected
}

export function getCategoryById(categoryId: string): Category | undefined {
  return BLOG_CATEGORIES.find(cat => cat.id === categoryId);
}

export function getAllCategories(): Category[] {
  return BLOG_CATEGORIES;
}

export function getPopularCategories(blogs: any[]): { category: Category; count: number }[] {
  const categoryCounts = new Map<string, number>();
  
  blogs.forEach(blog => {
    const category = categorizeContent(blog.title, blog.tags || [], blog.tone || '');
    if (category) {
      categoryCounts.set(category, (categoryCounts.get(category) || 0) + 1);
    }
  });
  
  return Array.from(categoryCounts.entries())
    .map(([categoryId, count]) => ({
      category: getCategoryById(categoryId)!,
      count
    }))
    .filter(item => item.category)
    .sort((a, b) => b.count - a.count);
}