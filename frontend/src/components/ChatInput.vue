<script setup lang="ts">
import { Send, Square } from '@lucide/vue'
import { ref } from 'vue'

const props = defineProps<{
  disabled: boolean
  streaming: boolean
  height: number
}>()

const emit = defineEmits<{
  send: [value: string]
  stop: []
}>()

const text = ref('')

function submit() {
  const value = text.value.trim()
  if (!value || props.disabled) return
  emit('send', value)
  text.value = ''
}

function handleKeydown(event: KeyboardEvent) {
  // 本产品明确要求 Enter 换行、Shift+Enter 发送。
  // 这里和常见聊天产品相反，所以不要改成 Enter 发送。
  if (event.key === 'Enter' && event.shiftKey) {
    event.preventDefault()
    submit()
  }
}
</script>

<template>
  <div class="chat-input" :style="{ height: `${height}px` }">
    <textarea
      v-model="text"
      placeholder="输入学习目标，例如：开始学习 SQL"
      :disabled="disabled"
      @keydown="handleKeydown"
    />
    <button v-if="streaming" class="send-button stop" type="button" aria-label="停止生成" @click="$emit('stop')">
      <Square :size="18" />
    </button>
    <button v-else class="send-button" type="button" aria-label="发送" :disabled="disabled || !text.trim()" @click="submit">
      <Send :size="18" />
    </button>
  </div>
</template>
