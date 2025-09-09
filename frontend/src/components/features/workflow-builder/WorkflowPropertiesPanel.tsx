import type { Node } from 'reactflow';
import { Button } from '../../common/Button';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface WorkflowPropertiesPanelProps {
  node: Node | null;
}

export function WorkflowPropertiesPanel({ node }: WorkflowPropertiesPanelProps) {
  if (!node) return null;

  return (
    <div className="w-80 glass-dark border-l border-white/5 p-4 overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-semibold">Properties</h3>
        <button className="text-gray-400 hover:text-white">
          <XMarkIcon className="h-4 w-4" />
        </button>
      </div>

      <div className="space-y-4">
        {/* Node Info */}
        <div>
          <label className="text-sm text-gray-400">Node Type</label>
          <p className="text-white font-medium">{node.data.label}</p>
        </div>

        {/* Node-specific configuration */}
        {node.data.type === 'content-generation' && (
          <>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Prompt</label>
              <textarea
                className="input min-h-[100px]"
                placeholder="Enter generation prompt..."
                defaultValue={node.data.config?.prompt}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Model</label>
              <select className="input">
                <option>GPT-4</option>
                <option>GPT-3.5</option>
                <option>Claude</option>
                <option>Gemini</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Max Length</label>
              <input
                type="number"
                className="input"
                placeholder="1500"
                defaultValue={node.data.config?.length}
              />
            </div>
          </>
        )}

        {node.data.type === 'image-generation' && (
          <>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Style</label>
              <select className="input">
                <option>Photorealistic</option>
                <option>Digital Art</option>
                <option>Anime</option>
                <option>Oil Painting</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Resolution</label>
              <select className="input">
                <option>1024x1024</option>
                <option>1024x1792</option>
                <option>1792x1024</option>
              </select>
            </div>
          </>
        )}

        {node.data.type === 'social-media' && (
          <>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Platforms</label>
              <div className="space-y-2">
                {['Twitter', 'LinkedIn', 'Instagram', 'Facebook'].map((platform) => (
                  <label key={platform} className="flex items-center gap-2">
                    <input type="checkbox" className="rounded border-dark-700" />
                    <span className="text-sm text-white">{platform}</span>
                  </label>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Save button */}
        <Button className="w-full" size="sm">
          Apply Changes
        </Button>
      </div>
    </div>
  );
}