import { defineStore } from 'pinia'

import {
  createConversation,
  deleteConversation,
  listConversations,
  pinConversation,
  unpinConversation,
  updateConversationSummary,
} from '../api/conversations'
import type { Conversation } from '../types'

export const useConversationStore = defineStore('conversations', {
  state: () => ({
    items: [] as Conversation[],
    currentId: '',
    loading: false,
  }),
  getters: {
    current(state) {
      return state.items.find((item) => item.id === state.currentId) ?? null
    },
  },
  actions: {
    async load() {
      this.loading = true
      try {
        this.items = await listConversations()
        if (!this.currentId && this.items.length > 0) {
          this.currentId = this.items[0].id
        }
      } finally {
        this.loading = false
      }
    },
    async create(title = '新对话') {
      const conversation = await createConversation(title)
      this.items = [conversation, ...this.items]
      this.currentId = conversation.id
      return conversation
    },
    select(id: string) {
      this.currentId = id
    },
    async togglePin(conversation: Conversation) {
      const updated = conversation.is_pinned
        ? await unpinConversation(conversation.id)
        : await pinConversation(conversation.id)
      this.items = this.items
        .map((item) => (item.id === updated.id ? { ...item, ...updated } : item))
        .sort((a, b) => Number(b.is_pinned) - Number(a.is_pinned) || b.updated_at.localeCompare(a.updated_at))
    },
    async remove(id: string) {
      await deleteConversation(id)
      this.items = this.items.filter((item) => item.id !== id)
      if (this.currentId === id) {
        this.currentId = this.items[0]?.id ?? ''
      }
    },
    async editSummary(conversation: Conversation, summary: string) {
      const updated = await updateConversationSummary(conversation.id, summary)
      this.items = this.items.map((item) => (item.id === updated.id ? { ...item, ...updated } : item))
    },
  },
})
