import { useEffect } from 'react';

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string[];
  image?: string;
  url?: string;
  type?: 'website' | 'article';
  publishedTime?: string;
  modifiedTime?: string;
  author?: string;
  siteName?: string;
  twitterCard?: 'summary' | 'summary_large_image';
}

export function SEO({
  title = 'Donkey Betz - Blog',
  description = 'Discover insights, stories, and AI-powered content from Donkey Betz',
  keywords = [],
  image,
  url,
  type = 'website',
  publishedTime,
  modifiedTime,
  author,
  siteName = 'Donkey Betz',
  twitterCard = 'summary_large_image'
}: SEOProps) {
  useEffect(() => {
    // Set document title
    document.title = title;

    // Update or create meta tags
    updateMetaTag('description', description);
    updateMetaTag('keywords', keywords.join(', '));
    
    // Open Graph meta tags
    updateMetaProperty('og:title', title);
    updateMetaProperty('og:description', description);
    updateMetaProperty('og:type', type);
    updateMetaProperty('og:site_name', siteName);
    
    if (url) updateMetaProperty('og:url', url);
    if (image) updateMetaProperty('og:image', image);
    if (publishedTime) updateMetaProperty('article:published_time', publishedTime);
    if (modifiedTime) updateMetaProperty('article:modified_time', modifiedTime);
    if (author) updateMetaProperty('article:author', author);

    // Twitter Card meta tags
    updateMetaName('twitter:card', twitterCard);
    updateMetaName('twitter:title', title);
    updateMetaName('twitter:description', description);
    if (image) updateMetaName('twitter:image', image);

    // Canonical URL
    if (url) {
      updateCanonicalLink(url);
    }

    // JSON-LD structured data for articles
    if (type === 'article' && publishedTime) {
      updateStructuredData({
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': title,
        'description': description,
        'image': image,
        'url': url,
        'datePublished': publishedTime,
        'dateModified': modifiedTime || publishedTime,
        'author': {
          '@type': 'Organization',
          'name': author || siteName
        },
        'publisher': {
          '@type': 'Organization',
          'name': siteName
        }
      });
    }

    return () => {
      // Cleanup function to reset to default values when component unmounts
      document.title = 'Donkey Betz';
    };
  }, [title, description, keywords, image, url, type, publishedTime, modifiedTime, author, siteName, twitterCard]);

  return null;
}

// Helper functions
function updateMetaTag(name: string, content: string) {
  if (!content) return;
  
  let meta = document.querySelector(`meta[name="${name}"]`);
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute('name', name);
    document.head.appendChild(meta);
  }
  meta.setAttribute('content', content);
}

function updateMetaProperty(property: string, content: string) {
  if (!content) return;
  
  let meta = document.querySelector(`meta[property="${property}"]`);
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute('property', property);
    document.head.appendChild(meta);
  }
  meta.setAttribute('content', content);
}

function updateMetaName(name: string, content: string) {
  if (!content) return;
  
  let meta = document.querySelector(`meta[name="${name}"]`);
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute('name', name);
    document.head.appendChild(meta);
  }
  meta.setAttribute('content', content);
}

function updateCanonicalLink(url: string) {
  let link = document.querySelector('link[rel="canonical"]');
  if (!link) {
    link = document.createElement('link');
    link.setAttribute('rel', 'canonical');
    document.head.appendChild(link);
  }
  link.setAttribute('href', url);
}

function updateStructuredData(data: any) {
  // Remove existing structured data
  const existing = document.querySelector('script[type="application/ld+json"]');
  if (existing) {
    existing.remove();
  }

  // Add new structured data
  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.textContent = JSON.stringify(data);
  document.head.appendChild(script);
}

// Utility function to generate SEO-friendly URLs
export function generateSEOUrl(title: string, id: number): string {
  const slug = title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single
    .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
  
  return `/blog/${id}/${slug}`;
}

// Extract the first image from blog content for OG image
export function extractImageFromContent(content: string): string | null {
  const imageMatch = content.match(/!\[([^\]]*)\]\(([^)]+)\)/);
  return imageMatch ? imageMatch[2] : null;
}