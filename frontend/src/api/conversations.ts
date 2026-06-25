import { apiClient } from './client'
import type { Conversation, Message } from '../types'

export async function listConversations(): Promise<Conversation[]> {
  const { data } = await apiClient.get<{ items: Conversation[] }>('/api/conversations')
  return data.items
}

export async function createConversation(title = '新对话'): Promise<Conversation> {
  const { data } = await apiClient.post<Conversation>('/api/conversations', { title })
  return data
}

export async function updateConversationSummary(id: string, summary: string): Promise<Conversation> {
  const { data } = await apiClient.patch<Conversation>(`/api/conversations/${id}`, { summary })
  return data
}

export async function pinConversation(id: string): Promise<Conversation> {
  const { data } = await apiClient.post<Conversation>(`/api/conversations/${id}/pin`)
  return data
}

export async function unpinConversation(id: string): Promise<Conversation> {
  const { data } = await apiClient.post<Conversation>(`/api/conversations/${id}/unpin`)
  return data
}

export async function deleteConversation(id: string): Promise<void> {
  await apiClient.delete(`/api/conversations/${id}`)
}

export async function listMessages(conversationId: string): Promise<Message[]> {
  const { data } = await apiClient.get<{ items: Message[] }>(`/api/conversations/${conversationId}/messages`)
  return data.items
}

export async function createMessage(conversationId: string, content: string): Promise<Message> {
  const { data } = await apiClient.post<Message>(`/api/conversations/${conversationId}/messages`, { content })
  return data
}

export async function updateMessage(messageId: string, content: string): Promise<Message> {
  const { data } = await apiClient.patch<Message>(`/api/messages/${messageId}`, { content })
  return data
}
