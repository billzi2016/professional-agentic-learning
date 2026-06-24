import { defineStore } from 'pinia'

import { createMessage, listMessages, updateMessage } from '../api/conversations'
import { answerQuiz, getQuiz } from '../api/learning'
import type { Message, Quiz, QuizAnswer } from '../types'
import { streamApi } from '../utils/sse'

export const useMessageStore = defineStore('messages', {
  state: () => ({
    items: [] as Message[],
    activeQuiz: null as Quiz | null,
    quizAnswer: null as QuizAnswer | null,
    loading: false,
    streaming: false,
    error: '',
    abortController: null as AbortController | null,
  }),
  actions: {
    async load(conversationId: string) {
      this.loading = true
      try {
        this.items = await listMessages(conversationId)
        this.activeQuiz = null
        this.quizAnswer = null
      } finally {
        this.loading = false
      }
    },
    async send(conversationId: string, content: string) {
      const userMessage = await createMessage(conversationId, content)
      this.items.push(userMessage)
      await this.startLearning(conversationId, userMessage.id, 'start')
    },
    async editLatest(messageId: string, content: string) {
      const updated = await updateMessage(messageId, content)
      this.items = this.items.map((item) => (item.id === updated.id ? updated : item))
    },
    async startLearning(conversationId: string, userMessageId: string, action: 'start' | 'continue' | 'regenerate') {
      const draft = this.createAssistantDraft()
      this.items.push(draft)
      await this.runCardStream(`/api/conversations/${conversationId}/learn/stream`, {
        user_message_id: userMessageId,
        action,
      }, draft.id)
    },
    async continueLearning(conversationId: string) {
      const latestUser = [...this.items].reverse().find((item) => item.role === 'user')
      if (latestUser) {
        await this.startLearning(conversationId, latestUser.id, 'continue')
      }
    },
    async regenerateLatest(conversationId: string, cardId: string) {
      const latestUser = [...this.items].reverse().find((item) => item.role === 'user')
      if (latestUser) {
        await this.startLearning(conversationId, latestUser.id, 'regenerate')
      } else {
        this.error = `找不到卡片 ${cardId} 对应的用户输入`
      }
    },
    async generateQuiz(conversationId: string, learningCardId: string) {
      this.activeQuiz = null
      this.quizAnswer = null
      this.streaming = true
      this.error = ''
      this.abortController = new AbortController()
      let quizId = ''
      try {
        await streamApi(
          `/api/conversations/${conversationId}/quiz/stream`,
          { learning_card_id: learningCardId },
          this.abortController.signal,
          {
            onEvent: (event, data) => {
              if (event === 'quiz_done' && typeof data.quiz_id === 'string') {
                quizId = data.quiz_id
              }
              if (event === 'error') {
                this.error = String(data.message ?? '题目生成失败')
              }
            },
            onError: (message) => {
              this.error = message
            },
          },
        )
        if (quizId) {
          this.activeQuiz = await getQuiz(quizId)
        }
      } finally {
        this.streaming = false
        this.abortController = null
      }
    },
    async answerActiveQuiz(index: number) {
      if (!this.activeQuiz) return
      this.quizAnswer = await answerQuiz(this.activeQuiz.id, index)
    },
    stopStreaming() {
      this.abortController?.abort()
      this.streaming = false
    },
    createAssistantDraft(): Message {
      return {
        id: `draft-${crypto.randomUUID()}`,
        role: 'assistant',
        message_type: 'learning_card',
        content: '',
        is_editable: false,
        can_regenerate_from_here: false,
        metadata: {},
        created_at: new Date().toISOString(),
      }
    },
    async runCardStream(path: string, body: Record<string, unknown>, draftId: string) {
      this.streaming = true
      this.error = ''
      this.abortController = new AbortController()
      try {
        await streamApi(path, body, this.abortController.signal, {
          onEvent: (event, data) => {
            if (event === 'card_delta') {
              this.appendToDraft(draftId, String(data.delta ?? ''))
            }
            if (event === 'card_done') {
              const messageId = String(data.message_id ?? draftId)
              const cardId = String(data.card_id ?? '')
              this.items = this.items.map((item) =>
                item.id === draftId
                  ? { ...item, id: messageId, learning_card_id: cardId, can_regenerate_from_here: true }
                  : item,
              )
            }
            if (event === 'error') {
              this.error = String(data.message ?? '生成失败')
            }
          },
          onError: (message) => {
            this.error = message
          },
        })
      } finally {
        this.streaming = false
        this.abortController = null
      }
    },
    appendToDraft(draftId: string, delta: string) {
      this.items = this.items.map((item) => (item.id === draftId ? { ...item, content: item.content + delta } : item))
    },
  },
})
