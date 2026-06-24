<script setup lang="ts">
import { CheckCircle2, XCircle } from '@lucide/vue'
import { watch } from 'vue'

import type { Quiz, QuizAnswer } from '../types'
import { fireSuccessConfetti } from '../utils/confetti'

const props = defineProps<{
  quiz: Quiz
  answer: QuizAnswer | null
}>()

defineEmits<{ answer: [index: number] }>()

watch(
  () => props.answer?.is_correct,
  (isCorrect) => {
    if (isCorrect) fireSuccessConfetti()
  },
)
</script>

<template>
  <section class="quiz-card">
    <div class="message-label">选择题</div>
    <h3>{{ quiz.question }}</h3>
    <div class="quiz-options">
      <button
        v-for="(option, index) in quiz.options"
        :key="option.label"
        type="button"
        :disabled="Boolean(answer)"
        :class="{
          correct: answer && index === answer.correct_option_index,
          wrong: answer && index === answer.selected_option_index && !answer.is_correct,
        }"
        @click="$emit('answer', index)"
      >
        <strong>{{ option.label }}</strong>
        <span>{{ option.text }}</span>
      </button>
    </div>
    <p v-if="answer" class="quiz-result" :class="{ ok: answer.is_correct }">
      <CheckCircle2 v-if="answer.is_correct" :size="18" />
      <XCircle v-else :size="18" />
      {{ answer.is_correct ? '回答正确' : '回答错误' }}。{{ answer.explanation }}
    </p>
  </section>
</template>
