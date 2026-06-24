<script setup lang="ts">
import { BookOpen, ListChecks } from '@lucide/vue'

defineProps<{ disabled: boolean }>()
defineEmits<{
  continue: []
  quiz: []
}>()
</script>

<template>
  <div class="action-bar">
    <button type="button" :disabled="disabled" @click="$emit('continue')">
      <BookOpen :size="16" />
      继续学习
    </button>
    <button type="button" :disabled="disabled" @click="$emit('quiz')">
      <ListChecks :size="16" />
      出题练习
    </button>
  </div>
</template>
