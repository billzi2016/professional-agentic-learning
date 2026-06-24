export type HealthStatus = 'healthy' | 'unhealthy' | 'checking'

export interface Conversation {
  id: string
  title: string
  is_pinned: boolean
  last_message_preview?: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system' | 'tool'
  message_type: 'plain' | 'learning_card' | 'quiz' | 'action'
  content: string
  is_editable: boolean
  can_regenerate_from_here: boolean
  learning_card_id?: string | null
  metadata: Record<string, unknown>
  created_at: string
}

export interface ProviderStatus {
  provider: string
  provider_type: string
  model: string
  base_url: string
  status: HealthStatus
  latency_ms?: number | null
  checked_at?: string | null
  error?: string | null
}

export interface Quiz {
  id: string
  question: string
  options: Array<{ label: string; text: string }>
  answered: boolean
}

export interface QuizAnswer {
  is_correct: boolean
  selected_option_index: number
  correct_option_index: number
  explanation: string
}
