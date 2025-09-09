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
        agent.specialization.toLowerCase() === selectedSpecialization.toLowerCase()
      );
    }

    // Filter by search term
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(agent =>
        agent.name.toLowerCase().includes(searchLower) ||
        agent.description.toLowerCase().includes(searchLower) ||
        agent.specialization.toLowerCase().includes(searchLower) ||
        agent.capabilities.some(cap => cap.toLowerCase().includes(searchLower))
      );
    }

    return filtered;
  }, [agents, searchTerm, selectedSpecialization]);

  // Get unique specializations
  const specializations = useMemo(() => {
    const specs = agents.map(agent => agent.specialization);
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
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`
        relative p-4 border rounded-lg cursor-pointer transition-all duration-200
        ${isSelected 
          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' 
          : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
        }
        ${isSuggested ? 'ring-2 ring-purple-200 border-purple-300' : ''}
        ${compact ? 'p-3' : 'p-4'}
      `}
      onClick={() => onAgentSelect(isSelected ? null : agent)}
    >
      {isSelected && (
        <div className="absolute -top-2 -right-2">
          <div className="bg-blue-500 text-white rounded-full p-1">
            <CheckIcon className="h-3 w-3" />
          </div>
        </div>
      )}

      {isSuggested && (
        <div className="absolute -top-2 -left-2">
          <div className="bg-purple-500 text-white rounded-full p-1">
            <SparklesIcon className="h-3 w-3" />
          </div>
        </div>
      )}

      <div className="space-y-2">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h4 className={`font-semibold text-gray-900 ${compact ? 'text-sm' : 'text-base'}`}>
              {agent.name}
            </h4>
            <div className="flex items-center mt-1">
              <TagIcon className="h-3 w-3 text-gray-400 mr-1" />
              <span className="text-xs text-gray-500 capitalize">
                {agent.specialization}
              </span>
            </div>
          </div>
          <CpuChipIcon className={`text-gray-400 ${compact ? 'h-4 w-4' : 'h-5 w-5'}`} />
        </div>

        {!compact && (
          <>
            <p className="text-sm text-gray-600 line-clamp-2">
              {agent.description}
            </p>

            <div className="flex flex-wrap gap-1">
              {agent.capabilities.slice(0, 3).map((capability) => (
                <span
                  key={capability}
                  className="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                >
                  {capability}
                </span>
              ))}
              {agent.capabilities.length > 3 && (
                <span className="inline-block px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded">
                  +{agent.capabilities.length - 3} more
                </span>
              )}
            </div>

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{agent.llm_provider} · {agent.llm_model}</span>
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
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="border border-gray-200 rounded-lg p-4">
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded mb-4"></div>
                <div className="flex space-x-2">
                  <div className="h-6 bg-gray-200 rounded w-16"></div>
                  <div className="h-6 bg-gray-200 rounded w-20"></div>
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
          <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2" />
          <div>
            <h3 className="text-sm font-medium text-red-800">Failed to load agents</h3>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header and Controls */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Select an Agent
          </h3>
          {onSuggestAgents && taskDescription.trim() && (
            <button
              onClick={handleSuggestAgents}
              disabled={suggestionLoading}
              className="inline-flex items-center px-3 py-2 border border-purple-300 rounded-lg text-sm font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {suggestionLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-700 mr-2" />
              ) : (
                <SparklesIcon className="h-4 w-4 mr-2" />
              )}
              Get Suggestions
            </button>
          )}
        </div>

        {/* Search and Filter */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search agents by name, description, or capabilities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <select
            value={selectedSpecialization}
            onChange={(e) => setSelectedSpecialization(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent min-w-[150px]"
          >
            <option value="">All Specializations</option>
            {specializations.map((spec) => (
              <option key={spec} value={spec}>
                {spec.charAt(0).toUpperCase() + spec.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Selection Summary */}
        {selectedAgent && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm text-blue-800">
              <strong>Selected:</strong> {selectedAgent.name} ({selectedAgent.specialization})
            </p>
          </div>
        )}
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-purple-700 flex items-center">
            <SparklesIcon className="h-4 w-4 mr-1" />
            Suggested Agents
          </h4>
          <div className={`grid gap-3 ${compact ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-2'}`}>
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

      {/* Agents Grid */}
      <div className="space-y-3">
        {filteredAgents.length === 0 ? (
          <div className="text-center py-8">
            <CpuChipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {searchTerm || selectedSpecialization 
                ? 'No agents match your criteria. Try adjusting your search or filters.' 
                : 'No agents available'
              }
            </p>
          </div>
        ) : (
          <>
            <h4 className="text-sm font-medium text-gray-700">
              Available Agents ({filteredAgents.length})
            </h4>
            <motion.div 
              layout
              className={`grid gap-3 ${
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