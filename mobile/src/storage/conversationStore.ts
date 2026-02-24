import AsyncStorage from '@react-native-async-storage/async-storage';

const ACTIVE_CONVO_KEY = 'active_conversation_id';

export async function getActiveConversationId(): Promise<string | null> {
  return AsyncStorage.getItem(ACTIVE_CONVO_KEY);
}

export async function setActiveConversationId(id: string): Promise<void> {
  await AsyncStorage.setItem(ACTIVE_CONVO_KEY, id);
}

export async function clearActiveConversationId(): Promise<void> {
  await AsyncStorage.removeItem(ACTIVE_CONVO_KEY);
}
