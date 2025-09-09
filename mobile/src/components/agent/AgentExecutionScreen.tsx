/**
 * React Native Agent Execution Screen for DBAO
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  StyleSheet,
  ActivityIndicator,
  Animated,
  RefreshControl,
  Modal,
  FlatList,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform
} from 'react-native';
import { useDBAAO, useAgents, useAgentExecution } from '../../hooks/useDBAAO';
import { Agent, AgentInstance } from '../../services/dbao.service';
import { DBAO_CONFIG } from '../../config/dbao.config';

interface AgentCardProps {
  agent: Agent;
  selected: boolean;
  onSelect: () => void;
  suggested?: boolean;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, selected, onSelect, suggested = false }) => {
  const animatedValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.spring(animatedValue, {
      toValue: selected ? 1 : 0,
      useNativeDriver: false,
    }).start();
  }, [selected, animatedValue]);

  const borderColor = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: ['#E5E7EB', '#3B82F6']
  });

  const backgroundColor = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: ['#FFFFFF', '#EFF6FF']
  });

  return (
    <TouchableOpacity onPress={onSelect} style={styles.agentCardContainer}>
      <Animated.View 
        style={[
          styles.agentCard,
          { borderColor, backgroundColor },
          suggested && styles.suggestedCard
        ]}
      >
        {suggested && (
          <View style={styles.suggestedBadge}>
            <Text style={styles.suggestedText}>✨</Text>
          </View>
        )}
        
        <View style={styles.agentHeader}>
          <Text style={styles.agentName}>{agent.name}</Text>
          <Text style={styles.agentSpecialization}>{agent.specialization}</Text>
        </View>
        
        <Text style={styles.agentDescription} numberOfLines={2}>
          {agent.description}
        </Text>
        
        <View style={styles.agentCapabilities}>
          {agent.capabilities.slice(0, 3).map((capability, index) => (
            <View key={index} style={styles.capabilityTag}>
              <Text style={styles.capabilityText}>{capability}</Text>
            </View>
          ))}
          {agent.capabilities.length > 3 && (
            <View style={styles.capabilityTag}>
              <Text style={styles.capabilityText}>+{agent.capabilities.length - 3}</Text>
            </View>
          )}
        </View>
      </Animated.View>
    </TouchableOpacity>
  );
};

interface InstanceCardProps {
  instance: AgentInstance;
  onPress?: () => void;
}

const InstanceCard: React.FC<InstanceCardProps> = ({ instance, onPress }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processing':
        return '#F59E0B';
      case 'completed':
        return '#10B981';
      case 'failed':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing':
        return '⏳';
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
      default:
        return '⏸️';
    }
  };

  return (
    <TouchableOpacity onPress={onPress} style={styles.instanceCard}>
      <View style={styles.instanceHeader}>
        <Text style={styles.instanceAgent}>{instance.template.name}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(instance.status) + '20' }]}>
          <Text style={[styles.statusText, { color: getStatusColor(instance.status) }]}>
            {getStatusIcon(instance.status)} {instance.status}
          </Text>
        </View>
      </View>
      
      <Text style={styles.instanceTask} numberOfLines={2}>
        {instance.task_description}
      </Text>
      
      <View style={styles.instanceMeta}>
        <Text style={styles.instanceTime}>
          {new Date(instance.created_at).toLocaleDateString()}
        </Text>
        {instance.tokens_used > 0 && (
          <Text style={styles.instanceTokens}>
            {instance.tokens_used.toLocaleString()} tokens
          </Text>
        )}
      </View>
    </TouchableOpacity>
  );
};

const AgentExecutionScreen: React.FC = () => {
  const [taskDescription, setTaskDescription] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [showAgentSelector, setShowAgentSelector] = useState(false);
  const [suggestions, setSuggestions] = useState<Agent[]>([]);
  const [parameters, setParameters] = useState({
    max_tokens: 2000,
    temperature: 0.7,
    priority: 'normal' as 'low' | 'normal' | 'high'
  });

  const { agents, loading: agentsLoading, error: agentsError, refetch: refetchAgents } = useAgents();
  const { 
    executing, 
    instances, 
    error: executionError, 
    executeAgent, 
    suggestAgents,
    refetchInstances 
  } = useAgentExecution();

  const { connected: wsConnected, connecting: wsConnecting } = useDBAAO();

  const handleSuggestAgents = useCallback(async () => {
    if (!taskDescription.trim()) {
      Alert.alert('Task Required', 'Please enter a task description to get suggestions');
      return;
    }

    try {
      const agentSuggestions = await suggestAgents(taskDescription);
      const suggestedAgents = agentSuggestions.map(s => s.agent);
      setSuggestions(suggestedAgents);
      
      if (suggestedAgents.length > 0) {
        Alert.alert('Suggestions Found', `Found ${suggestedAgents.length} agent suggestions`);
      } else {
        Alert.alert('No Suggestions', 'No specific agent suggestions found for this task');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to get agent suggestions');
    }
  }, [taskDescription, suggestAgents]);

  const handleExecute = useCallback(async () => {
    if (!taskDescription.trim()) {
      Alert.alert('Task Required', 'Please enter a task description');
      return;
    }

    if (!selectedAgent) {
      Alert.alert('Agent Required', 'Please select an agent to execute the task');
      return;
    }

    try {
      const instance = await executeAgent({
        agent_type: selectedAgent.specialization,
        task_description: taskDescription,
        parameters
      });

      if (instance) {
        Alert.alert('Success', 'Agent execution started successfully');
        setTaskDescription('');
        setSelectedAgent(null);
        setSuggestions([]);
      }
    } catch (error) {
      // Error handling is done in the hook
    }
  }, [taskDescription, selectedAgent, parameters, executeAgent]);

  const handleSelectAgent = useCallback((agent: Agent) => {
    setSelectedAgent(agent);
    setShowAgentSelector(false);
  }, []);

  const renderAgentItem = ({ item }: { item: Agent }) => (
    <AgentCard
      agent={item}
      selected={selectedAgent?.id === item.id}
      onSelect={() => handleSelectAgent(item)}
      suggested={suggestions.some(s => s.id === item.id)}
    />
  );

  const renderInstanceItem = ({ item }: { item: AgentInstance }) => (
    <InstanceCard
      instance={item}
      onPress={() => {
        if (item.status === 'completed' && item.result) {
          Alert.alert(
            'Execution Result',
            typeof item.result === 'string' ? item.result : JSON.stringify(item.result, null, 2),
            [{ text: 'OK' }],
            { scrollEnabled: true }
          );
        } else if (item.status === 'failed' && item.error_message) {
          Alert.alert('Execution Failed', item.error_message);
        }
      }}
    />
  );

  if (agentsLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#3B82F6" />
          <Text style={styles.loadingText}>Loading agents...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (agentsError) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Failed to load agents</Text>
          <Text style={styles.errorMessage}>{agentsError}</Text>
          <TouchableOpacity onPress={refetchAgents} style={styles.retryButton}>
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView 
          style={styles.scrollView}
          refreshControl={
            <RefreshControl
              refreshing={agentsLoading}
              onRefresh={() => {
                refetchAgents();
                refetchInstances();
              }}
            />
          }
        >
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Agent Execution</Text>
            <View style={styles.statusContainer}>
              <View style={[
                styles.connectionStatus, 
                { backgroundColor: wsConnected ? '#10B981' : wsConnecting ? '#F59E0B' : '#EF4444' }
              ]} />
              <Text style={styles.statusText}>
                {wsConnected ? 'Live' : wsConnecting ? 'Connecting' : 'Offline'}
              </Text>
            </View>
          </View>

          {/* Task Input */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Task Description</Text>
            <TextInput
              style={styles.taskInput}
              value={taskDescription}
              onChangeText={setTaskDescription}
              placeholder="Describe what you want the agent to do..."
              multiline
              numberOfLines={4}
              textAlignVertical="top"
            />
          </View>

          {/* Agent Selection */}
          <View style={styles.section}>
            <View style={styles.agentSectionHeader}>
              <Text style={styles.sectionTitle}>Selected Agent</Text>
              <TouchableOpacity
                onPress={handleSuggestAgents}
                disabled={!taskDescription.trim()}
                style={[styles.suggestButton, !taskDescription.trim() && styles.disabledButton]}
              >
                <Text style={[styles.suggestButtonText, !taskDescription.trim() && styles.disabledText]}>
                  ✨ Suggest
                </Text>
              </TouchableOpacity>
            </View>

            {selectedAgent ? (
              <View style={styles.selectedAgentContainer}>
                <AgentCard
                  agent={selectedAgent}
                  selected={true}
                  onSelect={() => setShowAgentSelector(true)}
                />
                <TouchableOpacity
                  onPress={() => setShowAgentSelector(true)}
                  style={styles.changeAgentButton}
                >
                  <Text style={styles.changeAgentText}>Change Agent</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <TouchableOpacity
                onPress={() => setShowAgentSelector(true)}
                style={styles.selectAgentButton}
              >
                <Text style={styles.selectAgentText}>Select an Agent</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Execute Button */}
          <TouchableOpacity
            onPress={handleExecute}
            disabled={executing || !taskDescription.trim() || !selectedAgent}
            style={[
              styles.executeButton,
              (executing || !taskDescription.trim() || !selectedAgent) && styles.disabledButton
            ]}
          >
            {executing ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={[
                styles.executeButtonText,
                (executing || !taskDescription.trim() || !selectedAgent) && styles.disabledText
              ]}>
                ▶️ Execute Agent
              </Text>
            )}
          </TouchableOpacity>

          {/* Execution Error */}
          {executionError && (
            <View style={styles.errorBanner}>
              <Text style={styles.errorBannerText}>{executionError}</Text>
            </View>
          )}

          {/* Recent Executions */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Executions ({instances.length})</Text>
            {instances.length > 0 ? (
              <FlatList
                data={instances.slice(0, 10)}
                renderItem={renderInstanceItem}
                keyExtractor={(item) => item.id}
                scrollEnabled={false}
              />
            ) : (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>No executions yet</Text>
                <Text style={styles.emptySubtext}>Execute your first agent to see results here</Text>
              </View>
            )}
          </View>
        </ScrollView>

        {/* Agent Selector Modal */}
        <Modal
          visible={showAgentSelector}
          animationType="slide"
          presentationStyle="pageSheet"
        >
          <SafeAreaView style={styles.modalContainer}>
            <View style={styles.modalHeader}>
              <TouchableOpacity
                onPress={() => setShowAgentSelector(false)}
                style={styles.closeButton}
              >
                <Text style={styles.closeButtonText}>Cancel</Text>
              </TouchableOpacity>
              <Text style={styles.modalTitle}>Select Agent</Text>
              <View style={styles.placeholder} />
            </View>

            {suggestions.length > 0 && (
              <View style={styles.suggestionsSection}>
                <Text style={styles.suggestionsTitle}>✨ Suggested Agents</Text>
                <FlatList
                  data={suggestions}
                  renderItem={renderAgentItem}
                  keyExtractor={(item) => `suggestion-${item.id}`}
                  horizontal
                  showsHorizontalScrollIndicator={false}
                  style={styles.suggestionsList}
                />
              </View>
            )}

            <FlatList
              data={agents}
              renderItem={renderAgentItem}
              keyExtractor={(item) => item.id}
              numColumns={1}
              contentContainerStyle={styles.agentsList}
            />
          </SafeAreaView>
        </Modal>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6B7280',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  errorText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#EF4444',
    marginBottom: 8,
  },
  errorMessage: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 16,
  },
  retryButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  connectionStatus: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    color: '#6B7280',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  taskInput: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    minHeight: 100,
  },
  agentSectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  suggestButton: {
    backgroundColor: '#8B5CF6',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  suggestButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  disabledButton: {
    backgroundColor: '#D1D5DB',
  },
  disabledText: {
    color: '#9CA3AF',
  },
  selectedAgentContainer: {
    position: 'relative',
  },
  changeAgentButton: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#3B82F6',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  changeAgentText: {
    color: 'white',
    fontSize: 10,
    fontWeight: '600',
  },
  selectAgentButton: {
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#D1D5DB',
    borderStyle: 'dashed',
    borderRadius: 8,
    padding: 24,
    alignItems: 'center',
  },
  selectAgentText: {
    color: '#6B7280',
    fontSize: 16,
    fontWeight: '500',
  },
  executeButton: {
    backgroundColor: '#3B82F6',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  executeButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  errorBanner: {
    backgroundColor: '#FEF2F2',
    borderColor: '#FECACA',
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  errorBannerText: {
    color: '#DC2626',
    fontSize: 14,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyText: {
    fontSize: 16,
    color: '#6B7280',
    fontWeight: '500',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 4,
  },
  agentCardContainer: {
    marginBottom: 12,
  },
  agentCard: {
    backgroundColor: 'white',
    borderWidth: 2,
    borderRadius: 12,
    padding: 16,
    position: 'relative',
  },
  suggestedCard: {
    borderColor: '#8B5CF6',
  },
  suggestedBadge: {
    position: 'absolute',
    top: -6,
    right: -6,
    backgroundColor: '#8B5CF6',
    borderRadius: 12,
    width: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  suggestedText: {
    fontSize: 12,
  },
  agentHeader: {
    marginBottom: 8,
  },
  agentName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
  },
  agentSpecialization: {
    fontSize: 12,
    color: '#6B7280',
    textTransform: 'capitalize',
  },
  agentDescription: {
    fontSize: 14,
    color: '#4B5563',
    marginBottom: 12,
  },
  agentCapabilities: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  capabilityTag: {
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginRight: 6,
    marginBottom: 4,
  },
  capabilityText: {
    fontSize: 10,
    color: '#374151',
  },
  instanceCard: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#E5E7EB',
  },
  instanceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  instanceAgent: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  instanceTask: {
    fontSize: 13,
    color: '#4B5563',
    marginBottom: 8,
  },
  instanceMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  instanceTime: {
    fontSize: 11,
    color: '#9CA3AF',
  },
  instanceTokens: {
    fontSize: 11,
    color: '#9CA3AF',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    backgroundColor: 'white',
  },
  closeButton: {
    paddingVertical: 8,
  },
  closeButtonText: {
    color: '#3B82F6',
    fontSize: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
  },
  placeholder: {
    width: 60,
  },
  suggestionsSection: {
    backgroundColor: 'white',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  suggestionsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#8B5CF6',
    marginBottom: 12,
    paddingHorizontal: 16,
  },
  suggestionsList: {
    paddingHorizontal: 16,
  },
  agentsList: {
    padding: 16,
  },
});

export default AgentExecutionScreen;