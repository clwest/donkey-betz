import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

export function WorkflowExecutionPanel() {
  const logs = [
    { node: 'Research Input', status: 'completed', message: 'Loaded 3 documents', time: '10:45:23' },
    { node: 'Content Generation', status: 'running', message: 'Generating content...', time: '10:45:25' },
    { node: 'Blog Publishing', status: 'pending', message: 'Waiting...', time: '' },
  ];

  return (
    <div className="absolute bottom-0 left-64 right-80 glass-dark border-t border-white/5 p-4 max-h-64 overflow-y-auto">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-white font-semibold">Execution Log</h4>
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 bg-yellow-400 rounded-full animate-pulse" />
          <span className="text-sm text-gray-400">Running...</span>
        </div>
      </div>
      
      <div className="space-y-2">
        {logs.map((log, index) => (
          <div key={index} className="flex items-start gap-3 text-sm">
            <span className="text-gray-500 font-mono text-xs">{log.time}</span>
            <div className="flex items-center gap-2 flex-1">
              {log.status === 'completed' && <CheckCircleIcon className="h-4 w-4 text-green-400" />}
              {log.status === 'running' && <div className="h-4 w-4 rounded-full border-2 border-yellow-400 border-t-transparent animate-spin" />}
              {log.status === 'pending' && <div className="h-4 w-4 rounded-full border-2 border-gray-600" />}
              <span className="text-white font-medium">{log.node}:</span>
              <span className="text-gray-400">{log.message}</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-3 border-t border-white/5">
        <div className="w-full bg-dark-800 rounded-full h-2">
          <div className="bg-gradient-primary h-2 rounded-full transition-all duration-500" style={{ width: '45%' }} />
        </div>
        <p className="text-xs text-gray-400 mt-2">45% complete</p>
      </div>
    </div>
  );
}