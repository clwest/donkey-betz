import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MagnifyingGlassIcon,
  SparklesIcon,
  CpuChipIcon,
  TagIcon,
  CheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import type { Agent } from '../../services/agent-orchestra.service';
import { Logger } from '../../utils/logger';

interface AgentSelectorProps {
  agents: Agent[];
  selectedAgent: Agent | null;
  onAgentSelect: (agent: Agent | null) => void;
  loading?: boolean;
  error?: string | null;
  taskDescription?: string;
  onSuggestAgents?: (taskDescription: string) => Promise<Agent[]>;
  className?: string;
  compact?: boolean;
}

export const AgentSelector: React.FC<AgentSelectorProps> = ({
  agents,
  selectedAgent,
  onAgentSelect,
  loading = false,
  error = null,
  taskDescription = '',
  onSuggestAgents,
  className = '',
  compact = false
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSpecialization, setSelectedSpecialization] = useState<string>('');
  const [suggestions, setSuggestions] = useState<Agent[]>([]);
  const [suggestionLoading, setSuggestionLoading] = useState(false);

  // Filter and search agents
  const filteredAgents = useMemo(() => {
    let filtered = agents;

    // Filter by specialization
    if (selectedSpecialization) {
      filtered = filtered.filter(agent => 
        (agent.specialization?.toLowerCase() || '') === selectedSpecialization.toLowerCase()
      );
    }

    // Filter by search term
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(agent =>
        (agent.name?.toLowerCase() || '').includes(searchLower) ||
        (agent.description?.toLowerCase() || '').includes(searchLower) ||
        (agent.specialization?.toLowerCase() || '').includes(searchLower) ||
        (agent.capabilities || []).some(cap => (typeof cap === 'string' ? cap.toLowerCase() : '').includes(searchLower))
      );
    }

    return filtered;
  }, [agents, searchTerm, selectedSpecialization]);

  // Get unique specializations
  const specializations = useMemo(() => {
    const specs = agents.map(agent => agent.specialization).filter(Boolean);
    return Array.from(new Set(specs)).sort();
  }, [agents]);

  // Handle agent suggestion
  const handleSuggestAgents = async () => {
    if (!onSuggestAgents || !taskDescription.trim()) {
      return;
    }

    setSuggestionLoading(true);
    try {
      const suggestedAgents = await onSuggestAgents(taskDescription);
      setSuggestions(suggestedAgents);
      Logger.debug('Agent Selector', `Found ${suggestedAgents.length} suggestions`);
    } catch (error) {
      Logger.error('Agent Selector', { message: 'Failed to get suggestions', error });
    } finally {
      setSuggestionLoading(false);
    }
  };

  // Clear suggestions when task description changes
  React.useEffect(() => {
    if (suggestions.length > 0) {
      setSuggestions([]);
    }
  }, [taskDescription]);

  const AgentCard: React.FC<{ agent: Agent; isSelected: boolean; isSuggested: boolean }> = ({ 
    agent, 
    isSelected, 
    isSuggested 
  }) => (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 1.03, y: -4 }}
      whileTap={{ scale: 0.98 }}
      className={`bg-card relative overflow-hidden cursor-pointer group ${compact ? 'p-4' : 'p-5'}`}
      style={{
        border: `2px solid ${
          isSelected ? 'hsl(var(--muted))' :
          isSuggested ? 'hsl(var(--muted))' :
          'hsl(var(--muted))'
        }`,
        boxShadow: isSelected ? '0 0 25px rgba(0, 255, 255, 0.4)' :
                   isSuggested ? '0 0 20px rgba(157, 78, 221, 0.3)' :
                   '0 0 10px rgba(0, 0, 0, 0.1)'
      }}
      onClick={() => onAgentSelect(isSelected ? null : agent)}
    >
      {/* Gaming border glow effect */}
      <div className="bg-card"></div>
      
      {/* Status indicators */}
      <div className={`absolute top-0 left-0 w-full h-1 ${
        isSelected ? 'bg-gradient-to-r from-cyan-400 to-blue-400 animate-pulse' :
        isSuggested ? 'bg-gradient-to-r from-purple-400 to-pink-400' :
        'bg-gradient-to-r from-gray-400 to-gray-600'
      } opacity-70`}></div>

      {isSelected && (
        <div className="absolute -top-2 -right-2 z-10">
          <div className="rounded-full p-2 animate-pulse" style={{
            background: 'hsl(var(--muted))',
            boxShadow: '0 0 15px rgba(0, 255, 255, 0.8)'
          }}>
            <CheckIcon className="h-3 w-3" style={{ color: 'hsl(var(--muted))' }} />
          </div>
        </div>
      )}

      {isSuggested && (
        <div className="absolute -top-2 -left-2 z-10">
          <div className="rounded-full p-2 animate-pulse" style={{
            background: 'hsl(var(--muted))',
            boxShadow: '0 0 15px rgba(157, 78, 221, 0.8)'
          }}>
            <SparklesIcon className="h-3 w-3" style={{ color: 'hsl(var(--muted))' }} />
          </div>
        </div>
      )}

      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h4 className={`font-black uppercase tracking-wider ${compact ? 'text-sm' : 'text-base'}`} style={{
              color: 'hsl(var(--muted))',
              fontFamily: 'var(--font-mono)',
              textShadow: isSelected ? '0 0 10px rgba(0, 255, 255, 0.5)' : 'none'
            }}>
              {agent.name}
            </h4>
            <div className="flex items-center mt-2 gap-2">
              <TagIcon className="h-3 w-3" style={{ 
                color: 'hsl(var(--muted))',
                filter: 'drop-shadow(0 0 5px rgba(157, 78, 221, 0.6))'
              }} />
              <span className="text-xs font-bold uppercase tracking-wider" style={{
                color: 'hsl(var(--muted))',
                fontFamily: 'var(--font-mono)'
              }}>
                {agent.specialization}
              </span>
            </div>
          </div>
          <div className="relative">
            <CpuChipIcon className={`${compact ? 'h-5 w-5' : 'h-6 w-6'}`} style={{ 
              color: isSelected ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
              filter: isSelected ? 'drop-shadow(0 0 8px rgba(0, 255, 255, 0.8))' : 'none'
            }} />
            {isSelected && (
              <div className="absolute inset-0 rounded-full bg-cyan-400/20 animate-ping"></div>
            )}
          </div>
        </div>

        {!compact && (
          <>
            <p className="text-sm line-clamp-2" style={{ 
              color: 'hsl(var(--muted))',
              fontFamily: 'var(--font-mono)'
            }}>
              {agent.description}
            </p>

            <div className="flex flex-wrap gap-2">
              {agent.capabilities.slice(0, 3).map((capability) => (
                <span
                  key={capability}
                  className="inline-block px-2 py-1 text-xs font-semibold rounded border transition-all duration-200 hover:scale-105"
                  style={{
                    background: 'rgba(0, 255, 255, 0.1)',
                    border: '1px solid hsl(var(--muted))',
                    color: 'hsl(var(--muted))',
                    fontFamily: 'var(--font-mono)',
                    textTransform: 'uppercase',
                    boxShadow: '0 0 5px rgba(0, 255, 255, 0.2)'
                  }}
                >
                  {capability}
                </span>
              ))}
              {agent.capabilities.length > 3 && (
                <span className="inline-block px-2 py-1 text-xs font-semibold rounded border" style={{
                  background: 'rgba(124, 124, 138, 0.1)',
                  border: '1px solid hsl(var(--muted))',
                  color: 'hsl(var(--muted))',
                  fontFamily: 'var(--font-mono)',
                  textTransform: 'uppercase'
                }}>
                  +{agent.capabilities.length - 3} MORE
                </span>
              )}
            </div>

            <div className="flex items-center justify-between text-xs font-semibold" style={{
              color: 'hsl(var(--muted))',
              fontFamily: 'var(--font-mono)'
            }}>
              <span className="uppercase tracking-wider">
                {agent.llm_provider} · {agent.llm_model}
              </span>
            </div>
          </>
        )}
      </div>
    </motion.div>
  );

  if (loading) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-muted/20 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="border border-border rounded-lg p-4">
                <div className="h-4 bg-muted/20 rounded mb-2"></div>
                <div className="h-3 bg-muted/20 rounded mb-4"></div>
                <div className="flex space-x-2">
                  <div className="h-6 bg-muted/20 rounded w-16"></div>
                  <div className="h-6 bg-muted/20 rounded w-20"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center">
          <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-2" />
          <div>
            <h3 className="text-sm font-medium text-red-800">Failed to load agents</h3>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header and Controls - Cyberpunk Style */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CpuChipIcon className="h-6 w-6" style={{ 
              color: 'hsl(var(--muted))',
              filter: 'drop-shadow(0 0 10px rgba(0, 255, 255, 0.7))'
            }} />
            <h3 className="text-lg font-black uppercase tracking-wider" style={{
              color: 'hsl(var(--muted))',
              fontFamily: 'var(--font-mono)',
              textShadow: '0 0 15px rgba(0, 255, 255, 0.5)'
            }}>
              Select Neural Agent
            </h3>
          </div>
          
          {onSuggestAgents && taskDescription.trim() && (
            <div className="relative">
              <div className={`absolute inset-0 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 opacity-30 blur-sm ${
                suggestionLoading ? 'animate-pulse' : ''
              }`}></div>
              <button
                onClick={handleSuggestAgents}
                disabled={suggestionLoading}
                className="relative px-4 py-2 rounded-lg font-bold uppercase tracking-wider text-sm transition-all duration-300 hover:transform hover:scale-105"
                style={{
                  background: 'hsl(var(--muted))',
                  border: '2px solid hsl(var(--muted))',
                  color: 'hsl(var(--muted))',
                  boxShadow: '0 0 15px rgba(157, 78, 221, 0.3)',
                  textShadow: '0 0 10px rgba(157, 78, 221, 0.5)'
                }}
              >
                <div className="flex items-center gap-2">
                  {suggestionLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2" style={{ borderColor: 'hsl(var(--muted))' }} />
                  ) : (
                    <SparklesIcon className="h-4 w-4" style={{ 
                      filter: 'drop-shadow(0 0 8px rgba(157, 78, 221, 0.8))'
                    }} />
                  )}
                  AI SUGGEST
                </div>
              </button>
            </div>
          )}
        </div>

        {/* Search and Filter - Cyberpunk Interface */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4" style={{ 
              color: 'hsl(var(--muted))',
              filter: 'drop-shadow(0 0 5px rgba(0, 255, 255, 0.6))'
            }} />
            <input
              type="text"
              placeholder="SCAN NEURAL NETWORK FOR AGENTS..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 rounded-lg transition-all duration-300 focus:outline-none"
              style={{
                background: 'hsl(var(--muted))',
                border: `2px solid ${searchTerm ? 'hsl(var(--muted))' : 'hsl(var(--muted))'}`,
                color: 'hsl(var(--muted))',
                fontFamily: 'var(--font-mono)',
                fontSize: '14px',
                boxShadow: searchTerm ? '0 0 15px rgba(0, 255, 255, 0.2)' : 'none',
                textTransform: 'uppercase'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'hsl(var(--muted))';
                e.target.style.boxShadow = '0 0 20px rgba(0, 255, 255, 0.3)';
              }}
              onBlur={(e) => {
                if (!searchTerm) {
                  e.target.style.borderColor = 'hsl(var(--muted))';
                  e.target.style.boxShadow = 'none';
                }
              }}
            />
          </div>

          <div className="relative">
            <select
              value={selectedSpecialization}
              onChange={(e) => setSelectedSpecialization(e.target.value)}
              className="px-4 py-3 rounded-lg min-w-[180px] transition-all duration-300 focus:outline-none appearance-none cursor-pointer"
              style={{
                background: 'hsl(var(--muted))',
                border: `2px solid ${selectedSpecialization ? 'hsl(var(--muted))' : 'hsl(var(--muted))'}`,
                color: 'hsl(var(--muted))',
                fontFamily: 'var(--font-mono)',
                fontSize: '14px',
                fontWeight: 'bold',
                textTransform: 'uppercase',
                boxShadow: selectedSpecialization ? '0 0 15px rgba(157, 78, 221, 0.2)' : 'none'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'hsl(var(--muted))';
                e.target.style.boxShadow = '0 0 20px rgba(157, 78, 221, 0.3)';
              }}
              onBlur={(e) => {
                if (!selectedSpecialization) {
                  e.target.style.borderColor = 'hsl(var(--muted))';
                  e.target.style.boxShadow = 'none';
                }
              }}
            >
              <option value="">ALL SPECIALIZATIONS</option>
              {specializations.map((spec) => (
                <option key={spec} value={spec}>
                  {spec.toUpperCase()}
                </option>
              ))}
            </select>
            {/* Custom dropdown arrow */}
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
              <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent" style={{
                borderTopColor: 'hsl(var(--muted))'
              }}></div>
            </div>
          </div>
        </div>

        {/* Selection Summary - Cyberpunk Style */}
        {selectedAgent && (
          <div className="relative p-4 rounded-lg border-2 border-cyan-400 transition-all duration-300" style={{
            background: 'rgba(0, 255, 255, 0.1)',
            boxShadow: '0 0 20px rgba(0, 255, 255, 0.2)'
          }}>
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-400 to-blue-400 opacity-70 animate-pulse"></div>
            <p className="text-sm font-bold uppercase tracking-wider" style={{
              color: 'hsl(var(--muted))',
              fontFamily: 'var(--font-mono)',
              textShadow: '0 0 10px rgba(0, 255, 255, 0.5)'
            }}>
              <span style={{ color: 'hsl(var(--muted))' }}>AGENT SELECTED:</span> {selectedAgent.name} 
              <span style={{ color: 'hsl(var(--muted))' }}> [{selectedAgent.specialization}]</span>
            </p>
          </div>
        )}
      </div>

      {/* Suggestions - AI Recommendation Section */}
      {suggestions.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <SparklesIcon className="h-5 w-5" style={{ 
              color: 'hsl(var(--muted))',
              filter: 'drop-shadow(0 0 10px rgba(157, 78, 221, 0.8))'
            }} />
            <h4 className="text-base font-black uppercase tracking-wider" style={{
              color: 'hsl(var(--muted))',
              fontFamily: 'var(--font-mono)',
              textShadow: '0 0 15px rgba(157, 78, 221, 0.5)'
            }}>
              AI Recommendations
            </h4>
            <div className="px-2 py-1 rounded text-xs font-bold" style={{
              background: 'rgba(157, 78, 221, 0.2)',
              color: 'hsl(var(--muted))',
              fontFamily: 'var(--font-mono)'
            }}>
              {suggestions.length} FOUND
            </div>
          </div>
          <div className={`grid gap-4 ${compact ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-2'}`}>
            {suggestions.map((agent) => (
              <AgentCard
                key={`suggestion-${agent.id}`}
                agent={agent}
                isSelected={selectedAgent?.id === agent.id}
                isSuggested={true}
              />
            ))}
          </div>
        </div>
      )}

      {/* Agents Grid - Neural Network Display */}
      <div className="space-y-4">
        {filteredAgents.length === 0 ? (
          <div className="text-center py-12">
            <div className="relative mb-6">
              <CpuChipIcon className="h-16 w-16 mx-auto" style={{ 
                color: 'hsl(var(--muted))',
                filter: 'drop-shadow(0 0 10px rgba(124, 124, 138, 0.3))'
              }} />
              <div className="absolute inset-0 rounded-full bg-gray-400/20 animate-ping"></div>
            </div>
            <p className="text-lg font-bold uppercase tracking-wider mb-2" style={{
              color: 'hsl(var(--muted))',
              fontFamily: 'var(--font-mono)'
            }}>
              {searchTerm || selectedSpecialization 
                ? 'NO NEURAL MATCHES FOUND'
                : 'NEURAL NETWORK OFFLINE'
              }
            </p>
            <p className="text-sm" style={{
              color: 'hsl(var(--muted))',
              fontFamily: 'var(--font-mono)'
            }}>
              {searchTerm || selectedSpecialization 
                ? 'ADJUST SCAN PARAMETERS AND RETRY'
                : 'NO AGENTS AVAILABLE IN NETWORK'
              }
            </p>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-3">
              <CpuChipIcon className="h-5 w-5" style={{ 
                color: 'hsl(var(--muted))',
                filter: 'drop-shadow(0 0 10px rgba(57, 255, 20, 0.7))'
              }} />
              <h4 className="text-base font-black uppercase tracking-wider" style={{
                color: 'hsl(var(--muted))',
                fontFamily: 'var(--font-mono)',
                textShadow: '0 0 15px rgba(57, 255, 20, 0.5)'
              }}>
                Available Neural Agents
              </h4>
              <div className="px-3 py-1 rounded-lg border" style={{
                background: 'rgba(57, 255, 20, 0.1)',
                border: '1px solid hsl(var(--muted))',
                color: 'hsl(var(--muted))',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                fontWeight: 'bold'
              }}>
                {filteredAgents.length.toString().padStart(2, '0')} ONLINE
              </div>
            </div>
            <motion.div 
              layout
              className={`grid gap-4 ${
                compact 
                  ? 'grid-cols-1 sm:grid-cols-2' 
                  : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
              }`}
            >
              <AnimatePresence>
                {filteredAgents.map((agent) => (
                  <AgentCard
                    key={agent.id}
                    agent={agent}
                    isSelected={selectedAgent?.id === agent.id}
                    isSuggested={suggestions.some(s => s.id === agent.id)}
                  />
                ))}
              </AnimatePresence>
            </motion.div>
          </>
        )}
      </div>
    </div>
  );
};