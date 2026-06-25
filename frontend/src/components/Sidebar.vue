<script setup lang="ts">
import { MessageSquarePlus, Pencil, Pin, PinOff, Trash2 } from '@lucide/vue'
import dayjs from 'dayjs'

import { useConversationStore } from '../stores/conversations'

defineEmits<{ select: [id: string] }>()

const conversations = useConversationStore()

async function editSummary(item: { id: string; summary: string; title: string }) {
  const value = window.prompt('修改左侧摘要', item.summary || item.title)
  if (value?.trim()) {
    await conversations.editSummary(item as never, value.trim())
  }
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <strong>学习对话</strong>
      <button class="icon-button" type="button" aria-label="新建对话" @click="conversations.create()">
        <MessageSquarePlus :size="18" />
      </button>
    </div>

    <div class="conversation-list">
      <button
        v-for="item in conversations.items"
        :key="item.id"
        class="conversation-item"
        :class="{ active: item.id === conversations.currentId, pinned: item.is_pinned }"
        type="button"
        @click="$emit('select', item.id)"
      >
        <span class="conversation-title">{{ item.summary || item.title }}</span>
        <span class="conversation-time">{{ dayjs(item.updated_at).format('MM-DD HH:mm') }}</span>
        <span class="conversation-actions" @click.stop>
          <button class="mini-button" type="button" aria-label="修改摘要" @click="editSummary(item)">
            <Pencil :size="14" />
          </button>
          <button class="mini-button" type="button" :aria-label="item.is_pinned ? '取消置顶' : '置顶'" @click="conversations.togglePin(item)">
            <PinOff v-if="item.is_pinned" :size="14" />
            <Pin v-else :size="14" />
          </button>
          <button class="mini-button danger" type="button" aria-label="删除对话" @click="conversations.remove(item.id)">
            <Trash2 :size="14" />
          </button>
        </span>
      </button>
    </div>
  </aside>
</template>
