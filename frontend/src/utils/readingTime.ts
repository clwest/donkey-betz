interface ReadingTimeResult {
  minutes: number;
  words: number;
  text: string;
}

export function calculateReadingTime(content: string, wordsPerMinute: number = 200): ReadingTimeResult {
  // Remove markdown formatting and HTML tags for accurate word count
  const cleanContent = content
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, '') // Remove images
    .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold
    .replace(/\*(.*?)\*/g, '$1') // Remove italic
    .replace(/<[^>]*>/g, '') // Remove HTML tags
    .replace(/#{1,6}\s+/g, '') // Remove markdown headers
    .replace(/\n+/g, ' ') // Replace line breaks with spaces
    .trim();

  // Count words
  const words = cleanContent.split(/\s+/).filter(word => word.length > 0).length;
  
  // Calculate reading time in minutes
  const minutes = Math.ceil(words / wordsPerMinute);
  
  // Generate readable text
  let text: string;
  if (minutes < 1) {
    text = 'Less than 1 min read';
  } else if (minutes === 1) {
    text = '1 min read';
  } else {
    text = `${minutes} min read`;
  }

  return {
    minutes,
    words,
    text
  };
}

export function getReadingTimeFromWordCount(wordCount: number, wordsPerMinute: number = 200): ReadingTimeResult {
  const minutes = Math.ceil(wordCount / wordsPerMinute);
  
  let text: string;
  if (minutes < 1) {
    text = 'Less than 1 min read';
  } else if (minutes === 1) {
    text = '1 min read';
  } else {
    text = `${minutes} min read`;
  }

  return {
    minutes,
    words: wordCount,
    text
  };
}