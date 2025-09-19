import { useState, useRef, useEffect, forwardRef } from 'react';
import { Button } from '../common/Button';
import { 
  BoldIcon, 
  ItalicIcon,
  ListBulletIcon,
  QueueListIcon,
  ChatBubbleLeftRightIcon,
  CodeBracketIcon,
  ClockIcon,
  DocumentDuplicateIcon,
  PhotoIcon
} from '@heroicons/react/24/outline';

interface RichTextEditorProps {
  content: string;
  onChange: (content: string) => void;
  onAutoSave?: () => void;
  autoSaveInterval?: number; // in seconds
  placeholder?: string;
  className?: string;
  onInsertImage?: () => void; // Callback to open image insertion modal
}

export const RichTextEditor = forwardRef<HTMLTextAreaElement, RichTextEditorProps>(({
  content,
  onChange,
  onAutoSave,
  autoSaveInterval = 30,
  placeholder = "Start writing your chapter...",
  className = "",
  onInsertImage
}, _ref) => {
  const editorRef = useRef<HTMLTextAreaElement>(null);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [autoSaveTimer, setAutoSaveTimer] = useState<ReturnType<typeof setTimeout> | null>(null);
  const [isFocused, setIsFocused] = useState(false);

  // Auto-save functionality
  useEffect(() => {
    if (onAutoSave && content.trim()) {
      // Clear existing timer
      if (autoSaveTimer) {
        clearTimeout(autoSaveTimer);
      }

      // Set new timer
      const timer = setTimeout(() => {
        onAutoSave();
        setLastSaved(new Date());
      }, autoSaveInterval * 1000);

      setAutoSaveTimer(timer);

      return () => {
        if (timer) clearTimeout(timer);
      };
    }
  }, [content, onAutoSave, autoSaveInterval]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  const insertText = (before: string, after: string = '') => {
    if (!editorRef.current) return;

    const textarea = editorRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = content.substring(start, end);
    
    const newText = content.substring(0, start) + before + selectedText + after + content.substring(end);
    onChange(newText);

    // Set cursor position after the inserted text
    setTimeout(() => {
      textarea.selectionStart = start + before.length;
      textarea.selectionEnd = start + before.length + selectedText.length;
      textarea.focus();
    }, 0);
  };

  const formatBold = () => insertText('**', '**');
  const formatItalic = () => insertText('_', '_');
  const formatQuote = () => insertText('> ');
  const formatBulletList = () => insertText('- ');
  const formatNumberedList = () => insertText('1. ');
  const formatCode = () => insertText('`', '`');

  // Method to insert image at cursor position
  const insertImage = (imageUrl: string, altText?: string) => {
    if (!editorRef.current) return;

    const textarea = editorRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    
    const imageMarkdown = `\n![${altText || 'Image'}](${imageUrl})\n`;
    const newContent = content.substring(0, start) + imageMarkdown + content.substring(end);
    
    onChange(newContent);
    
    // Focus back to textarea and position cursor after the inserted image
    setTimeout(() => {
      textarea.focus();
      const newCursorPosition = start + imageMarkdown.length;
      textarea.setSelectionRange(newCursorPosition, newCursorPosition);
    }, 100);
  };

  // Store the insertImage function in a ref so it can be accessed from parent
  useEffect(() => {
    if (editorRef.current) {
      (editorRef.current as any).insertImage = insertImage;
    }
  }, [content]);

  const calculateStats = (text: string) => {
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const readingTime = Math.ceil(words / 200); // 200 words per minute
    return { words, readingTime };
  };

  const stats = calculateStats(content);

  return (
    <div className={`border border-dark-600 rounded-lg bg-card ${className}`}>
      {/* Toolbar */}
      <div className="border-b border-dark-600 p-3">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Formatting buttons */}
          <div className="flex items-center gap-1">
            <Button
              size="sm"
              variant="ghost"
              onClick={formatBold}
              className="p-1"
              title="Bold (Ctrl+B)"
            >
              <BoldIcon className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={formatItalic}
              className="p-1"
              title="Italic (Ctrl+I)"
            >
              <ItalicIcon className="h-4 w-4" />
            </Button>
          </div>

          <div className="w-px h-6 bg-dark-600" />

          {/* List buttons */}
          <div className="flex items-center gap-1">
            <Button
              size="sm"
              variant="ghost"
              onClick={formatBulletList}
              className="p-1"
              title="Bullet List"
            >
              <ListBulletIcon className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={formatNumberedList}
              className="p-1"
              title="Numbered List"
            >
              <QueueListIcon className="h-4 w-4" />
            </Button>
          </div>

          <div className="w-px h-6 bg-dark-600" />

          {/* Other formatting */}
          <div className="flex items-center gap-1">
            <Button
              size="sm"
              variant="ghost"
              onClick={formatQuote}
              className="p-1"
              title="Quote"
            >
              <ChatBubbleLeftRightIcon className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={formatCode}
              className="p-1"
              title="Code"
            >
              <CodeBracketIcon className="h-4 w-4" />
            </Button>
          </div>

          {/* Image insertion button */}
          {onInsertImage && (
            <>
              <div className="w-px h-6 bg-dark-600" />
              <Button
                size="sm"
                variant="ghost"
                onClick={onInsertImage}
                className="p-1"
                title="Insert Image"
              >
                <PhotoIcon className="h-4 w-4" />
              </Button>
            </>
          )}

          {/* Stats */}
          <div className="ml-auto flex items-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <DocumentDuplicateIcon className="h-3 w-3" />
              <span>{stats.words.toLocaleString()} words</span>
            </div>
            <div className="flex items-center gap-1">
              <ClockIcon className="h-3 w-3" />
              <span>{stats.readingTime} min read</span>
            </div>
            {lastSaved && (
              <div className="text-green-500">
                Saved {lastSaved.toLocaleTimeString()}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Editor */}
      <div className="p-4">
        <textarea
          ref={editorRef}
          value={content}
          onChange={handleInputChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          className="w-full h-96 bg-transparent text-foreground placeholder-gray-500 resize-none focus:outline-none font-mono text-sm leading-relaxed"
          style={{ minHeight: '24rem' }}
        />
      </div>

      {/* Status bar */}
      <div className="border-t border-dark-600 px-4 py-2 flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-4">
          <span>Lines: {content.split('\n').length}</span>
          <span>Characters: {content.length.toLocaleString()}</span>
          <span>Characters (no spaces): {content.replace(/\s/g, '').length.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-2">
          {onAutoSave && (
            <span className="text-muted-foreground">
              Auto-save every {autoSaveInterval}s
            </span>
          )}
          <div className={`w-2 h-2 rounded-full ${isFocused ? 'bg-green-400' : 'bg-gray-600'}`} />
        </div>
      </div>
    </div>
  );
});

RichTextEditor.displayName = 'RichTextEditor';