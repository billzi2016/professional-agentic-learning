<script setup lang="ts">
import { Download } from '@lucide/vue'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { initializeCsrf } from '../api/client'
import ActionBar from '../components/ActionBar.vue'
import ChatInput from '../components/ChatInput.vue'
import MessageBubble from '../components/MessageBubble.vue'
import ProviderStatus from '../components/ProviderStatus.vue'
import QuizCard from '../components/QuizCard.vue'
import Sidebar from '../components/Sidebar.vue'
import { useConversationStore } from '../stores/conversations'
import { useLayoutStore } from '../stores/layout'
import { useMessageStore } from '../stores/messages'
import { useProviderStore } from '../stores/provider'
import { exportElementToPdf } from '../utils/pdf'
import { clamp } from '../utils/storage'

const route = useRoute()
const router = useRouter()
const conversations = useConversationStore()
const messages = useMessageStore()
const provider = useProviderStore()
const layout = useLayoutStore()

const threadRef = ref<HTMLElement | null>(null)
const exportRef = ref<HTMLElement | null>(null)
const exporting = ref(false)

const latestCard = computed(() =>
  [...messages.items].reverse().find((item) => item.role === 'assistant' && item.learning_card_id),
)

function canEditMessageAt(index: number) {
  const item = messages.items[index]
  if (!item?.is_editable) return false

  // 用户刚发出消息时还没有形成一轮对话，此时不展示“修改输入”。
  // 只有后面已经出现 AI 回复，才说明这是可回退的最近一轮输入。
  return messages.items.slice(index + 1).some((next) => next.role === 'assistant')
}

async function selectConversation(id: string) {
  conversations.select(id)
  await router.replace(`/chat/${id}`)
  await messages.load(id)
}

async function send(value: string) {
  let conversationId = conversations.currentId
  if (!conversationId) {
    const created = await conversations.create(value.slice(0, 40))
    conversationId = created.id
    await router.replace(`/chat/${conversationId}`)
  }
  await messages.send(conversationId, value)
  await conversations.load()
  conversations.select(conversationId)
}

function startSidebarResize(event: PointerEvent) {
  const startX = event.clientX
  const startWidth = layout.sidebarWidth

  // 拖拽只负责改变侧栏宽度，不承担通用拖拽框架职责。
  // 宽度范围在 store 里二次 clamp，避免布局被拖坏。
  function move(moveEvent: PointerEvent) {
    layout.setSidebarWidth(startWidth + moveEvent.clientX - startX)
  }
  function stop() {
    window.removeEventListener('pointermove', move)
    window.removeEventListener('pointerup', stop)
  }
  window.addEventListener('pointermove', move)
  window.addEventListener('pointerup', stop)
}

function startInputResize(event: PointerEvent) {
  const startY = event.clientY
  const startHeight = layout.inputHeight

  function move(moveEvent: PointerEvent) {
    layout.setInputHeight(clamp(startHeight - (moveEvent.clientY - startY), 80, 320))
  }
  function stop() {
    window.removeEventListener('pointermove', move)
    window.removeEventListener('pointerup', stop)
  }
  window.addEventListener('pointermove', move)
  window.addEventListener('pointerup', stop)
}

async function exportPdf() {
  if (!exportRef.value || exporting.value) return
  exporting.value = true
  try {
    await exportElementToPdf(exportRef.value, conversations.current?.title ?? '学习记录')
  } finally {
    exporting.value = false
  }
}

watch(
  () => messages.items.length,
  async () => {
    await nextTick()
    threadRef.value?.scrollTo({ top: threadRef.value.scrollHeight })
  },
)

onMounted(async () => {
  await initializeCsrf()
  await Promise.all([conversations.load(), provider.load()])
  provider.startHeartbeat()
  const routeId = String(route.params.conversationId ?? '')
  const target = routeId || conversations.currentId
  if (target) {
    await selectConversation(target)
  }
})

onUnmounted(() => {
  provider.stopHeartbeat()
})
</script>

<template>
  <main class="app-shell">
    <div class="sidebar-shell" :style="{ width: `${layout.sidebarWidth}px` }">
      <Sidebar @select="selectConversation" />
      <button class="resize-handle vertical" type="button" aria-label="调整侧边栏宽度" @pointerdown="startSidebarResize" />
    </div>

    <section class="workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">Learning cards</p>
          <h1>{{ conversations.current?.title ?? 'AI 学习卡片' }}</h1>
        </div>
        <div class="topbar-actions">
          <button class="export-button" type="button" :disabled="exporting || messages.items.length === 0" @click="exportPdf">
            <Download :size="16" />
            {{ exporting ? '导出中' : '导出 PDF' }}
          </button>
          <ProviderStatus />
        </div>
      </header>

      <div ref="threadRef" class="thread">
        <div ref="exportRef" class="export-surface">
          <div v-if="messages.items.length === 0" class="empty-state">
            <h2>从一个具体目标开始</h2>
            <p>例如：开始学习 SQL。系统会一次生成一张卡片，再给你继续学习或出题练习。</p>
          </div>

          <MessageBubble
            v-for="(item, index) in messages.items"
            :key="item.id"
            :message="item"
            :can-edit="canEditMessageAt(index)"
            @edit="messages.editLatest"
            @regenerate="(cardId) => conversations.currentId && messages.regenerateLatest(conversations.currentId, cardId)"
            @next-topic="(topic) => conversations.currentId && messages.continueWithTopic(conversations.currentId, topic)"
          />

          <QuizCard
            v-if="messages.activeQuiz"
            :quiz="messages.activeQuiz"
            :answer="messages.quizAnswer"
            @answer="messages.answerActiveQuiz"
          />
        </div>
      </div>

      <footer class="composer">
        <button class="resize-handle horizontal" type="button" aria-label="调整输入框高度" @pointerdown="startInputResize" />
        <p v-if="messages.error" class="error-line">{{ messages.error }}</p>
        <ActionBar
          v-if="latestCard"
          :disabled="messages.streaming"
          @continue="conversations.currentId && messages.continueLearning(conversations.currentId)"
          @quiz="conversations.currentId && latestCard?.learning_card_id && messages.generateQuiz(conversations.currentId, latestCard.learning_card_id)"
        />
        <ChatInput
          :height="layout.inputHeight"
          :disabled="messages.loading"
          :streaming="messages.streaming"
          @send="send"
          @stop="messages.stopStreaming"
        />
      </footer>
    </section>
  </main>
</template>
