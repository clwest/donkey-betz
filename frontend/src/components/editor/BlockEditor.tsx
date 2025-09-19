import { useState, useRef, useEffect } from 'react';
import { ImageInsertion } from '../features/blog/ImageInsertion';
import type { ContentBlock } from '../../types/blockEditor';
import { 
  PlusIcon,
  PhotoIcon,
  Bars3Icon,
  XMarkIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

// Re-export for convenience
export type { ContentBlock };

interface BlockEditorProps {
  blocks: ContentBlock[];
  onChange: (blocks: ContentBlock[]) => void;
  placeholder?: string;
  className?: string;
}

export function BlockEditor({ 
  blocks, 
  onChange, 
  placeholder = "Start writing...",
  className = "" 
}: BlockEditorProps) {
  const [activeBlockId, setActiveBlockId] = useState<string | null>(null);
  const [hoveredBlockId, setHoveredBlockId] = useState<string | null>(null);
  const [showAddMenu, setShowAddMenu] = useState<string | null>(null);
  const [imageInsertionOpen, setImageInsertionOpen] = useState(false);
  const [insertAfterBlockId, setInsertAfterBlockId] = useState<string | null>(null);
  const blockRefs = useRef<{ [key: string]: HTMLElement | null }>({});

  // Initialize with at least one text block if empty
  useEffect(() => {
    if (blocks.length === 0) {
      const initialBlock: ContentBlock = {
        id: generateId(),
        type: 'text',
        content: ''
      };
      onChange([initialBlock]);
    }
  }, []);

  const generateId = () => {
    return `block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  const handleBlockChange = (blockId: string, content: string) => {
    const updatedBlocks = blocks.map(block => 
      block.id === blockId ? { ...block, content } : block
    );
    onChange(updatedBlocks);
  };

  const handleAddBlock = (afterBlockId: string, type: 'text' | 'image' | 'heading') => {
    const index = blocks.findIndex(b => b.id === afterBlockId);
    const newBlock: ContentBlock = {
      id: generateId(),
      type,
      content: type === 'heading' ? '' : '',
      metadata: type === 'heading' ? { level: 2 } : undefined
    };

    const updatedBlocks = [...blocks];
    updatedBlocks.splice(index + 1, 0, newBlock);
    onChange(updatedBlocks);
    setShowAddMenu(null);

    // Focus the new block if it's text or heading
    if (type === 'text' || type === 'heading') {
      setTimeout(() => {
        const newBlockElement = blockRefs.current[newBlock.id];
        if (newBlockElement) {
          const input = newBlockElement.querySelector('textarea, input');
          (input as HTMLElement)?.focus();
        }
      }, 100);
    } else if (type === 'image') {
      setInsertAfterBlockId(afterBlockId);
      setImageInsertionOpen(true);
    }
  };

  const handleImageInsert = (imageUrl: string, altText?: string) => {
    if (insertAfterBlockId) {
      const index = blocks.findIndex(b => b.id === insertAfterBlockId);
      const newBlock: ContentBlock = {
        id: generateId(),
        type: 'image',
        content: altText || 'Image',
        metadata: {
          imageUrl,
          altText
        }
      };

      const updatedBlocks = [...blocks];
      updatedBlocks.splice(index + 1, 0, newBlock);
      onChange(updatedBlocks);
      setImageInsertionOpen(false);
      setInsertAfterBlockId(null);
    }
  };

  const handleDeleteBlock = (blockId: string) => {
    // Don't delete if it's the only block
    if (blocks.length <= 1) {
      const updatedBlocks = blocks.map(block => 
        block.id === blockId ? { ...block, content: '' } : block
      );
      onChange(updatedBlocks);
    } else {
      const updatedBlocks = blocks.filter(block => block.id !== blockId);
      onChange(updatedBlocks);
    }
  };

  const handleMoveBlock = (blockId: string, direction: 'up' | 'down') => {
    const index = blocks.findIndex(b => b.id === blockId);
    if (
      (direction === 'up' && index === 0) || 
      (direction === 'down' && index === blocks.length - 1)
    ) {
      return;
    }

    const newIndex = direction === 'up' ? index - 1 : index + 1;
    const updatedBlocks = [...blocks];
    const [movedBlock] = updatedBlocks.splice(index, 1);
    updatedBlocks.splice(newIndex, 0, movedBlock);
    onChange(updatedBlocks);
  };

  const handleKeyDown = (e: React.KeyboardEvent, blockId: string, blockIndex: number) => {
    const block = blocks[blockIndex];
    
    // Handle Enter key to create new block
    if (e.key === 'Enter' && !e.shiftKey && block.type === 'text') {
      e.preventDefault();
      
      const textarea = e.target as HTMLTextAreaElement;
      const cursorPosition = textarea.selectionStart;
      const content = block.content;
      
      // Split content at cursor position
      const beforeCursor = content.substring(0, cursorPosition);
      const afterCursor = content.substring(cursorPosition);
      
      // Update current block with content before cursor
      const updatedBlocks = [...blocks];
      updatedBlocks[blockIndex] = { ...block, content: beforeCursor };
      
      // Create new block with content after cursor
      const newBlock: ContentBlock = {
        id: generateId(),
        type: 'text',
        content: afterCursor
      };
      
      updatedBlocks.splice(blockIndex + 1, 0, newBlock);
      onChange(updatedBlocks);
      
      // Focus the new block
      setTimeout(() => {
        const newBlockElement = blockRefs.current[newBlock.id];
        if (newBlockElement) {
          const textarea = newBlockElement.querySelector('textarea');
          if (textarea) {
            textarea.focus();
            textarea.setSelectionRange(0, 0);
          }
        }
      }, 100);
    }
    
    // Handle Backspace at beginning to merge with previous block
    if (e.key === 'Backspace' && blockIndex > 0) {
      const textarea = e.target as HTMLTextAreaElement;
      if (textarea.selectionStart === 0 && textarea.selectionEnd === 0) {
        e.preventDefault();
        
        const prevBlock = blocks[blockIndex - 1];
        if (prevBlock.type === 'text') {
          // Merge with previous text block
          const mergedContent = prevBlock.content + block.content;
          const cursorPosition = prevBlock.content.length;
          
          const updatedBlocks = [...blocks];
          updatedBlocks[blockIndex - 1] = { ...prevBlock, content: mergedContent };
          updatedBlocks.splice(blockIndex, 1);
          onChange(updatedBlocks);
          
          // Focus previous block and set cursor position
          setTimeout(() => {
            const prevBlockElement = blockRefs.current[prevBlock.id];
            if (prevBlockElement) {
              const textarea = prevBlockElement.querySelector('textarea');
              if (textarea) {
                textarea.focus();
                textarea.setSelectionRange(cursorPosition, cursorPosition);
              }
            }
          }, 100);
        }
      }
    }
  };

  const renderBlock = (block: ContentBlock, index: number) => {
    const isActive = activeBlockId === block.id;
    const isHovered = hoveredBlockId === block.id;
    const showControls = isActive || isHovered;

    return (
      <div
        key={block.id}
        ref={(el) => { blockRefs.current[block.id] = el; }}
        className={`relative group ${isActive ? 'ring-1 ring-primary-500/30' : ''}`}
        onMouseEnter={() => setHoveredBlockId(block.id)}
        onMouseLeave={() => setHoveredBlockId(null)}
        onFocus={() => setActiveBlockId(block.id)}
        onBlur={() => setActiveBlockId(null)}
      >
        {/* Block Controls */}
        <div className={`absolute -left-12 top-0 flex flex-col gap-1 transition-opacity ${
          showControls ? 'opacity-100' : 'opacity-0'
        }`}>
          <button
            onClick={() => handleMoveBlock(block.id, 'up')}
            className="p-1 text-muted-foreground hover:text-foreground hover:bg-dark-700 rounded transition-colors"
            title="Move up"
            disabled={index === 0}
          >
            <ChevronUpIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleMoveBlock(block.id, 'down')}
            className="p-1 text-muted-foreground hover:text-foreground hover:bg-dark-700 rounded transition-colors"
            title="Move down"
            disabled={index === blocks.length - 1}
          >
            <ChevronDownIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleDeleteBlock(block.id)}
            className="p-1 text-muted-foreground hover:text-red-500 hover:bg-dark-700 rounded transition-colors"
            title="Delete block"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>

        {/* Block Content */}
        <div className="relative">
          {block.type === 'text' && (
            <textarea
              value={block.content}
              onChange={(e) => handleBlockChange(block.id, e.target.value)}
              onKeyDown={(e) => handleKeyDown(e, block.id, index)}
              placeholder={index === 0 ? placeholder : "Continue writing..."}
              className="w-full px-2 py-2 bg-transparent text-foreground placeholder-gray-500 resize-none focus:outline-none leading-relaxed"
              style={{ minHeight: '2rem' }}
              rows={1}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = target.scrollHeight + 'px';
              }}
            />
          )}

          {block.type === 'heading' && (
            <input
              type="text"
              value={block.content}
              onChange={(e) => handleBlockChange(block.id, e.target.value)}
              placeholder="Heading..."
              className={`w-full px-2 py-2 bg-transparent text-foreground placeholder-gray-500 focus:outline-none font-bold ${
                block.metadata?.level === 1 ? 'text-3xl' : 'text-2xl'
              }`}
            />
          )}

          {block.type === 'image' && block.metadata?.imageUrl && (
            <div className="relative my-4">
              <img
                src={block.metadata.imageUrl}
                alt={block.metadata.altText || 'Image'}
                className="w-full rounded-lg"
              />
              <input
                type="text"
                value={block.content}
                onChange={(e) => handleBlockChange(block.id, e.target.value)}
                placeholder="Image caption..."
                className="w-full px-2 py-2 mt-2 bg-transparent text-sm text-muted-foreground placeholder-gray-600 focus:outline-none text-center"
              />
            </div>
          )}
        </div>

        {/* Add Block Button */}
        <div className={`relative h-0 transition-all ${showControls ? 'h-8' : ''}`}>
          <div className={`absolute left-1/2 transform -translate-x-1/2 -bottom-4 transition-opacity ${
            showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
          }`}>
            {showAddMenu === block.id ? (
              <div className="flex items-center gap-2 bg-dark-700 rounded-lg p-2 shadow-lg">
                <button
                  onClick={() => handleAddBlock(block.id, 'text')}
                  className="p-2 text-muted-foreground hover:text-foreground hover:bg-dark-600 rounded transition-colors"
                  title="Add text"
                >
                  <Bars3Icon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleAddBlock(block.id, 'heading')}
                  className="p-2 text-muted-foreground hover:text-foreground hover:bg-dark-600 rounded transition-colors"
                  title="Add heading"
                >
                  <span className="font-bold text-sm">H</span>
                </button>
                <button
                  onClick={() => handleAddBlock(block.id, 'image')}
                  className="p-2 text-muted-foreground hover:text-foreground hover:bg-dark-600 rounded transition-colors"
                  title="Add image"
                >
                  <PhotoIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setShowAddMenu(null)}
                  className="p-2 text-muted-foreground hover:text-foreground hover:bg-dark-600 rounded transition-colors"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAddMenu(block.id)}
                className="p-2 bg-dark-700 hover:bg-dark-600 rounded-full text-muted-foreground hover:text-foreground transition-all transform hover:scale-110"
                title="Add block"
              >
                <PlusIcon className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`block-editor ${className}`}>
      <div className="space-y-2 pl-16 pr-4">
        {blocks.map((block, index) => renderBlock(block, index))}
      </div>

      {/* Add initial block if empty */}
      {blocks.length === 0 && (
        <div className="text-center py-12">
          <button
            onClick={() => handleAddBlock('', 'text')}
            className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-foreground rounded-lg transition-colors"
          >
            <PlusIcon className="h-5 w-5" />
            Start Writing
          </button>
        </div>
      )}

      {/* Image Insertion Modal */}
      <ImageInsertion
        isOpen={imageInsertionOpen}
        onClose={() => {
          setImageInsertionOpen(false);
          setInsertAfterBlockId(null);
        }}
        onInsert={handleImageInsert}
      />
    </div>
  );
}