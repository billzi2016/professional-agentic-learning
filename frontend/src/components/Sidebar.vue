<script setup lang="ts">
import { MessageSquarePlus, Pin, PinOff, Trash2 } from '@lucide/vue'
import dayjs from 'dayjs'

import { useConversationStore } from '../stores/conversations'

defineEmits<{ select: [id: string] }>()

const conversations = useConversationStore()
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
        :class="{ active: item.id === conversations.currentId }"
        type="button"
        @click="$emit('select', item.id)"
      >
        <span class="conversation-title">{{ item.title }}</span>
        <span class="conversation-preview">{{ item.last_message_preview || '还没有消息' }}</span>
        <span class="conversation-time">{{ dayjs(item.updated_at).format('MM-DD HH:mm') }}</span>
        <span class="conversation-actions" @click.stop>
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
