<script setup lang="ts">
import { Pencil, RotateCcw } from '@lucide/vue'
import { computed, ref } from 'vue'

import type { Message } from '../types'
import MarkdownRenderer from './MarkdownRenderer.vue'

const props = defineProps<{
  message: Message
  canEdit: boolean
  canRegenerate: boolean
  regenerateCardId?: string
}>()
const emit = defineEmits<{
  edit: [id: string, value: string]
  regenerate: [cardId: string]
  nextTopic: [topic: string]
}>()

const editing = ref(false)
const draft = ref(props.message.content)
const nextTopic = computed(() => {
  const value = props.message.metadata?.next_topic
  return typeof value === 'string' ? value : ''
})

function saveEdit() {
  const value = draft.value.trim()
  if (!value) return
  emit('edit', props.message.id, value)
  editing.value = false
}
</script>

<template>
  <div class="message-row" :class="message.role">
    <div v-if="message.role === 'user' && (canEdit || canRegenerate)" class="message-side-actions">
      <button v-if="canEdit" type="button" @click="editing = true">
        <Pencil :size="14" />
        修改输入
      </button>
      <button
        v-if="canRegenerate && regenerateCardId"
        type="button"
        @click="$emit('regenerate', regenerateCardId)"
      >
        <RotateCcw :size="14" />
        重新生成
      </button>
    </div>

    <article class="message" :class="message.role">
      <template v-if="editing">
        <textarea v-model="draft" class="edit-textarea" />
        <div class="inline-actions">
          <button type="button" @click="saveEdit">保存</button>
          <button type="button" @click="editing = false">取消</button>
        </div>
      </template>
      <MarkdownRenderer v-else :source="message.content || '正在生成...'" />

      <button
        v-if="nextTopic"
        class="next-topic"
        type="button"
        @click="$emit('nextTopic', nextTopic)"
      >
        下一个知识点：{{ nextTopic }}
      </button>
    </article>
  </div>
</template>
