interface BlogPost {
  id: number;
  title: string;
  tags: string[];
  word_count: number;
  created_at: string;
  preview?: string;
  meta_description?: string;
  tone?: string;
  length?: string;
}

interface RelatedPost extends BlogPost {
  similarity_score: number;
  similarity_reasons: string[];
}

export function findRelatedPosts(currentPost: BlogPost, allPosts: BlogPost[], limit: number = 3): RelatedPost[] {
  // Filter out the current post
  const otherPosts = allPosts.filter(post => post.id !== currentPost.id);
  
  // Calculate similarity scores for each post
  const postsWithScores = otherPosts.map(post => {
    const { score, reasons } = calculateSimilarity(currentPost, post);
    return {
      ...post,
      similarity_score: score,
      similarity_reasons: reasons
    };
  });

  // Sort by similarity score (descending) and return top results
  return postsWithScores
    .sort((a, b) => b.similarity_score - a.similarity_score)
    .slice(0, limit);
}

function calculateSimilarity(post1: BlogPost, post2: BlogPost): { score: number; reasons: string[] } {
  let score = 0;
  const reasons: string[] = [];

  // Tag similarity (highest weight)
  const commonTags = post1.tags?.filter(tag => post2.tags?.includes(tag)) || [];
  if (commonTags.length > 0) {
    const tagScore = (commonTags.length / Math.max(post1.tags?.length || 1, post2.tags?.length || 1)) * 50;
    score += tagScore;
    reasons.push(`${commonTags.length} shared tag${commonTags.length > 1 ? 's' : ''}: ${commonTags.slice(0, 2).join(', ')}`);
  }

  // Tone similarity
  if (post1.tone && post2.tone && post1.tone === post2.tone) {
    score += 20;
    reasons.push(`Same tone: ${post1.tone}`);
  }

  // Length similarity
  if (post1.length && post2.length && post1.length === post2.length) {
    score += 15;
    reasons.push(`Similar length: ${post1.length}`);
  }

  // Word count similarity
  const wordCountDiff = Math.abs((post1.word_count || 0) - (post2.word_count || 0));
  if (wordCountDiff < 200) {
    score += 10;
    reasons.push('Similar word count');
  }

  // Title similarity (simple word overlap)
  const titleSimilarity = calculateTextSimilarity(post1.title, post2.title);
  if (titleSimilarity > 0.3) {
    score += titleSimilarity * 15;
    reasons.push('Similar title themes');
  }

  // Content preview similarity
  const content1 = post1.preview || post1.meta_description || '';
  const content2 = post2.preview || post2.meta_description || '';
  if (content1 && content2) {
    const contentSimilarity = calculateTextSimilarity(content1, content2);
    if (contentSimilarity > 0.2) {
      score += contentSimilarity * 10;
      reasons.push('Similar content themes');
    }
  }

  // Recency boost (prefer newer posts)
  const post2Date = new Date(post2.created_at);
  const daysDiff = Math.abs(Date.now() - post2Date.getTime()) / (1000 * 60 * 60 * 24);
  if (daysDiff < 30) {
    score += 5;
    reasons.push('Recent post');
  }

  return { score: Math.round(score), reasons };
}

function calculateTextSimilarity(text1: string, text2: string): number {
  // Simple word overlap similarity
  const words1 = text1.toLowerCase().split(/\s+/).filter(w => w.length > 3);
  const words2 = text2.toLowerCase().split(/\s+/).filter(w => w.length > 3);
  
  if (words1.length === 0 || words2.length === 0) return 0;
  
  const commonWords = words1.filter(word => words2.includes(word));
  return commonWords.length / Math.max(words1.length, words2.length);
}

export function formatSimilarityReasons(reasons: string[]): string {
  if (reasons.length === 0) return 'Related content';
  if (reasons.length === 1) return reasons[0];
  if (reasons.length === 2) return reasons.join(' and ');
  return `${reasons.slice(0, -1).join(', ')} and ${reasons[reasons.length - 1]}`;
}