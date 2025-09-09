import { 
  DocumentTextIcon,
  MicrophoneIcon,
  PhotoIcon,
  ChartBarIcon,
  CpuChipIcon,
  SparklesIcon,
  VideoCameraIcon,
  PencilIcon,
  ArrowsRightLeftIcon,
  TagIcon,
  ShareIcon,
  BookOpenIcon,
  EnvelopeIcon,
  PresentationChartBarIcon,
  CloudArrowUpIcon,
  GlobeAltIcon,
} from '@heroicons/react/24/outline';

const nodeCategories = {
  input: {
    label: 'Inputs',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/20',
    nodes: [
      { type: 'research-input', name: 'Research', icon: DocumentTextIcon },
      { type: 'voice-input', name: 'Voice', icon: MicrophoneIcon },
      { type: 'text-input', name: 'Text', icon: DocumentTextIcon },
      { type: 'image-input', name: 'Image', icon: PhotoIcon },
      { type: 'data-input', name: 'Data', icon: ChartBarIcon },
    ],
  },
  process: {
    label: 'Process',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/20',
    nodes: [
      { type: 'content-generation', name: 'Generate', icon: SparklesIcon },
      { type: 'image-generation', name: 'Image Gen', icon: PhotoIcon },
      { type: 'video-generation', name: 'Video Gen', icon: VideoCameraIcon },
      { type: 'content-enhancement', name: 'Enhance', icon: PencilIcon },
      { type: 'format-conversion', name: 'Convert', icon: ArrowsRightLeftIcon },
      { type: 'content-optimization', name: 'Optimize', icon: CpuChipIcon },
      { type: 'summarization', name: 'Summarize', icon: DocumentTextIcon },
      { type: 'tagging', name: 'Tag', icon: TagIcon },
    ],
  },
  output: {
    label: 'Outputs',
    color: 'text-green-400',
    bgColor: 'bg-green-500/20',
    nodes: [
      { type: 'social-media', name: 'Social', icon: ShareIcon },
      { type: 'blog-publishing', name: 'Blog', icon: GlobeAltIcon },
      { type: 'ebook-creation', name: 'eBook', icon: BookOpenIcon },
      { type: 'email-campaigns', name: 'Email', icon: EnvelopeIcon },
      { type: 'presentations', name: 'Slides', icon: PresentationChartBarIcon },
      { type: 'storage', name: 'Save', icon: CloudArrowUpIcon },
    ],
  },
};

export function WorkflowNodeLibrary() {
  const onDragStart = (event: React.DragEvent, nodeType: any, category: string) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify({ ...nodeType, category }));
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div className="w-64 glass-dark border-r border-white/5 p-4 overflow-y-auto">
      <h3 className="text-white font-semibold mb-4">Node Library</h3>
      
      {Object.entries(nodeCategories).map(([category, { label, color, bgColor, nodes }]) => (
        <div key={category} className="mb-6">
          <h4 className={`text-sm font-medium ${color} mb-3`}>{label}</h4>
          <div className="space-y-2">
            {nodes.map((node) => (
              <div
                key={node.type}
                draggable
                onDragStart={(e) => onDragStart(e, node, category)}
                className={`flex items-center gap-2 px-3 py-2 ${bgColor} border border-white/10 rounded-lg cursor-move hover:bg-white/10 transition-colors`}
              >
                <node.icon className="h-4 w-4" />
                <span className="text-sm text-white">{node.name}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}