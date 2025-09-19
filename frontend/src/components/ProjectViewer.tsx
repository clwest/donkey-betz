import React, { useState, useEffect } from 'react';
import {
  X,
  Download,
  Code,
  FileText,
  Terminal,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  Rocket,
  DollarSign,
  Clock,
  User,
  ExternalLink
} from 'lucide-react';

interface ProjectFile {
  filename: string;
  content: string;
  file_type: string;
}

interface ProjectData {
  name: string;
  description: string;
  project_type: string;
  revenue_potential: string;
  strategy: {
    title: string;
    difficulty: string;
    time_to_implement: string;
    actionable_steps: string[];
  };
  files: ProjectFile[];
  advisor_insights: Array<{
    advisor: string;
    advice: string;
    recommendations: string[];
  }>;
  launch_command: string;
}

interface ProjectViewerProps {
  project: any;
  onClose: () => void;
}

const ProjectViewer: React.FC<ProjectViewerProps> = ({ project, onClose }) => {
  const [selectedFile, setSelectedFile] = useState<ProjectFile | null>(null);
  const [copied, setCopied] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    files: true,
    insights: true,
    setup: true
  });

  // Mock project files for now - will be replaced with API call
  const projectFiles: ProjectFile[] = project.files_created?.map((filename: string) => ({
    filename,
    content: `# ${filename}\n# Project: ${project.strategy?.title || project.name}\n# This file will contain the actual code from the backend`,
    file_type: filename.endsWith('.py') ? 'python' :
               filename.endsWith('.txt') ? 'text' :
               filename.endsWith('.md') ? 'markdown' : 'text'
  })) || [];

  useEffect(() => {
    if (projectFiles.length > 0 && !selectedFile) {
      setSelectedFile(projectFiles[0]);
    }
  }, [projectFiles]);

  const copyToClipboard = async (text: string) => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadProject = () => {
    // Create a zip file with all project files
    const projectData = {
      name: project.strategy?.title || project.name,
      files: projectFiles,
      metadata: {
        revenue_potential: project.revenue_potential,
        launch_command: project.launch_command,
        created_at: new Date().toISOString()
      }
    };

    const blob = new Blob([JSON.stringify(projectData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${project.project_id || 'project'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'python':
        return <Code className="w-4 h-4 text-blue-500" />;
      case 'markdown':
        return <FileText className="w-4 h-4 text-green-500" />;
      default:
        return <FileText className="w-4 h-4 text-muted-foreground" />;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-background rounded-xl max-w-7xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-6 flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-foreground mb-2">
              {project.strategy?.title || project.name || 'AI Project'}
            </h2>
            <p className="text-foreground/90">
              {project.strategy?.description || project.description || 'AI-powered application'}
            </p>

            <div className="flex flex-wrap gap-4 mt-4">
              <div className="flex items-center gap-2 bg-white/20 px-3 py-1 rounded-full">
                <DollarSign className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {project.revenue_potential || project.strategy?.potential_revenue || 'TBD'}
                </span>
              </div>
              <div className="flex items-center gap-2 bg-white/20 px-3 py-1 rounded-full">
                <Clock className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {project.strategy?.time_to_implement || '2-4 weeks'}
                </span>
              </div>
              <div className="flex items-center gap-2 bg-white/20 px-3 py-1 rounded-full">
                <span className="text-sm font-medium capitalize">
                  {project.strategy?.difficulty || 'intermediate'}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={downloadProject}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors flex items-center gap-2 text-foreground"
            >
              <Download className="w-4 h-4" />
              Download
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors text-foreground"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <div className="w-80 bg-card border-r border-gray-700 overflow-y-auto">
            {/* Files Section */}
            <div className="p-4">
              <button
                onClick={() => toggleSection('files')}
                className="flex items-center justify-between w-full text-left mb-3 hover:text-purple-400 transition-colors"
              >
                <h3 className="font-semibold text-foreground flex items-center gap-2">
                  <Code className="w-4 h-4" />
                  Project Files
                </h3>
                {expandedSections.files ?
                  <ChevronDown className="w-4 h-4 text-muted-foreground" /> :
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                }
              </button>

              {expandedSections.files && (
                <div className="space-y-1">
                  {projectFiles.map((file, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedFile(file)}
                      className={`w-full text-left px-3 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                        selectedFile?.filename === file.filename
                          ? 'bg-purple-600 text-foreground'
                          : 'hover:bg-gray-700 text-muted-foreground'
                      }`}
                    >
                      {getFileIcon(file.file_type)}
                      <span className="text-sm truncate">{file.filename}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Setup Instructions */}
            <div className="p-4 border-t border-gray-700">
              <button
                onClick={() => toggleSection('setup')}
                className="flex items-center justify-between w-full text-left mb-3 hover:text-purple-400 transition-colors"
              >
                <h3 className="font-semibold text-foreground flex items-center gap-2">
                  <Terminal className="w-4 h-4" />
                  Setup & Launch
                </h3>
                {expandedSections.setup ?
                  <ChevronDown className="w-4 h-4 text-muted-foreground" /> :
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                }
              </button>

              {expandedSections.setup && (
                <div className="space-y-3 text-sm">
                  <div className="bg-background rounded-lg p-3">
                    <p className="text-muted-foreground mb-1">Install dependencies:</p>
                    <code className="text-green-500">pip install -r requirements.txt</code>
                  </div>

                  <div className="bg-background rounded-lg p-3">
                    <p className="text-muted-foreground mb-1">Launch command:</p>
                    <code className="text-green-500">
                      {project.launch_command || 'python ai_app.py'}
                    </code>
                  </div>

                  <div className="bg-background rounded-lg p-3">
                    <p className="text-muted-foreground mb-1">Required:</p>
                    <ul className="text-muted-foreground text-xs space-y-1">
                      <li>• OpenAI API key in .env file</li>
                      <li>• Python 3.8+</li>
                    </ul>
                  </div>
                </div>
              )}
            </div>

            {/* Advisor Insights */}
            {project.advisor_insights && project.advisor_insights.length > 0 && (
              <div className="p-4 border-t border-gray-700">
                <button
                  onClick={() => toggleSection('insights')}
                  className="flex items-center justify-between w-full text-left mb-3 hover:text-purple-400 transition-colors"
                >
                  <h3 className="font-semibold text-foreground flex items-center gap-2">
                    <User className="w-4 h-4" />
                    Advisor Insights
                  </h3>
                  {expandedSections.insights ?
                    <ChevronDown className="w-4 h-4 text-muted-foreground" /> :
                    <ChevronRight className="w-4 h-4 text-muted-foreground" />
                  }
                </button>

                {expandedSections.insights && (
                  <div className="space-y-3">
                    {project.advisor_insights.slice(0, 2).map((insight: any, index: number) => (
                      <div key={index} className="bg-background rounded-lg p-3">
                        <p className="text-purple-400 font-medium text-sm mb-2">
                          {insight.advisor}
                        </p>
                        <p className="text-muted-foreground text-xs italic">
                          "{insight.advice}"
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Code Viewer */}
          <div className="flex-1 bg-gray-950 overflow-hidden flex flex-col">
            {selectedFile ? (
              <>
                <div className="bg-card px-6 py-3 flex items-center justify-between border-b border-gray-700">
                  <h3 className="text-foreground font-medium flex items-center gap-2">
                    {getFileIcon(selectedFile.file_type)}
                    {selectedFile.filename}
                  </h3>
                  <button
                    onClick={() => copyToClipboard(selectedFile.content)}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors flex items-center gap-2 text-sm text-muted-foreground"
                  >
                    {copied ? (
                      <>
                        <Check className="w-4 h-4 text-green-500" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        Copy
                      </>
                    )}
                  </button>
                </div>

                <div className="flex-1 overflow-auto p-6">
                  <pre className="text-muted-foreground text-sm font-mono">
                    <code>{selectedFile.content}</code>
                  </pre>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <Code className="w-12 h-12 mx-auto mb-3 text-gray-600" />
                  <p>Select a file to view its contents</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectViewer;