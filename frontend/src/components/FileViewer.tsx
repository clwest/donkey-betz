import React, { useState, useEffect } from 'react';
import { X, Download, Copy, CheckCircle, FileText, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';

interface FileViewerProps {
  filename: string;
  onClose: () => void;
}

export const FileViewer: React.FC<FileViewerProps> = ({ filename, onClose }) => {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchFileContent();
  }, [filename]);

  const fetchFileContent = async () => {
    try {
      setLoading(true);
      // Extract just the filename without the directory prefix
      let cleanFilename = filename;
      if (filename.includes('/')) {
        // Get the last part after the last slash
        const parts = filename.split('/');
        cleanFilename = parts[parts.length - 1];
      }

      // If the filename ends with .md, use it directly
      // Otherwise, convert it to the expected format
      if (!cleanFilename.endsWith('.md')) {
        cleanFilename = cleanFilename.replace(/ /g, '_') + '.md';
      }

      // Encode for URL
      const encodedFilename = encodeURIComponent(cleanFilename);
      console.log('Fetching file:', cleanFilename, 'from URL:', `http://localhost:8000/api/v1/intelligence/income-builder/file/${encodedFilename}/`);
      const response = await fetch(`http://localhost:8000/api/v1/intelligence/income-builder/file/${encodedFilename}/`);
      const data = await response.json();

      if (data.success) {
        setContent(data.content);
      } else {
        toast.error('Failed to load file');
      }
    } catch (error) {
      console.error('Error fetching file:', error);
      toast.error('Error loading file');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      toast.success('Content copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error('Failed to copy content');
    }
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('File downloaded');
  };

  const handleOpenInNewTab = () => {
    const newWindow = window.open('', '_blank');
    if (newWindow) {
      newWindow.document.write(`
        <html>
          <head>
            <title>${filename}</title>
            <style>
              body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                line-height: 1.6;
                color: #d1d5db;
                background: #111827;
              }
              pre {
                background: #1f2937;
                color: #d1d5db;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                border: 1px solid #374151;
              }
              code {
                background: #374151;
                color: #67e8f9;
                padding: 2px 5px;
                border-radius: 3px;
              }
              h1 { color: #a5f3fc; margin-top: 2em; }
              h2 { color: #67e8f9; margin-top: 1.5em; }
              h3 { color: #22d3ee; margin-top: 1em; }
              ul, ol { margin-left: 20px; color: #d1d5db; }
              a { color: #22d3ee; }
              a:hover { color: #67e8f9; text-decoration: underline; }
            </style>
          </head>
          <body>
            <pre>${content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
          </body>
        </html>
      `);
      newWindow.document.close();
    }
  };

  const renderMarkdown = (text: string) => {
    // Simple markdown rendering
    const lines = text.split('\n');
    return lines.map((line, index) => {
      // Headers
      if (line.startsWith('### ')) {
        return <h3 key={index} className="text-lg font-semibold mt-3 mb-2 text-cyan-400">{line.slice(4)}</h3>;
      }
      if (line.startsWith('## ')) {
        return <h2 key={index} className="text-xl font-bold mt-4 mb-2 text-cyan-300">{line.slice(3)}</h2>;
      }
      if (line.startsWith('# ')) {
        return <h1 key={index} className="text-2xl font-bold mt-4 mb-3 text-cyan-200">{line.slice(2)}</h1>;
      }

      // Lists
      if (line.match(/^\d+\./)) {
        return <li key={index} className="ml-6 list-decimal text-gray-300">{line.replace(/^\d+\.\s*/, '')}</li>;
      }
      if (line.startsWith('- ')) {
        return <li key={index} className="ml-6 list-disc text-gray-300">{line.slice(2)}</li>;
      }

      // Links
      if (line.includes('http')) {
        const parts = line.split(' ');
        return (
          <p key={index} className="my-1 text-gray-300">
            {parts.map((part, i) => {
              if (part.startsWith('http')) {
                return (
                  <a key={i} href={part} target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-cyan-300 hover:underline">
                    {part}
                  </a>
                );
              }
              return <span key={i}> {part} </span>;
            })}
          </p>
        );
      }

      // Regular text
      if (line.trim()) {
        return <p key={index} className="my-1 text-gray-300">{line}</p>;
      }

      return <br key={index} />;
    });
  };

  return (
    <Card className="fixed inset-4 z-50 flex flex-col bg-gray-900 shadow-2xl border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center gap-3">
          <FileText className="h-5 w-5 text-cyan-400" />
          <h2 className="text-lg font-semibold text-gray-100">{filename}</h2>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={handleOpenInNewTab}
            className="gap-2"
          >
            <ExternalLink className="h-4 w-4" />
            New Tab
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={handleCopy}
            className="gap-2"
          >
            {copied ? (
              <>
                <CheckCircle className="h-4 w-4 text-green-600" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="h-4 w-4" />
                Copy
              </>
            )}
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={handleDownload}
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            Download
          </Button>

          <Button
            size="icon"
            variant="ghost"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1 p-6 bg-gray-900">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
          </div>
        ) : (
          <div className="prose prose-invert max-w-none text-gray-200">
            {renderMarkdown(content)}
          </div>
        )}
      </ScrollArea>
    </Card>
  );
};

export default FileViewer;