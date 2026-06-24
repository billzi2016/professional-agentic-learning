<script setup lang="ts">
import { Pencil, RotateCcw } from '@lucide/vue'
import { ref } from 'vue'

import type { Message } from '../types'
import MarkdownRenderer from './MarkdownRenderer.vue'

const props = defineProps<{ message: Message }>()
const emit = defineEmits<{
  edit: [id: string, value: string]
  regenerate: [cardId: string]
}>()

const editing = ref(false)
const draft = ref(props.message.content)

function saveEdit() {
  const value = draft.value.trim()
  if (!value) return
  emit('edit', props.message.id, value)
  editing.value = false
}
</script>

<template>
  <article class="message" :class="message.role">
    <div class="message-label">{{ message.role === 'user' ? '你' : 'AI 导师' }}</div>

    <template v-if="editing">
      <textarea v-model="draft" class="edit-textarea" />
      <div class="inline-actions">
        <button type="button" @click="saveEdit">保存</button>
        <button type="button" @click="editing = false">取消</button>
      </div>
    </template>
    <MarkdownRenderer v-else :source="message.content || '正在生成...'" />

    <div class="message-actions">
      <button v-if="message.is_editable" type="button" @click="editing = true">
        <Pencil :size="14" />
        修改输入
      </button>
      <button
        v-if="message.can_regenerate_from_here && message.learning_card_id"
        type="button"
        @click="$emit('regenerate', message.learning_card_id)"
      >
        <RotateCcw :size="14" />
        重新生成
      </button>
    </div>
  </article>
</template>
