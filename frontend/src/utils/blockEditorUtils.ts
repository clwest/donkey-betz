import type { ContentBlock } from '../types/blockEditor';

/**
 * Convert blocks to markdown format
 */
export function blocksToMarkdown(blocks: ContentBlock[]): string {
  return blocks.map(block => {
    switch (block.type) {
      case 'text':
        return block.content;
      
      case 'heading':
        const level = block.metadata?.level || 2;
        const prefix = '#'.repeat(level);
        return `${prefix} ${block.content}`;
      
      case 'image':
        const altText = block.metadata?.altText || block.content || 'Image';
        const imageUrl = block.metadata?.imageUrl || '';
        return `![${altText}](${imageUrl})${block.content ? `\n*${block.content}*` : ''}`;
      
      default:
        return block.content;
    }
  }).join('\n\n');
}

/**
 * Convert markdown to blocks format
 */
export function markdownToBlocks(markdown: string): ContentBlock[] {
  if (!markdown) {
    return [{
      id: `block-${Date.now()}`,
      type: 'text',
      content: ''
    }];
  }

  const lines = markdown.split('\n');
  const blocks: ContentBlock[] = [];
  let currentTextBlock = '';
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // Check for headings
    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      // Save any accumulated text block
      if (currentTextBlock.trim()) {
        blocks.push({
          id: `block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: 'text',
          content: currentTextBlock.trim()
        });
        currentTextBlock = '';
      }
      
      blocks.push({
        id: `block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'heading',
        content: headingMatch[2],
        metadata: {
          level: headingMatch[1].length
        }
      });
      continue;
    }
    
    // Check for images
    const imageMatch = line.match(/^!\[(.*?)\]\((.*?)\)$/);
    if (imageMatch) {
      // Save any accumulated text block
      if (currentTextBlock.trim()) {
        blocks.push({
          id: `block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: 'text',
          content: currentTextBlock.trim()
        });
        currentTextBlock = '';
      }
      
      // Check for caption on next line
      let caption = '';
      if (i + 1 < lines.length && lines[i + 1].match(/^\*.*\*$/)) {
        caption = lines[i + 1].replace(/^\*|\*$/g, '');
        i++; // Skip the caption line
      }
      
      blocks.push({
        id: `block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'image',
        content: caption || imageMatch[1],
        metadata: {
          imageUrl: imageMatch[2],
          altText: imageMatch[1]
        }
      });
      continue;
    }
    
    // Accumulate text lines
    if (line.trim() || currentTextBlock) {
      currentTextBlock += (currentTextBlock ? '\n' : '') + line;
    }
    
    // If we hit an empty line and have accumulated text, save it as a block
    if (line.trim() === '' && currentTextBlock.trim()) {
      blocks.push({
        id: `block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'text',
        content: currentTextBlock.trim()
      });
      currentTextBlock = '';
    }
  }
  
  // Save any remaining text
  if (currentTextBlock.trim()) {
    blocks.push({
      id: `block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'text',
      content: currentTextBlock.trim()
    });
  }
  
  // Ensure at least one block exists
  if (blocks.length === 0) {
    blocks.push({
      id: `block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'text',
      content: ''
    });
  }
  
  return blocks;
}