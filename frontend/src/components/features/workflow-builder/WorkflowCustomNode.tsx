import { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import clsx from 'clsx';

export const WorkflowCustomNode = memo(({ data, selected }: NodeProps) => {
  const categoryColors = {
    input: {
      bg: 'bg-blue-500/20',
      border: 'border-blue-500/50',
      handle: 'bg-blue-500',
    },
    process: {
      bg: 'bg-purple-500/20',
      border: 'border-purple-500/50',
      handle: 'bg-purple-500',
    },
    output: {
      bg: 'bg-green-500/20',
      border: 'border-green-500/50',
      handle: 'bg-green-500',
    },
  };

  const colors = categoryColors[data.category as keyof typeof categoryColors] || categoryColors.process;

  return (
    <div
      className={clsx(
        'px-4 py-3 rounded-lg border backdrop-blur-xl transition-all',
        colors.bg,
        colors.border,
        selected && 'ring-2 ring-primary-500 ring-offset-2 ring-offset-dark-950'
      )}
    >
      {data.category !== 'input' && (
        <Handle
          type="target"
          position={Position.Top}
          className={clsx('!w-3 !h-3 !border-2 !border-white', `!${colors.handle}`)}
        />
      )}
      
      <div className="flex items-center gap-2">
        <div className={clsx('w-2 h-2 rounded-full', colors.handle)} />
        <span className="text-sm font-medium text-white">{data.label}</span>
      </div>
      
      {data.config?.prompt && (
        <div className="mt-2 text-xs text-gray-400 truncate max-w-[150px]">
          {data.config.prompt}
        </div>
      )}
      
      {data.category !== 'output' && (
        <Handle
          type="source"
          position={Position.Bottom}
          className={clsx('!w-3 !h-3 !border-2 !border-white', `!${colors.handle}`)}
        />
      )}
    </div>
  );
});

WorkflowCustomNode.displayName = 'WorkflowCustomNode';