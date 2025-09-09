export interface ContentBlock {
  id: string;
  type: 'text' | 'image' | 'heading';
  content: string;
  metadata?: {
    imageUrl?: string;
    altText?: string;
    level?: number; // for headings
  };
}