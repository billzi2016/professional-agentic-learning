import { apiClient } from './client'
import type { Quiz, QuizAnswer } from '../types'

export async function getQuiz(quizId: string): Promise<Quiz> {
  const { data } = await apiClient.get<Quiz>(`/api/quizzes/${quizId}`)
  return data
}

export async function answerQuiz(quizId: string, selected_option_index: number): Promise<QuizAnswer> {
  const { data } = await apiClient.post<QuizAnswer>(`/api/quizzes/${quizId}/answer`, {
    selected_option_index,
  })
  return data
}

export async function regenerateCard(cardId: string): Promise<Response> {
  return fetch(`${import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'}/api/learning-cards/${cardId}/regenerate`, {
    method: 'POST',
    credentials: 'include',
  })
}
