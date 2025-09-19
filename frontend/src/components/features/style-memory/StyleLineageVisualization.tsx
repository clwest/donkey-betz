import { useEffect, useRef } from 'react';
import { XMarkIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { Button } from '../../common/Button';
import { Card } from '../../common/Card';
import { useStyleMemoryStore } from '../../../store/styleMemoryStore';

export function StyleLineageVisualization() {
  const svgRef = useRef<SVGSVGElement>(null);
  const {
    currentLineage,
    showLineage,
    toggleLineage,
    generateSimilar,
  } = useStyleMemoryStore();

  useEffect(() => {
    if (currentLineage && svgRef.current) {
      renderLineageTree();
    }
  }, [currentLineage]);

  const renderLineageTree = () => {
    if (!currentLineage || !svgRef.current) return;

    const svg = svgRef.current;
    const width = svg.clientWidth;
    const height = svg.clientHeight;

    // Clear previous content
    svg.innerHTML = '';

    // Simple tree layout
    const nodeRadius = 30;
    const levelHeight = 80;
    const nodeSpacing = 100;

    // Calculate positions
    const allNodes = [
      ...currentLineage.ancestors.map(a => ({ ...a, type: 'ancestor' })),
      { content_id: currentLineage.content.id, generation: 0, type: 'current', similarity: 1.0 },
      ...currentLineage.descendants.map(d => ({ ...d, type: 'descendant' })),
    ];

    // Group by generation
    const generations = allNodes.reduce((acc, node) => {
      const gen = node.generation;
      if (!acc[gen]) acc[gen] = [];
      acc[gen].push(node);
      return acc;
    }, {} as Record<number, any[]>);

    const minGen = Math.min(...Object.keys(generations).map(Number));
    const maxGen = Math.max(...Object.keys(generations).map(Number));

    // Position nodes
    const positions: Record<string, { x: number; y: number; node: any }> = {};

    Object.entries(generations).forEach(([gen, nodes]) => {
      const generation = parseInt(gen);
      const y = height / 2 + (generation - 0) * levelHeight;
      const totalWidth = (nodes.length - 1) * nodeSpacing;
      const startX = (width - totalWidth) / 2;

      nodes.forEach((node, index) => {
        positions[node.content_id] = {
          x: startX + index * nodeSpacing,
          y,
          node,
        };
      });
    });

    // Draw connections
    Object.values(positions).forEach(({ x, y, node }) => {
      if (node.type === 'descendant') {
        // Find parent (should be current or another descendant with lower generation)
        const parentGen = node.generation - 1;
        const possibleParents = Object.values(positions).filter(p => 
          p.node.generation === parentGen
        );
        
        if (possibleParents.length > 0) {
          const parent = possibleParents[0]; // Simplified - in reality you'd track actual parent relationships
          
          // Draw line
          const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
          line.setAttribute('x1', parent.x.toString());
          line.setAttribute('y1', parent.y.toString());
          line.setAttribute('x2', x.toString());
          line.setAttribute('y2', y.toString());
          line.setAttribute('stroke', '#8b5cf6');
          line.setAttribute('stroke-width', '2');
          line.setAttribute('stroke-opacity', '0.6');
          svg.appendChild(line);
        }
      }
    });

    // Draw nodes
    Object.values(positions).forEach(({ x, y, node }) => {
      const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      group.setAttribute('transform', `translate(${x}, ${y})`);
      group.setAttribute('class', 'cursor-pointer');

      // Node circle
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('r', nodeRadius.toString());
      circle.setAttribute('stroke', getNodeColor(node.type));
      circle.setAttribute('stroke-width', node.type === 'current' ? '3' : '2');
      circle.setAttribute('fill', 'rgba(0, 0, 0, 0.8)');
      circle.setAttribute('class', 'hover:fill-opacity-60 transition-all duration-200');

      // Node label
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dy', '0.35em');
      text.setAttribute('fill', 'white');
      text.setAttribute('font-size', '10');
      text.setAttribute('font-weight', node.type === 'current' ? 'bold' : 'normal');
      text.textContent = `Gen ${node.generation}`;

      // Similarity indicator
      if (node.similarity !== undefined && node.type !== 'current') {
        const similarityText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        similarityText.setAttribute('text-anchor', 'middle');
        similarityText.setAttribute('dy', '1.5em');
        similarityText.setAttribute('fill', '#9ca3af');
        similarityText.setAttribute('font-size', '8');
        similarityText.textContent = `${Math.round(node.similarity * 100)}%`;
        group.appendChild(similarityText);
      }

      group.appendChild(circle);
      group.appendChild(text);

      // Click handler
      group.addEventListener('click', () => {
        if (node.type !== 'current') {
          // Navigate to or preview this image
          console.log('View image:', node.content_id);
        }
      });

      svg.appendChild(group);
    });
  };

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'current': return '#8b5cf6';
      case 'ancestor': return '#3b82f6';
      case 'descendant': return '#10b981';
      default: return '#6b7280';
    }
  };

  const handleGenerateVariation = async (variationType: 'subtle' | 'moderate' | 'creative') => {
    if (currentLineage) {
      await generateSimilar(currentLineage.content.id, variationType);
    }
  };

  if (!showLineage || !currentLineage) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm">
      <div className="min-h-full flex items-center justify-center p-4">
        <Card className="w-full max-w-4xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-white/10">
            <div>
              <h2 className="text-xl font-bold text-foreground">Style Lineage</h2>
              <p className="text-muted-foreground">Family tree of your image evolution</p>
            </div>
            <Button variant="ghost" onClick={toggleLineage}>
              <XMarkIcon className="h-5 w-5" />
            </Button>
          </div>

          {/* Visualization */}
          <div className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full border-2 border-blue-500" />
                  <span className="text-muted-foreground">Ancestors</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full border-2 border-primary-500" />
                  <span className="text-muted-foreground">Current</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full border-2 border-green-500" />
                  <span className="text-muted-foreground">Descendants</span>
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => handleGenerateVariation('subtle')}
                >
                  <ArrowPathIcon className="h-4 w-4" />
                  Subtle
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => handleGenerateVariation('moderate')}
                >
                  <ArrowPathIcon className="h-4 w-4" />
                  Moderate
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => handleGenerateVariation('creative')}
                >
                  <ArrowPathIcon className="h-4 w-4" />
                  Creative
                </Button>
              </div>
            </div>

            <div className="bg-background rounded-lg p-4">
              <svg
                ref={svgRef}
                className="w-full"
                style={{ height: '400px' }}
                viewBox="0 0 800 400"
              />
            </div>

            {/* Stats */}
            <div className="mt-4 grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-foreground">{currentLineage.ancestors.length}</div>
                <div className="text-sm text-muted-foreground">Ancestors</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-foreground">{currentLineage.descendants.length}</div>
                <div className="text-sm text-muted-foreground">Descendants</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-foreground">{currentLineage.total_generations}</div>
                <div className="text-sm text-muted-foreground">Total Generations</div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}