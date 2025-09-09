import React from 'react';
import { Upload, FileText, Sparkles, BookOpen, Image, Mic, Video } from 'lucide-react';

interface EmptyStateProps {
  type: 'knowledge' | 'gallery' | 'content' | 'memories' | 'conversations';
  onAction?: () => void;
}

const EmptyState: React.FC<EmptyStateProps> = ({ type, onAction }) => {
  const getEmptyStateContent = () => {
    switch (type) {
      case 'knowledge':
        return {
          icon: <Upload className="w-16 h-16 text-gray-400 dark:text-gray-600" />,
          title: "Build Your Knowledge Base",
          description: "Upload documents, notes, or any content you want the AI to learn from. This personalizes your AI experience.",
          actionText: "Upload Your First Document",
          tips: [
            "Upload PDFs, Word docs, or text files",
            "Add your brand guidelines and style guides",
            "Include past content for AI to learn your voice",
            "Organize with categories and tags"
          ]
        };
        
      case 'gallery':
        return {
          icon: <Image className="w-16 h-16 text-gray-400 dark:text-gray-600" />,
          title: "Your Gallery is Empty",
          description: "Start generating amazing content to build your gallery. Every creation is automatically saved here.",
          actionText: "Create Your First Image",
          tips: [
            "Generate images with 50+ artistic styles",
            "Create videos from text or images",
            "Save your favorites for quick access",
            "Share your best creations publicly"
          ]
        };
        
      case 'content':
        return {
          icon: <FileText className="w-16 h-16 text-gray-400 dark:text-gray-600" />,
          title: "No Content Yet",
          description: "Create your first piece of content using AI. Choose from blogs, social posts, eBooks, and more.",
          actionText: "Generate Content",
          tips: [
            "Start with a blog post to test the waters",
            "Try social media posts for quick wins",
            "Create eBooks for comprehensive content",
            "Generate podcasts scripts with timestamps"
          ]
        };
        
      case 'memories':
        return {
          icon: <Sparkles className="w-16 h-16 text-gray-400 dark:text-gray-600" />,
          title: "No Memories Yet",
          description: "As you interact with the AI, it will remember your preferences and past conversations to provide better assistance.",
          actionText: "Start a Conversation",
          tips: [
            "Share your brand voice and tone",
            "Tell the AI about your goals",
            "Provide feedback on generated content",
            "Build context over time"
          ]
        };
        
      case 'conversations':
        return {
          icon: <Mic className="w-16 h-16 text-gray-400 dark:text-gray-600" />,
          title: "Start Your First Conversation",
          description: "Chat with your AI assistant about content ideas, get help with writing, or ask questions about the platform.",
          actionText: "Start Chatting",
          tips: [
            "Ask for content ideas and suggestions",
            "Get help improving your drafts",
            "Learn about platform features",
            "Request specific content formats"
          ]
        };
        
      default:
        return {
          icon: <BookOpen className="w-16 h-16 text-gray-400 dark:text-gray-600" />,
          title: "Get Started",
          description: "Begin your AI content creation journey.",
          actionText: "Get Started",
          tips: []
        };
    }
  };

  const content = getEmptyStateContent();

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="text-center max-w-md">
        {content.icon}
        <h3 className="mt-4 text-xl font-semibold text-gray-900 dark:text-white">
          {content.title}
        </h3>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          {content.description}
        </p>
        
        {onAction && (
          <button
            onClick={onAction}
            className="mt-6 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-medium hover:from-blue-600 hover:to-purple-600 transition-colors"
          >
            {content.actionText}
          </button>
        )}
        
        {content.tips.length > 0 && (
          <div className="mt-8 text-left">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Quick Tips:
            </h4>
            <ul className="space-y-2">
              {content.tips.map((tip, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {tip}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmptyState;