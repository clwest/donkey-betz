import { useState } from 'react';
import { UnifiedAIAssistant } from './UnifiedAIAssistant';
import { MessageCircle, X } from 'lucide-react';

/**
 * Safe wrapper for UnifiedAIAssistant that prevents UI blocking
 * Shows as a small floating button that opens the chat widget on demand
 */
export function SafeAIAssistant() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating toggle button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-primary rounded-full shadow-lg hover:scale-110 transition-all duration-200 z-40 flex items-center justify-center group"
          aria-label="Open AI Assistant"
        >
          <MessageCircle className="w-6 h-6 text-white" />
          <span className="absolute -top-8 right-0 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            AI Assistant
          </span>
        </button>
      )}

      {/* Chat widget container */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-[400px] h-[600px] max-h-[80vh] z-50 animate-in slide-in-from-bottom-5 duration-300">
          {/* Close button */}
          <button
            onClick={() => setIsOpen(false)}
            className="absolute -top-2 -right-2 w-8 h-8 bg-red-500 rounded-full flex items-center justify-center hover:bg-red-600 transition-colors z-10 shadow-md"
            aria-label="Close AI Assistant"
          >
            <X className="w-4 h-4 text-white" />
          </button>

          {/* AI Assistant component */}
          <div className="h-full rounded-lg shadow-2xl overflow-hidden border border-gray-700">
            <UnifiedAIAssistant />
          </div>
        </div>
      )}
    </>
  );
}

export default SafeAIAssistant;